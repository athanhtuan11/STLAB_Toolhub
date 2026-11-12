---
task: quote-tune
cwd: .
allow:
  - "tools/print/scripts/tune/presets.json"
  - "tools/print/scripts/geometry_profile.py"
  - "tools/print/scripts/tune_rules.py"
  - "tools/print/scripts/quote_slice.py"
  - "studio/toolhub/quote.py"
  - "studio/toolhub/quote_tune.py"
  - "studio/toolhub/views.py"
  - "studio/toolhub/templates/quote.html"
  - "studio/toolhub/templates/quote-tune.html"
  - "studio/toolhub/static/*.js"
  - "studio/toolhub/static/style.css"
gate: "studio/.venv/Scripts/python.exe -X utf8 studio/tests/test_quote_tune.py"
timeout_min: 30
max_rounds: 2
executor: auto
read: ["docs/reports", "tools/print", "studio/toolhub", "studio/design"]
---

# Mục tiêu
Thêm bước **"Tối ưu in"** vào trang Báo giá của Toolhub (Tuan duyệt 2026-11-12): kéo file → phân tích hình học → đề xuất
thông số slicer theo luật (mỗi dòng có lý do + mức nguồn S/P) → người dùng chỉnh → cắt lớp 2 phương án (mặc định hãng /
tối ưu) → xem 2 ảnh cạnh nhau → tải `.3mf` phương án tối ưu. Nguồn luật + giá trị: `docs/reports/slicer-auto-tune-research.md`
(mục 3, mục 8.9). Executor KHÔNG tự đặt ngưỡng/giá trị ngoài spec này và báo cáo.

# Yêu cầu
1. `tools/print/scripts/tune/presets.json`: dict 7 preset `{tên: {"process": {...}, "filament": {...}}}` chép **đúng nguyên văn**
   7 khối ```json``` của mục `### 8.9` trong báo cáo (tên = tiêu đề `#### \`tên\``). Không thêm/bớt khóa.
2. `tools/print/scripts/geometry_profile.py` – `features(stl_path) -> dict` (numpy; dùng lại `printability.doc_stl`,
   `printability.phan_tich`, `printability.MAC_DINH`; chạy được bằng Python FreeCAD lẫn venv studio):
   - `can_support` (= phan_tich), `contact_mm2` (= tiep_xuc_mm2), `height_mm`, `aspect` (cao / cạnh ngắn bbox XY),
     `max_overhang_mm2` (cụm cần đỡ lớn nhất trong `cum_nho`, 0 nếu không có), `bbox_mm` [x,y,z],
     `small` (= max(bbox x, y) < 20), `top_flat_mm2` (tổng diện tích tam giác pháp tuyến nz > 0,99 nằm ở z ≥ zmax − 0,2),
     `curved_frac` (diện tích tam giác 0,5 ≤ |nz| ≤ 0,985 / tổng diện tích), `holes` (genus của lưới kín: hàn đỉnh làm tròn
     1e-4 mm, χ = V − E + F, genus = round((2·số thân − χ)/2), số thân = số thành phần liên thông; tối thiểu 0).
3. `tools/print/scripts/tune_rules.py` – `suggest(features, goals=()) -> {"process": {}, "filament": {}, "items": [...]}`;
   mỗi item `{"key","value","pack": "process"|"filament","reason": tiếng Việt,"level": "S"|"P","preset": tên hoặc ""}`.
   Áp lần lượt (sau ghi đè trước):
   a. `can_support` False → `enable_support="0"` (S, lý do: không có phần nhô cần đỡ).
   b. `can_support` True → `enable_support="1"` (S) + preset `support_easy` (mặc định) hoặc `support_pretty` nếu `"support_pretty"`
      trong goals; nếu goals chưa chọn support_pretty và `max_overhang_mm2 > 100` → `support_type="normal(auto)"`,
      `support_style="default"` (P, mảng nhô lớn phẳng), ngược lại `support_type="tree(auto)"` (S, mặc định A1).
   c. Brim: `contact_mm2 < 120` hoặc `aspect >= 2.5` → preset `brim_easy` + `brim_type="outer_only"`; nếu `aspect >= 2.5`
      → thêm preset `tall_thin`. Ngược lại → `brim_type="no_brim"` (P, chân lớn thấp không cần brim). Goal `pretty_edge`
      → `brim_object_gap="0.2"` (P).
   d. `small` → preset `small_parts`.
   e. `holes >= 4` → preset `petg_stringing`.
   f. `curved_frac > 0.3` → `layer_height="0.16"` (P, mặt cong lớn).
   g. Goal `surface_pretty` → preset `surface_pretty`; goal `plate_only` → `support_on_build_plate_only="1"`.
   Level của khóa lấy từ báo cáo nếu có (bảng preset có cột Mức); khóa không rõ → "P". CLI: `python tune_rules.py <stl>
   [goal ...]` in JSON.
4. `tools/print/scripts/quote_slice.py`: thêm đối số `overrides=<file json>` dạng `{"process": {...}, "filament": {...}}`;
   process ghi đè áp **sau cùng** trong `write_proc` (đè cả SUPPORT); filament ghi đè áp vào dict filament trước khi ghi
   `filament.json`. Không đổi hành vi khi không có đối số.
5. Toolhub:
   - `GET /quote?mode=tune`: giao diện "Tối ưu in" (template riêng `quote-tune.html` hoặc tab trong `quote.html`, ẩn phần giá).
     Gồm: ô kéo file (dùng lại `/api/quote/upload`), ô chọn mục tiêu (support_pretty, surface_pretty, pretty_edge, plate_only),
     bảng "Thông số | Giá trị (sửa được) | Lý do | S/P", nút "Cắt lớp so sánh", 2 ảnh cạnh nhau (Mặc định hãng / Tối ưu) kèm
     giờ, gam, cảnh báo, nút tải `.3mf` mỗi bên. Trang /quote thường thêm 1 liên kết "Tối ưu in". Màu/chữ theo
     `design/tokens.json` (không hex trong CSS).
   - `POST /api/quote/tune/analyze` `{token, goals}` → `{features, process, filament, items}` (file STL/OBJ đầu tiên của token;
     STEP: đổi STL như quote_slice; 3MF → 400 "Tối ưu in chỉ nhận STL/OBJ/STEP").
   - `POST /api/quote/tune/slice` `{token, material, process, filament}` → `{default: {...}, tuned: {...}}`, mỗi bên
     `{image_url, download_url, hours, grams, warnings}`; chạy `quote_slice.py` 2 lần (không overrides / có overrides),
     support=auto; ảnh = `plate_1.png`; tải file qua route GET mới trả `quote.3mf` (chỉ trong thư mục work của token).
   - Mã đặt ở `toolhub/quote_tune.py` (blueprint hoặc hàm gọi từ views.py); dùng lại `quote._run_slice`/`work_dir`/
     `default_profile` khi được.

# Không làm
- Không sửa `tests/`, `docs/reports/`, `slice.py`, `printability.py`, các test cũ. Không đổi luồng báo giá hiện có.
- Không gọi mạng. Không tự đặt ngưỡng ngoài mục 3 ở trên.

# Tiêu chí PASS
- Gate exit 0. Claude tự chạy thêm `studio/tests/test_quote.py`, `test_quote_slice.py` (không được hỏng).
