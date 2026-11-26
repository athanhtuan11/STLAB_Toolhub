# nfc-story-box – BOM + sơ đồ chân (giai đoạn 1, bản giấy)

Claude 2026-11-26, sau khi Tuan chọn **dáng A – Cú trên gốc cây** và **bo ESP32-S3** (thay A1S). **Chưa thử breadboard.**
Sơ đồ dây chi tiết: `wiring.yaml` (Toolhub vẽ hình). Thông số chưa có nguồn ghi `TODO`, không đoán.

## An toàn (đọc trước)
- Nguồn **USB 5 V ≥ 2 A**, không pin Li-ion ở v1. Đang cấp nguồn qua cổng USB-C lưng thì **không** cắm thêm cáp máy tính vào bo
  (hai nguồn 5 V đấu nhau) – nạp firmware: rút nguồn lưng trước.
- **RC522 chỉ 3,3 V.** MAX98357A + LED lấy 5 V, không lấy từ chân 3V3 của bo.
- Hai dây loa không được chạm GND (ngõ ra cầu). Tụ 1000 µF đúng cực.
- Trần âm lượng trong firmware (tai trẻ 3–6) – `TODO` đo dB ở 30 cm rồi chốt mức.
- Vỏ kín, vít giấu dưới đáy; nhiệt ampli + bo trong vỏ: `TODO` đo °C sau 1 giờ phát liên tục.

## Vì sao đổi so với brief (A1S → S3)
- S3 dư chân → thẻ SD và đầu đọc NFC mỗi cái **một bus SPI riêng** (SPI2 / SPI3), không chung MISO.
- Đọc NFC đổi **PN532 I2C → RC522 SPI**: rẻ, cùng loại với `card-coding-robot` (dùng chung thư viện + thẻ NTAG213).
- Ampli MAX98357A dùng lại **đúng chân đã chạy thật** của Cú Bông S3 (`maker/english-teacher/hardware/wiring-s3.md`).
- Bỏ được rủi ro "1 bo A1S cho 3 dự án". `TODO` Tuan xác nhận còn 1 bo S3 N16R8 rảnh (Cú Bông + block-coding-car đang dùng S3).

## BOM
| # | Linh kiện | SL | Ghi chú | Nguồn thông số |
|---|---|---|---|---|
| 1 | ESP32-S3 N16R8 devkit | 1 | loại Cú Bông đang dùng; thư viện `esp32-s3-devkitc-1` | Espressif DXF (parts-library) |
| 2 | Module MAX98357A (I2S, class D) | 1 | 5 V; GAIN + SD để trống như Cú Bông | english-teacher wiring-s3.md |
| 3 | Loa 4 Ω 3 W Ø52 × 26 mm | 1 | loại Tuan đã có | english-teacher CLAUDE.md (Tuan đo) |
| 4 | Tụ hóa 1000 µF 16 V | 1 | sát VIN–GND ampli | như Cú Bông |
| 5 | Module microSD (SPI) | 1 | `TODO` chọn loại có ổn áp 3,3 V hay trần; thẻ microSD ≤ 32 GB FAT32 (`TODO` kiểm thư viện firmware) | TODO |
| 6 | Module RC522 13,56 MHz | 1 | 3,3 V; kích thước + lỗ bắt `TODO` đo module thật; khoảng đọc qua 2–3 mm PETG `TODO` đo | [NXP MFRC522](https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf) |
| 7 | Sticker NTAG213 tròn | 10+ | ép giữa 2 lớp thẻ Ø50; `TODO` đường kính sticker (thường Ø25, đo hàng thật) | [NXP NTAG213](https://www.nxp.com/docs/en/data-sheet/NTAG213_215_216.pdf) |
| 8 | LED WS2812B | 2 | mắt cú; độ sáng ≤ 25 % | [Worldsemi](https://docid81hrs3j1.cloudfront.net/medialibrary/2018/10/WS2812B_V1.4_EN_18090714224701.pdf) (VIH 0,7·VDD) |
| 9 | IC 74AHCT125 | 1 | nâng mức 3,3 → 5 V cho dây dữ liệu LED (như drum-pad / block-coding-car) | [TI](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf) |
| 10 | Nút nhấn | 3 | Chơi/Dừng + To hơn + Nhỏ hơn; nắp in 3D ≥ Ø25; `TODO` chọn loại (switch MX như Cú Bông hay nút 12 mm) | TODO |
| 11 | Module USB-C 5 V (chỉ nguồn) | 1 | cổng ở lưng, có chống giật dây | TODO mã |
| 12 | Vít + tán cấy nóng | – | chốt ở CAD theo fit-library | fit-library |

## Sơ đồ chân ESP32-S3
| Chức năng | GPIO | Ghi chú |
|---|---|---|
| Ampli BCLK / LRC / DIN | 15 / 16 / 7 | giống Cú Bông S3 (đã chạy thật) |
| SD (SPI2) CS / MOSI / SCK / MISO | 10 / 11 / 12 / 13 | |
| RC522 (SPI3) CS(SDA) / SCK / MOSI / MISO / RST | 17 / 18 / 8 / 9 / 21 | |
| Nút Chơi/Dừng / To / Nhỏ | 4 / 5 / 6 | kéo lên nội, nhấn = GND |
| LED mắt (qua 74AHCT125) | 2 | |
| Tránh | 0, 3, 45, 46 (strapping) · 19, 20 (USB) · 35–37 (PSRAM) · 38, 48 (LED trên bo) · 43, 44 (UART log) | |

## Cách chạy (dự kiến, chốt ở giai đoạn 2)
- Thẻ → thư mục trên SD: `cards.csv` (UID → thư mục truyện). Đặt thẻ = phát; nhấc = tạm dừng; đặt lại cùng thẻ = phát tiếp chỗ cũ
  (nhớ vị trí trong NVS); thẻ mới = phát truyện mới. Mỗi truyện có bản Việt + bản Anh (nhấn giữ Chơi/Dừng để đổi tiếng – đề xuất).
- Tham khảo cộng đồng trước khi viết firmware: TonUINO / ESPuino (hộp nhạc NFC mã nguồn mở) – `TODO` kiểm license, hỗ trợ S3,
  ghim vào `community/` theo quy trình, chỉ đọc.

## Bước tiếp
1. Tuan xác nhận bo S3 rảnh + mua: RC522, module microSD, sticker NTAG213, 74AHCT125, 2 WS2812B, module USB-C, 3 nút.
2. Đo thật: RC522 (kích thước, lỗ bắt, khoảng đọc qua PETG), module SD, sticker → mới dựng CAD dáng A.
3. Song song: firmware v0.1 (SD + MP3 → MAX98357A, đọc UID RC522, nút) + kịch bản/TTS 4 truyện mẫu.
