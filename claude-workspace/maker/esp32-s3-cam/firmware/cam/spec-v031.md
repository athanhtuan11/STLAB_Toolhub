# spec-v031 – firmware cam 0.3.0 → 0.3.1: giảm nhiệt

cwd: `maker/esp32-s3-cam/firmware/cam`
allow: `main/**`, `sdkconfig.defaults`, `README.md`
**Không sửa:** `check_*.py`, `test_*.py`, `thermal_log.py`, `partitions.csv`, `managed_components/`, `../probe/`, `ota.py`, `ota-setup.py`.

gate: `python check_cam.py && powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 && python check_cam.py && python check_v03.py && python check_v031.py`

## Vấn đề (đo 2026-11-05)
Trong vỏ, chip 68,8–70,8 °C kể cả lúc không ai xem (mạch trần nghỉ 41 °C). Nguyên nhân Claude suy ra từ code:
1. Khi "nghỉ" task camera chỉ ngừng gọi `esp_camera_fb_get`, nhưng driver (`CAMERA_GRAB_LATEST`, XCLK 20 MHz, DMA) vẫn chụp liên tục.
2. Wi-Fi luôn `WIFI_MODE_APSTA` → AP luôn phát, không có modem sleep.
3. CPU cố định 240 MHz, `CONFIG_PM_ENABLE` tắt.

## Việc
1. **Camera ngủ thật:** không ai xem stream, không có `/capture` đang chờ, `motion=0` liên tục `CAM_IDLE_SLEEP_S` (= 15 s) → `esp_camera_deinit()` (dừng XCLK + DMA), log `[CAM] Camera ngu`, `/status` `cam_sleep: true`. Có người xem / `/capture` / bật motion → init lại (dùng lại hàm init sẵn có, bỏ 3 khung đầu như khi đổi framesize), log `[CAM] Camera thuc`. `/capture` từ lúc ngủ phải trả JPEG < 3 s. Không vi phạm luật "chỉ task camera gọi `esp_camera_fb_get`" (gate đếm ≤ 2 chỗ). Watchdog NULL > 3 s giữ nguyên nhưng không được tính lúc đang ngủ. Đổi framesize/cài đặt khi đang ngủ: lưu cấu hình, áp khi thức.
2. **Wi-Fi:** STA có IP liên tục `AP_OFF_DELAY_S` (= 60 s) → `esp_wifi_set_mode(WIFI_MODE_STA)` (tắt AP), `ap_on: false`. STA mất kết nối liên tục `AP_BACK_DELAY_S` (= 60 s) hoặc chưa cài Wi-Fi nhà → `WIFI_MODE_APSTA` (AP như cũ, mật khẩu như cũ). Giữ logic tự kết nối lại STA + mDNS sẵn có. Không ai xem stream → `esp_wifi_set_ps(WIFI_PS_MIN_MODEM)`; có ≥ 1 người xem → `WIFI_PS_NONE` (giữ fps). `/status` `wifi_ps`: `"none"` / `"min_modem"`. Lưu ý: ở APSTA không được dùng modem sleep → chỉ gọi PS khi đang `WIFI_MODE_STA`.
3. **Quản lý điện năng:** `CONFIG_PM_ENABLE=y`; `esp_pm_configure` max 240 MHz, min 80 MHz, `light_sleep_enable = false` (không light sleep – camera, HTTP, UART lệnh WIFI/OTAKEY phải chạy bình thường).
4. **Trang web:** hiện "Camera đang nghỉ – mở xem để bật" khi `cam_sleep`; sửa tràn ngang trên điện thoại khổ 360–430 px (lưới/flex dùng `minmax(0,1fr)`/`min-width:0`, ảnh `max-width:100%`). ≤ 40 KB.
5. `CAM_VERSION "0.3.1"`; README: mục Nhiệt độ thêm 3 cơ chế + kết quả đo (bảng trước/sau).

## Đo + phát hành (bắt buộc, trên mạch thật – mạch đang chạy 0.3.0 qua OTA, IP stlab-cam.local)
1. **Trước khi OTA:** `python thermal_log.py --min 15 --out thermal-0.3.0.csv` (ghi lại cả số người xem; có người xem thì ghi chú trong báo cáo).
2. Gate PASS → `python ota.py --host stlab-cam.local` (khóa ở biến môi trường người dùng `STLAB_CAM_OTA_KEY`; shell hiện tại chưa có thì đọc HKCU\Environment). KHÔNG nạp USB.
3. `python test_v031.py --host stlab-cam.local` và `python test_v03.py --host stlab-cam.local` (không `--ota`; bước vẫy tay có thể FAIL nếu không có người – ghi rõ).
4. Sau OTA chờ 2 phút rồi `python thermal_log.py --min 15 --out thermal-0.3.1.csv`. Báo bảng: đầu / cuối / max / người xem cho 2 bản.
5. Bản mới lỗi nặng (không lên mạng) → bootloader tự quay về 0.3.0 sau reset; báo ngay, không nạp USB khi chưa hỏi.

## Không làm
Không đổi XCLK/fps/quality mặc định, không đổi chân, không đổi bảng phân vùng, không bật light sleep, không đổi logic OTA/thẻ TF/chuyển động ngoài phần ngủ–thức camera.
