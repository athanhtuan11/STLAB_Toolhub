# spec-server – máy chủ xiaozhi tự chạy trên máy lab (Windows, không Docker)

cwd: `maker/english-teacher/server`
allow: `setup.ps1`, `run.ps1`, `run.py`, `selftest.py`, `stlab.config.yaml`, `prompt-teacher.md`, `README.md`, `.gitignore`, `runtime/**` (gitignore)
Không sửa: `test_server.py`, mọi thứ trong `claude-workspace/community/` (bản ghim chỉ đọc).
gate: chạy server nền bằng `run.ps1`, chờ cổng 8000 mở, rồi `python test_server.py` (server phải đang chạy); tắt server sau khi test.

## Bối cảnh
- Nguồn ghim: `claude-workspace/community/xinnan-tech-xiaozhi-esp32-server` tag v0.9.8 (sparse, chỉ `main/xiaozhi-server`). README triển khai
  nguồn: `docs/Deployment.md` (python 3.10, `pip install -r requirements.txt`, `python app.py`; torch 2.2.2, funasr 1.4.16, modelscope).
- Server đọc `config.yaml` + ghi đè bằng `data/.config.yaml` (config/config_loader.py). Không hỗ trợ biến môi trường cho khóa.
- Máy lab: Windows 11, i5-13400F, RAM 30 GB, IP LAN 192.168.1.47 (biến `STLAB_XIAOZHI_SERVER` nếu đổi). Có `uv` (`C:\Users\hoang\.local\bin\uv.exe`).
- Khóa Gemini: biến môi trường người dùng **`GOOGLE_API_KEY`** (đã có). **Không được ghi khóa ra bất kỳ file nào** (gate quét).
- Firmware xiaozhi v2.5.2 trên bo A1S gọi `http://192.168.1.47:8003/xiaozhi/ota/` rồi WebSocket `ws://192.168.1.47:8000/xiaozhi/v1/`.

## Việc
1. `setup.ps1`: chép `main/xiaozhi-server` từ bản ghim sang `runtime/` (gitignore; xóa cũ, giữ `runtime/models` nếu đã tải); `uv venv runtime/.venv --python 3.10`;
   cài `requirements.txt` (torch bản CPU nếu được – máy dùng CPU); tải model SenseVoiceSmall vào `runtime/models/SenseVoiceSmall` theo đúng cách README chỉ (modelscope).
   Ghi log `runtime/setup.log`. Chạy lại được (idempotent).
2. `stlab.config.yaml` (lên git, không khóa): chép vào `runtime/data/.config.yaml` lúc chạy. Nội dung:
   - `server`: ip 0.0.0.0, port 8000, http_port 8003, `websocket: ws://<IP>:8000/xiaozhi/v1/` (run.ps1 thay `<IP>`), `vision_explain` tương tự.
   - `delete_audio: true`; tắt mọi lưu ghi âm/hội thoại lâu dài có trong config (nếu có mục memory/lưu lịch sử: dùng loại không lưu hoặc chỉ trong RAM).
   - `selected_module`: VAD SileroVAD, ASR **FunASR** (`language: en` – bé nói tiếng Anh; ghi chú SenseVoice không hỗ trợ tiếng Việt → TODO),
     LLM **GeminiLLM** (`model_name`: model Gemini Flash miễn phí đang có – kiểm bằng API list models, ghi tên chọn + lý do), TTS **EdgeTTS**
     `voice: en-US-AnaNeural` (giọng trẻ em) hoặc giọng en-US nữ chậm rõ – ghi lý do; Intent: loại đơn giản nhất không cần LLM thứ 2.
   - `prompt`: lấy từ `prompt-teacher.md` (xem mục 3).
3. `prompt-teacher.md` (tiếng Anh cho LLM + chú thích tiếng Việt): "cô giáo tiếng Anh cho bé 2–5 tuổi": câu ≤ 6 từ, nói chậm, lặp lại từ mới 2 lần, luôn khen,
   hỏi 1 câu mỗi lượt, khi bé bí nói tiếng Việt ngắn rồi quay lại tiếng Anh; chỉ chủ đề an toàn cho trẻ (màu sắc, con vật, số đếm, đồ vật, gia đình,
   bài hát thiếu nhi); không hỏi tên thật/địa chỉ/trường/số điện thoại; gặp chủ đề người lớn/bạo lực/đáng sợ → lái về bài nhẹ nhàng; không giả làm người thật.
   Bài mặc định: "Colors" (red, blue, yellow, green, apple, sky…).
4. `run.py`: nạp `runtime/` vào sys.path, **vá trong bộ nhớ** hàm nạp cấu hình (config_loader) để điền `api_key` của GeminiLLM từ `os.environ["GOOGLE_API_KEY"]`
   (lỗi rõ ràng nếu thiếu biến), rồi chạy điểm vào của `app.py` với cwd = `runtime/`. Không in khóa.
   `run.ps1`: xác định IP (biến hoặc IPv4 LAN), sinh `runtime/data/.config.yaml` từ `stlab.config.yaml` (không khóa), chạy `run.py` bằng venv; log `runtime/server.log`.
5. `selftest.py` (chạy bằng venv, cwd runtime/, dùng chính provider của server, không cần thiết bị): EdgeTTS nói "Apple. Red apple." → in `[TTS] ok <bytes> bytes`;
   đưa âm thanh đó (đổi 16 kHz mono) vào ASR FunASR → in `[ASR] text=<...>`; gửi "What color is an apple?" + prompt cô giáo vào GeminiLLM → in `[LLM] text=<...>`.
6. README.md: cài đặt (setup.ps1), chạy (run.ps1), đổi IP, chọn model, quyền riêng tư (giọng bé xử lý trên máy; chỉ chữ gửi Gemini; TTS gửi chữ tới Microsoft Edge),
   tường lửa Windows mở cổng 8000/8003 cho mạng riêng (hướng dẫn lệnh, KHÔNG tự đổi tường lửa – báo phiên chính).

## Không làm
Không sửa community/, không Docker/WSL, không dùng xiaozhi.me, không manager-web/api (không cần DB), không ghi khóa ra file, không tự mở tường lửa, không nạp firmware.
