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
