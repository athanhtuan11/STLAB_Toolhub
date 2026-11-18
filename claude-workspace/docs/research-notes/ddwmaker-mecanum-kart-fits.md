# DDWMaker kart Mecanum (CyberBrick Modular Bricks) – thông số lắp ghép

> **An toàn:** pin Li-ion ZL003: sạc bằng sạc hãng, tháo nắp sau rút giắc pin trước khi sạc; không làm chập cực pin. Servo PG002 không có bảo vệ kẹt – không giữ bánh khi đang chạy.

## Nguồn

- MakerWorld "CyberBrick Modular Bricks Kart (Mecanum Wheel)", tác giả DDWMAKER, license Standard Digital File License (dùng cá nhân, không đăng lại, không lên git). File ở `community/makerworld-ddwmaker-modular-bricks-kart-mecanum/` (git bỏ qua).
- 3 bộ in: Basic Modular Bricks (CHƯA tải – Tuan cần tải thêm), Chassis and Body (5 bàn: Chassis A, Chassis B, Body A, Body B, Body C=80 chốt + dụng cụ nhổ chốt), Mecanum Wheels (3 bàn: PLA vành, PLA 64 bạc, TPU 90A 36 con lăn).
- Máy tác giả: Bambu A1 mini 0,4, lớp 0,2, Bambu PLA Basic 220 °C, Textured PEI 65 °C, xy_hole_compensation 0, 2 vách, 15 % zig-zag. Chassis: support tree(manual) – chỉ vùng tác giả tô sẵn. Con lăn: TPU 90A 225 °C, max 2,8 mm³/s, 0 % infill, 3 vách, đáy/mặt 4 lớp concentric. Bạc: brim ngoài 1,6.
- Phần cứng: ZK004 Beginner kit, ZL003 pin sạc, thêm 3 servo 360° PG002 (tổng 4), 4 gói chốt đồng 2×33 DA006 (cần 32), vít M2,5×6 BHCS (12 cho bánh + 4 thân + 6 bộ Basic), LED hub + 4 RGB LED.
- Điều khiển: tay CyberBrick tiêu chuẩn hoặc Modular Bricks Remote; file JSON trong app; tiến/lùi, rẽ, trượt ngang, nút LED.

## Số đo (stl-fit, measure_features + cắt lát)

| Giao diện | Lỗ | Chốt/trục | Khe | Fit | Ghi chú |
|---|---|---|---|---|---|
| Khung Technic | lỗ Ø4,92 xuyên, bậc Ø6,1 sâu ~0,9 (biến thể 0,7) hai mặt, pitch 8, dày 8 | chốt in Ø4,6 (vát 2 mặt còn 3,8) | 0,32 | clearance/bấm | gờ giữa Ø5,6 dài ~1,5; 2 đầu ngạnh Ø5,84; khe xẻ 2,4–3,0; dài 15,7; 76 cần + 4 dư |
| Bạc trên trục đồng | lỗ bạc Ø2,44 | trục Ø2 | 0,44 | rotate | – |
| Bạc trong con lăn TPU | lỗ con lăn Ø4,02 | bạc Ø3,96 (dài 5,0, vành Ø6,4×0,4) | 0,06 | press | TPU mềm giữ bằng ma sát; con lăn Ø10,6×25,4 |
| Trục đồng trong vành | lỗ mù Ø2,2 sâu 2,9 nghiêng 45° | Ø2 | 0,2 | clearance | bị kẹp giữa 2 nửa vành khi siết vít |
| Vít tự ren M2,5 | Ø2,3 sâu 4,6, miệng Ø2,7 | TODO | TODO | tự ren | cùng khoảng 2,2 MEC-1 và 2,4 tipflow |
| Vít xuyên M2,5 | Ø2,9 + bậc đầu Ø5,2; lỗ tâm bánh Ø2,8 | TODO | TODO | clearance | – |
| Khớp lục giác bánh–servo | hốc lục giác đối cạnh ~6,12 | TODO | TODO | TODO | confidence 0,6; TODO ghép cặp khi có bộ Basic |
| Bánh | – | – | – | – | Ø48,2; nửa vành cao 19,2 (giữ con lăn) và 14,8 (nắp, có chữ A/B); 8 con lăn/bánh |

## Mẫu thiết kế rút ra

- Lắp như xếp gạch, không vít/keo trừ bánh; dụng cụ nhổ chốt in kèm (đầu nhổ/ấn chốt, đuôi đẩy giắc dây).
- 4 servo 360° thay 4 motor vì receiver CyberBrick chỉ 2 cổng motor nhưng 4 cổng servo; servo cho mô-men tốt.
- Bánh mecanum không cần vòng bi: bạc PLA + trục đồng + con lăn TPU; bánh A/B gương.
- Hướng dẫn lắp có cảnh báo đi dây, kẹp dây, chiều giắc, dấu tròn bên trái – nên học cách viết ASSEMBLY cho học sinh.
- Mục fit-library đã thêm: ddw-kart/technic-pin-printed, roller-bush-on-dowel, bush-in-tpu-roller, dowel-2mm-in-hub, m2.5-self-tap, m2.5-clearance, wheel-hex-socket (tất cả community, verified=false).

## Lưu ý khi STLab in (A1 + PETG mặc định)

- Khe tác giả chỉnh cho PLA. PETG dẻo hơn: chốt bấm có thể chặt/lỏng khác → in thử bàn Body C (chốt) trước hoặc in PLA đúng như tác giả. TODO: in xong cập nhật verified.
- Con lăn bắt buộc TPU 90A (không có thì không chạy được).
