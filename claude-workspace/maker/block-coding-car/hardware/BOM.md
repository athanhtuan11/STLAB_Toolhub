# BOM – block-coding-car (1 xe) – Claude 2026-11-16, giai đoạn 1

Số liệu có nguồn ghi ở cột Nguồn; chưa có → `TODO`. Giá: TODO (Tuan mua).

## An toàn điện (đọc trước)
- **Không cấp pin thẳng vào chân 5V của DevKit.** LDO trên ESP32-S3-DevKitC-1 v1.1 là SGM2212-3.3, áp vào tối đa khi
  hoạt động **5,5 V** (datasheet SGMicro) và chân 5V nối thẳng vào LDO (sơ đồ Espressif v1.1, không có diode). 4 × NiMH vừa
  sạc có thể vượt 5,5 V (`TODO` đo thật bằng đồng hồ ngay sau khi sạc – Panasonic không công bố số này) → dùng **mạch buck-boost 5 V**.
- **Không cắm USB khi công tắc pin đang bật** (nguồn USB và mạch 5 V có thể dồn ngược). `TODO` đọc sơ đồ v1.1 phần VBUS/diode.
  Xe cập nhật firmware qua OTA, bé không cần cắm USB.
- Pin NiMH, hộp pin vặn vít, cầu chì tự phục hồi trên dây dương. Không Li-ion.

## Danh sách
| # | Linh kiện | SL | Ghi chú | Nguồn số liệu |
|---|---|---|---|---|
| 1 | ESP32-S3-DevKitC-1 v1.1 N16R8 (hoặc bo tương thích N16R8) | 1 | Bo 25,4 × 62,74 mm; bản clone `TODO` đo lại | parts-library `esp32-s3-devkitc-1` |
| 2 | Động cơ bước 28BYJ-48 **5 V** | 2 | 50 Ω/cuộn, hộp số 64:1 danh định (đo thực ~63,68:1 → hiệu chỉnh bước/ô), mô-men kéo vào 300 gf·cm | Kiatronics datasheet |
| 3 | Mạch ULN2003 cho 28BYJ-48 | 2 | ~35 × 31 mm, 4 lỗ Ø3,2 (tùy hãng – `TODO` đo) | TI ULN2003A; Reichelt ME016 |
| 4 | Mạch buck-boost ra 5 V, vào ~3–6 V, ≥ 1 A | 1 | **Ưu tiên Pololu S9V11F5** (2026-11-17): Vin 2–16 V (khởi động ≥ 3 V), 1,5 A khi Vin ≥ Vout, có chân EN, 7,6 × 11,4 × 3,8 mm, hiệu suất 85–95 %. Dự phòng **S13V20F5** (Vin 2,8–22 V, 1–2,5 A tùy Vin, 8,9 × 12,1 × 5,6 mm, không có EN). Không dùng S7V8F5 (> 500 mA, không chắc đủ 1 A). Module TPS63020 chỉ dùng khi có datasheet của chính module đó. `TODO` đọc đồ thị dòng ra ở Vin 4,5 V (đang boost) trước khi chốt mua | [pololu.com/product/2836](https://www.pololu.com/product/2836), [/4085](https://www.pololu.com/product/4085), [/2123](https://www.pololu.com/product/2123/specs) |
| 5 | Hộp pin 4 × AA có nắp vặn vít + 4 pin AA NiMH | 1 | 4,8 V danh định | Panasonic eneloop (1,2 V/cell) |
| 6 | Công tắc gạt nguồn (giấu dưới đáy) | 1 | Cần định mức DC ≥ 2 A. **Không dùng SS12D00** (chỉ 0,5 A). Có nguồn: C&K 7201 (gạt cần, 5 A @ 28 VDC) nhưng to; công tắc trượt nhỏ ≥ 2 A: `TODO` mã | [C&K 7000](https://www.ckswitches.de/media/1453/7000rocker.pdf) |
| 7 | Cầu chì tự phục hồi (PTC) dây dương pin | 1 | **Bourns MF-R135** (giữ 1,35 A, ngắt 2,70 A, 30 V). Dòng phía pin lớn hơn phía 5 V khi boost (≈ 5 V × I_ra / (V_pin × hiệu suất)) nên MF-R110 (giữ 1,10 A) dễ ngắt nhầm khi pin yếu. `TODO` đo dòng pin thật, nếu < 0,9 A thì MF-R110 cũng được | [Bourns MF-R](https://www.bourns.com/docs/Product-Datasheets/mfr.pdf) |
| 8 | LED WS2812B (mắt) | 2 | nối chuỗi, cấp 5 V; chân DIN cần mức cao ≥ 0,7 × VDD = 3,5 V → phải qua 74AHCT125 | [Worldsemi WS2812B v1.4](https://docid81hrs3j1.cloudfront.net/medialibrary/2018/10/WS2812B_V1.4_EN_18090714224701.pdf) |
| 9 | IC đệm 74AHCT125 (nâng mức 3,3 → 5 V cho dây dữ liệu LED) | 1 | Đã xác nhận: VIH = 2 V @ VCC 5 V (GPIO 3,3 V đủ), VOH ≥ 4,4 V (> 3,5 V của WS2812B), trễ 5–10 ns | [TI SN74AHCT125](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf) |
| 10 | Ampli I2S MAX98357A + loa 4 Ω nhỏ | 1 | cùng loại Cú Bông S3 | `maker/english-teacher/hardware/wiring-s3.yaml` |
| 11 | Tụ 1000 µF 16 V (sát VIN ampli) + tụ 470 µF 16 V (đầu ra buck-boost) | 1+1 | chống sụt áp khi stepper đổi pha | – |
| 12 | Switch bàn phím **MX** (loại lắp không PCB) cho nút **Dừng** + mũ đỏ in 3D Ø24 (gờ Ø32 dưới nóc, không rút ra được) | 1 | nối GPIO13 ↔ GND; chọn **Cherry MX Black** (60 cN ≈ 61 gf, nặng nhất trong loại đã kiểm; MX Red 45 cN) để bé khó bấm nhầm – `TODO` Tuan bấm thử | [Cherry MX2A Black](https://www.cherry.de/fileadmin/media/Industrial/Switch/MX_BLACK/Data_sheet_MX2A_Black.pdf) ·  fit-library `catpaw/mx-socket` 14,0 |
| 13 | Điện trở 100 kΩ × 2 (chia áp đo pin) | 2 | pin → GPIO1 (ADC1) | – |
| 14 | Bánh xe in 3D vành Ø45 + O-ring **NBR 40 × 3 mm** (ID × tiết diện, cỡ ISO 3601 có bán sẵn) → Ø48 | 2 | chu vi 150,8 mm ≈ 1 ô | `solidcraft/params.json` |
| 15 | (bỏ) – chân trượt vòm in liền đế thay bi đỡ | – | trẻ không nuốt được bi rời | – |
| 16 | Dây Dupont, ốc M3 | – | – | – |

## Dòng điện ước tính (tính từ datasheet, `TODO` đo thật)
- 1 cuộn 28BYJ-48 ở 5 V qua ULN2003: (5 − ~0,9 V sụt Vce(sat) @100 mA) / 50 Ω ≈ 82 mA.
- Nửa bước, tối đa 2 cuộn/motor × 2 motor ≈ 330 mA cho động cơ.
- ESP32-S3 phát Wi-Fi: đỉnh 340 mA (802.11b @ 21 dBm), 283–291 mA (g/n) – [Espressif datasheet](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf). MAX98357A tĩnh 2,4 mA; dòng khi phát vào 4 Ω: `TODO` (ADI chỉ công bố hiệu suất cho 8 Ω). LED: `TODO` đo.
- Cộng phần có nguồn: ≈ 0,67 A đỉnh ở 5 V, chưa tính loa + LED.
- → buck-boost ≥ 1 A ra là đủ dư. Firmware **nhả cuộn khi đứng yên** (giảm nóng + tiết kiệm pin).

## Tốc độ (giới hạn của 28BYJ-48)
- Tần số kéo vào không tải > 600 Hz (datasheet). Nửa bước ~4 076 bước/vòng trục ra (theo tỉ số đo 63,68:1).
- Bánh Ø48 → 1 ô ≈ 1 vòng bánh. Ở ~500 bước/s nửa bước ≈ **8 s/ô**; thử chế độ cả bước + tăng/giảm tốc để còn ~4–5 s/ô
  (`TODO` đo trên thảm thật – xe chậm là chấp nhận được với lớp 1, đổi lại đi đúng ô).
- Quay 90° tại chỗ (vết bánh 58 mm – GĐ4 CAD 2026-11-16): mỗi bánh lăn π·58/4 ≈ 45,6 mm ≈ 0,30 vòng ≈ 1231 nửa bước.

## Trọng tâm + chống lật (gate cho CAD giai đoạn 4)
- Đế 3 điểm (GĐ4, `solidcraft/params.json`): 2 bánh trục qua tâm xe (0,0), vết 58 mm + chân trượt vòm chính sau (x −48,5) liền đế; 3 chân chống lật cao 1,5 mm. Không bi rời (trẻ nuốt được). Pin: 1 hộp 4×AA nắp vít đứng sau trục (hộp phẳng 2×AA đè lên bánh).
- Pin 4 × AA (khối nặng nhất) nằm phẳng sát đáy, sau trục bánh → trọng tâm nằm giữa trục và bi: xe không chúi mũi.
- Gate CAD: trọng tâm (tính từ khối lượng từng chi tiết trong .sc + linh kiện) nằm trong tam giác đỡ, cách mỗi cạnh ≥ 15 mm;
  góc lật ≥ 30° mọi hướng (cùng gate card-coding-robot). Khối lượng pin/motor hiện `TODO` (cân hàng thật trước khi chốt).
