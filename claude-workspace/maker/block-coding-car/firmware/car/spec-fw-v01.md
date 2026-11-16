---
task: block-coding-car-fw-v01
cwd: maker/block-coding-car/firmware/car
allow:
  - "CMakeLists.txt"
  - "main/*"
  - "sdkconfig.defaults"
  - "partitions.csv"
  - "build.ps1"
  - "ota.py"
  - "wifi-setup.py"
  - "tests/run_golden.c"
  - "README.md"
gate: "..\\.venv-host\\Scripts\\python.exe -m pytest -q tests && powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1"
timeout_min: 45
max_rounds: 2
executor: coder
read: ["maker/block-coding-car/protocol", "maker/block-coding-car/hardware", "maker/esp32-s3-cam/firmware/cam", "maker/english-teacher/hardware/wiring-s3.yaml"]
---

# Mục tiêu
Firmware ESP-IDF v0.1.0 cho xe block-coding-car (ESP32-S3 N16R8): phục vụ app web từ flash, nhận chương trình JSON qua
WebSocket, thông dịch và chạy 2 động cơ bước 28BYJ-48, báo tiến độ từng bước. Chưa có phần cứng – gate = test máy tính + build thật.

# Đầu vào (chỉ đọc)
- `../../protocol/PROTOCOL.md` – **nguồn duy nhất** (mục 1–2 cho `prog.c`, mục 4–5 cho phần còn lại). Số liệu (bước/ô, tốc độ,
  ngưỡng pin, giới hạn âm lượng/độ sáng) lấy đúng từ đây, KHÔNG tự chọn.
- `../../protocol/golden.json` – 33 ca kiểm chung với app.
- `../../hardware/wiring.yaml` – GPIO (test so khớp `pins.h`).
- `maker/esp32-s3-cam/firmware/cam/` – mẫu đã chạy trên S3 N16R8 của lab: `build.ps1` (gọi ESP-IDF 5.5.4, xóa biến MSYS),
  `main/wifi_nha.c` (lệnh UART `WIFI`, `OTAKEY`, không in mật khẩu), `ota_post` trong `cam_main.c` + `ota.py` + `ota-setup.py`
  (OTA đẩy qua HTTP, khóa `X-OTA-Key` từ biến môi trường), mDNS, `sdkconfig.defaults`, `partitions.csv`. Dùng lại cách làm, đổi tên
  biến môi trường thành `STLAB_CAR_OTA_KEY`.
- `maker/english-teacher/hardware/wiring-s3.yaml` – cách nối MAX98357A đã chạy.

# Yêu cầu
## Cấu trúc
- `main/prog.c` + `prog.h`: **C thuần** (chỉ `<stdlib.h> <string.h> <stdbool.h> <stdint.h> <math.h>` + `cJSON.h`), biên dịch
  được trên máy tính: `int prog_expand(const char *json_text, prog_step_t *out, int max, const char **err_code)` (trả số bước ≥ 0
  hoặc −1 + mã lỗi PROTOCOL). Kiểu `prog_step_t {int id; prog_op_t op; int arg;}` + hàm `prog_op_name()`. Thông điệp `run`/`dry`
  có `prog` là mảng → hàm phụ nhận `cJSON *` mảng `prog` dùng chung (bọc `{"v":1,"prog":…}`).
  Số nguyên: cJSON lưu double → kiểm `valuedouble == (int)valuedouble`; `true/false` không phải số.
- `tests/run_golden.c`: `main(argc, argv)` đọc file JSON `argv[1]`, gọi `prog_expand`, in đúng **1 dòng** JSON:
  `{"ok":true,"steps":[[0,"fwd",1],...]}` hoặc `{"ok":false,"code":"bad_arg"}` (không khoảng trắng thừa cũng được – test parse JSON).
  Biên dịch với `-DPROG_HOST_TEST=1 -Wall -Werror` bằng zig cc (xem `tests/test_golden_fw.py`).
- `main/pins.h`: `PIN_ML_IN1..4` (GPIO 4,5,6,7), `PIN_MR_IN1..4` (15,16,17,18), `PIN_LED` 12, `PIN_I2S_BCLK` 9, `PIN_I2S_LRC` 10,
  `PIN_I2S_DIN` 11, `PIN_BTN_STOP` 13, `PIN_BATT_ADC` 1 (ADC1_CH0), `DIR_LEFT` / `DIR_RIGHT` (+1/−1, mặc định trái −1 phải +1 vì 2 motor
  gắn đối xứng – `TODO` kiểm trên xe thật), `#define SOUND_MAX_PCT 30`, `#define LED_MAX_PCT 25`.
- `main/stepper.c/.h`: 2 motor nửa bước 8 pha, chạy trong 1 task ưu tiên cao + `esp_timer`/gptimer; đồng bộ 2 bánh (cùng nhịp);
  dốc tốc 200 → 500 bước/s trong 300 bước đầu, giảm đối xứng ở cuối; hàm `stepper_move(int left_steps, int right_steps)` chặn tới
  khi xong hoặc bị hủy; `stepper_abort()` (gọi được từ ISR/ task khác, dừng ≤ 50 ms); `stepper_release()` đưa 8 chân về 0.
  Gọi `stepper_release` khi chương trình xong, khi dừng (client/nút/pin), khi lỗi.
- `main/sound.c` (I2S std, MAX98357A, 16 kHz mono): 3 âm tự sinh – 0 bíp 880 Hz 150 ms, 1 còi 2 tông 440/660 Hz ~600 ms,
  2 nhạc vui 4 nốt C5-E5-G5-C6 ~1 s; biên độ ≤ `SOUND_MAX_PCT` % full-scale; tắt kênh khi dừng.
- `main/eyes.c`: 2 × WS2812 qua component `espressif/led_strip` (RMT), độ sáng ≤ `LED_MAX_PCT` %; màu theo PROTOCOL bảng `eye`
  + màu trạng thái mục 5. Sau `done/stopped` trả về màu trạng thái.
- `main/batt.c`: `adc_oneshot` + `adc_cali` (curve fitting), × 2 (chia áp 100k/100k) → mV pin; đọc trung bình 8 mẫu mỗi 500 ms.
- `main/main.c`: NVS, Wi-Fi STA (lệnh UART `WIFI`, `WIFI?`, `WIFI_CLEAR`, `OTAKEY`, `NAME <ten> <#mau>`), 20 s không nối được hoặc
  chưa cấu hình → AP mở `robot-<...>` IP 192.168.4.1; mDNS `<name>.local`; HTTP server: `/` trả app gzip nhúng
  (`Content-Encoding: gzip`, `text/html; charset=utf-8`), `/info`, `/ws` (WebSocket, `CONFIG_HTTPD_WS_SUPPORT`), `POST /ota`
  (như esp32-s3-cam, `esp_ota_mark_app_valid_cancel_rollback` sau khi Wi-Fi + HTTP chạy); task chạy chương trình nhận lệnh qua
  queue; gửi `step/done/stopped/batt` tới **mọi** client ws (`httpd_ws_send_frame_async` theo danh sách fd); thông điệp không phải JSON
  hoặc thiếu `t` → `err bad_msg`. Nút Dừng: ngắt GPIO + chống dội 30 ms → `stepper_abort` + `stopped why:"button"`.
  `cal` lưu `steps_cell`/`steps_90` bằng `nvs_set_i32` namespace `car`, kiểm khoảng (1000–8000 / 500–4000), ngoài khoảng → `err bad_msg`.
  Đang chạy mà client ngắt → vẫn chạy hết. Version `0.1.0` (`PROJECT_VER`).
- `main/CMakeLists.txt`: `EMBED_FILES "www/index.html.gz"`; `main/idf_component.yml`: `espressif/mdns`, `espressif/led_strip`.
- `build.ps1` (mẫu cam, IdfId `esp-idf-20ee62e792ea89630ac6a777ab3ebc57`): bước 1 tạo `main/www/index.html.gz` bằng
  `python ..\..\app\build.py --out main\www\index.html.gz`; nếu file `..\..\app\build.py` chưa có hoặc lỗi → nén
  `main/placeholder.html` (trang tiếng Việt ngắn "App đang được làm") thành `main/www/index.html.gz` bằng Python `gzip` và ghi WARN.
  Xóa `.bin` cũ trước khi build; exit ≠ 0 nếu không có `build\block_coding_car.bin`.
- `sdkconfig.defaults`: như cam (16 MB, PSRAM octal, rollback, custom partitions) + `CONFIG_HTTPD_WS_SUPPORT=y`; bỏ phần camera/SD.
- `partitions.csv`: nvs + otadata + phy_init + ota_0 + ota_1 (4 MB mỗi slot như cam).
- `ota.py` (đổi biến thành `STLAB_CAR_OTA_KEY`, host mặc định `robot-do.local`, bin `build/block_coding_car.bin`); `wifi-setup.py`
  (gửi `WIFI`/`NAME` qua cổng COM, mật khẩu nhập bằng `getpass`, không ghi file, không in).
- `README.md` tiếng Việt: an toàn (buck-boost 5 V, không cắm USB khi bật pin – copy từ `../../hardware/BOM.md`), build, nạp lần đầu
  bằng USB (`idf.py -p COMx flash` – CHỈ khi pin đã tắt), cài Wi-Fi/tên, OTA, hiệu chỉnh `cal`, bảng `TODO` đo trên xe thật.

# Không làm
- Không sửa `tests/test_*.py`, `../../protocol/`, `../../hardware/`, `../../app/`.
- Không flash/nạp vào mạch thật, không mở cổng COM trong gate.
- Không ghi mật khẩu Wi-Fi/khóa OTA vào file, log hay UART.
- Không đổi số liệu trong PROTOCOL.md; số chưa chắc để `TODO` trong comment.
- Không để hàm rỗng/khối chỉ comment (test chặn `) {}`); không dùng `if (x) {}` hay `(T){}`.

# Tiêu chí PASS
- Gate exit 0: 33 ca golden khớp trên máy tính + test tĩnh (chân, hằng số, mã lỗi, gọi API thật) + `idf.py build` ra `block_coding_car.bin`.
- Báo lại: kích thước .bin, % slot OTA còn trống, các `TODO` cần đo trên xe thật.
