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
- 2026-11-17: umi_set.py điều khiển đàn từ PC qua BLE OK (âm lượng 20→10→20). Thử Wi-Fi "Cấu hình AI" bằng điểm phát PC (UMI-K9-2026, 2,4 GHz) – đàn không vào mạng (PC đang ở 5 GHz ch60, nghi điểm phát bị kéo 5 GHz). **Tuan: Wi-Fi không cần → bỏ qua.** Tiếp: trang web điều khiển qua Web Bluetooth.
- 2026-11-17: **firmware v0.1 A1S gate PASS** (host 25 mục + build thật 552 KB = 27 % phân vùng). Chưa nạp mạch. TODO: xác nhận ADC LIN1, PGA 0 dB, pin cố định 12,0 V, mic/âm ly/LED chỉ lưu. Tiếp: Tuan đồng ý → nạp COM5, thử app Umi + TONE + KEY5/6; v0.2 A2DP.
- 2026-11-18: Tuan: **bỏ qua app Umi, ưu tiên mạch tự chạy**. "Loop" của mạch khách = bật nguồn, gảy đàn là tiếng ra loa ngay (không bấm gì) – KHÔNG phải looper ghi/phát lặp (bản looper dở → `backup/20261118-guitar-looper-wip/`). Firmware: mặc định **mic trên bo (IN 2) + PGA 24 dB**, lệnh UART `IN`/`GAIN` lưu NVS; đã nạp COM5, khởi động tự chạy (mức vào ~2 900, vòng 171/172). TODO: Tuan gảy đàn nghe thử, kiểm hú (mic gần loa). A2DP = v0.3 (`firmware/a1s/spec-v03.md`, gate `tests/test_gate_v03.py`, chưa giao).
