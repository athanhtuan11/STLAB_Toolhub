---
task: esp32-s3-cam-home-wifi
cwd: maker/esp32-s3-cam/firmware/probe
allow:
  - "main/*"
  - "sdkconfig.defaults"
  - "wifi-setup.py"
  - "README.md"
gate: 'powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 && python check_probe.py && python check_wifi.py'
timeout_min: 30
max_rounds: 3
executor: kilo
---

# Mục tiêu
Firmware dò (đang chạy trên mạch thật) thêm **Wi-Fi nhà** để Tuan xem camera thẳng trên máy tính: mạch vào mạng nhà (STA),
quảng bá `http://stlab-cam.local`, vẫn giữ AP `STLAB-CAM-xxxx` dự phòng. Mật khẩu Wi-Fi nhà **không bao giờ** nằm trong mã,
file hay log. Gate `check_probe.py`, `check_wifi.py`, `build.ps1` do Claude viết – **KHÔNG sửa**. Giữ nguyên mọi chức năng cũ.

# Lần trước bị loại (2026-11-03)
Bản trước chỉ viết comment trong 3 nhánh lệnh UART và gọi `nvs_set_str(NULL, ...)` → không biên dịch được. `check_wifi.py`
đã siết: phải có mã thật (NVS_READWRITE + nvs_commit, nvs_erase, esp_wifi_set_config(WIFI_IF_STA), connect/disconnect,
IP_EVENT_STA_GOT_IP, tự thử lại khi WIFI_EVENT_STA_DISCONNECTED, esp_wifi_sta_get_ap_info, uart_driver_install, tách tab),
không khối rỗng. Build phải sạch (lỗi -Werror = FAIL).

# Firmware
- `WIFI_MODE_APSTA`. AP như cũ. STA: đọc `ssid`/`pass` từ NVS namespace `wifi_nha`; có thì kết nối, tự thử lại mỗi 10 s khi mất.
  Có IP → in `[DO] STA IP=<ip> – mo http://stlab-cam.local hoac http://<ip>` (KHÔNG in mật khẩu). Không có → in
  `[DO] Chua cai Wi-Fi nha – chay wifi-setup.py`.
- **Lệnh qua UART0** (cổng COM CH340, 115200, dòng kết thúc `\n`), đọc bằng task riêng `uart_read_bytes` (cài driver UART0 nếu
  console chưa cài; không làm hỏng log):
  - `WIFI <ssid>\t<pass>` (tab ngăn cách vì SSID có thể chứa dấu cách) → lưu NVS, in `[DO] Da luu Wi-Fi nha: <ssid>`, kết nối lại.
  - `WIFI?` → in trạng thái (ssid đã lưu, đã kết nối?, IP, RSSI). `WIFI_CLEAR` → xóa NVS, ngắt STA.
- mDNS (`espressif/mdns` trong `main/idf_component.yml`): hostname `stlab-cam`, instance "STLab ESP32-S3-CAM", service `_http._tcp`
  cổng 80.
- `/status` thêm: `sta_ssid`, `sta_ip`, `sta_rssi`, `mdns`: "stlab-cam.local". Trang `/` hiển thị địa chỉ truy cập.
- HTTP server phải phục vụ được cả 2 mạng (bind mọi interface – mặc định).

# Script máy tính `wifi-setup.py` (Python 3, chỉ cần `pyserial`; chạy bằng Python của ESP-IDF)
- `python wifi-setup.py --port COM6 [--ssid TEN] [--ask] [--clear]`.
- Không có `--ssid`: lấy SSID mạng Windows đang kết nối (`netsh wlan show interfaces`, dòng `SSID`, bỏ `BSSID`).
- Mật khẩu: mặc định lấy từ profile Windows (`netsh wlan show profile name="<ssid>" key=clear`, dòng "Key Content"; hỗ trợ
  Windows tiếng Việt: dòng "Nội dung khóa"). Không đọc được hoặc có `--ask` → `getpass.getpass()`.
- Mở cổng COM **không reset mạch** (dtr = rts = False trước khi open: dùng `serial.Serial()` rồi đặt thuộc tính rồi `.open()`),
  gửi `WIFI <ssid>\t<pass>\n`, đọc log tối đa 30 s tới khi thấy `STA IP=` → in `Mo: http://stlab-cam.local  (IP: x.x.x.x)`.
- **Không in, không ghi file mật khẩu**; khi cần hiển thị thì in `***`. Mật khẩu chỉ nằm trong biến, xóa sau khi gửi.
- `--clear` gửi `WIFI_CLEAR`.
- README.md: thêm mục "Xem trên máy tính" (tiếng Việt có dấu).

# Không làm
- Không sửa gate/build.ps1/flash.bat. Không ghi SSID/mật khẩu nhà vào mã. Không OTA/cloud.

# Tiêu chí PASS
- Gate exit 0. Claude nạp lên mạch thật, chạy wifi-setup.py, kiểm `curl http://stlab-cam.local/status`.
