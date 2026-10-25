# pump-control – điều khiển máy bơm 2 kW từ xa bằng ESP32-WROOM-32D (công trình cho khách)

## Bối cảnh
- **Công trình cho khách** (2026-10-25): khách chưa có gì (chưa tủ điện, chưa máy chủ). Đây là việc **thương mại** →
  kiểm license thư viện/điều khoản cloud trước khi giao (khác các dự án phi thương mại khác của STLab).
- Điều khiển: **ESP RainMaker** + Wi-Fi của khách (Tuan chọn 2026-10-25). RainMaker public chỉ để đánh giá → dùng cho
  bản thử; bàn giao khách cần RainMaker **private** (liên hệ Espressif) hoặc đổi lớp kết nối (Telegram) – **Tuan quyết ở GĐ4**.

## An toàn (bắt buộc, đọc trước mọi việc)
- 220 V AC + nước. Phần điện lực (CB, RCD, contactor, relay nhiệt, motor) do **thợ điện có nghề** lắp và đóng điện.
  Claude/STLab chỉ thiết kế + làm phần điều khiển điện áp thấp. Học sinh không đụng tủ đang có điện.
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
