# Nghiên cứu: cộng đồng làm CAD in 3D thế nào – STLab cần cải thiện gì

Viết 2026-10-24 cho pipeline `maker/robotics-cad/` (dự án `pushrod-arm`, `cyberbrick-car`). Tuan sửa/bổ sung trực tiếp file này.

**Phạm vi:** thiết kế cho in FDM ở mức chi tiết cơ khí robot nhỏ (dung sai, lỗ, ren/insert, hướng in, bánh răng),
hiệu chuẩn Bambu A1, cách dự án robot mở tổ chức repo, hệ sinh thái Bambu, vòng phản hồi sau in.

**Không lặp:** Assembly/VarSet/PartDesign/TopoNaming/TechDraw/headless/addon lắp ráp, code-CAD, CI, `metrics.json`, release
đã có trong [freecad-automation-research.md](freecad-automation-research.md) và [quy-trinh-chuan-hoa-cad.md](quy-trinh-chuan-hoa-cad.md).
FEM + số liệu TDS (E, σ theo X-Y/Z) đã có trong `maker/robotics-cad/kiem-tra-model.md` mục 4.

Nhãn: **[nguồn gốc]** = tài liệu/mã nguồn của hãng hoặc dự án · **[máy]** = đọc file cài trên máy (Bambu Studio 02.07,
Fasteners 0.5.67, Gears 1.4.0), không chạy gì · **(thứ cấp)** = blog/forum/đại lý · `TODO` = chưa xác nhận.

## 0. Kết luận nhanh

1. **Khoảng trống lớn nhất là dung sai chưa đo trên máy thật.** Khe 0,2 mm là số Tuan chốt nhưng chưa in mẫu.
   Prusa khuyên khe cho chi tiết **chuyển động bắt đầu ≥ 0,3 mm**. Bambu Lab khuyên **đo rồi bù trong slicer**
   (`xy_hole_compensation`, `xy_contour_compensation`, `filament_shrink`) chứ không đoán. Profile A1 đang để 2 thông số bù lỗ/viền = 0.
2. **Cộng đồng in "thước đo" trước khi in cả bộ.** SO-ARM100 (7 863★) bắt in `Gauge_0` thử khớp với **servo thật**
   trước khi in cả cánh tay. STLab chưa có thước đo cho hốc SG90/PG001/N20, lỗ vít M2/M2.5 hay trục double-D.
3. **Lỗ cho heat-set insert phải lấy theo nhà sản xuất.** Ruthex (bảng qua đại lý 3DJake): M3 có D3 = 4,0 mm, L = 5,7 mm,
   W(min) = 1,6 mm; M2 có D3 = 3,2 mm, L = 4,0 mm, W(min) = 1,3 mm. Nghĩa của từng cột chưa xác nhận.
   STLab chưa có quy ước lỗ vít/insert nào có nguồn.
4. **Có thể thay ngưỡng brim "TẠM" bằng công thức của chính slicer.** `Brim.cpp` của Bambu Studio tính brim tự động từ
   chiều cao/mômen quán tính mặt chân, hệ số PETG = 2, bỏ brim < 5 mm, tối đa 18 mm. `brim_contact_max_mm2` = 120 và
   `brim_aspect_min` = 2,5 đang là số Claude tự đặt.
5. **Bù lỗ tự động của Bambu không hỗ trợ PETG Basic.** `enable_circle_compensation` chỉ nhận PLA Basic, PLA CF, PET CF,
   PETG CF, PETG HF (theo mã nguồn), nên với nhựa mặc định của STLab phải bù tay.
6. **Hướng sợi chưa vào bước kiểm.** TDS PETG Basic: σ kéo theo X-Y là 51 MPa, theo Z chỉ 35 MPa (−31 %), nhưng
   `printability.py` chỉ xét nhô ra. Chưa có cảnh báo cho chốt/tai chịu lực bị in đứng.
7. **Điều khiển A1 từ script bị giới hạn.** Muốn gửi lệnh in thì phải bật **Developer Mode** (chỉ chạy LAN, mở MQTT/FTP,
   Bambu không hỗ trợ) hoặc đi qua Bambu Connect. Chưa nên làm. Giá trị thật nằm ở **vòng đo sau in**.

## 1. Dung sai lắp ghép và bù kích thước trên Bambu A1

**Cộng đồng/hãng làm gì**
- Prusa KB [nguồn gốc]: không có giá trị dung sai "chung" vì nó phụ thuộc kích thước, hướng in, hình dạng, hiệu chuẩn và vật liệu.
  Máy Prusa chính xác "ít nhất 0,2 mm". Chi tiết chuyển động (bản lề) nên bắt đầu từ **≥ 0,3 mm**. Nên vát mép thay vì bo tròn
  ở cạnh hướng xuống bàn, và vát mép chỗ 2 chi tiết lồng vào nhau. Bản thiết kế phải in thử nhiều vòng.
- Bambu wiki [nguồn gốc] có quy trình 3 lớp, theo thứ tự:
  - (1) **Shrinkage** (`filament_shrink`, %, mặc định 100 %): co toàn chi tiết theo X-Y, tính bằng đo/thiết kế × 100 %,
    in khối 20 mm để đo. Thông số này **không** sửa lỗ.
  - (2) **X-Y hole / contour compensation** (`xy_hole_compensation`, `xy_contour_compensation`, mm): lấy (sai số đo)/2 vì
    giá trị cộng theo **bán kính**, nên đường kính lỗ tăng gấp đôi giá trị nhập. Ví dụ trên wiki: lỗ M6 đo 5,66 mm → thiếu 0,24 mm
    → nhập 0,12 mm → lỗ lại dư 0,04 mm.
  - (3) **Auto circle contour-hole compensation**.
  - Trước khi bù, wiki yêu cầu loại trừ các nguyên nhân khác: elephant foot, nhựa ẩm, flow dynamics, lỗ gần cỡ đầu phun
    (< 1 mm khó chỉnh), thiếu vát dẫn hướng, đường nối (seam).
  - Giới hạn: bù lỗ **chỉ áp lên đường kín**. Lỗ có cửa hở ra cạnh thì không được bù, và bật bù có thể làm **tách lớp** quanh lỗ.
- Mã nguồn Bambu Studio `PrintConfig.cpp` [nguồn gốc]:
  - `xy_hole_compensation`, `xy_contour_compensation`: mặc định 0.
  - `elefant_foot_compensation`: "shrink the initial layer".
  - `enable_circle_compensation`: thử nghiệm, Ø < 50 mm, **chỉ PLA Basic, PLA CF, PET CF, PETG CF, PETG HF**.
    Đi kèm `circle_compensation_manual_offset`: số dương làm chặt hơn.
- Profile đang cài [máy, Bambu Studio 02.07, profile `02.07.00.07`]:
  - `0.20mm Standard @BBL A1`: `elefant_foot_compensation` = **0,075 mm**, `xy_hole/contour_compensation` = 0.
  - `Bambu PETG Basic @BBL A1`: `filament_flow_ratio` = 0,94, `filament_shrink` = 100 %, đầu phun 245 °C,
    Textured PEI 70 °C, khoảng nhiệt 230–270 °C.
- OrcaSlicer wiki [nguồn gốc]: có sẵn mẫu "Orca Tolerance Test" gồm 6 lỗ lục giác với khe **0 / 0,05 / 0,1 / 0,2 / 0,3 / 0,4 mm**,
  thử bằng lục giác chìm 6 mm hoặc miếng thử in kèm. Có thêm Shrinkage Z và "Precise Z height".

**STLab hiện có:** `min_clearance_mm: 0.2` (Tuan chốt, chưa in thử). `thresholds.yaml` đã ghi rằng profile A1 để bù = 0.
Chưa có `xy_hole_compensation` trong `print.yaml`, chưa đo co ngót PETG Basic trên máy này. Bề dày vỏ theo bội số đường in đã có.

**Khoảng trống**
- Chưa có số đo nào trên A1 + PETG Basic: lỗ đứng, lỗ nằm, trục, khe trượt.
- Chưa tách **khe theo loại lắp**: lắp ép, lắp trượt, quay. Hiện chỉ có một số 0,2 mm. Prusa gợi ý quay/trượt ≥ 0,3 mm.
- Chưa chọn **sửa ở đâu**: bù trong slicer (một chỗ, áp cho mọi lỗ kín) hay vẽ dư trong CAD (rõ ràng nhưng phải sửa model khi đổi nhựa).
  Đánh đổi: bù slicer không áp được cho lỗ hở cạnh, và đổi cả ngoại hình chi tiết. Vẽ dư thì đổi cuộn nhựa phải sửa CAD.
  Khuyến nghị: **CAD vẽ đúng kích thước danh định + khe theo loại lắp**, còn bù co ngót/lỗ đặt trong **preset process riêng**
  (`print.yaml` `overrides`), có số đo làm nguồn.

## 2. Hiệu chuẩn và mẫu in thử

**Cộng đồng/hãng làm gì**
- Bambu wiki Flow Dynamics [nguồn gốc]:
  - A1 **tự hiệu chuẩn** K bằng cảm biến dòng xoáy ở chỗ gạt nhựa, từ firmware **01.04.00.00**.
  - Cần chạy lại khi đổi hãng/loại nhựa, thay hoặc mòn đầu phun, đổi nhiệt độ hay `max volumetric speed`.
  - Kết quả dao động khoảng 10 %. Không tin cậy khi nhựa ẩm, nhựa mềm (TPU) hoặc dùng hotend bên thứ ba.
  - Trong mã nguồn, `pressure_advance` ghi chú "Useless for Bambu Printer", nên **không** chỉnh tay PA trên A1.
- Bambu wiki Flow Rate [nguồn gốc]:
  - Tự động chỉ có trên dòng X1. A1 hiệu chuẩn tay theo 2 bước: thô 80–120 % (bước 5 %), rồi tinh 91–100 % (bước 1 %).
  - Chỉ làm khi đã chỉnh flow dynamics mà vẫn dư hoặc thiếu nhựa.
- Mẫu dung sai:
  - Bambu wiki dùng mẫu thử lỗ bằng vít M3–M6 trên MakerWorld (tác giả Lebadjuras) và mẫu viền lồng vào lõi cuộn nhựa Bambu.
    Vít M6 thực tế khoảng 5,9 mm vì dung sai ren ISO 6g, nên đo vít trước.
  - Orca có Tolerance Test (mục 1).
- **SO-ARM100** [nguồn gốc, README]: bước 3 "Check Printer Accuracy" trước bước 4 "Print the Parts".
  In `Gauge_0` và `Gauge_tight_1` để thử khớp với **servo STS3215 thật**, hoặc mẫu thử với gạch Lego 4×2 (`zero`, `-0.1`).
  Không vừa thì chỉnh máy rồi in lại.

**STLab hiện có:** không có mẫu nào (mẫu cũ `maker/in-3d` đã xóa 2026-10-23). `/print-result` chỉ ghi đạt/không đạt bằng chữ.

**Khoảng trống:** thiếu một **bàn in hiệu chuẩn STLab** (~30–45 phút in, `TODO` ước theo slicer) gồm:
- (a) thang lỗ đứng/nằm Ø2–Ø6 mm, khe 0–0,4 mm;
- (b) hốc thử **servo SG90/PG001/MG90S, N20, trục double-D LA013** với khe 0,1 / 0,2 / 0,3 mm;
- (c) lỗ vít M2/M2.5 tự ren và lỗ insert;
- (d) khối 20 mm để đo co ngót.

Bàn này sinh bằng script (`build_*.py` giống cyberbrick-car), chạy qua `prepare-print`. Kết quả đo ghi vào file (mục 9).

## 3. Lỗ vít, ren in và heat-set insert

**Cộng đồng/hãng làm gì**
- Ruthex (bảng kỹ thuật trên trang đại lý 3DJake, chưa đọc được trang gốc ruthex.de do bị chặn 429):

  | Ren | ⌀D1 | ⌀D2 | ⌀D3 | L | W (min.) |
  |---|---|---|---|---|---|
  | M2 | 3,6 | 3,1 | 3,2 | 4,0 | 1,3 |
  | M3 | 4,6 | 3,9 | 4,0 | 5,7 | 1,6 |
  | M4 | 6,3 | 5,5 | 5,6 | 8,1 | 2,1 |

  Trang **không chú thích cột**. Cách hiểu thường gặp là D1 = ngoài khía, D2 = đầu dẫn, D3 = **lỗ khuyên dùng**,
  W = **thành tối thiểu quanh lỗ**. Cách hiểu này `TODO` xác nhận bằng bản vẽ Ruthex. Cỡ M2.5: `TODO` (không thấy bảng).
- Prusa (trang sản phẩm insert, đọc qua trích đoạn tìm kiếm vì trang chặn 403): nung mỏ hàn bằng **nhiệt in của nhựa + 10–20 °C**.
  Lỗ vừa đủ để đặt insert dễ, không để gờ dưới insert. Kích thước lỗ nằm trong hình vẽ: `TODO`.
- Ý kiến forum Prusa (thứ cấp): lỗ sâu hơn insert ≥ 0,5 mm để chứa nhựa chảy.
- Fasteners WB 0.5.67 [máy, mã nguồn]:
  - Có loại **"IUT[A/B/C] Heat Staked Metric Insert"** (`FsData/HeatInserts.csv`), M3 có `D` = 4,00, `Length` = 5,74,
    `ExtDia` = 4,55. Đây là **dòng insert khác Ruthex** và nghĩa cột `D` chưa xác nhận.
  - Có chế độ ren **"3D printer compatible"** với hệ số Scale (A) và Offset (B) riêng cho vít và đai ốc
    (`Widget3DPrintSettings.ui`, `tuningTable.csv`).
  - Có lệnh **Screw Calc** tính lỗ cho từng loại vít.

**STLab hiện có:** vít M2/M2.5 được đếm vào BOM theo Label. **Không có quy ước đường kính lỗ** cho vít tự ren vào nhựa,
lỗ xuyên, hốc đai ốc hay insert. Trục vít (worm) của pushrod là ren in. `short_overhang_mm` cũng ghi "Tuan in kiểm ren trục vít rồi chỉnh".

**Khoảng trống**
- Cần bảng `holes:` trong `thresholds.yaml`, mỗi dòng có nguồn hoặc `TODO`: lỗ xuyên, lỗ vít tự ren, lỗ insert, thành tối thiểu.
- Insert: khi in thử mẫu mục 2 thì thử Ø3,2 (M2) và Ø4,0 (M3) theo Ruthex.
- `check.py` có thể kiểm thêm "**thành quanh lỗ ≥ W(min)**" (đã có đo thành mỏng bằng tia).
- Đánh đổi insert và vít tự ren: insert bền khi tháo lắp nhiều lần (phù hợp đồ dạy học sinh), nhưng thêm bước mỏ hàn
  (rủi ro bỏng, mỏ hàn khoảng 255–265 °C nếu theo Prusa +10–20 °C trên 245 °C) và thêm chi phí. **Tuan quyết.**

## 4. Hướng in và độ bền

**Cộng đồng/hãng làm gì**
- TDS Bambu PETG Basic (đã trích trong `kiem-tra-model.md` 4.4): σ kéo **X-Y 51 ± 1 MPa, Z 35 ± 6 MPa**; E theo X-Y 2 780, theo Z 2 550 MPa.
- Prusa KB: chi tiết FFF "như gỗ" (bền theo một phương), nên hướng in cho chi tiết chịu lực phải chọn theo độ bền.
- Hubs, hãng dịch vụ in, bản hướng dẫn FDM của họ:
  - Chốt **< 5 mm** chỉ gồm đường viền nên yếu; thêm bo nhỏ ở chân chốt.
  - Cạnh chạm bàn nên **vát 45° hoặc bo** (vì elephant foot).
  - Cầu ngang có võng và vết support khi dài **> 5 mm**.
  - Nhô ra khoảng **45°** in được.
  - Lỗ đứng quan trọng thì in nhỏ rồi khoan lại.

**STLab hiện có:** hướng in khai trong `print.yaml`. `printability.py` kiểm nhô ra và kiểm theo lớp. cyberbrick-car đã chọn
"trục bánh trước in liền vành, in đứng, chắc hơn trục nằm ngang" theo cảm nhận, chưa dựa trên số liệu.

**Khoảng trống**
- Chưa có quy tắc "**chi tiết chịu lực khai phương tải**", ví dụ `load_axis: z` trong `print.yaml`. Khi phương tải trùng Z in
  (chốt, tai bắt vít in đứng), cần WARN và nhắc dùng σ_Z = 35 MPa thay vì 51 MPa trong FEM.
- Chưa có cảnh báo chốt/trục in **Ø < 5 mm**. Trục bánh Ø5 của cyberbrick-car nằm đúng ở biên này.
- Vát chân 45° ở cạnh chạm bàn chưa có trong checklist. Profile A1 đã bù 0,075 mm, nhưng chi tiết lắp ghép ở lớp đầu vẫn nên vát.

## 5. Bánh răng in

**Cộng đồng/hãng làm gì**
- Gears WB 1.4.0 [máy, `involutegear.py`]: bánh răng thân khai có `module`, `pressure_angle`, `shift` (dịch chỉnh),
  `undercut`, bo đỉnh/chân, và nhóm **tolerance** gồm `backlash`, `reversed_backlash`, `clearance`, `head`.
  Có sẵn rack, worm, bevel, cycloid, timing. Đã cài, nhưng STLab đang tự viết script bánh răng.
- Module tối thiểu và khe răng cho FDM 0,4 mm: **không tìm được nguồn hãng**, ghi `TODO`. Không đưa số nào vào ngưỡng
  khi chưa in thử.

**STLab hiện có:** pushrod-arm dùng m1 (z10/z60), worm–rack. Cặp ăn khớp khai `mesh-pair`, nghĩa là bỏ qua khi kiểm va chạm.
Bàn P5 dùng lớp 0,16 mm, 4 vách, infill 40 %.

**Khoảng trống**
- `mesh-pair` hiện **tắt kiểm**, chưa có kiểm "khe răng tối thiểu". Có thể đo khoảng cách nhỏ nhất giữa 2 bánh qua `sweep`
  rồi so với `backlash` khai trong tham số.
- Muốn tham số hóa được thì bánh răng mới nên dựng bằng Gears WB (backlash, dịch chỉnh, chống cắt chân) thay vì script tay.
- Mẫu in thử mục 2 nên có một cặp m1 với backlash 0 / 0,1 / 0,2 mm để chọn bằng tay.

## 6. Dự án robot mở tổ chức thế nào (đọc repo trực tiếp, sao tra 2026-10-24)

| Dự án | Sao | CAD | Tổ chức | Điều đáng học |
|---|---|---|---|---|
| [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) | 7 863 | SolidWorks (STEP + STL) | `STEP/`, `STL/` (theo bản: SO100/SO101, `Individual/`, `Gauges/`), `Simulation/` (URDF), `Optional/`, `CHANGELOG.md`, `3DPRINT.md`, `CITATION.cff` | **Thước đo trước khi in**; STL gộp sẵn 1 bàn cho mỗi cỡ bàn (Ender 220, Prusa 250); thông số in tối thiểu (PLA+, 0,2 mm, infill 15 %, support > 45°, **không support trong lỗ vít nằm ngang**); CHANGELOG ghi mã phiên bản CAD (`SO_5DOF_ARM100_08k`) cho mỗi lần thay STL |
| [AngelLM/Thor](https://github.com/AngelLM/Thor) | 1 626 | **FreeCAD** | `freecad-src/`, `step/`, `stl/`, `mods/` (bản sửa cộng đồng), release tag v1.0 / v2.1.1; BOM, lắp, điện nằm trên web riêng | Nguồn FreeCAD + STEP + STL đều lên git; tách `mods/` để không lẫn bản chuẩn |
| [AlexanderKoch-Koch/low_cost_robot](https://github.com/AlexanderKoch-Koch/low_cost_robot) | 3 423 | – | (không đọc sâu) | – |
| [BCN3D/BCN3D-Moveo](https://github.com/BCN3D/BCN3D-Moveo) | 2 010 | – | ngừng cập nhật từ 2022 | – |

**STLab hiện có:** `README`/`ASSEMBLY.md`/`.pdf`, `BOM.md`, `print.yaml`. STL và 3MF là file sinh, không lên git.
FCStd chỉ nằm trên máy. GĐ C (Release) chưa làm.

**Khoảng trống**
- Chưa có **CHANGELOG** theo phiên bản in. Lịch sử nằm rải trong README, và `metrics.json` diff mới là thô.
- Chưa có **STEP từng chi tiết** đi kèm bản phát hành. Người ngoài (hoặc học sinh) không mở được FCStd nếu không có dữ liệu trên máy.
- Chưa có thông số in tối thiểu dạng "in trên máy khác" cho người không dùng A1.
- Chưa có thư mục `gauges/` cho mỗi dự án.
- Những việc này gộp vào GĐ C khi làm `release.py`.

## 7. Hệ sinh thái Bambu

- **Điều khiển máy từ script** [nguồn gốc, Bambu wiki]:
  - Từ firmware có cơ chế xác thực, các lệnh in, di chuyển, nhiệt độ, hiệu chuẩn và firmware từ phần mềm khác phải đi qua
    **Bambu Connect**. Không bị chặn: trạng thái qua MQTT (cho Home Assistant), in từ thẻ SD.
  - **Developer Mode** (A1: Setting → LAN Only Mode → Developer Mode) làm máy hoạt động như firmware cũ: mở MQTT, live stream
    và FTP, **không kết nối Bambu Cloud được**, Bambu không hỗ trợ.
  - Rủi ro: mạng của trung tâm có học sinh thì ai trong mạng LAN cũng có thể điều khiển máy (gia nhiệt, di chuyển) → **không bật**
    khi chưa có mạng tách riêng. **Tuan quyết.**
  - Đọc trạng thái (chỉ đọc) là đủ cho "in xong thì nhắc `/print-result`". `TODO`: kiểm A1 ở chế độ thường có cho đọc MQTT
    cục bộ không, và cần mã truy cập gì.
- **Phát hiện lỗi in trên A1:** trang wiki Spaghetti detection nói về dòng X1. Một nguồn thứ cấp (Obico) nói A1 không có AI.
  Tình trạng A1 là `TODO` (chưa xác nhận).
- **MakerWorld Parametric Model Maker:** chạy OpenSCAD trên web để người dùng chỉnh tham số rồi tải 3MF. **Không có tài liệu
  chính thức**; repo tài liệu không chính thức ghi nhận điều này (2026-04-21). Liên quan STLab chỉ khi muốn đăng mẫu cho học sinh
  tự chỉnh (ví dụ gá servo theo cỡ). Ưu tiên thấp, vì pipeline STLab dùng FreeCAD/Python, không dùng OpenSCAD.
- **3MF:** Bambu CLI đã xuất 3MF theo bàn. Có thể dùng **modifier/part settings trong 3MF** để tăng vách quanh lỗ insert
  thay vì tăng `wall_loops` cả bàn. `TODO`: kiểm CLI nhận 3MF đầu vào có modifier (chưa thử).

## 8. Ngưỡng "TẠM" trong `thresholds.yaml`: thay bằng gì

| Khóa | Hiện tại | Có nguồn thay được? | Đề xuất |
|---|---|---|---|
| `print.bridge_max_mm` | 5,0 (TẠM) | **Có**: Hubs FDM guide, cầu > 5 mm thì võng/vết | giữ 5,0, ghi nguồn; xác nhận bằng mẫu in mục 2 |
| `print.brim_contact_max_mm2` | 120 (TẠM) | **Có cách tốt hơn**: `Brim.cpp` của Bambu tính bề rộng brim = hệ số bám (PETG 2, TPU 0,5, còn lại 1) × min(max(chiều cao/mômen quán tính mặt chân × tốc độ max / 24, …), 18) mm; < 5 mm thì bỏ | thay 2 ngưỡng diện tích/tỉ lệ bằng **công thức của slicer** (tính lại trong `printability.py`), hoặc để `brim_type: auto_brim` của slicer quyết. Tuan đã chốt "chi tiết nhỏ phải brim" → so 2 cách trên 2 dự án trước khi đổi |
| `print.brim_aspect_min` | 2,5 (TẠM) | như trên | như trên |
| `print.support_min_patch_mm2` | 4,0 (TẠM) | không tìm thấy | giữ TẠM, đo trên mẫu in |
| `print.short_overhang_mm` | 2,5 (TẠM) | không tìm thấy | giữ TẠM; Tuan đang in kiểm ren trục vít |
| `min_overlap_mm3`, `thin_area_min_mm2` | 0,1 / 1,0 (TẠM) | là ngưỡng lọc nhiễu số học, không có nguồn ngoài | giữ, ghi rõ "ngưỡng nội bộ" |
| `overhang_deg` | 45 | Prusa 45–60° với đầu phun 0,4; Hubs khoảng 45°; TDS PETG ghi khoảng 70° (không rõ cách đo) | giữ 45, thêm nguồn Prusa |
| `min_clearance_mm` | 0,2 (Tuan chốt) | Prusa: chuyển động ≥ 0,3 mm | tách `clearance.fixed/slide/rotate`; **chờ in mẫu** |
| (mới) `holes.insert_*` | – | Ruthex M2 Ø3,2 / M3 Ø4,0, W ≥ 1,3 / 1,6 mm (nghĩa cột `TODO`) | thêm, kèm `TODO` xác nhận |
| (mới) `print.pin_min_d_mm` | – | Hubs: chốt < 5 mm yếu | thêm WARN |

## 9. Vòng phản hồi sau in (đo bằng thước kẹp)

**Cộng đồng/hãng làm gì:**
- Bambu wiki: in mẫu → để nguội tới nhiệt độ phòng → đo bằng thước kẹp → co ngót = đo/thiết kế × 100 % → bù lỗ = sai số/2 → in lại để
  xác nhận → lặp nếu cần.
- Bambu wiki khuyên chi tiết lắp ghép yêu cầu cao thì hiệu chỉnh riêng từng model.
- Orca: hiệu chỉnh riêng cho từng cặp máy + nhựa.
- SO-ARM: chưa khớp thước đo thì không in bộ.

**STLab hiện có:** `/print-result` → README + `harness-lab/inbox.md` (chữ). GĐ E: "lỗi lặp ≥ 2 lần thành quy tắc".

**Khoảng trống:** chưa có **dữ liệu số**. Đề xuất file `maker/robotics-cad/measurements.yaml` (lên git):
- Mỗi dòng gồm: ngày, máy (A1 + đầu phun), nhựa (preset + lô cuộn), process, chi tiết/mẫu, kích thước thiết kế, kích thước đo
  (trung bình 3 lần), loại (lỗ đứng/lỗ nằm/trục/khe), kết quả lắp (lỏng/vừa/chặt).
- Script tính đề xuất `filament_shrink` và `xy_hole_compensation`, rồi ghi **nguồn = id phép đo** vào `thresholds.yaml`.
- Ngưỡng nào đổi thì thấy trong `git diff`. Cách này thay dần các giá trị "TẠM".

## Đề xuất xếp theo lợi/công

Công: 1 buổi ≈ 3–4 giờ làm cùng Claude (**ước lượng**, chưa đo). Thời gian in không tính vào công.

| # | Việc | Lợi | Công | Đánh đổi | Ai quyết |
|---|---|---|---|---|---|
| 1 | **Bàn in hiệu chuẩn STLab** (script sinh): thang lỗ/khe 0–0,4 mm, hốc SG90/PG001/N20/double-D, lỗ M2/M2.5 tự ren + insert Ø3,2/Ø4,0, khối 20 mm, cặp bánh răng m1 với backlash 0/0,1/0,2 | thay số "chưa thử" bằng số đo; một lần in dùng cho mọi dự án | 1 buổi + 1 lần in | tốn khoảng 1 giờ máy + nhựa; phải đo cẩn thận | Claude làm được; **cần in thử** |
| 2 | `measurements.yaml` + script đề xuất `filament_shrink` / `xy_hole_compensation` | ngưỡng có nguồn = phép đo; theo dõi theo cuộn nhựa | 0,5 buổi | thêm bước nhập số đo tay | Claude làm được |
| 3 | Tách `clearance` theo loại lắp (cố định/trượt/quay) trong `thresholds.yaml` + `check.py` | khớp quay bớt kẹt (Prusa ≥ 0,3 mm) | 0,5 buổi | phải gán loại cho từng cặp (thêm khai báo) | **Tuan quyết** số sau mẫu #1 |
| 4 | Bảng `holes:` (xuyên/tự ren/insert/thành tối thiểu) + kiểm "thành quanh lỗ ≥ W" | lỗ vít/insert đúng ngay lần đầu | 0,5–1 buổi | cần quy ước Label/tên lỗ để script nhận ra | Claude làm; Tuan chọn insert hay tự ren |
| 5 | Preset process "STLab PETG Basic A1 – lắp ghép" (bù lỗ/co theo #2), gọi qua `print.yaml` | sửa một chỗ cho mọi bàn | 0,25 buổi | bù lỗ không áp cho lỗ hở cạnh, có thể tách lớp | Claude làm sau #1–#2 |
| 6 | Brim theo công thức `Brim.cpp` (thay 2 ngưỡng TẠM) hoặc `auto_brim` | bỏ 2 số không nguồn | 0,5 buổi | công thức có thể đổi theo bản Bambu Studio → ghim phiên bản | **Tuan** (đã chốt chi tiết nhỏ phải brim) |
| 7 | WARN hướng sợi: `load_axis` trong `print.yaml` + chốt Ø < 5 mm | bắt chốt/tai yếu trước khi gãy | 0,5 buổi | phải khai phương tải bằng tay | Claude làm được |
| 8 | Bánh răng mới bằng Gears WB (backlash, dịch chỉnh) + đo khe răng thay vì tắt bằng `mesh-pair` | ăn khớp có tham số | 1 buổi | đổi cách dựng; bánh răng cũ giữ nguyên | **Tuan** |
| 9 | Thư mục `gauges/` + CHANGELOG + STEP từng chi tiết, gộp vào GĐ C | người khác in lại được, giống SO-ARM | trong GĐ C | thêm file vào release | **Tuan** (cùng GĐ C) |
| 10 | Modifier 3MF tăng vách quanh lỗ insert | bền lỗ mà không tăng nhựa cả bàn | 1 buổi thử | CLI chưa kiểm | hoãn tới khi dùng insert |
| 11 | A1 Developer Mode / MQTT gửi lệnh | tự in, tự nhận kết quả | 1–2 buổi | **rủi ro bảo mật LAN**, mất cloud, không được hỗ trợ | **Hoãn**, Tuan quyết |
| 12 | MakerWorld Parametric Model Maker | học sinh tự chỉnh mẫu | 1+ buổi | OpenSCAD, không tài liệu chính thức | Hoãn |

## Top 5 việc nên làm tiếp

1. **In bàn hiệu chuẩn STLab (#1)**: thước đo cho servo/N20/double-D + thang khe + lỗ vít/insert. Đây là việc chặn mọi việc sau
   (khe 0,2 mm, ren trục vít, lỗ insert).
2. **`measurements.yaml` + công thức Bambu (#2)**, rồi lập **preset bù riêng (#5)**: số đo thay giá trị "TẠM", có lịch sử trên git.
3. **Tách khe theo loại lắp (#3)**, xuất phát từ Prusa ≥ 0,3 mm cho chuyển động; Tuan chốt số sau khi đo.
4. **Bảng `holes:` + kiểm thành quanh lỗ (#4)**: dùng Ruthex Ø3,2/Ø4,0 làm điểm đầu, xác nhận bằng mẫu in.
5. **WARN hướng sợi + chốt < 5 mm (#7)**: rẻ, đúng loại lỗi gãy ở robot nhỏ. Trong FEM dùng σ_Z = 35 MPa khi tải theo Z.

## Nguồn
- Prusa KB, Modeling with 3D printing in mind (dung sai ≥ 0,3 mm cho chi tiết chuyển động, vát/bo, hướng in, vách theo đường in): https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
- Bambu wiki:
  - Co ngót, bù lỗ, auto circle: https://wiki.bambulab.com/en/knowledge-sharing/3d-prints-shrinkage
  - X-Y Hole/Contour Compensation (quy trình, ví dụ M6, giới hạn đường kín): https://wiki.bambulab.com/en/software/bambu-studio/xy-hole-contour-compensation
  - Flow Dynamics (A1 tự hiệu chuẩn bằng cảm biến dòng xoáy, FW 01.04.00.00, dao động 10 %): https://wiki.bambulab.com/en/software/bambu-studio/calibration_pa
  - Flow Rate (thô/tinh, chỉ X1 tự động): https://wiki.bambulab.com/en/software/bambu-studio/calibration_flow_rate
  - Developer Mode: https://wiki.bambulab.com/en/knowledge-sharing/enable-developer-mode
  - Third-party integration / Bambu Connect: https://wiki.bambulab.com/en/software/third-party-integration
  - Spaghetti detection (X1): https://wiki.bambulab.com/en/knowledge-sharing/Spaghetti_detection
- Mã nguồn Bambu Studio:
  - `PrintConfig.cpp` (`xy_hole_compensation`, `xy_contour_compensation`, `elefant_foot_compensation`, `enable_circle_compensation`, `filament_shrink`, `pressure_advance`): https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp
  - `Brim.cpp` (công thức auto brim, hệ số PETG 2): https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Brim.cpp
- Profile Bambu Studio trên máy [máy]: `C:/Program Files/Bambu Studio/resources/profiles/BBL/process/0.20mm Standard @BBL A1.json`, `.../filament/Bambu PETG Basic @BBL A1.json`, `.../filament/Bambu PETG Basic @base.json` (bộ profile 02.07.00.07)
- OrcaSlicer wiki, Tolerance Calibration (mẫu 0–0,4 mm): https://www.orcaslicer.com/wiki/calibration/tolerance_calib.html · mẫu: https://github.com/OrcaSlicer/OrcaSlicer/blob/main/resources/handy_models/OrcaToleranceTest.drc
- Ruthex insert, bảng kỹ thuật trên trang đại lý (thứ cấp, chưa đọc được ruthex.de):
  - https://www.3djake.com/ruthex/threaded-insert-m3-100-pieces
  - https://www.3djake.com/ruthex/m2-m3-m4-m5-threaded-insert-assortment-box
- Prusa heat-set inserts (trang sản phẩm, đọc qua trích đoạn tìm kiếm, trang trả 403): https://www.prusa3d.com/product/heat-set-inserts-m3-standard-100-pcs/
- Forum Prusa, lỗ insert (thứ cấp): https://forum.prusa3d.com/forum/prusaslicer/hole-for-heat-set-insert/
- Hubs, How to design parts for FDM (chốt < 5 mm, cầu 5 mm, vát chân 45°): https://www.hubs.com/knowledge-base/how-design-parts-fdm-3d-printing/
- Fasteners WB 0.5.67 [máy]: `%APPDATA%/FreeCAD/v1-1/Mod/fasteners/{FsData/HeatInserts.csv, FsFunctions/FSmakeHeatInsert.py, FS3dpSettings.py, Widget3DPrintSettings.ui, FSScrewCalc.py}` · repo: https://github.com/shaise/FreeCAD_FastenersWB
- Gears WB 1.4.0 [máy]: `%APPDATA%/FreeCAD/v1-1/Mod/freecad.gears/freecad/gears/involutegear.py` · repo: https://github.com/looooo/freecad.gears
- Dự án robot:
  - SO-ARM100 README + CHANGELOG: https://github.com/TheRobotStudio/SO-ARM100
  - Thor: https://github.com/AngelLM/Thor
  - https://github.com/AlexanderKoch-Koch/low_cost_robot
  - https://github.com/BCN3D/BCN3D-Moveo
  - Số sao: GitHub REST API, tra 2026-10-24.
- MakerWorld Parametric Model Maker: tài liệu không chính thức (thứ cấp) https://github.com/nelsonjchen/unofficial-makerworld-parametric-model-maker-openscad-docs · forum Bambu (thứ cấp) https://forum.bambulab.com/t/any-documentation-on-parametric-model-maker/230605
- A1 không có AI phát hiện lỗi (thứ cấp, chưa xác nhận): https://obico.io/blog/tags/ai-spaghetti-detection
