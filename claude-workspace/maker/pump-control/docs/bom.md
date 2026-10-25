# BOM tủ điều khiển máy bơm – bản tối giản (chốt 2026-10-25)

**Phạm vi (Tuan quyết 2026-10-25): chỉ điều khiển bật/tắt máy bơm từ xa qua Wi-Fi.** Bỏ phần bảo vệ motor (relay nhiệt,
dừng khẩn, chống chạy khô, đo dòng). MCB/RCD dùng của tủ điện nhà khách.
Motor 220 V 1 pha 2 HP (≈ 1,5 kW), dòng chạy ≈ 12,5 A, khởi động ~60–90 A (ước tính – `power-and-wiring.md` mục 4).

## Bắt buộc
| # | Món | Thông số cần | SL | Vì sao |
|---|---|---|---|---|
| 1 | Contactor | **AC-3 ≥ 18 A**, cuộn hút **220 VAC** | 1 | Đóng cắt motor. Relay module (~10 A) không chịu dòng khởi động → dính/cháy tiếp điểm |
| 2 | Bo ESP32 | **ESP32-DevKitC WROOM-32D**, cấp 5 V vào chân 5V | 1 | Wi-Fi + RainMaker |
| 3 | Nguồn AC-DC cách ly | 220 VAC → **5 V ≥ 1 A**, module đóng kín | 1 | Nuôi ESP32 + module relay |
| 4 | Module relay | Opto 1–2 kênh 5 V, jumper H/L → **đặt H**. Thử bật/tắt khi nhận hàng | 1 | Đóng cuộn hút contactor |
| 5 | Dây | Cu **2,5 mm²** động lực (L, N, PE); 1 mm² điều khiển | – | |
| 6 | Tủ nhựa | IP65 (nếu ngoài trời), ray DIN, cầu đấu, ốc siết cáp | 1 | |

## Nên có (rẻ, tùy Tuan)
| Món | Lợi |
|---|---|
| Cầu chì 2 A + đế cho mạch cuộn hút / nguồn 5 V | Chập dây điều khiển không cháy tủ |
| Công tắc 2 vị trí TAY / TỰ ĐỘNG (song song tiếp điểm relay) | Mất Wi-Fi / hỏng ESP32 vẫn bật bơm được bằng tay |

## Nối mạch cuộn hút
L → (cầu chì 2 A) → tiếp điểm NO relay kênh 1 → cuộn hút A1; A2 → N. Contactor đóng L và N tới motor; PE nối thẳng motor + tủ.
GPIO26 → IN1 của module relay; 5V/GND chung với ESP32.

## Firmware (miễn phí, Tuan tự lập trình – gợi ý)
- Khởi động/mất điện xong → mặc định **TẮT**.
- Giới hạn thời gian chạy mỗi lần (tự tắt), tránh quên tắt từ xa.
- Hiện trạng thái bật/tắt trên app RainMaker.
