# Nơi chứa kích thước chính thức của linh kiện STLab

Viết 2026-10-24. Mục đích: với mỗi linh kiện/vật tư STLab dùng, chỉ ra **nguồn gốc chứa kích thước lắp ghép**
(bản vẽ, STEP, bảng tiêu chuẩn) để thiết kế hốc/lỗ/gá theo số có nguồn, không tự đo/đoán.
Liên quan: [components.yaml](../maker/robotics-cad/library/components.yaml) ·
[cad-community-gaps-research.md](cad-community-gaps-research.md) (mục 3: lỗ vít/insert) · [COMMUNITY.md](COMMUNITY.md).

Nhãn: **[hãng]** tài liệu nhà sản xuất · **[chuẩn]** tiêu chuẩn ISO/DIN (qua bảng mở) · **[máy]** file đã cài/đã ghim,
chỉ đọc · **(thứ cấp)** đại lý/blog/trường · `TODO` chưa xác nhận. Đơn vị mm, g, V, A, °C.
"Ghim" = đã nằm trong `community/` hoặc `*.tsv`.

## 0. Kết luận nhanh

1. **43 mục trong components.yaml:** 34 có nguồn tốt (bản vẽ hoặc STEP của hãng), 4 trung bình (SG90, NEMA17,
   ESP32-CAM, Pico), 5 yếu, không có hãng đứng sau (Mabuchi encoder, ESP32 DOIT, HC-SR04, module L298N, Blue Pill).
2. **CyberBrick là nhóm mạnh nhất:** cả 18 mục có STEP chính hãng đã ghim. PG001 và LA002 có bản vẽ kích thước có dung sai
   trong PDF đã ghim. Một số con số còn nằm trong PDF mà yaml chưa chép: spline 40T/Φ4,85, mốc cao 16,30/23,20/27,30, trục N20 có dung sai.
3. **Ruthex đã giải được:** bảng của TU Dresden (dòng ruthex) định nghĩa D = **lỗ khoan**, L = **sâu lỗ tối thiểu**,
   T = **thành tối thiểu**. **M2.5 dùng chung thân với M3**: lỗ Ø4,0, sâu ≥ 6,7, thành ≥ 1,6.
   Nhiệt ép thì Ruthex không công bố, chỉ có quy tắc của CNC Kitchen là nhiệt in + 10–20 °C (`TODO` thử).
4. **Vít/đai ốc/vòng đệm:** bảng ISO 4762/4032/7089 đã có sẵn trong Fasteners WB đang cài. Riêng ISO 7380 (đầu tròn, loại
   AA050 của CyberBrick) **không có cỡ M2.5** → dùng STEP AA050 chính hãng.
5. **Mâu thuẫn mới phát hiện:**
   - PG002 nặng **12,4 g**, không phải 9 g, và bảng ghi **không có** bảo vệ kẹt.
   - Pin PC003: tên CAD ghi 800 mAh, bảng phụ kiện ghi 700 mAh.
   - TODO "trục N20 9,3 so với 10" thật ra là so lệch mốc (xem mục 3).
6. **Nên ghim thêm** 4 file nhỏ (Pi 4 drawing, UNO R4 WiFi datasheet, 17HS4401S, ảnh A–F của TowerPro) và một ảnh chụp
   bảng Ruthex/TU Dresden. Mỗi file có SHA-256 ở mục 4.

## 1. Bảng nguồn theo linh kiện

### 1.1 CyberBrick (Bambu Lab) – STEP chính hãng đã ghim (`cyberbrick-sources.tsv`, CDN `store.bblcdn.com`)
License: không ghi, hãng phát hành công khai (COMMUNITY.md).

| Linh kiện (id) | Nơi chứa | Loại | Ghim? | Kích thước lắp ghép chính | Ghi chú |
|---|---|---|---|---|---|
| `cb-pg001-servo-9g` (PG001) | `community/cyberbrick-official/pdf/9g Servo Motor 180° - PG001.pdf` (B-PG001 REV 01) [hãng] | PDF bản vẽ + STEP | Có | Thân rộng 12,00. Mặt bích dài 32,50. **Lỗ Φ2,20 cách tâm 27,80**. Thân giữa 2 tai 23,0. Mốc cao tính từ đáy: **16,30** tới mặt dưới tai, **23,20** tới đỉnh vỏ, **27,30** tới đỉnh trục. 8,56 là vị trí trục ra (mốc `TODO`). **Spline 40T/Φ4,85**. Vít horn Φ2,3 × 4,5 PWA. Dây 245 ± 5 | Bản vẽ không ghi dung sai chung |
| `cb-pg001-servo-9g` (PG002 360°) | `.../pdf/9g Servo Motor 360° - PG002.pdf` (B-PG002) [hãng] | PDF (hình kích thước mờ) | Có | Hình vẽ quá nhỏ, không đọc được số → lấy theo STEP chung. Nặng **12,4 ± 0,5 g**. Spline 40T. Vít horn Φ2,3 × 4,5 | Bảng ghi **không có** bảo vệ kẹt, nhiệt, áp, dòng ("无"). Tốc độ 80 ± 15 vòng/phút @ 6 V |
| `cb-n20-motor` (LA002/3/4) | `.../pdf/B-LA002.pdf` (2024-03-08) [hãng], B_LA003, B-LA004 | PDF bản vẽ | Có | Thân 12,0 ± 0,2 × 10,0 ± 0,2. Hộp số 9,0 ± 0,3. Động cơ 15,1 ± 0,2. Bo sau 1,2 ± 0,1, đầu cắm 2,4. **Trục Φ3,0 (+0/−0,05), dài 10,0 ± 0,3 tính từ mặt hộp số** (gồm gờ Φ4,0 ± 0,1 cao 0,8). Mặt vát D dài 6,0 ± 0,2. Số 2,5 ± 0,05 nhiều khả năng là bề dày qua mặt vát (`TODO` xác nhận). **2 × M1.6 × 0,35, cách 9,0 ± 0,1**. Dung sai chung ±0,2 | Hãng không phát hành STEP (dùng Pololu) |
| `cb-la024-motor-030` | `.../pdf/030_Micro_DC_Motor_-LA024.pdf` + STEP | PDF + STEP | Có | Trục 1,5 (yaml). Hộp số: STEP `*-reducer.step` | Tỉ số: `TODO` (Assembly_Guide) |
| `cb-xa003-controller-core` | `.../pdf/Accessories Specification.pdf` mục 1.1 + STEP | PDF + STEP | Có | Bo **22 × 27**, 6 g. Chân dạng stamp-hole | Pinout trên wiki |
| `cb-xa004-receiver` | `.../pdf/Remote_Control_Receiver_Shield_-_XA004.pdf` + STEP | PDF + STEP | Có | Bo **29 × 30**, 4 lỗ ở góc. **Ø lỗ và khoảng cách lỗ không ghi** → đo trên STEP | Mỗi cổng motor tối đa 1 A. Servo 5 V: mỗi bên ≤ 2 A, tổng ≤ 3 A |
| `cb-xa005-transmitter` | Accessories Spec 1.3 + STEP | PDF + STEP | Có | Bo 34 × 31, 5,5 g | – |
| `cb-xa006-led-hub` | Accessories Spec 1.4 | PDF + STEP | Có | 6 × 28 | – |
| `cb-xa007-power-switch` | Accessories Spec 1.5 + PDF XA007 | PDF + STEP | Có | 32 × 20,5, một tai bắt. **Dòng cho phép 3 A**, tối đa 12,6 V, 4,1 g | Giải TODO dòng |
| `cb-xa008-button` | Accessories Spec 1.6 | PDF + STEP | Có | 29 × 13, 2 tai | – |
| `cb-xa009-joystick-1axis` | Accessories Spec 1.7 | PDF + STEP | Có | 34 × 27, 6,15 g | – |
| `cb-xa010-rocker-3pos` | Accessories Spec 1.8 | PDF + STEP | Có | rộng 27, 2,73 g | – |
| `cb-xa011-joystick-2axis` | Accessories Spec 1.9 | PDF + STEP | Có | 34 × 27, 6,6 g | – |
| `cb-kb003-led` | Accessories Spec 1.10 | PDF + STEP | Có | IDC 0,8 4P, 3,5–5,3 V | – |
| `cb-pc003-battery-14500` | Accessories Spec 1.11 + STEP | PDF + STEP | Có | Thân pin: đo trên STEP (hộp bao gồm dây). Theo tiêu chuẩn, cell 14500 có Ø14 × 50 nhưng hãng không ghi → `TODO` | **2S 700 mAh** (Accessories Spec) ≠ 800 mAh (tên CAD) |
| `cb-xa012-aaa-case`, `cb-la026-differential`, `cb-la027-tire` | STEP + `Differential Assembly.pdf` | STEP | Có | Lốp Φ33,7 × 13,85 (tên hãng) | – |
| `cb-phu-kien` (CA001, AA050, BB007/BB016) | STEP + `Accessories Specification.pdf` | STEP | Có | Nam châm **Φ4 × 2**. Vít **M2.5 × 6 BHCS** (AA050). Lò xo 0,5 × 5 × 20 và 0,6 × 8 × 20 (tên hãng) | AA050 là cỡ duy nhất có STEP M2.5 đầu tròn |

### 1.2 Servo rời
| Linh kiện (id) | Nơi chứa | Loại | Ghim? | Kích thước lắp ghép chính | Ghi chú |
|---|---|---|---|---|---|
| `sg90` | [TowerPro SG90](https://towerpro.com.tw/product/sg90-7/) + [hình A–F](http://torqpro.com/wp-content/uploads/2014/07/小馬達尺寸標示圖B.jpg) [hãng] | Trang web + ảnh | Chưa | **A 30,3** (đáy → đỉnh trục) · **B 22,7** (thân) · **C 27** (đáy → đỉnh vỏ) · **D 12,2** (rộng) · **E 32,3** (dài cả tai) · **F 17** (đáy → mặt dưới tai). Bảng thông số ghi 23 × 12,2 × 29 | **Khoảng cách lỗ, Ø lỗ, spline: hãng không ghi** → `TODO`. Trang ghi nặng 9 g, mục "Additional information" ghi 0,019 kg |
| MG90S (cyberbrick-car, chưa có id) | [TowerPro MG90S](https://towerpro.com.tw/product/mg90s-3/) [hãng]; STEP GrabCAD `community/grabcad/towerpro-mg90s/` (thứ cấp, Tuan đã tải 2026-10-23) | Trang + STEP (thứ cấp) | STEP có, không SHA | **A 32,5 · B 22,8 · C 28,4 · D 12,4 · E 32,1 · F 18,5**. Bảng ghi 22,8 × 12,2 × 28,5. 13,4 g | STEP GrabCAD đo được 32,2 × 12,15 × 28,3 (COMMUNITY.md) |

So sánh mốc F (đáy → mặt dưới tai): PG001 16,30 · SG90 17 · MG90S 18,5. **Hốc gá của 3 loại không dùng chung được** nếu
tai tựa lên mặt gá. Phải chọn theo đúng mã đang lắp.

### 1.3 Động cơ
| Linh kiện (id) | Nơi chứa | Loại | Ghim? | Kích thước lắp ghép chính | Ghi chú |
|---|---|---|---|---|---|
| `n20-gearmotor` | [Pololu dimensions PDF](https://www.pololu.com/file/0J949/micro-metal-gearmotors-dimensions.pdf) (03-04-2024) + STEP [hãng] | PDF + STEP | Có (`n20-sources.tsv`) | Mặt cắt 12,0 × 10,0. Hộp số L = 9 (bản 1000:1 là 12,5). Động cơ 15 (bản HPCB 15,4). **Trục Φ3,0, dài 10 tính từ mặt hộp số** (gồm gờ Φ4,0 × 0,7). **Mặt vát D: 2,5**. **2 × M1.6, mỗi lỗ cách tâm trục 4,5** (cách nhau 9,0). OL tối đa 25,6 (không encoder) / 32,5 (có encoder). Bo encoder 12,5 × 13,6 | License không ghi |
| `nema17-17hs4401` | [Handsontec 17HS4401S](https://www.handsontec.com/dataspecs/17HS4401S.pdf) (thứ cấp: đại lý, không phải hãng sản xuất) | PDF bản vẽ | Chưa | **Lỗ 31,0 ± 0,1, 4-M3 sâu ≥ 4,5**. **Gờ định tâm Φ22,0 (−0,05) cao 2,0**. Trục Φ5,0 (−0,012) dài 23 ± 0,5, **vát D 4,5 ± 0,1**. Thân 42,0 max, dài 40 max. **2,8 mH**, 280 g | Giải 2 TODO. Kích thước mặt bích là chuẩn NEMA 17, nhưng chưa thấy văn bản chuẩn NEMA ICS 16 bản mở → `TODO` |
| `dc-motor-encoder-mabuchi` | Không xác định được mã → **không có nguồn** | – | – | `TODO` | Yếu |

### 1.4 Board vi điều khiển / máy tính nhúng
| Linh kiện (id) | Nơi chứa | Loại | Ghim? | Kích thước lắp ghép chính | Ghi chú |
|---|---|---|---|---|---|
| `raspberry-pi-4b` | [RPi 4 mechanical drawing](https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf) (chuyển hướng sang pip-assets.raspberrypi.com, bản RP-008343-DS-1) [hãng] | PDF bản vẽ | **Chưa** | 85 × 56, góc R3,0. **4 lỗ Ø2,7, tâm 58 × 49, cách mép 3,5**, đệm Ø6. Chiều cao (Z): USB-A 16,0 · Ethernet 13,5 · header 8,5 · USB-C 3,2 · micro-HDMI 3,0. Theo trục x tính từ mép: USB-C 11,2, HDMI 26,0 / 39,5 | Giải TODO "đối chiếu bản vẽ chính thức"; thay 2 nguồn thứ cấp đang ghi |
| `raspberry-pi-5`, `raspberry-pi-zero-2-w` | Bản vẽ chính hãng trong `community/boards-official/drawings/` [hãng] | PDF | Có | (đã chép trong yaml) | Chiều cao cổng của Pi 5 đang mượn của Pi 4. Bản vẽ Pi 4 ở trên **có ghi Z**, là nguồn tốt hơn model FreeCAD-library |
| `raspberry-pi-pico` | [Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) mục "Mechanical specification" [hãng] | PDF (> 10 MB) | Chưa | 51 × 21, PCB dày 1. **4 lỗ Ø2,1 (±0,05)**. Hai số này đọc qua trích đoạn của đại lý, chưa mở được PDF. Tọa độ lỗ: `TODO` | Trung bình |
| `arduino-uno-r4-wifi` | [ABX00087 datasheet](https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf) mục 13 (rev 9, 20/10/2026) [hãng] | PDF bản vẽ + STEP | STEP có, PDF chưa | **68,58 × 53,34, PCB 1**. **4 lỗ R1,6 (Ø3,2)**. Header 8,5 trên mặt PCB. Số ghi trên hình: 13,97 / 15,24 / 2,54 / 7,62 / 17,78 (gán từng số cho lỗ nào: `TODO` đọc kỹ). **Logic 5 V** (RA4M1), ESP32-S3 3,3 V. VIN 6–24 V, mỗi GPIO ≤ 8 mA | Giải TODO "mức logic" + "lỗ bắt" |
| `arduino-uno-q`, `arduino-nano-esp32`, `arduino-nano-r4`, `arduino-giga-r1-wifi`, `arduino-modulino` | STEP chính hãng (arduino/docs-content) + datasheet trên docs.arduino.cc [hãng] | STEP + PDF | STEP có | Lấy mặt bằng từ STEP. Mức logic: đọc datasheet từng board (`TODO`) | CC-BY-SA-4.0 |
| `esp32-devkitc-v4`, `esp32-s3-devkitc-1` | Bản vẽ/DXF Espressif đã ghim [hãng] | PDF/DXF | Có | (đã chép trong yaml) | Board không có lỗ bắt |
| `esp32-module` | espressif/kicad-libraries 3.2.1 [hãng] | STEP | Có | Module S3-WROOM-1: 18 × 25,5 × 3,1 | CC-BY-SA-4.0 |
| `lolin-d1-mini-v4` | wemos.cc dim PDF [hãng] | PDF | Có | (đã chép trong yaml) | – |
| `stm32-nucleo-64` | ST UM1724 Rev 14 [hãng] | PDF | Có | (đã chép trong yaml); Ø lỗ: `TODO` | – |
| `esp32-cam` | Datasheet AI-Thinker (qua Elecrow) | PDF | Có | (đã chép trong yaml) | Trung bình: bản vẽ của hãng gốc nằm trên docs.ai-thinker.com |
| `esp32-doit-devkit-v1`, `stm32-blue-pill` | Không có hãng đứng sau (hàng generic) | – | – | Đo hàng thật | Yếu |

### 1.5 Cảm biến, driver
| Linh kiện (id) | Nơi chứa | Loại | Ghim? | Kích thước chính | Ghi chú |
|---|---|---|---|---|---|
| `hc-sr04` | Datasheet trên SparkFun CDN (thứ cấp, hãng gốc không rõ) | PDF | Chưa | 45 × 20 × 15 | Yếu. Vị trí lỗ bắt: đo thật |
| `l298n-module` | ST chỉ có datasheet chip L298; module là hàng generic | – | – | Đo thật | Yếu |

### 1.6 Vít, đai ốc, vòng đệm, insert
Nguồn [chuẩn] đọc từ `%APPDATA%/FreeCAD/v1-1/Mod/fasteners/FsData/*.csv` (Fasteners WB 0.5.67) [máy]. Repo:
https://github.com/shaise/FreeCAD_FastenersWB (license: `TODO` kiểm file LICENSE).

| Vật tư | Nguồn (file) | M2 | M2.5 | M3 |
|---|---|---|---|---|
| ISO 4762 vít lục giác chìm đầu trụ: dk / k / s (lục giác) | `iso4762def.csv` (cột `P,b,dk_max,da,ds_mean,e,lf,k,r,s_mean,t,v,dw,w`) | 3,8 / 2,0 / 1,5 | 4,5 / 2,5 / 2,0 | 5,5 / 3,0 / 2,5 |
| ISO 7380-1 đầu tròn: dk / k / s | `iso7380def.csv` | **không có** | **không có** → STEP AA050 | 5,7 / 1,65 / 2,0 |
| ISO 4032 đai ốc lục giác: s / m / e | `iso4032def.csv` (`P,c,damax,dw,e,m,mw,s_nom`) | 4,0 / 1,6 / 4,4 | 5,0 / 2,0 / 5,5 | 5,5 / 2,4 / 6,1 |
| ISO 7089 vòng đệm: d1 / d2 / h | `iso7089def.csv` | 2,2 / 5,0 / 0,3 | 2,7 / 6,0 / 0,5 | 3,2 / 7,0 / 0,5 |
| Lỗ khoan để taro ren kim loại | `ScrewMaker.py` `FSCScrewHoleChart`; [Optimas](https://optimas.com/technical-resources/tapping-sizes/) (thứ cấp) | 1,6 | 2,05 | 2,5 |
| Lỗ xuyên ISO 273 kín / vừa / rộng | [Optimas](https://optimas.com/technical-resources/tapping-sizes/) (thứ cấp, ghi "close/medium/free"); văn bản [ISO 273:1979](https://www.iso.org/standard/4183.html) phải mua | 2,2 / 2,4 / 2,6 | 2,7 / 2,9 / 3,1 | 3,2 / 3,4 / 3,6 |

**Heat-set insert Ruthex** (giải mục 3 của cad-community-gaps-research):

| Ren | Ruthex ⌀D1 / ⌀D2 / ⌀D3 / L / W(min) ([3DJake](https://www.3djake.com/ruthex/threaded-insert-m25-70-pieces), thứ cấp) | TU Dresden, dòng ruthex: **lỗ øD / sâu lỗ min L / thành min T / mặt phẳng min øE / kích thước chi tiết min W** ([TU Dresden](https://tu-dresden.de/ing/elektrotechnik/die-fakultaet/fakultaetswerkstatt/werkstattteil-praezisionsmechanik/waermeeinbettung-bei-fdm-3d-drucken), thứ cấp, cấp trường) |
|---|---|---|
| M2 (M2×4) | 3,6 / 3,1 / 3,2 / 4,0 / 1,3 | 3,2 / 5,0 / 1,3 / 5,5 / 5,8 |
| **M2.5 (M2.5×5,7)** | **4,6 / 3,9 / 4,0 / 5,7 / 1,6** | **4,0 / 6,7 / 1,6 / 6,5 / 7,2** |
| M3 (M3×5,7) | 4,6 / 3,9 / 4,0 / 5,7 / 1,6 | 4,0 / 6,7 / 1,6 / 6,5 / 7,2 (bản ngắn: L 5,0) |
| M4 | 6,3 / 5,5 / 5,6 / 8,1 / 2,1 | 5,6 / 9,1 / 2,1 / 9,0 / 9,8 |

- **Nghĩa cột:**
  - D3 của Ruthex = øD của TU Dresden = **đường kính lỗ**.
  - W(min) của Ruthex = T = **thành tối thiểu**.
  - Sâu lỗ tối thiểu = chiều dài insert + 1,0 (5,7 → 6,7; 4,0 → 5,0).
  - D1 > lỗ, D2 < lỗ nên nhiều khả năng D1 = vành khía ngoài, D2 = đầu dẫn hướng. **Đây là suy luận**: nghĩa D1/D2 vẫn `TODO`
    (TU Dresden không định nghĩa 2 cột này).
- **Đối chiếu với Fasteners WB** (`HeatInserts.csv`, dòng IUT, không phải Ruthex):
  - M2.5 và M3 cùng thân: `D` = 4,00, `Length` = 5,74, `ExtDia` = 4,55.
  - M2: `D` = 3,23, `Length` = 4,00.
  - Khớp với Ruthex ở mức ±0,05.
- **Nhiệt ép:**
  - Ruthex: không thấy số công bố (ruthex.de trả 429, ruthex.com là công ty khác) → `TODO`.
  - [CNC Kitchen](https://cnckitchen.com/blog/tips-and-tricks-for-heat-set-inserts) (hãng insert): nhiệt in + 10–20 °C,
    ví dụ PETG khoảng 245 °C.
  - [Prusa](https://www.prusa3d.com/product/threaded-inserts-m2-5-standard-100-pcs/): nhiệt in + 10 °C.
  - Với PETG Basic in ở 245 °C → thử **255–265 °C**.
  - **An toàn:** mỏ hàn > 250 °C. Học sinh làm phải có giá đỡ mỏ hàn và kìm. Không ép insert vào chi tiết đang lắp pin Li-ion.

### 1.7 Bạc đạn, nam châm, khác
| Vật tư | Nơi chứa | Loại | Ghim? | Kích thước chính | Ghi chú |
|---|---|---|---|---|---|
| `bearing-608zz` | ISO 15 (d/D/B) [chuẩn]; SKF 608-2Z qua TDS trên [Electrokit](https://www.electrokit.com/upload/quick/5c/fe/e8cc_41024551-tds.pdf) (thứ cấp) | PDF | Chưa | 8 × 22 × 7. d1 ≈ 12,15. D2 19,2. **Vai trục da min 10, vai lỗ Da max 20**. 12,5 g | Trang skf.com cần JS, không đọc được. da max: các nguồn lệch nhau (12 / 10,5) → `TODO` |
| Nam châm CA001 Φ4 × 2 | STEP CyberBrick | STEP | Có | Φ4 × 2 | Cấp từ tính: `TODO` |

## 2. Vật tư dùng trong dự án nhưng chưa có trong danh mục

| Vật tư | Dùng ở | Nơi chứa kích thước |
|---|---|---|
| Vít M2.5 × 6/8/10/16, M2 × 6/8 (đầu?) | pushrod-arm (27 cái), cyberbrick-car (17 cái) | Mục 1.6: ISO 4762/7380. **Loại đầu chưa ghi trong Label** → `TODO` chọn ISO 4762 hay 7380; nếu là AA050 thì dùng STEP CyberBrick |
| Heat-set insert M2/M2.5/M3 | (đề xuất, Tuan chưa chốt) | Mục 1.6: Ruthex + TU Dresden |
| Đai ốc M2/M2.5/M3, vòng đệm | (chưa dùng) | ISO 4032, 7089 trong Fasteners WB |
| Servo MG90S | cyberbrick-car (theo ghi chú dự án) | TowerPro (mục 1.2) |
| Horn servo (`LK_Servo_horn`, `Servo_horn`) | cả 2 dự án | PG001: STEP horn trong thư mục `pg002-pg001-*` (cross/half/line-arm); spline 40T/Φ4,85 (PDF PG001) |
| Đầu cắm SH1.0 / XH2.54 / JR servo | mọi CyberBrick | Hãng gốc JST (SH, XH): bản vẽ trên jst-mfg.com → `TODO` (chưa tra); JR 2,54 3 chân (PG002) |
| `Socket_2x8` (header cái 2 × 8) | pushrod-arm | Bước chân 2,54 (chuẩn chung); chiều cao thân phụ thuộc hãng → `TODO` |
| Hộp số 030 dual-axis (`CB_Gearbox_030_dual_axis`) | cyberbrick-car | `Assembly_Guide_of_Dual_Axis_030_Reduction_Motor.pdf` + STEP reducer (đã ghim) |

## 3. Đề xuất cập nhật components.yaml (chỉ gợi ý, chưa sửa)

```yaml
  - id: cb-pg001-servo-9g
    thong_so:
      kich_thuoc_mm: "thân 23,0 × 12,00; tai dài 32,50; lỗ Φ2,20 cách 27,80; đáy→mặt dưới tai 16,30, →đỉnh vỏ 23,20, →đỉnh trục 27,30 (bản vẽ PG001)"
      spline: "40T / Φ4,85; vít horn Φ2,3 × 4,5 PWA"
      khoi_luong_g: "PG001 9 ± 0,5; PG002 12,4 ± 0,5"
      ghi_chu_pg002: "B-PG002 ghi KHÔNG có bảo vệ kẹt/nhiệt/áp/dòng; 80 ± 15 vòng/phút @ 6 V; không tải ≤ 200 mA; kẹt ≤ 550 mA"
    nguon: ["pdf/9g Servo Motor 180° - PG001.pdf", "pdf/9g Servo Motor 360° - PG002.pdf"]
    todo: [mốc của số 8,56 trên bản vẽ PG001]

  - id: cb-n20-motor
    thong_so:
      kich_thuoc_mm: "12,0 ± 0,2 × 10,0 ± 0,2; hộp số 9,0 ± 0,3; động cơ 15,1 ± 0,2; trục Φ3,0 (+0/−0,05) dài 10,0 ± 0,3 TÍNH TỪ MẶT HỘP SỐ (gồm gờ Φ4,0 × 0,8); vát D dài 6,0 ± 0,2; 2 × M1.6 cách 9,0 ± 0,1; dung sai chung ±0,2"
    todo: ["bỏ TODO 'trục 9,3 so với 10': Pololu cũng đo 10 từ mặt hộp số (gờ 0,7 + 9,3), LA002 đo 10 (gờ 0,8 + 9,2) → lệch ≤ 0,1 + dung sai ±0,3", "nghĩa số 2,5 ± 0,05 (bề dày qua mặt vát?)"]

  - id: n20-gearmotor
    thong_so:
      kich_thuoc_mm: "12 × 10; hộp số L 9 (1000:1: 12,5); trục Φ3 dài 10 từ mặt hộp số (gờ Φ4 × 0,7), vát D 2,5; 2 × M1.6 cách tâm trục 4,5"

  - id: cb-pc003-battery-14500
    thong_so:
      dung_luong_mah: "800 (tên CAD) / 700 (Accessories Specification 1.11) – đọc nhãn pin thật"

  - id: cb-xa007-power-switch
    thong_so: {dong_toi_da_a: 3, dien_ap_toi_da_v: 12.6, khoi_luong_g: 4.1}
    nguon: ["pdf/Accessories Specification.pdf mục 1.5"]
    todo: []

  - id: nema17-17hs4401
    thong_so:
      lo_bat: "4-M3 sâu ≥ 4,5, cách 31,0 ± 0,1"
      go_dinh_tam_mm: "Φ22,0 (−0,05) cao 2,0"
      truc_mm: "Φ5,0 (−0,012) dài 23 ± 0,5, vát D 4,5 ± 0,1"
      dien_cam_mh: 2.8
      khoi_luong_g: 280
    todo: []

  - id: raspberry-pi-4b
    thong_so:
      lo_bat: "4 lỗ Ø2,7, tâm 58 × 49, cách mép 3,5, đệm Ø6; góc R3"
      chieu_cao_mm: "USB-A 16,0; Ethernet 13,5; header 8,5; USB-C 3,2; micro-HDMI 3,0"
    nguon: [https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf]
    todo: ["nguồn 5 V – dòng tối thiểu"]

  - id: arduino-uno-r4-wifi
    thong_so:
      bo_mach_mm: "68,58 × 53,34, PCB 1"
      lo_bat: "4 lỗ Ø3,2 (R1,6) – tọa độ xem datasheet mục 13"
      muc_logic_v: "5 (RA4M1); ESP32-S3 3,3 – không nối chéo"
      gpio_ma: 8
    nguon: [https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf]
    todo: ["chép tọa độ 4 lỗ từ mục 13"]

  - id: raspberry-pi-pico
    thong_so: {bo_mach_mm: "51 × 21, PCB 1", lo_bat: "4 lỗ Ø2,1 ± 0,05"}
    nguon: [https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf]
    todo: ["tọa độ lỗ (mục Mechanical specification)"]

  - id: sg90
    thong_so:
      kich_thuoc_mm: "A 30,3 (đáy→đỉnh trục), B 22,7, C 27 (đáy→đỉnh vỏ), D 12,2, E 32,3 (cả tai), F 17 (đáy→mặt dưới tai) – hình A–F TowerPro"
    todo: [khoảng cách + Ø lỗ tai, spline – TowerPro không công bố]

  - id: bearing-608zz
    thong_so: {vai_truc_da_min_mm: 10, vai_lo_Da_max_mm: 20, khoi_luong_g: 12.5}
    nguon: ["SKF 608-2Z TDS (qua Electrokit)"]
```

Thêm mục mới (gợi ý): `mg90s` (TowerPro A–F ở mục 1.2, STEP GrabCAD ghi rõ "thứ cấp") và `heat-insert-ruthex`
(bảng mục 1.6). Bảng lỗ nên đặt ở `thresholds.yaml` `holes:` theo đề xuất #4 của cad-community-gaps-research.

## 4. Nguồn nên ghim thêm (chỉ đề xuất)

Đề xuất tạo file `maker/robotics-cad/library/datasheet-sources.tsv` theo mẫu `n20-sources.tsv`, file lưu vào
`community/boards-official/drawings/` (board) hoặc `community/datasheets/` (mới). SHA-256 dưới đây tính trên bản tải
ngày 2026-10-24 (thư mục tạm của Claude, không phải workspace). Khi tải lại, kiểm SHA-256 trước rồi mới ghim.

| file đề xuất | url | sha256 | bytes | Lý do · license |
|---|---|---|---|---|
| raspberry-pi-4-mechanical-drawing.pdf | https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf | a5c88057563016631ebca26666fd672614fc9aaa1c59128a541612c7798e9809 | 22819 | Pi 4 chính hãng, có Z cổng · không ghi license |
| abx00087-uno-r4-wifi-datasheet.pdf | https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf | 4c59ecec0a9a9f5d0029b8e11cdda23e917ce9262fe6ecddb1933182ff84f6bd | 3455270 | Lỗ bắt, logic · Arduino docs (CC-BY-SA-4.0, `TODO` xác nhận cho PDF) |
| handsontec-17hs4401s.pdf | https://www.handsontec.com/dataspecs/17HS4401S.pdf | 57daaff02e4eb2b62c16762f73875036ad79dd02050569e663a87e0042bc468f | 136062 | Bản vẽ NEMA17 · đại lý, không ghi license |
| towerpro-servo-dim-a-f.jpg | http://torqpro.com/wp-content/uploads/2014/07/小馬達尺寸標示圖B.jpg | 239562be5f25bb06d03900741d7388dcb30ab004a294155a060c10875b151f8c | 146730 | Nghĩa A–F (số nằm trên từng trang sản phẩm) · không ghi license |
| pico-datasheet.pdf | https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf | `TODO` (> 10 MB, chưa tải) | – | Tọa độ lỗ Pico. Cân nhắc chỉ trích trang cơ khí |
| Ruthex/TU Dresden | 2 trang web ở mục 1.6 | không ghim được (HTML) | – | Chép bảng vào `thresholds.yaml` + lưu ảnh chụp trang vào `docs/` khi cần |

Ngoài ra nên thêm Fasteners WB vào `community/pins.tsv`: https://github.com/shaise/FreeCAD_FastenersWB tag `0.5.67`
(SHA và license: `TODO`). Bảng ISO dùng ở mục 1.6 lấy từ bản này, nên ghim để số không đổi khi addon tự cập nhật.

## 5. Còn chưa tìm được (TODO)

- **Ruthex:**
  - Bản vẽ gốc định nghĩa D1/D2.
  - Nhiệt ép do hãng công bố (ruthex.de trả 429; thử lại sau, hoặc đọc tờ hướng dẫn trong hộp insert).
- **SG90/MG90S (TowerPro):**
  - Khoảng cách và Ø lỗ tai, spline (số răng/Φ). Hãng không công bố → đo hàng thật hoặc dùng STEP thứ cấp có ghi nhãn.
- **PG001:**
  - Mốc của số 8,56.
  - Hình kích thước PG002 (bản PDF mờ). Hỏi Bambu hoặc đo STEP.
- **XA004/XA003:** Ø lỗ và khoảng cách lỗ bắt không có trong PDF → đo trên STEP chính hãng (đã ghim).
- **Pico:** tọa độ 4 lỗ.
- **UNO R4 WiFi:** gán số trên hình cho từng lỗ.
- **Nucleo-64, Zero 2 W:** Ø lỗ.
- **Cổng/header (boards-official):** chiều cao theo hãng. Bản vẽ Pi 4 có Z, các board khác vẫn ước tính.
- **Bạc đạn 608:**
  - da max (12 hay 10,5).
  - Bán kính góc r1,2 min. Lấy từ catalogue SKF (trang web cần JS).
- **Đầu cắm:** bản vẽ JST SH/XH.
- **Vít trong BOM:** loại đầu chưa ghi trong Label.
- **Lỗ tự ren vào PETG** (không insert): **không có số của hãng**. Bảng khoan taro (1,6/2,05/2,5) là cho kim loại.
  - EJOT PT có hệ số lỗ = 0,75 × d cho PET (`FSScrewCalc.py`), nhưng chỉ cho vít EJOT.
  - Cần mẫu in thử (đề xuất #1 của gaps-research).
- **Linh kiện không có hãng đứng sau** (Mabuchi encoder, ESP32 DOIT, HC-SR04, L298N, Blue Pill): chỉ đo hàng thật.

## Nguồn

- File đã ghim [hãng], đọc 2026-10-24:
  - `community/cyberbrick-official/pdf/{9g Servo Motor 180° - PG001.pdf, 9g Servo Motor 360° - PG002.pdf, B-LA002.pdf, Accessories Specification.pdf, Remote_Control_Receiver_Shield_-_XA004.pdf}`
  - `community/n20-motor/pdf/pololu-micro-metal-gearmotors-dimensions.pdf`
- Pololu 2364 (trục 9 mm, giá bắt #989/#1086/#1089): https://www.pololu.com/product/2364
- TowerPro: https://towerpro.com.tw/product/sg90-7/ · https://towerpro.com.tw/product/mg90s-3/ · hình A–F: http://torqpro.com/wp-content/uploads/2014/07/小馬達尺寸標示圖B.jpg
- Raspberry Pi:
  - Pi 4 mechanical drawing: https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf
  - Pico datasheet: https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf
  - Lỗ Ø2,1 Pico (thứ cấp, đại lý): https://uk.rs-online.com/web/p/raspberry-pi/2122161
- Arduino UNO R4 WiFi datasheet (rev 9): https://docs.arduino.cc/resources/datasheets/ABX00087-datasheet.pdf
- Handsontec 17HS4401S: https://www.handsontec.com/dataspecs/17HS4401S.pdf
- Ruthex (thứ cấp):
  - https://www.3djake.com/ruthex/threaded-insert-m25-70-pieces
  - https://www.3djake.com/ruthex/threaded-insert-m2-70-pieces
  - https://www.3djake.com/ruthex/m2-m3-m4-m5-threaded-insert-assortment-box
- TU Dresden, Wärmeeinbettung bei FDM-3D-Drucken (định nghĩa D/L/T/E/W, dòng ruthex): https://tu-dresden.de/ing/elektrotechnik/die-fakultaet/fakultaetswerkstatt/werkstattteil-praezisionsmechanik/waermeeinbettung-bei-fdm-3d-drucken
- Nhiệt ép:
  - CNC Kitchen: https://cnckitchen.com/blog/tips-and-tricks-for-heat-set-inserts
  - Prusa: https://www.prusa3d.com/product/threaded-inserts-m2-5-standard-100-pcs/
- Fasteners WB 0.5.67 [máy]: `%APPDATA%/FreeCAD/v1-1/Mod/fasteners/{FsData/iso4762def.csv, iso7380def.csv, iso4032def.csv, iso7089def.csv, HeatInserts.csv, ScrewMaker.py, FSScrewCalc.py, FsFunctions/FSmakeCylinderHeadScrew.py, FSmakeButtonHeadScrew.py, FSmakeHeatInsert.py}`
- Lỗ xuyên/taro (thứ cấp): https://optimas.com/technical-resources/tapping-sizes/ · ISO 273:1979: https://www.iso.org/standard/4183.html
- SKF 608-2Z TDS (thứ cấp, mirror): https://www.electrokit.com/upload/quick/5c/fe/e8cc_41024551-tds.pdf
