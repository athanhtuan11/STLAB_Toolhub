# Quản lý nguồn cộng đồng

Nguồn sự thật về điểm ghim là `community/pins.tsv`; bảng dưới đây là bản để đọc.
Sau mỗi lần `apply`/`rollback`, cập nhật cột "Ghim" và "Kiểm tra".

## Nguồn đang dùng

| Repo | Ghim | License | Tin cậy | Kiểm tra | Dùng cho |
|---|---|---|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | `dbd4588f9e10` | Apache-2.0; docx/pdf/pptx/xlsx là source-available | **Chính thức** (allowlist) | 2026-10-21 | `docx`, `pptx`, `xlsx` → stlab |
| [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | `9f9f5d9faec1` (sparse: `.claude`, `best-practice`, `tips`) | MIT | Cộng đồng | 2026-10-21 | Mẫu cấu trúc `.claude`/CLAUDE.md (chỉ đọc) |
| [mattpocock/skills](https://github.com/mattpocock/skills) | `v1.3.1` (`24fe0ef7737e`) | MIT | Cộng đồng | 2026-10-21 | `grill-me`, `handoff`, `diagnosing-bugs`, `research` (~/.claude); `pr` (oss-toolkit) |
| [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) | `408d3c9eee2d` | MIT | Cộng đồng | 2026-10-21 | Agent `embedded-systems`, `iot-engineer`, `cpp-pro`, `python-pro` → maker |
| [homeassistant-ai/skills](https://github.com/homeassistant-ai/skills) | `68f2690ff868` | MIT | Cộng đồng | 2026-10-21 | `home-assistant-best-practices` → smart-home |
| [homeassistant-ai/ha-mcp](https://github.com/homeassistant-ai/ha-mcp) | `v8.7.0` (`a96752286be1`) | MIT | Cộng đồng | 2026-10-21 | MCP Home Assistant (**chưa bật**) |
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | `v0.1.27` (`78bf0230a033`) | MIT | Cộng đồng | 2026-10-21 | MCP FreeCAD → prompt-library |
| GrabCAD – Tower Pro MG90S micro servo (snapshot 3, STEP) | file zip Tuan tải 2026-10-23 (đăng nhập GrabCAD) → `community/grabcad/towerpro-mg90s/` | Điều khoản GrabCAD (phi thương mại) – xem lại khi thương mại | Cộng đồng (không có SHA) | 2026-10-23: đo STEP khớp kích thước hãng công bố 32,2 × 12,15 × 28,3 | Servo lái MG90S → maker/cyberbrick-car |
| [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | `5a3618fccb2d` | MIT | Cộng đồng | 2026-10-21 | MCP Blender → prompt-library |
| [YujxZJCN/teaching-skills](https://github.com/YujxZJCN/teaching-skills) | `fd0c486e61cb` | MIT | Cộng đồng (ít người dùng) | 2026-10-21 | `lesson-builder`, `lab-forge` → stlab |
| [GarethManning/education-agent-skills](https://github.com/GarethManning/education-agent-skills) | `6bbbce418f82` | **CC BY-SA 4.0** | Cộng đồng | 2026-10-21 | `backwards-design-unit-planner`, `criterion-referenced-rubric-generator` → stlab |
| [drfenixion/freecad.robotcad](https://github.com/drfenixion/freecad.robotcad) | `v12.10.3` (`80c483bcccca`) | LGPL-2.1 | Cộng đồng, 454★ | 2026-10-21 | Workbench RobotCAD (URDF, khớp, quán tính) → FreeCAD Mod |
| [looooo/freecad.gears](https://github.com/looooo/freecad.gears) | `83ec154b1925` | GPL-3.0 | Cộng đồng, 363★ | 2026-10-21 | Workbench bánh răng → FreeCAD Mod |
| [shaise/FreeCAD_SheetMetal](https://github.com/shaise/FreeCAD_SheetMetal) | `cbf6595b68ad` (0.8.26) | LGPL-2.1 | Cộng đồng, 349★ | 2026-10-21 | Workbench tấm/bracket → FreeCAD Mod |
| [shaise/FreeCAD_FastenersWB](https://github.com/shaise/FreeCAD_FastenersWB) | `V0.5.67-beta` (`fddd07af422b`) | GPL-2.0-or-later | Cộng đồng | 2026-10-24 (trước đó cài bằng Addon Manager, không ghim) | Workbench vít/đai ốc/insert; **bảng kích thước ISO** dùng cho lỗ vít → FreeCAD Mod |
| Datasheet/bản vẽ kích thước linh kiện (5 file) | SHA-256 trong `tools/robotics-cad/library/datasheet-sources.tsv` → `community/datasheets/` | Theo từng hãng (Raspberry Pi, Arduino CC-BY-SA-4.0 `TODO` xác nhận cho PDF, Handsontec/TowerPro không ghi) | Chính hãng, trừ Handsontec (đại lý) | 2026-10-24 | Kích thước lắp ghép trong `components.yaml` (xem `docs/component-dimension-sources.md`) |
| [FreeCAD/FreeCAD-library](https://github.com/FreeCAD/FreeCAD-library) | `f5ca01cdcaa2` (sparse, `freecad-library.sparse`) | **CC-BY 3.0** (ghi công) | Chính thức (tổ chức FreeCAD), 2k★ | 2026-10-21 | Thư viện linh kiện robotics (~950 MB) + macro PartsLibrary |
| [arduino/docs-content](https://github.com/arduino/docs-content) | `b12ffb3a317c` (sparse: chỉ `*-step.zip` của 5 board + 14 Modulino, `arduino-docs-content.sparse`, ~9 MB) | **CC-BY-SA-4.0** | **Chính hãng** (tổ chức Arduino) | 2026-10-22 | STEP UNO R4 WiFi, UNO Q, Nano ESP32, Nano R4, GIGA R1, Modulino → giải nén bằng `tools/robotics-cad/library/boards.py` |
| [espressif/kicad-libraries](https://github.com/espressif/kicad-libraries) | `3.2.1` (`1dfc3110895c`, sparse: `3dmodels/`) | **CC-BY-SA-4.0** + miễn trừ cho thiết kế (như thư viện KiCad) | **Chính hãng** (Espressif), 1,4k★ | 2026-10-22 | 29 STEP module ESP32/S2/S3/C3/C5/C6/H2 (không có board DevKit) |
| [anthropics/skills](https://github.com/anthropics/skills) – `frontend-design` | cùng bản ghim `dbd4588f9e10` | Apache-2.0 | Chính thức (Anthropic) | 2026-10-24: chỉ là SKILL.md, không chạy mã | Skill thiết kế giao diện → `~/.claude/skills` (bước 0 "Giao diện") |
| [Be Vietnam Pro](https://github.com/bettergui/BeVietnamPro) (Google Fonts v12) | 6 file woff2 (400/600/700 × latin/vietnamese) tải 2026-10-24 → `studio/toolhub/static/fonts/` | **OFL-1.1** (kèm `OFL.txt`) | Cộng đồng Việt, Google Fonts | 2026-10-24 | Font Toolhub, chạy offline |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | `613efc8c21d9` (sparse: `skills/freecad-scripts`) | MIT | Tổ chức GitHub, 40k★ | 2026-10-21 | Skill `freecad-scripts` → `~/.claude/skills` (dùng chung) |
| [midasmatterhorn/artcraft-skills](https://github.com/midasmatterhorn/artcraft-skills) | `aa35c244d115` (sparse: `filmcraft/`, `lightcraft/`) | MIT | Cộng đồng, 30★ (dẫn chứng theo mã nguồn FilmCraft 0.9.0 @4a69a03, LightCraft 0.9.1 @4f0b110) | 2026-10-21 | Skill `filmcraft`, `lightcraft` → `~/.claude/skills` |
| [abpy/FujifilmCameraProfiles](https://github.com/abpy/FujifilmCameraProfiles) | `b5a1f16abfb2` | **Không có file LICENSE** | Cộng đồng, 588★ | 2026-10-21 | LUT Fuji film sim. Chỉ `provia conversion luts/` áp thẳng lên JPEG được (Classic Neg, Nostalgic Neg); `cube lut/` cần RAW + profile tuyến tính |
| [cedeber/hald-clut](https://github.com/cedeber/hald-clut) | `3b3180f82d4d` (sparse: Film Simulation/Color/{Fuji,Kodak}, Fujifilm XTrans III) | Repo GPL-3.0; bộ RawTherapee Film Simulation **CC BY-SA 4.0** (Pat David, Pavlov Dmitry, Michael Ezra) | Cộng đồng, 324★ | 2026-10-21 | HaldCLUT phim (Portra, 400H…) → `photo-ai/scripts/luts.py` đổi sang `.cube`. **Không lấy** `Apple/`, `Pixelmator Pro/` (trích từ app thương mại). XTrans III chỉ dành cho RAW trung tính |
| [peva3/Lightroom-Presets](https://github.com/peva3/Lightroom-Presets) | `f22f4d8057aa` | MIT | Cộng đồng, 99★, repo mới (2026-05) | 2026-10-21 | 445 preset XMP Lightroom (chỉ `.xmp` + `.md`) → LightCraft `render --settings x.xmp` (áp được) |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | `6c67adcd9cdb` (@remotion/skills 4.0.538) | **Không có file LICENSE**; Remotion License của monorepo (free cá nhân/công ty ≤ 3 NV) | **Chính hãng** (tổ chức Remotion), 5,6k★ | 2026-10-24 | Skill `remotion-best-practices` (router, chứa đủ 11 skill con) → `~/.claude/skills`: video motion graphics bằng React |
| [antonbabenko/deliberation](https://github.com/antonbabenko/deliberation) | `v3.31.0` (`ef84a71a66bf`) | MIT | Cộng đồng, 178★, phát hành đều (tạo 2026-05) | 2026-10-26 | Plugin `deliberation@antonbabenko-deliberation` (user, marketplace cục bộ): Gemini qua `agy` + GPT qua Codex, chỉ đọc – xem `docs/model-routing.md` |
| [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) | `v1.0.6` (`db52e28f4d9d`) | Apache-2.0 | **Chính hãng** (OpenAI), 34,6k★ | 2026-10-26 | Plugin `codex@openai-codex` (user, marketplace cục bộ từ bản ghim): `/codex:review` bằng ChatGPT Free |

## Những gì nguồn chạy/truy cập (đọc mã ngày 2026-10-21)
- **Skill markdown** (mattpocock, homeassistant-ai, teaching-skills, GarethManning): không có script,
  không có `allowed-tools`, không có hook. Riêng `diagnosing-bugs` có `hitl-loop.template.sh`,
  là mẫu để copy, chỉ dùng `read`/`printf`.
- **docx/pptx/xlsx**: script Python gọi `soffice` (LibreOffice) và git cục bộ qua `subprocess`.
  Không gọi mạng (`urllib` chỉ dùng để parse đường dẫn).
- **Agent VoltAgent**: được cấp `Read, Write, Edit, Bash, Glob, Grep`, model `sonnet`.
- **freecad-mcp**: addon mở XML-RPC và `exec()` code nhận được trong FreeCAD.
  Mặc định chỉ nghe ở `127.0.0.1`; tùy chọn `0.0.0.0` kèm lọc IP: **không bật**.
- **mcp-for-blender**: `execute_blender_code` chạy Python tùy ý. Telemetry gửi về Supabase
  (có thể kèm `prompt_text`) nếu đồng ý: tắt bằng `DISABLE_TELEMETRY=1` (đã đặt trong `.mcp.json`).
  Addon tự kiểm tra bản mới từ nhánh `main`: tắt bằng `BLENDERMCP_NO_UPDATE_CHECK=1`.
  Có tích hợp API ngoài (Poly Haven, Sketchfab, Hyper3D/fal.ai, Poly Pizza, "premium").
  `BLENDER_MCP_SAFE_MODE=1` bật sandbox giới hạn module/builtin.
- **ha-mcp**: cần token admin Home Assistant. Có tool xóa entity/device, restart, ghi/xóa file.
  Có chế độ read-only (`/readonly`), bật/tắt từng tool. Không có telemetry (theo README).

### FreeCAD robotics (đọc mã 2026-10-21)
- **Gears, SheetMetal**: `subprocess` chỉ trong script dev (dịch, test) – không chạy khi dùng. Không gọi mạng.
- **RobotCAD**:
  - Không tự `pip install` khi nạp; thiếu thư viện thì mở hộp thoại để người dùng bấm cài (PyPI, không ghim).
    → Đã cài sẵn **bản ghim** bằng `studio/freecad/install-robotcad-deps.bat` (lock: `requirements-robotcad.lock.txt`)
    vào `~\.local\share\FreeCAD\AdditionalPythonPackages\py311` (RobotCAD đặt thư mục này đầu `sys.path`).
    **Không** cài numpy/lxml/setuptools… ở đó vì sẽ đè bản của FreeCAD (numpy 1.26.4).
  - Biến môi trường `DEBUG` → mở `debugpy` trên **0.0.0.0:5678** (ai trong LAN cũng chạy được mã).
    Launcher gỡ `DEBUG` khi mở FreeCAD (`env_unset` trong `studio/apps.json`).
  - **Lỗi package.xml (2026-10-24, còn ở v12.10.4 và `main`)**: khai `<subdirectory>freecad/robotcad</subdirectory>`
    nhưng mã ở `freecad/cross` → FreeCAD 1.1 `os.add_dll_directory()` lỗi → "Error in InitApplications" → bỏ qua phần
    cuối InitApplications: thư mục **Macro không vào `sys.path`**, `PATH` không thêm Mod (ảnh hưởng MỌI addon/macro).
    Sửa **không đụng bản ghim**: `custom/freecad/robotcad_overlay.py` dựng `custom/freecad/robotcad-overlay/`
    (junction tới từng mục bản clone + `freecad/robotcad` rỗng); `Mod/freecad.robotcad` trỏ vào đó (`links.tsv`).
    Đổi bản ghim RobotCAD → chạy lại script. Upstream sửa xong → trả `links.tsv` về bản clone, xóa overlay.
  - Lệnh do người dùng bấm có gửi dữ liệu ra ngoài: "Transfer project to external code generator" (robotcad.ru),
    LLM provider (openrouter.ai, routerai.ru, Ollama local). **Không dùng.**
  - 4 git submodule (ros2_controllers, sdformat, robot_descriptions, Dynamic_World_Generator) **chưa tải**:
    phục vụ ROS2/Gazebo (cần Linux/WSL2).
- **FreeCAD-library**: dữ liệu (STEP/FCStd) + macro `PartsLibrary.FCMacro` (chức năng git chỉ bật khi có python-git – chưa cài).
  Repo có tên file chứa `:` → clone đặt `core.protectNTFS=false` **chỉ trong clone này** và loại thư mục đó khỏi sparse.
- **freecad-scripts**: chỉ markdown (SKILL.md + references), không script/hook.
- **RobotCAD v12.10.3 – lỗi upstream (2026-10-22)**: `package.xml` khai `<subdirectory>freecad/robotcad`, mã thật ở
  `freecad/cross` → FreeCAD in `Error in InitApplications … freecad
obotcad` khi khởi động. Workbench vẫn nạp
  (`import freecad.cross` OK) và RobotCAD là Mod nạp cuối nên không chặn Mod khác. Không sửa bản ghim; xem lại khi lên bản mới.
- **manifold3d 3.5.4** (Tuan duyệt 2026-10-23) – thư viện boolean mesh [elalish/manifold](https://github.com/elalish/manifold),
  **Apache-2.0**, cũng là solver boolean "Manifold" của OpenSCAD/Blender. Dùng trong `tools/robotics-cad/scripts/check.py`
  cho va chạm (giao khối `^` + `volume()`, khe hở `min_gap()`) thay boolean B-rep (1 cặp bánh răng mất ~700 s → < 1 s).
  - Wheel `manifold3d-3.5.4-cp311-cp311-win_amd64.whl`, SHA-256 `34ef0b1b70b6d153eb12a72706e128e9b629c562cd4ab103083afd17ca071fbd`
    (PyPI). Chỉ phụ thuộc numpy (dùng numpy 1.26.4 của FreeCAD).
  - Cài **riêng cho dự án**, không đụng bản cài FreeCAD: `"C:/Program Files/FreeCAD 1.1/bin/python.exe" -m pip install
    --no-deps --target tools/robotics-cad/.pylib manifold3d==3.5.4` (thư mục `.pylib/` không lên git). Script tự thêm vào `sys.path`;
    thiếu thư viện thì lùi về B-rep (chậm).
  - Là mã biên dịch (`.pyd` + `msvcp140` kèm theo), chỉ tính hình học: không mạng, không subprocess, không ghi file.

### Model board vi điều khiển (tìm 2026-10-22)
- **Đã có** trong FreeCAD-library: Arduino UNO/Mega/Nano, ESP32 DOIT DevKit v1, Pi 4B, Pico.
- **Thêm** (chính hãng, chỉ dữ liệu): Arduino docs-content, Espressif kicad-libraries (bảng trên).
- **Không có STEP ghim được** → dựng từ bản vẽ cơ khí chính hãng bằng `tools/robotics-cad/library/boards_param.py`
  (mặt bằng đúng bản vẽ, chiều cao linh kiện ƯỚC – đo hàng thật): Pi 5, Pi Zero 2 W, ESP32-DevKitC V4,
  ESP32-S3-DevKitC-1 (đọc tọa độ từ DXF), STM32 Nucleo-64 (UM1724 Fig. 5, khớp chéo chuẩn Arduino UNO – xem
  `models/stm32-nucleo-64/doi-chieu-ban-ve.png`), LOLIN D1 mini v4, ESP32-CAM (datasheet AI-Thinker).
  Bản vẽ lưu ở `community/boards-official/drawings/` (datasheets.raspberrypi.com, dl.espressif.com, wemos.cc;
  UM1724 lấy từ bản lưu của mikrocontroller.ti.bfh.ch vì st.com chặn tải tự động; datasheet ESP32-CAM từ elecrow.com).
- **Blue Pill**: hàng generic, không có bản vẽ hãng. Nguồn cộng đồng mâu thuẫn (23 × 53 stm32-base, 22,5 × 53 qeda,
  22,86 × 53,34 diyAudio; khoảng 2 hàng chân 15 hoặc 15,24) → dựng 22,86 × 53,34 / 15,24, **phải đo hàng thật**.
- **Còn thiếu**: NodeMCU (nhiều biến thể: Amica ~49 × 26, LoLin V3 ~58 × 31 – cần biết STLab dùng loại nào;
  repo chính thức nodemcu/nodemcu-devkit-v1.0 chỉ có Altium/Gerber .rar).
- **Cân nhắc, chưa lấy**: Adafruit_CAD_Parts (MIT, 1,5k★, ~1,2 GB – chỉ board Adafruit); NopSCADlib (GPL-3, OpenSCAD →
  chỉ STL; có Pi Zero/3/4, BlackPill, TP4056, MT3608, MP1584EN…); KiCad packages3D (chỉ Pico/Pico W);
  GrabCAD/Printables/SnapMagic (cần tài khoản, license thường không rõ – không ghim được).
- `update-community.sh clone`: sửa lỗi dừng ngang khi file `.sparse` không có dòng `# git-config` (grep trả 1 + pipefail).

### Video AI (2026-10-21)
- **FilmCraft 0.9.0** (đã cài; [storytold/filmcraft](https://github.com/storytold/filmcraft), Apache-2.0, 15k★): cổng `--control 7920`
  **không có token**. Bản phát hành **không có Whisper/Kokoro** (`transcript.generate`, `tts.*` giọng tự nhiên không chạy).
- **artcraft-skills/filmcraft**: chỉ markdown; KHÔNG chạy `install.sh/ps1` của repo (dùng symlink).
- **faster-whisper 1.2.1** (MIT) + ctranslate2 4.8.3, PyAV ghim < 19 (bản 19 làm hỏng faster-whisper 1.2.1).
  Model `large-v3-turbo` tải 1 lần từ Hugging Face vào `%LOCALAPPDATA%\stlab-video-ai\models`. Chạy CPU (GPU 1660 chậm hơn).
- Đã xem, không dùng: `juan52878911/filmcraft-studio` (MIT, chỉ macOS – tham khảo kiến trúc), `jhonsu01/filmcraft-mcp-server`
  (trùng MCP có sẵn), auto-editor / PySceneDetect (FilmCraft + ffmpeg đã đủ), PhoWhisper (ngừng cập nhật 2024).
- `edge-tts 7.3.1` chỉ dùng **một lần** (uvx, không cài) để tạo clip thử giọng Việt; 7.2.8 bị Microsoft từ chối (403).

### Ảnh AI – LightCraft (duyệt 2026-10-21, giai đoạn 1)
- **artcraft-skills/lightcraft**: chỉ markdown (`SKILL.md`, `evidence.md`, `agents/openai.yaml`); không script, hook,
  `allowed-tools`, không gọi mạng. Viết cho LightCraft **0.9.1** = bản đã cài (`lightcraft-cli 0.9.1`, đủ `run/render/mcp`).
  - Skill mô tả macOS. Trên Windows: app `C:\Program Files\LightCraft\lightcraft.exe`, **CLI có sẵn** cạnh app
    (macOS phải tải riêng), log/thư viện theo `%APPDATA%`/`Pictures` (TODO: xác nhận đường dẫn log ở giai đoạn 2).
  - Thử headless 2026-10-21 (`run --demo … app.export`): OK, ra JPEG 2048×1365 px. Trên Windows `app.export path=`
    phải là **đường dẫn file** (`…\demo1.jpg`); đưa thư mục → `Access is denied (os error 5)`.
    `develop.set` trả `null` nhưng **có áp** (kiểm bằng `develop.get`, 2026-10-21). `develop.auto` quá tay với ảnh
    JPEG ngược sáng (exposure −0,88, shadows +52 → xám, đục): **không dùng**, dùng preset riêng.
    `render --settings` **không áp** preset JSON phẳng (`{"light.exposure":…}`) – dùng `--set k=v` (2026-10-21,
    khớp 100% với `run develop.set`). `app.export metadata=copyright` vẫn giữ Artist/Copyright do máy ảnh ghi (có thể là email người chụp).
  - Điều skill nhấn mạnh: cổng `--control` **không có token**; một thư viện chỉ một tiến trình ghi (`catalog.lock`);
    `ok: true` không chứng minh ảnh đúng – phải kiểm file xuất. Khử nhiễu AI / SAM 3 không kèm model.
- Công cụ bổ trợ **đã duyệt, chưa cài** (cài + ghim lock ở giai đoạn 3–4, môi trường `uv` riêng):

| Công cụ | Bản dự kiến | License | Tin cậy | Dùng cho | Ghi chú an toàn |
|---|---|---|---|---|---|
| [ExifTool](https://exiftool.org) | 13.59 | GPL / Perl Artistic | Chuẩn ngành, 5k★ (mirror) | Ghi tác giả/bản quyền, **xóa GPS** | Chạy cục bộ, không mạng |
| [opencv-python-headless](https://github.com/opencv/opencv-python) | 5.0.0.93 | MIT (wrapper) / Apache-2.0 (OpenCV) | Tổ chức OpenCV | Chấm độ nét, cháy sáng → lọc ảnh | Không mạng |
| [ImageHash](https://github.com/JohannesBuchner/imagehash) | 4.3.2 | BSD-2-Clause | 3,9k★ | Tìm ảnh trùng/chụp liên tiếp | Nhẹ (thay imagededup) |
| [rembg](https://github.com/danielgatis/rembg) | v2.0.85 (`202e42649a84`) | MIT | 25k★ | Tách nền ảnh sản phẩm | Mặc định `bria-rmbg` (tốt nhất, ~1 GB; thương mại phải trả phí → xem bảng "Xem lại khi làm thương mại"); `birefnet-general` (MIT) là phương án thay. **Cấm** `withoutbg` (gửi ảnh lên cloud – lý do riêng tư, không phải license). Model tải từ GitHub release của rembg lần đầu |
| BiRefNet (model) | `birefnet-general` | MIT ([ZhengPeng7/BiRefNet](https://github.com/ZhengPeng7/BiRefNet), 4,3k★) | — | Model tách nền | — |
| [Real-ESRGAN-ncnn-vulkan](https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan) | `realesrgan-ncnn-vulkan-20220424-windows.zip` (release Real-ESRGAN v0.2.5.0) | MIT (file LICENSE; Real-ESRGAN gốc BSD-3) | 37k★ (gốc), không cập nhật từ 2022 | Phóng ảnh điện thoại nhỏ | Vulkan chạy GTX 1660 SUPER 6 GB. Model `realesrgan-x4plus`. **Đã cài 2026-10-22** vào `photo-ai/tools/realesrgan/`, SHA-256 zip `abc02804…802d` (`photo-ai/tools/SHA256SUMS`); 800→3200 px ≈ 8 s. Nét hơn nhưng **da mịn kiểu sáp, chữ bị viền** → chỉ dùng cho ảnh nhỏ thật sự |

### CyberBrick – model chính thức Bambu Lab (tải 2026-10-21)
- Nguồn: link "3D Model / Solid Model / Specification" trên trang sản phẩm Bambu Store (CDN `store.bblcdn.com`),
  danh sách trong wiki https://wiki.bambulab.com/en/makerworld/cyberbrick/component-list. 48 file (215 MB):
  36 STL, 36 STEP, 45 PDF, 4 3MF, 10 JSON (cấu hình điều khiển). **Không có file chạy** (đã quét trước khi giải nén).
- Lưu ở `community/cyberbrick-official/` (không lên git); danh sách + SHA-256: `tools/robotics-cad/library/cyberbrick-sources.tsv`;
  tải/sắp lại: `tools/robotics-cad/library/cyberbrick.py`. FreeCAD 1.1 mở hợp lệ cả 26 STEP (2026-10-21).
- Không có license ghi kèm (tài liệu kỹ thuật do hãng phát hành công khai) → bảng "Xem lại khi làm thương mại".
- Hãng không phát hành model N20 (LA002–LA004), chỉ datasheet → dùng model N20 chuẩn của Pololu (mục dưới).

### Động cơ N20 – model Pololu Micro Metal Gearmotor (tải 2026-10-21)
- N20 là khuôn chung nhiều hãng (12 × 10 mm, hộp số 9 mm, trục Φ3 vát D, lỗ M1.6). FreeCAD-library không có;
  GitHub chỉ có dự án dùng N20, không có model đáng tin. Chọn **Pololu** (hãng phát hành STEP chính thức):
  https://www.pololu.com/product/2364/resources → zip 26 STEP (278 MB giải nén) + PDF bản vẽ kích thước.
- Đã quét: chỉ `.step` + README, không có file chạy. SHA-256 trong `tools/robotics-cad/library/n20-sources.tsv`.
- Sắp 8 biến thể vào `community/n20-motor/models/` (STEP + STL xuất bằng FreeCAD 1.1). So datasheet CyberBrick LA002:
  dài 35,8 so với ≈ 36,1 mm (trục 9,3 so với 10) – đủ để dựng gá, đo hàng thật trước khi làm khớp chặt.
- Không ghi license kèm file → bảng "Xem lại khi làm thương mại".
- Mã nguồn lõi: [CyberBrick-Official/CyberBrick_Controller_Core](https://github.com/CyberBrick-Official/CyberBrick_Controller_Core) (234★, chưa ghim).

### Datasheet / bản vẽ kích thước linh kiện (ghim 2026-10-24)
- Nghiên cứu nơi chứa kích thước chính thức: `docs/component-dimension-sources.md`. Số đã đưa vào `components.yaml`
  (PG001/PG002, SG90, N20, NEMA17, Pi 4, Pico, UNO R4 WiFi, XA007, PC003, 608ZZ), mỗi số kèm nguồn.
- File tĩnh (PDF/JPG), không chạy gì. Tải lại theo `datasheet-sources.tsv`, kiểm SHA-256; lệch → không dùng.
- Fasteners WB: đọc mã 2026-10-24 – không gọi mạng; `subprocess` chỉ trong `Resources/translations/compile_translations.py`
  (script dịch cho dev). Bản ghim trùng 100 % nội dung bản Addon Manager đã cài (khác mỗi CRLF).

### LUT / preset cộng đồng cho ảnh (duyệt 2026-10-21)
- LightCraft ≈ Lightroom, PhotoCraft ≈ Photoshop → dùng lại tài nguyên định dạng Adobe. Chỉ là **dữ liệu**
  (`.xmp`, `.cube`, `.png`), không có mã chạy; không gọi mạng.
- Kiểm thực tế: LightCraft `render --settings preset.xmp` **áp được** XMP Lightroom (PV 15.4); PhotoCraft
  `image.adjustments.colorLookup {"file": "D:/.../x.cube"}` áp được LUT (đường dẫn **kiểu Windows**, `/d/...` lỗi).
  PhotoCraft **chép EXIF từ ảnh vào** → luôn đưa ảnh đã `metadata=none` và kiểm GPS ở QA.
- So sánh 12 kiểu trên 4 ảnh 20/10 (`scripts/looks.py`): LUT RawTherapee (Portra 160 NC, Fuji 400H) cho da
  tự nhiên nhất; preset XMP peva3 áp thẳng lên JPEG ngược sáng thường bị nhạt/đục.
- Không tìm được bộ Photoshop Actions `.atn` miễn phí có uy tín trên GitHub (chủ yếu hàng bán); PhotoCraft
  tự làm được chọn người/trời/mặt (`select.subject`, `select.sky`, `image.detectFaces`) nên không cần.
- Tránh: repo kiểu "Lightroom Photo Studio for Windows" mới tạo (dấu hiệu mồi mã độc);
  `dpnkrpl/awesome-lightroom-presets` (5000 preset không rõ nguồn, có thể là preset bán bị chia sẻ lậu).

### Remotion skills (đọc mã 2026-10-24)
- 12 skill (`remotion-best-practices` là router chứa bản sao các skill còn lại → chỉ liên kết skill này, tránh trùng tên).
  Không hook, không `allowed-tools`, không `.mcp.json`. 2 script `prep-*.mjs` (remotion-maps) chỉ đọc/ghi file cục bộ.
- Lệnh skill sẽ bảo chạy: `npx create-video@latest` (**không ghim** – khi dùng thì ghim phiên bản), `npm i`, `npx remotion studio/render`
  (tải Chromium headless lần đầu). Node đã có: v24.15.0. `remotion-docs` gọi Algolia search (key công khai chỉ đọc) + remotion.dev.
- Remotion **chưa cài** vào dự án nào. Telemetry Remotion: `TODO` đọc trước khi cài (xem `docs/project-video-marketing-research.md`).
- `scripts/*.ts`, `package.json` của repo là công cụ đồng bộ nội bộ của Remotion – không chạy.

### deliberation (đọc mã 2026-10-26)
- Node thuần, chỉ module có sẵn của Node (không `npm install`). Plugin khai 4 MCP server: `deliberation` (bộ điều phối),
  `deliberation-gemini`, `-grok`, `-openrouter`. Không hook. `commands/` = lệnh `/deliberation:*` (namespace riêng).
- Gemini: chạy `agy -p` (tiến trình con, `shell:false`) với `--sandbox` (chỉ chặn lệnh terminal). **Windows không có
  sandbox HĐH** (Seatbelt chỉ macOS) → còn lời nhắc READ-ONLY + xóa biến môi trường dạng key/token/`GIT_ASKPASS`/
  `SSH_AUTH_SOCK` + phát hiện thay đổi git (không hoàn tác). `workspace-write` → `--dangerously-skip-permissions`.
- Bộ điều phối luôn chỉ đọc (provider dựng không có `allowImplement`). Đường ghi chỉ ở tool `gemini` của server
  `deliberation-gemini` → **chặn** bằng `permissions.deny` (kèm grok/openrouter).
- GPT: gọi `codex` CLI (đăng nhập ChatGPT; không đọc `OPENAI_API_KEY`), chế độ advisory chỉ đọc.
- Mạng: agy/codex tự gọi Google/OpenAI; Grok/OpenRouter chỉ khi bật + có key (đang tắt). Dashboard HTTP chỉ
  `127.0.0.1` + token, **tắt**. Không thấy telemetry.
- Ghi file: config/journal/sessions ở `%APPDATA%\deliberation` (sessions/journal tắt). Tham số `files`: với Gemini
  **không** chèn nội dung (chỉ `dir` → `--add-dir`, thử 2026-10-26) → STLab chép file vào `agy-scratch\<ten-viec>`;
  Codex tự đọc đường dẫn (sandbox chỉ đọc). Danh sách cấm gửi trong `CLAUDE.md`.
- `/deliberation:setup` ghi `~/.claude/rules/deliberation/` (luật tự giao việc trên mọi tin nhắn) + `~/.claude.json`
  → **không chạy**; config tự viết (`docs/model-routing.md`).
- PAL MCP (`BeehiveInnovations/pal-mcp-server` v9.8.2) đã thẩm định và cài thử cùng ngày rồi gỡ: mã dừng từ 2025-12-15.

### Codex plugin (đọc mã 2026-10-26)
- Node script gọi Codex CLI (`@openai/codex` 0.164.0, chính hãng) qua app-server cục bộ; Codex dùng đăng nhập ChatGPT.
- Sandbox: `review`/`adversarial-review` = `read-only`; `rescue` = `workspace-write` khi yêu cầu ghi
  (`approvalPolicy: never`) → chỉ dùng khi Tuan đồng ý.
- Hook: `SessionStart`/`SessionEnd` (dọn job + tắt broker, timeout 5 s); `Stop` = cổng review khi dừng, **mặc định tắt**
  (`stopReviewGate: false`), bật chỉ qua `/codex:setup`. Trạng thái lưu ở thư mục dữ liệu plugin/`%TEMP%\codex-companion`.
- Agent `codex:codex-rescue` dùng `model: sonnet` (chỉ chuyển tiếp lệnh, vẫn tốn quota Claude ít).
- Không có URL cứng trong script; mạng do Codex CLI gọi OpenAI.

## Thay đổi bên ngoài workspace (để gỡ/khôi phục)
| Ngày | Vị trí | Thay đổi | Khôi phục |
|---|---|---|---|
| 2026-10-21 | `~/.claude/skills/{grill-me,handoff,diagnosing-bugs,research,robotics-cad,freecad-scripts}` | symlink → workspace (nguồn duy nhất) | `update-community.sh unlink` |
| 2026-10-21 | `~/.claude/CLAUDE.md` | tạo mới (trước đó không có) | xóa file |
| 2026-10-21 | `%APPDATA%\FreeCAD\v1-1\Mod\FreeCADMCP` | symlink → freecad-mcp v0.1.27 | `unlink`, rồi chuyển `Mod-backup\FreeCADMCP-0.1.26-2026-10-21` về `Mod\FreeCADMCP` |
| 2026-10-24 | Blender 5.1 đã gỡ, máy có **5.2.2 LTS**: `studio/apps.json` trỏ 5.2; symlink addon chuyển sang `%APPDATA%\Blender Foundation\Blender\5.2\scripts\addons\blender_mcp.py` (đã thử: addon nạp OK trên 5.2, factory-startup). Addon **chưa bật** trong cài đặt 5.2: lần đầu mở 5.2 chọn chép cài đặt 5.1 (đã bật MCP) hoặc Edit → Preferences → Add-ons bật "Blender MCP" | sửa lại `apps.json`, `links.tsv` |
| 2026-10-21 | `%APPDATA%\Blender Foundation\Blender\5.1\scripts\addons\blender_mcp.py` | symlink → mcp-for-blender | `unlink` |
| 2026-10-21 | Blender 5.1 `config\userpref.blend` | bật addon "MCP for Blender" | chép đè từ `userpref.blend.bak-2026-10-21` |
| 2026-10-21 | Biến môi trường người dùng | `BLENDERMCP_NO_UPDATE_CHECK=1` | `reg delete HKCU\Environment /v BLENDERMCP_NO_UPDATE_CHECK` |
| 2026-10-21 | Windows | Bật Developer Mode (cho symlink) | Settings → For developers |
| 2026-10-21 | `%APPDATA%\FreeCAD\v1-1\Mod\{freecad.robotcad, freecad.gears, SheetMetal}`, `Macro\PartsLibrary.FCMacro` | symlink → bản ghim | `update-community.sh unlink` |
| 2026-10-24 | `%APPDATA%\FreeCAD\v1-1\Mod\freecad.robotcad` | symlink đổi từ bản clone sang `custom/freecad/robotcad-overlay` (sửa lỗi package.xml) | gỡ symlink, sửa `links.tsv` về `community/drfenixion-freecad-robotcad`, `update-community.sh link` |
| 2026-10-24 | `%APPDATA%\FreeCAD\v1-1\Mod\fasteners` | bản Addon Manager 0.5.67 chuyển sang `Mod-backup\fasteners-0.5.67-2026-10-24`; thay bằng symlink → bản ghim `V0.5.67-beta` | `update-community.sh unlink`, rồi chuyển thư mục backup về `Mod\fasteners` |
| 2026-10-21 | `~\.local\share\FreeCAD\AdditionalPythonPackages\py311` | thư viện Python ghim cho RobotCAD (16 gói, xem lock) | xóa thư mục |
| 2026-10-21 | `%LOCALAPPDATA%\stlab-video-ai\models` | model faster-whisper large-v3-turbo (~1,6 GB) | xóa thư mục |
| 2026-10-21 | FreeCAD tham số `Plugins/parts_library/destination` | trỏ tới `community/freecad-library` | macro PartsLibrary → Settings |
| 2026-10-21 | Claude Desktop `%LOCALAPPDATA%\Claude-Data\claude_pzs8sxrjxfjjc\claude_desktop_config.json` | **chưa đổi**; `sync-claude-desktop.bat` sẽ thêm blender, lightcraft và thay freecad (`uvx freecad-mcp` không ghim) bằng bản ghim | chép đè từ file `.bak-*` cạnh nó |
| 2026-10-21 | `%USERPROFILE%\Pictures\stlab-studio\` | thư mục PhotoCraft được đọc/ghi qua MCP | xóa thư mục |
| 2026-10-21 | `~/.claude/skills/lightcraft` | symlink → artcraft-skills/lightcraft (`aa35c24`) | `update-community.sh unlink` |
| 2026-10-24 | `~/.claude/skills/remotion-best-practices` | symlink → remotion-dev/skills (`6c67adc`) | `update-community.sh unlink` |
| 2026-10-26 | `~/.claude/settings.json` + `~/.claude/plugins/` | marketplace cục bộ `antonbabenko-deliberation` → `community/antonbabenko-deliberation`, plugin `deliberation@antonbabenko-deliberation` (user) | `claude plugin uninstall deliberation@antonbabenko-deliberation`, `claude plugin marketplace remove antonbabenko-deliberation` |
| 2026-10-26 | `~/.claude/settings.json` `permissions.deny` | chặn `mcp__plugin_deliberation_deliberation-{gemini,grok,openrouter}` | xóa 3 luật, hoặc chép đè từ `settings.json.bak-2026-10-26` |
| 2026-10-26 | `%APPDATA%\deliberation\config.json` | config tự viết (codex + gemini, tắt phần còn lại) | xóa thư mục |
| 2026-10-26 | `%LOCALAPPDATA%\agy\bin` + PATH người dùng | Antigravity CLI 1.4.7 (tự cập nhật); đăng nhập Google lưu ở `~/.gemini` (**Tuan tự làm**) | xóa thư mục, bỏ khỏi PATH |
| 2026-10-26 | `D:\04_Stlab\agy-scratch` | thư mục trống làm `cwd` cho agy | xóa thư mục |
| 2026-10-26 | Biến môi trường người dùng | `AGY_BIN=%LOCALAPPDATA%\agy\bin\agy.exe` (MCP deliberation không thấy agy trên PATH) | `[Environment]::SetEnvironmentVariable('AGY_BIN',$null,'User')` |
| 2026-10-26 | `~/.claude/settings.json` + `~/.claude/plugins/` | marketplace cục bộ `openai-codex` → `community/openai-codex-plugin-cc`, plugin `codex@openai-codex` (user) | `claude plugin uninstall codex@openai-codex`, `claude plugin marketplace remove openai-codex` |
| 2026-10-26 | npm global | `@openai/codex@0.164.0` | `npm uninstall -g @openai/codex` |
| 2026-10-26 | `~/.claude/agents/{check-runner,doc-writer,git-scribe}.md` | symlink → `custom/agents/` | `update-community.sh unlink` |

Các bản clone có `__pycache__/`, `*.pyc`, `build/`, `*.egg-info/`, `logs/` trong `.git/info/exclude`
(lệnh `exclude`), vì FreeCAD/Blender/uv/MCP server Python sinh các file này khi chạy trực tiếp từ bản ghim.

## Đã xem và KHÔNG dùng
| Repo | Lý do |
|---|---|
| schwarztim/bambu-mcp | Nhúng khóa trích từ Bambu Connect để vượt xác thực firmware: rủi ro pháp lý/ToS |
| Eyalm321, griches, rowbotik (bambu) | Không hỗ trợ A1 / 0★ |
| musistudio/claude-code-router, LiteLLM proxy (2026-10-26) | Gateway đổi `ANTHROPIC_BASE_URL` → Claude tính theo API, không dùng gói Pro |
| jarrodwatts/claude-delegator (2026-10-26) | Đã archive; Codex bỏ lệnh `mcp-server` nó dùng |
| cheaper-inference/OmniRoute, gpt4free (2026-10-26) | Có tuyến cookie web/giả vân tay TLS (wreq-js) – rủi ro vi phạm ToS |
| jamubc/gemini-mcp-tool (2026-10-26) | Backend `agy` thử nghiệm, không có chế độ chỉ đọc; deliberation làm tốt hơn |
| BeehiveInnovations/pal-mcp-server (2026-10-26) | Cài thử rồi gỡ: mã dừng từ 2025-12-15, lỗi path traversal báo 2026-10-24 chưa vá; fork còn sống 0–3★ |
| Zen4-bit/Proxima (2026-10-26) | Dùng phiên web (README nhận có thể vi phạm ToS); license chỉ cá nhân |
| Lykhoyda/ask-llm (2026-10-26) | Chỉ Linux/macOS, 18★ |
| greenpolo/cc-multi-cli-plugin – Grok Build (2026-10-26) | Để sau: 193★, hạn mức Grok free không công bố |
| loryanstrant, bberrevoets, NickLD, Vortitron (ESPHome MCP) | Quá mới, ít người dùng: xem lại sau |
| ezrover, agodianel, f2daz (skill ESP32) | Ít người dùng hoặc ngừng cập nhật: thử nghiệm sau khi đọc mã |
| idealo/imagededup | Kéo theo PyTorch (vài GB) cho việc ImageHash làm được |
| dpnkrpl/awesome-lightroom-presets | 5000 preset không rõ nguồn gốc (nghi chia sẻ lậu preset bán) |
| WattSnailInferno/lightroom-presets-studio, patriciasilvadatamac/Lightroom-Photo-Studio, digistoremaster/… | Repo mới, mô tả "phần mềm Lightroom cho Windows": dấu hiệu mồi mã độc |
| pyrocat101/Fujifilm-LUTs | LUT cho ACES/log (video, RAW), không hợp JPEG |
| cedeber/hald-clut `Apple/`, `Pixelmator Pro/` | Trích từ app thương mại |

## Xem lại khi làm thương mại
Chính sách (2026-10-21): STLab dùng **phi thương mại** → license không chặn, ưu tiên repo nhiều sao.
Khi chuyển sang thương mại, rà bảng này trước (và cột License ở bảng "Nguồn đang dùng").

| Nguồn | License / ràng buộc | Đang dùng ở đâu |
|---|---|---|
| hesreallyhim/awesome-claude-code | CC BY-NC-ND 4.0 (phi thương mại, không phái sinh) | Tra cứu |
| GarethManning/education-agent-skills | CC BY-SA 4.0 (ghi công, chia sẻ cùng license) | stlab |
| FreeCAD/FreeCAD-library | CC-BY 3.0 (ghi công) | FreeCAD |
| anthropics/skills docx/pdf/pptx/xlsx | Source-available | stlab |
| theosib/FreeCAD-MCP-Server | Không có license | Chưa dùng |
| chaofengc/IQA-PyTorch (pyiqa) | NTU S-Lab + CC BY-NC-SA 4.0 | Ứng viên chấm điểm thẩm mỹ ảnh |
| remotion-dev/skills + Remotion | Repo skill không có license; Remotion License: free cá nhân/công ty ≤ 3 NV/phi lợi nhuận, trên đó cần Company License | `~/.claude/skills/remotion-best-practices` |
| briaai/RMBG-1.4, RMBG-2.0 (mặc định của rembg) | BRIA: thương mại phải trả phí | Ứng viên tách nền (chất lượng tốt nhất của rembg) |
| upscayl (fork ncnn) | AGPL-3.0 | Chưa dùng |
| Pololu Micro Metal Gearmotor STEP (N20) | Không ghi license; hãng phát hành công khai | tools/robotics-cad |
| CyberBrick model/datasheet (Bambu Lab) | Không ghi license; tài liệu hãng phát hành công khai | tools/robotics-cad, cyberbrick-car |
| abpy/FujifilmCameraProfiles | Không có license (mặc định: giữ mọi quyền) | photo-ai LUT Classic/Nostalgic Neg |
| RawTherapee Film Simulation (qua cedeber/hald-clut) | CC BY-SA 4.0 (ghi công Pat David và cộng sự; LUT phái sinh cùng license) | photo-ai `luts/*.cube` |
| RawTherapee Film Simulation HaldCLUT | Không rõ (nhiều tác giả) | Ứng viên LUT cho PhotoCraft |
| abpy/FujifilmCameraProfiles (588★) | Không có license; mô phỏng giả lập phim của Fujifilm | Ứng viên LUT |
| Nguồn tham khảo cơ cấu tay robot + dạy CAD (Thor CC-BY-SA, PAROL6 GPL-3.0, Faze4, Onshape/Fusion EDU…) | Xem bảng "Xem lại khi thương mại" trong `docs/cad-mechanisms-teaching-research.md` (2026-10-25) | Chỉ tham khảo |

## Chính sách cập nhật (tóm tắt)
1. Ghim tag/SHA, không bám `main`. Nâng cấp từng repo một, giữ `prev_sha` để rollback.
2. Mặc định chỉ kiểm tra và báo cáo. Bạn duyệt từng repo rồi mới `apply`.
3. Tự áp dụng chỉ khi `allowlist=yes` **và** `auto=on` (hiện tất cả đều `off`).
   Có thay đổi nhạy cảm thì tự dừng.

## Lệnh (chạy tại `claude-workspace`, Git Bash)
```bash
bash community/update-community.sh status            # diem ghim va trang thai
bash community/update-community.sh check [ten]       # bao cao -> community/reports/YYYY-MM-DD.md
bash community/update-community.sh apply <ten> <ref> # chuyen ghim (sau khi duyet)
bash community/update-community.sh rollback <ten>    # quay ve ghim truoc
bash community/update-community.sh check --auto      # chi tac dong repo allowlist + auto=on
bash community/update-community.sh clone             # may moi: clone dung diem ghim
bash community/update-community.sh link | verify | unlink   # symlink theo links.tsv
```
Trong Claude Code: `/update-community [ten]` (chỉ báo cáo).
Đánh dấu nhạy cảm gồm: `HOOK`, `MCP`, `QUYEN` (settings), `PHU-THUOC`, `SCRIPT-MOI`, `SHELL-DOI`,
và `NOI-DUNG` (dòng thêm có `curl`, `eval(`, `subprocess`, `Bash(`, `allowed-tools`, `mcpServers`…).
