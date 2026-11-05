# STLab Cam – firmware chính v0.3.0

Camera giám sát ESP32-S3-CAM N16R8 + OV3660. Ưu tiên: chạy ổn định, xem video và chụp cùng lúc, không kẹt khi đóng tab, không quá nóng.

## Build và nạp
- Build (ESP-IDF 5.5.4, đã xóa biến MSYS): `powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1` → `build/stlab_cam.bin`.
- Nạp USB lần đầu: `idf.py -p <COM> flash` (từ môi trường ESP-IDF PowerShell, không dùng Git Bash; phải nạp cả bootloader vì bật rollback). Sau đó phát hành bằng OTA (mục dưới).
- Kiểm tĩnh: `python check_cam.py`. Kiểm trên mạch: `python test_cam.py --host <IP>`.
- Bảng phân vùng 16 MB: nvs, otadata, phy_init, ota_0 4 MB, ota_1 4 MB (OTA qua Wi-Fi từ v0.3.0).
- `managed_components/` là bản chép từ `../probe` (esp32-camera 2.1.8, mdns 1.14.1) để build không cần mạng.

## Cài Wi-Fi nhà
Dùng `../probe/wifi-setup.py` (lấy SSID + mật khẩu từ Windows, gửi qua cổng COM, không lưu file). Lệnh UART0 trực tiếp: `WIFI <ssid>TAB<mật khẩu>`, `WIFI?`, `WIFI_CLEAR`. Mạch lưu vào NVS, tự vào lại sau khi reset, mDNS `stlab-cam.local`.
AP dự phòng: SSID `STLAB-CAM-xxxx` (xxxx = 2 byte cuối MAC), mật khẩu = 4 byte cuối MAC viết hoa hex (sinh lúc chạy, không in ra log), địa chỉ `http://192.168.4.1`.

## Endpoint
- Cổng 80: `/` (trang web), `/capture` (JPEG khung mới), `/status` (JSON), `/control`, `POST /ota`, `/event.jpg` (ảnh sự kiện chuyển động gần nhất, 404 nếu chưa có), `/events` (JSON 20 sự kiện gần nhất), `/sd?f=<đường dẫn>` (file JPEG trên thẻ; `..`/ký tự lạ 400, không thẻ 503, không có 404).
- Cổng 81: `/stream` (MJPEG, tối đa 2 người xem; người thứ 3 nhận 503 "Toi da 2 nguoi xem").
- `/status`: version, ota_partition, sd_ok, sd_free_mb, time_ok, motion, motion_thr, motion_pct, motion_count, motion_last_s, uptime_s, nhiet_do_chip, nong, fps_cai, fps_thuc, so_nguoi_xem, framesize, quality, vflip, hmirror, brightness, contrast, saturation, aec, ae_level, heap_free, psram_free, frame_loi, cam_reinit, cam_ok, rotate, sta_ssid/sta_ip/sta_rssi/sta_connected, mdns, ap_ssid.

## /control?var=<tên>&val=<số>
| var | giá trị | mặc định |
|---|---|---|
| framesize | QVGA 6, VGA 10, SVGA 11, XGA 12, HD 13, UXGA 15, QXGA 19 (enum esp32-camera 2.1) | 11 (SVGA) |
| quality | 10–40 (nhỏ = đẹp hơn) | 12 |
| vflip, hmirror | 0/1 | 1, 1 (camera lắp ngược 180°) |
| brightness, contrast, saturation | −2..2 | 0 |
| fps | 1–25 (fps stream) | 10 |
| aec | 0/1 (tự phơi sáng) | 1 |
| ae_level | −2..2 | 0 |
| motion | 0/1 (phát hiện chuyển động) | 0 |
| motion_thr | 5–80 (ngưỡng lệch độ sáng 1 điểm ảnh) | 25 |
| motion_pct | 1–50 (% điểm ảnh đổi) | 3 |
| rotate | 0/90/180/270 (chỉ lưu NVS; trang web tự xoay hiển thị và xoay khi tải ảnh) | 0 |

Sai tên/giá trị → HTTP 400. Lưu NVS namespace `cam_cfg`, nạp lại khi khởi động.

## Giao diện v0.2 (main/index.html)
- Một file ≤ 40 KB, nhúng vào flash (`EMBED_TXTFILES`), không tài nguyên ngoài, tự sáng/tối theo `prefers-color-scheme`, chạy cả khi mở qua AP `192.168.4.1`.
- Video `<img id="video">` lấy `http://<location.hostname>:81/stream`. Lỗi stream: nếu `/status` báo ≥ 2 người xem thì hiện "Đã đủ 2 người xem – thử lại sau" + nút Thử lại; ngược lại tự thử lại sau 4 s.
- `/status` cập nhật mỗi 2 s; mất kết nối → chấm đỏ "Mất kết nối", tự thử lại. Ngưỡng nhiệt hiển thị 60/70 °C là hằng số đầu script (`// TODO Tuan chốt ngưỡng`).
- Nút: Chụp ảnh (xem trước), Tải ảnh (`stlab-cam-YYYYMMDD-HHMMSS.jpg`, xoay bằng canvas nếu rotate ≠ 0), Lật 180° (vflip + hmirror), Xoay 90°, độ phân giải, Sáng / Tương phản / fps.
- Đổi struct cấu hình (thêm `rotate`) làm blob NVS cũ không còn khớp kích thước → lần nạp đầu về mặc định (SVGA, lật 180°, 10 fps).

## Kiến trúc
- Một task camera duy nhất gọi `esp_camera_fb_get`: lấy khung theo nhịp fps, copy JPEG vào "khung mới nhất" (5 ô PSRAM, đếm tham chiếu), trả `camera_fb_t` ngay. Stream và capture chỉ đọc khung đã copy.
- Không có người xem và không có yêu cầu chụp → task nghỉ (không lấy khung). `/capture` đánh thức và chỉ nhận khung không cũ hơn 0,3 s.
- Stream ở server cổng 81, mỗi người xem một task riêng (`httpd_req_async_handler_begin`), handler trả về ngay nên cổng 80 không bị chặn. Bộ đếm người xem giảm ở mọi đường thoát của task (lỗi gửi, timeout 5 s không có khung, đóng socket).
- Hai server đều `lru_purge_enable = true`, timeout gửi/nhận 5 s, `ctrl_port` khác nhau (32768 / 32769).
- Đổi framesize: giữ mutex camera (task lấy khung dừng), `set_framesize`, bỏ 3 khung đầu, tiếp tục.
- Watchdog: `fb_get` trả NULL liên tục > 3 s → `esp_camera_deinit` + init lại (đếm `cam_reinit`, log `[CAM] Khoi dong lai camera`).
- Bộ đệm JPEG của driver đặt cố định 768 KB (`jpeg_buffer_size`), không để mặc định.

## Nhiệt độ
Chip > 70 °C → tự hạ còn 5 fps (`[CAM] Nong <t> C - ha fps`, `nong: true`); < 62 °C → trả lại. TODO: ngưỡng 70/62 °C là `#define TEMP_HOT_C` / `TEMP_OK_C` theo yêu cầu spec, chưa có nguồn datasheet; cần xác nhận.

## Lỗi đã sửa
1. Probe phục vụ 1 kết nối/lúc: nay stream ở cổng 81 với task riêng, cổng 80 độc lập.
2. Đóng tab → camera kẹt, `cam_hal: FB-OVF`, `/capture` 500 tới khi reset. Nguyên nhân (suy ra từ đọc code thư viện `managed_components/espressif__esp32-camera/driver/cam_hal.c` và `probe_main.c`, chưa tái hiện riêng trên mạch):
   - (a) Giả thuyết chính: handler stream của probe chạy thẳng trên luồng của server, giữ `camera_fb_t` suốt lúc gửi, và khi `fb_get` trả NULL thì `continue` vĩnh viễn không bao giờ thoát; khi trình duyệt đóng, luồng không kiểm tra kết nối nên chiếm server + khung. `cam_start_frame` (cam_hal.c) chỉ chạy khi có khung rảnh (`frames[x].en == 1`, chỉ được đặt bởi `cam_give` lúc `fb_return`); mọi khung bị giữ → DMA về IDLE, vsync tiếp theo bắt đầu giữa chừng, nhiều tác vụ (`/capture` cùng lúc) tranh khung → trạng thái kẹt. Xác minh: đọc `cam_take`/`cam_give`/`cam_start_frame` trong cam_hal.c và vòng lặp `while(true) { fb_get ... continue }` trong probe.
   - (b) Bộ đệm JPEG chỉ là `rộng × cao / 5` tính theo khung lúc khởi tạo (cam_hal.c dòng ~588–596: `recv_size = width*height/5` khi `jpeg_buffer_size = 0`); khung SVGA chi tiết (q12) hoặc đổi framesize lên cao làm dữ liệu vượt bộ đệm → `FB-OVF`/`DMA overflow` và khung bị loại liên tục.
   - Cách tránh lặp lại: chỉ một task camera lấy khung và trả ngay sau khi copy (không ai giữ `camera_fb_t` trong lúc gửi mạng); `jpeg_buffer_size` cố định 768 KB; đổi framesize dưới mutex rồi bỏ khung đầu; watchdog NULL > 3 s tự init lại camera. Cần Claude xác nhận bằng `test_cam.py` mục 3 (đóng socket đột ngột 5 lần).
3. Stream liên tục 22 fps làm chip 67,8 °C: mặc định 10 fps, hạ 5 fps khi nóng, task nghỉ khi không ai xem.
4. Camera lắp ngược 180°: mặc định vflip = 1, hmirror = 1.

## v0.3.0: OTA, chuyển động, thẻ TF
### OTA qua Wi-Fi
- Cài khóa 1 lần: `python ota-setup.py --port <COM>` – sinh khóa (`secrets.token_urlsafe(24)`), gửi `OTAKEY <khóa>` qua UART0 (mạch lưu NVS namespace `ota`, trả `OTAKEY OK`), lưu `STLAB_CAM_OTA_KEY` vào biến môi trường người dùng bằng `setx` (mở terminal mới mới thấy). Biến đã có thì dùng lại khóa cũ (nhiều mạch dùng chung). `OTAKEY?` trả `OTAKEY SET`/`OTAKEY NONE`; khóa không bao giờ in ra log/UART/HTTP.
- Phát hành: `python ota.py [--host stlab-cam.local] [--bin build/stlab_cam.bin]` – POST `/ota` (header `X-OTA-Key`, body = file .bin ≤ 4 MB), chờ mạch lên lại, so `version` + `ota_partition`. Sai/thiếu/chưa cài khóa 403; đang OTA 409; ảnh hỏng 400/500 và không đổi phân vùng boot.
- Rollback bật (`CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE`): bản mới tự đánh dấu hợp lệ sau 30 s chạy ổn và camera OK; reset/crash trước đó thì bootloader quay về bản cũ. Trang web không có nút tải firmware.
### Phát hiện chuyển động
- Tắt mặc định. Bật: task camera lấy khung ≥ 2 fps kể cả không ai xem (vẫn chỉ MỘT chỗ gọi `esp_camera_fb_get`); task `motion` mỗi 500 ms đọc khung đã copy, giải mã thu nhỏ 1/8 (`jpg2rgb565`) → xám → so với nền trung bình trượt (1/16 mỗi lần). Tỉ lệ điểm lệch > `motion_pct` 2 lần liên tiếp = sự kiện; nghỉ 10 s sau sự kiện. Nóng vẫn chạy 2 fps.
- Sự kiện: log `[MOTION] x%`, `motion_count` tăng, ảnh lưu PSRAM (`/event.jpg`), vòng 20 sự kiện (`/events`), có thẻ thì ghi `stlab-cam/YYYYMMDD/HHMMSS.jpg` (chưa có giờ: `stlab-cam/boot/<giây>.jpg`). Giờ lấy SNTP `pool.ntp.org` sau khi có Wi-Fi nhà, `TZ=ICT-7`.
### Thẻ TF
- SDMMC 1-bit: CLK GPIO39, CMD GPIO38, D0 GPIO40, pull-up trong, 20 MHz. Chân theo Prusa-Firmware-ESP32-Cam `module_ESP32-S3-CAM.h` (cùng bộ chân camera); **chưa thử trên mạch thật** (Tuan chưa có thẻ).
- Không bao giờ format thẻ. Không thẻ: log `[SD] Khong co the` một lần, thử mount lại mỗi 30 s. Chỉ ghi/xóa trong `/sdcard/stlab-cam/`; còn < 10 % hoặc < 200 MB thì xóa thư mục ngày cũ nhất. Ghi ở task riêng qua queue; lỗi ghi → unmount, thử lại mỗi 30 s.
