# pushrod-arm – cánh tay robot xi-lanh đẩy

Cánh tay 4 bậc dùng bộ điều khiển **CyberBrick** (Bambu Lab): xoay đế (servo 360°), nâng vai và gập khuỷu bằng
2 xi-lanh **piston** (2026-10-25, kiểu Cyberbrick Excavator: bánh răng z28/z12 → ty ren M3 → piston kẹp đai ốc M3 → ty rỗng)
chạy động cơ **CyberBrick 030 + hộp giảm tốc 1 trục** (đặt cạnh ống), kẹp 2 hàm ăn khớp răng (servo 180°).
Thay xi-lanh thanh răng cũ vì `Rack_Elbow` lệch khi lên xuống – phân tích: `docs/reports/pushrod-arm-actuator-alternatives.md`.
In trên **Bambu Lab A1**, đầu phun 0,4 mm, PLA (+ đệm kẹp TPU 95A).

Lắp ráp: **[ASSEMBLY.pdf](ASSEMBLY.pdf)** (15 trang, chữ + hình – để in/gửi) · nguồn [ASSEMBLY.md](ASSEMBLY.md).

## An toàn
- Pin: `Battery_bay` là khoang pin của bộ CyberBrick – loại pin, điện áp: **TODO** (xem datasheet XA003/XA004 trước khi cắm).
  Pin Li-ion: không sạc khi không có người trông, không để chập cực khi lắp dây.
- Động cơ 030 (LA024, 5–9 V) + ty ren M3: **không để kẹt trục khi cấp điện** (datasheet: nóng, nguy cơ cháy) – thử tay trước,
  lần đầu chạy chậm. **Không có công tắc hành trình**: không giữ cần điều khiển khi ty đã ra/vào hết.

## Linh kiện mua (BOM) – đếm từ model 2026-10-23
Bản tự sinh đầy đủ (vít, linh kiện, chi tiết in → bàn/nhựa): [BOM.md](BOM.md) / `BOM.csv` – cập nhật mỗi lần *Chuẩn bị in*.
| Linh kiện | SL | Ghi chú |
|---|---|---|
| CyberBrick Multi-Function Controller Core XA003 | 1 | MCU |
| CyberBrick Remote Control Receiver Shield XA004 | 1 | ghép với XA003 (lõi cắm mặt dưới) |
| CyberBrick servo 9g 360° | 1 | xoay đế |
| CyberBrick servo 9g 180° | 1 | kẹp |
| CyberBrick 030 Micro DC Motor LA024 + Single-axis Reduction Gear Kit (LA012…LA022, mã TODO) | 2 | vai, khuỷu; vỏ hộp số in theo file hãng |
| Ty ren M3 inox (cắt 55 mm + 45 mm) | 2 | xi-lanh khuỷu / vai (2026-10-25) |
| Đai ốc lục giác M3 (DIN 934) | 4 | 2 kẹp trong bánh răng z12, 2 trong piston |
| Khoang pin (`Battery_bay`) | 1 | TODO loại pin |
| Vít M2.5 × 6 | 21 | gồm 6 vít khóa chốt in |
| Vít M2.5 × 8 | 4 | bắt deck |
| Vít M2.5 × 10 | 2 | |
Nguồn model linh kiện: `community/cyberbrick-official` (xem `tools/robotics-cad/library/cyberbrick-sources.tsv`).

## In (bản 2026-10-25 – Bambu PETG Basic, 8 bàn)
Nhựa: cuộn **Bambu PETG Basic** – profile chính hãng `Bambu PETG Basic @BBL A1` (245 °C, bàn Textured PEI 70 °C, flow 0,94,
13 mm³/s, quạt 30–50 %); đệm kẹp TPU 95A. 8 bàn, tổng **~10 h 58, ~288 g** (cắt lớp 2026-10-25).
**Support: KHÔNG vẽ vào STL – Tuan tô trong Bambu Studio** (support tự vẽ từng lấp rãnh thanh răng Housing + lỗ trục Worm).
Khi tô: giữ trống rãnh thanh răng, rãnh chữ U trục vít, hốc bánh vít, mọi lỗ chốt.
Bảng số liệu luôn mới nhất: [BOM.md](BOM.md) mục "Bàn in".
Ảnh: `print/plates/print-overview.png`; file in: `print/plates/<plate>/<plate>.3mf` (mở Bambu Studio, chọn cuộn PETG Basic).
| Bàn | Thời gian | Nhựa | Ghi chú |
|---|---|---|---|
| P1_Base (0,24 Draft) | 2 h 27 | 92,9 g | vấu deck có vát 45° → không support |
| P2_Turret_Turntable (0,20) | 2 h 56 | 76,3 g | **brim** (đệm, washer nhỏ) |
| P3_Forearm_Plates (0,20) | 41 ph | 21,3 g | |
| P4_Boom_Gripper_Housings (0,20) | 2 h 29 | 71,5 g | **Tuan tô support**: dưới Boom, tai chốt 2 Housing, Gripper_frame |
| P5_Gears_Racks (0,16) | 1 h 13 | 16,9 g | **brim** |
| P6_GripperPads (TPU 95A) | 5 ph | 0,6 g | brim |
| P7_Worms (0,12, 100%) | 34 ph | 1,9 g | trục vít dựng đứng, lỗ trục hộp số ở đáy (mái lỗ tự bắc cầu) |
| P8_Pins (0,16, **100%**) | 29 ph | 6,8 g | chốt khớp **đặc, in nằm**, thân Ø4,8 (khe 0,3 mm/bên) |
In lại riêng (còn dùng): `plates-reprint-cylinders-2026-10-26/` (R10 2 vỏ xi-lanh, R11 2 ty piston, R9 bánh răng z28/z12 +
Pin_gearbox) và `plates-reprint-pins-2026-10-25/` (R5: 7 chốt Ø4,8). 2026-10-26 đã xóa bộ cũ không dùng: R1–R3 (trục vít),
R6 (vỏ thanh răng), R7/R8 (piston chưa lắp được), bộ chốt thử Ø4,6–4,9 (đã chọn Ø4,8; sinh lại: `freecad/scripts/make_pin_gauge.py`).

Lưu ý PETG Basic (TDS chính hãng): PEI bám rất chặt → **đợi bàn nguội rồi mới gỡ**; cuộn để ngoài > 72 h ở độ ẩm > 50 %
thì sấy trước (máy sấy/tủ sấy có quạt, không dùng lò vi sóng/lò bếp).

## Nâng cấp lần sau (v2) – Tuan 2026-10-25
- **Làm lại đế chuẩn (`Base_housing`)**: trụ bắt bộ thu phải đúng chiều cao chồng XA003 + XA004 chính hãng (cao 21,5 mm)
  ngay trên vỏ – **bỏ 4 ống nâng `Receiver_riser`** (bản này chỉ kê tạm vì vẽ sai chiều cao bộ thu) và vít bộ thu về cỡ ngắn.
- Cùng lúc sửa đế: ngàm/vít giữ chân đế với vỏ (hiện dán băng dính), chỗ giữ khối pin (hiện dán), máng đi dây, giữ servo đế
  bằng ngàm thay vì chỉ dựa tấm đậy.
- Quy tắc: đổi/sai linh kiện thì **sửa chi tiết gốc**, không thêm miếng kê/đệm tạm (trừ khi đã in rồi và Tuan cho làm tạm).

## Lịch sử sửa
- 2026-10-26: **xi-lanh LẮP ĐƯỢC** (Tuan: `Housing_Elbow` + `Piston_rod_Elbow` in rời không lắp vào nhau). Công cụ mới
  `tools/robotics-cad/scripts/assembly_paths.py` + test `T9Assemble` tìm 4 lỗi ở cả 2 xi-lanh: piston 6 × 10,4 > bạc miệng
  ống 6,6 × 8,6 (đầu kia kín); đai ốc M3 nhốt trong hốc kín; ty ren M3 đâm 8,8 mm³ thành trước buồng bánh răng (bị
  `ignore-pair=LK_*|*` che – đã bỏ); `Pin_gearbox` đâm hộp số ~52 mm³/chốt (STEP: kênh Ø4 bịt 2 đầu – **chờ xem hộp số
  thật**, test expectedFailure). Sửa (`history/2026-10-26_cylinder_assemblable.py`, `..._piston_nut_rot30.py`): lòng ống
  thẳng 6,6 × 8,6 hở miệng, piston gọt về tiết diện ty 6 × 8, rãnh đai ốc hở mặt trên + ghế lục giác xoay 30° (đai ốc gọn
  trong ty, khe ống 0,55), lỗ Ø3,6 tròn. 20/21 test + 1 expected failure, động học 24 tư thế sạch, kiểm nhanh không FAIL.
  **In lại** `print/plates-reprint-cylinders-2026-10-26/`: R10 2 vỏ 51 ph 16,7 g, R11 2 ty 18 ph 6,5 g (thay R7/R8 cũ).
  ASSEMBLY bước 12–15, 18, 23–26 viết lại theo piston (ảnh TODO). Ảnh duyệt `freecad/images/review/12-cylinder-assemblable.png`.
- 2026-10-25 tối: **xi-lanh thanh răng → PISTON** (Tuan thử: `Rack_Elbow` lệch khi lên xuống). Giữ motor 030 + hộp số, chốt A–D,
  Boom, cẳng tay. Bỏ Worm, bánh vít, thanh răng, vòng đệm trục. Mới: `Housing_*` (ống + buồng bánh răng + tấm gá), `Piston_rod_*`,
  `Gear_z28_*`, `Gear_z12_*`, `Pin_gearbox_*` (mới), ty ren M3 + 4 đai ốc. 1,17 mm/vòng trục ra, ren M3 tự hãm.
  Script `freecad/scripts/history/2026-10-25_piston_cylinder_030.py`; kiểm: động học 30/30, 18/18 test, prepare-print WARN.
  In lại: `print/plates-reprint-piston-2026-10-25/` (R7 vỏ 50 ph, R8 ty 19 ph, R9 bánh răng + chốt 48 ph; ~31 g).
  R7: vùng "cần support" z 9–11 mm là **trần lòng ống piston** – KHÔNG tô support ở đó; chỉ tô dưới tai chốt.
  Ảnh duyệt: `freecad/images/review-piston/`. TODO: ASSEMBLY.md bước 11b–15 + ảnh lắp còn theo xi-lanh cũ.
- 2026-10-25: **chốt khớp** S/A–E/jaw2 thân Ø5,0 → **Ø4,8** (khe 0,3 mm/bên với lỗ Ø5,4), đặc 100 % (bàn P8), in nằm cả
  Pin_jaw2, lỗ vít M2.5 sâu 5,5; bộ chốt thử; test `T7Pins` (`history/2026-10-25_pins_clearance_solid.py`).
- 2026-10-25: bỏ support tự vẽ (Tuan tô trong slicer); vát miệng lỗ trục Worm 0,4 mm; luật mái lỗ kín bắc cầu ≤ 8 mm;
  ASSEMBLY: lắp động cơ + trục vít SAU CÙNG (bước 11b, trục vít tự hãm).
- 2026-10-24: xi-lanh dùng động cơ CyberBrick 030 + hộp số (thay N20), bộ thu XA003/XA004 có shield, khe bánh răng/trượt
  0,3 mm, khắc số khớp (commit c2d0af7).
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
- 2026-10-25 | G1 bộ chốt thử | PASS | Ø4,8 vừa (Tuan thử) → giữ chốt Ø4,8, in bàn R5/P8.
- 2026-10-25 | P8/R5 chốt | FAIL | chốt Ø5,0 không nhét vào lỗ Ø5,4 (Boom001/Turret); ruột rỗng (infill 40 %) → sửa Ø4,8 + 100 %.
- 2026-10-25 | R1/P4 Housings | FAIL | mất 1 bên thành ngoài (bật support hay không): vách ngoài rãnh thanh răng chỉ 0,2 mm
  (nới rãnh ±6,3, mặt ngoài 6,5) → slicer bỏ → đắp 0,7 mm ra ngoài (vách 0,9, né Boom001 khi duỗi hết), in R6.
- 2026-10-25 | R1 Housings | FAIL | support tự vẽ lấp rãnh thanh răng → Rack_Elbow không luồn qua → bỏ support tự vẽ, in lại R1.
- 2026-10-23 | (bàn chưa ghi rõ) | FAIL | phần treo/nhô ra in không support → lỗi; chi tiết nhỏ cần brim (Tuan báo).
  Nguyên nhân: slicer chỉ báo cụm rời hẳn, phần nhô dính liền không bị báo. Đã sửa quy trình, cắt lại 8 bàn – xem Lịch sử sửa.
  TODO Tuan: bàn/chi tiết nào hỏng + ảnh, để đối chiếu với danh sách tự phát hiện.
