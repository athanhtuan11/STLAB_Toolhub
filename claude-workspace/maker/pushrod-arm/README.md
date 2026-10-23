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

## In (bản 2026-10-23 – chưa in thử)
8 bàn, tổng **~9 giờ, ~295 g** nhựa (theo Bambu Studio 02.07, profile A1 chính hãng, 15:00). Ảnh: `anh/tong-quan-in.png`.
| Bàn | Thời gian | Nhựa | Ghi chú |
|---|---|---|---|
| P1 Đế (0,24 Draft) | 1 h 59 | 97,7 g | vấu deck đã có vát 45° → không support |
| P2 Turret, mâm (0,20) | 2 h 19 | 78,1 g | |
| P3 Forearm, vỏ xi-lanh (0,20) | 38 ph | 22,3 g | |
| P3 – support | 1 h 08 | 25,9 g | 2 Housing: tai chốt treo z 3–9 mm |
| P4 Boom, khung kẹp (0,20, support) | 1 h 21 | 47,0 g | |
| P5 Bánh răng, thanh răng, chốt (0,16) | 1 h 18 | 22,9 g | |
| P6 Đệm kẹp TPU 95A | 4 ph | 0,5 g | |
| P7 Trục vít (0,12, 100%) | 8 ph | 0,9 g | |

## Lịch sử sửa
- 2026-10-23 15:00 (Claude, VS Code, Tuan duyệt): mài hốc servo kẹp trong `Gripper_frame` 0,05 mm (2 mặt 52,5 mm²,
  khe 0,15 → 0,2); vát 45° dưới 4 vấu bắt vít deck trong `Base_housing` (+0,7 cm³) → bàn P1 **bỏ được support**;
  washer chặn trục để tự do 0,1 mm (khai `an-khop`). Kết quả: kiểm nhanh WARN (không FAIL), cắt lớp PASS.
- 2026-10-23 (Claude, VS Code): về tư thế gốc (file bị lưu lúc mô phỏng); khe lắp ghép lên 0,2 mm – mài 2 washer trục
  1,2 → 1,1 mm, khoét housing 0,2 mm vùng bánh vít quay (2 housing); gọt 2 trụ vít lấn 0,1 mm qua khe đáy
  `Base_housing` (bỏ 2 mặt treo 0,09 mm²). Backup: `D:\06_FreeCAD\pushrod_arm\_backup\*20261023-142*`.
- 2026-10-23 (Claude Desktop): sửa va chạm gear z60/servo 360, plate R/servo kẹp, trục mâm (vít M2.5 × 10 + vấu),
  4 vít deck (M2.5 × 8 + vấu housing), dựng lại plate L/R (B-spline bậc 14 hỏng), deck còn mảnh vách lỗ cũ.

## Lịch sử in
<!-- /ket-qua-in ghi vào đây: ngày | bàn | đạt/lỗi | mô tả | ảnh -->
(chưa in)
