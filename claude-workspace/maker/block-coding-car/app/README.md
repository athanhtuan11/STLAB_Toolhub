# App kéo thả khối lệnh – xe robot STLab

Web app cho bé lớp 1 (6–7 tuổi) lập trình xe robot ESP32-S3 bằng khối icon: một dải lệnh
ngang, lưới ô 6 × 6 có xe ảo chạy thử, nút **Chạy xe thật** gửi chương trình qua WebSocket.
HTML/CSS/JS thuần – không framework, không CDN, không phụ thuộc npm.

Nguồn duy nhất cho định dạng chương trình, mã lỗi và mô phỏng: `../protocol/PROTOCOL.md`
(kèm `golden.json` do `make_golden.py` sinh). App không tự đổi ngữ nghĩa khối hay giới hạn.

## Chạy thử

- Mở trực tiếp **`dist/index.html`** bằng trình duyệt (một file, không cần máy chủ):
  chạy thử xe ảo; bấm vào ô tên xe để nhập `robot-do` khi muốn nối xe thật.
- Bản nguồn `src/index.html` dùng ES module nên cần phục vụ qua HTTP:
  `python -m http.server` trong `src/`, rồi mở `http://<may>/index.html`.
  Khi trang chạy bằng `http:`/`https:` app tự nối `ws://<host>/ws`.
- Trên xe thật, app được nhúng vào flash và phục vụ ở `http://robot-do.local/`.

## Cấu trúc

| Tệp | Việc |
|---|---|
| `src/sim.js` | `expand(doc)` và `simulate(steps, start, size)` – đúng PROTOCOL mục 1–3 |
| `src/program.js` | `LEVELS`, `buildDoc`, `countBlocks`, `canAdd` |
| `src/carlink.js` | trạng thái kết nối xe (`initialState`, `reduce`) + `msgRun/msgStop/msgHello` |
| `src/ui.js` | DOM: lưới, dải lệnh, kho khối, kéo thả, TTS, WebAudio, WebSocket |
| `src/index.html`, `src/style.css` | bố cục U1 + màu/icon lấy từ `../design/ui-mockups/u1-stage-top.html` |
| `build.py` | gộp thành 1 file HTML (nhúng flash), ghi `.gz` + bản chưa nén |
| `tests/` | gate (không sửa) |

## Cấp học và khối

- **Cấp 1:** Tiến, Lùi, Quay trái, Quay phải – tối đa 8 khối.
- **Cấp 2:** thêm Lặp (1 khung, không lồng), Âm thanh, Đèn mắt – tối đa 8 khối.
- **Cấp 3:** như Cấp 2, tối đa 12 khối; Tiến/Lùi chọn 1–4 ô.
- Khung Lặp chứa tối đa 6 khối. Khối Tiến/Lùi gửi `n` 1–4; Quay trái/phải không gửi `n`.
- Ô Bắt đầu (cờ xanh) cố định ở đầu dải, không xóa được. Không có khối Kết thúc, không khối Chờ.

## Build và kiểm

```sh
python build.py --out dist/index.html.gz   # ghi dist/index.html.gz + dist/index.html
node --test "tests/*.test.mjs"             # gate: golden 33 ca, program/carlink, bản gộp
```

Firmware gọi `python build.py` (xem `firmware/car/build.ps1`) rồi nhúng `dist/index.html.gz`.

## Ghi chú cho giáo viên

- Bấm khối trong kho = thêm vào cuối dải; kéo thả để sắp xếp, kéo vào khung Lặp, kéo ra ngoài để xóa.
- Bấm khối trên dải để đổi số: Tiến/Lùi 1–4 (Cấp 3), Lặp ×2/×3/×4, 3 kiểu âm thanh, 6 màu mắt.
- Giữ chuột/ngón tay khoảng 0,6 s trên khối để nghe tên tiếng Việt (nếu máy có giọng `vi-VN`).
- Bấm đúp vào ô lưới để dời ngôi sao (đích) – mặc định `[3, 2]`.
- **DỪNG** luôn hiện và luôn bấm được: gửi `stop` cho xe (nếu đang nối) và dừng xe ảo ngay.
- Nút Xuất/Nhập ở góc phải để lưu hoặc mở lại chương trình `.json`.
- Dải lệnh và cấp học được lưu trong `localStorage` của trình duyệt.

## An toàn

Xe dùng pin NiMH 4 × AA và nút Dừng cứng trên xe; app chỉ gửi chương trình đã mô phỏng
không chạm mép. Không cấp pin thẳng vào DevKit – xem `../hardware/BOM.md`.
