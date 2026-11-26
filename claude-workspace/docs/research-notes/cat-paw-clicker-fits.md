# Cat Paw Clicker (voxo3d) - số đo lắp ghép keycap + ổ switch MX

Nguồn: `community/makerworld-cat-paw-clicker/cat-paw-clicker-02.3mf` (chỉ đọc). Đo 2026-11-26 bằng python + trimesh:
tách từng object trong `3D/Objects/*.model` (hệ tọa độ cục bộ của chi tiết, gốc ở tâm hộp bao), cắt lát mặt phẳng ngang
(`section`, bước 0,05-0,4 mm), tìm mức z chuyển hình bằng chia đôi. Chi tiết: `object_32` = keycap "up"
(in vành váy chạm bàn), `object_9` = thân "body" (in miệng ổ hướng lên), `object_16` = lò xo in.
Fit-library trỏ tới file này: `catpaw/mx-socket`, `catpaw/mx-keycap-cross` (tools/model-study/fit-library/fits.json).

## Keycap (object_32, z từ vành váy lên; vành váy tại z = -5,65 cục bộ)

| Đặc điểm | z cục bộ | Tính từ vành váy (mm) | Ghi chú |
|---|---|---|---|
| Vành váy (đáy keycap, chạm bàn in) | -5,65 | 0 | váy ngoài 36,14 x 27,2; trong 33,15 x 24,2 -> váy dày 1,5 |
| Đầu ống chữ thập | -1,34 | 4,31 | ống đặc Ø5,71, lùi vào trong váy 4,3 |
| Đáy lỗ chữ thập = trần hốc | 4,15 | 9,80 | lỗ chữ thập 4,19 x 1,25 (tay đo 4,19 và 3,90 rộng bên trong 1,25); sâu từ đầu ống = 4,15 - (-1,34) = 5,49 (ghi 5,6 trong fits.json = làm tròn trên) |
| Mặt trên keycap | 5,65 | 11,30 | nắp trên dày 1,5 (từ 4,15 đến 5,65), mặt cong thu nhỏ 34,9 -> 30,7 |

- **Quanh ống KHÔNG có rãnh vòng riêng**: ống Ø5,71 đứng tự do trong cả hốc keycap (hốc trong 33,15 x 24,2, sâu 9,80 từ vành).
  Khoảng hở quanh ống tới váy >= 9 mm mọi phía; vỏ switch (khoảng 14 x 14 trên cùng ~15,6 gờ) lọt TRONG hốc, không chạm ống.
  Nghĩa là mẫu khoảng trống quanh ống = toàn bộ hốc (đáy hốc cách đầu ống 5,49), còn rãnh vòng bán kính 4,6 sâu 4 của bản S3
  là phát minh riêng (không có trong mẫu).
- Chữ thập: tay dài 4,19, rộng 1,25 (khe chữ thập vs thân switch 4,0 x 1,17 danh nghĩa: +0,19 / +0,08).

## Thân (object_9, mặt phẳng z cục bộ, đáy thân z = -7,65, đỉnh = +7,65)

| Đặc điểm | z cục bộ | Ghi chú |
|---|---|---|
| Đáy ổ switch (kín) | -5,15 | đáy ổ cách đáy thân 2,5 |
| Miệng ổ switch | 3,43 | sâu 8,58; ống ổ ngoài 17 x 17 (thành 1,5), trong 14,00 x 14,00 |
| Rãnh V (ngàm switch) | 1,94 -> 3,44 dưới miệng, sâu nhất 2,69 dưới miệng rộng 15,44 | 45 độ, thành +0,72 mỗi bên |
| Đáy trần thân (mặt dưới) | 7,0 | mặt trên trần thân 7,65 -> trần dày 0,65 |
| Miệng -> mặt dưới trần | 3,57 | |

## Chồng lớp theo phương ấn (keycap + switch + ổ) - từ số đo

Với switch MX đặt kín đáy ổ, vỏ switch (nắp trên) cao `HOUSING_H` trên miệng và chân dài `STEM_H` trên vỏ (số switch: **TODO nguồn
datasheet, script bản S3 đang dùng 3,0 và 3,6 - chưa xác minh trong phiên này**). Từ keycap mẫu:
- Chân chữ thập vào được tối đa 5,49 (sâu lỗ) > chân lộ 3,6 -> còn dư 1,89 mm phía trên đầu chân (ở trần hốc).
- Đầu ống dừng khi chạm vỏ switch; trước đó chữ thập đã ăn trọn 3,6 mm của chân. Vỏ switch + ống nằm trong hốc rộng nên
  **mặt dưới trần hốc (z 4,15) không bao giờ chạm vỏ**: giữa vỏ switch và trần hốc chỉ có ống Ø5,71 - đáy hốc cao hơn đầu ống 5,49.
- Hành trình nắp đi xuống = khe giữa đầu ống và vỏ switch lúc nghỉ + dư; mẫu không có gờ chặn riêng cho keycap ngoài trần thân
  (mặt dưới trần thân z 7,0) - **TODO**: khe mép váy keycap - đáy hốc lúc nghỉ chưa đo vì keycap và thân là chi tiết rời, vị trí lắp
  chỉ suy ra khi có switch (cần số switch xác minh) hoặc từ `Elephant.3mf` (đã liệt kê, chưa đo - object_7/12 nặng 41-57 MB).

## Điểm chính cho nắp S3 (khuyến nghị, chưa đưa vào code - chờ Claude)
1. Nắp mẫu: ống Ø5,71 nhô 4,31 dưới "mép váy" và lỗ chữ thập 5,49 > chân lộ 3,6 -> chữ thập ăn trọn chân, vẫn dư 1,89.
2. S3 hiện: MX_INSERT = 1,2 (chữ thập chỉ ăn 1,2 của 3,6) + mặt dưới phẳng -> không bám được. Cần: ống nhô >= 4,3, lỗ >= 5,5.
3. Quanh ống phải trống >= ~9 mm bán kính (mẫu) hoặc ít nhất rộng hơn vỏ switch trên cùng (15,6 theo script) để vỏ lọt vào
   khoét lõm - rãnh vòng r 4,6 (nhỏ hơn nửa vỏ 7,8) KHÔNG đủ: vỏ switch đụng mép rãnh và đẩy chân lún.
