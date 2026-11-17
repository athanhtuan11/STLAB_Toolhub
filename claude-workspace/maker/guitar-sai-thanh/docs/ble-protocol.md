# Giao thức BLE của đàn "GUITAR UMI" (dự án STLab_GuitarSaiThanh)

Giải mã 2026-11-17. Cách làm: (1) PC đọc GATT + nghe notify (bleak), (2) ghi nhật ký HCI trên điện thoại Honor (Android 17)
trong lúc app **Umi Music** (`com.guitar.umi`, Play Store) kéo từng thanh trượt, rồi ghép lệnh ghi theo giờ. Chưa gửi lệnh nào từ PC.

## Phần cứng (từ ảnh bo)
- SoC **Nordic nRF52832** (QFAA, 512 KB flash / 64 KB RAM), anten mạch in `ANT2`. Không có USB dữ liệu (USB-C chỉ sạc – `TODO` xác nhận).
- Đường tiếng: pickup (JST 3 chân) → tiền khuếch đại → ampli class-D (2 IC TSSOP có pad tản nhiệt + cuộn lọc, mã `TODO`) → loa + jack 6,35.
- 3 núm vặn vật lý được chip đọc số (gửi trong gói trạng thái): âm lượng, âm sắc, echo.

## GATT
| UUID | Handle (giá trị) | Quyền | Dùng |
|---|---|---|---|
| 0x1800 Device Name | – | read, write | "GUITAR UMI" |
| **Service 0x2B00** (UUID 16-bit mượn dải SIG – riêng của hãng) | | | |
| 0x2B12 | 0x000D | write, write-no-rsp | App → đàn: lệnh |
| 0x2B10 | 0x000F (CCCD 0x0010) | notify | Đàn → app: trạng thái 129 byte |
| 0x2B16 | 0x0012? | write, notify | Kênh thứ 2 (notify giống hệt 0x2B10) |

Không ghép đôi / không mã hóa: ai ở gần cũng kết nối và ghi được.

## Trình tự app dùng
1. Ghi CCCD `0x0010` = `01 00` (bật notify 0x2B10).
2. Ghi `0x000D` = `55 ff fe 01` → đàn trả 1 gói trạng thái (đoán: lệnh "đọc trạng thái").
3. Mỗi lần kéo thanh trượt: ghi `0x000D` **cả khung 129 byte** (write request, ~15 lần/s khi kéo).

## Khung 129 byte
- Đàn gửi (notify): header `03 10 01 00 <b4> 00 00 00` – `b4` = 0x72…0x75 (đoán mức pin/trạng thái, `TODO`).
- App ghi: header `03 00 01 00 00 00 00 00` + cùng vùng tham số. Byte 40–128 = 0.

| Byte | Ý nghĩa (đã kiểm: app + núm vật lý, 2026-11-17) | Giá trị |
|---|---|---|
| [4] (chỉ gói đàn gửi) | **Điện áp pin × 0,1 V** (0x6D = 10,9 V khớp tab Thông số; 0x75 = 11,7 V lúc pin đầy hơn) | pin 3 cell Li-ion (đoán từ 10,9–11,7 V) |
| [8] | **Độ sáng LED** | 0–30 (35 % ≈ 13, 75 % ≈ 24) |
| [11] | **Màu LED**: nibble thấp = màu chính, nibble cao = màu phụ | đỏ = 1, xanh ngọc = 6 (bảng 8 màu – `TODO` thứ tự đủ) |
| [15] | **Âm lượng guitar** (núm vật lý + app) | 0–30 |
| [19] | **Âm sắc** (núm vật lý + app) | 0–30 |
| [20] | **Mức nhạy dây đàn** | 75 = Trung bình (quạt chả), 100 = Tối đa (rải dây) |
| [21] | **Tự động cân bằng** | 0 = tắt, 2 = bật |
| [22] | **Ngõ ra cho âm ly** (jack ra ampli ngoài) | 0 / 1 |
| [25] | **Độ nhạy mic** (chỉ app) | 0–30 |
| [27] | **Echo** (núm vật lý + app) | 0–30 |
| [30] = 20 | chưa rõ (không đổi khi thử mọi mục) | `TODO` |
| [32] | đàn tự tính (đổi theo âm lượng/âm sắc, 15–25); app chép lại giá trị đàn gửi | `TODO` |
| [45] | **Hiệu ứng âm thanh 3D** | 0 / 1 |

- Tab **Thông số** không ghi gì: hiện pin (từ byte [4]), nhà sản xuất "UMI", phần sụn 0.0.1, ID 00:00:00:00:00:00.
- Mục **Cấu hình AI** (tên + mật khẩu Wi-Fi) có trong app nhưng **chưa thử** (không nhập thông tin Wi-Fi thật). nRF52832 không có Wi-Fi →
  hoặc trên bo có thêm module Wi-Fi, hoặc tính năng chưa dùng (`TODO` kiểm bo).

## Việc còn lại
- Học Solo chưa thử; Cấu hình AI chưa thử (cần quyết có nhập Wi-Fi thử không).
- Thử ghi từ PC (bleak) 1 khung đổi âm lượng – chỉ khi Tuan đồng ý.
- Nếu làm firmware/app STLab: thêm ghép đôi BLE (hiện không bảo mật).
