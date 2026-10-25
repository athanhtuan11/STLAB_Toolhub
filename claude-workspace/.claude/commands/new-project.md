---
description: Tạo dự án CAD/in 3D mới theo mẫu chuẩn – mọi thứ trong maker/<name>/ (freecad/ + print/)
argument-hint: "<project-name-kebab-case> [mô tả 1 dòng]"
---

Tạo dự án mới từ `tools/robotics-cad/project-template/` (cấu trúc: `tools/robotics-cad/CLAUDE.md` mục "Dự án").

1. Lấy tên từ `$ARGUMENTS` (từ đầu tiên). Bắt buộc **tiếng Anh**, không dấu, kebab-case (vd. `line-follower`);
   sai thì hỏi lại. Tên file model = tên đó đổi `-` thành `_` (vd. `line_follower.FCStd`).
2. Kiểm tra `claude-workspace/maker/<name>/` CHƯA tồn tại; có rồi thì DỪNG, báo Tuan (không ghi đè).
3. Chép `project-template/` → `maker/<name>/`; thay `<project-name>`, `<model>`, `<mô tả 1 dòng>` trong
   `CLAUDE.md`, `README.md`, `print/print.yaml`. Tạo `freecad/scripts/`, `freecad/images/` (trống).
3b. **Bước 0 – Giao diện** (Tuan 2026-10-24): điền `design/brief.md` cùng Tuan (hỏi mức A/B/C, cảm giác, kích thước, cuộn nhựa), rồi làm concept → `design/contact-sheet.png` cho Tuan chọn TRƯỚC khi dựng cơ khí.
4. Không tạo file `.FCStd` – Tuan dựng trong FreeCAD và Lưu đúng `maker/<name>/freecad/<model>.FCStd`.
   Không để dữ liệu dự án ở nơi khác (Documents, D:\...).
5. Nhắc Tuan: tên Label theo quy ước (`CB_`/`LK_` linh kiện mua, `_TPU`, `_L`/`_R`, `Gear_`/`Pinion_`),
   khai hướng in trong `print/print.yaml` mục `export.rules`, rồi bấm **Chuẩn bị in** ở Toolhub → Dự án.
6. Commit + push phần lên git (`.FCStd` và file sinh đã có trong `.gitignore`) – theo memory "tự lưu + tự push".
