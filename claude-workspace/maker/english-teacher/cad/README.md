# CAD vỏ Cú Bông – bản 1 (ESP32-A1S Audio Kit, 2 loa)

Sinh bằng `build_owl.py` (Blender 5.2 bpy, boolean MANIFOLD). Gate: `gate_owl.py` (xem `spec-owl.md`). Ảnh duyệt: `out/owl-preview.png`, `out/owl-exploded.png`.
Hệ lắp ráp: mm, +Z lên, mặt trước −Y; mặt ráp hai nửa là mặt phẳng y = 0,37. Mọi số đặt ở đầu `build_owl.py`, ghi vào `out/owl-params.json`.

## Bố trí (đổi 2026-11-05: 2 loa trái + phải)
- 2 loa Ø52 × 26, trục x, mặt ra ngoài, tâm (±51,5; 0; 46), hốc Ø52,6. Mỗi loa nằm trong **vành loa** (`speaker-bezel.stl`, in 2 cái): mặt phẳng Ø72 (mép vát 50° + bo nhỏ, ống non 25°) chứa
  lưới Ø56 (lỗ Ø2,8, bước 5,6, 82 lỗ), ống non 30° làm yên côn lắp **từ trong ra ngoài** (không rút ra từ ngoài được), ống ôm vành loa có 3 vấu M2.5 bắt vòng ép (xem mục "Giữ loa").
- Bo 82 × 73 × 25 dựng đứng giữa thân, **82 theo Y** (sâu), 73 theo Z, dày 25 theo X; tâm (0; 8; 60). 2 tấm ray đứng (khe 0,3) + chân chặn trước.
- Tấm bụng (kem, `belly.stl`): mặt trơn, 4 vảy lông chữ V khắc nông 0,6, KHÔNG thủng; yên côn lắp từ trong.
- Mắt: 2 lỗ Ø34 hướng theo pháp tuyến, ống đỡ + hốc Ø40,6; kính khuếch tán 0,8 + vành 3 (Ø40) lắp từ trong; **vòng mắt kem Ø54** (`eye-ring.stl`, in 2 cái) mỏng 3 mm ôm sát mặt cong, dán ngoài vỏ (không lắp từ trong); sau kính là khoang trống cho LED (WS2812 5 mm hoặc module tròn).
- Mỏ: lỗ Ø18,4, gờ Ø24 trong, trục hơi chúc xuống; nút Ø50 hành trình ~2 mm, vành giữ Ø58 trong, chân ép Ø16 lên công tắc 6 × 6 (giá công tắc ở nửa sau, đỉnh z = 136,3).
- Micro: 3 lỗ Ø2 ở trán (z = 132), nằm ở **nửa trước** (trán thuộc nửa trước), cách tâm loa > 100 mm.
- Nửa sau: 5 khe 2 × 18 ở lưng, khe cáp 40 × 12 chân lưng (z 4–16, y ≥ 38).
- Vít: 4 vít M3 từ đáy xuyên **tấm đế** (`base-plate.stl`, dày 4, lõm Ø9 sâu 2,8 dưới miếng cao su Ø16) và sàn vỏ (xuyên 3,4) vào đai ốc lục giác 5,8 thả từ trên vào hốc đỉnh 4 trụ trong vỏ (2 trụ mỗi nửa).

## Giữ loa (2026-11-06)
- **Lý do đổi:** bản cũ 4 vấu nằm sau đáy loa 2,7–4,3 mm (không chạm loa → rè); chỉ bám được nếu đáy loa to Ø52; vành loa không bị chặn tụt vào trong.
- **Mới:** giữ loa bằng **mép trước** (mép loa dày 5 mm).
  - Ron EVA dày 2 mm (vòng ngoài Ø52, trong ~Ø46 – tự cắt) giữa mặt sau tấm lưới và mặt loa, ép còn 1,5 mm.
  - Vòng ép `speaker-ring.stl` (in rời; dày 2,4, lỗ giữa Ø42 (đè lên mép loa 5 mm/bên), 3 tai) ép mặt sau mép loa.
  - 3 vít M2.5 × 8 tự ren qua lỗ Ø2,8 của vòng ép vào 3 vấu trên ống ôm vành loa (lỗ mồi Ø2,3 sâu 6; lỗ theo fit-library đo mẫu cộng đồng). Mỗi loa 3 vít → tổng 6 vít M2.5 × 8.
- **Chống tụt vào trong:** vành loa chưa có khóa cơ khí → khi lắp, dán mặt côn vành loa vào lỗ côn vỏ bằng epoxy hoặc keo CA. Loa vẫn tháo được từ bên trong nhờ vòng ép.
- **Vành loa:** mép mặt lưới đổi từ bo R8 sang vát 50° + bo nhỏ (in úp mặt lưới không cần support). Mặt loa lùi 1,3 mm so với bản cũ.
- **In:** `print/print.yaml` bàn `A_speakers` (2 vành loa + 2 vòng ép, Bambu PETG Basic, 0,20 mm, 3 tường, 20 %), cắt lớp PASS, không support, 169 phút, 53,4 g. File: `print/plates/A_speakers/A_speakers.3mf`. STL sinh từ `cad/out`, chép thành `-l`/`-r` trong `print/stl`.
- **Gate `gate_owl` PASS:** kiểm thêm `speaker-bezel`, `speaker-ring` (kín, 1 khối), loa mô hình mép Ø52 × 5 + thân Ø39 không chạm, số khe kẹp.

## Lắp loa
> [!IMPORTANT]
> **An toàn (bé < 3 tuổi):** vít, ron và vòng ép nằm trong vỏ, không lộ ra ngoài sau khi đóng.

1. Đặt ron EVA lên mặt sau tấm lưới của vành loa.
2. Đặt loa vào vành (mặt loa tựa ron).
3. Đặt vòng ép (`speaker-ring`) lên mặt sau mép loa.
4. Vặn đều 3 vít M2.5 × 8 qua lỗ Ø2,8 của vòng ép vào 3 vấu trên ống ôm vành loa.
5. Lặp lại bước 1–4 cho loa thứ hai.
6. Trước khi đóng vỏ: dán mặt côn vành loa vào lỗ côn vỏ bằng epoxy hoặc keo CA.

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
| shell-front | 134,4 × 168,7 × 56,1 | mặt ráp xuống | mơ |
| shell-back | 134,7 × 168,7 × 56,5 | mặt ráp xuống | mơ |
| belly | 87,5 × 87,5 × 16,5 | mặt trước xuống | kem |
| speaker-bezel (×2) | 86 × 86 × 15,0 | mặt lưới xuống | mơ |
| speaker-ring (×2) | 61 × 62,5 × 2,4 | mặt ép xuống | mơ (nằm trong, không lộ) |
| base-plate | 101,8 × 86,4 × 4,0 | phẳng | kem hoặc mơ |
| beak | 24 × 24 × 16,5 | gờ xuống | bơ |
| button-cap | 58 × 58 × 25,2 | mặt trên xuống | bơ |
| eye-diffuser (×2) | 40 × 40 × 3,8 | cửa sổ xuống | PETG trắng tự nhiên |
| eye-ring (×2) | 54 × 54 × 8,3 | trục mắt thẳng đứng, mép ngoài xuống | kem; **cần support/brim** (vỏ mỏng cong) |

## Vùng nghi cần support / kiểm khi cắt lớp
- Trần trong nửa trước và nửa sau (mái vòm khi in mặt ráp xuống): cầu rộng > 15 mm ở đỉnh vòm → có thể phải tô support cục bộ trong Bambu Studio.
- Lỗ lớn của yên côn vành loa/bụng ở nửa vỏ: mép lỗ nghiêng ≤ 30°, thường không cần.
- Tai/cánh đặc in mặt cắt xuống bàn: bán elip úp, ổn; vành nút Ø58 chìa 4 mm (cầu ngắn).
- Hốc đai ốc lục giác (trần cầu 6 mm) và lỗ xuyên Ø3,4 nằm dọc theo trục in, ổn; ống mắt nghiêng theo pháp tuyến ~30°: kiểm.
- Vành loa in úp mặt lưới, không support (mép vát 50°); vòng ép in không support (print.yaml, cắt lớp PASS). Chưa in thật.

## Chưa chắc / TODO
- Độ dày, cao linh kiện bo Audio Kit; vị trí USB: không có nguồn → khe cáp rộng; bo giữ bằng ray + chân chặn phía trước, **sau bo chưa có chốt giữ** (gate cấm vật chạm khối 82 × 73 × 25) → dùng xốp/keo nóng.
- Chiều cao công tắc tactile (giả định 4,3): TODO đo. Thân loa sau mép < Ø39 (Tuan đo 2026-11-06), lọt lỗ vòng ép Ø42.
- fit-library chưa có mục M3 / ống non: **chưa in thử** mọi khe (0,3 hốc linh kiện, 0,3 yên côn, 0,4 nút).
- Đáy phẳng vát 0,8 mm chưa làm. Khắc ▲ và logo STLAB chưa làm.

## File CAD để đo (SolidCraft, 2026-11-06)
- `out/owl-assembly.sc`: mở bằng SolidCraft, 17 chi tiết, mỗi chi tiết một component **đúng vị trí lắp**, đơn vị mm (gồm loa và bo mạch giữ chỗ `*-dummy`, không in).
- Sinh lại: chạy `build_owl.py` (Blender) rồi `python export_cad.py out`.
- Chi tiết là thân lưới: đo bằng Measure, bắt đỉnh/cạnh. Vành loa và vòng ép có thể chuyển sang mặt phẳng/trụ thật bằng Convert Mesh để đo dễ hơn.
