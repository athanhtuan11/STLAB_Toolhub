# Spec Cú Bông v3 – lắp ráp thật (Claude chốt 2026-11-27 theo Tuan)

## Vì sao
`tools/assembly-check` chạy trên bản hiện tại (`assembly.json`): **14 FAIL**. Bụng + mỏ chồng vỏ; đường lắp vành loa, vòng ép, nắp nút,
nắp màn, khay ampli bị vỏ chặn; chốt 2 nửa chưa vẽ (lỗ Ø2 khe 0); nắp nút + kẹp mic không có gì giữ. Tuan in thử: huy hiệu STLAB,
nắp màn, mỏ không lắp được; vành loa/tai không bắt được vào khung; 2 nửa không có chỗ bắt vít.

## Nguyên tắc (Tuan 2026-11-27)
1. **Vỏ trước = khung.** Mọi chi tiết bắt cố định vào **vỏ trước**. Vỏ sau = nắp: chỉ có lỗ sạc USB-C + giếng vít.
2. Lắp 1 chi tiết xong là **cố định ngay** trên vỏ trước (vít/lẫy), không chờ vỏ sau kẹp lại.
3. Huy hiệu bụng STLAB, nắp màn (face-plate), mỏ: **lắp từ ngoài vào**.
4. Vỏ sau nối vỏ trước bằng **vít M2.5 tự ren** (Tuan chọn): lỗ mồi Ø2,4 (fit-library, đã in thật) trên trụ vỏ trước;
   vỏ sau có **giếng vít** từ mặt lưng xuống sát mặt ráp: lỗ thông Ø2,8 + giếng Ø5,6 cho đầu vít, đáy giếng dày 3,0.
   Vít M2.5 × 12 (TODO Tuan xác nhận có sẵn; đổi chiều dài thì đổi `SCREW_L`, ăn ren ≥ 6 mm). 6 vít: 2 thấp, 2 giữa (trên vành loa,
   z ≥ 100), 2 trên đỉnh; vị trí cuối do gate (trụ nằm trong thành, không chạm linh kiện).
5. **Bo ESP32-S3 + 2 ampli: 1 khay in rời bắt vào vỏ trước** (Tuan chọn), M2.5 × 6 tự ren, cổng USB-C chĩa ra lỗ vỏ sau
   (lỗ = cổng/đầu cáp + 0,5 mỗi bên để bù lệch). **Chặn:** bo S3 + ampli CHƯA đo hàng thật (khối giữ chỗ 72 × 29 × 16) → đo trước khi vẽ khay.
6. **Bỏ tấm đế** (Claude đề xuất, báo Tuan): đáy chia đôi liền 2 nửa vỏ, khay điện tử bắt vỏ trước → bớt 1 mặt + 4 vít M3.
   Nếu Tuan muốn giữ tấm đế → chỉ bắt vào vỏ trước.

## Giữ mặt ráp y = 0,37
In 2 nửa mặt ráp xuống bàn đã PASS không support. Dời mặt ráp ra sau → lưng nghiêng > 45° (cần support). Chi tiết vắt qua mặt ráp:
- **Vành loa L/R**: đặt vào vỏ trước theo **−y** (nửa lỗ mở về +y), bắt **2 tai vít M2.5 × 6** vào trụ vỏ trước. Vòng ép ngàm xoay giữ
  nguyên (0,40/0,40/0,45 đã in đạt). Vỏ sau đóng bao quanh, khe 0,3.
- **Nút nói**: ổ switch tách khỏi vỏ thành **đế nút** (ổ MX 14,00 + rãnh V, ống/chữ thập giữ nguyên số đã ĐẠT) bắt 2 vít M2.5 × 6
  vào vỏ trước, đặt theo −y. Nắp nút (vành Ø54 > lỗ Ø50,8) đặt trước khi đóng vỏ sau.
- Kẹp mic: thêm chặn (vít hoặc lẫy) vào vỏ trước (đang tự do +y, −z).

## Lắp từ ngoài: ràng buộc in (quan trọng)
Vỏ trước in mặt ráp xuống → trục y đứng; **mặt hướng +y (vào trong) là trần treo**. Gờ móc vuông ngay sau lỗ = in treo → KHÔNG dùng.
Mặt móc lẫy phải là **cạnh trên của ô cửa sổ** khoét trên vách ống (cầu ≤ 6 mm, in bắc cầu được) hoặc vát 45°.
- Mỗi lỗ (bụng, màn, mỏ): miệng ngoài có **hốc chìm 1,0** cho vành chi tiết ngồi (định vị + chặn vào trong), ống sau lỗ tựa phễu 45°
  xuống thành vỏ (không treo), **3–4 ô cửa sổ** trên ống cho lẫy.
- Lẫy trên chi tiết: dài ≥ 10, dày 1,2, gờ 0,8 + khe 0,2 → biến dạng 1,8 % (TODO: chưa có số lẫy PETG đã in thật trong fit-library →
  **in mẫu thử nhỏ** 1 bàn: đoạn vỏ quanh lỗ bụng + huy hiệu, 2 cỡ gờ 0,6 / 0,8). Lẫy in đứng (theo Z) yếu theo lớp → chân lẫy bo R0,8.
- Mỏ: lỗ Ø10 quá nhỏ cho lẫy → nới lỗ Ø14 (đế mỏ Ø17,2 còn vành ≥ 1,5).
- Nắp màn: bỏ vành chặn 104 × 68 + 4 vít trong; màn vẫn bắt 4 vít tự ren Ø2,4 vào nắp (giữ số đã in đạt), cả cụm đẩy từ ngoài.

## Gate bắt buộc trước khi đưa in
1. `gate_owl_s3_screen.py` PASS (cập nhật kỳ vọng cho v3).
2. `assembly.json` cập nhật theo v3 (đường lắp −y cho chi tiết vắt mặt ráp, từ ngoài cho bụng/màn/mỏ, joint vít thật) →
   `tools/assembly-check` **PASS** (0 FAIL; chỉ chạm ở cặp khai báo).
3. Cắt lớp tất cả bàn PASS không support; 1 file .3mf nhiều plate.
4. Bàn thử nhỏ trước: góc vỏ quanh 1 trụ vít + giếng, lỗ bụng + huy hiệu lẫy, 1 tai vành loa.
