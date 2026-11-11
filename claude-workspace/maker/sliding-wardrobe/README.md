# sliding-wardrobe – Tủ âm tường 2 cánh lùa, khung sắt + lam sóng nguyên cây

Tủ treo đồ nằm giữa 3 bức tường (trái, sau, phải). Không có vách ván: phần chịu lực là **khung sắt hộp**.
Mặt trước là **2 cánh lùa**. Mỗi cánh ghép từ **7 thanh lam sóng ngoài trời 220 × 2900 × 26, nguyên cây, không cắt**
(tổng 14 thanh). Bên trong chỉ treo đồ bằng **ống tròn Ø27**.

**Hệ lùa (Tuan 2026-11-11, bản cuối):** có **bệ tủ cao 40** phủ cả lòng tủ, 2 thanh U nằm **chìm ngang mặt bệ** → sàn ngoài phẳng, không vấp.
- **Dưới chịu tải:** 2 thanh **thép U chấn 40 × 40** nằm ngửa trên sàn (vật tư dễ mua). Mỗi cánh có 4 bánh 608 bọc POM chạy trong lòng U.
- **Trên giữ đứng:** **ray hộp 40 × 40** anh đã có, cùng xe treo. Xe treo **không chịu tải**, chỉ giữ cánh đứng thẳng và chống nhảy ray.

Lịch sử phương án:
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

Sửa `P` trong `build_wardrobe.py` (W sau khi đo, `lam_kg` sau khi cân, số đo U/bánh/ray thật) rồi chạy lại.
Script kiểm 14 điều kiện, tất cả đang PASS. Ảnh 3D tổng hợp: `design/renders/00-3d-tong-hop.png`.

## Vì sao chọn "U dưới chịu tải + ray trên giữ đứng"

Cánh khoảng **37 kg, cao 2,94 m**. Tách việc cho hai ray:

| Việc | Ai làm | Vì sao chắc |
| --- | --- | --- |
| Đỡ cánh ~37 kg | **4 bánh/cánh lăn trong lòng U chấn** (nên ≥ 14 kg/bánh) | Tải xuống thẳng sàn. Sàn đỡ suốt chiều dài U nên U không võng, bánh 608 dễ mua và rẻ |
| Giữ chân cánh không lắc | **Thành U** ôm càng bánh | Càng 30 trong lòng U 36 → chân cánh chỉ lắc ±3 mm, 2 cánh cách nhau 8 không cọ |
| Giữ đầu cánh đứng thẳng | **Xe treo trong ray hộp 40 × 40** | Xe treo hở 3 mm trên mép ray nên không gánh tải; loại xe treo nào vừa ray cũng dùng được |
| Chống nhấc cánh khỏi ray | Xe treo kín trong ray hộp | Nhấc cánh tối đa ~5 mm là xe treo chạm nóc ray; bánh cần nhấc 38 mm mới thoát được U (kiểm `chong_nhay`) |

Nghiên cứu trước đó (vẫn đúng): cánh **chỉ treo trên mà không có gì giữ chân thì đung đưa như con lắc**
([Pinky's Iron Doors](https://pinkysirondoors.com/blogs/specialty-doors/bottom-track-for-sliding-barn-doors-a-must-have-or-a-nice-to-have)).
Các bộ treo hãng đều kèm dẫn hướng sàn
([Hager](https://www.hagerco.com/Files/Images/Images/Instructions/9613RS%20&%209614RS%20[60lb%20By-Pass%20Sliding%20Door%20Hardware%20Set%20Installation%20Instructions]%20[4].pdf),
[Häfele EKU Porta 100 kg](https://www.build.com/hafele-941-00-005/s387211); Häfele chỉ cho cánh cao ≤ 2,7 m).
Ở bản này tải nằm ở U dưới, xe treo trên chỉ giữ đứng.

## Bệ tủ – che ray và bánh (Tuan 2026-11-11: "U trên sàn đi lại dễ vấp")

- **Bệ cao 40 = đúng chiều cao thanh U**, phủ toàn bộ lòng tủ (3000 × ~700 phía sau 2 thanh U):
  3 đà **sắt hộp 20 × 40 đặt nằm** (cao 20) chạy tường – tường + **ván 18** (plywood/MFC chịu ẩm) bắt vít lên đà, chêm ≤ 3 cho mặt ván
  bằng miệng U (kiểm `be_phang`). Ván khoét lỗ cho chân cột khung.
- 2 thanh U nằm **chìm ngang mặt bệ** ở mép trước; giữa 2 U hàn **thanh la đệm 8 × 40** → mặt bệ liền một mặt phẳng.
- **Mặt trước bệ = thành U ngoài sơn đen**, nhìn như chân đế tủ. Sàn phòng trước tủ để nguyên, phẳng.
- Đáy cánh cách mặt bệ chỉ 6 → bánh nằm trong lòng U, **không thấy bánh**.
- Khi mở 1 nửa: thấy 2 khe U (lòng 36) chạy ngang mép trước bệ – không vấp vì không ai bước lên bệ; hút bụi lòng U định kỳ.
- Ống treo dưới (cao 1030 từ sàn) còn cách mặt bệ 990 – đồ dài ≤ ~850 vẫn thoải mái.

## Kích thước chính (W = 3000)

- **2 cánh × 7 thanh**, mỗi cánh rộng **1582**, cao **2943**; **chồng mí 164** (W từ ~2965 đến ~3125 vẫn giữ cách chia này).
- Lùa 1 cánh hết cỡ: **mở nửa trái 1418** hoặc **mở nửa phải 1418**.
- Cao độ từ sàn: miệng U 40 · đáy cánh 46 (hở 6) · đỉnh cánh 2989 · đáy ray trên 3014 · đỉnh ray 3054 · **đỉnh dầm 3094**.
- Vùng ray phía trước sâu 120 (2 lớp cánh dày 40, khe giữa 8).

## Ray dưới – U chấn 40 × 40 (chịu tải)

- 2 thanh **U chấn 40 × 40 × 2** (Tuan 2026-11-11: thép dày 2) dài 3000, nằm ngửa, mỗi lớp cánh 1 thanh, cách nhau 8.
  Đặt đúng dưới tâm ray trên (dọi dây).
- Bắt xuống sàn bằng **vít nở đầu bằng, khoan côn** cho đầu vít chìm phẳng lòng U (bánh lăn qua), khoảng 400 mm/vít. Sàn lệch thì
  chêm tôn dưới U cho thẳng và phẳng.
- **Chặn cuối cao su trong lòng U** ở 2 đầu (cụm bánh chạm thì dừng, mép cánh sát tường).
- **Cụm bánh** (2 cụm/cánh, tâm cách mép cánh 110): càng thép rộng 30 hàn dưới viền dưới; 2 bánh 608 bọc POM Ø32 × 12 cách nhau 60,
  trục bu lông M8. Có vít chỉnh cao để cân cánh thẳng đứng.
- **Tải mỗi bánh nên ≥ (khối lượng cánh ÷ 4) × 1,5 ≈ 14 kg** (cánh ~37 kg); Tuan tự chọn bánh phù hợp. Bạc đạn 608 trần chịu được nhiều hơn mức này; lớp POM bọc
  ngoài cần hỏi người bán tải/bánh (`TODO`, điền `wheel_kg`).

## Ray trên – ray hộp 40 × 40 (chỉ giữ đứng)

- 2 ray hộp 40 × 40 (anh đã có), mỗi lớp cánh 1 ray, bắt dưới 1 dầm **hộp 40 × 40** (dầm không còn chịu tải nên không cần 40 × 80).
  Dầm tựa vào cột trước ở 2 tường + cột trước giữa.
- 2 xe treo/cánh, bu lông treo xuống bát treo bắt trên viền trên (tán rút ren M8). **Chỉnh đai ốc để bánh xe treo hở 3 mm trên mép ray**:
  xe treo không gánh tải, chỉ giữ đầu cánh.
- **Chặn cuối trong ray**: đầu cánh đóng (C1 ở tường trái, C2 ở tường phải) dùng **chặn có lẫy** giữ cánh đóng, đầu kia chặn cao su.
- **Lắp:** bắt U xuống sàn + dầm + ray trên → luồn xe treo vào ray → dựng cánh, đặt 4 bánh vào lòng U → nối bu lông xe treo với bát treo
  → chỉnh vít cụm bánh cho cánh đứng thẳng → chỉnh đai ốc xe treo hở 3 → lắp chặn cuối.

## Cánh tự hàn

- **Viền = sắt hộp 20 × 40 × 1,2 đặt nằm** (mặt 20 lộ ra trước, sâu 40 = dày cánh), bao kín 4 cạnh 7 thanh lam, sơn đen.
- 4 thanh giằng **hộp 13 × 26** hàn phía sau đỡ lam, bắt vít từ sau.
- Dưới viền dưới hàn **2 càng bánh**; trên viền trên bắt **2 bát treo**.
- Khối lượng cánh ≈ sắt ~13,4 kg + 7 × (1 thanh lam) + ~2,5 kg phụ kiện. Lam **~3 kg/thanh** (Tuan) → **~37 kg/cánh**.
- Chống vênh: hàn trên mặt phẳng, kẹp chặt, đính chéo góc, **2 đường chéo lệch ≤ 2** mới hàn chết.
- Sơn: mài mối hàn → lót chống gỉ → đen mờ; sơn xong mới bắt lam.
- `TODO`: vẽ lại bản vẽ gia công cánh 7 thanh (bảng cắt, càng bánh, bát treo, lỗ khóa) sau khi anh duyệt và có số U/bánh/xe treo thật.

## Khóa + tay nắm

- **1 khóa ấn** ở chỗ chồng mí: mặt khóa trên lam số 7 của C1 (x = 1428); chốt Ø8 bắn ra sau qua khe 8 vào lỗ Ø10 trên viền C2.
- **Khe nắm xuyên lam 30 × 200**, tâm **cao 950**, đối xứng: C1 ở lam 2, C2 ở lam 6 (cách mỗi tường 351).
  C2 lùa hết sang trái vẫn còn chỗ móc tay kéo về (kiểm `tay_nam_thay`).

## Khung sắt (hộp 40 × 40 × 1,4)

- **3 khung đầy đủ** (cột trước + sau suốt sàn → đỉnh, cột giữa đỡ ống, dầm kệ, dầm đỉnh) ở 2 tường và giữa tủ. Cột trước giữa nấp sau
  chỗ chồng mí, nên mở nửa nào cũng không chắn.
- **2 khung lửng** (không cột trước) ở x = 760 và 2240, để ống treo chỉ nhịp 700 (40 kg/ống: 67 MPa, võng 1,3 mm, PASS).
- 4 thanh ngang tường – tường, bản đế 60 × 60 × 4 mỗi chân cột, bắt nở vào 3 tường.
- Vật tư (`design/bom.csv`): hộp 40 × 40 ~59,7 m, 20 × 40 17,9 m + 13 × 26 12,3 m (2 cánh), U chấn 40 × 40 2 × 3 m, sắt ~141 kg
  (theo độ dày giả định, `TODO` theo hàng mua).

| Khoang | Lọt lòng | Ống Ø27 (cao từ sàn) |
| --- | --- | --- |
| K1–K4 | ~700 mỗi khoang | 2050 + 1030 (treo 2 tầng) |
| Hộp nóc | kệ ván 17 ở cao 2300 | chăn mền, vali |

## Danh sách mua phụ kiện

| # | Phụ kiện | SL | Ghi chú |
| --- | --- | --- | --- |
| 1 | **Thép U chấn 40 × 40 × 2**, dài 3 m | 2 | ray dưới chịu tải |
| 2 | **Bánh 608 bọc POM Ø32 × 12** (hoặc bánh ổ bi tương đương), bu lông trục M8 | 8 | Tuan tự chọn, nên ≥ 14 kg/bánh |
| 3 | Thép bản 4–5 mm làm càng bánh (tự cắt hàn) | 4 cụm | rộng 30, vít chỉnh cao M8 |
| 4 | Ray hộp 40 × 40 dài 3 m | 2 | anh đã có |
| 5 | Xe treo vừa ray 40 × 40 (loại thường, không cần tải nặng) + bu lông treo | 4 | chỉ giữ đứng |
| 6 | Chặn cuối: trong ray trên (2 có lẫy + 2 cao su) + cao su trong lòng U (4) | 8 | |
| 7 | Vít nở đầu bằng (khoan côn) bắt U xuống sàn | ~16 | đầu vít chìm phẳng lòng U |
| 8 | Khóa ấn tủ cửa lùa (push lock), hành trình chốt ≥ 13 | 1 | |
| 9 | Tán rút ren thép M8 (bát treo) + M5, kìm rút | ~20 | |
| 10 | Ron chổi chống bụi mép chồng mí | 2 × 2,9 m | |
| 11 | Ống inox Ø27 dày 1,2 + tai đỡ hàn | 8 ống | |
| 12 | Nở sắt M8 + bát L bắt khung vào tường | ~16 | |
| 13 | Bệ tủ: sắt hộp 20 × 40 (3 × 3 m) + ván 18 chịu ẩm 3000 × ~700 + la 8 × 40 (3 m) đệm giữa 2 U | 1 bộ | mặt ván = miệng U |

## Mô phỏng trượt (Blender)

Mở `design/wardrobe.blend`, bấm **Space**: C1 lùa phải hết cỡ rồi đóng, rồi C2 lùa trái hết cỡ rồi đóng.
`TODO`: render lại video cho bản này (`--anim` + ffmpeg như bản cũ).

## TODO

- W thực tế.
- Đo bánh POM (Ø, bề rộng, tải), ray hộp (độ dày vách, khe đáy), xe treo (cao) → điền vào `P`, chạy lại.
- Bản vẽ gia công cánh 7 thanh.
- Tường sau ẩm thì chừa khe ~20 sau quần áo hoặc ốp tấm chống ẩm.

## An toàn

- Cánh **~37 kg, cao 2,94 m**: **2–3 người** dựng và lắp cánh. Lắp chặn cuối ở cả ray trên và U dưới trước khi lùa thử.
- Mép trước bệ cao 40 (như chân tủ); lòng U hở khi mở cửa – hút bụi, không để vật cứng lọt vào.
- Khung sắt **phải bắt nở vào tường** ở cả 3 phía + sàn. Khoan tường/sàn: dò đường điện, ống nước âm trước.
- Trẻ nhỏ dễ kẹt tay ở chỗ chồng mí và mép cánh khi cánh chạy về tường; dặn không thò tay qua khe nắm khi đang lùa.
