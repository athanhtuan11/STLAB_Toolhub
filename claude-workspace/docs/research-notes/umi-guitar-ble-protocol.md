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

| Byte | Ý nghĩa (đã kiểm bằng thanh trượt app + núm vật lý) | Khoảng |
|---|---|---|
| [15] | **Âm lượng guitar** (núm vật lý + app) | 0–30 (bước 1 qua app, bước 2 qua núm) |
| [19] | **Âm sắc** (núm vật lý + app) | 0–30 |
| [25] | **Độ nhạy mic** (chỉ app) | 0–30 |
| [27] | **Echo** (núm vật lý + app) | 0–30 |
| [32] | Đàn tự tính (đổi ngược chiều âm lượng/âm sắc, 15–25) – app chép lại giá trị cũ | `TODO` |
| [8]=13, [11]=17, [20]=75, [30]=20 | Chưa rõ – có thể là các mục app ở dưới chưa thử (Tự động cân bằng…) | `TODO` |

## Việc còn lại
- Thử các mục app chưa kéo (Tự động cân bằng, Học Solo, Thông số) → ghép byte còn lại.
- Thử ghi từ PC (bleak) 1 khung đổi âm lượng – chỉ khi Tuan đồng ý.
- Nếu làm firmware/app STLab: thêm ghép đôi BLE (hiện không bảo mật).
