# Nguồn cộng đồng cho Arduino UNO, Raspberry Pi, ESP32, STM32 (STLab, 2026-11-01)

File này dùng kèm `docs/research-notes/arduino-mega-2560.md`. Các bảng repo bên dưới đã kiểm bằng GitHub API ngày 2026-11-01 (sao, push cuối, license). Nội dung khác (an toàn điện, tài liệu web, mục đề xuất) do Codex tra web, đánh dấu "(Codex, chưa đối chiếu)"; cần đối chiếu datasheet chính hãng trước khi dùng cho thiết kế.

## A. Arduino UNO (R3, R4 Minima/WiFi)

**An toàn điện** (Codex, chưa đối chiếu):
- R3: logic 5 V; 20 mA/chân khuyến nghị; 40 mA không được vượt.
- R4 Minima: logic 5 V; 8 mA/chân; 60 mA tổng.
- R4 WiFi: 8 mA/chân; phần ESP32-S3 logic 3,3 V – không đưa 5 V vào.
- Không cấp motor/tải lớn từ GPIO.

| Nguồn | Dùng làm gì | Sao | Push cuối | License |
|---|---|---|---|---|
| docs.arduino.cc/hardware/uno-rev3/, /uno-r4-minima/, /uno-r4-wifi/ | Tài liệu chính hãng: pinout, datasheet, schematic, CAD (Codex, chưa đối chiếu) | – | – | – |
| arduino/ArduinoCore-avr | Core UNO R3 | 1514 | 2026-08-02 | LGPL-2.1+ (ghi trong mã; API GitHub không nhận dạng) |
| arduino/ArduinoCore-renesas | Core UNO R4 | 191 | 2026-05-28 | MIT |
| arduino-libraries/Servo (thuộc github.com/arduino-libraries) | Thư viện servo chính thức | 332 | 2026-09-27 | LGPL-2.1 |

Đã có trong thư viện Toolhub: UNO R4 WiFi (STEP chính hãng).

## B. Raspberry Pi 4/5 + Pico/Pico 2

**An toàn điện** (Codex, chưa đối chiếu):
- GPIO Pi 4/5 là 3,3 V, KHÔNG chịu 5 V.
- Pi đời trước: tổng dòng GPIO tối đa 50 mA.
- Pico/Pico 2: GPIO 3,3 V – kiểm datasheet từng mẫu.
- Motor/servo dùng driver ngoài.

| Nguồn | Dùng làm gì | Sao | Push cuối | License |
|---|---|---|---|---|
| raspberrypi/documentation | Tài liệu chính hãng (GPIO, pinout) | 5624 | 2026-10-28 | CC-BY-SA-4.0 |
| raspberrypi/pico-sdk | SDK C/C++ | 5012 | 2026-10-29 | BSD-3-Clause |
| raspberrypi/pico-examples | Ví dụ blink → ADC, Wi-Fi/Bluetooth, PIO | 3958 | 2026-10-12 | BSD-3-Clause |
| datasheets.raspberrypi.com | Datasheet Pico (Codex, chưa đối chiếu) | – | – | – |
| pip.raspberrypi.com | STEP Pico 2 (Codex, chưa đối chiếu) | – | – | – |

Đã có trong thư viện Toolhub: Raspberry Pi 4B, 5, Zero 2 W, Pico.

## C. ESP32 (DevKit V1, S3, C3, ESP32-CAM)

**An toàn điện** (Codex, chưa đối chiếu):
- Logic 3,3 V; không đưa 5 V vào GPIO.
- Nguồn 3,3 V cấp được ≥ 500 mA.
- DevKitC chỉ cấp nguồn bằng MỘT trong USB / 5V / 3V3, không cấp đồng thời.
- Board "DevKit V1" và nhiều ESP32-CAM là hàng bên thứ ba – datasheet chip không mô tả hết board.

| Nguồn | Dùng làm gì | Sao | Push cuối | License |
|---|---|---|---|---|
| espressif/esp-idf | SDK chính hãng | 19394 | 2026-10-30 | Apache-2.0 |
| espressif/arduino-esp32 | Core Arduino | 17649 | 2026-11-01 | LGPL-2.1 |
| espressif/esp32-camera | Driver camera | 2836 | 2026-10-30 | Apache-2.0 |
| docs.espressif.com | Hướng dẫn DevKitC, ESP Hardware Design Guidelines (Codex, chưa đối chiếu) | – | – | – |
| espressif.com | Datasheet ESP32/S3/C3 (Codex, chưa đối chiếu) | – | – | – |

Đã có trong repo: `espressif/kicad-libraries` (STEP module, đã ghim); ESP-IDF dùng cho pump-control.

## D. STM32 (Blue Pill, Nucleo-64)

**An toàn điện** (Codex, chưa đối chiếu):
- GPIO 3,3 V.
- Một số chân F103 chịu 5 V, nhưng không phải mọi chân – xem datasheet đúng mã chip.
- Dòng GPIO tối đa: TODO theo datasheet.
- Blue Pill là board bên thứ ba.

| Nguồn | Dùng làm gì | Sao | Push cuối | License |
|---|---|---|---|---|
| st.com | Tài liệu STM32F103 (datasheet, reference manual, errata); Nucleo-64 user manual UM1724 (Codex, chưa đối chiếu) | – | – | – |
| STMicroelectronics/STM32CubeF1 | HAL/LL + ví dụ F1 | 746 | 2026-09-16 | Nhiều license theo thành phần |
| STMicroelectronics/STM32CubeF4 | Gói F4 | 1360 | 2026-10-05 | Nhiều license theo thành phần |
| stm32duino/Arduino_Core_STM32 | Dùng Arduino IDE với STM32 (cộng đồng, không phải ST hỗ trợ chính thức – Codex, chưa đối chiếu) | 3376 | 2026-10-30 | Không nhận dạng |

Đã có trong thư viện Toolhub: STM32 Nucleo-64, Blue Pill.

## E. Đề xuất (chờ Tuan)

- Agent research-scout (đang dựng) sẽ theo dõi bản mới của esp-idf, arduino-esp32, pico-sdk, ArduinoCore-renesas, Arduino_Core_STM32 mỗi ngày.
- Giáo án nhập môn cho từng nền tảng làm sau (đã có cho Mega).
- Không ghim repo nào vào `community/` lúc này; dùng khi cần STEP/ví dụ cụ thể.
