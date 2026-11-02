# Nghiên cứu mô phỏng và demo STLab

Tra cứu web ngày **2026-11-02**; số sao là snapshot GitHub API cùng ngày, có thể thay đổi. Đây là nghiên cứu để Tuan chọn, không cài công cụ, không nối thiết bị thật và không coi mô phỏng là kiểm chứng an toàn.

## 1. Boi canh STLab

- STLab ở Đức Trọng, Lâm Đồng; phục vụ học sinh lớp 3–12. Mô phỏng giúp dạy thuật toán, demo phụ huynh/khách và Open Lab, cho thử tư thế/chuyển động trước khi in hoặc lắp.
- Ràng buộc: Windows 11, máy yếu, không GPU rời mạnh, không model AI local; chỉ dùng giải pháp miễn phí lâu dài (mã nguồn mở hoặc free tier phù hợp). Máy thật chưa benchmark nên hiệu năng đồ họa: TODO.
- Bốn ca mẫu: **line-bot** dò line RCJ Rescue Line (Mega 2560, N20, mảng IR, HC-SR04); **cyberbrick-arm** tay 3 khớp + kẹp servo, CAD tham số; **pump-control** ESP32/RainMaker bật-tắt bơm; **smart-home** ESP32/ESPHome + Home Assistant. Dự án/đặc tính tại [line-bot README](../../maker/line-bot/README.md), [arm params](../../maker/cyberbrick-arm/freecad/params.json), [pump README](../../maker/pump-control/README.md), [smart-home README](../../maker/smart-home/README.md).
- Mô phỏng pump-control chỉ diễn hoạt trạng thái số/ảo; tuyệt đối không đóng cắt bơm 220 V trong demo phần mềm. Chính sách và trạng thái dự án tại [pump-control CLAUDE](../../maker/pump-control/CLAUDE.md).

## 2. Robot 3D

| Bộ mô phỏng | CPU / Windows | URDF, mesh từ FreeCAD | Cảm biến / controller | Học sinh lớp 6–9, sa bàn RCJ |
|---|---|---|---|---|
| **Webots** | Vật lý chạy CPU; có bản Windows native. Viewport cần OpenGL; máy yếu cần thử scene nhỏ. | Có đường nhập URDF; xuất mesh từ FreeCAD/RobotCAD rồi kiểm lại scale, trục và collision. | Camera, distance sensor; IR line cần mô hình hóa reflectance bằng bảng đo/custom logic, siêu âm là sensor ảo. Controller C/C++/Python. | GUI trực quan, mức vừa. Có thể tự dựng đường line/world; không thấy bộ sa bàn RCJ chuẩn sẵn đã xác minh. |
| **Gazebo (gz-sim)** | Chủ yếu Linux; Windows hiện ở trạng thái experimental, có vấn đề runtime đã biết. Không hợp máy/lớp nếu phải dựng ROS 2/WSL2. | URDF thường qua ROS 2/SDFormat; mesh được hỗ trợ nhưng cấu hình plugin và môi trường phức tạp. | Camera, ray/IMU và plugin sensor; controller ROS 2 C++/Python. | Khó cho lớp 6–9; không có sa bàn RCJ tích hợp đã xác minh. |
| **MuJoCo** | CPU nhanh cho articulated dynamics; Windows native và Python. GUI/render dùng OpenGL. | Đọc được URDF; MJCF là định dạng chuẩn để tinh chỉnh. Mesh hiển thị và collision nên tách/giản lược. | Camera, rangefinder/ray; không phải mô phỏng cảm biến HC-SR04/IR phản xạ hoàn chỉnh. Python/C API. | Tốt cho khớp, tiếp xúc và kẹp; cần người hướng dẫn viết model/controller, độ khó vừa-cao. |
| **PyBullet** | Physics chạy CPU; Python và Windows. Mô hình lớn/render vẫn cần đồ họa. | Có loader URDF và mesh. | Camera/raycast; IR/siêu âm cần quy đổi thành ray/logic riêng. Python dễ viết hơn C++. | Dễ bắt đầu bằng script, giao diện dạy học ít liền mạch; arena RCJ phải tự dựng. Issue tracker repo đang đóng để dọn hỗ trợ. |
| **CoppeliaSim Edu** | Có ứng dụng desktop; cần thử hiệu năng trên máy STLab. | Có công cụ nhập robot/URDF và mesh; tính năng, giới hạn theo bản Edu cần đối chiếu license. | Proximity sensor, camera và remote API; controller qua script/Python. | Môi trường dựng robot/scene trực quan, phù hợp demo; bản Edu không phải OSS. Điều khoản cho trung tâm có thu học phí: TODO. |
| **NVIDIA Isaac Sim** | Windows/Linux nhưng yêu cầu tối thiểu hiện công bố RTX 4080, VRAM 16 GB và RAM 32 GB. **Loại** với máy STLab. | URDF/mesh có workflow nhưng không khắc phục được rào cản GPU. | Nhiều sensor/ROS; chi phí tài nguyên quá cao cho mục tiêu hiện tại. | Không đề xuất. |

**Đề xuất:** line-bot dùng **Webots**: dễ dựng mặt sân, đọc sensor và điều khiển Python/C; đưa RobotCAD URDF vào làm phần thân, còn sa bàn RCJ và cảm biến line cần tự hiệu chỉnh. Tay máy dùng **MuJoCo**: hợp bài học khớp/động học/kẹp và có Python; giữ phần CAD/visual mesh riêng với collision đơn giản. Cả hai chỉ dùng CPU cho tính toán vật lý; FPS thực tế còn phụ thuộc GPU tích hợp và scene, cần benchmark trước lớp. RobotCAD trong quy trình STLab đã có xuất URDF; ROS 2/Gazebo cần Linux/WSL2 ([quy trình robotics-cad](../../tools/robotics-cad/CLAUDE.md)). Chữ **CROSS** chưa xác định được vai trò/phiên bản trong tài liệu được phép đọc: TODO.

Sao/license snapshot: Webots **4,743★, Apache-2.0**; gz-sim **1,563★, Apache-2.0**; MuJoCo **16,025★, Apache-2.0**; Bullet/PyBullet **14,840★**, GitHub API báo NOASSERTION nên kiểm notice theo thành phần trước khi phân phối; CoppeliaSim core library **152★**, license API NOASSERTION (không đại diện license ứng dụng); Isaac Sim repo **4,411★**, license API NOASSERTION. Chi tiết link trong [nguồn 1–6](#nguồn).

## 3. Mach dien tu va code

| Công cụ | Mega 2560 / ESP32, linh kiện | Offline / tài khoản / đánh giá |
|---|---|---|
| **Wokwi** | Có mô hình Arduino Mega 2560, ESP32, servo, HC-SR04, relay; Wi-Fi ảo cho ESP32 kết nối MQTT/HTTP. Mảng IR line không phải mô hình cảm biến thật; dùng input ảo hoặc viết chip/custom logic. | Free Community: 0 €, không giới hạn simulation và public project, dành cho dự án mã nguồn mở; private/unlisted, custom library, fast build và VS Code/offline plugin nằm ở gói trả phí. Trình duyệt cần mạng; không coi là chạy offline. Classroom/account theo từng học sinh và điều kiện dùng cho lớp thu học phí: TODO. |
| **SimulIDE CE** | Dự án nói hỗ trợ PIC, AVR, Arduino; xác nhận đúng ATmega2560/Mega và bộ linh kiện cụ thể: TODO. Không thấy ESP32 được hỗ trợ; không thay thế mô phỏng ESP32. | Phần mềm desktop mã GPL-3.0, dùng mạch đơn giản/giáo dục, model không chính xác phân tích điện tử. Có thể chạy cục bộ, nên không cần tài khoản web; bản build Windows hiện hành: TODO. |
| **Tinkercad Circuits** | Hợp bài Arduino nhập môn; Mega 2560/ESP32 và relay/IR tương ứng không xác nhận được từ trang công khai: TODO, không chọn làm nền cho firmware hai dự án này. | Dịch vụ web Autodesk miễn phí; cần xác minh quy trình tài khoản lớp và quyền dùng khi bán khóa học trước khi đưa học sinh vào. Không offline. |
| **QEMU ESP32 của Espressif** | Mô phỏng CPU, memory và một số peripheral của ESP32; ESP-IDF chạy/debug qua `idf.py qemu`. Không mô phỏng mạch dây/servo/relay thật, không phải board Mega 2560. | Có binary Windows x86_64; hợp test firmware/log, không hợp trình diễn mạch tương tác. License/điều kiện phân phối của fork theo repo Espressif cần kiểm trước khi đóng gói. |
| **Proteus** | Mô hình vi điều khiển/phần tử phong phú nhưng giấy phép phần mềm trả phí. | Loại khỏi shortlist theo yêu cầu miễn phí lâu dài; có bản dùng thử không đồng nghĩa free tier dài hạn. |

**Đề xuất lớp:** dùng Wokwi cho mã nguồn công khai, bài Mega/ESP32 và trạng thái MQTT; dùng SimulIDE chỉ làm mạch AVR cơ bản khi Mega được xác nhận. Mỗi bài cần ghi rõ phần được mô phỏng và phần không (đặc biệt cảm biến IR, driver motor, dòng relay). Không dùng kết quả ảo để chốt thông số linh kiện hay an toàn.

## 4. Demo tren web

- **Three.js** (MIT, khoảng **117k★**) hoặc **Babylon.js** (Apache-2.0, khoảng **26k★**) dựng robot/sa bàn 3D ngay trong trình duyệt. Rapier WASM làm vật lý va chạm; cannon-es là lựa chọn JS đơn giản hơn. WebGL/WebGPU và mesh nhiều polygon có thể chậm trên GPU tích hợp; dùng mesh nhẹ, giới hạn scene rồi benchmark. Stars/API và license xem [nguồn 7–10](#nguồn).
- Luồng mesh: FreeCAD xuất mesh nhẹ (glTF/GLB hoặc STL) cho viewport; URDF loader trong Three.js có thể gắn link/joint và mesh, nhưng không chuyển STEP trực tiếp. Mô phỏng động học đơn giản phù hợp trình diễn; không thay physics engine/URDF chính để xác nhận cơ khí. MuJoCo WASM có bindings chính chủ nhưng trạng thái WIP, Windows/browser support còn experimental; chưa chọn làm nền lớp.
- **Blockly** (Apache-2.0, **13,599★**, cập nhật gần thời điểm tra) nhúng editor kéo-thả; block sinh lệnh `tiến`, `rẽ`, `đọc cảm biến`, `đặt góc khớp` cho API robot ảo. Scratch phù hợp lớp nhỏ hơn nhưng repo `scratch-gui` đã chuyển vào monorepo; không nên lấy repo cũ làm nền mới. [Blockly live demo](https://raspberrypifoundation.github.io/blockly/packages/blockly/demos/code/index.html).
- **Ví dụ mở:** [Line-Follower-Computer-Vision-Webots](https://github.com/2black0/Line-Follower-Computer-Vision-Webots) có PID/fuzzy/ML, world Webots và camera; **2★, MIT**, nhưng chạy Webots desktop, push gần nhất 2025-05-04, không phải demo chạy browser/sa bàn RCJ. [Charmbytes robotic-arm-simulator](https://github.com/Charmbytes/robotic-arm-simulator) có Three.js, kinematics và pick-place mini-game; **1★, MIT**, repo mới nhưng chưa thấy trang demo public (GitHub Pages chưa bật). Có thể chạy theo README sau khi người phụ trách kiểm, không coi là giải pháp đã duyệt.
- Chưa xác minh được web demo công khai, cập nhật tốt cho sa bàn line RCJ hay tay cyberbrick-arm cụ thể. Webots Cloud là điểm tham khảo mô phỏng robot trực tuyến, nhưng không tìm thấy project line-bot phù hợp được xác nhận; không dẫn link chung thành demo đã có. Kết luận thực tế: làm một trang STLab nhỏ bằng Three.js + Rapier + Blockly là hướng chủ động; thử Blockly bằng live demo trước, phần robot phải tự dựng.

## 5. Smart home va IoT

- **Wokwi + MQTT:** ESP32 ảo kết nối `Wokwi-GUEST`; docs nêu MQTT/HTTP qua internet ảo. Có thể publish state giả (`pump/state`) và nhận lệnh ảo (`pump/cmd`) về Node-RED/Home Assistant demo. Dùng broker public chỉ với dữ liệu giả, không thông tin khách hoặc credentials.
- **Home Assistant Demo** là giao diện mẫu cho người xem thử dashboard, không phải bản HA lab có thiết bị ESP32 thật. **Node-RED** có flow editor trên browser và lưu flow JSON; phù hợp dựng luồng `nút bấm → MQTT giả → trạng thái đèn/bơm`. Node-RED không tự mô phỏng ESP32/relay.
- **ESPHome** là firmware/configuration tool chứ không phải mô phỏng phần cứng đầy đủ. Cho demo ESPHome, tách firmware thật khỏi giao diện: dùng Wokwi hoặc một MQTT mock để trình bày trạng thái, rồi so sánh YAML/logic mà không flash.
- **Pump-control safety gate:** scene chỉ đổi một entity/đèn “bơm ảo”; không đưa pin tới GPIO, không cấp điện cho relay/contactor, không nối bơm 220 V. Firmware/thiết bị thật và OTA chỉ thao tác theo đồng ý riêng của Tuan. Smart-home hiện là ý tưởng, cấu hình HA/ESPHome chưa chốt ([smart-home CLAUDE](../../maker/smart-home/CLAUDE.md)).

## 6. Ghep vao quy trinh STLab

1. **FreeCAD → URDF/mesh:** dùng RobotCAD xuất link/joint/URDF; mesh visual tách khỏi collision đơn giản. Kiểm trục, đơn vị, tâm khớp và scale trước khi đưa vào Webots/MuJoCo. RobotCAD và quy định không gửi code ra dịch vụ ngoài ghi tại [tools/robotics-cad/CLAUDE.md](../../tools/robotics-cad/CLAUDE.md).
2. **Params → chuyển động:** arm đã có `params.json` và các tư thế/giới hạn khớp dùng cho script dựng model; có thể viết converter đọc cùng JSON, tạo URDF/MJCF keyframe và test góc/tầm với đối chiếu model. File hiện mô tả một số khối massing, không phải bộ đo đã xác nhận cho mọi linh kiện; không tự suy diễn kích thước mới. Line-bot chưa có thông số cảm biến/sa bàn đầy đủ để hiệu chỉnh sensor sim.
3. **Trước khi in:** chạy mô phỏng tư thế/va chạm để phát hiện vấn đề hình học sớm; vẫn chạy gate CAD, prepare-print và test coupon theo quy trình. Mô phỏng không thay kiểm va chạm/lắp thực tế hay kiểm theo slicer.
4. **Video/demo:** tạo screenshot/clip của scene; dùng công cụ Blender 5.2 và `tools/render` sẵn có theo bối cảnh repo. Trang web demo chạy trong Toolhub Flask cục bộ; không cần đưa model/dữ liệu lên cloud.
5. **Tự động hóa:** Claude có thể viết generator world/controller Python, adapter `params.json`, Blockly blocks, script chụp frame và bộ test kết quả; agent/check-runner có thể chạy gate/log theo quy trình. Tuan quyết định chọn công cụ, cấp phép, số liệu phần cứng và duyệt trước mọi tác động thiết bị thật. Phân vai/giới hạn agent tại [docs/model-routing.md](../model-routing.md), an toàn arm tại [cyberbrick-arm CLAUDE](../../maker/cyberbrick-arm/CLAUDE.md), line-bot tại [line-bot CLAUDE](../../maker/line-bot/CLAUDE.md), Toolhub tại [studio CLAUDE](../../studio/CLAUDE.md).

## 7. De xuat xep loi/cong

Ước lượng công là effort dựng demo tối thiểu, không gồm mua phần cứng hay duyệt của Tuan; xếp lợi/công giảm dần. **★ = nên ưu tiên trước.**

| Đề xuất | Mảng | Lợi | Công (giờ) | Rủi ro | Nguồn |
|---|---|---:|---:|---|---|
| ★ Wokwi demo Mega + HC-SR04/servo, thuật toán giả lập đầu vào | Điện/code | Cao | 2–4 | Không phản ánh mảng IR/N20 đúng thực tế; dự án miễn phí phải public/open source | [Wokwi pricing](https://wokwi.com/pricing), [Mega](https://docs.wokwi.com/parts/wokwi-arduino-mega) |
| ★ Webots world line-bot + controller PID Python, so sánh với project mẫu | Robot 3D | Cao | 4–8 | Arena/sensor calibration và hiệu năng máy yếu cần thử | [Webots](https://github.com/cyberbotics/webots), [line sample](https://github.com/2black0/Line-Follower-Computer-Vision-Webots) |
| ★ Blockly + robot line 3D tối giản nhúng Toolhub | Web | Cao | 8–16 | Tự viết physics/UX, WebGL hiệu năng; không có sample RCJ web đạt yêu cầu | [Blockly](https://github.com/RaspberryPiFoundation/blockly), [Three.js](https://github.com/mrdoob/three.js) |
| MuJoCo arm import từ URDF, thử tư thế và kẹp vật ảo | Robot 3D | Cao | 4–8 | Collision/gripper phải hiệu chỉnh; không chứng minh servo thật đúng | [MuJoCo](https://github.com/google-deepmind/mujoco), [params](../../maker/cyberbrick-arm/freecad/params.json) |
| Three.js + Rapier viewer cho arm/line, dùng mesh đã giảm polygon | Web | Vừa | 8–16 | Browser/iGPU, scale và vật lý khác engine desktop | [Three.js](https://github.com/mrdoob/three.js), [Rapier](https://github.com/dimforge/rapier) |
| MQTT mock + Node-RED + dashboard Home Assistant cho pump-control | IoT | Vừa | 3–6 | Chỉ demo logic trạng thái; tuyệt đối không nối tải thật | [Node-RED](https://nodered.org/about/), [HA demo](https://demo.home-assistant.io/) |
| QEMU test logic ESP-IDF không flash board | IoT/code | Vừa | 3–6 | Peripheral không đầy đủ; không thay board/sensor thật | [Espressif QEMU guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/tools/qemu.html) |
| So sánh SimulIDE/Tinkercad cho bài mạch AVR cơ bản | Điện/code | Thấp | 2–4 | Mega/ESP32, account lớp và điều khoản thương mại còn chưa rõ | [SimulIDE](https://github.com/SimulIDE/SimulIDE), [Tinkercad Circuits](https://www.tinkercad.com/circuits) |

## Nguồn

Mọi link dưới đây được truy cập **2026-11-02**; sao/license/push là dữ liệu có thể đổi.

1. [Webots GitHub API: stars/license](https://api.github.com/repos/cyberbotics/webots); [docs cài Windows](https://cyberbotics.com/doc/guide/installation-procedure); [URDF/import](https://cyberbotics.com/doc/guide/imported-robots); [distance sensor](https://cyberbotics.com/doc/reference/distance-sensor).
2. [gz-sim GitHub API](https://api.github.com/repos/gazebosim/gz-sim); [Gazebo install matrix/Windows experimental](https://gazebosim.org/docs/latest/getstarted/).
3. [MuJoCo GitHub API](https://api.github.com/repos/google-deepmind/mujoco); [overview/URDF/Python](https://mujoco.readthedocs.io/en/stable/overview.html); [WASM status](https://github.com/google-deepmind/mujoco/tree/main/wasm).
4. [Bullet/PyBullet GitHub API](https://api.github.com/repos/bulletphysics/bullet3); [PyBullet project/readme](https://github.com/bulletphysics/bullet3).
5. [CoppeliaSim core GitHub API](https://api.github.com/repos/CoppeliaRobotics/coppeliaSimLib); [pricing/license](https://www.coppeliarobotics.com/pricing); thông tin Edu cho chương trình có thu phí cần đối chiếu điều khoản hiện hành.
6. [Isaac Sim GitHub API](https://api.github.com/repos/isaac-sim/IsaacSim); [system requirements](https://docs.isaacsim.omniverse.nvidia.com/latest/installation/requirements.html).
7. [Three.js GitHub API](https://api.github.com/repos/mrdoob/three.js); [Babylon.js GitHub API](https://api.github.com/repos/BabylonJS/Babylon.js); [Rapier](https://github.com/dimforge/rapier); [cannon-es](https://github.com/pmndrs/cannon-es); [URDF loader](https://github.com/gkjohnson/urdf-loaders).
8. [Blockly GitHub API](https://api.github.com/repos/RaspberryPiFoundation/blockly); [live demo](https://raspberrypifoundation.github.io/blockly/packages/blockly/demos/code/index.html); [Scratch migration](https://github.com/scratchfoundation/scratch-editor).
9. [Wokwi plans/free limitations](https://wokwi.com/pricing); [VS Code license](https://docs.wokwi.com/vscode/getting-started); [virtual Wi-Fi/MQTT](https://docs.wokwi.com/guides/esp32-wifi); [Mega](https://docs.wokwi.com/parts/wokwi-arduino-mega); [HC-SR04](https://docs.wokwi.com/parts/wokwi-hc-sr04); [servo](https://docs.wokwi.com/parts/wokwi-servo); [relay](https://docs.wokwi.com/parts/wokwi-relay-module).
10. [SimulIDE CE GitHub](https://github.com/SimulIDE/SimulIDE); [Tinkercad Circuits](https://www.tinkercad.com/circuits); [Proteus licensing/pricing](https://www.labcenter.com/pricing/); [Espressif QEMU/Windows supported](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/tools/qemu.html).
11. [Home Assistant demo](https://demo.home-assistant.io/); [Node-RED about](https://nodered.org/about/); [ESPHome docs](https://esphome.io/).
12. [Webots line-follow sample API](https://api.github.com/repos/2black0/Line-Follower-Computer-Vision-Webots); [arm simulator API](https://api.github.com/repos/Charmbytes/robotic-arm-simulator); [Webots Cloud](https://webots.cloud/).
13. Nguồn dự án STLab đã đọc (đường dẫn từ gốc workspace): `docs/robotics-github-landscape-research.md`, `tools/robotics-cad/CLAUDE.md`, `maker/line-bot/README.md`, `maker/line-bot/CLAUDE.md`, `maker/cyberbrick-arm/freecad/params.json`, `maker/cyberbrick-arm/CLAUDE.md`, `maker/pump-control/README.md`, `maker/pump-control/CLAUDE.md`, `maker/smart-home/README.md`, `maker/smart-home/CLAUDE.md`, `studio/CLAUDE.md`, `docs/model-routing.md`, `tools/robotics-cad/project-template/design/brief.md`, `tools/robotics-cad/workbench/README.md`, `tools/robotics-cad/scripts/build_replay.py`, `tools/render/render.py`.
