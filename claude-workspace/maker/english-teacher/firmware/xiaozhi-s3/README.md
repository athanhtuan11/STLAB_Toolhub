# xiaozhi-s3 – Cú Bông bản ESP32-S3, trò chuyện trực tiếp (bé ngắt lời bằng giọng)

xiaozhi-esp32 v2.5.2 (bản ghim `community/78-xiaozhi-esp32`, commit 49b4380, **chỉ đọc**) cho ESP32-S3 N16R8 + mic INMP441 + ampli MAX98357A.
Không có codec trả tham chiếu loa → AEC trên bo dùng **tham chiếu phần mềm**. Spec: `spec-s3-realtime.md`. Bản A1S: `../xiaozhi-a1s/` (không đụng).

## Sync / build / nạp
```
powershell -NoProfile -ExecutionPolicy Bypass -File sync.ps1     # chép bản ghim -> C:\xzb\s3, thêm bo stlab-s3, áp patches, ghi sdkconfig.defaults
powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1    # ESP-IDF 6.1, log build.log, xóa .bin cũ trước khi build
python check_s3.py                                               # gate
```
Máy chủ lab lấy từ biến `STLAB_XIAOZHI_SERVER` (không đặt thì dùng IPv4 LAN máy này) → `CONFIG_OTA_URL=http://<ip>:8003/xiaozhi/ota/`.
`build-src` là junction tới `C:\xzb\s3` (đường thật phải ngắn, xem README A1S). Lần build đầu tải ~74 component, mất lâu; nếu bị ngắt giữa chừng
thì xóa `C:\xzb\s3\managed_components` rồi build lại (thư mục dở dang gây `FileExistsError`).
Nạp (khi Tuan đồng ý, sẽ đè firmware đang có): `idf.py -p COMx flash monitor` chạy từ `C:\xzb\s3` trong PowerShell đã kích hoạt IDF 6.1.

Patch: `0001` đăng ký bo (Kconfig `BOARD_TYPE_STLAB_S3` + CMake) và thêm bo vào `depends on` của `USE_DEVICE_AEC`; `0002` móc `stlab_afe_out_hook`
(weak) trong `afe_audio_engine.cc` để log RMS sau AFE. Có `USE_DEVICE_AEC` thì xiaozhi tự vào `kListeningModeRealtime` (gửi `listen mode=realtime`,
máy chủ `bridge.py` bật `full_duplex`).

## Wi-Fi
`python wifi-nvs.py --port COMx [--ssid TEN] [--server IP]` (bản sao `../xiaozhi-a1s/wifi-nvs.py`, chỉ đổi `--chip esp32s3`; mật khẩu lấy từ Windows, không lưu file).
Phân vùng `partitions/v2/16m.csv`: `nvs` ở **0x9000**, dài 0x4000 – giống 4m.csv của A1S nên offset/size không đổi (đã đối chiếu file).

## Sơ đồ chân (mức 3,3 V)
| Chức năng | GPIO |
|---|---|
| INMP441 WS / SCK / SD | 4 / 5 / 6 (chân L/R nối GND → kênh trái; VDD 3,3 V) |
| MAX98357A DIN / BCLK / LRC | 7 / 15 / 16 (VIN 5 V hoặc 3,3 V theo module; SD để hở/nối VIN) |
| Nút nói NGOÀI (switch MX 2 chân: GPIO1 ↔ GND, pull-up nội) | 1 |
| Nút BOOT (chìm trong vỏ, chỉ để thử trên bàn, cùng hành vi) | 0 |
| Vol + / Vol − | 40 / 39 |
| LED trạng thái (WS2812 trên bo, nếu có) | 48 |
GPIO35–37 bị PSRAM octal (N16R8) chiếm – không dùng. Nút: chạm = mở/đóng phiên, chạm lúc cô nói = ngắt, giữ lâu = ngủ (chạm lúc ngủ = nói ngay); vol+ giữ lâu không làm gì (đã bỏ cấu hình Wi-Fi qua điện thoại). GPIO1 là RTC GPIO nên dùng được làm chân đánh thức deep sleep nếu bật sau này.

## AEC phần mềm (`boards/stlab-s3/stlab_loopback_codec.*`)
- `Write()`: áp âm lượng, ghi ra MAX98357A **và** chép mẫu (thang 16 bit) vào vòng đệm PSRAM 16384 mẫu.
- `Read()`: trả xen kẽ `[mic, ref, mic, ref…]` (`input_channels_=2`, `input_reference_=true`) – đúng định dạng `"MR"` của `afe_audio_engine.cc`
  (kênh 0 = M, kênh 1 = R; `HandleVoiceResult` lấy `data[i]` bước `channels` làm mic). Loa im / thiếu mẫu → ref = 0.
- Vào/ra 16 kHz, nên ref không đổi tần số.

### Chỉnh `STLAB_AEC_REF_DELAY_MS` (`boards/stlab-s3/config.h`, mặc định 100)
Log mỗi ~5 s khi cô đang nói: `[AEC] delay=100 ms rms mic=… ref=… afe_out=…`.
1. Để cô nói (phát bài/bíp), **không ai nói** gần mic. Nhìn `afe_out` so với `mic`: càng nhỏ hơn mic càng tốt (vọng bị khử).
2. Đổi trễ ±20 ms (khoảng 0–200), build lại, so `afe_out`; chọn giá trị làm `afe_out/mic` nhỏ nhất. Nếu `ref=0` khi loa đang phát → vòng đệm không nạp (kiểm `StlabAEC` log đầu).
3. Còn vọng nhiều: tăng khoảng cách/cách âm mic–loa, giảm âm lượng, rồi nâng `STLAB_BARGE_THRESHOLD` / `STLAB_BARGE_MS` bên máy chủ.
Giá trị 100 ms là **ước tính** (hàng đợi DMA phát 6×240 mẫu = 90 ms + ~10 ms loa→mic), chưa đo trên bo.

## Máy chủ (cầu nối Gemini Live)
`server/live/duplex.py` `BargeGate`: lúc cô nói chỉ coi là bé ngắt lời khi xác suất Silero ≥ `STLAB_BARGE_THRESHOLD` (0,7) liên tục ≥ `STLAB_BARGE_MS` (240 ms);
trước đó gửi số 0. Log `[BARGE]`. Gate: `server/test_full_duplex.py`. Khởi động lại máy chủ để nạp mã mới (không làm trong phiên này).

## Chưa chắc (cần đo trên bo)
- Trễ tham chiếu tối ưu; INMP441 qua `>>12` của xiaozhi có thể bão hòa khi nói to sát mic (nếu `rms mic` ~ 32000 thì đổi dịch bit).
- Chân LED 48 là WS2812 trên phần lớn devkit N16R8; không sáng thì bỏ qua.

## OTA (2026-11-13)
- Phiên bản STLab nằm ở `VERSION` (dạng `2.5.2.1`, 4 số: `ParseVersion` của ota.cc chấp nhận số đoạn bất kỳ, bản dài hơn cùng tiền tố tính là mới); `sync.ps1` đặt `PROJECT_VER` bản chép theo file này.
- Phát hành: `powershell -NoProfile -ExecutionPolicy Bypass -File release.ps1 -Bump` (hoặc `-Version x.y.z.w`): sync + build thật + `check_s3.py`, đọc version trong `xiaozhi.bin` (phải khớp), chép `server/data/firmware/s3/xiaozhi-<ver>.bin` + `manifest.json` (sha256, size). Giữ 3 bản, cũ hơn vào `server/backup/<ngày>-firmware-cu/`. Không nạp bo, không restart máy chủ.
- Bo hỏi `POST /xiaozhi/ota/` mỗi lần khởi động; `bridge.py` chỉ trả URL khi chip `esp32s3` + board `stlab-s3` + version bo cũ hơn manifest + sha256/file khớp. Có bản mới thì bo tải, ghi phân vùng app (không cập nhật assets) rồi tự khởi động lại; bản bằng nhau thì không làm gì (không vòng lặp).
- A1S (ESP32, 4 MB, không khe OTA) không bao giờ nhận URL. Tắt khẩn cấp: biến môi trường `STLAB_OTA_DISABLE=1` (rồi restart máy chủ).
- Rollback: `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y` đã bật trong sdkconfig build → bản mới hỏng (không tự xác nhận) thì bootloader quay về khe cũ. Cần bản 2.5.2 đang chạy trên bo đã có bootloader này (bootloader chỉ đổi qua USB).
- Lần đầu KHÔNG cần USB: bản 2.5.2 trên bo đã có client OTA; chỉ cần Wi-Fi + máy chủ chạy bản bridge.py mới (restart máy chủ 1 lần).
