# pushrod-arm – cánh tay robot xi-lanh đẩy (CyberBrick)

Dự án đầu tiên theo quy trình chuẩn `maker/robotics-cad` (mẫu: `maker/robotics-cad/mau-du-an/`).

## Ở đâu
- **Trong repo (nguồn, lên git):** thư mục này – `README.md` (mục tiêu, BOM, lịch sử), `in_3d/ban-in.yaml`
  (hướng in + tham số kiểm + bàn in), `anh/` (ảnh kết quả của bản đã duyệt).
- **Ngoài repo (dữ liệu nặng):** `D:\06_FreeCAD\pushrod_arm\` – `pushrod_arm.FCStd` (lắp ráp, ~8 MB),
  `pushrod_arm_rest.json` (tư thế gốc), `pushrod_arm_sim.FCMacro` (mô phỏng), `_backup/`, `_work/` (script nháp),
  `in_3d/STL`, `in_3d/PLATES_cat-lop` (file sinh – không sửa tay).

## Làm việc
- Chuẩn bị in (kiểm + xuất STL + cắt lớp, ~1–2 phút):
  `"C:/Program Files/FreeCAD 1.1/bin/python.exe" maker/robotics-cad/scripts/chuan-bi-in.py maker/pushrod-arm/in_3d/ban-in.yaml`
  hoặc nút **Chuẩn bị in** / **Tự chạy khi Lưu** ở Toolhub → Dự án → maker/pushrod-arm.
- Sửa model: theo quy ước `maker/robotics-cad/CLAUDE.md` (1 phiên giữ FreeCAD; kiểm `UndoCount`; backup `_backup/`;
  giữ `Placement`; sửa xong tự Lưu). File từng bị **Lưu lúc đang mô phỏng** (23/10 13:34) → luôn về tư thế gốc trước khi sửa.
- In xong: `/ket-qua-in` ghi kết quả (đạt/lỗi) vào README + `harness-lab/inbox.md`.

## Còn chờ Tuan quyết (2026-10-23)
- Hốc servo kẹp trong `Gripper_frame` khít 0,15 mm (cả 2 phía, mặt lớn ~800 mm²): giữ (kẹp chặt servo) hay mài 0,05 mm?
- Washer trục bánh vít đã mài 1,2 → 1,1 mm (khe bánh vít 0,2 mm) → độ rơ dọc trục bánh vít 0,1 → 0,3 mm: chấp nhận không?
- `Jaw_1_driven_by_servo`: lưới tự cắt (slicer vẫn cắt được) – cần soi.
- 4 vấu bắt vít deck trong `Base_housing` treo z ≈ 21 mm → đang dùng support (+0,7 g); muốn bỏ thì thêm vát 45° dưới vấu.
