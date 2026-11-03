---
task: switch-clicker-v2
cwd: maker/switch-clicker/blender
allow:
  - "build_body.py"
  - "build_keycap.py"
  - "out/body-v2*"
  - "out/keycap-round*"
gate: '"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_body.py -- out && "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_keycap.py -- out && "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_body.py -- out && "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_keycap.py -- out'
timeout_min: 40
max_rounds: 2
executor: opencode
read: ["maker/switch-clicker/design"]
---

# Mục tiêu
Móc khóa clicker 1 switch MX bản 2: **viết lại** `build_body.py` (thân v2) và viết mới `build_keycap.py` (keycap tròn khắc tên).
Blender 5.2 `bpy` + `bmesh`, chạy `blender -b -P <file> -- out`. Đơn vị 1 = 1 mm. Gate `gate_body.py`, `gate_keycap.py`,
`gate_lib.py` do Claude viết – **KHÔNG sửa**. Số ô switch/keycap lấy từ mẫu cộng đồng đã in + chạy trên Bambu A1 + PETG Basic
(fit-library `catpaw/mx-socket`, `catpaw/mx-keycap-cross`) – KHÔNG đổi số. Mọi số đặt thành biến ở đầu file.

# Kết quả
- `out/body-v2.stl`, `out/body-v2-params.json`; `out/keycap-round.stl`, `out/keycap-round-params.json`;
  `out/v2-preview.png` (Eevee 1600×1000: thân + keycap lắp ở tư thế dùng, nhìn 3/4; cạnh đó keycap lật thấy ống chữ thập).

# Thân v2 – STL theo hướng in = hướng dùng (đáy z = 0)
- Khối 34 (X) × 30 (Y) × 15,31 (Z), tâm XY gốc. Bo 4 cạnh đứng R 4,8; cạnh trên (z = 15,31) bo R 2,0; cạnh đáy vát 0,6 × 45°.
- **Hốc keycap**: trụ Ø 27,0 tâm (0,0), z 11,19 → 15,31 (đáy hốc phẳng ở z 11,19). Mép hốc bo R 0,6.
- **Ô switch** (đáy hốc → xuống): lỗ vuông 14,00 × 14,00 tâm (0,0), cạnh song song trục, z 2,61 → 11,19; đáy kín (z 0 → 2,61 đặc).
- **Rãnh V cho ngàm**: quanh ô switch, tiết diện tam giác cân: mở rộng mỗi cạnh từ 0 tại z 9,25 lên +0,72 tại z 8,50 rồi về 0
  tại z 7,75 (mặt nghiêng 45°, in không support). Tức lỗ rộng 15,44 tại z 8,50.
- **Vòng treo**: vành OD 12 / lỗ Ø 5,4, dày 4,0 (z 0 → 4,0), tâm (−20,5, 14,0), nối liền góc (−X, +Y), bo vành R 1,0 (trừ mặt
  z = 0: vát 0,4).
- Khắc chìm mặt đáy z = 0: "STLAB" cao 4, nét ≥ 0,8, sâu 0,4, tâm (0, −8), đọc đúng khi nhìn từ dưới.
# Keycap tròn – STL theo hướng in: **úp**, mặt trên keycap sát bàn (z = 0), miệng váy ở trên (z = 11,3)
- Thân trụ Ø 26,0 cao 11,3. Mặt trên (z = 0): vát 1,2 × 45° quanh mép (KHÔNG bo tiếp tuyến bàn).
- Hốc váy: trụ Ø 23,0 từ z 1,4 → 11,3 (mở ở miệng). Váy dày 1,5, trần dày 1,4.
- **Ống chân**: trụ ngoài Ø 5,71 tâm, từ trần z 1,4 → z 7,0 (đáy ống lùi 4,3 so với miệng váy).
- **Lỗ chữ thập** trong ống: 2 tay bằng nhau dài 4,19, rộng 1,25, cạnh thẳng, từ z 7,0 (đáy ống, mở) vào tới z 1,4 (sâu 5,6).
  Vát miệng lỗ 0,2 × 45° ở z 7,0 (dẫn hướng).
- Khắc chìm chữ trên mặt trên (z = 0, sâu 0,6, nét ≥ 0,8): biến `TEXT = "STLAB"`, cao chữ tự co để rộng ≤ 19; đọc đúng khi
  nhìn từ trên (keycap ở tư thế dùng). Cho chạy `-- out TEN` để ra `out/keycap-round-<ten>.stl` (mặc định ra `keycap-round.stl`).
## Chung
- Boolean EXACT (apply); trụ ≥ 96 cạnh; mỗi file 1 khối kín. Xuất `bpy.ops.wm.stl_export` binary, scale 1.

# Không làm
- Không sửa gate*.py, `../design/`. Không làm clicker không switch. Không làm keycap tạo hình (để sau). Không cài gói.

# Tiêu chí PASS
- Gate exit 0. Claude xem preview + cắt lớp `--orient 0`.
