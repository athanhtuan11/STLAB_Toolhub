# Bước 0 – Giao diện: line-bot (xe dò line + tránh vật cản)

Tuan 2026-11-01: "thêm dự án xe dò line, tránh vật cản (tìm hiểu nội dung thi đấu), lên ý tưởng, plan, document".
Mức **A** (xe có vỏ/khung nhìn thấy). Hệ thiết kế: `studio/design/DESIGN.md`. Chưa chọn concept thì chưa dựng cơ khí.
Nghiên cứu luật: `docs/research-notes/line-robot-competitions.md`. Bộ điều khiển: `docs/research-notes/arduino-mega-2560.md`.

## Luật đã kiểm (Claude đọc PDF chính thức 2026-11-01)
| Luật | Số liệu dùng làm ràng buộc |
|---|---|
| RoboCupJunior Rescue Line 2026 | Sa bàn ô 30 × 30 cm, nền trắng, line đen rộng 1–2 cm, cách mép ≥ 10 cm; dấu giao lộ xanh lá 25 × 25 mm; có dốc, gờ giảm tốc, đứt line, bập bênh, vật cản (gạch, khối nặng); cửa ô ≥ 25 cm, trần thấp nhất 25 cm; không dùng điện lưới, ≤ 48 V DC |
| WRO Future Engineers 2026 | Xe ≤ 300 × 200 × 300 mm, ≤ 1,5 kg, **4 bánh có cơ cấu lái** (không vi sai), vạch màu 20 mm, tường 100 mm, biển đỏ/xanh – khác dạng xe này → để bản sau |
| ROBOTACON WRO (VN) | RoboMission dùng LEGO theo thể lệ VN 2026 → xe tự chế **không** dùng được ở bảng này (theo Codex – `TODO` xin thể lệ BTC) |

→ **Chọn chuẩn thiết kế: RCJ Rescue Line** (dò line + giao lộ + vật cản + dốc) – có đủ "dò line, tránh vật cản" và
luật mở phần cứng; sa bàn ô 30 cm làm được ở STLab. Bản `line-bot-fe` (4 bánh lái, camera) để sau nếu đội lên THPT.

## Brief
- **Sản phẩm:** xe tự hành dò line + tránh vật cản, dùng cho lớp robot STLab và đi thi chuẩn RCJ Rescue Line.
  Đối tượng: học sinh **THCS (lớp 6–9)**, đội 2–3 em – `TODO` Tuan xác nhận lớp.
- **Cảm giác:** chắc – mở là thấy mạch – nhanh mà gọn.
- **Kích thước bao (Claude chốt):** ≤ 180 × 180 × 150 mm (lọt cửa ô 25 cm, xoay tại chỗ trong ô 30 cm, dưới trần 25 cm);
  khối lượng mục tiêu ≤ 1,2 kg.
- **Bộ điều khiển:** Arduino Mega 2560 (`arduino-mega-2560` – 54 chân, 4 UART: đủ cho mảng cảm biến + màu + siêu âm).
  Bắt bằng 4 trong 6 lỗ Ø3,2 (đo STEP; bản vẽ chính hãng ghi Ø3) – vít M3, tọa độ trong thư viện.
- **Truyền động:** vi sai 2 bánh + 1 bi đỡ (xoay tại chỗ ở giao lộ, qua gờ). Motor: N20 có encoder (`n20-gearmotor`,
  6 V định mức) – `TODO` chọn tỉ số truyền khi có số đo tốc độ sa bàn.
- **Cảm biến:** mảng hồng ngoại dò line 5–8 kênh (`TODO` chọn module, thêm thư viện); HC-SR04 phía trước (`hc-sr04`)
  tránh vật cản; 2 cảm biến màu đọc dấu xanh hai bên line (`TODO` chọn module).
- **Driver:** TB6612FNG (`TODO` thêm thư viện) – khuyến nghị thay L298N có sẵn (`l298n-module`): L298N sụt áp lớn,
  to và nặng; đổi lại L298N rẻ, đã có ở STLab.
- **Nguồn:** pin Li-ion 2S (7,4 V danh định) có BMS + công tắc + cầu chì – `TODO` chốt dung lượng.
  Đánh đổi: 2S nằm trong dải VIN 7–12 V của Mega khi pin còn đầy, nhưng pin xuống gần 7 V thì ổn áp Mega hụt → cần đo
  thử hoặc thêm mạch buck 5 V (Claude quyết sau khi đo).
- **Nhựa:** Bambu PETG Basic @BBL A1 (mặc định). Màu: Tuan chọn khi in. In không vẽ support vào STL.

## 3 hướng concept (Tuan chọn bằng ảnh)
| | A – Khung tầng | B – Thân liền | C – Khung lưới module |
|---|---|---|---|
| Dáng | 2 tấm phẳng + cột M3, Mega nằm tầng trên, mảng cảm biến gắn mũi | Vỏ liền cong che hết, khoét cửa cảm biến | Tấm lưới lỗ bước đều để học sinh tự gắn cảm biến/servo |
| Hợp với | Lớp học + đi thi (mở nắp là sửa được) | Đi thi, chụp ảnh, đăng MakerWorld | Lớp sáng tạo, thử nhiều bố trí |
| Đổi lại | Kém "đẹp" | Khó sửa dây, in lâu, nặng | Kém cứng, dây lộn xộn |

**Khuyến nghị: A** (dạy được + thi được; đăng MakerWorld kèm hướng dẫn lắp – đúng tiêu chí Boost).

## An toàn (ghi vào ASSEMBLY.md)
- Pin Li-ion 2S: có BMS, cầu chì, không sạc khi không có người trông; khoang pin không để dây cọ mép nhựa; không để chập cực khi lắp.
- Không cấp motor từ chân 5 V của Mega; motor đi qua driver, nguồn motor riêng, chung GND.
- Clone Mega CH340: kiểm ổn áp thực tế trước khi cấp 2S.

## Đầu ra bước 0 (ảnh – Tuan duyệt)
- `concepts/` – 3 concept A/B/C: bóng hông, bóng đỉnh, phối cảnh 3/4 (khối đúng kích thước Mega + pin + motor).
- `cmf.png`, `contact-sheet.png`.

## Quyết định
<!-- Tuan chọn: ngày | concept | ghi chú → chép 1 dòng vào README "Lịch sử sửa" -->
