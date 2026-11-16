# Firmware xe lập trình kéo thả (block-coding-car) v0.1.0

ESP32-S3 N16R8 + 2 × 28BYJ-48 (ULN2003) + 2 × WS2812 + MAX98357A + nút Dừng + đo pin. Xe tự phục vụ app web (nhúng flash, gzip),
nhận chương trình JSON qua WebSocket `/ws` và thông dịch. Giao thức/số liệu: `../../protocol/PROTOCOL.md` (nguồn duy nhất).
Chân GPIO: `main/pins.h` (khớp `../../hardware/wiring.yaml`, có test).

## An toàn (từ `../../hardware/BOM.md`)
- **Buck-boost 5 V bắt buộc**: LDO trên DevKitC-1 v1.1 (SGM2212) chịu tối đa 5,5 V và chân 5V nối thẳng LDO. Không cấp pin 4 × AA thẳng vào 5V.
- **Không cắm USB khi công tắc pin đang bật.** Nạp bằng USB chỉ khi pin đã tắt; sau đó cập nhật qua Wi-Fi (OTA).
- Trẻ 6–7 tuổi: firmware nhả cuộn stepper khi đứng yên/xong/dừng/lỗi; âm thanh ≤ 30 %, đèn ≤ 25 %.
- Mật khẩu Wi-Fi và khóa OTA nằm trong NVS, không in ra log/UART, không ghi vào file.

## Build
```
powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1
```
Tạo `main/www/index.html.gz` từ `../../app/build.py --out` (chưa có/lỗi thì dùng `main/placeholder.html` và in WARN), rồi `idf.py build`
bằng ESP-IDF 5.5.4. Kết quả `build/block_coding_car.bin`. Test máy tính: `..\.venv-host\Scripts\python.exe -m pytest -q tests`.

## Nạp lần đầu bằng USB (CHỈ khi pin đã tắt)
```
idf.py -p COMx flash
```
Sau đó mở UART0 115200 hoặc dùng `wifi-setup.py` ở dưới. Lần sau cập nhật qua OTA, không cần cắm USB.

## Cài Wi-Fi, tên, khóa OTA (UART0 115200, mỗi lệnh 1 dòng)
| Lệnh | Việc |
|---|---|
| `WIFI <ssid><TAB><mật khẩu>` | lưu NVS + nối Wi-Fi lab |
| `WIFI?` / `WIFI_CLEAR` | xem trạng thái / xóa |
| `NAME <ten> <#RRGGBB>` | tên (a-z, 0-9, `-`, ≤ 24) + màu thân, xe tự khởi động lại; mặc định `robot-do` `#E0453A` |
| `OTAKEY <khóa>` / `OTAKEY?` | nạp khóa OTA (16–64 ký tự in được) |

Dùng `python wifi-setup.py --port COM7` (hỏi SSID, mật khẩu bằng `getpass`), `--name robot-xanh --color "#2A7DE1"`, `--ota-key`, `--clear`.
Chưa cấu hình hoặc 20 s không nối được → xe phát Wi-Fi mở `robot-<tên>` (mắt vàng), vào `http://192.168.4.1`. Nối được → `http://<tên>.local`.
Màu mắt trạng thái: xanh lá = sẵn sàng, xanh dương nhấp nháy = đang nối, vàng = điểm phát, đỏ nhấp nháy = pin yếu (< 4400 mV).

## OTA
Đặt khóa 1 lần cho cả máy tính (`setx STLAB_CAR_OTA_KEY <khóa>`, mở terminal mới) rồi nạp vào xe bằng `wifi-setup.py --ota-key`.
Phát hành: `python ota.py --host robot-do.local` (khi xe không chạy chương trình). Xe tự quay về bản cũ nếu bản mới không chạy ổn.

## Hiệu chỉnh `cal`
Mặc định `steps_cell = 4054` (bước/ô 150 mm) và `steps_90 = 1231` (bước mỗi bánh để quay 90°, vết bánh 58 mm theo CAD) – tính toán, chưa đo thật.
Giáo viên chỉnh từ app (thông điệp ws `cal`, khoảng 1000–8000 và 500–4000), lưu NVS namespace `car`. Cách đo: chạy `fwd 4` trên thảm ô,
đo quãng đường thật, nhân tỉ lệ; `left` x4 phải về đúng hướng cũ.

## TODO – đo trên xe thật
| Việc | Ghi chú |
|---|---|
| Chiều quay motor `DIR_LEFT`/`DIR_RIGHT` (`pins.h`) | mặc định trái −1, phải +1; xe lùi thay vì tiến thì đổi dấu cả hai |
| `steps_cell`, `steps_90` | hiệu chỉnh trên thảm thật (trượt bánh, tải) |
| Tốc độ 200 → 500 bước/s, dốc 300 bước | bỏ bước (mất lực) thì giảm; giới hạn kéo vào > 600 Hz theo datasheet |
| Ngưỡng pin 4400 mV (từ chối chạy) / 4200 mV (dừng sau 2 s) | NiMH 4 × AA, đo khi động cơ chạy tải |
| Dải ADC chia áp 100k/100k | tối đa ~2,9 V khi pin ~5,8 V (xem `wiring.yaml`); đối chiếu bằng đồng hồ |
| Âm lượng MAX98357A, độ sáng mắt | 30 % / 25 % theo PROTOCOL – nghe/nhìn thử với bé |
| Nút Dừng GPIO13, chống dội 30 ms | nhấn khi xe đang chạy và khi không có Wi-Fi |
| Thông điệp `stopped why:"wifi"` | PROTOCOL có nhưng chưa dùng: xe chạy hết chương trình dù mất kết nối (theo mục 4) |
