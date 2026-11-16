# block-coding-car

Xe robot cho bé **lớp 1**: kéo thả khối lệnh bằng hình (Tiến, Lùi, Quay trái/phải, Lặp, Âm thanh, Đèn) trên máy tính,
xem xe ảo chạy thử trên lưới ô, rồi bấm **Chạy xe thật** – xe ESP32-S3 đi đúng từng ô 150 mm trên thảm.

- Phần cứng: ESP32-S3 N16R8 DevKit, 2 × 28BYJ-48 + ULN2003, WS2812 (mắt), MAX98357A + loa, nút Dừng, 4 × AA NiMH.
- Kết nối: Wi-Fi lab; mở trình duyệt Chrome/Edge vào `robot-<màu>.local`. Không cài phần mềm, không tài khoản.

## An toàn
- Không Li-ion: 4 × AA NiMH trong hộp pin vặn vít. Không chi tiết nhỏ tháo rời; bánh giấu trong thân.
- Motor + ULN2003 có thể ấm khi chạy lâu – firmware nhả cuộn khi dừng; `TODO` đo nhiệt độ (°C) sau 10 phút chạy.

## Giai đoạn
0. Giao diện (dáng xe + mockup app) – **ảnh xong, chờ Tuan chọn** (`design/contact-sheet.png`)
1. Phần cứng giấy (BOM, wiring, parts-library) · 2. Firmware · 3. App kéo thả + mô phỏng · 4. CAD + in · 5. Bài học + GUIDE + Toolhub

## Lịch sử sửa
- 2026-11-16: tạo dự án, chốt S3 N16R8 + 28BYJ-48 + Wi-Fi lab, dùng chung thân xe với card-coding-robot.
- 2026-11-16: bước 0 – 3 dáng xe (Blender), 3 mockup app, cmf, contact-sheet; báo cáo docs/research-notes/education/block-coding-car-curriculum.md.
