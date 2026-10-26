# cyberbrick-car – xe điều khiển thể thao (CyberBrick)

Xe coupé gầm thấp, cầu sau chủ động (**2 động cơ**, mỗi bánh sau 1 động cơ qua hộp số 1 trục, **không vi sai**), lái servo kiểu Ackermann. Điều khiển bằng
bộ phát/thu CyberBrick (XA003 + XA004/XA005). Model **sinh từ tham số**: `freecad/scripts/build_car.py`
(sửa tham số `P` ở đầu file rồi chạy lại – không sửa tay trong FreeCAD). Ảnh: `freecad/images/`.

## An toàn
- Pin PC003 là **Li-ion 2S 7,4 V**: không sạc khi không có người trông, không để chập cổng XH2.54, không đè/đâm thủng pin.
  Khoang pin hở thoáng (không bọc kín sát pin).
- Bộ thu XA004 cần 7,4–12,6 V, tối đa 3 A; mỗi cổng động cơ tối đa 1 A (datasheet `Accessories Specification.pdf`).
- Lần chạy đầu: kê bánh lên, chạy chậm, kiểm nhiệt động cơ 030 và servo (servo PG001 có ly hợp, ngắt khi kẹt 5 s).

## Thông số (model hiện tại, 2026-10-26)
| | |
|---|---|
| Dài × rộng × cao | thân 222,5 × 88,6 mm, nóc cao 57,7 mm so với mặt đất (đo trên lưới); chiều dài cơ sở 140 mm, vệt bánh 72 mm |
| Bánh | lốp CyberBrick LA027 Φ33,7 × 13,85 mm trên vành in (5 nan) |
| Truyền động | **2 bộ động cơ 030 (LA024) kèm hộp số 1 trục** (STEP chính hãng), mỗi bánh sau 1 động cơ; trục ra lồi 8,1 mm vào moay-ơ bánh sau; hộp số dựng lưng tựa lưng |
| Lái | servo **PG001** (CyberBrick) hoặc **MG90S** (mua ngoài) – giá servo dùng chung; chốt lái trước tâm bánh 7 mm (caster) |
| Thân | dáng **GT bo tròn** (đường vai, kính nghiêng) + **kính khắc chìm 0,4 mm**; gắn bằng 4 cặp nam châm 4 × 2 mm (tháo nhanh) |
| In | 3 bàn, **~7 h 04, ~114,3 g** Bambu PETG Basic (số liệu luôn mới: [BOM.md](BOM.md)); **không support** |

Tốc độ ước tính (chưa đo): 030 không tải 10 500 vòng/phút ±10 % (8 V), định mức 6 900 → qua 1:21 (tạm tính; tỉ số của
bộ 1 trục: TODO kiểm) ≈ 330–500 vòng/phút ở bánh Φ33,7 → **≈ 0,6–0,9 m/s**. TODO: đo thật.

## Chọn servo lái
`P["servo_type"]` trong `build_car.py`: `"pg001"` (mặc định) hoặc `"mg90s"`; thử nhanh: `CAR_SERVO=mg90s freecadcmd build_car.py`.
Số đo từ STEP (PG001 chính hãng; MG90S GrabCAD – `community/grabcad/towerpro-mg90s/`):

| | PG001 | MG90S |
|---|---|---|
| Thân (dài × rộng) | 22,7 × 11,9 | 22,7 × 12,2 |
| Lỗ tai so với trục | −19,15 / +8,47 | −19,4 / +8,5 |
| Mặt trước tai → đỉnh trục | 12,22 | 11,75 |

Giá servo: mặt tựa theo MG90S; PG001 vít kéo áp vào giá (lệch 0,47 mm, horn vẫn còn khe). Lỗ vít M2 ở trung bình 2 loại.

## In (không support – chính sách STLab)
- **Thân in đứng, đuôi úp xuống bàn** (cao 222,5 mm; A1 tối đa 256 mm): vách gần như thẳng đứng nên tự in được.
  Đã vẽ để không cần support:
  - đuôi nở ≤ 45°;
  - trần trong ở mũi làm sống mái dốc 50°;
  - hốc bánh nhọn 45° phía trước;
  - gân nam châm mọc từ vỏ (50°), hốc giọt nước.
- Khớp lái in úp (mặt trên xuống bàn); trục bánh trước **in liền vành** (in đứng, chắc hơn trục nằm ngang).
- Kiểm: `printability.py` (mặt nhô + **kiểm theo lớp** giống slicer) – tất cả chi tiết sạch; Bambu cắt lớp PASS.

## Lắp (tóm tắt – chi tiết sẽ viết ASSEMBLY.md sau khi in thử)
1. Lắp 2 bộ động cơ 030 + hộp số 1 trục. Bộ phải = bộ trái lật úp (xoay 180° quanh trục X).
2. Đặt 2 hộp số lưng tựa lưng vào cửa sổ sàn giữa 2 vách (khe giữa 2 vỏ 0,4 mm; mặt vỏ phía trục ở |y| 18,2 mm; trục ra
   lồi 8,1 mm vào moay-ơ bánh sau, moay-ơ từ |y| 18,5 mm). Vách ngoài kẹp 2 bên: mỗi vách 2 chốt D3,6 vào 2 lỗ D4 mặt phía
   trục của vỏ; bắt thanh chặn trên dài hơn (2 × M2.5 × 6).
3. Ép 2 vành sau lên trục double-D.
4. Khớp lái: M2.5 × 16 làm chốt lái (từ trên xuống tai dưới sàn). Luồn trục vành trước qua lỗ khớp lái, đặt long đen
   và bắt vít M2.5 × 6 vào đầu trục.
5. Thanh giằng: 2 × M2.5 × 6 vào đầu tay lái. Servo luồn từ sau ra trước qua giá, bắt 2 × M2 × 8, đưa về giữa,
   lắp horn hướng lên. Chốt horn: khoan lỗ ngoài cùng của horn Φ2,0 mm, vít M2 × 8 làm chốt vào khe thanh giằng.
6. Bộ thu (4 × M2.5 × 6 từ dưới sàn), công tắc (2 × M2 × 6). Pin PC003 **đứng cạnh bên trái động cơ trái** (nằm ngang
   thì lấn động cơ 4 mm): x 45,5..96,7 mm, đỉnh pin cao 35,1 mm, thấp hơn vai thân (37 mm). Giữ bằng chân sau, chân
   trước; vách ngoài cao 20 mm, vách trong chỉ ở đoạn trước động cơ (TODO dây velcro).
7. Dây: servo → S1; động cơ trái → M1, động cơ phải → M2 của bộ thu (mỗi cổng tối đa 1 A, tổng 3 A theo datasheet).
   Động cơ phải quay ngược chiều: đảo chiều trong app CyberBrick hoặc đảo 2 dây. 8 nam châm (để ý cực hút nhau).

## TODO (cần đo/hỏi trước khi in khớp chặt)
- Dòng khóa (stall) của động cơ 030 LA024: chưa có số liệu. Cần để kiểm không vượt 1 A mỗi cổng M của XA004.
- Tỉ số truyền bộ hộp số 1 trục: chưa có số (tốc độ đang tính tạm theo 1:21). Kiểm trước khi chốt.
- App CyberBrick: gán 1 kênh ga cho cả 2 cổng M (M1, M2) và đảo chiều động cơ phải.
- Bộ phát: chọn cấu hình kênh (lái/ga) trong app CyberBrick.
- Lốp LA027 ôm vành: kiểm độ chặt (vành Φ26,8/Φ30,1).

## Mua (ngoài bộ phát/thu đã có)
2 bộ động cơ 030 LA024 kèm hộp số 1 trục, 4 lốp LA027, servo PG001 hoặc MG90S, pin PC003 + công tắc XA007,
8 nam châm 4 × 2 mm, vít (bảng vít trong [BOM.md](BOM.md)).

## Lịch sử sửa
- 2026-10-26 (2): **thiết kế lại 2 motor 1 trục** (Tuan yêu cầu). Bỏ hộp số 2 trục LA013 (không có file/sơ đồ chính
  hãng); thay bằng 2 bộ động cơ 030 LA024 + hộp số 1 trục (STEP chính hãng), mỗi bánh sau 1 động cơ. Vẫn lái servo
  Ackermann, không vi sai. Hai hộp số lưng tựa lưng, khe 0,4 mm. Pin PC003 đứng cạnh động cơ trái (x 45,5..96,7 mm).
  Vách kẹp kép (chốt D3,6 vào lỗ D4 mặt phía trục). Cửa sổ giảm tải dưới pin bo, thêm cửa sổ dưới 2 động cơ. Trụ nam
  châm sau x -14 → -15,5; trụ trước y ±33 → ±35,5. Kiểm: va chạm không chồng (khe pin–thân 0,7 mm, hộp số–sàn 0,2 mm),
  test 6/6, cắt lớp Bambu PASS không support: P1 thân 4 h 18 / 59,5 g; P2 sàn + lái 1 h 32 / 35,3 g; P3 bánh 1 h 14 /
  19,5 g; cả xe 7 h 04 / 114,3 g. Ảnh mới: `freecad/images/two-motor/`. `freecad/scripts/gearbox_housing_dual.py`
  (vỏ hộp số 2 trục tự in): không còn dùng từ 2026-10-26, giữ file. Động cơ phải đảo chiều (xem bước Lắp 7).
- 2026-10-26: **thân GT** (Tuan chọn: GT bo tròn + kính khắc chìm; không cánh gió/LED). Mặt cắt nửa trên = B-spline:
  sườn đứng tới vai → vai bo r ≤ 1,4 mm → kính nghiêng → mép mái (`upper_curve` trong `build_car.py`). Kính hông/lái/sau
  khắc sâu `win_d` 0,4 mm (vỏ còn 0,9 mm = 2 đường). Cắt lớp PASS, không support: P1 thân 4 h 18, 59,9 g (trước 63,3 g);
  cả xe 7 h 15, 114,6 g. Concept: `freecad/scripts/concept_gt_body.py`, ảnh `freecad/images/concept-gt/`.
  Ảnh render CLI: `freecad/scripts/render_car_cli.py` → `freecad/images/car-*.png`, `contact-sheet.png`.
- 2026-10-23 (2): tiết kiệm nhựa 127 → 118 g:
  - Vỏ 1,6 → 1,3 mm. Thử 1,2 mm thì slicer báo floating.
  - Sàn 3 → 2,4 mm, thêm 6 cửa sổ giảm tải.
  - Infill: sàn 25 → 15 %, vành 40 → 20 %.

  Chắn bùn phồng che kín bánh. Trước đó hốc bánh xuyên thủng nóc chắn bùn và để lại vỏ mỏng mà Bambu báo cantilever.
  Trần cửa sổ giá servo đổi thành mái 45°. Quy trình mới: kiểm hết rồi mới cắt lớp.
- 2026-10-23: v0.2 – in không support (thân in đứng, khớp lái mới trục in liền vành, gân nam châm, hốc bánh 45°),
  giá servo dùng chung PG001/MG90S, `safe_edit` bắt được 3 boolean hỏng âm thầm (removeSplitter lộn ngược solid,
  mảnh vụn, mặt gần trùng). Kiểm nhanh WARN (hộp số ước bằng bao lồi), cắt lớp PASS 7 h 17, 127 g.
- 2026-10-23: v0.1 – bố cục khung gầm + thân coupé đầu tiên.
