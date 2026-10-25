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

## 4b. Hướng bổ sung (nghiên cứu vòng 2, 2026-10-25)

### E. Bánh răng quạt tại khớp (giữ gần hết cụm truyền động hiện có) – **khuyến nghị mới**
- Thay thanh răng thẳng bằng **bánh răng quạt** (sector) gắn chặt vào cần, đồng tâm chốt khớp. Vỏ xi-lanh **bắt cứng** vào khâu trước
  (không xoay quanh chốt nữa); bánh răng z10 hiện có ăn khớp với quạt. Thanh răng = quạt bán kính vô hạn → chỉ "uốn cong" nó lại.
- Trục bánh vít hiện song song Y = song song các chốt khớp → hình học tương thích.
- Ưu: **không còn chi tiết trượt** → hết lệch; giữ motor 030 + hộp số, trục vít tự hãm, bánh vít + z10 (in lại vỏ + quạt);
  khoảng cách tâm cố định nên không có lực đẩy thanh răng ra khỏi răng như hiện tại.
- Nhược: toàn bộ mô-men khớp đi qua răng m1 bằng nhựa → phải tính tải răng (TODO: mô-men khớp lớn nhất, có thể cần mặt răng rộng hơn
  hoặc m1,5); mất kiểu dáng "xi-lanh". Cộng đồng có tay máy in 3D dùng trục vít ở khớp (bài báo Plymouth 2023, 3 bậc, trục vít giữ tư thế
  không cần điện) và hộp số trục vít in 30:1 tự hãm (góc xoắn < 5°, ~3 Nm theo người đăng, PLA) – không có file quạt sẵn, phải tự vẽ.

### F. Tay quay + thanh truyền (kiểu servo RC kéo thanh nối)
- Hộp số + trục vít quay một **tay quay** gắn trên khâu trước; thanh nối 2 đầu chốt nối tay quay với cần (cơ cấu 4 khâu).
- Ưu: chỉ có chốt xoay, không trượt; in đơn giản. Nhược: tỉ số thay đổi theo góc, phải tránh điểm chết; rơ cộng dồn ở 4 chốt
  (chốt hiện có khe 0,3 mm/bên). Nguồn cộng đồng: so sánh slider-crank / bánh răng ở wiki thiết kế robot UT Austin.

### G. Cáp capstan / dây đai từ đế
- **Forte** (arXiv 2507.15693): tay 6 bậc in 3D, vai + khuỷu dùng **cáp thép capstan + dây đai**, giá vật liệu < 215 USD.
  Dây Dyneema DM20 được cộng đồng chuộng cho capstan.
- Dây đai GT2 từ motor ở đế: người làm báo **puly GT2 in bị nhảy răng khi mô-men lớn** → chuyển HTD 5M.
- Đánh giá: chính xác, nhẹ cần, nhưng phức tạp (căng cáp, quấn dây) – quá sức cho bài lắp của học sinh. Không khuyến nghị cho bản này.

### H. Lò xo bù trọng lực (bổ sung cho mọi phương án)
- Lò xo kéo/nén bù mô-men do trọng lượng cần → giảm tải motor và giảm lực tách răng; có thể làm A khả thi hơn.
- CyberBrick có sẵn lò xo nén BB007 (0,5 × 5 × 20 mm) và BB016 (0,6 × 8 × 20 mm), STEP trong `community/cyberbrick-official/models/`;
  độ cứng **TODO** (chưa có datasheet). Lò xo nén này cũng dùng được làm lực ép con lăn tựa lưng của phương án A.

### Khuyến nghị cập nhật
| Hướng | Sửa/in lại | Hết lệch? | Ghi chú |
|---|---|---|---|
| A con lăn + rãnh kín | Housing, Rack | Một phần | Nhanh nhất, thử trước nếu lệch kiểu (a) |
| **E bánh răng quạt** | Housing (bắt cứng), quạt thay Rack, điểm bắt trên Boom/Turret | **Có** | Giữ motor + bánh vít + z10; cần tính tải răng |
| B vít me ống lồng | Cả xi-lanh | Có | Giữ kiểu "pushrod", cộng đồng CyberBrick đã làm |
| F tay quay | Housing, thêm tay quay + thanh nối | Có | Tỉ số không đều |
| H lò xo bù | Thêm | – | Kết hợp với bất kỳ |

## 4c. Mổ xẻ Cyberbrick Excavator (MakerWorld 2371626) – 2026-10-25
Tuan tải `Cyberbrick+Excavator.zip` (75 STL, không kèm hướng dẫn/license). Đo bằng cắt lát STL (số đo ± 0,3 mm; module quạt là ước lượng):

**Khớp cần chính (boom – khớp chịu tải lớn nhất) = bánh răng quạt, KHÔNG dùng xi-lanh** → cùng ý tưởng phương án E.
- Quạt răng **liền khối ở gốc `boom`**, quét ~118°, bán kính đỉnh ≈ 25 mm, ~m1,1 (ước lượng), **mặt răng rộng ≈ 21 mm** (cả bề dày boom).
- Dẫn động: `boom_drive_gear` (m1 z30 + bánh răng con dài) → `boom_reduction_gear` (m1 z40 + z~15) → quạt. Giảm tốc nhiều cấp bánh răng thẳng,
  không trục vít (giữ tư thế nhờ hộp số motor – không tự hãm như trục vít của mình).
- Rút ra: quạt nhỏ (r ≈ 25 mm) đặt sát khớp, bánh răng dẫn đặt trên khâu trước, mặt răng rộng để chịu mô-men.

**Tay gầu + gầu = xi-lanh vít me (phương án B)**:
- `cylinder_Base`: ống tròn Ø16,8 dài 90 mm. Nửa dưới lỗ Ø12,6 chứa motor N20 (BOM: N20 trục ren M3 × 45, 1000 rpm);
  nửa trên lỗ **không tròn** (~12,6 × 10,6, có gờ) làm rãnh chống xoay cho piston.
- `push_rod`: đầu piston 12 × 9 mm có **hốc đai ốc vuông M3 (6,1 × 6,1)**; thân ty tiết diện chữ D 8 × 7,3 mm, lỗ dọc Ø4,4 cho ty ren chui vào.
  → Ty được dẫn **2 điểm** (piston trong ống + miệng ống), lực đi dọc trục, không có lực tách răng.
- Gầu dùng thêm `dogbone` + `Hlink` (cơ cấu 4 khâu) để khuếch đại góc quay từ hành trình xi-lanh ngắn.

**So với pushrod-arm**: thanh răng của mình chỉ dẫn 1 rãnh hở + lực tách răng; máy xúc tránh hẳn thanh răng – khớp tải lớn dùng quạt,
khớp nhẹ dùng vít me trong ống kín. Củng cố khuyến nghị: **khuỷu → E (quạt)**, nếu muốn giữ dáng xi-lanh → B kiểu ống Ø16,8 + đai ốc vuông.

**Bài học bố cục cho E** (từ thử dựng quạt trên model, 2026-10-25): tâm z10 hiện cách chốt E 61,6 mm → quạt m1 z113 (r 56,5), quét 78° khi khuỷu
đi hết hành trình; **đặt ở mặt phẳng giữa sẽ đâm vào thân Boom001** (Boom đặc ở góc 220–240° quanh E, r 40–58). Hai cách: (1) quạt bắt ngoài
`Forearm_plate_R` (y −20…−15), dời cụm xi-lanh ngang −17,75 mm (script concept `freecad/scripts/render_concept_sector.py`, chưa chạy);
(2) như máy xúc: dời bánh răng dẫn sát khớp → quạt nhỏ r ≈ 25–30 mm, thêm 1 cấp giảm tốc (vẽ lại vỏ nhiều hơn).

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
- Tay máy trục vít 3 bậc in 3D (Plymouth 2023): https://www.astesj.com/v08/i05/p09/
- Hộp số trục vít in 30:1 tự hãm: https://3dgo.app/models/makerworld/674621
- Forte – capstan + dây đai: https://arxiv.org/abs/2507.15693v1 ; giới thiệu capstan: https://aaronnewmanb.substack.com/p/capstan-drives-affordable-precision
- Puly GT2 in nhảy răng ở khớp tay máy: https://michaelteeuw.nl/tag/belt
- Slider-crank vs bánh răng (UT Austin): https://cloud.wikis.utexas.edu/wiki/spaces/RMD/pages/667877618
- Bù trọng lực bằng lò xo/đối trọng: https://la.disneyresearch.com/wp-content/uploads/A-Passively-Safe-and-Gravity-Counterbalanced-Anthropomorphic-Robot-Arm-Paper.pdf

Ghi chú: các trang MakerWorld/Printables chặn đọc tự động – thông tin lấy từ đoạn trích tìm kiếm; license từng mẫu **chưa kiểm** (xem trước khi dùng file, theo chính sách phi thương mại).
