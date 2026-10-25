# pump-control – điều khiển máy bơm 220 V 1 pha 2 HP (≈ 1,5 kW) từ xa bằng ESP32-WROOM-32D (công trình cho khách)

## Bối cảnh
- **Công trình cho khách** (2026-10-25): khách chưa có gì (chưa tủ điện, chưa máy chủ).
- **Tuan tự lắp điện và tự lập trình.** Claude: tra thông số (có nguồn), review sơ đồ/BOM/code khi Tuan hỏi, ghi tài liệu.
- Điều khiển: **ESP RainMaker** + Wi-Fi của khách (Tuan chọn 2026-10-25). License/điều khoản cloud (RainMaker public ghi
  "để đánh giá"): **Tuan chấp nhận rủi ro, tự giải quyết** – chỉ ghi chú, không chặn việc.

## An toàn (bắt buộc, đọc trước mọi việc)
- 220 V AC + nước. Tuan tự lắp tủ: cắt nguồn + treo biển/khóa, **thử không điện bằng bút/đồng hồ** trước khi chạm, nối đất
  PE cho tủ và motor, bấm nút TEST của RCD sau khi lắp. Học sinh không đụng tủ đang có điện.
- ESP32 **chỉ đóng cuộn hút contactor**, không đóng dòng motor. Không dùng module relay 10 A hay SSR để chạy motor.
- Bảo vệ bằng **phần cứng** (không phụ thuộc ESP32): RCD 30 mA, relay nhiệt, nút dừng khẩn NC, công tắc TAY/TẮT/TỰ ĐỘNG,
  chống chạy khô (phao/áp) nối thẳng vào mạch cuộn hút.
- Firmware mặc định TẮT khi khởi động, giới hạn thời gian chạy, nghỉ giữa 2 lần bật, tắt khi công suất bất thường.
- Số liệu dòng điện hiện là **ước tính** – chốt theo nhãn motor (`docs/survey-checklist.md`). Không bịa thông số linh kiện.

## Cấu trúc
- `README.md` – tổng quan, giai đoạn, trạng thái, quyết định.
- `docs/power-and-wiring.md` – nguồn ESP32, mức logic, chọn GPIO, sơ đồ khối tủ.
- `docs/survey-checklist.md` – khảo sát tại chỗ khách (GĐ0).
- `design/` – bước 0 "giao diện trước": vẽ trước app + bố trí tủ, duyệt bằng ảnh.
- `firmware/` – firmware 2 lớp: điều khiển + an toàn (độc lập) / kết nối (RainMaker hoặc Telegram).

## Quy ước
- Bí mật (Wi-Fi, token, khóa RainMaker) **không** ghi vào file trong git – dùng biến môi trường / file bị `.gitignore`.
- Flash/OTA lên thiết bị thật: chỉ khi Tuan đồng ý.
- Kích thước mm; ghi đơn vị V, A, W cho mọi đại lượng.
