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
| shell-front | 134,4 × 168,7 × 56,1 | mặt ráp xuống | mơ; 128 g, 4 h 23 |
| shell-back | 134,7 × 168,7 × 56,5 | mặt ráp xuống | mơ; 152 g, 4 h 55 |
| belly | 87,5 × 87,5 × 16,5 | mặt trước xuống | kem |
| speaker-bezel (×2) | 86 × 86 × 15,0 | mặt lưới xuống | mơ |
| speaker-ring (×2) | 63,3 × 63,3 × 7,7 | đáy vòng xuống, ống tay hướng lên | mơ (nằm trong, không lộ) |
| base-plate | 101,8 × 86,4 × 4,0 | **lật**: mặt sát vỏ (rộng hơn) xuống, lõm Ø9 hướng lên | kem hoặc mơ |
| beak | 22 × 22 × 16,5 | gờ xuống | bơ |
| button-cap | 58 × 58 × 26,8 | mặt trên xuống (vành vát 45° ở trên) | bơ |
| mx-cap-vol-up / -down | 17,2 × 17,2 × 11,5 | đầu Ø17,2 xuống (dấu + / − lõm ở mặt đầu), lỗ chữ thập hướng lên | bơ |
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
6. Chốt định vị Ø2 dời (±56, 92) → (±34, 130) (chỗ cũ trùng cụm nút âm lượng).
Lưu ý: hai nửa vỏ có khối đặc dày (mái chữ A) – hộp bo vẫn lọt, nhưng **dây loa / LED phải đi qua đường hầm loa + giếng mắt** (chưa vẽ rãnh đi dây riêng – TODO nếu cần). Công cụ kiểm nhanh: `tools/robotics-cad/scripts/printability.py out`; build nhanh bỏ ảnh: đặt biến môi trường `OWL_FAST=1`.

## 3 nút MX (2026-11-08, ý tưởng clicker – thay công tắc 6 × 6)
Số lắp ghép **lấy từ fit-library** (`tools/model-study/fit-library/fits.json`): `catpaw/mx-socket` (lỗ vuông 14,00 press, sâu 8,58 từ miệng, rãnh V 45°: 1,94 → 3,44 dưới miệng, sâu nhất 2,69, rộng 15,44) và `catpaw/mx-keycap-cross` (lỗ chữ thập 4,19 × 1,25). Ghi vào `out/owl-params.json` mục `mx`; file lắp ráp: `out/asm/mx-switch-<talk|vol_up|vol_down>.stl` (khối giả switch), `mx-cap-vol-up/-down.stl`, `button-cap.stl`.
- **Lỗ switch xoay 45° quanh trục** (hình thoi) – như mẫu catpaw – nên trần lỗ là mái 45° (in không support). Lỗ nằm **trên đường ráp**: mỗi nửa vỏ giữ nửa lỗ → **kẹp switch + nắp khi đóng vỏ** (lắp từ trong trước khi đóng; bé < 3 tuổi không rút nắp ra từ ngoài được).
- **talk** (KEY4, GPIO23): dưới nắp nút đầu, trục z, miệng lỗ z = 133,6. Nắp `button-cap`: vành Ø58 vát 45° tì vào yên côn của vỏ (lỗ vỏ Ø50,8, nắp Ø50, vành hơn lỗ **3,6 mm/bên**), mặt dưới có lỗ chữ thập 4,19 × 1,25 sâu 3,6 cắm vào chân MX.
- **vol_up** (KEY5, GPIO18) ở +x và **vol_down** (KEY6, GPIO5) ở −x: 2 nắp nhỏ `mx-cap-vol-up/-down.stl` (đầu Ø17,2 + dấu + / − **lõm** 0,8 mm, cổ Ø8 qua lỗ vỏ Ø9, vành Ø14,4 vát 45° tì yên côn: hơn lỗ **2,7 mm/bên**) – đặt ở **hai bên đầu** (z = 117, đệm Ø20 nhô ≤ 3 mm), **không ở lưng** như ý ban đầu: lỗ trục y ở lưng khi in mặt ráp xuống có trần kín và không có đường lắp switch + nắp từ trong; trên đường ráp thì lắp được. Khối đệm đặc |x| 38–55,6 quanh nút.
- Nắp **không chạm vỏ ở vị trí nghỉ** (khe 0,1 ở yên côn, nâng 0,2 mm lên phía trên); gate kiểm.
- **Giả định (TODO đo switch thật):** thân switch trên mặt 6,6 mm (15,6 × 15,6 cao 3,0 + chân chữ thập cao 3,6), thân dưới 5,0, chân 3,3; hành trình MX ~ 4,0 mm: nắp chỉ chạy **~2,4 mm** (chạm thân switch) – MX bật ở ~2,0 mm nên đủ; chân chữ thập cắm vào nắp 1,2 mm lúc nghỉ. Chưa in thử, chưa kiểm lực ép lỗ 14,00 (press) với PETG.
- **Dây:** hàn 2 chân mỗi switch **song song** nút KEY4 / KEY5 / KEY6 trên bo A1S (GPIO23 / GPIO18 / GPIO5 xuống GND); dây xuống khoang qua cửa sổ đáy lỗ (thoi 9 mm). An toàn: rút USB trước khi hàn; điện 3,3 V (không có điện áp cao); mỏ hàn nóng; dây đủ dài để mở 2 nửa vỏ, cố định bằng keo nến; nắp nút bị giữ trong vỏ (vành trong lớn hơn lỗ vỏ).

## Chưa chắc / TODO
- Độ dày, cao linh kiện bo Audio Kit; vị trí USB: không có nguồn → khe cáp rộng; bo giữ bằng ray + chân chặn phía trước, **sau bo chưa có chốt giữ** (gate cấm vật chạm khối 82 × 73 × 25) → dùng xốp/keo nóng.
- Kích thước switch MX (xem mục 3 nút MX): giả định, TODO đo switch thật; lực press lỗ 14,00 chưa in thử. Thân loa sau mép < Ø39 (Tuan đo 2026-11-06), lọt lỗ vòng ép Ø42.
- fit-library chưa có mục M3 / ống non: **chưa in thử** mọi khe (0,3 hốc linh kiện, 0,3 yên côn, 0,4 nút).
- Đáy phẳng vát 0,8 mm chưa làm. Khắc ▲ và logo STLAB chưa làm.

## File CAD để đo (SolidCraft, 2026-11-06)
- `out/owl-assembly.sc`: mở bằng SolidCraft, 22 chi tiết, mỗi chi tiết một component **đúng vị trí lắp**, đơn vị mm (gồm loa và bo mạch giữ chỗ `*-dummy`, không in).
- Sinh lại: chạy `build_owl.py` (Blender) rồi `python export_cad.py out`.
- Chi tiết là thân lưới: đo bằng Measure, bắt đỉnh/cạnh. Vành loa và vòng ép có thể chuyển sang mặt phẳng/trụ thật bằng Convert Mesh để đo dễ hơn.
