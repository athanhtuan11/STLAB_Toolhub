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

## 2 khối in riêng (v3.6)
- `p1-mount-v3` – **gá (khối dưới)** + ống đệm L1: tấm chứa trọn công tắc (31,35 × 25,6), ổ chốt rỗng J1 Ø5,3 sâu 4,5, vấu L2 ren Ø3,4.
- `p2-switch-base` – **đế (khối trên)**: tấm 3,5 có lỗ P1 Ø5,3, lỗ L Ø4,4, chốt nối DE-J Ø5 × 4 ở mặt dưới (in úp mặt trên xuống bàn).
- Lắp: đế cắm chốt vào J1 → công tắc úp lên đế (P1 vào lỗ) → ống đệm dưới tai L → ốc **M4×25** qua tai + ống đệm + đế, vặn vào vấu L2 của gá.
- File .sc để đo: mỗi chi tiết 1 body có tên (T_tam_ga, E6_vanh_om, A1/A2, B2, J2, L1/L2, S, N, DE_cong_tac_khoi_tren); ảnh đế: `review/switch-base.png`.

## TODO
- Loại cảm biến + cách gắn lên gá.
- Kiểm vành ôm R10 có trùng mép thật (ảnh ước tâm cung lệch trái tâm đai ốc 3 mm).
- Trụ B Ø7 sát thân xi-lanh bên phải – nếu cấn thì giảm `boss_b.od`.
