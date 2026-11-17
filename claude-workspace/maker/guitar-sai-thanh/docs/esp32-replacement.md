# Thay nRF52832 bằng ESP32 được không? (phân tích 2026-11-17)

Dựa trên: ảnh bo (`photos/`), giao thức đã giải mã (`ble-protocol.md`). Chưa đo mạch thật → các chỗ ghi `TODO`.

## 1. nRF52832 đang làm gì (suy ra từ giao thức + ảnh)
| Việc | Bằng chứng |
|---|---|
| BLE với app Umi (service 0x2B00, khung 129 byte) | đọc GATT + nhật ký HCI |
| Đọc 3 núm vặn (âm lượng, âm sắc, echo) bằng ADC → gửi app | gói trạng thái đổi theo núm |
| Đo điện áp pin (byte [4], 10,9 V) | khớp tab Thông số |
| Đặt âm lượng / âm sắc / echo / độ nhạy mic / mức nhạy dây / tự động cân bằng / 3D / ngõ ra âm ly | app ghi byte → âm thanh đổi. **Cách chip áp dụng (I2C tới DSP? biến trở số? PWM?) chưa biết** – `TODO` |
| Điều khiển LED (độ sáng, 2 màu) | byte [8], [11] |
| "Cấu hình AI" qua Wi-Fi | app có ô nhập Wi-Fi, nhưng nRF52832 **không có Wi-Fi** → trên bo có chip khác hoặc tính năng chưa làm – `TODO` |

Echo, 3D, tự động cân bằng là xử lý âm thanh số → gần như chắc có **chip DSP âm thanh riêng** (2 IC TSSOP mặt sau / chip QFN gần cuộn cảm).
nRF52832 chỉ là "bộ não điều khiển", tiếng không đi qua nó (đoán – `TODO` đo).

## 2. ESP32 làm được các việc đó không?
**Về chức năng: ĐƯỢC, và còn hơn.** ESP32-C3 / ESP32-S3: BLE 5 (giả lập đúng GATT 0x2B00 → app Umi vẫn dùng được), ADC cho núm + pin,
I2C/PWM điều khiển DSP/ampli, RMT cho LED, **có Wi-Fi** (làm được mục "Cấu hình AI" mà nRF52832 không làm được).

## 3. Thay thẳng trên bo (hàn chip ESP32 vào chỗ nRF52832): KHÔNG
- Khác chân, khác vỏ (nRF52832 QFN48 6×6 vs ESP32-C3 QFN32 / S3 QFN56) → không có chỗ hàn.
- Khác thạch anh (nRF 32 MHz, ESP32 40 MHz), khác mạch phối hợp anten.
- Dòng: ESP32 phát Wi-Fi đỉnh khoảng 340 mA (S3, datasheet Espressif) so với nRF52832 vài mA → mạch nguồn 3,3 V trên bo có thể không đủ – `TODO` đo IC ổn áp.

## 4. Hướng làm được (khuyên)
**Phương án A – Gắn module ESP32 ngoài, giữ nguyên mạch tiếng (khuyên):**
1. Đo xem nRF52832 nối ra những đường nào: I2C tới DSP (header có chân SDA/SCL), chân ADC núm, LED, chân bật ampli/ngõ ra.
2. Bắt bằng **máy phân tích logic** (loại 8 kênh 24 MHz giá rẻ) trên SDA/SCL trong lúc kéo từng mục trong app → ghép "byte khung BLE → lệnh I2C tới DSP".
3. Giữ nRF52832 ở trạng thái reset (hoặc cắt đường), nối module ESP32 (vd ESP32-C3 SuperMini) vào đúng các đường đó, nguồn 3,3 V riêng qua buck từ pin.
4. Firmware ESP32: giả lập GATT 0x2B00 (app Umi vẫn chạy) + thêm Wi-Fi/tính năng STLab.

**Phương án B – Làm lại toàn bộ bằng ESP32 có codec (vd bo ESP32-A1S / ES8388):** pickup → ADC codec → ESP32 tự làm EQ, echo, 3D bằng phần mềm
→ DAC → ampli. Linh hoạt nhất, hợp dạy STEAM, nhưng phải thiết kế lại tiền khuếch đại pickup và ampli – việc lớn.

## 5. ⚠️ An toàn
- Pin **3 cell Li-ion (10,9–12,6 V)**: chân ESP32 chỉ chịu 3,3 V → phải có buck 3,3 V; không nối pin vào chân ESP32. Ngắt pin khi hàn.
- Tụ 680 µF 25 V giữ điện sau khi tắt; xả trước khi chạm.
- Chưa sao lưu được firmware gốc nRF52832 (cần SWD, có thể bị khóa APPROTECT) → làm phương án A thì **giữ nguyên nRF trên bo** để còn quay lại được.

## 6. Cần để quyết
1. Ảnh nét, thẳng mã chữ trên 2 IC TSSOP mặt sau + chip QFN gần cuộn cảm + chip `U12` → biết DSP/ampli.
2. Máy phân tích logic (nếu chọn A).
3. Có thêm module Wi-Fi trên bo không (tìm anten/khối kim loại thứ hai).
