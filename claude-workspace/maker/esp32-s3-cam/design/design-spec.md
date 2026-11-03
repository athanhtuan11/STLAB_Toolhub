# esp32-s3-cam – design spec bước 0 "Giao diện" (vỏ camera + web)

Ngày 2026-11-03 · product-designer · Tuan duyệt bằng ảnh: `contact-sheet.png` (tổng), `concepts/*.png` (vỏ), `ui/*.png` (web).
Khối minh họa dựng bằng `make_concepts.py` (Blender 5.2, Cycles), **chưa phải CAD**. Không đổi mạch, không sửa firmware.
Ghi chú: "khối 27 × 40,5 × 12 mm" trong ảnh A/B/C ban đầu là giả định cũ; D dùng khối mục 0 (27 × 40,5 × 20–25 mm).

> **Phương án D được Tuan chọn ngày 2026-11-03** (mục 2b). A/B/C giữ để tham khảo.

## 0. Khối mạch dùng cho CAD (số cộng đồng, ƯỚC – in thử để kiểm)

Nguồn: `docs/research-notes/esp32-s3-cam-hardware.md` mục 5 (Tuan không đo; CAD dùng số cộng đồng rồi in thử kiểm).
- Mạch ESP32-S3-CAM cỡ AI-Thinker ESP32-CAM: **27 × 40,5 × 4,5 mm**; camera gập nằm trên khe TF, đầu camera ~ 8,5 × 8,5 × 4,2 mm.
- Mạch chồng trên **đế nạp kiểu ESP32-CAM-MB** ~ 40 × 27 mm, dày ~ 10 mm; **cổng mini USB + nút IO0/RST nằm trên đế nạp, ở cạnh ngắn** (render: rìa dưới).
- **Khối tổng ước 27 × 40,5 × 20–25 mm** (ƯỚC). Mạch đứng thẳng, mặt 27 × 40,5 song song mặt trước, ống kính ra mặt trước.
  Hộc mạch 31 × 44,5 × 28 mm (dư 2 mm mỗi bên + chỗ FPC); hộp D sâu 40 mm = bezel 3 + hộc 28 + thành sau ≥ 1,6 + gờ giữ ⇒ vẫn đủ, tỉ lệ 56 × 40 × 64 vẫn đẹp (kiểm trên ảnh), không cần làm sâu hơn. Nếu số thật > 25 mm → tăng sâu hộp, thêm 4–5 mm.
- Nút IO0/RST ở đế nạp cạnh ngắn: cần lỗ chọc kim hoặc nút nhấn xuyên vỏ (TODO khi CAD biết vị trí – xem ảnh mạch thật; không bịa tọa độ).
- Các giá trị chưa có nguồn (TODO, đo/ảnh mạch lúc CAD): tâm ống kính (render giả định lệch lên 9 mm), tọa độ 2 đèn (giả định Ø3,4 cách nhau 7 mm, dưới ống kính 12–14 mm), lỗ bắt vít (nếu có – nếu không thì kẹp bằng gờ + nắp), kích thước đầu cáp mini USB (đầu thẳng cần ≥ ~ 30 mm phía dưới; **khuyến nghị cáp mini USB đầu vuông góc** hoặc dùng ô cắt sau-dưới cho cáp uốn ra sau).
- **Chiều camera:** module camera thật nằm **NGHIÊNG 90° so với mạch** (ảnh test bị xoay 90°, không phải 180°). CAD đặt mạch xoay 90° trong hộp sao cho ảnh thẳng; firmware chỉ lật 180°. Chiều +90°/−90°: xác định lúc in thử.

## 1. Ngôn ngữ hình khối chung

"Khối mềm có một mặt phẳng nói chuyện": thân trắng bo to, **một mặt trước phẳng khác màu mang mắt (ống kính + 2 đèn + chữ STLAB)**.
Ba từ khóa: **thân thiện · gọn gàng · tinh nghịch**.

Chung cho cả 3 phương án (không đổi giữa A/B/C để sau làm "mắt robot" cùng ngôn ngữ):
- Ống kính hiển thị: vòng ngoài Ø26 (A, B) hoặc iris Ø40 (C), đồng tâm kính Ø12 (lỗ thật cho ống kính mạch: **Ø ≥ ống kính đo + 1,0 mm, TODO đo**).
- 2 đèn trạng thái dưới ống kính, khoảng cách ngang 7 mm: cửa sổ Ø3,4 mm, **da mỏng 0,4–0,6 mm** (2 lớp) để PETG trắng khuếch tán ánh đèn,
  không cần chi tiết light pipe riêng. TODO thử mẫu da mỏng với WS2812 thật (độ sáng) – nếu mờ, khoét thông + dán miếng nhựa trong.
- Chữ **STLAB** (Be Vietnam Pro Bold, cao 4,4–5 mm, nét ≥ 0,8 mm) khắc sâu 0,6 mm dưới đèn. Chấm nhấn vàng (nếu muốn): vạch 6 × 2 mm cạnh chữ, tô bút/miếng dán, **không** làm part riêng.
- Khe thoát nhiệt (bắt buộc, chip lên 67,8 °C): **hút ở dưới – thoát ở trên**, mỗi nhóm 6–7 khe 2,0 × 18–20 mm (≈ 216–280 mm² mỗi nhóm), khe tạo theo
  hướng thẳng đứng/ngang trên mặt phẳng ngang để in không support. Không che khe bằng đế/tường (xem từng phương án).
- Cổng USB: ô cắt 13 × 8 mm ở rìa dưới mặt sau (đầu cáp mini USB có vỏ nhựa, TODO đo), cáp ra phía sau-dưới, **bo mép lỗ ≥ 1,5 mm**, không ép dây vào cạnh nhựa.
- Chốt chiều camera: vỏ chỉ lắp được **một chiều** – USB luôn ở dưới, khe nhiệt ra ở trên (mũi tên ▲ khắc 0,6 mm ở mặt trong nắp sau và dưới đáy để dễ ráp);
  mạch được dẫn bằng 2 rãnh bên + 1 gờ lệch (chống lắp ngược). Vì camera nằm nghiêng 90° so với mạch, **CAD phải đặt mạch xoay 90° trong hộp sao cho ảnh thẳng** (hộc mạch, rãnh dẫn, vị trí lỗ ống kính và cổng USB tính theo chiều đã xoay); firmware chỉ lật được 180° nên không bù được 90°. Chiều xoay (+90° hay −90°) xác định khi in thử.
- Không cạnh sắc: mép cầm ≥ bo R1; chân tiếp bàn vát 0,8 mm (không bo tròn tại mặt bàn in).
- Thành vỏ ≥ 1,6 mm (4 đường 0,4); khe lắp theo `tools/model-study` fit-library (không tự đặt khe – ghi `fit: TODO` tại từng khớp bên dưới).
- Tối đa 3 màu nhựa; mỗi màu = part riêng (hạn chế AMS).

## 2. Phương án

### A – "Sỏi" (khối ~ 60 × 40 × 66 mm + đế hình đĩa Ø70)
- Hình: viên sỏi vuông bo to (bo mặt ngoài R9 trên render), mặt trước phẳng xanh thông, đế đĩa có cổ + khớp cầu Ø22.
- Part: ① mặt trước (xanh thông) ② thân sau (trắng) ③ đế đĩa + cổ (cát/be) ④ cầu khớp. 4 part đơn sắc.
- Pan/tilt: khớp cầu in sẵn bắt chặt bằng ma sát (snap): thuận tiện xoay mọi hướng; rủi ro: khe khớp cầu rất nhạy dung sai/co ngót PETG, cần mẫu thử.
- Treo tường: đĩa đế có 1 lỗ khóa (keyhole) giữa đáy + vùng băng dính 3M Ø50 (lõm 0,5 mm). Khi treo, thân quay ngược → khe hút/thoát nhiệt đổi vai: **cần quyết** (xem mục 6).
- Đánh đổi: đẹp nhất khi nhìn thẳng (mặt xanh), nhưng khớp cầu là rủi ro lớn nhất về in + lắp lại.
- In: mặt trước và thân in theo mặt ráp (phẳng) xuống bàn, vòm lên trên; **bản in thay bo R9 bằng vát 45° 7 mm + bo R2** (render bo mềm hơn một chút, ngoại hình gần như giữ);
  trần hộc dạng mái 45° (bậc thang) để không cầu > 15 mm. Hộc mạch mở ở mặt sau; nắp sau snap-fit + 1 vít (fit: TODO).

### B – "Hộp bo tròn" (khối 56 × 40 × 64 mm, bo R5; khung chữ U + đế 72 × 48 × 7 mm)
- Hình: hộp trắng bo vừa, mặt trước ốp **khung đen** dày 3 mm (đen = mắt trông "như camera thật", chữ STLAB khắc trên khung), khung chữ U xanh thông giữ 2 bên,
  tâm xoay M3 (đầu vít đen Ø10 trên mặt ngoài).
- Part: ① thân + nắp sau (trắng) ② khung mặt trước (đen) ③ khung chữ U + đế (xanh thông) ④ 2 đầu chốt (đen) hoặc dùng vít M3 – 3 màu, 4–5 part.
- Pan/tilt: nghiêng ±30° bằng ma sát ở 2 chốt tâm (M3 + đệm, fit: TODO); xoay trái/phải = xoay cả đế trên bàn (chưa có pan thật; nếu cần, thêm đĩa xoay – xem mục 6).
- Treo tường: **đế = tấm treo**: 2 lỗ khóa Ø4,2/Ø8 (TODO theo vít dùng), cách nhau 58 mm; mặt dưới có vùng băng dính 3M 40 × 30 mm lõm 0,5 mm. Treo thì khung U đứng sát tường – thân vẫn thông thoáng 14 mm dưới đáy nhờ chân khung.
- Đánh đổi: dễ in và dễ tháo lắp nhất, nhìn chắc chắn "như thiết bị"; ít cá tính hơn A/C, đế hơi to so với camera.
- In: thân in mặt ráp xuống (hộc mở lên trên), vát 45° 5 mm + bo R2 phía sau; khung U nằm ngang trên bàn (đế phẳng); khung đen in mặt trước xuống bàn (mặt nhám Textured PEI hợp kính mờ).

### C – "Mắt" (cầu cụt Ø58, dày 41 mm, mặt phẳng Ø41; vành đế Ø52 + đĩa Ø72)
- Hình: cầu trắng cắt phẳng hai đầu (vừa để in, vừa tạo "iris"), mặt trước phẳng xanh thông Ø40 chứa vòng đen và kính; nằm trong vành đế đen, xoay tự do như nhãn cầu.
- Part: ① nửa trước (trắng) ② nửa sau (trắng) ③ iris (xanh thông, dán/snap) ④ vành đế + đĩa (đen). 3 màu, 4 part.
- Pan/tilt: tilt = lăn cầu trong vành (ma sát); pan = xoay vành trên đĩa. Rất thân thiện lớp học; **làm mắt robot cùng thân C**: đĩa thay bằng tấm bắt vào robot (TODO lỗ theo robot).
- Treo tường: lăn vành + 2 lỗ khóa trên đĩa; băng dính 3M dưới đĩa. Cầu hơi to so với mạch (dư ~ 20 mm) – lợi cho tản nhiệt, thừa chỗ pin/loa sau này.
- **Lưu ý đã thấy khi nhìn ảnh:** khe hút nhiệt phía dưới cầu bị vành đế che trong bản render → CAD phải khoét 4 khe hút ở thành vành (hoặc đáy đĩa có 4 khe); nếu không, đối lưu bị chặn.
- In: mỗi nửa cầu in mặt chia xuống bàn, vòm lên; mặt phẳng cụt Ø41 ≥ 2 R sin45° (= Ø41) đảm bảo mặt nghiêng ≥ 45° so với bàn, không cầu > 15 mm; hộc cắt chữ nhật lệch tâm tránh bù cầu.
- Đánh đổi: khác biệt rõ nhất, đúng "mắt robot"; to nhất, nhiều khoảng trống, ráp 2 nửa cầu cần khe chuẩn.

## 3. CMF (A/B/C)

**Màu chỉ để tham khảo; khi in Tuan tự chỉnh theo nhựa thực tế có sẵn.** Không cần tên màu hãng.

Tên màu hãng: **TODO xác nhận từng cuộn** (chưa kiểm danh mục Bambu PETG Basic; render dùng gần đúng hex bên dưới).

| Vai | Màu | Hex render | A | B | C |
|---|---|---|---|---|---|
| Thân | Trắng (White) | `#CBD1CD` (sau tông ảnh) | thân sau | thân + nắp | cầu 2 nửa |
| Mặt "mắt" | Xanh thông (Forest Green / Dark Green, TODO) | `#1E5A45` | mặt trước | khung U + đế | iris |
| Khung/đế tối | Đen (Black) | `#1B1E1F` | – | khung mặt trước + chốt | vành đế + đĩa |
| Đế nhẹ | Cát/be (Sand / Beige, TODO) | `#CBB997` | đế + cổ + cầu | – | – |
| Nhấn | Vàng sợi nhựa `#E8B33A` | – | chấm vàng cạnh chữ STLAB (bút/dán) | cùng | cùng |

Bề mặt: mặt dưới tiếp bàn = Textured PEI (hạt nhám); mặt nhìn thấy in mặt phẳng lên (0,16 mm) để láng; không sơn. Ống kính = lỗ thật + kính/lens của mạch,
vòng ngoài trang trí in đen/xanh.

## 4. Mockup giao diện web (`ui/cam-ui.html`)

HTML tĩnh 1 file, không mạng ngoài, không framework, JS ~ 25 dòng (chỉ đổi theme/nhiệt độ cho mockup – dữ liệu thật sẽ lấy từ `/status`).
Dùng palette `studio/design/tokens.json` sáng (trang ESP32 giữ bộ sáng) + biến thể tối; font Be Vietnam Pro (khi nhúng flash: bỏ font, dùng font hệ thống).

- Nội dung: khung video 4:3 lớn, nút **Chụp ảnh** (nút chính), **Tải ảnh**, công tắc **Lật ảnh 180°**, chọn độ phân giải (QVGA → UXGA);
  thẻ "Kết nối": Wi-Fi nhà `VIETTEL_Suong`, −49 dBm (thanh tín hiệu + chữ "Tốt"), IP 192.168.1.127, `stlab-cam.local`;
  thẻ "Chip": 53,8 °C (số lớn + chữ "Bình thường" + thanh), 18 fps, SVGA 800 × 600.
- Cảnh báo nóng: **< 60 °C bình thường (xanh) · 60–70 °C "Hơi nóng" (vàng) · ≥ 70 °C "Quá nóng" (đỏ)** – màu + chữ + câu hướng dẫn ("đừng che khe trên và khe dưới").
  Ngưỡng đề xuất (TODO chỉnh theo đo thực: chip 41–42 °C lúc nghỉ, 67,8 °C khi stream lâu). Ảnh `ui-phone-toi-canhbao.png` xem trạng thái này.
- Kiểm checklist DESIGN.md: không tràn ngang ở 390 px; nút ≥ 46 px; có viền focus; chụp cả sáng và tối.
- Nút Chụp ảnh/Tải ảnh/Lật ảnh/Độ phân giải **chưa nối** firmware (probe hiện có `/capture`, `/stream`, `/control?framesize=`); "Lật ảnh" cần thêm tham số vflip/hmirror – việc firmware sau.
- Kích thước nhúng ước tính: HTML+CSS+JS ~ 12,9 KB chưa nén (~ 4,5 KB gzip, gồm cả SVG mẫu và @font-face); SVG hình mẫu **bỏ** khi nhúng.

## 5. Đã sửa gì sau khi nhìn ảnh

1. Lần 1 ảnh cháy sáng (thân trắng mất chi tiết, nền trùng thân) → hạ đèn ~ 4 lần, thêm hiệu chỉnh phơi sáng −0,8, thân trắng ngả xám nhẹ (`#CBD1CD`), sàn xám xanh đậm hơn nền.
2. A: mặt xanh là tấm phẳng vuông chồng lên thân, nhìn như "ốp tường" → đổi thành lát cắt trước của chính viên sỏi (bo R9 liên tục, đường chia màu 0,3 mm) – nhìn ra viên sỏi.
3. A: mặt trước đen kịt do hai mặt trùng phẳng → đẩy mặt xanh ra 0,3 mm.
4. C: cầu "nổi" trên vành đế → hạ cầu vào vành 5 mm. Phát hiện vành che khe hút dưới → ghi vào mục "Lưu ý" của C.
5. Ảnh mặt sau lóa vì đèn nhiệt gần camera → lật đèn ra phía sau camera và giảm 45 %.
6. Web: bản chụp điện thoại lần đầu bị cắt ngang (Edge headless ép cửa sổ ≥ 500 px) → chụp trong iframe 390 px rồi cắt; kiểm lại không tràn.

## 2b. Phương án D – ĐƯỢC TUAN CHỌN (2026-11-03): hộp B + khung U của B trên đế tròn xoay kiểu C

Ảnh: `contact-sheet-D.png`, `concepts/D-ghep-{truoc,sau,tile,conhieu,no}.png`.

- **Hộp + khung U giữ như B**: hộp trắng 56 × 40 × 64 mm bo R5, khung đen mặt trước 3 mm, ống kính Ø26/Ø12, 2 đèn, chữ STLAB, khe nhiệt trên + dưới, ô USB 13 × 8 mm đáy sau.
  Khung U: 2 tay dày 7 mm cao 70 mm, khoảng hở 0,6 mm mỗi bên (fit: lấy từ fit-library khi CAD).
- **Trục tilt = vít M3 + đai ốc hoặc insert, mỗi bên 1 vít** (Tuan chốt). Render: đầu vít Ø5,6 có rãnh chữ thập + long đen Ø8,5 trên mặt ngoài 2 tay U. Chiều dài vít, kiểu đai ốc/insert (lục giác lõm vào thân, hay insert ép nóng), khe lỗ trục: **lấy từ fit-library khi CAD, chưa có số**.
  Nghiêng ±30° bằng ma sát siết bằng vít. Kiểm hình học: tâm trục cao hơn đĩa 52 mm, góc đáy thân quét bán kính ≈ 38 mm ⇒ không chạm đĩa ở ±30° (khe hút nhiệt dưới vẫn thông).
- **Đế xoay (pan) kiểu C, 2 part**: ① **đế/vành** Ø86 × 10 mm, lõm Ø77 sâu 4 mm, chốt giữa Ø8, 3 tai ma sát đàn hồi ② **đĩa xoay** Ø76 × 6 mm mang khung U (liền khối với khung U).
  - Đĩa lồng lên chốt giữa, nằm trong lõm; xoay ngang bằng tay.
  - Cơ cấu ma sát/nấc (in được, không support): **3 tai đàn hồi** (lưỡi mảnh in nằm ngang theo mặt bàn) trên đáy lõm tì vào mặt dưới đĩa, hoặc rãnh nấc 12 vị trí khắc dưới đĩa + 1 tai bi nhựa. Giữ đĩa khỏi nhấc lên: nắp chặn nhấn (snap) ở đầu chốt hoặc 1 vít ở đầu chốt – chọn khi dựng CAD (ưu tiên snap). Khe chốt/lỗ, độ dày tai, lực nấc: **lấy từ fit-library khi CAD, không đặt số ở đây**.
  - Toàn bộ chi tiết in mặt phẳng xuống bàn: đế (lõm hướng lên), đĩa + khung U (đĩa xuống bàn, tay U đứng lên – tay U cao 62 mm có thể in nằm nếu cần độ bền, quyết ở CAD), không support.
- **Treo tường**: đáy đế có **2 lỗ khóa** (Ø4,2 / đầu Ø8,5, cách nhau 58 mm – TODO theo vít dùng) + **vùng dán 3M Ø50 mm lõm 0,6 mm**. Treo tường thì **khung U vẫn thẳng** (đế là phần dính tường, đĩa xoay + khung vẫn quay quanh chốt nằm ngang → pan thành xoay quanh trục ngang; nếu muốn pan ngang thật khi treo, cần quyết: hộp hướng ra phía trước và xoay đĩa tạo hướng nhìn trái/phải sẽ lệch trục – chỉ phù hợp treo trên trần/kệ ngửa. Ghi vào "Cần quyết").
  Đáy lật hiện trong `D-ghep-no.png` (bên phải).
- Cổng USB: sau-dưới thân; cáp luồn ra phía sau giữa 2 tay U, có chỗ trống ≈ 20 mm giữa đáy thân và đĩa (thân nâng thêm 8 mm so với B để cáp uốn).
- **Màu (1 phối)**: thân trắng, khung mặt trước đen, **khung U + đĩa + đế xanh thông**, đầu vít kim loại tối, chấm vàng nhấn cạnh STLAB. Chọn xanh thông cho khung U/đế vì kết nối với mặt "mắt" của A/C, hài hòa với thân trắng và khung đen; đế đen sẽ nặng nề hơn. Màu chỉ để tham khảo; Tuan tự chỉnh theo nhựa có sẵn.
- Đánh đổi: nhiều part hơn B (thêm đế + đĩa), cao ≈ 96 mm, đế Ø86 chiếm bàn hơn B; đổi lại pan + tilt + treo tường và nhìn gọn, ổn định.

## 6. Câu còn mở

1. **Ngưỡng cảnh báo nhiệt web 60 / 70 °C** – Tuan chưa trả lời (đề xuất < 60 xanh, 60–70 vàng, ≥ 70 đỏ; TODO chỉnh theo đo thực).
2. Chiều xoay mạch 90° trong hộp (+90° hay −90°) – xác định khi in thử (mục 0).
3. Treo tường với D: đế dính tường thì trục pan nằm ngang; chọn hướng treo (treo ngửa/trần hoặc bỏ pan khi treo tường). Đề xuất: khi treo tường dùng khóa đĩa (không xoay), chỉ tilt.
4. Giữ đĩa xoay: snap hay vít ở đầu chốt (quyết lúc dựng CAD).
5. In thử kiểm khối mạch (số cộng đồng, mục 0) trước khi chốt CAD.

(Đã chốt: phương án D; trục tilt = vít M3 + đai ốc/insert.)

## 7. Việc kỹ sư phải dựng (sau khi Tuan chọn + đo)

- Mô hình tham số theo mục 0 (đọc từ `params.json` khi đã có số đo); part + màu theo mục 2–3.
- Chuẩn bị kiểm: thành ≥ 1,6; không cầu > 15 mm; mặt nghiêng ≥ 45° (nhất là bản vát thay bo R9, trần hộc mái 45°); khe lắp lấy từ fit-library.
- Khớp cần mẫu thử trước: khớp cầu (A), chốt xoay B (ma sát), da mỏng đèn 0,4–0,6 mm, lỗ ống kính.
- Khắc dấu lắp: mũi tên ▲ (chiều camera), chữ STLAB khắc 0,6 mm; ghi "Chiều camera" + "không che khe" vào `ASSEMBLY.md` khi có.
- Kiểm nhiệt thực sau lắp (stream 30 phút trong vỏ) – chip nghỉ 41–42 °C, ngưỡng khi stream 67,8 °C; nếu > 75 °C thêm khe hoặc tản nhiệt dán.
- Chưa có: ảnh tỉ lệ với bàn tay (dùng ổ điện 86 × 86 mm làm tham chiếu – cần xác nhận kích thước ổ điện cho đúng loại phổ biến ở Đức Trọng, TODO).

## 8. Đã sửa gì sau khi nhìn ảnh (phương án D)

1. Lần 1: chốt giữa của đế nhô lên khỏi đĩa, lộ dưới thân hộp → rút chốt về nằm trong lỗ đĩa.
2. Lần 1: ảnh "nghiêng + xoay" lệch khung vì khớp cha-con sai (phép nghịch đảo tính trước khi cập nhật vị trí) → cập nhật cảnh trước khi gán.
3. Thêm ảnh tách rời để thấy chốt, tai ma sát và đáy lật (lỗ treo, vùng dán 3M).
4. Đổi khối mạch theo số cộng đồng (27 × 40,5 × 20–25 mm): nâng hộp D thêm 8 mm (tâm trục 64 mm) để cáp/đầu USB có chỗ; tay U cao 70 mm.
