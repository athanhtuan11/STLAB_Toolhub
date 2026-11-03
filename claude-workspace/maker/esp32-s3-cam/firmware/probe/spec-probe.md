---
task: esp32-s3-cam-probe
cwd: maker/esp32-s3-cam/firmware/probe
allow:
  - "CMakeLists.txt"
  - "sdkconfig.defaults"
  - "partitions.csv"
  - "main/*"
  - "README.md"
gate: 'powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 && python check_probe.py'
timeout_min: 45
max_rounds: 3
executor: opencode
read: ["maker/pump-control/firmware", "maker/esp32-s3-cam/CLAUDE.md"]
---

# Mục tiêu
Firmware ESP-IDF 5.5.4 (C) **dò phần cứng** cho mạch ESP32-S3-CAM N16R8 + camera OV3660: Tuan nạp 1 lần, đọc log serial +
xem hình trên điện thoại để chốt bộ chân camera. Tham khảo cấu trúc `maker/pump-control/firmware` (CMake, component manager).
Gate `check_probe.py`, `build.ps1` do Claude viết – **KHÔNG sửa**.

# Yêu cầu
- Project tên `probe` (ra `build/probe.bin`), target esp32s3. `main/idf_component.yml`: `espressif/esp32-camera: "^2.1.5"`.
- `sdkconfig.defaults`: `CONFIG_IDF_TARGET="esp32s3"`, `CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y`, `CONFIG_SPIRAM=y`,
  `CONFIG_SPIRAM_MODE_OCT=y`, `CONFIG_SPIRAM_USE_MALLOC=y`, `CONFIG_ESP32S3_DEFAULT_CPU_FREQ_240=y`, partition custom
  `partitions.csv` (app factory ≥ 3 MB), `CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=n` để log ra UART0 mặc định (nếu cổng USB-C của
  mạch là USB native thì log vẫn qua USB-Serial-JTAG: bật cả hai bằng `CONFIG_ESP_CONSOLE_SECONDARY_USB_SERIAL_JTAG=y`).
- Khi khởi động in rõ (tiếng Việt không dấu, mỗi dòng bắt đầu `[DO]`): model chip + số lõi + revision, dung lượng flash
  (`esp_flash_get_size`), PSRAM (`esp_psram_get_size`), MAC.
- **Bảng bộ chân** (mảng struct, dễ thêm bộ mới): bộ 1 "FREENOVE_GOOUUU" = XCLK 15, SIOD 4, SIOC 5, D0..D7 = 11, 9, 8, 10, 12,
  18, 17, 16, VSYNC 6, HREF 7, PCLK 13, PWDN −1, RESET −1. KHÔNG tự thêm bộ chân khác (chưa có nguồn) – để comment chỗ thêm.
  Với mỗi bộ thử XCLK 20 MHz rồi 10 MHz; `esp_camera_init` JPEG, FRAMESIZE_SVGA, jpeg_quality 12, fb_count 2, fb trong PSRAM,
  grab_mode LATEST. In kết quả từng lần thử; khi thành công in PID cảm biến (`esp_camera_sensor_get()->id.PID`, nhận diện
  OV3660 = 0x3660, OV2640 = 0x26, OV5640 = 0x5640) và chụp thử 5 khung, in kích thước JPEG + thời gian.
- Nếu mọi bộ lỗi: quét I2C (SCCB) trên SIOD/SIOC của từng bộ, in địa chỉ trả lời (OV3660 thường 0x3C – ghi chú "chưa chắc"),
  rồi vẫn bật Wi-Fi + trang /status báo lỗi.
- Wi-Fi **SoftAP** SSID `STLAB-CAM-XXXX` (4 hex cuối MAC), WPA2, mật khẩu = 8 ký tự hex cuối MAC viết hoa (tính lúc chạy từ
  `esp_read_mac`, in ra log) – KHÔNG ghi mật khẩu cố định trong mã. IP mặc định 192.168.4.1.
- HTTP server (`esp_http_server`): `/` trang HTML tiếng Việt có dấu (UTF-8): ảnh stream + nút chụp + bảng trạng thái, chọn độ phân
  giải (QVGA/VGA/SVGA/XGA/UXGA/QXGA) + chất lượng; `/stream` MJPEG multipart; `/capture` 1 JPEG; `/status` JSON: chip, flash,
  psram, bo_chan, xclk_mhz, pid, ten_cam_bien, framesize, fps_do_duoc (trung bình 5 s), heap_free, psram_free, nhiet_do_chip
  (temperature_sensor), uptime_s; `/control?framesize=&quality=` đổi tham số.
- In mỗi 10 s: fps, heap, nhiệt độ chip.
- `README.md` ngắn (tiếng Việt có dấu): cách nạp (`flash.bat COMx`), kết nối Wi-Fi, mở 192.168.4.1, gửi lại gì cho Claude.

# Không làm
- Không sửa `build.ps1`, `flash.bat`, `check_probe.py`. Không thêm bộ chân không nguồn. Không bật OTA/cloud. Không mật khẩu cố định.

# Tiêu chí PASS
- Gate exit 0 (build ra `build/probe.bin` + kiểm tĩnh).
