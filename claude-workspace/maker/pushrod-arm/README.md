# pushrod-arm – cánh tay robot xi-lanh đẩy

Cánh tay 4 bậc dùng bộ điều khiển **CyberBrick** (Bambu Lab): xoay đế (servo 360°), nâng vai và gập khuỷu bằng
2 xi-lanh **thanh răng – bánh vít – trục vít** chạy động cơ N20, kẹp 2 hàm ăn khớp răng (servo 180°).
In trên **Bambu Lab A1**, đầu phun 0,4 mm, PLA (+ đệm kẹp TPU 95A).

## An toàn
- Pin: `Battery_bay` là khoang pin của bộ CyberBrick – loại pin, điện áp: **TODO** (xem datasheet XA003/XA004 trước khi cắm).
  Pin Li-ion: không sạc khi không có người trông, không để chập cực khi lắp dây.
- Động cơ N20 + trục vít tự hãm: khi kẹt cơ khí dòng tăng, nhựa quanh động cơ có thể nóng – thử lần đầu ở tốc độ thấp.

## Linh kiện mua (BOM) – đếm từ model 2026-10-23
| Linh kiện | SL | Ghi chú |
|---|---|---|
| CyberBrick Multi-Function Controller Core XA003 | 1 | MCU |
| CyberBrick Remote Control Receiver Shield XA004 | 1 | + socket 2×8 |
| CyberBrick servo 9g 360° | 1 | xoay đế |
| CyberBrick servo 9g 180° | 1 | kẹp |
| Động cơ N20 (bản CyberBrick, có trục vít) | 2 | vai, khuỷu |
| Khoang pin (`Battery_bay`) | 1 | TODO loại pin |
| Vít M2.5 × 6 | 15 | |
| Vít M2.5 × 8 | 4 | bắt deck |
| Vít M2.5 × 10 | 2 | |
Nguồn model linh kiện: `community/cyberbrick-official` (xem `maker/robotics-cad/library/cyberbrick-sources.tsv`).

## In (bản 2026-10-23 – PETG, chưa in thử)
Nhựa mặc định **PETG KINGROON** (preset riêng đã hiệu chỉnh: flow 0,95, PA 0,02, 8 mm³/s, 240/250 °C, bàn textured 70 °C);
đệm kẹp TPU 95A. 7 bàn, tổng **~12 h 29, ~288 g** (Bambu Studio 02.07). Ảnh: `print/plates/print-overview.png`;
file in: `print/plates/<plate>/<plate>.3mf` (mở bằng Bambu Studio, chọn đúng cuộn PETG KINGROON).
| Bàn | Thời gian | Nhựa | Ghi chú |
|---|---|---|---|
| P1_Base (0,24 Draft) | 3 h 18 | 95,4 g | vấu deck có vát 45° → không support |
| P2_Turret_Turntable (0,20) | 3 h 17 | 76,3 g | |
| P3_Forearm_Plates (0,20) | 51 ph | 21,8 g | |
| P4_Boom_Gripper_Housings (0,20, support) | 3 h 13 | 71,1 g | gộp 2 Housing (tai chốt cần support) vào bàn support sẵn có |
| P5_Gears_Racks_Pins (0,16) | 1 h 29 | 22,4 g | |
| P6_GripperPads (TPU 95A) | 4 ph | 0,5 g | |
| P7_Worms (0,12, 100%) | 13 ph | 0,9 g | |

Muốn nhanh hơn: làm **Calibration → Max volumetric speed** trong Bambu Studio cho cuộn KINGROON. Nếu đạt 12 mm³/s
thì sửa preset → tổng ~10 h 37 (đã cắt thử 2026-10-23: 10 mm³/s ~11 h 19). Chưa hiệu chỉnh thì giữ 8.

## Lịch sử sửa
- 2026-10-23 15:40: đổi nhựa PLA → **PETG KINGROON** (preset riêng); gộp 2 Housing vào bàn support P4 → 7 bàn
  (thời gian in 9 h → 12 h 29 do preset giới hạn 8 mm³/s; PLA chính hãng 21 mm³/s).
- 2026-10-23 15:15: gom toàn bộ dự án về `maker/pushrod-arm/` (`freecad/` + `print/`), đặt tên tiếng Anh;
  thôi dùng `D:\06_FreeCAD` (giữ 3 bản sao lưu mới nhất ở `freecad/backup/`; thư mục cũ Tuan tự xóa).
- 2026-10-23 15:00 (Claude, VS Code, Tuan duyệt): mài hốc servo kẹp trong `Gripper_frame` 0,05 mm (2 mặt 52,5 mm²,
  khe 0,15 → 0,2); vát 45° dưới 4 vấu bắt vít deck trong `Base_housing` (+0,7 cm³) → bàn P1 **bỏ được support**;
  washer chặn trục để tự do 0,1 mm (khai `mesh-pair`). Kết quả: kiểm nhanh WARN (không FAIL), cắt lớp PASS.
- 2026-10-23 (Claude, VS Code): về tư thế gốc (file bị lưu lúc mô phỏng); khe lắp ghép lên 0,2 mm – mài 2 washer trục
  1,2 → 1,1 mm, khoét housing 0,2 mm vùng bánh vít quay (2 housing); gọt 2 trụ vít lấn 0,1 mm qua khe đáy
  `Base_housing` (bỏ 2 mặt treo 0,09 mm²). Script đã chạy: `freecad/scripts/history/2026-10-23_*.py`.
- 2026-10-23 (Claude Desktop): sửa va chạm gear z60/servo 360, plate R/servo kẹp, trục mâm (vít M2.5 × 10 + vấu),
  4 vít deck (M2.5 × 8 + vấu housing), dựng lại plate L/R (B-spline bậc 14 hỏng), deck còn mảnh vách lỗ cũ.

## Lịch sử in
<!-- /print-result ghi vào đây: ngày | plate | PASS/FAIL | mô tả | ảnh -->
(chưa in)
