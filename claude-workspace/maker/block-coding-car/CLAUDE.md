# block-coding-car – xe ESP32-S3 lập trình kéo thả kiểu ScratchJr cho bé lớp 1

Tuan bắt đầu 2026-11-16. Bé (lớp 1, 6–7 tuổi) kéo thả khối lệnh bằng hình trên máy tính → bấm Chạy → **xe thật** chạy trên thảm ô.
Thiết kế mới của STLab – tham khảo cách học của ScratchJr (khối icon ngang), KHÔNG chép giao diện/nhân vật/icon của ScratchJr.
Kế hoạch đã duyệt: `C:\Users\hoang\.claude\plans\l-n-d-n-robotics-fizzy-pearl.md` (tóm tắt ở README).

## Đã chốt (2026-11-16)
- Bo **ESP32-S3 N16R8 DevKit**; **2 × 28BYJ-48 5 V + ULN2003**; pin **4 × AA NiMH** hộp khóa vít (không Li-ion).
- Kết nối **Wi-Fi lab**, xe tự phục vụ app web (`robot-<màu>.local`, websocket `/ws`), không cài phần mềm.
- Dùng chung thông số thân xe/thảm ô 150 mm với `maker/card-coding-robot/` (Cú con – tạm dừng).
- Firmware ESP-IDF (chuẩn repo). App HTML/JS thuần nhúng flash. Chương trình = JSON danh sách khối, xe thông dịch.

## Bước 0 – Giao diện – `design/` (làm TRƯỚC)
- `brief.md` → 3 dáng xe (`concepts/`) + 3 bố cục app (`ui-mockups/`) + `cmf.png` → `contact-sheet.png` → Tuan chọn bằng ảnh.
- Chưa chọn thì chưa làm cơ khí/firmware/app thật.

## Cấu trúc
`design/` · `app/` (web kéo thả + mô phỏng) · `firmware/` (ESP-IDF) · `hardware/` (wiring.yaml, BOM) · `solidcraft/` · `print/` · `lessons/` · `docs/`.

## An toàn
- Trẻ 6–7: không chi tiết rời nhỏ, vít không lộ, bánh giấu, hộp pin mở bằng tua vít, NiMH. Firmware nhả cuộn stepper khi đứng yên.
- `TODO` kiểm NiMH đầy (~5,6 V) cấp chân 5V DevKit có an toàn không (datasheet LDO) – nếu không thêm ổn áp 5 V.

## Trạng thái
- 2026-11-16: bước 0 xong ảnh (concepts, ui-mockups, cmf, contact-sheet) + báo cáo giáo dục. **Chờ Tuan chọn** dáng + bố cục (mục "Chờ Tuan quyết" trong design/brief.md).
