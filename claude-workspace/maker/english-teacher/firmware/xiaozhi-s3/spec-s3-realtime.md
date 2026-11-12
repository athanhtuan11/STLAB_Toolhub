# Spec: Cú Bông bản ESP32-S3 – trò chuyện trực tiếp (realtime, bé ngắt lời bằng giọng)

Claude viết 2026-11-12. Tuan: "đã về mạch INMP441 và MAX98357, phát triển English teacher theo hướng real time,
trò chuyện trực tiếp thay về A1S". Bản A1S giữ nguyên (không sửa `firmware/xiaozhi-a1s/`).

## Phần cứng (Claude chốt, không đổi số)
- ESP32-S3 N16R8 (flash 16 MB, PSRAM 8 MB octal → GPIO35–37 cấm dùng).
- Mic INMP441 (I2S, 3,3 V): WS GPIO4, SCK GPIO5, SD GPIO6; chân L/R của INMP441 nối GND → kênh trái.
- Ampli MAX98357A (I2S): DIN GPIO7, BCLK GPIO15, LRC GPIO16. Chân giống `bread-compact-wifi` (simplex, 2 cổng I2S).
- Nút nói: GPIO0 (BOOT) trước để thử trên bàn; vol+ GPIO40, vol− GPIO39; LED trên bo GPIO48 (WS2812 phần lớn devkit N16R8 – nếu không
  sáng cũng không sao). Giữ hành vi nút như A1S: chạm = mở/đóng phiên, chạm lúc cô nói = ngắt, giữ 5 s = ngủ.
- Âm lượng mặc định 70 (Tuan bỏ trần 2026-11-06), 0..100.

## Kiến trúc AEC (Claude chốt)
Không codec → không có tham chiếu loa phần cứng. Dùng **tham chiếu phần mềm** trên bo:
1. Lớp codec riêng trong `boards/stlab-s3/` (ví dụ `StlabLoopbackCodec`, dựa theo `NoAudioCodecSimplex` của xiaozhi
   v2.5.2 – đọc `main/audio/codecs/no_audio_codec.*`), `input_reference_ = true`, `input_channels_ = 2`.
2. `Write()`: mẫu PCM **sau khi áp âm lượng** (đúng mẫu ra MAX98357A) chép vào vòng đệm PSRAM (`heap_caps_malloc(..., MALLOC_CAP_SPIRAM)`).
3. `Read()`: trả xen kẽ [mic, ref] (định dạng "MR" mà `afe_audio_engine.cc` mong đợi – kiểm thứ tự kênh trong file đó), ref lấy từ vòng
   đệm trễ `STLAB_AEC_REF_DELAY_MS` (config.h, mặc định 0–200, chọn giá trị khởi đầu hợp lý theo độ sâu DMA I2S, ghi lý do
   trong comment). Loa im → ref = 0. Vòng đệm thiếu mẫu → ref = 0, không chặn.
4. Vào/ra cùng **16 kHz** (`AUDIO_OUTPUT_SAMPLE_RATE 16000`) để ref không phải đổi tần số.
5. Thêm `BOARD_TYPE_STLAB_S3` vào Kconfig + `depends on` của `USE_DEVICE_AEC` bằng **patch trên bản chép build-src**
   (community/78-xiaozhi-esp32 chỉ đọc). sdkconfig: `USE_AUDIO_PROCESSOR=y`, `USE_DEVICE_AEC=y`, KHÔNG `USE_SERVER_AEC`,
   PSRAM octal, flash 16 MB, `partitions/v2/16m.csv`, `LANGUAGE_VI_VN=y`, OTA_URL về máy lab từ `STLAB_XIAOZHI_SERVER`.
   Có `USE_DEVICE_AEC` thì xiaozhi tự vào `kListeningModeRealtime` (application.cc ~dòng 1189).
6. Thêm log đo (ESP_LOGI mỗi ~5 s khi đang nói): RMS mic, RMS ref, RMS sau AFE – để chỉnh `STLAB_AEC_REF_DELAY_MS` khi có bo.

## Máy chủ (cầu nối Gemini Live `server/live/bridge.py`)
- Module mới `server/live/duplex.py` lớp `BargeGate(threshold, hold_ms, frame_ms)`:
  `feed(pcm, prob, tts_on) -> (out_bytes, barge_bool)`, `reset()`. Hành vi đúng như `server/test_full_duplex.py`
  (đọc kỹ test: tts tắt → qua thẳng; tts bật → số 0 cho tới khi prob ≥ ngưỡng liên tục ≥ hold_ms; lúc đó trả cả các khung đã giữ,
  barge True đúng 1 lần; prob tụt → reset bộ đếm).
- bridge.py: thiết bị gửi `{"type":"listen","state":"start","mode":"realtime"}` → `self.full_duplex = True` (A1S auto mode = False,
  hành vi A1S giữ NGUYÊN: lúc cô nói bỏ mic). Với full_duplex: lúc `tts_on` vẫn giải mã mic, lấy xác suất Silero từ VadGate hiện có
  (thêm hàm trả prob nếu cần, không phá test_vad_near), qua BargeGate, gửi `out` cho Gemini. `barge` True → làm như nhánh abort
  hiện có (clear_out, fast_stop, aborted, "STOP", tell_interrupted) để thiết bị dừng phát ngay. Ngưỡng từ biến môi trường
  `STLAB_BARGE_THRESHOLD` (mặc định 0.7) và `STLAB_BARGE_MS` (mặc định 240). Log `[BARGE]` mỗi lần ngắt.
- Gemini tự báo `sc.interrupted` → giữ xử lý hiện có.

## Gate (Claude viết, KHÔNG sửa)
1. `cd maker\english-teacher\server && runtime\.venv\Scripts\python.exe -X utf8 test_full_duplex.py` → PASS
2. Các gate cũ vẫn PASS: `test_vad_near.py test_free.py test_curriculum.py test_progress.py test_roadmap.py test_switch.py test_topic.py test_seed_lessons.py`
3. `cd maker\english-teacher\firmware\xiaozhi-s3 && powershell -File sync.ps1 && powershell -File build.ps1 && python check_s3.py` → PASS
   (build phải chạy thật, `build.ps1` xóa .bin cũ). Mẫu: `firmware/xiaozhi-a1s/{sync.ps1,build.ps1,patches,boards}` – chép kiểu đó,
   thư mục thật ngắn `C:\xzb\s3`, managed_components cache riêng.

## Được sửa
- `maker/english-teacher/firmware/xiaozhi-s3/**` (trừ `check_s3.py`, spec này)
- `maker/english-teacher/server/live/duplex.py` (mới), `server/live/bridge.py`, `server/live/vad_gate.py` (chỉ thêm, không đổi hành vi cũ)
- `maker/english-teacher/firmware/xiaozhi-s3/README.md`: cách sync/build/nạp, sơ đồ chân, cách chỉnh STLAB_AEC_REF_DELAY_MS.

## Không làm
- KHÔNG nạp firmware vào bo, KHÔNG khởi động lại máy chủ đang chạy (cổng 8000/8003, task "STLab xiaozhi server"),
  không chạy test_live/test_live_lesson (gọi Gemini thật, dùng cổng thật).
- Không sửa `community/`, `firmware/xiaozhi-a1s/`, các test/gate có sẵn, `server/data/`, `lessons*/`.
- Không đưa token/mật khẩu Wi-Fi vào file. Wi-Fi nạp sau bằng `firmware/xiaozhi-a1s/wifi-nvs.py --port COMx` (ghi chú README nếu
  cần sửa offset NVS cho phân vùng 16m – kiểm partitions/v2/16m.csv, không đoán).
- Không commit (phiên chính lo).
