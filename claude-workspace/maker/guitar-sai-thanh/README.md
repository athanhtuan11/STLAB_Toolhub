# guitar-sai-thanh – Đàn guitar có loa Bluetooth (GUITAR UMI)

Đàn guitar gắn sẵn mạch thu âm dây đàn → chỉnh âm → ampli → loa trong thân; chỉnh âm lượng, âm sắc, echo, độ nhạy mic qua
app Umi Music (Bluetooth LE).

## Trạng thái
- 2026-11-17: phân tích mạch từ ảnh (nRF52832 + ampli class-D); giải mã giao thức BLE một phần (`docs/ble-protocol.md`).

## An toàn
- Có pin + tụ lớn: ngắt pin trước khi mở mạch, không chạm chân tụ 680 µF.
- Đàn không có bảo mật Bluetooth: ai ở gần cũng điều khiển được.

## Thư mục
- `docs/ble-protocol.md` – GATT + khung lệnh 129 byte.
- `docs/photos/` – ảnh bo (chỉ trên máy).
- `tools/` – `ble_scan.py`, `ble_dump.py`, `ble_watch.py` (bleak), `parse_btsnoop.py` (đọc nhật ký HCI Android).
