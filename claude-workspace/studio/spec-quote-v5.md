---
task: toolhub-quote-v5-model-extras
cwd: .
allow: ["studio/toolhub/quote.py", "studio/toolhub/views.py", "studio/toolhub/templates/quote.html"]
read: ["studio/tests/test_quote_model_extras.py", "studio/spec-quote-v4.md"]
gate: 'studio\.venv\Scripts\python.exe studio\tests\test_quote_model_extras.py && studio\.venv\Scripts\python.exe studio\tests\test_quote.py && studio\.venv\Scripts\python.exe studio\tests\test_quote_bulk.py && studio\.venv\Scripts\python.exe studio\tests\test_quote_slice.py && studio\.venv\Scripts\python.exe studio\tests\test_library_pages.py'
executor: auto
timeout_min: 30
max_rounds: 2
---

# Mục tiêu
Tuan (2026-10-30): phụ kiện (nam châm, insert, vít…) **Tuan tự chọn + nhập số lượng bằng tay** cho từng sản phẩm.
Tab Báo giá phải **nhớ lại theo mẫu (tên file)**: lần sau thả cùng mẫu thì ô phụ kiện tự điền sẵn, vẫn sửa tay được.
Hành vi đúng = `studio/tests/test_quote_model_extras.py` (KHÔNG sửa test). 4 test cũ vẫn PASS.

# Yêu cầu
## `studio/toolhub/quote.py`
- `model_key(name)`: `name` là chuỗi hoặc list chuỗi.
  - Một tên: `Path(name.strip()).name`, bỏ đuôi cuối (`.3mf/.stl/.obj/.step/.stp`, không phân biệt hoa thường),
    rồi bỏ thêm `.gcode` nếu còn ở cuối; `.strip()`; chữ thường. Ví dụ `"Moc-Khoa.gcode.3mf"` → `"moc-khoa"`,
    `"  Moc Khoa .step "` → `"moc khoa"`.
  - List: key từng tên, bỏ rỗng, sắp xếp, nối bằng `"+"`. Rỗng → `""`.
- Bảng mới trong `connect()`: `CREATE TABLE IF NOT EXISTS model_extras(model_key TEXT PRIMARY KEY,
  extras_json TEXT, updated_at TEXT)`.
- `save_model_extras(conn, key, extras)`: key rỗng → trả `None`, không ghi. Chuẩn hóa: khóa `int(k)` (bỏ khóa lỗi),
  chỉ giữ id có trong bảng `extras` (active=1), số lượng `int(v)`; bỏ số ≤ 0. Ghi đè cả bản ghi (upsert),
  `updated_at = datetime.now().isoformat(timespec="seconds")`. Kết quả rỗng `{}` **vẫn lưu**. Trả
  `{"extras": {str(id): n}, "updated_at": ...}`.
- `get_model_extras(conn, key)`: không có → `None`; có → cùng dạng trên, **lọc bỏ id không còn active** trong `extras`.

## `studio/toolhub/views.py`
- Hàm phụ `_model_info(names)` → `{"model_key": ..., "saved_extras": get_model_extras(...) hoặc None}`
  (mở/đóng conn như `_pricing_now`).
- `/api/quote/upload`: key từ list `names`. `/api/quote/parse` (cả nhánh upload file và nhánh `path` dự án): key
  từ `name`. Thêm 2 trường trên vào JSON trả về. Lưu `model_key` vào `_parsed[token]`.
- `POST /api/quote/model-extras` body `{token, extras}`: cùng kiểu chặn X-Studio như các POST khác của tab
  (không có header → 403). Token không có hoặc không có `model_key` → 400 `{"error": ...}`. Thành công → 200
  `{"model_key", "extras", "updated_at"}`.

## `studio/toolhub/templates/quote.html`
- Dưới tiêu đề "Phụ kiện (số lượng mỗi sản phẩm)" thêm `<p id="extras-note" class="muted"></p>`.
- `handleToken(j)`: nếu `j.saved_extras` có → đặt mọi ô `#extra-counts input[data-id]` = số đã lưu (không có → 0),
  ghi note `Đã điền theo lần trước (dd/mm/yyyy) – sửa số sẽ nhớ lại cho mẫu “<model_key>”.`
  Nếu không có → đặt tất cả = 0, note `Mẫu mới – chọn phụ kiện bằng tay, Toolhub sẽ nhớ cho lần sau.`
  Không được giữ số của file trước sang file mới. Thứ tự: điền xong mới gọi `schedulePrice()`.
- `renderCounts()` khi bảng giá nạp lại: giữ số đang nhập như cũ (không đổi hành vi).
- Khi Tuan sửa một ô phụ kiện (và đã có `token`): ngoài `schedulePrice` cũ, debounce ~800 ms rồi
  `POST /api/quote/model-extras` với `{token, extras: extrasMap()}` (header như các POST JSON khác, `HJ`);
  thành công → note `Đã nhớ phụ kiện cho mẫu “<model_key>”.`; lỗi → `toast(false, ...)`.

# Không làm
- Không nhận dạng theo hình học/hash, không đọc BOM dự án, không tự đếm lỗ.
- Không đổi cách tính giá `compute`, không đổi `quote_defaults.json`, không sửa các test.

# Tiêu chí PASS
- Gate exit 0.
- Claude tự kiểm thêm: mở /quote, thả file 2 lần, ô phụ kiện tự điền lần 2.
