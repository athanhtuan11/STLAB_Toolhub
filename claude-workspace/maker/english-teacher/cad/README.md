# CAD vỏ Cú Bông – bản 1 (ESP32-A1S Audio Kit, 2 loa)

Sinh bằng `build_owl.py` (Blender 5.2 bpy, boolean MANIFOLD). Gate: `gate_owl.py` (xem `spec-owl.md`). Ảnh duyệt: `out/owl-preview.png`, `out/owl-exploded.png`.
Hệ lắp ráp: mm, +Z lên, mặt trước −Y; mặt ráp hai nửa là mặt phẳng y = 0,37. Mọi số đặt ở đầu `build_owl.py`, ghi vào `out/owl-params.json`.

## Bố trí (đổi 2026-11-05: 2 loa trái + phải)
- 2 loa Ø52 × 26, trục x, mặt ra ngoài, tâm (±51,5; 0; 46), hốc Ø52,6. Mỗi loa nằm trong **vành loa** (`speaker-bezel.stl`, in 2 cái): mặt phẳng Ø72 (mép vát 50° + bo nhỏ, ống non 25°) chứa
  lưới Ø56 (lỗ Ø2,8, bước 5,6, 82 lỗ), ống non 30° làm yên côn lắp **từ trong ra ngoài** (không rút ra từ ngoài được), ống ôm vành loa có 3 chốt ngàm xoay cho vòng ép (xem mục "Giữ loa").
- Bo 82 × 73 × 25 dựng đứng giữa thân, **82 theo Y** (sâu), 73 theo Z, dày 25 theo X; tâm **(0; 0,37; 70)** (đổi 2026-11-08: 82 chia đều 2 nửa vỏ, nâng lên z 70 để trần mái nhọn không support). 2 tấm vẩy đứng (khe 0,3); **chân chặn đầu/cuối bo = chính mái chữ A** (trần hầm bo ở h = 41,3 mm mỗi nửa).
- Tấm bụng (kem, `belly.stl`): mặt trơn, 4 vảy lông chữ V khắc nông 0,6, KHÔNG thủng; yên côn lắp từ trong.
- Mắt: 2 lỗ **Ø35,8** (đổi từ Ø34: gờ tựa kính còn 2,4 mm để không support) hướng theo pháp tuyến, hốc Ø40,6; kính khuếch tán 0,8 + vành 3 (Ø40) lắp từ trong qua **giếng Ø40,6 nghiêng 34°** (khoét vào khối vỏ); **vòng mắt kem Ø54** (`eye-ring.stl`, in 2 cái) **mặt trước PHẲNG** (vuông góc trục mắt, nhô 3 mm tại tâm, dày dần ra mép – in úp mặt phẳng xuống không support), dán ngoài vỏ; sau kính là khoang trống cho LED (WS2812 5 mm hoặc module tròn).
- Mỏ: lỗ Ø18,4, **gờ Ø22** trong (đổi từ Ø24: trần hốc gờ còn 2,2 mm), trục hơi chúc xuống; nút đầu Ø50 (lỗ Ø50,8) + vành giữ **Ø58 vát 45°** trong vỏ, nằm trên **switch MX** (xem mục "3 nút MX").
- Micro: 3 lỗ Ø2 ở trán (**z = 120**, x = −7/0/+7; đổi vì cụm nút đầu chiếm z 125–145), nằm ở **nửa trước**, cách tâm loa > 100 mm.
- Nửa sau: 5 khe 2 × 18 ở lưng, khe cáp 40 × 12 chân lưng (z 3–16, từ mặt ráp ra ngoài; vẩy bo vẫn nối sàn qua mép trên chạm mái).
- Vít: 4 vít M3 từ đáy xuyên **tấm đế** (`base-plate.stl`, dày 4, lõm Ø9 sâu 2,8 dưới miếng cao su Ø16) và sàn vỏ (xuyên 3,4) vào đai ốc lục giác 5,8 thả từ trên vào hốc đỉnh 4 trụ trong vỏ (2 trụ mỗi nửa).

## Giữ loa (2026-11-06) – không vít, ngàm xoay
- **Lý do đổi:** bản đầu 4 vấu nằm sau đáy loa 2,7–4,3 mm (không chạm loa → rè). Bản vít M2.5 bỏ vì Tuan: chỗ quá nhỏ, không có cầu bắt vít.
- **Giữ loa bằng mép trước** (mép dày 5 mm, thân sau mép < Ø39 – Tuan đo):
  - Ron EVA dày 2 mm (vòng ngoài Ø52, lỗ trong **Ø47** – mép trong của mép loa Ø46 (Tuan đo), chừa 0,5 mm/bên để không chạm viền màng loa; vành ron rộng 2,5) giữa mặt sau tấm lưới và mặt loa; khi khóa còn **1,2 mm**.
  - Vòng ép **ngàm xoay** `speaker-ring.stl`: môi lỗ Ø42 đè lên mép loa 5 mm/bên; ống tay ôm ngoài ống ôm vành loa (khe 0,25), mặt trong có **3 rãnh chữ L**.
  - Ống ôm vành loa có **3 chốt** (rộng 4, nhô 1,1, dày 1,5). Xoay khóa **30°**; ron đẩy vòng ép lùi, mặt chốt tì vào vách rãnh → không tự xoay ra.
- **Chống tụt vành loa vào trong:** dán mặt côn vành loa vào lỗ côn vỏ bằng **epoxy** (hoặc CA) – Tuan chốt dán keo.
- **Vành loa:** mép mặt lưới vát 50° + bo nhỏ (in úp mặt lưới không support).
- **In:** `print/print.yaml` bàn `A_speakers` (2 vành loa + 2 vòng ép, Bambu PETG Basic, 0,20 mm, 3 tường, 20 %): PASS, không support, 173 phút, 60,6 g. File `print/plates/A_speakers/A_speakers.3mf`.
- **Gate `gate_owl` PASS:** chi tiết kín 1 khối; loa (mép Ø52 × 5 + thân Ø39) ở vị trí đã khóa không chạm; số khe ngàm; **thử lắp trên hình**: vòng ép lọt rãnh dọc khi đưa vào, xoay hết 30° khi ấn thêm 0,2, nằm khít ở vị trí khóa.

## Lắp loa
> [!IMPORTANT]
> **An toàn (bé < 3 tuổi):** ron và vòng ép nằm trong vỏ, không lộ ra sau khi đóng. Keo epoxy: nơi thoáng, đeo găng, chờ khô hẳn rồi mới cho bé dùng.

1. Đặt ron EVA lên mặt sau tấm lưới của vành loa.
2. Đặt loa vào vành (mặt loa tựa ron).
3. Úp vòng ép lên, xoay cho 3 rãnh dọc trùng 3 chốt, ấn xuống (ép ron), **xoay 30°** tới hết rãnh, buông tay.
4. Thử phát tiếng xem có rè không. Tháo: ấn nhẹ vòng ép, xoay ngược 30°, rút ra.
5. Lặp lại cho loa thứ hai.
6. Dán mặt côn vành loa vào lỗ côn vỏ bằng epoxy (đẩy từ trong ra), chờ khô.

## Khác với spec (cần Claude/Tuan duyệt)
1. **Không có gờ–rãnh dọc đường ráp**: gờ nhô qua mặt ráp nên nửa mang gờ phải in đứng trên gờ, trong khi tai/cánh đặc nằm lơ lửng. Thay bằng 6 lỗ chốt Ø2 sâu 8 mỗi nửa
   (đoạn nhựa 1,75 mm) ở tai, cánh và vành nút. Khớp + khe 0,2 theo bảng khe: chưa có, chưa in thử.
2. **Vít M3 không bắt chéo hai nửa**: tab chéo mặt ráp cũng làm hỏng hướng in → thêm part **tấm đế** kẹp cả hai nửa. Chiều cao tổng không đổi (đế nằm z 0–4).
3. Dáng (vòng chỉnh 2): cánh giọt nước áp sườn, nhô ≤ 6 mm, mép trên z ≈ 112, che nửa trên vành loa; tai chỏm nhọn mềm nghiêng 20°; mắt x = ±36,5; bụng Ø~70 mặt trơn. Tổng 138 × 117,7 × 172,7 (spec 142 × 116 × 175 ± 6; hẹp hơn vì cánh không còn chìa).
4. `eye-diffuser.stl` chỉ chứa 1 cái (gate buộc 1 khối), in 2 lần. Ảnh render dùng STL thật, màu theo design-spec, nhám 0,6.
5. **Mép vành loa** đổi từ bo R8 sang vát 50° + bo nhỏ (in úp mặt lưới, không cần support). Mặt loa lùi 1,3 mm so với bản cũ.

## Kích thước part (đã đặt hướng in, mm)
| Part | X × Y × Z | Hướng in | Ghi chú |
|---|---|---|---|
| shell-front | 134,4 × 168,7 × 56,1 | mặt ráp xuống | mơ; 126,5 g, 4 h 11 |
| shell-back | 134,7 × 168,7 × 56,5 | mặt ráp xuống | mơ; 155,7 g + 2 pod, 5 h 11 (cả bàn C) |
| belly | 87,5 × 87,5 × 16,5 | mặt trước xuống | kem |
| speaker-bezel (×2) | 86 × 86 × 15,0 | mặt lưới xuống | mơ |
| speaker-ring (×2) | 63,3 × 63,3 × 7,7 | đáy vòng xuống, ống tay hướng lên | mơ (nằm trong, không lộ) |
| base-plate | 101,8 × 86,4 × 4,0 | **lật**: mặt sát vỏ (rộng hơn) xuống, lõm Ø9 hướng lên | kem hoặc mơ |
| beak | 22 × 22 × 16,5 | gờ xuống | bơ |
| button-cap | 58 × 58 × 26,8 | mặt trên xuống (vành vát 45° ở trên) | bơ |
| mx-cap-vol-up / -down | 17,2 × 17,2 × 11,5 | đầu Ø17,2 xuống (dấu + / − lõm ở mặt đầu), lỗ chữ thập hướng lên | bơ (vành Ø13,6, côn 45°) |
| **vol-pod-up / -down** (2026-11-08) | 28,4 × 30,3 × 26,8 | **mặt trong xuống** (mặt ngoài cong hướng lên), ô switch mở xuống bàn | mơ (cùng vỏ sau); down = gương của up |
| eye-diffuser (×2) | 40 × 40 × 3,8 | cửa sổ xuống | PETG trắng tự nhiên |
| eye-ring (×2) | 54 × 54 × 9,6 | **mặt trước phẳng xuống**, mặt lõm ôm vỏ hướng lên | kem (không support) |

## Hết support (2026-11-08) – cắt lớp 6 bàn PASS, không support
Kết quả `slice.py print/print.yaml`: A 172 ph / 60,6 g, B 263 ph / 128,4 g, C 295 ph / 151,9 g, D 97 ph / 48,8 g, E 51 ph / 27,0 g, F 8 ph / 3,4 g – tổng 14 h 44, 420,1 g (trước: 12 h 04, 297,7 g – vỏ dày hơn vì trần đặc, hạ infill nếu cần).
Sửa hình học (giữ ngoại hình + các khe lắp loa / ngàm xoay / ron / bo 82 × 73 × 25 – gate kiểm):
1. **Khoang trong vỏ**: bỏ vòm elipsoid (trần ngang ~97 mm – nguyên nhân support 3797 + 11443 mm²). Thay bằng khoang giao (∩ khoang cũ) của: **mái chữ A** dọc theo z (rộng 48 ở mặt ráp, dốc 45° mỗi bên), **hầm bo** (thành đứng ±12,8 + mái chữ A trên đầu cuối bo), **đường hầm loa** (tiết diện giọt nước: tròn Ø41 + chóp 45° – lắp thân loa Ø39), **ống trụ bụng** (tấm bụng lắp từ trong; ống Ø88,8 + vát 45° ở đỉnh). Mọi trần nghiêng ≥ 45° hoặc đỉnh phẳng ≤ 2 mm.
2. Yên côn tấm bụng: nửa góc 30° → **10°** (ống trụ bụng rộng 44 chạm mái / giếng kính tạo răng nhọn 0,01 mm² làm slicer báo "floating regions"; 10° vẫn giữ tấm bụng từ ngoài: sau rộng hơn trước 2,9 mm).
3. **Trụ vít** ×4: thêm khối xuống mặt ráp (hình bia mộ) – không còn trụ tròn treo; hốc đai ốc vẫn thả từ trên vào.
4. Ống mắt: vành đầu ống 2,3 mm, gờ tựa kính 2,4 mm (lỗ mắt Ø35,8), giếng Ø40,6 xiên 34° cho kính lắp từ trong; hốc vành mỏ: vành trần 2,2 mm; **lỗ nút đầu** dạng giọt nước (chóp 45°, lỗ ngang không treo; chóp lộ thành rãnh nhọn nhỏ ở mép lỗ trước/sau đầu).
5. Đế `base-plate`: in lật. Vòng mắt: mặt trước phẳng. Nắp nút đầu: vành vát 45°.
6. Chốt định vị Ø2 dời (±56, 92) → (±34, 130) (chỗ cũ trùng cụm nút âm lượng; giữ nguyên chỗ mới).
7. 2026-11-08 (sau): bỏ đệm + lỗ nút âm lượng hai bên đầu (commit 25accf3); nút âm lượng về **lưng** bằng cụm rời `vol-pod` (mục dưới). Cắt lớp lại: A 171 ph / 60,6 g, B 251 ph / 126,5 g, C 311 ph / 155,7 g, D 96 ph / 48,8 g, E 50 ph / 26,9 g, F 8 ph / 3,4 g – **tổng 14 h 51, 423,2 g, 6 bàn PASS, không support** (v2: C 312 ph / 157,0 g).
Lưu ý: hai nửa vỏ có khối đặc dày (mái chữ A) – hộp bo vẫn lọt, nhưng **dây loa / LED phải đi qua đường hầm loa + giếng mắt** (chưa vẽ rãnh đi dây riêng – TODO nếu cần). Công cụ kiểm nhanh: `tools/print/scripts/printability.py out`; build nhanh bỏ ảnh: đặt biến môi trường `OWL_FAST=1`.

## 3 nút MX (2026-11-08, ý tưởng clicker – thay công tắc 6 × 6)
Số lắp ghép **lấy từ fit-library** (`tools/model-study/fit-library/fits.json`): `catpaw/mx-socket` (lỗ vuông 14,00 press, sâu 8,58 từ miệng, rãnh V 45°: 1,94 → 3,44 dưới miệng, sâu nhất 2,69, rộng 15,44) và `catpaw/mx-keycap-cross` (lỗ chữ thập 4,19 × 1,25). Ghi vào `out/owl-params.json` mục `mx`; file lắp ráp: `out/asm/mx-switch-<talk|vol_up|vol_down>.stl` (khối giả switch), `mx-cap-vol-up/-down.stl`, `button-cap.stl`.
- **Lỗ switch xoay 45° quanh trục** (hình thoi) – như mẫu catpaw – nên trần lỗ là mái 45° (in không support). Lỗ nằm **trên đường ráp**: mỗi nửa vỏ giữ nửa lỗ → **kẹp switch + nắp khi đóng vỏ** (lắp từ trong trước khi đóng; bé < 3 tuổi không rút nắp ra từ ngoài được).
- **talk** (KEY4, GPIO23): dưới nắp nút đầu, trục z, miệng lỗ z = 133,6. Nắp `button-cap`: vành Ø58 vát 45° tì vào yên côn của vỏ (lỗ vỏ Ø50,8, nắp Ø50, vành hơn lỗ **3,6 mm/bên**), mặt dưới có lỗ chữ thập 4,19 × 1,25 sâu 3,6 cắm vào chân MX.
- **vol_up** (KEY5, GPIO18) ở +x và **vol_down** (KEY6, GPIO5) ở −x – **ở LƯNG** (Tuan 2026-11-08, bản 25accf3 tự ý đưa lên hai bên đầu, đã bỏ). Mỗi nút là **cụm rời `vol-pod-up/-down`** (2 pod giống nhau, down = gương) lắp **từ trong vỏ** qua cửa sổ ở lưng, giữ bằng **2 vít M2.5 mỗi pod bắt từ trong vỏ** (giấu vít):
  - **Vị trí:** tâm x = ±24, **z = 103**, trục +y. Lý do z = 103: vách lưng ở đó nghiêng ~23° so với phương thẳng đứng (≤ 25°); cửa sổ (z 93,1 → 113,7) nằm trên 5 khe thoát nhiệt (z ≤ 91) và dưới tai/nút đầu; chốt định vị (±34, 130) không vướng. **|x| = 24, không phải 16 như spec** vì hộp bo 25 × 82 × 73 (x ±12,5, y tới 41,4, z tới 106,5) chạm switch ở x = 16; 24 còn giúp cửa sổ cách thành khe bo (x = 12,8) tới 1,8 mm – ở x = 22 (cách 0,2 mm) máy cắt lớp báo "floating cantilever" ở trần khe bo. 2 tâm nút cách nhau 48 mm.
  - **Nắp** `mx-cap-vol-up/-down`: đầu Ø17,2 + dấu +/− lõm, cổ Ø8, **vành Ø13,6** (côn 45°, hơn khe cổ Ø9,0 **2,3 mm/bên**, < 14,00 nên không cần luồn qua lỗ ép). Nắp nhô ra ngoài lưng 2,7 mm ở tâm (mặt pod thấp hơn mặt lưng 1,0 mm).
  - **Pod** (v2, 2026-11-08): **mặt ngoài cong theo vỏ** (cắt bằng chính mặt ngoài vách lưng) → liền mạch với vỏ; quanh mỗi nắp có **lõm Ø18,0** xuống mặt phẳng tựa (nắp Ø17,2 + 0,4/bên). Tấm tựa dày 3 mm có **rãnh cổ nắp 9,0** hở về mép dưới + **yên côn 45°** (nắp tì côn, như nút đầu); kênh vai switch 15,8; vát 45° → ô switch **14,00 (press)** + rãnh V catpaw, mở ra mặt trong (chân quay vào trong để hàn). Switch không xoay 45°. Cặp nắp + switch **trượt vào pod từ mép dưới**; khi pod vào vỏ, thành dưới cửa sổ cao hơn mặt phẳng tựa chặn đầu nắp → nắp không trượt ra, không rút ra từ ngoài. Khe pod – cửa sổ 0,3 mỗi bên (cửa sổ 19,8 × 20,55). **In mặt TRONG xuống bàn** (mặt ngoài cong hướng lên), không support.
  - **Độ liền mạch (đo thật):** `vol_pod.flush_max_dev` = **0,21 mm** (BVH raycast từ ngoài vào, 328 điểm dọc viền cửa sổ 2 pod, so mặt pod với mặt vỏ cách viền 0,35 mm; chênh chủ yếu do độ dốc × khe 0,3). Nắp nhô **3,2 mm** (`cap_protrusion`) so với mặt lưng ở tâm nút (≤ 4).
  - **Giữ pod bằng vít M2.5 tự ren, bắt TỪ TRONG vỏ ra (giấu vít):** mỗi pod có "tai" ở phía trên (z 113–124, trên hộp bo): khối đặc dưới trần mái chữ A, mặt trên dốc 45° song song trần (khe 0,4), 2 lỗ thông **Ø2,8** + hốc đầu vít **Ø5,0** mở ra mặt trong (đáy hốc cách mặt tai 4,0). Vít xuyên tai rồi ăn vào **lỗ mồi Ø2,2 sâu 6,2** khoan thẳng vào khối trần đặc (không thủng ra mặt ngoài: thành ngoài còn ≥ 2,2 mm, `vol_pod.screws.info`). **Vít M2.5 × 10, ăn ren 5,6 mm** (≥ 5). Tua-vít vào từ mặt ráp khi vỏ sau mở (cột trống bên dưới tai).
  - **Khác đề xuất "trụ kín":** không dựng trụ rời từ trần vì trụ treo dưới trần có đáy phẳng phải in "lơ lửng" (slicer báo floating regions, đã thử) – dùng chính khối đặc của trần mái làm trụ, tai pod lấp khoảng trống bên dưới. Hai lỗ ở x = 14,8 và 8,8 (cách nhau 7,6 mm), cùng M2.5 × 10 (hốc đầu vít sâu khác nhau: 2,1 và 8,1).
  - **Lắp:** (1) cắm nắp vào chân chữ thập switch (2) trượt cặp nắp + switch vào kênh pod từ mép dưới (ô 14,00 ép chặt) (3) hàn dây song song KEY5 / KEY6 trên bo vào chân switch – **rút USB trước, mỏ hàn nóng, điện 3,3 V** (4) đặt pod từ trong vào cửa sổ ở lưng, nắp ra ngoài (5) vặn **2 vít M2.5 × 10** từ mặt ráp, **vừa tay – siết quá sẽ toét ren trong nhựa**. Xem `out/vol-pod.png`, `out/owl-back.png`.
  - **Vít:** M2.5 × 10 tự ren (2 vít / pod, 4 vít tổng); lỗ mồi 2,2 theo fit-library `mec1/tipflow m2.5-self-tap`, lỗ thông 2,8 theo `mec1/m2.5-clearance`.
  - **Giả định / TODO:** chưa in thử lực press 14,00, ren tự cắt trong PETG, đầu vít thật (Ø5,0 theo yêu cầu).
- Nắp **không chạm vỏ ở vị trí nghỉ** (khe 0,1 ở yên côn, nâng 0,2 mm lên phía trên); gate kiểm.
- **Ổ switch + lỗ chữ thập: số đã kiểm chứng**, giống hệt `maker/switch-clicker` (cùng fit-library `catpaw/mx-socket` 14,00 sâu 8,58 + rãnh V,
  `catpaw/mx-keycap-cross` 4,19 × 1,25 – mẫu Cat Paw Clicker tác giả in + chạy thật trên Bambu A1 + PETG Basic, cùng máy/nhựa của STLab).
- **Còn giả định – chiều cao switch phía trên mặt ổ** (switch-clicker cũng chưa đo, form-spec ghi TODO): thân trên 15,6 × 15,6 cao 3,0 + chân chữ thập 3,6
  (= 6,6 trên mặt), thân dưới 5,0, chân 3,3; nắp chạy **~2,4 mm** (chạm thân switch), chân chữ thập cắm vào nắp 1,2 mm lúc nghỉ.
  Nếu switch thật cao/thấp hơn thì nắp nhô/lún tương ứng → đo 1 số khi có switch: **từ vai ngàm (mặt tấm 14,00) tới đỉnh chân chữ thập**.
- **Dây:** hàn 2 chân mỗi switch **song song** nút KEY4 / KEY5 / KEY6 trên bo A1S (GPIO23 / GPIO18 / GPIO5 xuống GND); dây xuống khoang qua cửa sổ đáy lỗ (thoi 9 mm). An toàn: rút USB trước khi hàn; điện 3,3 V (không có điện áp cao); mỏ hàn nóng; dây đủ dài để mở 2 nửa vỏ, cố định bằng keo nến; nắp nút bị giữ trong vỏ (vành trong lớn hơn lỗ vỏ).

## Chưa chắc / TODO
- Độ dày, cao linh kiện bo Audio Kit; vị trí USB: không có nguồn → khe cáp rộng; bo giữ bằng ray + chân chặn phía trước, **sau bo chưa có chốt giữ** (gate cấm vật chạm khối 82 × 73 × 25) → dùng xốp/keo nóng.
- Switch MX (xem mục 3 nút MX): ổ 14,00 + rãnh V + chữ thập đã kiểm chứng (giống switch-clicker); chỉ còn chiều cao phía trên mặt ổ là giả định. Thân loa sau mép < Ø39 (Tuan đo 2026-11-06), lọt lỗ vòng ép Ø42.
- fit-library chưa có mục M3 / ống non: **chưa in thử** mọi khe (0,3 hốc linh kiện, 0,3 yên côn, 0,4 nút).
- Đáy phẳng vát 0,8 mm chưa làm. Khắc ▲ và logo STLAB chưa làm.

## File CAD để đo (SolidCraft, 2026-11-06)
- `out/owl-assembly.sc`: mở bằng SolidCraft, 24 chi tiết, mỗi chi tiết một component **đúng vị trí lắp**, đơn vị mm (gồm loa và bo mạch giữ chỗ `*-dummy`, không in).
- Sinh lại: chạy `build_owl.py` (Blender) rồi `python export_cad.py out`.
- Chi tiết là thân lưới: đo bằng Measure, bắt đỉnh/cạnh. Vành loa và vòng ép có thể chuyển sang mặt phẳng/trụ thật bằng Convert Mesh để đo dễ hơn.

## Bản ESP32-S3 (1 loa ở bụng, mic ở trán chính giữa, 1 nút, 2026-11-12)

Sinh bằng `build_owl_s3.py` (Blender 5.2 bpy), xuất ra `out-s3/` (STL in, `asm/` vị trí lắp, `owl-params.json`, `owl-assembly.sc`, ảnh
`owl-preview/exploded/front/back.png`). Gate: `gate_owl_s3.py`. Bàn in: `print/print-s3.yaml` → `print/plates-s3/` (PETG Bambu A1 0,20, KHÔNG support).
Quyết định Tuan 2026-11-12: chỉ 1 nút (nói, GPIO 1), cáp USB-C thẳng, chưa có TPU → mọi thứ in PETG, không dùng tấm EVA.

### Vị trí cuối (mm; +Z lên, mặt trước −Y, mặt ráp y = 0,37)
| Linh kiện | Tâm | Hộp giữ chỗ | Ghi chú |
|---|---|---|---|
| Loa Ø52 × 26 | (0; −42,8; 48) | trục Y, mặt ra −Y | mặt loa ÁP SÁT vành; vành/vòng ép đặt ở y −41,6 (như bản A1S, chỉ đổi trục) |
| Ampli MAX98357A | (0; −12; 18) | 22 × 22 × 10 (x, y, z) | khay `amp-tray.stl` đặc từ sàn z = 4 lên đáy module z = 12,8; 2 vách bên cao 9 |
| Bo ESP32-S3 | (0; 8,7; 34) | 29 × 72 × 16 (x, y, z) | NẰM NGANG, dọc theo Y; mặt cổng USB y = 44,7 hướng +y (lưng), đầu trước y = −27,3 |
| Lỗ cáp USB-C | (0; 50,7; 34) | 14 × 9, R2 | xuyên phần đặc sau mái hốc dài 11,4; thẳng hàng cổng USB (lệch 0) |
| Mic INMP441 | (0; −34,5; 115,4) | 17 × 8 × 17 | trán, x = 0 giữa 2 mắt trên mỏ, hướng −Y; 3 lỗ Ø2 tại x −1,5/0/1,5, z 116,4 (ống dẫn âm cao hơn tâm module 1,0 để tránh mặt sau mỏ) |
| Nút nói MX (GPIO 1) | (0; 0,37; TALK_RIM) | | đỉnh đầu dưới nắp Ø50, giữ nguyên |

**Bo S3 nằm ngang:** hốc đúng bo (x ±14,8, z 25,8..42,2) khoét vào phần đặc sau; mái hốc hình chữ A (dốc 45°, đỉnh cao hơn chân mái 8,2) nên in không support.
Hai vách ray (x ±14,8..17,2, dựng từ sàn) + 2 gác đỡ cạnh PCB (x 12,5..14,8, z 24..25,8, dày 1,8) + 2 khối chặn đầu trước (không USB). Lắp bo từ trên xuống trước khi đóng 2 nửa.
Bo chạm sàn hốc ở phần đặc phía sau. Hộp 29 × 72 × 16 là chỗ chừa, gồm cả chân header: TODO đo lại bo clone N16R8 thật.

**Mic + ống dẫn âm (PETG, không ron):** nắp kẹp `mic-clamp.stl` trượt từ DƯỚI vào 2 rãnh (tường rãnh dựng từ mặt ráp tới vách trán, in đứng), giữ bằng ma sát (khe 0,15/bên).
Tấm kẹp ép module từ phía sau; phía trước module có yoke + ỐNG DẪN ÂM OD 7 / ID 3 dài từ mặt module tới vách. Đầu ống cắm vào GỜ LÕM Ø7,3 sâu 1,0 trên mặt trong vách trán
(`mic.seal {labyrinth, depth 1.0, clearance 0.15}`), cách đáy gờ 0,3. 3 lỗ Ø2 xuyên vách trong lòng gờ (2 lỗ biên dời vào ±1,5 nên 3 lỗ nối thành rãnh dài ~5).
Muốn kín hơn: chấm keo nóng hoặc silicone quanh mép ống. Mỏ khoét nhẹ mặt sau chỗ ống đi qua (`beaknotch`).
TODO: kiểm mặt lỗ âm + hướng header của INMP441 thật (ống giả định lỗ âm ở giữa module); nắp kẹp chỉ giữ bằng ma sát, tụt thì chấm keo nóng.

**Loa không ron (PETG):** mép loa ì thẳng vào vành. Vòng ép ngàm xoay (3 chốt, xoay 30°, số của bản A1S) có 4 LẪY LÒ XO PETG
(`speaker_clamp.petg_spring {n 4, t 1.2, len 8.5, width 3.5, preload 1.5}`) đè lên mặt sau mép loa: thanh dốc 45° rồi đoạn phẳng, gờ tròn R1 ở đầu tự do.
Mô hình lắp (`asm/speaker-ring.stl`) vẽ lẫy ở trạng thái đã ép; STL in (`speaker-ring.stl`) là trạng thái tự do. Rãnh ron giữ nguyên (`gasket_slot_kept: true`):
có TPU thì in ron Ø52/Ø46 × 2 TPU 95A (cuộn ngoài, không qua AMS lite), lẫy vẫn đè được. TODO: thử lực lẫy trên loa thật (tính tay ~1–3 N mỗi lẫy).

**Khay ampli:** dán keo nóng xuống sàn (Tuan chọn), không cần vít.

### Vật tư (bản S3)
1 switch MX (nút nói, GPIO 1) + nắp `button-cap`, keo nóng (khay ampli, nắp mic nếu lỏng), cáp USB-C THẲNG, loa 4 Ω 3 W Ø52 × 26, ESP32-S3 N16R8, INMP441, MAX98357A.
Không còn tấm EVA. Đã bỏ: 2 nút âm lượng (GPIO 39/40), vol-pod, nắp mx-cap-vol, lỗ cửa sổ ở lưng (vỏ lưng liền, giữ khe nhiệt).

### Bàn in S3 (PASS cả 6, không support)
A 1.5 h 23 g; B 4.6 h 143 g; C 5.1 h 169 g; D 1.2 h 37 g; E 0.7 h 24 g; F 0.1 h 2 g.

### Chưa chắc / TODO
- Kích thước thật bo clone ESP32-S3 N16R8 2 cổng USB-C (đang chừa 72 × 29 × 16).
- Hướng lỗ âm INMP441; kín tiếng mic chỉ bằng gờ lõm PETG (chưa đo).
- Lẫy lò xo PETG: lực thực tế + nứt mỏi chưa thử.
- Lệch spec đã báo: mic z 115,4 / y −34,5 (trần hốc trán z = 124; vách trán cong dạng mái 45°); loa y −42,8 (mặt loa ì vành).
