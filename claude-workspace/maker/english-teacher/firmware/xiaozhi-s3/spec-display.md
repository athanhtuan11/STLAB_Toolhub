# Spec: mắt Cú Bông trên màn TFT 2,8" (MSP2807) + cảm ứng – firmware xiaozhi-s3

Claude viết 2026-11-28, giao `coder`. Gate: `python check_display.py` (Claude viết, KHÔNG sửa) – chạy SAU `sync.ps1` + `build.ps1`.
Mockup đã duyệt (Tuan chốt dáng màn 2026-11-26): `../../design/concepts/a2-cu-bong-screen-ui.png`, mã vẽ tham chiếu
`../../design/make_sheet_screen.py` hàm `ui()` (k = 1 → đúng pixel màn 320 × 240).

## 1. Phần cứng (số Claude chốt – không đổi)
Màn MSP2807: 240 × 320 SPI, đặt **NGANG** (320 rộng × 240 cao, header phía +x). Chip: LCDWiki ghi **ILI9341**, shop ghi ST7789 → chọn lúc build:
`#define STLAB_LCD_ST7789 0` trong `config.h` (0 = ILI9341 mặc định, 1 = ST7789). Cảm ứng XPT2046 (điện trở).

| Tín hiệu | GPIO | define trong config.h |
|---|---|---|
| LCD SCK (chung T_CLK) | 12 | `DISPLAY_SCK_PIN` |
| LCD MOSI (chung T_DIN) | 11 | `DISPLAY_MOSI_PIN` |
| LCD CS | 10 | `DISPLAY_CS_PIN` |
| LCD DC | 9 | `DISPLAY_DC_PIN` |
| LCD RESET | 8 | `DISPLAY_RST_PIN` |
| Đèn nền LED (PWM) | 14 | `DISPLAY_BACKLIGHT_PIN` |
| Touch T_DO (MISO) | 13 | `TOUCH_MISO_PIN` |
| Touch T_CS | 17 | `TOUCH_CS_PIN` |
| Touch T_IRQ | 18 | `TOUCH_IRQ_PIN` |

- Một bus SPI (SPI2_HOST hoặc SPI3_HOST) cho cả LCD + touch, MISO = GPIO13. LCD clock **20 MHz** (`DISPLAY_SPI_HZ 20000000`, dây ≤ 10 cm,
  wiring-s3.md mục 6); touch **≤ 2 MHz**.
- Hướng ngang: theo mẫu `bread-compact-wifi-lcd/config.h` (`CONFIG_LCD_ILI9341_240X320`), thêm swap_xy = true; các define
  `DISPLAY_WIDTH 320`, `DISPLAY_HEIGHT 240`, `DISPLAY_SWAP_XY`, `DISPLAY_MIRROR_X/Y`, `DISPLAY_INVERT_COLOR`, `DISPLAY_RGB_ORDER` để
  trong config.h – **chưa thử hàng thật**, ghi comment `// TODO thu that: lat/dao mau thi doi o day`.
- Chân âm thanh 4/5/6/7/15/16 và nút 0/1 giữ nguyên. Bỏ hẳn nút âm lượng GPIO39/40 (vỏ không có nút, wiring-s3.md 5.6) – xóa define
  + Button tương ứng (chân trống để dành).
- **Không có màn vẫn phải chạy bình thường** (bo hiện có thể chưa cắm màn): không `ESP_ERROR_CHECK` làm reset vì touch/LCD; touch đọc
  rác → lọc (IRQ phải ở mức thấp + áp lực Z ≥ ngưỡng + 2 lần đọc liên tiếp cách ≤ 30 mm/px... dùng ngưỡng của component), T_IRQ pull-up.

## 2. Hiển thị = chỉ đôi mắt (không chữ, không thanh trạng thái, không phụ đề – bé 2–5 tuổi)
Lớp mới `OwlEyesDisplay` (file `boards/stlab-s3/owl_eyes_display.{h,cc}`), kế thừa `SpiLcdDisplay`/`LcdDisplay` của xiaozhi hoặc
`LvglDisplay`, tự vẽ bằng LVGL 9 (đối tượng tròn/cung, `lv_anim`) – **không** dùng ảnh/GIF/asset. Override `SetupUI` (dựng mắt,
không gọi UI gốc), `SetEmotion`, `SetStatus`, `SetChatMessage` (bỏ qua chữ), `ShowNotification` (chỉ hiện khi đang cài Wi-Fi/lỗi, mục 2.3).

### 2.1 Hình học (pixel, gốc trên-trái, màn 320 × 240) – theo `ui()` k = 1
Nền `#0A0F18`. Hai mắt tâm x = 160 ∓ 83 = **77 / 243**, y = **120** (Ngủ: 130). r = 72.
| Trạng thái | Màu | Hình | Động |
|---|---|---|---|
| **Nghe** (`kDeviceStateListening`) | `#4FC3F7` | elip rx = ry = 72; con ngươi `#14203A` r = 36 tâm lệch y +6; điểm sáng trắng r = 10 tâm (x + 24, y − 24); cung r = 84 dày 5 từ 200° → 340° (đỉnh trên) | cung "thở": opacity 40 ↔ 100 % chu kỳ 1 s |
| **Nói** (`kDeviceStateSpeaking`) | `#FFC83D` | elip rx = 62, ry = 82; con ngươi elip rx 31 × ry 35,6, lệch y +6; điểm sáng như Nghe; không cung | con ngươi co giãn ±8 % chu kỳ 400 ms (giả biên độ); chớp mắt mục 2.2 |
| **Khen** (`SetEmotion` ∈ {happy, laughing, loving, funny, winking, cool, delicious, kissy, confident}) | `#FF7FB0` | mắt cười = cung elip hộp (x ± 62, y − 30 … y + 70) góc 205° → 335°, dày 16; má elip 44 × 24 tâm (x ∓ 50 ra phía ngoài, y + 52); 3 sao 4 cánh (tâm (160, 40) r 16; (30, 50) r 10; (290, 45) r 11; bán kính trong 0,3 r) | sao nhấp nháy 2 lần (scale 70 ↔ 100 %, 250 ms) rồi giữ; **2,5 s sau tự về trạng thái theo DeviceState** |
| **Ngủ** (Idle quá 60 s / `SetPowerSaveMode(true)` / board ngủ) | `#A99BE0` pha 55 % lên nền (= `#636282` xấp xỉ) | mắt nhắm = cung elip hộp (x ± 62, y − 62 … y + 28) góc 25° → 155°, dày 14, tâm y = 130; chữ "Z" 2 cái vẽ bằng đường gấp (tại (240, 40) cỡ 22 và (268, 20) cỡ 14, nét 3) | cả mắt thở opacity 60 ↔ 100 % chu kỳ 4 s |
| **Chờ** (`kDeviceStateIdle` chưa ngủ) | `#4FC3F7` 70 % | như Nghe, không cung | chớp mắt mục 2.2 |
| **Nghĩ** (`kDeviceStateConnecting`, `Starting`, `Activating`, `Upgrading`) | `#4FC3F7` | như Chờ, con ngươi + điểm sáng dời lên-phải (+14, −14) | con ngươi quét trái ↔ phải ±14 px chu kỳ 2 s |
| **Lỗi / mất mạng** (`kDeviceStateFatalError`, `SetStatus` lỗi) | `#7A8699` | như Chờ, con ngươi dời xuống (0, +16) | không động |
| **Cài Wi-Fi** (`kDeviceStateWifiConfiguring`) | nền + chữ trắng | mắt Chờ thu nhỏ 50 % ở nửa trên + 2 dòng chữ (font có sẵn của xiaozhi, tiếng Việt/Anh) nửa dưới: tên Wi-Fi AP và địa chỉ cấu hình (lấy từ `ShowNotification`/`SetChatMessage` lúc cài) | – (cho người lớn) |

### 2.2 Chớp mắt (Chờ / Nghe / Nói / Nghĩ)
Mí = hình chữ nhật nền `#0A0F18` kéo xuống che mắt rồi rút lên, tổng **150 ms**; khoảng cách ngẫu nhiên **2,5–6 s**.

### 2.3 Chuyển trạng thái
Theo `Application` DeviceState (xiaozhi gọi `SetStatus`/`SetEmotion` qua `Display`; nếu cần, board đăng ký callback đổi trạng thái).
Mọi lệnh LVGL phải trong `DisplayLockGuard`. Chuyển trạng thái fade **200 ms**. Không phát âm thanh mới.

## 3. Đèn nền (mắt bé)
PWM LEDC trên GPIO14 (dùng `PwmBacklight` của xiaozhi nếu có). Mức (%): Nghe/Nói/Khen/Nghĩ **40**, Chờ **25**, Ngủ **8**, Cài Wi-Fi **60**.
Define `STLAB_BL_ACTIVE 40`, `STLAB_BL_IDLE 25`, `STLAB_BL_SLEEP 8` trong config.h. **Trần 60 %** (không bao giờ vượt). Lúc khởi động: tắt
(0) tới khi vẽ xong khung đầu (tránh nháy trắng), rồi lên mức.

## 4. Cảm ứng
Component `espressif/esp_lcd_touch_xpt2046` (thêm vào `main/idf_component.yml` qua **patch mới** `patches/0003-...patch` và `sync.ps1`
áp nó như 0001/0002; ghim phiên bản `^1`). Đọc bằng task/timer 30 ms hoặc LVGL indev; chỉ cần "có chạm" (không cần tọa độ chính xác,
không cần hiệu chỉnh). Hành vi:
- Đang **Ngủ** → thức dậy: gọi cùng đường với nút nói ngắn khi ngủ (`power_save_timer_->WakeUp()`, `sleeping_ = false`) + mắt mở; **không** tự mở phiên nói.
- **Chờ / Nghe** → chớp mắt vui (nhắm 300 ms + mắt cười Khen 600 ms) rồi về; đánh thức power save timer.
- **Nói** → chỉ chớp mắt, **không** ngắt lời cô (nút nói đã làm việc này; bé chạm màn liên tục không được làm gián đoạn bài).
- Chống dội: 1 lần chạm / 400 ms.

## 5. Không làm
- Không đổi âm thanh/AEC/nút nói/giao thức/OTA; không sửa `community/`; không thêm ảnh/GIF/phông lớn; không nạp, không chạy `release.ps1`.
- Không sửa `check_display.py`, `check_s3.py`.

## 6. Tiêu chí PASS
- `python check_s3.py` vẫn PASS và `python check_display.py` PASS (gate chạy build thật qua `build.ps1` – `.bin` mới, không tin bản cũ).
- Claude tự kiểm thêm: đọc `owl_eyes_display.cc` đủ 8 trạng thái, số pixel/màu khớp bảng 2.1; RAM tĩnh tăng < 64 KB.
