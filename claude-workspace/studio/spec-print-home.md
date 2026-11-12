---
task: print-home
cwd: studio
allow:
  - "toolhub/prints.py"
  - "toolhub/views.py"
  - "toolhub/opener.py"
  - "toolhub/templates/*.html"
  - "toolhub/static/*.js"
  - "toolhub/static/style.css"
  - "apps.json"
  - "toolhub/workspace.py"
gate: ".venv/Scripts/python.exe -X utf8 tests/test_print_home.py"
timeout_min: 30
max_rounds: 2
executor: auto
read: ["../maker", "design", "CLAUDE.md"]
---

# Mục tiêu
Tuan 2026-11-12: "quá khó để tìm file CAD để in; giao diện quá nhiều topic nhưng không hữu dụng" → chọn **trang chính = In 3D**:
ô tìm + lưới thẻ bàn in (mới nhất trước), mỗi thẻ có ảnh, tên dự án + tiêu đề, tên bàn, giờ, gam, nút **In** (mở .3mf bằng
Bambu Studio), **CAD** (mở file CAD), **Thư mục**. Menu chỉ còn **In 3D · Dự án · Báo giá · Thêm ▾**; các mục cũ chuyển vào
"Thêm" và trang mới **Công cụ** `/tools`.

# Yêu cầu
1. `toolhub/prints.py`:
   - `list_prints()`: quét `maker/*/` tìm `**/plates/<bàn>/<bàn>.3mf` (bỏ thư mục bắt đầu `_`, bỏ `backup/`, `.venv`, `node_modules`,
     không duyệt sâu hơn 4 cấp dưới thư mục dự án). Mỗi bàn: `project` (tên thư mục dự án), `plate`, `title` (dòng `# ` đầu
     README.md dự án, bỏ dấu `#`), `minutes` (tổng `prediction` giây trong `result.json` → phút, làm tròn; không có → null),
     `grams` (tổng `filaments[].total_used_g` của `sliced_plates`, 1 chữ số thập phân; không có → null), `image_url`
     (`/prints/img/<project>/<plate>` nếu có `preview.png` hoặc `plate_1.png`), `mtime` (mtime file .3mf, số), `cad`
     (danh sách đường dẫn tương đối `maker/<project>/...` các file `.sc` rồi `.FCStd` trong dự án, bỏ `build/`, `backup/`, `_*`).
     Sắp `mtime` giảm dần. Cache theo mtime thư mục, trang phải hiện < 1 s.
   - `resolve(project, plate, what)`: chỉ chấp nhận project có trong `list_prints()`; trả đường dẫn tuyệt đối file .3mf / file
     CAD đầu tiên / thư mục bàn. Không nhận đường dẫn từ web.
2. Route (views.py): `GET /api/prints` → `{"prints": [...]}`; `GET /prints/img/<project>/<plate>` → ảnh (chỉ từ list_prints);
   `POST /api/prints/open` `{project, plate, what: "3mf"|"cad"|"folder"}` → mở bằng ứng dụng: .3mf → Bambu Studio (dùng cơ
   chế `opener`), .sc → SolidCraft (`C:\Program Files\SolidCraft\solidcraft.exe`, thêm opener `solidcraft` vào `apps.json`
   mục `openers` + đuôi `.sc` vào `opener.OPENERS`), .FCStd → FreeCAD (như opener hiện có), thư mục → `explorer`. Biến môi
   trường `STLAB_DRY_OPEN=1` → không chạy gì, trả `{"ok": true, "dry": true, "path": ...}`. Sai tham số → 400/404.
   POST vẫn qua kiểm X-Studio có sẵn.
3. Trang chính `/` (template `prints.html`): tiêu đề "In 3D", ô `<input type="search" id="print-search">` lọc ngay theo
   project/title/plate (không phân biệt hoa thường, bỏ dấu tiếng Việt), lưới thẻ nạp bằng JS từ `/api/prints`. Thẻ: ảnh,
   tên dự án đậm + title nhỏ, tên bàn, "14 ph · 1,5 g" (giờ ≥ 60 ph ghi "3 g 36 ph"), 3 nút. Bấm nút → POST open + báo nhỏ.
   Dòng "Cần chú ý" (`/api/health`, chỉ hiện khi có lỗi) giữ ở đầu trang.
4. `/tools` (template `tools.html`): chuyển nguyên các khối cũ của trang chính: hàng ứng dụng (đèn + Mở), nút tắt mô phỏng
   robotics (`data-sim-shortcut`), ô Nhân sự AI (`/api/org`), thẻ dự án "Đang làm"/dự án khác. Giữ hành vi cũ.
5. Menu (base template): link trực tiếp chỉ `In 3D` (/), `Dự án`, `Báo giá` (/quote) + "Thêm ▾" chứa: Công cụ (/tools),
   Robotics, Linh kiện, Ứng dụng & MCP, Nguồn cộng đồng, Skills & agents,
   Prompt library (giữ mọi link cũ).
6. Trang dự án `/projects/<slug>`: đầu trang là khối "Bàn in" (thẻ giống trang chính, lọc theo dự án) + nút mở từng file CAD;
   nội dung CLAUDE.md/README hiện tại đưa vào `<details><summary>Ghi chú kỹ thuật</summary>…</details>` gập sẵn.
7. Màu/chữ chỉ dùng `var(--…)` từ `static/tokens.css` (không hex). Gọn, chữ to, thẻ rộng ~260 px, hợp màn hình 1366 px.

# Không làm
- Không sửa `tests/`, `toolhub/quote*.py`, template `quote*.html` (việc khác đang làm). Không xóa trang/route cũ.
- Không gọi mạng.

# Tiêu chí PASS
- Gate exit 0. Claude tự chạy thêm toàn bộ `tests/test_*.py` của studio (không hỏng test cũ).

# Bổ sung (Tuan 2026-11-12)
- "Nghiên cứu không cần vì có README rồi, bỏ phần này trên giao diện": bỏ link **Nghiên cứu** (/research) và **Báo cáo nghiên cứu**
  (/reports) khỏi menu và khỏi trang chính/`/tools`. Route cũ vẫn giữ (không xóa mã). Test cũ đã cập nhật theo.
- **Phụ kiện in của linh kiện** (Tuan 2026-11-12: "trong library, từng linh kiện sẽ có bản CAD để in nếu có custom giống như
  SG90 custom arm cho CyberBrick"): `tools/parts-library/components.yaml` có trường `in_3d: [{ten, thu_muc}]` (thư mục tính từ
  `tools/parts-library/`, hiện có `printables/servo-horn-sg90` gắn cho `sg90` và `cb-pg001-servo-9g`).
  - `list_prints()` quét thêm `tools/parts-library/printables/*/` (cùng luật), mỗi bàn thêm `source` = `"du-an"` (maker) hoặc
    `"linh-kien"` (printables), `folder` = đường dẫn tương đối thư mục gốc (vd `tools/parts-library/printables/servo-horn-sg90`);
    `project` = tên thư mục. Với printables, `title` lấy README trong thư mục đó; `resolve()`/`/api/prints/open` nhận cả hai nguồn.
  - Trang `/library/<id>`: đầu trang khối **"CAD để in"** cho mỗi mục `in_3d` (thẻ bàn in như trang chính + nút mở file CAD .sc).
  - Trang `/library`: thẻ linh kiện có `in_3d` gắn thuộc tính `data-printables="<số>"` và nhãn nhỏ "Có CAD in".
  - Trang chính In 3D: thẻ của phụ kiện linh kiện có nhãn "Linh kiện" (tìm "SG90" ra arm servo).
- allow thêm: `toolhub/workspace.py` (đọc in_3d), `toolhub/templates/library*.html`.
