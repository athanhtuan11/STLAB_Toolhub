# Hướng dẫn lắp ráp – Camera ESP32-S3-CAM vỏ mẫu D (để bàn, đế xoay)

Dành cho học sinh từ lớp 6, làm cùng thầy/cô. Viết 2026-11-05 từ model SolidCraft `solidcraft/cam_d.sc`
(sau `python solidcraft/build_cam_d.py`). Ảnh: `solidcraft/images/assembly/step-XX.png` – tạo lại bằng
`python solidcraft/render_assembly.py`.

Ảnh: chi tiết **mới màu vàng**, phần đã lắp **màu xám**, mạch **màu xanh lá**, ống kính **màu vàng đậm**.
Chi tiết mới được kéo ra theo hướng lắp.

## Trước khi bắt đầu

**In 3D**
- In trước Coupon (`solidcraft/plates/p1-fit-test/p1-fit-test.3mf`) để chọn cỡ lỗ M3, ổ đai ốc, lỗ ống kính, da đèn, chốt xoay.
  Báo cỡ cho Claude sửa thông số rồi mới in vỏ.
- Vỏ in **PETG**, **1 bàn in** `solidcraft/plates/p2-enclosure/p2-enclosure.3mf` (đã xếp sẵn, đúng hướng in, **không cần support**;
  khoảng 3 giờ 36 phút, 98 g). Mở bằng Bambu Studio rồi in, không phải xếp lại.
- Trên bàn có 5 chi tiết: thân `body` (nằm mặt sau xuống), mặt trước `bezel` (úp mặt trước xuống), khung U `u_frame`
  (đĩa xoay liền 2 tay), đế `base`, nắp chốt `pin_cap`.

**An toàn**
- Chỉ cấp nguồn **USB 5 V** qua cổng mini USB của đế nạp.
- Cắm/rút cáp FPC camera **khi đã rút nguồn**. Cáp FPC dễ gãy, không gập mạnh.
- Mạch nóng tới khoảng **70 °C** khi chạy video lâu. **KHÔNG che**, không dán kín các khe tản nhiệt trên nóc và dưới đáy thân, không bọc vỏ.
- Gỡ chi tiết PETG khi bàn in **đã nguội**. Cạo ba-via bằng kìm, lưỡi hướng ra xa tay.

**Dụng cụ**
- Lục giác/tua vít hợp với vít đã mua.
- Kìm mũi nhọn.
- Giấy nhám mịn.

**Vít cần** (xếp riêng từng loại vào hộp, ghi nhãn):
| Vít | Số lượng | Vị trí / Ghi chú |
|---|---|---|
| M2.5 đầu bằng (đầu côn 90°, mũ ≤ Ø5 mm), dài 8–10 mm | 4 | Mặt trước, tự ren vào trụ nhựa |
| M2.5 đầu trụ/đầu tròn × 8 mm | 1 | Nắp chốt, tự ren vào chốt đế |
| M3 × 12 đầu trụ lục giác chìm (DIN 912) + đai ốc M3 | 2 + 2 | Trục nghiêng |
| Vít gỗ đầu bằng Ø4 mm (mũ ≤ Ø8,5 mm) | 2 | Tuỳ chọn: bắt đế xuống bàn/kệ |

Vít tự ren vào nhựa: vặn chậm, **vừa tay**, siết quá sẽ toét ren.

**Thứ tự**: A. Đế xoay (1–3) → B. Thân + mạch (4–6) → C. Ráp thân lên khung U (7) → D. Kiểm tra + chỉnh nét (8).

## Bước 1 – Đế
**Cụm A – Đế xoay**
**Cần lấy:** đế `base` ×1. Tuỳ chọn: vít gỗ đầu bằng Ø4 mm ×2.
![](solidcraft/images/assembly/step-01.png)
1. Đặt đế lên mặt phẳng.
2. Tuỳ chọn: bắt đế xuống bàn/kệ bằng 2 vít gỗ qua 2 lỗ côn trong lòng đế. **Phải làm TRƯỚC bước 2** vì khung U che lỗ.

**Kiểm tra:** đầu vít chìm hẳn dưới mặt lòng đế, không cấn đĩa xoay.

## Bước 2 – Khung U lên đế
**Cụm A – Đế xoay**
**Cần lấy:** khung U `u_frame` ×1.
![](solidcraft/images/assembly/step-02.png)
1. Lồng lỗ giữa đĩa xoay vào chốt Ø8 mm ở giữa đế. Đĩa nằm trong lòng đế.

**Kiểm tra:** xoay đĩa bằng tay thấy trơn. Chặt thì chà nhẹ lỗ đĩa bằng giấy nhám, **không ép**.

## Bước 3 – Nắp chốt
**Cụm A – Đế xoay**
**Cần lấy:** nắp chốt `pin_cap` ×1, vít M2.5 × 8 đầu trụ/đầu tròn ×1.
![](solidcraft/images/assembly/step-03.png)
1. Đặt nắp vào hốc tròn giữa đĩa.
2. Vặn vít xuyên nắp vào lỗ giữa chốt. Siết vừa tay.

**Kiểm tra:** đĩa vẫn xoay được nhưng không nhấc lên được (nắp giữ đĩa, có khe 0,2 mm).

## Bước 4 – Đai ốc vào thân
**Cụm B – Thân + mạch**
**Cần lấy:** thân `body` ×1, đai ốc M3 ×2.
![](solidcraft/images/assembly/step-04.png)
1. Ấn mỗi đai ốc vào ổ lục giác ở mặt trong của 2 trụ hai bên thân (từ **BÊN TRONG** thân). **Phải làm trước khi cho mạch vào.**
2. Lỏng thì dán một chút băng dính giữ. Chặt thì **[Cần người lớn]** dùng vít M3 kéo đai ốc vào.

**Kiểm tra:** đai ốc nằm phẳng trong ổ, không xoay.

## Bước 5 – Mạch + camera vào thân
**Cụm B – Thân + mạch**
**Cần lấy:** mạch ESP32-S3-CAM đã cắm trên đế nạp CH340; camera OV3660 đã cắm cáp FPC và dán lên khay thẻ nhớ.
![](solidcraft/images/assembly/step-05.png)
1. **Rút nguồn.**
2. Luồn khối mạch vào thân từ mặt trước, ống kính hướng ra ngoài. Mép mạch trượt theo 2 ray hai bên, đẩy tới khi chạm gờ phía sau.
3. Cổng mini USB của đế nạp phải nằm đúng ô chữ nhật ở đáy thân.
4. TODO: kiểm cổng USB của đế nạp nằm ở cạnh ngắn phía dưới (đối diện đầu camera). Nếu nằm cùng đầu với camera thì báo Claude sửa vỏ.

**Kiểm tra:** khối mạch không lắc, cáp FPC không bị kẹp.

## Bước 6 – Mặt trước
**Cụm B – Thân + mạch**
**Cần lấy:** mặt trước `bezel` ×1, vít M2.5 đầu bằng dài 8–10 mm ×4.
![](solidcraft/images/assembly/step-06.png)
1. Luồn ống kính qua lỗ tròn lớn của mặt trước (lỗ rộng hơn ống kính 0,5 mm mỗi bên).
2. 4 chân nhỏ mặt sau tì vào 4 góc mạch.
3. Vặn 4 vít ở 4 góc, đầu vít chìm vào lỗ côn.

**Kiểm tra:** ống kính không chạm thành lỗ, xoay ống kính bằng tay vẫn được. Mặt trước khít, không hở.

## Bước 7 – Thân lên khung U
**Cụm C – Ráp thân lên khung U**
**Cần lấy:** cụm thân đã lắp (bước 4–6), vít M3 × 12 đầu trụ lục giác chìm ×2.
![](solidcraft/images/assembly/step-07.png)
1. Đặt thân vào giữa 2 tay khung U, trùng lỗ trục 2 bên.
2. Từ mặt ngoài mỗi tay, luồn vít M3 qua lỗ (đầu vít nằm trong hốc lõm) vào đai ốc trong thân.
3. Nghiêng thân tới góc muốn rồi siết vừa đủ để thân giữ góc.

**Kiểm tra:** thân nghiêng được khi nới vít, đứng yên khi siết. Mặt thân không cọ vào tay khung.

## Bước 8 – Kiểm tra + chỉnh nét
**Cụm D – Kiểm tra + chỉnh nét**
![](solidcraft/images/assembly/step-08.png)
1. Cắm cáp USB 5 V vào cổng mini USB qua ô ở đáy.
2. Mở `http://stlab-cam.local` (cùng Wi-Fi nhà) để xem hình.
3. Xoay ống kính để chỉnh nét. Ảnh bị nằm nghiêng 90° là do camera xoay so với mạch – chỉnh trong firmware, **không phải lỗi lắp**.
4. Chạy thử 20 phút, sờ thân vỏ. Nóng ấm là bình thường. Nóng không chạm tay được thì **rút điện**, báo lại.
   TODO: đo nhiệt khi đã lắp vỏ.

**Kiểm tra cuối:** đế xoay trơn, thân nghiêng giữ góc, hình nét.

## Lịch sử
- 2026-11-05 bản đầu (SolidCraft, lỗ ống kính 15,0 mm, ống kính nhô khoảng 10 mm trước mặt vỏ để chỉnh nét).
