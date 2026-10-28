---
task: toolhub-quote-v4-bulk
cwd: .
allow: ["studio/toolhub/quote.py", "studio/toolhub/views.py", "studio/toolhub/templates/quote.html", "studio/toolhub/templates/quote-print.html"]
read: ["studio/toolhub/quote_defaults.json", "studio/spec-quote-v3.md", "studio/tests/test_quote_bulk.py"]
gate: 'studio\.venv\Scripts\python.exe studio\tests\test_quote_bulk.py && studio\.venv\Scripts\python.exe studio\tests\test_quote.py && studio\.venv\Scripts\python.exe studio\tests\test_quote_slice.py && studio\.venv\Scripts\python.exe studio\tests\test_library_pages.py'
executor: opencode
timeout_min: 30
max_rounds: 2
---

# Mục tiêu
Tuan (2026-10-28): STLab chủ yếu in **mẫu có sẵn**, bán theo số lượng. Thêm **giá sỉ theo số lượng**, học theo bảng
giá đối thủ: móc khóa lẻ 18.000 → 50 cái 16.000 đ (−11 %) → 100 cái 15.000 đ (−17 %). Hiện mua 100 cái chỉ rẻ hơn
1 cái vài chục đồng. Ship **không** tính vào đơn giá (đã có ô "phí khác"; không đổi).
Hành vi đúng = `studio/tests/test_quote_bulk.py` (không sửa test); 3 test cũ vẫn PASS.
Claude đã thêm vào `quote_defaults.json` 4 khóa (có nguồn): `bulk1_min_qty` 50, `bulk1_discount_pct` 0.10,
`bulk2_min_qty` 100, `bulk2_discount_pct` 0.15. KHÔNG sửa file này.

# Yêu cầu
## `studio/toolhub/quote.py`
- `BULK_KEYS = ("bulk1_min_qty", "bulk1_discount_pct", "bulk2_min_qty", "bulk2_discount_pct")` – **không** đưa vào
  `SETTINGS_KEYS` (thiếu thì coi như không có giá sỉ, không raise). `save_settings` cho phép thêm BULK_KEYS.
- `compute(...)`: giữ nguyên cách tính `lines`, `cost`, `price` hiện tại. Sau đó:
  - bậc áp dụng = bậc có `min_qty` lớn nhất mà `q >= min_qty` (bỏ bậc có min_qty hoặc discount thiếu/≤ 0);
    `disc` = discount của bậc đó, không có thì 0.
  - **Học đối thủ (Claude sửa vòng 2):** đơn giá dựa trên **giá lẻ 1 cái** = `price` của cùng phép tính với
    `quantity=1` (cùng extras/materials_map), KHÔNG phải `price / q` (chia công chuẩn bị theo q làm giảm 2 lần:
    móc khóa 11.000 → 6.000 đ ở 50 cái). `raw = price_1 * (1 - disc)`; dưới bậc 1 → `raw = price_1` (giữ giá lẻ).
    Sàn: `raw = max(raw, cost / q)` (cost của SL q) → `bulk_floor = True` nếu sàn có tác dụng, không thì False.
    `unit_price_list` = giá lẻ 1 cái làm tròn.
  - `unit_price = ceil(raw / step - 1e-9) * step` (như cũ); `subtotal`, `total` như cũ.
  - Trả thêm: `bulk_discount_pct` (= disc, số 0 khi không giảm), `bulk_floor`, `unit_price_list` (giá lẻ 1 cái
    làm tròn, như trên), `next_bulk` = bậc kế tiếp có `min_qty > q`:
    `{"min_qty", "discount_pct", "unit_price"}` với `unit_price` = `compute(... quantity=min_qty ...)["unit_price"]`
    (cùng extras/materials_map/other_fee; tránh đệ quy vô hạn), không có thì `None`.

## `studio/toolhub/views.py`
- `/api/quote/pricing` GET/POST đi qua 4 khóa BULK như khóa khác. `_texts`: thêm `unit_price_list_text`.
  Trả `next_bulk` (+ `unit_price_text` trong đó) ở `/api/quote/price`, `/api/quote/calc`.
- Báo giá đã lưu giữ `bulk_discount_pct`, `unit_price_list` trong data_json để trang in đọc.

## `quote.html`
- Bảng giá (`META`): thêm 4 ô có `data-key` đúng tên khóa: "Giá sỉ bậc 1 – từ (cái)", "Giảm bậc 1 (0–1)",
  "Giá sỉ bậc 2 – từ (cái)", "Giảm bậc 2 (0–1)"; hiện nguồn như các ô khác.
- Dưới `#unit-line`: `<div id="bulk-line" hidden>` → khi `bulk_discount_pct > 0`: "Giá sỉ ≥{min} cái: −{x} %
  (giá lẻ {unit_price_list_text})"; `bulk_floor` → thêm "– đã chạm giá vốn". `<div id="bulk-hint" hidden>` → khi có
  `next_bulk`: "Mua từ {min_qty} cái: {unit_price_text}/cái (−{x} %)". Phần trăm kiểu Việt (dấu phẩy), chữ màu
  theo token sẵn có, không thêm hex.
- Cạnh ô số lượng: chữ nhỏ tóm tắt bậc ("Sỉ: ≥50 cái −10 %, ≥100 cái −15 %") từ bảng giá đang dùng.

## `quote-print.html`
- Có giảm sỉ → dòng ghi chú dưới bảng: "Đã áp giá sỉ ≥{min} cái: −{x} % (giá lẻ {đơn giá lẻ})". Không có → không hiện.

# Không làm
- Không đổi công thức giá vốn, không sửa test, không sửa `quote_defaults.json`, không thêm thư viện.
