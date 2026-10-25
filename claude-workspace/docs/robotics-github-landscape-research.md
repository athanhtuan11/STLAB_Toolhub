# Nghiên cứu: bức tranh robotics mã nguồn mở trên GitHub, STLab nên làm mảng nào

Viết 2026-10-25. Số liệu GitHub tra cùng ngày qua GitHub REST API (search + repos), Tuan sửa/bổ sung trực tiếp file này.

**Phạm vi:** gom các dự án robotics mã nguồn mở trên GitHub thành **mảng**, rồi chấm độ hợp với STLab
(dạy học cấp 1–3, dự án maker, video marketing) theo năng lực hiện có: Bambu A1 + PETG, FreeCAD 1.1 tự động hóa,
Blender, bộ CyberBrick (XA003 = ESP32-C3 + MicroPython, XA004 = 2 motor DC + 4 servo, pin PC003 Li-ion 2S 7,4 V),
ESP32, Raspberry Pi, PC i5-13400F + GTX 1660 Super 6 GB.

**Không lặp:** cơ khí cánh tay in 3D (SO-ARM, PAROL6, Arctos, Moveo, Thor, EEZYbotARM), nối trục/truyền động in,
kiểm khớp trước in, dạy CAD → [cad-mechanisms-teaching-research.md](cad-mechanisms-teaching-research.md).
Dung sai/in FDM → [cad-community-gaps-research.md](cad-community-gaps-research.md). Tự động hóa FreeCAD →
[freecad-automation-research.md](freecad-automation-research.md). Làm dáng/mockup trước →
[design-first-research.md](design-first-research.md). Video → [project-video-marketing-research.md](project-video-marketing-research.md),
[project-video-tutorial-hashtag-workflow.md](project-video-tutorial-hashtag-workflow.md), [trend-content-ideas.md](trend-content-ideas.md).

**Nhãn:** **[nguồn gốc]** = README/docs chính thức/paper của dự án · **[API]** = số liệu GitHub API ngày 2026-10-25
· **(thứ cấp)** = blog/forum/đại lý · `TODO` = chưa xác nhận.

**Cách đọc số GitHub:** "★" = số sao; "push" = `pushed_at` (lần push gần nhất lên bất kỳ nhánh nào, gần đúng
"commit gần nhất", không phải ngày release). Không có star history theo thời gian → **"★/tháng" = sao ÷ số tháng kể từ khi
tạo repo**, chỉ là tốc độ trung bình, không phải xu hướng hiện tại. Xu hướng thật (đang tăng/chững) = `TODO` (star-history.com).

## 0. Kết luận nhanh

1. **Mảng nóng nhất là "AI cho robot" (imitation learning chi phí thấp).** `huggingface/lerobot` 28 447★ (~860★/tháng),
   cánh tay SO-ARM100/101 7 866★, XLeRobot 5 634★ trong 18 tháng. Nhưng phần cứng chuẩn dùng **servo bus có phản hồi**
   (Feetech STS3215), không phải servo CyberBrick → STLab phải mua mới (~230 USD cho cặp leader+follower SO-101, chưa tính in).
2. **Mảng hợp STLab nhất ngay bây giờ là robot 4 chân mini ESP32 in 3D.** `dorianborian/sesame-robot` 4 818★ chỉ trong
   11 tháng (~440★/tháng), 50–60 USD linh kiện, 8 servo MG90S, ESP32 + Arduino, **in được, ít support**, có mặt OLED biểu cảm,
   và bo V3 **hỗ trợ pin Bambu Lab 7,4 V** – rất "ăn video".
3. **Giọng nói + LLM trên ESP32 bùng nổ.** `78/xiaozhi-esp32` 31 887★ (~1 230★/tháng): ESP32-S3/C3…, wake word offline,
   MCP điều khiển servo/GPIO, MCP phía cloud điều khiển smart home → nối thẳng `smart-home` (Home Assistant) và robot để bàn.
4. **Mô phỏng: GTX 1660 Super không chạy được Isaac Sim/Isaac Lab** (yêu cầu tối thiểu RTX 4080 16 GB, "GPU không có RT core
   không được hỗ trợ"). Dùng **MuJoCo / Webots / Gazebo** (chạy CPU/OpenGL). Huấn luyện LeRobot `act` cần ~2–6 GB VRAM
   theo bảng của LeRobot → 6 GB **có thể vừa** với batch nhỏ, chưa thử (`TODO`); policy lớn hơn phải dùng Colab/cloud.
5. **ROS 2 + micro-ROS trên ESP32 là con đường "nghiêm túc" cho cấp 3/CLB**, nhưng khó và ít giá trị video so với 4 chân/giọng nói.
   micro-ROS ESP-IDF đã thử trên ESP32, S2, S3, **C3** (đúng chip CyberBrick), C6, P4.
6. **Drone hot trên GitHub (ArduPilot 16 200★, PX4 12 897★) nhưng rủi ro an toàn cao** (cánh quạt, LiPo) → để sau,
   chỉ làm khi `uwb-drone-positioning` có lồng bay + kill-switch.
7. **Robot thi đấu học sinh (line follower, sumo) phân mảnh**: repo lẻ < 150★, không có "dự án chuẩn" để bám → STLab nên tự làm
   bộ bài thi riêng trên nền CyberBrick/ESP32 thay vì chờ cộng đồng.
8. **Đề xuất làm trước 3 mảng:** (A) robot 4 chân mini ESP32, (B) robot trợ lý giọng nói ESP32 + smart home,
   (C) imitation learning LeRobot ở mức "1 cánh tay, 1 việc gắp". Chi tiết ở [Lộ trình đề xuất](#lộ-trình-đề-xuất).

## 1. Bảng tổng hợp các mảng

Độ hợp STLab và giá trị video: thang 1–5, Claude chấm theo năng lực ở đầu file (ý kiến, không phải số đo).

| # | Mảng | Repo tiêu biểu (★ [API]) | Chi phí phần cứng (nguồn) | Độ khó | GPU | Hợp STLab | Video |
|---|---|---|---|---|---|---|---|
| 1 | AI cho robot / imitation learning | lerobot 28 447, openpi 14 380, Isaac-GR00T 8 252, SO-ARM100 7 866, XLeRobot 5 634 | SO-101 cặp leader+follower 229,88 USD; XLeRobot ~660 USD [nguồn gốc] | Cao | `act` 2–6 GB; VLA 10–40 GB | 3 | 5 |
| 2 | Robot di động & ROS 2 | ros2 6 231, navigation2 4 876, OpenBot 3 575, turtlebot3 2 085, linorobot2 1 063, micro_ros_* 421–580 | OpenBot ~50 USD + điện thoại [nguồn gốc]; LiDAR `TODO` | Cao | Không | 3 | 3 |
| 3 | Robot chân / quadruped mini | OpenCat 5 496, sesame-robot 4 818, champ 2 331, spotMicro 2 160, StanfordQuadruped 1 824 | Sesame 50–60 USD [nguồn gốc] | Trung bình | Không | **5** | **5** |
| 4 | Humanoid nhỏ & robot biểu cảm | openarm 3 637, jumper 2 878, berkeley-humanoid-lite 1 993, reachy_mini 1 585, toddlerbot 788 | Berkeley Lite < 5 000 USD [nguồn gốc]; còn lại `TODO` | Rất cao | Huấn luyện RL cần GPU/Colab | 2 | 5 |
| 5 | Robot giáo dục giá rẻ | OpenBot 3 575, pybricks 352, Makeblock libs 276, CyberBrick core 235, OttoDIYLib 205 | Otto `TODO`; CyberBrick đã có | Thấp | Không | 4 | 4 |
| 6 | Drone | ardupilot 16 200, PX4 12 897, betaflight 11 695, inav 4 276, esp-drone 2 268, crazyflie 1 562 | `TODO` | Trung bình–cao | Không | 2 | 4 |
| 7 | Mô phỏng | genesis-world 30 117, mujoco 15 859, IsaacLab 8 456, webots 4 720, mujoco_menagerie 4 259, gz-sim 1 552 | 0 (phần mềm) | Trung bình | Isaac: RTX 4080+; MuJoCo/Webots/Gazebo: không cần GPU lớn | 4 | 3 |
| 8 | Thị giác trên thiết bị nhỏ | ultralytics 62 813, mediapipe 37 397, openmv 2 888, esp-who 2 169, ESP32-CAM_MJPEG2SD 1 765 | `TODO` | Trung bình | Huấn luyện YOLO nhỏ: có thể trên 1660 (`TODO`) | 4 | 4 |
| 9 | Giọng nói / LLM cho robot | xiaozhi-esp32 31 887, OM1 2 956, esp-sr 1 549, wyoming 409, reachy_mini_conversation_app 334 | `TODO` (bo ESP32-S3 + mic + loa) | Trung bình | Không (dùng server/cloud) | **5** | **5** |
| 10 | Robot + smart home | home-assistant/core 91 709, zigbee2mqtt 15 756, esphome 11 951, Valetudo 9 839 | Đã có ESP32 | Thấp–TB | Không | 4 | 3 |
| 11 | Robot thi đấu học sinh | FtcRobotController 1 381, allwpilib 1 313, pybricks 352; line follower/sumo < 150 | `TODO` | Thấp–TB | Không | 3 | 4 |
| 12 | Firmware/công cụ cho học sinh | micropython 22 153, arduino-esp32 17 617, blockly 13 592, platformio 9 559, pxt-microbit 809, Mixly_Arduino 316 | 0 | Thấp | Không | 5 (nền) | 2 |

## 2. Từng mảng

### 2.1 AI cho robot / imitation learning chi phí thấp

| Repo | ★ | Push | Tạo | License |
|---|---|---|---|---|
| [huggingface/lerobot](https://github.com/huggingface/lerobot) | 28 447 | 2026-10-24 | 2024-01 | Apache-2.0 |
| [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | 14 380 | 2026-08-24 | 2024-10 | Apache-2.0 |
| [NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) | 8 252 | 2026-10-22 | 2025-03 | Apache-2.0 |
| [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) (SO-100/101) | 7 866 | 2026-10-06 | 2024-05 | Apache-2.0 |
| [Vector-Wangel/XLeRobot](https://github.com/Vector-Wangel/XLeRobot) | 5 634 | 2026-10-06 | 2025-04 | Apache-2.0 |
| [AlexanderKoch-Koch/low_cost_robot](https://github.com/AlexanderKoch-Koch/low_cost_robot) (Koch) | 3 423 | 2024-09-21 | 2024-03 | MIT – **chững** (không push > 2 năm) |

- **Chi phí [nguồn gốc]:** SO-101 cặp leader+follower **229,88 USD** (12 servo STS3215 7,4 V × 13,89 USD + 2 bo điều khiển
  + nguồn + kẹp bàn; không tính in). Chỉ follower rẻ hơn. XLeRobot (2 tay + đế di động) **~660 USD**, không tính in 3D.
  Giá về VN: `TODO`.
- **GPU [nguồn gốc – LeRobot Compute HW Guide]:** `act` ~2–6 GB VRAM (batch 8), `diffusion` 8–14 GB, `smolvla` 10–16 GB,
  `pi0`/`groot` 24–40 GB. GTX 1660 Super 6 GB: chỉ nhắm `act`, batch nhỏ; Turing TU116 không có tensor core nên chậm hơn
  bảng (bảng chỉ có RTX 3090/4090, L4, A100) – thời gian thực `TODO`.
- **Hợp STLab:** in khung trên A1 được; **không dùng lại servo CyberBrick** (cần servo bus đọc được vị trí). pushrod-arm là cơ cấu
  khác (xi-lanh đẩy) – chỉ dùng làm bài so sánh động học. Cấp 3/CLB. Video rất mạnh ("dạy robot bằng cách cầm tay").
- **An toàn:** nguồn 5–12 V adapter, kẹp ngón tay ở gripper; không có pin nếu dùng adapter.

### 2.2 Robot di động & ROS 2

| Repo | ★ | Push | License |
|---|---|---|---|
| [ros2/ros2](https://github.com/ros2/ros2) (repo tổng) | 6 231 | 2026-10-20 | không ghi (`TODO`; từng gói có license riêng) |
| [ros-navigation/navigation2](https://github.com/ros-navigation/navigation2) | 4 876 | 2026-10-23 | NOASSERTION |
| [ob-f/OpenBot](https://github.com/ob-f/OpenBot) (trước là isl-org) | 3 575 | 2026-10-25 | MIT |
| [ROBOTIS-GIT/turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3) | 2 085 | 2026-06-15 | Apache-2.0 |
| [linorobot/linorobot2](https://github.com/linorobot/linorobot2) | 1 063 | 2026-10-06 | Apache-2.0 |
| [micro-ROS/micro_ros_espidf_component](https://github.com/micro-ROS/micro_ros_espidf_component) / [micro_ros_arduino](https://github.com/micro-ROS/micro_ros_arduino) | 421 / 580 | 2026-10-02 / 2026-01-28 | Apache-2.0 |

- micro-ROS ESP-IDF: đã thử với ESP-IDF 5.2–6.0 trên ESP32, S2, S3, **C3**, C6, P4 [nguồn gốc]. micro_ros_arduino liệt kê "ESP32 Dev Module".
- linorobot2: URDF có sẵn LiDAR/RGBD/IMU, Nav2, Gazebo; hỗ trợ LiDAR rẻ (LD06, LD19, RPLIDAR C1…) [nguồn gốc]; firmware chính cho Teensy.
- OpenBot: thân xe ~50 USD, **điện thoại Android làm não** (bám người, tự hành) [nguồn gốc] – hợp với lớp không có Pi.
- **Hợp STLab:** cyberbrick-car → thêm encoder + micro-ROS là thành robot ROS 2 nhỏ; FreeCAD → URDF qua RobotCAD đã có
  trong `robotics-cad`. Khó cho cấp 1–2; cấp 3/CLB. Video trung bình (bản đồ SLAM đẹp nhưng chậm).

### 2.3 Robot chân / quadruped mini

| Repo | ★ | Push | Tạo | License |
|---|---|---|---|---|
| [PetoiCamp/OpenCat-Quadruped-Robot](https://github.com/PetoiCamp/OpenCat-Quadruped-Robot) | 5 496 | 2026-09-08 | 2021-01 | MIT |
| [dorianborian/sesame-robot](https://github.com/dorianborian/sesame-robot) | 4 818 | 2026-10-15 | **2025-11** | Apache-2.0 |
| [chvmp/champ](https://github.com/chvmp/champ) | 2 331 | 2024-07-04 | 2019-05 | BSD-3 – chững |
| [mike4192/spotMicro](https://github.com/mike4192/spotMicro) | 2 160 | 2021-03-20 | 2020-03 | MIT – chững |
| [stanfordroboticsclub/StanfordQuadruped](https://github.com/stanfordroboticsclub/StanfordQuadruped) (Pupper) | 1 824 | 2024-10-24 | 2020-01 | MIT – chững |
| [michaelkubina/SpotMicroESP32](https://github.com/michaelkubina/SpotMicroESP32) | 426 | 2024-11-25 | 2020-07 | GPL-3.0 |

- **Sesame [nguồn gốc]:** 8 servo MG90S **loại 180°** (README cảnh báo mua sai loại sẽ không chạy), OLED 0,96" SSD1306,
  ESP32-S2 Mini hoặc bo Sesame V3; nguồn 5 V 3 A (USB-C PD hoặc pin + buck); tùy chọn **pin Bambu Lab 14500 7,4 V 800 mAh**;
  REST/JSON API, web UI, Sesame Studio soạn động tác, app Python điều khiển giọng nói. Thiết kế cho **PLA**, ít support.
- OpenCat: repo này cho bo NyBoard cũ; phần cứng hiện hành (Bittle X, ESP32) ở `OpenCatEsp32-Quadruped-Robot` [nguồn gốc].
  Petoi là sản phẩm thương mại (kit), firmware mở.
- **Hợp STLab: 5/5.** In A1 (thử PETG thay PLA – `TODO`), ESP32/Arduino, MG90S đã dùng trong cyberbrick-car, cùng hệ pin Bambu.
  Lưu ý: bộ thu CyberBrick XA004 chỉ **4 servo** → Sesame cần 8 → dùng bo Sesame/ESP32 riêng hoặc PCA9685 (`TODO` chọn).
  Cấp 2–3 lắp ráp, cấp 1 điều khiển bằng app/khối lệnh. Video 5/5 (đi, vẫy tay, mặt cảm xúc).
- **An toàn:** 8 servo kéo dòng đỉnh lớn – buck phải ≥ 3 A theo README; pin Li-ion 2S: không sạc khi không có người, không chập.

### 2.4 Humanoid / biped nhỏ & robot biểu cảm

| Repo | ★ | Push | License |
|---|---|---|---|
| [enactic/openarm](https://github.com/enactic/openarm) | 3 637 | 2026-10-23 | Apache-2.0 |
| [KingKongRobotics/jumper](https://github.com/KingKongRobotics/jumper) (cua 22 bậc tự do) | 2 878 | 2026-10-19 | Apache-2.0 – **tạo 2026-09-28, < 1 tháng** |
| [HybridRobotics/berkeley-humanoid-lite](https://github.com/HybridRobotics/berkeley-humanoid-lite) | 1 993 | 2026-03-10 | code MIT, tài sản CC BY-SA 4.0 |
| [pollen-robotics/reachy_mini](https://github.com/pollen-robotics/reachy_mini) | 1 585 | 2026-10-24 | code Apache-2.0, **phần cứng CC BY-SA-NC** |
| [hshi74/toddlerbot](https://github.com/hshi74/toddlerbot) | 788 | 2026-07-31 | code MIT, **thiết kế CC BY-NC-SA** |
| [TheRobotStudio/HOPEJr](https://github.com/TheRobotStudio/HOPEJr) | 839 | 2026-05-04 | không ghi (`TODO`) |

- Berkeley Humanoid Lite: < 5 000 USD, hộp số in 3D [nguồn gốc]. Reachy Mini: có bản mô phỏng MuJoCo, app store qua HF Spaces [nguồn gốc].
- Jumper: huấn luyện dáng đi bằng MuJoCo/mjlab + RL, có notebook Colab GPU [nguồn gốc] – mẫu tốt cho "AI agent tạo động tác".
- **Hợp STLab: 2/5** – đắt, cần RL/GPU. Lấy ý tưởng (robot biểu cảm để bàn kiểu Reachy Mini) cho mảng 2.9 thì hợp hơn.

### 2.5 Robot giáo dục giá rẻ

| Repo | ★ | Push | License |
|---|---|---|---|
| [ob-f/OpenBot](https://github.com/ob-f/OpenBot) | 3 575 | 2026-10-25 | MIT |
| [pybricks/pybricks-micropython](https://github.com/pybricks/pybricks-micropython) (LEGO) | 352 | 2026-10-24 | NOASSERTION |
| [Makeblock-official/Makeblock-Libraries](https://github.com/Makeblock-official/Makeblock-Libraries) (mBot) | 276 | 2026-10-10 | không ghi |
| [CyberBrick-Official/CyberBrick_Controller_Core](https://github.com/CyberBrick-Official/CyberBrick_Controller_Core) | 235 | 2026-06-09 | NOASSERTION (`TODO`) |
| [OttoDIY/OttoDIYLib](https://github.com/OttoDIY/OttoDIYLib) | 205 | 2024-06-08 | GPL-3.0 – chững |

- Ít sao vì cộng đồng giáo dục sống ở nơi khác (web Otto, Makeblock, Bambu MakerWorld) – số sao GitHub đánh giá thấp mảng này.
- **Hợp STLab: 4/5** – CyberBrick chính là bộ giáo dục STLab đang dùng; Otto (biped 4 servo) là bài nhập môn rẻ (giá `TODO`).

### 2.6 Drone

| Repo | ★ | Push | License |
|---|---|---|---|
| [ArduPilot/ardupilot](https://github.com/ArduPilot/ardupilot) | 16 200 | 2026-10-23 | GPL-3.0 |
| [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) | 12 897 | 2026-10-25 | BSD-3 |
| [betaflight/betaflight](https://github.com/betaflight/betaflight) | 11 695 | 2026-10-24 | GPL-3.0 |
| [iNavFlight/inav](https://github.com/iNavFlight/inav) | 4 276 | 2026-10-23 | GPL-3.0 |
| [espressif/esp-drone](https://github.com/espressif/esp-drone) | 2 268 | 2026-08-10 | GPL-3.0 |
| [bitcraze/crazyflie-firmware](https://github.com/bitcraze/crazyflie-firmware) | 1 562 | 2026-10-23 | GPL-3.0 |

- ESP-Drone: ESP32/S2/S3, điều khiển qua app/gamepad Wi-Fi, code port từ Crazyflie, **nhắm STEAM education** [nguồn gốc];
  yêu cầu ESP-IDF release/v5.0 (cũ).
- **Hợp STLab: 2/5 lúc này.** Nối với `uwb-drone-positioning` (còn TODO). **Rủi ro:** cánh quạt cắt tay/mắt, LiPo cháy –
  bắt buộc lồng bay/lưới, kính, kill-switch, tháo cánh khi test bàn (đã ghi trong CLAUDE.md dự án). Không hợp cấp 1.

### 2.7 Mô phỏng

| Repo | ★ | Push | License | Chạy trên GTX 1660 Super 6 GB? |
|---|---|---|---|---|
| [Genesis-Embodied-AI/genesis-world](https://github.com/Genesis-Embodied-AI/genesis-world) | 30 117 | 2026-10-25 | Apache-2.0 | `TODO` (có backend CPU? chưa kiểm) |
| [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco) | 15 859 | 2026-10-24 | Apache-2.0 | Có (vật lý chạy CPU) – `TODO` thử |
| [isaac-sim/IsaacLab](https://github.com/isaac-sim/IsaacLab) | 8 456 | 2026-10-25 | NOASSERTION | **Không** – Isaac Sim tối thiểu RTX 4080 16 GB, GPU không RT core không hỗ trợ [nguồn gốc] |
| [cyberbotics/webots](https://github.com/cyberbotics/webots) | 4 720 | 2026-10-24 | Apache-2.0 | Có (`TODO` thử) |
| [google-deepmind/mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie) | 4 259 | 2026-10-23 | NOASSERTION (theo từng model) | Có |
| [gazebosim/gz-sim](https://github.com/gazebosim/gz-sim) | 1 552 | 2026-10-24 | Apache-2.0 | Có (`TODO` thử) |

- **Hợp STLab: 4/5** – FreeCAD → URDF (RobotCAD) → MuJoCo/Gazebo là cầu nối tự nhiên với `robotics-cad`. Video 3/5
  (mô phỏng đẹp nhưng kém "thật" hơn robot thật).

### 2.8 Thị giác máy tính trên thiết bị nhỏ

| Repo | ★ | Push | License |
|---|---|---|---|
| [ultralytics/ultralytics](https://github.com/ultralytics/ultralytics) (YOLO) | 62 813 | 2026-10-24 | **AGPL-3.0** |
| [google-ai-edge/mediapipe](https://github.com/google-ai-edge/mediapipe) | 37 397 | 2026-10-25 | Apache-2.0 |
| [openmv/openmv](https://github.com/openmv/openmv) | 2 888 | 2026-10-23 | không ghi (`TODO`) |
| [espressif/esp-who](https://github.com/espressif/esp-who) | 2 169 | 2026-08-21 | NOASSERTION |
| [s60sc/ESP32-CAM_MJPEG2SD](https://github.com/s60sc/ESP32-CAM_MJPEG2SD) | 1 765 | 2026-10-23 | AGPL-3.0 |
| [hailo-ai/hailo-rpi5-examples](https://github.com/hailo-ai/hailo-rpi5-examples) | 955 | 2026-01-25 | MIT |

- **Hợp STLab: 4/5** – ESP32-CAM/Pi + MediaPipe (bàn tay, khuôn mặt) cho bài "robot nhìn theo tay" rất hợp cấp 2–3.
  Pi 4 chạy YOLO: tốc độ `TODO`. Đi kèm mảng 2.3/2.9 thay vì làm riêng.

### 2.9 Giọng nói / LLM cho robot

| Repo | ★ | Push | Tạo | License |
|---|---|---|---|---|
| [78/xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) | 31 887 | 2026-10-24 | 2024-08 | MIT |
| [OpenMind/OM1](https://github.com/OpenMind/OM1) | 2 956 | 2026-10-13 | 2025-01 | MIT |
| [espressif/esp-sr](https://github.com/espressif/esp-sr) | 1 549 | 2026-10-13 | 2019-07 | NOASSERTION (`TODO`) |
| [OHF-Voice/wyoming](https://github.com/OHF-Voice/wyoming) (giao thức giọng nói của HA) | 409 | 2026-09-29 | 2023-09 | MIT |
| [pollen-robotics/reachy_mini_conversation_app](https://github.com/pollen-robotics/reachy_mini_conversation_app) | 334 | 2026-10-24 | 2025-09 | Apache-2.0 |

- **xiaozhi-esp32 [nguồn gốc]:** ESP32/C3/C5/C6/S3/P4, wake word offline (ESP-SR), ASR + LLM + TTS hoặc mô hình realtime,
  OLED/LCD biểu cảm, **MCP phía thiết bị** (loa, LED, servo, GPIO) và **MCP phía cloud** (smart home…), 39 ngôn ngữ giao diện.
  Cần ESP-IDF ≥ 6.0.1. Cần server: dịch vụ của tác giả hoặc tự host (`xinnan-tech/xiaozhi-esp32-server`).
  Có ví dụ "ESP-HI Low Cost Robot Dog". Tiếng Việt cho ASR/TTS: `TODO`.
- **Hợp STLab: 5/5** – nối `smart-home` (HA) + robot 4 chân/robot để bàn + giọng Việt đã làm cho video (VieNeu-TTS).
- **Rủi ro:** dữ liệu giọng nói học sinh gửi lên server bên ngoài → ưu tiên server tự host trong lab; API key để biến môi trường.

### 2.10 Robot + smart home

| Repo | ★ | Push | License |
|---|---|---|---|
| [home-assistant/core](https://github.com/home-assistant/core) | 91 709 | 2026-10-25 | Apache-2.0 |
| [Koenkk/zigbee2mqtt](https://github.com/Koenkk/zigbee2mqtt) | 15 756 | 2026-10-24 | GPL-3.0 |
| [esphome/esphome](https://github.com/esphome/esphome) | 11 951 | 2026-10-25 | NOASSERTION (MIT + GPLv3 theo phần – `TODO`) |
| [Hypfer/Valetudo](https://github.com/Hypfer/Valetudo) (robot hút bụi chạy offline) | 9 839 | 2026-10-24 | Apache-2.0 |

- **Hợp STLab: 4/5** – đã có dự án `smart-home`. Robot ở đây là "thiết bị chấp hành" (rèm, cửa, robot báo động) – video vừa.

### 2.11 Robot thi đấu học sinh

| Repo | ★ | Push | License |
|---|---|---|---|
| [FIRST-Tech-Challenge/FtcRobotController](https://github.com/FIRST-Tech-Challenge/FtcRobotController) | 1 381 | 2026-09-12 | BSD-3-Clause-Clear |
| [wpilibsuite/allwpilib](https://github.com/wpilibsuite/allwpilib) (FRC) | 1 313 | 2026-10-25 | NOASSERTION |
| [pybricks/pybricks-micropython](https://github.com/pybricks/pybricks-micropython) | 352 | 2026-10-24 | NOASSERTION |
| Line follower/sumo: repo lẻ, vd. [0xShyamRavi/PID-Line-Follower-Robot](https://github.com/0xShyamRavi/PID-Line-Follower-Robot) 140★, [ErichStyger/McuMiniSumoRobot](https://github.com/ErichStyger/McuMiniSumoRobot) 25★ | < 150 | – | – |

- FTC/FRC gắn phần cứng thương mại (REV, VEX…) – ở VN ít tham gia (`TODO` giải nào học sinh Lâm Đồng dự được, WRO có cho pybricks không).
- **Hợp STLab: 3/5** – tự ra luật thi line follower/sumo mini trên CyberBrick (đã có xe) là rẻ và kéo học sinh.

### 2.12 Firmware & công cụ cho học sinh

| Repo | ★ | Push | License |
|---|---|---|---|
| [micropython/micropython](https://github.com/micropython/micropython) | 22 153 | 2026-10-23 | NOASSERTION (MIT – `TODO`) |
| [espressif/arduino-esp32](https://github.com/espressif/arduino-esp32) | 17 617 | 2026-10-25 | LGPL-2.1 |
| [RaspberryPiFoundation/blockly](https://github.com/RaspberryPiFoundation/blockly) (chuyển từ google/blockly) | 13 592 | 2026-10-24 | Apache-2.0 |
| [platformio/platformio-core](https://github.com/platformio/platformio-core) | 9 559 | 2026-10-16 | Apache-2.0 |
| [microsoft/pxt-microbit](https://github.com/microsoft/pxt-microbit) (MakeCode) | 809 | 2026-10-22 | NOASSERTION |
| [mixly/Mixly_Arduino](https://github.com/mixly/Mixly_Arduino) | 316 | 2025-04-16 | NOASSERTION |

- Nền cho mọi mảng: CyberBrick = MicroPython; Sesame = Arduino; xiaozhi = ESP-IDF. Blockly → giao diện kéo-thả cho cấp 1.

### 2.13 Mảng mới nổi đáng theo dõi: AI agent làm CAD/động tác cho robot

- [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 22 957★, tạo 2026-04-22, MIT, "Give your agent CAD superpowers" [API]
  – cùng hướng với pipeline FreeCAD tự động của STLab; xem trong [freecad-automation-research.md](freecad-automation-research.md), không đánh giá ở đây.
- Jumper (2.4) dùng AI agent để thiết kế ngoại hình + huấn luyện động tác. Tốc độ sao 2 repo này rất cao nhưng mới < 7 tháng – xu hướng `TODO`.

## Lộ trình đề xuất

Chỉ là **đề xuất**, chờ Tuan quyết. Thứ tự theo "tận dụng đồ có sẵn + giá trị video / chi phí".

### A. Robot 4 chân mini ESP32 (mảng 2.3) – làm trước

- **Dự án khởi đầu:** `maker/mini-quadruped/` – dựng **Sesame** đúng thiết kế gốc (8 × MG90S 180°, ESP32-S2 Mini, OLED),
  in trên A1 bằng PETG; sau đó bản STLab: vỏ vẽ lại bằng FreeCAD script (quy trình `robotics-cad`), dùng pin Bambu 7,4 V
  chung hệ CyberBrick. Bước 0 theo quy tắc "giao diện trước": mockup dáng + mặt OLED, duyệt bằng ảnh.
- **Nối dự án có sẵn:** MG90S và quy trình in/kiểm (`prepare-print.py`) của cyberbrick-car; khắc dấu lắp như pushrod-arm.
- **Đánh đổi:** rẻ (50–60 USD theo README), video mạnh, cấp 2–3 làm được; nhưng servo MG90S rẻ hay rơ/nóng,
  dáng đi 2 bậc/chân đơn giản (ít "AI"). Thiết kế gốc cho PLA – PETG mềm hơn, cần in thử (`TODO`).

### B. Robot trợ lý giọng nói ESP32 + smart home (mảng 2.9 + 2.10)

- **Dự án khởi đầu:** `maker/voice-robot/` – xiaozhi-esp32 trên một bo ESP32-S3 có mic/loa trong danh sách hỗ trợ,
  server tự host trong lab; MCP thiết bị điều khiển 1–2 servo (gật đầu/quay đầu) + MCP gọi Home Assistant của `smart-home`
  ("bật đèn lab"). Giai đoạn 2: gắn lên robot 4 chân của mục A.
- **Đánh đổi:** cực "ăn video" và hợp mọi cấp học (cấp 1 chỉ nói chuyện); nhưng phụ thuộc LLM/ASR tiếng Việt
  (chất lượng `TODO`), tốn chi phí API hoặc phải tự host, vấn đề quyền riêng tư giọng nói học sinh.

### C. Imitation learning với LeRobot (mảng 2.1 + 2.7)

- **Dự án khởi đầu:** `maker/so101-lerobot/` – in SO-101 (follower + leader) trên A1, mua 12 servo STS3215 + 2 bo,
  ghi ~50 lượt "gắp khối CyberBrick bỏ vào hộp", huấn luyện `act`: thử trên GTX 1660 Super trước, chậm quá thì Colab.
  Trước khi mua: chạy mô phỏng SO-101 trong MuJoCo để dạy khái niệm leader–follower miễn phí.
- **Nối dự án có sẵn:** cơ khí cánh tay ở `cad-mechanisms-teaching-research.md`; pushrod-arm làm bài so sánh
  (servo không phản hồi → không ghi được dữ liệu dạy).
- **Đánh đổi:** đúng xu hướng lớn nhất (AI vật lý), uy tín cho CLB cấp 3; nhưng ~230 USD + phí ship/thuế, huấn luyện chậm
  trên 6 GB, kết quả policy không ổn định (cần nhiều lượt ghi) – không hợp cấp 1–2.

**Để sau:** ROS 2/micro-ROS trên cyberbrick-car (khi có CLB cấp 3 ổn định), drone ESP-Drone (khi có lồng bay),
humanoid (khi có ngân sách/GPU).

## Bảng xem lại khi thương mại

STLab đang phi thương mại → không loại nguồn nào; danh sách này để xem lại nếu bán kit/khóa học có thu phí.

| Nguồn | License | Điểm cần xem |
|---|---|---|
| ultralytics (YOLO) | AGPL-3.0 | Dùng trong sản phẩm/dịch vụ mạng phải mở mã hoặc mua license thương mại |
| s60sc/ESP32-CAM_MJPEG2SD | AGPL-3.0 | Như trên |
| toddlerbot (thiết kế) | CC BY-NC-SA | **Cấm thương mại** thiết kế |
| reachy_mini (phần cứng) | CC BY-SA-NC | **Cấm thương mại** phần cứng |
| berkeley-humanoid-lite (tài sản), AngelLM/Thor | CC BY-SA 4.0 | Share-alike: bản sửa phải cùng license |
| ardupilot, betaflight, inav, esp-drone, crazyflie, OttoDIYLib, SpotMicroESP32, zigbee2mqtt | GPL-3.0 | Phát hành firmware sửa đổi phải kèm mã nguồn |
| arduino-esp32 | LGPL-2.1 | Ràng buộc khi liên kết tĩnh – `TODO` |
| esp-sr, esp-who, CyberBrick_Controller_Core, esphome, IsaacLab, pybricks, Mixly, allwpilib, mujoco_menagerie, navigation2 | NOASSERTION | License không chuẩn/nhiều phần – đọc file LICENSE (esp-sr có thể giới hạn chip Espressif – `TODO`) |
| openmv, HOPEJr, Makeblock-Libraries, ros2/ros2 | API không nhận license | `TODO` đọc repo |
| Sesame, Petoi, XLeRobot | Apache/MIT | Mở, nhưng tên/thương hiệu và kit bán sẵn là của tác giả – không dùng tên khi bán |

## Điểm chưa xác nhận (TODO)

1. **Xu hướng sao theo thời gian** (đang tăng/chững) – mới có ★/tháng trung bình; tra star-history.com cho lerobot, sesame, xiaozhi, genesis.
2. **Giá phần cứng tại VN** (MG90S 180°, STS3215, bo ESP32-S3 có mic/loa, LiDAR LD06) – chưa có số liệu.
3. **Huấn luyện `act` trên GTX 1660 Super 6 GB**: chạy được không, mất bao lâu.
4. **MuJoCo / Webots / Gazebo / Genesis trên máy STLab**: chưa chạy thử.
5. **Sesame in PETG** thay PLA: khớp servo, độ cứng chân.
6. **Điều khiển 8 servo từ CyberBrick**: XA004 chỉ có 4 servo – chọn ESP32 riêng, 2 bộ thu hay PCA9685.
7. **xiaozhi-esp32 tiếng Việt** (ASR/TTS) và chi phí server; bo ESP32-S3 nào mua được ở VN.
8. **Giải thi đấu robot cho học sinh Lâm Đồng/VN** và luật dùng phần mềm mở (WRO + pybricks?).
9. **Isaac Sim trên GTX 1660**: tài liệu không nêu tên GTX 1660, chỉ nói GPU không RT core không hỗ trợ và tối thiểu RTX 4080 → coi như không chạy.
10. License NOASSERTION/không ghi ở bảng trên.

## Nguồn

**[API]** GitHub REST API (`/search/repositories`, `/repos/{owner}/{repo}`), tra 2026-10-25: số sao, `pushed_at`, `created_at`, license của mọi repo ở trên.

**[nguồn gốc]**
- LeRobot README + Compute HW Guide: https://github.com/huggingface/lerobot · https://huggingface.co/docs/lerobot/hardware_guide
- SO-ARM100/101 README (bảng giá): https://github.com/TheRobotStudio/SO-ARM100
- XLeRobot README (giá ~660 USD): https://github.com/Vector-Wangel/XLeRobot
- Sesame README + BOM: https://github.com/dorianborian/sesame-robot · https://github.com/dorianborian/sesame-robot/blob/main/hardware/bom/README.md
- OpenCat README: https://github.com/PetoiCamp/OpenCat-Quadruped-Robot
- OpenBot README: https://github.com/ob-f/OpenBot
- linorobot2 README: https://github.com/linorobot/linorobot2
- micro-ROS ESP-IDF component README: https://github.com/micro-ROS/micro_ros_espidf_component · micro_ros_arduino: https://github.com/micro-ROS/micro_ros_arduino
- ESP-Drone README: https://github.com/espressif/esp-drone
- Isaac Sim requirements: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html
- xiaozhi-esp32 README: https://github.com/78/xiaozhi-esp32
- OM1 README: https://github.com/OpenMind/OM1
- Reachy Mini README: https://github.com/pollen-robotics/reachy_mini
- Berkeley Humanoid Lite README: https://github.com/HybridRobotics/berkeley-humanoid-lite
- ToddlerBot README: https://github.com/hshi74/toddlerbot
- Jumper README: https://github.com/KingKongRobotics/jumper
- CyberBrick (bộ thu XA004 4 servo): `maker/cyberbrick-car/CLAUDE.md` (theo wiki hãng)

**(thứ cấp)** Không dùng.
