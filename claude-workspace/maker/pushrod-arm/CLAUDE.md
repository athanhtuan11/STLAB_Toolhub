# pushrod-arm – cánh tay robot xi-lanh đẩy (CyberBrick)

Mọi thứ của dự án nằm trong thư mục này (2026-10-23; trước đó ở `D:\06_FreeCAD\pushrod_arm` – không dùng nữa).
Cấu trúc chuẩn: `tools/robotics-cad/CLAUDE.md` mục "Dự án".

## FreeCAD – `freecad/`
- `pushrod_arm.FCStd`: lắp ráp, ~7 MB, **chỉ trên máy** (không lên git; bản sao lưu ở `backup/`).
- `pushrod_arm_rest.json`: tư thế gốc. `pushrod_arm_sim.FCMacro`: mô phỏng (macro FreeCAD → `pushrod_arm_sim`
  là file chuyển tiếp tới đây).
- `scripts/`: `kinematics_test.py` (quét tư thế + kẹp, chạy `freecadcmd`/`fc_job`, ra `check/`),
  `reset_rest_pose.py` (gửi qua RPC khi file bị Lưu lúc mô phỏng); `history/` = script sửa model đã chạy (chỉ đọc lại).
- `images/assembly/`: ảnh 32 bước lắp kiểu "thao tác" + `cover.png` (`scripts/render_assembly_steps.py` qua gui_run →
  `scripts/crop_assembly_images.py`; ảnh gốc 2400 px ở `raw/` không lên git). Hướng dẫn: `ASSEMBLY.md` / `ASSEMBLY.pdf`.
- `check/`: kết quả kiểm nhanh (`overview.png`) – file sinh.

## Bàn in – `print/`
- `print.yaml`: hướng in từng chi tiết, tham số kiểm, 8 bàn in (profile A1 chính hãng + ghi đè). Nhựa mặc định
  **Bambu PETG Basic** (profile chính hãng `Bambu PETG Basic @BBL A1`); đệm kẹp TPU 95A.
- `plates/<plate>/<plate>.3mf`: **file để mở Bambu Studio và in**; `plates/print-overview.png`: bảng + ảnh từng bàn.
- `stl/`: STL theo hướng in – file sinh.

## Làm việc
- Chuẩn bị in (~1–2 phút): Toolhub → Dự án → maker/pushrod-arm → **Chuẩn bị in** (hoặc **Tự chạy khi Lưu**), hay
  `"C:/Program Files/FreeCAD 1.1/bin/python.exe" tools/robotics-cad/scripts/prepare-print.py maker/pushrod-arm/print/print.yaml`
- Sửa model: theo quy ước `tools/robotics-cad/CLAUDE.md` (1 phiên giữ FreeCAD; `UndoCount == 0`; so `rest.json`;
  backup `freecad/backup/`; giữ `Placement`; sửa xong tự Lưu).
- In xong: `/print-result pushrod-arm <plate> pass|fail [mô tả]`.

## Trạng thái (2026-10-25)
- 16/16 test PASS (`freecad/tests`); kiểm nhanh WARN (không FAIL); cắt lớp 8 bàn ~10 h 58, ~288 g; BOM PASS.
- Support: Tuan tô trong Bambu Studio (không vẽ vào STL). Chốt khớp Ø4,8, đặc, in nằm (bàn P8 100 %).
- Bộ chốt thử: Ø4,8 vừa (Tuan 2026-10-25). Chờ Tuan: in lại 7 chốt (R5); in **R6 Housings** (`plates-reprint-housings-2026-10-25/`,
  vách ngoài rãnh thanh răng 0,2 → 0,9 mm – KHÔNG dùng Housing trong R1/P4 cũ); lắp theo ASSEMBLY (bước 11b);
  thử tự hãm trục vít khi tắt điện.
- `print.yaml` giờ 8 bàn (thêm P8_Pins 100 %).
