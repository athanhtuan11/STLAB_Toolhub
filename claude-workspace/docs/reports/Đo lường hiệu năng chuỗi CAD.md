# Ghi mỗi bước một dòng, đo cả bản in

Câu trả lời ngắn: chuỗi CAD của STLab chỉ cần **một file `runs.jsonl` nối tiếp** do `run_v3.py` ghi ở ranh giới từng bước (dựng Blender, assembly-check, xuất CAD, cắt lớp), cộng **một file `prints.jsonl` ghi tay** sau mỗi lần in thử/lắp. Hai file này đủ để trả lời cả ba câu hỏi: bước nào chậm đi (a), bên trong bước đó thời gian đi đâu (b), và thiết kế có tốt dần lên không (c). Hầu hết số liệu đã có sẵn mà chưa ai thu. Bambu Studio CLI tự ghi `peak_rss_mb` và thời gian từng giai đoạn của từng bàn vào `result.json`. SolidCraft có sẵn `--profile-out` xuất Chrome trace. Windows tự giữ đỉnh RAM của mỗi tiến trình, nên không cần lấy mẫu dày. Phát hiện quan trọng nhất khi thử trên máy: **cProfile không thấy thời gian nằm trong bpy.ops/depsgraph**. Một operator chạy 21,8 s nhưng cProfile chỉ ghi 0,075 s. Vì vậy trong Blender phải đặt timer `perf_counter` quanh từng part/boolean, không dựa vào profiler Python. Về cảnh báo chậm đi, ngưỡng % cố định so với lần trước là cách MongoDB đã thử và bỏ, vì vừa báo nhầm vừa bỏ sót. Nên dùng median + MAD theo nhóm cùng `mode`/`cache`, cộng một lượt change-point định kỳ. Ở cấp dự án, chỉ số đáng giá nhất không phải tốc độ mà là **số vòng in tới khi lắp đạt** và **gate escape rate** (gate PASS mà in vẫn hỏng vì thiết kế). Chúng đo trực tiếp chi phí lớn nhất của xưởng: giờ máy, nhựa và thời gian của Tuan. Báo cáo này là đề xuất chờ duyệt, chưa sửa code nào.

**Cách đọc số.** Báo cáo dùng bốn nhãn. **[máy]** là số đo trên chính máy này (phiên nghiên cứu 2026-11-27, hoặc kết quả áp dụng tối 2026-11-27 của báo cáo tăng tốc trước). **[nguồn]** là số có trích dẫn. **[chọn]** là lựa chọn kỹ thuật (ngưỡng, hệ số, tần suất), không có nguồn và cần chỉnh theo lịch sử thật. **TODO** là chưa kiểm.

## Mốc hiện tại: 30 s một vòng, nhưng chưa có lịch sử để biết nó giữ được bao lâu

Đợt tăng tốc tối 2026-11-27 đưa vòng `run_v3.py --slice` của Cú Bông v3 (hình không đổi) từ **120–131 s xuống 30 s** [máy]. Có ba cách đã làm. Thứ nhất, `export_cad.py --fast` chỉ xuất 3MF (38 s → 1 s). Thứ hai, cache chữ ký hình học từng part (`meshhash.py`, `.cadhash`). Thứ ba, cache cắt lớp từng bàn và cache bước gộp project (`.slicehash`, `.mergehash`; 5 bàn 22–64 s → 6 s). Đợt này cũng cho thấy vì sao cần đo liên tục. Boolean MANIFOLD dựng lại cùng hình nhưng **khác thứ tự tam giác và lệch ±4 tam giác** mỗi lần, nên hash theo byte không dùng được. Riêng `shell-back` có vài đỉnh xê dịch ~0,06 mm giữa các lần dựng, làm bàn B thỉnh thoảng phải cắt lại (~10 s) [máy]. Những hiện tượng kiểu này chỉ lộ ra khi có **tỉ lệ cache hit theo thời gian**. Thời gian một lần chạy không cho thấy chúng. Bài học từ Turborepo cũng vậy: bản tóm tắt mỗi lần chạy (`--summarize`) được thiết kế riêng để gỡ lỗi "cache misses" và "task timing changes over time" ([Turborepo](https://turborepo.dev/docs/reference/run)).

Các công cụ build lớn đều đo như một **sản phẩm phụ của lần chạy bình thường**, không cần job benchmark riêng. Bazel bật JSON profile mặc định, giữ 5 profile gần nhất và gộp các sự kiện ngắn để file nhỏ ([Bazel](https://bazel.build/advanced/performance/json-trace-profile)). pytest-benchmark đưa commit vào tên file kết quả, ví dụ `0001_c9cca5de..._20150815_215724.json` ([pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/comparing.html)). Từ đó có ba nguyên tắc cho STLab. Đo ở script điều phối chứ không ở trong từng công cụ. Mỗi bản ghi mang `git_commit`. Giữ toàn bộ JSONL (rất nhỏ) nhưng chỉ giữ N trace gần nhất.

## Một dòng JSONL mỗi bước, gắn nhãn đủ để chỉ so cùng loại

Định dạng đề xuất là `metrics/runs.jsonl`, chỉ nối thêm, mỗi bước một dòng, cuối mỗi lần chạy thêm một dòng `step:"run"` tổng. JSONL ghi được từ nhiều worker song song. Nếu máy treo giữa chừng thì chỉ hỏng dòng cuối, bỏ qua là xong. pandas đọc được ngay. Ước tính khoảng 50 lần chạy/ngày × ~10 bước vẫn chỉ vài MB/năm [chọn, chưa đo]. SQLite chỉ đáng dùng khi cần truy vấn SQL qua nhiều tháng.

```json
{"run_id":"20261128-0812-a3f","ts_start":"2026-11-28T08:12:03+07:00","project":"english-teacher","cmd":"run_v3.py --slice",
 "git_commit":"b52393b","git_dirty":true,"mode":"fast","trigger":"manual","parallelism":3,
 "step":"slice","part":null,"plate":"B","duration_s":9.8,"exit_code":0,"cache":"miss","input_hash":"…",
 "tri_count":41230,"n_parts":4,"out_bytes":812345,
 "peak_mem_mb":612,"mem_metric":"peak_rss","cpu_s":27.4,
 "host_mem_avail_mb":5210,"host_cpu_pct":18,"first_run_after_boot":false,
 "tool":{"blender":"5.2.2","bambu":"<ver>","solidcraft":"<ver>"},
 "detail":{"prepare_time":660,"sliced_time":1290,"make_perimeters_time":196,"export_gcode_time":192,"bambu_peak_rss_mb":103.1}}
```

Những nhãn quan trọng nhất là các nhãn **ngăn so sai loại**. `mode` (`fast` = vòng 3MF, `release` = .sc/.step/.blend) và `cache` (`hit|miss|na`) tách hai quần thể khác hẳn nhau: một lần cắt lớp trúng cache mất ~0 s, trượt cache mất ~10 s, trộn lẫn thì median vô nghĩa. `parallelism` cần có vì `slice.py` đã cắt các bàn song song, nên thời gian từng bàn phụ thuộc số worker chạy cùng lúc. `host_mem_avail_mb`/`host_cpu_pct` lúc bắt đầu cần có vì máy này còn dùng làm việc khác, và `memjob.py` đã quyết định chạy dựa trên RAM trống, nên ghi luôn quyết định đó. `tool` cần có để một lần nâng cấp Blender/Bambu được giải thích, không bị báo thành chậm đi. `tri_count` cần có để chuẩn hóa: model lớn lên hợp lệ thì phải so theo **giây trên 100k tam giác**, không so giây thô.

Cách lấy số trên Windows như sau. Thời gian dùng `time.perf_counter()` quanh `Popen…wait()`. Đỉnh RAM tiến trình con không cần lấy mẫu dày, vì Windows tự giữ `PeakWorkingSetSize` suốt đời tiến trình ([Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters)). psutil 8 trả trường này dưới tên `memory_info().peak_rss`; tên cũ `peak_wset` vẫn chạy nhưng báo DeprecationWarning ([psutil](https://psutil.io/api/)). Phải đọc trước khi handle biến mất, nên chạy một thread ~1 Hz đọc `peak_rss` và `cpu_times()` cho tiến trình và các con. Lưu ý **`children_user/children_system` luôn bằng 0 trên Windows**, phải tự cộng các tiến trình con ([psutil](https://psutil.io/api/)). Cách chính xác hơn cho cả cây tiến trình là Job Object: `PeakProcessMemoryUsed`/`PeakJobMemoryUsed` được hệ thống "tracks constantly", và cùng struct đó đặt được giới hạn RAM, tức có thể thay luôn phần chặn của `memjob.py` ([Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)). Nhưng số này là commit (private bytes), không phải working set, nên phải ghi `mem_metric` để không so lẫn. Blender `-b` và Bambu CLI có sinh tiến trình con hay không thì chưa kiểm (TODO), và điều đó quyết định có cần Job Object không. hyperfine không đo được RAM trên Windows ([hyperfine](https://github.com/sharkdp/hyperfine)), nên chỉ dùng nó cho A/B có chủ đích.

Riêng bước cắt lớp gần như miễn phí: CLI tự ghi `result.json` vào `outputdir`, có `times` cấp tác vụ (`import_time`, `prepare_time`, `export_time`, `export_3mf_time`…), `peak_rss_mb`, và `sliced_plates[]` với `sliced_time`, `sliced_time_with_cache` cùng thời gian từng giai đoạn (`make_perimeters_time`, `infill_time`, `export_gcode_time`…) ([BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)). Mẫu thật trên máy (2816 tam giác) cho `prepare_time` 660, `sliced_time` 1290, `sliced_time_with_cache` 207, `peak_rss_mb` 103,1 [máy]. Đơn vị gần như chắc là ms, vì mã dùng đồng hồ monotonic tính ms, nhưng chưa xác nhận cho từng trường. Ý nghĩa chính xác của `sliced_time_with_cache` cũng chưa xác nhận (TODO). `slice.py` chỉ cần chép các trường này vào `detail`.

## Cảnh báo chậm đi bằng median + MAD, xác nhận bằng change-point

MongoDB từng báo động khi thời gian chênh hơn 10 % giữa hai phiên bản. Kết quả: cách này "missed small regressions", báo nhầm nhiều trên test nhiễu, và đôi khi báo đúng nhưng sai thời điểm. Chỉnh ngưỡng riêng từng test cũng không khắc phục được. Họ chuyển sang câu hỏi "thay đổi nào làm đổi hiệu năng?" và dùng change-point detection (E-Divisive) trên cả lịch sử ([MongoDB](https://www.mongodb.com/blog/post/using-change-point-detection-find-performance-regressions); [ICPE 2020](https://research.spec.org/icpe_proceedings/2020/proceedings/p67.pdf)). Hunter cải tiến bằng cách thay phép kiểm hoán vị ngẫu nhiên bằng t-test để kết quả tất định ([arXiv 2301.03034](https://arxiv.org/abs/2301.03034)). asv mô hình dữ liệu là "piecewise constant plus random noise" với khớp L1 (median có trọng số), nên chịu được điểm ngoại lai ([asv](https://asv.readthedocs.io/en/stable/step_detection.html)).

Với một người dùng, cách gọn là kết hợp hai tầng. **Tầng 1, mỗi lần chạy:** với mỗi nhóm (`step`, `mode`, `cache`, `parallelism`), lấy ~20 bản ghi gần nhất, tính median và MAD. Báo WARN nếu `duration_s > median + max(k·1.4826·MAD, abs_floor, rel_floor·median)` và vượt **2 lần liên tiếp**. **Tầng 2, hằng ngày hoặc khi cần:** chạy `ruptures` (PELT) hoặc Hunter/Apache Otava trên từng chuỗi bước, báo commit tại điểm gãy kèm median trước/sau, đúng vòng phân loại của MongoDB. WARN ở tầng 1 chỉ để thông tin, **không chặn gate**. Chỉ khi tầng 2 xác nhận một dịch chuyển kéo dài mới đáng xử lý.

| Tín hiệu | Ngưỡng ban đầu | Loại số |
|---|---|---|
| Thời gian bước (cùng nhóm) | k = 3,5; abs_floor 1 s; rel_floor 15 %; 2 lần liên tiếp | [chọn] |
| Cả vòng `run_v3.py --slice`, hình không đổi | > 45 s (mốc 30 s × 1,5) | mốc [máy], hệ số [chọn] |
| Tỉ lệ cache hit của vòng không đổi hình | < 100 % cho bước xuất; < 80 % số bàn cho cắt lớp | [chọn]; vì bàn B đôi khi trượt [máy] |
| Đỉnh RAM một tiến trình | > (RAM trống lúc bắt đầu − 3 GB) | quy tắc `memjob.py` của xưởng |
| `tri_count` một part | > 200k thì nhắc decimate | quy tắc sẵn có của xưởng |
| CPU-s tăng mà wall-time phẳng | > 20 % so với median | [chọn]; nghĩa là việc thật đã tăng |

Tỉ lệ cache hit là tín hiệu riêng: hit rate tụt là chậm đi thật, kể cả khi thời gian từng bước vẫn phẳng. Khi cần so A/B có chủ đích (ví dụ thử `--skip-useless-pick`), dùng hyperfine với `--warmup 1`. Mặc định hyperfine chạy ≥ 10 lần ([hyperfine](https://github.com/sharkdp/hyperfine)), nhưng với bước dài vài chục giây thì đặt `-r 3..5` và chấp nhận sai số rộng hơn. Không có nguồn nào cho số lần lặp đã kiểm chứng cho bước CAD/slicer nhiều phút.

## Profiling bên trong bước: timer tự đặt cho Blender, profiler có sẵn cho SolidCraft và Bambu

Khi tầng 2 chỉ ra một bước chậm đi, câu hỏi tiếp theo là thời gian đi đâu bên trong bước đó. Mỗi công cụ có một cách khác nhau.

**Blender 5.2.2.** Blender nhúng Python 3.13.13 [máy], nên chưa có `profiling.sampling`/`profiling.tracing`, vốn chỉ có từ Python 3.15 ([Python docs](https://docs.python.org/3/library/profile.html)). Nặng hơn thế, cProfile **bỏ sót hoàn toàn** thời gian trong lời gọi C của bpy. Thử trên máy: `primitive_uv_sphere_add(512×256)` mất 21 797 ms theo `perf_counter` nhưng cProfile chỉ báo tổng 0,0748 s. Ba boolean cộng `depsgraph.update()` bị báo "0.000 seconds" [máy]. Nguyên nhân chưa rõ (TODO). Vì vậy cách đáng tin là một context manager `span(name, **args)` ghi sự kiện Chrome trace `X` quanh từng part và từng boolean. Phải **ép đánh giá ngay trong khối đo** (`depsgraph.update()` hoặc `evaluated_get().to_mesh()`), vì modifier đánh giá lười, không ép thì thời gian sẽ "rơi" sang bước export. Đối chứng bằng `--debug-depsgraph-time`: dòng "updated in 0,049192 s" khớp timer tự đặt (49,5 ms) [máy], nhưng cờ này chỉ cho tổng mỗi lần update, không tách theo object. Cùng ca đó, EXACT mất 49,5 ms, MANIFOLD 6,8 ms, FLOAT 3,2 ms [máy, một mẫu nhỏ]. Muốn so sánh khử nhiễu thì dùng `--debug-depsgraph-no-threads`. cProfile vẫn hữu ích cho phần Python thuần (numpy, vòng bmesh, `meshhash.py`), miễn là code nằm trong hàm. `py-spy --native` hỗ trợ x86-64 Windows ([py-spy](https://github.com/benfred/py-spy)) và là ứng viên duy nhất để thấy stack C của Blender mà không cần build debug, nhưng chưa ai kiểm trên `blender.exe` (TODO). py-spy, pyinstrument và psutil hiện chưa cài, và Python của Blender không có psutil [máy].

**Bộ nhớ trong Blender.** `tracemalloc` báo 19 KB trong khi đỉnh thật là 316 MB [máy], nên vô dụng ở đây. Đọc `GetProcessMemoryInfo` qua ctypes (PeakWorkingSetSize 316 MB, PeakPagefileUsage 389 MB) [máy]. Bẫy cần nhớ: phải đặt `GetProcessMemoryInfo.argtypes = [HANDLE, c_void_p, DWORD]` và `GetCurrentProcess.restype = HANDLE`, không thì lỗi `OverflowError` vì pseudo-handle −1 [máy]. Ghi giá trị sau mỗi part thành sự kiện counter `C`. Vì peak chỉ tăng chứ không giảm, part gây tăng RAM là part làm peak nhảy lên.

**SolidCraft.** Đây là công cụ dễ nhất. `solidcraft-cli run … --timings` cho ms từng lệnh. `--profile` tách `boolean_ms/tessellate_ms/other_ms` và in bảng span (count, total, self, longest) ra stderr. `--profile-out trace.json` ghi Chrome trace mở được trong Perfetto. `SOLIDCRAFT_PROFILE=1` bật cho mọi lệnh. `bench-open --ops` đo từng lệnh cùng chi phí evaluate kéo theo [máy, `--help`]. Ý nghĩa "self/longest" mới suy theo tên, chưa có tài liệu.

**Bambu CLI.** CLI không xuất trace, nhưng `result.json` đã tách sẵn giai đoạn. Chuyển các trường `*_time` thành chuỗi sự kiện `X` nối tiếp nhau để đặt lên cùng timeline. Vị trí trên timeline chỉ là xấp xỉ, vì không có timestamp thật. Với chi tiết nhỏ, mẫu thật cho thấy make_perimeters, export_gcode và slice_layers là các giai đoạn lớn nhất [máy].

**Gộp và xem.** Mỗi tiến trình ghi `trace-<step>.json`, với `ts`/`dur` tính bằng µs. Script điều phối truyền mốc `T0` chung qua biến môi trường để các file ghép được lên một trục thời gian. Mỗi worker song song dùng một `tid` riêng, vì Perfetto đòi sự kiện trên cùng track phải lồng nhau đúng, sự kiện chồng lấn bị đẩy sang overflow track. Perfetto mở được một file .zip chứa nhiều trace và gộp chúng lên **một timeline** ([Perfetto](https://perfetto.dev/docs/getting-started/other-formats)). Flame graph mẫu từ py-spy/pyinstrument thì xem bằng speedscope chạy offline, không upload ([speedscope](https://github.com/jlfwong/speedscope)). Chỉ giữ ~5 trace gần nhất, theo cách giữ file của Bazel. Biểu đồ xu hướng (mỗi bước một ô, dải median ± 3·MAD, tô màu theo hit/miss, vạch dọc tại change-point ghi short commit) xuất ra PNG để duyệt bằng ảnh, đúng quy ước của xưởng, hoặc đưa vào một trang Toolhub.

## Chỉ số dự án: số vòng in tới khi lắp đạt quan trọng hơn mọi giây tiết kiệm

Tối ưu 120 s xuống 30 s tiết kiệm 1,5 phút mỗi vòng máy tính. Một lần in lại vì khe sai tốn hàng giờ máy, vài chục gram nhựa và một lượt lắp của Tuan. Không có framework công bố riêng cho studio in 3D nhỏ, nhưng DORA chuyển được sang phần cứng. DORA hiện có 5 chỉ số, chia hai nhóm throughput (lead time, tần suất, thời gian phục hồi) và instability (change fail rate, rework rate) ([DORA](https://dora.dev/guides/dora-metrics/)). Thoughtworks đã áp dụng cho ô tô bằng cách đổi "deploy" thành "kiểm chứng trong môi trường tốt nhất hiện có", trên một thang từ phần mềm/emulator tới xe thật ([Thoughtworks](https://www.thoughtworks.com/insights/blog/agile-engineering-practices/4-key-metrics-automotive)). Thang tương ứng của STLab là: `check.py` → slice thật → mẫu thử nhỏ (chỉ chỗ lắp) → bộ in đủ → lắp thật/học sinh dùng. Mục tiêu là **đẩy phát hiện lỗi về tầng trái**. Quy tắc "mẫu thử nhỏ gọn" của xưởng chính là giảm batch size theo Reinertsen: cân bằng giữa chi phí phản hồi chậm và chi phí chuẩn bị mỗi batch ([InformIT](https://www.informit.com/articles/article.aspx?p=2928185&seqNum=6)).

| Chỉ số | Định nghĩa | Nguồn dữ liệu | Cặp đối trọng (chống Goodhart) |
|---|---|---|---|
| Edit-to-feedback time | median giây từ lúc chạy `run_v3.py` tới khi có gate/ảnh | tự động, `runs.jsonl` | gate escape rate |
| Iterations to good fit | số lần in vật lý (theo bộ/part) tới lần lắp đạt | `prints.jsonl` | cost per iteration |
| First-print success rate | % part đạt ngay lần in đầu, **chỉ tính lỗi thiết kế** | `prints.jsonl` | — |
| Gate escape rate | % lần in hỏng do thiết kế mà gate đã PASS | `prints.jsonl` × `runs.jsonl` theo `git_commit` | gate pass rate |
| Rework cause Pareto | đếm `cause` mỗi tháng | `prints.jsonl` | — |
| Fit hit rate | % khe đạt "fit" lần đầu theo loại khớp | `prints.jsonl` (từng khe) | — |
| Cost per iteration | Σ gram × giá/g + giờ in × chi phí giờ máy | `slice_info.config` | lỗi `design-strength` |
| Assembly simplicity | `part_count`, `fastener_count`, `fastener_types`, `plates_with_support` (mục tiêu 0), `dfa_ratio` | BOM + slice | `plates_with_support`, quy tắc hạn chế AMS |

Phần lớn số model là tự động và rẻ. File .gcode.3mf của Bambu có `Metadata/slice_info.config`, trong đó mỗi bàn có `prediction` (giây in), `weight` (gram) và `support_used` (bool) ([Printago](https://printago.io/blog/3mf-file-format)). Đọc file này đáng tin hơn regex log của CLI, vì có báo lỗi preset ngoài bị bỏ qua cho ra `total_used_g: 0.0` ([Bambu forum](https://forum.bambulab.com/t/cli-cannot-apply-external-presets/197842)). Cách tính chi phí theo SimplyPrint: khối lượng nhựa × giá/g cộng các dòng điện, nhân công, khấu hao ([SimplyPrint](https://simplyprint.io/features/statistics.md)). Giá điện/khấu hao của STLab chưa có (TODO), nên trước mắt chỉ đo gram và giờ. DFA theo Boothroyd-Dewhurst dùng `Em = 3·Nm/Tm`. Một part được tính vào Nm chỉ khi nó chuyển động tương đối, cần vật liệu khác, hoặc phải tách để lắp các part khác ([Altium](https://resources.altium.com/p/design-manufacturing-and-assembly-dfma-or-predictive-engineering)). Vì hiếm khi có thời gian lắp thật, đề xuất bản đơn giản `dfa_ratio = Nm/part_count`, với Nm do người thiết kế gắn cờ từng part [chọn].

Phần ghi tay chính là thứ phần mềm farm không có. SimplyPrint/3DPrintForge chỉ phân loại succeeded/cancelled/failed/printer error ([SimplyPrint](https://simplyprint.io/features/statistics); [3DPrintForge](https://skynett81.github.io/3dprintforge/en/analytics/statistics)). Studio thiết kế cần thêm **kết quả từng khe** và **nguyên nhân là thiết kế hay máy**. Đề xuất `prints.jsonl`, mỗi lần in một dòng, kèm mảng khe:

```json
{"ts":"2026-11-28T15:40+07:00","project":"english-teacher","print_set":"print-v3.3mf","plate":"B","git_commit":"b52393b",
 "gate_run_id":"20261128-0812-a3f","result":"fail","cause":"design-fit","machine":"A1","filament":"Bambu PETG Basic",
 "print_time_h":2.4,"filament_g":38.5,"reprint_of":null,"photo":"maker/english-teacher/print/photos/…jpg",
 "fits":[{"part_pair":"shell-front/tray","feature_id":"m2.5-boss-1","nominal_mm":2.5,"clearance_mm":0.2,"orientation":"Z","result":"tight","note":"vít vào cứng"}]}
```

`cause` dùng danh mục cố định: `design-fit`, `design-strength`, `design-printability`, `design-assembly`, `machine`, `material`, `operator`. Dữ liệu `fits` tích lũy dần sẽ thay số mặc định trong fit-library bằng số thật của máy A1 + PETG. Các nguồn tham chiếu chỉ cho khoảng chung: khe 0,15–0,2 mm phổ biến cho lắp vừa, press-fit 0 mm vẫn có thể quá chặt ([All3DP](https://all3dp.com/2/3d-printing-tolerances-test-fdm/)). Nguồn đó cũng nhất quán với quy tắc +0,2 mm của xưởng. Gate escape rate là chỉ số "độ tin của gate". Đúng như ghi nhận ngày 2026-11-27 (bụng STLAB của Cú Bông lỗi lắp dù đã qua gate): mỗi escape phải dẫn tới một kiểm tra mới trong gate, rồi xem escape rate tháng sau có giảm không. Không có benchmark ngành cho FPY hay số vòng lặp của studio nhỏ, và con số 98,8 % thành công lưu hành trên mạng không có nguồn. Vì vậy chỉ so mỗi dự án với chính nó theo thời gian, đúng khuyến cáo của DORA ([DORA](https://dora.dev/guides/dora-metrics/)). Mọi chỉ số đều có cặp đối trọng, vì "when a measure becomes a target, it ceases to be a good measure" ([Goodhart](https://www.wikipedia.org/wiki/Goodhart%27s_law)). Tối ưu gate pass rate thì gate bị nới. Tối ưu gram nhựa thì vách mỏng dễ gãy. Tối ưu part_count thì sinh ra part cần support hoặc phải in nhiều màu trên AMS.

## Thứ tự làm theo lợi ích/công sức

| # | Việc | Lợi ích | Công sức | Ghi chú |
|---|---|---|---|---|
| 1 | Wrapper bước trong `run_v3.py` ghi `runs.jsonl` (thời gian, exit, cache, mode, commit, tải máy, tri_count) | Có lịch sử; mọi việc sau dựa vào đây | Thấp (~50 dòng) | Mang theo `parallelism`, `tool` |
| 2 | `slice.py` chép `result.json` (times, sliced_plates, peak_rss_mb) + `slice_info.config` (prediction, weight, support_used) vào `detail` | Profile cắt lớp và chi phí in miễn phí | Thấp | Mỗi bàn đã có outputdir riêng |
| 3 | `prints.jsonl` + lệnh nhỏ ghi kết quả in/lắp (có `fits`, `cause`, `gate_run_id`) | Mở khóa toàn bộ chỉ số cấp dự án | Thấp (kỷ luật ghi là phần khó) | Có thể là form trên Toolhub |
| 4 | Guard median + MAD, 2 lần liên tiếp, cảnh báo cache hit rate | Phát hiện chậm đi ngay khi chạy | Thấp | Ngưỡng [chọn], chỉnh sau ~2 tuần dữ liệu |
| 5 | `span()` + ép đánh giá trong script Blender; ctypes đọc peak RAM sau mỗi part | Biết part/boolean nào tốn | Thấp–vừa | Không dựa cProfile cho bpy |
| 6 | Bật `--profile-out` SolidCraft ở `--release`; gộp trace .zip mở Perfetto | Timeline cả chuỗi | Thấp | Giữ 5 trace gần nhất |
| 7 | Báo cáo tháng: biểu đồ xu hướng PNG + change-point (`ruptures`/Hunter) + Pareto `cause` | Quyết định cải tiến có căn cứ | Vừa | Thêm `ruptures` vào môi trường Python ngoài Blender |
| 8 | Job Object thay polling + thay phần chặn RAM của `memjob.py` | Đỉnh RAM cả cây, giới hạn cứng | Vừa | Chỉ cần nếu Blender/Bambu sinh tiến trình con (TODO) |
| 9 | Thử `py-spy record --native` trên `blender.exe` | Thấy stack C khi timer chưa đủ | Thấp (thử) | Chưa kiểm, có thể cần quyền admin |

Thứ tự đề xuất là 1 → 2 → 3 → 4, đủ cho cả ba câu hỏi ở mức thô trong một buổi làm. 5–6 làm khi tầng cảnh báo chỉ ra bước cần đào sâu. 7 làm khi đã có khoảng một tháng dữ liệu. Theo quy trình của xưởng, việc code sẽ viết spec + gate rồi giao qua `delegate.py`.

## Kết luận

Thứ thay đổi khi nhìn kỹ là **đơn vị cải tiến**. Sau đợt tăng tốc, 30 s mỗi vòng máy tính đã nhỏ so với một vòng in thử vật lý. Vì vậy giá trị lớn nhất của hệ đo không nằm ở việc cắt thêm giây, mà ở việc nối `runs.jsonl` với `prints.jsonl` qua `git_commit`. Chỉ khi nối được hai file, xưởng mới thấy gate nào để lọt lỗi gì, khe nào trên A1 + PETG thật sự cần +0,2 mm hay hơn. Khi đó mỗi lần in hỏng trở thành một kiểm tra mới trong gate hoặc một dòng mới trong fit-library. Với phần hiệu năng, cái bẫy cần tránh là tin công cụ "tự nhiên" như cProfile hay ngưỡng % so với lần trước. Cả hai đều đã được chứng minh là sai ở đây (cProfile mù với bpy) hoặc ở nơi khác (MongoDB). Tỉ lệ cache hit, chứ không phải thời gian thô, là chỉ báo sớm nhất cho việc chuỗi 30 s đang trượt về lại 120 s.

## Kết quả áp dụng (2026-11-27 tối → 2026-11-28)

| # | Việc | Trạng thái |
|---|---|---|
| 1 | `tools/metrics/runlog.py` + `run_v3.py` ghi `cad/metrics/runs.jsonl` | XONG (032b74e) |
| 2 | `slice.py` chép `result.json` vào mục `perf` từng bàn (RAM đỉnh, `sliced_time`, các giai đoạn ms, số tam giác); `run_v3.py` ghi từng bàn (cache, RAM, ms cắt, giờ in, gam, support) vào `runs.jsonl` | XONG 2026-11-28 |
| 3 | `tools/metrics/printlog.py` → `prints.jsonl` + `--report` | XONG (032b74e) |
| 4 | Cảnh báo trung vị + MAD, 2 lần liên tiếp | XONG (032b74e) |
| 5–9 | span Blender, trace SolidCraft, báo cáo tháng, Job Object, py-spy | CHỜ – làm khi cảnh báo chỉ ra bước cần đào sâu / đủ ~1 tháng dữ liệu |

Ghi chú đo [máy]: bàn trúng cache giữ số `perf` của lần cắt thật gần nhất (cờ `cache: true` để không lẫn). Lần chạy đầu sau khi bật máy
chậm ~2× mọi bước (cắt lớp trúng cache 35 s so với 6 s khi chạy lại ngay) – lý do để cảnh báo cần 2 lần liên tiếp.
