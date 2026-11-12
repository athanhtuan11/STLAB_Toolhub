# Servo horn SG90 và CyberBrick – ghi chú thông số lắp

Ghi chú nghiên cứu từ 2 nguồn, để thiết kế arm servo in 3D lắp lẫn với CyberBrick. Ứng dụng: `maker/servo-horn-sg90`.

Cách đo: cắt lát STL (trimesh), fit đường thẳng/đường tròn, sai số ≤ 0,001 mm.

## 1. Print2Drive – khớp trục SG90

- Model "Servo Arm Universal Set – MG90 SG90 PG001 PG002" (MakerWorld). License Standard Digital File License: chỉ dùng cá nhân, không đăng lại.
- File ở `community/makerworld-servo-arm-sg90/`, không lên git.
- Cấu hình tác giả: Bambu Studio 02.09.01.70, A1 0,4, Bambu PETG Basic @BBL A1, lớp 0,16 mm, 3 tường, 20 %, xy_hole_compensation 0, không support.
- 5 kiểu arm: đơn 7,00 × 21,10 mm; đôi 35,2 mm; chữ thập; sao 6 tay; đĩa Ø25 mm. Cùng hub cao 4,87 mm.
- Hub OD 7,00 mm, cao 2,70 mm dưới arm.
- Lỗ trục tròn, không răng: Ø5,00 mm từ miệng tới sâu 0,49 mm, côn thẳng (0,0815 mm bán kính/mm) tới Ø4,64 mm ở sâu 2,70 mm.
- Lỗ vít Ø2,70 mm (vách 0,575 mm), loe 90° Ø2,70 → Ø5,00 mm, hốc Ø5,00 mm sâu 0,445 mm. Arm dày 2,17 mm.
- Arm đơn: rộng 7,00 mm thẳng, đầu R3,50 mm, dài 17,60 mm từ tâm; 5 lỗ Ø1,50 mm bước 2,375 mm từ 5,60 tới 15,10 mm.

## 2. CyberBrick chính hãng – dáng arm

- Nguồn: `community/cyberbrick-official`, CyberBrick Module CAD Models / 9g Servo Motor with Clutch Protection-PG002-PG001: half arm1, line arm, cross arm (.stp + .stl).
- Hub OD 7,26 mm; arm dày 1,85 mm; tổng cao 4,15 mm.
- STEP đơn giản hóa: lỗ hub tròn Ø4,30 mm sâu 2,30 mm, không răng → không dùng làm số ép (dùng số Print2Drive).
- Lỗ vít Ø2,50 mm; hốc đầu vít Ø4,90 mm sâu 1,10 mm.
- Hub R3,63 mm. Cạnh y = ±(3,08 − 0,083·x) cắt hub tại x ≈ 2,19 mm (góc gãy, không tiếp tuyến), tiếp tuyến đầu R1,90 mm tại x = 14,14 mm → dài 16,05 mm từ tâm.
- Cross:
  - +X: y = ±(3,75 − 0,1058·x), đầu R2,00 mm tại x = 16,46 mm (dài 18,46 mm).
  - −X: như half (dài 16,05 mm).
  - ±Y: rộng 3,80 mm, đầu R1,90 mm tại x = 6,45 mm (dài 8,35 mm).
  - Góc lượn nhỏ ~R0,3 mm chỗ giao.
- Lỗ Ø1,00 mm (vị trí 10,75 mm là Ø1,10 mm), bước 2,0 mm từ 4,75 tới 14,75 mm; cross +X tới 16,75 mm; tay ±Y: 4,75 mm và 6,75 mm.

## 3. So sánh

| Thông số | Print2Drive | CyberBrick chính hãng | Dùng trong servo-horn-sg90 |
|---|---|---|---|
| Hub OD (mm) | 7,00 | 7,26 | 7,00 (Print2Drive) |
| Hub cao dưới arm (mm) | 2,70 | TODO | 2,70 |
| Tổng cao (mm) | 4,87 | 4,15 | 4,87 |
| Arm dày (mm) | 2,17 | 1,85 | 2,17 |
| Lỗ trục | Ø5,00 → Ø4,64, sâu 2,70 mm, không răng | Ø4,30 sâu 2,30 mm, STEP đơn giản hóa | Theo Print2Drive |
| Lỗ vít | Ø2,70, loe Ø5,00, hốc Ø5,00 sâu 0,445 mm | Ø2,50, hốc Ø4,90 sâu 1,10 mm | Theo Print2Drive |
| Lỗ arm (mm) | Ø1,50, bước 2,375 (arm đơn) | Ø1,00, bước 2,0 | Ø1,2, bước 2,0 |
| Dáng arm | Arm đơn 7,00 thẳng, đầu R3,50 | Theo đường bao CyberBrick | Theo CyberBrick |

## 4. Kết luận dùng

- Khớp trục in: lấy Print2Drive (cùng máy A1 0,4 và nhựa Bambu PETG Basic của STLab, sản phẩm đã chạy).
- Dáng arm tương thích CyberBrick: lấy số CyberBrick để lắp lẫn.
- Lỗ arm in FDM: nên ≥ Ø1,2 mm. CyberBrick đúc Ø1,0 mm, in dễ bít; vách giữa 2 lỗ còn 0,8 mm.

## 5. TODO

- Ø ngoài và số răng trục khía SG90 (datasheet).
- Hub cao dưới arm của CyberBrick (chưa có số).
- In thử độ chặt khi ép trên trục SG90 và trên PG001.
