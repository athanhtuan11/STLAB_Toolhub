# sliding-wardrobe – Tủ âm tường 2 cánh lùa TREO, khung sắt + lam sóng nguyên cây

Tủ treo đồ nằm giữa 3 bức tường (trái, sau, phải). Không có vách ván: phần chịu lực là **khung sắt hộp**,
mặt trước là **2 cánh lùa treo** trên ray hộp 40 × 40, **không có ray dưới**. Mỗi cánh ghép từ **7 thanh lam sóng ngoài trời
220 × 2900 × 26, nguyên cây, không cắt** (tổng 14 thanh, đúng số đã tính). Bên trong chỉ treo đồ bằng **ống tròn Ø27**.

- **2026-11-11 (Tuan):** "chỉ có ray cửa lùa 40×40, chỉ muốn 2 cánh" → đổi từ 4 cánh bánh đỡ dưới sang 2 cánh treo.
  Bản 4 cánh: `backup/2026-11-11-truoc-2-canh-treo/`. Bản v1 thân ván MFC: `backup/2026-11-09-v1-than-van-mfc/`.
- Giả định: "ray 40×40" là **ray hộp 40 × 40 mm** (xe treo chạy bên trong, bu lông treo thò qua khe đáy). `TODO` đo ray thật.

## Lệnh

```text
cd design
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P build_wardrobe.py -- --out renders
python draw_hanging.py     # 12 mặt cắt ray treo + dẫn hướng, 13 mặt bằng hành trình
python draw_plans.py       # 10 khung sắt, 11 cánh + mặt bằng + mặt cắt, bom.csv, 00-contact-sheet
```

Sửa `P` trong `build_wardrobe.py` (W sau khi đo, `lam_kg` sau khi cân, số ray và xe treo thật) rồi chạy lại.
Script in PASS/FAIL cho 14 điều kiện, tất cả đang PASS.

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

**Áp dụng cho tủ** (bản vẽ `renders/12-mat-cat-treo-dan-huong.png`, `13-mat-bang-hanh-trinh.png`):
- **1 dẫn hướng sàn ở giữa tủ (x = 1500).** Cánh rộng 1582 > nửa tủ 1500, nên ở **mọi vị trí** (đóng, lùa hết trái, lùa hết phải)
  điểm giữa luôn nằm dưới cả 2 cánh, cách đầu rãnh ≥ 60 (script kiểm `dan_huong`). Sàn chỉ có 1 cục đế 3 × 60 × 84 bắt 2 vít nở,
  không vấp chân, dễ lau.
- **Rãnh dưới đáy mỗi cánh:** 2 sắt la 3 × 15 hàn dưới viền dưới, lòng 12, chạy suốt chiều rộng cánh.
- **Chốt nylon Ø10** (hoặc bạc đạn nhỏ) trên đế, ăn 10 mm vào rãnh → **chân cánh chỉ lắc ±1 mm**. Đáy rãnh cách sàn 8.
- Cánh treo không chịu tải ở chân → không cần bánh dưới, không cần cân chỉnh sàn phẳng tuyệt đối.
- Điều kiện để chạy êm: **ray trên phải thẳng và cân bằng**. Ray lệch thì dẫn hướng dưới phải "cãi" lại, gây kẹt.
  Lắp ray trước, dọi dây kiểm thẳng, rồi mới đặt dẫn hướng sàn đúng dưới tâm 2 ray.

## Kích thước chính (W = 3000)

- **2 cánh × 7 thanh**, mỗi cánh rộng **1582**, cao **2943**; **chồng mí 164** (W từ ~2965 đến ~3125 vẫn giữ cách chia này).
- Lùa 1 cánh hết cỡ: **mở nửa trái 1418** hoặc **mở nửa phải 1418**. Không còn cột trước nào chắn lối lấy đồ.
- Cao độ từ sàn: đáy rãnh 8 · đáy cánh 23 · đỉnh cánh 2966 · đáy ray 2991 · đỉnh ray = đáy dầm 3031 · **đỉnh dầm 3111**.
  Khe đỉnh cánh – ray 25 là phần bát treo + bu lông chỉnh cao (`TODO` theo xe treo mua).
- Vùng ray phía trước sâu 120 (2 lớp cánh dày 40, khe giữa 8).

## Hệ treo

- **2 ray hộp 40 × 40**, mỗi lớp cánh 1 ray, dài 3000 (tường – tường). Mỗi ray bắt **dưới 1 dầm 40 × 80 đặt đứng**
  (cạnh 80 theo phương đứng là phương cứng). 2 dầm đặt cạnh nhau, cách 8.
- Dầm tựa vào **cột trước ở 2 tường + cột trước giữa** (bát nối) → nhịp 1460. Kiểm với cánh 86 kg treo giữa nhịp:
  ứng suất 44 MPa, võng 1,0 mm (giới hạn L/400 = 3,6) → PASS. Nếu đặt dầm nằm như bản cũ thì cứng kém khoảng 3 lần.
- **2 xe treo/cánh**, tâm cách mép cánh 110, bu lông treo M8 xuống **bát treo** bắt trên viền trên bằng tán rút ren M8.
- Xe treo nằm kín trong ray hộp → **không nhảy ray**. Bỏ khóa chống nhảy của bản cũ.
- **Chặn cuối trong ray:** đầu cánh đóng (C1 ở tường trái, C2 ở tường phải) dùng **chặn có lẫy giữ** (giữ cánh đóng, thay chốt bi);
  đầu kia chặn cao su.
- **Lắp:** bắt dầm + ray → luồn xe treo vào từ đầu ray → treo cánh → chỉnh bu lông cho cánh thẳng đứng, đáy rãnh cách sàn 8
  → đặt dẫn hướng sàn đúng dưới tâm 2 ray, bắt vít → lắp chặn cuối.

### Tải và chọn xe treo

- Khối lượng cánh ≈ sắt ~14,5 kg + 7 × (1 thanh lam) + ~1,5 kg phụ kiện. Đang giả định **10 kg/thanh lam** (WPC rỗng 2,9 m,
  `TODO` **cân 1 thanh thật**) → **~86 kg/cánh**.
- **Tải mỗi xe treo ≥ (khối lượng cánh ÷ 2) × 1,5 = ~65 kg/xe**, tức bộ 2 xe phải được hãng ghi ≥ 130 kg/cánh.
- Các bộ bánh treo cửa lùa phổ thông trên thị trường ghi 30–100 kg ([Chiaki](https://chiaki.vn/banh-xe-lua-treo-hammered-4-banh-8-banh-tai-trong-40kg-70kg)),
  **không đủ**. Cần loại cửa kho / cổng treo / barn door tải ≥ 130 kg/bộ, đúng cỡ ray 40 × 40 anh có.
  Khi mua, hỏi 3 số: tải/bộ, khe đáy ray (bu lông đi qua), chiều cao từ đáy ray tới mặt bát treo.
  Có số thì điền `trolley_kg`, `track_slot`, `hanger_gap` vào `P`, script sẽ kiểm `xe_treo`.

## Cánh tự hàn

- **Viền = sắt hộp 20 × 40 × 1,2 đặt nằm** (mặt 20 lộ ra trước, sâu 40 = dày cánh), bao kín 4 cạnh 7 thanh lam, sơn đen.
- 4 thanh giằng **hộp 13 × 26** hàn phía sau đỡ lam, bắt vít từ sau (vít ngắn hơn chiều dày lam).
- **Mới:** dưới viền dưới hàn 2 sắt la 3 × 15 tạo rãnh dẫn hướng lòng 12, suốt chiều rộng cánh. Trên viền trên bắt 2 bát treo.
- Chống vênh: hàn trên mặt phẳng, kẹp chặt, đính chéo góc, **2 đường chéo lệch ≤ 2** mới hàn chết. Cánh treo **phải phẳng**:
  cánh vặn thì đáy cánh lệch khỏi rãnh, cọ cánh kia.
- Sơn: mài mối hàn → lót chống gỉ → đen mờ; sơn xong mới bắt lam.
- Bản vẽ gia công chi tiết (bảng cắt, tọa độ lỗ) của bản 4 cánh nằm trong backup. `TODO` vẽ lại cho cánh 7 thanh sau khi anh duyệt dáng
  và có số xe treo thật.

## Khóa + tay nắm

- **1 khóa ấn** ở chỗ chồng mí: mặt khóa trên lam số 7 của C1 (x = 1428), cao 1132; chốt Ø8 bắn ra sau qua khe 8 vào lỗ Ø10 trên viền
  C2. Hai cánh đóng kín tường – tường và tì chặn cuối, nên khóa 1 điểm là không lùa được cánh nào.
- **Khe nắm xuyên lam 30 × 200**, tâm **cao 950** (hạ từ 1000 để tránh giằng sau), đối xứng: C1 ở lam 2 (cách tường trái 351),
  C2 ở lam 6 (cách tường phải 351). Script kiểm `tay_nam_thay`: C2 lùa hết sang trái vẫn còn chỗ móc tay kéo về.
- Không dùng tay nắm lồi: 2 cánh chỉ cách 8 mm.

## Khung sắt (hộp 40 × 40 × 1,4, dầm đầu cửa 40 × 80 đặt đứng)

- **3 khung đầy đủ** (cột trước + cột sau suốt sàn → đỉnh, cột giữa đỡ ống treo, dầm kệ, dầm đỉnh) ở 2 tường và giữa tủ.
  Cột trước giữa nấp sau chỗ chồng mí, khi mở nửa nào cũng không chắn.
- **2 khung lửng** (không cột trước) ở x = 760 và 2240: cột sau + cột giữa + dầm kệ/đỉnh gác lên thanh ngang trước.
  Nhờ vậy ống treo vẫn chỉ nhịp 700 (tải 40 kg/ống: 67 MPa, võng 1,3 mm, PASS).
- 4 thanh ngang tường – tường (kệ trước/sau, đỉnh trước/sau), bản đế 60 × 60 × 4 mỗi chân cột, bắt nở vào 3 tường.
- Vật tư (`design/bom.csv`): hộp 40 × 40 ~53,8 m, 40 × 80 6,0 m (2 dầm), 20 × 40 17,9 m + 13 × 26 12,3 m (2 cánh), sắt ~136 kg
  (theo độ dày giả định, `TODO` theo hàng mua).

| Khoang | Lọt lòng | Ống Ø27 (cao từ sàn) |
| --- | --- | --- |
| K1–K4 | ~700 mỗi khoang | 2050 + 1030 (treo 2 tầng) |
| Hộp nóc | kệ ván 17 ở cao 2300 | chăn mền, vali |

## Danh sách mua phụ kiện (bản 2 cánh treo)

| # | Phụ kiện | SL | Ghi chú |
| --- | --- | --- | --- |
| 1 | Ray hộp 40 × 40 dài 3 m | 2 | anh đã có – đo lại khe đáy, độ dày |
| 2 | Xe treo đúng ray 40 × 40, **≥ 65 kg/xe** (≥ 130 kg/bộ 2 xe) + bu lông treo chỉnh cao | 4 | `TODO` hãng; phổ thông 30–100 kg/bộ là không đủ |
| 3 | Chặn cuối trong ray: 2 loại có lẫy giữ + 2 cao su | 4 | thường đi kèm bộ ray |
| 4 | Dẫn hướng sàn: đế thép 3 × 60 × 84 + 2 chốt nylon Ø10 (tự làm, hoặc mua "floor guide" cửa bypass loại chốt) | 1 | bắt 2 vít nở |
| 5 | Sắt la 3 × 15 (rãnh đáy cánh) | 2 × 2 × 1,6 m | hàn dưới viền dưới |
| 6 | Khóa ấn tủ cửa lùa (push lock), hành trình chốt ≥ 13 | 1 | |
| 7 | Tán rút ren thép M8 (bát treo) + M5, kìm rút | ~20 | |
| 8 | Ron chổi chống bụi mép chồng mí | 2 × 2,9 m | |
| 9 | Ống inox Ø27 dày 1,2 + tai đỡ hàn | 8 ống | |
| 10 | Nở sắt M8 + bát L bắt khung vào tường | ~16 | 2 tường bên + tường sau |

Không còn dùng: bánh đỡ dưới, ray U dưới, máng trên 2 sắt la, bánh dẫn hướng 608, khóa chống nhảy, chốt bi.

## Mô phỏng trượt (Blender)

Mở `design/wardrobe.blend`, bấm **Space**: C1 lùa phải hết cỡ rồi đóng, sau đó C2 lùa trái hết cỡ rồi đóng.
Video: `blender -b -P build_wardrobe.py -- --out renders --anim` → ghép bằng ffmpeg như bản cũ (`TODO` chạy lại cho bản 2 cánh).

## TODO

- W thực tế; **cân 1 thanh lam** (`lam_kg`); số sóng lam.
- Đo ray 40 × 40: khe đáy, độ dày; chọn xe treo ≥ 65 kg/xe → điền `trolley_kg`, `track_slot`, `hanger_gap`.
- Vẽ lại bản vẽ gia công cánh 7 thanh (bảng cắt, lỗ bát treo, rãnh, khóa) sau khi duyệt.
- Tường sau ẩm thì chừa khe ~20 sau quần áo hoặc ốp tấm chống ẩm.

## An toàn

- Cánh **~86 kg, cao 2,94 m** treo trên ray: **2–3 người** nâng và treo cánh. Siết đủ bu lông treo, lắp **chặn cuối 2 đầu ray**
  trước khi buông tay, không để cánh chạy tuột khỏi đầu ray.
- Dầm đầu cửa + ray chịu toàn bộ tải 2 cánh: bắt dầm vào tường bằng nở thép (không dùng nở nhựa), hàn/bát chắc vào cột trước giữa.
- Khung sắt **phải bắt nở vào tường** ở cả 3 phía + sàn. Khoan tường: dò đường điện âm trước.
- Trẻ nhỏ dễ kẹt tay ở chỗ chồng mí và ở mép cánh khi cánh chạy về tường; dặn không thò tay qua khe nắm khi đang lùa.
