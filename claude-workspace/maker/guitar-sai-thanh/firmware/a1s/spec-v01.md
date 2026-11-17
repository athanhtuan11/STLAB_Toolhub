# Spec firmware v0.1 – mạch thay thế đàn GUITAR UMI trên ESP32-A1S (Claude viết 2026-11-17)

Mục tiêu: bản thử trên bàn. Tiếng vào **LINE IN** của A1S (sau này là pickup) → ES8388 ADC → ESP32 xử lý (âm lượng, âm sắc, echo,
nhạy dây, tự cân bằng, 3D) → ES8388 DAC → loa (ampli trên bo, PA GPIO21) + tai nghe. **App Umi Music kết nối được** vì firmware giả lập
đúng giao thức BLE của đàn gốc (`../../docs/ble-protocol.md`).

## Thư mục / build
- `maker/guitar-sai-thanh/firmware/a1s/` – ESP-IDF **5.5.4**, target `esp32`, project name `guitar_a1s` → `build/guitar_a1s.bin`.
- `build.ps1` theo mẫu `maker/english-teacher/firmware/probe-a1s/build.ps1` (IdfId `esp-idf-20ee62e792ea89630ac6a777ab3ebc57`, xóa biến MSYS,
  xóa .bin cũ trước khi build). Bảng phân vùng: app ≥ 1,94 MB (vd `partitions.csv` 1 factory 0x1F0000 + nvs), flash 4 MB.
- `sdkconfig.defaults`: NimBLE (`CONFIG_BT_ENABLED=y`, `CONFIG_BT_NIMBLE_ENABLED=y`, tắt Bluedroid), PSRAM tắt được (v0.1 không cần).
- Gate: `..\..\..\block-coding-car\firmware\.venv-host\Scripts\python.exe tests\test_gate.py` (đặt `GATE_NO_BUILD=1` khi lặp nhanh, gate
  cuối phải có build). **Không sửa** `tests/`.

## Phần cứng A1S (đã dò thật 2026-11-05, `maker/english-teacher/CLAUDE.md`)
- ES8388 @0x10, I2C SCL32 SDA33; I2S MCLK0 BCK27 WS25 DOUT26 DIN35; PA GPIO21; nút KEY1–6 = GPIO36,13,19,23,18,5; LED GPIO22.
- Khởi tạo ES8388: dùng lại trình tự thanh ghi trong `maker/english-teacher/firmware/probe-a1s/main/probe_a1s_main.c` (đã phát + thu được trên
  bo này). Thêm: chọn ngõ vào ADC bằng hằng `GUITAR_ADC_INPUT` (1 = LIN1/RIN1, 2 = LIN2/RIN2; mặc định **1** – line-in; `TODO` xác nhận khi
  thử). **Không** dùng/không chép mã RudeBox (không license).
- I2S std **44100 Hz**, 16 bit, stereo, song công (tx + rx), MCLK 256·fs. Khung xử lý 256 mẫu.

## Module (giao diện cố định – gate gọi đúng tên)
`main/umi_proto.h/.c` (C thuần, không phụ thuộc ESP-IDF):
```c
#define UMI_FRAME_LEN 129
typedef struct { uint8_t p[UMI_FRAME_LEN]; } umi_state_t;
void umi_state_default(umi_state_t *s);   // p[8..40] = 0d 00 00 11 00 00 00 14 00 00 00 0c 4b 00 00 00 00 1e 00 00 00 00 14 00 0f, còn lại 0
int  umi_handle_write(umi_state_t *s, const uint8_t *d, size_t n, int *changed);
     // 55 ff fe 01 -> return 1, *changed=0.  n==129 && d[0..3]==03 00 01 00 -> chép d[8..128] vào s->p[8..128] rồi chặn khoảng:
     // [8],[15],[19],[25],[27] 0..30 | [20] <88 -> 75, >=88 -> 100 | [21] !=0 -> 2 | [22],[45] !=0 -> 1 ; return 1, *changed = có byte đổi.
     // khác -> return 0 (bỏ qua, không đổi s).
void umi_build_status(const umi_state_t *s, uint8_t batt_dv, uint8_t *out);  // 03 10 01 00 batt 00 00 00 + s->p[8..128]
```
`main/dsp.h/.c` (C thuần, float được):
```c
typedef struct { int volume, tone, echo, mic, string_sens, auto_bal, amp_out, fx3d; } dsp_params_t;
void  dsp_params_from_state(const umi_state_t *s, dsp_params_t *o); // [15],[19],[27],[25],[20],[21],[22],[45]
int   dsp_init(int sample_rate);          // cấp bộ đệm echo tĩnh/heap tối đa 400 ms, xóa trạng thái; 0 = OK
void  dsp_set(const dsp_params_t *p);
void  dsp_process(const int16_t *in_l, const int16_t *in_r, int16_t *out_l, int16_t *out_r, int n); // v0.1: dùng in_l (mono), bỏ in_r
float dsp_volume_gain(int volume);         // 0 -> 0.0, 30 -> 1.0, tăng dần (vd (v/30)^2)
```
Chuỗi DSP (số do Claude chốt):
1. Nhạy dây [20]: 75 → hệ số 1,0; 100 → 1,6.
2. Âm sắc [19]: **high-shelf biquad 2 kHz**, độ lợi = (tone − 15) × 0,6 dB (0 → −9 dB, 30 → +9 dB); **tone 15 = bỏ qua bộ lọc** (đi qua nguyên).
3. Tự cân bằng [21] = 2: nén đơn giản (ngưỡng −18 dBFS, tỉ lệ 4:1, attack 5 ms, release 200 ms); 0 = bỏ qua.
4. Echo [27]: trễ **250 ms**, mix = echo/30 × 0,5, phản hồi 0,35; echo 0 = bỏ qua (không cộng gì).
5. Âm lượng [15]: × `dsp_volume_gain`.
6. 3D [45] = 1: làm rộng stereo (vd phải = trễ 12 ms + trộn ngược pha nhẹ); 0 → trái = phải.
7. Giới hạn đỉnh: bão hòa về ±32767 (không tràn số); mẫu dưới ngưỡng không bị đổi (đường phẳng phải đi qua nguyên ±2 LSB).
- [25] mic, [22] ngõ ra âm ly, [8]/[11] LED: v0.1 chỉ lưu + báo lại (A1S không có các phần đó) – ghi `TODO`.

## BLE (NimBLE)
- Tên quảng bá **"GUITAR UMI"** (hằng `GUITAR_BLE_NAME`), quảng bá UUID dịch vụ 16-bit **0x2B00**.
- Service 0x2B00: char **0x2B12** write + write-no-rsp; **0x2B10** notify; **0x2B16** write + write-no-rsp + notify.
- Ghi vào 0x2B12 hoặc 0x2B16 → `umi_handle_write`; trả 1 → notify khung trạng thái (`umi_build_status`) trên **cả 0x2B10 và 0x2B16**,
  cắt còn (MTU − 3) byte nếu MTU nhỏ (đàn gốc cũng vậy). Có đổi → `dsp_set` + hẹn lưu NVS sau 2 s.
- Notify trạng thái định kỳ **15 s** khi có kết nối. Pin: A1S không đo được → `batt_dv` = 120 (12,0 V) cố định, `TODO`.
- Ngắt kết nối → quảng bá lại.

## Khác
- NVS: lưu `p[8..128]` (blob), nạp khi khởi động; không có thì `umi_state_default`.
- Nút: KEY5 (GPIO18) âm lượng −1, KEY6 (GPIO5) +1 (chống dội 30 ms), đổi → notify + lưu.
- UART 115200 lệnh: `STAT` (in byte chính), `SET <idx> <val>` (qua `umi_handle_write`), `IN 1|2` (đổi ngõ vào ADC), `TONE` (phát sine 1 kHz 2 s
  để thử loa, âm lượng theo [15]).
- **Trần an toàn tai/loa**: thêm hằng `GUITAR_OUT_MAX` = 0,7 (nhân sau âm lượng) – v0.1 để mặc định 0,7. (Ghi chú: gate dùng `dsp_process`
  thuần, trần này áp ở tầng ghi I2S trong main, không trong dsp.c.)

## Không làm
- Không đụng mạch đàn gốc, không nạp mạch (Claude/Tuan nạp sau). Không sửa `tests/`. Không thêm thư viện ngoài ESP-IDF.

## PASS
- `test_gate.py` exit 0 có build thật. Báo cáo: kích thước bin, % phân vùng, những `TODO`.

## Kế hoạch v0.2 (Tuan 2026-11-17: "có thể sử dụng bluetooth thay thế" dây line-in)
- Thêm **A2DP sink** (điện thoại phát nhạc qua Bluetooth Classic vào A1S) → đổi NimBLE sang **Bluedroid dual-mode** (BLE GATT 0x2B00 giữ nguyên).
- Luồng A2DP (SBC 44,1 kHz) qua ring buffer, trộn vào đầu vào chuỗi DSP cùng tiếng line-in/pickup (cùng âm lượng/âm sắc/echo).
- Thử phần cứng: loa 4 Ω gắn cổng **Left** của A1S (kênh trái = kênh chính).
- Làm sau khi v0.1 PASS + thử app Umi trên mạch thật.
