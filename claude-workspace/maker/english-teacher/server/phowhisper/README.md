# PhoWhisper (thử nghiệm, CHƯA ghép vào cầu nối)

Mô hình nhận dạng tiếng Việt của VinAI, tinh chỉnh từ Whisper. Nguồn: https://github.com/VinAIResearch/PhoWhisper, HF `vinai/PhoWhisper-{small,medium}`.
**License: BSD-3-Clause** (cho phép dùng/phân phối, giữ thông báo bản quyền VinAI).

- `setup-phowhisper.ps1`: tạo `.venv` (uv, torch CPU + transformers + faster-whisper + edge-tts), tải từ HF, đổi sang CTranslate2 int8
  bằng `ct2-transformers-converter` -> `server\models\phowhisper-<size>-ct2\` (đã .gitignore). Chạy lại được (bỏ qua mô hình đã có).
- `bench_asr.py`: đo Whisper small hiện tại vs PhoWhisper-small/medium. Âm thanh Edge TTS là GIẢ LẬP, không phải giọng trẻ thật
  (giọng vi-VN không nhận rate/pitch nên tốc độ x1,25 và cao độ x1,25 làm bằng ffmpeg). Kết quả: `bench-result.md`.

Chạy: `.\.venv\Scripts\python.exe -X utf8 -I bench_asr.py` (cần mạng cho Edge TTS, đôi khi từ chối ngẫu nhiên nên có thử lại).
