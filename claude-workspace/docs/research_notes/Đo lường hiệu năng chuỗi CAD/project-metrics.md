# Bộ chỉ số dự án CAD cho studio maker / in 3D (ngoài tốc độ pipeline)

> Ghi chú nghiên cứu, 2026-11-27. Nguồn trích inline. Mục "Inferences" là suy luận của người nghiên cứu, không phải số liệu đã công bố. Không có benchmark ngành cho tỷ lệ in đạt lần đầu hay số vòng lặp của studio nhỏ (xem Gaps).

## 1. Chỉ số vòng lặp / quy trình (iteration, DORA chuyển sang phần cứng)

### Takeaway
DORA (5 chỉ số, chia throughput và instability) chuyển được sang phần cứng nếu đổi "deploy" thành "kiểm chứng trong môi trường tốt nhất hiện có" (gate → slice → in thử → lắp thật). Thoughtworks đã làm đúng việc này cho ô tô. Không có framework riêng công bố cho studio in 3D nhỏ; phải tự ghép từ DORA + SPACE + Reinertsen (flow, feedback nhanh, batch nhỏ).

### Cited Findings
- DORA hiện dùng 5 chỉ số. **Throughput**: change lead time (từ commit tới production), deployment frequency, failed deployment recovery time. **Instability**: change fail rate (tỷ lệ deploy cần can thiệp ngay: rollback/hotfix) và deployment rework rate (tỷ lệ deploy không kế hoạch do sự cố). MTTR đã được thay bằng failed deployment recovery time. — [DORA metrics guide](https://dora.dev/guides/dora-metrics/)
- Rework rate được thêm năm 2024; ví dụ: 10 lần deploy có 3 lần không kế hoạch → 30 %. — [IBM](https://www.ibm.com/think/topics/dora-metrics); [Steve Fenton, DEV](https://dev.to/_steve_fenton_/the-dora-4-key-metrics-become-5-1ceg). Có nguồn (Dynatrace) ghi mốc 01/2026, mâu thuẫn về ngày. — [Dynatrace](https://www.dynatrace.com/knowledge-base/dora-framework/)
- DORA cảnh báo: biến chỉ số thành chỉ tiêu (vd bắt deploy nhiều lần/ngày) sẽ bị "chơi số" (Goodhart); cần nhiều chỉ số có sức căng với nhau; chỉ so một ứng dụng với chính nó theo thời gian, không xếp hạng giữa các nhóm; làm tích hợp dữ liệu cầu kỳ có thể tốn hơn lợi, bắt đầu bằng trao đổi hoặc DORA Quick Check là đủ. — [DORA metrics guide](https://dora.dev/guides/dora-metrics/)
- Thoughtworks chuyển 4 chỉ số cho ô tô (phần cứng hạn chế): **Change lead time** = thời gian kiểm chứng thay đổi trong môi trường QA hiện có (SiL/HiL); **Deployment frequency** = tần suất kiểm chứng trong "môi trường tốt nhất hiện có gần với production"; **Change failure rate** gồm cả thất bại ở môi trường sớm; **MTTR** = tốc độ xử lý lỗi tìm thấy ở khâu sau. Thang môi trường: phần mềm/emulator → virtual ECU → board đánh giá → mockware → prototype → xe. Câu then chốt: "rapid feedback loops regardless of release cadence"; cảnh báo chỉ số cấp nhóm dễ tối ưu cục bộ. — [Thoughtworks, 4 key metrics automotive](https://www.thoughtworks.com/insights/blog/agile-engineering-practices/4-key-metrics-automotive)
- DORA 2025 (*State of AI-assisted Software Development*, ~5.000 người, 23/09/2025): ~90 % dùng AI; AI giờ gắn với throughput cao hơn; AI là "bộ khuếch đại": nhóm có kiến trúc tách rời và vòng phản hồi nhanh được lợi, nhóm chậm/gắn chặt hầu như không. — [Google blog](https://blog.google/technology/developers/dora-report-2025/); [DORA report 2025](https://dora.dev/dora-report-2025/). Nhận xét "AI cũng tăng instability" là của bài review thứ cấp, chưa xác nhận trong báo cáo. — [Splunk](https://www.splunk.com/en-us/blog/learn/state-of-devops.html)
- SPACE (Forsgren, Storey và cộng sự, 2021): năng suất không đo bằng 1 chỉ số; 5 chiều Satisfaction, Performance, Activity, Communication, Efficiency/flow; chỉ số hoạt động (số commit, dòng code) là tín hiệu yếu nếu đứng một mình; khuyến nghị dùng ≥3 chiều. — [ACM Queue](https://queue.acm.org/detail.cfm?id=3454124); [InfoQ](https://www.infoq.com/news/2021/03/space-developer-productivity)
- Reinertsen (*Principles of Product Development Flow*, 2009): cost of delay là chỉ số quyết định; batch tối ưu cân bằng holding cost (chậm phản hồi) với transaction cost (chi phí chuẩn bị batch), nên phải giảm transaction cost để batch nhỏ có lợi; phản hồi chậm khiến theo đường sai lâu hơn; gợi ý thử giảm batch 33–50 %. (Nguồn thứ cấp, không phải bản gốc sách.) — [InformIT](https://www.informit.com/articles/article.aspx?p=2928185&seqNum=6); [Scrum.org](https://www.scrum.org/node/101842); [PMI Disciplined Agile](https://www.pmi.org/disciplined-agile/what-is-flow)
- First-pass yield (tỷ lệ thiết kế qua kiểm chứng không cần làm lại) và cost of poor quality (phế phẩm, làm lại, lỗi hiện trường) được Autodesk đề xuất làm chỉ số phát triển sản phẩm, gắn FPY thấp với xung đột không gian vỏ–mạch. (Blog vendor, quảng bá; trang trả 403 khi fetch, chỉ thấy qua snippet.) — [Autodesk Fusion blog](https://www.autodesk.com/products/fusion-360/blog/connected-product-development-autodesk-fusion/)

### Inferences
- Ánh xạ đề xuất cho chuỗi scripted CAD → gate → slice → in thử (suy luận):
  - **Edit-to-feedback time** (≈ change lead time tầng 1): từ lúc sửa script tới khi có kết quả gate/ảnh. Thu tự động: timestamp đầu/cuối của lệnh run_*.py.
  - **Design-to-fit lead time** (tầng cuối): từ commit đầu của một thay đổi tới khi in thử báo "vừa". Thu: commit time + ngày ghi kết quả in.
  - **Iterations to good print**: số vòng in vật lý (theo part hoặc theo bộ) tới lần lắp đạt. Đây là chỉ số "chất lượng thiết kế" quan trọng nhất, vì mỗi vòng in tốn giờ máy + nhựa + thời gian Tuan.
  - **First-print success rate** (FPY): % part/bộ đạt ngay lần in đầu (không in lại vì sai thiết kế). Tách riêng lỗi máy (bong, kẹt) khỏi lỗi thiết kế.
  - **Gate escape rate** (≈ change fail rate): % lần gate PASS nhưng in thử vẫn hỏng vì lỗi thiết kế. Đây là thước đo độ tin của gate tự động; tăng → cần thêm kiểm tra vào gate.
  - **Rework rate**: % commit model là sửa lỗi do in thử phát hiện (không phải tính năng mới). Gắn nhãn commit (`fix-fit:`, `fix-print:`) để đếm tự động.
  - **Time to recover**: từ lúc phát hiện lỗi in tới khi có bản sửa đã qua gate.
- Thang môi trường kiểu Thoughtworks cho STLab: check.py nhanh → slice thật → mẫu thử nhỏ (chỉ chỗ lắp) → bộ in đầy đủ → lắp thật/học sinh dùng. Mục tiêu là đẩy phát hiện lỗi về tầng trái (rẻ hơn).
- Theo Reinertsen, mẫu thử nhỏ gọn (chỉ in chỗ lắp, gộp 1 bàn) chính là giảm batch size để phản hồi nhanh; có thể đo bằng "giờ in mỗi vòng phản hồi".

### Gaps
- Không tìm thấy framework năng suất công bố riêng cho phát triển phần cứng/in 3D quy mô nhỏ, cũng không có benchmark số vòng lặp hay FPY cho studio maker.
- Không đọc được bản gốc sách Reinertsen và bài Autodesk (403); chỉ dựa trên tóm tắt.

## 2. Chỉ số model / bản in (geometry, slicer, DFA)

### Takeaway
Hầu hết chỉ số model lấy được tự động, rẻ: thời gian in, gram nhựa, có support hay không cho từng bàn nằm sẵn trong `Metadata/slice_info.config` của file .gcode.3mf do Bambu Studio xuất. DFA (Boothroyd-Dewhurst) cho chỉ số lắp ráp: số part tối thiểu lý thuyết và design efficiency; bản đơn giản hóa (đếm part + đếm vít + số part "có lý do tồn tại") đủ dùng cho studio nhỏ.

### Cited Findings
- File .gcode.3mf của Bambu có `Metadata/slice_info.config`, mỗi plate có `prediction` (thời gian in, giây), `weight` (gram nhựa), `support_used` (bool). — [Printago, 3MF file format](https://printago.io/blog/3mf-file-format)
- CLI Bambu Studio: `--slice`, `--load-settings "machine.json;process.json"`, `--load-filaments`, `--export-3mf`; `--export-settings` chỉ dump cấu hình đã gộp, không phải kết quả slice. — [Printago Bambu Studio CLI reference](https://printago.io/blog/bambu-studio-cli-reference); [BambuStudio wiki CLI](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)
- Không thấy JSON kết quả chính thức từ CLI; wrapper cộng đồng phải regex log text → đọc `slice_info.config` đáng tin hơn. Có báo lỗi preset ngoài bị bỏ qua cho ra `total_used_g: 0.0` và lỗi CLI crash không ra 3MF. — [Bambu forum](https://forum.bambulab.com/t/cli-cannot-apply-external-presets/197842); [GitHub issue 9636](https://github.com/bambulab/BambuStudio/issues/9636); [bambustudio-mcp cli.py](https://glama.ai/mcp/servers/@hunter-stradley/bambustudio-mcp/blob/8eeb6a606bc047ce74e3da4d28bdda84d078e2c8/bambustudio_mcp/slicer/cli.py)
- Boothroyd-Dewhurst: design efficiency thủ công **Em = 3 × Nm / Tm** (Nm = số part tối thiểu lý thuyết, Tm = tổng thời gian lắp, giây; 3 s ≈ thời gian lý tưởng mỗi part). — [Slide DFA](https://www.slideshare.net/slideshow/tp05-pub214/40745682); [Lecture DFA worksheet](https://www.scribd.com/doc/4354891/Lecture-5-DFA-Boothro)
- Một part được tính vào Nm chỉ khi trả lời "có" ít nhất một câu: có chuyển động tương đối với part khác, cần vật liệu khác/cách ly, hoặc phải tách để lắp/tháo các part khác. Ứng viên loại bỏ thường là vít, phụ kiện, part lặp. — [Altium DFMA](https://resources.altium.com/p/design-manufacturing-and-assembly-dfma-or-predictive-engineering); [Machine Design](https://www.machinedesign.com/cad/software-analysis-yields-metric-improving-product-development)
- Biến thể: DFA index = thời gian lắp lý tưởng / thời gian thực; một bản dùng cố định 2,933 s/part nên chỉ dùng so sánh tương đối. — [Machine Design](https://www.machinedesign.com/cad/software-analysis-yields-metric-improving-product-development); [Clemson DETC2011](https://cecas.clemson.edu/cedar/wp-content/uploads/2017/03/DETC2011-47530.pdf)
- Chưa đọc được bản gốc sách *Product Design for Manufacture and Assembly* (Boothroyd, Dewhurst, Knight); các công thức trên lấy từ slide/bài hội nghị/viết lại thương mại.

### Inferences
- Bộ chỉ số model tối thiểu đề xuất, mỗi bộ in (tự động):
  - `print_time_h`, `filament_g` tổng và theo bàn (từ slice_info.config).
  - `plates` (số bàn), `plates_with_support` (đếm `support_used=true`); với quy tắc "sửa model cho hết support" của STLab, chỉ số mục tiêu = 0.
  - `part_count`, `fastener_count` (đếm từ danh sách component trong file lắp / BOM), `fastener_types` (số loại vít khác nhau, ít hơn = dễ lắp cho học sinh).
  - `dfa_ratio` ≈ Nm / part_count (Nm do người thiết kế gắn cờ "cần thiết" từng part theo 3 câu hỏi B-D). Thời gian lắp thật hiếm khi có → dùng tỷ số part thay Em (suy luận, đơn giản hóa).
  - `tri_count` / face count: chỉ là chỉ số kỹ thuật pipeline (tốc độ boolean/slice), không phải chất lượng thiết kế; giữ để cảnh báo ngưỡng (vd decimate > 200k) chứ không tối ưu.
  - `support_volume`: slice_info chỉ có cờ bool, không có thể tích; nếu cần phải tính khác (TODO, chưa có nguồn).
- Chi phí mỗi prototype ≈ filament_g × giá/g + giờ in × chi phí giờ máy (điện + khấu hao) – theo cách SimplyPrint tính (mục 3).

### Gaps
- Không tìm thấy trường thể tích support trong slice_info.config; không xác nhận được toàn bộ schema file (chỉ ba trường trên).
- Không có số Em/DFA tham chiếu cho đồ chơi/robot in 3D.

## 3. Tín hiệu chất lượng (fit test, log lỗi, chi phí prototype)

### Takeaway
Phần mềm quản lý farm (SimplyPrint, 3DPrintForge…) đo kết quả in theo phân loại succeeded / cancelled / failed / printer error, có lý do hủy, gram nhựa, chi phí mỗi job. Studio thiết kế cần thêm một trục mà farm tool không có: **kết quả lắp theo từng khe** (vừa / chặt / lỏng) và **nguyên nhân gốc là thiết kế hay máy**.

### Cited Findings
- SimplyPrint: success rate = số in hoàn tất / tất cả bản in trong khung thời gian (gồm cả đang in, nên in dài chưa xong làm tụt số); các thẻ: số job, tổng giờ in, gram nhựa, prints/day, giờ in trung bình, printer run time (≈ utilization), tổng chi phí; biểu đồ lý do hủy (tùy chỉnh); xuất CSV. — [SimplyPrint statistics](https://simplyprint.io/features/statistics.md)
- SimplyPrint: chi phí job = khối lượng nhựa × giá/g + các dòng chi phí cấu hình (điện, nhân công, hậu xử lý, khấu hao máy), chia theo máy, loại nhựa, khách. — [SimplyPrint statistics](https://simplyprint.io/features/statistics.md)
- Kết quả in phân loại: succeeded, regretted, failed, printer error (SimplyPrint); successful / cancelled bởi người / failed do Print Guard, lỗi HMS, phần cứng (3DPrintForge cho Bambu). — [SimplyPrint](https://simplyprint.io/features/statistics); [3DPrintForge statistics](https://skynett81.github.io/3dprintforge/en/analytics/statistics)
- Bộ đếm bảo trì theo giờ in, gram nhựa, số lần in từ lần bảo trì trước. — [SimplyPrint maintenance](https://simplyprint.io/features/printer-maintenance)
- Thực hành farm: ghi audit "ai chạy job gì lúc nào"; dán nhãn và chụp ảnh chi tiết ngay sau mỗi job để nhận diện revision; một máy "đặc biệt" (ống quạt khác, dây đai mòn) làm sai lệch kết quả; requeue mù chỉ đốt thêm nhựa. — [Sovol, print farm automation 2026](https://www.sovol3d.com/blogs/news/3d-print-farm-automation-in-2026-a-practical-system-for-10-30-printers); [Sovol, swarm printing](https://www.sovol3d.com/blogs/news/3d-print-farm-management-swarm-printing-for-small-batch-production)
- Khe hở: guide khuyên press-fit 0–0,05 mm trên Bambu nhưng cảnh báo 0 mm vẫn có thể quá chặt; khe 0,15–0,2 mm phổ biến để lắp vừa; press-fit luôn phải in thử trước; dung sai phụ thuộc vật liệu, hướng in, độ dày vách. — [All3DP tolerances](https://all3dp.com/2/3d-printing-tolerances-test-fdm/); [UAL CCI wiki](https://wiki.cci.arts.ac.uk/books/digital-fabrication-lab/page/design-the-clearance-and-tolerance)
- Nghiên cứu FDM PLA (Processes 11, 2810, 2023): đạt được miền dung sai và kiểu lắp hở theo ISO 286 trên máy in để bàn. — [MDPI Processes](https://mdpi.com/2227-9717/11/10/2810)
- Không có thống kê độc lập về tỷ lệ in thành công điển hình; con số 98,8 % / 400 bản in trên DEV là không có nguồn, không nên dùng. — [DEV post](https://dev.to/johalputt/octoprint-how-to-set-up-for-perfect-results-3j2c)

### Inferences
- Log fit test tối thiểu (1 dòng / khe / lần in): `project, part_pair, feature_id, nominal_mm, clearance_mm, material, orientation, result{fit|tight|loose|broken}, note, photo`. Tích lũy → cập nhật fit-library theo dữ liệu thật thay cho số mặc định; chỉ số = **fit hit rate** (% khe đạt "fit" lần đầu) theo từng loại khớp.
- Log lỗi / làm lại: mỗi lần in lại ghi `cause` theo danh mục cố định: `design-fit`, `design-strength`, `design-printability` (support, overhang), `design-assembly` (không lắp được, va chạm), `machine` (bong bàn, kẹt), `material`, `operator`. Pareto nguyên nhân hàng tháng → quyết định đưa kiểm tra nào vào gate (vd va chạm mọi cặp part).
- **Cost per prototype iteration** = Σ(filament_g × giá/g) + giờ in × chi phí giờ máy cho các vòng in thử tới lúc đạt; chỉ số tổng hợp của "chất lượng thiết kế + chất lượng gate".
- Không bắt buộc số giá; nếu chưa có giá điện/khấu hao thì ghi TODO, chỉ đo gram và giờ.

### Gaps
- Không tìm thấy nguồn công bố về cách studio thiết kế (không phải farm) ghi kết quả fit test theo khe; mẫu log trên là suy luận.
- Không có số liệu công khai về tỷ lệ lỗi thiết kế vs lỗi máy ở studio nhỏ.

## 4. Cách ghi nhận, dùng để ra quyết định, và bẫy

### Takeaway
Bắt đầu nhẹ: một file log dạng dòng (CSV/JSONL) ghi tự động bởi script gate/slice, cộng một dòng tay sau mỗi lần in thử; xem xu hướng theo dự án, không so giữa các dự án. Giữ 5–8 chỉ số có sức căng nhau (tốc độ vs độ ổn định vs chi phí) để tránh Goodhart.

### Cited Findings
- Mẫu dashboard farm: hàng thẻ số (tổng job, giờ in, success rate, nhựa, run time, chi phí) + biểu đồ xu hướng bên dưới. — [SimplyPrint dashboards](https://simplyprint.io/features/dashboards)
- DORA khuyên bắt đầu bằng trao đổi/Quick Check thay vì tích hợp dữ liệu phức tạp; so một hệ thống với chính nó theo thời gian; sở hữu chung chỉ số. — [DORA metrics guide](https://dora.dev/guides/dora-metrics/)
- Goodhart (1975): "Any observed statistical regularity will tend to collapse once pressure is placed upon it for control purposes"; bản Strathern (1997): "When a measure becomes a target, it ceases to be a good measure." Manheim: thất bại khi thước đo lệch mục tiêu thật, khi hệ thống khuyến khích gian lận, hoặc khi thước đo cũ vẫn dùng sau khi bối cảnh đổi. — [Wikipedia Goodhart's law](https://www.wikipedia.org/wiki/Goodhart%27s_law); [Manheim, MPRA 98288](https://mpra.ub.uni-muenchen.de/98288/5/MPRA_paper_98288.pdf)
- Ví dụ phần mềm: đo độ tin cậy qua số bug → bug được sửa theo cách làm hệ thống kém tin cậy hơn nhưng không hiện thành bug đếm được; báo cáo DORA 2023 khuyên đánh giá trên nhiều mặt người/quy trình/kỹ thuật. — [Hillel Wayne](https://buttondown.com/hillelwayne/archive/goodharts-law-in-software-engineering)
- SPACE: chỉ số năng suất không bao giờ dùng riêng lẻ và không dùng để thưởng/phạt. — [Pluralsight SPACE](https://www.pluralsight.com/resources/blog/software-development/Implementing-the-SPACE-of-developer-productivity-framework)

### Inferences
- Bẫy cụ thể cho chuỗi CAD (suy luận):
  - Tối ưu **gate pass rate** → nới gate cho dễ PASS; phải đi cặp với **gate escape rate** (lỗi lọt ra bản in).
  - Tối ưu **edit-to-feedback time** → bỏ bớt kiểm tra; đi cặp với escape rate.
  - Tối ưu **filament_g / print_time** → vách mỏng, gãy; đi cặp với lỗi `design-strength`.
  - Tối ưu **part_count** (DFA) → gộp part cần support hoặc không in được trên A1/không tách màu được (quy tắc hạn chế AMS); đi cặp với `plates_with_support`.
  - **tri_count, số commit, số file sinh ra** là vanity metric cho chất lượng thiết kế.
- Bộ "compact" đề xuất (≤8, tự động hóa được):
  1. Edit-to-feedback time (median, s) – tự động từ run log.
  2. Iterations to good fit (số vòng in vật lý/bộ) – log in thử.
  3. First-print success rate (thiết kế) – log in thử.
  4. Gate escape rate – log in thử × kết quả gate.
  5. Rework causes Pareto – trường `cause`.
  6. Fit hit rate theo loại khe – log fit.
  7. Cost per iteration (g nhựa, giờ máy) – slice_info.config.
  8. Assembly simplicity: part_count, fastener_count, plates_with_support – BOM + slice.
- Nhịp dùng: xem mỗi khi đóng một dự án/bộ in (retro ngắn) và tháng một lần cho xu hướng; quyết định cải tiến = chọn nguyên nhân đầu Pareto → thêm 1 kiểm tra vào gate hoặc 1 mục fit-library → xem escape rate và iterations tháng sau có giảm không.
- Với 1 người + agent, log JSONL nối tiếp trong repo (commit cùng model) là đủ; dashboard có thể là một trang Toolhub đọc file log. Không cần công cụ farm vì chỉ có ít máy.

### Gaps
- Không tìm thấy bài viết maker/studio phần cứng nhỏ mô tả bộ chỉ số thật đang dùng; mọi đề xuất "compact set" ở trên là suy luận ghép từ DORA/SPACE/DFA/farm tools.
- Chưa có nguồn về Printago/OctoFarm/Bambu Farm Manager stats cụ thể (chỉ kiểm SimplyPrint, 3DPrintForge).
