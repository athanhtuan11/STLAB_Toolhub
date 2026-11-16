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
| 4 | Mạch buck-boost ra 5 V, vào ~3–6 V, ≥ 1 A | 1 | Gợi ý dòng Pololu S9V11F5 / tương đương – `TODO` chọn mã theo hàng có + datasheet | TODO |
| 5 | Hộp pin 4 × AA có nắp vặn vít + 4 pin AA NiMH | 1 | 4,8 V danh định | Panasonic eneloop (1,2 V/cell) |
| 6 | Công tắc gạt nguồn (giấu dưới đáy) | 1 | `TODO` mã | – |
| 7 | Cầu chì tự phục hồi (PTC) dây dương pin | 1 | `TODO` dòng giữ ~1 A theo dòng đo thật | – |
| 8 | LED WS2812B (mắt) | 2 | nối chuỗi, cấp 5 V | TODO datasheet WS2812B |
| 9 | IC đệm 74AHCT125 (nâng mức 3,3 → 5 V cho dây dữ liệu LED) | 1 | Dữ liệu WS2812 ở 5 V cần mức cao ~0,7·VDD > 3,3 V – `TODO` xác nhận datasheet | TODO |
| 10 | Ampli I2S MAX98357A + loa 4 Ω nhỏ | 1 | cùng loại Cú Bông S3 | `maker/english-teacher/hardware/wiring-s3.yaml` |
| 11 | Tụ 1000 µF 16 V (sát VIN ampli) + tụ 470 µF 16 V (đầu ra buck-boost) | 1+1 | chống sụt áp khi stepper đổi pha | – |
| 12 | Nút nhấn **Dừng** đỏ, mũ Ø28 trên nóc | 1 | nối GPIO13 ↔ GND | – |
| 13 | Điện trở 100 kΩ × 2 (chia áp đo pin) | 2 | pin → GPIO1 (ADC1) | – |
| 14 | Bánh xe in 3D Ø48 + vòng cao su (O-ring) | 2 | chu vi 150,8 mm ≈ 1 ô | card-coding-robot params.json |
| 15 | Bi đỡ Ø10 (bi thép/bi nhựa trong ổ in) | 1 | phía sau | – |
| 16 | Dây Dupont, ốc M3 | – | – | – |

## Dòng điện ước tính (tính từ datasheet, `TODO` đo thật)
- 1 cuộn 28BYJ-48 ở 5 V qua ULN2003: (5 − ~0,9 V sụt Vce(sat) @100 mA) / 50 Ω ≈ 82 mA.
- Nửa bước, tối đa 2 cuộn/motor × 2 motor ≈ 330 mA cho động cơ. ESP32-S3 Wi-Fi + loa + LED: `TODO` đo.
- → buck-boost ≥ 1 A ra là đủ dư. Firmware **nhả cuộn khi đứng yên** (giảm nóng + tiết kiệm pin).

## Tốc độ (giới hạn của 28BYJ-48)
- Tần số kéo vào không tải > 600 Hz (datasheet). Nửa bước ~4 076 bước/vòng trục ra (theo tỉ số đo 63,68:1).
- Bánh Ø48 → 1 ô ≈ 1 vòng bánh. Ở ~500 bước/s nửa bước ≈ **8 s/ô**; thử chế độ cả bước + tăng/giảm tốc để còn ~4–5 s/ô
  (`TODO` đo trên thảm thật – xe chậm là chấp nhận được với lớp 1, đổi lại đi đúng ô).
- Quay 90° tại chỗ (khoảng cách 2 bánh 80 mm): mỗi bánh lăn π·80/4 ≈ 62,8 mm ≈ 0,42 vòng.

## Trọng tâm + chống lật (gate cho CAD giai đoạn 4)
- Đế 3 điểm: 2 bánh (trục x = 20, cách nhau 80 mm) + 1 bi đỡ sau (x ≈ −57) – theo `design/concepts/dims.json` (ước lượng).
- Pin 4 × AA (khối nặng nhất) nằm phẳng sát đáy, sau trục bánh → trọng tâm nằm giữa trục và bi: xe không chúi mũi.
- Gate CAD: trọng tâm (tính từ khối lượng từng chi tiết trong .sc + linh kiện) nằm trong tam giác đỡ, cách mỗi cạnh ≥ 15 mm;
  góc lật ≥ 30° mọi hướng (cùng gate card-coding-robot). Khối lượng pin/motor hiện `TODO` (cân hàng thật trước khi chốt).
