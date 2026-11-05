# probe-a1s - Firmware do ESP32-A1S Audio Kit

ESP-IDF 5.5.4, target `esp32`. Chay 1 luot khi khoi dong, log UART 115200 voi tien to `[DO]`:
chip/flash/PSRAM, quet I2C tren 2 bo chan (SCL/SDA 32/33 va 23/18), nhan dien codec
(ES8388 0x10/0x11, AC101 0x1A), init ES8388 + I2S 16 kHz 16-bit, bat PA (GPIO21),
phat bip 1 kHz 1,5 s, thu micro 3 s (RMS/peak moi 0,5 s) roi phat lai, doc 6 nut 15 s,
va dong tong ket `[KQ]`. Sau do idle; bam nut bat ky de chay lai buoc bip + thu.

Am luong tran: hang `VOL_MAX` (mac dinh 30 %) trong `main/probe_a1s_main.c`.

## Build + nap
```bat
powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1
python check_probe.py
flash.bat COM5
```
Chi dung bo chan trong bang cua `../../CLAUDE.md`; AC101 chi duoc nhan dien, chua ho tro phat.
