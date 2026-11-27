# maker – quy ước chung cho các dự án phần cứng

Các dự án con tự nạp file này. Phần riêng nằm trong CLAUDE.md của từng dự án.

## Quy ước
- Đơn vị: mm cho cơ khí; luôn ghi V/A/W/Ω/°C. Sơ đồ chân ghi rõ GPIO và mức logic (3.3 V hay 5 V).
- Thông số linh kiện phải lấy từ datasheet (ghi nguồn); chưa có thì ghi `TODO`, không đoán.
- **Co ngót in 3D (Tuan 2026-11-26): lỗ và khe lắp ghép = kích thước thật + 0,2 mm** (tối thiểu, mỗi bên với khe trượt/xoay; Ø lỗ cho trục/vít thông). Khớp xoay/ngàm xoay PETG cần lớn hơn (ngàm loa Cú Bông: 0,25 quá khít → 0,40–0,45). Ngoại lệ: số **đã in + chạy thật** trong fit-library (vd. ổ switch MX 14,00 ép, lỗ vít tự ren M2.5 Ø2,4) giữ nguyên vì đã gồm co ngót cùng máy + nhựa. Mỗi dự án ghi bảng khe trong CLAUDE.md dự án.
- **Tách part LUÔN có mối ghép âm dương / gờ phổ biến** (Tuan 2026-11-27): gờ–rãnh, bậc chồng mép, gờ rời, chốt định vị, đuôi én, lẫy, ngàm xoay – không bao giờ mặt ráp trơn. Bảng chọn dạng + số mặc định + ràng buộc in: skill `mechanical-design` mục "Tách part".
- Mỗi dự án có `CLAUDE.md` (quy ước riêng cho Claude) + `README.md` (trạng thái, an toàn, BOM, lịch sử sửa/in).
- Thư mục chuẩn: `design/` (bước 0: dáng + mockup), `solidcraft/` + `print/` (CAD, mẫu: `card-coding-robot/`, `esp32-s3-cam/solidcraft/`),
  `firmware/`, `hardware/` (sơ đồ, PCB), `docs/`. Công cụ dùng chung ở `tools/`, không đặt trong `maker/`.
- Dự án FreeCAD cũ (pushrod-arm, cyberbrick-car, cyberbrick-arm, line-bot): tooling ở `backup/20261111-legacy-freecad/`
  (2026-11-11). Làm tiếp thì dựng lại bằng SolidCraft, không khôi phục workbench.

## An toàn (nhắc trước khi hướng dẫn)
- Pin Li-ion/LiPo/LiFePO4: có mạch bảo vệ (BMS), cầu chì, không sạc khi không có người trông.
- Điện lưới 220 V: cách ly, nối đất; khuyến nghị dùng module có chứng nhận.
- Không flash firmware hay điều khiển thiết bị thật khi chưa hỏi.

## Agent rẻ dùng chung (`~/.claude/agents/`, nguồn `custom/agents/`)
`check-runner` (chạy kiểm/test, tóm tắt), `doc-writer` (viết tài liệu, nháp bằng Gemini free qua `agy`), `git-scribe` (commit + push) –
model `haiku`. Khi nào giao việc: mục "Phân việc theo model" trong `claude-workspace/CLAUDE.md`.

## Agent cộng đồng (VoltAgent, MIT)
`embedded-systems`, `iot-engineer`, `cpp-pro`, `python-pro` được liên kết theo từng dự án.
Các agent này có quyền Read/Write/Edit/Bash và mặc định dùng model `sonnet`.
