---
task: cyberbrick-arm-form-B
cwd: maker/cyberbrick-arm
allow:
  - "freecad/scripts/build_arm.py"
gate: "\"C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe\" --safe-mode -P freecad/tests -t test_form && \"C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe\" --safe-mode -P freecad/tests -t test_skeleton"
timeout_min: 50
max_rounds: 3
executor: opencode
---

# Mục tiêu
Tạo dáng **phương án B "công nghiệp vát"** (Tuan chọn 2026-11-02) cho các khối in trong `freecad/scripts/build_arm.py`
(khung đã PASS `test_skeleton` 10/10 – giữ nguyên khớp, tầm với, vị trí linh kiện). Mọi số đọc từ `params.json` khối `dang`
(Claude chốt). Mô tả thiết kế: `design/form-spec.md` (cột B) – chỉ để hiểu ý; số trong params là chuẩn.

# Đầu vào (chỉ đọc)
`freecad/params.json`, `freecad/tests/test_form.py` + `test_skeleton.py` (KHÔNG sửa), `design/form-spec.md`.
Font logo: `params.dang.logo.font` tính từ thư mục `claude-workspace/` (= `../../` so với cwd) – Be Vietnam Pro Bold (OFL).

# Việc (tất cả bằng tham số; sửa script hiện có, không viết lại)
1. **Vát cạnh** (`Part.Shape.makeChamfer`) các khối in Base_drum, Turntable (đĩa + tháp), Switch_holder: `vat_canh`;
   Forearm: `vat_cang_tay_canh`; Head: `vat_dau_kep`. **Mọi cạnh nằm trên mặt tiếp bàn in (đáy) dùng `vat_day`**.
   Foot_plate: vát mép đáy `vat_day`. Chamfer lỗi trên cạnh nào → bỏ qua cạnh đó (try/except từng nhóm), không để mất solid.
2. **Arm_upper_L/R**: thay "sân vận động" bằng hai đầu **bát giác**: bao lồi của 2 hình vuông cạnh 2·r_dau quanh J1, J2
   (trong mặt XZ, cạnh vuông song song/vuông góc trục tay), mỗi góc vuông vát `tay_tren_bat_giac_vat`. Giữ lỗ Ø lo_d.
3. **Forearm**: cắt vát góc trên-trước (cạnh song song Y tại s = L, n = n_truoc[1]) bằng mặt phẳng, chân vát `vat_cang_tay`
   trên cả hai mặt s và n. Khắc logo `chu` lên **cả hai mặt ±Y**: ShapeString (Part / Draft `make_shapestring`), chữ cao
   `cao` theo n, căn giữa tại (s, n) của logo, kéo dài `dai` theo s (scale X cho vừa), sâu `sau` vào vỏ; chữ đọc xuôi
   khi nhìn từ phía mặt đó.
4. **Base_drum**: `khe_tan_nhiet.so` khe đứng rộng `rong`, z trong `z`, xuyên hết thành trống, tâm khe ở góc
   `goc_tam + (i − (so−1)/2)·buoc_goc` (độ, đo từ +X trong mặt XY).
5. Tất cả vẫn 1 solid hợp lệ; không phình hộp bao (test_skeleton test_07 không chồng phải vẫn PASS).

# Không làm
- Không sửa params.json, tests/, design/, print/, .FCStd có sẵn; không mở GUI.
- Không tự đổi số; mâu thuẫn → `ESCALATE: <số nào, vì sao>`.

# Tiêu chí PASS
Gate exit 0 (test_form 7 test + test_skeleton 10 test). Ghi chú cuối file script: dòng `# FORM B OK`.
