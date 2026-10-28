---
task: toolhub-quote-v2
cwd: studio
allow: ["toolhub/quote.py", "toolhub/views.py", "toolhub/templates/quote.html", "toolhub/templates/quote-print.html"]
read: ["toolhub/quote_defaults.json", "spec-quote.md"]
gate: '.venv\Scripts\python.exe tests\test_quote.py && .venv\Scripts\python.exe tests\test_library_pages.py'
executor: opencode
timeout_min: 30
max_rounds: 2
---

# Mục tiêu
Tuan (2026-10-28): "báo giá dựa vào mẫu in + chọn nhựa thôi; các chi phí kia auto-gen (vẫn sửa được theo thời giá)".
Tab `/quote` đã có (xem `spec-quote.md`). Thêm: **thời giá mặc định** từ `toolhub/quote_defaults.json` (Claude đã tra,
có nguồn – KHÔNG sửa file này), **chọn nhựa**, bảng giá gập lại. Hành vi đúng = `tests/test_quote.py`.

# Yêu cầu
## quote.py
- Nạp `quote_defaults.json` (cạnh file .py). `connect()`: khóa settings CHƯA có trong DB → ghi `value` mặc định; nhựa
  mặc định chưa có → thêm; phụ kiện mặc định: chỉ thêm khi bảng `extras` chưa có dòng cùng `label` (không nhân đôi).
  Bỏ dict `DEFAULTS` cũ (thay bằng file json).
- `reset_defaults(conn)`: ghi đè mọi settings + nhựa mặc định về giá trị file; phụ kiện mặc định cập nhật giá theo
  label (không tạo trùng); không xóa nhựa/phụ kiện Tuan tự thêm; không đụng `shop_*`, `payment_note`.
- `pricing_sources()` → `{key: {"source", "url"?, "gia_dinh"?}}` cho settings + `"material:<tên>"` cho nhựa.
- `save_settings`: giá trị `None` = xóa khóa (để compute báo thiếu).
- `compute(..., materials_map=None)`: `materials_map` {loại trong file → tên nhựa trong bảng giá}; loại không có trong
  map thì giữ tên gốc. Gộp gam theo nhựa ĐÃ CHỌN, tính filament theo giá nhựa đó. Nhựa không có trong bảng giá →
  `QuoteError` nêu tên (vd "ABS", "TPU"). Trả thêm `"materials": {tên nhựa đã chọn: tổng gam (1 sản phẩm)}`.
- `save_quote`: lưu cả `materials_map` + `materials` trong data_json; bản cho khách ghi vật liệu = nhựa đã chọn.

## views.py
- `/api/quote/calc` và `/api/quote/save` nhận `materials_map`. `GET /api/quote/pricing` thêm `"sources"`.
- `POST /api/quote/pricing/reset` → `reset_defaults` → trả get_pricing (+ sources).

## quote.html (luồng mới, bố cục vẫn như mockup đã duyệt)
1. **File in**: chọn/thả file → ngay dưới hiện `<div id="material-map">`: mỗi loại nhựa trong file một `<select>`
   (danh sách nhựa trong bảng giá, mặc định = cùng tên nếu có, không thì nhựa đầu tiên) + số gam.
2. Đổi file / nhựa / số lượng / phụ kiện → **tự tính lại** (không cần bấm nút). Giá vốn + Giá bán hiện ngay.
3. Tùy chọn (số lượng, phụ kiện, phí khác, khách, tiêu đề, ghi chú) + Lưu báo giá: giữ như cũ.
4. **Bảng giá** đưa vào `<details id="pricing-panel">` (đóng sẵn), tiêu đề "Bảng giá (thời giá – tự điền, sửa khi giá
   đổi)" + dòng "cập nhật <updated>". Dưới mỗi ô nhập hiện `source` (chữ nhỏ `--muted`; `gia_dinh` → nhãn "giả định"
   màu `--warn`; có `url` http → link mở tab mới). Nút `id="pricing-reset"` "Khôi phục thời giá mặc định" (confirm
   trước khi ghi đè). Lưu bảng giá xong → tự tính lại báo giá đang mở.
5. Lịch sử báo giá giữ nguyên.

## quote-print.html
- Số thập phân kiểu Việt (giờ `2,92 h`, gam `76,1 g`), vật liệu = nhựa đã chọn.

# Không làm
- KHÔNG sửa `tests/`, `toolhub/quote_defaults.json`, `static/*`, file ngoài `allow`. Không thêm thư viện/CDN.

# Tiêu chí PASS
- Gate exit 0. Claude chụp ảnh `/quote` (đã chọn file) + bản cho khách để duyệt.
