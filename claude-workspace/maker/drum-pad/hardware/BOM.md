# drum-pad – BOM + kế hoạch chân (giai đoạn 1, bản giấy 2026-11-17)

Dáng **B – Vòng quanh loa** (Tuan chọn 2026-11-17, `design/contact-sheet.png`): hộp 232 × 220 × 67 mm, 4 pad Ø70 ở 4 góc, loa Ø52 ở giữa.
Số có nguồn ghi cột Nguồn; chưa có → `TODO`. Giá: TODO (Tuan mua). **Chưa thử breadboard** – mạch pad là đề xuất, phải đo trước khi chốt.

## ⚠️ An toàn điện (đọc trước khi lắp)
- Piezo gõ mạnh có thể sinh điện áp đỉnh **hàng chục V** (`TODO` đo bằng oscilloscope) → **bắt buộc** mạch kẹp (Schottky về 3,3 V và GND)
  + điện trở nối tiếp trước ADC. Không bao giờ nối piezo thẳng vào chân IC.
- Nguồn USB 5 V của bo, không pin Li-ion ở v1. Trần âm lượng trong firmware (tai trẻ 7–11 tuổi).

## Vì sao cần ADC ngoài (kiểm 2026-11-17)
Theo sơ đồ Ai-Thinker ESP32-Audio-Kit V2.2 ([PDF](https://docs.ai-thinker.com/_media/esp32-audio-kit_v2.2_sch.pdf)) + driver
[`AudioKitEs8388v1.h`](https://github.com/pschatzmann/arduino-audio-driver/blob/main/src/AudioBoards/AudioKitEs8388v1.h):
mọi chân ADC1 đã có việc (32/33 I2C codec, 34 SD detect, 35 I2S DIN, 36 KEY1, 39 headphone detect); 37/38 không thấy ra header.
LINE IN codec chỉ 2 kênh, kênh LIN2/RIN2 dùng chung mic trên bo (RudeBox README) → không đủ 4 pad.
→ **ADS7830 (8 kênh, I2C) chung bus I2C codec GPIO32/33** (địa chỉ ADS7830 0x48 ≠ ES8388 0x10) – không mất nút nào.

## Kế hoạch chân
| Việc | GPIO | Ghi chú |
|---|---|---|
| I2C codec ES8388 + ADS7830 | SCL 32, SDA 33 | dùng chung bus, 2 địa chỉ khác nhau |
| I2S codec | MCLK 0, BCK 27, WS 25, DOUT 26, DIN 35 | như english-teacher (đã dò) |
| Ampli loa (PA) | 21 | |
| 6 nút trên bo | 36, 13, 19, 23, 18, 5 | đưa ra mặt hộp bằng nắp nút: bộ tiếng, âm lượng +/−, chế độ (`TODO` gán) |
| 4 LED WS2812B (chuỗi) | 15 qua 74AHCT125 | không dùng thẻ SD → 14/15 rảnh; `TODO` xác nhận DIP switch Audio Kit để 15 không nối SD/JTAG |
| Mẫu trống | flash (LittleFS) | không cần thẻ SD; 4 bộ × 4 tiếng WAV mono 16 bit (`TODO` tần số mẫu, dung lượng) |

## Linh kiện
| # | Linh kiện | SL | Ghi chú | Nguồn |
|---|---|---|---|---|
| 1 | ESP32-A1S Audio Kit V2.2 (ES8388) | 1 | Đã có (bo cũ của Cú Bông A1S). 82 × 73 mm; dày, lỗ vít `TODO` đo | Ai-Thinker datasheet |
| 2 | Mạch ADC **ADS7830** 8 kênh I2C (module, vd "ADS7830 STEMMA QT") | 1 | RudeBox đã chạy module này với ESP32 Audio Kit; `TODO` tốc độ lấy mẫu/kênh từ datasheet TI | [RudeBox](../../../community/jakubthedeveloper-rudebox/README.md), TODO datasheet TI |
| 3 | Đĩa piezo Ø27 hoặc Ø35 | 4 | dán dưới mặt pad, có lớp đệm; `TODO` chọn cỡ theo pad Ø70 | TODO |
| 4 | Mạch mỗi pad: 1 Schottky kép **BAT54S** (kẹp 3,3 V / GND) + Schottky nắn đỉnh + tụ giữ đỉnh + điện trở xả + điện trở nối tiếp | 4 bộ | Giá trị **đề xuất** τ ≈ 10 ms (vd 22 nF ∥ 470 kΩ), 10 kΩ nối tiếp vào ADC – `TODO` chỉnh khi thử: gõ nhanh 8 lần/s phải tách được | thiết kế STLab, kẹp theo kiểu RudeBox |
| 5 | LED WS2812B | 4 | dưới viền mỗi pad (đỏ kick, vàng snare, xanh lá hi-hat, xanh dương tom); độ sáng ≤ 25 % | [Worldsemi](https://docid81hrs3j1.cloudfront.net/medialibrary/2018/10/WS2812B_V1.4_EN_18090714224701.pdf) (VIH 0,7·VDD) |
| 6 | IC 74AHCT125 | 1 | nâng mức 3,3 → 5 V cho dây dữ liệu LED (VIH 2 V, VOH ≥ 4,4 V) | [TI](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf) |
| 7 | Loa 4 Ω 3 W Ø52 × 26 mm | 1 | loại Tuan đã có (Cú Bông) | english-teacher CLAUDE.md |
| 8 | Mặt pad mềm Ø70 (TPU in 3D hoặc EVA/cao su cắt) | 4 | `TODO` chọn vật liệu + độ dày (êm tay, truyền rung tới piezo) | TODO |
| 9 | Dây, header, ốc M3 | – | | |

## Việc tiếp
1. Tuan mua #2–#6, #8 (hoặc in TPU).
2. Thử breadboard 1 pad: đo điện áp đỉnh piezo, chỉnh tụ/điện trở giữ đỉnh, đo trễ gõ → tiếng (mục tiêu `TODO` ≤ 15 ms).
3. Song song: firmware v0.1 (ESP-IDF, phát WAV từ flash qua ES8388, đọc ADS7830) + CAD hộp B (SolidCraft).
