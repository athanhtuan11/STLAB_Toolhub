---
# Đặc tả giao việc – Claude viết 2026-11-17, executor làm. Đường dẫn tương đối tính từ claude-workspace/.
task: english-teacher-session-pin
cwd: maker/english-teacher/server
allow:
  - "live/curriculum.py"
  - "live/curriculum_web.py"
  - "live/static/curriculum.js"
  - "live/static/curriculum.css"
gate: "runtime\\.venv\\Scripts\\python.exe -X utf8 test_session_pin.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_curriculum_web.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_topic.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_curriculum.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_seed_lessons.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_switch.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_roadmap.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_progress.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_free.py && runtime\\.venv\\Scripts\\python.exe -X utf8 test_detour.py"
timeout_min: 25
max_rounds: 2
executor: auto
read: ["stlab/english-curriculum/seed", "maker/english-teacher/lessons-seed"]
---

# Mục tiêu
Cú Bông (máy dạy tiếng Anh cho bé, máy chủ Python `live/`) thêm 2 tính năng:
1. **Ghim từng buổi:** trên trang web `/curriculum/<unit>`, người lớn ghim **một buổi cụ thể** (Buổi 1–8 trong giáo án)
   cho một máy. Máy dạy nội dung đúng buổi đó cho tới khi bỏ ghim / ghim lại.
2. **Bé xin chủ đề → nhảy bài:** khi Gemini gọi `change_topic` (bé/người lớn xin chủ đề khác bằng giọng) mà chủ đề **có trong
   giáo trình**, máy dạy luôn bài đó trong buổi hiện tại (từ vẫn tính tiến độ), web hiện "Đang dạy: <bài> 🙋 bé xin".
   **Không** dời con trỏ lộ trình; hết buổi quay lại lộ trình. Chủ đề ngoài giáo trình → giữ đường vòng như cũ.

# Đầu vào
- `live/curriculum.py` – lớp `Curriculum(data_path, lessons_dir)`: `pin/unpin/pin_info/_pin_of`, `start`, `_build_pinned`,
  `pinned_instructions`, `set_topic`, `end_session`, `finish`, `mark`, `_age`, `_prof`, `today_plan`, `_guide_new`.
  Bài máy = file `maker/english-teacher/lessons-seed/<lesson_id>.md`, dòng đầu `# Seed 1 · Unit 5 – Animals (Con vật)`.
- Giáo án theo buổi: `stlab/english-curriculum/seed/lesson-plans/<lesson_id>.md` (cùng tên file với bài máy), mục
  `## Buổi N – <tiêu đề>` (N = 1..8); sau Buổi 8 còn mục `## Sổ quan sát ...` (không thuộc buổi nào).
- `live/curriculum_web.py` (`setup(app, cur, seed_dir, devices, active)`, `device_cards`, `unit_state`, `unit_html`, `h_pin`),
  `live/static/curriculum.js` (nút `data-pin`, sheet chọn máy, `post("/curriculum/api/pin", ...)`).
- Gate: `test_session_pin.py` (mới, mô tả chính xác hành vi) + các gate cũ phải vẫn PASS.

# Yêu cầu
## A. `Curriculum`
- Tham số mới tùy chọn `plans_dir=None`; mặc định `Path(lessons_dir).resolve().parents[2] / "stlab/english-curriculum/seed/lesson-plans"`.
- `session_plan(lesson_id, n) -> (heading, text) | None`: đọc mục `## Buổi n` (so khớp đầu tiêu đề "Buổi n" + ký tự không phải số),
  `text` = thân mục tới trước `## ` kế tiếp. Không có file/mục → `None`. Không lỗi khi lesson_id lạ.
- `pin(device, lesson_id, session=None)`: `session` phải là `int` (không nhận bool/float/str) có `session_plan` khác None,
  sai → `ValueError`. Lưu `pins[dev] = {"lesson_id", "at", "session": n}`; ghim không có session thì **không** có khóa session
  (ghim lại cả bài xóa session cũ). `pin_info` trả cả `session` khi có. Giữ tương thích ghim cũ (không session).
- Khi máy ghim có session: `start(...)` và `pinned_instructions(...)` trả thêm `"session": n`, `instructions` = như ghim cả bài
  **cộng** đoạn: "An adult chose class session N of this unit's teacher plan. Follow it today, adapted for ONE child at home,
  voice only (no materials: talk about crafts instead of making them). Plan:" + heading + text (cắt tối đa 3000 ký tự).
  Không kèm buổi khác. Tổng instructions < 9000 ký tự.
- `set_topic(nickname, device, topic, words)` – trước nhánh cũ, tìm bài khớp `_match_lesson(L, topic, words)`:
  - Ứng viên theo tuổi: `_age(L) <= 3` → bài id bắt đầu `s1-`; ngược lại `s2-` rồi `s3-`. Không có ứng viên khớp → thử mọi bài.
  - Ưu tiên 1: từ yêu cầu (lower) nằm trong `vocab` của bài (bài đầu tiên theo thứ tự `self.order`).
  - Ưu tiên 2: chuẩn hóa chủ đề (lower, bỏ dấu tiếng Việt bằng `unicodedata` NFD + bỏ dấu kết hợp, `đ`→`d`, bỏ ký tự không
    phải chữ/số) khớp tên tiếng Anh hoặc tên tiếng Việt của bài (phần trong ngoặc ở dòng đầu file; lưu thêm `title_vi`
    lúc nạp): bằng nhau, hoặc chuỗi này chứa chuỗi kia (độ dài ≥ 4).
  - Khớp → ghi `L["detour"] = {"lesson_id": lid, "at": now ISO phút}`, chọn tối đa 1 (tuổi ≤ 3) / 2 từ chưa dạy của bài
    (hết thì lấy từ đầu bài để ôn), **không** đổi `L["lesson"]`, `L["week"]`, con trỏ, `taught`. Trả
    `{"ok": True, "jump": True, "lesson_id": lid, "words": [...], "instructions": ...}`; instructions gồm chỉ dẫn bài
    (`self.lessons[lid]["instructions"]`), câu "The child asked for '<topic>'. Switch now, warmly, to this lesson from our
    curriculum: <title>. Call mark_word for these words as usual.", `_guide_new`, kiểu nói theo tuổi như nhánh cũ.
  - Không khớp → hành vi cũ y nguyên (không có `jump`).
- `detour_info(nickname=None, device=None) -> {"lesson_id","at"} | None`.
- Xóa `detour` trong `end_session`, `finish` và đầu `start`.

## B. Web
- `h_pin`: nhận `session` tùy chọn (JSON số nguyên); sai → 400 `{"error": "session"}`. Trả thêm `"session"`. Máy đang
  trong buổi → gửi ngay `pinned_instructions` (đã kèm buổi) như hiện tại.
- `unit_html`: mỗi `<details data-session>` có tiêu đề `Buổi N` thêm nút
  `<button class="btn" type="button" data-pin-session="N">📌 Cú Bông dạy buổi này</button>` (đặt trong khối, không làm hỏng
  `<summary>`). Sheet chọn máy dùng chung, ghi rõ "Buổi N" khi ghim buổi.
- `curriculum.js`: bấm `data-pin-session` → mở sheet, xác nhận → `post(..., {device, lesson, session: N})`; nút cũ
  `data-pin` (ghim cả bài) giữ nguyên.
- `device_cards`: máy ghim có session → "Đang dạy: <bài> · Buổi N – <tiêu đề ngắn>". Máy đang trong buổi và có
  `detour_info` → "Đang dạy: <tên bài detour>" + `<span class="pill">🙋 bé xin</span>`.
- `unit_state`/trang chính: unit chứa bài detour của máy đang học → trạng thái `now` (class `unit-on`), nhãn "🙋 bé đang học".
- Escape HTML mọi chuỗi từ file/người dùng như code hiện tại; không thêm mã hex màu mới (dùng class có sẵn).

# Không làm
- Không sửa gate `test_*.py`, `bridge.py`, `lessons-seed/`, `stlab/english-curriculum/` (chỉ đọc).
- Không đổi định dạng `learners.json` ngoài khóa mới `detour` và `pins[*].session`. Không gọi mạng.

# Tiêu chí PASS
- Lệnh gate exit 0 (gate mới + 9 gate cũ).
- Claude tự xem trang `/curriculum/s2-u1` có 8 nút buổi và thử trên máy thật.
