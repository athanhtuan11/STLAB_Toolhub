# CAD vỏ Cú Bông – bản 1 (ESP32-A1S Audio Kit, 2 loa)

Sinh bằng `build_owl.py` (Blender 5.2 bpy, boolean MANIFOLD). Gate: `gate_owl.py` (xem `spec-owl.md`). Ảnh duyệt: `out/owl-preview.png`, `out/owl-exploded.png`.
Hệ lắp ráp: mm, +Z lên, mặt trước −Y; mặt ráp hai nửa là mặt phẳng y = 0,37. Mọi số đặt ở đầu `build_owl.py`, ghi vào `out/owl-params.json`.

## Bố trí (đổi 2026-11-05: 2 loa trái + phải)
- 2 loa Ø52 × 26, trục x, mặt ra ngoài, tâm (±49,8; 0; 46), hốc Ø52,6. Mỗi loa nằm trong **vành loa** (`speaker-bezel.stl`, in 2 cái): mặt phẳng Ø72 (mép bo R8, ống non 25°) chứa
  lưới Ø56 (lỗ Ø2,8, bước 5,6, 82 lỗ), ống non 30° làm yên côn lắp **từ trong ra ngoài** (không rút ra từ ngoài được), ống ôm loa + 4 vấu mềm giữ vành loa phía sau.
- Bo 82 × 73 × 25 dựng đứng giữa thân, **82 theo Y** (sâu), 73 theo Z, dày 25 theo X; tâm (0; 8; 60). 2 tấm ray đứng (khe 0,3) + chân chặn trước.
- Tấm bụng (kem, `belly.stl`): mặt trơn, 4 vảy lông chữ V khắc nông 0,6, KHÔNG thủng; yên côn lắp từ trong.
- Mắt: 2 lỗ Ø34 hướng theo pháp tuyến, ống đỡ + hốc Ø40,6; kính khuếch tán 0,8 + vành 3 (Ø40) lắp từ trong; **vòng mắt kem Ø54** (`eye-ring.stl`, in 2 cái) mỏng 3 mm ôm sát mặt cong, dán ngoài vỏ (không lắp từ trong); sau kính là khoang trống cho LED (WS2812 5 mm hoặc module tròn).
- Mỏ: lỗ Ø18,4, gờ Ø24 trong, trục hơi chúc xuống; nút Ø50 hành trình ~2 mm, vành giữ Ø58 trong, chân ép Ø16 lên công tắc 6 × 6 (giá công tắc ở nửa sau, đỉnh z = 136,3).
- Micro: 3 lỗ Ø2 ở trán (z = 132), nằm ở **nửa trước** (trán thuộc nửa trước), cách tâm loa > 100 mm.
- Nửa sau: 5 khe 2 × 18 ở lưng, khe cáp 40 × 12 chân lưng (z 4–16, y ≥ 38).
- Vít: 4 vít M3 từ đáy xuyên **tấm đế** (`base-plate.stl`, dày 4, lõm Ø9 sâu 2,8 dưới miếng cao su Ø16) và sàn vỏ (xuyên 3,4) vào đai ốc lục giác 5,8 thả từ trên vào hốc đỉnh 4 trụ trong vỏ (2 trụ mỗi nửa).

## Khác với spec (cần Claude/Tuan duyệt)
1. **Không có gờ–rãnh dọc đường ráp**: gờ nhô qua mặt ráp nên nửa mang gờ phải in đứng trên gờ, trong khi tai/cánh đặc nằm lơ lửng. Thay bằng 6 lỗ chốt Ø2 sâu 8 mỗi nửa
   (đoạn nhựa 1,75 mm) ở tai, cánh và vành nút. Khớp + khe 0,2 theo bảng khe: chưa có, chưa in thử.
2. **Vít M3 không bắt chéo hai nửa**: tab chéo mặt ráp cũng làm hỏng hướng in → thêm part **tấm đế** kẹp cả hai nửa. Chiều cao tổng không đổi (đế nằm z 0–4).
3. Dáng (vòng chỉnh 2): cánh giọt nước áp sườn, nhô ≤ 6 mm, mép trên z ≈ 112, che nửa trên vành loa; tai chỏm nhọn mềm nghiêng 20°; mắt x = ±36,5; bụng Ø~70 mặt trơn. Tổng 138 × 117,7 × 172,7 (spec 142 × 116 × 175 ± 6; hẹp hơn vì cánh không còn chìa).
4. `eye-diffuser.stl` chỉ chứa 1 cái (gate buộc 1 khối), in 2 lần. Ảnh render dùng STL thật, màu theo design-spec, nhám 0,6.

## Kích thước part (đã đặt hướng in, mm)
| Part | X × Y × Z | Hướng in | Ghi chú |
|---|---|---|---|
| shell-front | 134,4 × 168,7 × 56,1 | mặt ráp xuống | mơ |
| shell-back | 134,7 × 168,7 × 56,5 | mặt ráp xuống | mơ |
| belly | 87,5 × 87,5 × 16,5 | mặt trước xuống | kem |
| speaker-bezel (×2) | 86 × 86 × 33,5 | mặt lưới xuống | mơ |
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
- Vấu giữ loa: 4 tay dài 3 mm, mảnh 1,4 mm; chưa in thử, loa thật có thể cần chỉnh.

## Chưa chắc / TODO
- Độ dày, cao linh kiện bo Audio Kit; vị trí USB: không có nguồn → khe cáp rộng; bo giữ bằng ray + chân chặn phía trước, **sau bo chưa có chốt giữ** (gate cấm vật chạm khối 82 × 73 × 25) → dùng xốp/keo nóng.
- Chiều cao công tắc tactile (giả định 4,3), loa thật (vành, phần sau), độ êm vấu: TODO đo.
- fit-library chưa có mục M3 / ống non: **chưa in thử** mọi khe (0,3 hốc linh kiện, 0,3 yên côn, 0,4 nút).
- Đáy phẳng vát 0,8 mm chưa làm. Khắc ▲ và logo STLAB chưa làm.
