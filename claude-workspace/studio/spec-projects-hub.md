---
task: projects-hub
cwd: studio
allow:
  - "toolhub/wiring.py"
  - "toolhub/robotics.py"
  - "toolhub/views.py"
  - "toolhub/templates/projects.html"
  - "toolhub/templates/project-guide.html"
  - "toolhub/templates/robotics.html"
  - "toolhub/static/app.js"
  - "toolhub/static/hub.js"
  - "toolhub/static/style.css"
gate: ".venv\\Scripts\\python.exe tests\\test_projects_hub.py && .venv\\Scripts\\python.exe tests\\test_robotics.py && .venv\\Scripts\\python.exe tests\\test_print_home.py && .venv\\Scripts\\python.exe tests\\test_products_reports.py && .venv\\Scripts\\python.exe tests\\test_pin_diagram.py"
timeout_min: 30
max_rounds: 2
executor: auto
---

# Mục tiêu
Gộp trang `/robotics` vào `/projects` thành một trang "Dự án" có thẻ ảnh + chip lọc nhóm, thêm mục "Chạy được – làm theo được",
và trang hướng dẫn 7 bước cho học sinh `/projects/<slug>/guide` có sơ đồ đấu dây WireViz sinh từ file YAML của dự án.
Mockup Tuan đã duyệt: `../docs/reports/projects-merge/mockup-list.png`, `mockup-guide.png` (HTML cùng tên để xem bố cục).

# Đầu vào (đã có, KHÔNG sửa)
- `toolhub/robotics.json`: manifest, đã thêm `groups` + trường mới mỗi dự án: `group`, `works` (bool, mặc định False),
  `works_note`, `difficulty`, `duration`, `guide` (đường dẫn tương đối thư mục dự án tới GUIDE.md), `wiring` (yaml), `title`, `cover`.
- `../maker/english-teacher/hardware/wiring-s3.yaml`: định dạng sơ đồ dây (xem chú thích đầu file). `../maker/english-teacher/GUIDE.md`.
- Mẫu WireViz đang chạy: `toolhub/pin_diagram.py` (`_ensure_dot`, `wv_parse(..., return_types="svg")`, `_clean_wireviz`, cache theo mtime).
- Gate: `tests/test_projects_hub.py` (chính), `tests/test_robotics.py`, `tests/test_print_home.py` – đọc kỹ, nó là đặc tả chi tiết.

# Yêu cầu
1. **`toolhub/wiring.py` (mới)**
   - `load(path) -> dict {title, groups, parts, wires, notes}`. Mỗi dây: `from_part, from_pin, to_part, to_pin, from_label, to_label,
     level, color, color_name, group, group_label, note` (note thiếu → ""). Tách `"part.pin"` theo dấu chấm ĐẦU TIÊN.
   - `level` ∈ {5v, 3v3, gnd, tin-hieu, loa}; `color` ∈ RD OG BK YE GN BU VT TQ WH PK GY BN; tên màu tiếng Việt đúng bảng trong gate.
     Part/pin/group/level/màu sai hoặc thiếu dấu chấm → `ValueError` có thông báo rõ.
   - `svg(path, group=None) -> str`: dựng dict WireViz (mỗi part = 1 connector, pins theo thứ tự yaml, nhãn = label; mỗi dây = 1
     cable 1 sợi đúng màu; connections part→cable→part), render SVG inline giống `pin_diagram.wiring_svg` (bỏ `<?xml`/DOCTYPE).
     `group` = chỉ các dây nhóm đó (và chỉ các part có dây trong nhóm). group lạ → ValueError. Cache theo (path, mtime, group).
2. **`toolhub/robotics.py`**: giữ API cũ; thêm khóa `group, group_label, works, works_note, difficulty, duration, guide_url`
   vào mỗi dự án của `data()`; `guide_url = /projects/<slug>/guide` chỉ khi manifest có `guide` VÀ file tồn tại. Kiểm: group phải
   có trong `groups`; `guide`/`wiring` phải nằm trong thư mục dự án (chặn `..`) → ValueError. Thêm hàm trả danh sách thẻ cho trang
   gộp: manifest + mọi `workspace.projects()` chưa có trong manifest (nhóm `khac` nếu rel bắt đầu `maker/`, ngược lại `tools`).
3. **`/projects` (views.py + projects.html)** theo mockup-list: chip `data-filter` (all + từng nhóm có dự án, kèm số đếm), container
   có `data-active-filter` lấy từ `?nhom=` (chỉ nhận khóa nhóm hợp lệ, khác → `all`, không phản chiếu chuỗi lạ); mục "Chạy được"
   (thẻ `data-works` cho dự án works=True, nút xanh "Hướng dẫn làm" khi có guide_url); lưới thẻ: mỗi dự án đúng 1 thẻ
   `data-project="<slug>" data-group="<nhóm>"` (ảnh lazy, trạng thái, cấp học, mô tả, bước tiếp, nút Chi tiết/ASSEMBLY.pdf/Mô phỏng);
   dòng dev nhỏ (link `/projects/<slug>` "CLAUDE.md" + nút `data-post="/api/open/<slug>"` VS Code + mở file chính nếu có).
   Giữ khu "Mẫu in" (sản phẩm theo dõi) và khu Mô phỏng (`data-sim`, như robotics.html cũ). Thẻ trong mục "Chạy được" KHÔNG
   dùng thuộc tính `data-project` (để mỗi dự án chỉ 1 `data-project`).
4. **`/robotics`** → redirect 302 tới `/projects?nhom=robotics`. Bỏ "Robotics" khỏi menu "Thêm". Các route `/robotics/img|file|sim/...` giữ nguyên;
   trang README/giáo án mô phỏng: link quay lại = `/projects?nhom=robotics`.
5. **`/projects/<slug>/guide`** (template mới `project-guide.html`) theo mockup-guide: hero (ảnh, h1 = title, nhãn works_note,
   ô thông tin nhanh: cấp học / thời gian / độ khó / số bàn in – trống thì ghi "TODO"); render GUIDE.md bằng `mdrender`, mỗi `## `
   thành `<section>` có `<h2 id="...">` + ô `data-step-done`; section có tiêu đề chứa "An toàn" thêm class `guide-safe` (khung đỏ dùng
   token màu); mục lục `data-toc` link tới các id. Dòng `<!-- wiring -->` thay bằng khối `data-wiring`: SVG toàn bộ + SVG từng nhóm
   (`data-wire-svg="<nhóm>"`, ẩn sẵn), nút lọc `data-wire-group="all|<nhóm>"`, ghi chú `notes`, bảng dây (mỗi dòng `data-wire="<i>"`,
   `<input type="checkbox">`, số thứ tự, từ (label + pin), đến, vạch màu + tên màu, ghi chú). Không có guide → 404.
6. **JS `static/hub.js`** (nạp ở 2 trang): chip lọc ẩn/hiện thẻ theo `data-group`; nút lọc dây đổi SVG; ô tích dây + ô bước lưu
   `localStorage` theo slug – MỌI truy cập localStorage nằm trong try/catch, trang vẫn chạy khi bị chặn.
7. **CSS**: lớp mới tiền tố `hub-`, `guide-`, `wiring-`; chỉ dùng biến token (`var(--...)` trong `static/tokens.css`), KHÔNG hex.
   Màu vạch dây trong bảng: dùng tên màu WireViz → biến CSS hoặc thuộc tính `style` inline từ bảng màu cố định trong wiring.py là
   được (không nằm trong style.css).

# Không làm
- Không sửa `robotics.json`, file trong `../maker/`, các file `tests/`, `pin_diagram.py`, `tokens.css`, `design/`.
- Không đổi số chân/màu/nội dung trong YAML hay GUIDE.md. Không thêm thư viện mới (WireViz, PyYAML, Graphviz đã có).
- Không xóa route `/robotics/img|file|sim`. Không commit.

# Tiêu chí PASS
- Lệnh gate exit 0 (5 test).
- Claude tự chạy Toolhub, chụp `/projects`, `/projects?nhom=robotics`, `/projects/maker--english-teacher/guide` so với mockup.
