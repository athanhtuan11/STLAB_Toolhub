---
task: ops-page
cwd: studio
allow:
  - "toolhub/ops.py"
  - "toolhub/views.py"
  - "toolhub/templates/ops.html"
  - "toolhub/templates/overview.html"
  - "toolhub/templates/base.html"
  - "toolhub/static/ops.js"
  - "toolhub/static/style.css"
gate: ".venv/Scripts/python.exe tests/test_ops.py && .venv/Scripts/python.exe tests/test_org_board.py && .venv/Scripts/python.exe tests/test_library_pages.py"
timeout_min: 30
max_rounds: 2
executor: auto
---

# Mục tiêu
Bước 2–3 của trung tâm điều hành (`docs/reports/ops-center-design.md` mục 3–4, Tuan duyệt "từ 1 tới hết"
2026-11-01): trang `/ops` 6 khung + API + dải tóm tắt ở trang chính, để Tuan thấy việc đang chạy/chờ duyệt mà không
phải hỏi.

# Đầu vào
- Gate `tests/test_ops.py` (Claude viết, KHÔNG sửa) – đặc tả chính xác route + khóa JSON.
- Thiết kế: `../docs/reports/ops-center-design.md` mục 3; mockup `design/mockups/ops-center.html` (bố cục, màu);
  token màu/chữ `design/DESIGN.md` + `toolhub/static/tokens.css` (luôn giao diện tối).
- Kho sự kiện: `../tools/org/events.py` (`recent`, `list_approvals`, `resolve`) – import bằng cách thêm
  `<workspace>/tools/org` vào `sys.path` trong `ops.py`; KHÔNG sửa events.py.
- Run delegate: `%LOCALAPPDATA%/stlab-usage/delegate-runs/<YYYYmmdd-HHMMSS-task>/` với `state.json`
  (`state`, `pid`, `executor`...) khi đang chạy, `result.json` (`verdict`, `task`, `escalate`...) khi xong,
  `handoff.md`. Xem cách `toolhub/usage.py` đọc (hàm `_is_process_alive`, `_read_json` – dùng lại, không chép).

# Yêu cầu
- Module mới `toolhub/ops.py` chứa logic; `views.py` chỉ thêm route mỏng:
  - `GET /ops` → `ops.html` có 6 khung `data-widget`: approvals, running, board, timeline, org, commits.
  - `GET /api/ops` → `{approvals, running, board, timeline, commits, summary}` như gate.
    - `approvals`: mục `state == "cho"`, mới nhất trước.
    - `running`: run chưa có `result.json` và `pid` còn sống: `{task, run, executor, seconds}` (giây tính từ mtime
      `state.json` hoặc thời điểm trong tên thư mục).
    - `board`: `dang_chay` (= running), `xong` (PASS), `loi` (FAIL, hoặc chưa có result mà pid chết = bị cắt ngang),
      `bao_len` (ESCALATE, `note` = trường `escalate`). Mỗi mục `{task, run, verdict?, note?}`. Tối đa 20 mục mới nhất mỗi
      cột. `task` lấy từ `result.json["task"]`, không có thì phần tên thư mục sau `YYYYmmdd-HHMMSS-`.
    - `timeline`: 50 sự kiện mới nhất (`events.recent(50)`).
    - `commits`: 10 commit cuối `git log -10 --format=%h%x09%ad%x09%s --date=format:%Y-%m-%d %H:%M` chạy trong
      workspace (subprocess, hạn 5 s, lỗi → danh sách rỗng); `{hash, date, subject}`.
    - `summary`: `{cho_duyet, dang_chay, loi}` (loi = số mục cột `loi`).
  - `GET /api/ops/timeline?after=<id>` → `{timeline: [...]}` các sự kiện id > after.
  - `POST /api/ops/approvals/<id>` body `{state: da-duyet|tu-choi, note?}` → `events.resolve(id, state, "tuan", note)`;
    state sai → 400; id không có → 404. (X-Studio đã được `__init__.py` kiểm cho mọi POST – không sửa `__init__.py`.)
  - `GET /api/ops/run/<run>/handoff` → nội dung `handoff.md` dạng text/plain; `run` chỉ nhận
    `^\d{8}-\d{6}-[a-z0-9-]+$`, ngoài ra 400; không có file 404.
- `ops.html` + `static/ops.js` (JS thuần, không thư viện ngoài, không CDN):
  - Làm mới 5 s: timeline dùng `?after=` (nối thêm, giữ tối đa 200 dòng), phần khác gọi lại `/api/ops`.
  - Khung approvals: câu hỏi, nguồn, link ref, nút Duyệt / Từ chối + ô ghi chú; POST kèm header `X-Studio: 1`.
  - Khung board: 4 cột, bấm mục → mở handoff trong khung xem (pre).
  - Khung org: tái dùng dữ liệu `/api/org` (hạn mức theo nguồn + cảnh báo `attention`), không viết lại logic.
  - Mỗi khung có nút ẩn/hiện + kéo lên/xuống (nút ↑ ↓ là đủ); lưu thứ tự + ẩn vào `localStorage` khóa `ops-layout`.
  - Mọi chữ hiển thị tiếng Việt có dấu; escape HTML mọi dữ liệu từ API (không dùng innerHTML với chuỗi chưa escape).
- `overview.html`: dải tóm tắt có thuộc tính `data-ops-summary`, link `href="/ops"`: "N cần duyệt · N đang chạy ·
  N lỗi" (render phía server từ cùng hàm trong ops.py).
- `base.html`: thêm mục menu "Điều hành" → `/ops` cạnh các mục hiện có.
- `style.css`: thêm khối CSS riêng có chú thích `/* ops */`, dùng biến từ tokens.css, không sửa rule cũ.

# Không làm
- Không sửa `tests/`, `toolhub/__init__.py`, `toolhub/usage.py`, `../tools/org/`.
- Không đọc/hiển thị nội dung prompt, mã hay log dài ngoài `handoff.md`.

# Tiêu chí PASS
- Gate exit 0; `node --check toolhub/static/ops.js` (Claude tự chạy).
- Claude chạy Toolhub, chụp ảnh `/ops` để Tuan duyệt.
