---
task: block-coding-car-app-v01
cwd: maker/block-coding-car/app
allow:
  - "src/*.js"
  - "src/index.html"
  - "src/style.css"
  - "build.py"
  - "package.json"
  - "README.md"
gate: "node --test \"tests/*.test.mjs\""
timeout_min: 30
max_rounds: 2
executor: auto
read: ["maker/block-coding-car/protocol", "maker/block-coding-car/design/ui-mockups", "maker/block-coding-car/design/brief.md"]
---

# Mục tiêu
App web kéo thả khối lệnh cho bé lớp 1 (6–7 tuổi) điều khiển xe robot ESP32-S3: dải lệnh ngang, lưới ô 6 × 6 có
**xe ảo** chạy thử, nút **Chạy xe thật** gửi chương trình qua WebSocket. HTML/CSS/JS thuần, không framework, không CDN.
App được nhúng vào flash xe (phục vụ ở `http://robot-do.local/`) và cũng mở được trực tiếp file (chỉ chạy thử, không xe).

# Đầu vào (chỉ đọc)
- `../protocol/PROTOCOL.md` – **nguồn duy nhất**: định dạng chương trình, quy tắc lỗi, bung bước, mô phỏng lưới, WebSocket.
- `../protocol/golden.json` + `../protocol/make_golden.py` – bản tham chiếu Python; `sim.js` phải cho kết quả y hệt.
- `../design/ui-mockups/u1-stage-top.html` – bố cục **U1 đã duyệt** (Tuan chọn): thanh trên (trạng thái xe, Chạy thử,
  Chạy xe thật, Cấp 1/2/3, DỪNG đỏ), lưới ô ở giữa, dải lệnh, kho khối theo màu ở đáy. **Lấy lại màu (`:root` tokens)
  và các icon SVG `<symbol>` trong file này**, bỏ font-face ngoài (dùng `system-ui, "Segoe UI", sans-serif`).
- `../design/brief.md` mục "Nguyên tắc app cho bé lớp 1" và "Quyết định".
- `tests/*.test.mjs` – gate, KHÔNG sửa.

# Yêu cầu
## Module (ES module trong `src/`, gate import trực tiếp)
- `src/sim.js`: `export function expand(doc)` → `{ok:true, steps}` | `{ok:false, code}`; `export function simulate(steps, start=[0,5,'N'], size=6)`
  → `{trace, final, edge}` (`edge` = `null` nếu không chạm mép). Đúng PROTOCOL mục 1–3. Không sửa `doc` đầu vào.
- `src/program.js`: `export const LEVELS` (`{1:{ops,maxBlocks:8,counts:false}, 2:{ops,maxBlocks:8,counts:false}, 3:{ops,maxBlocks:12,counts:true}}`;
  cấp 1 = fwd/back/left/right; cấp 2 và 3 = thêm repeat/sound/eye; `counts` = khối Tiến/Lùi có chọn số ô 1–4);
  `export function buildDoc(strip)` (dải lệnh `[{op,n?,body?}]` → `{v:1, prog}` đánh `id` 0,1,2… duyệt trước, KHÔNG gửi `n` cho left/right);
  `export function countBlocks(strip)`; `export function canAdd(strip, op, level, intoRepeat=false)` (op thuộc cấp, tổng khối < maxBlocks,
  không lồng repeat, body ≤ 6).
- `src/carlink.js`: `export function initialState()`, `export function reduce(state, msg)` (thuần, trả state mới; trường:
  `connected, name, color, fw, battMv, busy, running, activeId, stepIndex, stopWhy, lastError`), `export function msgRun(doc)`,
  `msgStop()`, `msgHello()` (trả chuỗi JSON). Xem `tests/program.test.mjs` để biết đúng hành vi.
- `src/ui.js`: phần DOM (không cần test đơn vị) – import 3 module trên.
- `package.json`: `{"type":"module","private":true}` – không thêm phụ thuộc npm.

## Giao diện (`src/index.html` + `src/style.css` + `src/ui.js`) – theo U1, màn 1920 × 1080 và 1366 × 768
- `id` bắt buộc: `conn` (icon xe màu thân + chấm trạng thái + tên), `btn-try` (Chạy thử), `btn-real` (Chạy xe thật), `level-1/2/3`,
  `btn-stop` (chữ **DỪNG**, nền đỏ `--fail`, **luôn hiện và luôn bấm được**), `grid` (lưới 6 × 6), `strip` (dải lệnh), `palette` (kho khối),
  `btn-clear` (xóa dải lệnh, icon thùng rác).
- Khối ≥ **96 px** trên dải lệnh, ≥ 80 px trong kho; màu nhóm: di chuyển `--move`, điều khiển `--ctrl`, âm thanh/đèn `--snd`.
  Ô **Bắt đầu** (cờ xanh) cố định ở đầu dải, không xóa được. Không có khối Kết thúc, không khối Chờ.
- **Bấm khối trong kho = thêm vào cuối dải** (bé lớp 1 kéo còn vụng); kéo thả (Pointer Events, chạy cả chuột lẫn cảm ứng) để
  sắp xếp lại / kéo vào khung Lặp / kéo ra ngoài để xóa. Bấm khối trên dải → nút nhỏ đổi số (Tiến/Lùi 1–4 ở cấp 3, Lặp ×2/×3/×4,
  âm thanh 3 loại, màu mắt 6 màu) – hiển thị bằng hình/chấm màu + chữ số, không câu chữ dài.
- Lặp = 1 khung vàng chứa khối bên trong (như mockup), nhãn ×n.
- Khi `canAdd` = false: khối kho mờ đi, rung nhẹ khi bấm.
- Giữ chuột/ngón tay ~0,6 s trên khối → đọc tên tiếng Việt bằng `speechSynthesis` (giọng `vi-VN` nếu có; không có thì im) –
  tên: Tiến, Lùi, Quay trái, Quay phải, Lặp lại, Âm thanh, Đèn mắt.
- **Chạy thử**: xe ảo chạy theo `simulate` (mỗi ô ~0,6 s, quay ~0,4 s, có chuyển động mượt CSS), khối đang chạy sáng lên
  (`.run` như mockup), âm `sound` phát bằng WebAudio (âm ngắn, nhỏ), `eye` đổi màu mắt xe ảo. Chạm mép → xe dừng, ô đó
  nhấp nháy đỏ, khối gây lỗi viền đỏ. Ô ngôi sao (đích) mặc định ở `[3,2]`; giáo viên bấm đúp vào ô lưới để dời ngôi sao.
  Xe kết thúc trên ngôi sao → hiệu ứng ăn mừng (sao xoay + âm vui).
- **Chạy xe thật**: chỉ bật khi `connected && !running` và mô phỏng không chạm mép; gửi `msgRun(buildDoc(strip))`; tô sáng khối
  theo tin `step` (`activeId`); xe ảo đi theo từng bước cùng lúc. `err` → hiện thông báo icon + chữ ngắn (`msg` của xe).
- **DỪNG**: gửi `msgStop()` (nếu có kết nối) và dừng xe ảo ngay.
- Kết nối: nếu trang phục vụ qua `http:` → WebSocket `ws://${location.host}/ws`; mở bằng `file:` → ô nhập tên xe (vd `robot-do`)
  trong hộp thoại bấm vào `conn`. Tự nối lại sau 2 s khi mất kết nối; chấm trạng thái: xanh lá = nối, vàng = đang nối, xám = không có xe.
  Icon xe trong `conn` tô bằng `color` xe gửi. Pin < 4400 mV → icon pin đỏ cạnh tên.
- Lưu dải lệnh + cấp đang chọn vào `localStorage` (bọc try/catch); có nút nhỏ Xuất/Nhập file `.json` cho giáo viên (góc phải, icon).
- Đổi cấp: khối không thuộc cấp mới bị bỏ khỏi dải (hỏi lại bằng hộp xác nhận có icon).
- Tiếng Việt có dấu trong mọi chữ hiển thị; `<html lang="vi">`, `<meta charset="utf-8">`.

## `build.py`
- `python build.py --out <đường dẫn>.html.gz` (mặc định `dist/index.html.gz`): gộp `index.html` + `style.css` + các module
  `sim.js, program.js, carlink.js, ui.js` (theo thứ tự đó) thành 1 file HTML, xóa dòng `import ...` và tiền tố `export `
  để chạy trong **một** `<script>` thường; ghi thêm `dist/index.html` (chưa nén) để mở xem. Chỉ dùng thư viện chuẩn Python.
- Firmware gọi đúng lệnh này (`firmware/car/build.ps1`) để nhúng app.

# Không làm
- Không sửa `tests/`, `../protocol/`, `../firmware/`, `../design/`.
- Không thêm thư viện npm/CDN/font ngoài, không framework (React/Vue/Blockly…).
- Không chép icon/nhân vật/giao diện ScratchJr – dùng icon SVG sẵn trong mockup U1.
- Không tự đổi ngữ nghĩa khối, giới hạn số khối, mã lỗi (đã chốt trong PROTOCOL.md).

# Tiêu chí PASS
- Lệnh gate exit 0 (mô phỏng khớp 33 ca golden, program/carlink, bản gộp < 150 KB gzip, cú pháp đúng).
- Claude tự kiểm thêm: mở `dist/index.html` chụp ảnh 1920 × 1080 + 1366 × 768, chạy thử chương trình mẫu.
