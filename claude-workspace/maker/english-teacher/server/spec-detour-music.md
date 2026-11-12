# Spec: Cú Bông dạy theo Seed nhưng làm theo yêu cầu khác (kể chuyện, hát, mở nhạc…)

Claude viết 2026-11-12. Tuan: "teacher đang ép học, không chuyển nhu cầu khác được" → "tìm cách chạy seed bài và cũng có thể
yêu cầu khác như mở nhạc". Chế độ hiện tại: lộ trình Seed (`lessons-seed/`, `free-lesson.off`), cầu nối Gemini Live `live/bridge.py`.

## Hành vi (Claude chốt)
1. **Seed là xương sống**: buổi học vẫn bắt đầu và tiến theo `Curriculum` như hiện tại (con trỏ từ, mark_word, last_words…).
2. **DETOUR** – bé/người lớn xin việc khác (kể chuyện, hát, nói chuyện, trò chơi, hỏi điều gì đó, chủ đề khác, **mở nhạc**):
   cô **làm theo ngay, không từ chối, không kéo về bài**. Trong lúc rẽ ngang, nếu tự nhiên được thì **lồng từ của bài đang học**
   (lesson words) vào chuyện/bài hát/câu trả lời. Rẽ ngang xong (bé hết hứng / xong chuyện / hết nhạc) → **quay lại bài** bằng 1 câu
   nối nhẹ. Bé nói đúng từ của bài trong lúc rẽ ngang vẫn gọi `mark_word` như thường. Xin hẳn chủ đề khác → dùng `change_topic` đã có.
   Viết thành mục `## DETOUR` (tiếng Anh, như phần còn lại của prompt) trong `prompt-teacher.md`, phải chứa các ý: never refuse,
   story, song, play_music, weave lesson words, return to the lesson.
3. **Không còn tự động ép**: nhánh `wants_switch(self.in_buf)` trong bridge (~dòng 953) hiện ép sang từ kế tiếp / trò ôn khi bé xin đổi.
   Ở chế độ lộ trình: KHÔNG tự `CUR.switch` nữa – để Gemini xử lý theo DETOUR (đánh dấu nhánh mới bằng comment chứa chữ `DETOUR`).
   `Curriculum.switch` giữ lại (test_switch còn dùng).
4. **Mở nhạc từ thư mục máy chủ** – module mới `live/music.py`:
   - `MUSIC_DIR = Path(os.environ.get("STLAB_MUSIC_DIR") or <server>/music)`; đuôi nhận: .mp3 .m4a .ogg .wav .flac.
   - `list_tracks(folder) -> list[str]` tên file không đuôi, sắp theo chữ thường; thư mục không có → `[]`.
   - `find_track(query, folder) -> Path | None`: so khớp mờ bỏ dấu tiếng Việt + hoa thường + bỏ chữ thừa ("song", "bài", "nhạc"…);
     query rỗng → 1 bài ngẫu nhiên; không khớp → None. Đúng như `test_detour.py`.
   - `decode_pcm(path, rate) -> bytes`: ffmpeg → PCM s16le mono `rate` Hz (ffmpeg có sẵn trong PATH runtime, xem bridge dòng 13).
   - Bridge: 3 công cụ Gemini `play_music(query)`, `stop_music()`, `list_music()` (khai báo cạnh VOLUME_TOOLS hoặc live_tools).
     `play_music`: tìm bài → trả kết quả cho Gemini (tên bài / không thấy + gợi ý list) → phát: giải mã OUT_RATE, mã Opus bằng
     `self.enc` khung OUT_FRAME, đẩy vào `out_q` theo nhịp như tiếng cô (dùng lại cơ chế pacer/START/STOP hiện có; trong lúc phát coi
     như `tts_on` để mic qua BargeGate với bo full duplex, A1S bỏ mic như cũ). Gemini im trong lúc nhạc.
   - Dừng: `stop_music`, bé chạm nút (abort – nhánh hiện có `clear_out`), hoặc BargeGate báo bé nói chen → dừng nhạc rồi để Gemini nghe.
   - Hết bài (không bị dừng): gửi Gemini `"[music ended] The song finished. Talk briefly about it, then return to the lesson."`.
   - Giới hạn 1 bài/lần gọi; bài > 6 phút chỉ phát 6 phút đầu. Log `[MUSIC] play <tên> / stop <lý do> / end`.
   - `.gitignore`: thêm `maker/english-teacher/server/music/` (nhạc không lên git). Tạo `server/music/README.md` ngắn (tiếng Việt):
     chép file nhạc vào đây, tên file = tên bài; nhạc Tuan tự có quyền dùng (lớp học/gia đình).
5. Âm lượng nhạc: phát nguyên mức file, bo chỉnh bằng âm lượng chung (set_volume) – không thêm khuếch đại.

## Gate (Claude viết, KHÔNG sửa)
`cd maker\english-teacher\server && runtime\.venv\Scripts\python.exe -X utf8 test_detour.py` → PASS, và các gate cũ vẫn PASS:
`test_full_duplex.py test_vad_near.py test_free.py test_curriculum.py test_progress.py test_roadmap.py test_switch.py test_topic.py test_seed_lessons.py`.

## Được sửa
`server/live/music.py` (mới), `server/live/bridge.py`, `server/live/curriculum.py` (chỉ thêm khai báo công cụ nếu cần),
`server/prompt-teacher.md`, `server/music/README.md` (mới), `claude-workspace/.gitignore` (1 dòng), `server/README.md` (mục ngắn).

## Không làm
- Không khởi động lại máy chủ đang chạy (cổng 8000/8003), không chạy test_live*, không đụng `server/data/`, `lessons*/`, firmware.
- Không tải nhạc từ mạng/YouTube, không thêm nhạc mẫu có bản quyền vào repo.
- Không commit.
