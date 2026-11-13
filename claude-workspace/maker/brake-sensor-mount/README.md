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

## 1 khối (v3.7)
- `p1-mount-v3` – gá + đế **gộp 1 khối**: tấm phẳng dày 7 mm (z 5,5 → 12,5), in úp mặt trên xuống bàn, không support; kèm ống đệm L1 cao 4,85.
- Lỗ B Ø4,4 xuyên hết từ đáy trụ B2 lên mặt trên, hốc đầu ốc Ø8 sâu 4,2 (đầu ốc nằm dưới công tắc).
- Lỗ L Ø3,4 xuyên cả khối (ốc M4 tự ren, ăn ren khoảng 10 mm).
- Lắp: ốc M4 qua B (bắt trước khi úp công tắc) → công tắc úp lên (P1 vào lỗ) → ống đệm L1 dưới tai L → ốc M4 qua tai + ống đệm vào lỗ L.
- Hình: tất cả trong `review/` (ảnh đầu vào của Tuan ở `review/input/`, bản cũ ở `review/archive/`).

## TODO
- Loại cảm biến + cách gắn lên gá.
- Kiểm vành ôm R10 có trùng mép thật (ảnh ước tâm cung lệch trái tâm đai ốc 3 mm).
- Trụ B Ø7 sát thân xi-lanh bên phải – nếu cấn thì giảm `boss_b.od`.
