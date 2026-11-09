# sliding-wardrobe – Tủ áo cửa lùa 4 cánh, lam sóng 2900

Tủ treo đồ cao 2900 × rộng ~3000 (đo lại) × sâu 800 mm. Cửa lùa 4 cánh trên 2 ray, mặt cánh và 2 vách ngoài
ốp thanh lam sóng 2900. Bên trong **chỉ treo đồ bằng ống tròn Ø27** (Tuan 2026-11-09: không ngăn kéo, không kệ).

## Lệnh
```text
cd design
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P build_wardrobe.py -- --out renders
python draw_plans.py
```
Đổi kích thước: sửa `P` (W, H, D…) và `BAYS` (cao độ ống) trong `build_wardrobe.py`, chạy lại 2 lệnh.
Kết quả: `wardrobe.blend`, `renders/00-contact-sheet.png` (ảnh + bản vẽ), `cut-list.csv` (bảng cắt ván).

## Bố trí (mm, cao độ tính từ sàn)
| Khoang | Lòng rộng | Ống treo Ø27 | Dùng cho |
| --- | --- | --- | --- |
| K1 (trái) | 718 | 2050 + 1030 | treo 2 tầng: sơ mi, áo ngắn, quần vắt (dài ≤ 850) |
| K2 | 718 | 1950 | treo dài: áo khoác, váy, đầm (≤ 1500) |
| K3 | 718 | 1950 | treo dài |
| K4 (phải) | 718 | 2050 + 1030 | treo 2 tầng |
| Hộp nóc | 4 ô × 718, cao 566 | – | chăn mền, vali |

- Ống đặt giữa lòng sâu (cách mặt trong 346), móc áo rộng ~450 nằm gọn trong lòng sâu 691.
- 4 khoang khớp với 4 cánh: lùa 1 cánh là mở trọn 1 khoang. Vách đứng nằm sau chỗ chồng mí.

## Vì sao chia module
- Ván MFC/MDF khổ chuẩn **1220 × 2440** (TODO: xác nhận với xưởng): vách 2900 không cắt được từ 1 tấm.
  → Module dưới cao 2300 + hộp nóc 600; ngang chia 2 tủ × 1488. Mọi tấm đều vừa khổ (draw_plans kiểm).
- Dựng tủ: thân dưới nằm → dựng đứng cần trần ≥ đường chéo √(2300² + 800²) ≈ 2435. Hộp nóc đặt lên sau.
- Thanh lam sóng 2900 **nguyên cây, không cắt** ốp 2 vách ngoài: che đường nối module, đẹp, nhanh.
- Cánh: khung nhôm + dán lam sóng cắt còn ~2681 (cánh 765,5 × 2746, chồng mí 40).

## TODO đo / chốt trước khi cắt
- **W thực tế** (đo 3 điểm trên/giữa/dưới, lấy số nhỏ nhất, trừ khe bù tường 10–20/bên).
- **Trần nhà**: cần ≥ ~2920 để luồn hộp nóc vào. Nếu trần đúng 2900 → giảm H.
- Bộ ray lùa đôi: chiều sâu vùng ray (đang để 100), khe trên/dưới, tải trọng cánh – theo hãng mua.
- Lam sóng: rộng thanh, độ dày, bước sóng → tính số thanh (đang ước 12 dày, sóng 30).
- Tủ sát tường 2 bên thì đặt `clad_sides=False` (không cần ốp).

## An toàn
- Tủ cao 2,9 m, hẹp so với chiều cao: **bắt ke chống lật vào tường** (mỗi module ít nhất 2 điểm).
- Cánh cao 2,75 m: dùng ray có **chặn chống nhảy ray** + giảm chấn, kiểm cánh không vênh trước khi treo.
- Ống Ø27 nhịp 717: không võng khi treo bình thường; ống inox dày ≥ 1 mm (TODO theo hàng mua), bát đỡ bắt vít vào vách 17.
