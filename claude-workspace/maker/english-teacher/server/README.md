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
- Giọng bé được xử lý TRÊN MÁY (VAD Silero + ASR SenseVoiceSmall). `delete_audio: true`: xóa file âm thanh ngay sau khi dùng; bộ nhớ hội thoại tắt (`nomem`).
- Chỉ CHỮ (lời bé đã nhận dạng + prompt) gửi tới Google Gemini. Chữ câu trả lời gửi tới dịch vụ Microsoft Edge TTS để tạo giọng.
- Prompt cấm hỏi/ghi tên thật, địa chỉ, trường, số điện thoại. Log (`runtime\server.log`) có thể chứa chữ hội thoại: xóa định kỳ nếu cần.

## Tường lửa Windows (KHÔNG tự đổi; chạy PowerShell Quản trị khi cần cho bo kết nối từ LAN)
```powershell
New-NetFirewallRule -DisplayName "STLab xiaozhi 8000/8003" -Direction Inbound -Protocol TCP -LocalPort 8000,8003 -Action Allow -Profile Private
```
Mạng nhà phải được đặt là "Private". Gỡ: `Remove-NetFirewallRule -DisplayName "STLab xiaozhi 8000/8003"`.

## Ghi chú / TODO
- ASR SenseVoiceSmall đặt `language: en` (bé nói tiếng Anh). TODO: SenseVoice không hỗ trợ tiếng Việt; nếu cần nghe tiếng Việt của bé, đổi ASR khác.
- `Intent: nointent` (không gọi LLM thứ hai) nên các lệnh nhạc/âm lượng bằng giọng không hoạt động.
- Bài hát/nhạc, kịch bản bài học nhiều bước: chưa làm (xem spec chính).
