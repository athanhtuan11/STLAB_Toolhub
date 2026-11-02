---
task: toolhub-products-reports
cwd: studio
allow:
  - "toolhub/products.py"
  - "toolhub/mdrender.py"
  - "toolhub/views.py"
  - "toolhub/templates/projects.html"
  - "toolhub/templates/project-detail.html"
  - "toolhub/templates/reports.html"
  - "toolhub/templates/report-doc.html"
  - "toolhub/static/app.js"
  - "toolhub/static/ops.js"
  - "toolhub/static/research.js"
  - "toolhub/static/style.css"
  - "data/.gitkeep"
gate: '.venv\Scripts\python.exe tests\test_products_reports.py && .venv\Scripts\python.exe tests\test_library_pages.py && .venv\Scripts\python.exe tests\test_ops.py && .venv\Scripts\python.exe tests\test_research.py'
timeout_min: 30
max_rounds: 2
executor: auto
read: ["docs/reports"]
---

# Mục tiêu
Toolhub (Flask, `studio/toolhub/`) thêm 3 thứ Tuan đã duyệt 2026-11-02 (xem `docs/reports/toolhub-ui-gap-review.md`):
(1) theo dõi vòng đời mẫu in trên trang dự án, (2) trang đọc báo cáo `docs/reports/`, (3) báo lỗi rõ thay vì nuốt lỗi.
Gate `tests/test_products_reports.py` do Claude viết – **KHÔNG sửa file test**. Đọc `studio/CLAUDE.md` trước.

# Yêu cầu
## 1. Vòng đời mẫu in – module mới `toolhub/products.py` (chỉ thư viện chuẩn)
- `STAGES = ("thiet-ke", "in-thu", "da-duyet", "da-dang", "dang-ban")`, nhãn tiếng Việt tương ứng
  `Thiết kế, In thử, Đã duyệt, Đã đăng, Đang bán` (dict `LABELS`).
- `store_path()` = biến môi trường `STLAB_PRODUCTS_FILE` nếu có, mặc định `studio/data/products.json`. Đọc mỗi lần gọi
  (không cache lúc import).
- `get(slug)` → dict hoặc None; `all()` → dict; `set_stage(slug, stage)` ghi `{slug: {"stage", "updated": ISO datetime giây,
  "history": [{"stage", "at"}...]}}`. Ghi an toàn: ghi file tạm cùng thư mục rồi `os.replace`; tạo thư mục nếu chưa có;
  UTF-8, `ensure_ascii=False`, indent 2.
- Route `POST /api/products/<slug>/stage/<stage>` trong `views.py`: stage không thuộc STAGES → 400 JSON; slug không có trong
  `ws.projects()` → 404 JSON; hợp lệ → `{"ok": true, "msg": "Đã chuyển <tên dự án> sang <nhãn>"}`. Lỗi không được ghi file.
  (Middleware X-Studio sẵn có đã chặn 403 – không đổi `__init__.py`.)
- `project-detail.html`: khối "Vòng đời mẫu in" – 5 bước theo thứ tự, bước hiện tại có class `current`; mỗi bước là
  `<button data-post="/api/products/<slug>/stage/<stage>" data-confirm="Chuyển sang <nhãn>?" data-reload="1">`. Dự án chưa
  theo dõi vẫn hiện 5 nút (bấm bước đầu là bắt đầu theo dõi). Thêm link `<a href="/quote">Báo giá</a>`.
- `projects.html`: khu "Mẫu in" ở đầu trang liệt kê dự án đã có trong products (tên + nhãn trạng thái + ngày cập nhật, link
  tới trang dự án); chưa có thì hiện câu "Chưa có mẫu in nào được theo dõi". Thẻ dự án bên dưới có nhãn trạng thái nếu có.
- `app.js`: trong handler `button[data-post]`, nếu `btn.dataset.confirm` có → `if (!confirm(btn.dataset.confirm)) return;`
  TRƯỚC khi khóa nút. Không đổi hành vi nút khác.
- `studio/data/.gitkeep` (rỗng). Không tạo `products.json` thật.

## 2. Trang Báo cáo
- Module `toolhub/mdrender.py`: `render(text) -> str` Markdown tối thiểu, chỉ thư viện chuẩn: **escape HTML toàn bộ trước**
  (`html.escape`), rồi: `#`…`####` → h1–h4; bảng `| a | b |` + dòng `|---|` → `<table>` có `<th>/<td>`; danh sách `- ` / `1. `;
  đoạn văn; `**đậm**`, `` `code` ``; khối ```` ``` ```` → `<pre><code>`; link `[x](url)` → `<a href>` CHỈ khi url bắt đầu bằng
  `http://`, `https://` hoặc là đường dẫn tương đối không chứa `:` (còn lại để chữ thường); `target="_blank" rel="noopener"` cho http(s).
- `GET /reports`: liệt kê `docs/reports/*.md` (bỏ `*.spec.md`), mới sửa trước; mỗi dòng: tiêu đề (dòng `# ` đầu tiên), tên file,
  ngày sửa; link `/reports/<name>`. Template `reports.html` kế thừa `base.html`.
- `GET /reports/<name>`: `name` phải khớp `^[a-z0-9][a-z0-9-]*\.md$`, không kết thúc `.spec.md`, file phải nằm đúng trong
  `docs/reports/` → render `report-doc.html` (kế thừa base, nội dung `mdrender.render`, đánh dấu `|safe` chỉ ở chỗ này).
  Sai → 404.
- `nav()` trong `views.py`: thêm `("hub.reports", "Báo cáo nghiên cứu")` vào `more` (endpoint tên `reports`, trang chi tiết
  endpoint `reports_doc`).
- CSS bảng/heading tối thiểu trong `style.css` nếu cần (giữ kiểu hiện có).

## 3. Báo lỗi rõ
- `ops.js`: `refresh()` và `pollTimeline()` không được `catch{}` rỗng – khi lỗi hiện một dòng `Không tải được dữ liệu điều hành
  (<lỗi>)` vào khu `#log` (dùng class `toast err` như app.js) hoặc phần tử thông báo trên trang; không spam: tối đa 1 thông báo
  mỗi 30 s.
- `research.js` nút `#research-scan`: kiểm `r.ok`; OK → toast "Đang quét – tải lại sau 1 phút"; lỗi/không kết nối →
  toast class `toast err` "Không quét được (HTTP <mã>)" hoặc "Không kết nối được Toolhub".

# Không làm
- Không sửa `tests/`, `toolhub/__init__.py`, `quote.py`, `printprep.py`, `workspace.py` (chỉ gọi hàm có sẵn).
- Không thêm thư viện vào pyproject. Không chạy server thật, không ghi vào `maker/` hay `docs/`.
- Không làm nút đăng MakerWorld / OTA.

# Tiêu chí PASS
- Gate exit 0 (4 test). Claude tự kiểm thêm: `node --check` 3 file JS, chạy Toolhub xem trang.
