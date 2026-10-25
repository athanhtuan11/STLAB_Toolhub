# pump-control

Điều khiển máy bơm 220 V 1 pha 2 HP (≈ 1,5 kW) từ xa bằng ESP32-WROOM-32D – công trình cho khách. Quy ước và an toàn: `CLAUDE.md`.

## Quyết định
| Ngày | Quyết định |
|---|---|
| 2026-10-25 | Khách chưa có gì → STLab làm trọn tủ điện + bộ điều khiển; **Tuan tự lắp điện và tự lập trình** |
| 2026-10-25 | Điều khiển qua **ESP RainMaker**, kết nối bằng **Wi-Fi của khách** |
| 2026-10-25 | License/điều khoản RainMaker: Tuan chấp nhận rủi ro, tự giải quyết (không chặn) |

## Giai đoạn
| GĐ | Việc | Trạng thái |
|---|---|---|
| 0 | Khảo sát (`docs/survey-checklist.md`): nhãn motor, loại bơm, sóng Wi-Fi; vẽ trước app + bố trí tủ (`design/`) | chưa |
| 1 | Bản thử 12 V: ESP32 + relay + bơm mini + PZEM, firmware 2 lớp, RainMaker public, thử đủ tình huống lỗi | chưa |
| 2 | Sơ đồ tủ + BOM theo dòng trên nhãn (`docs/power-and-wiring.md` mục 4) | chưa |
| 3 | Tuan lắp tủ → thử không tải → có tải, đo dòng khởi động; bàn giao + hướng dẫn khách | chưa |
| 4 | Thông báo cho khách (bật/tắt, lỗi) + hoàn thiện app | chưa |

## Khảo sát
- Motor: **220 V, 1 pha, 2 HP** (Tuan, 2026-10-25). Còn thiếu: dòng A trên nhãn, loại bơm, sóng Wi-Fi tại chỗ đặt tủ.
