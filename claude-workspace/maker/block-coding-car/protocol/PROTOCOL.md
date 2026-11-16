# Giao thức + ngữ nghĩa khối – block-coding-car v1

Claude chốt 2026-11-16. **Nguồn duy nhất** cho firmware (`firmware/car/main/prog.c`) và app (`app/src/sim.js`).
Ca kiểm chung: `golden.json` (sinh bằng `make_golden.py` – bản tham chiếu Python của chính đặc tả này).
Đổi ngữ nghĩa → sửa file này + `make_golden.py` → chạy lại → cả 2 gate phải PASS lại.

## 1. Chương trình (JSON)
```json
{"v": 1, "prog": [ {"id": 0, "op": "fwd", "n": 2}, {"id": 1, "op": "repeat", "n": 2, "body": [ {"id": 2, "op": "left"} ]} ]}
```
| op | Nhóm (màu) | `n` | Ý nghĩa |
|---|---|---|---|
| `fwd` | di chuyển (xanh dương) | 1–4, mặc định 1 | Tiến n ô (1 lần chạy liền) |
| `back` | di chuyển | 1–4, mặc định 1 | Lùi n ô |
| `left` | di chuyển | bỏ qua | Quay trái 90° tại chỗ |
| `right` | di chuyển | bỏ qua | Quay phải 90° tại chỗ |
| `sound` | âm thanh/đèn (tím) | 0–2, mặc định 0 | 0 bíp · 1 còi xe · 2 nhạc vui (~1 s) |
| `eye` | âm thanh/đèn | 0–5, mặc định 0 | màu mắt: 0 đỏ · 1 xanh lá · 2 xanh dương · 3 vàng · 4 tím · 5 tắt |
| `repeat` | điều khiển (vàng) | 2–4, mặc định 2 | Lặp `body` n lần |

Quy tắc hợp lệ (vi phạm → lỗi, KHÔNG chạy gì):
- `v` phải = 1 (`bad_version`); `prog` là mảng không rỗng (`empty`). JSON hỏng / thiếu `prog` → `bad_json`.
- `id`: số nguyên 0–999, không trùng trong toàn chương trình kể cả trong `body` (`dup_id`; thiếu/sai kiểu → `bad_arg`).
- `op` lạ → `bad_op`. `n` không phải số nguyên hoặc ngoài khoảng → `bad_arg`.
- `repeat`: `body` là mảng 1–6 khối (`empty_repeat` nếu rỗng/thiếu, >6 → `too_many_blocks`), **không lồng** `repeat` (`nested_repeat`).
- Tổng số khối (đếm cả khối `repeat` và khối trong `body`) ≤ **12** (`too_many_blocks`).
- Không giới hạn riêng số bước: 12 khối + repeat ≤ 4 + body ≤ 6 ⇒ tối đa 40 bước.
- Khóa lạ trong khối: bỏ qua. Ca kiểm lỗi trong golden mỗi ca chỉ có đúng 1 vi phạm.

## 2. Bung thành bước (expand)
Duyệt theo thứ tự; `repeat` bung `body` n lần, **bản thân khối repeat không sinh bước**.
Mỗi bước = `[id, op, arg]`: `arg` = n đã áp mặc định với `fwd/back/sound/eye`; `arg` = 0 với `left/right`.
Xe gửi `{"t":"step","i":<chỉ số bước>,"id":<id>}` khi BẮT ĐẦU mỗi bước → app tô sáng khối `id`.

## 3. Mô phỏng trên lưới (chỉ app)
- Lưới 6 × 6 ô (1 ô = 150 mm thật). `x` cột 0–5 trái→phải, `y` hàng 0–5 trên→dưới. Hướng `N E S W` (N = lên trên).
- Xuất phát mặc định `{x:0, y:5, h:"N"}` (góc dưới trái, mặt hướng lên).
- `fwd n`: đi từng ô theo hướng; `back n`: đi từng ô ngược hướng (mặt giữ nguyên). `left`: N→W→S→E→N; `right`: ngược lại.
- Ô kế tiếp ra ngoài lưới → **dừng chương trình**, `edge = id` khối đó, xe đứng ở ô hợp lệ cuối cùng (không chạy bước sau).
- `sound`, `eye`: không đổi vị trí.
- `trace` = vị trí `[x, y, h]` SAU mỗi bước đã chạy xong (bước gặp mép: ghi vị trí đã dừng, rồi kết thúc).
- App chỉ bật nút **Chạy xe thật** khi mô phỏng không gặp mép (xe thật không biết mép thảm).

## 4. WebSocket `ws://<xe>/ws` (JSON text, 1 thông điệp / frame)
App → xe:
| `t` | Trường | Xe làm |
|---|---|---|
| `hello` | – | trả `hello` |
| `run` | `prog` (mảng như mục 1) | kiểm + bung; lỗi → `err`; đang chạy → `err busy`; pin yếu → `err batt_low`; OK → `started` rồi chạy |
| `stop` | – | dừng ngay (≤ 50 ms), nhả cuộn, tắt loa → `stopped why:"client"` |
| `dry` | `prog` | chỉ kiểm + bung, KHÔNG chạy → `dry` hoặc `err` (để so khớp với app) |
| `cal` | `steps_cell`, `steps_90` (số nguyên 1000–8000 / 500–4000) | lưu NVS → `cal` (giáo viên chỉnh) |

Xe → app:
| `t` | Trường |
|---|---|
| `hello` | `name` (vd `robot-do`), `color` (`#RRGGBB` màu thân), `fw` (`0.1.0`), `batt_mv`, `busy` (bool), `steps_cell`, `steps_90` |
| `started` | `n` (số bước) |
| `step` | `i`, `id` |
| `done` | – (chạy hết, đã nhả cuộn) |
| `stopped` | `why`: `client` \| `button` \| `batt` \| `wifi` |
| `err` | `code` (mã ở mục 1, hoặc `busy`, `batt_low`, `bad_msg`), `msg` (tiếng Việt ngắn cho giáo viên) |
| `dry` | `steps`: mảng `[id, op, arg]` |
| `cal` | `steps_cell`, `steps_90` |
| `batt` | `mv` – gửi mỗi 5 s tới mọi client |

- Nhiều app cùng mở 1 xe: mọi client nhận `step/done/stopped/batt`; chỉ 1 chương trình chạy một lúc.
- Mất kết nối client đang chạy: **xe vẫn chạy hết** chương trình (bé còn nút Dừng trên xe), không dừng giữa chừng.

## 5. Xe thật (firmware)
- 28BYJ-48 nửa bước (8 pha), 2 motor chạy cùng lúc, đồng bộ bước (cùng số bước, cùng nhịp).
  Tiến: 2 bánh lăn về trước (motor trái và phải gắn đối xứng → chiều quay ngược nhau, đặt bằng `DIR_LEFT`/`DIR_RIGHT` trong `pins.h`).
  Quay trái tại chỗ: bánh trái lùi, bánh phải tiến, mỗi bánh `steps_90` bước.
- Mặc định (tính từ BOM, `TODO` hiệu chỉnh trên thảm thật): `steps_cell = 4054` (150 mm / (π·48 mm) × 4076 bước/vòng),
  `steps_90 = 1231` (vết bánh 58 mm theo CAD: π·58 mm / 4 / (π·48 mm) × 4076). Lưu NVS namespace `car`.
- Tốc độ: khởi động 200 bước/s, tăng tuyến tính tới tối đa 500 bước/s trong 300 bước đầu, giảm đối xứng cuối đoạn
  (giới hạn kéo vào > 600 Hz theo datasheet – không vượt 500). Nghỉ 300 ms giữa 2 bước.
- **Nhả cuộn** (4 chân về 0) khi xong/dừng/lỗi. Nút Dừng (GPIO13, kéo lên nội, chống dội 30 ms) dừng mọi lúc kể cả khi không có Wi-Fi.
- Pin (chia áp 1/2 → GPIO1 ADC1, có hiệu chỉnh ADC): `batt_mv` = mV ở pin. < **4400 mV** → từ chối `run` (`batt_low`);
  đang chạy < **4200 mV** liên tục 2 s → dừng (`stopped why:"batt"`). `TODO` chỉnh ngưỡng khi đo xe thật (NiMH 1,1 / 1,05 V/cell).
- Âm thanh I2S MAX98357A: tự sinh âm (không file), biên độ ≤ 30 % để bảo vệ tai trẻ. Mắt WS2812 ×2 (RMT, `led_strip`).
- Màu mắt trạng thái (khi không chạy chương trình): xanh lá = Wi-Fi OK chờ lệnh · xanh dương nhấp nháy = đang nối Wi-Fi ·
  vàng = chế độ điểm phát (AP) · đỏ nhấp nháy = pin yếu. Độ sáng ≤ 25 %.
- Wi-Fi: STA theo NVS (`wifi` / `ssid`, `pass`), nạp bằng lệnh UART `WIFI <ssid>\t<pass>` (như esp32-s3-cam). Không có cấu hình
  hoặc 20 s không nối được → bật AP `robot-<màu>` (không mật khẩu, IP 192.168.4.1) để dạy không cần mạng lab.
- Tên: NVS `car`/`name` (mặc định `robot-do`), `color` (mặc định `#E0453A`); lệnh UART `NAME <ten> <#mau>`. mDNS `<name>.local`.
- HTTP: `/` = app (gzip nhúng flash), `/ws`, `/info` (JSON như `hello`), `POST /ota` (khóa `X-OTA-Key`, như esp32-s3-cam), rollback bật.
