# guitar-sai-thanh – đàn guitar có loa + Bluetooth "GUITAR UMI" (STLab_GuitarSaiThanh)

Tuan đưa vào 2026-11-17: đàn guitar có mạch thu âm từ dây đàn rồi phát ra loa tích hợp, điều khiển qua app **Umi Music**
(`com.guitar.umi`, Play Store). Mục tiêu hiện tại: hiểu mạch + giao thức, xem có thay chip điều khiển bằng ESP32 được không.

## Đã biết
- 2 bộ não: **Nordic nRF52832** (BLE với app, ANT2) + **ESP32-PICO-D4** (xử lý âm thanh + Wi-Fi "Cấu hình AI", ANT1) → DAC **TI PCM5100** → ampli U12. Bo "Ledtech": chỉnh âm Bass/Middle/Treble, ampli class-D, tụ 680 µF 25 V, pin + sạc USB.
  Ảnh: `docs/photos/` (chỉ trên máy, không lên git).
- Giao thức BLE đã giải mã một phần: `docs/ble-protocol.md`. Công cụ: `tools/` (bleak + đọc btsnoop).
- Điện thoại thử: Honor BKQ-AN10 (Android 17), adb qua Wi-Fi; nhật ký HCI của Honor nằm ở `/data/log/bt/btsnoop_hci_*.log`
  (không có trong bugreport). Git Bash: đặt `MSYS_NO_PATHCONV=1` khi gọi adb với đường dẫn `/sdcard`, `/data`.

## Quy tắc
- **Không ghi lệnh vào đàn khi Tuan chưa đồng ý** (đàn không có bảo mật BLE; lệnh lạ có thể đổi cài đặt / kích DFU).
- Không nạp lại hoặc xóa firmware nRF52832 (chưa sao lưu được – cần SWD + kiểm APPROTECT).
- Mạch có pin (nhiều khả năng Li-ion) + tụ 680 µF: ngắt pin trước khi đo/hàn.

## Trạng thái
- 2026-11-17: giải mã gần đủ khung 129 byte (âm lượng, âm sắc, echo, độ nhạy mic, mức nhạy dây, cân bằng, 3D, ngõ ra âm ly, LED, pin ×0,1 V). Phân tích ESP32: `docs/esp32-replacement.md` – thay thẳng chip KHÔNG được; gắn module ESP32 ngoài giữ mạch tiếng ĐƯỢC (cần ảnh chip DSP + máy phân tích logic bắt I2C).
- 2026-11-17: ảnh mặt sau → có sẵn ESP32-PICO-D4 + PCM5100. Hướng: sao lưu flash ESP32 (esptool, USB–UART 3,3 V, chỉ đọc) + bắt UART nRF↔ESP32; chờ Tuan có USB–UART / máy phân tích logic.
