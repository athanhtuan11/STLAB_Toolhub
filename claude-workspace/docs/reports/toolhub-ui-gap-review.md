# Rà soát khoảng trống giao diện Toolhub

Ngày: 2026-11-02. Phạm vi: đọc mã và tài liệu, không chạy server; không đọc dữ liệu báo giá bên ngoài repo. Đây là đề xuất để Tuan duyệt, chưa triển khai.

## 1. Hien trang Toolhub

| Trang/route GET | Chức năng | Module / template | Menu điều hướng | Test |
|---|---|---|---|---|
| `/` | Ứng dụng, dự án in, trạng thái nhân sự và điều hành | `toolhub/views.py` → `overview.html` | Trang chính | Có kiểm qua `tests/test_ops.py`, `tests/test_org_board.py` |
| `/apps` | Mở ứng dụng, kiểm MCP, bố trí cửa sổ / đồng bộ Desktop qua các API POST | `views.py` → `apps.html` | Thêm ▾ | Chưa thấy test trang riêng trong `studio/tests/` |
| `/projects` | Danh sách dự án, file chính và trạng thái TODO | `views.py`, `workspace.py`, `opener.py` → `projects.html` | Dự án | Chưa thấy test trang riêng |
| `/projects/<slug>` | Đọc CLAUDE.md, mở file, xem/chạy chuẩn bị in | `views.py`, `printprep.py` → `project-detail.html` | Không có mục riêng; liên kết từ `/` và `/projects` | Chưa thấy test route riêng |
| `/library` | Danh mục linh kiện, lọc/tìm, thống kê thư viện | `views.py`, `workspace.py` → `library.html` | Linh kiện | `tests/test_library_pages.py` |
| `/library/<cid>` | Chi tiết linh kiện, ảnh chân, sơ đồ chân/đấu dây SVG | `workspace.py` + `pinout.py` / `pin_diagram.py` → `library-detail.html` | Không có mục riêng; liên kết từ `/library` | `test_library_pages.py`, `test_pinout.py`, `test_pin_diagram.py` |
| `/community` | Trạng thái repo ghim, symlink và báo cáo cộng đồng | `views.py`, `workspace.py` → `community.html` | Thêm ▾ | Chưa thấy test trang riêng |
| `/community/report/<name>` | Đọc báo cáo cộng đồng | `workspace.py` → `report.html` | Không có mục riêng; liên kết từ `/community` | Chưa thấy test route riêng |
| `/research` | Digest tuần, lọc tin và đánh dấu quan tâm/bỏ qua; quét nền | `research.py` → `research.html`, `research.js` | Menu chính | `tests/test_research.py` |
| `/ops` | Duyệt việc, theo dõi executor, handoff, dòng sự kiện và commit | `ops.py` → `ops.html`, `ops.js` | Menu chính | `tests/test_ops.py` |
| `/skills` | Tình trạng liên kết skill/agent theo scope | `workspace.py` → `skills.html` | Thêm ▾ | Chưa thấy test trang riêng |
| `/prompt` | Danh sách prompt FreeCAD/Blender | `workspace.py` → `prompt.html` | Thêm ▾ | Chưa thấy test trang riêng |
| `/quote` và `/quote/<id>` | Cắt lớp/tính giá, lưu báo giá, bản in/PDF | `quote.py`, `views.py` → `quote.html`, `quote-print.html` | `/quote` ở Thêm ▾; bản báo giá từ lịch sử | `test_quote*.py` |

Các API như `/api/health`, `/api/print/...`, `/api/quote/...` và `/api/ops/...` phục vụ trang hiện hữu, không phải trang điều hướng độc lập (`studio/toolhub/views.py`). `pinout` và `pin_diagram` đã được dùng trong chi tiết linh kiện, không phải khoảng trống web (`studio/toolhub/workspace.py`).

## 2. Tinh nang repo chua len web

| Công cụ | Lệnh hiện tại (nguồn) | Lợi khi lên web | Rủi ro | Nên/không nên |
|---|---|---|---|---|
| Fit-library tra khe | `fit_lib.py lookup <interface>` / `recommend <interface>`; CLI được mô tả trong `tools/model-study/spec-fit-lib.md`; mã và kho là `tools/model-study/fit-library/fit_lib.py`, `tools/model-study/fit-library/fits.json` | Tra thông số đã lưu, nguồn và mức xác nhận mà không phải mở terminal | Dữ liệu chỉ để tham khảo; ghi thêm/sửa kho có thể làm sai cơ sở thiết kế | Nên làm trang tra cứu chỉ đọc trước |
| Model-study contact sheet | `python tools/model-study/study_3mf.py <input> <output>` (`study_3mf.py`) | Xem ảnh tổng hợp, CSV và tóm tắt để Tuan duyệt bằng ảnh | Đọc model; tạo/ghi đè nhiều file trong thư mục output; model cộng đồng chỉ dùng học/fit | Nên làm thư viện xem kết quả; nút chạy chỉ sau khi chốt thư mục output |
| Render Blender | `python tools/render/render.py <model.FCStd> --cmf <cmf.json> --out <dir> ...` (`tools/render/README.md`) | Chọn model/CMF/view rồi xem ảnh render ngay trong dự án | Tốn thời gian/tài nguyên; ghi ảnh/scene JSON; không được sửa FCStd | Nên; chỉ chọn dự án đã biết, báo rõ nơi ghi và không ghi đè mặc định |
| Chuẩn bị in | `python.exe scripts/prepare-print.py maker/<project>/print/print.yaml` (`tools/robotics-cad/CLAUDE.md`); implementation `tools/robotics-cad/scripts/prepare-print.py`, `tools/robotics-cad/scripts/watch.py`; Toolhub đã có nút ở trang dự án (`studio/toolhub/printprep.py`) | Đã đáp ứng nhu cầu bấm nút và xem kết quả; nên cải thiện tiến độ/lỗi và xem contact sheet | Chạy tiến trình nền, ghi STL/3MF/log; chỉ dùng file đã lưu; kết quả không phải lệnh in vật lý | Không tạo trang trùng; nên hoàn thiện UX hiện tại |
| Delegate status | `python tools/delegate/delegate.py --status` (`tools/delegate/README.md`, `tools/delegate/delegate.py`) | Biết executor bị giới hạn/run gián đoạn mà không mở terminal | Chỉ đọc tình trạng local; không bấm chạy/resume executor từ web ở phiên đầu | Nên làm thẻ chỉ đọc trong `/ops` |
| Research Scout | `python scan.py`, `python digest.py`, `python scout.py mark ID quan-tam` (`tools/research-scout/README.md`, `tools/research-scout/scan.py`); `/research` đã có quét và đánh dấu | Hiển thị rõ lần quét gần nhất, đang chạy/thất bại và link digest | Quét nguồn công khai qua tiến trình nền; DB cục bộ có thể thay đổi | Không tạo trang mới; nên phản hồi trạng thái/lỗi chính xác |
| Sao lưu FCStd | `python tools/backup/backup_fcstd.py` (`tools/backup/README.md`, `tools/backup/backup_fcstd.py`) | Xem lần sao lưu/đích bị thiếu; thao tác tay giảm | Ghi bản sao ra ổ G:/OneDrive; khôi phục/ghi đè có thể làm mất phiên bản; file thiết kế nội bộ | Nên làm trạng thái chỉ đọc; chưa nên thêm nút khôi phục/xóa |
| OTA pump-control | `powershell -ExecutionPolicy Bypass -File release.ps1 -Version ... -Notes ...` (`maker/pump-control/firmware/release.ps1`) | Có thể trình bày version/note và checklist duyệt phát hành | Sửa version, build, xóa artifact cũ, commit/push và phát hành firmware tới thiết bị khách điều khiển máy bơm | Không đưa nút phát hành/flash lên Toolhub; chỉ checklist/tài liệu sau khi Tuan duyệt |
| Báo cáo `docs/reports/` | Không thấy lệnh; đọc Markdown trực tiếp. Trang hiện tại liệt kê `community/reports/` (`studio/toolhub/workspace.py`) | Tìm, lọc và mở báo cáo nghiên cứu/quy trình tại một chỗ | Chỉ đọc; cần tránh đưa dữ liệu cá nhân hoặc nội dung nhạy cảm vào danh sách | Nên thêm danh sách chỉ đọc trong trang cộng đồng hoặc `/ops` |

## 3. Van de giao dien hien tai

- **Menu lệch tài liệu:** `studio/CLAUDE.md` mô tả menu chính chỉ có Trang chính/Dự án/Linh kiện, nhưng `nav()` hiện đưa Điều hành và Nghiên cứu vào menu chính (`studio/toolhub/views.py:27-34`; `studio/toolhub/templates/base.html`). Cần cập nhật tài liệu sau khi Tuan chốt cách phân nhóm.
- **Đường vào trang chi tiết:** linh kiện, dự án và báo cáo cộng đồng không có mục menu riêng nhưng được liên kết từ danh sách tương ứng; đây là chủ đích theo luồng hiện tại, không thấy route GET nào mất đường vào (`views.py:58-65, 193-198, 218-225`).
- **Template:** các trang dùng chung `base.html`; không thấy bằng chứng template trang bị sao chép trùng. `quote-print.html` là bản trình bày riêng phục vụ in/PDF (`templates/base.html`, `templates/quote-print.html`).
- **POST thiếu bước xác nhận:** `app.js` gửi POST trực tiếp khi bấm `data-post`, chỉ khóa nút và hiện toast; không có confirm trước hành động (`static/app.js`). Áp dụng cả thao tác mở/sync và chuẩn bị in; các thao tác thay đổi cài đặt/phát sinh tác dụng nên có cảnh báo mô tả trước khi thực hiện.
- **Lỗi bị nuốt hoặc báo thành công sớm:** `/ops` bắt lỗi fetch rồi bỏ qua, người dùng có thể chỉ thấy widget trống (`static/ops.js:17-18`). Nút quét research không kiểm `response.ok` nhưng luôn hiện “Đang quét” (`static/research.js:6`); cần phân biệt nhận lệnh thành công với lỗi.
- **Đọc đĩa đồng bộ:** trang chủ gọi `ws.projects()`, trạng thái chuẩn bị in từng dự án và `ops.summary()` ngay trong GET (`views.py:68-84`). Trang Linh kiện gọi `_stats()` đếm STEP/FCStd/STL bằng `os.walk` thư viện trong lúc render (`workspace.py:230-245`). Chưa có số đo thời gian; nên đo trước khi tối ưu/cache.
- **Đường dẫn cứng:** Python FreeCAD cố định ở `C:\Program Files\FreeCAD 1.1\bin\python.exe` (`toolhub/printprep.py`, `toolhub/quote.py`); Edge PDF thử hai thư mục Program Files cố định (`views.py:321-322`); Graphviz cũng có fallback cố định (`pin_diagram.py`). Máy cài khác vị trí có thể không dùng được; ưu tiên cấu hình tập trung/fallback báo lỗi rõ.
- **Mô hình bảo vệ:** `create_app()` kiểm tra Host, yêu cầu `X-Studio: 1` cho POST và xác minh Origin nếu có (`toolhub/__init__.py`). Tài liệu nói cấu hình loopback (`studio/CLAUDE.md`), nhưng middleware kiểm header Host chứ không tự ép socket bind loopback; không mở Flask ra mạng. `X-Studio` là marker, không phải thông tin xác thực bí mật.
- **Dữ liệu báo giá:** upload model được ghi ra thư mục làm việc local; báo giá lưu tên/SĐT trong SQLite ngoài repo (`views.py:620-659, 694-706`; `toolhub/quote.py:107-121, 332-337, 648-668`). Giữ nguyên ranh giới local, không đưa dữ liệu khách vào báo cáo hay endpoint công khai.
- **Độ phủ test:** có test cho linh kiện, ops, nhân sự, pinout, quote và research; chưa thấy test trang riêng cho apps, projects, community, skills, prompt (`studio/tests/`). Ưu tiên test quyền Host/X-Studio, lỗi tiến trình và đường dẫn ghi trước khi thêm nút mới.
- **Ngôn ngữ:** `base.html` khai báo `lang="vi"` và các template chính có tiếng Việt dấu; chưa thấy căn cứ để kết luận chữ Việt giao diện đang mất dấu. Chuẩn hóa thêm các trạng thái lỗi/toast theo giọng thống nhất.

## 4. Mau in dang cong dong va ban

Nghiên cứu mẫu in đề xuất vừa chia sẻ thiết kế mới, vừa thử bán sản phẩm/biến thể địa phương; chưa phải phê duyệt giá hay phát hành (`docs/reports/print-products-market-research.md`, mục 1, 7, 10).

- **Tận dụng `/projects` làm danh mục nội bộ:** mỗi dự án mẫu có ảnh duyệt/contact sheet, phiên bản, trạng thái đề xuất `Thiết kế → In thử → Đã duyệt → Đăng → Đang bán`, link profile/file phát hành và ghi chú lỗi thử in. Hiện trang mới đọc CLAUDE.md và nút chuẩn bị in, chưa có lifecycle sản phẩm (`studio/toolhub/templates/projects.html`, `project-detail.html`; `tools/robotics-cad/CLAUDE.md`).
- **Duyệt bằng ảnh:** dùng contact sheet từ `tools/model-study/study_3mf.py` và ảnh render Blender; giữ việc Tuan chọn/duyệt trước khi chuyển trạng thái, không tự đăng. Ghi rõ ảnh là render hay ảnh mẫu in thật (`tools/model-study/study_3mf.py`, `tools/render/README.md`; `print-products-market-research.md`, mục 3, 7).
- **Nối `/quote` ở bước bán:** link trực tiếp từ dự án sang báo giá, chọn file đã slice hoặc model, xem giá vốn/giá bán và lưu bản báo giá. Giá trong nghiên cứu là tham khảo có thời điểm; dùng bảng giá và phép tính hiện hành trong `/quote`, không tự chốt giá/chiết khấu (`studio/toolhub/views.py:511-529, 693-714`; `print-products-market-research.md`, mục 5, 9.3).
- **Checklist gói MakerWorld:** thiết kế do STLab sở hữu; license/quyền logo được kiểm; profile A1 và vật liệu đã thử; file/profile đặt tên rõ; ảnh thật + ảnh/render; hướng dẫn lắp/hướng in/support; kích thước sau slice; giới hạn và cảnh báo; người duyệt và ngày cập nhật. Điều khoản nền tảng cần kiểm lại trước lúc đăng (`print-products-market-research.md`, mục 2-3, 6-7).
- **Không tự động hóa publish:** bài đăng/nhãn độc quyền/điểm thưởng và giao dịch cần người duyệt; đơn tùy biến cần khách xác nhận quyền tên/logo, giá và bản xem trước. Không tái đăng model cộng đồng, không quảng bá mẫu chưa thử như đã an toàn (`print-products-market-research.md`, mục 1, 6-7).

## 5. De xuat xep loi/cong

Ước lượng công là giờ triển khai UI/kiểm thử sơ bộ, chưa phải cam kết; 4 việc ★ nên ưu tiên xin duyệt. Giữ các phần ghi dữ liệu hoặc tác động thiết bị sau gate duyệt riêng.

| Đề xuất | Mục | Lợi | Công (giờ) | Rủi ro | File liên quan |
|---|---|---:|---:|---|---|
| ★ Danh mục mẫu và trạng thái lifecycle trên `/projects` | 4 | Cao | 8–14 | Trung bình: thêm metadata, cần quy ước chuyển trạng thái | `studio/toolhub/workspace.py`, `templates/projects.html`, `templates/project-detail.html`, `maker/` |
| ★ Xem contact sheet/render và đánh dấu duyệt bằng ảnh | 4 | Cao | 4–8 | Thấp-vừa: chỉ đọc ảnh đã tạo; xác định nguồn ảnh | `tools/model-study/study_3mf.py`, `tools/render/README.md`, `templates/project-detail.html` |
| ★ Danh sách báo cáo `docs/reports/` chỉ đọc | 2 | Cao | 3–5 | Thấp: giới hạn thư mục, không hiển thị dữ liệu khách | `studio/toolhub/workspace.py`, `views.py`, `templates/community.html`, `docs/reports/` |
| ★ Fit-library tra cứu chỉ đọc, hiện nguồn/mức xác nhận | 2 | Cao | 4–7 | Trung bình: người dùng có thể hiểu nhầm dữ liệu chưa kiểm là chuẩn | `tools/model-study/fit-library/fit_lib.py`, `fits.json`, `studio/toolhub/views.py` |
| Trạng thái/log dễ hiểu cho chuẩn bị in và research scan | 3 | Cao | 3–6 | Thấp-vừa: hai tiến trình nền, phân biệt trạng thái cũ/mới | `studio/toolhub/printprep.py`, `research.py`, `static/research.js`, `templates/project-detail.html` |
| Thẻ delegate `--status` chỉ đọc trong `/ops` | 2 | Vừa | 3–5 | Thấp: dữ liệu local; không cho chạy/resume từ UI | `tools/delegate/README.md`, `studio/toolhub/ops.py`, `templates/ops.html` |
| Trang trạng thái backup chỉ đọc | 2 | Vừa | 4–7 | Trung bình: đích ngoài repo, không nhầm trạng thái với bản sao an toàn | `tools/backup/README.md`, `studio/toolhub/views.py` |
| Nút render Blender theo dự án đã biết | 2 | Vừa | 8–12 | Trung bình-cao: tiến trình dài, ghi nhiều file, cần chặn ghi đè | `tools/render/README.md`, `studio/toolhub/workspace.py`, `templates/project-detail.html` |
| Bổ sung kiểm thử route/menu/lỗi cho apps, projects, community, skills, prompt | 3 | Vừa | 4–8 | Thấp | `studio/tests/`, `studio/toolhub/views.py` |
| Nút phát hành OTA hoặc publish MakerWorld từ web | 2, 4 | Thấp | Không làm | Rất cao: firmware thiết bị khách / phát hành công khai; có ghi file và push | `maker/pump-control/firmware/release.ps1`, `maker/pump-control/CLAUDE.md`, `docs/reports/print-products-market-research.md` |

## Claude kiểm lại (2026-11-02)

- Đúng: `/ops` nuốt lỗi bằng `catch{}` (`studio/toolhub/static/ops.js:17-18`); nút quét research không kiểm `response.ok` (`studio/toolhub/static/research.js:6`); không có `confirm(` nào trong `static/*.js`.
- Bổ sung mục 3 "Mô hình bảo vệ": socket đã bind loopback qua `studio/.flaskenv` (`FLASK_RUN_HOST=127.0.0.1`, cổng 5050) – không phải lỗ hổng, chỉ cần giữ nguyên khi đổi cách chạy.
- Copilot viết, gate PASS lần 1; delegate báo ESCALATE chỉ vì xin xóa file tạm trong `.delegate-tmp/` (đã gitignore) – bỏ qua.
