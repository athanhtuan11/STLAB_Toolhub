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

## 10. A2 – Cú Bông có màn (2026-11-26, product-designer)

Tuan chốt 2026-11-26: thay 2 vành mắt LED (eye-ring Ø54 + eye-diffuser) bằng **1 màn TFT 2,8" SPI cảm ứng** làm "mắt động"; bé chạm mặt cú bằng ngón tay; **không tấm che trước kính**.
Ảnh duyệt: `contact-sheet-screen.png`, `concepts/a2-cu-bong-screen-{v1,v2}-{hero,side,state-listen|speak|praise|sleep}.png`, mockup UI phẳng `concepts/a2-cu-bong-screen-ui.png`. Dựng lại: `python make_screen_concepts.py` rồi `python make_sheet_screen.py`.
Ngôn ngữ: giữ khối trứng mềm của A, thêm "đĩa mặt" kem bo lớn ôm màn như đĩa mặt chim cú. Từ khóa: **ấm · tròn · biết chớp mắt**.

### 10.1 Số liệu (nguồn / TODO)
| Mục | Giá trị | Nguồn |
|---|---|---|
| PCB | 50,0 × 86,0 mm, đặt NGANG (86 rộng × 50 cao) | LCDWiki MSP2807 |
| Vùng hiển thị | 57,6 rộng × 43,2 cao mm (320 × 240 ngang) | LCDWiki MSP2807 |
| Số CHÍNH THỨC (cập nhật 2026-11-26, thay ô giữ chỗ 62 × 47 – xem 10.9) | PCB 50,00 × 86,00 × 1,60; kính TP 50,00 × 69,20, cách mép trên PCB 6,40; AA lệch trong kính: trên 2,90 / dưới (phía header, FPC) 8,70 / hai bên 3,40; dày 5,60 không header, 12,78 có header; 4 lỗ Ø3,20 cách tâm 44,00 × 76,08 | bản vẽ LCDWiki MSP2807, `tools/parts-library/components.yaml` id `tft-2-8-spi-ili9341-touch` |
| Vị trí cổ kết nối/khe SD | TODO (lấy từ ảnh/bản vẽ khi dựng CAD) | |
| Ảnh render 10.2/x-ray | vẫn dùng ô 62 × 47 + hộp PCB dày 8: chỉ khác nhỏ, an toàn hơn (dày hơn thật); chưa render lại | |

### 10.2 Hình khối đĩa mặt (cùng cho V1/V2; số trong ảnh, kỹ sư dựng theo khi có số đo)
- **Đĩa mặt** (kem `#FFF3DF`, part riêng, lồng từ trong như eye-ring cũ): 94 × 58 mm (PCB 86 × 50 + thành ≥ 3,5 mm mỗi bên), bo cạnh trước **R ≥ 9 mm** (ảnh dùng 12), nhô khỏi thân ~4 mm ở tâm; phía sau chạm thân phẳng – **thân vỏ trước phải có mặt phẳng nền (hơi nghiêng theo vách ~ 8–10°) dưới đĩa**, chuyển về mặt cong bằng vai R ≥ 8; trong ảnh đã làm đầu "vuông hơn" (n 2,2 → 3,4) để đĩa không nhô quá ~8 mm ở hai mép (xem ảnh cạnh bên). Mép đáy đĩa nằm trên mặt phẳng ráp/tựa in (không support – kỹ sư kiểm bằng slice).
- **Cửa sổ**: 58,4 × 44,0 mm (vùng hiển thị + 0,4 mm mỗi bên; TODO khớp mép kính thật), góc R 2,5. **Viền đè lên kính ≥ 1,2 mm** ngoài vùng hiển thị (kính phải rộng hơn hiển thị ≥ 1,2 mm mỗi bên – TODO kiểm kính thật), **mặt kính lùi 1,0 mm** so mặt viền, mép kính + mép PCB nằm kín sau viền (không lộ), không góc nhọn.
- Thành đĩa ≥ 1,6 mm; ngàm giữ màn + khe theo `fit-library` (không tự đặt khe); khay bắt PCB bằng trụ vít M2 – TODO vì chưa có lỗ bắt. Dây FPC/jumper không ép mép nhựa (rãnh luồn dây bo R ≥ 1).
- Cảm ứng: kính phải bị viền đè nhẹ nhưng không ép (ép làm lệch/vỡ cảm ứng) – TODO đo độ dày để chốt khe; ngón bé chạm vùng 58 × 43 là vùng chạm.
- Tránh vùng mic: tâm mic phải z ≥ 100; **cạnh trên đĩa cách tâm lỗ mic ≥ 4 mm (ảnh: ≥ 5 mm)** – mic dời LÊN so concept cũ (xem 10.4).
- Khắc dấu lắp: ▲ khắc sâu 0,6 mm (nét ≥ 0,8) ở mép dưới đĩa, cạnh mỏ/giữa; STLAB khắc nổi mặt dưới như cũ.

### 10.3 Hai phương án vị trí mỏ
| | **V1 – màn cao, mỏ DƯỚI màn** | **V2 – màn thấp, mỏ CHỒNG mép dưới viền** (KHUYẾN NGHỊ) |
|---|---|---|
| Tâm màn (z thân) | 112 (gần chỗ mắt cũ 108) | 104 (thấp 8 so V1) |
| Mỏ | dựng trên đỉnh bụng, khoảng trống giữa viền và bụng (tâm z ≈ 74), tách hẳn màn | treo lên mép dưới đĩa, tâm cách tâm màn 31 mm, đè viền ~2 mm, không che vùng hiển thị (mỏ cách cửa sổ ≥ 1 mm) |
| Bụng/loa | hạ thấp: lưới Ø56 tâm z ≈ 42 (cũ 54), tấm bụng thấp 8–12 mm | hạ ít: tâm z ≈ 48, hạ ~6 mm |
| Mic | tâm z ≈ 148 (dời lên ~ +16, vùng trán dốc ~ 45°) | tâm z ≈ 141 (+9) |
| Đánh đổi | đẹp "đúng mặt cú", mỏ hở dễ thấy; nhưng đụng vào loa/bụng, mic lên cao sát tai/nút → ảnh hưởng hú + đường dây; ống/khoang loa phải dời | mặt cú gọn, ít dời linh kiện; mỏ nhìn như "cằm" giữ nhận diện cú; mỏ chồng viền nên cần tách part bơ gắn lên viền (hai part chạm nhau, kiểm AMS) |
**Khuyến nghị V2**: dời ít nhất (bụng/loa/mic chỉ dời 6–9 mm), vẫn giữ mỏ làm mốc nhận diện cú, ít rủi ro với loa Ø52 và mic xa loa. V1 chỉ nếu Tuan muốn mỏ tách hẳn khỏi màn.

### 10.4 Mockup UI (màn 320 × 240 ngang, nền #0A0F18, mắt to 2 bên; chi tiết ở `a2-cu-bong-screen-ui.png`)
| Trạng thái | Màu | Hình mắt | Động |
|---|---|---|---|
| Nghe | xanh dương `#4FC3F7` | tròn to + con ngươi + điểm sáng, vòng cung phía trên | vòng cung "thở" 1 Hz |
| Nói | vàng `#FFC83D` | hơi cao, con ngươi to, điểm sáng | chớp/co theo biên độ giọng |
| Khen | hồng `#FF7FB0` | mắt cười ^ ^ + má hồng + 3 sao lấp lánh | 2 nhấp rồi giữ 2 s |
| Ngủ | tím `#A99BE0`, mờ ~ 35 % | mắt nhắm ∪ + "z z" | thở rất chậm; **chạm mặt = thức dậy** |
Chạm khi Nghe = chớp mắt vui; chạm khi Nói = tạm lặng (TODO firmware quyết). Độ sáng nền trần thấp (mắt bé; TODO nit), tự dim sau thời gian không chạm.

### 10.5 CMF (giữ 3 màu, hạn chế AMS)
Thân mơ + đĩa mặt/bụng kem + mỏ, nút bơ (cuộn Bambu PETG Basic: tên màu TODO). Kính màn đen = màn tắt, không thêm màu. Bề mặt: đáy Textured PEI; đĩa mặt in **mặt trước phẳng xuống bàn** (mặt tiếp kính hướng lên) – chưa có support; bo R9 mặt trước chạm bàn nên cần vát 0,8 thay bo tại tiếp xúc – kỹ sư kiểm.

### 10.6 Cần quyết
1. Chọn V1 hay V2 (khuyến nghị V2).
2. Tuan đo: độ dày tổng màn + khoảng cách lỗ bắt vít, vị trí cổ nối/khe SD, kích thước kính thật; chốt chiều đặt (ngang đã chốt) và hướng cổ nối (xuống dưới, phía bụng?).
3. Dời mic lên (+9 mm V2 / +16 mm V1) và hạ bụng/loa: phiên chính chấp nhận đổi CAD (đây là đề xuất, chưa đổi gì).
4. Mất đèn LED mắt → bỏ eye-ring/eye-diffuser và dây WS2812 mắt (nút đầu/LED khác nếu có thì giữ?).
5. Vỏ trước cần mặt phẳng nền (hoặc đĩa mặt chấp nhận nhô ≤ 8 mm ở hai mép).
6. An toàn: màn nóng ít; cạnh viền chỉ cạnh bo; vỏ bé < 3 tuổi chạm màn → không tấm che nên kính phải được viền đè chắc (không bong), kiểm lực kéo 10 N sau khi có số.

### 10.7 Việc kỹ sư dựng (sau khi chọn)
`face-plate` (kem) + cửa sổ 58,4 × 44,0 + ô giữ màn (TODO số); mặt phẳng nền trên vỏ trước; dời mic/loa/bụng theo phương án; bỏ eye-ring + eye-diffuser; rãnh dây màn; ▲ + khắc STLAB; slice kiểm không support.

### 10.8 Đã sửa gì sau khi nhìn ảnh
- Bản 1: đĩa mặt như tấm ốp 90° (bo 9) nhìn như tivi → bo 12, mắt lớn hơn (r 13,5, tâm ±15).
- Cạnh bên: đĩa nhô ~13 mm ở hai mép vì thân cong → làm thân vuông hơn ở phần đầu (n 3,4) → còn ~8 mm; ghi yêu cầu "mặt phẳng nền" cho CAD.
- Mỏ V2 ban đầu đè lên vùng hiển thị → dời tâm mỏ xuống −31 mm so tâm màn.

### 10.9 V2-2L – 2 loa ở 2 sườn (Tuan chốt 2026-11-26: V2 + 2 loa)
Ảnh duyệt: `contact-sheet-screen-2l.png`, `concepts/a2-cu-bong-screen-v2-2l-{h0,h25}-{hero,side,back,xray-front,xray-top}.png`. Dựng lại: `python make_screen_2l.py` rồi `python make_sheet_screen_2l.py`. Không sửa CAD.

**Hình khối.** Giữ V2 (màn tâm z=104, mỏ chồng viền, mic tâm z=141). Bụng hết loa: tấm kem trơn + 12 vạch lông vũ nhẹ (khắc nông, nét 1,2) + logo STLAB khắc sâu 0,6 ở z≈22 (chữ ≥ 0,8 nét; ảnh chỉ là khối giữ chỗ). Canh đổi: dời LÊN z≈112, ra sau (y≈+22), nhỏ lại (20 × 44 × 56) để nhường bezel loa – chỉ trang trí, phiên chính xác nhận.

**2 loa** (Ø52 × 26: mặt trước 5 mm Ø52, thân sau Ø38 dài 21), tâm z=50, 2 bezel/lưới Ø56 (lỗ Ø2,8 bước 5,6, speaker-bezel 86 × 86 × 15 giữ nguyên, cone nằm trong vỏ). Bezel 86 × 86 phủ z 7–93 → không chạm sàn; trên cùng z=93 vẫn dưới cánh (đáy cánh z≈84 ở khối concept, lệch về sau y > −2 nên không đè). Concept dùng vành kem Ø68 nhô 1,5 (H0) / 3,5 (H25) chỉ để vẽ; CAD cắt phẳng vuông góc trục loa, nhô ≤ 2 mm, vát 0,8.

| | **H0 – ngang 0°** (KHUYẾN NGHỊ) | **H25 – chếch trước 25°** |
|---|---|---|
| Trục loa | ±X | (±cos25°, −sin25°) |
| Mặt loa | nhìn thẳng ngang, chỉ thấy rõ từ cạnh/chéo | lộ ra ở ảnh 3/4 trước, mắt bé thấy lưới → "có loa" rõ hơn, âm hướng về bé |
| Tâm mic (z=141) → tâm khối loa / → tâm lưới | 113,5 / 122,1 mm (≥ 60 ✓) | 104,0 / 109,9 mm (≥ 60 ✓) |
| Nội thất | thoáng, thân sau 2 loa cách nhau ~73 mm | khối loa chạy chéo, thân sau (x 33–49, y −37…−1) tiến gần sau màn (≥ 25 mm) |
| Khó dựng | bezel gần phẳng, vỏ đơn giản | bezel nghiêng 25° trên mặt cong → phải cắt phẳng nghiêng + gờ khóa nghiêng; ống ôm loa dựng khó hơn |
Khuyến nghị H0: gọn, ít rủi ro CAD, đã đủ xa mic; H25 chỉ nếu Tuan thích nhìn lưới từ phía trước.

**Bố trí bên trong (ảnh x-ray, hệ trục thân: x phải, y sau, z lên).** Vỏ trước+sau dày 2,4 → lòng rộng 129,6 (thân 134,4 giữ nguyên, **KHÔNG cần nới**), sâu ~112.
- Loa: mặt tại |x|≈62,4 (H0), thân sau tới |x|≈36,4; hai loa không chạm nhau (khe giữa hai thân sau ≈ 73 mm).
- Bo S3: pcb_box 29 × 16 × 72 dựng đứng, tâm (0, +34, 64): z 28–100, chân USB ở lưng-dưới (khe cáp 40 × 12 ở chân lưng như cũ).
- 2 ampli MAX98357A ~22 × 22 × 10 (dựng, mỏng theo x), mỗi cái cạnh loa của nó, tâm (±27, +16, 50) → cách thân sau loa 4,4 mm (render vẽ ở ±30 = chỉ cách 1,4 mm; **dùng ±27**), cách bo S3 7,5 mm theo x. H25: ampli cách khối loa ≥ 6 mm theo y.
- Màn: PCB 86 × 50 × 1,6 ngay sau kính; cùng lúc dưới màn z=79 và đỉnh loa z=76 → **chỉ 3 mm theo z** (khác y: màn ở y≈−50, loa y 0…±26 ở H0): không chạm nhau nhưng sát; nếu cần dư, hạ tâm loa xuống z=46 (đáy bezel z=3, vát vào đáy) – đề xuất, chưa đổi.
- Màn → bo S3: ≥ 70 mm theo y còn trống để luồn dây; không ép dây vào mép nhựa.
- Thoát nhiệt: 5 khe 2 × 18 lưng như cũ (không đổi).

**Màn: số chính thức và cách đặt ngang (thay ô 62 × 47)**
- Đặt PCB 86 ngang, **header/FPC (dây) về bên phải mặt cú (phía x+)** – dây chạy ra sau về bo S3 ở giữa, tránh mỏ. Tâm PCB = tâm đĩa mặt (đĩa 94 × 58 đối xứng, tâm lỗ vít không đổi).
- Từ tâm PCB: tâm vùng hiển thị (AA) lệch **−4,9 mm theo x** (về phía trái, xa header) vì AA cách mép kính trên 2,90 và dưới 8,70 và kính cách đầu PCB 6,40/10,40. Vùng hiển thị 57,6 × 43,2 → x −33,7…+23,9, z ±21,6.
- **Chọn: cửa sổ 58,4 × 44,0 lệch tâm −4,9 mm** (khoảng rim đĩa: trái 12,9, phải 22,7, trên/dưới 7,0), và **firmware dịch hình mắt +4,9 mm = +27 px (0,18 mm/px) sang phải** để mắt nhìn cân giữa mặt cú. Phương án khác (đĩa lệch + cửa sổ giữa) làm mỏ/viền lệch → bỏ.
- Kính TP 50,00 × 69,20 → khay giữ kính: kính từ x −36,6 đến +32,6 (tâm −2,0 so tâm PCB), z ±25. Viền đè lên kính: dọc trên/dưới 3,0 mm/bên (≥1,2 ✓), đầu trái 2,5 mm, đầu phải 8,3 mm.
- Dày: 5,60 (không header) → khoang trước ≥ 6,0 + khe fit-library, mặt kính lùi 1,0 so mặt viền như 10.2. Header: 12,78 − 5,60 = 7,2 mm nhô sau → hốc sau PCB sâu ≥ 8 mm ở góc phải.
- 4 lỗ Ø3,20 cách tâm PCB 44,00 (z) × 76,08 (x) → tâm lỗ x = ±38,04, z = ±22,0 so tâm PCB: trụ vít M3 (hoặc M3 ép insert tuỳ fit-library, TODO) ở thành sau đĩa mặt. Chú ý lỗ phải x=+38,04 cách mép đĩa (±47) chỉ 8,96 → trụ Ø7 còn 5,5 mm; kiểm khi dựng.

**Cần quyết thêm:** (1) H0 hay H25; (2) hạ loa z=46 hay giữ 50 (màn–loa 3 mm theo z); (3) chấp nhận dời cánh lên/ra sau; (4) header về bên phải mặt cú (đã chọn, đổi thì đối xứng); (5) cổ kết nối/khe SD màn: TODO khi dựng.

**Đã sửa gì sau khi nhìn ảnh:** bản 1 thiếu chỗ cho bezel (cánh chồng lưới) → dời cánh lên/ra sau; ampli ở x=±30 chỉ cách loa 1,4 mm → đề xuất ±27; H25: lưới lộ ra ở mặt trước gần mỏ/bụng rõ nên giữ vành kem nhô 3,5 để không bị thân che.
