# xiaozhi-a1s – xiaozhi-esp32 v2.5.2 cho ESP32-A1S Audio Kit (STLab)

Bản ghim `community/78-xiaozhi-esp32` (v2.5.2, commit 49b4380) **chỉ đọc**. Mọi thứ của STLab nằm ở đây; `sync.ps1` chép bản ghim
sang `build-src/` (bị `.gitignore`), thêm bo `boards/stlab-a1s`, áp `patches/`, ghi `sdkconfig.defaults`.

## Build / nạp
```
powershell -NoProfile -ExecutionPolicy Bypass -File sync.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1     # ESP-IDF 6.1, log: build.log
python check_a1s.py                                               # gate
flash.bat COM5                                                    # idf.py -p COM5 flash monitor
```
`build-src` là **junction** tới `C:\xzb\a1s` (sync.ps1 tự tạo bằng `mklink /J`). Lý do: đường dẫn dự án dài làm dòng lệnh
biên dịch vượt 32767 ký tự (ninja: "CreateProcess: The parameter is incorrect"); Python/CMake giải junction/subst về đường thật nên
thư mục thật phải ngắn. `sync.ps1` xóa sạch `C:\xzb\a1s` (trừ `managed_components` được giữ lại để khỏi tải lại), xóa `sdkconfig` cũ,
áp patch trong thư mục đó và kiểm patch đã vào; `build.ps1` chạy `idf.py` từ `C:\xzb\a1s`. Gỡ junction: `rmdir build-src` (không `rm -r`).

Patch: `0001` đăng ký bo (Kconfig + CMake); `0002` Es8388AudioCodec protected (để chọn LIN2); `0003` bản ghim loại `es8388_audio_codec.cc`
khỏi ESP32 và code dùng trường I2S chỉ có ở chip đời mới (`ext_clk_freq_hz`, `left_align`, `big_endian`, `bit_order_lsb`) – patch bật lại
file và bỏ 4 trường đó (ESP32 không có; giá trị mặc định 0). LED dùng lớp riêng trong board .cc vì `gpio_led.cc` không biên dịch được trên ESP32.

Lần build đầu tải component (cần mạng). Nạp sẽ **đè firmware đang có** trên bo – hỏi trước.
An toàn: cấp nguồn USB 5 V; không cắm/rút loa, tai nghe khi đang phát âm lượng lớn.

## Chân (đo trên mạch thật 2026-11-05, bộ "ES8388 v1")
| Chức năng | GPIO |
|---|---|
| I2C SCL / SDA (ES8388 @0x10) | 32 / 33 |
| I2S MCLK / BCLK / WS / DOUT / DIN | 0 / 27 / 25 / 26 / 35 |
| PA (khuếch đại loa) | 21 |
| LED trạng thái | 22 (mức thấp = sáng, TODO kiểm) |
| KEY4 – nói | 23 |
| KEY5 – âm lượng + | 18 |
| KEY6 – âm lượng − | 5 |

GPIO0 là MCLK nên không có nút BOOT. KEY1 (36), KEY2 (13), KEY3 (19) chưa dùng.

## Micro (ES8388 LIN2/RIN2)
Đo thật: mic nối đầu vào 2 (LIN2/RIN2); đầu vào 1 im lặng. Driver `esp_codec_dev` (`device/es8388/es8388.c`, `es8388_open`) cố định
`ADCCONTROL2 = ADC_INPUT_LINPUT1_RINPUT1`. Cách làm: `patches/0002` đổi thành viên `Es8388AudioCodec` từ private sang protected;
lớp `StlabEs8388Codec::EnableInput(true)` gọi base rồi ghi thanh ghi 0x0A (ADCCONTROL2) = 0x50 (LINSEL/RINSEL = LIN2/RIN2, giá trị
`ADC_INPUT_LINPUT2_RINPUT2` trong `es_common.h` của esp_codec_dev). Gain mic giữ mặc định xiaozhi (24 dB); bíp PC gần mic từng chạm clip
(peak 31951) nên không tăng thêm. `STLAB_MIC_INPUT_LINE2 1` trong config.h chỉ là ghi chú.

## Nút
- KEY4: giữ để nói, thả ra là gửi. Lúc vừa khởi động (chưa có Wi-Fi): bấm để vào chế độ cấu hình Wi-Fi.
- KEY5 / KEY6: âm lượng +10 / −10. Giữ KEY5 lâu: vào cấu hình Wi-Fi.
- Không có wake word (bé 2–5 tuổi dùng nút).

## Âm lượng trần
`STLAB_MAX_VOLUME 60` (config.h). Lớp `StlabEs8388Codec` kẹp mọi lệnh `SetOutputVolume` (nút, MCP, máy chủ) và kẹp giá trị đã lưu lúc
khởi động. Mặc định lần đầu 40.

## Máy chủ trong lab
`CONFIG_OTA_URL = http://<IP>:8003/xiaozhi/ota/` (xinnan server, `http_port: 8003`). Không dùng api.tenclass.net.
IP lấy từ biến môi trường `STLAB_XIAOZHI_SERVER`; không đặt thì `sync.ps1` lấy IPv4 LAN của máy và in cảnh báo. Đổi IP:
```
$env:STLAB_XIAOZHI_SERVER = '192.168.1.50'
powershell -NoProfile -ExecutionPolicy Bypass -File sync.ps1; powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1
```
Phân vùng `partitions/v2/4m.csv` (factory 0x2F0000 + assets 1 MB, không OTA firmware).
