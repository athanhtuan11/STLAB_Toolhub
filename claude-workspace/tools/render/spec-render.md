---
task: blender-render-tool
cwd: tools/render
allow:
  - "render.py"
  - "fc_export.py"
  - "blender_scene.py"
  - "README.md"
gate: "python -m unittest tests/test_render.py -v"
timeout_min: 40
max_rounds: 3
executor: opencode
---

# Mục tiêu
Công cụ render ảnh duyệt **đẹp** (studio, vật liệu nhựa PETG) từ model FreeCAD bằng Blender 5.2, dùng cho bước 0
"Giao diện" của mọi dự án maker (thay ảnh khối matplotlib). Một lệnh:
`python tools/render/render.py <model.FCStd> --cmf <cmf.json> --out <dir> [--views iso,front,top,side34] [--samples 64]
[--size 1600x1200] [--name <tiền tố>] [--engine eevee|cycles]` → `<dir>/<name>-<view>.png` + `<dir>/<name>-scene.json`,
in dòng cuối `RENDER OK <n ảnh>`. `--name` mặc định = tên file model.

# Cấu trúc (3 file, Claude chốt)
1. `fc_export.py` – chạy bằng `C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe` (gọi qua subprocess từ render.py, tham số
   qua biến môi trường). **Chỉ đọc** FCStd: mọi `Part::Feature` có Solid, bỏ Label bắt đầu `_` và object ẩn
   (`Visibility` False) → mỗi object 1 STL (`MeshPart.meshFromShape`, LinearDeflection 0.05, AngularDeflection 0.2) vào
   `<out>/_stl/`. Ghi danh sách label + đường dẫn STL ra JSON tạm.
2. `blender_scene.py` – chạy `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe -b --factory-startup -P blender_scene.py -- <scene.json>`.
   - Nhập STL (`bpy.ops.wm.stl_import`), mm → giữ tỉ lệ (scene unit scale 0.001 hoặc scale vật thể 0.001 – nhất quán), shade
     auto smooth 30°.
   - Vật liệu Principled BSDF theo `finish`: `matte` (roughness 0.65, specular 0.3), `satin` (0.45), `gloss` (0.25); màu từ hex
     (chuyển sRGB → linear đúng). Thêm Bevel shader nhẹ (0,3 mm) nếu engine hỗ trợ, không thì bỏ.
   - Studio: phông cong liền (cyclorama) màu `background`; 3 đèn area (key 45° trên-trái, fill phải yếu, rim sau); world tối nhẹ;
     View Transform **AgX**, look Medium Contrast; bóng mềm trên nền.
   - Camera: khung theo hộp bao toàn cảnh, lề 12 %; view `iso` (az −45°, el 30°), `front` (nhìn theo +Y – thấy mặt hông XZ),
     `top` (từ trên), `side34` (az −30°, el 15°, tiêu cự 85 mm). Ortho cho front/top, perspective 50 mm cho iso, 85 mm side34.
   - Engine mặc định `eevee` (nhanh); `cycles` dùng `--samples`, denoise bật. Kích thước theo `--size`.
3. `render.py` – Python hệ thống (stdlib): đọc cmf, gọi fc_export → gán màu/finish cho từng label theo **quy tắc ĐẦU TIÊN
   khớp** (`fnmatch` trên `names`), không khớp → `default`; ghi `<name>-scene.json`
   `{"background": hex, "views": [...], "objects": [{"label","stl","color","finish"}...]}` rồi gọi Blender.
   Lỗi subprocess → in log ngắn + exit 1.

# cmf.json (đầu vào, do product-designer viết)
`{"rules": [{"names": ["Base_*"], "color": "#1E5A45", "finish": "matte"}], "default": {"color": "#D9DDD9", "finish": "satin"},
"background": "#ECF1EF"}` – `background` mặc định `#ECF1EF` (màu "sương" của `studio/design/tokens.json`).

# README.md
Ngắn (tiếng Việt): lệnh, định dạng cmf.json, các view, mẹo (eevee để xem nhanh, cycles 128 mẫu cho ảnh chốt).

# Không làm
- Không sửa/lưu file `.FCStd` nào, không sửa `tests/`, không mở GUI FreeCAD/Blender, không cài gói pip mới.
- Không tự chọn số khác bảng trên; thiếu gì → `ESCALATE: <cần gì>`.

# Tiêu chí PASS
Gate exit 0 (8 test). Thời gian 1 lần render eevee 800×600 hai view < 3 phút.

# Sửa lần 2 (Claude 2026-11-02) – gate cũ PASS nhưng ảnh SAI
Render thật line_bot.FCStd ra 1 khối trắng to chiếm gần hết khung (iso) và mặt phẳng xám (side34) – không thấy chi tiết nào.
Nghi: hộp bao/phông/camera tính trên tọa độ chưa áp `scale 0.001` (`matrix_world` chưa cập nhật – cần
`bpy.context.view_layer.update()` sau khi scale, hoặc áp scale bằng `transform_apply`), phông cong bao trùm cả camera.
Gate mới có `test_05_thay_mau_chi_tiet` (phải thấy màu xanh tấm + vàng chi tiết, vật thể chiếm 15–85 % khung).
**Tự Read ảnh PNG** ra trong thư mục tạm để nhìn trước khi báo xong. Gate 5 test.

# Sửa lần 3 (Claude 2026-11-02) – ĐÃ TÌM RA NGUYÊN NHÂN
Khối trắng = **Cube mặc định của Blender** (`--factory-startup` có sẵn Cube 2 m + Camera + Light); robot 0,14 m nằm TRONG cube.
Sửa: đầu `blender_scene.py` xóa sạch scene trước khi nhập
(`for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)`, xóa luôn mesh/material/camera/light mồ côi),
rồi mới import STL, dựng phông/đèn/camera. Kiểm lại hộp bao chỉ tính trên object STL. Gate 5 test; tự Read ảnh trước khi báo.

# Lần 4 (Tuan duyệt đề xuất #1 + #2, 2026-11-02 – `docs/reports/delegate-pipeline-pain-2026-11.md`)
1. **Đường dẫn tuyệt đối:** `render.py` đổi `model`, `--cmf`, `--out` sang tuyệt đối theo cwd của lệnh **trước** khi gọi
   FreeCAD/Blender; scene.json chỉ chứa đường dẫn tuyệt đối; `render.filepath` trong Blender dùng đường dẫn tuyệt đối.
2. **Viền ảnh = nền:** không để mép phông/sàn tối lọt khung ở mọi view (front ortho đang lộ dải đen dưới đáy): phông cong
   đủ rộng/cao theo khung camera, hoặc world/film nền đúng màu `background`; 4 cạnh ảnh phải là nền.
3. **Smooth by Angle:** bỏ vòng `use_smooth=True` cho mọi polygon; dùng "Smooth by Angle" 30° (Blender 4.1+:
   `bpy.ops.object.shade_smooth_by_angle(angle=…)` hoặc modifier tương đương) để mặt phẳng CAD không loang.
Gate: 8 test (thêm test_06 viền, test_07 đường dẫn tương đối, test_08 smooth). Tự Read ảnh trước khi báo xong.
