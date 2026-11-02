---
task: simulation-demo-research
cwd: .
allow: ["docs/reports/simulation-demo-research.md"]
read: ["docs/robotics-github-landscape-research.md", "tools/robotics-cad/CLAUDE.md", "maker/line-bot", "maker/cyberbrick-arm/freecad", "maker/pump-control", "maker/smart-home", "studio/CLAUDE.md", "docs/model-routing.md"]
gate: 'python tools/delegate/check_report.py docs/reports/simulation-demo-research.md "## 1. Boi canh STLab" "## 2. Robot 3D" "## 3. Mach dien tu va code" "## 4. Demo tren web" "## 5. Smart home va IoT" "## 6. Ghep vao quy trinh STLab" "## 7. De xuat xep loi/cong" --max-todo 8 --min-files 6'
ky_nang: [bao-cao]
timeout_min: 45
max_rounds: 3
executor: copilot
---

# Mục tiêu
Viết `docs/reports/simulation-demo-research.md` (tiếng Việt có dấu, ≤ 260 dòng): nghiên cứu **xây dựng chương trình mô phỏng /
giả lập để demo** cho STLab (Tuan 2026-11-02, chọn cả 4 mảng). Chỉ ĐỌC + tra web; **không cài, không sửa gì** – Tuan quyết
rồi mới làm ("nghiên cứu trước, cải tiến sau").

# Bối cảnh bắt buộc (đọc file trong `read`)
- STLab: trung tâm STEAM (Đức Trọng, Lâm Đồng), học sinh lớp 3–12; demo cho phụ huynh/khách, Open Lab, lớp robot.
- Máy: Windows 11, **máy yếu, không GPU rời mạnh, không model AI local**. Chỉ trả Claude Pro – công cụ phải **miễn phí**
  (open source hoặc gói free dùng được lâu dài). Ưu tiên nhiều sao + còn cập nhật; license ghi chú (phi thương mại, không chặn).
- Dự án thật để demo: `maker/line-bot` (xe dò line RCJ Rescue Line, Mega 2560, N20, mảng IR, HC-SR04), `maker/cyberbrick-arm`
  (tay 3 khớp servo + kẹp, khung tham số FreeCAD, `params.json`), `maker/pump-control` (ESP32 + RainMaker bật/tắt bơm),
  smart home. Model CAD dựng bằng FreeCAD script; có `tools/render` (Blender 5.2); Toolhub là web Flask (`studio/`).

# Mục bắt buộc (đúng tiêu đề)
- `## 1. Boi canh STLab`: mục đích demo (dạy, bán khóa học, thử trước khi in/lắp), ràng buộc máy/chi phí, 4 dự án mẫu.
- `## 2. Robot 3D`: so sánh Webots, Gazebo (gz-sim), MuJoCo, PyBullet, CoppeliaSim (edu), Isaac (chỉ để loại vì GPU) …:
  chạy CPU được không, Windows native, nhập URDF/mesh từ FreeCAD (RobotCAD/CROSS – xem tools/robotics-cad/CLAUDE.md),
  cảm biến ảo (IR line, siêu âm, camera), viết controller bằng Python/C, độ khó cho lớp 6–9, sa bàn RCJ có sẵn không.
  Đề xuất 1 lựa chọn cho line-bot và 1 cho tay máy (có thể trùng).
- `## 3. Mach dien tu va code`: Wokwi (gói free: giới hạn gì, chạy offline/VS Code?), SimulIDE, Tinkercad Circuits, QEMU ESP32,
  Proteus (loại nếu trả phí) – hỗ trợ Mega 2560/ESP32, linh kiện có sẵn (servo, HC-SR04, relay, IR), dùng được trong lớp
  không cần tài khoản cho từng HS?
- `## 4. Demo tren web`: mô phỏng chạy trong trình duyệt nhúng vào Toolhub/website: Three.js/Babylon.js + vật lý (Rapier,
  cannon-es, MuJoCo WASM), Blockly/Scratch để HS lập trình kéo thả điều khiển robot ảo; ví dụ dự án mở có sẵn (sa bàn dò line
  web, tay máy web) – sao, license, demo link.
- `## 5. Smart home va IoT`: giả lập thiết bị ESP32/MQTT (Wokwi + MQTT, Home Assistant demo mode, Node-RED, ESPHome
  mô phỏng), demo pump-control không cần bơm 220 V thật (an toàn).
- `## 6. Ghep vao quy trinh STLab`: đường đi FreeCAD → (URDF/mesh) → bộ mô phỏng; dùng `params.json` để mô phỏng trước khi in;
  quay video demo (HyperFrames/Blender đã có); việc nào Claude/agent tự động được.
- `## 7. De xuat xep loi/cong`: bảng ≤ 12 dòng: đề xuất | mảng | lợi (cao/vừa/thấp) | công (giờ) | rủi ro | nguồn.
  Xếp lợi/công giảm dần; đánh dấu 2–3 việc nên làm trước.

# Quy tắc
- Mỗi khẳng định về công cụ bên ngoài (giá, giới hạn gói free, OS hỗ trợ, license, số sao, commit gần nhất) phải có link
  nguồn gốc + ngày truy cập 2026-11-02. Không chắc → `TODO`. Không bịa phiên bản/giá.

# Tiêu chí PASS
Gate exit 0.
