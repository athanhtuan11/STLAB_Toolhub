# CAD vỏ Cú Bông

**Bản hiện tại: có màn 2,8" + 2 loa** (WIP 2026-11-26, mục "Bản có màn + 2 loa" bên dưới). Bản S3 1 loa và A1S là lịch sử, đã vào `backup/` (mục "Lịch sử" cuối file).

**Bàn in thử v3 (2026-11-26):** `print/print-s3-test.yaml` → `print/plates-s3-test/p1-fit-test/p1-fit-test.3mf`, PASS 105 phút, 54,2 g, 1 màu: `face-plate`, `speaker-ring-L`, `button-cap`. Chờ in (cần 4 vít M2.5 × 6).

## Bản có màn + 2 loa (H0 ngang, 2026-11-26, gate PASS)
Sinh bằng `build_owl_s3_screen.py` (Blender 5.2) → `out-s3-screen/` (STL, `asm/`, `owl-params.json`, ảnh, `owl-assembly.sc`);
bàn in `print/print-s3-screen.yaml` → `print/plates-s3-screen/` (STL in ở `print/stl-s3-screen/`; `amp-tray` in 2 cái = `amp-tray.stl` + `amp-tray-2.stl`).
Gate `gate_owl_s3_screen.py` PASS; 5 bàn PASS không support: A vỏ trước 304 ph 150 g, B vỏ sau 296 ph 157 g, C loa 166 ph 58 g, D kem 107 ph 52 g, E bơ 51 ph 25 g.

### Vị trí cuối (mm; +Z lên, mặt trước −Y, mặt ráp y = 0,37)
| Linh kiện | Tâm / số | Ghi chú |
|---|---|---|
| Màn MSP2807 | PCB (0; −50,7; 100), header +x, kính y −55,5 | lỗ PCB (±40; ±22) hàng thật V1.1; cửa sổ 58,4 × 44 lệch −4,9; viền đè 2,5; glass_recess 1,5 (viền 1,35) |
| face-plate | đĩa 94 × 58 R10 nhô 4, yên vát 45° rộng 5, vành chặn 104 × 68 × 2 | lắp từ trong; 4 vít M2.5 × 6 ở (±45,5; ±27,5) (đổi từ (±49; ±31) vì góc vành R15) |
| Hộp nền màn | thẳng y −53, thành 2,4, mép trước bo 6, thu nhỏ 45° về thân | khe vành chặn 0,3; R plan 17,7 |
| Loa L/R | (∓51,8; 0,37; 46), trục [∓1; 0; 0] | vành loa + yên nón 25° + hầm giọt nước như bản A1S; ngàm xoay + gờ Ø48; mặt vành x = ±69 |
| Ampli ×2 | (−3; −13; 7,3) và (+3; +12,5; 7,3) | dưới bo S3 giữa 2 ray (khay v2), cách loa ≤ 70 |
| Mic | module Ø15 nghiêng 45° tâm (0; −29,2; 133,3), trục [0; −0,7075; 0,7067] | lỗ Ø4 trong vách vỏ cách PCB 0,2; kẹp mic = ống lót nửa dưới + gờ vát; giữ PCB bằng keo nóng |
| Mỏ | tâm z 63,4, mặt gốc y −57,4 (trước đĩa, khe 0,4) | dome đỉnh z 72 (chồng mép dưới đĩa 1,0; đỉnh ≤ 77); tâm không đạt 69 vì vành giữ mỏ phải dưới lỗ màn (z 70,7) |
| Bụng | Ø36 tâm z 28, 12 vạch + chữ STLAB | trơn, không lỗ loa |
| Cánh | (±55; 14; 110) nhỏ 12 × 24 × 32, sát thân | không đè vành loa |
| Bu-lông đế | (±24; ±14) như bản S3 | |

### TODO còn lại
1. Dáng: hộp nền vẫn nhô khỏi thân (thành thẳng ~15 mm ở góc trên/dưới trước khi thu 45°); vai R ≥ 12 chỉ đạt ở góc mặt phẳng (R17,7), mép trước bo R6 (R12 làm mặt trước hẹp hơn lỗ 94,6) – cần Claude xem ảnh.
2. Mỏ: hơi chồng đĩa 1 mm, chưa chồng ~4 mm như V2 (vành giữ mỏ chạm đĩa).
3. Mic: ống dẫn âm = lỗ Ø4 trong vách vỏ; khớp mê cung chỉ ghi tham số (`mic.seal`), chưa có rãnh thật.
4. Đo thật: PCB ampli / INMP441 (độ dày, linh kiện) như bản v2.
