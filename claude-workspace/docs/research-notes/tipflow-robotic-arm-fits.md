# Robotic arm CyberBrick (tipflow) – dung sai lắp đo từ STL

> **An toàn:** pin Li-ion 2 cell 7,4 V. Không làm chập cực pin, không để dây kẹt khi vặn đế xoay.

## Nguồn và cách đo

- Model cộng đồng MakerWorld của tipflow, file gốc ở `claude-workspace/community/makerworld-tipflow-cyberbrick-robotic-arm/`. License chỉ dùng cá nhân, không đưa lên GitHub.
- Tách bằng `tools/model-study/study_3mf.py` → 33 chi tiết, 3 plate. Ảnh tổng: `tools/model-study/_out/arm/contact-sheet.png`.
- Đo lỗ/trục tròn bằng `tools/model-study/measure_holes.py`: cắt lát 0,25 mm theo trục x/y/z, fit đường tròn, sai số tròn ≤ 0,03 mm. Kết quả: `tools/model-study/_out/arm/holes.csv`, 71 feature.
- Kiểm bằng fixture tổng hợp: lỗ Ø6,10/Ø5,70 và chốt Ø3,00/Ø2,40 đo đúng ±0,03 mm.
- Giới hạn:
  - Chỉ thấy lỗ song song trục x/y/z theo hướng in của tác giả.
  - Chốt in nằm nghiêng (chi tiết 20, 22), lỗ khớp ở thanh tay 07/11 và ngón kẹp 14/16/18 chưa đo được → TODO đo theo trục tự dò.

## Linh kiện (theo PDF lắp của tác giả)

| Linh kiện | Thông số / vị trí |
|---|---|
| Pin Li-ion | 14500, 7,4 V, 800 mAh |
| Motor + hộp số | Motor 030 + hộp số chính hãng (cổng M2) |
| Servo 9g 180° | Có ly hợp, S1, S2 |
| Servo 9g 360° | Có ly hợp, kẹp; quay vít me chi tiết 02 |
| Vít ghép vỏ | M2.5×6 BHCS, ghép vỏ trên/dưới |
| Công tắc nguồn | Dây XH2.54, 100 mm |

## Bảng số đo chính (mm, đường kính)

| Giao diện | Lỗ | Trục/chốt | Khe (đường kính) | Chi tiết |
|---|---|---|---|---|
| Núm/khớp xoay | Ø5,467 | Ø5,068 | 0,40 | lỗ ở 03, 05, 23; núm 17, 19 |
| Tâm bánh răng đế xoay | Ø8,868 | Ø8,468 | 0,40 | bánh răng 12 trên trục 13 |
| Lỗ trục ra hộp số 030 | Ø5,684–5,698 | TODO | – | 01, 08 |
| Lỗ phụ hộp số | Ø2,19 | TODO | – | 04, 08 |
| Vít bắt servo 9g | Ø1,80 (vít tự ren) | – | – | 03, 05, 29; 2 lỗ ở 03 cách nhau 27,8 |
| Vít ghép đế (M2.5) | Ø2,40 | – | – | 01 và 03, cùng bộ toạ độ (±18,4; ±23,4) |
| Vành quanh lỗ khớp | ngoài Ø7,26 | – | – | 03, 05 |

- Bánh răng 24 răng (10) có lỗ dạng D (có mặt phẳng) cho trục motor. Lỗ không tròn nên tool không đo được → TODO đo tay.

## Bài học cho STLab

- Tác giả dùng khe đường kính 0,40 mm (0,20 mm mỗi bên) cho mọi khớp quay đo được (vật liệu in tác giả dùng: TODO). Khe này trùng với khe đang dùng ở dự án `cyberbrick-car`. Giữ 0,40 mm làm mặc định cho khớp quay.
- Lỗ vít tự ren: Ø1,8 mm cho vít servo 9g, Ø2,4 mm cho vít M2.5.
- Hướng in: lỗ khớp đặt song song trục Z hoặc nằm ngang theo mặt bàn. Chốt nhỏ in nằm nghiêng.

## Việc tiếp theo

- Đo tay lỗ D của bánh răng 10, lỗ khớp 07/11, ngón 14/16/18 (TODO).
- Đề xuất bản "chuẩn hơn": chờ Tuan chọn hướng cải tiến.
