# Cú Bông bản ESP32-S3 – hướng dẫn hàn và đấu dây

Bo: **ESP32-S3 N16R8 devkit** (đã đọc chip 2026-11-12: ESP32-S3 rev v0.2, PSRAM 8 MB, flash 16 MB).
Mic **INMP441** (I2S) + ampli **MAX98357A** (I2S) + loa 52 mm. Sơ đồ chân giống bo `bread-compact-wifi` của xiaozhi.

## 1. An toàn – đọc trước khi hàn

- **INMP441 chỉ cấp 3,3 V.** Cấp 5 V có thể hỏng mic.
- **MAX98357A cấp 5 V**, không lấy từ chân 3,3 V của bo (quá tải mạch ổn áp, ESP32 chập chờn).
- **Hai dây loa (+ và −) không được nối GND.** Ngõ ra ampli là kiểu cầu, chạm GND là chập ampli.
- **Tụ hóa có cực**: chân dài (+) vào VIN, chân ngắn / vạch trắng (−) vào GND. Cắm ngược tụ có thể phồng, nổ.
- Rút USB khi hàn. Mỏ hàn khoảng 330–350 °C, hàn xong để nguội, không chạm đầu mỏ.
- Nguồn: cục sạc 5 V ≥ 2 A. Đang dùng nguồn ngoài vào chân 5V thì không cắm thêm cáp máy tính.
- Âm lượng thử ≤ 70. Loa 4 Ω 3 W (nhãn loa) – hợp MAX98357A ở 5 V; nghe rè thì hạ âm lượng.

## 2. Chuẩn bị

| Món | Số lượng |
|---|---|
| ESP32-S3 N16R8 devkit | 1 |
| Module INMP441 | 1 |
| Module MAX98357A | 1 (2 loa trái + phải → 2 con, xem mục 6) |
| Loa 52 mm | 1 |
| Tụ hóa 1000 µF 16 V | 1 |
| Dây Dupont cái–cái hoặc dây điện mềm | ~12 sợi |
| Hàng rào (pin header) | đi kèm module |

## 3. Hàn chân

1. Hàn hàng rào cho INMP441 và MAX98357A (cắm hàng rào vào breadboard để giữ thẳng, đặt module lên rồi hàn).
2. MAX98357A: hàn **cầu đấu vít 2 chân** (hoặc 2 dây) ở cổng loa.
3. Hàn tụ 1000 µF **sát chân VIN – GND của MAX98357A** (mặt dưới module hoặc ngay đầu dây). Đúng cực!
4. Mối hàn: bóng, hình nón, không dính sang chân bên cạnh.

## 4. Đấu dây

### INMP441 → ESP32-S3

| INMP441 | ESP32-S3 |
|---|---|
| VDD | **3V3** |
| GND | GND |
| L/R | **GND** (chọn kênh trái – bắt buộc nối, không để trống) |
| WS | GPIO4 |
| SCK | GPIO5 |
| SD | GPIO6 |

### MAX98357A → ESP32-S3

| MAX98357A | ESP32-S3 |
|---|---|
| VIN | **5V** (chân 5V / VIN của bo) |
| GND | GND |
| LRC | GPIO16 |
| BCLK | GPIO15 |
| DIN | GPIO7 |
| GAIN | để trống |
| SD | để trống |
| Loa + / Loa − | 2 dây loa (không nối GND) |
| Tụ 1000 µF | chân (+) vào **VIN**, chân (−) vào **GND** của MAX98357A (xem bên dưới) |

### Tụ 1000 µF (chống sụt áp khi loa kêu to)

Tụ mắc **song song** với nguồn của ampli, đặt **sát chân VIN – GND trên module MAX98357A** (không đặt ở đầu bo ESP32):

```
  Bo ESP32-S3 5V ───────────┬──────── VIN  (MAX98357A)
                            │
                          ( + )   chân dài, phía KHÔNG có vạch
                         [ 1000 µF ]
                          ( − )   chân ngắn, phía có VẠCH trắng
                            │
  Bo ESP32-S3 GND ──────────┴──────── GND  (MAX98357A)
```

- Cách hàn dễ nhất: hàn 2 chân tụ thẳng vào 2 chân hàng rào **VIN** và **GND** ở mặt dưới module (2 chân này nằm cạnh nhau
  trên phần lớn module MAX98357A – đọc chữ in trên module để chắc), rồi mới cắm dây nguồn.
- Tụ tháo bo cũ dùng được (vd. 1000 µF 50 V): đỉnh tụ phẳng, không phồng, không rỉ nước; điện áp định mức ≥ 10 V là đủ.
- **Ngược cực = tụ có thể phồng, nổ.** Kiểm lại vạch trắng nằm phía GND trước khi cắm điện.
- 2 module MAX98357A (2 loa) → mỗi module 1 tụ.

### Nút

| Chức năng | Chân |
|---|---|
| Nói (chạm = bắt đầu/kết thúc, chạm lúc cô nói = ngắt, giữ 5 s = ngủ) | nút **BOOT** trên bo (GPIO0) – không cần hàn |
| Âm lượng + | GPIO40 → nút → GND (tùy chọn) |
| Âm lượng − | GPIO39 → nút → GND (tùy chọn) |

Không dùng GPIO35, 36, 37 (PSRAM của bo N16R8 chiếm).

## 5. Bố trí

- Dây I2S (GPIO4/5/6/7/15/16) càng ngắn càng tốt (khuyến nghị ≤ 15 cm).
- **Mic xa loa nhất có thể**, không hướng lỗ mic vào loa – giúp khử vọng (bé ngắt lời cô bằng giọng) tốt hơn.
  Khi thử trên bàn: đặt mic cách loa ≥ 15 cm, loa quay hướng khác.
- Không bịt lỗ thu âm của INMP441.

## 6. Hai loa trái + phải (sau)

Mỗi MAX98357A chỉ kéo 1 loa. 2 loa = 2 module, **dùng chung** LRC (GPIO16), BCLK (GPIO15), DIN (GPIO7), 5V, GND.
Firmware phát cùng tiếng ra cả 2 – để chân SD cả 2 module trống. Mỗi module 1 tụ 1000 µF.

## 7. Kiểm tra trước khi cắm điện

1. Đồng hồ vạn năng thang thông mạch: **5V – GND** và **3V3 – GND** phải **không** kêu.
2. Kiểm từng dây theo bảng mục 4 (đầu này – đầu kia kêu).
3. Loa + / Loa − không thông với GND.
4. Cắm USB: đèn nguồn bo sáng, không có mùi khét, không linh kiện nào nóng tay. Có bất thường → rút ngay.

## 8. Thử

- Bấm BOOT → cô chào → nói "Hello" → cô trả lời.
- Lúc cô đang nói, nói chen "Cô ơi!" → cô dừng và nghe.
- Bo tự khởi động lại khi loa to (log `brownout`) → cấp 5 V riêng cho ampli qua module USB-C, GND chung.
- Cô hay tự ngắt lời khi không ai nói → tiếng vọng lọt: đưa mic xa loa hơn, báo Claude để chỉnh `STLAB_AEC_REF_DELAY_MS`.
