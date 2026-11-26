# nfc-story-box – hộp kể chuyện NFC Cú con trên ESP32-A1S cho trẻ 3–6 tuổi

Tuan bắt đầu 2026-11-26 (khuyến nghị số 1 trong danh sách ý tưởng bo A1S). Brief: `design/brief.md`.

## Đã chốt (2026-11-26)
- Bo **ESP32-A1S Audio Kit V2.2** (ES8388) – chân đã dò ở `tools/esp32-a1s/README.md` (I2C 32/33, I2S 0/27/25/26/35, PA 21,
  nút 36,13,19,23,18,5, SD 1-bit 14/15/2).
- Nhân vật **Cú con** (họ Cú Bông) – thiết kế mới của STLab, không chép sản phẩm thương mại.
- Truyện MP3 trên thẻ microSD; thẻ truyện = đĩa in 3D + NTAG213; đọc bằng PN532 I2C (đề xuất, chưa thử).

## Bước 0 – Giao diện (làm TRƯỚC)
- `design/`: 3 dáng + CMF + contact-sheet → Tuan chọn bằng ảnh. Chưa chọn thì chưa làm cơ khí/firmware thật.

## An toàn
- USB 5 V, không Li-ion ở v1. Trần âm lượng trong firmware. Vỏ kín, vít giấu, không chi tiết nhỏ rời.
