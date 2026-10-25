# robotics-cad – thiết kế robot bằng FreeCAD 1.1

## Mục tiêu
Thiết kế cơ khí robot (khung, gá động cơ/cảm biến, hộp số) để in trên Bambu A1, xuất URDF khi cần mô phỏng.

## Công cụ (đã ghim, xem docs/COMMUNITY.md)
- MCP `freecad` (điều khiển FreeCAD đang mở) – mở bằng Toolhub "Mở + Claude".
- Workbench: **RobotCAD** v12.10.3 (link/joint, khối lượng/quán tính, xuất URDF), **Gears**, **SheetMetal**,
  Fasteners (đã có), Assembly tích hợp của FreeCAD 1.1.
- Thư viện linh kiện: `community/freecad-library` (CC-BY 3.0, chỉ phần robotics) + danh mục
  `library/components.yaml`. Macro duyệt: Macro → PartsLibrary.
- **CyberBrick** (Bambu Lab): 22 model STEP + STL chính thức + datasheet trong `community/cyberbrick-official/`
  (không lên git). Tải lại: `python library/cyberbrick.py fetch` (kiểm SHA-256 theo `library/cyberbrick-sources.tsv`)
  rồi `build`. Nguồn: CDN cửa hàng Bambu (store.bblcdn.com) + wiki component list.
- **N20** (khuôn chung): model Pololu Micro Metal Gearmotor (8 biến thể, STEP + STL) trong `community/n20-motor/models/`;
  nguồn + SHA-256: `library/n20-sources.tsv`.
- **Board vi điều khiển** (2026-10-22), dữ liệu trong `community/boards-official/` (không lên git):
  - STEP chính hãng Arduino (UNO R4 WiFi, UNO Q, Nano ESP32, Nano R4, GIGA R1, 14 Modulino):
    `python library/boards.py extract`, đo hộp bao: `freecadcmd library/boards.py` → `models.json`.
  - 29 module ESP32 chính hãng: `community/espressif-kicad-libraries/3dmodels/espressif.3dshapes/`.
  - Dựng từ bản vẽ (`drawings/`): Pi 5, Pi Zero 2 W, ESP32-DevKitC V4, ESP32-S3-DevKitC-1, STM32 Nucleo-64,
    Blue Pill (nguồn cộng đồng), LOLIN D1 mini v4, ESP32-CAM → `freecadcmd library/boards_param.py`
    (ra STEP + ảnh hình chiếu `.png`). **Mặt bằng đúng bản vẽ; chiều cao cổng/header là ước tính** → chừa khe ≥ 1 mm
    và đo hàng thật trước khi in hộp.
- Skill (dùng chung, `~/.claude/skills` → symlink về workspace): `freecad-scripts` (viết script FreeCAD đúng API),
  `robotics-cad` (quy trình + danh mục). Dùng với Claude Code hoặc tab **Code** của Claude Desktop.
- **Workbench STLab** (2026-10-24, `workbench/`, xem `workbench/README.md`): giao diện trong FreeCAD cho quy trình
  bên dưới – 6 toolbar theo bước (Dự án · Linh kiện · Thiết kế · Kiểm tra · In 3D · Tài liệu) + bảng **STLab Workflow**.
  Chỉ gọi lại `scripts/` (chạy nền, không treo FreeCAD). Cài: `python workbench/install.py` (junction vào `Mod/STLab`).
  Sửa logic pipeline thì sửa trong `scripts/`, workbench tự theo.

## Quy trình
0. **Giao diện trước** (Tuan 2026-10-24): `design/brief.md` → 3 concept dáng (bóng hông/đỉnh/3/4) + `cmf.png` (≤ 3 màu, cuộn có thật) + render + mockup UI nếu có → `contact-sheet.png` → Tuan chọn bằng ảnh. Chưa chọn thì chưa dựng cơ khí. Mức A/B/C và checklist: `studio/design/DESIGN.md`, `project-template/design/brief.md`.
1. Chọn linh kiện trong `library/components.yaml`; chèn STEP từ thư viện (không tự vẽ lại linh kiện chuẩn).
2. Dựng khung quanh linh kiện; tham số hóa kích thước chính bằng Spreadsheet.
3. Kiểm tra va chạm và tầm quay khớp trong Assembly.
4. **Một lệnh chuẩn bị in** (2026-10-23, pushrod-arm ~1–2 phút; trước đó >1 giờ):
   `"C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/prepare-print.py maker/<project>/print/print.yaml`
   = **kiểm hết trước, sạch mới cắt lớp** (Tuan 2026-10-23): tầng 1 (`check.py`) ∥ xuất STL (`export-stl.py`) ∥
   `metrics.py` → khả năng in trên STL (`printability`: nhô ra không đỡ + **kiểm theo lớp**) → chỉ khi không FAIL mới
   tầng 2 cắt lớp (`slice.py`) ra .3mf. Có lỗi → dừng, không ra file in (ép: thêm `force`).
   Hướng in, tham số kiểm, bàn in khai trong `print/print.yaml` (mẫu `project-template/print/print.yaml`;
   bản đầy đủ: `maker/pushrod-arm/print/print.yaml`). Chỉ đọc file đã **Lưu**; có `rest_pose` thì tự về tư thế gốc.
   Toolhub → Dự án → nút **Chuẩn bị in** / **Tự chạy khi Lưu** (`scripts/watch.py`); in xong `/print-result`.
   Trong FreeCAD: workbench STLab → **Chuẩn bị in** (Ctrl+Shift+P) hoặc ô "Tự chuẩn bị in mỗi khi Lưu".
   Kèm theo (chỉ cảnh báo, không FAIL):
   - `scripts/metrics.py`: thể tích/hộp bao/trọng tâm/số solid từng chi tiết + giờ/gam từng bàn → `freecad/metrics.json`
     (**lên git**, commit cùng lần sửa model), so với commit trước: chi tiết đổi ngoài ý muốn hiện ngay;
     `git diff freecad/metrics.json` = nhật ký thay đổi hình học. Tay: `python scripts/metrics.py diff <print.yaml>`.
   - `scripts/bom.py`: `BOM.csv` + `BOM.md` (vít đếm theo cỡ, linh kiện mua, chi tiết in → bàn/nhựa) từ Label;
     so SL vít với bảng trong `ASSEMBLY.md` (lệch → WARN, không tự sửa file viết tay).
   **Support – chính sách Tuan (cập nhật 2026-10-25):** vẽ tối ưu để ít cần support (vát 45°, lỗ giọt nước, chia chi
   tiết, đổi hướng in). **KHÔNG vẽ/dựng support vào model hay STL nữa – Tuan tự tô support trong Bambu Studio.**
   Lý do: support tự vẽ (`support: true` cũ) lấp kín lỗ trục Worm và rãnh thanh răng Housing của pushrod-arm (bản in hỏng).
   - `scripts/printability.py` phân tích STL theo hướng in: mặt úp xuống < 43°, rộng > 5 mm (mái lỗ kín ≤ 8 mm bắc cầu
     được), dải > 2,5 mm, cao > 1 mm → **WARN "CẦN SUPPORT – tô trong Bambu Studio"** kèm vị trí (mm², z) – không chặn cắt lớp.
     Báo rõ cho Tuan chi tiết nào/vùng nào cần tô, và **lỗ/khe chức năng nào KHÔNG được để support lọt vào**.
   - `support: true` trong quy tắc xuất print.yaml giờ chỉ là ghi chú (danh sách `support_trong_slicer` trong
     `_export-stl.json`), không dựng gì. Không vẽ `Support_*` trong CAD.
   - Lơ lửng thật (cụm rời) = FAIL → sửa thiết kế. `support_policy: slicer` (slicer tự sinh support) – chỉ khi Tuan cho phép.
   - **Chi tiết nhỏ** (chân chạm bàn < 120 mm² hoặc cao/mảnh) → bàn đó bật brim 5 mm (ghi đè `auto_brim`).
   Ngưỡng: `thresholds.yaml` mục `print:`. Tay: `python scripts/printability.py <thư mục stl>`.
   Chi tiết từng tầng:
   - **Tầng 1 – mỗi lần sửa** (file LẮP RÁP, có cache): `freecadcmd scripts/check.py --pass <file.FCStd>
     components=... ignore-pair=... mesh-pair=... multi-solid=...` → hình học, lưới, **va chạm** (manifold3d),
     quét khớp (`sweep=`). Ngưỡng: `thresholds.yaml`. Ra `freecad/check/overview.png`.
   - **Tầng 2 – trước khi in** (STL theo HƯỚNG IN, ~10–40 s): `slice.py print/print.yaml` → Bambu Studio CLI cắt lớp
     theo profile A1 chính hãng: lơ lửng, support, thời gian, số gam. Ra `print/plates/<plate>/<plate>.3mf` (mở Bambu
     để in) + `print/plates/print-overview.png`.
   - **Quét khớp / mô phỏng / script đo riêng: KHÔNG dùng boolean B-rep mỗi tư thế** (`common`/`distToShape`
     0,1–12 s/cặp) → `scripts/fast_collide.py`: chia lưới 1 lần (manifold3d, linh kiện lưới hở → bao lồi), mỗi
     tư thế chỉ nhân ma trận (~ms/cặp). pushrod-arm 2026-10-24: quét 24 tư thế + kẹp **16 s thay 395 s**, kết quả
     trùng B-rep. `min_gap` giữ bán kính ≤ 20 mm (50 mm trả sai/treo). FreeCAD 1.1 không có lệnh kiểm va chạm sẵn
     (Assembly chỉ có Solve/Simulation/BOM) – nút kiểm của hãng đã dùng: Part Check Geometry (BOP, `mode=full`),
     Mesh, Bambu Studio CLI (tầng 2).
   - `check.py mode=full` (BOP, độ dày thành, overhang theo hướng trong file, ~2 phút) chỉ khi cần soi kỹ;
     độ dày/overhang **đúng hướng in** thì tin kết quả slicer ở tầng 2.
   - FEM nếu chịu lực: theo `model-checks.md` mục 4. In thử chi tiết lắp ghép nhỏ trước.
5. Robot di động/tay máy cần mô phỏng → RobotCAD: gán link/joint, vật liệu → xuất URDF.

## Dự án (cấu trúc chuẩn, 2026-10-23 – mọi thứ của 1 dự án nằm trong `maker/<project>/`)
```
maker/<project>/            tên tiếng Anh, kebab-case
  README.md  CLAUDE.md      mục tiêu, an toàn, BOM, bàn in, lịch sử sửa/in (nội dung tiếng Việt)
  ASSEMBLY.md / .pdf        hướng dẫn lắp từng bước + ảnh freecad/images/assembly/ (mẫu: maker/pushrod-arm);
                            PDF: scripts/assembly-pdf.py (Edge headless, không cần cài thêm)
  freecad/                  THÔNG TIN FREECAD
    <model>.FCStd           chỉ trên máy (không lên git)  ·  <model>_rest.json (tư thế gốc)  ·  <model>_sim.FCMacro
    images/  scripts/ (công cụ; history/ = script sửa model đã chạy)
    check/  backup/         file sinh / bản sao lưu (không lên git)
  print/                    THÔNG TIN BÀN IN
    print.yaml              hướng in + tham số kiểm + bàn in
    stl/  plates/           file sinh (không lên git): plates/<plate>/<plate>.3mf để in, print-overview.png
```
- Tạo bằng `/new-project <name>`: chép `project-template/` → `maker/<name>/`. Không để dữ liệu dự án ở nơi khác.
- Macro trong thư mục macro của FreeCAD chỉ là **file chuyển tiếp** `exec(...)` tới macro trong dự án (1 nguồn).
- Tên Label trong FreeCAD: linh kiện mua bắt đầu `CB_` (CyberBrick) hoặc `LK_` (khác), vít `M2_5x6`, `M3x8`…;
  nhựa dẻo hậu tố `_TPU`; chi tiết đối xứng `_L`/`_R`; bánh răng `Gear_*`/`Pinion_*`
  → glob trong `print.yaml` dùng chung, khỏi khai từng dự án.

## Quy ước
- **Lưu ý BẮT BUỘC khi viết ASSEMBLY.md / hướng dẫn lắp** (Tuan 2026-10-24): đưa vào bước liên quan, kèm nguồn
  (`docs/component-dimension-sources.md`, `components.yaml`):
  - **PG002 (servo 360°) KHÔNG có bảo vệ kẹt/nhiệt/quá dòng** (datasheet B-PG002) → không để kẹt lâu khi đang cấp
    điện; thử tay trước khi cấp nguồn. PG001 có ly hợp (ngắt khi kẹt 5 s).
  - **Pin PC003 (Li-ion 2S 7,4 V)**: dung lượng mâu thuẫn 800 / 700 mAh → đọc nhãn pin thật; nhắc an toàn Li-ion
    (không đâm/ép/làm nóng, sạc đúng bộ sạc, không để học sinh sạc không giám sát).
  - **Ép heat-set insert**: mỏ hàn > 250 °C (PETG thử 255–265 °C, chưa có số hãng) → giá đỡ mỏ hàn, kìm, người lớn
    giám sát; **không** ép insert vào chi tiết đang lắp pin. Lỗ insert theo bảng Ruthex (M2.5/M3: Ø4,0, sâu ≥ 6,7).
  - Công tắc XA007 tối đa 3 A / 12,6 V.
  - Hốc servo SG90 / PG001 / MG90S **không dùng chung** (đáy→mặt dưới tai 17 / 16,3 / 18,5 mm) → ghi đúng loại servo.
- **Đọc `docs/freecad-automation-research.md` mục 7 trước khi viết script FreeCAD** (11 bẫy CLI đã dính + cách chặn,
  số đo hiệu năng, `fc_cli.py` / `gui_run.py` / bộ test `-t`).
- **Ảnh dựng từng bước cho video** (2026-10-25): `scripts/build_replay.py` qua `gui_run.py` (biến `REPLAY_OUT`, `REPLAY_MODE`
  auto|body|parts, `REPLAY_SIZE`) → `step-XX.png` + `steps.json`. PartDesign: từng feature (+ khung sketch); chỉ Part: theo nhóm.
- **CLI trước, GUI chỉ để xem** (Tuan 2026-10-24: "mở FreeCAD dễ crash"): sửa model bằng
  `"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" script.py` trên file đã Lưu, **GUI phải đóng file đó**
  (hoặc xong thì File → Revert). Lưu từ CLI làm mất dữ liệu hiển thị (màu, ẩn hiện, thumbnail; hình học giữ nguyên)
  → `se.save(doc, gui_from=<backup trước khi sửa>)` chép lại. Không gửi tính toán nặng (slice/distToShape/boolean
  trên STEP linh kiện) qua RPC vào GUI: 2026-10-24 cắt lát treo GUI > 2 phút, cùng script chạy CLI 16 s.
  CLI không làm được: màu/ViewProvider, chụp ảnh màn hình → render bằng matplotlib/Blender.
  Đã thử theo mã nguồn FreeCAD (2026-10-24, đừng thử lại): `FreeCADGui.setupWithoutGUI()` tạo `Gui::Application(false)`
  → không có ViewProvider/`getDocument`, không giữ được màu; `distToShape(s, tol)` = deflection của
  `BRepExtrema_DistShapeShape` (đã đa luồng), nới tol KHÔNG nhanh hơn (0,94 → 3,67 s) → dùng lưới.
  `freecadcmd --safe-mode script.py`: không nạp addon (ROS, laser-cut, RobotCAD…), khởi động 1,1 → 0,4 s.
  GUI crash: thử mở `FreeCAD.exe --safe-mode -l` – hết crash thì lỗi do addon; log ở thư mục người dùng FreeCAD.
- **Một phiên Claude giữ FreeCAD** (2026-10-23, Tuan): 2 phiên cùng sửa/chạy FreeCAD thì lệch nhau và chậm.
  Phiên khác chỉ chạy `freecadcmd` riêng trên file đã lưu (kiểm, xuất) – không gửi lệnh vào FreeCAD đang mở.
  Trước khi sửa model qua RPC/MCP: kiểm `doc.UndoCount == 0` (có thao tác chưa lưu – vd. đang mô phỏng – thì
  DỪNG, hỏi Tuan; **không dùng `isTouched()`**: FreeCAD bật nó ngay khi nạp file), so tư thế với `rest.json`
  (file từng bị Lưu lúc mô phỏng; công cụ: `freecad/scripts/reset_rest_pose.py`), lưu bản sao vào `freecad/backup/`,
  giữ nguyên `Placement`, sửa xong kiểm lại rồi **tự Lưu**.
  STEP linh kiện lỗi BOP (servo/N20 CyberBrick) làm boolean thất bại âm thầm → script sửa model dùng
  **`scripts/safe_edit.py`**: `guard()` (UndoCount, tư thế gốc) → `backup()` → `safe_cut()`/`safe_fuse()` (so lượng
  bỏ/thêm với `expect_mm3` hoặc thể tích giao tính trên lưới manifold3d, thử lại boolean fuzzy, sai → `SafeEditError`,
  model giữ nguyên) → `apply()` → kiểm → `save()`. Vẫn lỗi → dùng khối đơn giản (hộp, mặt đùn) làm dao cắt.
  Thử 2026-10-23 trên servo (BOP lỗi): cắt 21,07 mm³ = ước lưới 21,07 mm³; N20 lưới không kín → phải truyền
  `max_mm3`/`expect_mm3`.
- **Nhựa mặc định: Bambu PETG Basic** (Tuan 2026-10-23) – profile chính hãng `Bambu PETG Basic @BBL A1` (245 °C, bàn 70 °C,
  13 mm³/s). Bàn in: Textured PEI (TDS: SuperTack/Textured/Smooth PEI, 65–75 °C; PEI bám chặt → đợi bàn nguội mới gỡ).
  `slice.py` đọc được cả preset riêng (vd. KINGROON-PETG) nếu đổi cuộn. Đệm/chi tiết dẻo: TPU 95A.
- Vỏ mỏng in đứng: bề dày = **bội số đường in Bambu** (0,42 + n × 0,45: 1 đường 0,42 / 2 đường 0,87 / 3 đường 1,3 mm).
  Lệch (vd. 1,2 mm) → slicer in thiếu đường + lấp khe vụn → báo "floating" (cyberbrick-car 2026-10-23).
  Slicer báo lỗi mà không chỉ chỗ → cắt STL thành lát (manifold3d) cho Bambu cắt từng lát để khoanh vùng.
- Khe hở lắp ghép: **0,2 mm** (Tuan 2026-10-23, đã tính co ngót nhựa). Bánh răng ăn khớp / đệm lỏng khai `mesh-pair`.
- Đặt tên **tiếng Anh** cho thư mục, file, script, khóa YAML, tham số (Tuan 2026-10-23); nội dung tài liệu tiếng Việt.
- mm; dung sai lắp ghép in FDM: ghi giá trị đã thử, chưa thử thì `TODO` (không đoán).
- Thông số linh kiện chỉ lấy từ `components.yaml` hoặc datasheet có nguồn; thêm linh kiện mới phải kèm nguồn.
- Model trong `models/<du-an>/` (FCStd + STEP xuất). Ghi công tác giả khi dùng model CC-BY trong tài liệu.
- RobotCAD: KHÔNG dùng "Transfer to external code generator" (gửi dự án lên robotcad.ru) và các LLM provider
  ngoài trong RobotCAD; phần ROS2/Gazebo cần Linux/WSL2.

## TODO
- TODO: danh sách robot đang làm (xe 2 bánh? tay máy 4 bậc? robot 4 chân?).
- TODO: dung sai lắp ghép trên A1 – in mẫu thử khe 0,1–0,4 mm (mẫu cũ `maker/in-3d` đã xóa 2026-10-23; dựng lại khi cần).
