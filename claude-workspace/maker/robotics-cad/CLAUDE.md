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
4. Kiểm tra trước khi in theo checklist `kiem-tra-model.md` (hình học + BOP, lưới, giao thoa theo góc khớp,
   FEM nếu chịu lực, khối lượng). In thử chi tiết lắp ghép nhỏ trước (xem `maker/in-3d`).
5. Robot di động/tay máy cần mô phỏng → RobotCAD: gán link/joint, vật liệu → xuất URDF.

## Quy ước
- mm; dung sai lắp ghép in FDM: ghi giá trị đã thử, chưa thử thì `TODO` (không đoán).
- Thông số linh kiện chỉ lấy từ `components.yaml` hoặc datasheet có nguồn; thêm linh kiện mới phải kèm nguồn.
- Model trong `models/<du-an>/` (FCStd + STEP xuất). Ghi công tác giả khi dùng model CC-BY trong tài liệu.
- RobotCAD: KHÔNG dùng "Transfer to external code generator" (gửi dự án lên robotcad.ru) và các LLM provider
  ngoài trong RobotCAD; phần ROS2/Gazebo cần Linux/WSL2.

## TODO
- TODO: danh sách robot đang làm (xe 2 bánh? tay máy 4 bậc? robot 4 chân?).
- TODO: dung sai lắp ghép trên A1 – in `maker/in-3d/models/mau-dung-sai-a1` rồi ghi vào `maker/in-3d/CLAUDE.md`.
