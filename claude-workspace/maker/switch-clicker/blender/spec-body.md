---
task: switch-clicker-body-a
cwd: maker/switch-clicker/blender
allow:
  - "build_body.py"
  - "out/body-a*"
gate: '"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_body.py -- out && "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_body.py -- out'
timeout_min: 30
max_rounds: 2
executor: opencode
read: ["maker/switch-clicker/design"]
---

# Mục tiêu
Viết `build_body.py` (Blender 5.2 `bpy` + `bmesh`, `blender -b -P build_body.py -- out`) dựng **thân A** của móc khóa clicker
1 switch MX (dáng duyệt ở `../design/contact-sheet.png`, mô tả `../design/form-spec.md` mục "Chi tiết thân A").
STL đặt theo **hướng in: lật, tấm kẹp switch nằm sát bàn (z = 0)**. Gate `gate_body.py` do Claude viết – **KHÔNG sửa**.

# Kết quả
- `out/body-a.stl` (1 khối), `out/body-a-params.json`, `out/body-a-preview.png` (Eevee 1600×1000: 1 ảnh tư thế dùng – mặt tấm
  hướng lên, nhìn 3/4; ghép cạnh 1 ảnh hướng in) .

# Hình học (Claude chốt – KHÔNG đổi số; mọi số là biến ở đầu file để chỉnh sau khi in thử)
Hệ trục hướng in: z = 0 là MẶT TRÊN khi dùng (mặt tấm kẹp), z = 14 là đáy khi dùng.
- Khối chính 34 (X) × 30 (Y) × 14 (Z), tâm XY tại gốc. Bo 4 cạnh đứng R 4,8. Cạnh quanh mặt z = 0 (mặt cầm khi dùng): bo R 3,0
  nhưng phần sát bàn thay bằng vát 45° cao 0,8 (không bo tiếp tuyến bàn). Cạnh quanh mặt z = 14: bo R 1,0.
- `HOLE = 14.0` lỗ vuông xuyên tấm, tâm (0, 0), z 0 → 1,5 (`PLATE = 1.5`).
- Hốc switch 15,4 × 15,4 tâm (0, 0), z 1,5 → 11,8 (đáy kín dày 2,2: z 11,8 → 14). Không bo trong lỗ/hốc.
- Vòng treo: vành OD 12 / lỗ Ø 5,4, dày 4,0 (z 0 → 4,0), tâm tại (−17 − 3,5, +15 − 1,0) = (−20,5, 14,0) – nối liền thân ở góc
  (−X, +Y); bo cạnh vành R 1,0 trừ mặt z = 0 (vát 0,4).
- Khắc chìm mặt z = 14 (đáy khi dùng): chữ "STLAB" cao 4, nét ≥ 0,8, sâu 0,6, tâm (0, −6); mũi tên ▲ (cao 3) tâm (0, +6) chỉ +Y.
  Chữ đọc đúng chiều khi nhìn từ dưới lên đáy (lật gương phù hợp).
- Boolean EXACT (apply); trụ ≥ 64 cạnh; 1 khối kín. Xuất `bpy.ops.wm.stl_export` binary, scale 1.
- params.json ghi mọi số + "nguon_mx": "Cherry MX datasheet: lo 14,0 +-0,05, tam 1,5; vo duoi tam 5,0 + chan 3,3".

# Không làm
- Không sửa `gate_body.py`, `gate_switch_coupon.py`, `../design/`, file `out/` khác. Không dựng keycap. Không cài gói.

# Tiêu chí PASS
- Gate exit 0. Claude xem preview.
