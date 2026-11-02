# line-bot – xe dò line + tránh vật cản

- Chuẩn luật = RCJ Rescue Line (`docs/research-notes/line-robot-competitions.md`).
- Bộ điều khiển = arduino-mega-2560 (thư viện Toolhub).

Tạo bằng `/new-project`. Cấu trúc chuẩn: `tools/robotics-cad/CLAUDE.md` mục "Dự án". Mẫu đầy đủ: `maker/pushrod-arm/`.

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
  `"C:/Program Files/FreeCAD 1.1/bin/python.exe" tools/robotics-cad/scripts/prepare-print.py maker/line-bot/print/print.yaml`
- Sửa model theo quy ước `tools/robotics-cad/CLAUDE.md`; in xong `/print-result`.

## Trạng thái
- Bước 0 xong (2026-11-01): concept **A – Khung tầng**, lớp 6. Giai đoạn 1: chờ Tuan chụp ảnh linh kiện có sẵn (Tuan 2026-11-01) → Claude đọc mã in trên linh kiện, chốt module + thêm thư viện Toolhub.
- 2026-11-02: `print/print.yaml` xong, prepare-print PASS/WARN: 2 bàn (P1 Base 1h42 47 g, P2 Top + gá 1h59 67 g;
  tổng 3h41 114 g PETG). Sửa HC-SR04 dựng sai chiều (đâm pin) + gate test_10. WARN duy nhất: Motor_mount trần hốc
  motor là cầu 12,4 mm ở z 12,4 – PETG cầu được, không bắt buộc tô support. Số linh kiện vẫn là giả định → chờ ảnh
  linh kiện thật rồi mới in.
