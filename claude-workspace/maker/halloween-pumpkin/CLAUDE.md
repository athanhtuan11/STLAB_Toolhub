# halloween-pumpkin – bí ngô in 3D (đạo cụ video)

Mô tả, phương án dáng và số in: `README.md`. Quy ước CAD/in chung: skill `mechanical-design` + `tools/print/`.

## Cấu trúc
- `design/`: concept bước 0 (`concepts/*.png`, `contact-sheet.png`) – Tuan chọn bằng ảnh.
- `freecad/scripts/build_pumpkin.py`: sinh lưới tham số (không có file FreeCAD).
- `print/print.yaml`: cắt lớp `python ../../tools/print/scripts/slice.py print/print.yaml`.

## Lưu ý
- Nhựa: Bambu PETG Basic (mặc định); đổi cuộn sang xanh ở độ cao ghi trong README.
