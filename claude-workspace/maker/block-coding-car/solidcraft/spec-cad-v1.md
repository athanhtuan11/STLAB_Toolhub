---
task: block-coding-car-cad-v1
cwd: maker/block-coding-car
allow:
  - "solidcraft/build_car.py"
  - "solidcraft/render_assembly.py"
  - "solidcraft/parts/*.py"
  - "print/print.yaml"
gate: "cd solidcraft && ..\\..\\..\\tools\\model-study\\.venv\\Scripts\\python.exe tests\\test_build.py"
timeout_min: 90
max_rounds: 2
executor: coder
read: ["maker/esp32-s3-cam/solidcraft", "maker/card-coding-robot/solidcraft", "maker/sesame-quadruped/print", "maker/block-coding-car/design", "tools/print"]
---

# Spec CAD v1 – thân xe A "Xe hộp mặt cười" (block-coding-car) bằng SolidCraft (Claude, 2026-11-16)

Tuan chọn **dáng A** (`../design/brief.md` mục Quyết định; dáng gốc `../design/make_concepts.py` hàm dáng A, ảnh `../design/contact-sheet.png`).
Mẫu code SolidCraft: `maker/esp32-s3-cam/solidcraft/build_cam_d.py` (params.json → script lệnh JSON, cache sha256, chạy song song,
`component.insert_design`, `build-report.json`) – đọc `spec-build.md` + `spec-speed.md` ở đó (lệnh đã chạy được, lỗi nhân truck đã biết:
côn trùng trục + trùng bán kính lỗ → `top_radius` −0,3; trụ tiếp tuyến thành → d −0,1). CLI: `C:\Program Files\SolidCraft\solidcraft-cli.exe`
(`solidcraft-cli snapshot x.sc --view iso` chụp ảnh nhanh). Gate mẫu cùng kiểu: `maker/card-coding-robot/solidcraft/tests/test_build.py`.

## Việc
Viết `solidcraft/build_car.py` (+ `solidcraft/parts/*.py` nếu tách): đọc `params.json` (KHÔNG số cứng linh kiện; hằng hình học nhỏ như bo 1,
khe 0,3… được, đặt tên hằng có comment), dựng → **`car.sc` lắp ráp** (mỗi chi tiết 1 component/body có tên = Label, `appearance.assign`
đúng màu `colors`, `parameters.add` cho số chính – Tuan mở đo), xuất:
- `stl/<label viết thường>.stl`: mỗi chi tiết in, **đúng hướng in**, zmin = 0; `stl/colors.json` = {"<tên>.stl": "#RRGGBB"} theo `params.colors`;
- `out/asm/<label viết thường>.stl`: mỗi chi tiết in + mỗi `Ref_*`, **tọa độ lắp ráp** (gate dùng);
- `build-report.json` như mẫu (volume, bbox, closed, shells cho từng body); `check-car.png` ảnh 3/4 (render_assembly.py hoặc snapshot).
In `CAR OK`, exit ≠ 0 nếu lỗi.

Sau đó viết `print/print.yaml` (mẫu `maker/sesame-quadruped/print/print.yaml`): `stl: ../solidcraft/stl`, Bambu PETG Basic @BBL A1, Textured PEI,
`plates_dir: plates`, **mỗi bàn 1 màu** (màu tự lấy từ colors.json – `tools/print/scripts/slice.py`): tên bàn `p<số>-<việc>` kebab-case tiếng Anh,
vd `p1-body`, `p2-chassis`, `p3-small-black` (Deck, lid, holders, wheels, coupon), `p4-face`, `p5-white`, `p6-stop`. Chi tiết nhỏ (Stop_cap,
Diffuser) bật brim nếu slice.py hỗ trợ. Cắt lớp dùng `--orient 0` (STL đã đúng hướng in) nếu print.yaml có khóa tương ứng.

Hệ tọa độ: sàn z = 0, xe nhìn **+X**, trục 2 bánh trùng trục Y đi qua (0, 0, od/2). `_L` = phía +Y.

## Bố trí (Claude đã tính – theo đúng, chỗ nào không khớp được thì DỪNG báo lại, không tự đổi params)
- **Bánh**: tâm y = ±track/2 = ±29, z = 24. Vành Ø `rim_d` 45, dày 8, rãnh O-ring rộng 3,2 sâu 1,5 giữa vành, lỗ trục double-D
  `dshaft_use` (Ø5,1 / phẳng 3,1) xuyên suốt, vát miệng lỗ 0,3. Mặt ngoài có 5 nan/lõm trang trí (không bắt buộc). In nằm (trục theo Z).
- **Motor 28BYJ-48** (`Ref_Motor_L/R`): trục theo Y, mặt bích (tai) ở |y| = center_gap/2 + body_h = 21, thân lệch **lên** trên trục
  `shaft_offset` 8 → tâm thân z 32, đáy thân z 18. Ref gồm thân trụ, tai 2 bên (lỗ cách 35 theo X tại z 32), hộp đấu dây `cap_*` hướng −X
  hoặc +Z (chọn hướng không vướng), boss Ø9 cao 1,5 + trục Ø5 dài 10 ra phía bánh.
- **Chassis** (đen): sàn mặt dưới z = `ground_clearance_min` 4 (trừ chân trượt), chu vi = mặt bằng trong `Body` trừ khe 0,3. Gồm:
  2 vách đỡ motor dày `bulkhead_t` ở |y| 21…23,5 (lỗ boss Ø10, 2 lỗ M2.5 tự ren Ø2,3 trùng lỗ tai Ø4,2 để vít M2.5 xuyên tai bắt vào
  vách – ghi chú: tai Ø4,2 rộng hơn vít, đệm long đen); hốc bánh (khe ≥ 2 quanh vành theo X/Z, ≥ 1,5 theo Y); **ống pin** đứng ôm
  `Ref_Battery` (hộp 4×AA 16 × 58 × 62, tâm x −34, đáy z 5, khe `fit_gap`) mở từ đáy, cao tới ≥ 2/3 hộp; 4 cột lên đỡ `Deck` (vít M2.5
  từ trên); 4 lỗ xuyên M2.5 Ø2,8 + bậc đầu Ø5 ở đáy cho vít lên cột góc `Body`; chân trượt vòm Ø10: chính (−48,5, 0) chạm z 0, 3 chân
  chống lật (params.skid.anti_tip) đáy ở z 1,5; khe công tắc nguồn (`power_switch`, cần gạt lộ ra đáy, có gờ che 2 bên chống vướng ngón);
  lỗ luồn dây giữa tầng dưới và Deck. Mép ngoài bo ≥ 1.
- **Battery_lid** (đen): nắp ống pin từ dưới, dày 1,8, mặt dưới z ≥ 4, 1 móc/gờ phía trước + 1 vít M2.5 phía sau (bé không mở tay được).
- **Deck** (đen): tấm z 50…52,5 trên 4 cột; trên đó (gợi ý `stop_button._vi_tri`): `Ref_ESP32` nằm dọc theo Y ở x 20…46 trong **giá đỡ
  2 gờ cạnh dài + 2 lẫy** (bo không lỗ bắt; đáy PCB cao `under_clear` 17 trên mặt Deck, hở 2 bên cho dây Dupont); 2 `Ref_ULN_L/R` (35 × 32 × 15)
  ở |y| 18…53, x −22…13, 4 trụ M2.5 tự ren theo lỗ Ø3,2 (`TODO` khoảng lỗ theo hàng – đặt trụ theo hình chữ nhật cách mép 3, ghi TODO);
  `Ref_Amp` + `Ref_Buck` chỗ trống còn lại (trên hoặc dưới Deck). **Để trống |y| < 18 quanh Ref_MX.** Lỗ luồn dây.
- **Body** (màu thân): hộp bo mặt bằng 112 × 112 góc R26 (mặt bằng), z 4 → 82,5, thành 2,2, nóc phẳng 2,5, vát mép nóc 4 × 45°; in **úp
  nóc xuống bàn** (không support). Mặt trước khoét chữ U từ mép dưới lên z 74, rộng 84 (cho `Face`). Nóc: lỗ Ø25 cho mũ Dừng tại
  (stop_button.x, y); 2 trụ dưới nóc giữ `Btn_holder`. 4 cột góc trong (liền thành, từ nóc tới mép dưới – in được) có lỗ M2.5 tự ren Ø2,3 sâu 10
  từ mép dưới. Không lỗ nào khác trên Body.
- **Face** (kem): tấm mặt trước vừa khung chữ U (khe 0,3) + gờ `face_flange` 3 trùm ra sau thành Body 2 bên + trên → lắp từ trong, bị
  Chassis kẹp dưới, không rút ra ngoài được. 2 lỗ mắt Ø14 tại y ±20, z 62 có bậc giữ `Diffuser` từ trong; miệng cười khắc rãnh 1,0
  (cung) dưới mắt; vùng lưới loa (khe dọc, rộng 2, ≥ 6 khe) trước `Ref_Speaker` (Ø28, tâm z 24, mặt loa ở x ~50 hướng +X), 2 vấu giữ loa.
  In mặt ngoài úp bàn.
- **Diffuser_L/R** (trắng): đĩa Ø18 dày 1,0 nằm sau lỗ mắt Ø14 (gờ 2 mỗi bên), bị `Eye_holder` ép từ trong.
- **Eye_holder** (đen): giá trên mép trước Deck (vít M2.5) giữ 2 `Ref_LED_L/R` (mạch tròn Ø10 × 1,6 + LED 1,6) sát sau Diffuser, ép Diffuser.
- **Stop_cap** (đỏ `stop`): mũ Ø24 nhô trên nóc 6 (≥ mx_travel + 1), gờ Ø32 dày 2 nằm dưới nóc (khe 0,3 lúc nghỉ), hốc chữ thập
  `stem_cross` 4,19 ăn vào stem MX. In úp mặt trên xuống (mặt trên phẳng/bo nhẹ ≥ 1).
- **Btn_holder** (đen): tấm giữ switch MX (lỗ vuông `mx_socket` 14,0, dày `mx_plate_t` 1,5 vùng lỗ) bắt 2 vít M2.5 vào trụ dưới nóc, đặt
  sao cho stem MX ăn vào mũ khi gờ mũ cách nóc 0,3. `Ref_MX`: hộp 15,6 × 15,6 dưới tấm `mx_below_plate` 8,3 + trên tấm 6,6 (stem).
  Nhấn hết `mx_travel` 4: gờ mũ không chạm Btn_holder/Body.
- **Coupon** (đen, không nằm trên xe – đặt ngoài xe trong lắp ráp, vd x = 200): 3 lỗ double-D `dshaft_press_try`, 3 lỗ M2.5 tự ren
  (2,2 / 2,3 / 2,4), 1 lỗ vuông MX 14,0, 1 lỗ Ø25 + đĩa Ø24 thử khe mũ; khắc số cạnh mỗi lỗ.
- `Ref_Speaker` (Ø28 × 6), `Ref_Switch` (12 × 6 × 6 ở `power_switch.x/y`, trên sàn Chassis), `Ref_Buck`, `Ref_Amp`, `Ref_Battery`: hộp/trụ đúng
  cỡ params, chỉ trong `out/asm/`, không xuất `stl/`.

## Ràng buộc (gate `tests/test_build.py` kiểm – KHÔNG sửa gate)
1. Mọi body kín, 1 shell; `car.sc` có; bao xe ≤ `max_bbox`.
2. Trục bánh qua (0,0) ± 0,5; vết bánh 58 ± 0,5; mọi điểm cách trục quay ≤ `max_turn_radius` 70 (quay tại chỗ không ra khỏi ô 150).
3. Chỉ chân trượt chính chạm sàn z 0 (bánh in đáy z 1,5 + O-ring); chân chống lật đáy z 1,5; còn lại ≥ 4; bánh nằm trong hình chiếu Body ≥ 2.
4. Trọng tâm (nhựa × 1,27 × 0,45 + khối lượng Ref) **sau trục** (x < −1) và cách chân chính ≥ 10; góc lật ≥ 30°; tâm pin z ≤ 38.
5. Không va chạm > 2 mm³ giữa mọi cặp (trừ bánh–motor, mũ–MX).
6. Nút Dừng: mũ đúng vị trí, nhô ≥ 5, nhấn 4 không kẹt.
7. Face, Diffuser (đẩy +X 5 mm) và Stop_cap (đẩy +Z 5 mm) phải vướng chi tiết khác → không rút ra từ ngoài.
8. STL in zmin 0, đúng thể tích bản lắp ráp, màu `stl/colors.json` đúng `params.colors`.
9. `slice.py` mọi bàn **PASS**, không support, không STL chưa xếp bàn.
- Tự kiểm thêm (không có trong gate): vách còn lại sau mọi hốc/lỗ ≥ `wall_min` 0,9 (2 đường in); lỗ ngang dùng giọt nước/vát đỉnh.

## Không làm
- Không sửa `params.json`, `tests/`, file nào ngoài `allow`. Không vẽ support. Không commit.
- Số chưa chắc → hằng có tên + `# TODO` trong code. Không bịa số linh kiện; thiếu số → DỪNG báo phiên chính.
- Không chép dáng/chi tiết xe đồ chơi thương mại.

## Gate
`cd solidcraft && ..\..\..\tools\model-study\.venv\Scripts\python.exe tests\test_build.py` (chạy được nhanh không cắt lớp: thêm `--no-slice`
khi lặp; lần cuối PHẢI chạy đủ). Việc nặng: bọc bằng `python tools/print/scripts/memjob.py 3 -- <lệnh>` (máy từng đứng vì cắt lớp – memory "Giới hạn RAM").

Báo kèm (≤ 25 dòng): thời gian build; vết bánh, bán kính quay, trọng tâm, góc lật; gam + phút in từng bàn; đường dẫn `car.sc`, `check-car.png`;
các TODO cần đo hàng thật; chỗ nào phải chọn khác gợi ý.

## Sửa 2026-11-16 (sau báo cáo coder – Claude chọn phương án A)
- **Chân trượt tách riêng**: `Skid_Main` (−48,5, 0, đáy z 0) + `Skid_Tip_L/R/F` (params.skid.anti_tip, đáy z 1,5), màu `chassis`.
  Vòm Ø10 + chốt định vị + **vít M2.5 từ TRONG sàn xuống** (lỗ xuyên Ø2,8 + bậc đầu Ø5 phía trên sàn Chassis, lỗ tự ren Ø2,3 trong chân) –
  đầu vít nằm trong xe, bé không tháo được. Chassis giờ toàn bộ ≥ z 4, in đúng hướng lắp (mặt dưới sàn úp bàn), không support.
  Chân in vòm lên trên hoặc mặt phẳng xuống bàn – chọn cách không support.
- **Face phẳng**: `face_notch_w` 56 (nằm trong phần thành phẳng |y| ≤ 30 của R26), mắt `eye.y` ±18. Gờ Face chỉ trùm phần thành phẳng.
- Đồng ý cách xử lý 4 điểm coder nêu: lid có hốc 0,8 cho đáy pin (ống pin từ z 5,8); `Ref_MX` phần qua tấm 13,9; Stop_cap in xuôi gờ xuống
  bàn; Face dày 6 (mặt trong x 50), Diffuser nằm hốc 1,3.
- Gate đã cập nhật (SKIDS trong PRINT/COLOR_OF, test_04/05 lấy chân từ `Skid_*`). print.yaml: chân trượt vào bàn nhỏ màu đen.
