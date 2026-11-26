# nfc-story-box – hộp kể chuyện NFC Cú con trên ESP32-S3 cho trẻ 3–6 tuổi

Tuan bắt đầu 2026-11-26 (ý tưởng số 1 của danh sách bo A1S, Tuan đổi sang S3). Brief: `design/brief.md`.

## Đã chốt (2026-11-26)
- **Dáng A – Cú trên gốc cây** (Tuan 2026-11-26), bao 156 × 149 × 160 mm.
- Bo **ESP32-S3 N16R8** (Tuan 2026-11-26, thay A1S) + MAX98357A (chân như Cú Bông S3) + module microSD (SPI2) + RC522 (SPI3)
  + 3 nút + 2 WS2812B qua 74AHCT125. Chân + BOM: `hardware/BOM.md`, `hardware/wiring.yaml` (bản giấy, chưa thử).
- Nhân vật **Cú con** (họ Cú Bông) – thiết kế mới của STLab, không chép sản phẩm thương mại.
- Truyện MP3 trên thẻ microSD; thẻ truyện = đĩa in 3D Ø50 + NTAG213.

## Bước 0 – Giao diện (làm TRƯỚC)
- `design/`: 3 dáng + CMF + contact-sheet → Tuan chọn bằng ảnh. Chưa chọn thì chưa làm cơ khí/firmware thật.

## An toàn
- USB 5 V, không Li-ion ở v1. Trần âm lượng trong firmware. Vỏ kín, vít giấu, không chi tiết nhỏ rời.
