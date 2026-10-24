# halloween-pumpkin

Bí ngô in 3D làm đạo cụ cho video #17 "Robot cầm bí ngô" (`docs/trend-content-ideas.md`), cánh tay `maker/pushrod-arm`
cầm được. Lưới tham số sinh bằng `freecad/scripts/build_pumpkin.py` (không có file FreeCAD, không lắp ráp).

## Giao diện (bước 0)
3 phương án trong `design/contact-sheet.png` – **Tuan chọn**: TODO.

| Phương án | Kích thước (mm) | In (A1, 0.20 mm, 2 vách, 10 %) | Đổi cuộn sang xanh ở |
|---|---|---|---|
| A_round8 – tròn 8 múi | Ø40 × 41 | 39 ph, 7,8 g | z 31,6 |
| B_tall10 – cao 10 múi | Ø36 × 49 | 46 ph, 8,1 g | z 39,5 |
| C_wide12 – bè 12 múi | Ø46 × 35 | 38 ph, 9,0 g | z 27,6 |

Số in: Bambu Studio CLI (`slice.py`, profile PETG Basic – đổi sang cuộn cam thật khi có danh sách cuộn).
Kiểm: không cần support, không cần brim, kiểm theo lớp sạch (`printability.py`), 2026-10-24.

## Kẹp được không
Khe 2 đệm kẹp pushrod-arm (đo trên model): 0° 7 mm · −20° 32 mm · −30° 42 mm · mở hết 63 mm → cả 3 phương án lọt.
Đệm kẹp nhỏ (~9 × 6 mm) → kẹp ngang thân (chỗ phình nhất), chưa thử thật: TODO.

## In 2 màu (tùy chọn)
A1 1 đầu phun: Bambu Studio → chuột phải thanh lớp ở z "đổi cuộn" → *Add pause / Change filament* → thay cuộn xanh.

## An toàn
Đồ trang trí, không cho trẻ nhỏ ngậm; PETG không dùng đựng thực phẩm.
