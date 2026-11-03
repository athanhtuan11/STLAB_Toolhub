# ESP32-S3-CAM N16R8 + OV3660 – phần cứng và phần mềm (tra 2026-11-03)

Codex tra web; Claude chưa mở từng link. Dự án: maker/esp32-s3-cam.

> **An toàn:** pin Li-ion (18650) chỉ dùng cell có bảo vệ + mạch tăng áp đúng dòng. Chưa đọc mạch thật nên mọi thông số nguồn để TODO.

## 1. Sơ đồ chân camera

- Không có sơ đồ chung cho "ESP32-S3-CAM N16R8"; N16R8 chỉ là bộ nhớ, chân do mạch quyết định.

| Tín hiệu | GOOUUU (GPIO) | Freenove (GPIO) |
|---|---|---|
| XCLK | 15 | 15 |
| SIOD | 4 | 4 |
| SIOC | 5 | 5 |
| D0 | 11 | 11 |
| D1 | 9 | 9 |
| D2 | 8 | 8 |
| D3 | 10 | 10 |
| D4 | 12 | 12 |
| D5 | 18 | 18 |
| D6 | 17 | 17 |
| D7 | 16 | 16 |
| VSYNC | 6 | 6 |
| HREF | 7 | 7 |
| PCLK | 13 | 13 |
| PWDN | TODO (chưa rõ) | −1 |
| RESET | TODO (chưa rõ) | −1 |

- Nguồn GOOUUU: https://github.com/Mi-Bee-Studio/esp32s3-n16r8/blob/main/cam/README.md
- Nguồn Freenove: https://github.com/Freenove/Freenove_Ultimate_Starter_Kit_for_ESP32_S3/blob/main/C/Sketches/Sketch_32.1_CameraWebServer/camera_pins.h
- Một mạch ESP32-S3-CAM khác (thẻ TF 1-bit SDIO, LED GPIO2, WS2812 GPIO48) – không chắc áp dụng cho mạch này: https://github.com/larryli/esp-idf_esp32_s3_cam/blob/master/docs/hardware.md
- Chân trống cho robot: TODO – chờ log firmware dò + ảnh mạch.

## 2. OV3660

- esp32-camera hỗ trợ ESP32-S3 + OV3660 tới 2048×1536, có JPEG. Cần PSRAM (trừ ≤ CIF JPEG). RGB/YUV có thể mất dữ liệu khi Wi-Fi tải nặng → dùng JPEG.
- Driver: https://github.com/espressif/esp32-camera ; https://github.com/espressif/esp32-camera/blob/master/sensors/ov3660.c
- Bản v2.1.5 thêm OV3660 cho XIAO ESP32-S3: https://github.com/espressif/esp32-camera/releases
- ESP32-S3: 2 MP chỉ ổn cho ảnh tĩnh JPEG: https://github.com/espressif/esp-video-components/blob/master/esp_cam_sensor/README.md
- FPS thực tế: TODO (đo bằng firmware dò).
- Nguồn cảm biến (datasheet OmniVision): analog 2,6–3,0 V (2,8 V điển hình); lõi 1,425–1,575 V (1,5 V điển hình). Module tự có LDO. https://files.seeedstudio.com/wiki/SeeedStudio-XIAO-ESP32S3/res/OV3660_datasheet.pdf
- Hậu tố 8225N / 40027: TODO. FPC 24 chân tương thích OV2640: TODO (không mặc định).

## 3. Nguồn, nhiệt

- Dòng khi stream: TODO. Tham khảo một bộ XIAO (không phải mạch này): ~300–400 mA khi quay/stream/tải lên – https://github.com/Mi-Bee-Studio/seeed-esp32s3-cam/blob/main/docs/en/hardware.md
- IC ổn áp, dòng USB-C, chạy pin 18650: TODO – đọc mạch thật.

## 4. Phần mềm theo mục tiêu

| Mục tiêu | Chọn | Link |
|---|---|---|
| STEAM lớp 6–9 | Arduino CameraWebServer. Blockly cho mạch này: TODO | https://github.com/espressif/arduino-esp32/blob/master/libraries/ESP32/examples/Camera/CameraWebServer/CameraWebServer.ino |
| Smart home | ESPHome esp32_camera + Home Assistant | https://esphome.io/components/esp32_camera/ |
| Mắt robot | CameraWebServer hoặc ESP-IDF esp32-camera (stream MJPEG) | Xem các link trên |
| AI: phát hiện/nhận diện khuôn mặt, người đi bộ | ESP-WHO (bo mẫu ESP32-S3-EYE) | https://github.com/espressif/esp-who |
| AI: suy luận trên chip | ESP-DL | https://github.com/espressif/esp-dl/releases |
| AI: phát hiện người | TFLite Micro person detection | https://github.com/espressif/esp-tflite-micro/tree/master/examples/person_detection |
| AI: huấn luyện mô hình | Edge Impulse (phải đổi chân camera) | https://github.com/edgeimpulse/firmware-espressif-esp32 |
| MicroPython | micropython-camera-API (OV2640/OV5640; OV3660: TODO) | https://github.com/cnadler86/micropython-camera-API |
| Giám sát camera, phía máy chủ | Frigate / MotionEye: TODO | TODO |

## 5. Vỏ tham khảo (để đo sau)

- https://www.printables.com/model/142405-esp32-cam-indoor-and-outdoor-cases
- https://www.printables.com/model/1749497-esp32-cam-no-cut-case-usb-c
- MakerWorld: TODO.

## 5. Kích thước cơ khí (tra cộng đồng 2026-11-03, Claude mở nguồn; Tuan không đo – dùng cho CAD giả định)

- Mạch của Tuan thuộc dòng **"ESP32-S3-CAM" dạng ESP32-CAM**: 2 hàng header 8 chân, khe FPC 24 chân ở giữa, camera gập
  nằm trên khe thẻ TF, chồng lên **đế nạp kiểu ESP32-CAM-MB** (CH340 + cổng USB + nút IO0/RST). Prusa ghi: mạch là
  "bản sao kích thước của AI-Thinker ESP32-CAM", "không có tài liệu hay sơ đồ chính thức"; sơ đồ chân header:
  trái 5V, GND, GPIO14, 47, 38, 39, 40, 41; phải 3V3, GND, GPIO0, 20, 19, RX, TX, RESET; TF dùng GPIO39/40/41;
  status LED GPIO2, flash LED GPIO48 (theo Prusa – mạch Tuan đèn xanh là WS2812; GPIO48 khớp larryli, chưa thử).
  https://github.com/prusa3d/Prusa-Firmware-ESP32-Cam/blob/master/doc/ESP32-S3-CAM/README.md
- **AI-Thinker ESP32-CAM: 27 × 40,5 × 4,5 mm (±0,2 mm), 10 g** – theo datasheet V1.0 (trích lại bởi SunFounder, cnx-software;
  Claude chưa đọc được trực tiếp PDF): https://docs.sunfounder.com/projects/zeus-car-dev/en/latest/hardware/cpn_esp_32_cam.html ,
  https://www.cnx-software.com/2018/09/30/esp32-cam-esp32-camera-board/
- Header bước 2,54 mm (chuẩn, thấy trên ảnh). Khoảng cách 2 hàng: **ước ~22,9 mm từ ảnh Prusa** (≈ 0,9" = 22,86 mm) – ƯỚC, chưa có nguồn số.
- **Đế nạp ESP32-CAM-MB: ~40 × 27 mm, dày ~10 mm (tính cả header cái)** – số người bán, lệch nhau (39,8–40,5 × 25–27; bản USB-C ~48 mm).
  https://probots.co.in/esp32-cam-mb-micro-usb-programmer-shield-type-a-ch340-serial-downloader.html ,
  https://circuit.rocks/products/esp32-cam-usb-programmer-esp32-cam-mb-ov2640-2mp-wi-fi-ble-usb-c-ch340-8mb-psram
- **Camera OV3660 24 chân loại chung: đầu camera ~8,5 × 8,5 × 4,2 mm, FPC 75 mm, FOV 66–160° tùy loại** – manual người bán,
  không phải đúng mã WS-OV3660-8225N-40027 (mã này không tìm thấy): https://manuals.plus/ae/1005006848295902
- Vỏ cộng đồng để đối chiếu khi CAD: MakerWorld 2688073 (ESP32-S3-CAM + OV3660 ống kính lớn – không mở được, 403),
  Printables "ESP32 CAM Case" ac1dburn https://www.printables.com/model/568613-esp32-cam-case-by-ac1dburn
- **Gợi ý cho CAD giả định:** khối mạch + đế nạp 27 × 40,5 mm, cao tổng ~TODO (4,5 mạch + header + đế ~10 → ước 20–25 mm
  tính cả camera gập); cổng USB ở cạnh ngắn của đế nạp (theo ảnh Prusa). Dung sai lắp: khe 0,3–0,5 mm/bên + fit-library.

## 6. Vỏ cộng đồng ESP32_CAM_CASE.step (Tuan tải 2026-11-03, tác giả/license chưa rõ → chỉ đọc số)

- File: `community/unknown-esp32-cam-case/` (không commit). 2 part: đáy 58,65 × 29,82 × 14,15 mm, nắp 58,65 × 29,82 × 10,45 mm.
- Hốc mạch **40,2 × 27,2 mm** (góc R1), mạch tựa gờ; dưới mạch chỉ ~4 mm; từ mặt mạch tới mặt dưới nắp 7,7 mm.
  Lỗ ống kính trên nắp Ø8,3 mm, tâm cách cạnh ngắn hốc 9,4 mm, giữa chiều rộng. Ngăn phụ 17 mm + lỗ hông Ø6,5 mm.
- **Kết luận: vỏ này cho ESP32-CAM đứng một mình (tháo đế nạp), KHÔNG vừa bộ 2 tầng của Tuan** (shield ESP32-S3-CAM cắm
  chồng lên đế nạp CH340 + USB + nút IO0/RST). Dùng được: kích thước hốc mạch, vị trí ống kính.
- Đế nạp đi kèm mạch S3: ảnh Prusa (board2.png) cho thấy đế cùng bề rộng, cổng USB + nút RST ở cạnh ngắn, IO0 cạnh bên.
  Kích thước đế + khoảng chồng 2 tầng: chưa có nguồn số → CAD dùng ước ~40 × 27 × 10 mm (người bán) và in thử khối kiểm.
