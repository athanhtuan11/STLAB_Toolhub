# Spec: màn tương tác chữ viết Cú Bông (firmware + cầu nối) – Claude viết 2026-11-28

Thiết kế đã chốt (Tuan "bạn tự chọn"): `../../design/screen-literacy-spec.md`, mockup `../../design/make_screen_literacy.py`
(hàm `screen()` với K = 1 → đúng pixel 320 × 240). Chốt: làm đủ 6 màn; màn B + C chỉ bé > 3 tuổi; hình **Twemoji 14.0.2
(CC BY 4.0)**; chữ **thường** hết; phông **Andika Bold (SIL OFL)**.

## 0. Giao thức chung (KHÔNG đổi – 2 phần làm song song dựa vào đây)
Máy chủ → bo: JSON-RPC `tools/call` qua `{"type":"mcp"}` (bridge `mcp_call`). Bo khai báo bằng `McpServer::AddTool` trong `stlab_s3.cc`:
| Tool | Tham số | Màn |
|---|---|---|
| `self.screen.show_word` | `word` (string a–z, cách, `-`) | A thẻ từ (gạch chân vàng chạy ~220 ms/chữ khi cô đang nói) |
| `self.screen.show_pick` | `target`, `other` | B chọn 1 trong 2 (vị trí trái/phải do BO trộn ngẫu nhiên) |
| `self.screen.show_letter` | `word` | C chữ cái đầu + thẻ nhỏ |
| `self.screen.show_stickers` | `words` (string, cách nhau dấu phẩy, tối đa 3) | D sticker cuối buổi |
| `self.screen.clear` | – | về đôi mắt |
Mỗi tool trả `true` ngay (không chờ vẽ xong). Từ không có hình → chỉ hiện chữ to hơn (màn vẫn chạy).

Bo → máy chủ khi bé chạm (chỉ khi kênh đang mở): `SendMcpMessage` một **notification** JSON-RPC (không `id`):
`{"jsonrpc":"2.0","method":"notifications/stlab_touch","params":{"screen":"word|pick|letter|sticker","word":"cat","correct":true|false|null}}`
(`correct` chỉ có nghĩa ở `pick`). Chống dội 400 ms; mỗi lần chạm 1 notification.

## 1. Phần BO (firmware) – thư mục `firmware/xiaozhi-s3`
- `OwlEyesDisplay`: thêm lớp thẻ theo mockup (tọa độ/màu/cỡ lấy từ `make_screen_literacy.py`, K = 1): nền `#0A0F18`, thẻ kem
  `#FFF3DF` bo góc 18, chữ `#22304A`, chữ cái đầu cam `#FF8A3D`, viền vàng `#FFC83D` khi cô đọc, đúng = viền xanh `#5BD27A` dày 6
  + sao, thẻ sai/không chọn mờ `#5A6273`. **Mắt thu nhỏ** ở dải trên (tâm y 26, x 134/186, r 17), vẫn đổi màu theo trạng thái.
- Tự về đôi mắt sau **8 s** không chạm (màn B: **15 s**). `Khen` (SetEmotion happy) khi đang ở thẻ: mắt nhỏ cười, thẻ giữ.
- Vùng chạm: cả thẻ (màn A), mỗi thẻ (B), ô chữ cái (C), mỗi sticker (D). Chạm màn A/D/C → chớp viền + notification.
  Chạm B → đúng: viền xanh + sao + notification `correct:true`; sai: thẻ rung ±6 px 300 ms + `correct:false` (được chọn lại).
- Tọa độ chạm XPT2046 → màn: hiệu chỉnh thô bằng `cfg.x_max/y_max` + cờ swap/mirror giống màn; chỉ cần đúng NỬA TRÁI/PHẢI và
  trên/dưới (thẻ to). Ghi `// hieu chinh` trong config.h: `TOUCH_SWAP_XY`, `TOUCH_MIRROR_X`, `TOUCH_MIRROR_Y` (mặc định theo màn).
- **Hình:** script `assets/make_pics.py`: đọc từ mới Seed 1–3 trong `../../lessons-seed/ROADMAP.md` (dòng `new:`), bảng
  `assets/pic-map.yaml` (word → mã emoji Twemoji, `null` nếu không có hình hợp – KHÔNG ép hình sai nghĩa), tải PNG 72 × 72 từ
  `https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/<ma>.png` (cache `assets/.cache/`, gitignore), đổi sang ảnh
  LVGL 9 RGB565A8 (`.bin` có header `lv_image_header_t`), ghi `assets/pics/<word>.bin` (gitignore – sinh lại được). Đưa vào phân vùng
  assets bằng `DEFAULT_ASSETS_EXTRA_FILES` cho bo stlab-s3 (patch mới `0004-...` + `sync.ps1` chạy `make_pics.py` trước build).
  Bo đọc bằng `Assets::GetAssetData("<word>.bin")` (mmap, không chép RAM).
- **Phông:** Andika Bold (google/fonts `ofl/andika`, ghi commit/URL + OFL.txt vào `assets/fonts/`), `npx lv_font_conv@1.5.2`
  bpp 4, ký tự a–z + `- '`: cỡ **52** (thẻ) , **34** (thẻ nhỏ/sticker), **120** (chữ cái màn C, chỉ a–z). File C trong `boards/stlab-s3/`.
- Ghi công Twemoji trong `README.md`: "Hình: Twemoji © Twitter, Inc và người đóng góp – CC BY 4.0".
- Không đổi âm thanh/AEC/nút/OTA; không nạp bo, không `release.ps1`, không commit. `check_s3.py` + `check_display.py` phải vẫn PASS.
- Gate: `python check_literacy.py` (sau `sync.ps1` + `build.ps1`).

## 2. Phần MÁY CHỦ (cầu nối) – thư mục `server`
- `live/screen.py` mới (thuần, test được): `find_lesson_word(text, words, recent)` (khớp nguyên từ, không phân biệt hoa thường,
  cụm 2 từ như "thank you"; bỏ từ đã hiện trong **10 s**), `touch_to_prompt(params, word_list, older)` → câu chèn cho Gemini
  (tiếng Anh ngắn, kèm 1 câu Việt nếu cần), vd `"[touch] The child tapped the card 'cat'. Say 'cat' again slowly, once."`;
  pick đúng → `"[touch] The child chose 'cat' – correct! Praise in one short sentence."`, sai → gợi ý lại 1 câu không chê.
- `bridge.py`: (a) khi lời cô (output transcription) chứa từ của buổi (new + review hiện tại) → `mcp_call("tools/call",
  {"name":"self.screen.show_word","arguments":{"word":w}})` **không chặn** luồng âm thanh (task nền, lỗi chỉ log);
  (b) tool Gemini mới chỉ khai khi bé > 3 tuổi: `show_pick(target, other)` và `show_letter(word)` → gọi tool bo tương ứng;
  thêm 1 câu vào chỉ dẫn OLDER: "When you ask the child to choose between two words, call show_pick first."
  (c) cô chào tạm biệt / hết buổi → `show_stickers` với tối đa 3 từ mới của buổi; (d) nhận `notifications/stlab_touch` từ bo →
  `touch_to_prompt` → chèn bằng hàm chèn chữ đã có (send_client_content, dự phòng send_realtime_input). Không có bo màn (bo trả lỗi
  tool) → im lặng bỏ qua, buổi học chạy như cũ.
- Gate: `runtime\.venv\Scripts\python.exe -m pytest` không có → chạy `python -m pytest server/test_screen_literacy.py -q` + các test
  cũ `test_praise_emotion.py test_volume_intent.py test_curriculum.py test_seed_lessons.py` vẫn PASS. KHÔNG khởi động lại máy chủ.

## Không làm
- Không tô chữ/viết, không game phụ, không âm thanh mới, không hotspot trang trí. Không sửa `community/`, gate của Claude, `org/`.
