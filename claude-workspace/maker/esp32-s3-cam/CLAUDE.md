# esp32-s3-cam – camera AI ESP32-S3 + OV3660

Dự án Tuan bắt đầu 2026-11-03. Mạch **ESP32-S3-CAM N16R8** (16 MB flash, 8 MB PSRAM octal, dạng giống ESP32-CAM, khe FPC 24 chân)
+ camera **WS-OV3660-8225N-40027** (OV3660 3 MP; ý nghĩa hậu tố 8225N/40027: TODO – chưa có nguồn).

## Mục tiêu (Tuan chọn cả 4)
1. Nhận diện AI trên chip (ESP-WHO / ESP-DL, TFLite Micro person detection, Edge Impulse).
2. Bài học STEAM / bộ kit bán (vỏ in 3D + firmware mẫu + giáo án).
3. Mắt robot (stream cho line-bot / tay máy CyberBrick).
4. Camera giám sát / smart home (ESPHome + Home Assistant).

## Đã biết (có nguồn – xem docs/research-notes/esp32-s3-cam-hardware.md)
- Không có sơ đồ chân chung cho "ESP32-S3-CAM N16R8": tùy hãng mạch. Bộ chân Freenove/GOOUUU: XCLK 15, SIOD 4, SIOC 5,
  D0–D7 = 11, 9, 8, 10, 12, 18, 17, 16, VSYNC 6, HREF 7, PCLK 13, PWDN/RESET −1 (chưa chắc cho mạch của Tuan).
- `espressif/esp32-camera` hỗ trợ OV3660 tới 2048 × 1536 (JPEG); cần PSRAM; ESP32-S3 2 MP chỉ ổn cho ảnh tĩnh JPEG.
- OV3660 cần nguồn 2,8 V (analog) + 1,5 V (lõi) – module camera tự có LDO (kiểm trên module).
- Dòng tiêu thụ khi stream, IC ổn áp trên mạch: TODO (đo/đọc mạch thật).

## An toàn
- Cấp nguồn USB-C 5 V. Camera + ESP32-S3 nóng khi stream lâu – không bọc kín vỏ không lỗ thoát nhiệt.
- Pin Li-ion 18650 (nếu dùng): chỉ cell có mạch bảo vệ + mạch tăng áp/sạc đúng dòng; chưa thiết kế phần pin.
- Cắm/rút cáp FPC camera khi đã rút nguồn; cáp FPC dễ gãy.

## Firmware
- `firmware/probe/` (ESP-IDF 5.5.4): dò chip/PSRAM/flash, thử bộ chân camera, đọc PID cảm biến, phát Wi-Fi AP
  `STLAB-CAM-xxxx` (mật khẩu in ra cổng serial, sinh từ MAC – không lưu trong mã) + trang xem hình.
  Build: `powershell -ExecutionPolicy Bypass -File build.ps1`; nạp + xem log: `flash.bat COMx`.

## Kết quả dò phần cứng (2026-11-03, mạch thật của Tuan)
- Chip ESP32-S3R8 QFN56 rev v0.2 (hàn thẳng, không module), thạch anh 40 MHz; PSRAM 8 MB octal trong chip (AP gen 3,
  3 V, 80 MHz); flash 16 MB Boya (0x68/0x4018), DIO/QIO, 3,3 V; MAC 98:A3:16:EC:54:68.
- Nạp/log: cổng **mini USB → CH340 → UART0 (COM6)**, tự reset bằng RTS. USB native (GPIO19/20) có đi dây (demo xưởng chạy
  TinyUSB 303A:4001) – cổng nào: TODO. Đèn đỏ = nguồn; đèn xanh = **WS2812** (demo xưởng `led_strip`; chân: TODO).
- **Camera: bộ chân FREENOVE_GOOUUU đúng**, XCLK 20 MHz, OV3660 PID 0x3660 @ I2C 0x3C. SVGA JPEG ~19 KB/khung, 35 ms/khung.
- Chân đã chiếm: camera (4,5,6,7,8,9,10,11,12,13,15,16,17,18), PSRAM octal (35–37), UART0 (43/44), USB (19/20).
  Chân trống cho robot: TODO – đối chiếu header thật (ảnh mạch).
- Nhiệt chip lúc nghỉ 41–42 °C. Cảnh báo `NO-SOI` lúc Wi-Fi khởi động (vài khung hỏng) – theo dõi khi stream.
- Lưu ý build: esp32-camera mặc định driver I2C mới; probe quét I2C bằng driver cũ → đặt
  `CONFIG_SCCB_HARDWARE_I2C_DRIVER_LEGACY=y` (IDF 5.5 cấm trộn 2 driver → abort khởi động).

## Trạng thái
- 2026-11-03: firmware dò chạy trên mạch thật. Tiếp: Tuan xem hình qua AP → đo fps stream/nhiệt khi chạy lâu → bước 0 dáng
  vỏ + giao diện web → chọn thứ tự 4 hướng.
