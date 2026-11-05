# english-teacher – design spec bước 0 (dáng sản phẩm)

2026-11-05 · product-designer · duyệt bằng ảnh: `contact-sheet.png`, `concepts/*.png` · dựng lại ảnh: `python make_concepts.py all` rồi `python make_sheet.py`.
Chưa phải CAD. Khớp, linh kiện, tầm với do phiên chính quyết; mọi con số dưới đây là **ước lượng theo khối giả định** (mục 1).

## 1. Khối giả định (TODO đo thật)

| Linh kiện | Số dùng để kiểm khoang | Nguồn |
|---|---|---|
| Bo Ai-Thinker ESP32-A1S Audio Kit | **≈ 75 × 65 × 25 mm** (gồm hàng chân, nút, jack) | **TODO**: chưa tìm được bản vẽ cộng đồng (thử `Ai-Thinker-Open/ESP32-A1S-AudioKit` trên GitHub: 404). Tuan đo bo thật bằng thước kẹp trước khi dựng CAD |
| Loa Ø52 mm | Ø52 × **20 mm sâu** (giả định), lỗ bắt vít/gờ: TODO | Tuan có loa; đo sâu + chỗ bắt |
| Cáp USB (Micro-USB hay USB-C): TODO | lỗ 15 × 8 mm ở lưng | xem bo thật |

Bố trí chung (cả 3 concept): loa nằm **hướng thẳng ra trước**, ép sát mặt trong lưới (mặt loa cách mặt ngoài ≤ 5 mm); bo dựng đứng sau loa,
cổng USB quay ra lưng, đáy chừa ≥ 15 mm cho dây. Khoang trong luôn rộng ≥ 100 × 85 mm → vừa bo với dư ≥ 10 mm mỗi phía.
Loa Ø52 là khối giới hạn khi thu nhỏ bản 2: thân không nhỏ hơn ≈ 90 mm rộng nếu vẫn dùng loa này (loa 40 mm: TODO → ≈ 75 mm). Bản 2 (S3 + INMP441 + MAX98357A,
bo nhỏ ≈ 25–35 mm mỗi cạnh: TODO) bỏ được khoảng 40 % thể tích sau loa → **thu hệ số ≈ 0,8 theo cả 3 trục** là hợp lý; hình khối cả 3 concept tròn nên co đều không méo.

Thước đo trong ảnh: **ly Ø80 × 95 mm** (ly sứ thường) và **sách tranh 200 × 200 mm**.

## 2. Ràng buộc chung (an toàn bé < 3 tuổi + in)

- Vỏ **một khối liền** hình ngoài; chia 2 nửa trước/sau, **4 vít M3 giấu ở đáy** (lỗ lõm Ø9 sâu 6 mm, dán miếng đệm cao su Ø16 che kín) – cùng một loại vít.
- Không chi tiết rời nhỏ: tai, cánh, tay, tai nghe **liền thân** (in chung thành part). Nút bấm = nắp silicon/PETG mềm **Ø50 mm**, cao nổi 9 mm, cạnh bo R 6; hành trình ≈ 2 mm (TODO công tắc: nút tactile 6 mm đặt dưới, nắp trượt trong vòng giữ).
- **Bo cạnh ngoài R ≥ 3 mm** mọi nơi (vùng cầm R ≥ 8 mm); không góc nhọn. Không có chi tiết nhô < Ø20 mm.
- Lưới loa: **lỗ Ø2,8 mm** (hình ảnh vẽ Ø2,8), bước 5,6 mm, vùng Ø56 mm. Ngón bé lọt Ø ≥ 6 mm nên không lọt. Lỗ micro: **3 lỗ Ø2 mm** gần nhau (ngón không lọt), cách loa ≥ 60 mm để giảm hú.
- Khe thoát nhiệt ở lưng: **5 khe 2 × 18 mm** (chừa vì PA/codec nóng); không khe nào ≥ 4 mm bề rộng.
- Đèn trạng thái: LED RGB phía sau nắp khuếch tán PETG tự nhiên mỏng **0,8 mm** (≈ 2 lớp bù thành vỏ 1,6 mm chỗ khác) → ánh sáng mềm, không thấy chip.
  Độ sáng trần trong firmware (không chói mắt bé; TODO nit).
- Không support: đáy phẳng chạm bàn vát 0,8 mm; mọi mặt nghiêng ≥ 45°; mặt ráp chia đôi theo mặt phẳng đứng (trước/sau); mỗi nửa in nằm **mặt ráp xuống bàn** (cầu ≤ 15 mm; tai/mái ≥ 45°, kỹ sư kiểm lại bằng slice).
- Thành vỏ 2,4 mm (6 đường); gờ ráp + khe theo `fit-library` (không tự đặt khe ở đây).
- Pin: bản 1 cấp USB 5 V, không pin. Nếu thêm pin Li-ion: ngăn riêng bắt vít, **chỉ cell có mạch bảo vệ** – chưa thiết kế.
- Chân: không chân; đáy phẳng + 4 miếng chống trượt cao su Ø16 (đồng thời che vít).

## 3. Trạng thái (nghe · nói · khen · ngủ)

| Trạng thái | Màu LED | Mẫu |
|---|---|---|
| Nghe | xanh dương `#4FC3F7` | sáng đều, thở chậm 1 Hz |
| Nói | vàng `#FFC83D` | nhấp nhẹ theo biên độ giọng |
| Khen | hồng `#FF7FB0` | nhấp 2 lần rồi sáng đều 2 s |
| Ngủ | tím nhạt `#A99BE0` | mờ 10 %, thở rất chậm; chạm nút để dậy |

Màu cố định trong cả 3 concept để phụ huynh học 1 lần; xanh/vàng/hồng/tím khác biệt rõ cả với bé mù màu đỏ-xanh lá (không dùng đỏ/lục).
Concept B thêm mặt biểu cảm (mắt tròn · mắt + miệng o · mắt cười ^ ^ + má hồng · mắt nhắm + "z") trên màn hình.

## 4. Ba concept

Cả ba: nút "nói" lớn ở đỉnh đầu, loa ở phần dưới thân, đèn trạng thái ở "mặt". Chi tiết CMF = màu hiển thị trong render; **cuộn thật TODO** (Bambu PETG Basic: Tuan tự chuẩn bị, kỹ sư khớp tên màu hãng gần nhất; pastel có thể phải trộn với
bản sáng/HF, ghi lại khi chọn). Bề mặt: mặt dưới Textured PEI; mặt thấy được in thường (lớp 0,12–0,16 mm; làm mịn bằng ironing đỉnh nếu cần).

### A – Cú Bông (con vật tròn) – KHUYẾN NGHỊ bản 1

- Ngôn ngữ: khối trứng dẹt, mềm, cân đối như đồ chơi nhồi bông. Từ khóa: **ấm · tròn · hiền**.
- Kích thước ≈ **142 W × 116 D × 175 H mm** (thân 132 × 112 × 160, tai nhô lên 15, nút cao 9, cánh hai bên nhô 5).
- Thân (mơ `#F6BE9A`): superellipsoid, đáy phẳng, đáy bo vát 0,8; mặt trên tròn; 2 tai trên đầu (liền thân, R đỉnh 17 mm); 2 cánh áp sườn (liền thân, 22 × 52 × 72).
- Bụng (kem `#FFF3DF`): tấm bụng bầu ≈ 94 × 88 mm nhô 4 mm, **part riêng** bắt từ trong vào thân (đường chia màu = viền bụng, không phải đường ráp ngoài). Chứa lưới loa Ø56.
- Mắt: 2 vòng kem Ø54 + cửa sổ khuếch tán Ø34 (LED RGB sau). Vòng kem + cửa sổ khuếch tán là part riêng lồng từ trong (khe theo fit-library, TODO).
- Mỏ (bơ `#FFC857`): khối tròn Ø18 × 26, **liền thân** (in cùng part màu bơ gắn lún vào thân, hoặc đổi màu giữa lớp; kiểm AMS), không tháo được.
- Nút trên đầu (bơ `#FFC857`) Ø50 × 12, rãnh viền sâu 1 mm.
- Khắc dấu lắp: mũi tên ▲ khắc sâu 0,6 mm (nét 1 mm) ở mép bụng/thân để học sinh dựng đúng chiều; logo **STLAB** khắc nổi 0,6 ở mặt dưới gần miếng cao su (không ở mặt trước, bé không nhìn).
- 3 màu: mơ + kem + bơ (**không** màn hình). Đánh đổi: giá thấp nhất, bền; biểu cảm chỉ bằng màu (bé 2–3 tuổi vẫn hiểu); khó thêm mặt cười sau này.

### B – Trứng Bi (robot tròn kiểu "trứng", có màn hình)

- Ngôn ngữ: quả trứng bóng mịn trên đế kem, mặt kính tối như bé robot. Từ khóa: **sạch · thông minh · vui**.
- Kích thước ≈ **146 W × 120 D × 177 H mm** (vỏ trứng 124 × 114 × 156 trên đế kem 128 × 118 × 28, tay 2 bên nhô ra 10).
- Vỏ bạc hà `#BFE6D5` + đế/tay kem `#FFF3E2` + mặt kính xanh đêm `#27364A` + nút san hô `#FF8F85`: 4 màu → vượt tinh thần "hạn chế AMS", chấp nhận nếu đế + tay in 1 màu kem trên 2 lần đổi.
- Mặt: visor oval 80 × 62 nhô 7 mm (PETG xanh đêm bóng), cửa sổ màn hình 49 × 37 mm (module **2,4" 240 × 320** – TODO xác nhận kích thước hiển thị và giá).
- Tay 2 bên: khối kem liền thân (20 × 34 × 50), không nhỏ, không tháo.
- Chia đôi: đường ngang đáy trứng và đường trên đế (khe ráp); nút đỉnh + 3 lỗ micro dưới nút.
- Khắc dấu lắp: mũi tên ▲ trên visor mép dưới; STLAB nổi ở đáy.
- Đánh đổi: **đẹp nhất, biểu cảm phong phú**, nhưng +chi phí màn hình (≈ TODO), +firmware vẽ mặt, **thêm thời gian bé nhìn màn hình** (ngược mục tiêu "nghe nói"), cửa sổ cần miếng kính/PC trong hoặc in 2 lớp trong; chi tiết nhiều nhất.

### C – Bạn Tai Nghe (nhân vật đeo tai nghe)

- Ngôn ngữ: quả bóng ú tròn đội tai nghe to, miệng là loa. Từ khóa: **vui · nghe-nói · dễ thương**.
- Kích thước ≈ **152 W × 110 D × 147 H mm** (thân 116 × 108 × 132, tai nghe nhô mỗi bên 18, quai trên đỉnh).
- Thân tím lilac `#D7C6F3`, tai nghe + quai vàng bơ `#FFDF86` (quai đỉnh Ø14 mm, **liền thân và hai tai nghe** – in 1 part từ đáy lên, quai cong ≥ 45° ở đoạn đỉnh; phần nằm ngang tại đỉnh quai: chia part tại đây nếu cần).
- Mắt: 2 cửa sổ khuếch tán Ø22 trên 2 vòng kem Ø34; miệng = tấm kem tròn Ø72 chứa lưới loa Ø56; **vòng sáng tai nghe** Ø42 ở mặt ngoài mỗi tai nghe (đèn thứ 2); vòng sáng viền miệng.
- Nút hồng `#FF9DBB` Ø50 nằm giữa đỉnh đầu, trước quai.
- Mẹo trạng thái: **tai (phải) sáng = nghe; miệng sáng = nói; cả hai = khen; tắt hết = ngủ**.
- Đánh đổi: khối thấp, vững, hình dễ nhận ra nhất cho bé; nhưng loa bụng quay nhẹ lên trên ít hơn A; 3 vùng sáng → thêm 2 LED/dây (bản 1: có thể dùng 1 LED RGB + ống dẫn sáng, TODO).

## 5. So sánh và khuyến nghị

| | A Cú Bông | B Trứng Bi | C Bạn Tai Nghe |
|---|---|---|---|
| Biểu cảm | màu mắt | mặt trên màn hình (phong phú) | màu mắt + tai + miệng (rõ ràng) |
| Màn hình | không | có (2,4") | không |
| Chi phí linh kiện thêm | thấp nhất | +màn hình | +1–2 LED |
| Màu nhựa | 3 | 4 | 4 |
| An toàn < 3 tuổi | tốt nhất (ít chi tiết) | khá (kính cửa sổ phải chắc) | tốt (quai liền) |
| Thu nhỏ bản 2 | dễ | dễ | khó hơn (quai + tai nghe) |

**Khuyến nghị: A – Cú Bông cho bản 1**: ít chi tiết nhất, không màn hình (bé 2–5 tuổi không nhìn màn hình, tập nghe + nói), 3 màu, dễ in không support, co đều được cho bản 2.
Nếu sau cần "mặt biểu cảm", đổi sang B không đổi bố trí loa/bo (chỉ thêm màn hình sau visor).

## 6. Cần quyết (cho Tuan / phiên chính)

1. Chọn A/B/C (khuyến nghị A).
2. Kích thước bo Audio Kit + loa Ø52 sâu bao nhiêu: **Tuan đo thật** (hoặc cho ảnh bo), để dựng khoang trong.
3. Có pin Li-ion trong bản 1 không (hiện không – USB 5 V). Nếu có: thêm ngăn pin, cần quyết trước CAD.
4. Có chấp nhận cụm nhiều màu AMS (B = 4 màu) hay đổi sang A (3 màu).
5. Tên màu nhựa thật: TODO sau khi Tuan có cuộn.

## 7. Việc kỹ sư phải dựng (sau khi chọn)

1. Thân 2 nửa trước/sau theo kích thước mục 4 (thành 2,4 mm, bo ≥ 3 mm, đáy vát 0,8 mm) + gờ ráp theo `fit-library`.
2. Khoang loa Ø52 (gờ tựa mặt loa, 4 trụ giữ + keo/vít nhỏ – TODO), lưới Ø56, bố trí 3 lỗ micro, khe nhiệt lưng, lỗ USB.
3. 4 trụ vít M3 từ đáy (cùng loại), lỗ che Ø9 × 6 mm + miếng đệm.
4. Cửa sổ khuếch tán LED 0,8 mm; nút Ø50 + công tắc tactile 6 mm; kiểm không lọt ngón.
5. Khắc ▲ dấu lắp (sâu 0,6 mm, nét 1 mm) + logo STLAB mặt dưới.
6. Kiểm printability: không support, đáy phẳng, cầu ≤ 15 mm, thành ≥ 1,6 mm.

## 8. Đã sửa gì sau khi nhìn ảnh

- Lần 1: cả ảnh cháy sáng, mất hình → hạ công suất đèn xuống ~5 lần, nền kem ấm, exposure −0,8.
- Phông: thêm phông cong liền (cyclorama) để không thấy đường chân trời xám; ảnh lưng quay sản phẩm 180° thay vì quay máy ảnh.
- Bố cục hero: ly + sách ở sát sản phẩm (trước: để xa, sản phẩm nhỏ 20 % khung); sách phẳng phía trước.
- Mắt/vòng sáng cháy trắng nên mất màu trạng thái → hạ phát sáng 7 → 1,3 và tô nền theo màu trạng thái.
- Cánh cú dạng lưỡi dao mỏng (mất hợp bé) → làm tròn, dày hơn (R ≥ 11 mm).
- C: nút bị nghiêng theo mặt cong → đặt lại đứng, thấp hơn quai; mặt tai nghe + vòng sáng tách riêng.
- Hero lần 2: cắt khung theo sản phẩm + ly, sách tranh vào góc dưới để làm thước (sản phẩm to rõ hơn).
- Sau khi nhìn contact sheet: nhãn màu tràn lề → xuống dòng; ảnh lưng ban đầu lưới loa nằm sai mặt (lỗi quay vật) → quay mọi chi tiết đồng bộ.
- Còn thấy: vài chấm lưới loa lấn mép tấm miệng ở C (kỹ sư: giữ vùng lỗ ≥ 3 mm cách mép tấm).

## 9. Nguồn

- Chân Audio Kit/CLAUDE.md dự án; hình khối là thiết kế mới, **không** chép sản phẩm thương mại (không dùng tên/logo hãng).
- Chưa có nguồn cộng đồng cho kích thước bo (xem mục 1).
