# sliding-wardrobe – Tủ âm tường cửa lùa 4 cánh, khung sắt + lam sóng nguyên cây

Tủ treo đồ nằm giữa 3 bức tường (trái, sau, phải). Không có vách ván: phần chịu lực là **khung sắt hộp**,
mặt trước là **4 cánh lùa** ghép từ thanh **lam sóng ngoài trời 220 × 2900 × 26 mm, dùng nguyên cây, không cắt**.
Bên trong chỉ treo đồ bằng **ống tròn Ø27** (Tuan 2026-11-09). Bản v1 (thân ván MFC) nằm ở `backup/2026-11-09-v1-than-van-mfc/`.

## Lệnh
```text
cd design
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P build_wardrobe.py -- --out renders
python draw_plans.py
```
Sửa `P["W"]` (tường – tường) sau khi đo rồi chạy lại. Script tự chọn số thanh/cánh và tính chồng mí.
Kết quả: `wardrobe.blend`, `renders/00-contact-sheet.png`, `bom.csv` (vật tư).

## Kích thước chính (W = 3000)
- Cánh: **4 thanh × 220 = 880**, cao **2900** (= thanh lam), chồng mí **173**. W từ ~2810 đến ~3400 vẫn dùng 4 thanh/cánh, chỉ đổi chồng mí.
- Lùa 1 cánh: khoang ngoài mở 707, khoang giữa mở 533.
- Đỉnh dầm đầu cửa **2985** (cánh 2900 + khe bánh xe 15 + ray trên + dầm 40). TODO: chỉnh theo bộ ray thật.
- Vùng ray phía trước sâu 120 (cánh dày 26 + khung 20 = 46/cánh × 2 ray).

| Khoang | Lọt lòng | Ống Ø27 (cao từ sàn) | Dùng cho |
| --- | --- | --- | --- |
| K1 (trái) | 733 | 2050 + 1030 | treo 2 tầng: áo sơ mi, áo ngắn, quần vắt |
| K2 | 667 | 1950 | treo dài: áo khoác, váy |
| K3 | 667 | 1950 | treo dài |
| K4 (phải) | 733 | 2050 + 1030 | treo 2 tầng |
| Hộp nóc | 4 ô, kệ ván 17 ở cao 2300 | – | chăn mền, vali |

## Khung sắt (hộp 40×40×1,4 sơn tĩnh điện, dầm đầu cửa 40×80)
- 5 khung đứng: 2 khung áp tường trái/phải + 3 khung ở chỗ chồng mí cánh, nên cột không cản lối lấy đồ.
  Mỗi khung gồm: cột giữa (sàn → 2260, bắt bát ống treo), dầm đỡ kệ, 2 cột trên + dầm đỉnh (vùng hộp nóc).
- 4 thanh ngang tường – tường (kệ trước/sau, đỉnh trước/sau) + dầm đầu cửa 40×80 bắt ray trên.
- Bắt vào tường bằng bát + nở sắt ở 2 tường bên và tường sau. Cột giữa có bản đế 100×100×4 bắt nở xuống sàn.
- Vật tư (`bom.csv`): ~35,8 m hộp 40×40, 3 m hộp 40×80, 32,6 m hộp 20×40 (khung cánh), tổng ~104 kg
  (tính theo độ dày giả định, TODO theo hàng mua).

## Ray – gợi ý tiết kiệm
Cánh lam WPC ngoài trời thường nặng. **Cân 1 thanh trước khi mua ray.** Khối lượng cánh ≈ 4 × (1 thanh) + ~8,8 kg khung 20×40.
- Cánh ≤ ~40 kg: ray tủ áo phổ thông loại 40–50 kg/cánh là đủ, rẻ nhất (vd ray âm T309 ~95.000 đ/3 m, nguồn Phú Hải;
  Garis GR67 bánh xe 156.000 đ/cánh, ray 140.000 đ/3 m – chưa công bố tải trọng, hỏi người bán).
- Cánh nặng hơn: dùng **bánh xe đỡ dưới** loại tải 80–100 kg (cửa lùa nhôm/kho), ray trên chỉ dẫn hướng. Giá: TODO.
- Ưu tiên kiểu **đỡ dưới** vì sàn chịu tải, dầm đầu cửa không bị võng. Bắt buộc có **chặn chống nhảy ray**.

## TODO
- W thực tế; số sóng, khối lượng 1 thanh lam; bộ ray (khe dưới, cao ray trên, sâu ray đôi); độ dày hộp sắt.
- Tường sau ẩm thì chừa khe ~20 sau quần áo hoặc ốp tấm chống ẩm (chưa có trong model).

## An toàn
- Khung sắt **phải bắt nở vào tường** ở cả 3 phía + sàn. Không để khung tự đứng.
- Cánh cao 2,9 m, nặng: 2 người lắp, có chặn chống nhảy ray và chặn cuối ray. Trẻ nhỏ dễ kẹt tay ở chỗ chồng mí.
- Khoan tường: dò đường điện âm trước khi khoan.
