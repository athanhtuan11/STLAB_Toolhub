# pushrod-arm – cánh tay robot xi-lanh đẩy

Cánh tay 4 bậc dùng bộ điều khiển **CyberBrick** (Bambu Lab): xoay đế (servo 360°), nâng vai và gập khuỷu bằng
2 xi-lanh **thanh răng – bánh vít – trục vít** chạy động cơ N20, kẹp 2 hàm ăn khớp răng (servo 180°).
In trên **Bambu Lab A1**, đầu phun 0,4 mm, PLA (+ đệm kẹp TPU 95A).

Lắp ráp: **[ASSEMBLY.pdf](ASSEMBLY.pdf)** (15 trang, chữ + hình – để in/gửi) · nguồn [ASSEMBLY.md](ASSEMBLY.md).

## An toàn
- Pin: `Battery_bay` là khoang pin của bộ CyberBrick – loại pin, điện áp: **TODO** (xem datasheet XA003/XA004 trước khi cắm).
  Pin Li-ion: không sạc khi không có người trông, không để chập cực khi lắp dây.
- Động cơ N20 + trục vít tự hãm: khi kẹt cơ khí dòng tăng, nhựa quanh động cơ có thể nóng – thử lần đầu ở tốc độ thấp.

## Linh kiện mua (BOM) – đếm từ model 2026-10-23
Bản tự sinh đầy đủ (vít, linh kiện, chi tiết in → bàn/nhựa): [BOM.md](BOM.md) / `BOM.csv` – cập nhật mỗi lần *Chuẩn bị in*.
| Linh kiện | SL | Ghi chú |
|---|---|---|
| CyberBrick Multi-Function Controller Core XA003 | 1 | MCU |
| CyberBrick Remote Control Receiver Shield XA004 | 1 | + socket 2×8 |
| CyberBrick servo 9g 360° | 1 | xoay đế |
| CyberBrick servo 9g 180° | 1 | kẹp |
| Động cơ N20 (bản CyberBrick, có trục vít) | 2 | vai, khuỷu |
| Khoang pin (`Battery_bay`) | 1 | TODO loại pin |
| Vít M2.5 × 6 | 21 | gồm 6 vít khóa chốt in |
| Vít M2.5 × 8 | 4 | bắt deck |
| Vít M2.5 × 10 | 2 | |
Nguồn model linh kiện: `community/cyberbrick-official` (xem `maker/robotics-cad/library/cyberbrick-sources.tsv`).

## In (bản 2026-10-23 chiều – Bambu PETG Basic, sau lần in thử đầu)
Nhựa: cuộn **Bambu PETG Basic** – profile chính hãng `Bambu PETG Basic @BBL A1` (245 °C, bàn Textured PEI 70 °C, flow 0,94,
13 mm³/s, quạt 30–50 %); đệm kẹp TPU 95A. 7 bàn, tổng **~10 h 26, ~289 g** (Bambu Studio 02.07). **Không dùng support
của slicer** – support tự vẽ (trụ, khe 0,2 mm) chỉ ở bàn P4.
Bảng số liệu luôn mới nhất: [BOM.md](BOM.md) mục "Bàn in".
Ảnh: `print/plates/print-overview.png`; file in: `print/plates/<plate>/<plate>.3mf` (mở Bambu Studio, chọn cuộn PETG Basic).
| Bàn | Thời gian | Nhựa | Ghi chú |
|---|---|---|---|
| P1_Base (0,24 Draft) | 2 h 27 | 92,9 g | vấu deck có vát 45° → không support |
| P2_Turret_Turntable (0,20) | 2 h 53 | 75,5 g | **brim** (đệm, washer nhỏ) |
| P3_Forearm_Plates (0,20) | 41 ph | 21,3 g | |
| P4_Boom_Gripper_Housings (0,20) | 2 h 29 | 74,6 g | **support tự vẽ** dưới Boom, 2 Housing, Gripper_frame – TODO sửa model để bỏ (xem dưới) |
| P5_Gears_Racks_Pins (0,16) | 1 h 33 | 23,1 g | **brim**; bánh vít: phần nhô chỉ là vành hẹp ≤ 1,3 mm → không support |
| P6_GripperPads (TPU 95A) | 5 ph | 0,6 g | brim |
| P7_Worms (0,12, 100%) | 14 ph | 0,9 g | trục vít **dựng đứng** (ren tự in, không support; nằm ngang thì lơ lửng) |

TODO sửa model để bỏ support P4 (Tuan duyệt): Boom001 mặt dưới cách bàn 1,2 mm (vấu nhô 1,2 mm kê cả thân – 607 mm²);
Housing ×2 tai chốt ngang rộng ~7 mm ở z 9,4 / 21,6 (vát 45° mặt dưới tai); Gripper_frame vùng 341 mm² ở z 1,5.

Lưu ý PETG Basic (TDS chính hãng): PEI bám rất chặt → **đợi bàn nguội rồi mới gỡ**; cuộn để ngoài > 72 h ở độ ẩm > 50 %
thì sấy trước (máy sấy/tủ sấy có quạt, không dùng lò vi sóng/lò bếp).

## Lịch sử sửa
- 2026-10-23 18:00: chính sách support mới (Tuan): không để slicer sinh support → P4 dùng support tự vẽ (export
  `support: true`), trục vít dựng đứng, bánh vít không cần support → 7 bàn, 10 h 26, 289 g.
- 2026-10-23 17:40: in thử lỗi (Tuan) – phần nhô ra in **không support**, chi tiết nhỏ bong bàn. Sửa QUY TRÌNH (không
  sửa model): `printability.py` phân tích STL theo hướng in trước khi cắt; bật brim cho bàn có chi tiết nhỏ (P2, P5, P6).
- 2026-10-23 16:00: nhựa → **Bambu PETG Basic** (profile chính hãng, 13 mm³/s) → 10 h 26, 281 g.
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
- 2026-10-23 | (bàn chưa ghi rõ) | FAIL | phần treo/nhô ra in không support → lỗi; chi tiết nhỏ cần brim (Tuan báo).
  Nguyên nhân: slicer chỉ báo cụm rời hẳn, phần nhô dính liền không bị báo. Đã sửa quy trình, cắt lại 8 bàn – xem Lịch sử sửa.
  TODO Tuan: bàn/chi tiết nào hỏng + ảnh, để đối chiếu với danh sách tự phát hiện.
