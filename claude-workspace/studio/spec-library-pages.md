---
task: toolhub-library-list-detail
cwd: studio
allow: ["toolhub/views.py", "toolhub/workspace.py", "toolhub/templates/library.html", "toolhub/templates/library-detail.html"]
read: ["tools/robotics-cad/library", "studio/design"]
gate: '.venv\Scripts\python.exe tests\test_library_pages.py && .venv\Scripts\python.exe tests\test_pin_diagram.py && .venv\Scripts\python.exe tests\test_pinout.py'
executor: opencode
timeout_min: 25
max_rounds: 2
---

# Mục tiêu
Tab "Linh kiện" (`/library`) đang hiện toàn bộ chi tiết mỗi linh kiện → dài, nặng. Tuan (2026-10-28): danh sách chỉ ghi
**tên + thông tin cơ bản**; bấm vào thẻ mới mở **trang chi tiết** (nội dung đầy đủ như thẻ hiện tại). Đọc 3 file test để
biết đúng hành vi (`tests/test_library_pages.py` mới; 2 test cũ đã chuyển sang trang chi tiết).

# Yêu cầu
- `workspace.py`: tách `library()` thành phần nhẹ cho danh sách (KHÔNG gọi `pin_diagram`/`pinout` – WireViz chậm) và
  `library_item(id)` trả 1 linh kiện đầy đủ (có `pinout` như hiện nay) hoặc `None`. Thêm cho mỗi linh kiện ở danh sách:
  `has_pinout` (có `chan`), `thumb` (URL `/library/img/<anh_chan.file>` nếu có `anh_chan`), `todo_count`,
  `key_specs` = tối đa 3 cặp (nhãn, giá trị) đầu tiên của `thong_so`, giá trị cắt ~60 ký tự + "…".
- `views.py`: `GET /library/<id>` → `library-detail.html`; id không có → 404. Giữ `/library` và `/library/img/<path>`
  (route ảnh phải khớp trước route id – kiểm thứ tự/converter).
- `library.html` (danh sách): giữ phần đầu trang, nút, bộ lọc theo loại (`data-type`). Thêm ô tìm kiếm `<input id="q"
  type="search" placeholder="Tìm linh kiện…">` lọc theo tên/id bằng JS thuần (kết hợp với bộ lọc loại). Mỗi thẻ là
  `<a class="card …" href="/library/<id>" data-type=…>` gồm: chấm trạng thái model + tên (h3) + badge loại; ảnh nhỏ
  `thumb` (cao ~96 px, `object-fit:contain`, `loading="lazy"`, alt = tên) nếu có; badge STEP/STL/"chưa có model";
  badge "Sơ đồ chân" nếu `has_pinout`; ≤ 3 dòng `key_specs` (chữ nhỏ); "N TODO" (badge warn) nếu có. Không liệt kê
  TODO, không nguồn, không sơ đồ. Lưới `minmax(240px,1fr)`. Thẻ link: không gạch chân, focus nhìn thấy, hover nhẹ
  (chỉ `var(--…)`, inline style hoặc `<style>` trong template – KHÔNG sửa style.css).
- `library-detail.html` (mới, extends base.html): link "← Linh kiện" (`href="/library"`), tiêu đề tên + badge loại,
  rồi **toàn bộ nội dung thẻ chi tiết hiện có** (hộp bao, bảng thông số với `labels`, TODO, Sơ đồ chân, nguồn, đường
  dẫn model). Đưa dict `labels` sang dùng chung (vd `{% include %}`/macro hoặc truyền từ views) để không chép 2 lần.
  Sơ đồ đấu WireViz trong khung `overflow-x:auto`.
- Footer chú thích danh mục giữ ở trang danh sách.

# Không làm
- KHÔNG sửa `tests/`, `components.yaml`, `static/style.css`, `static/tokens.css`, `toolhub/pin_diagram.py`, `toolhub/pinout.py`.
- Không thêm thư viện/CDN/build.

# Tiêu chí PASS
- Gate exit 0 (3 test).
- Claude xem ảnh chụp danh sách + trang chi tiết relay.
