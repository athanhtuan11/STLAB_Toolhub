---
task: toolhub-quote
cwd: studio
allow: ["toolhub/quote.py", "toolhub/views.py", "toolhub/templates/quote.html", "toolhub/templates/quote-print.html", "toolhub/templates/base.html"]
read: ["tools/robotics-cad/scripts/slice.py", "tools/robotics-cad/scripts/assembly-pdf.py", "community/printcalc/PRICING.md", "studio/design"]
gate: '.venv\Scripts\python.exe tests\test_quote.py && .venv\Scripts\python.exe tests\test_library_pages.py'
executor: opencode
timeout_min: 30
max_rounds: 2
---

# Mục tiêu
Tab **Báo giá** (`/quote`) trong Toolhub: thả file Bambu `.gcode.3mf` (hoặc chọn `.3mf` của dự án) → tính giá vốn
→ giá bán → lưu báo giá → bản cho khách (HTML in A4 + PDF). Bảng giá và báo giá lưu **SQLite** (Tuan 2026-10-28:
"chỉ tạo database và lưu lại được" – Tuan tự nhập giá trên trang, không có file YAML). Đọc `tests/test_quote.py`:
đó là hành vi đúng (tên hàm, khóa, số tiền).

# Yêu cầu
## `toolhub/quote.py` (chỉ thư viện chuẩn: sqlite3, zipfile, xml.etree, base64, math)
- `QuoteError(Exception)` – thông điệp tiếng Việt có dấu.
- `read_3mf(path | file-like)` đọc `Metadata/slice_info.config`: mỗi `<plate>` → `{"index", "seconds"`(int của
  metadata `prediction`)`, "grams": {type: tổng used_g}, "image_png": bytes của Metadata/plate_<index>.png hoặc None}`;
  thêm `hours` (tổng giây/3600) và `grams` (cộng mọi bàn). Không phải zip / không có slice_info → `QuoteError`
  có cụm "cắt lớp" (gợi ý: File → Export → Export plate sliced file trong Bambu Studio).
- DB: đường dẫn = env `STLAB_QUOTES_DB`, mặc định `%LOCALAPPDATA%\stlab-quotes\quotes.db` (tạo thư mục). **Không
  bao giờ trong repo** (có tên/SĐT khách). `connect()` tạo bảng nếu chưa có:
  `settings(key PK, value TEXT JSON, updated_at)`, `materials(name PK, spool_price_vnd, spool_weight_g, updated_at)`,
  `extras(id INTEGER PK, label, price_vnd, active)`, `quotes(id INTEGER PK, number UNIQUE, created_at, customer_name,
  customer_phone, title, note, total_vnd, data_json)`. Mặc định khi chưa có: `round_to_vnd=1000`, `valid_days=7`,
  `pricing_method="markup"`.
- `get_pricing(conn)` → `{"settings": {...}, "materials": {name: {"spool_price_vnd", "spool_weight_g"}}, "extras":
  [{"id","label","price_vnd"}]}` (số giữ kiểu int nếu nguyên). `save_settings(conn, dict)` (chỉ nhận khóa trong
  danh sách SETTINGS_KEYS bên dưới + `shop_phone`, `shop_contact`, `payment_note`), `save_material`, `delete_material`,
  `save_extra(conn, label, price_vnd, id=None) -> id`, `delete_extra`.
- `compute(parsed, pricing, quantity=1, extras=None, other_fee_vnd=0)` – Q = quantity, H = parsed["hours"],
  N = số bàn. Thiếu khóa bắt buộc hoặc thiếu giá nhựa có trong file → `QuoteError` liệt kê TẤT CẢ tên thiếu.
  ```
  filament     = Σ_type grams[type] × spool_price_vnd/spool_weight_g × Q
  electricity  = printer_power_w/1000 × H × electricity_price_vnd_per_kwh × Q
  depreciation = machine_price_vnd/machine_lifetime_hours × H × Q
  labor        = labor_rate_vnd_per_hour × (setup_hours_per_job + post_hours_per_plate × N × Q)
  extras       = Σ price_vnd[id] × count[id] × Q          (count = số mỗi sản phẩm)
  failure      = failure_pct × (filament + electricity + depreciation)
  cost         = tổng 6 dòng
  price        = cost × (1 + v)  (markup)   |   cost / (1 − v)  (margin, v phải < 1)
  unit_price   = ceil(price / Q / round_to_vnd) × round_to_vnd
  subtotal     = unit_price × Q ;  total = subtotal + other_fee_vnd   (phí khác không nhân markup)
  ```
  Trả `{"lines": {...6 dòng}, "cost", "price", "unit_price", "subtotal", "other_fee", "total", "quantity", "hours",
  "grams", "method", "value"}`. SETTINGS_KEYS bắt buộc: electricity_price_vnd_per_kwh, printer_power_w,
  machine_price_vnd, machine_lifetime_hours, labor_rate_vnd_per_hour, setup_hours_per_job, post_hours_per_plate,
  failure_pct, pricing_method, pricing_value, round_to_vnd.
- `fmt_vnd(n)` → `"1.234.000 đ"`.
- `save_quote(conn, customer_name, customer_phone, title, parsed, calc, note) -> id`: số `BG-YYYYMMDD-NN` (NN tăng
  trong ngày); `data_json` giữ calc + tóm tắt bàn (giờ, gam) + ảnh bàn 1 (base64) + bảng giá lúc lập + `valid_days`.
  `get_quote(conn, id)` (dict, `None` nếu không có), `list_quotes(conn, limit=50)` mới nhất trước.
- `project_3mf_files()` → list `Path` tất cả `maker/*/print/plates/*/*.3mf` (ROOT từ `workspace.py`).

## `toolhub/views.py`
- `GET /quote` → `quote.html`; `GET/POST /api/quote/pricing` (POST nhận `settings`, `materials` (dict; giá trị
  `null` = xóa), `extras` (list; không có `id` = thêm, `delete: true` = xóa) → trả get_pricing).
- `POST /api/quote/parse`: multipart `file` **hoặc** JSON `{"path": rel}` – path chỉ nhận nếu khớp đúng một phần tử
  `project_3mf_files()` (không thì 404). Lưu bản parse trong bộ nhớ (dict token → parsed, giữ ≤ 20 mục) → trả
  `{"token", "name", "hours", "grams", "plates": [{index, seconds, grams, image: "data:image/png;base64,..." | null}]}`.
  `QuoteError`/zip hỏng → 400 `{"error"}`.
- `POST /api/quote/calc` `{token, quantity, extras: {id: count}, other_fee_vnd}` → compute + các trường `*_text`
  (fmt_vnd) cho `total`, `unit_price`, `cost`, `subtotal`; lỗi → 400 `{"error"}`.
- `POST /api/quote/save` (thêm customer_name, customer_phone, title, note) → `{"id", "number"}`.
- `GET /quote/<int:id>` → `quote-print.html`; không có → 404. `GET /quote/<int:id>/pdf` → Edge headless
  `--print-to-pdf` (làm như `assembly-pdf.py`: tìm msedge, `--user-data-dir` tạm, file HTML tạm đã render, font từ
  `static/fonts` bằng file URI) → `application/pdf`, tên `BG-....pdf`.
- `GET /api/quote/projects` → list rel path `.3mf` (cho ô chọn).
- POST đã có kiểm `X-Studio` chung trong `create_app` – không bỏ.

## `quote.html` (extends base.html; bố cục mockup Tuan đã duyệt, KHÔNG có nút Zalo)
Cột trái: **1. File in** (vùng thả + `<input id="file" type="file" accept=".3mf">` + `<select>` file dự án; hiện ảnh
bàn, giờ, gam), **2. Tùy chọn** (`id="quantity"`, mỗi extra một ô số đếm/sản phẩm, phí khác, tên + SĐT khách, tiêu
đề), **3. Giá vốn** (6 dòng + Giá vốn + Giá bán màu `--highlight`; lỗi thiếu giá hiện chữ `--warn` kèm link tới
bảng giá), nút **Lưu báo giá** (lưu xong mở `/quote/<id>` tab mới, có nút Xuất PDF ở đó).
Cột phải / bên dưới: **Bảng giá** `<form id="pricing-form">` sửa và Lưu: settings (nhãn tiếng Việt + đơn vị), bảng nhựa
(thêm/xóa), phụ kiện (thêm/xóa), thông tin cửa hàng (SĐT, liên hệ, ghi chú thanh toán). **Lịch sử báo giá**: 20 cái mới
nhất (số, ngày, khách, tổng, link). JS thuần, `fetch` POST luôn gửi header `X-Studio: 1`. Màu chỉ `var(--…)`.

## `quote-print.html` (trang độc lập, nền trắng, A4 `@page`, KHÔNG extends base)
Như mockup bên phải: STLab + "Trung tâm STEAM · Đức Trọng, Lâm Đồng", SĐT/liên hệ từ settings (trống thì bỏ dòng),
"BÁO GIÁ IN 3D", số, ngày, khách, SĐT, hiệu lực (ngày + valid_days), bảng (ảnh bàn, tiêu đề, vật liệu, SL, đơn giá,
thành tiền; phụ kiện ghi trong mô tả), phí khác, Tổng cộng, ghi chú (+ payment_note), "Người lập báo giá / Tuan".
KHÔNG hiện giá vốn/khấu hao/công. Nút "Xuất PDF" + "In" ẩn khi in (`@media print`).

## base.html
Thêm `/quote` "Báo giá" vào menu "Thêm ▾" (theo cách các mục khác).

# Không làm
- KHÔNG sửa `tests/`, `static/style.css`, `static/tokens.css`, `community/`, file khác ngoài `allow`.
- Không thêm thư viện pip/CDN. Không ghi DB vào repo. Không ghi dữ liệu khách ra log.

# Tiêu chí PASS
- Gate exit 0. Claude chạy thêm `QUOTE_PDF=1` và xem ảnh trang `/quote` + PDF.
