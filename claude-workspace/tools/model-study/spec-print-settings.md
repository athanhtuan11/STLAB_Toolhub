---
task: model-study-print-settings
cwd: tools/model-study
allow: ["study_3mf.py", "_out/**", "_out/*"]
gate: "python test_print_settings.py && python test_study.py && python test_render.py && python test_holes.py"
timeout_min: 20
max_rounds: 2
executor: codex
---

# Mục tiêu
`study_3mf.py` đọc thêm CẤU HÌNH IN theo object mà tác giả đặt trong `Metadata/model_settings.config` của 3MF Bambu
(bật support, kiểu support, extruder, số tường, infill…) để Claude biết tác giả cho chi tiết nào cần support và so với
`tools/robotics-cad/scripts/printability.py`. Học ý từ `docs/reports/cad-mesh-libs-study.md` mục 4 (KHÔNG chép mã OrcaSlicer).

# Yêu cầu
- Mỗi `<object id>` trong `model_settings.config`: mọi `<metadata key=... value=...>` cấp object (không lấy của `<part>`).
- `parts.csv` thêm 3 cột cuối: `support` (= `enable_support`, "" nếu không có), `support_type`, `print_settings`
  (JSON các key còn lại trừ `name`, sắp khóa). Thư mục STL (không phải 3MF) → để trống / `{}`.
- `summary.md` thêm mục `## Cau hinh in cua tac gia`: liệt kê chi tiết bật support (idx, tên, plate, support_type)
  + các key in khác biệt giữa các chi tiết.
- File GIỮ UTF-8 KHÔNG BOM (lần trước bị mojibake). Không đổi đầu ra hiện có khác; `test_study.py`,
  `test_render.py`, `test_holes.py` phải vẫn PASS.

# Không làm
- Không sửa test_*.py, render.py, measure_holes.py, measure_step.py, _sample/.
