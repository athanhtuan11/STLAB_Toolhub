# servo-horn-sg90 – arm servo in 3D: khớp trục SG90 + dáng CyberBrick

Arm servo 9g in 3D. Lỗ trục ép lên trục khía SG90/MG90 (theo mẫu Print2Drive đã chạy). Dáng, độ dài, bề rộng và vị trí lỗ giống arm chính hãng CyberBrick PG001/PG002 → lắp lẫn với mẫu CyberBrick. Tuan yêu cầu 2026-11-12.

## Kiểu arm

| Kiểu | Số tay | Kích thước (mm, từ tâm trục) |
|---|---|---|
| half | 1 | dài 16,05 |
| line | 2 | tổng 32,1 |
| cross | 4 | +X 18,46; −X 16,05; ±Y 8,35 |

## Khớp trục SG90 (Print2Drive)

Nguồn: Print2Drive "Servo Arm Universal Set – MG90 SG90 PG001 PG002", in A1 0,4 + Bambu PETG Basic, lớp 0,16 mm, 3 tường, 20 %.

- Hub: OD 7,26 mm (bằng bề rộng hub CyberBrick; Print2Drive 7,00 – vách quanh lỗ dày thêm 0,13 mm), cao 2,70 mm.
- Lỗ trục tròn, không vẽ răng: miệng Ø5,00 mm sâu 0,49 mm, côn tới Ø4,64 mm ở đáy. Răng trục tự ăn vào nhựa khi ép.
- Lỗ vít Ø2,70 mm, loe 90° lên Ø5,00 mm. Hốc đầu vít Ø5,00 mm sâu 0,445 mm.
- Arm dày 2,17 mm; tổng cao 4,87 mm.

## Dáng arm (CyberBrick)

Đo từ STEP chính hãng CyberBrick, fit sai số ≤ 0,001 mm (x, y tính bằng mm từ tâm trục):

- Cạnh thẳng: y = ±(3,08 − 0,083·x), tiếp tuyến đầu tròn R1,90 tại x = 14,14.
- Cross +X: y = ±(3,75 − 0,1058·x), đầu R2,00 tại x = 16,46.
- Tay ±Y: rộng 3,80, đầu R1,90 tại x = 6,45.

## Lỗ arm

- Vị trí theo CyberBrick: bước 2,0 mm từ 4,75 tới 14,75; cross +X tới 16,75; tay ±Y: 4,75 và 6,75.
- Cỡ lỗ Ø1,2 mm. CyberBrick đúc Ø1,0 mm, in Ø1,0 mm dễ bít. Vách giữa 2 lỗ còn 0,8 mm.
- Đổi cỡ: `plate.hole_d` trong `solidcraft/params.json`.

## Khác bản CyberBrick

- Hub và arm dày theo SG90: arm 2,17 mm thay vì 1,85 mm.
- Bỏ góc lượn nhỏ ~R0,3 mm ở chỗ tay cross gặp nhau.

## File

- CAD mở đo được: `solidcraft/servo-horn.sc` (3 component, cách nhau 45 mm theo Y).
- Nguồn: `solidcraft/params.json` + `solidcraft/build_horn.py`. Chạy `python build_horn.py`, ~10 s.
- STL hướng in: `solidcraft/stl/` – mặt arm úp xuống bàn, hub hướng lên, không support.
- Bàn in: `solidcraft/plates/p1-servo-horns/p1-servo-horns.3mf` – cắt lớp PASS, 14 phút, 1,5 g, Bambu PETG Basic, 0,16 Optimal, 3 tường, 20 %.
- Cấu hình in: `solidcraft/print/print.yaml`.

## Kiểm (2026-11-12)

- Đường bao so STEP CyberBrick: IoU 0,999 cả 3 kiểu.
- Lỗ côn cắt lát khớp SG90: Ø5,000 / 4,835 / 4,656 mm; loe 4,15 → 5,00 mm.

## Lắp

1. Ép thẳng arm lên trục servo, không xoay.
2. Bắt vít arm kèm servo.
3. Với PG001/PG002 CyberBrick: tác giả Print2Drive ghi vừa, STLab chưa thử → TODO in thử.

## Thông số trong kho

- `tools/model-study/fit-library/fits.json`: mục `sg90-horn/*` và `cyberbrick-horn/*`.
- TODO: Ø ngoài và số răng trục khía SG90 (datasheet).
- Nghiên cứu chi tiết: `docs/research-notes/servo-horn-sg90-cyberbrick-fits.md`.

## Lịch sử

- 2026-11-12: tạo dự án, v1.
