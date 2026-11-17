# drum-pad – bộ trống STEAM 4 pad trên ESP32-A1S cho học sinh lớp 2–5

Tuan bắt đầu 2026-11-17 (hướng B cho bo ESP32-A1S rảnh sau khi Cú Bông chuyển S3). Brief: `design/brief.md`.

## Đã chốt (2026-11-17)
- Bo **ESP32-A1S Audio Kit V2.2** (ES8388) – thông số đã dò ở `maker/english-teacher/CLAUDE.md` (bộ chân "ES8388 v1": I2C 32/33,
  I2S 0/27/25/26/35, PA GPIO21, LED 22, nút 36,13,19,23,18,5; PSRAM 8 MB; flash 4 MB; mic trên bo = LIN2/RIN2).
- **Lớp 2–5**, **4 pad**, **âm mẫu trống thật** (không synth).
- Tham khảo chỉ đọc: `community/jakubthedeveloper-rudebox` (không license → không chép mã; tự viết firmware).

## Bước 0 – Giao diện (làm TRƯỚC)
- `design/`: 3 dáng + CMF + contact-sheet → Tuan chọn bằng ảnh. Chưa chọn thì chưa làm cơ khí/firmware thật.

## An toàn
- USB 5 V, không Li-ion ở v1. Trần âm lượng trong firmware. Vỏ kín, vít giấu, không chi tiết nhỏ rời.
- Đầu vào pad piezo có thể sinh điện áp đỉnh cao khi gõ mạnh → bắt buộc mạch bảo vệ (điện trở + diode kẹp) trước codec/ADC.

## Trạng thái
- 2026-11-17: tạo dự án, brief bước 0; RudeBox ghim vào community (chỉ đọc). Đang: 3 dáng hộp (product-designer).
