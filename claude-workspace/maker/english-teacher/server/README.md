# Máy chủ xiaozhi tự chạy (cô giáo tiếng Anh cho bé 2–5 tuổi)

Chạy trên máy lab (Windows 11, không Docker). Nguồn: `community/xinnan-tech-xiaozhi-esp32-server` tag v0.9.8 (chỉ đọc, chép sang `runtime/`).
Bo A1S (firmware xiaozhi v2.5.2) gọi OTA `http://<IP>:8003/xiaozhi/ota/` rồi WebSocket `ws://<IP>:8000/xiaozhi/v1/`.

## Cài đặt (một lần, chạy lại được)
```powershell
cd maker\english-teacher\server
.\setup.ps1        # chép nguồn -> runtime\, venv Python 3.10 (uv), torch CPU 2.2.2, requirements, tải SenseVoiceSmall (modelscope) ; log: runtime\setup.log
```
Cần: `uv`, `ffmpeg` trong PATH, biến môi trường người dùng `GOOGLE_API_KEY` (khóa Gemini, KHÔNG ghi vào file).

## Chạy
```powershell
.\run.ps1          # Ctrl+C để tắt ; log: runtime\server.log
python test_server.py   # kiểm (server đang chạy)
runtime\.venv\Scripts\python.exe selftest.py   # chỉ thử TTS -> ASR -> LLM, không cần bo
```
- Đổi IP: `$env:STLAB_XIAOZHI_SERVER = "192.168.1.xx"` trước khi chạy `run.ps1` (mặc định tự lấy IPv4 LAN; test dùng 192.168.1.47).
- Đổi model Gemini / giọng / tốc độ nói: sửa `stlab.config.yaml` (`model_name`, `voice`, `rate`). Xem danh sách model:
  `curl "https://generativelanguage.googleapis.com/v1beta/models?key=$env:GOOGLE_API_KEY"` (chỉ lấy model hỗ trợ generateContent).
  Hiện chọn `gemini-3.1-flash-lite` (bản ổn định, miễn phí, nhanh); `gemini-2.5-*` đã đóng với tài khoản mới.
- Đổi nội dung bài giảng / an toàn trẻ em: sửa `prompt-teacher.md` (phần sau dòng `-----`), chạy lại `run.ps1`.
- `run.ps1` sinh `runtime\data\.config.yaml` từ `stlab.config.yaml`; `run.py` điền khóa Gemini trong bộ nhớ từ biến môi trường (không ghi file, không in).

## Quyền riêng tư
- Giọng bé được xử lý TRÊN MÁY (VAD Silero + Whisper `small` chạy tại máy, chỉ nghe 127.0.0.1:8010). `delete_audio: true`: xóa file âm thanh ngay sau khi dùng; bộ nhớ hội thoại tắt (`nomem`).
- Chỉ CHỮ (lời bé đã nhận dạng + prompt) gửi tới Google Gemini. Chữ câu trả lời gửi tới dịch vụ Microsoft Edge TTS để tạo giọng.
- Prompt cấm hỏi/ghi tên thật, địa chỉ, trường, số điện thoại. Log (`runtime\server.log`) có thể chứa chữ hội thoại: xóa định kỳ nếu cần.

## Tường lửa Windows (KHÔNG tự đổi; chạy PowerShell Quản trị khi cần cho bo kết nối từ LAN)
```powershell
New-NetFirewallRule -DisplayName "STLab xiaozhi 8000/8003" -Direction Inbound -Protocol TCP -LocalPort 8000,8003 -Action Allow -Profile Private
```
Mạng nhà phải được đặt là "Private". Gỡ: `Remove-NetFirewallRule -DisplayName "STLab xiaozhi 8000/8003"`.

## Ghi chú / TODO
- ASR cũ SenseVoiceSmall (`FunASR`) còn trong cấu hình làm dự phòng nhưng KHÔNG nghe được tiếng Việt.
- `Intent: nointent` (không gọi LLM thứ hai) nên các lệnh nhạc/âm lượng bằng giọng không hoạt động.
- Bài hát/nhạc, kịch bản bài học nhiều bước: chưa làm (xem spec chính).

## Song ngữ Việt – Anh (2026-11-05)
- Bé nói tiếng Việt -> cô trả lời 1 câu Việt ngắn + dạy 1 từ Anh ("Con mèo là cat. Con nói: cat!"). Bé nói tiếng Anh -> cô trả lời tiếng Anh. Câu <= 8 từ, <= 3 câu/lượt.
- ASR: `whisper-local/` = faster-whisper `small` (CPU int8, 8 luồng) tại `127.0.0.1:8010`, API giống OpenAI `/v1/audio/transcriptions`; tự dò vi/en (khác thì dùng en), gợi từ vựng bằng `initial_prompt`; file tạm xóa ngay.
  `run.ps1` bật Whisper trước (chờ `/health`), rồi bật server; tắt `run.ps1` (Ctrl+C) thì tắt cả Whisper. Đổi model: `$env:STLAB_WHISPER_MODEL = "medium"` (setup.ps1 sẽ tải).
- TTS: `en-US-AvaMultilingualNeural`, rate -12 %. Nghe thử giọng trong `out-voice/` (vi-ava, vi-emma, en-ava, en-emma .mp3; không commit); đổi sang Emma ở `voice:` trong `stlab.config.yaml`.
- Gemini bị chậm bất thường (chunk đầu có lúc 5-35 s): `run.py` gọi Gemini REST SSE trực tiếp, gửi thêm 1 yêu cầu nếu sau 1,5 s chưa có chữ (tối đa 2), dừng khi gặp 429.
- Quyền riêng tư: giọng bé chỉ qua Whisper trên máy; chỉ CHỮ gửi Gemini; chữ trả lời gửi Microsoft Edge TTS.

### Số đo (máy lab, 16 luồng CPU)
- Whisper `small`: câu 2-3 s ~1,3-3 s (đo lúc server chạy); nghe đúng "Con mèo màu vàng.", "Apple. Red apple.", câu Việt dài có "cat". `medium`: 8-10 s cho cùng câu, đúng như small -> chọn `small`.
- test_e2e (thả nút -> tiếng đầu tiên, giả lập bo): thường 3,8-4,2 s; lúc Gemini chậm 7-11 s (4/5 lần < 8 s). Chạy: `$env:PATH="$PWDuntime;$env:PATH"; runtime\.venv\Scripts\python.exe test_e2e.py` (cần opus.dll trong PATH).

## Phiên nói chuyện tự động (2026-11-06)
- Khóa mới trong `stlab.config.yaml`:
  - `min_silence_duration_ms: 600` (VAD chốt câu sau 600 ms im lặng): chậm thì giảm, bị cắt câu thì tăng.
  - `close_connection_no_voice_time: 30` (30 s im lặng thì cô chào tạm biệt và nghỉ).
  - `end_prompt`: câu chào tạm biệt Việt–Anh (bản gốc là prompt tiếng Trung).
  - `exit_commands`: viết LIỀN không khoảng trắng, phân biệt hoa thường. Máy chủ so khớp chính xác sau khi bỏ dấu câu và khoảng trắng.
- Gate độ trễ LLM: `runtime\.venv\Scripts\python.exe -X utf8 test_llm_latency.py`
- Tự bật khi đăng nhập Windows: `install-autostart.ps1` (gỡ: `-Remove`).

## Rẽ ngang khi học Seed + mở nhạc (2026-11-12)
- Seed vẫn là xương sống nhưng bé xin việc khác (kể chuyện, hát, trò chơi, mở nhạc) thì cô làm theo rồi quay lại bài (mục `## DETOUR` trong `prompt-teacher.md`); bridge không còn tự `CUR.switch` (bật lại: `STLAB_FORCE_SWITCH=1`).
- Nhạc: chép file vào `server/music/` (hoặc `STLAB_MUSIC_DIR`), công cụ Gemini `play_music/stop_music/list_music`, module `live/music.py`. Gate: `test_detour.py`.
- Khóa biệt danh theo bo: bo đã có trong `data/devices.json` thì bridge không đổi biệt danh khi nghe tên con vật khác (mặc định bật; `STLAB_LOCK_DEVICE_NICK=0` = hành vi cũ).
- Tự chỉnh ngưỡng (2026-11-12): `live/tuning.py` lưu `data/tuning.json` (`STLAB_TUNING_PATH`): barge_threshold/barge_ms + AGC mic; bridge tự nâng/hạ sau mỗi `[BARGE]` (ngắt nhầm = không ai nói thật trong 3 s hoặc lời giống câu cô vừa nói; bỏ sót = bé chạm nút khi VadGate đã thấy giọng), log `[TUNE]`. Người lớn nói "chế độ kỹ thuật" (10 phút) rồi nhờ cô chỉnh mic/barge/gain bằng giọng. Phân tích log: `python tune/analyze.py [--since HH:MM] [--json]`. Gate `test_tuning.py`.
