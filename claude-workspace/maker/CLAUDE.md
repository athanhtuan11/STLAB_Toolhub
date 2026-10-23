# maker – quy ước chung cho các dự án phần cứng

Các dự án con tự nạp file này. Phần riêng nằm trong CLAUDE.md của từng dự án.

## Quy ước
- Đơn vị: mm cho cơ khí; luôn ghi V/A/W/Ω/°C. Sơ đồ chân ghi rõ GPIO và mức logic (3.3 V hay 5 V).
- Thông số linh kiện phải lấy từ datasheet (ghi nguồn); chưa có thì ghi `TODO`, không đoán.
- Mỗi dự án có `README.md` (mục tiêu, BOM, sơ đồ, cách build) và `docs/` cho ghi chú.
- Thư mục gợi ý: `firmware/`, `hardware/` (sơ đồ, PCB), `cad/` (FreeCAD/STL), `docs/`.

## An toàn (nhắc trước khi hướng dẫn)
- Pin Li-ion/LiPo/LiFePO4: có mạch bảo vệ (BMS), cầu chì, không sạc khi không có người trông.
- Điện lưới 220 V: cách ly, nối đất; khuyến nghị dùng module có chứng nhận.
- Không flash firmware hay điều khiển thiết bị thật khi chưa hỏi.

## Agent cộng đồng (VoltAgent, MIT)
`embedded-systems`, `iot-engineer`, `cpp-pro`, `python-pro` được liên kết theo từng dự án.
Các agent này có quyền Read/Write/Edit/Bash và mặc định dùng model `sonnet`.
