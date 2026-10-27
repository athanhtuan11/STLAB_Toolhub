# cyberbrick-arm – tay máy 3 khớp + kẹp 3 ngón điều khiển CyberBrick (vẽ lại từ tham khảo tipflow)

Tạo 2026-10-27 theo `tools/robotics-cad/project-template/`. Cấu trúc chuẩn: `tools/robotics-cad/CLAUDE.md` mục "Dự án".

## Nguồn
- Tham khảo: `community/makerworld-tipflow-cyberbrick-robotic-arm/` – license chỉ dùng cá nhân: **không** đưa STL/ảnh
  của tác giả vào repo; bản STLab vẽ lại từ đầu. Ghi chú đo: `docs/research-notes/tipflow-robotic-arm-fits.md`.
- Công cụ học model: `tools/model-study/` (study_3mf.py, measure_holes.py, measure_step.py).

## Bước 0 – Giao diện – `design/` (làm TRƯỚC)
- `design/brief.md`: 3 hướng A/B/C chờ Tuan chọn. Chưa chọn thì chưa dựng cơ khí.

## FreeCAD – `freecad/`
- Dựng bằng script tham số (CLI trước, GUI để xem; GUI mở ở màn hình phụ). Khe lắp ghép tính bằng mm, in coupon thử.

## Bàn in – `print/`
- `print.yaml` (mẫu) – Bambu PETG Basic @BBL A1, Textured PEI. KHÔNG vẽ support vào STL (Tuan tô trong Bambu Studio).

## Trạng thái
- 2026-10-27: tạo dự án, brief bước 0 + bảng ảnh tham khảo; chờ Tuan chọn hướng/màu/cấp học.
