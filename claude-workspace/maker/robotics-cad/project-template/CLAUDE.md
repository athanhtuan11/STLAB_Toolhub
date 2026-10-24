# <project-name> – <mô tả 1 dòng>

Tạo bằng `/new-project`. Cấu trúc chuẩn: `maker/robotics-cad/CLAUDE.md` mục "Dự án". Mẫu đầy đủ: `maker/pushrod-arm/`.

## Bước 0 – Giao diện – `design/` (làm TRƯỚC, Tuan 2026-10-24)
- `brief.md` → 3 concept + `cmf.png` + render + mockup UI (nếu có) → `contact-sheet.png` → Tuan chọn bằng ảnh.
- Chưa chọn concept thì chưa dựng cơ khí. Hệ thiết kế: `studio/design/DESIGN.md`.

## FreeCAD – `freecad/`
- `<model>.FCStd` (chỉ trên máy), `<model>_rest.json` (tư thế gốc, nếu có mô phỏng), `scripts/`, `images/`.
- `check/`, `backup/`: file sinh / bản sao lưu (không lên git).

## Bàn in – `print/`
- `print.yaml`: hướng in + tham số kiểm + bàn in. `plates/<plate>/<plate>.3mf`: file để in. `stl/`: file sinh.

## Làm việc
- Chuẩn bị in: Toolhub → Dự án → **Chuẩn bị in** / **Tự chạy khi Lưu**, hoặc
  `"C:/Program Files/FreeCAD 1.1/bin/python.exe" maker/robotics-cad/scripts/prepare-print.py maker/<project-name>/print/print.yaml`
- Sửa model theo quy ước `maker/robotics-cad/CLAUDE.md`; in xong `/print-result`.

## Trạng thái
- TODO
