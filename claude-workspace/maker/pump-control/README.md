# pump-control

Điều khiển máy bơm 220 V 1 pha 2 HP (≈ 1,5 kW) từ xa bằng ESP32-WROOM-32D – công trình cho khách. Quy ước và an toàn: `CLAUDE.md`.

## Quyết định
| Ngày | Quyết định |
|---|---|
| 2026-10-25 | Khách chưa có gì → STLab làm trọn tủ điện + bộ điều khiển; **Tuan tự lắp điện và tự lập trình** |
| 2026-10-25 | Điều khiển qua **ESP RainMaker**, kết nối bằng **Wi-Fi của khách** |
| 2026-10-25 | License/điều khoản RainMaker: Tuan chấp nhận rủi ro, tự giải quyết (không chặn) |
| 2026-10-25 | **Chỉ điều khiển bật/tắt qua Wi-Fi**, bỏ bảo vệ motor; MCB/RCD dùng của nhà khách |

## Giai đoạn
| GĐ | Việc | Trạng thái |
|---|---|---|
| 0 | Khảo sát: motor 220 V 2 HP, Wi-Fi có, CB/RCD nhà bỏ qua; còn vẽ trước app + bố trí tủ (`design/`) | khảo sát xong |
| 1 | Firmware RainMaker bật/tắt (Tuan tự lập trình), thử với đèn/bơm 12 V trước | chưa |
| 2 | BOM tối giản (`docs/bom.md`) | xong |
| 3 | Tuan lắp tủ → thử không tải → có tải, đo dòng khởi động; bàn giao + hướng dẫn khách | chưa |
| 4 | Bàn giao app cho khách | chưa |

## Khảo sát
- Motor: **220 V, 1 pha, 2 HP**. Wi-Fi tại chỗ đặt tủ: **có**. CB/RCD nhà khách: Tuan bỏ qua kiểm.
