---
task: curriculum-web
cwd: maker/english-teacher/server
allow:
  - "live/curriculum.py"
  - "live/curriculum_web.py"
  - "live/bridge.py"
  - "live/static/curriculum.css"
  - "live/static/curriculum.js"
  - "deploy/nginx-engteacher.conf"
  - "deploy/README.md"
gate: "runtime\\.venv\\Scripts\\python.exe -X utf8 test_curriculum_web.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_seed_lessons.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_lesson_advance.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_curriculum.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_roadmap.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_switch.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_topic.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_detour.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_progress.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_public_access.py"
timeout_min: 40
max_rounds: 2
executor: coder
---

# Mục tiêu
Tuan (2026-11-15): "xây dựng giáo trình tiếng Anh trên giao diện web … lên web chọn bài học để eng teacher focus vô đó dạy".
Trang `/curriculum` chạy trên chính server Cú Bông (aiohttp trong `live/bridge.py`, cổng HTTP 8003; ra internet qua đường hầm
VPS 127.0.0.1:18003 → `https://engteacher.mamnoncaynho.com/curriculum`). Người lớn xem giáo trình Seed (3 chặng × 8 unit),
xem giáo án, bấm **"Cú Bông dạy bài này"** → **ghim** bài cho một máy tới khi bấm "Bỏ ghim".
Mockup Tuan đã duyệt: `../../../docs/reports/english-curriculum-web/mockup.png` (+ `mockup.html`). Thiết kế cho điện thoại trước.

# Đầu vào (KHÔNG sửa)
- Nội dung: `../../../stlab/english-curriculum/seed/units.yaml` (levels → units: id, theme, theme_vi, core, plus, patterns,
  song, make, tell, can_do; level: id, name, age) và `seed/lesson-plans/<unit-id>-*.md` (giáo án, mục `## ` = phần/buổi).
- Bài máy dạy: `../lessons-seed/<unit-id>-<slug>.md` (khóa bài = tên file không đuôi, vd `s1-u3-colours`) + `ROADMAP.md`.
- `data/devices.json` = {mac: biệt danh}. `data/learners.json` = hồ sơ (dữ liệu thật – test dùng file tạm qua tham số).
- Gate chính `test_curriculum_web.py` là đặc tả chi tiết – đọc kỹ.

# Yêu cầu
1. **`live/curriculum.py`** (giữ nguyên hành vi cũ, mọi test cũ phải PASS):
   - `pin(device, lesson_id)`: nhận khóa bài đầy đủ (`s1-u3-colours`) hoặc id unit ngắn (`s1-u3` → bài lessons-seed có tiền tố
     `s1-u3-`); không có → `ValueError`. Lưu `learners.json` khóa gốc `"pins": {device: {"lesson_id", "at"}}` (at = ISO phút).
     `unpin(device)`, `pin_info(device)` → dict hoặc None. Có khóa `self.lock` như các hàm khác.
   - `start(nickname, device=None)`: nếu `device` có ghim → dạy bài ghim: tự mới = vocab bài đó chưa có trong `L["taught"]`
     (tối đa như lộ trình, 2 từ/lần theo cách `_next_new` đang làm); hết từ → `mode="review"`, `new=[]`, `review` ⊂ vocab bài ghim
     (không nhảy sang bài khác). Kết quả thêm `pinned: True`, `lesson_id` = bài ghim, `instructions` = chỉ dẫn bài đó (như
     `_start_roadmap`: `_guide_new`, `today_plan`, TODDLER/OLDER mode). Từ dạy xong vẫn ghi vào `taught` như thường.
     Không có ghim / không truyền device → y như cũ. Áp dụng cả hồ sơ theo biệt danh lẫn theo máy (không biệt danh).
     Bài tự do (`free-lesson.on`) đang bật mà máy bị ghim → ghim thắng (người lớn đã chọn).
   - `progress(nickname, device=None)` → `{lesson_id: {"taught": n, "total": m}}` (m = số từ vocab bài; n = số từ đó trong
     `taught`); hồ sơ chưa có → `{}`.
2. **`live/curriculum_web.py` (mới)** – `setup(app, *, cur, seed_dir, devices, active)`:
   `devices()` → {mac: tên}; `active(mac)` → phiên đang mở (có `async send_lesson(text)`) hoặc None.
   - Route: `GET /curriculum` (danh sách), `GET /curriculum/{unit}` (unit khớp `^s[1-3]-u[1-8]$`, khác → 404),
     `POST /curriculum/login`, `POST /curriculum/logout`, `POST /curriculum/api/pin` {device, lesson}, `POST /curriculum/api/unpin`
     {device}, static `/curriculum/static/` (css/js). Không đọc file theo đường dẫn từ URL ngoài whitelist unit id.
   - **PIN**: `os.environ["STLAB_CURRICULUM_PIN"]` đọc lúc xử lý yêu cầu; không đặt → mọi route trả 503 "Trang giáo trình chưa bật".
     Chưa đăng nhập: GET trả form PIN (`name="pin"`), API trả 401. Đúng PIN → cookie phiên ký HMAC-SHA256 (khóa bí mật sinh ngẫu
     nhiên lúc khởi động bằng `secrets`, cookie chứa hạn + chữ ký, KHÔNG chứa PIN), `HttpOnly; SameSite=Strict; Path=/curriculum`,
     `Secure` khi `X-Forwarded-Proto: https`; hạn 30 ngày. So PIN và chữ ký bằng `hmac.compare_digest`. Sai PIN → 401;
     ≥ 10 lần sai trong 10 phút (toàn cục – sau đường hầm mọi IP là 127.0.0.1) → 429 tới khi hết cửa sổ.
   - **CSRF**: mọi POST phải có header `Origin` mà host:port trùng `Host` của yêu cầu, khác/thiếu → 403.
   - Trang danh sách (theo mockup màn 1): ô mỗi máy `data-device="<mac>"` (tên từ devices.json, escape HTML): đang dạy bài nào,
     `data-pinned` + nhãn "📌 Ghim bởi người lớn" + giờ khi có ghim, "đang trong buổi học" khi `active(mac)` khác None, nút
     Bỏ ghim; 3 tab `data-level="s1|s2|s3"` (tên + tuổi từ units.yaml); mỗi unit 1 thẻ `data-unit="<id>"` (số, theme · theme_vi,
     từ core, tiến độ từ `cur.progress` của biệt danh máy đầu tiên: đã học / đang dạy / n/m từ / chưa học) link tới trang bài.
   - Trang bài (màn 2): theme, theme_vi, cấp + tuổi, nút lớn `data-pin` "🦉 Cú Bông dạy bài này", bảng Core/Plus/Mẫu câu/
     Bài hát/Make & Tell/Bé làm được; giáo án: render `lesson-plans/<id>-*.md` bằng `markdown_it` (đã có trong runtime),
     mỗi mục `## ` thành `<details data-session>` gập/mở (tiêu đề = summary). Tắt HTML thô trong markdown (`html=False`).
   - Màn 3: bấm nút ghim → bảng chọn máy (radio theo devices) + câu giải thích "đổi ngay, giữ tới khi Bỏ ghim" → `fetch` POST
     `api/pin` (JS `live/static/curriculum.js`, không thư viện ngoài, có `Origin` tự động của trình duyệt). 1 máy thì chọn sẵn.
   - `api/pin`: máy không có trong `devices()` → 400; bài không có → 400; OK → `cur.pin(...)`, nếu `active(mac)` có phiên →
     `await sess.send_lesson("[lesson] An adult picked a lesson on the web: <title>. Switch to it now, warmly. " + instructions)`
     với instructions lấy từ `cur.start(<biệt danh>, device=mac)` (hoặc hàm riêng không đếm thêm buổi – ưu tiên không cộng buổi).
     Trả JSON `{ok, lesson_id, pushed}`.
   - CSS `live/static/curriculum.css`: biến màu ở `:root` (lấy đúng giá trị token của Toolhub `studio/toolhub/static/tokens.css`
     – nền tối), chữ hệ thống; bố cục 1 cột rộng tối đa ~520 px, nút ≥ 44 px; không tải gì từ CDN.
3. **`live/bridge.py`**: `ACTIVE_SESSIONS: dict[mac, Session]` – thêm khi phiên biết `device_id`, xóa khi đóng (finally);
   `begin_nick` gọi `CUR.start(nick, device=self.device_id or None)`; trong `main()` gọi
   `curriculum_web.setup(app, cur=CUR, seed_dir=<WS>/stlab/english-curriculum/seed (env STLAB_CURRICULUM_SEED ghi đè),
   devices=_devices_load (chỉ mac→tên), active=ACTIVE_SESSIONS.get)` trước `runner.setup()`. Gửi `send_lesson` từ web: chạy trong
   cùng event loop; nếu phiên đang có `pending_lesson`/đang nói thì đặt `pending_lesson` để `flush_lesson` gửi khi hợp lệ – không
   cắt ngang giữa câu cô đang nói. Log 1 dòng `[CURRICULUM] ghim <mac> <lesson>`.
4. **`deploy/nginx-engteacher.conf`**: thêm `location /curriculum { proxy_pass http://127.0.0.1:18003; ... }` (Host,
   X-Forwarded-Proto như các khối khác) TRƯỚC `location /` (vẫn 404). `deploy/README.md`: 3 dòng cách bật (đặt
   `STLAB_CURRICULUM_PIN` trên máy lab, chép conf lên VPS, `nginx -t && systemctl reload nginx`).

# Không làm
- Không sửa test, `units.yaml`, `lessons-seed/`, `lesson-plans/`, `data/*.json` thật, firmware, `free-lesson.*`, `live.on`.
- Không thêm thư viện mới (aiohttp, jinja2, markdown_it, pyyaml đã có trong runtime). Không CDN.
- Không đặt PIN/khóa trong mã hay file. Không tự khởi động lại bridge đang chạy, không SSH lên VPS. Không commit.

# Tiêu chí PASS
- Lệnh gate exit 0 (test mới + 9 test cũ).
- Claude tự chạy app thử (aiohttp cục bộ, PIN tạm), chụp `/curriculum`, `/curriculum/s1-u3` ở khổ điện thoại so với mockup.
