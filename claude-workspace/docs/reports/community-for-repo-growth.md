# Nguồn cộng đồng để phát triển repo STLab (4 mảng chưa nghiên cứu)

Ngày: 2026-10-26 · Người yêu cầu: Tuan · Trạng thái: **nghiên cứu, chưa cài/chưa ghim**

## Cách làm
- Tuan: "codex + agy quá nhiều, dùng nó tìm cộng đồng". Tra web bằng **Codex** (ChatGPT Free, `ask-gpt`) và **Gemini**
  (agy, `ask-gemini`), mỗi bên 2 mảng, song song. Chỉ gửi mô tả kỹ thuật chung (không dữ liệu khách/phụ huynh).
- **Mọi repo GitHub đã kiểm lại bằng GitHub API** (sao, lần push gần nhất, license, archived) ngày 2026-10-26; GitLab
  bằng GitLab API. Số trong bảng là số API, không phải số model đưa.
- Model free sai ở: 1 repo **không tồn tại** (`OttoDIY/DIY-starter-kit` – Gemini bịa đường dẫn; tổ chức OttoDIY có thật),
  **license sai** 2 repo (Thor: Gemini ghi GPL-3.0, thật CC-BY-SA-4.0; sethfischer/rover: ghi GPL-3.0, thật MIT), 1 số đo
  linh kiện không nguồn (trục 030 "~1,5 mm" – **bỏ**, số đo lấy theo STEP hãng như cũ). Link MakerWorld: Gemini chỉ đưa
  link tìm kiếm, Codex đưa link cụ thể nhưng chưa mở kiểm → `TODO`.
- Quy tắc lọc như `docs/COMMUNITY.md`: còn cập nhật (push 2026), ghi license (phi thương mại – chỉ ghi chú).

## 1. Kiểm model + slicer tự động (tools/robotics-cad)
| Repo | ★ | Push | License | Làm gì | Dùng cho STLab | Kết luận |
|---|---|---|---|---|---|---|
| [sunnyday-technologies/CADCLAW](https://github.com/sunnyday-technologies/CADCLAW) | 20 | 2026-10-14 | MIT | Kiểm lắp ráp STEP: va chạm, kề nhau, kích thước, hướng, cộng dồn dung sai; xuất trình tự lắp | So với `assembly_paths.py` + T9Assemble (mình tự viết 2026-10-26); lấy ý cộng dồn dung sai | **Đề xuất đọc** |
| [estampo/estampo](https://github.com/estampo/estampo) | 18 | 2026-08-30 | Apache-2.0 | Pipeline in tái lập: nạp → xếp bàn → slice (Bambu/Orca CLI) → đóng gói `.gcode.3mf` | So với `slice.py`/`prepare-print.py`; ý ghim profile + lưu đầu ra | **Đề xuất đọc** |
| [KD5RYN/b123d-print](https://github.com/KD5RYN/b123d-print) | 1 | 2026-10-25 | MIT | Kiểm in (build123d): chồng chi tiết lắp, nhô, cầu, vách mỏng, khe động; **mẫu thử khe/cầu** | Ý mẫu thử khe (như bộ chốt thử Ø4,6–4,9 đã làm) | Để sau (repo rất mới, 1 ★) |
| [jokroese/freecad-code-workbench](https://github.com/jokroese/freecad-code-workbench) | 8 | 2026-08-09 | LGPL-2.1 | CadQuery/build123d trong FreeCAD, có test headless FreeCAD trong CI | Mẫu chạy test FreeCAD headless trong CI (repo chỉ test trên máy) | Để sau |
| [dooosp/freecad-automation](https://github.com/dooosp/freecad-automation) | 6 | 2026-10-18 | MIT | Tự động FreeCAD: kiểm model, báo cáo, FEM, TechDraw | Tham khảo báo cáo kiểm | Để sau |
| [OrcaSlicer/OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer) | 16 134 | 2026-10-26 | AGPL-3.0 | Slicer có CLI + tự xoay hướng in | Đã có trong nghiên cứu cũ; chỉ dùng nếu Bambu Studio CLI thiếu | Giữ như cũ |
| [ExaltedTrou6/printable-mcp](https://github.com/ExaltedTrou6/printable-mcp) · [sksat/bambu-rs](https://github.com/sksat/bambu-rs) · [khromov/stl-fit](https://github.com/khromov/stl-fit) | 1 · 4 · 6 | 2026 | MIT · MIT · **không license** | MCP in OpenSCAD · điều khiển máy Bambu · xoay STL cho vừa bàn | Ít liên quan / không điều khiển máy in (chính sách) | Loại |

## 2. Hệ sinh thái CyberBrick (pushrod-arm, cyberbrick-car)
| Repo | ★ | Push | License | Làm gì | Dùng cho STLab | Kết luận |
|---|---|---|---|---|---|---|
| [CyberBrick-Official/CyberBrick_Controller_Core](https://github.com/CyberBrick-Official/CyberBrick_Controller_Core) | 236 | 2026-06-09 | NOASSERTION (`TODO` đọc file LICENSE) | MicroPython chính hãng XA003 (app RC, đường cong kênh) | Đọc trước khi viết điều khiển riêng (Tuan đang cấu hình bằng app) | **Đề xuất ghim** |
| [Shen-Ming-Hong/singular-blockly](https://github.com/Shen-Ming-Hong/singular-blockly) | 12 | 2026-10-26 | Apache-2.0 | Lập trình khối trong VS Code, sinh MicroPython cho CyberBrick | **Dạy học sinh nhỏ** lập trình xe/tay máy trước khi viết code | **Đề xuất thử** |
| [rotorman/CyberBrick_ESPNOW](https://github.com/rotorman/CyberBrick_ESPNOW) | 20 | 2026-10-03 | GPL-3.0 | Firmware ESP-NOW cho XA003/XA004 → dùng tay điều khiển RC (EdgeTX/ELRS) | Nếu tay máy 4 bậc khó điều khiển bằng app | Để sau |
| [unbug/CyberClaw](https://github.com/unbug/CyberClaw) | 8 | 2026-03-20 | MIT | Python/agent AI điều khiển CyberBrick | Lớp nâng cao: điều khiển tay máy từ máy tính | Để sau |
| [shuwn/CyberBrick-V7RC-Controller](https://github.com/shuwn/CyberBrick-V7RC-Controller) | 9 | 2025-08-12 | NOASSERTION | App V7RC qua Wi-Fi | Không cập nhật 2026 | Loại |

MakerWorld (cần Tuan mở xem – `TODO`, chưa kiểm link/license; file MakerWorld thường không cho remix thương mại):
Build-A-Droid (`makerworld.com/en/models/1549117`), Jimny RC (`.../1604771`) do Codex đưa; Gemini gợi ý tìm
"Cyberbrick Excavator", "Cyberbrick Skid Steer", "GT-RC Cyberbrick" (xe Ackermann + 2 hộp số – gần cyberbrick-car),
"L-ONE Desktop Robotic Arm". Wiki hãng: `wiki.bambulab.com/en/cyberbrick` (sơ đồ cổng XA004).

## 3. ESP32: máy bơm, pin mặt trời, nhà thông minh (pump-control, solar-battery, smart-home)
| Repo | ★ | Push | License | Làm gì | Dùng cho STLab | Kết luận |
|---|---|---|---|---|---|---|
| [syssi/esphome-jk-bms](https://github.com/syssi/esphome-jk-bms) | 1 040 | 2026-10-25 | Apache-2.0 | Đọc/điều khiển JK-BMS qua UART/BLE → Home Assistant | solar-battery: **chỉ đọc** trước | **Đề xuất** (nếu dùng JK-BMS) |
| [espressif/arduino-esp32 › RainMaker examples](https://github.com/espressif/arduino-esp32/tree/master/libraries/RainMaker/examples) | 17 626 | 2026-10-26 | LGPL-2.1 | Ví dụ RainMaker chính hãng (cấp phép Wi-Fi, OTA) | Đối chiếu firmware pump-control 1.1.2 | **Đề xuất đọc** |
| [ElectroIoT/Smart-Submersible-Pump-Controller-ESPHome](https://github.com/ElectroIoT/Smart-Submersible-Pump-Controller-ESPHome) | 4 | 2026-09-17 | MIT | Bơm ESPHome + PZEM-004T, **ngắt chạy khô theo dòng** | Ghi chú cho bản sau (Tuan đã bỏ bảo vệ motor ở bản khách) | Để sau |
| [g1ibby/water-tank-monitor](https://github.com/g1ibby/water-tank-monitor) | 11 | 2026-04-06 | MIT | Đo mực bồn không tiếp xúc (ESPHome) | Bài học cảm biến mực nước, khóa liên động | Để sau |
| [mp-se/victron-receiver](https://github.com/mp-se/victron-receiver) | 11 | 2026-04-22 | NOASSERTION | Nhận BLE Victron → MQTT/HA | Chỉ khi dùng thiết bị Victron | Để sau |
| [micropython/micropython](https://github.com/micropython/micropython) (tutorial ESP32) | 22 154 | 2026-10-26 | NOASSERTION (repo MIT) | Hướng dẫn ESP32 chính thức | Tài liệu nền cho lớp MicroPython (cũng là ngôn ngữ CyberBrick) | Tham khảo |
| AdejireA/solar-energy-monitoring-system · Future-EagleIoT/ESP32-Smart-Plant-Watering · galileoisonline/esp32-workshop · gavinjackson/electronics-lessons · holoduke/JKBMS · Niran078/Victron_VE-Direct… | 0–6 | 2026 | MIT/Apache/không rõ | Ví dụ nhỏ (INA226, tưới cây RainMaker, khóa ESP32 5 bài…) | Ý tưởng bài học | Để sau (rất ít người dùng; 3 repo không license) |

**An toàn:** các repo bơm/BMS có phần đấu điện lưới 220 V và pin Li-ion – học sinh chỉ làm phía điều khiển điện áp thấp;
đấu contactor/mains do thợ điện có chuyên môn; BMS chỉ đọc, không cho đổi cấu hình/MOSFET khi chưa có người lớn.

## 4. Dạy học + tài liệu lắp ráp (ASSEMBLY.md, giáo trình)
| Nguồn | ★ | Cập nhật | License | Làm gì | Dùng cho STLab | Kết luận |
|---|---|---|---|---|---|---|
| [GitBuilding](https://gitlab.com/gitbuilding/gitbuilding) | 29 (GitLab) | 2026-09-30 | GPL-3.0 | Tài liệu lắp ráp phần cứng mở dạng Markdown + BOM tự đồng bộ | So với `ASSEMBLY.md` + `assembly-pdf.py` (đang tự viết) | **Đề xuất đọc** |
| [nophead/NopSCADlib](https://github.com/nophead/NopSCADlib) | 1 657 | 2026-09-24 | GPL-3.0 | Thư viện OpenSCAD có script tự sinh BOM + ảnh từng bước lắp | Ý tưởng tự sinh ảnh bước lắp (đã có trong COMMUNITY.md) | Giữ tham khảo |
| [nasa-jpl/open-source-rover](https://github.com/nasa-jpl/open-source-rover) | 9 732 | 2026-10-22 | Apache-2.0 | Rover 6 bánh, BOM + hướng dẫn lắp chi tiết | Chuẩn mẫu tài liệu lắp ráp + BOM | **Đề xuất đọc** |
| [OttoDIY](https://github.com/OttoDIY) (tổ chức; vd. `OttoDIY/blockly` 139 ★, push 2026-08-14, GPL-2.0) | – | 2026 | GPL/MIT tùy repo | Robot giáo dục in 3D + lập trình khối | Nhịp bài học 1–2 giờ cho trẻ | Để sau |
| [AngelLM/Thor](https://github.com/AngelLM/Thor) | 1 628 | 2025-05-09 | **CC-BY-SA-4.0** | Tay máy 6 bậc, nguồn FreeCAD | Đã có trong nghiên cứu cũ; không cập nhật 2026 | Giữ như cũ |
| [alekssadowski95/freecad-beginners-handbook](https://github.com/alekssadowski95/freecad-beginners-handbook) | 11 | 2026-07-16 | **không license** | Sổ tay FreeCAD cho người mới | Không được dịch/phát hành lại khi chưa có license | Loại (hỏi tác giả nếu cần) |
| [gumyr/bd_warehouse](https://github.com/gumyr/bd_warehouse) · [CameronBrooks11/snapfit-scad](https://github.com/CameronBrooks11/snapfit-scad) · [sethfischer/rover](https://github.com/sethfischer/rover) | 113 · 3 · 7 | 2026 · 2026 · 2025 | Apache · MIT · MIT | Thư viện build123d · khớp snap-fit · rover CadQuery | Công thức snap-fit nếu cần khớp không vít | Để sau |
| [JMG1/ExplodedAssembly](https://github.com/JMG1/ExplodedAssembly) | 141 | 2024-02-24 | LGPL-2.1 | Hình nổ trong FreeCAD | Không cập nhật | Loại |
| printables.com/education · kevsrobots.com (SMARS) | – | – | CC (theo từng bài) | Bài học in 3D, robot snap-fit | Ý tưởng giáo trình | `TODO` xem tay |

## 5. Đề xuất (xếp theo lợi/công – chờ Tuan chọn, không tự cài)
| # | Việc | Lợi | Công | Đánh đổi |
|---|---|---|---|---|
| 1 | Ghim `CyberBrick_Controller_Core` vào `community/` (đọc LICENSE trước) | Có mã MicroPython chính hãng để viết điều khiển riêng cho xe/tay máy | Thấp | License NOASSERTION – chỉ dùng nội bộ tới khi rõ |
| 2 | Thử `singular-blockly` cho lớp nhỏ | Học sinh lập trình CyberBrick bằng khối trong VS Code | Thấp (1 buổi thử) | Extension mới (12 ★); kiểm có chạy với XA003 thật |
| 3 | Đọc CADCLAW + estampo, so với `assembly_paths.py`/`slice.py` → báo cáo "lấy gì" | Bớt tự viết công cụ kiểm/slice | Vừa | Cả hai còn nhỏ (≤ 20 ★); CADCLAW chạy trên STEP, không đọc thẳng FCStd |
| 4 | Đọc GitBuilding + open-source-rover → cải tiến mẫu ASSEMBLY | Tài liệu lắp chuẩn cộng đồng, BOM tự đồng bộ | Vừa | GitBuilding là công cụ riêng (Python, GPL); có thể chỉ học cấu trúc thay vì chuyển hẳn |

## 6. Chưa xác nhận (TODO)
- License thật của CyberBrick_Controller_Core và micropython (API ghi NOASSERTION).
- Link/license các mẫu MakerWorld; số đo linh kiện từ cộng đồng (chỉ dùng khi có ảnh đo/nguồn).
- singular-blockly có hỗ trợ đủ cổng XA004 (M1/M2, S1–S4) không.
