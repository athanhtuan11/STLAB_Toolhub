# sliding-wardrobe – Tủ âm tường 2 cánh lùa TREO, khung sắt + lam sóng nguyên cây

Tủ treo đồ nằm giữa 3 bức tường (trái, sau, phải). Không có vách ván: phần chịu lực là **khung sắt hộp**,
mặt trước là **2 cánh lùa treo hoàn toàn ở trên**, **sàn để trống** (không ray dưới, không vấp). Mỗi cánh ghép từ **7 thanh lam sóng ngoài trời
220 × 2900 × 26, nguyên cây, không cắt** (tổng 14 thanh, đúng số đã tính). Bên trong chỉ treo đồ bằng **ống tròn Ø27**.

- **2026-11-11 (Tuan):** "chỉ có ray cửa lùa 40×40, chỉ muốn 2 cánh" → đổi từ 4 cánh bánh đỡ dưới sang 2 cánh treo.
  Bản 4 cánh: `backup/2026-11-11-truoc-2-canh-treo/`. Bản v1 thân ván MFC: `backup/2026-11-09-v1-than-van-mfc/`.
- Cùng ngày, Tuan thử phương án U chấn 40 × 40 dưới chịu tải (`backup/2026-11-11-truoc-u-chim-giua/`) nhưng thấy **đi lại dễ vấp**
  → chốt **treo hoàn toàn + 1 đoạn U ngắn giấu giữa** (bản này).
- Ray trên + xe treo: **Tuan tự mua loại phù hợp** (cánh ~38 kg → nên ≥ 29 kg/xe). Model đang vẽ theo hộp 40 × 40; ray 40 × 40 anh có dùng được

## Lệnh

```text
cd design
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P build_wardrobe.py -- --out renders
python draw_hanging.py     # 12 mặt cắt ray treo + dẫn hướng U, 13 mặt bằng hành trình
python draw_plans.py       # 10 khung sắt, 11 cánh + mặt bằng + mặt cắt, bom.csv, 00-contact-sheet
```

Sửa `P` trong `build_wardrobe.py` (W sau khi đo, số ray và xe treo thật) rồi chạy lại.
Script in PASS/FAIL cho 13 điều kiện, tất cả đang PASS. Ảnh 3D tổng hợp: `design/renders/00-3d-tong-hop.png`.

## Nghiên cứu: không có ray dưới thì cánh có rung lắc không? (2026-11-11)

**Có, nếu không có gì giữ chân cánh.** Cánh treo chỉ được giữ ở mép trên, nên chân cánh lắc như con lắc mỗi khi đẩy
hoặc có gió ([Pinky's Iron Doors](https://pinkysirondoors.com/blogs/specialty-doors/bottom-track-for-sliding-barn-doors-a-must-have-or-a-nice-to-have)).
Với tủ này còn nguy hiểm hơn, vì **2 cánh chỉ cách nhau 8 mm**: lắc vài mm là 2 cánh cọ và đập vào nhau.

**Nhưng không cần ray dưới chạy suốt chiều ngang.** Mọi bộ cửa treo đều chỉ dùng **dẫn hướng sàn nhỏ**:
- Hager hướng dẫn cửa lùa 2 cánh vượt nhau (bypass): *"đặt dẫn hướng dưới chỗ chồng mí của 2 cánh và bắt xuống sàn"*,
  tức là **1 cục ở giữa** ([Hager 9613RS/9614RS](https://www.hagerco.com/Files/Images/Images/Instructions/9613RS%20&%209614RS%20[60lb%20By-Pass%20Sliding%20Door%20Hardware%20Set%20Installation%20Instructions]%20[4].pdf)).
- Bộ treo 100 kg của Häfele (EKU Porta) có kèm 1 dẫn hướng sàn, và chỉ cho **cánh cao tối đa 2,7 m**
  ([Häfele 941.00.005](https://www.build.com/hafele-941-00-005/s387211)). Cánh tủ này cao **2,94 m**, cao hơn mức hãng
  công bố, nên càng phải có dẫn hướng.

**Áp dụng cho tủ** (ảnh `renders/06-chi-tiet-dan-huong-giua.png`, bản vẽ `12-mat-cat-treo-dan-huong.png`, `13-mat-bang-hanh-trinh.png`):
- **Dẫn hướng = 2 đoạn U chấn 40 × 40 × 2 dài 140** (mỗi lớp cánh 1 đoạn, cách nhau 8), đặt ở **giữa tủ x = 1430 … 1570**,
  bắt 2 vít nở mỗi đoạn. Đây là vùng **luôn bị cả 2 cánh che** ở mọi vị trí (đóng, lùa hết trái, lùa hết phải; cánh rộng 1582 > nửa tủ 1500)
  → **đoạn U không bao giờ lộ ra, sàn trước tủ trống hoàn toàn, không vấp** (script kiểm `dan_huong`).
- Trong lòng mỗi đoạn U bắt **2 miếng POM/nylon dày 14,5** (cắt từ tấm POM, bắt vít qua thành U) chừa khe 7.
- **Gân dưới đáy mỗi cánh:** sắt la 5 × 36 hàn đứng dưới tâm viền dưới, suốt chiều rộng cánh, mép dưới cách sàn 10.
  Gân ăn 30 mm vào khe POM → **chân cánh chỉ lắc ±1 mm** (kiểm `gan_trong_U`). POM trơn, gân lùa êm, không kêu.
- Cánh treo không chịu tải ở chân → sàn không cần phẳng tuyệt đối, chỉ chỗ đặt đoạn U.
- Điều kiện để chạy êm: **ray trên phải thẳng và cân bằng**. Lắp ray trước, dọi dây kiểm thẳng, rồi mới đặt đoạn U đúng dưới tâm 2 ray.

## Kích thước chính (W = 3000)

- **2 cánh × 7 thanh**, mỗi cánh rộng **1582**, cao **2943**; **chồng mí 164** (W từ ~2965 đến ~3125 vẫn giữ cách chia này).
- Lùa 1 cánh hết cỡ: **mở nửa trái 1418** hoặc **mở nửa phải 1418**. Không còn cột trước nào chắn lối lấy đồ.
- Cao độ từ sàn: mép dưới gân 10 · miệng đoạn U 40 · đáy cánh 46 · đỉnh cánh 2989 · đáy ray 3014 · đỉnh ray = đáy dầm 3054 · **đỉnh dầm 3094**.
  Khe dưới cánh 46 (gân che bớt còn 10) – chỗ này chỉ có ở mặt trước tủ.
  Khe đỉnh cánh – ray 25 là phần bát treo + bu lông chỉnh cao (`TODO` theo xe treo mua).
- Vùng ray phía trước sâu 120 (2 lớp cánh dày 40, khe giữa 8).

## Hệ treo

- **2 ray hộp 40 × 40**, mỗi lớp cánh 1 ray, dài 3000 (tường – tường). Mỗi ray bắt **dưới 1 dầm hộp 40 × 40** (2 dầm đặt cạnh nhau, cách 8).
- Dầm tựa vào **cột trước ở 2 tường + cột trước giữa** (bát nối) → nhịp 1460. Kiểm với cánh 38 kg treo giữa nhịp:
  ứng suất 51 MPa, võng 2,3 mm (giới hạn L/400 = 3,6) → PASS.
- **2 xe treo/cánh**, tâm cách mép cánh 110, bu lông treo M8 xuống **bát treo** bắt trên viền trên bằng tán rút ren M8.
- Xe treo nằm kín trong ray hộp → **không nhảy ray**. Bỏ khóa chống nhảy của bản cũ.
- **Chặn cuối trong ray:** đầu cánh đóng (C1 ở tường trái, C2 ở tường phải) dùng **chặn có lẫy giữ** (giữ cánh đóng, thay chốt bi);
  đầu kia chặn cao su.
- **Lắp:** bắt dầm + ray → luồn xe treo vào từ đầu ray → treo cánh → chỉnh bu lông cho cánh thẳng đứng, đáy cánh cách sàn 46
  → đẩy 2 cánh về giữa, đặt 2 đoạn U (đã bắt POM) cho gân lọt vào khe, đánh dấu, bắt vít nở → lắp chặn cuối.

### Tải

- Khối lượng cánh ≈ sắt ~15,6 kg (gồm gân) + 7 × **3 kg/thanh lam** (Tuan 2026-11-11) + ~1,5 kg phụ kiện → **~38 kg/cánh**.
- Xe treo nên chịu **≥ (38 ÷ 2) × 1,5 ≈ 29 kg/xe** (bộ 2 xe ≥ ~57 kg/cánh). **Tuan tự chọn bánh/xe treo phù hợp.**
  Mua xong muốn script kiểm thì điền `trolley_kg`, `track_slot`, `hanger_gap` vào `P`.

## Cánh tự hàn

- **Viền = sắt hộp 20 × 40 × 1,2 đặt nằm** (mặt 20 lộ ra trước, sâu 40 = dày cánh), bao kín 4 cạnh 7 thanh lam, sơn đen.
- 4 thanh giằng **hộp 13 × 26** hàn phía sau đỡ lam, bắt vít từ sau (vít ngắn hơn chiều dày lam).
- Dưới viền dưới hàn **gân sắt la 5 × 36** (đứng, đúng tâm dày cánh), suốt chiều rộng cánh. Trên viền trên bắt 2 bát treo.
- Chống vênh: hàn trên mặt phẳng, kẹp chặt, đính chéo góc, **2 đường chéo lệch ≤ 2** mới hàn chết. Cánh treo **phải phẳng**:
  cánh vặn thì gân lệch khỏi khe POM, cọ cánh kia.
- Sơn: mài mối hàn → lót chống gỉ → đen mờ; sơn xong mới bắt lam.
- Bản vẽ gia công chi tiết (bảng cắt, tọa độ lỗ) của bản 4 cánh nằm trong backup. `TODO` vẽ lại cho cánh 7 thanh sau khi anh duyệt dáng
  và có số xe treo thật.

## Khóa + tay nắm

- **1 khóa ấn** ở chỗ chồng mí: mặt khóa trên lam số 7 của C1 (x = 1428), cao 1132; chốt Ø8 bắn ra sau qua khe 8 vào lỗ Ø10 trên viền
  C2. Hai cánh đóng kín tường – tường và tì chặn cuối, nên khóa 1 điểm là không lùa được cánh nào.
- **Khe nắm xuyên lam 30 × 200**, tâm **cao 950** (hạ từ 1000 để tránh giằng sau), đối xứng: C1 ở lam 2 (cách tường trái 351),
  C2 ở lam 6 (cách tường phải 351). Script kiểm `tay_nam_thay`: C2 lùa hết sang trái vẫn còn chỗ móc tay kéo về.
- Không dùng tay nắm lồi: 2 cánh chỉ cách 8 mm.

## Khung sắt (hộp 40 × 40 × 1,4, cả dầm đỡ ray)

- **3 khung đầy đủ** (cột trước + cột sau suốt sàn → đỉnh, cột giữa đỡ ống treo, dầm kệ, dầm đỉnh) ở 2 tường và giữa tủ.
  Cột trước giữa nấp sau chỗ chồng mí, khi mở nửa nào cũng không chắn.
- **2 khung lửng** (không cột trước) ở x = 760 và 2240: cột sau + cột giữa + dầm kệ/đỉnh gác lên thanh ngang trước.
  Nhờ vậy ống treo vẫn chỉ nhịp 700 (tải 40 kg/ống: 67 MPa, võng 1,3 mm, PASS).
- 4 thanh ngang tường – tường (kệ trước/sau, đỉnh trước/sau), bản đế 60 × 60 × 4 mỗi chân cột, bắt nở vào 3 tường.
- Vật tư (`design/bom.csv`): hộp 40 × 40 ~59,7 m (gồm 2 dầm đỡ ray), 20 × 40 17,9 m + 13 × 26 12,3 m (2 cánh), sắt ~132 kg
  (theo độ dày giả định, `TODO` theo hàng mua).

| Khoang | Lọt lòng | Ống Ø27 (cao từ sàn) |
| --- | --- | --- |
| K1–K4 | ~700 mỗi khoang | 2050 + 1030 (treo 2 tầng) |
| Hộp nóc | kệ ván 17 ở cao 2300 | chăn mền, vali |

## Danh sách mua phụ kiện (bản 2 cánh treo)

| # | Phụ kiện | SL | Ghi chú |
| --- | --- | --- | --- |
| 1 | Ray hộp 40 × 40 dài 3 m | 2 | anh đã có – đo lại khe đáy, độ dày |
| 2 | Xe treo đúng ray 40 × 40 + bu lông treo chỉnh cao | 4 | Tuan tự chọn, nên ≥ 29 kg/xe |
| 3 | Chặn cuối trong ray: 2 loại có lẫy giữ + 2 cao su | 4 | thường đi kèm bộ ray |
| 4 | **U chấn 40 × 40 × 2** – 2 đoạn dài 140 (cắt từ 1 cây) + 4 vít nở | 2 đoạn | dẫn hướng giữa tủ |
| 5 | Tấm POM (hoặc nylon) dày ~15 – cắt 4 miếng 14,5 × 38 × 140 + vít | 4 miếng | lót trong đoạn U, chừa khe 7 |
| 5b | Sắt la 5 × 36 (gân dưới cánh) | 2 × 1,6 m | hàn đứng dưới tâm viền dưới |
| 6 | Khóa ấn tủ cửa lùa (push lock), hành trình chốt ≥ 13 | 1 | |
| 7 | Tán rút ren thép M8 (bát treo) + M5, kìm rút | ~20 | |
| 8 | Ron chổi chống bụi mép chồng mí | 2 × 2,9 m | |
| 9 | Ống inox Ø27 dày 1,2 + tai đỡ hàn | 8 ống | |
| 10 | Nở sắt M8 + bát L bắt khung vào tường | ~16 | 2 tường bên + tường sau |

Không còn dùng: ray U dài trên sàn, bánh đỡ dưới, bánh 608, máng trên 2 sắt la, khóa chống nhảy, chốt bi.

## Mô phỏng trượt (Blender)

Mở `design/wardrobe.blend`, bấm **Space**: C1 lùa phải hết cỡ rồi đóng, sau đó C2 lùa trái hết cỡ rồi đóng.
Video: `blender -b -P build_wardrobe.py -- --out renders --anim` → ghép bằng ffmpeg như bản cũ (`TODO` chạy lại cho bản 2 cánh).

## TODO

- W thực tế; số sóng lam.
- Đo ray 40 × 40: khe đáy, độ dày; xe treo đã mua → điền `trolley_kg`, `track_slot`, `hanger_gap`.
- Vẽ lại bản vẽ gia công cánh 7 thanh (bảng cắt, lỗ bát treo, gân, khóa) sau khi duyệt.
- Tường sau ẩm thì chừa khe ~20 sau quần áo hoặc ốp tấm chống ẩm.

## An toàn

- Cánh **~38 kg, cao 2,94 m** treo trên ray: **2–3 người** nâng và treo cánh. Siết đủ bu lông treo, lắp **chặn cuối 2 đầu ray**
  trước khi buông tay, không để cánh chạy tuột khỏi đầu ray.
- Dầm đầu cửa + ray chịu toàn bộ tải 2 cánh: bắt dầm vào tường bằng nở thép (không dùng nở nhựa), hàn/bát chắc vào cột trước giữa.
- Khung sắt **phải bắt nở vào tường** ở cả 3 phía + sàn. Khoan tường: dò đường điện âm trước.
- Trẻ nhỏ dễ kẹt tay ở chỗ chồng mí và ở mép cánh khi cánh chạy về tường; dặn không thò tay qua khe nắm khi đang lùa.
