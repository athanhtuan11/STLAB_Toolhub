---
task: tet-goat-pip-coupon
cwd: maker/tet-goat-flexi/blender
allow:
  - "build_coupon.py"
  - "out/*"
gate: '"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_coupon.py -- out && "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_pip.py -- out expect_coupon.json'
timeout_min: 40
max_rounds: 2
executor: opencode
---

# Mục tiêu
Viết `build_coupon.py` (Blender 5.2 `bpy` + `bmesh`, chạy `blender -b -P build_coupon.py -- out`) sinh **mẫu thử khớp
in liền (print-in-place)** cho dê flexi: in 1 lần trên Bambu A1 + PETG, Tuan bẻ thử để chọn khe. Đơn vị: 1 = 1 mm.
Gate `gate_pip.py` + `expect_coupon.json` do Claude viết – **KHÔNG sửa**.

# Kết quả
- `out/coupon-desk.stl`, `out/coupon-keychain.stl` (mỗi file 1 mesh, gồm nhiều khối rời; in nằm, đáy z = 0).
- `out/coupon-params.json` (mọi số dưới đây + khe đo thực tế nếu tính), `out/coupon-preview.png` (render Eevee 1600×1000,
  nhìn 3/4 từ trên, nền sáng, thấy rõ 3 chuỗi và chữ khắc).

# Hình học (Claude chốt – KHÔNG tự đổi số)
Mỗi file = **3 chuỗi** đặt song song theo Y (khoảng trống giữa 2 chuỗi 6 mm), mỗi chuỗi **3 đốt** nối theo +X ⇒ 9 khối rời.
Ba chuỗi chỉ khác **khe hướng kính c** giữa chốt và lỗ: **0,4 / 0,5 / 0,6 mm**. Trục Z đứng, bàn in z = 0.

| Ký hiệu | Ý nghĩa | desk | keychain |
|---|---|---|---|
| W, H | rộng (Y), cao (Z) thân | 16, 8 | 10, 5 |
| S | bước giữa 2 chốt liên tiếp (= dài 1 đốt theo trục) | 20 | 12 |
| Ra | bán kính mặt đuôi lồi của đốt k, tâm chốt P_k | 8,4 | 5,2 |
| g | khe thân (mặt trước lõm đốt k+1 bán kính Ra + g, cùng tâm P_k) | 0,6 | 0,6 |
| d | Ø chốt đứng | 4,0 | 3,0 |
| T | dày lưỡi (z 0 → T) | 3,0 | 2,0 |
| zg | khe Z trên lưỡi (trần hốc ở z = T + zg) | 0,4 | 0,4 |
| Rt | nửa rộng lưỡi = bán kính đầu lưỡi tròn (tâm P_k) | 4,0 | 3,1 |
| sg | khe cạnh hốc + khe đầu lưỡi | 0,6 | 0,6 |
| φ | góc xoay cho phép mỗi khớp | ±15° | ±15° |
| chữ khắc chìm mặt trên đốt đầu mỗi chuỗi | "0.4"/"0.5"/"0.6" cao 5 sâu 0,6 | "4"/"5"/"6" cao 3 sâu 0,4 |

Dựng chuỗi (tọa độ theo trục X của chuỗi, P_k là tâm chốt của khớp giữa đốt k và k+1, P_k = (k·S, y_chuỗi)):
1. **Thân đốt k** (k = 0, 1, 2) = hộp rộng W, cao H; phía đuôi (+X) giới hạn bởi **trụ lồi** bán kính Ra tâm P_k (đỉnh đuôi
   x = k·S + Ra); phía đầu (−X) giới hạn bởi **trụ lõm** bán kính Ra + g tâm P_(k−1) (đỉnh đầu x = (k−1)·S + Ra + g).
   Đốt 0: đầu là mặt phẳng x = −S + Ra + g. Đốt 2 (cuối): đuôi là mặt phẳng x = 2·S + Ra, không hốc, không chốt.
   Dài đốt trên trục = S − g. Hai đốt kề nhau cách nhau đúng g = 0,6 ở mọi góc xoay.
2. **Lưỡi** thuộc đốt k+1: tấm z 0 → T, nửa rộng Rt, chạy từ mặt trước lõm của đốt k+1 về −X tới tâm P_k, đầu lưỡi là
   **nửa đĩa bán kính Rt tâm P_k**. Lỗ đứng Ø d + 2c tâm P_k (thành còn lại Rt − d/2 − c ≥ 1,0 desk / 0,6 keychain).
3. **Hốc** trong đốt k (trừ khỏi thân): z 0 → T + zg, mở ở đáy và ở mặt đuôi; đầu trong là nửa đĩa bán kính Rt + sg tâm
   P_k; hai thành bên **loe**: nửa rộng = Rt + sg tại P_k, tăng tuyến tính với khoảng cách t từ P_k về +X: Rt + sg + t·tan φ.
   (Kiểm: tại t = Ra nửa rộng = 4,6 + 8,4·tan15° = 6,85 < W/2 = 8 desk; 3,7 + 5,2·tan15° = 5,09 > W/2 = 5 keychain
   → keychain: thành hốc được phép thủng ra mặt bên đoạn cuối – chấp nhận, KHÔNG đổi số.)
4. **Chốt** thuộc đốt k: trụ Ø d tâm P_k, z 0 → T + zg (liền trần hốc), xuyên lỗ của lưỡi.
5. Bo cạnh trên thân 1,0 desk / 0,6 keychain (tùy chọn, bỏ nếu boolean lỗi) – KHÔNG bo cạnh đáy, không bo trong hốc/lưỡi.
6. Mỗi khối chạm bàn (z = 0), kín (manifold), không chồng lấn; khoảng cách nhỏ nhất 2 khối ≥ 0,38.
Boolean solver EXACT (apply) hoặc bmesh; trụ ≥ 64 cạnh. Gộp thành 1 object, xuất `bpy.ops.wm.stl_export` (binary,
apply modifiers, scale 1, đơn vị mm).

# Không làm
- Không sửa `gate_pip.py`, `expect_coupon.json`, thư mục `../design/`. Không cài thêm gói Python.
- Không làm con dê – chỉ mẫu thử khớp.

# Tiêu chí PASS
- Gate exit 0. Claude tự xem `coupon-preview.png` và kiểm chốt nằm trong lỗ (cắt lớp ngang).
