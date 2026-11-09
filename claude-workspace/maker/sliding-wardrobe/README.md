# sliding-wardrobe – Tủ âm tường cửa lùa 4 cánh, khung sắt + lam sóng nguyên cây

Tủ treo đồ nằm giữa 3 bức tường (trái, sau, phải). Không có vách ván: phần chịu lực là **khung sắt hộp**,
mặt trước là **4 cánh lùa** ghép từ thanh **lam sóng ngoài trời 220 × 2900 × 26 mm, dùng nguyên cây, không cắt**.
Bên trong chỉ treo đồ bằng **ống tròn Ø27** (Tuan 2026-11-09). Bản v1 (thân ván MFC) nằm ở `backup/2026-11-09-v1-than-van-mfc/`.

## Lệnh
```text
cd design
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P build_wardrobe.py -- --out renders
python draw_plans.py
```
Sửa `P["W"]` (tường – tường) sau khi đo rồi chạy lại. Script tính lại chồng mí, báo FAIL nếu ngoài 40–150.
Kết quả: `wardrobe.blend`, `renders/00-contact-sheet.png`, `bom.csv` (vật tư).

## Kích thước chính (W = 3000)
- Cánh **3-4-4-3 thanh**: 2 cánh ngoài 702 (3 thanh), 2 cánh giữa 922 (4 thanh), cao **2943**; chồng mí **83**.
  W từ ~2800 đến ~3130 vẫn giữ cách chia này, chỉ đổi chồng mí. Lam nguyên cây 2900, **14 thanh, không cắt**.
- Lùa 1 cánh (hành trình thật, cánh cùng ray không đè nhau): khoang ngoài mở trọn khoang, khoang giữa mở ~674
  (sửa 2026-11-09: số 757 trước đây sai do chưa tính cánh cùng ray chặn hành trình).
- Đỉnh dầm đầu cửa **3102** (đáy cánh 74 = ray Ø21 + bánh Ø48 + bát; cánh 2943; khe 5; máng sắt la 40; dầm 40). TODO đo hàng thật.
- Vùng ray phía trước sâu 120 (cánh dày 40 × 2 ray + khe).

## Cánh tự hàn (Tuan 2026-11-09)
- **Viền = sắt hộp 20×40×1,2 đặt nằm**: mặt 20 lộ ra trước, sâu 40 = dày cánh. Viền bao kín 4 cạnh lam, là nẹp chỉ
  + tay nắm luôn, sơn đen cùng khung. Không dùng sắt V (cán nóng hay lệch góc, tiết diện hở dễ xoắn khi hàn).
- Lam lọt trong viền, khe 1 mỗi bên, 1,5 mỗi đầu (giãn nở WPC – TODO theo hãng). Mặt lam lùi sau mép viền ~1.
- 4 thanh giằng **hộp 13×26** hàn phía sau đỡ lam; **bắt vít từ sau** (khoan mồi, vít ngắn hơn chiều dày lam).
- Hộp bánh dưới khoét lắp vào ống viền dưới; bánh trên + khóa chống nhảy bắt trên ống viền trên.
- Sắt/cánh (tính từ tiết diện): cánh 4 thanh ~10,4 kg, cánh 3 thanh ~9,4 kg. **Khối lượng cánh = sắt + số thanh × (1 thanh lam).**
- Chống vênh: hàn trên mặt phẳng, kẹp chặt, đính chéo các góc, **2 đường chéo lệch ≤ 2** mới hàn chết; hàn so le 2 mặt.
- Sơn: mài mối hàn → lót chống gỉ → đen mờ; sơn xong mới bắt lam.

| Khoang | Lọt lòng | Ống Ø27 (cao từ sàn) | Dùng cho |
| --- | --- | --- | --- |
| K1 (trái) | 733 | 2050 + 1030 | treo 2 tầng: áo sơ mi, áo ngắn, quần vắt |
| K2 | 667 | 2050 + 1030 | treo 2 tầng |
| K3 | 667 | 2050 + 1030 | treo 2 tầng |
| K4 (phải) | 733 | 2050 + 1030 | treo 2 tầng |
| Hộp nóc | 4 ô, kệ ván 17 ở cao 2300 | – | chăn mền, vali |

## Khung sắt (hộp 40×40×1,4 sơn tĩnh điện, dầm đầu cửa 40×80)
- 5 khung đứng: 2 khung áp tường trái/phải + 3 khung ở chỗ chồng mí cánh, nên cột không cản lối lấy đồ.
- Mỗi khung là **khung chữ nhật kín** (sửa 2026-11-09, Tuan thấy ngang kệ trước không có chống):
  cột trước + cột sau **suốt sàn → đỉnh**, cột giữa (sàn → 2260, hàn tai đỡ ống treo), dầm kệ + dầm đỉnh.
  Ngang kệ trước/sau tựa thẳng lên cột → tải hộp nóc xuống sàn, không còn công-xôn.
  Cột trước cách tim ống ~300: móc áo rộng 450 không chạm.
- 4 thanh ngang tường – tường (kệ trước/sau, đỉnh trước/sau) + dầm đầu cửa 40×80 bắt ray trên.
- Mỗi chân cột có bản đế 60×60×4 (tì sàn, bắt nở tùy chọn). Bắt vào tường bằng bát + nở ở 2 tường bên và tường sau
  (tường nhà Tuan – chọn bắt nở 2026-11-09).
- **Ống treo** Ø27 × 1,0 inox, nhịp lớn nhất 799: treo 40 kg/ống → ứng suất 77 MPa, võng 2,0 mm (PASS).
  Giới hạn ~52 kg/ống với dày 1,0; dày 1,2 → ~61 kg/ống. Ống bắt vào tai hàn trên cột giữa (không bắt vít vào hộp 1,4).
- Vật tư (`bom.csv`): ~59,4 m hộp 40×40, 3 m hộp 40×80, 29,7 m hộp 20×40 + 12,4 m hộp 13×26 (cánh), tổng ~148 kg
  (tính theo độ dày giả định, TODO theo hàng mua).

## Cửa lùa – bánh đỡ dưới + bánh dẫn hướng trên (bản vẽ `renders/12-chi-tiet-ray.png`)
- **Ray dưới** (nhôm, bắt vít xuống sàn): đế dày 5 + 2 gờ 6×8, 2 lằn cách 54. **Chịu toàn bộ tải cánh.**
- **Bánh đỡ dưới** Ø40 ổ bi, rãnh U/V ôm gờ, 2 bánh/cánh cách mép 70, hộp bánh có vít chỉnh cao (cân cánh thẳng đứng).
- **Ray trên**: 2 máng chữ U lòng 27 × sâu 45, treo dưới dầm đầu cửa 40×80. **Không chịu tải**, chỉ giữ cánh đứng.
- **Bánh dẫn hướng trên** Ø25 trục đứng, 2 bánh/cánh cách mép 60, ăn vào máng 20.
- **Lắp**: nâng cánh 25 đẩy bánh trên vào máng → hạ bánh dưới lên gờ → vặn **khóa chống nhảy** lên (khe còn 5 < 8 = độ nâng
  để bánh dưới thoát gờ) → không nhấc cánh ra được. Script tự kiểm 4 điều kiện (`PASS lap_dat/an_khop/chong_nhay/vung_ray`).
- Chặn cuối cao su 2 đầu mỗi máng; viền sắt cánh làm tay nắm; ron chổi ở mép chồng mí.
- Mép dưới cánh cách gờ 7, mép trên cách miệng máng 5 → đỉnh dầm 3055.

**Chọn mua (tiết kiệm):** mua **bộ cửa lùa đỡ dưới** (bánh dưới + bánh trên + ray dưới/trên cùng hãng) – rẻ hơn mua lẻ và
khớp nhau. Khi mua, đối chiếu 4 số với model: chiều cao gờ ray dưới, lòng + độ sâu máng trên, đường kính bánh, tải/bánh.
- **Tải mỗi bánh ≥ (khối lượng cánh ÷ 2) × 1,5.** Khối lượng cánh ≈ 4 × (1 thanh lam) + ~10,4 kg sắt → **cân 1 thanh trước**.
- Tham khảo giá: ray âm T309 ~95.000 đ/3 m, <50 kg/cánh (Phú Hải); Garis GR67 bánh 156.000 đ/cánh, ray 140.000 đ/3 m
  (chưa công bố tải). Cánh nặng hơn ~40 kg → bộ bánh đỡ dưới tải 80–100 kg (cửa lùa nhôm/kho), giá TODO.
- Có số thật thì sửa `P` (trk_base, ridge_h, wheel_d, roller_d, ch_depth…) → chạy lại, script báo FAIL nếu không lắp được.

## Mô phỏng trượt (Blender)
- Mở `design/wardrobe.blend`, bấm **Space**: lần lượt C1 → C2 → C3 → C4 lùa mở rồi đóng, đúng hành trình thật
  (dừng khi chạm cánh cùng ray/chặn cuối), bánh dưới quay theo quãng đường lăn. Mỗi cánh gắn vào 1 Empty `CanhN-goc`.
- Video: `blender -b -P build_wardrobe.py -- --out renders --anim` → khung ở `anim-frames/`, ghép
  `ffmpeg -framerate 24 -i anim-frames/f_%04d.png -c:v libx264 -pix_fmt yuv420p renders/20-mo-phong-lua-cua.mp4`.

## Khóa + chốt (Tuan 2026-11-09: chốt bi + khóa chồng mí; bản vẽ `renders/13-khoa-chot.png`)
- **Chốt bi** (4 cái): vít bi lò xo gắn trên khóa chống nhảy, bi Ø6 bật vào lỗ Ø5 khoan trên lưng máng trên ở đúng vị trí
  đóng của từng cánh → cánh không tự trôi, và lỗ khóa 2 cánh luôn thẳng hàng khi đóng.
- **Khóa chồng mí** (3 khóa ấn **đồng chìa**) ở 3 chỗ chồng mí, cao 1129: mặt khóa xuyên lam cánh ngoài (C1, C3), thân bắt
  vào giằng sau 13×26; chốt Ø8 bắn ra sau qua khe 8 vào lỗ Ø10 khoan trên **viền sắt** cánh trong (C2, C4) – không bắn vào lam.
  Vị trí khóa x = 629 / 1531 / 2308 (tâm viền cánh trong). Viền 2 cánh lệch nhau ~60 nên khóa phải nằm trên lam cánh ngoài.
- 4 cánh đóng kín tường–tường, C1/C4 tì chặn cuối → khóa 3 điểm là cả hàng không lùa được.
- Chặn cuối đã sửa: mặt chặn cách tường 46,5 (bánh trên cách mép 60, Ø25) → mép cánh dừng sát tường.
- Script kiểm thêm: `khoa_tren_lam` (lỗ khóa không cắt viền), `khoa_an_vien` (hành trình chốt ≥ khe + 5), `chot_bi`.
- TODO theo khóa mua: đường kính mặt khóa, hành trình chốt (đang giả định 14), chiều dài thân.

## Danh sách mua phụ kiện (giữ thiết kế bánh đỡ dưới + dẫn hướng trên, cánh ước 50–70 kg)
Tải mỗi bánh dưới ≥ (khối lượng cánh ÷ 2) × 1,5 → cánh 50 kg: 38 kg/bánh · 60 kg: 45 · 70 kg: 53. **Cân 1 thanh lam để chốt.**

| # | Phụ kiện | SL | Chọn | Giá tham khảo |
| --- | --- | --- | --- | --- |
| 1 | Bánh đỡ dưới cửa lùa sắt, ray U, **loại hàn** (hoặc bắt vít), bánh nylon ổ bi | 8 | hàn vào mặt sau (mặt trong) ống viền dưới → mặt trước sạch | 95.000 đ/bánh (vít 110.000) [vattunganhcua](https://www.vattunganhcua.vn/phu-kien-cua-cong?view=list) |
| 2 | Ray dưới U đúng cặp với bánh, 3 m | 2 | bắt vít/dán sàn, dóng thẳng dưới máng trên | TODO |
| 3 | Bánh bạc đạn 608 bọc nylon + bu lông M8 (dẫn hướng trên) | 8 | bắt lên ống viền trên bằng tán rút ren M8 | TODO |
| 4 | Máng trên: thép U (hoặc 2 sắt la hàn) lòng = Ø bánh trên + 2, sâu ≥ 45 | 2 × 3 m | hàn dưới dầm đầu cửa, sơn đen | TODO |
| 5 | Khóa chống nhảy tự làm: bu lông M8 + ê-cu hãm + đầu cao su trên ống viền trên | 4 | vặn lên còn khe 5 | vài nghìn đ |
| 6 | Vít bi lò xo M8 (chốt bi) | 4 | vặn vào đầu khóa chống nhảy | TODO |
| 7 | Khóa ấn tủ cửa lùa (push lock) **đồng chìa**, hành trình chốt ≥ 13 | 3 | thân bắt giằng sau 13×26 | TODO |
| 8 | Tán rút ren thép M5 + M8, kìm rút | ~40 | mọi chỗ bắt vít vào hộp 1,2–1,4 | TODO |
| 9 | Chặn cuối cao su (hoặc tự cắt cao su đặc) | 4 | 2 đầu mỗi máng, mặt chặn cách tường 46,5 | TODO |
| 10 | Ron chổi chống bụi dán mép chồng mí | 4 × 2,94 m | | TODO |
| 11 | Ống inox Ø27 **dày 1,2** + tai đỡ hàn | 8 ống | treo nặng: ~61 kg/ống | TODO |
| 12 | Nở sắt M8 + bát L bắt khung vào tường | ~20 | 2 tường bên + tường sau | TODO |

- Không dùng bộ bánh tủ áo thông dụng (vd Cariny CWA-204 40–50 kg/cánh): cánh 2,94 m nặng 50–70 kg vượt mức; catalogue QUITTE giới hạn bộ 50 kg ở cánh cao 2,5 m.
- Mua xong gửi số thật (Ø bánh dưới, cao từ đáy bánh tới mặt hàn, gờ ray, Ø bánh trên) → sửa `P` → script kiểm lại lắp đặt/chống nhảy.

## TODO
- W thực tế; số sóng, khối lượng 1 thanh lam; bộ ray (khe dưới, cao ray trên, sâu ray đôi); độ dày hộp sắt.
- Tường sau ẩm thì chừa khe ~20 sau quần áo hoặc ốp tấm chống ẩm (chưa có trong model).

## An toàn
- Khung sắt **phải bắt nở vào tường** ở cả 3 phía + sàn. Không để khung tự đứng.
- Cánh cao 2,9 m, nặng: 2 người lắp, có chặn chống nhảy ray và chặn cuối ray. Trẻ nhỏ dễ kẹt tay ở chỗ chồng mí.
- Khoan tường: dò đường điện âm trước khi khoan.
