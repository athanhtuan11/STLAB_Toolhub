---
task: toolhub-pin-diagram-photo
cwd: studio
allow: ["toolhub/pin_diagram.py", "toolhub/workspace.py", "toolhub/views.py", "toolhub/templates/library.html"]
read: ["tools/robotics-cad/library", "studio/design", "community/j0ono0-pinout", "community/wireviz"]
gate: '.venv\Scripts\python.exe tests\test_pin_diagram.py && .venv\Scripts\python.exe tests\test_pinout.py'
executor: opencode
timeout_min: 30
max_rounds: 2
---

# Mục tiêu
Trang `/library` của Toolhub thay "hộp chữ" bằng **sơ đồ chân trên ảnh bo thật** (thư viện `pinout` – j0ono0, đã cài
trong `.venv`, mã ở `community/j0ono0-pinout`) và **sơ đồ đấu theo dự án** bằng **WireViz** (đã cài, mã ở
`community/wireviz`; Graphviz `dot` cài ở `C:\Program Files\Graphviz\bin`). Đọc `tests/test_pin_diagram.py` để biết
đúng hành vi. Linh kiện mẫu: `relay-module-2ch-srd-05vdc` trong `tools/robotics-cad/library/components.yaml`.

# Dữ liệu (đã có – KHÔNG sửa YAML)
- `anh_chan: {file, w, h}`: ảnh tương đối theo thư mục `library/` (vd `images/relay-module-2ch-srd-05vdc.png`), kích thước px.
- `chan[]`: `{ten, ben: trai|phai|tren|duoi, muc: ac220|5v|3v3|gnd|tin-hieu, mo_ta, x, y, xac_nhan?}`. x,y = tâm chân trên ảnh (px).
- `so_do[]`: `{du_an, tieu_de, noi: [[chân, nối tới, ghi chú], ...]}`.

# Yêu cầu
## Module mới `toolhub/pin_diagram.py`
- `photo_svg(component) -> str`: dùng thư viện `pinout` (core/components) vẽ ảnh bo + với mỗi chân: chấm tròn tại (x,y), đường dẫn
  ra nhãn theo hướng `ben` (tren → nhãn phía trên ảnh, duoi → dưới, trai/phai → hai bên), nhãn = ô màu chứa `ten`
  (thêm "?" nếu `xac_nhan: false`, vd "COM1?") + `mo_ta` chữ nhỏ. Các nhãn cùng phía xếp so le/tách dòng để KHÔNG đè nhau
  (6 nhãn trên ở cùng hàng y gần nhau – dùng 2 tầng hoặc nghiêng). Ảnh tham chiếu bằng URL route `/library/img/<file>`
  (không base64, không đường dẫn ổ đĩa). Không có `anh_chan` → `""`.
- Màu theo `muc` qua CSS biến Toolhub (style/stylesheet nhúng trong SVG): ac220 `var(--err)`, 5v `var(--warn)`, 3v3 `var(--accent)`,
  gnd `var(--muted)`, tin-hieu `var(--text)`; chữ trên ô màu `var(--on-accent)` hoặc `var(--bg)`; font `var(--font-ui)`/`var(--font-mono)`.
  Không màu hex trong phần mình viết. Có chú thích mức điện áp ("220 VAC – nguy hiểm", "5 V", "3,3 V", "GND", "tín hiệu").
  Bỏ `<?xml …?>`; có `viewBox`; `width="100%"`, `style="max-width:…px"`. Không script.
- `wiring_svg(component, so_do) -> str`: dựng dict WireViz rồi `wireviz.wireviz.parse(dict, return_types="svg")`
  (đọc chữ ký hàm trong `community/wireviz/src/wireviz/wireviz.py`):
  - Connector linh kiện: `pins`/`pinlabels` = tên chân dùng trong `noi`, `image: {src: <đường dẫn ảnh thật>, width: ~180}`
    (sau khi render, THAY href ảnh trong SVG thành `/library/img/<file>`; không để lộ đường dẫn ổ đĩa / `file:`).
  - Mỗi đích (`nối tới`) là 1 connector `style: simple` có nhãn = chuỗi đích, ghi chú = `notes`.
  - Mỗi dây: màu theo `muc` của chân: ac220 `BN` (dây pha nâu), 5v `RD`, gnd `BK`, 3v3 `YE`, tin-hieu `GN`; dây ac220 ghi
    "220 VAC" (vd `wirelabels`/`notes`). Chân trong `noi` không có trong `chan` → vẫn vẽ, ghi "không có chân này".
  - Nếu không tìm thấy `dot` trên PATH → tự thêm `C:\Program Files\Graphviz\bin` vào `os.environ["PATH"]` trước khi gọi.
  - Bỏ `<?xml`/`<!DOCTYPE`; giữ `viewBox`; `width="100%"`. Bọc lỗi: Graphviz/WireViz lỗi → trả chuỗi rỗng + ghi log, trang không sập.
- Cache kết quả trong bộ nhớ theo (id, mtime components.yaml, mtime ảnh) – WireViz chạy `dot` chậm.

## `views.py`
- Route `GET /library/img/<path:rel>`: chỉ phục vụ file **nằm trong** `tools/robotics-cad/library/images/` (resolve + kiểm
  tiền tố; `..`/ngoài thư mục → 404), chỉ đuôi png/jpg/jpeg/svg/webp.

## `workspace.py` + `library.html`
- `library()`: linh kiện có `anh_chan` → `c["pinout"]` = [{"title": "Sơ đồ chân", "svg": photo_svg}] + mỗi `so_do`
  {"title": "Đấu cho <du_an>: <tieu_de>", "svg": wiring_svg}. Không có `anh_chan` nhưng có `chan` → giữ bản cũ
  `pinout.render_svg` (module `toolhub/pinout.py` giữ nguyên). Bỏ phần tử có svg rỗng.
- Template giữ mục `<details open><summary>Sơ đồ chân</summary>` hiện có; sơ đồ đấu đặt trong khung cuộn ngang
  (`overflow-x:auto`) nếu rộng. Card có sơ đồ: `grid-column: 1 / -1` (cả hàng).

# Không làm
- KHÔNG sửa `components.yaml`, `tests/`, `static/style.css`, `static/tokens.css`, `toolhub/pinout.py`, `community/`.
- Không gọi mạng, không CDN, không thêm thư viện ngoài 2 thư viện đã cài.

# Tiêu chí PASS
- Gate exit 0 (cả test mới và test cũ).
- Claude tự xem ảnh chụp `/library`: nhãn không đè nhau, đọc được, ảnh relay hiện.
