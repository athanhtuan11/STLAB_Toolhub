# MEC-1 – xe nâng đa hướng bánh Mecanum (CyberBrick) – thông số lắp ghép

> **An toàn:** 2 pin Li-ion. Không làm chập cực pin khi đấu công tắc và cổng sạc.

## Nguồn và cách đo

- Model cộng đồng MakerWorld, tác giả TeraE, file MEC-1.3mf (bản cập nhật 2026-07-30), profile "Main parts". File gốc ở `claude-workspace/community/makerworld-terae-mec-1/` (kèm hướng dẫn lắp PDF 22 trang, `description.txt`, `rc_main.txt`). License MakerWorld Exclusive License: chỉ dùng cá nhân, không đưa lên GitHub.
- Tách chi tiết: `tools/model-study/_out/mec-1/` (33 chi tiết, `contact-sheet.png`, `features.json`).
- Thông số tác giả công bố:
  - Nặng 490 g; dài 120 mm (không tính càng), rộng 82 mm, cao 113 mm.
  - Bánh Ø45 mm, rộng 22 mm; chiều dài cơ sở 60 mm.
  - Nâng 14 mm+; 3 cấp tốc độ 25/50/100 %.
- **Sản phẩm hoàn thiện**: tác giả đã in và chạy thật → mọi khe trong bảng là khe ĐÃ CHẠY ĐƯỢC, dùng làm số mặc định.
- Máy/nhựa tác giả (từ project_settings trong 3mf): Bambu A1 mini, đầu phun 0,4, lớp 0,2, Bambu PLA Basic, Textured PEI, `xy_hole_compensation = 0` (lỗ không bù).
- Trong fits.json vẫn để `verified: false` vì quy ước `verified` = STLab tự in thử trên A1 + PETG.

## Linh kiện (theo mô tả và PDF của tác giả)

| Linh kiện | Thông số / vị trí |
|---|---|
| Bộ điều khiển | CyberBrick Ultimate Kit; 2 receiver (1 = trái, 2 = phải) |
| Motor + hộp số | 4 motor DC + bộ bánh răng 48:1 của kit, trong vỏ hộp số TỰ IN (không dùng hộp số chính hãng) |
| Servo 360° | Kéo thanh răng nâng càng (bánh răng M1 15 răng, thanh răng dài 97,44 mm) |
| Pin Li-ion | 2 pin + 2 công tắc |
| LED hub | OUTPUT 1/2/3/4 = sau trái / sau phải / trước phải / trước trái |
| Nam châm | 4×2 mm, giữ vỏ |
| Con lăn Mecanum | Đổ silicone 20A (50 g, tỉ lệ AB 1:1) hoặc in TPU 90A |
| Vít mặc định | H2.5x6 (lục giác 1,5 → đầu tròn BHCS M2.5×6) |

## Bảng số đo chính (mm, đường kính)

| Giao diện | Lỗ | Chốt/trục | Khe | Chi tiết | Ghi chú |
|---|---|---|---|---|---|
| Lỗ trục ra hộp số | Ø5,70 | TODO | – | vỏ hộp số 10–13 | Khớp tipflow Ø5,691 → 2 tác giả độc lập cùng ~5,7 |
| Moay-ơ bánh ép vào trục ra | double-D: tròn Ø5,53, 2 mặt phẳng cách 3,80 | TODO | ép chặt | bánh 01/02 | Tác giả cảnh báo tháo dễ hỏng hộp số |
| Vít M2.5 xuyên qua | Ø2,8 (vỏ hộp số Ø2,7) | – | – | 01, 20, 21 | Lỗ bậc đầu vít Ø5,0 sâu 1,5–3,5 |
| Vít M2.5 tự ren | Ø2,2 | – | – | 03, 05, 06, 21 | tipflow dùng 2,4; cả hai đều chạy được → dải 2,2–2,4 dùng được |
| Chốt in nằm ngang | Ø5,0 | Ø4,7 (vát 2 mặt còn 4,07) | 0,3 | chốt 15–18 vào 21, 22, 31, 33 | In nằm để bền theo thớ, đầu mũ Ø6 |
| Khớp xích lắp bấm | Ø5,0 (lưỡi dày 3,4) | Ø4,4 dài 3,8 | 0,6 (dọc trục ~0,2/bên) | xích 22/23 | Bóp nhẹ mắt xích để lắp; cách ghép lỗ–chốt suy từ hình học (STL nhiều thân chồng nhau) |
| Vít bắt servo 9g | Ø2,0 xuyên, cách nhau 27,81 | – | – | giá servo 33 | tipflow Ø1,8 cùng khoảng cách ~27,8; cỡ vít TODO |
| Ổ nam châm 4×2 | Ø4,1 sâu 2,1–2,2 | 4,0 (danh nghĩa) | 0,1 | 05, 14 | Vẫn nhỏ keo 502; chú ý cùng cực |

## Cấu hình in của tác giả

- Bật support (tree, vẽ tay) chỉ cho 2 chi tiết khung lớn (20, 21); khung 14 chỉ support vùng quan trọng.
- Brim outer_only cho 2 tấm trang trí mỏng 07, 08.
- Xích 22/23 in infill 100 %, zig-zag.
- Giá servo 33 bridge_flow 1.5.
- Bánh: seam random.

## Bài học cho STLab

Ý tưởng, chưa làm. Số lấy từ sản phẩm đã chạy; chỉ cần lưu ý khác biệt PLA (tác giả) → PETG (STLab):

- Tự in vỏ hộp số cho motor + bộ bánh răng 48:1 của kit thay vì mua hộp số chính hãng. Hợp với hướng cầu sau 2 motor 030 của `cyberbrick-car`, cần đo trục ra thật (TODO).
- Moay-ơ double-D ép chặt: không cần vít giữ bánh. Mối ép là chỗ nhạy với đổi nhựa nhất (PETG dẻo hơn PLA) → nếu đổi sang PETG thì in 1 bánh trước khi in đủ 4.
- Chốt in nằm ngang có vát 2 mặt: dùng cho khớp chịu lực thay cho chốt in đứng.
- Vỏ trên cài bằng 4 trụ Ø7,5 (đầu Ø4,0/Ø6,5), đẩy vào rồi trượt ra sau để khóa cùng nam châm: không cần vít, mở vỏ nhanh.

## Việc tiếp theo

- Đo trục ra hộp số thật (TODO), điền cột Chốt/trục còn TODO.
- Đo cỡ vít servo 9g (TODO).
- Khi dùng PETG: in 1 bánh thử độ ép trên trục ra trước khi in đủ bộ.
