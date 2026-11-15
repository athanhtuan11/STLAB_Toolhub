---
task: plate-color
cwd: tools/print
allow:
  - "scripts/slice.py"
gate: '"C:\Program Files\FreeCAD 1.1\bin\python.exe" tests\test_plate_color.py'
timeout_min: 30
max_rounds: 2
executor: auto
---

# Mục tiêu
Tuan (2026-11-15): mẫu tự thiết kế (vd. Cú Bông) – bàn in `.3mf` phải **tự mang màu giống thiết kế 3D**, Tuan không phải đặt
màu lại trong Bambu Studio. Hiện mọi bàn mang màu mặc định của profile nhựa (`filament_colour` = `#00AE42` xanh lá).

# Đầu vào
- `scripts/slice.py` (cắt lớp theo print.yaml bằng Bambu Studio CLI; mỗi bàn ghép profile nhựa `fil` rồi ghi
  `_profile/filament_<ban>.json` → `--load-filaments`).
- Nguồn màu (ưu tiên từ cao xuống):
  1. `color: "#RRGGBB"` trong khai báo bàn ở print.yaml;
  2. `colors: {<ten.stl>: "#RRGGBB"}` cấp dự án trong print.yaml;
  3. file `<stl_dir>/colors.json` = `{<ten.stl>: "#RRGGBB"}` (script dựng hình xuất ra; khóa bắt đầu `_` là ghi chú → bỏ qua).
- Gate `tests/test_plate_color.py` là đặc tả chi tiết (KHÔNG sửa).

# Yêu cầu (chỉ sửa `scripts/slice.py`)
1. Hàm `mau_ban(cfg, ten_ban, b, stl_ban, stl_dir) -> str | None` ở cấp module:
   - `b["color"]` có → dùng. Không → gom màu của từng STL trong bàn theo `cfg["colors"]` rồi `colors.json` (cfg thắng file).
   - Kiểm định dạng `^#[0-9A-Fa-f]{6}$`, sai → `ValueError` nêu bàn + giá trị. Trả chữ HOA.
   - Các STL có màu khác nhau trong 1 bàn → `ValueError("bàn <ten>: N màu (...) – tách bàn theo màu (1 bàn 1 màu, hạn chế AMS)")`.
   - Không STL nào có màu và bàn không khai → `None`. Một số có, một số không → dùng màu đã có (không lỗi).
2. Trong vòng lặp bàn của `main()`: màu khác None → `fil["filament_colour"] = [mau]` (và `default_filament_colour` nếu cần
   để CLI giữ màu) TRƯỚC khi ghi `filament_<ban>.json`; kiểm thực tế bằng 3MF ra (`Metadata/project_settings.config` →
   `filament_colour[0]` đúng màu). Nếu CLI bỏ qua khóa trong profile thì hậu xử lý: mở 3MF ra, sửa `filament_colour` trong
   `Metadata/project_settings.config` (giữ nguyên các file khác, nén lại đúng chuẩn zip) – chọn cách nào miễn gate PASS và
   `bambu-studio.exe --info <file>` vẫn exit 0.
   - `ValueError` từ `mau_ban` (1 bàn 2 màu, sai định dạng) → in thông báo rõ và thoát exit 2 **trước khi** cắt bàn nào.
   - Bàn không có màu → vẫn cắt như cũ, thêm cảnh báo `chưa khai màu (colors.json / color:) – Bambu dùng màu mặc định`
     vào phần WARN của bàn đó (không làm bàn FAIL).
3. `print-report.json`: mỗi bàn thêm khóa `"mau": "#RRGGBB" | null`. `print-overview.png`: ô màu nhỏ cạnh tên bàn
   (matplotlib, tùy chọn – không bắt buộc qua gate).
4. Docstring đầu file: thêm 3 dòng mô tả nguồn màu.

# Không làm
- Không sửa test, thresholds.yaml, script khác, print.yaml/colors.json của dự án. Không thêm thư viện.
- Không đổi hành vi cắt lớp hiện có (support, brim, song song). Không commit.

# Tiêu chí PASS
- Gate exit 0. Claude cắt lại Cú Bông S3 (`maker/english-teacher/print/print-s3.yaml`) và xem ảnh bàn in đúng màu.
