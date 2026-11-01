# line-bot – xe dò line + tránh vật cản (chuẩn RCJ Rescue Line), Arduino Mega 2560

## Mục tiêu
- Xe tự hành dò line đen, nhận dấu giao lộ xanh, tránh vật cản, qua dốc và gờ giảm tốc trên sa bàn ô 30 × 30 cm.
- Dùng cho lớp robot STLab (THCS lớp 6–9, đội 2–3 em – TODO Tuan xác nhận lớp) và đi thi theo chuẩn RCJ Rescue Line.
- Kích thước bao ≤ 180 × 180 × 150 mm; khối lượng mục tiêu ≤ 1,2 kg (chi tiết: `design/brief.md`).
- Luật và lý do chọn chuẩn: `docs/research-notes/line-robot-competitions.md`.

## Giao diện (bước 0)
Chưa chọn concept – xem `design/brief.md` (3 hướng A/B/C, khuyến nghị A: Khung tầng). Chưa chọn concept thì chưa dựng cơ khí.

## An toàn
- Pin Li-ion 2S: có BMS, cầu chì, không sạc khi không có người trông; khoang pin không để dây cọ mép nhựa; không để chập cực khi lắp.
- Không cấp motor từ chân 5 V của Mega; motor đi qua driver, nguồn motor riêng, chung GND.
- Clone Mega CH340: kiểm ổn áp thực tế trước khi cấp 2S.
- Mega: VIN 7–12 V; mỗi chân I/O tối đa 20 mA (`docs/research-notes/arduino-mega-2560.md`).

## Linh kiện mua (BOM)
| Linh kiện | SL | Nguồn / datasheet | Ghi chú |
|---|---|---|---|
| Arduino Mega 2560 Rev3 (A000067) | 1 | Thư viện Toolhub `arduino-mega-2560` (TODO thêm); datasheet trong `community/` | Bộ điều khiển. Clone CH340: kiểm ổn áp |
| Motor N20 có encoder, 6 V định mức (`n20-gearmotor`) | 2 | TODO | Tỉ số truyền TODO – chờ số đo tốc độ sa bàn |
| Mảng dò line hồng ngoại 5–8 kênh | 1 | TODO chọn module, TODO thêm thư viện | |
| HC-SR04 (`hc-sr04`) | 1 | Thư viện Toolhub | Tránh vật cản phía trước |
| Cảm biến màu | 2 | TODO chọn module | Đọc dấu xanh hai bên line |
| Driver TB6612FNG | 1 | TODO thêm thư viện | Thay L298N (`l298n-module`): sụt áp lớn, to và nặng |
| Pin Li-ion 2S (7,4 V danh định) | 1 | TODO | Dung lượng TODO |
| BMS 2S | 1 | TODO | |
| Công tắc nguồn | 1 | TODO | |
| Cầu chì | 1 | TODO | Trị số TODO |
| Bi đỡ | 1 | TODO | Xoay tại chỗ, qua gờ |
| Vít M3 | TODO | TODO | Bắt Mega 4 trong 6 lỗ; lỗ Ø3,2 mm (đo STEP; bản vẽ chính hãng ghi Ø3 danh nghĩa) – vít M3 |

Lưu ý nguồn: pin 2S khi đầy nằm trong dải VIN 7–12 V của Mega, nhưng khi pin xuống gần 7 V thì ổn áp 5 V có thể hụt. Cần đo thử hoặc thêm mạch buck 5 V (quyết sau khi đo).

## In
Chạy **Chuẩn bị in** rồi chép bảng thời gian/nhựa từ `print/plates/print-overview.png` vào đây khi bản đã duyệt.
Nhựa mặc định: Bambu PETG Basic @BBL A1. Không vẽ support vào STL.

## Lộ trình
0. Concept + ảnh → Tuan chọn (đang làm)
1. Chốt linh kiện + thêm vào thư viện Toolhub (TB6612FNG, mảng dò line, cảm biến màu, pin 2S)
2. CAD khung FreeCAD (tham số), gá cảm biến theo fit-library, kiểm prepare-print
3. In + lắp + ASSEMBLY.md có ảnh
4. Firmware (PlatformIO, Mega): dò line PID, giao lộ dấu xanh, tránh vật cản, dốc/gờ – có test logic chạy trên máy tính
5. Sa bàn tập ô 30 × 30 cm (in decal/giấy) + bài chạy thử đo thời gian
6. Giáo án + video + gói đăng MakerWorld (thiết kế mới của STLab)

## Lịch sử sửa
- 2026-11-01: tạo dự án, brief bước 0, nghiên cứu luật thi.

## Lịch sử in
<!-- /print-result ghi vào đây: ngày | plate | PASS/FAIL | mô tả | ảnh -->
(chưa in)
