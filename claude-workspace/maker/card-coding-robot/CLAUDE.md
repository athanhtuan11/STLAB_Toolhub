# card-coding-robot – robot lập trình bằng thẻ cho trẻ 4–7 tuổi

Tuan bắt đầu 2026-11-09 (ý tưởng A trong 3 ý tưởng dự án cho trẻ; sau đó B = Otto biết nói, C = hộp kể chuyện NFC).
Thiết kế mới của STLab – tham khảo ý tưởng Plobot/Cubetto (lập trình bằng vật thể), KHÔNG chép dáng/tên/nhân vật.

## Bước 0 – Giao diện – `design/` (làm TRƯỚC)
- `brief.md` → 3 concept + mockup thẻ + `cmf.png` → `contact-sheet.png` → Tuan chọn bằng ảnh. Chưa chọn thì chưa dựng cơ khí.

## Cấu trúc
- `solidcraft/` – CAD (SolidCraft mặc định, mẫu `maker/esp32-s3-cam/solidcraft/build_cam_d.py`): params.json + build script → `.sc` lắp ráp.
- `firmware/` – ESP32 (đọc RC522, 2 stepper, I2S, WS2812). `lessons/` – giáo án theo buổi (nghiên cứu nền: `docs/research-notes/education/card-coding-robot-lessons.md`).
- `print/print.yaml` – bàn in (slice.py). Khe lắp ghép: tra fit-library, ghi bảng khe ở đây khi có.

## An toàn
- Trẻ 4–7: không chi tiết nhỏ rời, hộp pin khóa vít, NiMH (không Li-ion), bánh giấu trong vỏ. Chi tiết ở `design/brief.md`.

## Trạng thái
- 2026-11-09: bước 0 xong, Tuan chọn **C – Cú con**. Giai đoạn 1: dựng SolidCraft theo số ước lượng + chờ ảnh linh kiện thật.
