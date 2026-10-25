# pushrod-arm – thanh răng xi-lanh bị lệch: phân tích + cơ chế thay thế từ cộng đồng

Ngày: 2026-10-25 · Người yêu cầu: Tuan · Trạng thái: **nghiên cứu, chưa sửa model** (chờ Tuan chọn hướng).

## 1. Hiện trạng
Tuan thử `Housing_Elbow`: khi khuỷu lên/xuống, `Rack_Elbow` bị lệch → cơ chế không khả thi.

Cơ chế hiện tại (theo `freecad/scripts/history/2026-10-24_cylinder_030_gearbox.py`, `2026-10-22_build_pushrods_v3.py`):
- Động cơ 030 + hộp số → trục vít → bánh vít z16 → bánh răng z10 m1 (cùng trục) → **thanh răng 1 phía** cao 12 mm.
- Thanh răng chỉ được dẫn bằng **rãnh trượt trong vỏ** (khe 0,3 mm, có 2 cửa sổ hở x 20,5–27,5 và 34–41,5), không có con lăn tựa lưng.
- Hai đầu xi-lanh là chốt (vỏ ↔ tháp/cần, đầu thanh răng ↔ cần). Hành trình L 92 → 128 mm (≈ 36 mm).
- Động cơ + hộp số treo ngang (+Y) một bên vỏ.

## 2. Nguyên nhân có thể (suy luận từ hình học – **cần Tuan xác nhận kiểu lệch**)
| # | Nguyên nhân | Biểu hiện thường gặp |
|---|---|---|
| 1 | **Lực tách răng**: răng 20° đẩy thanh răng ra xa bánh răng ≈ 0,36 × lực đẩy. Không có gì tựa lưng ngoài vách rãnh 0,3 mm (lại có cửa sổ hở) → thanh răng bị đẩy ra, nhảy răng. | Kêu lạch cạch, thanh răng lùi khỏi bánh răng, nhảy răng khi có tải |
| 2 | **Thanh răng vừa truyền lực vừa làm khung**: cả cụm vỏ chỉ được giữ thẳng hàng bằng thanh răng trong rãnh. Vỏ nặng (motor treo 1 bên) + ma sát chốt → mô-men xoắn/uốn dồn vào thanh răng ở miệng rãnh. | Vỏ xoay quanh thanh răng, thanh răng nghiêng/xoắn trong rãnh |
| 3 | **Chiều dài dẫn hướng ngắn khi duỗi hết**: phần thanh răng còn trong rãnh ngắn so với phần thò ra → khe 0,3 mm thành góc nghiêng lớn ở đầu chốt. | Lệch tăng dần khi duỗi ra |
| 4 | PETG + khe 0,3 mm/bên + chốt khe 0,3 mm: cộng dồn rơ. | Lỏng ngay cả khi không tải |

**Hỏi Tuan (TODO):** lệch kiểu nào – (a) thanh răng bị đẩy xa bánh răng/nhảy răng, (b) xoắn/nghiêng sang ngang, (c) cong? Có ảnh/video càng tốt.

Nhận xét chung: thanh răng 1 phía chỉ chạy ổn khi có **dẫn hướng riêng** (ray/con lăn) gánh lực tách và lực ngang.
Trong cộng đồng, xi-lanh in 3D cho tay máy/máy xúc gần như đều dùng **vít me + đai ốc trong ống lồng**, không dùng thanh răng.

## 3. Các phương án

### A. Giữ thanh răng, sửa dẫn hướng (sửa ít nhất)
- **Con lăn tựa lưng** đối diện bánh răng: ổ bi nhỏ hoặc ống in xoay trên vít M2.5/M3, ép lưng thanh răng vào bánh răng.
  Đây là cách xe hơi/giàn CNC giữ thanh răng ăn khớp (cơ cấu lái dùng con lăn/đệm ép lưng thanh răng, cân bằng giữa lực ép và ma sát).
- **Rãnh kín** (bỏ cửa sổ hở), kéo dài đoạn dẫn hướng ≥ 2 × chiều cao thanh răng ở tư thế duỗi hết.
- Thanh răng có **gờ chữ T/đuôi én** chạy trong rãnh để không xoắn.
- Ưu: giữ motor, bánh vít, bánh răng; in lại Housing + Rack. Nhược: vẫn ma sát trượt nhựa–nhựa; nếu nguyên nhân #2 (vỏ xoay) thì chỉ đỡ chứ không hết.

### B. Vít me + đai ốc, ống lồng (khuyến nghị)
- Cộng đồng CyberBrick đã làm: **Cyberbrick Excavator** (MakerWorld 2371626) dùng motor N20 + **trục ren M3 × 45** + **đai ốc vuông M3**.
  Mẫu Printables "Micro Linear Actuator" (289703) cũng N20 + ty ren M4 + đai ốc + ổ bi (~3 USD/cái).
- Cấu tạo: motor 030 + hộp số quay trục ren đồng trục xi-lanh → đai ốc vuông kẹp trong **ống piston in** → ống piston trượt trong **ống vỏ** có tiết diện vuông/lục giác (chống xoay). Đầu ống piston là mắt chốt.
- Ưu: lực dọc trục, **không có lực tách**; ống lồng dài tự làm khung, chịu lực ngang tốt hơn thanh răng; ren M3 bước 0,5 mm **tự hãm** (thay vai trò trục vít hiện tại); linh kiện rẻ, dễ mua.
- Nhược: vẽ lại toàn bộ xi-lanh (Housing, Rack → ống piston, bỏ Worm + Pinion_WormWheel); trục ra hộp số Ø5,3 cần khớp nối in sang ty M3/M4;
  cần thêm ổ chặn/vòng đệm chịu lực dọc trục ở đầu hộp số. Tốc độ = vòng/phút trục ra × 0,5 mm – **TODO** đo vòng/phút hộp số 030 (chưa có số liệu kit).
- Hành trình 36 mm → ty ren ≥ ~50 mm; chiều dài thu ngắn nhất tăng → phải kiểm lại L_min 92 mm.

### C. Mua xi-lanh điện chính hãng PG003 (nhanh nhất để thử)
- Bambu Lab bán **"25mm Electric Push Rod for CyberBrick – PG003"** (~36 USD/cái). Cắm cổng **servo** (mạch trong xi-lanh đổi PWM → DC), dùng cho cẩu/máy xúc trên MakerWorld.
- Ưu: không phải in cơ cấu, đã được hãng làm cho CyberBrick; giải phóng cổng M1/M2.
- Nhược: hành trình **25 mm < 36 mm** hiện tại → phải dời điểm chốt để đủ góc; lực, chiều dài thu, kích thước lỗ chốt **TODO** (chưa tìm được datasheet);
  không có phản hồi vị trí (diễn đàn đoán dừng cuối hành trình theo dòng tải – chưa xác thực); 2 × ~36 USD; cần 2 cổng servo (hiện dùng S1, S3 → còn trống, kiểm lại).

### D. Bỏ xi-lanh – dẫn động thẳng khớp
- Trục vít + bánh vít đặt **ngay tại khớp** (tự hãm, bánh vít gắn vào cần), hoặc servo + thanh nối song song kiểu EEZYbotARM MK2 (động học thu nhỏ ABB IRB460, chỉ dùng servo, chốt M4).
- Ưu: không còn thanh trượt. Nhược: đổi kiểu dáng dự án (không còn "pushrod arm"), vẽ lại nhiều nhất.

## 4. Khuyến nghị
1. **Trước tiên**: Tuan mô tả/ảnh kiểu lệch (mục 2) – nếu chỉ là nhảy răng (#1) thì A (con lăn tựa lưng + rãnh kín) có thể đủ, in lại ít.
2. Nếu lệch do vỏ xoay/thanh răng xoắn (#2, #3) → chuyển **B (vít me M3/M4 + ống lồng)**: cùng hệ sinh thái CyberBrick đã có người làm chạy, giữ motor 030, cơ cấu bền hơn hẳn.
3. C chỉ nên chọn nếu muốn thử nhanh và chấp nhận vẽ lại vị trí chốt cho hành trình 25 mm.

Đánh đổi chính: A rẻ/nhanh nhưng có thể vẫn lệch; B chắc chắn hơn nhưng vẽ lại cả 2 xi-lanh; C tốn tiền + đổi hình học.

## 5. Nguồn
- Cyberbrick Excavator (N20 + trục ren M3×45 + đai ốc vuông M3): https://makerworld.com/models/2371626
- Máy xúc CyberBrick dựa trên bài "Electric Push Rod for Cyberbrick": https://makerworld.com/models/3021552
- Micro Linear Actuator N20 + M4: https://www.printables.com/model/289703-micro-linear-actuator
- PG003 trên cửa hàng Bambu: https://eu.store.bambulab.com/collections/electric-push-rod
- Diễn đàn Bambu – PG003 bên trong, cách nối: https://forum.bambulab.com/t/cyberbrick-linear-actuator-electric-pushrod/252221
- Cẩu CyberBrick dùng xi-lanh cổng servo: https://makerworld.com/en/community/post/1844019
- Con lăn ép lưng thanh răng (cơ cấu lái): https://patents.google.com/patent/US4215591 , https://patents.google.com/patent/US9469333
- Xi-lanh in 3D ty ren (độ rơ ty ren thường): https://hackster.io/news/3d-print-your-own-linear-actuators-bce586a10766 , https://www.instructables.com/Linear-Actuator-V2
- Máy xúc in 3D của Ivan Miranda (xi-lanh ty ren, chậm, dễ gãy): https://hackaday.com/tag/digger/
- EEZYbotARM MK2: https://www.myminifactory.com/object/3d-print-46620

Ghi chú: các trang MakerWorld/Printables chặn đọc tự động – thông tin lấy từ đoạn trích tìm kiếm; license từng mẫu **chưa kiểm** (xem trước khi dùng file, theo chính sách phi thương mại).
