---
task: cyberbrick-arm-skeleton
cwd: .
allow:
  - "maker/cyberbrick-arm/freecad/scripts/build_arm.py"
  - "maker/cyberbrick-arm/freecad/scripts/render_arm.py"
gate: "\"C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe\" --safe-mode -P maker/cyberbrick-arm/freecad/tests -t test_skeleton"
timeout_min: 50
max_rounds: 3
executor: opencode
---

# Mục tiêu
1. `freecad/scripts/build_arm.py`: script FreeCAD dựng **khung lắp ráp** tay máy cyberbrick-arm (khối massing + linh kiện
   STEP thật) **từ `freecad/params.json`**, ở một tư thế. Không số kích thước nào viết cứng ngoài các luật dưới đây.
2. `freecad/scripts/render_arm.py`: render ảnh duyệt.

# Đầu vào
- Thư mục dự án: `maker/cyberbrick-arm/` (mọi đường dẫn `freecad/...`, `design/...` dưới đây tính từ đó). `freecad/params.json` (Claude chốt – đọc hết `_ghi_chu`). Gate `freecad/tests/test_skeleton.py` (KHÔNG sửa) = đặc tả
  chính xác tên Label, file ra và các kiểm.
- Biến môi trường: `ARM_PARAMS` (mặc định `freecad/params.json`), `ARM_POSE` (mặc định `tu_the_mac_dinh`),
  `ARM_OUT` (mặc định `freecad/cyberbrick_arm.FCStd`; nếu file đích có sẵn → chép sang
  `freecad/backup/cyberbrick_arm.<YYYYmmdd-HHMMSS>.FCStd` trước khi ghi).
- Ra thêm `<ARM_OUT bỏ đuôi>.json`: `{"pose": ten, "angles": [vai, khuyu], "J1": [x,y,z], "J2": [...], "J3": [...], "T": [...]}`.
- Linh kiện: `community/cyberbrick-official/models/<đường dẫn trong params.linh_kien>` (đọc bằng `Part.read`).
  Thư viện hình: `tools/robotics-cad/scripts/cad_lib.py`. Mẫu cách đặt servo PG001 / hộp số 030 / bộ thu từ STEP
  (hệ toạ độ local, solid nào là thân): `maker/cyberbrick-car/freecad/scripts/build_car.py` (chỉ đọc).
- Render: `tools/robotics-cad/scripts/mpl_render.py`; mẫu `maker/line-bot/freecad/scripts/render_line_bot.py`.

# Hình học (mm; X trước, Y trái, Z lên; gốc = tâm trục đế trên mặt bàn)
Động học: J1 = (vai.J1[0], 0, vai.J1[1]); tay trên hướng góc `vai` so với +X trong mặt XZ; J2 = J1 + L·(cos, 0, sin);
cẳng tay hướng góc `vai + khuyu`, đơn vị d; J3 = J2 + cang_tay.L·d; T = J3 + ngon.L3·d.
Hệ cẳng tay: s dọc d từ J2; n = d xoay +90° trong mặt XZ = (−d.z, 0, d.x); y = trục Y.
Mọi khối in = khối bao − (hộp bao linh kiện nằm trong nó nới `khe` mỗi phía) − các lỗ kể dưới; bo tròn tùy chọn.

**Cố định (không quay):**
1. `Foot_plate`: tấm vuông bo góc `tam_day` (rộng × rộng × cao, đáy z=0), khoét hốc trụ R `hoc_r` sâu `hoc_sau` từ mặt trên.

**Quay theo đế (tư thế không đổi):**
2. `Base_drum`: ống trụ Ø `trong.d_ngoai`, thành `thanh`, z `z0`..`z1`, sàn dày `san` ở đáy; kệ pin ngang dày
   `ke_pin_day` đặt ở z `ke_pin_z`, phủ hình chữ nhật của `bo_tri.pin` (x, y) – nối liền thành trống.
   Không đè lên hộp số / bộ thu / pin / bánh răng (khoét).
3. `Pinion_24T`: trụ Ø `banh_rang_nho.d` dày `day`, tâm (tam), đáy z0 – nằm trong hốc Foot_plate (khối đại diện, chưa răng).
4. `Gearbox_shell`: hộp `bo_tri.hop_so`; trong có `CB_Motor_030` (STEP motor 030 trần, nằm dọc X, giữa hộp) – khoét chỗ motor.
5. `CB_XA004_receiver`: STEP bộ thu, xoay để cạnh 21,5 thẳng đứng, đặt giữa hộp `bo_tri.bo_thu`.
6. `CB_Battery_PC003`: chỉ THÂN pin (bỏ dây – lấy solid/khối có bao ≈ `pin_than`), nằm phẳng giữa hộp `bo_tri.pin`, cạnh 51,2 dọc X.
7. `Switch_holder`: hộp `bo_tri.gia_cong_tac` trừ trụ R(d_ngoai/2) (áp vào thành trống, không chồng), hốc chứa
   `CB_Switch_XA007` (STEP, cạnh 32 thẳng đứng) mở ra phía −X.
8. `Turntable`: đĩa Ø `trong.d_ngoai` z `mam.z0`..+`mam.day` + tháp hộp `mam.thap` (x, y, z từ mặt đĩa tới z1);
   khoét chỗ `CB_Servo9g_S1` (khoét xuyên mặt +Y của tháp cũng được).
9. `CB_Servo9g_S1`: STEP PG001 thân (bỏ dây như build_car), trục song song +Y đi qua J1, đỉnh trục đúng
   y = `tay_tren.y_trong` − 0,1; thân kéo về −X (trục cách đầu thân 6,0), dày 12 theo Z quanh J1.z.

**Quay theo vai/khuỷu:**
10. `Arm_upper_L` / `Arm_upper_R`: tấm hình sân vận động (2 nửa tròn R `r_dau` tâm J1, J2 + dải nối) dày `day`,
    L ở y [y_trong, y_trong+day], R ở y [−y_trong−day, −y_trong]; lỗ Ø `lo_d` tại J1, J2.
11. `Forearm`: đoạn sau s [`s_sau`, `s_doi`] × y `cang_tay.y` × n `n_sau`, ghép đoạn trước s [`s_doi`, L] × y × n `n_truoc`
    (1 solid). Khoét `CB_Servo9g_S2`, `CB_Servo9g_S3`, lỗ Ø(`truc_vit.d`+2·khe) dọc trục cẳng tay cho Worm xuyên vách trước.
12. `CB_Servo9g_S2`: trục +Y qua J2, đỉnh trục y = y_trong − 0,1; thân kéo về phía −s (trục cách đầu thân 6,0), dày 12 theo n.
13. `CB_Servo9g_S3`: trục dọc +d nằm trên trục cẳng tay (n=0, y=0), đỉnh trục tại s = `truc_vit.s0`; thân 22,7 dọc **n**,
    lệch về +n (trục cách đầu thân −n 6,0), dày 12 theo y.
14. `Worm`: trụ Ø `truc_vit.d` dài `dai` từ s = s0 dọc d (đồng trục S3).
15. `Head`: hộp s [L, L + `dau_kep.dai`], y và n ±`nua`; khoét Worm.
16. `Finger_L/R/D`: hộp tiết diện `tiet_dien` × `tiet_dien`, s [L + dau_kep.dai + khe, L + L3]; tâm cách trục `ban_kinh`
    theo góc `ngon.goc` (đo từ +y về phía +n).

Màu: chi tiết in xám nhạt; linh kiện CB_ tối; Worm/Pinion cam. Cuối: `doc.recompute()`, lưu, in
`ARM OK <pose> T=(x,z) <bao X×Y×Z>`.

# render_arm.py
Chạy `freecadcmd freecad/scripts/render_arm.py`: với mỗi tư thế trong params gọi build_arm.py (subprocess, `ARM_OUT` tạm,
không ghi đè FCStd thật) rồi render `design/concepts/arm-<pose>-{front,top,iso}.png` (front = nhìn hông). Thêm
`design/concepts/arm-reach.png`: 3 tư thế chồng nhau ở view front (tư thế phụ alpha 0,35), title ghi tầm với và chiều cao vai.
Cuối in `RENDER OK <n ảnh>`.


# Quyết định Claude sau ESCALATE 2026-11-02 (Claude đo STEP bằng freecadcmd) – làm đúng như dưới
Script đã có (`build_arm.py`, `render_arm.py`) – SỬA tiếp, không viết lại từ đầu. Gate lần trước: 5 FAIL + 2 ERROR.
1. **Servo PG001 STEP** – dùng `Solids[0]` (3 solid còn lại là dây). Hệ local: tai/thân dọc X (−4,9..27,6; thân 0..22,7),
   dày Y (−0,1..11,9, tâm 5,9), đáy z = 16,3; **trục ra tại (x 16,69; y 5,9), hướng −Z, đỉnh trục z = −14,52**.
   Gốc dịch: `P0 = (16.69, 5.9, -14.52)`; đặt = R·(p − P0) + điểm đích. Ma trận R (ảnh của e_x, e_y, e_z):
   - S1: e_x→+X, e_y→+Z, e_z→−Y; điểm đích (J1.x, y_trong − 0,1, J1.z).
   - S2: e_x→d, e_y→n, e_z→−Y; điểm đích J2 + (0, y_trong − 0,1, 0).
   - S3: e_x→−n, e_y→(0,−1,0), e_z→−d; điểm đích J2 + s0·d.
2. **Pin PC003 STEP** – 1 solid gồm cả dây, local Y 0..158,9; **thân = local Y 0..51,2** →
   `CB_Battery_PC003 = solid.common(box(x −20..20, y 0..51,2, z −10..12))`; rồi xoay local Y → world X, đặt giữa `bo_tri.pin`.
3. **Công tắc XA007 STEP** – không có solid (21 shell, có shell hở). Dùng **hộp bao của STEP** làm khối đại diện:
   `CB_Switch_XA007 = Part.makeBox(bao STEP)` (20,5 × 19,8 × 32), cạnh 32 thẳng đứng, đặt giữa hốc `Switch_holder`.
   Ghi chú trong code: "proxy hộp bao – STEP hãng không có solid".
4. **Motor 030 STEP** – `Solids[0].fuse(Solids[1])` (thân + trục); local dài theo Y (−8,4..43,8 = 52,2), X 12, Z 15,6.
   Xoay local Y → world X, đặt **tâm hộp bao motor trùng tâm `bo_tri.hop_so`** (54,4 ≥ 52,2 + 2·khe).
5. **Base_drum 1 solid** – kệ pin = dải |y| ≤ pin.y_max + 2 (=16,2), toàn bộ X, giao với trụ R(d_ngoai/2 − thanh + 0,5)
   → chạm thành trống ở 2 đầu X, fuse với ống trụ. Kệ ở z [ke_pin_z, ke_pin_z + ke_pin_day] – nằm trên hộp số (z1 31,5) và bộ thu.

# Không làm
- Không sửa `params.json`, `tests/`, `print/`, `design/brief.md`, file `.FCStd` có sẵn; không mở FreeCAD GUI.
- Không tự đổi số. Va chạm không tránh được với số trong params → dừng, `ESCALATE: <số nào, vì sao>`.

# Tiêu chí PASS
- Gate exit 0; `render_arm.py` chạy ra 10 ảnh.
