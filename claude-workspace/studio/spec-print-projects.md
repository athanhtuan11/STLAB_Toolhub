---
task: print-projects
cwd: studio
allow:
  - "toolhub/prints.py"
  - "toolhub/static/prints.js"
  - "toolhub/static/style.css"
  - "toolhub/templates/prints.html"
gate: ".venv\\Scripts\\python.exe -X utf8 tests\\test_print_projects.py && .venv\\Scripts\\python.exe -X utf8 tests\\test_print_home.py"
timeout_min: 25
max_rounds: 2
executor: auto
read: ["../maker"]
---

# Mục tiêu
Tuan 2026-11-16: "In 3D, gom dự án lại 1 mục thôi. Bạn đang làm 1 dự án từng chi tiết riêng lẻ. block-coding-car thì chỉ 1 mục.
Nhấn vô thì sẽ mở ra plates." → Trang chính `/` (In 3D) hiện **1 thẻ cho mỗi dự án**; nhấn thẻ → hiện các thẻ bàn in của dự án đó
(thẻ bàn giữ nguyên như hiện nay: ảnh, tên bàn, giờ, gam, nút In / CAD / Thư mục).

# Yêu cầu
1. `toolhub/prints.py`: thêm `list_print_projects()` gom kết quả `list_prints()` theo khóa `(source, folder)`. Mỗi nhóm:
   `project`, `title`, `source`, `folder`, `cad` (lấy từ bàn đầu), `plates` (danh sách bàn, **xếp theo tên bàn tăng dần**),
   `plate_count`, `minutes` (tổng phút các bàn có số; không bàn nào có số → null), `grams` (tổng, làm tròn 1 số lẻ; không có → null),
   `image_url` (ảnh của bàn đầu tiên – theo thứ tự đã xếp – có ảnh, không có → null), `mtime` (lớn nhất của các bàn).
   Danh sách nhóm xếp `mtime` giảm dần.
2. `toolhub/views.py` Claude đã sửa sẵn: `/api/prints` trả `{"prints": list_prints(), "projects": list_print_projects()}`
   (hiện báo lỗi vì hàm chưa có) – executor chỉ viết hàm trong prints.py, không sửa views.py.
3. `toolhub/static/prints.js` (trang chính):
   - Mặc định hiện lưới **thẻ dự án** từ `data.projects`: ảnh (`image_url`), tên dự án (`project`), tiêu đề (`title`), nhãn "Linh kiện" nếu
     `source === "linh-kien"`, dòng `"<plate_count> bàn in · <tổng giờ> · <tổng gam> g"` (dùng `printDuration` sẵn có, gam dấu phẩy).
     Thẻ dự án là `<article class="card print-card print-project">` có thể nhấn (role="button", tabindex="0", Enter/Space cũng mở).
   - Nhấn thẻ → đặt `location.hash = "#p=" + encodeURIComponent(source + ":" + folder)`; nghe `hashchange` để hiển thị:
     tiêu đề dự án + nút `← Tất cả dự án` (về hash rỗng) + lưới thẻ bàn bằng `printCard(item)` hiện có. Nút Back của trình duyệt quay lại
     danh sách. Mở trang với hash sẵn → vào thẳng dự án đó; hash không khớp → về danh sách.
   - Ô tìm: ở danh sách lọc thẻ dự án theo project + title + tên các bàn (bỏ dấu như `normalizePrintText`); ở trong dự án lọc thẻ bàn.
     Dòng đếm: `"<n> dự án"` ở danh sách, `"<n> bàn in"` trong dự án.
   - Giữ nguyên `openPrint`, khối `health`, sự kiện `data-print-open`.
4. `toolhub/static/style.css`: thêm `.print-project` (cursor pointer, viền/đổ bóng khi hover/focus-visible dùng biến màu có sẵn như
   `var(--accent)`, `var(--line)` – **không đặt mã hex**), `.print-back` cho nút quay lại, tiêu đề dự án.
5. `prints.html`: đổi chữ phụ thành "Chọn dự án để xem bàn in, mở nhanh 3MF hoặc CAD." và chữ đang tải "Đang tải dự án…".

# Không làm
- Không sửa `views.py`, template `print-card.html`, `library-detail.html`, `project-detail.html`, test.
- Không đổi `list_prints()` / `resolve()` / `image_path()` (trang linh kiện và trang dự án đang dùng).
- Không thêm thư viện, CDN.

# Tiêu chí PASS
- Gate exit 0.
- Claude tự chạy Toolhub chụp ảnh trang chính + trang trong block-coding-car.
