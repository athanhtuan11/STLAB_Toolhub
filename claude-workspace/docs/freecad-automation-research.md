# Nghiên cứu: FreeCAD 1.1 chuyên sâu, code-CAD và tự động hóa (STLab)

Viết 2026-10-23 cho pipeline `maker/robotics-cad/` (dự án mẫu `maker/pushrod-arm/`). Tuan sửa/bổ sung trực tiếp file này.
Nhãn: **[đã chạy]** = Claude đã chạy `freecadcmd` 1.1.4 trên file thử trong thư mục tạm (không đụng FreeCAD đang mở) ·
**[đọc mã]** = đọc mã nguồn bản cài `C:/Program Files/FreeCAD 1.1/Mod/...` · **[chưa kiểm]** = chỉ theo tài liệu.
Số sao GitHub tra bằng GitHub API ngày **2026-10-23**.

> Lưu ý nguồn: wiki.freecad.org đang chặn bot (Anubis) nên không tải được trực tiếp. Trang wiki được đọc qua bản sao
> chính thức [FreeCAD/FreeCAD-documentation](https://github.com/FreeCAD/FreeCAD-documentation) (cập nhật lần cuối
> 2025-01-15 → mục 1.0 đầy đủ, mục 1.1 là **bản nháp trước khi phát hành**). Link trong bài vẫn trỏ về wiki gốc.

## 0. Kết luận nhanh

1. **Assembly tích hợp của 1.1 đã đủ dùng cho STLab**: joint có giới hạn góc/hành trình, Simulation (1.1), BOM, Exploded View.
   Không cần Assembly4/A2plus/ExplodedAssembly cho dự án mới. Simulation **tự trả tư thế cũ khi đóng** → giải
   đúng lỗi "Lưu khi đang mô phỏng" mà `rest.json` đang vá.
2. Model "chết" (Part::Feature + boolean script) là gốc của nhiều việc tay. Hướng chuẩn: mỗi chi tiết in là 1
   **PartDesign Body** điều khiển bằng **VarSet**, sketch gắn mặt phẳng gốc/datum (tránh TopoNaming); lắp bằng Assembly.
3. **CI trên GitHub chưa đáng làm**: `.FCStd` không lên git (GĐ B) → runner GitHub không có model để kiểm. Lợi lớn hơn:
   **file chỉ số hồi quy** (`metrics.json`) + **release cục bộ**.
4. Code-CAD (build123d) mạnh cho chi tiết lặp/biến thể và diff trên git; dùng **song song** được qua STEP → FreeCAD
   Assembly. Không thay FreeCAD cho lắp ráp/linh kiện STEP.
5. **(2026-10-24) Sửa model bằng CLI, GUI chỉ để xem** – nhưng CLI có 4 bẫy làm hỏng dữ liệu âm thầm (mất màu, ẩn hết chi
   tiết, exit 0 khi lỗi, đọc kết quả cũ). Đã có công cụ chặn từng bẫy + test hồi quy – **đọc mục 7 trước khi viết script**.

## 1. FreeCAD 1.1 – tính năng đáng dùng

Mốc phiên bản (GitHub Releases): 1.0.0 ngày 2024-11-19, 1.1.0 ngày 2026-03-25, **1.1.4 ngày 2026-09-28 – bản bảo trì
cuối của dòng 1.1**, có 2 bản vá bảo mật khi mở file FCStd độc hại ([release 1.1.4](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4)).
Bản kế tiếp đổi cách đánh số: **26.3**, đang RC2 (2026-10-18), "một số mặc định và hành vi đã đổi" – đừng dùng RC cho
việc thật ([26.3rc2](https://github.com/FreeCAD/FreeCAD/releases/tag/26.3rc2)). Ghi chú phát hành 26.3: TODO (chưa đọc được).

### 1.1 Assembly workbench + solver

| Tính năng | Từ bản | Ghi chú cho STLab | Trạng thái |
|---|---|---|---|
| Workbench tích hợp, solver mã nguồn mở Ondsel | 1.0 | [RN 1.0](https://wiki.freecad.org/Release_notes_1.0), [OndselSolver](https://github.com/Ondsel-Development/OndselSolver) | – |
| Joint: Fixed, Revolute, Cylindrical, Slider, Ball, Distance, Parallel, Perpendicular, Angle, RackPinion, Screw, Gears, Belt; Revolute có `AngleMin/Max`, Slider `LengthMin/Max` | 1.0–1.1 | đủ cho servo, thanh răng–bánh răng, trục vít của pushrod-arm | [đọc mã] `JointObject.py` (xem `kiem-tra-model.md` 3.1) |
| Sub-assembly cứng / mềm (flexible) | 1.0 | chia cụm (Base, Turret, Gripper…) | [chưa kiểm] [RN 1.0](https://wiki.freecad.org/Release_notes_1.0) |
| **Simulation** (Motion theo `time`) | 1.1 | động học, không có lực | [đọc mã] [PR #16414](https://github.com/FreeCAD/FreeCAD/pull/16414) |
| Simulation lưu tư thế đầu và **trả lại khi đóng task panel** (`saveAssemblyPartsPlacements` → `restoreAssemblyPartsPlacements`) | 1.1 | thay macro `_sim.FCMacro` + `rest.json` | [đọc mã] `CommandCreateSimulation.py` dòng 779, 862 |
| Core Datum (hệ tọa độ, mặt, trục, điểm) gắn được và dùng làm chỗ đặt joint | 1.1 | gắn joint vào datum thay vì mặt STEP lỗi | [chưa kiểm] [PR #18332](https://github.com/FreeCAD/FreeCAD/pull/18332) |
| Insert New Part | 1.1 | tạo chi tiết mới ngay trong lắp ráp | [chưa kiểm] [PR #17922](https://github.com/FreeCAD/FreeCAD/pull/17922) |
| **BOM** (`Assembly::BomObject`, là Spreadsheet) | 1.0; 1.1 thêm cột thuộc tính | đếm Link theo chi tiết | **[đã chạy]** headless, xem 1.6 |
| **Exploded View** (các Move, tham số, mở lại sửa được); TechDraw vẽ được từ exploded view | 1.0 | ảnh/bản vẽ hướng dẫn lắp | [chưa kiểm] [Assembly CreateView](https://wiki.freecad.org/Assembly_CreateView) |
| Lệnh kiểm giao thoa/va chạm | – | **không có** → giữ `check.py` (manifold3d) | [đọc mã] (`kiem-tra-model.md` 3.1) |

- Joint chỉ cần tham chiếu mặt/cạnh/đỉnh, **không làm boolean** → STEP linh kiện lỗi BOP (servo/N20 CyberBrick) vẫn
  lắp được. Chỉ boolean (khoét hốc) mới hỏng → dùng khối "dao cắt" đơn giản (đã là quy ước).
- Tư thế gốc trong Assembly = giá trị joint (`Offset`, góc). Mở file → `asm.solve()` là về đúng tư thế, không cần
  `rest.json`. Quét khớp headless qua `j.Offset2` + `asm.solve()` đã chạy được (`kiem-tra-model.md` 3.2).
- `AssemblyObject` có sẵn `generateSimulation`, `numberOfFrames`, `updateForFrame`, `undoSolve`, `exportAsASMT` **[đã chạy:
  có trong `dir()`]** → có thể chạy mô phỏng không cần GUI, nhưng lớp Python tạo đối tượng Simulation nằm trong
  `CommandCreateSimulation.py` cần Qt (import lỗi `QtCore` trong freecadcmd) → **chạy headless: chưa kiểm**.

### 1.2 Tham số hóa: VarSet / Spreadsheet / Expressions

| | VarSet (`App::VarSet`, 1.0) | Spreadsheet | Expressions |
|---|---|---|---|
| Là gì | nhóm thuộc tính có đơn vị, dùng như biến ([Std VarSet](https://wiki.freecad.org/Std_VarSet), [PR #12135](https://github.com/FreeCAD/FreeCAD/pull/12135)) | bảng có alias | công thức trên mọi thuộc tính ([Expressions](https://wiki.freecad.org/Expressions)); 1.0 thêm hàm Vector |
| Hợp với | tham số thiết kế (khe 0,2 mm, đường kính chốt, bề dày thành) | bảng cấu hình/biến thể, xem trong TechDraw | nối tham số → kích thước |
| Script | `vs.addProperty("App::PropertyLength","Width","Dim")` | `sheet.set('A1',…)`, `setAlias` | `obj.setExpression("Length","Params.Width")` |

**[đã chạy]** VarSet `Width` → `AdditiveBox.Length` qua expression: thể tích Body 1 000 mm³ (20×10×5 mm), đổi `Width`=30 mm →
1 500 mm³ sau `recompute()`. Khuyến nghị: **1 VarSet `Params` ở tài liệu lắp ráp** cho khe hở/chốt/vít dùng chung,
Spreadsheet chỉ khi cần bảng biến thể.

### 1.3 PartDesign vs Part, TopoNaming

| | Part::Feature (đang dùng ở pushrod_arm) | PartDesign Body |
|---|---|---|
| Lịch sử tham số | không (hình "chết", sửa bằng boolean script) | có (Sketch → Pad/Pocket/Fillet…) |
| Sửa 1 kích thước | viết lại script boolean, dễ hỏng âm thầm | đổi VarSet → recompute |
| Một chi tiết in = | 1 Shape, có thể nhiều solid | 1 Body = 1 solid (khớp `export-stl.py` theo Label) |
| Rủi ro | boolean với STEP lỗi | TopoNaming khi sketch gắn lên mặt |

- 1.0 đưa vào mã giảm TopoNaming của realthunder, nhưng **"chưa giải quyết hoàn toàn"** ([RN 1.0](https://wiki.freecad.org/Release_notes_1.0),
  [PR #13705](https://github.com/FreeCAD/FreeCAD/pull/13705)). Cách chuẩn: gắn sketch vào **mặt phẳng gốc của Body hoặc datum
  plane** gắn với mặt phẳng gốc, không gắn vào mặt của Pad ([Topological naming problem](https://wiki.freecad.org/Topological_naming_problem),
  [Feature editing](https://wiki.freecad.org/Feature_editing)). **[đã chạy]** Shape có `ElementMapVersion` = `15.70200.5` (bản đồ tên phần tử đang bật).
- 1.0 đổi `Support` → `AttachmentSupport`; file Assembly4 mở ở bản cũ cần macro sửa ([RN 1.0](https://wiki.freecad.org/Release_notes_1.0)).

### 1.4 TechDraw (bản vẽ, BOM, exploded)
- Có Insert Spreadsheet View (đưa BOM lên bản vẽ), Balloon, vẽ từ Exploded View ([TechDraw](https://wiki.freecad.org/TechDraw_Workbench),
  [Assembly CreateView](https://wiki.freecad.org/Assembly_CreateView)).
- **[đã chạy]** headless: `DrawPage` + `DrawViewPart` tính được cạnh thấy (4 cạnh cho hình chiếu bằng hộp);
  `TechDraw.writeDXFPage()` ghi DXF được; module `TechDraw` **không có** hàm ghi SVG cả trang (chỉ `exportSVGEdges`);
  xuất PDF trang cần GUI → **chưa kiểm**.
- Với STLab (in 3D, không gia công): bản vẽ kích thước ít cần; giá trị chính là **trang lắp ráp có BOM + balloon** – nhưng
  `ASSEMBLY.md` → PDF hiện tại đã làm việc đó, nên TechDraw **ưu tiên thấp**.

### 1.5 Python API headless (FreeCADCmd)
- `freecadcmd script.py --pass args`; không tạo được ViewProvider; chỉ dựng được scenegraph bằng `Gui.setupWithoutGUI()`
  ([Headless FreeCAD](https://wiki.freecad.org/Headless_FreeCAD)). Đã dùng ổn ở `check.py`/`export-stl.py`.
- **[đã chạy]** trong freecadcmd 1.1.4: `import UtilsAssembly, JointObject, CommandCreateJoint, CommandExportASMT` OK;
  `CommandCreateBom`, `CommandCreateView`, `CommandCreateSimulation` lỗi `NameError: QtCore` (mã GUI). ⇒ BOM tạo trực tiếp
  bằng `Assembly::BomObject`; Exploded View/Simulation tạo trong GUI rồi Lưu.
- **[đã chạy]** `Import.export([body], "x.step")` → `Part.read()` đọc lại đúng thể tích (1 500 mm³).
- **[đã chạy]** boolean "fuzzy": `a.cut([b], 0.01)` chạy được (dung sai 0,01 mm; cùng thể tích 6 429,20 mm³ trên ca
  sạch). Có thể thử cho STEP lỗi BOP – **hiệu quả trên servo/N20: chưa kiểm**. `Part.ShapeFix.Shape(s).perform()` có sẵn.
- Phát hiện boolean thất bại âm thầm: sau mỗi cut kiểm `isValid()`, số solid, và **ΔV ≈ thể tích dao ∩ chi tiết**
  (tính bằng `common`) – lệch > vài % thì dừng. (Đề xuất, chưa viết.)

### 1.6 BOM headless – kết quả thử **[đã chạy]**
```python
asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
l1 = asm.newObject("App::Link", "L1"); l1.LinkedObject = body   # 2 Link cùng 1 Body
bom = UtilsAssembly.getBomGroup(asm).newObject("Assembly::BomObject", "BOM")
bom.columnsNames = ["Index", "Name", "Quantity", "File Name"]   # mặc định chỉ có "Index"
doc.recompute()   # A2..D2 = 1 | Body | 2 | <đường dẫn FCStd>
```
- Thuộc tính: `columnsNames`, `detailParts`, `detailSubAssemblies`, `onlyParts`. Cột Index/Name/File Name/Quantity tự sinh;
  cột "Description" và cột riêng không bị ghi đè (`CommandCreateBom.py` dòng 75 **[đọc mã]**).
- BOM chỉ có ý nghĩa khi chi tiết lặp là **App::Link** của 1 nguồn (vd. 6 chốt `Pin_*` = 1 Body × 6). pushrod_arm hiện là
  các Part::Feature riêng → BOM sẽ đếm mỗi cái 1.

### 1.7 Addon (đã có trong Mod: fasteners, SheetMetal, gears, robotcad, LCInterlocking, FreeCADMCP)

| Addon | Sao / cập nhật (2026-10-23) | Kết luận |
|---|---|---|
| Assembly4 | gốc đã dời sang Codeberg [Zolko/Assembly4](https://codeberg.org/Zolko/Assembly4) (3★ Codeberg); bản fork [leoheck/FreeCAD_Assembly4.1](https://github.com/leoheck/FreeCAD_Assembly4.1) 23★ | **Không cần** – Assembly tích hợp thay thế |
| [A2plus](https://github.com/kbwbe/A2plus) | 206★, đẩy lần cuối 2026-02-15 | **Không cần** |
| [Assembly3](https://github.com/realthunder/FreeCAD_assembly3) | 904★, 2025-11-08 | Không cần |
| [Fasteners](https://github.com/shaise/FreeCAD_FastenersWB) | 424★, 2026-09-10; bản cài 0.5.67 | **Dùng** cho vít/đai ốc: có lệnh **Generate BOM** ra Spreadsheet `Fasteners_BOM` ([đọc mã] `FastenerBase.py` dòng 1047–1066) |
| BOLTS | repo chính đã thành [BOLTS_archive](https://github.com/boltsparts/BOLTS_archive) (2023-05); [boltsfc](https://github.com/boltsparts/boltsfc) 41★, 2024-02 | Bỏ – Fasteners đủ |
| [ExplodedAssembly](https://github.com/JMG1/ExplodedAssembly) | 141★, 2024-02 | Bỏ – Exploded View tích hợp |
| [Render](https://github.com/FreeCAD/FreeCAD-render) | 239★; **tác giả ngừng bảo trì từ 2025-11-12** (README), cần renderer ngoài | Bỏ – render bằng Blender (đã có hướng FreeCAD → Blender) |
| [Cables](https://github.com/sargo-devel/Cables) | 103★, 2026-10-23 | **Đáng thử** cho đấu dây (đi dây, chiều dài dây) – chưa thử |
| [RobotCAD](https://github.com/drfenixion/freecad.robotcad) | 455★, 2026-10-06 | giữ (URDF); đọc được joint Assembly (`kiem-tra-model.md` 3.3) |

Danh mục addon: [FreeCAD/FreeCAD-addons `.gitmodules`](https://github.com/FreeCAD/FreeCAD-addons/blob/master/.gitmodules);
Addon Manager tách repo riêng [FreeCAD/AddonManager](https://github.com/FreeCAD/AddonManager).

## 2. Code-CAD so với FreeCAD (robot nhỏ in 3D)

| | FreeCAD 1.1 (GUI + Python) | [CadQuery](https://github.com/CadQuery/cadquery) | [build123d](https://github.com/gumyr/build123d) | [OpenSCAD](https://github.com/openscad/openscad) |
|---|---|---|---|---|
| Sao GitHub (2026-10-23) | 34 691 | 5 982 | 3 504 | 10 490 |
| Bản mới | 1.1.4 (2026-09-28) | 2.8.0 PyPI (2026-06-21) | 0.13.0 PyPI (2026-09-21) | ổn định **2021.01**; sau đó chỉ nightly ([releases](https://github.com/openscad/openscad/releases)) |
| Nhân | OpenCASCADE (B-rep) | OCCT (B-rep) | OCCT (B-rep) | CSG lưới |
| Xuất | STEP, STL, 3MF… | STEP (cả assembly), XML OCCT ([assy](https://cadquery.readthedocs.io/en/latest/assy.html)) | STEP có màu + nhãn, STL, 3MF, BREP, DXF, SVG, glTF ([import/export](https://build123d.readthedocs.io/en/latest/import_export.html)) | STL, OFF, AMF, 3MF, DXF, SVG… **không STEP** ([manual](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/STL_Import_and_Export)) |
| Lắp ráp | Assembly + solver, mô phỏng, BOM | constraint + `solve()` | joints (chưa đọc kỹ – TODO) | không |
| Diff trên git | FCStd nhị phân | file .py | file .py | file .scad |
| Linh kiện STEP | chèn trực tiếp | import STEP | `import_step()` → Compound | không (chỉ STL) |
| Người học STLab | dễ (GUI) | cần Python | cần Python | dễ nhất cho học sinh |

**Khuyến nghị:** giữ FreeCAD làm **tài liệu lắp ráp** (linh kiện STEP, joint, mô phỏng, BOM); chi tiết **lặp/biến thể**
(gá servo theo kích thước, bánh răng, chốt, spacer) viết **build123d** → STEP → chèn vào FreeCAD.
- Đánh đổi: thêm 1 môi trường Python (build123d 0.13.0 khai `requires_python >=3.11,<3.15` trên PyPI) – **cài riêng**, không vào Python FreeCAD;
  2 nguồn sự thật (script + FCStd) → phải quy ước "STEP sinh ra là file sinh, sửa ở script".
- build123d hơn CadQuery: Apache-2.0, cú pháp Python thuần (builder/algebra), STEP giữ màu + tên ([docs](https://build123d.readthedocs.io/en/latest/import_export.html)).
  Xem trực tiếp trong VS Code bằng [ocp-vscode](https://github.com/bernhard-42/vscode-ocp-cad-viewer) (418★).
- OpenSCAD: không có STEP, bản ổn định 2021 → chỉ hợp cho bài học nhập môn, **không** cho pipeline.
- **Chưa kiểm** trên máy: build123d → STEP → FreeCAD 1.1 giữ tên/màu; Assembly joint trên STEP nhập (mặt có ổn định khi xuất lại không).

## 3. Tự động hóa

### 3.1 CI / GitHub Actions
- **Ràng buộc chính:** `.FCStd` chỉ trên máy (Tuan chốt GĐ B) ⇒ runner GitHub **không có model**. CI chỉ chạy được trên
  (a) self-hosted runner = máy này, hoặc (b) phần sinh từ mã (build123d) nằm trong git.
- FreeCAD có AppImage Linux x86_64 (782 MB) ở mỗi release ([1.1.4 assets](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4)); chạy
  `freecadcmd` từ AppImage trên runner: **chưa kiểm**. Bambu Studio có AppImage Ubuntu 22/24 ([v02.08.04.57](https://github.com/bambulab/BambuStudio/releases)) –
  slicer CLI trên Linux headless có thể cần `xvfb` (đã ghi ở `quy-trinh-chuan-hoa-cad.md`), **chưa kiểm**.
- [FCBot](https://github.com/asymworks/FCBot): 3★, đẩy lần cuối 2025-03-09, chỉ hỗ trợ FreeCAD 1.0 (Debian, Python 3.13), xuất step/stl/screenshot/pdf
  theo YAML, có GitHub Action mẫu chạy theo tag `rev_*`. ⇒ **Chỉ lấy mẫu thiết kế**, không dùng (cũ, ít người dùng, STLab đã có `print.yaml` mạnh hơn).
- Bambu Studio CLI: `--slice 0` (mọi bàn), `--export-3mf`, `--load-settings "máy;process"`, `--arrange`, `--orient`, `--outputdir`;
  thứ tự ưu tiên: `--key=value` > file settings > giá trị trong 3MF ([wiki CLI](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)).
  OrcaSlicer: 16 087★, ổn định v2.4.2 (2026-07-07) ([releases](https://github.com/OrcaSlicer/OrcaSlicer/releases)) – không cần đổi, A1 dùng profile Bambu.
- Máy đang dùng Bambu Studio 02.07, mới nhất 02.08.04.57 (2026-09-22). Lên bản: chạy lại `slice.py` pushrod-arm so số giờ/gam trước khi đổi.

### 3.2 Kiểm thử hồi quy model (đề xuất – rẻ, lợi lớn)
- `check.py` đã có hộp bao mỗi chi tiết trong `report.json`, nhưng thư mục `check/` bị `.gitignore` → **không so được qua thời gian**.
- Đề xuất `freecad/metrics.json` (**lên git**, vài chục KB): mỗi Label → thể tích (mm³, làm tròn 0,1), hộp bao (mm, 0,01),
  trọng tâm, số solid; + mỗi bàn in → thời gian, gam (từ `print-report.json`). Lần chạy sau so với bản HEAD:
  chi tiết **không được sửa** mà đổi thể tích/hộp bao → WARN (bắt boolean hỏng âm thầm, chi tiết bị dời khi Lưu lúc mô phỏng).
  `git diff metrics.json` = changelog hình học cho Release.
- Bọc thành `unittest` chạy `freecadcmd -t` (exit code 1 khi FAIL – đã thử, `kiem-tra-model.md` 7.1).

### 3.3 Release artifact (GĐ C)
- Làm **cục bộ** (script `release.py`): khi `prepare-print` PASS và Tuan duyệt ảnh → tag `<project>-vX.Y`, đính 3MF từng bàn,
  `print-overview.png`, `ASSEMBLY.pdf`, `BOM.csv`, STEP chi tiết in, changelog từ diff `metrics.json`.
- Máy hiện **không có `gh` CLI** (Git Bash báo `gh: command not found`) → cần cài, hoặc dùng GitHub API + token trong biến môi trường.

### 3.4 Tự sinh BOM / hướng dẫn lắp / exploded
- **BOM**: quy ước Label đã có (`CB_`, `LK_`, `M2_5x6`, `_TPU`) → script đọc Label + thể tích × mật độ (`thresholds.yaml`) ra
  `BOM.csv`: linh kiện mua, vít (đếm theo cỡ), chi tiết in (gam). Dán bảng vít vào `ASSEMBLY.md` thay vì đếm tay.
  Khi dùng Link/Fasteners thì thay bằng `Assembly::BomObject` / Fasteners BOM.
- **Hướng dẫn lắp**: giữ `render_assembly.py` + `assembly-pdf.py`; khi có Assembly, thứ tự bước lấy từ cây sub-assembly,
  ảnh nổ từ Exploded View (GUI). Render đẹp: Blender (Render WB ngừng bảo trì).
- **Đấu dây**: Cables addon (chưa thử) hoặc bảng nối dây tay trong README – TODO Tuan chọn.

## 4. Đề xuất cho pipeline hiện tại (xếp theo lợi/công)

Công: 1 buổi ≈ 3–4 giờ làm cùng Claude (ước lượng, chưa đo).

| # | Việc | Lợi | Công | Đánh đổi | Ai quyết |
|---|---|---|---|---|---|
| 1 | `metrics.json` hồi quy (thể tích/hộp bao/trọng tâm + giờ/gam bàn in), lên git, so với HEAD | bắt lỗi âm thầm; changelog tự có | 0,5–1 buổi | thêm 1 file sinh vào git | Claude làm được |
| 2 | `safe_cut()` cho script sửa model: kiểm `isValid`, số solid, ΔV kỳ vọng; thử `cut(…, tol)` fuzzy với STEP lỗi | hết boolean hỏng âm thầm | 0,5–1 buổi | chậm hơn chút mỗi lần cut | Claude làm được |
| 3 | `bom.py`: BOM.csv từ Label + bảng vít cho `ASSEMBLY.md` | bỏ đếm tay | 1 buổi | phụ thuộc quy ước đặt tên | Claude làm được |
| 4 | GĐ C: `release.py` cục bộ (tag + file đính + changelog từ metrics) | bản in có phiên bản, chia sẻ dễ | 1–1,5 buổi | cần `gh` hoặc token; đẩy ra GitHub | **Tuan** (public/private repo, cài `gh`) |
| 5 | Thí điểm chuẩn mới cho dự án/cụm mới: PartDesign Body + VarSet `Params` + Assembly joints (thay `rest.json`, `_sim.FCMacro`) | sửa kích thước không cần script; mô phỏng chuẩn, hết lỗi Lưu-khi-mô-phỏng | 2–3 buổi (1 cụm, vd. Gripper) | học lại cách dựng; `check.py`/`export-stl.py` phải đọc Body/Link | **Tuan** |
| 6 | build123d cho chi tiết lặp (gá servo/N20, chốt, spacer) → STEP | diff/review trên git, biến thể nhanh | 1 buổi cài + 1 buổi/chi tiết mẫu | thêm môi trường Python; 2 nguồn sự thật | **Tuan** |
| 7 | Joint trên datum (Core Datum 1.1) cho linh kiện STEP lỗi | joint ổn định khi đổi STEP | trong #5 | – | – |
| 8 | Cables addon cho đấu dây | dây có chiều dài, vào BOM | 1 buổi thử | addon cộng đồng, cần ghim + đọc mã (COMMUNITY.md) | **Tuan** |
| 9 | GitHub Actions | nhiều người cùng sửa | 2+ buổi (self-hosted runner) | FCStd không trên git → giá trị thấp lúc này | Hoãn |
| 10 | TechDraw bản vẽ | bản vẽ kỹ thuật | 1 buổi | `ASSEMBLY.pdf` đã đủ cho in 3D | Hoãn |
| 11 | Lên FreeCAD 26.3 | tính năng mới | ? | RC, đổi mặc định; addon/RobotCAD có thể lỗi | Chờ bản chính thức + Tuan |

**Không nên:** chuyển pushrod_arm hiện có sang PartDesign toàn bộ (85 chi tiết, sắp in thật) – chỉ áp chuẩn mới cho chi tiết
phải sửa lại sau lần in thử.

## 5. Top 5 việc nên làm tiếp

| # | Việc | Lợi | Công | Rủi ro |
|---|---|---|---|---|
| 1 | **`metrics.json` hồi quy** trong `check.py`/`prepare-print.py` | thấy ngay chi tiết đổi ngoài ý muốn; changelog cho Release | 0,5–1 buổi | ngưỡng so (0,1 mm³ / 0,01 mm) có thể báo nhiễu do lưới → so trên B-rep, làm tròn |
| 2 | **`safe_cut()`** + thử boolean fuzzy trên STEP servo/N20 | hết lỗi boolean âm thầm | 0,5–1 buổi | fuzzy có thể không cứu được STEP hỏng nặng → vẫn dùng dao cắt đơn giản |
| 3 | **`bom.py`** → `BOM.csv` + bảng vít `ASSEMBLY.md` | bỏ đếm tay, BOM khớp model | 1 buổi | Label đặt sai → BOM sai; thêm kiểm "Label không theo quy ước" |
| 4 | **GĐ C `release.py`** (cục bộ) | bản in có phiên bản, gửi người khác in lại được | 1–1,5 buổi | đẩy file ra ngoài – **Tuan quyết** repo/visibility, cài `gh` |
| 5 | **Thí điểm Body + VarSet + Assembly** cho 1 cụm mới (vd. Gripper v2) | dựng lại bằng tham số, mô phỏng chuẩn, bỏ `rest.json` | 2–3 buổi | thời gian học; phải cập nhật `check.py`/`export-stl.py` cho Link/Body – **Tuan quyết** |

## 6. Thử nghiệm đã chạy (2026-10-23, freecadcmd 1.1.4, file thử trong thư mục tạm của phiên)
- VarSet + expression + PartDesign Body: 1 000 → 1 500 mm³ khi đổi tham số. `ElementMapVersion` = `15.70200.5`.
- `Assembly::BomObject` headless: 2 Link → `Body`, Quantity 2 (sau khi đặt `columnsNames`).
- Import headless: `CommandCreateBom/View/Simulation` lỗi `QtCore`; `UtilsAssembly`, `JointObject`, `CommandExportASMT` OK.
- TechDraw headless: DXF trang OK; không có hàm SVG trang; PDF chưa kiểm.
- STEP xuất/đọc lại đúng thể tích; `cut([b], 0.01)` chạy được.
- Không gửi lệnh nào vào FreeCAD đang mở (cổng 9875).

## 7. Chạy FreeCAD bằng dòng lệnh – kinh nghiệm đã kiểm (2026-10-24, FreeCAD 1.1.4)

Bối cảnh: Tuan "mở FreeCAD dễ bị crash" → chuyển sang CLI; làm lại xi-lanh pushrod-arm (motor 030) hoàn toàn bằng CLI.
Mọi số đo dưới đây chạy trên máy STLab (Windows 11), model `pushrod_arm.FCStd` 96 object, ~8 MB.

### 7.1 Các cách chạy – dùng cái nào

| Cách | Lệnh | Dùng khi | Ghi chú |
|---|---|---|---|
| CLI chuẩn | `FreeCADCmd.exe --safe-mode maker/robotics-cad/scripts/fc_cli.py --pass <script.py> [args]` | **mọi script sửa/đo model** | traceback đầy đủ + exit 1 khi lỗi **[đã chạy]** |
| CLI trần | `FreeCADCmd.exe script.py --pass a b` | tránh | lỗi vẫn **exit 0** **[đã chạy]**; `sys.argv` giữ nguyên cả `--pass a b` |
| Python thường | `"…/bin/python.exe" x.py` với `import FreeCAD` | điều phối (prepare-print), exit code đúng | nạp addon như GUI |
| GUI riêng, tự thoát | `set FC_FILE/FC_SCRIPT` → `FreeCAD.exe --safe-mode maker/robotics-cad/scripts/gui_run.py` | **render ảnh** (`saveImage`), cần ViewObject | không đụng phiên GUI của Tuan; 26 ảnh lắp ráp 18 s **[đã chạy]** |
| RPC vào GUI đang mở | cổng 9875 `execute_code` | chỉ lệnh **nhẹ** (mở file, hỏi trạng thái) | việc nặng → `GUI_DISPATCH_STUCK` sau 90 s, GUI treo > 2 phút **[đã chạy]** |
| Bộ test | `FreeCADCmd.exe --safe-mode -P <thư mục test> -t <module>` | kiểm yêu cầu thiết kế | unittest; **exit 1 khi có test trượt** **[đã chạy]** |

`--safe-mode`: không nạp addon (ROS, laser-cut, RobotCAD…) → khởi động 1,1 → 0,4 s **[đã chạy]**. Mở FCStd 8 MB: 1,4 s.
Tùy chọn khác (`FreeCADCmd --help`): `-l/--log-file`, `-u` user config, `-M/-E/-P` thêm đường dẫn, `--disable-addon`,
`-t/-r` chạy test (`-r` giữ UI mở). GUI hay crash → thử `FreeCAD.exe --safe-mode -l`: hết crash = lỗi do addon.

### 7.2 Bẫy đã dính và cách chặn

| # | Triệu chứng | Nguyên nhân | Chặn bằng |
|---|---|---|---|
| 1 | Script lỗi nhưng quy trình chạy tiếp; có lần thông báo lỗi **sai** (báo `guard` trong khi lỗi thật là `AttributeError`) | `freecadcmd` bắt exception, in 1 dòng, **exit 0** | `fc_cli.py`; điều phối không tin exit code |
| 2 | Quy trình dùng **STL/kết quả cũ** khi script con hỏng | file JSON của lần trước vẫn còn | `prepare-print.py: doc_moi()` chỉ nhận file ghi sau lúc chạy; `metrics.json` không ghi lại khi không đổi → kiểm dòng `METRICS` trong log |
| 3 | Mở trong GUI mất màu, ẩn/hiện, thumbnail | lưu từ CLI **bỏ** `GuiDocument.xml` + `*ColorArray*`, `ShapeAppearance*` (365 → 108 file trong zip; hình học nguyên) | `safe_edit.save(doc, gui_from=backup)` chép lại |
| 4 | Cách chặn #3 không chép được gì | `doc.saveCopy()` trong CLI **cũng** bỏ GUI → backup rỗng phần hiển thị | `safe_edit.backup()` ở CLI = **chép file trên đĩa** (sau `guard`, UndoCount 0) |
| 5 | BOM còn 6 vít thay 21, metrics báo "đã xóa" Pin_A…E, Boom… | file lưu CLI (không GuiDocument) mở trong GUI → **ẩn 85/85 chi tiết** (cả `obj.Visibility` App) **[đã chạy]**; GUI Lưu → ẩn ghi vào file; `check/metrics/bom/export` **bỏ qua chi tiết ẩn** | test `T0File.test_no_hidden_parts` + `test_gui_data_kept`; script `history/2026-10-24_unhide_parts.py` sửa cả App lẫn `GuiDocument.xml` |
| 6 | Object lệch vị trí trong mô phỏng / guard báo "không ở tư thế gốc" | `shape.transformShape(M)` với ma trận cứng chỉ gán **Placement của shape**; gán `obj.Shape = s` → FreeCAD đẩy Placement đó sang `obj.Placement` | bọc `Part.makeCompound([s])` (giữ obj.Placement) hoặc `transformGeometry` (nướng hình, có thể ra BSpline) |
| 7 | `isIdentity()` sai với Placement "bằng 0" | nhiễu số 2e-13 từ file | `pl.isSame(App.Placement(), 1e-6)` |
| 8 | `AttributeError: 'Part.Vertex' object has no attribute 'x'` | Vertex dùng `.X/.Y/.Z`, Vector dùng `.x/.y/.z` | – |
| 9 | Báo chồng giả 154 mm³ (trục vít ~ hộp số) | STEP linh kiện lưới hở → bao lồi **cả cụm** (bánh răng r6 + trục Ø5,3) phình to | chia lưới **từng solid**, chỉ solid hở mới bao lồi (`fast_collide._manifold`, dùng chung cho `check.py`) |
| 10 | Kết quả đo mặt vát = bán kính (lỗ tròn trơn, không truyền mô-men) | đo cả gờ tròn 0,1 mm ở chân trục | đo từ 0,5 mm khỏi mặt; test `test_worm_socket_drives` |
| 11 | `manifold3d.min_gap(…, 50)` trả sai / treo | bán kính tìm quá lớn | giữ ≤ 20 mm, xa hơn dùng `distToShape` |

### 7.3 Hiệu năng (đo thật)

| Thao tác | Thời gian | Ghi chú |
|---|---|---|
| `distToShape` B-rep | 0,2–12,2 s/cặp | STEP linh kiện chậm nhất; `tol` (= deflection `BRepExtrema_DistShapeShape`, **đã đa luồng** trong mã) nới ra **không nhanh hơn** (0,94 → 3,67 s) |
| `common` B-rep | 0,08–3,2 s/cặp | mỗi boolean FreeCAD còn chạy `BRepCheck_Analyzer` cho **cả 2 khối**, `SetRunParallel(True)`, auto-fuzzy = 1,0 × đường chéo × `Precision::Confusion` **[đọc mã]** |
| manifold3d (giao khối / min_gap) | 1–4 ms / 10–100 ms | sau khi chia lưới 1 lần (0,15–2 s/chi tiết) |
| `Shape.proximity(s, tol)` (OCC BVH) | 6–170 ms sau `tessellate()` | **phải tessellate trước**; chỉ trả cặp mặt gần, không thể tích/khe; **ném lỗi khi không có cặp nào**, 1 lần 33 s → chỉ làm lọc thô |
| Quét 24 tư thế + 6 góc kẹp | **16 s** (lưới) vs **395 s** (B-rep) | kết quả trùng 100 % |
| Bộ test 12 yêu cầu pushrod-arm | 32 s | |
| prepare-print (kiểm + xuất + cắt lớp 7 bàn) | 61 s | |

### 7.4 Kiểm thử thiết kế bằng bộ test của FreeCAD (đề xuất mục 3.2 → đã làm)
- Mỗi yêu cầu của Tuan = 1 test, ghi ngày + câu gốc trong docstring (`maker/pushrod-arm/freecad/tests/test_pushrod_arm.py`).
- Viết test **trước** khi sửa model (đỏ) → sửa đến khi xanh; sửa sau này chạy lại → biết ngay hỏng yêu cầu nào.
- Test hữu ích: khe ≥ 0,3 (lưới), không chồng, đồng trục (vector), "lỗ có mặt vát" (`isInside` theo vòng tròn), có
  dấu khắc (thuộc tính `STLab_Marks`), kết quả mô phỏng **mới hơn** model (so `mtime`), file còn GUI, không chi tiết ẩn.
- Test hỏng vì **test sai** cũng gặp (chiều cao bộ thu lấy từ STL 21,5 thay vì STEP 22,6) → sửa test kèm ghi lý do.

### 7.5 API có sẵn trong 1.1.4 đáng nhớ **[đã chạy]**
- `Part.Shape`: `check`, `fix`, `fixTolerance`, `cleaned`, `defeaturing`, `generalFuse`, `multiFuse`, `makeOffsetShape`,
  `proximity`, `isInside(p, tol, onFaceIsInside)`, `slice/slices`, `tessellate`, `transformGeometry`, `removeSplitter`.
- Khắc chữ/số: `Part.makeWireString(text, "C:/Windows/Fonts/arialbd.ttf", size, 0)` → mỗi ký tự là list wire (wire ngoài +
  lỗ) → `Part.Face` → extrude → `cut`. Kiểm vùng đặt chữ phẳng/đặc trước (lưới `isInside`) – lần đầu đặt trúng bậc.
- `MeshPart.meshFromShape(Shape, LinearDeflection, AngularDeflection)`; `Test.runTestsFromModule/Class`.
- `App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/Boolean")` rỗng = dùng mặc định trong mã.
- `FreeCADGui.setupWithoutGUI()` (trong freecadcmd): tạo `Gui::Application(false)` + Coin3D, **không** có `getDocument`/
  ViewProvider → không giữ màu, không render được **[đã chạy + đọc mã `src/Gui/ApplicationPy.cpp`]**.

### 7.6 Chưa kiểm / TODO
- Assembly Simulation (1.1) chạy headless để thay macro `rest.json` – import `CommandCreateSimulation` lỗi QtCore ở CLI;
  thử qua `gui_run.py`: TODO.
- TechDraw xuất PDF qua `gui_run.py`: TODO. Ghi chú phát hành 26.3: TODO.
- Vì sao chi tiết pushrod-arm bị ẩn trước 2026-10-24: giả thuyết = file từng được lưu từ script headless
  (`history/2026-10-22_*`) rồi mở + Lưu trong GUI (khớp bẫy #5) – chưa tái hiện từng bước.

## 8. Nguồn
- FreeCAD releases (ngày phát hành, 1.1.4, 26.3rc2, asset AppImage): https://github.com/FreeCAD/FreeCAD/releases ·
  https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4 · https://github.com/FreeCAD/FreeCAD/releases/tag/26.3rc2
- Release notes 1.0: https://wiki.freecad.org/Release_notes_1.0 (đọc qua bản sao https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Release_notes_1.0.md)
- Release notes 1.1: https://wiki.freecad.org/Release_notes_1.1 (bản sao nháp: https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Release_notes_1.1.md)
- Assembly Workbench: https://wiki.freecad.org/Assembly_Workbench · CreateView: https://wiki.freecad.org/Assembly_CreateView ·
  CreateBom: https://wiki.freecad.org/Assembly_CreateBom · CreateSimulation: https://wiki.freecad.org/Assembly_CreateSimulation
- PR: TNP #13705 https://github.com/FreeCAD/FreeCAD/pull/13705 · VarSet #12135 https://github.com/FreeCAD/FreeCAD/pull/12135 ·
  Simulation #16414 https://github.com/FreeCAD/FreeCAD/pull/16414 · Core Datum #18332 https://github.com/FreeCAD/FreeCAD/pull/18332 ·
  Insert New Part #17922 https://github.com/FreeCAD/FreeCAD/pull/17922
- OndselSolver: https://github.com/Ondsel-Development/OndselSolver
- Std VarSet: https://wiki.freecad.org/Std_VarSet · Expressions: https://wiki.freecad.org/Expressions
- Topological naming problem: https://wiki.freecad.org/Topological_naming_problem · Feature editing: https://wiki.freecad.org/Feature_editing
- TechDraw: https://wiki.freecad.org/TechDraw_Workbench · Headless FreeCAD: https://wiki.freecad.org/Headless_FreeCAD
- Mã nguồn bản cài: `C:/Program Files/FreeCAD 1.1/Mod/Assembly/{CommandCreateBom.py, CommandCreateView.py, CommandCreateSimulation.py, UtilsAssembly.py}`;
  Fasteners `%APPDATA%/FreeCAD/v1-1/Mod/fasteners/FastenerBase.py`
- Danh mục addon: https://github.com/FreeCAD/FreeCAD-addons/blob/master/.gitmodules · Addon Manager: https://github.com/FreeCAD/AddonManager
- Addon: https://codeberg.org/Zolko/Assembly4 · https://github.com/leoheck/FreeCAD_Assembly4.1 · https://github.com/kbwbe/A2plus ·
  https://github.com/realthunder/FreeCAD_assembly3 · https://github.com/shaise/FreeCAD_FastenersWB · https://github.com/boltsparts/BOLTS_archive ·
  https://github.com/boltsparts/boltsfc · https://github.com/JMG1/ExplodedAssembly · https://github.com/FreeCAD/FreeCAD-render ·
  https://github.com/sargo-devel/Cables · https://github.com/drfenixion/freecad.robotcad
- Code-CAD: https://github.com/CadQuery/cadquery · https://cadquery.readthedocs.io/en/latest/assy.html · https://github.com/gumyr/build123d ·
  https://build123d.readthedocs.io/en/latest/import_export.html · https://github.com/bernhard-42/vscode-ocp-cad-viewer ·
  https://github.com/openscad/openscad · https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/STL_Import_and_Export ·
  PyPI: https://pypi.org/project/cadquery/ · https://pypi.org/project/build123d/
- Tự động hóa: https://github.com/asymworks/FCBot · https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage ·
  https://github.com/bambulab/BambuStudio/releases · https://github.com/OrcaSlicer/OrcaSlicer/releases
- Mã nguồn FreeCAD (mục 7, đọc 2026-10-24): https://github.com/FreeCAD/FreeCAD/blob/main/src/Gui/ApplicationPy.cpp
  (`sSetupWithoutGUI`) · https://github.com/FreeCAD/FreeCAD/blob/main/src/Mod/Part/App/TopoShapePyImp.cpp (`distToShape`) ·
  https://github.com/FreeCAD/FreeCAD/blob/main/src/Mod/Part/App/FCBRepAlgoAPI_BooleanOperation.cpp (parallel, BRepCheck,
  auto-fuzzy) · https://github.com/FreeCAD/FreeCAD/blob/main/src/Mod/Part/App/FuzzyHelper.cpp ·
  bản cài `C:/Program Files/FreeCAD 1.1/Mod/Test/__init__.py` (runTestsFromModule)
- Datasheet động cơ 030 (lực dọc trục do trục vít, không để kẹt khi cấp điện): `community/cyberbrick-official/pdf/030_Micro_DC_Motor_-LA024.pdf`
- Số sao: GitHub REST API `api.github.com/repos/<owner>/<repo>` (`stargazers_count`), Codeberg API `codeberg.org/api/v1/repos/Zolko/Assembly4`, tra 2026-10-23.
