# BOM tủ điều khiển máy bơm – bản tối giản (chốt 2026-10-25)

**Phạm vi (Tuan quyết 2026-10-25): chỉ điều khiển bật/tắt máy bơm từ xa qua Wi-Fi.** Bỏ phần bảo vệ motor (relay nhiệt,
dừng khẩn, chống chạy khô, đo dòng). MCB/RCD dùng của tủ điện nhà khách.
Motor 220 V 1 pha 2 HP (≈ 1,5 kW), dòng chạy ≈ 12,5 A, khởi động ~60–90 A (ước tính – `power-and-wiring.md` mục 4).

## Bắt buộc
| # | Món | Thông số cần | SL | Vì sao |
|---|---|---|---|---|
| 1 | Contactor | **AC-3 ≥ 18 A**, cuộn hút **220 VAC** | 1 | Đóng cắt motor. Relay module (~10 A) không chịu dòng khởi động → dính/cháy tiếp điểm |
|   | ↳ đã có (2026-10-29) | **LS Metasol MC-22b**: AC-3 22 A, AC-1 40 A, UL 3 HP @230 V 1 pha, phụ 1NO+1NC. Cuộn hút: `TODO` đọc nhãn (phải 220 VAC). Toolhub → Linh kiện → `contactor-ls-mc-22b`; ảnh `img/contactor-ls-mc-22b-*.jpg` | | Đạt yêu cầu dòng |
| 2 | Bo ESP32 | **ESP32-DevKitC WROOM-32D**, cấp 5 V vào chân 5V | 1 | Wi-Fi + RainMaker |
| 3 | Nguồn AC-DC cách ly | 220 VAC → **5 V ≥ 1 A**, module đóng kín | 1 | Nuôi ESP32 + module relay |
| 4 | Module relay | Opto 1–2 kênh 5 V, jumper H/L → **đặt H**. Thử bật/tắt khi nhận hàng | 1 | Đóng cuộn hút contactor |
| 5 | Dây | Cu **2,5 mm²** động lực (L, N, PE); 1 mm² điều khiển | – | |
| 6 | Tủ nhựa | IP65 (nếu ngoài trời), ray DIN, cầu đấu, ốc siết cáp | 1 | |
| 7 | Công tắc xoay | **3 vị trí giữ nguyên TAY – TẮT – TỰ ĐỘNG**, lỗ **Ø22 mm**, **2NO (Tuan chốt 2026-10-25)**, ≥ 220 VAC. Tìm: "công tắc xoay 3 vị trí phi 22 2NO" (vd. Schneider XB7ND33 – `TODO` kiểm mô tả khi mua; Hanyoung/Idec/Chint tương đương) | 1 | Mất Wi-Fi / hỏng ESP32 vẫn bật bơm tay; TẮT tại tủ |

Bỏ (Tuan 2026-10-25): cầu chì mạch điều khiển, bảo vệ motor.

## Nối mạch cuộn hút
```
L ─► chân chung công tắc ─┬─ TAY ───────────────────────────► A1 cuộn hút contactor
                          ├─ TẮT: hở
                          └─ TỰ ĐỘNG ─► NO relay kênh 1 (ESP32) ─► A1
A2 ─► N.   Contactor đóng L và N tới motor; PE nối thẳng motor + tủ.
GPIO26 → IN1 module relay (jumper H); 5V/GND chung với ESP32.
```
Công tắc **1NO + 1NC** (thay vì 2NO): NC đóng cả ở vị trí giữa → vị trí TẮT vẫn để ESP32 bật bơm = chỉ còn 2 chế độ
TAY / TỰ ĐỘNG (tắt tại tủ bằng CB nhà). Muốn TẮT thật: dùng 2NO hoặc thay khối NC bằng khối NO. Mua loại nào cũng **đo
thông mạch 3 vị trí** trước khi đấu.
Ở TAY: app không tắt được và không biết bơm chạy (ESP32 không đọc công tắc – thêm 1 GPIO đọc vị trí nếu cần sau).

## Firmware (Tuan tự lập trình – đã đồng ý 2026-10-25)
- Khởi động/mất điện xong → mặc định **TẮT**.
- Giới hạn thời gian chạy mỗi lần (tự tắt), tránh quên tắt từ xa.
- Hiện trạng thái bật/tắt trên app RainMaker.
