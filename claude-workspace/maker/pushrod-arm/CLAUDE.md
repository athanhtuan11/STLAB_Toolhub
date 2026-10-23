# pushrod-arm – cánh tay robot xi-lanh đẩy (CyberBrick)

Mọi thứ của dự án nằm trong thư mục này (2026-10-23; trước đó ở `D:\06_FreeCAD\pushrod_arm` – không dùng nữa).
Cấu trúc chuẩn: `maker/robotics-cad/CLAUDE.md` mục "Dự án".

## FreeCAD – `freecad/`
- `pushrod_arm.FCStd`: lắp ráp, ~7 MB, **chỉ trên máy** (không lên git; bản sao lưu ở `backup/`).
- `pushrod_arm_rest.json`: tư thế gốc. `pushrod_arm_sim.FCMacro`: mô phỏng (macro FreeCAD → `pushrod_arm_sim`
  là file chuyển tiếp tới đây).
- `scripts/`: `kinematics_test.py` (quét tư thế + kẹp, chạy `freecadcmd`/`fc_job`, ra `check/`),
  `reset_rest_pose.py` (gửi qua RPC khi file bị Lưu lúc mô phỏng); `history/` = script sửa model đã chạy (chỉ đọc lại).
- `images/`: ảnh các bước lắp ráp. `check/`: kết quả kiểm nhanh (`overview.png`) – file sinh.

## Bàn in – `print/`
- `print.yaml`: hướng in từng chi tiết, tham số kiểm, 7 bàn in (profile A1 chính hãng + ghi đè). Nhựa mặc định
  **PETG KINGROON** (preset riêng của Tuan trong Bambu Studio, 8 mm³/s); đệm kẹp TPU 95A.
- `plates/<plate>/<plate>.3mf`: **file để mở Bambu Studio và in**; `plates/print-overview.png`: bảng + ảnh từng bàn.
- `stl/`: STL theo hướng in – file sinh.

## Làm việc
- Chuẩn bị in (~1–2 phút): Toolhub → Dự án → maker/pushrod-arm → **Chuẩn bị in** (hoặc **Tự chạy khi Lưu**), hay
  `"C:/Program Files/FreeCAD 1.1/bin/python.exe" maker/robotics-cad/scripts/prepare-print.py maker/pushrod-arm/print/print.yaml`
- Sửa model: theo quy ước `maker/robotics-cad/CLAUDE.md` (1 phiên giữ FreeCAD; `UndoCount == 0`; so `rest.json`;
  backup `freecad/backup/`; giữ `Placement`; sửa xong tự Lưu).
- In xong: `/print-result pushrod-arm <plate> pass|fail [mô tả]`.

## Trạng thái (2026-10-23)
- Kiểm nhanh: WARN, không FAIL. Cắt lớp PETG: PASS – 7 bàn, ~12 h 29, ~288 g. Support chỉ ở bàn P4 (Boom, khung kẹp,
  tai chốt 2 Housing). Nhanh hơn: hiệu chỉnh max volumetric speed (12 mm³/s → ~10 h 37).
- Chờ: in thật.
