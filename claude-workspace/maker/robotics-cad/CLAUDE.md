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

## Quy trình
1. Chọn linh kiện trong `library/components.yaml`; chèn STEP từ thư viện (không tự vẽ lại linh kiện chuẩn).
2. Dựng khung quanh linh kiện; tham số hóa kích thước chính bằng Spreadsheet.
3. Kiểm tra va chạm và tầm quay khớp trong Assembly.
4. **Một lệnh chuẩn bị in** (2026-10-23, pushrod-arm ~1–2 phút; trước đó >1 giờ):
   `"C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/prepare-print.py maker/<project>/print/print.yaml`
   = tầng 1 (`check.py`) song song [xuất STL theo hướng in (`export-stl.py`) → tầng 2 cắt lớp (`slice.py`)].
   Hướng in, tham số kiểm, bàn in khai trong `print/print.yaml` (mẫu `project-template/print/print.yaml`;
   bản đầy đủ: `maker/pushrod-arm/print/print.yaml`). Chỉ đọc file đã **Lưu**; có `rest_pose` thì tự về tư thế gốc.
   Toolhub → Dự án → nút **Chuẩn bị in** / **Tự chạy khi Lưu** (`scripts/watch.py`); in xong `/print-result`.
   Bàn in lơ lửng: tự cho Bambu **xoay hướng in trước**, vẫn lơ lửng mới **bật support** (tách bàn `__orient`/`__support`);
   nhưng ưu tiên sửa thiết kế (vát 45°, gân đỡ) để bỏ support.
   Chi tiết từng tầng:
   - **Tầng 1 – mỗi lần sửa** (file LẮP RÁP, có cache): `freecadcmd scripts/check.py --pass <file.FCStd>
     components=... ignore-pair=... mesh-pair=... multi-solid=...` → hình học, lưới, **va chạm** (manifold3d),
     quét khớp (`sweep=`). Ngưỡng: `thresholds.yaml`. Ra `freecad/check/overview.png`.
   - **Tầng 2 – trước khi in** (STL theo HƯỚNG IN, ~10–40 s): `slice.py print/print.yaml` → Bambu Studio CLI cắt lớp
     theo profile A1 chính hãng: lơ lửng, support, thời gian, số gam. Ra `print/plates/<plate>/<plate>.3mf` (mở Bambu
     để in) + `print/plates/print-overview.png`.
   - `check.py mode=full` (BOP, độ dày thành, overhang theo hướng trong file, ~2 phút) chỉ khi cần soi kỹ;
     độ dày/overhang **đúng hướng in** thì tin kết quả slicer ở tầng 2.
   - FEM nếu chịu lực: theo `kiem-tra-model.md` mục 4. In thử chi tiết lắp ghép nhỏ trước (xem `maker/in-3d`).
5. Robot di động/tay máy cần mô phỏng → RobotCAD: gán link/joint, vật liệu → xuất URDF.

## Dự án (cấu trúc chuẩn, 2026-10-23 – mọi thứ của 1 dự án nằm trong `maker/<project>/`)
```
maker/<project>/            tên tiếng Anh, kebab-case
  README.md  CLAUDE.md      mục tiêu, an toàn, BOM, bàn in, lịch sử sửa/in (nội dung tiếng Việt)
  ASSEMBLY.md               hướng dẫn lắp từng bước + ảnh freecad/images/assembly/ (mẫu: maker/pushrod-arm)
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
- **Một phiên Claude giữ FreeCAD** (2026-10-23, Tuan): 2 phiên cùng sửa/chạy FreeCAD thì lệch nhau và chậm.
  Phiên khác chỉ chạy `freecadcmd` riêng trên file đã lưu (kiểm, xuất) – không gửi lệnh vào FreeCAD đang mở.
  Trước khi sửa model qua RPC/MCP: kiểm `doc.UndoCount == 0` (có thao tác chưa lưu – vd. đang mô phỏng – thì
  DỪNG, hỏi Tuan; **không dùng `isTouched()`**: FreeCAD bật nó ngay khi nạp file), so tư thế với `rest.json`
  (file từng bị Lưu lúc mô phỏng; công cụ: `freecad/scripts/reset_rest_pose.py`), lưu bản sao vào `freecad/backup/`,
  giữ nguyên `Placement`, sửa xong kiểm lại rồi **tự Lưu**.
  STEP linh kiện lỗi BOP (servo/N20 CyberBrick) làm boolean thất bại âm thầm → dùng khối đơn giản làm dao cắt.
- **Nhựa mặc định: Bambu PETG Basic** (Tuan 2026-10-23) – profile chính hãng `Bambu PETG Basic @BBL A1` (245 °C, bàn 70 °C,
  13 mm³/s). Bàn in: Textured PEI (TDS: SuperTack/Textured/Smooth PEI, 65–75 °C; PEI bám chặt → đợi bàn nguội mới gỡ).
  `slice.py` đọc được cả preset riêng (vd. KINGROON-PETG) nếu đổi cuộn. Đệm/chi tiết dẻo: TPU 95A.
- Khe hở lắp ghép: **0,2 mm** (Tuan 2026-10-23, đã tính co ngót nhựa). Bánh răng ăn khớp / đệm lỏng khai `mesh-pair`.
- Đặt tên **tiếng Anh** cho thư mục, file, script, khóa YAML, tham số (Tuan 2026-10-23); nội dung tài liệu tiếng Việt.
- mm; dung sai lắp ghép in FDM: ghi giá trị đã thử, chưa thử thì `TODO` (không đoán).
- Thông số linh kiện chỉ lấy từ `components.yaml` hoặc datasheet có nguồn; thêm linh kiện mới phải kèm nguồn.
- Model trong `models/<du-an>/` (FCStd + STEP xuất). Ghi công tác giả khi dùng model CC-BY trong tài liệu.
- RobotCAD: KHÔNG dùng "Transfer to external code generator" (gửi dự án lên robotcad.ru) và các LLM provider
  ngoài trong RobotCAD; phần ROS2/Gazebo cần Linux/WSL2.

## TODO
- TODO: danh sách robot đang làm (xe 2 bánh? tay máy 4 bậc? robot 4 chân?).
- TODO: dung sai lắp ghép trên A1 – in `maker/in-3d/models/mau-dung-sai-a1` rồi ghi vào `maker/in-3d/CLAUDE.md`.
