# spec-v03 – firmware cam 0.2.0 → 0.3.0: OTA + phát hiện chuyển động + thẻ TF

cwd: `maker/esp32-s3-cam/firmware/cam`
allow: `main/**`, `sdkconfig.defaults`, `ota.py`, `ota-setup.py`, `README.md`
**Không sửa:** `check_cam.py`, `check_v03.py`, `test_v03.py`, `test_cam.py`, `partitions.csv`, `managed_components/`, `../probe/`.

gate: `python check_cam.py && powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 && python check_cam.py && python check_v03.py`
Trên mạch (nếu COM6 có mạch + Wi-Fi nhà): nạp USB lần đầu `idf.py -p COM6 flash` (phải nạp cả bootloader vì bật rollback),
chạy `python ota-setup.py --port COM6`, rồi `python test_v03.py --host stlab-cam.local --ota`. Không có mạch → báo rõ "chưa test trên mạch".

## Bối cảnh
ESP32-S3-CAM N16R8 (PSRAM 8 MB), OV3660, ESP-IDF 5.5.4. Kiến trúc hiện tại (README "Kiến trúc"): một task camera duy nhất gọi
`esp_camera_fb_get`, copy JPEG vào ô "khung mới nhất" (đếm tham chiếu) → GIỮ nguyên nguyên tắc này: chuyển động và ghi thẻ chỉ đọc
khung đã copy, không gọi `esp_camera_fb_get` thêm chỗ nào.
Nhiệt: mạch trần lên ~70 °C khi stream 10 fps → tính năng mới phải nhẹ.

## 1. OTA qua Wi-Fi
- `sdkconfig.defaults`: `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y`. Bảng phân vùng có sẵn ota_0/ota_1 4 MB – không đổi.
- `POST /ota` cổng 80, body = file `.bin` thô (Content-Length ≤ 4 MB, sai → 400). Header `X-OTA-Key` phải khớp khóa lưu NVS
  (namespace riêng `ota`), so sánh thời gian hằng. Thiếu/sai/chưa cài khóa → 403. Chỉ 1 OTA cùng lúc (đang chạy → 409).
- Trong lúc OTA: tạm dừng phát hiện chuyển động; stream có thể bị ngắt. `esp_ota_begin/write/end` → `esp_ota_end` lỗi (ảnh hỏng)
  → 400/500, không đổi phân vùng boot. OK → `esp_ota_set_boot_partition`, trả 200 "OK, khoi dong lai", chờ ~500 ms rồi `esp_restart`.
- Rollback: bản mới gọi `esp_ota_mark_app_valid_cancel_rollback()` chỉ khi camera init OK + chạy ổn 30 s (task hẹn giờ). Nếu
  crash/reset trước đó, bootloader tự quay về bản cũ.
- Lệnh UART0 (cùng chỗ xử lý `WIFI ...` trong wifi_nha.c hoặc tương đương): `OTAKEY <khóa>` (16–64 ký tự in được) lưu NVS,
  trả `OTAKEY OK`; `OTAKEY?` trả `OTAKEY SET`/`OTAKEY NONE` – **không bao giờ in khóa** ra log/UART/HTTP.
- `/status` thêm `ota_partition` ("ota_0"/"ota_1").
- `ota-setup.py --port COM6`: sinh khóa bằng `secrets.token_urlsafe(24)`, gửi `OTAKEY` qua UART (pyserial, 115200, chờ `OTAKEY OK`),
  lưu vào biến môi trường người dùng Windows bằng `setx STLAB_CAM_OTA_KEY <khóa>` (không ghi file, không in khóa).
  Nếu biến đã có thì dùng lại khóa cũ (để nhiều mạch dùng chung 1 khóa).
- `ota.py [--host stlab-cam.local] [--bin build/stlab_cam.bin]`: đọc `STLAB_CAM_OTA_KEY` từ môi trường, POST với header `X-OTA-Key`,
  in tiến trình, chờ mạch lên lại, so `version` + `ota_partition` trong `/status`, exit 0/1.

## 2. Thẻ TF (Tuan CHƯA có thẻ – mọi thứ phải chạy khi không có thẻ)
- SDMMC 1-bit: CLK GPIO39, CMD GPIO38, D0 GPIO40 (nguồn: Prusa-Firmware-ESP32-Cam `module_ESP32-S3-CAM.h`, bộ chân camera trùng
  mạch này; chưa thử trên mạch thật). Bật pull-up trong (`SDMMC_SLOT_FLAG_INTERNAL_PULLUP`), tần số mặc định 20 MHz.
- `esp_vfs_fat_sdmmc_mount("/sdcard", ...)` với `format_if_mount_failed = false` (**không bao giờ format thẻ**). Lỗi/không thẻ →
  `sd_ok=false`, log `[SD] Khong co the` một lần; thử mount lại mỗi 30 s (cắm thẻ sau không cần reset). Không được treo/abort.
- Chỉ ghi/xóa trong `/sdcard/stlab-cam/`. Đầy: khi còn < 10 % hoặc < 200 MB trống → xóa thư mục ngày cũ nhất trong `stlab-cam/`.
- Ghi thẻ ở task riêng nhận việc qua queue (giữ tham chiếu ô khung, nhả sau khi ghi) – không chặn task camera/HTTP.
  Lỗi ghi (rút thẻ) → unmount, `sd_ok=false`, quay lại thử mount mỗi 30 s.
- `/status` thêm `sd_ok` (bool), `sd_free_mb` (số, 0 nếu không thẻ).
- `GET /sd?f=<đường dẫn tương đối trong stlab-cam>`: trả file JPEG. Có `..`, `\`, ký tự lạ → 400. Không thẻ → 503. Không có → 404.

## 3. Phát hiện chuyển động
- Bật/tắt + tham số qua `/control`, lưu NVS cùng cấu hình (struct `cam_cfg`, chấp nhận về mặc định lần đầu như v0.2):
  `motion` 0/1 (mặc định 0 – để chip mát khi không dùng), `motion_thr` 5–80 (ngưỡng lệch độ sáng 1 điểm ảnh, mặc định 25),
  `motion_pct` 1–50 (% điểm ảnh đổi để tính là chuyển động, mặc định 3). Ngoài khoảng → 400.
- Khi `motion=1` task camera không nghỉ nữa mà lấy khung tối thiểu 2 fps (kể cả không ai xem). Mỗi ~500 ms lấy khung mới nhất,
  giải mã thu nhỏ (vd. `jpg2rgb565(..., JPG_SCALE_8X)` → SVGA thành 100×75) → xám → so với nền (trung bình trượt, cập nhật chậm
  để ánh sáng đổi dần không báo động). Chuyển động khi tỉ lệ điểm lệch > `motion_pct` **2 lần liên tiếp**; sau sự kiện nghỉ 10 s.
  Bộ đệm giải mã cấp phát 1 lần trong PSRAM.
- Sự kiện: log `[MOTION] <pct>%`, tăng `motion_count`, lưu bản sao JPEG khung đó trong PSRAM (thay bản cũ) → `GET /event.jpg`
  (chưa có sự kiện → 404). Vòng 20 sự kiện gần nhất trong RAM → `GET /events` JSON list
  `[{"t": "2026-11-05 14:03:22" hoặc "boot+123s", "pct": 7.5, "file": "stlab-cam/20261105/140322.jpg" hoặc null}]`.
  Có thẻ → gửi task ghi thẻ lưu `stlab-cam/YYYYMMDD/HHMMSS.jpg` (chưa có giờ → `stlab-cam/boot/<số giây>.jpg`).
- Giờ: SNTP `pool.ntp.org` sau khi có Wi-Fi nhà, `TZ=ICT-7`. `/status` thêm `time_ok`, `motion` (0/1), `motion_count`,
  `motion_last_s` (số giây từ sự kiện cuối, -1 nếu chưa có).
- Nóng (logic hạ fps sẵn có): chuyển động vẫn chạy ở 2 fps.

## 4. Giao diện (main/index.html, ≤ 40 KB, giữ phong cách v0.2, tiếng Việt có dấu)
- Khối "Chuyển động": công tắc bật/tắt, 2 thanh trượt Độ nhạy (`motion_thr`) + Vùng đổi % (`motion_pct`), ảnh `/event.jpg`
  (tải lại khi `motion_count` đổi), danh sách `/events` (giờ + %; có file thì link `/sd?f=...`).
- Dòng trạng thái thẻ: `sd_ok` → "Thẻ TF: còn X MB" / "Chưa cắm thẻ TF". Hiện version + phân vùng OTA ở chân trang.
- Không thêm nút tải firmware lên web (OTA chỉ qua `ota.py`).

## 5. README
Cập nhật: v0.3.0, mục OTA (cài khóa 1 lần bằng `ota-setup.py`, phát hành bằng `ota.py`), thẻ TF (chân + nguồn Prusa, "chưa thử
trên mạch"), chuyển động, endpoint mới, các trường `/status` mới.

## Không làm
- Không đổi bảng phân vùng, chân camera, logic stream/capture/nhiệt đã chạy ổn (chỉ sửa chỗ cần cho task camera không nghỉ khi motion=1).
- Không ghi khóa/mật khẩu vào file, mã, log. Không format thẻ. Không thêm thư viện tải từ mạng ngoài các component IDF có sẵn
  (`esp_https_ota` không cần; `fatfs`, `sdmmc`, `esp_driver_sdmmc`, `app_update`, `esp_netif` là component IDF).
- Không sửa gate/test.
