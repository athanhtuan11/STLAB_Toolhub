# sliding-wardrobe – Tủ âm tường 2 cánh lùa, khung sắt + tấm nhựa trong

Tủ treo đồ nằm giữa 3 bức tường (trái, sau, phải). Không có vách ván: phần chịu lực là **khung sắt hộp**.
Mặt trước là **2 cánh lùa**. Mỗi cánh ghép từ **4 tấm nhựa trong nhà 400 × 2900 × 10** (tổng 8 tấm), bắt vít lên
**mặt trước khung cánh** (Tuan 2026-11-26, thay lam sóng 220 × 2900 × 26). Bên trong chỉ treo đồ bằng **ống tròn Ø27**.

**Hệ lùa (Tuan 2026-11-11, bản cuối):** có **bệ tủ cao 40** phủ cả lòng tủ, 2 thanh U nằm **chìm ngang mặt bệ** → sàn ngoài phẳng, không vấp.
- **Dưới chịu tải:** 2 thanh **thép U chấn 40 × 40** nằm ngửa trên sàn (vật tư dễ mua). Mỗi cánh có 4 bánh 608 bọc POM chạy trong lòng U.
- **Trên giữ đứng:** **ray hộp 40 × 40** anh đã có, cùng xe treo. Xe treo **không chịu tải**, chỉ giữ cánh đứng thẳng và chống nhảy ray.

Lịch sử phương án:
- `backup/2026-11-26-truoc-tam-nhua/`: bản lam sóng 220 × 2900 × 26 (7 thanh/cánh, viền 20 × 40 không sống đứng, 2 dầm đầu
  40 × 40 ở ray trên, 13 bản đế 60 × 60 × 4). Bỏ vì Tuan đổi cánh sang tấm nhựa 400 × 2900 × 10 (2026-11-26).
- `backup/2026-11-11-truoc-2-canh-treo/`: bản 4 cánh, bánh đỡ dưới.
- `backup/2026-11-11-truoc-ray-u-duoi/`: bản 2 cánh treo hoàn toàn + dẫn hướng sàn giữa. Bỏ vì không tìm được dẫn hướng dưới,
  và xe treo chịu ≥ 65 kg/xe vừa ray 40 × 40 khó mua.
- `backup/2026-11-09-v1-than-van-mfc/`: bản v1 thân ván MFC.

## Lệnh

```text
cd design
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P build_wardrobe.py -- --out renders
python draw_hanging.py     # 12 mặt cắt ray (trên + dưới), 13 mặt bằng hành trình
python draw_plans.py       # 10 khung sắt, 11 cánh + mặt bằng + mặt cắt, bom.csv, 00-contact-sheet
```

Ảnh 3D tổng hợp: `design/renders/00-3d-tong-hop.png` (09 = cụm bánh nhấc lên trên U). Xem xoay tự do: mở `design/wardrobe.blend`.

```text
```

Sửa `P` trong `build_wardrobe.py` (W sau khi đo, `panel_kg` sau khi cân 1 tấm nhựa, số đo U/bánh/ray thật) rồi chạy lại.
Script kiểm 17 điều kiện, tất cả đang PASS. Ảnh 3D tổng hợp: `design/renders/00-3d-tong-hop.png`.

## Vì sao chọn "U dưới chịu tải + ray trên giữ đứng"

Cánh khoảng **39 kg** (tấm nhựa ~5 kg), **cao 2,90 m**. Tách việc cho hai ray:

| Việc | Ai làm | Vì sao chắc |
| --- | --- | --- |
| Đỡ cánh ~39 kg | **4 bánh/cánh lăn trong lòng U chấn** (nên ≥ 15 kg/bánh) | Tải xuống thẳng sàn. Sàn đỡ suốt chiều dài U nên U không võng, bánh 608 dễ mua và rẻ |
| Giữ chân cánh không lắc | **Thành U** ôm càng bánh | Càng 30 trong lòng U 36 → chân cánh chỉ lắc ±3 mm, 2 lớp cánh cách nhau 10 (khe) không cọ |
| Giữ đầu cánh đứng thẳng | **Xe treo trong ray hộp 40 × 40** | Xe treo hở 3 mm trên mép ray nên không gánh tải; loại xe treo nào vừa ray cũng dùng được |
| Chống nhấc cánh khỏi ray | Xe treo kín trong ray hộp | Nhấc cánh tối đa ~5 mm là xe treo chạm nóc ray; bánh cần nhấc 38 mm mới thoát được U (kiểm `chong_nhay`) |

Nghiên cứu trước đó (vẫn đúng): cánh **chỉ treo trên mà không có gì giữ chân thì đung đưa như con lắc**
([Pinky's Iron Doors](https://pinkysirondoors.com/blogs/specialty-doors/bottom-track-for-sliding-barn-doors-a-must-have-or-a-nice-to-have)).
Các bộ treo hãng đều kèm dẫn hướng sàn
([Hager](https://www.hagerco.com/Files/Images/Images/Instructions/9613RS%20&%209614RS%20[60lb%20By-Pass%20Sliding%20Door%20Hardware%20Set%20Installation%20Instructions]%20[4].pdf),
[Häfele EKU Porta 100 kg](https://www.build.com/hafele-941-00-005/s387211); Häfele chỉ cho cánh cao ≤ 2,7 m).
Ở bản này tải nằm ở U dưới, xe treo trên chỉ giữ đứng.

## Bệ tủ – che ray và bánh (Tuan 2026-11-11: "U trên sàn đi lại dễ vấp")

- **Bệ cao 40 = đúng chiều cao thanh U**, phủ toàn bộ lòng tủ (3000 × 680 phía sau 2 thanh U):
  3 dãn bệ **sắt hộp 20 × 40 đặt nằm** (cao 20, dày 1,4) đặt **đúng hàng cột** ở y = 125 (trước), 442,5 (giữa), 760 (sau).
  **Ván 18** (plywood/MFC chịu ẩm) bắt vít lên dãn, chêm ≤ 3 cho mặt ván bằng miệng U (kiểm `be_phang`). Ván khoét lỗ cho chân cột.
- 2 thanh U nằm **chìm ngang mặt bệ** ở mép trước; giữa 2 U hàn **hộp 20 × 40 đặt ĐỨNG** (cao 40 = miệng U, thay la 8 × 40 cũ)
  → mặt bệ liền một mặt phẳng.
- **Mặt trước bệ = tấm che ray dưới** (nhựa 10, cao 40, cùng mặt phẳng cánh ngoài), che hết thành U. Sàn phòng trước tủ để nguyên, phẳng.
- Đáy cánh cách mặt bệ (miệng U 40) chỉ 6 (đáy cánh 46) → bánh nằm trong lòng U, **không thấy bánh**.
- Lòng U nằm dưới cánh và sau tấm che dưới; hút bụi lòng U định kỳ qua khe khi mở cánh.
- Ống treo dưới (cao 1030 từ sàn) còn cách mặt bệ 990 – đồ dài ≤ ~850 vẫn thoải mái.

## Kích thước chính (W = 3000)

- **2 cánh × 4 tấm nhựa 400 × 2900 × 10** (8 tấm), mỗi cánh rộng **1600** (4 × 400), cao **2900**; **chồng mí 200**.
- Lùa 1 cánh hết cỡ: **mở nửa trái 1400** hoặc **mở nửa phải 1400**.
- **Dày cánh 50** (tấm 10 + khung 40); khe giữa 2 lớp cánh **10**; mặt trước cánh ngoài lùi vào 10 so với mép tường;
  cột trước lùi về y = 125.
- Cao độ từ sàn: miệng U 40 · đáy cánh 46 (hở 6) · đỉnh cánh 2946 · đáy ray trên 2971 · đỉnh ray 3011 · **đỉnh tủ (dầm đỉnh) 3051**
  (trước 3094).
- Tấm che ray: **trên** cao 99 (2952 → 3051), **dưới** cao 40 (0 → 40); cách mép cánh 6 (cánh chính không cọ).

## Ray dưới – U chấn 40 × 40 (chịu tải)

- 2 thanh **U chấn 40 × 40 × 2** (Tuan 2026-11-11: thép dày 2) dài 3000, nằm ngửa, mỗi lớp cánh 1 thanh, ở y = 20–60 và 80–120
  (khe 20 giữa 2 U). Đặt đúng dưới tâm ray trên (dọi dây).
- Bắt xuống sàn bằng **vít nở đầu bằng, khoan côn** cho đầu vít chìm phẳng lòng U (bánh lăn qua), khoảng 400 mm/vít. Sàn lệch thì
  chêm tôn dưới U cho thẳng và phẳng.
- **Đỡ U từ dưới:** cột đứng trên 3 dãn bệ 20 × 40 nằm (xem Bệ tủ); dãn bệ bắt nở M8 xuống sàn ~600/cái (18 cái).
  Thanh U trong nối vào dãn bệ trước bằng **7 bản mã chêm 5 × 20 × 40** (~500/cái). Bỏ 13 bản đế 60 × 60 × 4 cũ.
- **Chặn cuối cao su trong lòng U** ở 2 đầu (cụm bánh chạm thì dừng, mép cánh sát tường).
- **Cụm bánh** (2 cụm/cánh, tâm cách mép cánh 110): càng thép rộng 30 hàn dưới viền dưới; 2 bánh 608 bọc POM Ø32 × 12 cách nhau 60,
  trục bu lông M8. Có vít chỉnh cao để cân cánh thẳng đứng.
- **Tải mỗi bánh nên ≥ (khối lượng cánh ÷ 4) × 1,5 ≈ 15 kg** (cánh ~39 kg); Tuan tự chọn bánh phù hợp. Bạc đạn 608 trần chịu được nhiều hơn mức này; lớp POM bọc
  ngoài cần hỏi người bán tải/bánh (`TODO`, điền `wheel_kg`).

## Ray trên – ray hộp 40 × 40 (chỉ giữ đứng)

- **BỎ 2 dầm đầu 40 × 40 × 3000 + bắt dầm** (bản cũ). Nay **5 dầm đỉnh 40 × 40** (cao 3011 → 3051) kéo dài ra trước: đoạn đầu
  dài **105** tới mặt trước ray ngoài; nhịp đỡ ~740 (x = 20, 760, 1500, 2240, 2980).
- 2 ray hộp 40 × 40 × 3000 (anh đã có), mỗi lớp cánh 1 ray, **bắt thẳng dưới 5 dầm đỉnh** (ray cao 2971 → 3011, đỉnh tủ 3051).
- 2 xe treo/cánh, bu lông treo xuống bát treo bắt trên viền trên (tán rút ren M8). **Chỉnh đai ốc để bánh xe treo hở 3 mm trên mép ray**:
  xe treo không gánh tải, chỉ giữ đầu cánh.
- **Tấm che ray trên** (nhựa 10, cao 99 = 2952 → 3051, cùng mặt phẳng cánh ngoài): 2 mảnh 1499,5 nối ở giữa (x = 1500),
  bắt vào đầu 5 dầm đỉnh (hàn bịt đầu + tán rút ren M5) và thanh trước ray.
- **An toàn lắp:** thành ray dày 2, cạnh thanh ~3 → **KHOAN MỒI 3,3 + vít 4 × 12 đầu dù**, KHÔNG dùng vít tự khoan (mũi khoan lọt
  vào lòng U/ray làm chạm bánh).
- **Chặn cuối trong ray**: đầu cánh đóng (C1 ở tường trái, C2 ở tường phải) dùng **chặn có lẫy** giữ cánh đóng, đầu kia chặn cao su.
- **Lắp:** bắt U xuống sàn + dầm + ray trên → luồn xe treo vào ray → dựng cánh, đặt 4 bánh vào lòng U → nối bu lông xe treo với bát treo
  → chỉnh vít cụm bánh cho cánh đứng thẳng → chỉnh đai ốc xe treo hở 3 → lắp chặn cuối.

## Cánh tấm nhựa (Tuan 2026-11-26)

- **Tấm = nhựa trong nhà 400 × 2900 × 10**, 4 tấm/cánh (x = 0–400, 400–800, 800–1200, 1200–1600), **bắt vít lên MẶT TRƯỚC khung cánh**.
  Tổng 8 tấm cho 2 cánh + **1 tấm** cắt thành 4 mảnh 1499,5 làm 2 tấm che ray (mỗi tấm 2 mảnh) → **mua 9 tấm**.
- **Viền = sắt hộp 20 × 40 × 1,2 đặt nằm** (mặt 20 lộ ra trước, sâu 40): viền trên, viền dưới, 2 viền đứng; dài 1560 (ngang) và 2900 (đứng).
- Tấm có **hèm khóa bằng móc sắt** (Tuan 2026-11-26) → không cần sống đứng ở đường nối. Dùng **4 thanh ngang sắt hộp 20 × 40 đặt nằm**
  (sâu 40 = dày khung, mặt 20 sát sau tấm), dài 1560, tâm cao **638 / 1210 / 1782 / 2354** từ sàn (chia đều ~572).
  Móc hèm bắt vào viền trên/dưới + 4 thanh ngang. Bỏ 3 sống đứng và 4 giằng 13 × 26 cũ.
- **Dày cánh 50** = tấm 10 + khung 40. Khe giữa 2 lớp cánh 10.
- Khung cánh 20 × 40: ~30 m (viền + thanh ngang, cả 2 cánh; theo `bom.csv`).
- Dưới viền dưới hàn **2 càng bánh**; trên viền trên bắt **2 bát treo**.
- Khối lượng cánh ≈ **~39 kg/cánh** (tấm **~5 kg**, Tuan cân 2026-11-26) → bánh nên **≥ 15 kg/bánh**.
- Chống vênh: hàn/ghép trên mặt phẳng, kẹp chặt, đính chéo góc, **2 đường chéo lệch ≤ 2** mới chốt.
- Sơn: mài mối hàn → lót chống gỉ → đen mờ; sơn xong mới bắt tấm.
- `TODO`: vẽ lại bản vẽ gia công cánh (bảng cắt tấm, viền, thanh ngang, càng bánh, bát treo, lỗ khóa) sau khi anh duyệt
  và có tấm nhựa thật.

## Khóa + tay nắm


Tấm chỉ dày 10 → **mọi thứ chịu lực bắt vào sắt phía sau, không bắt vít chịu lực vào nhựa**.
- **Tay nắm: Tuan tự lắp** (2026-11-26), model không vẽ. Lưu ý khi lắp: dùng tay nắm âm, khay sâu ≤ 35 cho gọn trong lòng khung 40;
  tay nắm nổi trên C2 sẽ quẹt C1 (khe 10). Tránh vị trí 4 thanh ngang (cao 638 / 1210 / 1782 / 2354).
- **Khóa (tùy chọn)**: khóa ấn tủ cửa lùa ở chỗ chồng mí, nút xuyên tấm C1 tại x = 1410, cao 1160. **Thân khóa bắt lên ke L thép
  vít vào thanh ngang** ngay trên (cách 15), không treo vào nhựa. Chốt bắn ra sau qua khe 10, ăn 4 vào lỗ tấm C2 (sau lỗ là viền đứng C2).
  `TODO`: khóa mua cần **hành trình chốt ≥ 14**. Không cần khóa thì bỏ.

## Khung sắt (hộp 40 × 40 × 1,4)

- **3 khung đầy đủ** (cột trước + sau suốt sàn → đỉnh, cột giữa đỡ ống, dầm kệ, dầm đỉnh) ở x = 20, 1500, 2980.
  Cột trước ở y = 125 (sau mặt sau C2 y = 120), cột sau ở y = 760–800.
- **2 khung lửng** (không cột trước) ở x = 760 và 2240, để ống treo chỉ nhịp 700 (40 kg/ống: 67 MPa, võng 1,3 mm, PASS).
- **Ngang tường – tường:** chỉ còn kê trước và đỉnh trước 3000 (z 2260 và 3011). **Bỏ kê sau và đỉnh sau (2026-11-26)**:
  cột sau đã bắt bát L vào tường sau nên 2 thanh này trùng việc.
- **Chân cột:** 3 dãn bệ 20 × 40 đặt nằm dưới hàng cột (nở M8 ~600/cái). **Bỏ 13 bản đế 60 × 60 × 4.**
- **Cột sau** bắt **bát L 50 × 50 × 4** + nở M8 vào tường sau ở 2 độ cao **1500 và 2900** (10 bát cho 5 cột); Tuan xác nhận tường sau bắt nở được.
- **Dầm đỉnh:** bỏ 2 dầm đầu 40 × 40 × 3000 (xem Ray trên).
- Vật tư (`design/bom.csv`, tính lại 2026-11-26): hộp 40 × 40 **~47,6 m** (bớt ~12 m so với bản lam sóng, không kể 2 ray đã có),
  hộp 20 × 40 **~30 m** cho khung cánh (viền + thanh ngang) cộng **~12 m** cho bệ (3 dãn bệ + 1 hộp đứng giữa 2 U),
  U chấn 40 × 40 2 × 3 m, sắt **~139,5 kg** (theo độ dày giả định, `TODO` theo hàng mua).

| Khoang | Lọt lòng | Ống Ø27 (cao từ sàn) |
| --- | --- | --- |
| K1–K4 | ~700 mỗi khoang | 2050 + 1030 (treo 2 tầng) |
| Hộp nóc | kệ ván 17 ở cao 2300 | chăn mền, vali |

## Danh sách mua phụ kiện

| # | Phụ kiện | SL | Ghi chú |
| --- | --- | --- | --- |
| 1 | **Tấm nhựa trong nhà 400 × 2900 × 10** | **9 tấm** | 8 tấm làm 2 cánh (4/cánh) + 1 tấm cắt 4 mảnh 1499,5 làm 2 tấm che ray |
| 2 | **Thép U chấn 40 × 40 × 2**, dài 3 m | 2 | ray dưới chịu tải |
| 3 | **Bánh 608 bọc POM Ø32 × 12** (hoặc bánh ổ bi tương đương), bu lông trục M8 | 8 | Tuan tự chọn, nên ≥ 15 kg/bánh |
| 4 | Thép bản làm càng bánh (tự cắt hàn), rộng 30, vít chỉnh cao M8 | 4 cụm | `TODO` dày bản (bản cũ ghi 4–5 mm) |
| 5 | Ray hộp 40 × 40 dài 3 m | 2 | anh đã có |
| 6 | Xe treo vừa ray 40 × 40 (loại thường, không cần tải nặng) + bu lông treo | 4 | chỉ giữ đứng |
| 7 | Chặn cuối: trong ray trên (2 có lẫy + 2 cao su) + cao su trong lòng U (4) | 8 | |
| 8 | Vít 4 × 12 đầu dù (khoan mồi 3,3) bắt tấm che ray vào U/ray | 26 | ~250/vít, không dùng vít tự khoan |
| 9 | Vít nở đầu bằng (khoan côn) bắt U xuống sàn | 16 | đầu vít chìm phẳng lòng U |
| 10 | Khóa ấn (tùy chọn, hành trình ≥ 14, bắt ke L vào thanh ngang); tay nắm Tuan tự lắp | 1 | `TODO` chọn loại |
| 11 | Tán rút ren M8 (bát treo) + tán rút ren M5 (đầu 5 dầm đỉnh) + kìm rút | 4 + 5 | theo `bom.csv` |
| 12 | Ron chổi chống bụi mép chồng mí | 2 × 2,9 m | |
| 13 | Ống inox Ø27 + tai đỡ hàn (dài 698 mm/ống) | 8 ống | `TODO` dày ống: model ghi 1,0, bản cũ ghi 1,2 |
| 14 | Nở sắt M8 xuyên dãn bệ xuống sàn | 18 | ~600/cái |
| 15 | Bát L 50 × 50 × 4 + nở M8 bắt cột sau vào tường sau | 10 | 2 độ cao 1500 và 2900 × 5 cột |
| 16 | Bản mã chêm 5 × 20 × 40 (nối U trong vào dãn bệ trước) | 7 | ~500/cái |
| 17 | Sắt hộp 40 × 40 (cột, dầm, ngang) | ~47,6 m | 1,4 mm (giả định) |
| 18 | Sắt hộp 20 × 40 khung cánh (viền + 4 thanh ngang, 2 cánh) | ~30 m | 1,2 mm |
| 19 | Bệ tủ: sắt hộp 20 × 40 (3 dãn bệ 3 m + 1 hộp đứng giữa 2 U 3 m) | ~12 m | dãn bệ 1,4 mm |
| 20 | Ván 18 chịu ẩm 3000 × 680 (mặt bệ, khoét lỗ chân cột) | 1 tấm | mặt ván = miệng U |

## Mô phỏng trượt (Blender)

Mở `design/wardrobe.blend`, bấm **Space**: C1 lùa phải hết cỡ rồi đóng, rồi C2 lùa trái hết cỡ rồi đóng.
`TODO`: render lại video cho bản này (`--anim` + ffmpeg như bản cũ).

## TODO

- W thực tế.
- Cân 1 tấm nhựa 400 × 2900 × 10 thật → sửa `panel_kg` (Tuan: ~5 kg, đã sửa; cân chính xác nếu cần).
- Đo bánh POM (Ø, bề rộng, tải → `wheel_kg`), ray hộp (độ dày vách, khe đáy), xe treo (cao) → điền vào `P`, chạy lại.
- Dày ống inox Ø27: model 1,0, bản cũ 1,2 → xác nhận.
- Bản vẽ gia công cánh tấm nhựa (bảng cắt, viền, thanh ngang, càng bánh, bát treo, lỗ khóa).
- Tường sau ẩm thì chừa khe ~20 sau quần áo hoặc ốp tấm chống ẩm.

## An toàn

- Cánh **~39 kg, cao 2,90 m**: **2–3 người** dựng và lắp cánh. Lắp chặn cuối ở cả ray trên và U dưới trước khi lùa thử.
- Mép trước bệ cao 40 (như chân tủ) là tấm che ray dưới; lòng U nằm sau tấm che – hút bụi, không để vật cứng lọt vào.
- Tấm nhựa 400 × 2900: cắt/khoan trên mặt phẳng, đeo kính; khoan mồi 3,3 trước khi bắt vít 4 × 12 vào U/ray.
- Khung sắt **phải bắt nở vào tường** ở cả 3 phía + sàn. Khoan tường/sàn: dò đường điện, ống nước âm trước.
- Trẻ nhỏ dễ kẹt tay ở chỗ chồng mí và mép cánh khi cánh chạy về tường; dặn không thò tay vào khe chồng mí khi đang lùa.
