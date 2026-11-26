# CAD vỏ Cú Bông

**Bản hiện tại: có màn 2,8" + 2 loa** (WIP 2026-11-26, mục "Bản có màn + 2 loa" bên dưới). Bản S3 1 loa và A1S là lịch sử, đã vào `backup/` (mục "Lịch sử" cuối file).

**Nút nói làm lại (2026-11-26, Tuan in thử: "nút nhấn chìm xuống", chữ thập không ăn chân switch):** chép nguyên clicky chạy thật cat-paw
(`docs/research-notes/cat-paw-clicker-fits.md`): mặt dưới nắp có hốc trần cao **9,80** trên mép váy, ống Ø**5,71** từ trần xuống, đầu ống +**4,31** trên mép váy, lỗ chữ thập 4,19 × 1,25
xuyên hết ống (**5,49** = `mx.cross_depth`); bỏ rãnh vòng r4,6 + ống nhún cũ. Ổ switch ở đỉnh đầu: 14,00 sâu 8,58 + rãnh V catpaw, **miệng ổ = đáy hốc** (như mẫu, không còn khối bay 15,8).
Nắp lúc nghỉ ngồi trên chân (đầu ống cách đỉnh vỏ switch 1,0 mm → chữ thập ăn 2,6/3,6 mm chân), gờ chặn nón cách vành nắp **1,0 mm** (`stop_gap`, nắp nhấc 1 mm vẫn giữ chữ thập).
Giả định chưa có datasheet (ghi trong `mx.assumed`): vỏ switch cao 3,0, chân 3,6, hành trình 4,0.
Hai chỗ lệch yêu cầu ban đầu, cần Claude/Tuan duyệt: (1) PCB mic Ø15 nghiêng 45° (không đổi) có góc tại r 24,8 mm, z 139,17 nằm trong hốc nút → mặt dưới nắp phải khoét côn 45° và **vành nắp thu Ø58 → Ø54** (`TALK_FLANGE_R` 27, vành trong lỗ 1,6 ≥ 1,5); nắp đi xuống được ~3,9 mm trước khi chạm PCB mic (cần ≥ 4,5) → **đã sửa, xem mục "Mic dời" bên dưới (4,85 mm)**.
(2) Thành trụ hốc nút chỉ được cao ≤ 5,0 mm (slicer: mái vòm nằm > 5 mm là CAN SUPPORT) → đáy hốc phẳng ngang miệng ổ, nắp **chạm đáy ở ~3,0 mm** (`travel_free` = 3,39 tính, đo BVH ~3,0) thay vì ≥ 5,5 trống; switch (nguồn phụ 4,0) vẫn qua điểm tác động ~2,0.
Bàn thử nhanh: `p2-button` (nắp + `mx-socket-test.stl` Ø62,8 + vòng ép L). Khe ngàm xoay vòng ép nới (chỉ phía vòng ép, vành loa đã in dùng lại): ống tay 0,25 → **0,40**, chốt 0,25 → **0,40**, rãnh 0,30 → **0,45**.
**Vành loa +2 mm (Tuan 2026-11-26):** `BZL_RF` 36 → 38, vành ngoài Ø86 → Ø90 (lưới Ø56, cốc 29,0, chốt, gờ Ø48 giữ nguyên; lỗ trên vỏ sườn nới theo).
Tuan in thử 2026-11-26: vòng ép loa + gờ Ø48 ĐẠT.

**Bàn in thử v3 (2026-11-26):** `print/print-s3-test.yaml` → `print/plates-s3-test/p1-fit-test/p1-fit-test.3mf`, PASS 105 phút, 54,2 g, 1 màu: `face-plate`, `speaker-ring-L`, `button-cap`. Chờ in (cần 4 vít M2.5 × 6).

## Bản có màn + 2 loa (H0 ngang, 2026-11-26, gate PASS)
Sinh bằng `build_owl_s3_screen.py` (Blender 5.2) → `out-s3-screen/` (STL, `asm/`, `owl-params.json`, ảnh, `owl-assembly.sc`);
bàn in `print/print-s3-screen.yaml` → `print/plates-s3-screen/` (STL in ở `print/stl-s3-screen/`; `amp-tray` in 2 cái = `amp-tray.stl` + `amp-tray-2.stl`).
Gate `gate_owl_s3_screen.py` PASS; 5 bàn PASS không support (khung màn gọn 2026-11-26): A vỏ trước 297 ph 149,1 g, B vỏ sau 294 ph 156,6 g, C loa 171 ph 61,6 g, D kem 109 ph 52,4 g, E bơ 44 ph 19,6 g.

### Vị trí cuối (mm; +Z lên, mặt trước −Y, mặt ráp y = 0,37)
| Linh kiện | Tâm / số | Ghi chú |
|---|---|---|
| Màn MSP2807 | PCB (0; −50,7; 100), header +x, kính y −55,5 | lỗ PCB (±40; ±22) hàng thật V1.1; cửa sổ 58,4 × 44 lệch −4,9; viền đè 2,5; glass_recess 1,5 (viền 1,35) |
| face-plate | đĩa 94 × 58 **R14** (mép trước R3 + vát 0,88), nhô 4, yên vát 45° rộng 5, vành chặn 104 × 68 × 2 | lắp từ trong; 4 vít M2.5 × 6 ở (±45,5; ±27,5) (đổi từ (±49; ±31) vì góc vành R15) |
| Hộp nền màn | thẳng y −53, thành 2,4, mép trước bo 6, thu nhỏ 45° về thân | khe vành chặn 0,3; R plan 17,7 |
| Loa L/R | (∓51,8; 0,37; 46), trục [∓1; 0; 0] | vành loa + yên nón 25° + hầm giọt nước như bản A1S; ngàm xoay + gờ Ø48; mặt vành x = ±69 |
| Ampli ×2 | (−3; −13; 7,3) và (+3; +12,5; 7,3) | dưới bo S3 giữa 2 ray (khay v2), cách loa ≤ 70 |
| Mic | module Ø15 nghiêng 45° tâm (0; −29,2; 133,3), trục [0; −0,7075; 0,7067] | lỗ Ø4 trong vách vỏ cách PCB 0,2; kẹp mic = ống lót nửa dưới + gờ vát; giữ PCB bằng keo nóng |
| Mỏ | tâm z 63,4, mặt gốc y −57,4 (trước đĩa, khe 0,4) | dome đỉnh z 72 (chồng mép dưới đĩa 1,0; đỉnh ≤ 77); tâm không đạt 69 vì vành giữ mỏ phải dưới lỗ màn (z 70,7) |
| Bụng | Ø36 tâm z 28, 12 vạch + chữ STLAB | trơn, không lỗ loa |
| Cánh | (±55; 14; 110) nhỏ 12 × 24 × 32, sát thân | không đè vành loa |
| Bu-lông đế | (±24; ±14) như bản S3 | |

### Khung màn gọn (Tuan chọn 2026-11-26, spec mục 12)
| | Trước | Sau |
|---|---|---|
| Nền quanh màn | hộp nhô vuông: mép bo R6 rồi thành thẳng ~15–18 mm tới u 22 | vai ellip liên tục: lệch 6,4 mm × sâu 26 mm (u 4 → 30), không còn thành thẳng; nền rộng 110,4 × 74,4 (cũ 109,4 × 73,4) |
| Đĩa mặt (phần thấy) | góc R10, mép trước R6/vát 0,8 | góc **R14**, mép trước **R3** + vát 0,88 × 45° (chỗ chạm bàn) |
| Yên vát / vành chặn | R10 → R15, vát 5 | giữ (vành 104 × 68 × 2, vít (±45,5; ±27,5)); thêm đoạn chuyển R14 → R10 dài 1,7 mm (45°, không support); yên + vành lùi 1,7 mm |
| Giữ nguyên (đã in đạt) | hốc kính 69,2 + 0,3, kính lùi 1,5, cửa sổ 58,4 × 44 lệch −4,9, trụ vít tự ren Ø2,4 tại (±40; ±22), nút nói (mini-cap hốc 9,8, ống Ø5,71, chữ thập 4,19 × 1,25 sâu 5,49, ổ switch 14,00 + rãnh V) | không đổi |
Không thu vành chặn (vành 104 × 68 giữ để vít vào phần đặc ≥ 3,9 ở góc; thu còn 100 × 64 chưa cần). Hố vít dời mồi: lỗ mồi bắt đầu u 9 (tránh thủng vai).
Ảnh: `out-s3-screen/owl-preview.png`, `owl-face-close.png`, `owl-face-45.png`.
**Tuan in thử 2026-11-26: nút nói ĐẠT "rất tốt"** (mẫu p6-test-gon) – giữ nguyên số nút/ổ.

### TODO còn lại
1. Dáng: xem mục "Khung màn gọn" bên dưới. Vai R ≥ 12 KHÔNG đạt hết: lệch ngang tối đa 6,4 mm (mép phẳng 48,8 → thành 55,2) nên vai ellip 6,4 × 26 sâu, không phải R12 tròn; vành chặn chưa thu (giữ 104 × 68).
2. Mỏ: hơi chồng đĩa 1 mm, chưa chồng ~4 mm như V2 (vành giữ mỏ chạm đĩa).
3. Mic: ống dẫn âm = lỗ Ø4 trong vách vỏ; bịt bằng ron xốp 1,2 mm (xem "Mic dời + bịt kín"), chưa thử ron thật.
4. Đo thật: PCB ampli / INMP441 (độ dày, linh kiện) như bản v2.

### Mic dời + bịt kín (2026-11-26)
- Tâm mic hạ **0,9 mm** theo z: (0; −29,2; 133,3) → **(0; −29,2; 132,4)** (`MIC_DROP`), trục nghiêng 45° giữ, x = 0, cách tâm mỗi loa ≫ 60. Lỗ mic ≥ cạnh trên PCB màn + 7,4 (gate ≥ 7,0).
  Côn hốc dưới nắp **giữ theo tâm mic cũ** (`MIC_C_REF`) → nâng khe thật 0,9 mm.
- Đo BVH (nắp `asm/button-cap.stl` tịnh tiến −z đến khi chạm): PCB mic Ø15 × 1,6 = **4,85 mm** (≥ 4,5), kẹp mic 8,05. `mx.travel_free` = 4,85; `mx.travel_floor` = 3,39 (nắp chạm đáy hốc, đo BVH cũ ~3,0 – giới hạn thật còn là đáy hốc, switch cần ~2,0 để tác động).
- **Bịt mic = ron xốp**, bỏ `seal: labyrinth` (không có rãnh thật): hốc PCB Ø16,4 sâu thêm đến vách **w = 1,8** (cũ 1,0) → PCB mặt trước w 0,8, khe 1,0 mm cho ron vòng 1,2 mm (OD 12 / ID 6,4) dán lên vách quanh ống dẫn âm Ø4, PCB ép ron 0,2 (17 %). `mic.gasket_t` = 1,2. (Thử rãnh ron sâu 0,8 → slicer báo floating, bỏ.)
- Bo ESP32-S3: **chưa đo hàng thật** – vẫn khối giữ chỗ 72 × 29 × 16; ray chừa PCB 25,4–28,6 như cũ.

### Mẫu thử lắp nhanh p4 / p5 (`make_fit_coupons.py`)
Đọc STL đã xuất (`out-s3-screen`), cắt nguyên vẹn bằng boolean với hộp, giữ hướng in của vỏ (mặt ghép xuống bàn). Xuất vào `print/stl-s3-test/`:
| Bàn | File | Nội dung | Cắt lớp |
|---|---|---|---|
| `p4-mic-s3` | `mic-seat-coupon.stl` + `mic-clamp.stl` | vùng trán quanh mic 52 × 27 (mặt ghép đến z′ ~37) + kẹp mic; đặt module INMP441 Ø15 + ron xốp | PASS 46 ph, 11,2 g, không support |
| `p5-s3-rail` | `s3-rail-coupon.stl` | ray giữ bo S3 ~18 mm ledge (y 18..36) + hốc + lỗ cáp USB-C 14 × 9, vỏ lưng y 18..58 (72 × 24 × 38,8); đầu ray mở nằm ở mặt bàn | PASS 49 ph, 14,3 g, không support |
Cửa sổ cắt chọn bằng slicer: mẫu mic cần rộng ≥ ±26 mm (hẹp hơn Bambu báo floating vì mảnh vòm mất vách hai sườn), mẫu ray ±36. Lâu hơn 30 phút vì phải in đủ cao theo hướng thật (không thêm đế để khỏi chặn lối cho PCB/kẹp).

### Bảng khe lắp (Tuan 2026-11-26: lỗ/khe = kích thước thật + 0,2 mm, ngàm xoay ≥ 0,40)
Nguồn đầy đủ: `maker/english-teacher/CLAUDE.md` mục "Bảng khe lắp". Đã nâng: **tai ốc M3 (`M3_NUT_S`) 5,8 → 5,9 (0,15 → 0,20/bên)**; mọi khe khác đã ≥ 0,2.
Giữ nguyên vì đã in + chạy thật: khung màn (hốc kính 69,2 + 0,3/bên, PCB), 4 vít M2.5 × 6 tự ren Ø2,4, gờ giữ loa Ø48, vành loa, ổ MX 14,00 + rãnh V, chữ thập 4,19 × 1,25, ống Ø5,71.
