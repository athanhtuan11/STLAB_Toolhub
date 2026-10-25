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
Ước tính dòng (chưa có nhãn, `TODO`): 2 kW là công suất vào, 1 pha, hệ số công suất 0,8 → ≈ 11 A; 2 kW là công suất trục
(hiệu suất ~75 %) → ≈ 15 A; lúc khởi động gấp 5–7 lần trong < 1 s. CB/RCD/contactor/dây chốt lại theo dòng trên nhãn motor.
Tủ: nhựa IP65 mua sẵn, ray DIN (không in PETG làm vỏ tủ điện – PETG không chống cháy).

## Nguồn
- [ESP32-WROOM-32D/32U Datasheet (Espressif)](https://documentation.espressif.com/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf) – bảng 13, 14, 15; mục 3.1.
- [ESP32-DevKitC User Guide (Espressif)](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) – mục Power Supply Options.
- [Public vs Private RainMaker (Espressif)](https://docs.rainmaker.espressif.com/docs/deploy/deployment-overview/public-vs-private-rainmaker)
