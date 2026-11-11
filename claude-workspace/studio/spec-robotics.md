---
task: robotics-page
cwd: studio
allow:
  - "toolhub/robotics.py"
  - "toolhub/views.py"
  - "toolhub/templates/robotics.html"
  - "toolhub/static/style.css"
gate: ".venv\\Scripts\\python.exe tests\\test_robotics.py && .venv\\Scripts\\python.exe tests\\test_products_reports.py && .venv\\Scripts\\python.exe tests\\test_library_pages.py && .venv\\Scripts\\python.exe tests\\test_research.py"
timeout_min: 30
max_rounds: 2
executor: auto
---

# Mục tiêu
Trang Toolhub **"Robotics"** `/robotics` (Tuan 2026-11-11: "đưa các dự án robotics lên web"): một chỗ xem mọi dự án
robotics (ảnh bìa, trạng thái, bước tiếp, số bàn in, PDF lắp ráp, ngày cập nhật) + khu **Mô phỏng** (GearsBot, Erebus).
Trang chỉ ĐỌC; mọi số liệu tự đọc từ thư mục dự án, chỉ trạng thái/mô tả lấy từ manifest.

# Đầu vào
- Gate `tests/test_robotics.py` (Claude viết, KHÔNG sửa): đặc tả chính xác khóa dữ liệu, route, thứ tự ảnh bìa, lỗi.
- Manifest `toolhub/robotics.json` (Claude viết, KHÔNG sửa). Biến môi trường `STLAB_ROBOTICS_MANIFEST` thay đường dẫn.
- Mẫu cùng kiểu: `toolhub/research.py` + `templates/research.html`; render markdown: `toolhub/mdrender.py` +
  `templates/report-doc.html` (xem cách `reports_doc` trong `views.py` dùng). Workspace root: `workspace.ROOT`.
- Lớp CSS có sẵn: `.head .sub .grid .card .row .grow .muted .badge(.ok/.bad/.plain) .actions .btn`; màu chỉ dùng
  biến trong `static/tokens.css` (`--card --line --muted --accent --accent-soft --ok --warn --err --text --bg`).

# Yêu cầu
- `toolhub/robotics.py` (thư viện chuẩn) chứa logic; `views.py` chỉ thêm route mỏng.
  - `load()`: đọc manifest; `ValueError` (thông báo tiếng Việt) nếu `status` không thuộc `statuses`, `rel` không bắt đầu
    bằng `maker/`, chứa `..`, hoặc thư mục không tồn tại.
  - `data()` → `{"statuses", "projects": [...], "simulations": [...]}`, project giữ thứ tự manifest, đủ khóa trong gate:
    - `plates` = số file `print/plates/*/*.3mf` + `solidcraft/print/plates/*/*.3mf` (không đệ quy).
    - `updated` = `git log -1 --format=%cs -- <rel>` (chạy trong `ROOT`, `creationflags=CREATE_NO_WINDOW` trên Windows
      như `workspace._git`); thư mục chưa có commit → ngày sửa file mới nhất (mtime) dạng YYYY-MM-DD. Tổng `data()` < 3 s.
    - `todo` = số `\bTODO\b` trong CLAUDE.md (0 nếu không có); `detail_url` = `/projects/<slug>` chỉ khi có CLAUDE.md, ngược lại `""`.
    - `cover`: manifest có `cover` (đường dẫn tương đối trong dự án) thì dùng; không thì file đầu tiên tồn tại theo thứ tự:
      `solidcraft/images/assembly/cover.png`, `freecad/images/assembly/cover.png`, `design/cover.png`,
      `print/plates/*/preview.png` (sắp xếp tên, lấy đầu), `design/concepts/*-3-4.png` (sắp xếp, đầu),
      `design/concepts/*.png` (sắp xếp, đầu); không có → `""`. Giá trị = `/robotics/img/<slug>/<đường dẫn posix>`.
    - simulation: thêm `cover` = `/robotics/sim/<id>/cover` nếu manifest có ảnh và file tồn tại, ngược lại `""`;
      `readme_url`/`lesson_url` = `/robotics/sim/<id>/readme|lesson` nếu manifest có đường dẫn, ngược lại `""`.
- Route (`views.py`):
  - `GET /robotics` → `robotics.html`.
  - `GET /robotics/img/<slug>/<path:rel>`: slug phải là dự án trong manifest; file resolve phải nằm trong thư mục dự án;
    đuôi `.png .jpg .jpeg .webp .svg`; sai → 404. `send_file(max_age=0)`.
  - `GET /robotics/file/<slug>/ASSEMBLY.pdf`: chỉ đúng tên này, slug trong manifest, file tồn tại → `application/pdf`; khác → 404.
  - `GET /robotics/sim/<id>/cover|readme|lesson`: id trong manifest; readme/lesson render bằng `mdrender.render` trong
    `report-doc.html` (hoặc template tương tự kế thừa `base.html`) kèm link `← Robotics` về `/robotics`; không có → 404.
  - Menu: trong `nav()` thêm `("hub.robotics_page", "Robotics")` vào `main` ngay sau "Linh kiện" (endpoint tên
    `robotics_page`; các route con đặt tên bắt đầu `robotics_page_` để mục menu sáng `on`). Chữ tiếng Việt viết thẳng.
- `robotics.html` (kế thừa `base.html`, không JS, không CDN):
  - Đầu trang: `<h1>Robotics</h1>` + dòng `.sub` "N dự án · M sẵn sàng in · K tạm dừng".
  - Lưới thẻ dự án, mỗi thẻ `<article class="card robot-card" data-robot="<slug>">`: ảnh bìa tỉ lệ 4:3 `object-fit:contain`
    nền `var(--bg)`, `loading="lazy"`, `alt` = tên; không ảnh → ô giữ chỗ cùng kích thước ghi "Chưa có ảnh".
    Dưới ảnh: tên thư mục (h3, link `detail_url` nếu có), badge trạng thái (`ok` cho xong/sẵn sàng in, `bad` cho chưa rõ,
    `plain` cho tạm dừng/ý tưởng, mặc định cho đang làm), badge `audience` nếu có, `summary`, dòng "Tiếp: <next>",
    dòng `.muted` "<plates> bàn in · BOM · <todo> TODO · cập nhật <updated>" (bỏ phần trống/0), nút: "Chi tiết"
    (detail_url), "ASSEMBLY.pdf" (`/robotics/file/<slug>/ASSEMBLY.pdf`, mở tab mới) nếu có, "Mô phỏng" (`#sim-<id>`) nếu có `simulation`.
  - `<h2>Mô phỏng</h2>`: thẻ `data-sim="<id>"` `id="sim-<id>"`: ảnh (nếu có), tiêu đề, badge trạng thái, `note`,
    các nút link (`target="_blank" rel="noopener"`), link "README" và "Giáo án" nếu có.
  - Mọi `<a href="http...">` có `target="_blank" rel="noopener"`.
- CSS: thêm khối `/* robotics */` cuối `style.css`, lớp tiền tố `robot-` / `sim-`, chỉ dùng biến token, có
  `@media (max-width:600px)` 1 cột; không hex.

# Không làm
- Không sửa `tests/`, `toolhub/robotics.json`, `toolhub/__init__.py`, `toolhub/workspace.py`, template khác, `../maker/`.
- Không thêm thư viện, không gọi mạng, không nút ghi/sửa dữ liệu.
- Giữ nguyên thay đổi chưa commit trong `views.py`, `style.css`, `templates/overview.html`, `tests/test_products_reports.py`
  (vừa gỡ trang /ops – KHÔNG khôi phục ops).

# Tiêu chí PASS
- Gate exit 0.
- Claude tự chạy Toolhub, chụp ảnh `/robotics` (rộng 1280 px và 390 px) để duyệt.
