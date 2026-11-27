# Cú Bông – english-teacher

Máy dạy tiếng Anh cho bé 2–5 tuổi, dùng ESP32-S3 N16R8. Bé nói chuyện trực tiếp với cô qua máy chủ lab (Gemini Live, https://engteacher.mamnoncaynho.com/curriculum). Lộ trình theo giáo trình Seed (`lessons-seed/`).

## Trạng thái hiện tại (2026-11-26)
- **Khung màn gọn (spec mục 12):** bỏ hộp nền vuông, nền quanh màn = vai ellip 6,4 × 26 mm liền vỏ; đĩa mặt R14 + mép trước R3; vành chặn giữ 104 × 68. Bàn in A–E PASS không support (A 297 ph 149,1 g). Chi tiết trước/sau: `cad/README.md`. **Tuan in thử nút nói = ĐẠT "rất tốt"** (mini-cap hốc 9,8, ống Ø5,71, chữ thập 4,19 × 1,25 sâu 5,49, ổ 14,00 + rãnh V) – giữ nguyên.
- **Dáng mới A2 V2:** mắt = màn TFT 2,8" SPI cảm ứng (MSP2807, PCB 86 × 50 mm, bản vẽ LCDWiki), không tấm che kính; mỏ dưới màn; 2 loa Ø52 4 Ω 3 W ở 2 sườn **quay ngang (H0, Tuan chọn 2026-11-26; H25 chếch 25° bỏ vì phải in support)**, mỗi loa 1 ampli MAX98357A; gờ giữ loa Ø48 (bản thử v2 Ø47 không đưa loa vô được). Ảnh: `design/contact-sheet-screen-2l.png`.
- **CAD bản có màn H0 – gate PASS (2026-11-26):** `cad/build_owl_s3_screen.py` → `cad/out-s3-screen` (`owl-assembly.sc` mở bằng SolidCraft, ảnh `owl-preview.png`). 5 bàn `print/plates-s3-screen` PASS không support: A vỏ trước + kẹp mic + 2 khay ampli 302 ph 150,4 g · B vỏ sau 293 ph 156,6 g · C 2 vành (+2 mm) + 2 vòng ép loa 171 ph 61,6 g · D kem (khung màn, bụng, đế) 107 ph 51,8 g · E bơ (mỏ, nút mới, thước chữ thập) 44 ph 19,6 g (cập nhật 2026-11-26 chiều). Dáng: hộp màn còn hơi vuông, mỏ chồng mép khung màn chỉ 1 mm – chờ chủ dự án duyệt ảnh. **Chưa in cả bộ: đợi kết quả bàn thử v3 + p4/p5.**
- **Bàn thử nút `p2-button` – CHỜ IN (2026-11-26 chiều):** nút nói làm lại theo cat-paw (hốc 9,80, ống Ø5,71, chữ thập 5,49) + khối thử ổ `mx-socket-test` + `speaker-ring-L` khe nới (0,40/0,40/0,45). `print/plates-s3-test/p2-button/p2-button.3mf` PASS 79 ph 44,0 g, không support. Vành loa +2 mm (Tuan 2026-11-26); vòng ép + gờ Ø48 Tuan in thử ĐẠT. Chi tiết số + 2 điểm lệch: `cad/README.md`.
- **Bàn in thử v3 – CHỜ IN:** `print/print-s3-test.yaml` → `print/plates-s3-test/p1-fit-test/p1-fit-test.3mf`, PASS 105 phút, 54,2 g, 1 màu: `face-plate` (khung màn: kính vào hốc, 4 vít M2.5 × 6 bắt PCB, viền che mép kính, cảm ứng bấm được), `speaker-ring-L` (gờ Ø48, thử với vành loa đã in lần 1), `button-cap` (nút nói). Cần: 4 vít M2.5 × 6.
  Tuan in thử 2026-11-26: **khung màn (`face-plate`) ĐẠT, rất vừa** (hốc kính 69,2 + 0,3/bên × 50 + 0,3/bên, 4 vít M2.5 × 6 tự ren Ø2,4, lỗ PCB 80 × 44); gờ giữ loa Ø48 + vành loa ĐẠT. Các số này giữ nguyên (đã kiểm thật).
- **Mic dời + bịt kín, 2 mẫu thử mới (2026-11-26, chờ in):** tâm mic hạ 0,9 mm (z 133,3 → 132,4); nắp nút đi được **4,85 mm** (BVH) trước khi chạm PCB mic (cũ 3,9; kẹp mic 8,05). Bịt mic = **ron xốp 1,2 mm** (hốc PCB sâu thêm đến vách w = 1,8 → khe ron 1,0, ép 0,2), không còn mê cung. Bàn `p4-mic-s3` (`mic-seat-coupon` + `mic-clamp`, 46 ph, 11,2 g) và `p5-s3-rail` (`s3-rail-coupon`, 49 ph, 14,3 g) cắt lớp PASS không support (`cad/make_fit_coupons.py`, cắt nguyên vẹn từ vỏ). **Bo ESP32-S3 vẫn là khối giữ chỗ 72 × 29 × 16 (clone N16R8 2 USB-C, CHƯA đo hàng thật)** – ray chừa PCB rộng 25,4–28,6; không đổi số khi chưa có số đo.
- **Firmware:** chạy bản S3 1 loa (OTA `release.ps1`). CHƯA có driver màn/cảm ứng, CHƯA thử ampli 2. Chip màn: shop ghi ST7789, LCDWiki ghi ILI9341 → thử khi nạp.
- Bản S3 1 loa cũ (không màn) đã chuyển vào `cad/backup/20261126-ban-s3-1-loa-thay-bang-ban-man/` và `print/backup/20261126-ban-s3-1-loa-thay-bang-ban-man/` (2026-11-26).

## Câu hỏi chờ chủ dự án (xóa khi đã trả lời)
1. **Nút nói in lại:** bản v2 bị lỗi gì (lỏng/chặt chân switch, cỡ khe nào trên `mx-cross-gauge` vừa: 1/2/3 chấm)? (Tuan đang in thử v3 – báo sau khi in)
2. **GAIN MAX98357A:** chưa thử nối GAIN xuống GND (12 dB) – thử khi lắp 2 loa, nghe có vỡ tiếng / còn ngắt lời cô được không.
3. **Nguồn:** "sạc máy tính" là cục sạc laptop USB-C (thường cấp 5 V 3 A – đủ) hay cổng USB trên máy tính (chỉ 0,5–0,9 A – KHÔNG đủ)?
4. **Cú Bông v3 (2026-11-27):** (a) duyệt ảnh `cad/out-v3/owl-preview.png` + `owl-exploded.png` (bệ siêu ellip, ampli đứng 2 bên ray – Claude tự chọn); (b) xác nhận có vít M2.5 × 12 (6 cái nối vỏ + 1 thử) và M3 × 16 (4 cái bệ); (c) loại chân cao su Ø10; (d) cân loa + màn để tính lại góc lật; (e) in bàn thử `print/plates-v3-test` trước, báo cỡ lẫy bụng a hay b vừa.

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
