# maker – quy ước chung cho các dự án phần cứng

Các dự án con tự nạp file này. Phần riêng nằm trong CLAUDE.md của từng dự án.

## Quy ước
- Đơn vị: mm cho cơ khí; luôn ghi V/A/W/Ω/°C. Sơ đồ chân ghi rõ GPIO và mức logic (3.3 V hay 5 V).
- Thông số linh kiện phải lấy từ datasheet (ghi nguồn); chưa có thì ghi `TODO`, không đoán.
- Mỗi dự án có `CLAUDE.md` (quy ước riêng cho Claude) + `README.md` (trạng thái, an toàn, BOM, lịch sử sửa/in).
- Thư mục chuẩn: `design/` (bước 0: dáng + mockup), `freecad/` + `print/` (CAD, theo `tools/robotics-cad/project-template/`),
  `firmware/`, `hardware/` (sơ đồ, PCB), `docs/`. Công cụ dùng chung ở `tools/`, không đặt trong `maker/`.

## An toàn (nhắc trước khi hướng dẫn)
- Pin Li-ion/LiPo/LiFePO4: có mạch bảo vệ (BMS), cầu chì, không sạc khi không có người trông.
- Điện lưới 220 V: cách ly, nối đất; khuyến nghị dùng module có chứng nhận.
- Không flash firmware hay điều khiển thiết bị thật khi chưa hỏi.

## Agent rẻ dùng chung (`~/.claude/agents/`, nguồn `custom/agents/`)
`check-runner` (chạy kiểm/test, tóm tắt), `doc-writer` (viết tài liệu qua Gemini free), `git-scribe` (commit + push) –
model `haiku`. Khi nào giao việc: mục "Phân việc theo model" trong `claude-workspace/CLAUDE.md`.

## Agent cộng đồng (VoltAgent, MIT)
`embedded-systems`, `iot-engineer`, `cpp-pro`, `python-pro` được liên kết theo từng dự án.
Các agent này có quyền Read/Write/Edit/Bash và mặc định dùng model `sonnet`.
