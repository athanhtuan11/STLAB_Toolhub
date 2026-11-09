# Spec CAD v1: Cú con (card-coding-robot) bằng SolidCraft (Claude, 2026-11-09)

Tuan chọn concept **C – Cú con** (`../design/brief.md`, ảnh `../design/contact-sheet.png`, dáng gốc
`../design/make_concepts.py` hàm `concept_c`). Mẫu code SolidCraft: `../../esp32-s3-cam/solidcraft/build_cam_d.py`
(params.json → script lệnh JSON, cache sha256, chạy song song, `component.insert_design`, `build-report.json`). Đọc
`spec-build.md` + `spec-speed.md` ở đó để biết lệnh đã chạy được và lỗi nhân truck đã biết.
CLI: `C:\Program Files\SolidCraft\solidcraft-cli.exe`.

## Việc
Viết `build_owl.py` (thư mục này): đọc `params.json` (KHÔNG số cứng linh kiện; hằng hình học nhỏ như bo, khe 0,2… được,
đặt tên hằng), dựng → `owl.sc` lắp ráp (mỗi chi tiết 1 component), xuất:
- `stl/<label viết thường>.stl`: mỗi chi tiết in, **đúng hướng in**, zmin = 0;
- `out/asm/<label viết thường>.stl`: mỗi chi tiết in + mỗi `Ref_*`, **tọa độ lắp ráp** (gate dùng);
- `build-report.json` như mẫu (volume, bbox, closed, shells cho từng body).

In `OWL OK`, exit ≠ 0 nếu lỗi. Sau đó viết `../print/print.yaml`:
- mẫu: `../../sesame-quadruped/print/print.yaml`;
- `stl: ../solidcraft/stl`, Bambu PETG Basic @BBL A1, Textured PEI, `plates_dir: plates`;
- ghép bàn theo **màu**, mỗi bàn 1 màu (xanh lá / trắng / đen / vàng), cộng bàn `p-coupon`.

Hệ tọa độ: mặt sàn z = 0, robot nhìn hướng **+X**, tâm hình chiếu thân tại (0,0).

## Chi tiết (Label đúng tên – gate tìm theo tên)
| Label | Màu | Việc |
|---|---|---|
| `Chassis` | đen | Đế phẳng: 2 gá motor (tai 28BYJ-48, vít M3 tự ren). 2 khoang pin 2×AA (`battery_2aa`) nằm phẳng **trước và sau** cụm motor (motor ở giữa trên trục), mở từ **dưới** bằng 1 nắp vít chung hoặc 2 nắp. 2 chân trượt vòm trước/sau liền đế. Trụ/rãnh giữ ESP32, 2 ULN2003, MAX98357. Lỗ USB ESP32 ra lưng (−X). |
| `Battery_lid` | đen | Nắp khoang pin (1 nắp chung trùm cả 2 khoang), bắt 1–2 vít M3 tự ren (bé không mở tay được). |
| `Shell` | xanh lá | Vành thân trứng (siêu elip theo `shell`), phần in được KHÔNG support: cắt dưới/trên tại chỗ mặt dốc ~45°. Có lỗ mắt, lỗ mỏ, cửa bụng, 2 cửa cánh, 2 ô bánh. Bắt xuống `Chassis` bằng vít từ dưới (không lộ trên thân). |
| `Top` | xanh lá | Nắp đỉnh phẳng/hơi cong có **khe quẹt thẻ**: rãnh dẫn thẻ 60 mm, đáy rãnh mỏng ≤ 2 mm ngay trên RC522. 2 tai cú nhô lên, liền nắp, in không support. |
| `Belly` | trắng | Mảng bụng có khe loa hình chữ V (3 hàng); loa Ø36 gắn sau bụng. |
| `Eye_L`, `Eye_R` | trắng | Vòng mắt, lỗ giữa cho tấm khuếch tán. `Pupil_L/R` màu đen; `Diffuser_L/R` màu trắng, mỏng 0,8 mm, trước LED WS2812. |
| `Beak` | vàng | Mỏ tam giác chỉ hướng +X. |
| `Wing_Run` | vàng | Cánh phía **+Y** = nút Chạy, ấn xuống nút tact 12×12 bên trong; biểu tượng ▶ nổi. |
| `Wing_Clear` | trắng | Cánh phía −Y = nút Xóa; biểu tượng ✕ nổi. |
| `Wheel_L`, `Wheel_R` | đen | Bánh Ø `wheel.od` (tính cả O-ring), có rãnh O-ring và lỗ trục D ép (dùng giá trị giữa của `dshaft_press_try`). |
| `Coupon` | đen | Mẫu thử: 3 lỗ trục D (`dshaft_press_try`), 3 lỗ M3 tự ren, 3 lỗ M2 tự ren (`screw`); khắc số cạnh lỗ. |
| `Ref_Motor_L/R`, `Ref_ULN_L/R`, `Ref_ESP32`, `Ref_RC522`, `Ref_Speaker`, `Ref_Amp`, `Ref_Battery_F`, `Ref_Battery_R`, `Ref_Btn_Run/Clear`, `Ref_LED_L/R` | – | Khối tham chiếu linh kiện (hộp/trụ đơn giản đúng cỡ params), không xuất STL in. |

## Ràng buộc (gate kiểm)
1. Bao lắp ráp ≤ `max_bbox`; mọi body kín, 1 shell.
2. **Quay tại chỗ không ra khỏi ô:**
   - trục 2 bánh đi qua (0,0), sai ≤ 1 mm theo X và Y;
   - mọi điểm của mọi chi tiết cách trục quay ≤ `max_turn_radius`.
3. **Tiếp đất:**
   - chỉ `Wheel_*` và chân trượt của `Chassis` chạm z ≤ 0,3; mọi chi tiết khác có z ≥ `ground_clearance_min`;
   - bánh giấu dưới thân: nhìn từ trên, bánh nằm trong hình chiếu `Shell` (an toàn ngón tay).
4. **Góc lật ≥ `tip_angle_min_deg`:**
   - trọng tâm = khối nhựa × `petg_density_g_cm3` × `print_fill_factor`, cộng `mass_g` linh kiện đặt tại tâm `Ref_*`;
   - đa giác chống = điểm chạm sàn của bánh + chân trượt;
   - pin nằm thấp: đỉnh `Ref_Battery_F/R` ≤ `battery_z_max`.
5. **Không va chạm:** giao khối giữa 2 chi tiết bất kỳ (in + Ref) < 2 mm³. Trừ cặp `Wheel_*`/`Ref_Motor_*` (trục ép).
6. **Thẻ:** từ đỉnh `Ref_RC522` đi thẳng lên, mặt đầu tiên gặp thuộc `Top`, cách ≤ `rc522.card_gap_max`; đáy rãnh dày ≤ 2 mm.
7. **In:** `slice.py` cho mọi bàn **PASS** (không support, không CẦN SUPPORT), không còn STL chưa xếp bàn.
8. **An toàn trẻ:**
   - mắt, mỏ, bụng, cánh lắp **từ trong ra**: gờ lớn hơn lỗ thân ≥ 1,5 mm mỗi phía, nên không rút ra từ ngoài được;
   - ngoài `Coupon`, không chi tiết nào nằm ngoài thân mà lọt được trụ Ø31,7 mm;
   - mép ngoài bo ≥ 1 mm.

## Không làm
- Không sửa `params.json`, `tests/`, hay file nào ngoài `solidcraft/` và `../print/print.yaml`.
- Không vẽ support. Không commit.
- Số chưa chắc → đặt hằng có tên + ghi chú `# TODO` trong code. Không tự bịa số linh kiện mới; thiếu số → hỏi phiên chính.

## Gate (KHÔNG sửa)
Chạy `python tests/test_build.py` từ `solidcraft/`, bằng Python có trimesh: `../../../tools/model-study/.venv/Scripts/python.exe`.
PASS hết mới báo xong.

Báo kèm:
- thời gian build;
- góc lật tính được;
- gam + giờ in từng bàn;
- ảnh `check-owl.png` (render 3/4 lắp ráp; tùy chọn, như `render_assembly.py` trong mẫu).

## Sửa 2026-11-09 (sau báo cáo coder)
Hộp 4×AA 62×58 phẳng vướng đáy motor (trục z 24, motor lệch trục 8 mm lên → đáy z 18). Đổi: 2 hộp 2×AA trước + sau motor.
Gợi ý: tai motor quay sao cho thân motor lệch lên trên trục; hộp pin không nằm dưới thân motor.
Được phép: `Chassis` là **bệ đứng** rộng hơn mép cắt dưới của `Shell` (cú đứng trên bệ đen bo tròn, kiểu rounded-rect/elip)
để chứa 2 hộp pin – vẫn phải đạt bao ≤ `max_bbox`, bán kính quay ≤ `max_turn_radius`, bánh nằm trong hình chiếu `Shell`.
Ước tính Claude: hộp trước x ≈ 15 → 47, |y| ≤ 29 → góc xa trục ≈ 55 mm (+ thành 2 mm) < 70.
