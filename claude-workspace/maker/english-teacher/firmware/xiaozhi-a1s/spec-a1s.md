# spec-a1s – xiaozhi-esp32 v2.5.2 cho bo ESP32-A1S Audio Kit (STLab)

cwd: `maker/english-teacher/firmware/xiaozhi-a1s`
allow: `boards/**`, `patches/**`, `sync.ps1`, `build.ps1`, `flash.bat`, `sdkconfig.stlab`, `README.md`, `.gitignore`
Không sửa: `check_a1s.py`, mọi thứ trong `claude-workspace/community/` (bản ghim chỉ đọc – gate kiểm `git status` sạch).
gate: `powershell -NoProfile -ExecutionPolicy Bypass -File sync.ps1 && powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 && python check_a1s.py`

## Bối cảnh (đã kiểm)
- Nguồn: `claude-workspace/community/78-xiaozhi-esp32` = tag v2.5.2, commit `49b4380b3fae…`. Build cần ESP-IDF 6.1: PowerShell xóa biến MSYS
  (`MSYSTEM, MSYSTEM_PREFIX, MSYSTEM_CHOST, MINGW_PREFIX, MSYS, CHERE_INVOKING`) → `$env:IDF_TOOLS_PATH='C:\Espressif\tools-v6.1'` →
  `. C:\Espressif\frameworks\esp-idf-v6.1\export.ps1`.
- Bo dò thật (xem `../../CLAUDE.md` "Kết quả dò"): ESP32-D0WD-V3, flash 4 MB, PSRAM 8 MB (map 4 MB), **ES8388 @0x10**, I2C SCL32 SDA33,
  I2S MCLK0 BCLK27 WS25 DOUT26 DIN35, PA GPIO21, LED GPIO22, nút KEY1..6 = GPIO36,13,19,23,18,5 (active low; 36 chỉ vào, không pull-up trong;
  13 có thể dính khe thẻ nhớ/DIP – tránh). **GPIO0 là MCLK → không dùng làm nút BOOT.**
- Mẫu tham khảo trong bản ghim: `main/boards/bread-compact-esp32/` (target esp32, cách khai báo bo ESP32 thường) và các bo dùng
  `Es8388AudioCodec`: `main/boards/yunliao-s3/`, `main/boards/alientek/atk-dnesp32s3/`. Đăng ký bo = 1 mục `config BOARD_TYPE_…` trong
  `main/Kconfig.projbuild` (depends on IDF_TARGET_ESP32) + 1 nhánh `elseif(CONFIG_BOARD_TYPE_…) set(BOARD_DIR …)` trong `main/CMakeLists.txt`.
- Mặc định `CONFIG_OTA_URL` = `https://api.tenclass.net/xiaozhi/ota/` (máy chủ xiaozhi.me ở Trung Quốc) → **bắt buộc đổi** sang máy chủ trong lab
  `http://<IP>:8003/xiaozhi/ota/` (xinnan server, `http_port: 8003`). IP lấy từ biến môi trường `STLAB_XIAOZHI_SERVER` (vd. `192.168.1.47`);
  không có biến → tự lấy IPv4 LAN của máy (máy lab hiện 192.168.1.47) và in ra cảnh báo.

## Việc
1. `boards/stlab-a1s/`: `config.h` (đúng tên define gate kiểm: `AUDIO_CODEC_I2C_SCL_PIN`, `AUDIO_CODEC_I2C_SDA_PIN`, `AUDIO_I2S_GPIO_MCLK/BCLK/WS/DOUT/DIN`,
   `AUDIO_CODEC_PA_PIN`, `AUDIO_CODEC_ES8388_ADDR`), `AUDIO_INPUT_SAMPLE_RATE` / `AUDIO_OUTPUT_SAMPLE_RATE` theo mẫu ES8388, `AUDIO_DEFAULT_OUTPUT_VOLUME` 40,
   `#define STLAB_MAX_VOLUME 60` và board .cc **kẹp** mọi lệnh đặt âm lượng (nút, MCP, server) ≤ STLAB_MAX_VOLUME (vd. bọc codec SetOutputVolume).
   Nút: **nói** (giữ để nói / bấm để bắt đầu) = KEY4 GPIO23; **âm lượng +/−** = KEY5 GPIO18 / KEY6 GPIO5 (bước 10, kẹp trần); LED trạng thái GPIO22.
   Không màn hình (không OLED) – dùng `NoDisplay`/tương đương của mẫu. Không 4G.
2. `config.json`: `{"type": "stlab-a1s", "target": "esp32", "builds": [{"name": "stlab-a1s", "sdkconfig_append": [...]}]}` – append: bo, 4m.csv, wake word
   tắt hoặc mặc định của `sdkconfig.defaults.esp32` (bé 2–5 dùng nút "nói" là chính).
3. `patches/`: bản vá (unified diff) thêm `BOARD_TYPE_STLAB_A1S` vào Kconfig.projbuild + nhánh CMake → `boards/stlab-a1s`.
4. `sync.ps1`: kiểm `git -C community/78-xiaozhi-esp32 rev-parse HEAD` bắt đầu `49b4380`; xóa + chép bản ghim (không gồm `.git`) sang `build-src/`; chép `boards/stlab-a1s`
   vào `build-src/main/boards/`; áp `patches/*` (git apply trong build-src); ghi `build-src/sdkconfig.defaults` thêm `sdkconfig.stlab`
   (OTA_URL LAN, bo, 4m). Không đụng community/.
5. `build.ps1`: IDF 6.1 như trên, `cd build-src`, xóa `build/xiaozhi.bin` cũ, `idf.py set-target esp32` + `idf.py build` (log ra `build.log`), in 15 dòng cuối,
   exit ≠ 0 nếu thiếu .bin. `flash.bat COMx` = `idf.py -p COMx flash monitor`.
6. README.md: cách build/nạp, chân, âm lượng trần, máy chủ LAN, cách đổi IP.

## Nạp (sau gate PASS)
Hỏi phiên chính trước khi nạp đè firmware dò (Tuan cần dùng firmware dò thêm để thử nút + micro). **Không tự nạp.** Báo kích thước .bin và % phân vùng factory.

## Không làm
Không sửa community/, không dùng api.tenclass.net/xiaozhi.me, không bật lưu ghi âm, không âm lượng > 60, không thêm màn hình/4G/camera.
