# Nguồn và nối dây – ESP32-WROOM-32D điều khiển máy bơm

Viết 2026-10-25. Số liệu ESP32 lấy từ datasheet và hướng dẫn chính hãng Espressif (link cuối file).
Thông số motor/relay/PZEM chưa chốt → `TODO`.

## 1. "ESP32-D chạy 5 V?" – Bo thì cấp 5 V được, chip thì chạy 3,3 V

| | Điện áp | Nguồn |
|---|---|---|
| Module ESP32-WROOM-32D | **3,0–3,6 V** (điển hình 3,3 V); tuyệt đối tối đa 3,6 V | Datasheet bảng 13–14 |
| Dòng nguồn cấp cho module | **≥ 0,5 A** | Datasheet bảng 14 |
| Bo phát triển (DevKitC) | Cấp 1 trong 3 cách: cổng USB, **chân 5V**, hoặc chân 3V3. Bo có ổn áp xuống 3,3 V | Hướng dẫn DevKitC |
| Chân GPIO | Mức logic **3,3 V**, mức vào cao tối đa = VDD + 0,3 V ≈ **3,6 V** → **không chịu 5 V** | Datasheet bảng 15 |

Kết luận:
- Cấp **5 V vào chân 5V** của bo (từ nguồn cách ly 220 V → 5 V trong tủ) là đúng. Bo tự hạ xuống 3,3 V cho chip.
- Nguồn 5 V nên ≥ 1 A, vì còn cấp cho module relay và PZEM (`TODO` cộng dòng thực tế khi chốt linh kiện).
- **Chỉ dùng 1 nguồn tại 1 lúc.** Espressif ghi rõ 3 cách cấp nguồn loại trừ nhau, cấp cùng lúc có thể hỏng bo hoặc
  nguồn. → Khi cắm USB để nạp code: **ngắt nguồn 5 V của tủ** (hoặc rút chân 5V).
- **Không đưa tín hiệu 5 V vào GPIO.** Thiết bị nào xuất 5 V (vd. TX của PZEM nếu cấp 5 V) phải qua chia áp hoặc
  mạch chuyển mức.

## 2. Bẫy hay gặp: module relay 5 V kích mức thấp + GPIO 3,3 V
Nhiều module relay opto "5 V, kích mức thấp" nối VCC = 5 V. Khi GPIO ra mức cao (3,3 V), LED opto còn chênh khoảng
5 − 3,3 = 1,7 V → có thể **vẫn sáng mờ, relay không nhả** (`TODO` thử với module thật). Chọn một trong các cách:
- Module relay ghi rõ **kích được bằng 3,3 V, kích mức cao** (mất điện / ESP32 reset → relay nhả → contactor nhả: an toàn).
- Hoặc tự đệm bằng transistor NPN/MOSFET từ GPIO.
Relay này chỉ đóng **cuộn hút contactor** (dòng nhỏ), không đóng dòng motor.

## 3. Chọn GPIO
- Ra relay: **GPIO26 hoặc GPIO27** (hoặc 25/32/33).
- Tránh: GPIO0, 2, 12, 15 (chân strapping – ảnh hưởng chế độ khởi động; datasheet mục 3.1), GPIO1/3 (UART nạp code),
  GPIO34–39 (chỉ vào). `TODO`: kiểm chân nào phát xung lúc khởi động trên bo thật (đo bằng LED/oscilloscope) trước khi
  nối contactor.
- PZEM-004T (UART): dùng UART2, vd. GPIO16 (RX), GPIO17 (TX). Mức điện áp TX của PZEM: `TODO` theo datasheet PZEM.

## 4. Sơ đồ khối tủ (chốt dòng theo nhãn motor)
```
Nguồn 220 V ─ CB (≥ 1,25 × dòng định mức) ─ RCD 30 mA ─ Contactor (AC-3 ≥ dòng định mức) ─ Relay nhiệt (= dòng nhãn) ─ Motor
                                                       ▲ cuộn hút
  E-stop (NC) ─ NC relay nhiệt ─ chống chạy khô (NC) ─┤
  Công tắc TAY / TẮT / TỰ ĐỘNG ─ (TỰ ĐỘNG) ─ tiếp điểm relay ◄─ GPIO26 ESP32
  Nguồn cách ly 220 V → 5 V ─► chân 5V ESP32, VCC relay, PZEM
  PZEM-004T + CT kẹp dây pha ─UART─► ESP32 (V, A, W, kWh → biết bơm chạy thật, chạy khô, kẹt)
```
### Motor của khách: **220 V, 1 pha, 2 HP** (Tuan báo 2026-10-25) = 2 × 745,7 W ≈ **1,5 kW công suất trục**
(không phải 2 kW như mô tả ban đầu).

| Đại lượng | Giá trị | Cách có |
|---|---|---|
| Dòng chạy định mức | **≈ 11–12,5 A** | (a) 1 491 W ÷ hiệu suất ~0,75 ÷ (220 V × cos φ ~0,8) ≈ 11,3 A; (b) bảng NEC 430.248 (Mỹ): 2 HP 1 pha 230 V = 12 A → quy về 220 V ≈ 12,5 A. **Chốt theo nhãn** (`TODO` dòng A trên nhãn) |
| Dòng khởi động | ≈ 5–7 × → **~60–90 A**, < 1 s | ước tính chung cho motor 1 pha có tụ – `TODO` đo bằng PZEM/ampe kìm lần chạy đầu |

### Chọn thiết bị (quy tắc → giá trị đề xuất; chốt lại theo dòng nhãn)
Tuan 2026-10-25: tủ điện nhà khách đã có MCB/RCD → **tủ bơm chỉ lo phần điều khiển** (contactor, relay nhiệt, E-stop,
công tắc TAY/TẮT/TỰ ĐỘNG, chống chạy khô, ESP32). MCB/RCD chỉ thêm khi tủ nhà không đạt (2 dòng đầu bảng).
| Thiết bị | Quy tắc | Đề xuất |
|---|---|---|
| MCB (2 cực) | **Dùng MCB nhánh của tủ điện nhà nếu có** (16–25 A cho riêng nhánh bơm). Chỉ có CB tổng 40–63 A → thêm MCB nhánh (dây 2,5 mm² không được CB tổng bảo vệ) | nếu thiếu: **20 A curve D** |
| RCD/RCCB chống giật | **Dùng RCD tổng của nhà nếu là 30 mA và nút TEST nhảy** (đánh đổi: bơm rò → cả nhà mất điện). 100 mA hoặc không có → thêm | nếu thiếu: **2P 25 A 30 mA** |
| Contactor | AC-3 ≥ dòng định mức (cho cả L và N qua 2 cực) | **AC-3 18 A**, cuộn hút **220 VAC** |
| Relay nhiệt | Dải chỉnh chứa dòng nhãn | dải **≈ 9–13 A** hoặc 12–18 A, chỉnh = dòng nhãn |
| Dây động lực | theo dòng 20 A + chiều dài (sụt áp lúc khởi động) | **2,5 mm² Cu** nếu ngắn; dài > ~20 m: `TODO` tính sụt áp, có thể 4 mm² |
| Đo công suất | phải đo tới ≥ 90 A khởi động | **PZEM-004T bản 100 A có CT kẹp** (bản 10 A shunt KHÔNG đủ) |
| Nguồn ESP32 | cách ly 220 V → 5 V | ≥ 1 A |

Kiểm lại: tụ khởi động/tụ chạy của motor còn tốt không (motor 1 pha hỏng tụ → không quay, dòng cao, relay nhiệt cắt).
Tủ: nhựa IP65 mua sẵn, ray DIN (không in PETG làm vỏ tủ điện – PETG không chống cháy).

## Nguồn
- [ESP32-WROOM-32D/32U Datasheet (Espressif)](https://documentation.espressif.com/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf) – bảng 13, 14, 15; mục 3.1.
- [ESP32-DevKitC User Guide (Espressif)](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) – mục Power Supply Options.
- [Public vs Private RainMaker (Espressif)](https://docs.rainmaker.espressif.com/docs/deploy/deployment-overview/public-vs-private-rainmaker)
