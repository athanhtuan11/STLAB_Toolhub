---
task: seed-export-device
cwd: .
allow:
  - "stlab/english-curriculum/seed/export_device.py"
  - "maker/english-teacher/lessons-seed/*.md"
  - "maker/english-teacher/server/live/bridge.py"
gate: "maker/english-teacher/server/runtime/.venv/Scripts/python.exe -X utf8 maker/english-teacher/server/test_seed_lessons.py"
timeout_min: 20
max_rounds: 2
executor: auto
read: ["maker/english-teacher/lessons", "maker/english-teacher/server/live"]
---

# Mục tiêu
Máy Cú Bông (maker/english-teacher) dạy theo giáo trình Seed thay cho 12 bài cũ (Tuan chọn 2026-11-12). Viết script sinh
thư mục bài `maker/english-teacher/lessons-seed/` từ `stlab/english-curriculum/seed/units.yaml`, đúng định dạng mà
`server/live/curriculum.py` đang đọc (KHÔNG sửa curriculum.py), rồi cho `bridge.py` dùng thư mục mới.

# Đầu vào
- `stlab/english-curriculum/seed/units.yaml`: `levels[]` (id s1/s2/s3, name "Seed 1", age "3–4 tuổi", units[]);
  mỗi unit: id (vd `s2-u5`), theme, theme_vi, core[], plus[], patterns[], song, make, tell, can_do[].
- Định dạng máy đọc: xem `maker/english-teacher/lessons/03-numbers-1-5.md` (mục `## Chỉ dẫn cho AI`, dòng `Vocabulary:`),
  `maker/english-teacher/lessons/ROADMAP.md` mục 8 (dòng `Week N: ...`), parser ở `server/live/curriculum.py`
  (`__init__`, `_parse_roadmap`, `WEEK_RE`).

# Yêu cầu
1. `stlab/english-curriculum/seed/export_device.py` (Python 3, chỉ dùng pyyaml + thư viện chuẩn):
   - Mặc định: ghi `maker/english-teacher/lessons-seed/` (đường dẫn tính từ vị trí script, không cứng ổ đĩa). Xóa file `.md`
     cũ trong thư mục đó trước khi ghi (chỉ trong thư mục đó).
   - `--check`: sinh vào bộ nhớ, so với file đang có; khác/thiếu/thừa → in tên file, exit 1; giống hệt → in `OK`, exit 0.
   - Ghi UTF-8, xuống dòng `\n`, nội dung tất định (chạy 2 lần ra y hệt).
2. Mỗi unit 1 file `<id>-<slug>.md`; slug = theme viết thường, bỏ ký tự không phải chữ/số, nối bằng `-`
   (vd `s1-u1-hello.md`, `s2-u5-farm-animals.md`, `s3-u6-clothes-and-what-i-can-do.md`). Nội dung đúng khuôn:
   ```
   # <Seed n> · Unit <k> – <theme> (<theme_vi>)

   Tuổi: <age>. Sinh tự động từ stlab/english-curriculum/seed/units.yaml bằng export_device.py – không sửa tay.
   Lớp học cùng chủ đề: stlab/english-curriculum/seed/lesson-plans/<id>-*.md.

   ## Chỉ dẫn cho AI

   (Dùng cho máy chủ. Tiếng Anh, nói ngắn.)

   - Lesson: <theme> (<Seed n>, ages <age bỏ chữ "tuổi">). Vocabulary: <core nối ", ">. Teach ONE word per turn after greeting. Say each word twice, child repeats once.
   - Sentence patterns for this unit (use them as short models, ages 4+ only): <patterns nối " · ">.
   - Extra words only for a confident child, after the vocabulary is solid: <plus nối ", ">.
   - Song idea: <song>. If you do not know the exact words, make up a short simple chant with the vocabulary instead.
   - The class makes: <make>. Ask the child to tell about it like: <tell>.
   - Goals: <can_do nối "; ">.
   - Only listening and speaking: never ask the child to read or write.
   - If child is silent: wait 5 seconds, say the word again and invite once more; then move on. Do not ask more than twice in a row.
   - If child speaks Vietnamese: reply in one short Vietnamese sentence, then teach one English word.
   - If child says a word wrong: praise the try and repeat the right word once, slowly. Never say "wrong".
   - Never ask the child's real name, age, school, address or parents' jobs.
   - If child seems hurt or scared, say in Vietnamese: "Con nói với ba mẹ nhé!"
   - Do not end the session or say goodbye yourself; the system decides when to stop (teaching the WORD 'bye-bye' is fine).
   ```
   - `<n>` lấy từ level name, `<k>` từ số sau `-u` của id. Từ vựng giữ nguyên chữ trong yaml (str(), vd `"no"`, `"yes"`).
   - Dòng Vocabulary phải kết thúc bằng `. ` đúng như mẫu (parser cắt ở `. ` / xuống dòng). Trong các dòng khác, nếu chuỗi
     từ yaml đã có dấu chấm cuối thì không thêm chấm thứ hai.
3. `lessons-seed/ROADMAP.md` (không được chứa chuỗi `Chỉ dẫn cho AI`):
   ```
   # Lộ trình Cú Bông theo giáo trình Seed (sinh tự động – không sửa tay)

   Nguồn: stlab/english-curriculum/seed/units.yaml (export_device.py). Bé 2–3 tuổi học Seed 1; bé 4–5 tuổi học Seed 2 rồi Seed 3.
   Mỗi hàng 2 từ Core mới theo đúng thứ tự trong units.yaml; tiến độ theo con trỏ từ của máy chủ.

   ## Lịch tuần 2–3 tuổi (máy đọc)

   ```text
   Week 1: s1-u1-hello | new: hello, bye-bye | review: - | daily: hello, thank you, good job, bye-bye, let's sing | song: s1-u1-hello
   ...
   ```

   ## Lịch tuần (máy đọc)

   ```text
   Week 1: s2-u1-how-are-you | new: ... | review: - | daily: ... | song: s2-u1-how-are-you
   ...
   ```
   ```
   - Bảng 2–3 tuổi = các unit của s1 theo thứ tự; bảng thứ hai = s2 rồi s3. Week đánh số liên tục từ 1 trong mỗi bảng.
   - Trong mỗi unit: chia core thành từng cặp theo thứ tự (unit lẻ từ thì hàng cuối 1 từ); bỏ từ đã xuất hiện ở hàng trước
     trong CÙNG bảng (không lặp từ mới); unit bị bỏ hết từ thì không có hàng.
   - `review` = các từ `new` của hàng ngay trước trong cùng bảng (hàng đầu: `-`). `song` = lesson-id của hàng.
   - `daily` cố định: `hello, thank you, good job, bye-bye, let's sing`.
4. `maker/english-teacher/server/live/bridge.py`: chỉ đổi dòng tạo `CUR = Curriculum(...)`: thư mục bài lấy từ biến môi
   trường `STLAB_LESSONS_DIR` nếu có, mặc định `SERVER.parent / "lessons-seed"`. Không đổi gì khác trong bridge.py.
5. Chạy `python stlab/english-curriculum/seed/export_device.py` để sinh thật thư mục, rồi chạy gate.

# Không làm
- Không sửa `curriculum.py`, các test có sẵn, `lessons/` cũ, `units.yaml`, file gate `test_seed_lessons.py`.
- Không chạy/khởi động lại máy chủ, không động vào `free-lesson.on`, `data/`.
- Không gọi mạng, không gọi Gemini.

# Tiêu chí PASS
- Gate exit 0 (`GATE PASS`).
- Các test cũ vẫn chạy (Claude tự chạy: test_curriculum, test_roadmap, test_progress, test_free, test_switch, test_topic).
