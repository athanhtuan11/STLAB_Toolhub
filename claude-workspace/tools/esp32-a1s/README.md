# ESP32-A1S Audio Kit V2.2 – thông số đã dò + firmware dò (dùng chung)

Bo của Tuan (trước dùng cho Cú Bông bản A1S, 2026-11-17 chuyển khỏi `maker/english-teacher`). Dự án đang dùng:
`maker/guitar-sai-thanh` (mạch thay thế đàn), `maker/drum-pad` (bộ trống STEAM).

## Chip (esptool 2026-11-05, COM5 qua CP210x)
- **ESP32-D0WD-V3 rev v3.1**, 40 MHz, flash **4 MB** (hãng 0x5e, mã 0x4016), MAC e0:8c:fe:64:20:a4 (BLE: …:a6). PSRAM 8 MB (ESP32 chỉ map 4 MB).

## Bộ chân (dò thật bằng `probe/`: **ES8388 v1**)
| Việc | GPIO |
|---|---|
| I2C codec ES8388 @0x10 | SCL 32, SDA 33 |
| I2S | MCLK 0, BCK 27, WS 25, DOUT 26, DIN 35 |
| Ampli loa (PA) | 21 |
| LED | 22 |
| Nút KEY1–6 | 36, 13, 19, 23, 18, 5 |
| Headphone detect | 39 |
| Thẻ SD (1-bit) / SD detect | CLK 14, CMD 15, D0 2 / 34 |

Bảng ứng viên gốc (pschatzmann/arduino-audio-driver, chỉ lấy số chân): ES8388 v2 = I2C 23/18, BCK 5; AC101 = WS/DOUT đảo 26/25.
Sơ đồ mạch: https://docs.ai-thinker.com/_media/esp32-audio-kit_v2.2_sch.pdf – **không còn chân ADC1 trống** (32–36, 39 đều đã dùng).

## Kết quả dò (2026-11-05/06, mạch thật)
- `[KQ] psram=8 codec=ES8388@0x10 i2c=32/33 i2s=0/27/25/26/35 pa=21 mic_rms=379/369`; bus 23/18 không có thiết bị.
- **Micro trên bo = ES8388 LIN2/RIN2** (PC phát 1 kHz: in2 đỉnh 1000 Hz SNR 23,7 dB; in1 im). LINE IN jack dùng chung đường LIN2/RIN2 với mic
  (RudeBox README) – `TODO` xác nhận ngõ LIN1 khi thử guitar.
- Loa cổng L + R kêu (lệnh BEEP); 6 nút OK. Chuỗi thanh ghi ES8388 trong `probe/main/probe_a1s_main.c` (viết theo ESP-ADF) phát + thu được.
- Kích thước bo **82 × 73 mm** (hình trong datasheet Ai-Thinker); độ dày, lỗ vít, chiều cao linh kiện: `TODO` đo.

## Firmware dò `probe/`
ESP-IDF **5.5.4**, target esp32: `probe/build.ps1`, nạp `probe/flash.bat COM5`, thu âm `probe/rec.py --port COM5 --sec 4 --in 2 --tone`.
