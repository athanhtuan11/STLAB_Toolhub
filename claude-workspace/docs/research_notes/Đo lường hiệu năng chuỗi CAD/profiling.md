# Profiling: tìm thời gian đi đâu trong từng bước chuỗi CAD (Blender headless, Python/numpy, SolidCraft CLI, Bambu Studio CLI)

Ghi chú nghiên cứu 2026-11-27. Máy kiểm thực tế: Windows 11 Pro, Blender 5.2.2 LTS (Python 3.13.13 nhúng, `python313.dll`), SolidCraft `C:\Program Files\SolidCraft\solidcraft-cli.exe`. Mục đánh dấu **[Thử trên máy]** là kết quả chạy thật trong phiên này (script ở scratchpad), không phải từ tài liệu.

## 1. Profiling Python bên trong Blender (cProfile, py-spy, pyinstrument, cờ debug của Blender)

### Takeaway
Trong Blender 5.2, cProfile **không thấy** thời gian nằm trong lời gọi C của bpy (bpy.ops, depsgraph update): một operator chạy 21,8 s mà cProfile chỉ ghi tổng 0,075 s. Muốn quy thời gian cho từng boolean/từng part thì dùng timer `time.perf_counter()` tự đặt quanh từng thao tác, cộng `--debug-depsgraph-time` để thấy thời gian đánh giá modifier. Dùng cProfile/pyinstrument chỉ cho phần Python thuần (numpy, bmesh loop, logic script). py-spy với `--native` là ứng viên để nhìn vào phần C nhưng chưa ai kiểm trên blender.exe.

### Cited Findings
**cProfile / profiling.tracing**
- Python 3.15 đổi tên: `profile` bị deprecate từ 3.15 (gỡ ở 3.17). `cProfile` vẫn là alias tương thích ngược của `profiling.tracing`. Bộ lấy mẫu thống kê mới là `profiling.sampling`. Tài liệu khuyên dùng `profiling.sampling` khi debug production và `profiling.tracing` khi dev/test — [Python docs: profile](https://docs.python.org/3/library/profile.html)
- Profiling deterministic theo dõi mọi sự kiện call/return/exception và đo khoảng giữa chúng. Profiling thống kê lấy mẫu instruction pointer: overhead thấp hơn nhưng chỉ cho thấy tỉ lệ tương đối — [Python docs](https://docs.python.org/3/library/profile.html)
- `Profile()` dùng được làm context manager từ Python 3.8. Có `enable()/disable()`, `dump_stats(file)`, `create_stats()`. Từ 3.13 `print_stats` nhận một tuple khóa sort để sort nhiều cấp — [Python docs](https://docs.python.org/3/library/profile.html)
- Giới hạn độ chính xác: tài liệu nói đồng hồ bên dưới nhảy khoảng 0,001 s. Độ trễ dispatch giữa sự kiện và lúc đọc timer cộng dồn ở các hàm gọi nhiều lần — [Python docs](https://docs.python.org/3/library/profile.html)
- Blender wiki hướng dẫn profile bằng cProfile có sẵn: `cProfile.run("import bpy; bpy.utils.load_scripts()", "blender.prof")`, rồi đọc kết quả bằng `pstats` — [Blender wiki: Profiling Python Code](https://wiki.blender.org/wiki/Tools/python_profile/)
- **[Thử trên máy]** Blender 5.2.2 nhúng Python 3.13.13 (MSC v.1944, 64 bit). Nghĩa là **chưa có** `profiling.sampling`/`profiling.tracing` (chỉ có từ 3.15). Dùng `cProfile` như cũ.
- **[Thử trên máy]** Trong Blender 5.2.2 headless: `cProfile` bật quanh `busy(); bpy.ops.mesh.primitive_uv_sphere_add(segments=512, ring_count=256); busy()`. Operator mất 21 797 ms theo `perf_counter`, nhưng `pstats.total_tt` chỉ 0,0748 s, gần bằng lần chạy không có operator (0,0757 s). Lần thử khác: thêm 3 boolean modifier rồi `depsgraph.update()` + `to_mesh()` (EXACT 49,5 ms) ở cấp module, cProfile báo "31 function calls in 0.000 seconds" và không có dòng nào cho các lời gọi đó. Kết luận thực nghiệm: thời gian trong bpy.ops / RNA C call bị **mất khỏi** báo cáo cProfile. Chưa rõ nguyên nhân (TODO).

**py-spy**
- Chạy được trên Linux, macOS, Windows, FreeBSD. Chế độ `--native` (profile cả phần mở rộng C/C++/Cython) có cho x86-64 trên Linux và **Windows**. Không hỗ trợ Windows 32 bit — [py-spy README](https://github.com/benfred/py-spy)
- Lệnh: `record` (mặc định ra SVG flame graph, `--format` speedscope/raw), `top` (xem trực tiếp), `dump` (stack từng thread, `--locals`). Cờ: `--subprocesses` (gồm process Python con), `--idle`, `--gil`, `--nonblocking` (không dừng chương trình đích, đổi lại thỉnh thoảng lấy mẫu sai) — [py-spy README](https://github.com/benfred/py-spy)
- Viết bằng Rust, chạy ngoài process đích, đọc bộ nhớ bằng `ReadProcessMemory` trên Windows. Tác giả nói "extremely low overhead". Mặc định có tạm dừng process khi lấy mẫu. Hỗ trợ CPython 2.3–2.7 và 3.3–3.15 — [py-spy README](https://github.com/benfred/py-spy)
- Mẫu chạy: `py-spy record -o profile.svg -- python myprogram.py` — [py-spy README qua tìm kiếm](https://raw.githubusercontent.com/benfred/py-spy/master/README.md)
- Không tìm thấy hướng dẫn nào đã kiểm py-spy trên blender.exe. Lệnh suy ra `py-spy record -- blender.exe -b --python x.py` là **chưa kiểm** — [kết quả tìm kiếm, không có nguồn Blender riêng](https://wiki.blender.org/wiki/Tools/python_profile/)
- **[Thử trên máy]** py-spy, pyinstrument, snakeviz, psutil đều **chưa cài** (không có trên PATH, Python của Blender không có `psutil`).

**pyinstrument (5.1.3)**
- Profiler lấy mẫu. Dùng được theo 3 cách: `Profiler().start()/stop()`, context manager `with pyinstrument.profile():`, decorator `@pyinstrument.profile()`. Khoảng lấy mẫu mặc định 0,001 s; khoảng nhỏ hơn thì overhead tăng — [pyinstrument guide](https://pyinstrument.readthedocs.io/en/latest/guide.html)
- Renderer: text (mặc định), html (`write_html`, `open_in_browser`), json, **speedscope**, pstats. `-o OUTFILE` tự suy định dạng từ đuôi file. `--timeline` giữ thứ tự gọi và không gộp các lần gọi lặp — [pyinstrument guide](https://pyinstrument.readthedocs.io/en/latest/guide.html)

**Cờ debug/timing của Blender** (**[Thử trên máy]**, `blender.exe --help`, 5.2.2)
- `--debug-depsgraph-time`: "Enable debug messages from dependency graph related on timing". Đầu ra thật: mỗi lần update in `Depsgraph built in X seconds.` và `Depsgraph [Scene :: ViewLayer] updated in X seconds.`. Lần update có boolean EXACT in 0,049192 s, khớp với timer tự đặt (49,5 ms). MANIFOLD 0,006480 s, FLOAT 0,002973 s. Chỉ có **tổng mỗi lần update**, không tách theo object/modifier.
- Các cờ khác: `--debug-depsgraph-eval`, `--debug-depsgraph-build`, `--debug-depsgraph-tag`, `--debug-depsgraph`, `--debug-depsgraph-pretty`, `--debug-depsgraph-uid`, `--debug-depsgraph-no-threads` (ép đánh giá đơn luồng, giúp so sánh/khử nhiễu), `--debug-jobs` ("time profiling for background jobs"), `--debug-python`, `--debug-memory` (cấp phát có guard đầy đủ, chậm), `--debug-io`, `--debug-all`, `-t/--threads N`.
- Logging: `--log "<category>"` (ví dụ `"*mesh*"`), `--log-level debug|trace`, `--log-show-memory` ("Show memory usage for each log message"), `--log-file`, `--log-list-categories`.
- `--profile-gpu`: "Enable CPU & GPU performance profiling for GPU debug groups (Outputs a profile.json file in the Trace Event Format)". Chỉ dành cho nhóm GPU debug, không giúp gì cho boolean chạy headless.
- Đối chiếu solver trên cùng một ca (cầu UV 64×32 trừ khối lập phương): EXACT 49,5 ms, MANIFOLD 6,8 ms, FLOAT 3,2 ms, cả 3 ra 1749 mặt. Chỉ là một mẫu nhỏ, không phải benchmark.

### Inferences
- Cách quy thời gian theo từng boolean hoặc từng part đáng tin nhất trong Blender: timer tự đặt quanh `depsgraph.update()` / `evaluated_get().to_mesh()` / `bpy.ops.*`, rồi so với dòng `--debug-depsgraph-time`. Modifier được đánh giá lười, nên phải ép đánh giá ngay trong khối đo, nếu không thời gian sẽ "rơi" vào lần export sau đó.
- cProfile vẫn có ích cho phần Python thuần trong script. Nên bọc code vào hàm: code ở cấp module không có frame hàm nên tổng có thể ra 0.
- py-spy `--native` trên Windows có thể là cách duy nhất để thấy stack C của Blender mà không cần build debug. Cần thử thật trước khi khuyến nghị (TODO).
- Cầu 512×256 tạo bằng bpy.ops mất 21,8 s ở chế độ nền là bất thường. Đáng đo riêng: tạo mesh bằng bmesh/`from_pydata` có thể nhanh hơn nhiều (chưa kiểm).

### Gaps
- Chưa có nguồn chính thức giải thích vì sao cProfile bỏ sót thời gian bpy.ops (có thể liên quan sys.monitoring của Python 3.12+ hoặc cách Blender gọi operator). Chưa kiểm.
- Chưa kiểm py-spy/pyinstrument chạy trong blender.exe (attach theo PID hay launch). Chưa rõ py-spy trên Windows có cần quyền admin khi attach không: README không nói.
- Trang manual Blender (docs.blender.org) trả 403 khi fetch, nên danh sách cờ lấy từ `--help` bản 5.2.2 cài trên máy.
- line_profiler: không đủ tool call để tra nguồn. Không đưa thông số.

## 2. Đo thủ công nhẹ: context manager theo part/op ghi Chrome trace

### Takeaway
Chrome Trace Event Format (JSON) là định dạng chung để gộp mọi bước: Perfetto và speedscope đều đọc được, và SolidCraft xuất sẵn định dạng này. Một context manager ~15 dòng ghi sự kiện `X` (ts/dur tính bằng µs, pid/tid) cho từng part và từng boolean là đủ. Overhead chỉ là hai lần gọi `perf_counter` cộng một lần append, rất nhỏ so với thao tác hình học tính bằng ms.

### Cited Findings
- Perfetto đọc JSON Trace Event: `B`/`E` và `X` hiển thị thành slice, `I` (instant) thành điểm, `C` (counter) thành track bộ đếm, `M` (metadata) để đặt tên process/thread, `s/t/f` là mũi tên flow. `ts` tính bằng **micro giây**. `pid`/`tid` quyết định sự kiện nằm trên track nào — [Perfetto: other formats](https://perfetto.dev/docs/getting-started/other-formats)
- Sự kiện duration phải **lồng nhau đúng**. Sự kiện chồng lấn mà không lồng bị đẩy sang overflow track. Muốn chồng lấn thì dùng async event — [Perfetto](https://perfetto.dev/docs/getting-started/other-formats)
- Perfetto theo đặc tả Trace Event Format, không theo các "quirk" của `chrome://tracing` cũ — [Perfetto](https://perfetto.dev/docs/getting-started/other-formats)
- speedscope chỉ hỗ trợ một tập con Trace Event: `B`, `E`, `X`, cộng `M` để đặt tên process/thread — [speedscope wiki: custom sources](https://github.com/jlfwong/speedscope/wiki/Importing-from-custom-sources)
- Bản thân Blender có một đường xuất Trace Event (`--profile-gpu` → `profile.json`), nhưng chỉ cho nhóm GPU debug — **[Thử trên máy]** `blender --help`
- `time.perf_counter()` trên máy này đo nhất quán với `--debug-depsgraph-time` (49,5 ms so với 49,192 ms) — **[Thử trên máy]**

Mẫu (tự viết, không lấy từ nguồn nào), dùng cho cả Blender lẫn Python thuần:
```python
import json, os, time, threading, contextlib
_EV = []; _PID = os.getpid(); _T0 = time.perf_counter_ns()
@contextlib.contextmanager
def span(name, **args):
    t = time.perf_counter_ns()
    try: yield
    finally:
        _EV.append({"name": name, "ph": "X", "pid": _PID, "tid": threading.get_ident(),
                    "ts": (t - _T0) / 1000, "dur": (time.perf_counter_ns() - t) / 1000, "args": args})
def dump(path, proc_name):
    _EV.append({"name": "process_name", "ph": "M", "pid": _PID, "args": {"name": proc_name}})
    json.dump({"traceEvents": _EV}, open(path, "w"))
# with span("part:shell"): with span("bool:diff", solver="EXACT"): dg.update()
```

### Inferences
- `ts` của từng process tính từ `_T0` riêng. Muốn gộp nhiều process lên một trục thời gian (Blender → SolidCraft → Bambu) thì dùng mốc tuyệt đối chung: `time.time_ns()` lúc bắt đầu, hoặc cho script điều phối truyền mốc T0 qua biến môi trường, rồi cộng offset khi gộp file.
- Nested `with span(...)` tự sinh cấu trúc lồng hợp lệ, vì sự kiện con luôn nằm trong khoảng của sự kiện cha.
- Đếm bộ nhớ theo thời gian dùng sự kiện `C`, ví dụ `{"ph":"C","name":"rss_mb","args":{"rss":...}}` ghi sau mỗi part.

### Gaps
- Không mở được bản gốc đặc tả Trace Event Format (Google Doc chỉ trả về tiêu đề). Các trường lấy theo mô tả của Perfetto/speedscope.
- Chưa có số đo overhead của context manager trong tài liệu. Nhận định "rất nhỏ" là suy luận.

## 3. Xem kết quả: speedscope, Perfetto/chrome://tracing, snakeviz, gộp trace nhiều process

### Takeaway
Perfetto UI (ui.perfetto.dev) là nơi xem chính cho trace dạng timeline: đọc JSON của SolidCraft và trace tự ghi, gộp nhiều trace bằng cách nén chung vào .zip. speedscope hợp để xem flame graph mẫu từ py-spy/pyinstrument (view Left Heavy/Sandwich). Cả hai chạy hoàn toàn trong trình duyệt, không upload dữ liệu.

### Cited Findings
- Perfetto: một trace archive (.zip/.tar) chứa nhiều trace, kể cả JSON, được UI và Trace Processor gộp lên **một timeline** — [Perfetto](https://perfetto.dev/docs/getting-started/other-formats)
- Perfetto còn mở được: Firefox Profiler JSON (sinh từ perf, simpleperf, samply hoặc `profiling.sampling` của Python), pprof, `perf script`, collapsed stack, Ninja log, macOS Instruments XML… — [Perfetto](https://perfetto.dev/docs/getting-started/other-formats)
- speedscope nhập được py-spy, pyspeedscope, Austin, pyinstrument, Chrome, pprof, perf… README **không** nhắc cProfile/pstats — [speedscope README](https://github.com/jlfwong/speedscope)
- speedscope chạy offline: `npm install -g speedscope` rồi `speedscope file`, hoặc tải bản release và mở `index.html`. Profile không bị upload — [speedscope README](https://github.com/jlfwong/speedscope)
- Các view của speedscope: Time Order (theo thứ tự thời gian), Left Heavy (gộp stack giống nhau, nặng nhất bên trái, để tìm chỗ tốn thời gian), Sandwich (bảng self/total time từng hàm, kèm flame graph caller/callee) — [speedscope README](https://github.com/jlfwong/speedscope)
- Định dạng collapsed stack của Brendan Gregg (mỗi dòng: frame cách nhau bằng `;` rồi đến trọng số) được cả speedscope lẫn Perfetto đọc — [speedscope wiki](https://github.com/jlfwong/speedscope/wiki/Importing-from-custom-sources); [Perfetto](https://perfetto.dev/docs/getting-started/other-formats)

### Inferences
- Quy trình gợi ý: mỗi bước ghi `trace-<step>.json` → gộp bằng zip hoặc bằng script nối `traceEvents` (sau khi cộng offset) → mở trên ui.perfetto.dev. Bambu Studio không xuất trace, nên chuyển `result.json` thành sự kiện `X` tổng hợp (xem mục 4).
- Muốn xem file pstats từ cProfile thì dùng pyinstrument renderer `pstats`, hoặc snakeviz (chưa tra nguồn snakeviz, xem Gaps).

### Gaps
- snakeviz: không tra được nguồn trong giới hạn tool call. Không đưa thông số.
- Không có nguồn về giới hạn dung lượng file trace của Perfetto/speedscope.

## 4. Đọc trường thời gian trong result.json của Bambu Studio CLI và --profile của SolidCraft

### Takeaway
SolidCraft có sẵn profiler đầy đủ: `--timings` (ms mỗi lệnh), `--profile` (tách boolean/tessellate/other cùng bảng span ra stderr), `--profile-out` (Chrome trace). Bambu Studio `result.json` có `times` cấp tác vụ (import/prepare/export) và `sliced_plates[].times` theo từng giai đoạn cắt lớp (perimeters, infill, support, gcode export…), cộng `peak_rss_mb`. Đơn vị gần như chắc là ms, nhưng chưa xác nhận cho từng trường.

### Cited Findings
**SolidCraft** (**[Thử trên máy]** `solidcraft-cli --help`)
- `run ... [--timings] [--profile] [--profile-out trace.json]`. `--timings` in `{timings: [{index, command, ms}], total_ms}` cho một script, thêm `--results` thì in kèm kết quả.
- `--profile` thêm profile cho từng lệnh: `{boolean_ms, tessellate_ms, other_ms}` (phần của kernel). Nó còn ghi "where the time goes, SMLib's calls, kernel operations, features, commands and import stages" và in bảng ra stderr: count, total, self time, longest cho mỗi span.
- `--profile-out FILE` ghi các span thành Chrome trace "for chrome://tracing or ui.perfetto.dev". Biến môi trường `SOLIDCRAFT_PROFILE=1` bật cùng chức năng cho **mọi** lệnh.
- Cũng có trên `eval` và `bench-open` (`--ops script.json`: chạy rồi undo từng lệnh, đo lệnh, các lần evaluate nó gây ra, và phần đặt/mesh lại). `RUST_LOG=error|warn|info|debug|trace` đặt mức log.

**Bambu Studio result.json**
- File ghi trong `record_exit_reson()`: `outputdir + "/result.json"` nếu có thư mục output, không thì `result.json` ở thư mục hiện tại. Các khóa cấp trên: `times`, `peak_rss_mb`, `layer_height`, `wall_loops`, `sparse_infill_density`, `sliced_plates` — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- `times` = `prepare_time, export_time, export_3mf_time, export_slicedata_time, load_slicedata_time, import_time`, lấy từ `sliced_info_t` (kiểu `size_t`) — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- Theo từng plate: `sliced_time`, `sliced_time_with_cache`, `make_perimeters_time`, `infill_time`… Các giai đoạn tra từ `slice_stage_times` (`unordered_map<string,long long>`) theo hằng `TIME_*`, thiếu khóa thì ra 0 — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- `j["peak_rss_mb"] = Slic3r::get_peak_rss_mb();`. Hàm mốc thời gian quan sát được: `Slic3r::Utils::get_current_milliseconds_time_monotonic()` (đồng hồ monotonic tính ms) — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp)
- **[Thử trên máy]** Mẫu thật (`backup/20261113-brake-mount-v3.6/p2-switch-base/result.json`, 2816 tam giác, 1 plate):
  - Cấp tác vụ: `import_time` 14, `prepare_time` 660, `export_3mf_time` 175, `export_time` 397, `peak_rss_mb` 103,1.
  - Plate: `sliced_time` 1290, `sliced_time_with_cache` 207, `make_perimeters_time` 196, `export_gcode_time` 192, `slice_layers_time` 89, `infill_time` 78, `prepare_infill_time` 57, `toolpath_time` 52, `generate_support_material_time` 43, `infill_generate_time` 21, `skirt_brim_time` 15, `detect_overhangs_time` 14, `wall_time` 107, `wipe_tower_time` 3. Các trường support_*, ironing, flush_plan, conflict_check bằng 0.
  - Ngoài ra có `feature_type_times` (giây in dự đoán theo loại đường, **không phải** thời gian máy tính), `main_predication`/`total_predication` (thời gian in dự đoán, s), `objects[].triangle_count`, `obj_cached_cnt`.
- **[Thử trên máy]** Một `result.json` khác ở gốc workspace (lần chạy không cắt lớp) chỉ có `import_time` 169, `prepare_time` 173, `peak_rss_mb` 79,1, không có `sliced_plates`.
- OrcaSlicer: không đủ tool call để tra xem có result.json tương đương không.

### Inferences
- Đơn vị `times` gần như chắc là ms (đồng hồ ms monotonic; 14/660/1290 hợp lý cho ca nhỏ). `prepare_time` có vẻ bao cả bước chuẩn bị trước cắt lớp. Quan hệ cộng dồn giữa `prepare_time`, `sliced_time` và `export_time` chưa xác nhận.
- `sliced_time_with_cache` (207) nhỏ hơn nhiều so với `sliced_time` (1290). Có thể đây là thời gian khi tận dụng cache object (`obj_cached_cnt`), nhưng chưa xác nhận.
- Hotspot Bambu thường gặp với chi tiết nhỏ: make_perimeters + export_gcode + slice_layers. Có thể chuyển các trường này thành sự kiện `X` nối tiếp nhau để đưa vào cùng timeline Perfetto (vị trí là xấp xỉ, vì không có ts thật).

### Gaps
- Chưa thấy chỗ gán giá trị cho từng trường thời gian, cũng như cài đặt `get_peak_rss_mb()` trên Windows (Peak Working Set hay Pagefile?). Nguồn còn ~500 k ký tự chưa đọc.
- Trường `--profile` của SolidCraft không có tài liệu ngoài `--help`. Ý nghĩa chính xác của "self time" và "longest" mới suy theo tên.
- OrcaSlicer: chưa tra.

## 5. Đo bộ nhớ cho mesh lớn (tracemalloc, psutil peak) trên máy Windows ít RAM

### Takeaway
`tracemalloc` chỉ thấy bộ nhớ Python cấp phát. Trong Blender nó gần như vô dụng: 19 KB, trong khi peak thật là 316 MB. Đỉnh RAM thật của process nên đọc bằng `GetProcessMemoryInfo` (PeakWorkingSetSize / PeakPagefileUsage) qua ctypes, vì Python của Blender không có psutil. Với Python ngoài Blender thì dùng `psutil.Process().memory_info()`. Bambu đã tự báo `peak_rss_mb`.

### Cited Findings
- **[Thử trên máy]** Trong Blender 5.2.2: `tracemalloc` bật quanh tạo cầu + 3 boolean, peak báo 19 KB. Đọc `GetProcessMemoryInfo` qua ctypes thì `PeakWorkingSetSize` 316 MB, `PeakPagefileUsage` 389 MB (sau khi tạo cầu 512×256). `import psutil` lỗi `No module named 'psutil'`.
- **[Thử trên máy]** Lưu ý ctypes: phải đặt `GetProcessMemoryInfo.argtypes = [HANDLE, c_void_p, DWORD]` và `GetCurrentProcess.restype = HANDLE`. Không đặt thì báo `OverflowError: int too long to convert` vì pseudo-handle −1 trên 64 bit.
- Blender có `--log-show-memory` (in mức dùng bộ nhớ kèm mỗi dòng log) và `--debug-memory` (cấp phát có guard đầy đủ, dùng để debug chứ không để đo hiệu năng) — **[Thử trên máy]** `blender --help`
- Bambu Studio ghi `peak_rss_mb` vào result.json qua `Slic3r::get_peak_rss_mb()` — [BambuStudio.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/BambuStudio.cpp). Mẫu thật: 79–103 MB cho chi tiết nhỏ (**[Thử trên máy]**).

### Inferences
- Ghi `PeakWorkingSetSize` sau từng part (sự kiện counter `C` trong trace) sẽ chỉ ra part nào đẩy RAM lên. Peak là giá trị **đơn điệu** từ lúc process khởi động, nên muốn biết part nào gây tăng thì xem độ chênh, hoặc đọc `WorkingSetSize` hiện tại.
- Với numpy ngoài Blender, tracemalloc có thấy cấp phát mảng numpy (numpy báo cho tracemalloc). Nhận định này chưa có nguồn trong phiên, TODO kiểm.
- Kết hợp với memjob.py sẵn có (giới hạn RAM): bước lấy đỉnh RAM cho từng bước giúp đặt ngưỡng đúng.

### Gaps
- Chưa tra tài liệu tracemalloc/psutil chính thức trong phiên (giới hạn tool call). Các nhận định về tracemalloc trong Blender dựa trên thử nghiệm, không dựa trên nguồn.
- Chưa rõ `peak_rss_mb` của Bambu trên Windows đo Working Set hay Commit.
