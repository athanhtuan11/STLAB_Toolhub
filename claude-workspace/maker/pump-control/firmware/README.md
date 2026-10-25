# Firmware máy bơm – ESP32-WROOM-32D + ESP RainMaker

ESP-IDF **5.5.4** (`C:\Espressif`), `esp_rainmaker` ~1.17.0, `rmaker_app_network` ~1.4.5, `rmaker_app_reset` ~1.0.0
(phiên bản chốt trong `dependencies.lock`).

## Cấu trúc
- `main/pump.c/.h` – điều khiển relay, **không phụ thuộc cloud**: khởi động → TẮT; tự tắt sau "Chạy tối đa".
- `main/app_main.c` – RainMaker: thiết bị "May bom" trên app, hẹn giờ, OTA, nút reset.
- `partitions.csv` – flash 4 MB, 2 vùng OTA (cập nhật firmware từ xa) + `fctry` (dữ liệu claim).

## Giao diện trên app "ESP RainMaker" (iOS / Android)
| Mục | Kiểu | Ghi chú |
|---|---|---|
| Bật/Tắt | công tắc | không lưu → mất điện có lại luôn TẮT |
| Chạy tối đa (phút) | thanh kéo 5–240, bước 5 | mặc định 30, lưu qua mất điện |
| Còn lại (phút) | chỉ đọc | cập nhật mỗi phút khi đang chạy |
| Lịch (Schedules) | có sẵn trong app | bật theo lịch vẫn bị giới hạn "Chạy tối đa" |
Tự tắt do hết giờ → app nhận thông báo "May bom da tu tat…".

## Nối dây
GPIO26 → IN1 module relay (jumper **H**); 5V/GND chung. Nút BOOT (GPIO0): giữ **3 s** = xóa Wi-Fi, **10 s** = reset nhà máy.

## Build / nạp (PowerShell)
```powershell
. C:\Espressif\Initialize-Idf.ps1 -IdfId esp-idf-20ee62e792ea89630ac6a777ab3ebc57
cd D:\04_Stlab\04_STLAB_Toolhub\claude-workspace\maker\pump-control\firmware
idf.py build
idf.py -p COM5 flash monitor     # COM5: đổi theo cổng thật (Device Manager)
```
**Khi cắm USB nạp code: ngắt nguồn 5 V của tủ** (chỉ 1 nguồn tại 1 lúc – Espressif DevKitC).

## Kết nối lần đầu
1. Cài app **ESP RainMaker**, đăng nhập tài khoản (tài khoản của STLab hoặc của khách – thiết bị gắn vào tài khoản đó).
2. Bật nguồn ESP32 → log Serial in **mã QR** + tên `PROV_xxxx` và mã PoP.
3. App → Add Device → quét QR (hoặc chọn Bluetooth) → chọn Wi-Fi 2,4 GHz nhà khách → xong.
4. Thử: Bật trên app → relay đóng → contactor hút. Đổi "Chạy tối đa" = 5 phút → chờ tự tắt.

## Chưa thử trên phần cứng thật (`TODO`)
- Module relay jumper H đóng/nhả dứt khoát với GPIO26.
- GPIO26 không có xung lúc cấp điện/khởi động (đo bằng LED/đồng hồ trước khi nối contactor).
- Assisted claim qua app trên tài khoản dùng thật.
