---
task: hidden-parts-stl-volume
cwd: tools/robotics-cad
allow:
  - "scripts/check.py"
  - "scripts/export-stl.py"
  - "scripts/prepare-print.py"
  - "model-checks.md"
gate: "\"C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe\" --safe-mode -P tests -t test_hidden_stl"
timeout_min: 25
max_rounds: 2
executor: opencode
---

# Mục tiêu
Đưa 2 bài học trong `harness-lab/inbox.md` (2026-10-25) vào công cụ kiểm:
1. Chi tiết **ẩn** đang bị `check.py` bỏ qua im lặng (`chi_tiet_la` bỏ `Visibility == False`), trong khi
   `export-stl.py` vẫn xuất STL cho nó → chi tiết được in mà chưa kiểm. Phải liệt kê ra và FAIL.
2. Kiểm phải chạy trên **artifact cuối**: `export-stl.py` so thể tích STL với thể tích model từng file.

# Đầu vào
- Gate `tests/test_hidden_stl.py` (Claude viết, KHÔNG sửa) – đặc tả chính xác tên khóa JSON.
- `scripts/check.py` (hàm `chi_tiet_la`, `tham_so`, `main`), `scripts/export-stl.py`, `scripts/prepare-print.py`.

# Yêu cầu
## check.py
- Tham số mới `hidden-ok` (dạng `khoa=gia-tri` như các tham số khác, glob theo Label, nhiều mẫu cách nhau dấu phẩy).
- "Chi tiết ẩn" = đối tượng trong `doc.Objects`: `isDerivedFrom("Part::Feature")`, `Shape.Solids` khác rỗng,
  `Visibility == False`, và **không** có đối tượng `Part::Feature` nào trong `InList` (tức không phải đầu vào của
  boolean/feature khác – giống tiêu chí "lá" trong `metrics.py`). Danh sách Label sắp xếp tăng dần.
- `report.json` thêm khóa `chi_tiet_an`: `{"trang_thai", "nhan": [...], "cho_phep": [...mẫu hidden-ok...]}`.
  `trang_thai` = `"PASS"` nếu rỗng; `"INFO"` nếu mọi chi tiết ẩn khớp `hidden-ok`; ngược lại `"FAIL"`.
- `trang_thai` này gộp vào `ket_luan` (FAIL → ket_luan FAIL, exit 1). INFO không ảnh hưởng.
- In 1 dòng tóm tắt khi có chi tiết ẩn: `CHI TIET AN (khong kiem): A, B` kèm gợi ý dùng `hidden-ok=`.
- Ảnh `overview.png` không bắt buộc đổi.
- Không đổi hành vi khác (cache, tiến trình con, va chạm...).

## export-stl.py
- Với mỗi STL ghi ra: `model_mm3` = thể tích solid trước khi chia lưới (`so.Volume`), `stl_mm3` = `Mesh.Volume` của
  lưới vừa tạo, `lech_pct = (stl - model) / model * 100` (làm tròn 3 chữ số). Ghi vào `_export-stl.json` khóa
  `the_tich: {<tên file>: {model_mm3, stl_mm3, lech_pct}}`.
- Ngưỡng (Claude chốt): `|lech_pct| > 2.0` → `FAIL`; `> 0.5` → `WARN`. Khóa `stl_lech`: danh sách
  `{file, lech_pct, trang_thai}` chỉ gồm file WARN/FAIL. Không đổi exit code của export-stl.py.

## prepare-print.py
- Thêm một dòng kết quả `("STL so với model", ...)` đọc `the_tich`/`stl_lech` từ `_export-stl.json`: FAIL nếu có mục
  FAIL, WARN nếu có WARN, ngược lại PASS; chi tiết liệt kê `file: lech x %`.
- STL lệch FAIL thì **không** cắt lớp (như lỗi khả năng in), trừ khi có `force`.
- Kết quả `chi_tiet_an` từ báo cáo check.py: nếu có, thêm vào chi tiết của dòng tầng 1 (tên các chi tiết ẩn).
- `model-checks.md`: thêm 2 gạch đầu dòng mô tả 2 kiểm mới + ngưỡng + tham số `hidden-ok` (tiếng Việt, ngắn).

# Không làm
- Không sửa `tests/`, `thresholds.yaml`, file `.FCStd`, `print.yaml` của dự án.
- Không đổi cách chia lưới, hướng in, tên file STL.

# Tiêu chí PASS
- Gate exit 0.
- Claude tự chạy prepare-print trên cyberbrick-car và pushrod-arm để xem có cảnh báo mới không.
