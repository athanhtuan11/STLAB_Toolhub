# Cú Bông – english-teacher

Máy dạy tiếng Anh cho bé 2–5 tuổi, dùng ESP32-S3 N16R8. Bé nói chuyện trực tiếp với cô qua máy chủ lab (Gemini Live, https://engteacher.mamnoncaynho.com/curriculum). Lộ trình theo giáo trình Seed (`lessons-seed/`).

## Trạng thái hiện tại (2026-11-26)
- **Dáng mới A2 V2:** mắt = màn TFT 2,8" SPI cảm ứng (MSP2807, PCB 86 × 50 mm, bản vẽ LCDWiki), không tấm che kính; mỏ dưới màn; 2 loa Ø52 4 Ω 3 W ở 2 sườn **quay ngang (H0, Tuan chọn 2026-11-26; H25 chếch 25° bỏ vì phải in support)**, mỗi loa 1 ampli MAX98357A; gờ giữ loa Ø48 (bản thử v2 Ø47 không đưa loa vô được). Ảnh: `design/contact-sheet-screen-2l.png`.
- **CAD bản có màn H0 – gate PASS (2026-11-26):** `cad/build_owl_s3_screen.py` → `cad/out-s3-screen` (`owl-assembly.sc` mở bằng SolidCraft, ảnh `owl-preview.png`). 5 bàn `print/plates-s3-screen` PASS không support: A vỏ trước + kẹp mic + 2 khay ampli 304 ph 150,3 g · B vỏ sau 296 ph 156,8 g · C 2 vành + 2 vòng ép loa 166 ph 58,3 g · D kem (khung màn, bụng, đế) 107 ph 51,8 g · E bơ (mỏ, nút, thước chữ thập) 51 ph 25,4 g. Dáng: hộp màn còn hơi vuông, mỏ chồng mép khung màn chỉ 1 mm – chờ chủ dự án duyệt ảnh. **Chưa in cả bộ: đợi kết quả bàn thử v3.**
- **Bàn in thử v3 – CHỜ IN:** `print/print-s3-test.yaml` → `print/plates-s3-test/p1-fit-test/p1-fit-test.3mf`, PASS 105 phút, 54,2 g, 1 màu: `face-plate` (khung màn: kính vào hốc, 4 vít M2.5 × 6 bắt PCB, viền che mép kính, cảm ứng bấm được), `speaker-ring-L` (gờ Ø48, thử với vành loa đã in lần 1), `button-cap` (nút nói). Cần: 4 vít M2.5 × 6.
- **Firmware:** chạy bản S3 1 loa (OTA `release.ps1`). CHƯA có driver màn/cảm ứng, CHƯA thử ampli 2. Chip màn: shop ghi ST7789, LCDWiki ghi ILI9341 → thử khi nạp.
- Bản S3 1 loa cũ (không màn) đã chuyển vào `cad/backup/20261126-ban-s3-1-loa-thay-bang-ban-man/` và `print/backup/20261126-ban-s3-1-loa-thay-bang-ban-man/` (2026-11-26).

## Câu hỏi chờ chủ dự án (xóa khi đã trả lời)
1. **Nút nói in lại:** bản v2 bị lỗi gì (lỏng/chặt chân switch, cỡ khe nào trên `mx-cross-gauge` vừa: 1/2/3 chấm)? (Tuan đang in thử v3 – báo sau khi in)
2. **GAIN MAX98357A:** chưa thử nối GAIN xuống GND (12 dB) – thử khi lắp 2 loa, nghe có vỡ tiếng / còn ngắt lời cô được không.
3. **Nguồn:** "sạc máy tính" là cục sạc laptop USB-C (thường cấp 5 V 3 A – đủ) hay cổng USB trên máy tính (chỉ 0,5–0,9 A – KHÔNG đủ)?

Đã trả lời 2026-11-26: vỏ chọn **H0** (loa quay ngang); lỗ màn hàng thật V1.1 **đối xứng**, mép lỗ cách cả 4 cạnh 1,35 → tâm cách 80,0 × 44,0 (bản vẽ V1.0 ghi 76,08); sau này chạy **pin sạc** (chưa thiết kế – cần cell có bảo vệ + mạch sạc/tăng áp 5 V, ngăn pin bắt vít).

## An toàn
- Nguồn USB 5 V ≥ 2 A. Mỗi loa 1 ampli, **không ghép 2 loa vào 1 ampli** (2 Ω quá tải).
- Kính màn lộ (không tấm che): viền đè mép kính; phụ huynh luôn ngồi cạnh.
- Âm lượng trần trong firmware (tai bé). Không chi tiết nhỏ rời (bé < 3 tuổi), vít giấu.
- Chân logic màn 3,3 V. J1 trên màn để hở khi cấp VCC 5 V (TODO kiểm).
- Giọng bé chỉ tới máy chủ lab, cần phụ huynh đồng ý. API key trong biến môi trường, không vào file.

## Linh kiện (BOM)
- ESP32-S3 N16R8 devkit × 1
- Mic INMP441 × 1
- Ampli MAX98357A × 2 (mỗi loa 1 ampli) + tụ 1000 µF 16 V × 2
- Loa Ø52 × 26 mm, 4 Ω 3 W × 2
- Màn TFT 2,8" SPI cảm ứng MSP2807 × 1
- Switch MX × 1 (nút nói, GPIO1) + nắp `button-cap`
- Vít M2.5 × 6 (4 bắt màn + 4 khung màn + khay ampli)
- Băng xốp 2 mm (loa)
- Nhựa Bambu PETG Basic, 3 màu mơ / kem / bơ

## Sơ đồ chân (tóm tắt)
| Khối | Chân ESP32-S3 | Ghi chú |
|---|---|---|
| Mic INMP441 | GPIO4 / 5 / 6 | WS / SCK / SD; VDD 3V3, L/R nối GND |
| Loa (2 × MAX98357A) | GPIO7 / 15 / 16 | DIN / BCLK / LRC, dùng chung cho 2 ampli; VIN 5V |
| Nút nói (switch MX) | GPIO1 | Chân 1 → GPIO1, chân 2 → GND |
| Màn TFT 2,8" | GPIO10 / 9 / 8 / 11 / 12 / 14 | CS / DC / RESET / MOSI / SCK / LED (PWM) |
| Cảm ứng màn | GPIO13 / 17 / 18 | T_DO / T_CS / T_IRQ; T_CLK chung GPIO12, T_DIN chung GPIO11 |

Đấu dây đầy đủ: [hardware/wiring-s3.yaml](hardware/wiring-s3.yaml) (nguồn), [hardware/wiring-s3.md](hardware/wiring-s3.md) (hàn và nối dây), trang Toolhub `/projects/maker--english-teacher/guide`.

## Thư mục
- `cad/` – script sinh vỏ (Blender bpy), gate, file CAD để đo.
- `print/` – cấu hình bàn in (`print-*.yaml`) và bàn đã xếp (`plates-*`).
- `design/` – concept dáng, contact sheet duyệt bằng ảnh.
- `firmware/xiaozhi-s3/` – firmware ESP32-S3 (nền xiaozhi).
- `server/` – máy chủ lab (Gemini Live, cầu nối, giáo trình web).
- `hardware/` – sơ đồ đấu dây (yaml, md, pdf).
- `lessons-seed/` – 24 bài học theo giáo trình Seed (sinh từ `stlab/english-curriculum`).
- `docs/` – ghi chú review.

## Lịch sử ngắn
- 2026-11-05: mở dự án (A1S, dáng A Cú Bông).
- 2026-11-12: chuyển S3 realtime INMP441 + MAX98357A, 1 loa.
- 2026-11-17: gỡ A1S (vào `backup/`).
- 2026-11-18: bàn thử v2.
- 2026-11-26: dáng A2 có màn + 2 loa, bàn thử v3.
