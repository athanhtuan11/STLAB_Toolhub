---
task: switch-clicker-fit-coupon
cwd: maker/switch-clicker/blender
allow:
  - "build_switch_coupon.py"
  - "out/*"
gate: '"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_switch_coupon.py -- out && "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_switch_coupon.py -- out'
timeout_min: 30
max_rounds: 2
executor: opencode
---

# Mục tiêu
Viết `build_switch_coupon.py` (Blender 5.2 `bpy` + `bmesh`, chạy `blender -b -P build_switch_coupon.py -- out`) sinh **mẫu thử
lắp switch bàn phím MX** cho móc khóa clicker STLab: in 1 lần trên Bambu A1 + PETG, Tuan cắm switch thật để chọn lỗ khít.
Đơn vị 1 = 1 mm, mọi STL đặt theo HƯỚNG IN (đáy z = 0). Gate `gate_switch_coupon.py` do Claude viết – **KHÔNG sửa**.

# Kết quả
- `out/plate-coupon.stl` (1 khối), `out/stem-coupon.stl` (3 khối rời trong 1 file), `out/switch-coupon-params.json`,
  `out/switch-coupon-preview.png` (Eevee 1600×1000, nhìn 3/4 từ trên, nền sáng, thấy chữ khắc).

# Hình học (Claude chốt – KHÔNG đổi số; nguồn: datasheet Cherry MX lỗ 14,0 ± 0,05, tấm 1,5; vỏ dưới tấm 5,0 + chân 3,3)
## plate-coupon (in úp: tấm kẹp nằm sát bàn)
- Khung hộp 66 (X) × 24 (Y) × 10,5 (Z). **Tấm** z 0 → 1,5 có 3 **lỗ vuông xuyên** cạnh **14,00 / 14,10 / 14,20**, tâm
  x = 11 / 33 / 55, y = 12, cạnh song song trục.
- Trên tấm: 3 **hốc** vuông 15,4 × 15,4 cùng tâm lỗ, z 1,5 → 10,5 (mở phía trên). Không bo trong lỗ/hốc.
- Chữ khắc chìm trên mặt trên khung (z = 10,5), dải y 19,7 → 24 (phía +Y của mỗi hốc): "14.0" / "14.1" / "14.2", cao chữ 2,8,
  sâu 0,6, căn giữa theo x của từng lỗ.
## stem-coupon (keycap thử, in ngửa: đáy sát bàn, lỗ chữ thập mở lên trên)
- 3 trụ Ø 14 × cao 6, tâm x = 0 / 20 / 40, y = 0, trụ ≥ 96 cạnh.
- Mỗi trụ có **lỗ chữ thập** từ mặt trên xuống sâu 4,0 (đáy lỗ ở z = 2,0), tâm trụ; hai tay bằng nhau, dài L, rộng t:
  trụ 1: L 4,33 / t 1,35 · trụ 2: L 4,43 / t 1,45 · trụ 3: L 4,53 / t 1,55 (cạnh thẳng, góc vuông, không bo).
- Khắc chìm số "1" / "2" / "3" trên mặt trên, tâm chữ tại (x_trụ, y = +4,6), cao 2,5, sâu 0,4 – không chạm lỗ chữ thập.
## Chung
- Boolean solver EXACT (apply). Mỗi khối kín (manifold). Xuất `bpy.ops.wm.stl_export` binary, apply modifiers, scale 1.
- Ghi params.json: mọi số trên + "nguon": "Cherry MX datasheet; dennisleexyz/keycaps stem.scad (4.23/1.25 + Tol)".

# Không làm
- Không sửa `gate_switch_coupon.py`, thư mục `../design/`. Không cài gói Python. Không dựng thân/keycap thật.

# Tiêu chí PASS
- Gate exit 0. Claude tự xem preview.
