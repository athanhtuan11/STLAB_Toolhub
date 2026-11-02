# Dê flexi Tết 2027 (năm Mùi) – design spec bước 0

Trạng thái: phác dáng để duyệt bằng ảnh, CHƯA phải CAD. Ảnh: `contact-sheet.png`, `concepts/{A,B,C}-{side,top}.png`.
Sinh ảnh: `concepts/make_concepts.py` (Blender 5.2, ellipsoid chồng nhau; sừng trong ảnh nhìn "gợn hạt" chỉ do dựng nhanh, CAD làm liền mượt).
Thiết kế nguyên bản STLab: ngôn ngữ chung "đốt bo tròn nối khớp in liền", không dựa model flexi có sẵn. Khe khớp, thành, kiểu khớp: Claude quyết ở bước CAD (spec này không định số).

## Ngôn ngữ hình khối (chung)
Chuỗi đốt tròn mập như hạt, cạnh bo lớn (R ≥ 3 mm bản để bàn), 3 từ khóa: **tròn – ấm – mập**. Đầu to hơn thân (chibi). Mọi mặt tiếp bàn là mặt phẳng nhỏ (hoặc vát), không bo cầu tiếp bàn. Số đốt dưới đây là ước lượng từ phác dáng.

## 3 hướng

| | A Mùi Tròn | B Mùi Núi | C Mùi Nằm |
|---|---|---|---|
| Tư thế | đứng 4 chân, đầu to | đứng, cổ dài, dáng dê núi | nằm phục, chân gập |
| Dài x cao (để bàn) | ~160 x 95 mm | ~190 x 110 mm | ~150 x 85 mm |
| Móc khóa | ~65 mm (x0,4) | ~65 mm (x0,35) | ~65 mm (x0,43) |
| Đầu | 1 đốt đầu + mõm + 2 tai + râu | 2 đốt + 2 tai | 1 đốt + mõm + 2 tai |
| Cổ/thân | 1 đốt cổ (khăn) + 3 đốt thân | 3 đốt cổ + 4 đốt thân | 1 đốt cổ + 3 đốt thân |
| Chân | 4 chân x 2 đốt (đùi + móng) | 4 chân x 3 đốt, mảnh | 4 chân gập, mỗi chân 1 đốt |
| Đuôi | 1 đốt + chóp | 3 đốt cong | 1 đốt nhỏ |
| Tổng đốt khớp | ~15 | ~24 | ~11 |
| Sừng | 1 cung ngắn dày mỗi bên | cung dài sau gáy | xoắn ốc cuộn (vòng 1 vòng) |

- Khớp: giữa mọi đốt kề nhau (cổ/thân/đuôi/chân); đầu-cổ 1 khớp. Sừng, tai, râu là phần cứng liền đầu (không khớp).
- Trên xuống (đối xứng trái-phải): A và C thân rộng ~40 mm (bản bàn) = ổn định; B hẹp ~32 mm.

### Đánh đổi
- **A**: dễ thương nhất, hợp quà Tết/trẻ em, chân ngắn dày nên khó gãy; hơi "chó" nếu thiếu sừng – cần sừng dày + râu để đọc ra dê.
- **B**: đẹp, giống dê thật nhất, nhưng 24 đốt, chân 3 đốt mảnh (~14 mm) → bản móc khóa khớp quá nhỏ, dễ gãy, in lâu; cổ dài dễ kẹt khớp. Rủi ro cao nhất.
- **C**: in chắc nhất, ít đốt, nằm sát bàn nên cầu/nhô ít; làm móc khóa tốt (gọn, dày). Ít "vẫy" được (chân không cử động), nhưng thân vẫn uốn được. Sừng xoắn cần kiểm cầu/vênh.

**Khuyến nghị: A cho bản để bàn (hàng chính), và C làm móc khóa nếu A móc khóa quá nhỏ** (hoặc làm A cả hai cỡ trước, đo thử ở bước CAD). Lý do: A cân bằng đẹp - in chắc - dễ nhận ra "dê"; B bỏ hoặc để phiên bản sau.

## Nét Tết Việt (khắc chìm nông, không logo)
- Lưng: hoa văn mây cuộn (vân xoắn) hoặc 1 hoa mai 5 cánh trên đốt thân giữa; sâu ~0,6 mm, nét ≥ 0,8 mm (mức khắc theo chuẩn STLab; Claude chốt ở CAD).
- Khăn quàng cổ: vòng dày liền đốt cổ (A,C) – hoặc part rời đỏ (biến thể phụ). Không lá/chữ quá nhỏ.
- Chữ "2027" hoặc "Mùi" nổi nhẹ/khắc ở bụng (mặt dưới) – tùy, không bắt buộc. Logo STLAB: khắc chìm mặt dưới đốt thân, không lên mặt nhìn thấy.
- Móc khóa: tai/vòng treo là phần liền đầu hoặc đuôi, lỗ ≥ 4 mm đường kính, thành quanh lỗ dày ≥ 3 mm (mức an toàn tạm; Claude chốt).

## CMF (gợi ý, Tuan tự chuẩn bị cuộn)
Bambu PETG Basic, 1 màu mỗi lần in, Textured PEI mặt dưới. TODO: tên màu hãng chính xác chưa xác nhận, Tuan chọn theo cuộn có sẵn.
- Bản chính: **trắng/kem** (hoặc vàng) cả con – ảnh minh họa dùng trắng kem.
- Biến thể 2 màu rời: **sừng + móng vàng** (part rời đơn sắc), **khăn đỏ** (part rời) – ráp vào, không đổi màu giữa lớp.
- Phiên bản "Tết đỏ": cả con đỏ, hoa văn khắc không cần màu.
- Trong ảnh: trắng #F7F2E6, vàng #E8B33A (cùng vàng sợi nhựa STLab), đỏ #C8372D – chỉ minh họa.
- Điểm nhấn tối đa 2 màu phụ + 1 màu chính.

## Rủi ro in (để bước CAD xử lý)
1. In nằm phẳng trên bàn, chân chạm bàn: các đốt tròn phải có mặt phẳng/vát tiếp bàn; đốt trên cao (đầu, sừng, tai) tự phát sinh nhô → đối xứng/vát ≥ 45° hoặc chia tư thế in (chân xòe nằm ngang) để không support. C ít rủi ro nhất, A trung bình, B cao.
2. Sừng cong/xoắn và tai dựng: đủ dày (≥ 8 mm bản bàn, ≥ 3,5 mm bản móc khóa theo ước lượng), tránh đầu nhọn; gốc sừng liền thân.
3. Khớp in-place: dính khe do PETG kéo tơ → cần test ngắn 1 khớp trước khi in cả con (Claude chốt khe ở CAD). Bản móc khóa 65 mm làm khe khớp chiếm tỉ lệ lớn; có thể nhỏ quá in được hay không là điều cần đo thử.
4. Chân mảnh (B) và đuôi nhiều đốt: gãy khi trẻ bẻ; A/C ít hơn.
5. An toàn trẻ em: không cạnh sắc, bo ≥ 1 mm toàn bộ; khe khớp kẹp ngón tay nhỏ – kiểm khe và ghi cảnh báo "không cho trẻ dưới 3 tuổi" trong bao bì/mô tả (phần nhỏ).
6. Time in ước lượng: A ~vài giờ (chưa tính). TODO đo sau CAD.

## Cần quyết (Tuan)
1. Chọn hướng: A (khuyến nghị) / B / C, hoặc ghép (đầu A + tư thế C).
2. Bản móc khóa dùng hướng nào (A nhỏ hay C).
3. Có làm biến thể part rời (sừng vàng, khăn đỏ) hay chỉ 1 màu.

## Việc kỹ sư dựng khi Tuan chọn
- Dựng chuỗi đốt + khớp in liền theo hướng được chọn, hai cỡ; chạy `printability.py` + test khớp mẫu; khắc hoa văn + logo; thêm dấu/chữ nhận biết theo mô tả MakerWorld.

---

# VÒNG 2 – chốt tư thế C (nằm phục) + đầu to chibi

Ảnh: `contact-sheet-v2.png`, `concepts-v2/v2-*.png`. Sinh ảnh: `concepts-v2/make_v2.py` (Blender 5.2 Cycles; đầu = metaball liền mạch, thân = hộp bo + boolean khắc; chỉ để duyệt dáng, KHÔNG phải CAD, số đo dưới đây là số trong ảnh, Claude chốt lại ở CAD).
Ngôn ngữ: **tròn – ấm – mập**; đầu là một khối liền (không ellipsoid rời), thân là 6 đốt hộp bo R≈5,5 mm nối chốt, khe giữa đốt nhìn thấy từ trên và từ bên.

## Kích thước trong ảnh (bản để bàn, mm)
- Dài ~170 (đuôi → mũi), rộng ~90 (tai–tai), cao ~85 (đỉnh sừng). Bản móc khóa: nhân 0,4 → ~68 mm + vòng treo ~12 mm.
- 6 đốt thân (dài x rộng x cao): đuôi 10x26x24, 14x40x32, 17x48x38 (mây), 18x50x40 (hoa mai), 16x44x38 (mây), cổ 14x30x30 (đội khăn). Khe giữa đốt 2 mm, chốt nối rộng 14 mm, cao ~55 % đốt (nhìn thấy trong khe).
- Đầu: khối liền ~52 x 54 x 48, mõm ngắn bè (~26 x 30), mắt Ø12,4 (to, cách nhau 34), 2 lỗ mũi nhỏ, tai ngang dẹt dài 38 (gốc liền đầu, hơi cụp), râu dê = chùm 3 hạt thu nhỏ dưới cằm, chạm bàn.
- Chân: 2 chân trước duỗi nằm sát hai bên cằm, 2 đùi sau mập + bàn chân gập; đùi chồng lên thân (liền, không tách rời). Mặt dưới phẳng; mọi khối tiếp bàn cắt phẳng.

## Chi tiết vỏ
| Chi tiết | Dạng khối | Bo/ghi chú |
|---|---|---|
| Sừng (part rời, vàng) | cung đặc dày, cong ra sau, mũi bo tròn, KHÔNG đốt; gốc có chốt cắm xuống đầu (Ø~9, sâu ~10 trong ảnh) | thân sừng Ø16 → mũi Ø5 (bản bàn); bản móc khóa dày thêm (~Ø16→8) để mũi ≥ 2 mm. Sừng vòng ra sau, nhô cao ~25 mm trên đầu; đoạn sau nghiêng xuống ~45° (cần kiểm cầu/in nằm: xem Lo ngại) |
| Khăn (part rời, đỏ) | vòng dày Ø38 (tiết diện Ø12) quanh cổ, hở đáy ~10 mm để kẹp, nút + 1 đuôi khăn rủ bên trái | cạnh bo ≥ 1,6; kẹp/khe: Claude chốt |
| Hoa văn lưng | hoa mai 5 cánh (5 lõm tròn Ø6,6 quanh 1 lõm giữa) trên đốt giữa; 2 xoắn mây (2,4 vòng, nét 2 mm) trên mỗi đốt kề, đối xứng trái/phải | sâu ~1,0 mm bản bàn; bản móc khóa nét 3 mm, sâu 1,5 mm (sau thu 0,4 → nét 1,2 / sâu 0,6) |
| Mắt/mũi | mắt nổi cầu Ø12 (bản màu: đen bóng + chấm sáng); bản 1 màu: mắt là chỏm nổi cùng màu | cần quyết: tô tay / part đen nhỏ / để nổi cùng màu |
| Logo STLAB | khắc chìm mặt dưới đốt giữa, không lên mặt nhìn thấy | |
| Vòng treo (móc khóa) | vòng dẹt nằm bàn gắn đuôi, lỗ ~Ø10,6 (→4,2 sau thu), thành dày ~6,4 (→2,6) | liền thân, cắt phẳng đáy |

## CMF vòng 2
- Bản chính 1 màu: trắng kem (ảnh #F7F2E6, TODO tên màu hãng Bambu PETG Basic); bản "Tết đỏ" cả con đỏ (#C8372D) – ảnh 4, 5.
- Biến thể part rời: sừng vàng (#E8B33A) + khăn đỏ, thân kem; 3 chi tiết đơn sắc, không AMS – ảnh 2, 6.
- Mắt/mũi đen chỉ minh họa, không in.

## Đã sửa gì sau khi nhìn ảnh
- Lần 1: sừng dựng thẳng giống tai thỏ → hạ cung, cong ra sau, dày hơn; ảnh cháy sáng → giảm đèn, nền xám sương.
- Đốt "cloud" biến mất (boolean hỏng vì xoắn tự cắt nhau) → giãn bước xoắn, nét 2,1 mm.
- Mõm nhọn như chuột/heo → mõm ngắn bè, mũi 2 lỗ; râu 1 que giống ngà → chùm 3 hạt rộng; ngọc mắt chấm sáng dính ngoài → áp sát mặt cầu mắt; tai to hơn, ngang.
- Ảnh top bị cắt → lùi camera; nền có vạch ngang → tăng clip camera.
- Còn thấy: đốt thân trông hơi "hộp"/vali (R5,5); đùi sau vẫn là khối tròn to; đầu hơi giống thỏ/chuột khi nhìn thẳng mặt – cần kiểm lại ở CAD (xem Lo ngại).

## Lo ngại (để Claude kiểm ở CAD)
1. Sừng: đoạn sau cong xuống ~45° và nhô ra sau gốc → không in được nếu in cùng đầu; part rời in riêng (nằm nghiêng/đặt bên) tránh support → cần hướng in cho sừng. Chốt cắm sừng + ổ cắm trên đầu: chưa định số.
2. Khăn dạng vòng kín hở đáy 10 mm không thể luồn qua cổ nếu cổ rộng 30: cần kẹp C đàn hồi hoặc chia 2 nửa; khe fit-library.
3. Khớp in-place ở bản 0,4x: khe khớp chiếm tỉ lệ lớn, đốt 14→5,6 mm; chốt nối 14→5,6 mm; có thể quá nhỏ → thử bản trung gian 0,5x.
4. Sừng/tai/mũi chia nhánh mảnh bản móc khóa (tai dày 10→4 mm ổn; mũi sừng ≥ 2 mm đã nới).
5. Mặt trên đốt phẳng chỉ ~5–9 mm nên hoa mai/mây khắc chạm vùng bo; chiều dài đốt có thể phải tăng.
6. Dáng "dê" hay "thỏ": nhận ra nhờ sừng cong + râu + tai ngang; vẫn mõm hơi tròn.

## Cần quyết (Tuan)
1. Chân/đùi: giữ khối tròn to hay đổi thành đốt có rãnh cho giống thân?
2. Mắt bản 1 màu: nổi cùng màu / dán tô / part đen nhỏ?
3. Dài thực ~170 mm (to hơn dự kiến 150): thu 0,9x hay giữ?
