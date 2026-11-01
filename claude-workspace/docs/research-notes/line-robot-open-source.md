# Robot dò line / tránh vật cản mã nguồn mở – học gì cho line-bot (2026-11-01)

> **Mục đích:** tổng hợp thư viện, firmware mã nguồn mở và tài liệu đội thi công khai để áp dụng vào firmware và thiết kế cơ khí `maker/line-bot`.
> **Ghi chú nguồn:**
> - **[Claude đã đọc]** – Claude đọc trực tiếp trang web / repo / API GitHub.
> - **[Codex tra, chưa đối chiếu]** – Codex tra web/datasheet, chưa đối chiếu với nguồn gốc. Trước khi dùng làm ràng buộc thiết kế phải đọc lại nguồn.

## 1. Tóm tắt

- Không ghim repo nào vào `community/` lúc này; đa số cũ hoặc ít sao. Xem lại khi bắt đầu viết firmware (chờ Tuan).
- Khi viết firmware: dùng `qtr-sensors-arduino` để học thuật toán đọc + hiệu chuẩn; `Arduino-PID-Library` làm vòng PID; `zumo-32u4-arduino-library` và `pololu-3pi-plus-32u4-arduino-library` làm ví dụ PID dò line.
- Kiến trúc firmware: state machine kiểu đội RCJ (dò line → giao lộ xanh → vật cản → dốc), PID dò line theo Pololu, hiệu chuẩn mảng lúc khởi động.
- Mảng dò line đặt cách sàn **3 mm**, gá có rãnh chỉnh cao ±3 mm.
- Nhiều số đo cơ khí chưa có nguồn (xem mục 4 và mục 8).

## 2. Thư viện / firmware [Claude đã đọc]

Số liệu: Claude kiểm GitHub API ngày 2026-11-01 (sao · lần push cuối · license).

### 2.1 pololu/qtr-sensors-arduino

- Chức năng: đọc + hiệu chuẩn mảng QTR, tính vị trí line.
- 149 sao · push cuối 2020-03-14 · license không nhận dạng (cần xem trực tiếp repo).
- Lâu không cập nhật → chỉ tham khảo thuật toán.

### 2.2 pololu/pololu-3pi-plus-32u4-arduino-library

- Chức năng: ví dụ `LineFollowerPID` cho robot 3pi+.
- 18 sao · push cuối 2022-09-07 · MIT.
- Code viết cho 3pi+ (32u4). Dùng cho Mega/N20 phải chuyển đổi chân và driver.

### 2.3 pololu/zumo-32u4-arduino-library

- Chức năng: thuật toán + hiệu chuẩn mảng dò line (code cho phần cứng Zumo).
- 69 sao · push cuối 2024-05-28 · MIT.
- Mới nhất trong 3 repo Pololu đã kiểm → ưu tiên đọc khi nghiên cứu.

### 2.4 br3ttb/Arduino-PID-Library

- Chức năng: PID tổng quát cho Arduino. [Codex tra, chưa đối chiếu] README ghi v1.2.1, MIT.
- 2208 sao · push cuối 2024-05-31.
- Nhiều sao nhất trong danh sách → lựa chọn khởi điểm cho vòng PID.

### 2.5 sparkfun/SparkFun_TB6612FNG_Arduino_Library

- Chức năng: điều khiển cầu H TB6612FNG.
- [Codex tra, chưa đối chiếu] README: 1,2 A liên tục, 3,2 A đỉnh; chân STBY phải kéo lên.
- 86 sao · push cuối 2019-11-13 · cũ → chỉ tham khảo, không cài trực tiếp.

### 2.6 Hướng dẫn PID dò line của Pololu (3pi đời cũ)

- Nguồn: https://www.pololu.com/docs/0J21 [chưa đối chiếu nội dung – TODO].
- Mô tả cách tính vị trí line từ mảng cảm biến và xây vòng PID.

## 3. Tài liệu đội RoboCupJunior Rescue Line công khai

### 3.1 Kho tổng hợp TDP / poster / BOM / code đội 2026

- URL: https://robocup-junior.github.io/rcj-rescue-docs-site/2026/line/
- Repo robocup-junior/rcj-rescue-docs-site · push cuối 2026-09-16. [Claude đã đọc]
- Nội dung: TDP, poster, BOM, code – tùy đội có chia sẻ hay không.

### 3.2 Một số repo đội cụ thể [Codex tra, chưa đối chiếu]

Sao và file CAD chưa kiểm.

| Repo | Phần cứng chính | Điểm đáng học |
|---|---|---|
| IITA-Proyectos/rcj-2026-rescue-line-iita-salta-robocup · MIT | Raspberry Pi 4B + Teensy 4.1, camera, ToF / siêu âm, cảm biến màu | Kết hợp nhiều loại cảm biến; cách viết TDP |
| JamesBond6873/Airborne_Rescue_Line_2025 · MIT | Raspberry Pi 5 + Pico, camera, AI | Cách viết TDP / poster |
| Lebob-Robotics/Lebob-Robocup2025 · MIT | LEGO SPIKE, PD với 2 cảm biến, state machine | Cách chia hành vi bằng state machine; gần với quy mô 2 cảm biến của line-bot (cần đọc code để xác nhận) |

### 3.3 Nhận xét

- Đội mạnh RCJ dùng camera và máy tính nhúng (Pi 4 / Pi 5); khác xa line-bot (Mega + mảng hồng ngoại).
- line-bot là bản nhập môn lớp 6 → học từ họ hai thứ: (1) chia hành vi bằng state machine (dò line → giao lộ xanh → vật cản → dốc); (2) cách viết TDP và poster.

## 4. Số đo thiết kế [Claude đã đọc]

Nguồn: trang Pololu 0J12, đọc ngày 2026-11-01.

| Thông số | Giá trị | Ghi chú |
|---|---|---|
| Khoảng cách giữa các mắt mảng QTR-8 | 9,525 mm (0,375 in) | 8 mắt cách đều |
| Khoảng đo tối ưu (QTR-8) | 3 mm (0,125 in) | Từ mảng xuống sàn |
| Khoảng đo tối đa khuyến nghị (QTR-8A) | 6 mm | |
| Khoảng đo đỉnh TCRT5000 | 2,5 mm | [Codex tra, chưa đối chiếu] đọc datasheet Vishay |
| Khoảng cách mảng cảm biến trước trục bánh | TODO | Chưa có nguồn – gá chỉnh được + thử trên sa bàn |
| Đường kính bánh / tốc độ tối ưu | TODO | Chưa có nguồn |
| Vị trí trọng tâm | TODO | Chưa có nguồn |

Quyết định thiết kế đã áp dụng (2026-11-01): mảng dò line đặt cách sàn **3 mm**, gá có rãnh chỉnh cao ±3 mm.

## 5. Áp dụng vào line-bot

- Tham số hóa: mọi kích thước linh kiện lưu ở `maker/line-bot/freecad/params.json`. Đổi linh kiện → sửa số, dựng lại model.
- Firmware (kế hoạch):
  - State machine kiểu đội RCJ: dò line, nhận giao lộ xanh, tránh vật cản, leo dốc.
  - PID dò line theo hướng dẫn Pololu (0J21).
  - Hiệu chuẩn mảng cảm biến lúc khởi động (tham khảo qtr-sensors-arduino và zumo-32u4-arduino-library).

## 6. Kết luận

- Không có thư viện nào cài thẳng được cho line-bot; tất cả đóng vai trò tham khảo thuật toán.
- Vòng PID khởi điểm: Arduino-PID-Library. Ví dụ dò line + hiệu chuẩn: zumo-32u4-arduino-library.
- Kiến trúc firmware: học state machine từ tài liệu đội RCJ (đọc code Lebob-Robocup2025 trước).
- Số đo cơ khí còn thiếu (khoảng cách mảng trước trục bánh, đường kính bánh, trọng tâm) phải thử trên sa bàn.

## 7. Đánh đổi

- Dùng thư viện Pololu (viết cho 3pi+ và Zumo) làm tham khảo: có thuật toán đã chạy trên robot thật, nhưng phải chuyển chân và driver sang Mega + N20 + TB6612FNG.
- Dùng Arduino-PID-Library tổng quát: tích hợp nhanh, nhưng chưa tinh chỉnh riêng cho động cơ N20. Có thể bổ sung sau.
- Gá mảng cách sàn 3 mm theo khuyến nghị QTR-8: nếu sa bàn có bậc ≤ 3 mm (RCJ cho phép) có thể chạm mảng → rãnh chỉnh ±3 mm là lớp đệm.

## 8. TODO

- Kiểm license repo qtr-sensors-arduino trực tiếp trên GitHub (hiện không nhận dạng được).
- Đọc nội dung trang Pololu 0J21 để đối chiếu hướng dẫn PID.
- Đối chiếu TCRT5000 (2,5 mm) với datasheet Vishay gốc [Codex tra, chưa đối chiếu].
- Đối chiếu SparkFun TB6612FNG (1,2 A / 3,2 A, chân STBY) với datasheet Toshiba và thực đo.
- Xác định khoảng cách mảng cảm biến trước trục bánh, đường kính bánh, tốc độ tối ưu, trọng tâm – thử trên sa bàn.
- Đọc TDP / code Lebob-Robocup2025 để xác nhận state machine.
- Lịch tuyển đội Việt Nam cho RCJ Rescue Line 2026–2027: xem `line-robot-competitions.md`.
- Chờ Tuan: có ghim repo nào vào `community/` khi viết firmware không.
