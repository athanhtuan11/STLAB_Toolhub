---
task: toolhub-pinout-graph
cwd: studio
allow: ["toolhub/pinout.py", "toolhub/workspace.py", "toolhub/templates/library.html"]
read: ["tools/robotics-cad/library", "studio/design"]
gate: '.venv\Scripts\python.exe tests\test_pinout.py'
executor: opencode
timeout_min: 25
max_rounds: 2
---

# Mục tiêu
Trang Toolhub "Thư viện linh kiện robotics" (`/library`) vẽ **sơ đồ chân** (graph SVG) cho linh kiện có khóa `chan`
trong `tools/robotics-cad/library/components.yaml`, kèm **sơ đồ đấu theo dự án** (`so_do`). Linh kiện đầu tiên:
`relay-module-2ch-srd-05vdc` (dự án pump-control). Đọc `tests/test_pinout.py` để biết đúng hành vi.

# Dữ liệu (đã có trong YAML – KHÔNG sửa YAML)
- `chan`: list `{ten, ben: trai|phai, muc: ac220|5v|3v3|gnd|tin-hieu, mo_ta?}`. Thiếu `ben` → `trai`, thiếu `muc` → `tin-hieu`.
- `so_do`: list `{du_an, tieu_de, noi: [[chân, nối tới, ghi chú], ...]}`.

# Yêu cầu
- Module mới `toolhub/pinout.py`, chỉ thư viện chuẩn Python: `render_svg(ten, chan, so_do=None) -> str`.
  - Không có chân → `""`.
  - Hộp linh kiện ở giữa (tên linh kiện làm tiêu đề), chân `trai` xếp dọc cạnh trái, `phai` cạnh phải, mỗi chân 1 ô
    nhỏ có tên + `mo_ta` (chữ nhỏ, màu muted).
  - Có `so_do`: với mỗi dòng `noi`, vẽ 1 đường (`<line>`/`<path>`) từ chân ra nhãn đích ở phía ngoài cùng bên, kèm ghi chú
    nhỏ. Chân trong `noi` không có trong `chan` → vẫn vẽ ở bên trái, viền nét đứt màu `var(--err)` + chữ "không có chân này".
    Chân không có trong `noi` → vẽ mờ (opacity ~0.45) = để trống. Tiêu đề sơ đồ ghi `du_an: tieu_de`.
  - Màu theo `muc` CHỈ bằng `var(--…)` (không hex): ac220 → `var(--err)`, 5v → `var(--warn)`, 3v3 → `var(--accent)`,
    gnd → `var(--muted)`, tin-hieu → `var(--text)`. Chữ `var(--text)`, nền hộp `var(--card)`, viền `var(--line)`,
    font `var(--font-ui)`/`var(--font-mono)` cho tên chân. Màu dùng qua thuộc tính `style="stroke:var(--err)"`/`fill:`.
  - Chú thích (legend) dưới cùng: chỉ các mức có mặt, ghi chữ: "220 VAC – nguy hiểm", "5 V", "3,3 V", "GND", "tín hiệu".
  - `html.escape` mọi chữ lấy từ YAML. Có `viewBox`, `width="100%"`, `role="img"`, `aria-label`. SVG là XML hợp lệ.
  - Kích thước tự tính theo số chân (cao mỗi hàng ~28 px); chữ dài cắt bớt ~28 ký tự + "…" (giữ bản đầy đủ trong `<title>`).
- `toolhub/workspace.py` → `library()`: với mỗi linh kiện có `chan`, gắn `c["pinout"] = [{"title": ..., "svg": ...}]`:
  1 sơ đồ chỉ chân (title "Sơ đồ chân") + mỗi `so_do` 1 sơ đồ (title "Đấu cho <du_an>"). Không làm hỏng dict gốc khi
  gọi lại (yaml đọc mới mỗi lần nên ổn – đừng cache).
- `templates/library.html`: trong card, nếu có `c.pinout` → mục `<details open>` với `<summary>Sơ đồ chân</summary>`,
  mỗi sơ đồ: tiêu đề nhỏ + `{{ p.svg|safe }}`. Card có sơ đồ chiếm 2 cột (`style="grid-column:span 2"`; màn hẹp vẫn ổn
  vì grid auto-fill). Thêm nhãn `anh` (nếu có khóa `anh`: link mở ảnh qua route sẵn có? KHÔNG – bỏ qua `anh`).
  Thêm vào bảng `labels`: `'tiep_diem': 'Tiếp điểm'`, `'cuon_day_v': 'Cuộn dây (V)'`, `'relay': 'Relay'`, `'chan': 'Chân'`.

# Không làm
- KHÔNG sửa `static/style.css`, `tokens.css` (phiên khác đang sửa dở), `components.yaml`, `tests/`.
- Không thêm thư viện, CDN, JS, build. Không gọi mạng.

# Tiêu chí PASS
- Gate exit 0.
- Claude tự xem ảnh chụp trang `/library` (sáng + tối) trước khi duyệt.
