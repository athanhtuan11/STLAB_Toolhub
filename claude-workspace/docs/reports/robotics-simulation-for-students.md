# Mô phỏng robotics cho học sinh: lắp ảo → chạy thử → lắp thật

Tra cứu web **2026-11-11**. Số sao, license và ngày push lấy từ GitHub API cùng ngày, có thể thay đổi.
Báo cáo này bổ sung cho [simulation-demo-research.md](simulation-demo-research.md) (2026-11-02), vốn viết cho mục đích *demo*
và đã so sánh các engine Webots, MuJoCo, Gazebo, PyBullet, CoppeliaSim, Isaac cùng Wokwi, SimulIDE và Three.js. Phần trùng không
nhắc lại. Mục đích lần này khác: **học sinh tự lắp linh kiện lên robot ảo, lập trình, chạy mô phỏng, rồi mới lắp ráp thật**.

> Lưu ý: ngày 2026-11-02 Tuan đã quyết "làm thật, không dựng mô phỏng" cho *demo dự án*. Đây là nghiên cứu cho
> *bài học* (bước trước khi lắp), chỉ để Tuan chọn. Không cài đặt gì.

## 1. Tiêu chí

- Học sinh **tự chọn và gắn linh kiện** (bánh, motor, cảm biến) lên robot ảo, không chỉ lập trình robot có sẵn.
- Có vật lý hoặc cảm biến đủ thật để lỗi lắp hiện ra trong mô phỏng: cảm biến đặt sai chỗ, bánh lệch, tay với không tới.
- Chạy trên máy yếu (Windows, GPU tích hợp), ưu tiên chạy ngay trong trình duyệt; miễn phí lâu dài, ưu tiên mã nguồn mở.
- Có lộ trình lên **code thật** (Python hoặc Arduino), gắn với cuộc thi (RCJ) hoặc dự án STLab.

## 2. Nhóm A – Lắp robot ảo + lập trình + mô phỏng

| Nền tảng | Lắp ráp | Lập trình | Chạy ở đâu | Mã nguồn / tình trạng | Hợp cấp |
|---|---|---|---|---|---|
| **GearsBot** (A Posteriori, Singapore) | **Robot Configurator**: thêm Body, tay quay (Arm/Swivel), bộ truyền tịnh tiến (Linear), bánh chủ động/bị động; gắn cảm biến màu, gyro, nam châm… theo cây cha–con; chỉnh khối lượng, ma sát. Lưu robot ra JSON. **World Builder** để dựng sân. | Blockly → tự đổi sang Python, hoặc viết Python trực tiếp (kiểu ev3dev). | Trình duyệt, không cần tài khoản (gears.aposteriori.com.sg). Babylon.js 3D + vật lý. | **GPL-3.0**, 91★, push **2026-11-06**, còn hoạt động. Có bộ giáo trình mở aposteriori-sg tutorials. | Lớp 5–9 (kéo-thả) → lớp 8–12 (Python) |
| **Erebus** (giải RCJ Rescue Simulation chính thức) | **Robot Customisation** (web): đặt tối đa 8 cảm biến khoảng cách, 3 camera, lidar, gyro, GPS, cảm biến màu, IMU, 2 bánh có encoder. Kéo gizmo 3D hoặc nhập số. **Có ngân sách**: mỗi cảm biến có giá, học sinh phải đánh đổi như mua hàng thật. Xuất JSON. | Python (hoặc C++), controller Webots. | Robot builder chạy trên web (robot.erebus.rcj.cloud). Sân và mô phỏng chạy bằng **Webots 2023b** desktop + Python 3.9+. | Repo `robocup-junior/erebus` 14★, push 2026-10-15, bản v26.x. GitHub không ghi license, cần xem trước khi phân phối (`TODO`). Robot builder và world editor (AGPL-3.0) là repo riêng. | Lớp 8–12; có giải thật để thi |
| **Open Roberta Lab** (Fraunhofer IAIS) | Không lắp hình học. Chỉ khai báo cấu hình cổng (cảm biến nào cắm cổng nào). | Khối NEPO; xuất code cho Arduino Uno/Nano/**Mega**, Calliope, micro:bit, EV3… | Trình duyệt. Mô phỏng **2D**, xe 2 bánh. | **Apache-2.0**, 147★, push 2026-11-06. | Lớp 3–7 |
| Webots Robot Designer | Kéo linh kiện, tự khớp vào khe. | – | Web | Apache-2.0 nhưng **ngừng từ 2020**. Loại. | – |
| assemblino.js, Juice, IncrediBots | Lắp kéo-thả + vật lý | JS / – | Node / desktop | Ngừng 2013–2021, ≤ 6★. Loại. | – |
| Critter Engine (trên MuJoCo) | Kéo robot, tay kẹp, vật thể vào cảnh | – | Trình duyệt | Không thấy license. Chưa xác minh. | `TODO` |

## 3. Nhóm B – Ghép mạch ảo trước khi đi dây thật

- **Wokwi** (đã có trong báo cáo cũ, mục 3): ghép Mega 2560/ESP32 với servo, HC-SR04, relay trên breadboard ảo rồi chạy code Arduino thật. Gói free bắt buộc dự án để public.
- **Falstad CircuitJS** (`pfalstad/circuitjs1`, **GPL-2.0**, 2,4k★, push 2026-11-10): mô phỏng mạch tương tự/số ngay trên web, thấy dòng điện chạy. Hợp bài định luật Ohm, LED + điện trở, cầu H, nhưng không có vi điều khiển.
- **Fritzing** (4,9k★, mã nguồn GPL, bản cài đặt có thu phí): vẽ breadboard giống thật, mô phỏng hạn chế. Hợp để in sơ đồ lắp cho học sinh hơn là để chạy thử.
- **Microsoft MakeCode** (`microsoft/pxt`, **MIT**, push 2026-11-11): có bộ mô phỏng micro:bit/Arcade trong trình duyệt. Không lắp linh kiện.

## 4. Nhóm C – Mô phỏng cơ cấu (thanh truyền, tay kẹp, khớp)

- **PMKS+** (WPI, pmksplus.com, repo `PMKS-Web/PMKS`, 29★, push 2026-11-10): học sinh đặt khớp quay/trượt, nối thanh rồi xem chuyển động, vận tốc và lực của cơ cấu phẳng. Hợp với tay kẹp, cơ cấu 4 khâu, pushrod. Dự án tự nhận là mã nguồn mở nhưng GitHub không ghi license (`TODO`). Hạn chế đã biết: dựng theo tọa độ khớp thì dễ, nhập theo chiều dài thanh + góc thì khó.
- MuJoCo hoặc Webots (báo cáo cũ) dùng cho tay máy 3D; mức khó vừa–cao, cần giáo viên dựng model sẵn.

## 5. Ghép vào STLab – lộ trình đề xuất

| Bước | Lớp 3–6 | Lớp 6–9 | Lớp 9–12 / đội thi |
|---|---|---|---|
| Lắp ảo | (bỏ qua) | **GearsBot Configurator**: gắn bánh, cảm biến màu, tay | **Erebus Customisation**: chọn cảm biến theo ngân sách |
| Ghép mạch | Wokwi mẫu có sẵn | Wokwi: Mega + HC-SR04 + servo | Wokwi / CircuitJS cho mạch công suất |
| Lập trình + chạy | Open Roberta 2D | GearsBot: khối → Python | Erebus: Python trên Webots |
| Cơ cấu | – | PMKS+: tay kẹp 4 khâu | PMKS+ / MuJoCo |
| Lắp thật | Bộ kit | line-bot, card-coding-robot | line-bot RCJ, tay máy |

**Khuyến nghị:** thử **GearsBot** trước. Nó gom đủ "lắp → lập trình → chạy" trong trình duyệt, không cần cài đặt, mã nguồn mở và còn được duy trì, nên hợp với phòng máy yếu.
- **Đánh đổi:** robot là khối hình học đơn giản, không nạp được CAD STLab; cảm biến là mô hình lý tưởng.
- **Hệ quả:** học sinh học được *bố trí* (cảm biến màu đặt trước hay sau trục bánh, cách thêm bánh tì) và *thuật toán*, nhưng không học được dung sai hay điện thật.

Với đội thi RCJ, dùng **Erebus**. Ngân sách cảm biến dạy được tư duy chọn linh kiện. Đánh đổi: cần cài Webots 2023b trên mỗi máy, và đây là Rescue *Maze* chứ không phải Rescue *Line* như line-bot (`TODO`: chưa thấy bộ mô phỏng chính thức cho Rescue Line).

**Nói rõ với học sinh và phụ huynh:** mô phỏng không thay được lắp thật. Cảm biến IR thật bị ánh sáng phòng làm nhiễu, motor N20 mỗi con một khác, khe in 3D lệch. Bài nên có bước "so sánh ảo với thật": chạy cùng một chương trình trên robot thật rồi ghi lại khác biệt.

## 6. Việc Tuan cần quyết

1. Có đưa mô phỏng vào giáo án không (khác quyết định 2026-11-02, vốn chỉ áp cho demo dự án)?
2. Nếu có: thử GearsBot trên 1 máy phòng lab (đo FPS, `TODO`) với 1 bài mẫu "xe dò line + cảm biến màu".
3. Đội RCJ: có muốn thi thêm hạng Rescue Simulation (Erebus) không?

## Nguồn (truy cập 2026-11-11)

1. GearsBot: [repo](https://github.com/QuirkyCort/gears), [wiki Robot Configurations](https://github.com/QuirkyCort/gears/wiki/Robot-Configurations), [World Builder](https://github-wiki-see.page/m/QuirkyCort/gears/wiki/World-Builder), [giáo trình Robot Configurator](https://aposteriori-sg.github.io/tutorials/17-Robotics-with-Gearsbot/40-Mechanical-Design-II/15-Robot-Configurator.html), [bản chạy web](https://gears.aposteriori.com.sg), [LICENSE GPL-3.0](https://github.com/QuirkyCort/gears/blob/master/LICENSE).
2. Erebus: [RCJ Rescue Simulation](https://junior.robocup.org/rcj-rescue-sim/), [repo erebus](https://github.com/robocup-junior/erebus), [robot customisation](https://github.com/robocup-junior/erebus-robot-customisation) / [web](https://robot.erebus.rcj.cloud), [RCJ Australia 2026 demo](https://www.robocupjunior.org.au/2026-rescue-simulation/).
3. Open Roberta: [Wikipedia](https://en.wikipedia.org/wiki/Open_Roberta), [Open Roberta Lab](https://roberta-home.de/en/lab), [GitHub](https://github.com/OpenRoberta), [Fraunhofer – Rescue Online Simulation](https://publica.fraunhofer.de/handle/publica/496178).
4. Đã loại: [Webots robot-designer](https://github.com/cyberbotics/robot-designer), [assemblino.js](https://github.com/omni360/assemblino.js), [Juice](https://github.com/natewaddoups/juice), [IncrediBots](https://sourceforge.net/projects/incredibots/), [Critter Engine](https://critter-website.pages.dev/).
5. Mạch: [CircuitJS](https://github.com/pfalstad/circuitjs1), [Fritzing](https://github.com/fritzing/fritzing-app), [MakeCode pxt](https://github.com/microsoft/pxt); Wokwi xem báo cáo cũ.
6. Cơ cấu: [PMKS+ (WPI)](https://digital.wpi.edu/concern/etds/9880vv46s), [repo PMKS-Web/PMKS](https://github.com/PMKS-Web/PMKS), [PMKS gốc (Oregon State)](https://design.engr.oregonstate.edu/node/16).
