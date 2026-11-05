# spec-vi – cô giáo nghe + nói được cả tiếng Việt (Tuan 2026-11-05: "nhiều bạn nhỏ chưa rành tiếng Anh")

cwd: `maker/english-teacher/server`
allow: `whisper-local/**`, `setup.ps1`, `run.ps1`, `run.py`, `selftest.py`, `stlab.config.yaml`, `stlab-base-prompt.txt`, `prompt-teacher.md`, `README.md`, `.gitignore`, `runtime/**`
Không sửa: `test_server.py`, community/. Khóa chỉ trong biến môi trường. Không mở tường lửa (Whisper chỉ nghe 127.0.0.1).
gate: chạy `run.ps1` nền (phải bật cả Whisper local), chờ cổng 8000, `python test_server.py` PASS, tắt hết tiến trình sau test.

## Hiện trạng
Máy chủ v0.9.8 chạy tốt (test_server 15/15 trước khi thêm tiếng Việt). ASR FunASR SenseVoice không có tiếng Việt; TTS en-US-AnaNeural chỉ tiếng Anh.
Lỗi đã sửa: `{{language}}` trong khung prompt mặc định "中文" → đã đặt `TTS.EdgeTTS.language` + khung `stlab-base-prompt.txt` (giữ cơ chế này).
Provider ASR `type: openai` (runtime/core/providers/asr/openai.py) POST multipart tới `base_url` + `model_name` → dùng để gọi Whisper chạy tại máy.

## Việc
1. **Whisper tại máy** `whisper-local/`: dịch vụ nhỏ (FastAPI/uvicorn hoặc http.server) trên **127.0.0.1:8010**, endpoint tương thích OpenAI
   `POST /v1/audio/transcriptions` (multipart `file`, `model`; trả `{"text": ...}`), dùng **faster-whisper** CPU int8 (venv riêng hoặc chung runtime nếu không xung đột torch 2.2.2).
   Model: thử `small` và `medium`, đo thời gian cho câu 2–3 s trên máy này; chọn cái nhanh mà vẫn nghe đúng cả 2 câu thử dưới (ghi số đo vào README).
   `language` để tự dò (vi/en); `initial_prompt` gợi từ vựng bài (màu sắc, con vật). Không ghi file âm thanh lâu dài (xóa ngay).
   setup.ps1 cài + tải model; run.ps1 bật Whisper trước, chờ sẵn sàng, rồi bật server; tắt server thì tắt cả Whisper.
2. `stlab.config.yaml`: ASR mới `LocalWhisperASR` (type openai, base_url `http://127.0.0.1:8010/v1/audio/transcriptions`, api_key giả "local", model_name).
   TTS EdgeTTS giọng **đa ngôn ngữ** `en-US-AvaMultilingualNeural` hoặc `en-US-EmmaMultilingualNeural` (chọn giọng đọc tiếng Việt rõ hơn, thử cả hai), rate chậm −10…−15 %,
   `language` = "Vietnamese and simple English". Lưu `out-voice/vi-test.mp3` + `en-test.mp3` (gitignore) để Tuan nghe chọn.
3. Khung `stlab-base-prompt.txt` + `prompt-teacher.md`: song ngữ – bé nói tiếng Việt → cô trả lời câu tiếng Việt ngắn + dạy 1 từ tiếng Anh ("Con mèo là cat. Con nói: cat!");
   bé nói tiếng Anh → trả lời tiếng Anh đơn giản; luôn khen; mỗi lượt ≤ 3 câu, câu ≤ 8 từ; không bao giờ tiếng Trung; giữ các quy tắc an toàn trẻ em cũ.
4. `selftest.py` thêm: TTS tiếng Việt "Con mèo màu vàng." → Whisper → in `[ASR-VI] text=...`; gửi "Con mèo tiếng Anh là gì?" vào LLM → `[LLM-VI] text=...`;
   giữ các dòng cũ `[TTS] ok`, `[ASR] text=` (câu "Apple. Red apple." qua ASR mới), `[LLM] text=`.
5. README: cách hoạt động song ngữ, quyền riêng tư (Whisper trên máy, chỉ chữ gửi Gemini, TTS gửi chữ tới Microsoft), số đo độ trễ.

## Không làm
Không dùng ASR đám mây (Groq/OpenAI) – giọng bé không ra khỏi máy. Không đổi firmware.
