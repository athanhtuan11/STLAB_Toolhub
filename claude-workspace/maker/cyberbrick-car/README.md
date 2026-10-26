# cyberbrick-car – xe điều khiển thể thao (CyberBrick)

Xe coupé gầm thấp, cầu sau chủ động (hộp số 2 trục ra, **không vi sai**), lái servo kiểu Ackermann. Điều khiển bằng
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
| Truyền động | động cơ 030 (LA024) + bộ bánh răng 2 trục **LA013 1:21** (khuyên dùng; có 1:37/1:48/…) – trục ra double-D làm luôn trục bánh sau |
| Lái | servo **PG001** (CyberBrick) hoặc **MG90S** (mua ngoài) – giá servo dùng chung; chốt lái trước tâm bánh 7 mm (caster) |
| Thân | dáng **GT bo tròn** (đường vai, kính nghiêng) + **kính khắc chìm 0,4 mm**; gắn bằng 4 cặp nam châm 4 × 2 mm (tháo nhanh) |
| In | 3 bàn, **~7 h 15, ~114,6 g** Bambu PETG Basic (số liệu luôn mới: [BOM.md](BOM.md)); **không support** |

Tốc độ ước tính (chưa đo): 030 không tải 10 500 vòng/phút ±10 % (8 V), định mức 6 900 → qua 1:21 ≈ 330–500 vòng/phút ở
bánh Φ33,7 → **≈ 0,6–0,9 m/s**. TODO: đo thật.

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
1. Lắp hộp số 2 trục (LA013 + 030) theo hướng dẫn chính hãng `Assembly_Guide_of_Dual_Axis_030_Reduction_Motor.pdf`.
2. Đặt hộp số vào cửa sổ sàn giữa 2 vách, chốt định vị vào lỗ vỏ, bắt thanh chặn trên (2 × M2.5 × 6).
3. Ép 2 vành sau lên trục double-D.
4. Khớp lái: M2.5 × 16 làm chốt lái (từ trên xuống tai dưới sàn). Luồn trục vành trước qua lỗ khớp lái, đặt long đen
   và bắt vít M2.5 × 6 vào đầu trục.
5. Thanh giằng: 2 × M2.5 × 6 vào đầu tay lái. Servo luồn từ sau ra trước qua giá, bắt 2 × M2 × 8, đưa về giữa,
   lắp horn hướng lên. Chốt horn: khoan lỗ ngoài cùng của horn Φ2,0 mm, vít M2 × 8 làm chốt vào khe thanh giằng.
6. Bộ thu (4 × M2.5 × 6 từ dưới sàn), công tắc (2 × M2 × 6), pin vào khay (TODO dây velcro).
7. Dây: servo → S1, động cơ → cổng M (theo sơ đồ chính hãng xe Truck); 8 nam châm (để ý cực hút nhau).

## TODO (cần đo/hỏi trước khi in khớp chặt)
- Trục ra **bộ 2 trục** (LA013): cửa hàng Bambu không ghi số. Đo theo tỉ lệ ảnh hướng dẫn lắp chính hãng
  (`Assembly_Guide_of_Dual_Axis_030_Reduction_Motor.pdf`, hình chiếu cạnh, lấy bề dày vỏ 18 mm làm thước):
  **lồi ≈ 9 mm mỗi bên (±1 mm)**, Φ ≈ 5,3–5,6, có mặt dẹt + lỗ ở đầu trục. Moay-ơ bánh sau ôm 8,4 mm – đủ.
  TODO đo thật khi có hàng.
- Vỏ hộp số 2 trục: có lỗ Φ4 ở cùng vị trí bộ 1 trục không (chốt định vị trên vách sàn).
- Lốp LA027 ôm vành: kiểm độ chặt (vành Φ26,8/Φ30,1).
- Bộ phát: chọn cấu hình kênh (lái/ga) trong app CyberBrick.

## Mua (ngoài bộ phát/thu đã có)
Động cơ 030 LA024, bộ bánh răng 2 trục LA013 (1:21), 4 lốp LA027, servo PG001 hoặc MG90S, pin PC003 + công tắc XA007,
8 nam châm 4 × 2 mm, vít (bảng vít trong [BOM.md](BOM.md)).

## Lịch sử sửa
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
