---
task: toolhub-quote-v6-catalog
cwd: studio
allow: ["toolhub/catalog.py", "toolhub/views.py", "toolhub/templates/quote.html", "toolhub/templates/quote-catalog.html"]
read: ["tests/test_quote_catalog.py", "spec-quote-v5.md"]
gate: '.venv\Scripts\python.exe tests\test_quote_catalog.py && .venv\Scripts\python.exe tests\test_quote_model_extras.py && .venv\Scripts\python.exe tests\test_quote_bulk.py && .venv\Scripts\python.exe tests\test_quote_slice.py'
executor: coder
timeout_min: 40
max_rounds: 2
---

# Mục tiêu
Tuan (2026-11-03): mỗi lần lưu báo giá thì thông tin **mẫu** (tên, ảnh, khối lượng, giá lẻ, giá sỉ) vào DB (bảng
`catalog`), để sau này **xuất 1 lần ra Excel toàn bộ mẫu**. Ảnh mẫu có **phông nền STLab** (bàn gỗ + bảng STLab)
ghép offline. Hành vi đúng = `tests/test_quote_catalog.py` (KHÔNG sửa test). 3 test quote cũ (model_extras, bulk, slice) vẫn PASS; `test_quote.py` FAIL sẵn từ trước (file thật P2 đổi số) – không thuộc việc này.
Thư viện đã cài sẵn trong `studio/.venv` (Claude đã `uv add`): openpyxl 3.1, pillow 12, onnxruntime 1.31, numpy 2.
Ảnh nền `toolhub/static/quote/stlab-desk.jpg` (1672×941) Claude đặt sẵn – không sửa/xóa.

# Yêu cầu

## `toolhub/catalog.py` (mới)
- `PLATE = Path(__file__).parent / "static" / "quote" / "stlab-desk.jpg"`.
- `photo_dir()` = `quote._db_path().parent / "catalog-photos"` (mkdir parents). Ảnh lưu `<id>.jpg`, JPEG q=88.
- `ensure(conn)`: `CREATE TABLE IF NOT EXISTS catalog(id INTEGER PRIMARY KEY, model_key TEXT UNIQUE, name TEXT,
  grams REAL, unit_price REAL, price_bulk1 REAL, price_bulk2 REAL, material TEXT, hours REAL, quote_id INTEGER,
  photo TEXT, note TEXT, created_at TEXT, updated_at TEXT)`. Mọi hàm dưới tự gọi `ensure`.
- Số trả về: REAL nguyên → `int` (41.0 → 41); `None` giữ `None`. `get(conn,id)` → dict hoặc `None`;
  `list_all(conn)` → list dict, `ORDER BY id`.
- `create(conn, name, grams=None, unit_price=None, price_bulk1=None, price_bulk2=None, note="")` → id
  (`model_key` NULL = mẫu nhập tay).
- `update(conn, id, **fields)`: chỉ nhận `name, grams, unit_price, price_bulk1, price_bulk2, note`, bỏ khóa lạ.
  Trường số: `""`/`None` → NULL, chuỗi số → float. Cập nhật `updated_at`. Trả bản ghi mới (hoặc `None` nếu không có).
- `delete(conn, id)`: xóa dòng + file ảnh nếu có.
- `upsert_from_quote(conn, model_key, name, parsed, pricing, extras=None, materials_map=None, quote_id=None)` → id:
  - `c1 = quote.compute(parsed, pricing, quantity=1, extras=extras, materials_map=materials_map)`;
    `unit_price = c1["unit_price_list"]`. Với `k in (1, 2)`: nếu settings có `bulk{k}_min_qty` > 0 →
    `price_bulk{k} = quote.compute(..., quantity=int(ceil(min_qty)))["unit_price"]`, không có → NULL.
  - `grams = round(sum(c1["materials"].values()), 1)`; `material = " + ".join(c1["materials"])`;
    `hours = parsed["hours"]`.
  - Đã có dòng cùng `model_key` → cập nhật số liệu + `quote_id` + `updated_at`; **giữ `note`, `photo`**; `name` chỉ đổi
    khi `name` mới khác rỗng. Chưa có → thêm dòng, `name = name or model_key`.
- `has_alpha(img)`: True nếu ảnh có kênh alpha và ≥ 5 % điểm có alpha < 250.
- `cutout_u2net(img) -> RGBA` (onnxruntime, CPU): model `os.environ.get("STLAB_U2NET")` hoặc `~/.u2net/u2net.onnx`;
  thiếu → tải từ `https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx` (urllib, ghi file tạm rồi
  đổi tên). Tiền xử lý như rembg: RGB → resize 320×320 LANCZOS → `/max` → trừ mean (0.485,0.456,0.406) chia std
  (0.229,0.224,0.225) → NCHW float32; lấy output[0][:,0], chuẩn hóa min–max → resize về cỡ gốc → làm alpha.
  Session cache ở biến module. **Hàm phải tra qua tên module lúc gọi** (`set_photo` gọi `cutout_u2net(...)` của module
  hiện hành) để test thay được.
- `compose_on_plate(rgba) -> RGB` (cỡ = ảnh nền). Số do Claude chốt (đã thử trên ảnh thật, duyệt bằng mắt):
  1. Alpha: `<128 → 0, còn lại 255`, `MinFilter(5)`, `GaussianBlur(1.2)`; cắt theo `getbbox()` của alpha.
  2. Thu phóng LANCZOS: `s = min(0.40*W / w, 0.58*H / h)`. Tâm ngang `cx = int(0.52*W)`, đáy `by = int(0.87*H)`;
     `x = cx - w'//2`, `y = by - h'`.
  3. Màu vật: `ImageEnhance.Color 1.10`, `Brightness 1.08`.
  4. Bóng (Image.composite màu đặc qua mặt nạ = alpha dán ở vị trí lệch, blur, nhân hệ số):
     bóng rộng `dx=int(W*.012), dy=int(H*.03), blur=H*.03, hệ số 0.45, màu (70,40,15)`; rồi bóng tiếp xúc
     `dx=0, dy=int(H*.008), blur=H*.008, hệ số 0.55, màu (35,20,8)`. Cuối cùng dán vật bằng alpha.
- `set_photo(conn, id, data: bytes, compose=True) -> filename`: mở bằng PIL (`ImageOps.exif_transpose`).
  `compose=False` → RGB, thu nhỏ để cạnh dài ≤ 1672. `compose=True` → `has_alpha` ? dùng luôn : `cutout_u2net(img)` (ảnh
  chụp thu nhỏ cạnh dài ≤ 1600 trước khi tách) → `compose_on_plate`. Lưu `<id>.jpg`, ghi cột `photo`.
- `export_xlsx(conn, pricing) -> bytes` (openpyxl), font **Arial** toàn bộ, 1 sheet tên `Bảng giá`:
  - Màu: xanh STLab `1E4FD8`, cam `F47B20`, chữ phụ `6B7280`, viền `D0D5DD`, dòng chẵn `F3F6FC`.
  - Cột A..H rộng 6 / 34 / 34 / 13 / 15 / 15 / 15 / 24.
  - Hàng 1 (gộp A1:H1): `STLab · 3D Printing • Robotics • STEAM` đậm 20 pt xanh. Hàng 2 (gộp): `Trung tâm STEAM ·
    Đức Trọng, Lâm Đồng` + ` · ĐT <shop_phone>` + ` · <shop_contact>` nếu settings có, 10 pt xám. Hàng 3: dải cam
    (fill A3:H3, cao 4 pt). Hàng 4 (gộp): `BẢNG GIÁ SẢN PHẨM IN 3D` đậm 16 pt giữa. Hàng 5 (gộp): `Cập nhật
    dd/mm/yyyy · Giá cho 1 sản phẩm, đã gồm nhựa, điện, công in` nghiêng 10 pt xám giữa. Hàng 6 trống cao 6 pt.
  - Hàng 7 tiêu đề: `STT | Hình ảnh | Tên sản phẩm | Khối lượng (g) | Giá lẻ (đ) | Sỉ ≥{bulk1_min_qty} cái (−{pct}%) |
    Sỉ ≥{bulk2_min_qty} cái (−{pct}%) | Ghi chú` (pct = discount × 100, số nguyên nếu tròn); nền xanh, chữ trắng đậm,
    giữa, wrap, cao 32 pt. `freeze_panes = "A8"`, `print_title_rows = "7:7"`.
  - Từ hàng 8, mỗi mẫu một hàng theo `list_all`: STT 1..n (giữa); tên đậm 11 pt wrap; khối lượng số (`0.#` nếu lẻ,
    `0` nếu nguyên) phải; giá: số, `number_format '#,##0" đ"'`, phải; giá `None` → chuỗi `Liên hệ` (giữa, xám);
    ghi chú wrap. Canh giữa dọc, viền mảnh, dòng chẵn tô nền. Cao hàng 102 pt.
  - Ảnh: thu nhỏ vừa 230×129 px (giữ tỉ lệ), JPEG q=85 vào BytesIO, `openpyxl.drawing.image.Image`, neo
    `OneCellAnchor` ô B, căn giữa ô (offset EMU). Mẫu không có ảnh → ô trống.
  - Sau bảng 1 hàng trống rồi ghi chú (gộp A:H, 9.5 pt xám): `• Giá sỉ áp dụng khi đặt cùng một mẫu.`,
    `• Giá chưa gồm phí vận chuyển.`, `• Báo giá có hiệu lực {valid_days} ngày kể từ ngày cập nhật.`
  - In: A4 dọc, `fitToPage`, `fitToWidth=1, fitToHeight=0`, lề 0.4", căn giữa ngang, footer giữa `STLab – Trang &P/&N`.
  - Trả bytes của workbook.

## `toolhub/views.py`
- `from . import catalog`. `/api/quote/save`: sau `save_quote`, nếu `_item(data)["model_key"]` có →
  `catalog.upsert_from_quote(conn, key, title, parsed, pricing, extras=_extras(data), materials_map=mapping,
  quote_id=qid)`; dòng chưa có ảnh và plate đầu có `image_png` → `catalog.set_photo(conn, cid, png, compose=True)`
  (lỗi ảnh không làm hỏng việc lưu: bắt Exception, bỏ qua). Trả thêm `"catalog_id"` (None nếu không có key).
- `GET /quote/catalog` → `quote-catalog.html` (`items = list_all`, `pricing`).
- `GET /quote/catalog/<int:id>/photo` → `send_file` JPEG, không có → 404. Thêm `?v=<updated_at>` khi in URL trong
  trang để tránh cache.
- `POST /api/quote/catalog` JSON → `create` → `{"id"}`; tên rỗng → 400.
- `POST /api/quote/catalog/<int:id>` JSON → `update` → bản ghi; không có → 404.
- `POST /api/quote/catalog/<int:id>/delete` → `{"ok": true}`; không có → 404.
- `POST /api/quote/catalog/<int:id>/photo` multipart `file` (+ `keep=1` → `compose=False`) → `{"photo_url"}`;
  không có mẫu → 404; không có file → 400; lỗi tách nền (`QuoteError`/Exception) → 500 `{"error"}` tiếng Việt.
- `GET /quote/catalog.xlsx` → `send_file(BytesIO, mimetype=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,
  download_name=f"BaoGia-STLab-{YYYYMMDD}.xlsx", as_attachment=True)`.
- Mọi POST đã có chặn X-Studio chung ở `__init__.py` – không sửa `__init__.py`.

## `toolhub/templates/quote-catalog.html` (mới, `{% extends %}` giống `quote.html`)
- Tiêu đề `Danh mục mẫu`, dòng phụ "Lưu báo giá là mẫu tự vào đây · ảnh tự ghép phông STLab".
  Nút chính `<a href="/quote/catalog.xlsx">Xuất Excel (tất cả mẫu)</a>`, nút `Thêm mẫu tay`, link về `/quote`.
- Lưới thẻ (CSS grid, ~280 px/thẻ, dùng biến CSS của `style.css`/`tokens.css` như trang quote): ảnh 16:9
  (`object-fit: cover`) hoặc ô trống "Chưa có ảnh"; ô sửa tên, khối lượng (g), giá lẻ, sỉ 1, sỉ 2, ghi chú – đổi là lưu
  (debounce 600 ms, `POST /api/quote/catalog/<id>`, header `HJ` như quote.html: `Content-Type: application/json`,
  `X-Studio: 1`); dòng nhỏ "Từ báo giá <số>" nếu có `quote_id`; nút `Tải ảnh chụp` (input file ẩn, accept image/*) +
  checkbox `Giữ nguyên ảnh (đã có phông)` → `POST .../photo` (FormData, header `X-Studio: 1`), hiện "Đang tách nền…"
  rồi thay ảnh; nút `Xóa` (confirm) → `.../delete` rồi bỏ thẻ. Lỗi → thông báo đỏ trên thẻ.
- Tiếng Việt có dấu đầy đủ, UTF-8.

## `toolhub/templates/quote.html`
- Thẻ "Lịch sử báo giá": thêm link `<a href="/quote/catalog">Danh mục mẫu →</a>` cạnh tiêu đề.
- Sau lưu thành công: nếu `j.catalog_id` → toast `Đã lưu <số> · đã cập nhật Danh mục mẫu`.

# Đang có thay đổi chưa commit cần GIỮ
- `pyproject.toml`, `uv.lock` (Claude vừa thêm thư viện), `toolhub/static/quote/stlab-desk.jpg`, `tests/test_quote_catalog.py`.

# Không làm
- Không sửa test, `quote.py` (trừ khi thật cần – báo lại), `quote_defaults.json`, `__init__.py`, ảnh nền.
- Không cài thêm thư viện (không rembg, không pymatting). Không gọi mạng ngoài việc tải u2net.onnx khi thiếu.
- Không đụng DB thật `%LOCALAPPDATA%\stlab-quotes` khi chạy thử (test dùng biến môi trường).

# Tiêu chí PASS
- Gate exit 0. `node --check` không áp dụng (JS trong template) – tự đọc lại JS 1 lượt.
- Claude tự kiểm thêm: mở /quote/catalog, tải ảnh thật, xuất Excel mở xem.
