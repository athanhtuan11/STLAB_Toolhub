# Erebus – RCJ Rescue Simulation cho đội STLab

[Erebus](https://erebus.rcj.cloud/) là nền tảng chính thức của hạng **RoboCupJunior Rescue Simulation**: robot ảo tự
khám phá mê cung, vẽ bản đồ, tìm nạn nhân. Học sinh **tự lắp robot trong giới hạn ngân sách** rồi lập trình bằng
Python trên Webots. Hợp đội lớp 8–12 đã biết Python (sau giáo án GearsBot).

Nguồn ghim: `community/robocup-junior-erebus/` (v26, `8e56efe`) và `community/robocup-junior-erebus-robot-customisation/`.
License hai repo chưa ghi trên GitHub (`TODO` hỏi BTC trước khi phân phát lại; dùng để học/thi thì không vấn đề).

> **Trạng thái 2026-11-11:** chưa cài Webots trên máy STLab nên **chưa chạy thử** controller. Mọi số dưới đây lấy từ mã
> nguồn Erebus đã ghim, không phải đo.

## Cài đặt (mỗi máy thi đấu/luyện tập)

1. Python **3.9+** (thêm vào PATH khi cài).
2. **Webots R2023b**: đúng bản này, bản mới hơn chưa chắc chạy được. Tải tại [cyberbotics.com](https://cyberbotics.com/).
3. Tải [bản phát hành Erebus mới nhất](https://github.com/robocup-junior/erebus/releases) (v26.0.0, 2026-01-27), giải nén.
4. Mở world trong thư mục `game/worlds/` bằng Webots, rồi nạp controller qua giao diện Erebus. Hướng dẫn chi tiết:
   [Erebus docs](https://erebus.rcj.cloud/).

Yêu cầu máy: Webots dùng OpenGL. Máy lab GPU tích hợp cần thử scene trước (`TODO` đo FPS).

## Lắp robot: ngân sách 3000 điểm

Lắp trên web [robot.erebus.rcj.cloud](https://robot.erebus.rcj.cloud): đặt cảm biến bằng gizmo 3D, xuất file JSON rồi
nạp vào Erebus. Erebus tự kiểm tra lại ngân sách khi nạp (`ProtoGenerator.py`).

| Linh kiện | Điểm | Giới hạn |
|---|---:|---|
| Bánh xe (có encoder) | 300 / bánh | robot mặc định 2 bánh = 600 |
| Cảm biến khoảng cách (hồng ngoại, đo 0–0,8 m) | 50 | tối đa 8 |
| Cảm biến màu | 100 | |
| Gyro / Inertial unit / Gia tốc kế | 100 mỗi loại | |
| GPS | 250 | |
| Camera | 500 + phụ phí độ phân giải | tối đa 3. Mỗi chiều 32/40 px: +0; 64: +100; 128: +200; 256: +300 |
| Lidar | 500 | |

**Bài tập chọn linh kiện (buổi 1 của đội):** mỗi học sinh lập 1 cấu hình ≤ 3000 điểm và trả lời 3 câu:
cảm biến nào để **đi mê cung** (khoảng cách, lidar), cảm biến nào để **thấy nạn nhân** (camera), cảm biến nào để **biết mình ở đâu**
(GPS, gyro, encoder bánh). Ví dụ cách cộng: 2 bánh 600 + 8 khoảng cách 400 + 2 camera 40×32 px 1000 + màu 100 + gyro 100
= 2200, còn dư 800 (thêm GPS 250 hoặc lidar 500). Đây chỉ là ví dụ phép tính, không phải cấu hình khuyến nghị.

## Controller khởi đầu

`controllers/stlab_starter.py` (chưa chạy thử): robot mặc định của trang lắp ráp, chạy thẳng, gặp tường thì xoay về phía thoáng.
Tên thiết bị theo `customName` trong file robot: bánh `wheel1 motor`/`wheel2 motor`, cảm biến `distance sensor1..4`.
Ví dụ chính chủ để đọc thêm: `community/robocup-junior-erebus/player_controllers/` (giao tiếp với supervisor, dò màu, nạn nhân).

## Lộ trình đội (đề xuất)

| Tuần | Việc | Sản phẩm |
|---|---|---|
| 1 | Cài Webots + Erebus, chạy controller khởi đầu | Robot chạy trong mê cung không đâm tường |
| 2 | Bài tập ngân sách, lắp robot của đội | File robot JSON ≤ 3000 |
| 3–4 | Bám tường (tay phải/tay trái), dùng encoder để đi đúng 1 ô | Đi hết mê cung đơn giản |
| 5–6 | Camera nhận nạn nhân, gửi kết quả cho supervisor | Ghi điểm nạn nhân |
| 7+ | Vẽ bản đồ, tối ưu theo luật năm thi | Luyện theo [luật chính thức](https://junior.robocup.org/rcj-rescue-sim/) |

Lưu ý: Erebus là Rescue **Maze** (mê cung). Đội line-bot thi Rescue **Line** thì đây là hạng **riêng**; chưa có bộ mô phỏng
chính thức cho Rescue Line (`TODO` nếu BTC công bố).

## Tài liệu
- [RCJ Rescue Simulation](https://junior.robocup.org/rcj-rescue-sim/), [Erebus](https://erebus.rcj.cloud/), [repo](https://github.com/robocup-junior/erebus)
- Nghiên cứu chọn công cụ: [docs/reports/robotics-simulation-for-students.md](../../../docs/reports/robotics-simulation-for-students.md)
