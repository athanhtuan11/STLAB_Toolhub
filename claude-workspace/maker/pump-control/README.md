# pump-control

Điều khiển máy bơm 2 kW từ xa bằng ESP32-WROOM-32D – công trình cho khách. Quy ước và an toàn: `CLAUDE.md`.

## Quyết định
| Ngày | Quyết định |
|---|---|
| 2026-10-25 | Khách chưa có gì → STLab làm trọn tủ điện + bộ điều khiển (phần điện lực do thợ điện có nghề lắp) |
| 2026-10-25 | Điều khiển qua **ESP RainMaker**, kết nối bằng **Wi-Fi của khách** |
| chờ GĐ4 | RainMaker public chỉ để đánh giá → bàn giao: RainMaker private (hỏi Espressif) hay Telegram |

## Giai đoạn
| GĐ | Việc | Trạng thái |
|---|---|---|
| 0 | Khảo sát (`docs/survey-checklist.md`): nhãn motor, loại bơm, sóng Wi-Fi; vẽ trước app + bố trí tủ (`design/`) | chưa |
| 1 | Bản thử 12 V: ESP32 + relay + bơm mini + PZEM, firmware 2 lớp, RainMaker public, thử đủ tình huống lỗi | chưa |
| 2 | Sơ đồ tủ + BOM theo dòng trên nhãn (`docs/power-and-wiring.md` mục 4) | chưa |
| 3 | Thợ điện lắp tủ → thử không tải → có tải, đo dòng khởi động; bàn giao + hướng dẫn khách | chưa |
| 4 | Lớp kết nối chính thức + thông báo | chưa |

## Khảo sát
TODO (sau GĐ0).
