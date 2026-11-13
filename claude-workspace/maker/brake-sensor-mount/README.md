# brake-sensor-mount – gá treo cảm biến trên tay thắng

**Trạng thái:** v2 (2026-11-13) – viền theo số Tuan đo (E1 10, E2 24, E3 11, cung đáy R11,8 tâm D); mới có tấm gá + cách cố định; chưa có chỗ gắn cảm biến (chờ Tuan báo loại cảm biến).

## Cố định vào tay thắng (tấm "44-24")
- Tấm gá dày 3 mm, nằm **cao 5,5 mm** trên mặt tay thắng, tựa lên đai ốc có sẵn (cao 5,5 mm).
- **Chốt A:** vai Ø7 cao 5,5 mm + chốt đặc Ø3,7 mm cắm sâu 5,5 mm vào lỗ A.
- **Trụ B:** trụ rỗng Ø7/Ø4,4 cao 5,5 mm, ốc M4 xuyên qua bắt vào lỗ B.
- **Vành ôm** cung R10 (khe 0,3 mm, thành 2 mm) phủ xuống 5,5 mm theo mép cung.
- Khoảng A–B = 13 mm (Tuan đo). Các vị trí còn lại lấy từ ảnh, tỉ lệ theo C → sai số ước ±0,5 mm.

## File
- CAD đo được: `solidcraft/brake-sensor-mount.sc`; số liệu: `solidcraft/params.json` → `python build_mount.py`.
- In: `solidcraft/plates/p1-mount-v3/p1-mount-v3.3mf` (PETG, mặt trên úp xuống bàn, không support, ~18 ph, 2,6 g).
- Ảnh duyệt: `review/sheet-v3.png`. Bản vẽ mã cạnh: `review/edges-named.png` (E1–E13, A, B, C, D – trùng note trong .sc; chiều dài từng cạnh ở `solidcraft/edges.json`). Đo trong SolidCraft rồi báo theo mã.

## In 2 phần riêng để test (v3.5)
- `p1-mount-v3`: gá gắn tay thắng + ống đệm L.
- `p2-switch-base`: đế công tắc (lỗ P1 Ø5,3 + trụ L liền Ø8 cao 11,26, lỗ ren Ø3,4 cho M4) – test vừa công tắc.
- File .sc để đo: mỗi chi tiết là 1 body có tên (T_tam_ga, E6_vanh_om, A1/A2, B2, L1/L2, S, N, DE_cong_tac_in_rieng); bấm vào mặt → thấy tên.

## TODO
- Loại cảm biến + cách gắn lên gá.
- Kiểm vành ôm R10 có trùng mép thật (ảnh ước tâm cung lệch trái tâm đai ốc 3 mm).
- Trụ B Ø7 sát thân xi-lanh bên phải – nếu cấn thì giảm `boss_b.od`.
