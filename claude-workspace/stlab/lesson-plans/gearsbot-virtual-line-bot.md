# Giáo án: Lắp robot ảo trước khi lắp thật – xe dò line (GearsBot)

## Thông tin
- Thời lượng: 3 buổi × 90 phút.
- Đối tượng: lớp 6–9 (cùng nhóm với `maker/line-bot`, lớp 6). Học sinh khá dùng Python từ buổi 2.
- Sĩ số / nhóm: 2 học sinh / máy. Sĩ số lớp: `[TODO]`.
- Công cụ: [GearsBot](https://gears.aposteriori.com.sg) trên trình duyệt (miễn phí, không cần tài khoản, mã nguồn mở GPL-3.0).
  Robot, sa bàn và link mở sẵn: [stlab/simulation/gearsbot/](../simulation/gearsbot/README.md).
- Nối tiếp: [arduino-mega-intro.md](arduino-mega-intro.md) (HC-SR04) → giáo án này → lắp `maker/line-bot` thật.

## Mục tiêu
- Giải thích được vì sao **vị trí cảm biến** (trước/sau trục bánh, khoảng cách hai mắt) làm robot bám line tốt hoặc lắc.
- Lắp được robot ảo trong Robot Configurator: thêm, xóa, dời cảm biến màu và siêu âm; lưu robot ra file `.json`.
- Lập trình được xe dò line 2 cảm biến bằng khối (cơ bản) hoặc Python (mở rộng), có tham số tốc độ và hệ số `KP`.
- Lập trình được vòng tránh vật cản 20 × 20 cm bằng cảm biến siêu âm.
- Kể được ít nhất 3 khác biệt giữa robot ảo và robot thật, và chọn được bố trí cảm biến cho bản thật.

## Chuẩn bị
| Vật tư | Số lượng | Ghi chú |
|---|---|---|
| Máy tính có trình duyệt Chrome/Edge | 1 / nhóm | Cần mạng để mở GearsBot online. Tốc độ khung hình trên máy lab: `[TODO]` đo trước buổi 1 |
| Link mở sẵn 3 bài (line đơn giản, cua gắt, vật cản) | — | In mã QR hoặc gửi qua nhóm lớp |
| Phiếu ghi kết quả (bảng thử nghiệm buổi 1) | 1 / nhóm | Mẫu ở cuối giáo án |
| Buổi 3: `maker/line-bot` đã lắp + sa bàn line in/dán băng keo đen trên nền trắng | 1 bộ / lớp | Nếu chưa có robot thật: giáo viên chiếu video chạy thật `[TODO]` |

## An toàn
- Buổi 1–2 chỉ dùng máy tính: nghỉ mắt 5 phút sau mỗi 30–40 phút nhìn màn hình.
- Buổi 3 (robot thật): pin 2S Li-ion (2 × 18650, 7,4 V danh định, 8,4 V khi đầy) – không để chạm chập hai cực, không sạc khi không có người lớn, pin phồng thì ngừng dùng. Motor N20 kẹt bánh sẽ nóng: tắt nguồn ngay khi robot kẹt. Giáo viên cấp nguồn và tháo pin sau buổi.
- Robot chạy trên bàn: chắn mép bàn hoặc chạy dưới sàn để robot không rơi.

## Buổi 1 (90 phút) – Lắp robot ảo, cảm biến đặt ở đâu?
1. **Khởi động (10 phút):** cho xem `maker/line-bot` thật (hoặc ảnh). Hỏi: "Nếu lắp sai chỗ cảm biến, phải tháo vít, in lại gá – mất bao lâu?" → giới thiệu ý tưởng *thử trên máy trước*.
2. **Khám phá (15 phút):** mở link "Line đơn giản". Làm quen tab **Simulator**: chạy ▶, đặt lại ⟳, đổi góc camera. Mở **Robot → Robot Configurator** để xem robot STLab: thân, 2 bánh, 2 cảm biến màu (cổng 1, 2), siêu âm (cổng 3).
3. **Thực hành (45 phút):**
   - Dùng chương trình mẫu 1 cảm biến của giáo viên (`solutions/00-one-sensor.py`, dán vào tab Python; thấy đen → rẽ trái, thấy trắng → rẽ phải). Nhóm nào muốn thì dựng lại bằng khối.
   - **Thí nghiệm bố trí:** mỗi nhóm thử 3 vị trí cảm biến trong Configurator – (a) trước trục bánh 6 cm (mặc định), (b) ngay trên trục bánh, (c) sau trục bánh. Mỗi lần: lưu robot, chạy, ghi vào phiếu: robot đi hết đường không, có lắc không, mất bao nhiêu giây.
   - Lưu robot nhóm thấy tốt nhất ra file `ten-nhom.json`.
4. **Chia sẻ (15 phút):** các nhóm so sánh phiếu. Rút ra quy tắc *của lớp* (không đọc đáp án trước): cảm biến ở đâu thì robot phản ứng kịp với khúc cua?
5. **Tổng kết (5 phút):** robot thật của STLab đặt mắt dò line trước trục bánh 60 mm – lý do là kết quả các em vừa thấy.

**Sản phẩm buổi 1:** phiếu thí nghiệm 3 vị trí + file robot `.json` của nhóm.

## Buổi 2 (90 phút) – Hai cảm biến và hệ số KP
1. **Khởi động (10 phút):** robot 1 cảm biến đi "zigzag" – vì sao? Hai cảm biến giúp gì?
2. **Khám phá (15 phút):** ý tưởng *độ lệch* = sáng trái − sáng phải. Lệch âm → line nằm bên trái → bánh trái chậm lại. Vẽ lên bảng.
3. **Thực hành (50 phút):**
   - **Cơ bản (khối):** lập trình tốc độ hai bánh = `tốc độ ± KP × độ lệch`. Thử `KP` = 0,2 / 0,6 / 1,5 trên sa bàn "Line đơn giản", ghi kết quả.
   - Chuyển sang tab **Python** để xem code GearsBot tự sinh từ khối.
   - **Mở rộng (học sinh khá, Python):** sa bàn "Cua gắt" – lời giải mẫu của giáo viên vẫn văng ở vòng kẹp tóc. Nhóm nào chỉnh `TOC_DO`, `KP` hoặc thêm luật "mất line thì quay tìm lại" để qua được?
4. **Chia sẻ (10 phút):** nhóm có `KP` tốt nhất trình chiếu; cả lớp chạy lại cùng tham số để kiểm.
5. **Tổng kết (5 phút):** `KP` lớn quá → lắc, nhỏ quá → trượt khỏi cua. Firmware line-bot thật dùng cùng ý tưởng (PID).

**Sản phẩm buổi 2:** chương trình dò line 2 cảm biến chạy hết sa bàn "Line đơn giản"; bảng thử `KP`.

## Buổi 3 (90 phút) – Vật cản và "ảo khác thật ở đâu?"
1. **Khởi động (5 phút):** chiếu sa bàn "Vật cản" (2 khối 20 × 20 cm nằm trên line).
2. **Thực hành ảo (35 phút):** dùng siêu âm cổng 3: gặp vật cản gần hơn 10 cm → xoay phải 90° → chạy vòng cung (bánh trái chậm hơn bánh phải) → gặp lại line thì xoay về hướng line. Nhóm khá tính bán kính cung từ khoảng cách 2 bánh (15,8 cm).
3. **Thử thật (35 phút, giáo viên điều khiển nguồn):** chạy `maker/line-bot` trên sa bàn thật cùng thuật toán. Các nhóm quan sát, ghi khác biệt vào bảng "ảo – thật": ánh sáng phòng, độ cao mắt dò line (ảo 28 mm, thật 3 mm), hai motor chạy lệch, trượt bánh khi xoay.
4. **Chia sẻ + tổng kết (15 phút):** mỗi nhóm nêu 1 điều mô phỏng giúp được và 1 điều mô phỏng **không** thay được (phải thử thật).

**Sản phẩm buổi 3:** chương trình tránh vật cản chạy trên sa bàn ảo; bảng "ảo – thật" có ít nhất 3 dòng.

## Đánh giá (rubric)
| Tiêu chí | Đạt | Tốt | Xuất sắc |
|---|---|---|---|
| Lắp robot ảo | Đổi được vị trí cảm biến, lưu file | Thử đủ 3 vị trí, ghi phiếu đầy đủ | Giải thích được kết quả bằng khoảng cách cảm biến – trục bánh |
| Dò line | Robot đi hết "Line đơn giản" | Có bảng thử ≥ 3 giá trị `KP`, chọn có lý do | Qua được "Cua gắt" |
| Tránh vật cản | Robot vòng qua 1 vật cản | Vòng qua cả 2 và về lại line | Tính bán kính cung trước khi thử |
| Ảo – thật | Kể 1 khác biệt | Kể 3 khác biệt | Đề xuất cách sửa cho bản thật (vd. hiệu chỉnh trắng/đen) |

## Câu hỏi kiểm tra cuối khóa
- Vì sao robot dò line đặt cảm biến **trước** trục bánh?
- Hệ số `KP` quá lớn thì robot chạy thế nào? Quá nhỏ thì sao?
- Nêu 2 việc mô phỏng **không** kiểm được thay cho robot thật.

## Phiếu thí nghiệm buổi 1 (mẫu)
| Lần | Vị trí cảm biến | Đi hết đường? | Lắc ít / nhiều | Thời gian (s) | Nhận xét |
|---|---|---|---|---|---|
| a | Trước trục 6 cm | | | | |
| b | Trên trục | | | | |
| c | Sau trục | | | | |

## Tài liệu
- Robot, sa bàn, lời giải mẫu, ảnh kiểm tra: [stlab/simulation/gearsbot/](../simulation/gearsbot/README.md) (đã chạy thử 2026-11-11: bài 1 và bài vật cản PASS).
- Nghiên cứu chọn công cụ: [docs/reports/robotics-simulation-for-students.md](../../docs/reports/robotics-simulation-for-students.md).
- Giáo trình GearsBot (tiếng Anh) của tác giả: [aposteriori-sg tutorials](https://aposteriori-sg.github.io/tutorials/17-Robotics-with-Gearsbot/10-Introduction/30-The-GearsBot-App.html).
