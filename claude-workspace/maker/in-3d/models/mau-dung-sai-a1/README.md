# Mẫu in thử dung sai – Bambu A1

Mục đích: tìm đường kính lỗ cần vẽ trong CAD để lắp vừa trên máy A1, rồi ghi vào `maker/in-3d/CLAUDE.md`.
Sinh lại (đổi giá trị trong `PARAMS`): `freecadcmd ../../scripts/mau_dung_sai_a1.py`.

| File | Nội dung | Kích thước |
|---|---|---|
| `tam-a-truc5-m3.stl` | 5 lỗ trục 5 mm (5,0–5,4) · 4 lỗ M3 xuyên (3,0–3,6) · 3 lỗ M3 tự tạo ren (2,5–2,9) | 120 × 46 × 6 mm |
| `tam-b-o608.stl` | 5 hốc ổ bi 608 (22,0–22,4), sâu 7 mm, lỗ Ø12 ở đáy để đẩy ổ bi ra | 151 × 40 × 9 mm |
| `mau-dung-sai-a1.step` / `.FCStd` | cả hai tấm (để sửa trong FreeCAD) | |

## In
- Đặt **mặt có chữ hướng lên**, không cần support.
- Ghi lại: vật liệu (PLA/PETG/…), profile, đầu phun, layer height – dung sai phụ thuộc các thông số này.
- Kết quả chỉ đúng cho **lỗ thẳng đứng** (trục lỗ song song trục Z). Lỗ nằm ngang thường hẹp hơn → TODO in thêm mẫu nằm ngang nếu cần.

## Thử và ghi kết quả
| Thử | Vừa đẹp | Chặt (ép tay/búa nhựa) | Lỏng |
|---|---|---|---|
| Trục/thanh thép 5 mm | TODO | TODO | TODO |
| Vít M3 đi qua | TODO | – | – |
| Vít M3 tự tạo ren (bắt chặt, không nứt) | TODO | – | – |
| Ổ bi 608 (ép, không lắc) | TODO | TODO | TODO |

Vật liệu: TODO · Đầu phun: 0,4 mm (mặc định) · Profile: 0.20mm Standard @BBL A1 (mặc định) · Ngày in: TODO

Xong thì chép giá trị "vừa đẹp" vào `maker/in-3d/CLAUDE.md` (mục Dung sai A1) để Claude dùng khi thiết kế.
