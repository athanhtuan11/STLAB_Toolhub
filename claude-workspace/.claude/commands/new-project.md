---
description: Tạo dự án CAD/in 3D mới – mọi thứ trong maker/<name>/ (design/ + solidcraft/ + print/)
argument-hint: "<project-name-kebab-case> [mô tả 1 dòng]"
---

Tạo dự án mới. CAD mặc định là **SolidCraft** (2026-11-11: template FreeCAD cũ ở `backup/20261111-legacy-freecad/`).
Mẫu tham khảo: `maker/card-coding-robot/` (cấu trúc + `design/brief.md`) và `maker/esp32-s3-cam/solidcraft/`
(script dựng, `params.json`, `tests/`, `print/print.yaml`).

1. Lấy tên từ `$ARGUMENTS` (từ đầu tiên). Bắt buộc **tiếng Anh**, không dấu, kebab-case (vd. `line-follower`);
   sai thì hỏi lại.
2. Kiểm tra `claude-workspace/maker/<name>/` CHƯA tồn tại; có rồi thì DỪNG, báo Tuan (không ghi đè).
3. Tạo `maker/<name>/` gồm:
   - `CLAUDE.md`: quy ước riêng (mô tả 1 dòng, cấu trúc thư mục, lệnh dựng/kiểm/cắt lớp, trạng thái `TODO`).
   - `README.md`: mục tiêu, **An toàn** (pin/động cơ/nhiệt, `TODO` nếu chưa có datasheet), BOM, In, Lịch sử sửa, Lịch sử in.
   - `design/brief.md` theo mẫu `maker/card-coding-robot/design/brief.md`.
   - `solidcraft/` (trống, có `tests/`) và `print/`.
4. **Bước 0 – Giao diện** (Tuan 2026-10-24): điền `design/brief.md` cùng Tuan (mức A/B/C, cảm giác, kích thước),
   làm concept → `design/contact-sheet.png` cho Tuan chọn TRƯỚC khi dựng cơ khí (agent `product-designer`).
5. Dựng cơ khí theo skill `mechanical-design` (tra `fit-library` trước khi chọn lỗ/chốt/khe). Xuất `.sc` lắp ráp, mỗi
   chi tiết 1 component. Cắt lớp: `tools/print/scripts/slice.py <print.yaml>` (mẫu print.yaml của esp32-s3-cam).
   Không để dữ liệu dự án ở nơi khác (Documents, D:\...).
6. Commit + push (file sinh đã có trong `.gitignore`) – theo memory "tự lưu + tự push".
