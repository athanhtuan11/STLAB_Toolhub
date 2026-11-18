# Spec firmware v0.3 – A2DP sink (nhạc Bluetooth từ điện thoại) cho GUITAR UMI trên ESP32-A1S (Claude viết 2026-11-18)

Nền: v0.1 (`spec-v01.md`, 2026-11-18 mặc định mic trên bo IN 2 + PGA 24 dB, lưu NVS). Looper v0.2 đã HỦY (Tuan: "loop" = tiếng đàn ra loa ngay, v0.1 đã làm; bản dở ở backup/20261118-guitar-looper-wip). v0.3 **giữ nguyên mọi hành vi v0.1**
(giao thức UMI, chuỗi DSP, NVS, KEY5/6, UART, trần `GUITAR_OUT_MAX`) và thêm: điện thoại ghép đôi Bluetooth Classic với "GUITAR UMI",
phát nhạc (A2DP, SBC) → trộn với tiếng đàn → loa.

## 1. Đổi ngăn xếp BT: NimBLE → Bluedroid dual-mode
- `sdkconfig.defaults`: `CONFIG_BT_ENABLED=y`, `CONFIG_BT_BLUEDROID_ENABLED=y`, `CONFIG_BT_NIMBLE_ENABLED=n`,
  `CONFIG_BTDM_CTRL_MODE_BTDM=y`, `CONFIG_BT_CLASSIC_ENABLED=y`, `CONFIG_BT_A2DP_ENABLE=y`, `CONFIG_BT_BLE_ENABLED=y`,
  `CONFIG_BT_GATTS_ENABLE=y`, `CONFIG_BT_GATTC_ENABLE=n` (không cần), `CONFIG_BT_SSP_ENABLED=y`.
  Nếu thiếu RAM: bật PSRAM (`CONFIG_SPIRAM=y`, bo có 8 MB, map 4 MB – `tools/esp32-a1s/README.md`) và đặt bộ đệm echo/ring vào PSRAM được.
- Sau khi đổi sdkconfig.defaults phải xóa `sdkconfig` + `build/` cũ (build.ps1 tự set-target khi thiếu) – **chuyển** `sdkconfig`, `sdkconfig.old`
  cũ vào `../../../../backup/2026xxxx-guitar-v03-nimble-sdkconfig/` (không xóa hẳn).
- BLE viết lại bằng **Bluedroid GATTS** (`esp_ble_gatts_*`, `esp_ble_gap_*`), **giữ đúng** giao diện v0.1:
  tên quảng bá "GUITAR UMI" (`GUITAR_BLE_NAME`), quảng bá UUID 16-bit 0x2B00; service 0x2B00: char 0x2B12 write + write-no-rsp; 0x2B10 notify
  (+CCCD 0x2902); 0x2B16 write + write-no-rsp + notify (+CCCD). Ghi → `umi_handle_write` → notify trạng thái trên cả 0x2B10 và 0x2B16
  (cắt còn MTU − 3), notify định kỳ 15 s, ngắt → quảng bá lại, có đổi → `dsp_set` + lưu NVS sau 2 s. Như v0.1.
  Đàn gốc gửi notify kể cả khi app chưa bật CCCD? Không rõ → gửi khi CCCD bật **hoặc** sau khi nhận lệnh ghi đầu tiên (app Umi có thể không
  ghi CCCD). `TODO` xác nhận bằng app thật.
- Mẫu tham khảo (đọc, không chép nguyên): `C:\Espressif\frameworks\esp-idf-v5.5.4\examples\bluetooth\bluedroid\classic_bt\a2dp_sink_stream`,
  `...\bluedroid\ble\gatt_server`, `...\bluedroid\coex\a2dp_gatts_coex` (đúng trường hợp A2DP + GATTS chung).

## 2. Bluetooth Classic / A2DP
- Tên Classic = "GUITAR UMI" (`esp_bt_gap_set_device_name`). Khi chưa có kết nối A2DP: connectable + discoverable
  (`esp_bt_gap_set_scan_mode(ESP_BT_CONNECTABLE, ESP_BT_GENERAL_DISCOVERABLE)`); khi đã kết nối: connectable, non-discoverable.
- SSP "Just Works": IO capability = `ESP_BT_IO_CAP_NONE`; tự xác nhận `ESP_BT_GAP_CFM_REQ_EVT`. Không mã PIN. Chỉ 1 nguồn A2DP cùng lúc.
- `esp_a2d_sink_init()` + `esp_a2d_sink_register_audio_data_callback` **hoặc** `esp_a2d_register_data_callback`
  (API nào có trong IDF 5.5.4 và chạy với SBC giải mã sẵn ra PCM 16 bit stereo xen kẽ – xem ví dụ a2dp_sink_stream).
- Tần số mẫu nguồn đọc từ `ESP_A2D_AUDIO_CFG_EVT` (SBC: 16000/32000/44100/48000) → `mix_set_src_rate`.
- Không làm AVRCP (không âm lượng tuyệt đối): điện thoại tự giảm PCM theo nút âm lượng của nó. Âm lượng app Umi [15] vẫn chi phối tổng.
- Callback dữ liệu chạy trên tác vụ BT: **chỉ** gọi `mix_push_pcm` (không printf, không khóa lâu).
- Ngắt A2DP / dừng phát → `mix_reset` (xả ring, không phát đuôi cũ).

## 3. Module mới `main/mix.h/.c` (C thuần, không phụ thuộc ESP-IDF – gate gọi đúng tên)
```c
#define MIX_RATE       44100
#define MIX_RING_CAP   8820   // mẫu mono int16 trong ring (200 ms @ 44,1 kHz)
#define MIX_PRIME      4410   // phải có >= 100 ms mới bắt đầu phát (và sau mỗi lần cạn)
typedef struct { ... } mix_t;  // tự định nghĩa; KHÔNG cấp phát động trong mix_push_pcm/mix_pop
void     mix_init(mix_t *m);                  // ring rỗng, src_rate = 44100, bộ đếm = 0
void     mix_reset(mix_t *m);                 // xả ring + trạng thái resampler, giữ src_rate và bộ đếm
void     mix_set_src_rate(mix_t *m, int hz);  // 16000/32000/44100/48000; giá trị khác -> giữ nguyên rate cũ, return-không có
int      mix_push_pcm(mix_t *m, const int16_t *lr, int frames);
         // lr = L,R xen kẽ, `frames` khung. Trộn mono (L+R)/2 -> đổi tần số tuyến tính về 44100 (pha liên tục giữa các lần gọi)
         // -> ghi ring. Đầy: bỏ phần dư, overflows += số mẫu bị bỏ. Trả số mẫu mono đã ghi.
int      mix_pop(mix_t *m, int16_t *out, int n);
         // Lấy n mẫu 44100 Hz. Chưa "primed" (fill < MIX_PRIME): ghi n số 0, trả 0. Đã primed: lấy min(n, fill) mẫu thật,
         // phần còn thiếu ghi 0; nếu thiếu (fill < n) -> underruns++ và về trạng thái chưa primed. Trả số mẫu thật.
int      mix_fill(const mix_t *m);            // số mẫu đang có trong ring
uint32_t mix_underruns(const mix_t *m);
uint32_t mix_overflows(const mix_t *m);
void     mix_add(int16_t *out_l, int16_t *out_r, const int16_t *music, int n, float gain);
         // out_x[i] = bão hòa(out_x[i] + music[i] * gain) về [-32768, 32767]
```
- An toàn luồng: 1 bên ghi (tác vụ BT) / 1 bên đọc (tác vụ âm thanh). Chỉ số ghi chỉ bên ghi sửa, chỉ số đọc chỉ bên đọc sửa
  (uint32 tăng dần, vị trí = chỉ số % CAP); dùng `volatile` (ESP32 ghi 32 bit là nguyên tử). `mix_reset` gọi từ tác vụ BT khi ngắt → để an toàn
  dùng cờ yêu cầu reset mà bên đọc thực hiện, hoặc khóa ngắn trong main (tùy, nhưng mix.c phải đúng khi gọi tuần tự như gate).

## 4. Trộn trong vòng lặp âm thanh (main)
Mỗi khung 256 mẫu, sau `dsp_process(guitar)`:
1. `mix_pop(&s_mix, music, 256)`.
2. `mix_add(out_l, out_r, music, 256, dsp_volume_gain(volume) * s_music_mix)` — nhạc **không** qua echo/nén/âm sắc/nhạy dây
   (nhạc nền đi qua echo nghe rè, nén làm bẹp) nhưng **theo âm lượng app** [15]. Nhạc mono cả 2 kênh (loa 4 Ω ở cổng Left).
3. Trần `GUITAR_OUT_MAX` như v0.1.
- `s_music_mix` mặc định **0,6** (hằng `GUITAR_MUSIC_MIX`); UART `MUSIC <0-100>` đổi % (không lưu NVS).
- Không có nhạc → `mix_pop` ra 0 → tiếng đàn y như v0.1.

## 5. UART thêm
- `BT` → in: trạng thái A2DP (idle/connected/playing), địa chỉ nguồn, src_rate, fill, underruns, overflows, kết nối BLE có/không, MTU.
- `MUSIC <0-100>` như trên. Lệnh cũ giữ nguyên (`STAT`, `SET`, `IN`, `TONE`, `GAIN`, `LVL` …).
- Log 1 dòng khi: A2DP kết nối/ngắt, bắt đầu/dừng phát, đổi src_rate.

## 6. Không làm
- Không sửa `tests/` (gồm cả `test_gate.py` – v0.3 dùng `tests/test_gate_v03.py`). Không thêm thư viện ngoài ESP-IDF.
- Không nạp mạch (Claude nạp sau bằng `flash.ps1`). Không đổi số DSP/giao thức của v0.1. Không AVRCP, không HFP, không Wi-Fi.

## 7. PASS
- `..\..\..\block-coding-car\firmware\.venv-host\Scripts\python.exe tests\test_gate_v02.py` exit 0 **có build thật**
  (`GATE_NO_BUILD=1` khi lặp nhanh). Báo cáo: kích thước bin, % phân vùng, RAM trống ước tính (`idf.py size` DRAM), `TODO`.

## Thử trên mạch (Claude/Tuan, sau gate)
- Điện thoại: Cài đặt Bluetooth → ghép "GUITAR UMI" → phát nhạc → nghe loa; `BT` xem underruns không tăng khi đứng yên 1 phút.
- App Umi vẫn kết nối BLE + đổi âm lượng trong khi đang phát nhạc (coex).
