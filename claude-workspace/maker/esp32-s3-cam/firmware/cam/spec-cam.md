---
task: esp32-s3-cam-firmware-cam
cwd: maker/esp32-s3-cam/firmware/cam
allow:
  - "main/*"
  - "CMakeLists.txt"
  - "sdkconfig.defaults"
  - "partitions.csv"
  - "README.md"
gate: 'powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 && python check_cam.py'
executor: coder
---

# Mục tiêu
Firmware CHÍNH (v0.1.0) cho camera giám sát ESP32-S3-CAM N16R8 + OV3660. Ưu tiên: CHẠY ỔN ĐỊNH, xem video + chụp
cùng lúc, không kẹt khi trình duyệt đóng, không quá nóng. Gate tĩnh `check_cam.py`, `build.ps1` và test phần cứng
`test_cam.py` do Claude viết – KHÔNG sửa. Claude nạp mạch và chạy `test_cam.py`.

# Gốc dùng lại (đã chạy trên mạch thật – xem ../probe)
- Bộ chân FREENOVE_GOOUUU cố định (không dò): XCLK 15, SIOD 4, SIOC 5, D0–D7 = 11, 9, 8, 10, 12, 18, 17, 16, VSYNC 6,
  HREF 7, PCLK 13, PWDN −1, RESET −1, XCLK 20 MHz, JPEG, fb trong PSRAM.
- `../probe/main/wifi_nha.c/.h` (Wi-Fi nhà APSTA, NVS, lệnh UART WIFI/WIFI?/WIFI_CLEAR, mDNS stlab-cam): COPY sang
  `main/` (giữ nguyên hành vi; `../probe/wifi-setup.py` dùng chung được).
- `sdkconfig.defaults` của probe (PSRAM octal, 16 MB, CONFIG_SCCB_HARDWARE_I2C_DRIVER_LEGACY=y nếu còn dùng driver I2C cũ;
  nếu không quét I2C nữa thì dùng driver mới và bỏ dòng này). Project name `stlab_cam` (ra build/stlab_cam.bin).
- AP dự phòng `STLAB-CAM-xxxx`, mật khẩu sinh từ MAC như probe (không lưu trong mã).

# Lỗi đã thấy trên mạch thật (phải hết)
1. Probe phục vụ 1 kết nối/lúc: đang xem /stream thì /capture, /status treo.
2. Đóng tab video → camera kẹt, log liên tục `cam_hal: FB-OVF`, `/capture` trả 500 tới khi reset.
3. Stream liên tục 22 fps → chip 67,8 °C.
4. Camera lắp ngược 180°.
Tìm nguyên nhân gốc cho (2) (ghi vào README mục "Lỗi đã sửa"), không chỉ vá triệu chứng.

# Chức năng
- 2 HTTP server: cổng 80 (`/`, `/capture`, `/status`, `/control`), cổng 81 (`/stream` MJPEG). Mỗi server cấu hình
  `lru_purge_enable = true`, `send_wait_timeout`/`recv_wait_timeout` ≤ 5 s, đủ socket. Stream tối đa 2 người xem cùng lúc
  (người thứ 3 nhận 503 text "Toi da 2 nguoi xem"); mỗi stream chạy task riêng hoặc dùng httpd async handler để không chặn.
- Chỉ 1 nơi gọi esp_camera_fb_get: task camera chụp theo nhịp fps, giữ "khung mới nhất" (copy JPEG vào buffer PSRAM có
  khóa/đếm tham chiếu); stream + capture đọc khung đó. Không ai giữ camera_fb_t quá 1 khung. Không người xem + không chụp →
  task camera nghỉ (không lấy khung) để giảm nhiệt; /capture đánh thức và trả khung mới (không phải khung cũ > 1 s).
- Giới hạn fps stream: mặc định 10 fps (1–25). Nhiệt chip (temperature sensor) > 70 °C → tự hạ còn 5 fps, in
  `[CAM] Nong <t> C - ha fps`, < 62 °C → trả lại; `/status` có `nong: true/false`. (Ngưỡng là `#define`, chưa có nguồn
  datasheet – ghi TODO trong README.)
- `/control?var=<ten>&val=<so>`: framesize (số enum framesize_t của esp32-camera 2.1: QVGA 6, VGA 10, SVGA 11, XGA 12, HD 13, UXGA, QXGA – kiểm trong sensor.h), quality (10–40),
  vflip (0/1), hmirror (0/1), brightness (−2..2), contrast (−2..2), saturation (−2..2), fps (1–25), aec (auto phơi sáng
  0/1), ae_level (−2..2). Sai tên/giá trị → 400. Lưu NVS namespace `cam_cfg`, nạp lại khi khởi động.
  Mặc định: SVGA, quality 12, **vflip 1 + hmirror 1** (sửa lắp ngược), fps 10, aec 1, ae_level 0 (ảnh thật đang cháy sáng
  vùng cửa sổ – để mặc định 0, Tuan tự chỉnh).
- Đổi framesize phải an toàn khi đang stream (dừng lấy khung → đổi → tiếp).
- `/status` JSON: version "0.1.0", uptime_s, nhiet_do_chip, nong, fps_cai, fps_thuc (stream), so_nguoi_xem, framesize (tên),
  quality, vflip, hmirror, brightness, contrast, saturation, aec, ae_level, heap_free, psram_free, frame_loi (đếm fb NULL),
  sta_ssid, sta_ip, sta_rssi, sta_connected, mdns, ap_ssid.
- `/`: trang web gọn (tiếng Việt có dấu, nhúng từ `main/index.html`, không tải tài nguyên ngoài): video từ
  `http://<host>:81/stream`, nút Chụp ảnh (mở/tải /capture), chọn độ phân giải, lật dọc/ngang, sáng/tương phản/fps, bảng
  trạng thái tự cập nhật 2 s (nhiệt đổi màu khi `nong`). Giao diện đẹp làm sau theo mockup – giờ chỉ cần đủ dùng.
- Log `[CAM]` mỗi 10 s: fps_thuc, người xem, nhiệt, heap, frame_loi.
- Watchdog: nếu fb_get trả NULL liên tục > 3 s → `esp_camera_deinit` + init lại camera (đếm `cam_reinit` trong /status), in
  `[CAM] Khoi dong lai camera`.

# Partition (16 MB)
nvs 0x6000, otadata 0x2000, phy_init 0x1000, ota_0 4 MB, ota_1 4 MB (chuẩn bị OTA về sau, CHƯA làm OTA).

# Không làm
Không OTA/cloud/RainMaker, không AI, không ghi thẻ nhớ, không lưu mật khẩu trong mã/log. Không sửa gate/test/build.ps1.

# Tiêu chí PASS
Gate exit 0, build không cảnh báo từ code mình. Sau đó Claude nạp + `python test_cam.py --host 192.168.1.127` PASS.
