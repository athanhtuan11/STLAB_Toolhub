---
task: toolhub-quote-v3-autoslice
cwd: .
allow: ["tools/robotics-cad/scripts/quote_slice.py", "tools/robotics-cad/scripts/slice.py", "studio/toolhub/quote.py", "studio/toolhub/views.py", "studio/toolhub/templates/quote.html", "studio/toolhub/templates/quote-print.html"]
read: ["studio/toolhub/quote_defaults.json", "studio/spec-quote.md", "studio/spec-quote-v2.md", "studio/toolhub/printprep.py"]
gate: 'studio\.venv\Scripts\python.exe studio\tests\test_quote_slice.py && studio\.venv\Scripts\python.exe studio\tests\test_quote.py && studio\.venv\Scripts\python.exe studio\tests\test_library_pages.py'
executor: opencode
timeout_min: 45
max_rounds: 2
---

# Mục tiêu
Tuan (2026-10-28): "chỉ muốn kéo file .3mf, .stl hay file in khác vô, chọn nhựa (vd PETG hãng Bambu) là ra giá cuối" –
KHÔNG phải tự cắt lớp trong Bambu Studio. Toolhub tự cắt lớp bằng **Bambu Studio CLI** theo profile A1 chính hãng
+ profile của nhựa đã chọn. Hành vi đúng = `studio/tests/test_quote_slice.py` (+ 2 test cũ vẫn PASS).

Claude đã thử 2026-10-28 (Python FreeCAD, hàm có sẵn trong `slice.py`): STL/OBJ cắt được (0,7–1,2 s CLI); PETG
**bắt buộc** `curr_bed_type: "Textured PEI Plate"` (thiếu → "Filaments are not compatible with the plate type");
STEP → CLI báo "can not be parsed" → phải đổi sang STL bằng FreeCAD trước; 3MF dự án nhiều màu + bật support → lỗi
"G-code conflicts" (tháp xả) → thử lại support tắt, vẫn ra gam/giờ kèm cảnh báo.

# Yêu cầu
## `tools/robotics-cad/scripts/slice.py`
- CHỈ thêm guard: `if __name__ == "__main__": sys.exit(main())` thay dòng gọi cuối. Không đổi gì khác.

## `tools/robotics-cad/scripts/quote_slice.py` (mới, chạy bằng `C:\Program Files\FreeCAD 1.1\bin\python.exe`)
- `quote_slice.py --list-filaments` → in 1 dòng JSON `{"filaments": [...], "processes": [...]}`: tên profile
  filament/process dùng được cho A1 0.4 (chính hãng có `@BBL A1` – loại `A1M`/A1 mini – và preset riêng của Tuan
  trong `%APPDATA%\BambuStudio\user\*\filament|process` có chữ "A1" và không "A1 mini"/"A1M"), sắp xếp, không trùng.
- `quote_slice.py <out_dir> filament="<tên>" [process="0.20mm Standard @BBL A1"] [infill=<số %>] [support=auto|off]
  <file...>` → cắt lớp, ghi `<out_dir>/quote_slice.json` và in cùng JSON ở dòng cuối stdout:
  `{"status": "ok"|"warn"|"fail", "seconds": int, "grams": {loại nhựa: g}, "gcode_3mf": path|null,
  "warnings": [...], "errors": [...], "support": bool, "fallback": str|null}`.
- Dùng lại hàm của `slice.py` (`chi_muc_profile`, `phang`, `ghi`, `cat`, `doc_ket_qua`, `SUPPORT`), không chép.
  Máy `Bambu Lab A1 0.4 nozzle` (`from: system`); process + `curr_bed_type: "Textured PEI Plate"`; infill →
  `sparse_infill_density: "<n>%"`; support auto → `SUPPORT` của slice.py; filament như slice.py làm (setdefault
  from/type/instantiation). STL/OBJ: `--orient` bật; 3MF: không orient.
- STEP/STP: đổi sang STL bằng `freecadcmd.exe` (`C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe`, script tạm,
  `Part.read` + `MeshPart.meshFromShape(Shape=..., LinearDeflection=0.1, AngularDeflection=0.523599)` → `.stl` trong
  out_dir; truyền đường dẫn qua biến môi trường, không ghép chuỗi vào code).
- `grams`: từ slice_info của .3mf ra (theo `type` của `<filament>`); không có 3mf mà result.json có số → dùng
  `total_used_g` gán cho loại nhựa của profile (`filament_type` trong profile phẳng).
- 3MF lỗi khi bật support → chạy lại support tắt, `fallback: "support-off"`, `status: "warn"` + cảnh báo
  "chưa tính support – kiểm lại trong Bambu Studio". Có số gam > 0 nhưng CLI báo lỗi → `warn` kèm lỗi; 0 g → `fail`.
- Thời gian tối đa 300 s mỗi lần CLI; file không tồn tại/đuôi lạ → `fail` + `errors`.

## `studio/toolhub/quote.py`
- Bảng `materials` thêm cột `type`, `slicer_profile` (nâng cấp DB cũ bằng `ALTER TABLE` nếu thiếu, giữ dữ liệu).
  Thiếu `type` → suy từ tên (tìm PLA, PETG, TPU, ABS, ASA, PC, PA, PCTG… trong tên viết hoa, ưu tiên chuỗi dài hơn:
  PETG trước PET, PCTG trước PC). Thiếu `slicer_profile`: nhựa trùng tên mặc định → profile trong
  `quote_defaults.json`; còn lại → `"Generic <type> @BBL A1"`. `save_material(..., type=None, slicer_profile=None)`.
  `get_pricing()["materials"][tên]` = `{spool_price_vnd, spool_weight_g, type, slicer_profile}`.
- `compute(... materials_map)`: loại trong file không có map → nhựa cùng tên, không thì nhựa đầu tiên cùng `type`.
- `work_dir()` = env `STLAB_QUOTES_WORK` hoặc `%LOCALAPPDATA%\stlab-quotes` (uploads/, slices/); giữ ≤ 30 lần upload
  gần nhất, xóa cũ hơn.
- `slice_model(files, material_name, options)` gọi `quote_slice.py` bằng Python FreeCAD (subprocess, cửa sổ ẩn như
  `printprep.py`), đọc JSON → parsed (dùng `read_3mf` trên `gcode_3mf` để có bàn + ảnh; không có thì dựng 1 bàn từ
  seconds/grams). Cache theo (token, slicer_profile, process, infill, support) trong bộ nhớ + file trên đĩa.
- `slicer_profiles()` gọi `--list-filaments` (cache trong bộ nhớ).

## `studio/toolhub/views.py`
- `POST /api/quote/upload` (multipart, `file` nhiều cái): đuôi `.stl .obj .step .stp .3mf` (`.gcode.3mf` tính là
  .3mf) – khác → 400. Lưu `work_dir()/uploads/<token>/`. Một file .3mf có `slice_info` → `kind: "sliced"` (parse ngay),
  còn lại `kind: "model"`. Trả `{token, kind, names, ...}`.
- `POST /api/quote/price` `{token, material, quantity, options?{process, infill, support}, extras?, other_fee_vnd?,
  materials_map?}` → model: cắt lớp (hoặc cache) theo profile của `material`; sliced: map mọi loại trong file → `material`
  (trừ khi có materials_map) → compute → trả calc (+ `*_text`) + `grams`, `hours`, `plates` (ảnh data URL), `slice`
  (status/warnings/fallback). Nhựa không có / cắt lỗi → 400 `{"error"}`.
- `/api/quote/save` nhận cùng tham số `price` (token + material + options). `GET /api/quote/slicer-profiles`.
- Giữ `/api/quote/parse`, `/api/quote/calc` cũ (test cũ dùng).

## `quote.html` (luồng 3 bước, bố cục mockup đã duyệt)
1. **Kéo file** `<input id="file" type="file" multiple accept=".stl,.obj,.step,.stp,.3mf">` (+ chọn file dự án như cũ).
2. **Nhựa** `<select id="material">` (tên nhựa – profile cắt lớp – giá/kg); mặc định nhựa đầu tiên có type PETG.
3. **Giá cuối** to, `id="final-price"`, + đơn giá × SL; dưới là bảng giá vốn (gập được) và ảnh bàn in.
- `<details id="print-options">` "Tùy chọn in": số lượng, chất lượng (process A1 từ API: 0.12 Fine … 0.28 Extra
  Draft, mặc định từ `print_options`), infill % (trống = theo profile), support (Tự động / Không), phụ kiện, phí khác.
- Khi đang cắt lớp: "Đang cắt lớp bằng Bambu Studio…" + vô hiệu nút Lưu; đổi nhựa/tùy chọn → tự gọi lại `price`.
  Cảnh báo cắt lớp (`slice.warnings`) hiện chữ `--warn`.
- Bảng giá: mỗi nhựa có ô chọn **Profile cắt lớp** (danh sách từ `/api/quote/slicer-profiles`). Khách hàng + Lưu như cũ.
- Đã cắt lớp sẵn (.gcode.3mf): bỏ qua cắt lớp; nếu file có nhiều loại nhựa thì hiện `material-map` như v2.

# Không làm
- KHÔNG sửa `tests/`, `quote_defaults.json`, `static/*`, `community/`, `print.yaml`, file ngoài `allow`.
- Không thêm thư viện. Không ghi upload/kết quả cắt lớp vào repo.

# Tiêu chí PASS
- Gate exit 0. Claude kéo thử STL + 3MF dự án thật trên trang và xem ảnh.
