# spec-owl-s3-screen – vỏ Cú Bông S3 CÓ MÀN + 2 LOA chếch 25° (Blender bpy)

Claude viết 2026-11-26. Tuan chốt: dáng **A2 V2** (`design/design-spec.md` mục 10 + 10.9, ảnh `design/contact-sheet-screen-2l.png`),
loa **H25** (2 sườn, chếch trước 25°), **dùng cảm ứng, KHÔNG tấm che**, gờ giữ loa **Ø48** (Tuan: Ø47 bản thử v2 không đưa loa vô được).
Hệ trục như `build_owl_s3.py`: mm, +Z lên, mặt trước −Y, mặt ráp y = `split_plane_y` 0,37.

## Cách làm
- Chép `build_owl_s3.py` → **`build_owl_s3_screen.py`** (giữ nguyên bản cũ), xuất **`out-s3-screen/`** (STL đúng hướng in + `asm/` +
  `owl-params.json` + `owl-preview.png` + `owl-exploded.png`).
- Chép `print/print-s3.yaml` → **`print/print-s3-screen.yaml`**, STL ở `print/stl-s3-screen/`, `plates_dir: plates-s3-screen`, xếp bàn THEO MÀU
  (mơ: shell-front, shell-back, speaker-bezel-L/R, speaker-ring-L/R; kem: face-plate, belly, base-plate; bơ: beak, button-cap; mic-clamp,
  amp-tray ×2 vào bàn nào cũng được). `amp-tray` in **2 cái** (số lượng 2 trong print yaml nếu hỗ trợ, không thì 2 file `amp-tray-L/R` giống nhau
  – khi đó gate vẫn đòi file `amp-tray.stl`). Cắt lớp `python ../../tools/print/scripts/slice.py print/print-s3-screen.yaml` → mọi bàn PASS, **không support**.
- `export_cad.py` → `.sc` nếu chạy được với out-s3-screen; không được thì ghi lý do vào README.

## 1. Màn TFT 2,8" (MSP2807) – số chính thức, không đổi
Bản vẽ LCDWiki (`tools/parts-library/components.yaml` id `tft-2-8-spi-ili9341-touch`): PCB 86,00 × 50,00 × 1,60 đặt **NGANG**; kính 69,20 × 50,00,
bắt đầu cách đầu PCB **đối diện header** 6,40; vùng hiển thị AA 57,60 × 43,20, tâm AA lệch **4,9 về phía đối diện header** so tâm PCB; dày 5,60
(không header), 12,78 có header (header nhô sau PCB 7,2, 14 chân bước 2,54 dọc cạnh 50 ở đầu header, tâm hàng cách mép PCB 2,0);
4 lỗ Ø3,20 cách tâm 76,08 (x) × 44,00 (z); **KHÔNG đối xứng theo x**: tâm lỗ cách đầu đối diện header 3,00, cách đầu header 6,92
→ với header +x: tâm lỗ x = **−40,00 và +36,08**, z = **±22,0** so tâm PCB (Tuan đo mép lỗ–cạnh 1,35 ≈ 3,00 − 1,60 ✓).
- **Header về phía +x của trục thân** (`header_side: "+x"`).
- **Tâm PCB (0, ?, 104)**. y: mặt kính (`glass_front_y`) lùi **1,0** sau mặt viền face-plate (`glass_recess` 1,0).
- **Cửa sổ 58,4 × 44,0**, góc R2,5, **lệch tâm −4,9 theo x** (`window_offset_x` −4,9) → viền đè kính: trái 2,5, phải 8,3, trên/dưới 3,0
  (`bezel_over` = 2,5). Mép kính + mép PCB không lộ, không góc nhọn ở mép cửa sổ (vát/bo 0,5).
- Hốc kính trong face-plate: 69,2 + **0,3/bên** × 50,0 + 0,3/bên (khe theo dung sai ±0,2 bản vẽ), sâu = 4,0 (TP 1,2 + LCD 2,3 + băng 0,5)
  + đến mặt PCB; kính **không bị ép** (khe dọc 0,1–0,2 khi siết).
- **Bắt PCB**: 4 trụ trên mặt sau face-plate tại lỗ PCB (x −40,00 / +36,08, z ±22,0), **lỗ vít tự ren M2.5 Ø2,4** (fit-library
  `tipflow-arm/m2.5-self-tap`, vít M2.5 × 6), trụ Ø5,6; trụ liền với thành hốc kính (trụ trái sát mép kính −36,6: khoét phẳng phía kính, khe 0,3).
- **Hốc header**: phía sau PCB đầu +x, rộng ≥ 3 (x) × dài ≥ 35,5 (z) × sâu ≥ 8,0 (y) không có nhựa; dây đi ra sau về bo S3, rãnh luồn dây bo R ≥ 1.
- Lấy dây khe SD/4 lỗ SD: bỏ trống, không cần hốc riêng (lỗ hàn phẳng).

## 2. face-plate (kem, part mới) + mặt phẳng nền trên shell-front
- Đĩa 94 × 58 (PCB + thành ≥ 3,5/bên), cạnh trước bo **R ≥ 9** (đặt R9–12), nhô khỏi thân ~4 ở tâm; tâm đĩa = tâm PCB (đĩa đối xứng, chỉ cửa sổ lệch).
- **Giữ vào vỏ chắc, không keo, bé kéo từ ngoài không ra** (kính lộ, không tấm che): vành face-plate tì mặt ngoài vỏ; vỏ bị kẹp giữa vành face-plate
  và chi tiết phía trong (PCB màn bắt vít hoặc khung/ngàm). Chọn cách nào ghi rõ trong README; nếu dùng ngàm → số theo fit-library, không tự đặt.
- `shell-front`: tạo **mặt phẳng nền** dưới đĩa (nghiêng theo vách ~8–10°), chuyển về mặt cong bằng vai R ≥ 8; khoét lỗ cho face-plate, khe trượt **0,3/bên**.
- **Bỏ** 2 lỗ mắt + `eye-ring`, `eye-diffuser`. In face-plate **mặt trước xuống bàn**: chỗ bo R9 chạm bàn thay bằng vát 0,8; không support.
- Khắc ▲ sâu 0,6 (nét ≥ 0,8) mép dưới đĩa (dấu chiều lắp).

## 3. Mỏ (V2): treo chồng mép dưới đĩa mặt
Tâm mỏ cách tâm màn −31 theo z (≈ z 73), đè viền ~2 mm, **đỉnh mỏ thấp hơn mép dưới cửa sổ ≥ 1 mm** (cửa sổ dưới z = 104 − 22 = 82 → đỉnh mỏ ≤ 81).
Mỏ part bơ riêng như cũ, gắn vào shell-front (không gắn vào face-plate).

## 4. Mic trán
Giữ nguyên cơ cấu mic-clamp + ống dẫn âm bản thử v2, chỉ dời **tâm lỗ mic lên z ≈ 141** (cạnh trên PCB màn z 129 → cách ≥ 8, gate kiểm), x = 0.
Mic cách tâm MỖI loa ≥ 60 (gate).

## 5. 2 loa H25 (thay loa bụng)
- Loa Ø52 × 26 (mép trước 5, thân sau ≤ Ø39). `speakers` = 2 mục `{center, axis}`; **axis = vector pháp mặt loa hướng RA NGOÀI**:
  L `[-0.9063, -0.4226, 0]`, R `[0.9063, -0.4226, 0]` (chếch trước 25°). **Tâm z = 46** (hạ 4 so concept để cách đáy màn).
  Tâm x/y: đặt để vành loa nằm trên vỏ sườn (gợi ý ≈ (±47, −20, 46), được dời ±8 x/y) – báo số cuối trong params.
- Dùng lại **nguyên cơ cấu** speaker-bezel + speaker-ring ngàm xoay 3 chốt của bản S3 (`speaker_clamp`, mọi số giữ: flange 5, bayonet n 3,
  twist 30, sleeve_clr 0,25…), quay theo trục loa; mỗi bên 1 bộ: `speaker-bezel-L/R`, `speaker-ring-L/R` (R = gương L).
  **Thay đổi duy nhất: gờ giữ loa `ring_id` = 48,0** (Tuan; trước 47,0) – đè mép Ø52 còn 2,0/bên; băng xốp 2 mm dán vòng mặt loa giữ như v2.
- Mặt vành loa: cắt phẳng vuông góc trục loa trên vỏ sườn cong, nhô ≤ 2, vát 0,8; lưới Ø56 lỗ Ø2,8 bước 5,6 như cũ.
- Cánh: dời lên (z ≈ 112) + ra sau + nhỏ lại để không đè vành loa (chỉ trang trí, nổi trên shell, không part riêng).
- **Bụng (`belly`)**: tấm kem trơn, **không lỗ loa**; 12 vạch lông vũ khắc nông 0,4 (nét 1,2) + chữ STLAB khắc sâu 0,6 (nét ≥ 0,8) gần đáy bụng.

## 6. Bo S3, 2 ampli, cáp
- Bo ESP32-S3: **giữ nguyên** vị trí + ray bản S3 hiện tại (`pcb_center` (0, 8,7, 34), `pcb_box` [29, 72, 16], cổng USB ra lưng, khe cáp lưng như cũ).
- **2 ampli MAX98357A**, mỗi loa 1 cái (KHÔNG ghép 2 loa 1 ampli): `amps` = 2 mục `{center, box [22,22,10], pcb {center, box, parts_h}}`,
  dùng lại khay `amp-tray` v2 (PCB trượt 2 ray, 2 vít M2.5 × 6 xuống đáy) – **đặt trên sàn**, mỗi cái gần loa của nó, gợi ý tâm (±32, +12, sàn),
  không chạm ray bo S3 (x ±14,5) và thân loa; cách loa ≤ 70 (gate).
- Bỏ `amp_center/amp_box/amp_pcb` cũ (thay bằng `amps`).

## 7. owl-params.json (gate đọc)
`variant: "s3-screen"`; giữ các khóa cũ gate dùng (wall 2,4, speaker_pocket_d 52,6, grille_hole_d 2,8, mic_hole_d 2,0, button_cap_d 50,
button_hole_d 50,8, vent_w 2,0, speaker_clamp, mx, mic, pcb_center/box, pcb_usb, cable_slot, split_plane_y); thêm `speakers` (2, axis vector),
`amps` (2), `screen: {center, glass_front_y, header_side, window [58.4, 44.0], window_offset_x -4.9, glass_recess 1.0, bezel_over 2.5,
holes [76.08, 44.0], hole_d 3.2, touch: true}`. Bỏ `diffuser_t`, `eyes`.

## Gate (Claude viết, KHÔNG sửa)
`"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl_s3_screen.py -- out-s3-screen`
→ `PASS gate_owl_s3_screen` (đòi cả `print/plates-s3-screen/print-report.json` mọi bàn PASS).

## Được sửa
`cad/build_owl_s3_screen.py`, `cad/out-s3-screen/**`, `print/print-s3-screen.yaml`, `print/stl-s3-screen/**`, `print/plates-s3-screen/**`,
`cad/README.md` (thêm mục "Bản có màn + 2 loa").

## Không làm
- Không sửa `build_owl_s3.py`, `gate_owl_s3.py`, `gate_owl_s3_screen.py`, `out-s3/`, `print/print-s3*.yaml` cũ, `plates-s3*/` cũ, firmware/, server/.
- Không đổi số ngoài spec; thiếu số → để rộng + `TODO` trong README.
- Không commit.

## 8. Bổ sung 2026-11-26 (Claude chốt, trả lời BLOCKED của Codex) – ghi đè chỗ còn mở ở mục 2 và 6
### 8.1 Giữ face-plate: LẮP TỪ TRONG, vành chặn + 4 vít (thay mục 2 "giữ vào vỏ")
- face-plate = **đĩa** 94 × 58 (nhìn thấy, bo R9–12, mặt trước nhô ~4 so mặt ngoài nền vỏ) + **vành chặn (flange)** phía sau 104 × 68 × 2,0, góc R4.
- shell-front: lỗ nền = đĩa 94 × 58 + **0,3/bên** (góc bo theo đĩa). face-plate **luồn từ trong ra**: vành chặn tì mặt trong nền ⇒ kéo từ ngoài không ra.
- Đẩy vào trong không lún: **4 vít M2.5 × 6** xuyên vành chặn (lỗ thông **Ø2,8**, fit-library `mec1/m2.5-clearance`) vặn vào **4 trụ trong**
  liền mặt trong shell-front (trụ Ø6,0, lỗ tự ren Ø2,4 sâu ≥ 6, gân nối vách ≥ 1,2), đặt ở 4 góc vành chặn ngoài đĩa (≈ (±49, ±31) so tâm đĩa).
  Lắp trước khi ráp 2 nửa vỏ (vặn từ phía sau shell-front).
- Chồng lớp (từ mặt trước đĩa ra sau): mặt trước đĩa → lùi **1,0** → mặt kính (`glass_front_y`) → kính + LCD + băng **4,0** → mặt trước PCB
  → PCB 1,6 → header 7,2. Vành cửa sổ dày ≥ 1,6, mép trong đè mặt kính với **khe 0,15** (không ép kính). Hốc kính 69,2 + 0,3/bên × 50,0 + 0,3/bên.
- PCB bắt vào 4 trụ face-plate (mục 1): mặt đầu trụ = mặt trước PCB; mặt trước PCB đầu +x có mối hàn header (dải 6 × 38) → face-plate lõm 1,6 ở đó.
- Mặt sau vành chặn phẳng; vành chặn không chạm mic-clamp, loa, vách cong (kiểm bằng gate: face-plate không chạm loa/màn).
### 8.2 Ampli
Dùng đúng số khay v2 trong `out-s3/owl-params.json`: `amp_pcb` box **18,0 × 19,4 × 1,6**, `parts_h` 3,0 (clone Shopee 18 × 19 / Adafruit 19,4 × 17,8 –
TODO đo, giữ như bản v2). Mỗi mục trong `amps` có `pcb: {center, box [18.0, 19.4, 1.6], parts_h 3.0}`; khay amp-tray giữ nguyên hình bản v2.
### 8.3 Dáng
Đọc `design/design-spec.md` mục 10/10.9 nếu được quyền; nếu không, dùng các số trong spec này là đủ (đĩa 94 × 58 R9–12 nhô ~4, mỏ ≤ z 81,
cánh dời lên z ≈ 112, bụng trơn) – không cần ảnh.

## 9. Quyết định 2026-11-26 (Claude, trả lời BÁO LÊN TRÊN của coder) – ghi đè mục 1, 2, 4, 8.1
1. **Mic**: hạ màn xuống **tâm PCB z = 100** (gate cho 98..110) → cạnh trên PCB z 125, mic tâm **z ≈ 133–135** (gate: ≥ 133). Được **vẽ lại kẹp mic**:
   module Ø15 **nghiêng theo vòm** (trục = pháp tuyến vỏ tại lỗ, lệch lên ≤ 45° – params `mic.axis` = vector [0, ay, az]), tấm trượt/khoang kẹp
   thấp hơn z 139 và nằm ngoài vùng nắp nút (r > 30 quanh trục nút); giữ ống dẫn âm + khớp mê cung/ron như v2; vách trước module ≥ 1,6.
   Mỏ: đỉnh ≤ cửa sổ dưới − 1 (cửa sổ dưới = 100 − 22 = 78 → đỉnh mỏ ≤ 77), tâm mỏ ≈ z 69.
2. **Nền màn**: mặt phẳng nền **thẳng đứng** (vuông góc y). Phần đắp hai bên làm **hộp rỗng thành 2,4**, chuyển về vỏ cong bằng vai R ≥ 8, mặt dưới
   mọi phần đắp vát ≥ 45° (không mái treo). **Chỗ tựa vành chặn = yên vát 45° rộng 5** quanh lỗ nền (lỗ 94,6 × 58,6 loe ra 104,6 × 68,6),
   face-plate có vát khớp (khe 0,3); 4 vít M2.5 × 6 xuyên 4 góc vào phần đặc dày ≥ 6 (lỗ thông Ø2,8 trên face-plate, lỗ tự ren Ø2,4 trên vỏ).
3. **Viền cửa sổ**: `glass_recess` = **1,5** → viền dày 1,35 sau khe 0,15 (≥ 3 đường thành 0,42). Đĩa: góc bo **R10 trong mặt phẳng** + vát 0,8 mép trước.
4. Ampli: dời khỏi thân loa (giữ cách ≥ 2 mm), vẫn trên sàn, cách loa ≤ 70.

## 10. Quyết định 2026-11-26 tối (Claude, trả lời BÁO LÊN TRÊN vòng 2) – ghi đè mục 5, 6, 9
1. **Bụng** Ø36 tâm z ≈ 28 (DUYỆT). **Mỏ**: tâm z ≈ 64, đỉnh ≤ 77 (dưới cửa sổ 78), phần trên mỏ nằm TRƯỚC mép dưới đĩa mặt (đĩa đáy z 71) –
   chồng ~4 mm theo V2, khe với mặt đĩa ≥ 0,3, không chạm face-plate (gate kiểm qua owl-assembled).
2. **Loa = chụp trụ (DUYỆT phương án coder)**: ống tay vành loa kéo dài thành **chụp trụ Ø72 sâu 25–35**, in liền vành (đĩa lưới xuống bàn, không support).
   Vỏ chỉ có **lỗ trụ** theo trục loa. **KHÔNG keo**: giữ cơ khí – chụp có **rãnh vòng** ngoài, mép lỗ trên vỏ có **gân vòng** lọt rãnh (khe 0,3/bên,
   gân cao 1,2), mặt ráp 2 nửa vỏ đi qua lỗ nên 2 nửa kẹp chụp khi ráp. Nếu mặt ráp không đi qua lỗ: 2 vít M2.5 × 6 từ trong vỏ vào gờ chụp
   (lỗ thông Ø2,8, tự ren Ø2,4). Gân/rãnh trên vỏ vát 45° để in không support. Cơ cấu ngàm xoay + gờ giữ Ø48 giữ nguyên bên trong chụp.
3. **2 ampli về phía LƯNG**: khay trên sàn/ tấm đế, mỗi bên 1 cái ở x ≈ ±(27..45), y ≈ +15..+45, không chạm bo S3 (ray x ±14,5), cách tâm loa của nó ≤ 70
   (gate). Vít khay như v2.
4. Duyệt: 4 vít face-plate (±45,5; ±27,5); đĩa R10; mic nghiêng 45°. **Không để buồng hở 5,4 trước mic**: ống dẫn âm phải tì sát PCB mic
   (khe ≤ 0,3 hoặc ron) – gate đã sửa: PCB mic kiểm theo trục nghiêng `mic.axis` (cần `mic.pcb` = {center, d 15, t 1,6}). Giữ PCB mic bằng **keo nóng: DUYỆT**
   (bên trong vỏ, bé không chạm).
5. Sửa non-manifold shell-front + mọi va chạm gate báo. Ghi `out-s3-screen`, yaml, cắt lớp, README, .sc như cũ.
