# Form spec – cyberbrick-arm (bước 0 Giao diện, lần 2)

Tác giả: product-designer (thử việc), 2026-11-02. Lý do làm lại: Tuan chê ảnh duyệt cũ "hơi xấu" (ảnh cũ = khối hộp thô,
bóng nhựa phẳng, không có đường chia màu, không bo cạnh).

**Ảnh duyệt là PHÁC minh họa** (`design/sketch/sketch_forms.py`, dựng khối bo/vát bằng Blender từ `freecad/params.json`
tư thế `nghi` 70°/-80°), **không phải CAD**. Khung lắp ráp (J1/J2/J3, tầm với 149 mm, vị trí linh kiện, ô trống đế Ø76×48)
**giữ nguyên**. Mọi bo/vát bên dưới chỉ **bớt vật liệu trong hộp bao hiện tại**, không lấn ra ngoài.

Ảnh: `concepts/form-A|B|C-{iso,side,back34}.png`, tổng hợp `contact-sheet.png`. Phối màu: `cmf-A|B|C.json` (dùng được với
`tools/render/render.py` để render khối thô – lưu ý cần đường dẫn tuyệt đối cho `--out`/`--cmf`, tương đối thì Blender ghi
vào `C:\` và hỏng).

## Ngôn ngữ hình khối chung
"Khối hộp có xương sống" – đế tròn nặng, cánh tay dẹt (thanh 4 mm bao ngoài), hộp cẳng tay lớn có logo, đầu kẹp nhỏ.
Ba từ khóa: **gọn – chắc – dễ lắp**. Nhìn bóng đen vẫn nhận ra: đế tròn + thanh xiên + hộp ngang + 3 ngón.
Tỉ lệ (từ khung): đế Ø76 × cao 54 (mâm tới z 60), tháp 38 × 35 × 20, tay trên 55,86 (r đầu 10), cẳng tay 52,2 + khối sau
24 (hộp 38 rộng), đầu kẹp 34,5 × 30,7 × 30,7, ngón dài ~15 (hết hộp bao 50).

Quy tắc chung mọi phương án:
- Mặt tiếp bàn in: **vát 0,6–1,0 mm**, không bo tròn (không support). Bo lớn chỉ ở cạnh KHÔNG chạm bàn.
- Thành vỏ ≥ 1,6 mm; chữ/dấu khắc sâu 0,6 mm, nét ≥ 0,8 mm; cầu ≤ 15 mm; không vẽ support vào STL (Tuan tô trong Bambu Studio).
- Cạnh chỗ cầm ≥ 1 mm bo (lớp 6, không cạnh sắc). Khe lắp lấy từ `fit-library`, spec này không đặt khe.
- Tay trên dày 4 mm → bo tối đa 1,5 mm (chừa lõi 1 mm phẳng).
- Màu: tối đa 3 cuộn + 1 điểm nhấn; điểm nhấn (nắp khớp, ngón, hộp công tắc) cùng 1 cuộn. Tên màu hãng: **TODO** Tuan xác
  nhận cuộn thật đang có (Bambu PETG Basic: trắng/đen/xám/cam/vàng có thật; xanh thông cần xem bảng màu hãng).

## Phương án

| | A – Giữ dáng tham khảo | B – Công nghiệp vát | C – Bo tròn, đồ chơi thông minh (**khuyến nghị**) |
|---|---|---|---|
| Ý | Gần ảnh tipflow: thân trắng, tay xám, ngón cam | Vát 1,8 mm sắc nét, đế/đầu đen | Bo lớn, xanh thông STLab + trắng, nhấn vàng |
| Bo/vát chính | bo 1,5; cẳng tay 3; đầu 4 | vát 1,8 (1 đoạn); cẳng tay 2; đầu 2 | bo 5; cẳng tay 8; đầu tròn Ø30,7; mâm 3,5 |
| Màu | trắng `#F2F2EF` / xám `#8E9196` / cam `#F26A1B` | đen `#2B2F33` / trắng / vàng `#E8B33A` | xanh `#1E5A45` / trắng / vàng `#E8B33A` |
| Được | Quen mắt, ít rủi ro, ít thay đổi so với khối thô | Trông "kỹ thuật", đế đen che bẩn | Hợp lớp 6 (không cạnh sắc), đúng màu thương hiệu, nổi bật khi chụp, trông "đắt" nhất |
| Mất | Hơi giống bản gốc (đã vẽ lại nhưng dáng quen); trắng dễ lộ bẩn | Cạnh vát nhiều = nhiều mặt, ít thân thiện với trẻ nhỏ; đầu đen khó thấy khe | Bo 8 mm tốn ~5–8 % nhựa hơn khi in? (TODO đo, bo bớt vật liệu nên thực tế ít hơn); cần cuộn xanh thông |
| Rủi ro in | Thấp | Thấp | Trung bình: bo cạnh đáy phải đổi sang vát 1 mm; hộp công tắc/ngón bo cần kiểm bằng `check.py` |

**Khuyến nghị C.** Lý do: lớp 6 + "không cạnh sắc" (brief), màu trùng bộ nhận diện STLab (thông + sợi nhựa), nhìn rõ nhất trên
ảnh Facebook; đổi được sang A/B vì chỉ khác tham số bo + màu.

## Từng chi tiết (kích thước mm; "b" = bán kính bo; "v" = vát)
Cột A/B/C ghi chênh lệch; ô trống = dùng chung.

| Chi tiết | Dạng khối | A / B / C | Đường chia màu / chỗ khắc |
|---|---|---|---|
| **Foot_plate** 82×82×6 | tấm vuông bo góc r8 (đã có), hõm Ø68,8 sâu 4 | cạnh trên bo 0,8 (A,B) / bo 2 (C); **mặt dưới vát 0,8** | đáy: khắc "STLAB" 0,6 sâu (mặt tiếp bàn Textured PEI) |
| **Base_drum** Ø76, z6–54 | trụ tròn, đáy vát 1 | bo mép trên 1,2 / 1,8 / 3,5 | A: rãnh chia ở z30 rộng 0,8 sâu 0,6, đáy trắng + mâm xám. B: dải khe tối z13,5–22,5 (khoét vỏ cho tản nhiệt). C: không rãnh, thân trắng tinh, mâm xanh |
| **Khe thoát nhiệt** (cả 3) | 5 khe đứng 1,6×12 xuyên thành 2 mm, cách 12° trên cung, hướng +X, z14–26 | – | bắt buộc (motor 030 + driver, An toàn); không khe quá 1,6 để không tụt dây |
| **Turntable** disc Ø76 dày 6 + tháp 38×35, cao tới z80 | đĩa + hộp tháp | bo đĩa 1,2/1,8/3,5; tháp bo 2,4/2,9/8 (đứng) | **dấu lắp**: tam giác khắc 0,6 sâu, cạnh 5 mm tại +X mép đĩa, đối diện tam giác trên đỉnh Base_drum (z54) – ghép 2 tam giác = đúng chiều |
| **Arm_upper_L/R** dày 4 | thanh "viên thuốc" (A,C) / bát giác cắt góc 4 mm (B), r đầu 10 | bo 1,5 mặt cạnh | màu: A xám, B trắng, C xanh; **nắp khớp** Ø14,4 dày 1,6 tại J1, J2 (màu nhấn) lún 0,6 vào lỗ Ø5,5 thành bậc, khe vặn tua vít 8,4×1,0 sâu 0,6 → nhìn thấy chỗ xoay |
| **Forearm** hộp 38 rộng | prism sau 24+12 (n ±11) và trước (n −13…24) giữ nguyên; **cắt vát góc trên-trước 6–9 mm** (A 7, B 6, C 9) cho đường nhìn trôi về đầu | bo cạnh 3 / 2 / 8 | **logo STLAB** khắc 0,6 sâu, cao chữ 6 mm, nét ≥0,8, đặt mặt −Y, trung tâm s=32,1, n=5,5 (đối xứng bản +Y cho mặt kia nếu muốn); đường ráp nắp S2 thẳng hàng với mép khối sau |
| **Head** 34,5×30,7×30,7 | A hộp bo 4; B hộp vát 2; **C trụ tròn Ø30,7 dài 34,5, mũi vát 2,5** | – | màu: A trắng, B đen, C trắng. Khe hở 0,4 so với Forearm làm đường tối tự nhiên (không cần thêm màu) |
| **Finger_L/R/D** 8×8 → thon về 5,2 ở đầu, dài ~15 | thanh thon đầu bo | bo 2,0 / 1,5 / 3,9 | màu nhấn; mặt trong kẹp: 3 rãnh ngang 0,6 sâu cách 3 (chống trượt) – chỉ vẽ khi kỹ sư xác nhận chỗ trống ở khớp bánh răng |
| **Switch_holder** hộp 24×25×34 | hộp sau lưng đế, **đáy vát 1** | bo đứng 1,5 / 1,8 / 5 | màu nhấn; cửa công tắc có mũi tên khắc "ON ↑" 0,6 sâu |
| **Worm, Pinion, Gearbox, CB_*** | ẩn trong vỏ | – | không đổi |

Dấu lắp thêm (lớp 6 lắp một chiều): (1) tam giác ghép mâm–đế; (2) nắp khớp có khe tua vít song song với tay khi lắp đúng;
(3) mũi tên trên hộp công tắc; (4) chấm 2 mm nổi trên Forearm phía lắp S3. Mỗi dấu **khắc 0,6, không nổi** (trừ chấm).

## CMF
| Chi tiết | A | B | C |
|---|---|---|---|
| Foot, Base_drum, Forearm/Head (xem bảng trên) | trắng | đen | foot xanh, drum trắng |
| Turntable, Arm_upper | xám | trắng | xanh |
| Điểm nhấn: nắp khớp, ngón, Switch_holder | cam | vàng | vàng |
Bề mặt: mặt dưới Textured PEI (nhám), mặt thấy được hướng lên in bằng bàn trơn nếu có (TODO Tuan chọn). Vàng nhấn chỉ ở
đúng 3 nhóm trên (DESIGN.md: một điểm nhấn).

## Việc kỹ sư dựng (nếu chọn)
1. Thêm tham số `bo_*`/`vat_*` vào build_arm.py: `makeFillet` trên cạnh đứng và cạnh trên; **cạnh đáy dùng chamfer**.
2. Cắt vát góc trên-trước Forearm (6–9 mm): **kiểm khoang S3 (cavity) không bị cắt** – chưa có số đo thân servo dọc theo n, nên
   đây là TODO; nếu vướng, giảm xuống 4 mm.
3. Khắc: logo, 4 dấu lắp, 5 khe tản nhiệt; test_skeleton vẫn phải qua (hộp bao không phình).
4. Đầu tròn (C): kiểm trục vít Ø9,7 + khe 0,4 còn thành ≥1,6: (30,7 − 9,7)/2 = 10,5 mm, thừa.
5. Chạy `check.py` + slice thật vì bo lớn tạo cung nghiêng gần 0° ở chân bo (chỉ ở cạnh không chạm bàn).

## Đã sửa gì sau khi nhìn ảnh
- Lần 1 (render công cụ có sẵn): khối thô mịn nhòe giữa các mặt, nền bị ô tối, cắt khung lệch → không dùng làm ảnh duyệt;
  thay bằng phác riêng.
- Phác vòng 1: trắng cháy sáng, nền xám loang, ảnh cạnh bị cắt đỉnh → giảm đèn ~58 %, bỏ nền cong dùng "shadow catcher" ghép
  nền sương `#ECF1EF`, nới khung cạnh.
- Cẳng tay trông là hộp thô trắng-trên-trắng → thêm cắt vát góc trên-trước (đường nhìn về đầu), khe tản nhiệt, rãnh chia, nắp khớp có khe, logo.
- Vòng 2 phương án C: bo cẳng tay 5 → 8 mm vì nhìn chưa khác A; đầu đổi thành trụ tròn.

- Bảng chốt (64 mẫu, contact-sheet): C đọc rõ nhất, B đầu đen che mất khe/đường chia nên chỉ để làm phương án dự phòng; ảnh cạnh còn vệt chân trời mờ ở mép dưới (giới hạn của phác, không ảnh hưởng spec).

## Cần quyết (Tuan / phiên chính)
1. Chọn A/B/C (khuyến nghị C) và cuộn màu thực có: xanh thông? (TODO tên màu hãng).
2. Cho phép **cắt vát góc Forearm** (bớt vật liệu trong hộp bao) – cần kỹ sư xác nhận khoang S3.
3. Có muốn khe tản nhiệt 5 khe hướng +X (đề xuất, khoét vỏ đế) – phụ thuộc bố trí motor/hộp số (gearbox ở y 0,5–22,5).
4. Logo STLAB một mặt hay hai mặt Forearm (khuyến nghị 2 mặt, đối xứng).
