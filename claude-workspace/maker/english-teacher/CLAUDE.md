# english-teacher – thiết bị nói chuyện dạy tiếng Anh cho bé 2–5 tuổi

Dự án Tuan mở 2026-11-05 (song song esp32-s3-cam). Kế hoạch: `C:\Users\hoang\.claude\plans\ng-l-m-tr-c-cuddly-curry.md`.

## Mục tiêu
- Bé 2–5 tuổi; kiểu học **kết hợp**: bài theo chủ đề + AI chỉ nói trong phạm vi bài.
- Bản 1: **ESP32-A1S Audio Kit** (có sẵn) – thử ý tưởng + nội dung. Bản 2 (sau): ESP32-S3 N16R8 + INMP441 + MAX98357A – làm kit.
- Nền: 78/xiaozhi-esp32 **v2.5.2** (ESP-IDF 6.1) + máy chủ xinnan-tech/xiaozhi-esp32-server **tự chạy trên máy lab**.

## Đã biết (có nguồn)
- Bo của Tuan (đọc esptool 2026-11-05, COM5 qua CP210x): **ESP32-D0WD-V3 rev v3.1**, 40 MHz, flash **4 MB** (hãng 0x5e, mã 0x4016),
  MAC e0:8c:fe:64:20:a4. PSRAM, chip codec: TODO (firmware dò).
- Bộ chân ứng viên Audio Kit (pschatzmann/arduino-audio-driver, src/AudioBoards/*.h – GPL-3.0, chỉ lấy số chân):
  | Bản | I2C SCL/SDA | I2S MCLK/BCK/WS/DOUT/DIN | PA | LED | Nút |
  |---|---|---|---|---|---|
  | ES8388 v1 | 32 / 33 | 0 / 27 / 25 / 26 / 35 | 21 | 22 | 36,13,19,23,18,5 |
  | ES8388 v2 | 23 / 18 | 0 / 5 / 25 / 26 / 35 | 21 | 22 | 36,13,19,23,18,5 |
  | AC101 | 32 / 33 | 0 / 27 / 26 / 25 / 35 | 21 | 22, 19 | 36,13,19,23,18,5 |

  Địa chỉ I2C 7-bit: ES8388 0x10 (hoặc 0x11), AC101 0x1A (TODO đối chiếu datasheet khi dò).
- xiaozhi v2.5.2: có `partitions/v2/4m.csv` (factory 0x2F0000 + assets 1 MB, không OTA), `sdkconfig.defaults.esp32` dùng WakeNet9
  "nihao xiaozhi"; có driver `main/audio/codecs/es8388_audio_codec.cc`; không có cấu hình bo A1S → tự viết.

- **Cơ khí** (2026-11-06): loa **Ø52 × cao 26 mm** (Tuan đo). Bo Audio Kit V2.2 **82 × 73 mm** theo hình kích thước trong datasheet
  Ai-Thinker (https://manuals.plus/m/733d5ba2d731002bae35fd49d2f607f00a214056ed9d35b7bb477eecc9a2aa24.pdf – bảng thông số cùng file ghi
  82 × 37, mâu thuẫn, bỏ). Độ dày, lỗ vít, chiều cao linh kiện, vị trí USB/jack/micro: không có nguồn → khay đỡ rãnh trượt khe rộng.

## An toàn
- Nguồn USB 5 V. Pin Li-ion (nếu dùng): chỉ cell có mạch bảo vệ, ngăn bắt vít – chưa thiết kế.
- Âm lượng trần trong firmware (tai bé). Vỏ không chi tiết nhỏ rời (bé < 3 tuổi hóc), vít giấu.
- Giọng bé chỉ tới máy chủ trong lab; không lưu ghi âm lâu dài; cần phụ huynh đồng ý trước khi bé dùng thử.
- Khóa API trong biến môi trường, không vào file.

## Firmware
- **ESP-IDF 6.1** (cho xiaozhi v2.5.2) cài 2026-11-05: nguồn `C:\Espressif\frameworks\esp-idf-v6.1`, công cụ riêng
  `C:\Espressif\tools-v6.1` (~6,4 GB, esp32 + esp32s3; không đụng 5.5.4). Kích hoạt trong PowerShell: xóa biến MSYS →
  `$env:IDF_TOOLS_PATH='C:\Espressif\tools-v6.1'; . C:\Espressif\frameworks\esp-idf-v6.1\export.ps1`. Kiểm: `idf.py --version` = v6.1.
- `firmware/probe-a1s/` (ESP-IDF 5.5.4): dò PSRAM, codec, chân ampli, thử loa + micro.

## Kết quả dò phần cứng (2026-11-05, firmware probe-a1s, mạch thật COM5)
- `[KQ] psram=8 codec=ES8388@0x10 i2c=32/33 i2s=0/27/25/26/35 pa=21 mic_rms=379/369`
- PSRAM 8 MB (ESP32 chỉ map 4 MB). Bus 23/18 không có thiết bị → **bộ chân "ES8388 v1"**: I2C SCL32 SDA33, I2S MCLK0 BCK27 WS25
  DOUT26 DIN35, PA GPIO21. Codec ghi/đọc thanh ghi OK.
- **Micro trên bo = ES8388 LIN2/RIN2** (đo 2026-11-05, PC phát bíp 1 kHz: in2 đỉnh 1000 Hz SNR 23,7 dB, peak 31951; in1 im, rms 2,4).
  Kiểm bằng `firmware/probe-a1s/rec.py --port COM5 --sec 4 --in 2 --tone` (lệnh UART `REC`, `BEEP`; log nút `[NUT]`).
- **Loa ✅** (2026-11-06: lệnh BEEP, Tuan nghe thấy ở cả cổng L và R – firmware phát cùng tiếng ra 2 kênh). **6 nút ✅** KEY1..6 = GPIO36,13,19,23,18,5
  (log `[NUT]` nhấn/nhả đủ 2 lượt, probe-log-nut.txt). Chuỗi thanh ghi ES8388 của firmware dò viết theo trí nhớ ESP-ADF – xiaozhi dùng driver riêng.

## Trạng thái
- 2026-11-05 đêm (Tuan ngủ, Claude tự làm): bo A1S chạy xiaozhi + Wi-Fi tự nạp (`firmware/xiaozhi-a1s/wifi-nvs.py`), phát 2 kênh L=R (chờ Tuan nghe lại);
  máy chủ **song ngữ Việt–Anh**: Whisper small tại máy 127.0.0.1:8010, Gemini 3.1 flash-lite (gửi song song khi chậm), Edge `en-US-AvaMultilingualNeural` −12 %;
  test_server 17/17 + test_e2e (giả lập bo) PASS – trễ thả nút → tiếng đầu ~3,8–7,4 s, có lần 11 s do Gemini. CAD Cú Bông v1 2 loa (gate PASS), 3 bài học `lessons/`.
  **Sáng mai:** bật máy chủ `serverun.ps1` → giữ KEY4 nói thử tiếng Việt + tiếng Anh, nghe 2 loa; nghe `server/out-voice/*.mp3` chọn giọng; duyệt `cad/out/owl-preview.png`; cắt lớp + print.yaml cùng Tuan.
- 2026-11-05: **Tuan chọn dáng A – Cú Bông** (design/contact-sheet.png, design-spec.md): không màn hình, mắt = LED RGB đổi màu
  (nghe xanh dương / nói vàng / khen hồng / ngủ tím mờ), nút "nói" Ø50 trên đỉnh, **2 loa trái + phải ở 2 sườn** (Tuan đổi 2026-11-05; trước: 1 loa ở bụng), 3 màu (mơ/kem/bơ – tách part, hạn chế AMS).
  Cần: LED RGB (vd. WS2812) + chân trống trên Audio Kit (TODO); Tuan đo bo Audio Kit + độ sâu loa Ø52 trước khi CAD; pin hay USB: chưa chốt.
- 2026-11-05: tạo dự án, đọc chip qua esptool. Đang: firmware dò + bước 0 dáng sản phẩm.
