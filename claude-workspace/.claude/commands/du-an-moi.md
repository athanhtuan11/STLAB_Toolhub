---
description: Tạo dự án CAD/in 3D mới theo mẫu chuẩn (repo maker/<ten> + dữ liệu D:\06_FreeCAD\<ten_du_an>)
argument-hint: "<ten-du-an-kebab-case> [mô tả 1 dòng]"
---

Tạo dự án mới theo `maker/robotics-cad/mau-du-an/` (quy trình: `maker/robotics-cad/CLAUDE.md` mục "Dự án mới").

1. Lấy tên từ `$ARGUMENTS` (từ đầu tiên). Bắt buộc không dấu, kebab-case (vd. `xe-do-line`); sai thì hỏi lại.
   Tên thư mục dữ liệu = tên đó đổi `-` thành `_` (vd. `xe_do_line`).
2. Kiểm tra `claude-workspace/maker/<ten>/` và `D:\06_FreeCAD\<ten_du_an>\` CHƯA tồn tại; có rồi thì DỪNG, báo Tuan
   (không ghi đè).
3. Chép `maker/robotics-cad/mau-du-an/` → `maker/<ten>/`; thay `<ten-du-an>`, `<ten_du_an>`, `<mô tả 1 dòng>`
   trong `CLAUDE.md`, `README.md`, `in_3d/ban-in.yaml`.
4. Tạo `D:\06_FreeCAD\<ten_du_an>\` với `_backup\`, `_work\`, `in_3d\` (trống). Không tạo file `.FCStd`
   (Tuan dựng trong FreeCAD, lưu đúng tên `<ten_du_an>.FCStd`).
5. Nhắc Tuan: đặt tên Label theo quy ước (`CB_`/`LK_` linh kiện mua, `_TPU`, `_L`/`_R`, `Gear_`/`Pinion_`),
   khai hướng in trong `in_3d/ban-in.yaml` mục `xuat.quy_tac`, rồi bấm **Chuẩn bị in** ở Toolhub → Dự án.
6. Commit + push phần trong repo (theo memory "tự lưu + tự push"): `maker/<ten>/`.
