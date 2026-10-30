---
task: model-study-fit-library
cwd: tools/model-study
allow: ["fit-library/fit_lib.py"]
read: ["test_fit_lib.py", "fit-library/fits.json", "measure_features.py"]
gate: '.venv\Scripts\python.exe test_fit_lib.py'
executor: auto
timeout_min: 25
max_rounds: 2
---

# Mục tiêu
Kho thông số lắp ghép STLab (Tuan 2026-10-30): AI/Claude thiết kế chi tiết lắp ghép phải tra kho thay vì tự đoán.
Dữ liệu `fit-library/fits.json` do Claude viết (KHÔNG sửa). Viết `fit-library/fit_lib.py` (thư viện + CLI) – hành vi
đúng = `test_fit_lib.py` (KHÔNG sửa test). Chỉ stdlib (json, statistics, argparse, os).

# Yêu cầu
- `DEFAULT = <thư mục file>/fits.json`. `FIT_TYPES = {"rotate","slide","press","clearance","self-tap","unknown"}`.
- `load(path=None) -> list[dict]`: đọc `entries`.
- `validate(entries) -> list[str]` (rỗng = hợp lệ). Mỗi lỗi là câu có **tên khóa** liên quan:
  thiếu khóa bắt buộc (`id, interface, fit, hole_mm, shaft_mm, clearance_mm, nominal_mm, source, confidence, verified`)
  → lỗi nêu tên khóa; `fit` ngoài FIT_TYPES; `hole_mm` và `shaft_mm` cùng None → lỗi chứa "hole_mm";
  có cả hole+shaft và clearance khác `hole − shaft` quá 0,005 → lỗi chứa "clearance"; `confidence` ngoài [0,1];
  `source` thiếu `model` hoặc `method` → lỗi chứa tên khóa đó; `id` trùng → lỗi chứa "id".
- `lookup(entries, interface) -> list`: các mục đúng interface, sắp: verified trước, rồi confidence giảm dần
  (bằng nhau giữ thứ tự gốc).
- `recommend(entries, interface) -> dict | None`: không có mục → None. Có mục verified → chỉ dùng chúng
  (`basis "verified"`), không thì dùng tất cả (`basis "community"`). Trả `{"interface", "basis", "n", "ids",
  "hole_mm", "shaft_mm", "clearance_mm", "fit"}`: mỗi kích thước = trung vị (`statistics.median`) các giá trị khác None,
  không có → None; `ids` theo thứ tự `lookup`; `fit` = fit phổ biến nhất.
- `add_from_features(path, features_json, feature_id, entry_id, interface, fit, model, nominal_mm=None, note="")`:
  đọc JSON của `measure_features.py` (object 1 file), tìm feature `id == feature_id` (không có → ValueError).
  `hole` → `hole_mm = d_mm`, `shaft_mm = None`; `boss` → ngược lại; `arc` → ValueError. `clearance_mm None`,
  `confidence` = của feature, `verified False`, `source = {"model", "parts": <basename file>#<feature_id>,
  "method": "stl-fit"}`, `print = {"printer": "TODO (tac gia)", "material": "TODO (tac gia)"}`. Validate cả kho sau khi
  thêm (id trùng / lỗi → ValueError, KHÔNG ghi). Ghi lại file giữ nguyên các khóa khác (`about`, `fit_types`),
  UTF-8, indent 1, ensure_ascii=False. Trả mục mới.
- CLI: `fit_lib.py check [--file F]` (in lỗi, exit 1 nếu có), `lookup <interface> [--file F]` (in JSON list),
  `recommend <interface> [--file F]` (in JSON; không có → in thông báo stderr, exit 1). Stdout UTF-8.
- Mã + chú thích ASCII không dấu.

# Không làm
- Không sửa `fits.json`, test, file khác.

# Tiêu chí PASS
- Gate exit 0.
