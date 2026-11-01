# Giáo án: Nhập môn Arduino Mega 2560

## Thông tin
- Thời lượng: 2 buổi × 90 phút.
- Đối tượng: học sinh THCS lớp 6–9 (TODO Tuan xác nhận lớp).
- Sĩ số / nhóm: TODO.

## Mục tiêu
- Nêu được chức năng các nhóm chân của Arduino Mega 2560: chân số, chân PWM, chân analog, UART, I2C.
- Cài được Arduino IDE và driver cho bo, nạp được chương trình vào bo.
- Điều khiển được LED bằng nút nhấn và PWM.
- Đọc được giá trị analog và cảm biến khoảng cách HC-SR04 qua Serial Monitor/Plotter.
- Làm được mini-project báo vật cản bằng LED hoặc còi, làm cầu nối sang `line-bot`.

## Chuẩn bị
- Arduino Mega 2560 hoặc bản clone CH340 (kèm driver WCH CH34x).
- Cáp USB-B.
- LED, điện trở, nút nhấn.
- Cảm biến HC-SR04.
- Breadboard và dây nối.

## An toàn
- VIN cấp 7–12 V.
- Mỗi chân I/O tối đa 20 mA. Không nối motor hoặc relay thẳng vào chân I/O; dùng driver/transistor và nguồn riêng, nối chung GND.
- Không để chạm chập 5 V với GND.
- Clone CH340: ổn áp và linh kiện nguồn tùy hãng; kiểm bo thực tế trước khi cấp nguồn ngoài.

## Buổi 1 (90 phút)
1. **Giới thiệu bo:** 54 chân digital, 15 chân PWM, 16 chân analog A0–A15, 4 UART, I2C ở D20/D21. Chỉ giới thiệu các nhóm chân chính, không đọc hết bảng pinout.
2. **Cài đặt:** cài Arduino IDE và driver CH34x (với bản clone), chọn đúng cổng COM và board.
3. **Thực hành:**
   - Ví dụ `01.Basics/Blink`: LED nhấp nháy.
   - Ví dụ `02.Digital/Button`: đọc nút nhấn, bật/tắt LED.
   - Ví dụ `01.Basics/Fade`: làm mờ LED bằng PWM.
4. **Chia sẻ:** mỗi nhóm trình bày đoạn code mình đã sửa.

**Sản phẩm buổi 1:** LED nhấp nháy, LED bật/tắt theo nút, LED mờ dần.

## Buổi 2 (90 phút)
1. **Đọc analog:** ví dụ `03.Analog/AnalogInOutSerial`. Mở Serial Monitor và Serial Plotter để quan sát giá trị.
2. **Cảm biến khoảng cách HC-SR04:** nối chân Trig và Echo vào chân số. Chân Echo của HC-SR04 ở mức 5 V; Mega làm việc ở 5 V nên nối thẳng được. Đọc khoảng cách và in ra Serial Monitor.
3. **Mini-project "báo vật cản":** khi cảm biến thấy vật gần, LED hoặc còi báo. Đây là cầu nối sang `maker/line-bot` (xe tránh vật cản).
4. **Trình bày:** nhóm chạy thử và nêu một lỗi đã gặp.

**Sản phẩm buổi 2:** mạch HC-SR04 + LED/còi chạy đúng, nhóm giải thích được cách đọc khoảng cách.

## Câu hỏi kiểm tra cuối buổi
- Chân nào trên Mega dùng để xuất PWM, và PWM dùng để làm gì?
- Vì sao không nối motor thẳng vào chân I/O?
- Serial Monitor khác Serial Plotter ở điểm nào?
- Muốn đọc khoảng cách từ HC-SR04 thì cần những chân nào?

## Tài liệu
- Pinout PDF chính hãng: `community/arduino-docs-content/content/hardware/mega/boards/mega-2560/downloads/A000067-full-pinout.pdf` (nguồn community, ghim `b12ffb3a317c`).
- Ghi chú nghiên cứu: `docs/research-notes/arduino-mega-2560.md`.
