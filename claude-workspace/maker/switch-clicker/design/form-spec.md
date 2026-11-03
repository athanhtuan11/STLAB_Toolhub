# switch-clicker – form spec (bước 0 "Giao diện trước", 2026-11-02)

Móc khóa clicker gắn 1 switch bàn phím cơ chuẩn Cherry MX. 1 THÂN chung + nhiều KEYCAP thay được. Bán quà Đức Trọng/Đà Lạt + đăng MakerWorld. Ảnh phác bằng Blender (`concepts/make_concepts.py`), CHƯA phải CAD.

## GIẢ ĐỊNH (chưa kiểm số thật – kỹ sư/Claude chốt ở CAD)
- Switch vẽ là khối 15,6 × 15,6 mm: phần dưới tấm 5,5 mm, phần trên tấm 5,5 mm, trụ chữ thập 4 × 4 × 4 mm. TODO đo switch thật.
- Lỗ chuẩn 14,0 × 14,0 mm, tấm kẹp 1,5 mm (theo datasheet Cherry, Tuan nêu). Số lỗ/khe/ngàm giữ switch, khe cắm keycap: KHÔNG chốt ở đây – lấy từ `fit-library`, Claude chốt ở CAD.
- Hành trình nút (travel) ~4 mm: TODO theo loại switch Tuan mua; ảnh phác để chân keycap cách mặt thân 1,5 mm.

## Ngôn ngữ hình khối
Viên đá cuội mềm nằm dưới một "nụ" tạo hình thay được; thân tối giản trung tính để keycap là nhân vật. Ba từ khóa: **mềm – đáng bóp – quà nhỏ**.

## 3 hướng dáng thân (ảnh `variants.png`)
Cùng chiều cao 14 mm, cùng vòng treo (OD 12 / lỗ Ø 5,4 / dày 4 mm, ngang mặt trên), cùng nắp đáy 2,2 mm.

| | Hình | Kích thước (mm) | Ưu | Nhược |
|---|---|---|---|---|
| A. Đá cuội | hộp vuông bo R4,8 | 34 × 30 × 14 | cầm vừa ngón cái, đặt đứng vững, in gọn (bàn nhỏ) | hơi "hộp" |
| B. Lục giác bo | lục giác R20, bo R5,5 | ~40 × 35 × 14 | nhìn lạ, hợp tổ ong/Đà Lạt | rộng nhất, tốn nhựa, tay khó xác định hướng |
| C. Viên thuốc | capsule bo R6,2 | 46 × 26 × 14 | ngón cái gác thoải mái, vòng treo cân đối | dài, ngồi trong túi dễ vướng; keycap lệch tâm 5 mm |

**Khuyến nghị A**: nhỏ nhất, 1 tấm in được nhiều chiếc/bàn, trình bày đẹp cạnh mọi keycap, ngón cái bao trọn. C là phương án 2 nếu Tuan muốn "dễ bấm" hơn.

## Chi tiết thân A (khuyến nghị)
- Khối chính 34 × 30 × 14, bo cạnh trên R4,8 (chỗ cầm; học sinh/người lớn không có cạnh sắc, tối thiểu bo 1 mm mọi chỗ).
- Cạnh chạm bàn (nắp đáy): vát 0,8 mm thay vì bo tròn. Ảnh phác vẽ bo cả đáy – CAD sửa theo đây.
- Đường chia màu/ráp: nằm ngang ở z = 2,2 mm từ đáy; nắp đáy (vòng 2,2 mm) màu khác = viền "xanh thông" nhìn như đường chỉ.
- Nắp đáy tháo được để thay switch: 2 vít hoặc ngàm khóa (TODO chốt ở CAD theo fit-library; 1 loại vít duy nhất, lắp một chiều: 1 góc chéo/ 1 chốt lệch). Khắc dấu mũi tên ▲ sâu 0,6 mm, nét ≥ 0,8 mm ở nắp đáy và ở thân để khớp.
- Mặt trên: 1 hốc vuông 14,0 × 14,0 mm tại tâm (tấm kẹp 1,5 mm); switch đặt từ dưới lên.
- Vòng treo: OD 12, lỗ Ø 5,4 (vòng khóa Ø ≤ 5 mm), dày 4 mm, nối vào góc sau trái, bo cạnh R1.
- Lỗ thoát nhiệt: không cần (switch cơ không phát nhiệt, không có pin). Không có linh kiện điện → không rủi ro pin Li-ion.
- Logo STLAB: khắc lõm sâu 0,6 mm, nét ≥ 0,8 mm, mặt dưới nắp đáy (không lộ khi cầm).
- Khoang trong: chừa chỗ chân switch ~3,3 mm (TODO đo) + thành ≥ 1,6 mm.

## 4 keycap (ảnh `set4.png`, chân keycap ở z = 15,5 mm; phủ ~22–24 mm)
Mỗi keycap là part riêng, **1 màu**; phần cắm vào trụ chữ thập (khe do Claude chốt ở CAD – chỉ coi là khoang ngửa).

| Keycap | Kích thước (rộng × sâu × cao trên chân) | Hình khối | Màu gợi ý (PETG Basic, Tuan tự chuẩn bị) |
|---|---|---|---|
| Hạt cà phê | 24 × 19 × 11,5 | elipsoid dẹt, rãnh chữ S rộng 1,9 × sâu 1,2 | nâu (TODO tên màu hãng) |
| Bông atiso | Ø 21 × 13 | 3 lớp cánh (11 / 9 / 6 cánh) + nụ giữa | xanh lá nhạt/ xanh xám (TODO) |
| Đầu dê chibi (Tết 2027) | 24 × 21 × 11 (sừng cao 15) | đầu bầu như dê flexi (cùng ngôn ngữ: tai dẹt, mõm tròn, mắt to), sừng vàng 2 chiếc | đầu kem/trắng (TODO); sừng vàng PART RIÊNG cắm chốt; mắt/mũi: khắc lõm 0,6 (hoặc chấm bút) |
| Tròn trơn khắc tên | Ø 22 × 10 | trụ, bo R2,8 trên, chữ khắc lõm 0,6 sâu, nét ≥ 0,8 | đỏ Tết hoặc kem (TODO); chữ lõm tô bút nếu muốn |

Nguyên tắc: thân đen than (hoặc xám đậm) + nắp đáy xanh thông là cố định; chỉ keycap đổi màu. ≤ 3 màu mỗi chiếc + 1 điểm nhấn (sừng vàng). Bề mặt: mặt tiếp bàn là Textured PEI (hạt mịn), mặt trên thân và keycap có thể khác nhau tùy hướng in (mục dưới).

## Hướng in (không support, 1 màu/part)
- **Thân (phần trên)**: in LẬT – mặt trên (tấm kẹp) úp xuống bàn, hốc switch và khoang rỗng quay lên, không support. Mặt trên ra Textured PEI (nhám đều, chấp nhận được; mặt đáy được tha). Bo R4,8 cắt theo tiếp tuyến 45°, vát 0,8 mm ở phần chạm bàn đầu tiên – tránh bo tròn tiếp bàn. Vòng treo ở mặt trên nên nằm sát bàn, in tốt.
- **Nắp đáy**: in nằm phẳng, 1 lớp 2,2 mm, viền vát 0,8.
- **Keycap**: in LẬT – đỉnh keycap úp xuống bàn, khoang chân ngửa lên, không support. Đỉnh bo thì cắt phẳng một mặt ~8 mm cho dính bàn. Bông atiso: cánh nghiêng ≥ 45° so với bàn khi lật nên in được, đỉnh cánh có thể mềm nét. Chữ khắc ở keycap tròn là cầu qua khe < 3 mm, ổn.
- **Sừng dê**: part nhỏ, in nằm, brim; chốt cắm Ø ≥ 2 mm vào lỗ đầu (khe theo fit-library).
- Bàn Bambu A1: 1 màu/ lần in, không AMS → mỗi màu một plate.

## Rủi ro
1. Switch thật khác giả định (cao, chân, ngàm clip MX 3-pin/5-pin): thân có thể dày thêm 1–2 mm hoặc keycap cao hơn. Cần switch thật trước khi chốt CAD.
2. Ngàm chữ thập keycap là chi tiết nhỏ nhất, dễ nứt/ lỏng trong PETG → in 3 mẫu thử độ khít trước.
3. Đỉnh cánh atiso và sừng dê nhỏ, dễ gãy khi bấm/rơi (chi tiết mảnh < 2 mm) → làm sừng ngắn, đầu tròn.
4. Chiều cao tổng ~30 mm (thân 14 + keycap), nhô khi ở trong túi; có thể hạ thân xuống 12 mm nếu switch đủ thấp.
5. Chữ khắc trên mặt textured/ lật: đáy bàn nhám làm chữ mờ → khắc sâu 0,6 + nét ≥ 0,8, có thể tô bút.
6. Tiếng "tạch" lớn có thể hơi ồn ở lớp học – mua switch tactile/linear êm nếu cần (TODO).
7. Không chép clicker/keycap thương mại; hình dáng đều vẽ mới.

## Cần quyết
1. Chọn hướng A (khuyến nghị) / B / C.
2. Loại switch Tuan sẽ mua (cho tôi chụp ảnh/ số đo: 3-pin hay 5-pin, độ cao) – số lỗ/khe chốt sau.
3. Đầu dê: sừng vàng part riêng (cần 2 màu, 2 plate) hay chỉ 1 màu?
4. Thân đen than + nắp xanh thông có hợp gu không (hay thân trắng kem)?

## Việc kỹ sư phải dựng (sau khi Tuan duyệt)
- build_body.py thân A (2 part: thân, nắp đáy) + vòng treo; hốc 14,0 × 14,0, tấm 1,5.
- 4 keycap + sừng dê + khe cắm trụ chữ thập (fit-library), dấu lắp ▲.
- print.yaml: 1 plate/ màu; kiểm printability/ slice lật.

## Đã sửa gì sau khi nhìn ảnh
Vòng 1 (xem set4/q34): switch trắng lộ ra như cái bệ dưới keycap, keycap nhìn lơ lửng. Sửa: hạ chân keycap từ 2,5 xuống 1,5 mm trên mặt thân, nới hạt cà phê (25 × 20,8) và đầu dê (25 × 22) để váy keycap phủ kín góc switch 15,6 mm (đường chéo 22 mm) ; đế atiso Ø 22,4. Rãnh hạt cà phê sâu hơn (r 1,15). Ảnh nổ ban đầu mất nắp đáy (chìm dưới sàn) → nâng cả cụm lên. Chỉnh khung camera (quá xa). Tồn tại: đầu dê hơi giống heo (mõm to) → khi dựng CAD thu mõm, thêm sừng/ tai dài như dê flexi; ảnh 5 thước chưa vẽ keycap tròn; ô viền đen ở contact sheet chỉ là lỗi cắt ảnh.
Kích thước keycap trong bảng ở trên theo bản chưa sửa: dùng số vòng 2 (cà phê 25 × 21 × 11,5, dê 25 × 22 × 11, atiso Ø 22,4).
