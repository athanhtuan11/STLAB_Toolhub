# Arduino Mega 2560 Rev3 (A000067) – tổng hợp nguồn cho STLab

> **Trạng thái:** nghiên cứu 2026-11-01, chưa thêm vào thư viện linh kiện Toolhub.

## 1. Đã có trong repo (đường dẫn tương đối claude-workspace)

- `community/arduino-docs-content/content/hardware/mega/boards/mega-2560/` (chính hãng, CC-BY-SA-4.0, ghim `b12ffb3a317c`):
  - `datasheet/en-datasheet.md` (kèm ảnh outline, lỗ bắt, pinout, sơ đồ khối, cây nguồn)
  - `downloads/A000067-full-pinout.pdf`, `A000067-schematics.pdf`, `A000067-cad-files.zip`, `A000067-fritzing.fzpz`
  - `tech-specs.md`, `features.md`, `essentials.md`, `tutorials/getting-started/`
- `community/freecad-library/Computing/SingleBoardComputers/Arduino/arduino-mega.step` (kèm `.fcstd`, `.stl`) – model 3D cộng đồng để lắp vào FreeCAD.

## 2. Thông số chính

Nguồn: datasheet chính hãng `en-datasheet.md`, bản sửa 22/05/2025.

| Hạng mục | Giá trị |
|---|---|
| Chip chính | ATmega2560, 16 MHz |
| Flash | 256 KB (trong đó 8 KB bootloader) |
| SRAM / EEPROM | 8 KB / 4 KB |
| Giao tiếp | 4 USART, SPI |
| Chip USB | ATmega16U2 (bản chính hãng) |
| Chân analog | 16 (A0–A15) |
| Chân PWM | 15 |
| Điện áp vào VIN / jack DC | min 7 V, max 12 V |
| Điện áp USB | 4,8–5,5 V |
| Ổn áp 5 V | Tuyến tính (IC1) |
| Nhiệt độ làm việc | −40…85 °C |
| Dòng tối đa mỗi chân I/O | 20 mA (theo pinout chính hãng, Codex đọc, chưa đối chiếu lần 2) |
| Dòng tối đa chân 3,3 V | 50 mA (theo pinout chính hãng, chưa đối chiếu lần 2) |
| Dòng tối đa chân 5 V | TODO |
| Polyfuse USB | TODO (xem schematic) |

**Cơ khí** (bản vẽ mục Mechanical Information trong datasheet):

- Bo 99 × 53 mm.
- Lỗ bắt vít Ø3 mm; hai lỗ trên cách nhau 75 mm.
- Phần đầu nối bên phải cao 33 mm.
- Tọa độ tuyệt đối từng lỗ: TODO – lấy từ `A000067-cad-files.zip` hoặc đo model STEP bằng công cụ `tools/model-study` trước khi vẽ vỏ.

## 3. An toàn điện

- Cấp VIN 7–12 V. Điện áp cao hơn làm ổn áp tuyến tính nóng.
- Không kéo động cơ, relay, LED dải trực tiếp từ chân I/O hoặc chân 5 V. Dùng driver/transistor, nguồn riêng, nối chung GND.
- Bản clone CH340 phổ biến ở VN cần driver WCH CH34x. Ổn áp và linh kiện nguồn tùy hãng clone; không suy thông số từ bản chính hãng, kiểm mã IC thực tế trên bo.
- Shield RAMPS 1.4: jack DC của Mega không cấp nguồn cho motor/bàn nhiệt qua RAMPS (theo RepRap wiki).

## 4. Nguồn cộng đồng đề xuất

Kiểm GitHub API ngày 2026-11-01.

| Nguồn | Dùng làm gì | Sao | Push cuối | License |
|---|---|---|---|---|
| [arduino/ArduinoCore-avr](https://github.com/arduino/ArduinoCore-avr) | Core AVR chính hãng; bảng chân `variants/mega/pins_arduino.h` | 1514 | 2026-08-02 | LGPL-2.1+ (ghi trong file; API GitHub không nhận dạng) |
| [arduino-libraries/Servo](https://github.com/arduino-libraries/Servo) | Thư viện servo chính hãng | 332 | 2026-09-27 | LGPL-2.1 |
| [waspinator/AccelStepper](https://github.com/waspinator/AccelStepper) | Bản GitHub của AccelStepper (động cơ bước). Fork adafruit/AccelStepper đã archive, không dùng | 219 | 2024-07-16 | TODO (chưa rõ, đọc license) |
| [platformio/platform-atmelavr](https://github.com/platformio/platform-atmelavr) | Board `megaatmega2560` cho PlatformIO | 162 | 2026-06-23 | Apache-2.0 |
| [MarlinFirmware/Marlin](https://github.com/MarlinFirmware/Marlin) | Firmware máy in 3D chạy Mega + RAMPS 1.4, làm ví dụ thực tế | 17645 | 2026-11-01 | GPL-3.0 |
| [Alarm-Siren/arduino-kicad-library](https://github.com/Alarm-Siren/arduino-kicad-library) | Symbol/footprint shield Mega cho KiCad (thiết kế PCB cắm lên Mega) | 451 | 2025-06-07 | CC-BY-SA-4.0 |
| [fritzing/fritzing-parts](https://github.com/fritzing/fritzing-parts) | Part Fritzing (bản chính hãng đã có `.fzpz` ở mục 1) | 628 | 2026-08-12 | TODO (chưa rõ) |

**Nguồn web:**

- docs.arduino.cc/hardware/mega-2560
- Datasheet ATmega2560 trên microchip.com
- Trang CH340 và driver của WCH (wch.cn, wch-ic.com)
- RAMPS 1.4 trên reprap.org/wiki/RAMPS_1.4

**Model vỏ tham khảo** (chỉ đọc kích thước, KHÔNG đăng lại theo luật Tuan 2026-11-01): Printables 309693 "Arduino MEGA 2560 Case" (CC BY 4.0, 3 bu-lông M3).

## 5. Bước tiếp (chờ Tuan chọn)

1. Thêm mục `arduino-mega-2560` vào thư viện linh kiện Toolhub (`tools/robotics-cad/library/components.yaml`): ảnh, thông số mục 2, sơ đồ chân, model STEP.
2. Đo tọa độ 4 lỗ và vị trí cổng USB-B, jack DC (từ CAD zip / STEP) → `fit-library` → vỏ Mega in 3D do STLab thiết kế (có thể đăng MakerWorld).
3. Ghim thêm ArduinoCore-avr (chỉ thư mục `variants/mega`) nếu cần bảng chân cho giáo án.
4. Giáo án: bài nhập môn Mega cho học sinh (giao doc-writer sau).
