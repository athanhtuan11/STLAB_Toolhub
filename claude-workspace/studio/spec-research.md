---
task: research-page
cwd: studio
allow:
  - "toolhub/research.py"
  - "toolhub/views.py"
  - "toolhub/templates/research.html"
  - "toolhub/static/research.js"
  - "toolhub/static/style.css"
gate: ".venv\\Scripts\\python.exe tests\\test_research.py && .venv\\Scripts\\python.exe tests\\test_ops.py && .venv\\Scripts\\python.exe tests\\test_library_pages.py"
timeout_min: 30
max_rounds: 2
executor: auto
---

# Mục tiêu
Trang Toolhub **"Nghiên cứu"** `/research` cho agent research-scout (Tuan 2026-11-01): xem bản "Gợi ý cho Tuan" tuần
mới nhất + danh sách tin đã quét, bấm **Quan tâm / Bỏ qua** (agent học ưu tiên chủ đề), nút **Quét ngay**.

# Đầu vào
- Gate `tests/test_research.py` (Claude viết, KHÔNG sửa) – đặc tả chính xác route, khóa JSON, hành vi.
- API dữ liệu: `../tools/research-scout/store.py` (`list_items`, `set_status`, `latest_digest`, `topics`, `connect`) –
  import bằng cách thêm `<workspace>/tools/research-scout` vào `sys.path` trong `research.py`; KHÔNG sửa store.py.
- Mẫu trang có sẵn cùng kiểu: `toolhub/ops.py` + `templates/ops.html` + `static/ops.js` (học cách làm, không sửa).

# Yêu cầu
- `toolhub/research.py` chứa logic; `views.py` chỉ thêm route mỏng + mục menu **"Nghiên cứu"** → `/research` (thêm vào
  danh sách `main` cạnh "Điều hành", chữ tiếng Việt viết thẳng, không `\u` escape).
- `GET /research`: khung 1 "Gợi ý tuần <week>" (model, ngày tạo, nội dung AI hiển thị dạng văn bản đã escape, giữ xuống
  dòng); khung 2 danh sách tin (mặc định ẩn `bo-qua`, điểm cao trước): tiêu đề là link `target="_blank"
  rel="noopener noreferrer"`, nguồn, chủ đề, điểm (1 chữ số thập phân), tóm tắt (văn bản thuần, cắt 200 ký tự), nút Quan tâm /
  Bỏ qua; bộ lọc chủ đề + trạng thái (JS gọi API). Không có digest → dòng "Chưa có bản gợi ý – chạy digest.py hoặc chờ
  Chủ nhật 07:30". DB rỗng/không có file → trang vẫn 200.
- `GET /api/research?topic=&status=` → `{items, digest, topics}`; không truyền status → loại `bo-qua`.
- `POST /api/research/<id>/status` body `{status: quan-tam|bo-qua|moi}` → 200; sai 400; id không có 404 (X-Studio đã do
  `__init__.py` kiểm).
- `POST /api/research/scan` → chạy nền (subprocess.Popen, không chờ, cửa sổ ẩn `CREATE_NO_WINDOW`) lệnh
  `STLAB_RESEARCH_SCAN_CMD` nếu có (shell) hoặc `python <workspace>/tools/research-scout/scan.py`; trả 202 `{started: true}`.
- `static/research.js`: JS thuần, dựng DOM bằng `textContent` (không innerHTML với dữ liệu); POST kèm `X-Studio: 1`;
  nút Quét ngay → thông báo "Đang quét – tải lại sau 1 phút".
- `style.css`: khối `/* research */` mới dùng biến tokens.css, không sửa rule cũ.
- Mọi chữ hiển thị tiếng Việt có dấu.

# Không làm
- Không sửa `tests/`, `toolhub/__init__.py`, `toolhub/ops.py`, `../tools/`.

# Tiêu chí PASS
- Gate exit 0; Claude tự `node --check` + chụp ảnh trang.
