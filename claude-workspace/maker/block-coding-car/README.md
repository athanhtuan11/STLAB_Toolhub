# block-coding-car

Xe robot cho bé **lớp 1**: kéo thả khối lệnh bằng hình (Tiến, Lùi, Quay trái/phải, Lặp, Âm thanh, Đèn) trên máy tính,
xem xe ảo chạy thử trên lưới ô, rồi bấm **Chạy xe thật** – xe ESP32-S3 đi đúng từng ô 150 mm trên thảm.

- Phần cứng: ESP32-S3 N16R8 DevKit, 2 × 28BYJ-48 + ULN2003, buck-boost 5 V, WS2812 (mắt) + 74AHCT125, MAX98357A + loa, nút Dừng, 4 × AA NiMH.
- Kết nối: Wi-Fi lab; mở trình duyệt Chrome/Edge vào `robot-<màu>.local`. Không cài phần mềm, không tài khoản.

## An toàn
- **Không cấp pin thẳng vào chân 5V của ESP32** (LDO chịu tối đa 5,5 V) – luôn qua mạch buck-boost 5 V. Không cắm USB khi công tắc pin đang bật.
- Không Li-ion: 4 × AA NiMH trong hộp pin vặn vít. Không chi tiết nhỏ tháo rời; bánh giấu trong thân.
- Motor + ULN2003 có thể ấm khi chạy lâu – firmware nhả cuộn khi dừng; `TODO` đo nhiệt độ (°C) sau 10 phút chạy.

## Giai đoạn
0. Giao diện – **xong**: dáng A Xe hộp mặt cười + app U1 (`design/contact-sheet.png`)
1. Phần cứng giấy – **xong** (`hardware/BOM.md`, `hardware/wiring.yaml`) · (BOM, wiring, parts-library) · 2. Firmware · 3. App kéo thả + mô phỏng · 4. CAD + in · 5. Bài học + GUIDE + Toolhub

## Lịch sử sửa
- 2026-11-16: tạo dự án, chốt S3 N16R8 + 28BYJ-48 + Wi-Fi lab, dùng chung thân xe với card-coding-robot.
- 2026-11-16: bước 0 – 3 dáng xe (Blender), 3 mockup app, cmf, contact-sheet; báo cáo docs/research-notes/education/block-coding-car-curriculum.md.
- 2026-11-16: Tuan chọn dáng A + bố cục U1 + bộ khối rút gọn; nút Dừng luôn đỏ.
- 2026-11-16: giai đoạn 1 – BOM, sơ đồ dây (GPIO tránh PSRAM/strapping/USB), nguồn qua buck-boost 5 V, thêm 28BYJ-48 + ULN2003 vào parts-library.
