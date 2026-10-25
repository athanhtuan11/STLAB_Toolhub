# Nghiên cứu: công cụ mở cho "bước 0 – giao diện" (mockup duyệt bằng PNG)

Viết 2026-10-25. Mục đích: chọn công cụ **Claude dùng được bằng code/file, chạy headless, xuất PNG** để làm mockup giao diện
cho 4 loại: (a) điều khiển thiết bị ESP32 (web trên ESP32, app ESP RainMaker, màn hình LVGL/TFT), (b) Toolhub Flask,
(c) workbench/dialog PySide trong FreeCAD 1.1, (d) điều khiển robot (teleop, joystick, trạng thái khớp).

**Không lặp:** Double Diamond, `frontend-design`/`theme-factory`/`canvas-design`, `ui-ux-pro-max`, token theme FreeCAD 1.1, OpenTheme,
Pico CSS (archived), Open Props, Tabler/Lucide, ESPHome `web_server`, ESPAsyncWebServer, ESP-DASH, WCAG 1.4.3 + 2.5.8
→ đã có ở [design-first-research.md](design-first-research.md). File này chỉ bổ sung.

**Nhãn:** **[nguồn gốc]** = README/LICENSE/docs/mã của dự án · **[API]** = GitHub REST API ngày 2026-10-25 (★ = sao,
push = `pushed_at`) · **[đo]** = tự đo ngày 2026-10-25 · **(thứ cấp)** = forum/tìm kiếm · `TODO` = chưa xác nhận.
Không cài, không clone, chỉ đọc README/LICENSE/header qua `raw.githubusercontent.com` và npm/PyPI registry.

## 0. Kết luận nhanh

1. **STLab đã có lõi design system** – `studio/design/tokens.json` + `DESIGN.md` + `build_tokens.py` (sinh `tokens.css`, **tự kiểm
   tương phản**, exit 1 khi lỗi), font Be Vietnam Pro (OFL) cục bộ. → **Không** cần thêm design system ngoài. Radix/Primer chỉ đáng
   **học cách đặt thang màu** (12 bậc, mỗi bậc một vai) nếu sau này cần thêm màu.
2. **Mockup rẻ và trung thực nhất = HTML thật dùng `tokens.css` + chụp Edge headless** (STLab đã làm trong `assembly-pdf.py`).
   Không cần Penpot/Figma: mockup chính là bản đầu của code, không vẽ hai lần. Công cụ vẽ (Excalidraw/draw.io/Penpot) chỉ hợp khi
   **Tuan muốn tự phác/sửa tay**.
3. **Penpot** (MPL-2.0, 61,6k★) có **MCP chính thức** (đã gộp vào repo chính, thư mục `mcp/`), nhưng MCP chạy qua **plugin trong trình
   duyệt đang mở Penpot** → không headless; tự host cần Docker. Lợi/công thấp với STLab lúc này.
4. **tldraw: license không phải mã mở** – cấm dùng ở "Production Environment", có khóa license. Bỏ.
5. **Excalidraw** (MIT, 134,5k★): JSON dễ cho Claude viết, nhưng xuất PNG headless phải tự dựng (lib `@excalidraw/utils` trong trình
   duyệt); CLI cộng đồng nhỏ, bỏ bê từ 2024. `excalidraw-mcp` là "MCP App" vẽ trong khung chat, khuyên dùng bản **remote** (cloud).
6. **Màn hình LVGL:** LVGL 9.6.0 (MIT) có sẵn `LV_USE_TEST_SCREENSHOT_COMPARE` (ghi PNG tham chiếu) + driver `LV_USE_WINDOWS`/SDL → Claude
   chụp được mockup **bằng mã C thật** trên PC. **LVGL Pro** (editor + CLI có lệnh tạo screenshot, UI viết bằng XML) gói Community
   **miễn phí cho maker/cá nhân/mã mở** → đáng thử; SquareLine (đóng, cần tài khoản) và EEZ Studio (GPL-3, thuần GUI) không hợp Claude.
   Font tích hợp của LVGL không có dấu tiếng Việt → cần `lv_font_conv` + Be Vietnam Pro.
7. **App RainMaker không vẽ được giao diện riêng**: app hãng tự dựng từ kiểu `esp.ui.*` của tham số (toggle, slider, dropdown, text…).
   Mockup = **bảng tham số → kiểu UI** + ảnh chụp app thật; không làm PNG giả.
8. **Robot:** Foxglove **đóng mã từ bản 2.0** (repo `foxglove/studio` archived); fork mở là **Lichtblick** (MPL-2.0, BMW). Cả hai, cùng
   roslibjs, chỉ đáng khi có ROS 2. Robot ESP32 của STLab → trang HTML + **JoyStick.js** (MIT, 7,3 KB) hoặc **nipplejs** (MIT, 21 KB)
   + Gamepad API của trình duyệt. LeRobot có **LeLab** (Apache-2.0, web UI teleop/record) cho lộ trình C.
9. **PySide trong FreeCAD:** **không** dùng QDarkStyle/qt-material/PyQtDarkTheme (ghi đè theme FreeCAD, PyQtDarkTheme không release từ
   2022). Đi tiếp hướng đã chọn: `palette()` + `tokens.json`. Mockup dialog = chạy chính file dialog bằng **PySide ngoài FreeCAD với
   `QT_QPA_PLATFORM=offscreen`** → `widget.grab().save()`, khỏi mở GUI FreeCAD hay crash (`TODO` kiểm phiên bản PySide của FreeCAD 1.1).
10. **Accessibility:** WCAG 2.2 có 2 tiêu chí AA mới rất sát robot: **2.5.7 Dragging Movements** (joystick kéo phải có cách bấm thay thế)
    và **2.4.11 Focus Not Obscured**. Kiểm tự động: `build_tokens.py` (đã có) đủ cho màu; axe-core chỉ thêm khi Toolhub lớn hơn.

## 1. Design system & bộ token mở

STLab hiện có [nguồn gốc – repo]: `tokens.json` (light/dark, status, màu 7 bước quy trình, radius, `esp32.touch_min_px: 44`),
`build_tokens.py` kiểm tương phản, `style.css` chỉ dùng `var(--…)`. Câu hỏi đúng là **"có gì đáng học/chép"**, không phải "dùng cái nào".

| Tên | ★ / push [API] | License | Cần build? | Hợp HTML tĩnh / ESP32? | Kết luận |
|---|---|---|---|---|---|
| [Radix Colors](https://github.com/radix-ui/colors) | 1 719 / 2025-12-17 | MIT | Không – npm `@radix-ui/colors` 3.0.0 có file CSS biến sẵn | Có | **Học** quy ước 12 bậc (1–2 nền, 3–5 nền thành phần, 6–8 viền, 9–10 nền đặc, 11–12 chữ) + cặp dark – `TODO` đọc lại docs trước khi áp. Không chép bảng màu (STLab có màu riêng) |
| [Radix Themes](https://github.com/radix-ui/themes) | 8 793 / 2026-04-11 | MIT | Có – React | Không | Bỏ |
| [shadcn/ui](https://github.com/shadcn-ui/ui) | 126 474 / 2026-10-25 | MIT | Có – React + Tailwind + Radix | Không | Bỏ; chỉ tham khảo dáng (đã loại `web-artifacts-builder` cùng lý do) |
| [Material Web](https://github.com/material-components/material-web) | 11 372 / 2026-10-22 | Apache-2.0 | Có – Lit, bundler | Không | **Bỏ**: README ghi *"MWC is in maintenance mode pending new maintainers"* [nguồn gốc] |
| [material-color-utilities](https://github.com/material-foundation/material-color-utilities) | 2 292 / 2026-10-19 | Apache-2.0 | Thư viện TS/Java/Dart/C++… | — | Tùy chọn: sinh thang tông từ 1 màu gốc (#1E5A45). Không bản Python chính chủ (`TODO`) |
| [IBM Carbon](https://github.com/carbon-design-system/carbon) | 9 578 / 2026-10-24 | Apache-2.0 | Có – Sass/React/web components | Không | Bỏ; tài liệu a11y tốt để đọc |
| [Fluent UI](https://github.com/microsoft/fluentui) | 20 362 / 2026-10-23 | MIT (file LICENSE) | Có – React/web components | Không | Bỏ |
| [Primer primitives](https://github.com/primer/primitives) | 415 / 2026-10-22 | MIT | Không – npm `@primer/primitives` 11.10.0 có CSS sinh sẵn | Có | **Học**: token JSON → CSS, giống hệt cách `tokens.json` → `tokens.css` của STLab. Xác nhận hướng đang đi đúng |
| [Primer CSS](https://github.com/primer/css) | 13 039 / 2026-10-25 | MIT | Sass | Nặng cho ESP32 | Bỏ |
| [USWDS](https://github.com/uswds/uswds) | 7 229 / 2026-10-25 | Phần lớn public domain; icon (Material, Apache-2.0) và font (OFL) có license riêng [nguồn gốc LICENSE.md] | Sass/Gulp | Không | Bỏ code; **đọc** hướng dẫn form/lỗi/vùng bấm (viết rõ, hợp học sinh) |
| Pico CSS / Open Props | — | MIT | — | — | Đã đánh giá ([design-first](design-first-research.md)): Pico archived, Open Props không cần |

**Kết luận:** giữ `tokens.json` làm nguồn duy nhất. Khi cần màu mới (vd. trạng thái "đang chạy", màu khớp robot), đặt theo thang bậc kiểu
Radix và để `build_tokens.py` kiểm. ESP32: chép khối biến từ `tokens.css` vào trang nhúng như `DESIGN.md` đã ghi.

## 2. Công cụ mockup/wireframe Claude dùng bằng file

STLab đã có: HTML → PNG bằng **Edge headless** (`msedge --headless --screenshot=… --window-size=375,812`), dùng trong
`maker/robotics-cad/scripts/assembly-pdf.py`; Edge 156 cài sẵn, Node v24, Python 3.13 [đo].

| Công cụ | ★ / push [API] | License | Định dạng Claude viết | Ra PNG headless? | Gửi dữ liệu ra ngoài? | Đánh giá |
|---|---|---|---|---|---|---|
| **HTML + `tokens.css` + Edge headless** | — | — | HTML/CSS/SVG | **Có**, đã chạy ở STLab | Không | **Dùng** – mockup = code đầu tiên, đúng font/màu thật |
| [Penpot](https://github.com/penpot/penpot) | 61 636 / 2026-10-23 | MPL-2.0 | File thiết kế qua Plugin API (định dạng `.penpot` – `TODO` chưa đọc spec) | Có service exporter khi tự host (`TODO`) | Bản cloud: có; tự host Docker: không | Không lúc này (xem 2.1) |
| [penpot-mcp](https://github.com/penpot/penpot-mcp) | 532 / 2026-03-19, **archived** → chuyển vào `penpot/penpot/mcp` | MPL-2.0 | JS chạy trong plugin | Không – cần trình duyệt mở Penpot + plugin | Có bản remote; local cần plugin `localhost:4400` | Theo dõi |
| [Excalidraw](https://github.com/excalidraw/excalidraw) | 134 511 / 2026-10-23 | MIT | JSON `.excalidraw` | Gián tiếp: `@excalidraw/utils` `exportToSvg/exportToBlob` chạy trong trình duyệt → tự viết 1 trang HTML + Edge headless | excalidraw.com là cloud; lib cục bộ thì không | Thử nếu Tuan muốn **phong cách vẽ tay** để duyệt bố cục |
| [excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp) | 5 568 / 2026-03-24 | MIT (package.json; API không nhận LICENSE) | MCP App | Không ra file PNG; hiển thị trong chat | README khuyên remote `mcp.excalidraw.com` | Không |
| [excalidraw-brute-export-cli](https://github.com/realazthat/excalidraw-brute-export-cli) | 16 / 2024-09-05 | MIT | — | Có (Playwright + Firefox) | Không | Không (nhỏ, bỏ bê) |
| [tldraw](https://github.com/tldraw/tldraw) | 51 075 / 2026-10-24 | **tldraw license** (không OSI) | JSON qua SDK React | Qua SDK | tldraw.com cloud | **Bỏ**: cấm "Production Environment", có License Key [nguồn gốc LICENSE.md] |
| [draw.io desktop](https://github.com/jgraph/drawio-desktop) | 63 642 / 2026-10-23 | GPL-3.0 (app), Apache-2.0 (lõi [jgraph/drawio](https://github.com/jgraph/drawio)) | XML `.drawio` (có thư viện hình mockup) | CLI xuất PNG (`--export --format png`, `TODO` kiểm `--help`) | README: *"No diagram data is ever sent externally"*; chỉ kiểm cập nhật (tắt bằng `DRAWIO_DISABLE_UPDATE=true`) | Thử khi Tuan muốn **tự sửa tay** sơ đồ bố trí |
| [Mermaid](https://github.com/mermaid-js/mermaid) + [mermaid-cli](https://github.com/mermaid-js/mermaid-cli) | 90 846 / 5 123 | MIT | Text | `mmdc` 12.0.0, peer `puppeteer ^25` (tải Chrome; `-p` config để trỏ Edge – `TODO`) | Không | Không cho mockup; **dùng cho luồng màn hình / state machine** chế độ robot |
| PlantUML Salt ([repo](https://github.com/plantuml/plantuml)) | 13 380 / 2026-10-24 | Nhiều bản (GPL/LGPL/Apache/MIT/EPL) | Text wireframe | Có (Java jar) | Không | Không – dáng cũ, cần Java |
| [D2](https://github.com/d2lang/d2) | 25 723 / 2026-10-11 | MPL-2.0 | Text | SVG/PNG/PDF (PNG có cần trình duyệt không – `TODO`) | Không | Không cho mockup; sơ đồ kiến trúc thì được |
| [Kroki](https://github.com/yuzutech/kroki) | 4 381 / 2026-10-21 | MIT | Gom nhiều ngôn ngữ text | Server tự host Docker | Bản kroki.io: có | Không cần |

### 2.1 Vì sao không chọn Penpot làm trung tâm
- Lợi: mã mở, có MCP chính thức, designer quen kiểu Figma, tự host được.
- Công: Docker nhiều container trên Windows; MCP yêu cầu **mở Penpot trong trình duyệt + chạy plugin** (README: plugin
  `http://localhost:4400/manifest.json`, MCP `http://localhost:4401/mcp`) → không chạy nền; LLM "write and execute arbitrary code
  snippets within the Penpot Plugin environment" [nguồn gốc]. Kết quả vẫn phải viết lại thành HTML/QSS/LVGL.
- Khi nào xem lại: STLab có người thiết kế làm việc song song, hoặc dạy học sinh môn thiết kế UI.

## 3. UI nhúng (ESP32, màn hình TFT)

### 3.1 LVGL
| Tên | ★ / push [API] | License | Claude dùng thế nào | Ghi chú |
|---|---|---|---|---|
| [LVGL](https://github.com/lvgl/lvgl) 9.6.0 (2026-09-16) | 25 003 / 2026-10-22 | MIT | Viết C → build PC → PNG | `lv_conf_template.h` [nguồn gốc]: `LV_USE_TEST` + `LV_USE_TEST_SCREENSHOT_COMPARE` (cần `LV_USE_LODEPNG`) "create it from the rendered screen" khi chưa có ảnh tham chiếu → **cách headless ra PNG**; còn `LV_USE_SNAPSHOT`, driver `LV_USE_WINDOWS` (không cần SDL) |
| [lv_port_pc_vscode](https://github.com/lvgl/lv_port_pc_vscode) | 549 / 2026-10-22 | MIT | Mẫu project PC | Windows: SDL2 qua vcpkg + MinGW + CMake [nguồn gốc] – cài khá nhiều |
| [lv_web_emscripten](https://github.com/lvgl/lv_web_emscripten) | 130 / 2025-11-25 | MIT | Build ra web → chụp Edge | Cần Emscripten SDK; ít cập nhật |
| [LVGL Pro](https://github.com/lvgl/lvgl_pro) (repo cũ `lvgl_editor`) | 672 / 2026-10-22 | **Thương mại**; gói *Community* "Free, unlimited seats, for makers, personal use, and open-source projects" [nguồn gốc] | UI = **XML** (Claude viết được); **CLI** "validates projects, exports C code, runs UI tests… and generates screenshots" | Online Viewer = cloud. STLab là trung tâm giáo dục có thu phí → có thuộc "maker" không: `TODO` hỏi LVGL |
| [lv_font_conv](https://github.com/lvgl/lv_font_conv) | 308 / 2026-09-17 | MIT | CLI Node: TTF → font C | Font Montserrat tích hợp chỉ có ASCII + ký hiệu (theo docs LVGL – `TODO` đọc lại bản 9.6) → **phải** tạo font Be Vietnam Pro với dải tiếng Việt; dung lượng flash `TODO` đo |
| [EEZ Studio](https://github.com/eez-open/studio) | 1 860 / 2026-10-22 | GPL-3.0; mã sinh ra thuộc người dùng [nguồn gốc] | GUI desktop; file `.eez-project` (JSON? `TODO`) | Hỗ trợ LVGL 8/9. Claude khó điều khiển → không |
| SquareLine Studio | đóng mã | Personal miễn phí, **không thương mại**, giới hạn 5 màn / 50 widget (thứ cấp – docs SquareLine Vision, giá các gói mâu thuẫn) | GUI + tài khoản | Không |

**Đề xuất:** làm mockup màn TFT trước bằng **HTML đúng kích thước pixel** (vd. 240×320, 320×240) với font/màu thật → Tuan duyệt nhanh.
Chỉ khi chốt dùng LVGL mới dựng project PC + `LV_USE_TEST_SCREENSHOT_COMPARE` để chụp ảnh thật (bước này cũng là test hồi quy UI).
LVGL Pro CLI: **thử 1 buổi** nếu dự án có ≥ 3 màn hình (`TODO` license giáo dục).

### 3.2 Web trên ESP32
| Tên | ★ / push [API] | License | Đánh giá |
|---|---|---|---|
| [ESPUI](https://github.com/s00500/ESPUI) | 1 132 / 2026-04-30 | MIT (file LICENSE; API ghi NOASSERTION) | UI sinh từ code firmware, frontend Skeleton CSS + zepto, WebSocket qua ESPAsyncWebServer, file trong PROGMEM hoặc LittleFS [nguồn gốc]. Đổi style hạn chế → không hợp "giao diện trước" theo token STLab. Thử nếu cần nhanh |
| [esphome-webserver](https://github.com/esphome/esphome-webserver) | 62 / 2026-10-20 | MIT | Frontend Lit của `web_server` (đã chọn cho dự án ESPHome). Không tùy biến token; mockup = chụp thiết bị thật |
| ESP-DASH, ESPAsyncWebServer | — | — | Đã đánh giá ở design-first |

Kích thước: không có số chính chủ cho ESPUI/ESPHome v3 → `TODO` đo khi build. Mốc tham khảo [đo]: JoyStick.js 7 298 B (gzip 2 651 B),
nipplejs 1.0.4 `dist/index.js` 21 359 B (gzip 6 310 B). Quy tắc STLab: 1 file HTML, CSS/JS/SVG nội tuyến, gzip, không CDN.

### 3.3 ESP RainMaker
App RainMaker dựng giao diện từ tham số; kiểu có sẵn trong `esp_rmaker_standard_types.h` [nguồn gốc]: `esp.ui.toggle`, `esp.ui.slider`,
`esp.ui.dropdown`, `esp.ui.text`, `esp.ui.hue-slider`, `esp.ui.hue-circle`, `esp.ui.push-btn-big`, `esp.ui.trigger`, `esp.ui.hidden`,
`esp.ui.qr-scan`. `pump-control` đang dùng toggle/slider/text. Chưa thấy cách đổi màu/bố cục app (`TODO`).
→ Bước 0 cho RainMaker = **bảng "tham số → kiểu UI → nhãn tiếng Việt → thứ tự"** trong `design/brief.md`, sau đó chụp app thật để duyệt.

## 4. UI điều khiển robot

| Tên | ★ / push [API] | License | Cần gì | Đánh giá |
|---|---|---|---|---|
| Foxglove ([repo cũ](https://github.com/foxglove/studio)) | 93 / 2024-07-18, **archived** | Đóng từ bản 2.0 | Tài khoản | Bỏ. 2.0 "discontinues the open source edition" (thứ cấp – thread Open Robotics; miễn phí cho nhóm học thuật) |
| [Lichtblick](https://github.com/Lichtblick-Suite/lichtblick) | 1 186 / 2026-10-22 | MPL-2.0 (BMW, fork Foxglove) | ROS 1/2, MCAP, rosbridge | Chỉ khi có ROS 2 (mảng 2.2 robotics). Không làm mockup |
| [roslibjs](https://github.com/RobotWebTools/roslibjs) | 831 / 2026-10-22 | BSD (file LICENSE) | rosbridge | Như trên |
| [webviz](https://github.com/cruise-automation/webviz) | 2 344 / 2022-12-17 | Apache-2.0 | — | Bỏ (ngừng) |
| [Rerun](https://github.com/rerun-io/rerun) | 11 637 / 2026-10-23 | Apache-2.0 (+MIT) | Python SDK, viewer | LeRobot dùng để xem dữ liệu. Hợp **gỡ lỗi**, không phải UI cho học sinh. Chụp headless `TODO` |
| [LeLab](https://github.com/huggingface/leLab) | 200 / 2026-10-22 | Apache-2.0 | LeRobot | Web teleop/calibrate/record cho SO-arm [nguồn gốc README LeRobot]. Dùng nguyên khi làm lộ trình C, không tự vẽ |
| [JoyStick.js](https://github.com/bobboteck/JoyStick) | 415 / 2026-06-29 | MIT | 1 file, canvas, vanilla | **Dùng** cho ESP32 (nhỏ nhất) |
| [nipplejs](https://github.com/yoannmoinet/nipplejs) | 1 950 / 2026-05-26 | MIT | 1 file UMD | Dùng khi cần đa điểm chạm / 2 joystick (`TODO` kiểm multitouch JoyStick.js) |
| Gamepad API (W3C, trình duyệt) | — | — | Không thư viện | Tay cầm USB/Bluetooth điều khiển robot qua trang web |

**Mẫu màn teleop STLab (đề xuất mockup):** trên điện thoại ngang – joystick trái (di chuyển), nút lớn phải (chế độ/gắp), **nút STOP luôn thấy**
(đỏ `err`, ≥ 44 px, không cần kéo), thanh trạng thái khớp = thanh ngang SVG có số độ (°) và giới hạn, pin (V) + kết nối.
Mỗi thao tác kéo có nút bấm thay thế (WCAG 2.5.7).

## 5. Qt/PySide theme & icon cho workbench FreeCAD

| Tên | ★ / push [API] · bản PyPI | License | Hợp workbench? |
|---|---|---|---|
| [QDarkStyleSheet](https://github.com/ColinDuquesnoy/QDarkStyleSheet) | 3 090 / 2025-07-16 · 3.2.3 (2023-11) | MIT (code) + **CC BY 4.0 (ảnh)** | **Không**: stylesheet toàn app, đè theme FreeCAD |
| [qt-material](https://github.com/UN-GCPDS/qt-material) | 2 870 / 2024-05-16 · 2.17 (2025-04) | BSD-2-Clause | Không, cùng lý do |
| [PyQtDarkTheme](https://github.com/5yutan5/PyQtDarkTheme) | 757 / 2026-10-19 · 2.1.0 (**2022-12**) | MIT | Không (release cũ) |
| [QtAwesome](https://github.com/spyder-ide/qtawesome) | 944 / 2026-08-31 · 1.4.2 (2026-04) | MIT (font icon có license riêng) | Không cần: phải pip vào Python của FreeCAD; SVG file đủ |
| [Lucide](https://github.com/lucide-icons/lucide) / [Tabler](https://github.com/tabler/tabler-icons) | 25 270 / 22 446 | ISC / MIT | **Dùng** (đã chọn). QIcon không hiểu `currentColor` → khi nạp SVG thay `stroke="currentColor"` bằng màu từ `tokens.json`/`palette()` rồi render bằng `QSvgRenderer` |
| [Phosphor](https://github.com/phosphor-icons/core) | 394 / 2026-01-06 (homepage 7 713★) | MIT | Dự phòng: 6 độ đậm (thin→fill), có bản fill dễ thấy ở 16 px |
| [Material Symbols](https://github.com/google/material-design-icons) | 54 158 / 2026-10-23 | Apache-2.0 | Dự phòng: nhiều icon kỹ thuật; font biến – nên lấy SVG lẻ |

**Mockup dialog không cần mở GUI FreeCAD:** viết dialog như module PySide thuần (không import `FreeCADGui` ở tầng widget), chạy bằng Python
có PySide với `QT_QPA_PLATFORM=offscreen`, áp `palette` sáng/tối giả lập từ `tokens.json`, `widget.grab().save("ui/<dialog>-light.png")`.
Rủi ro: font/DPI khác FreeCAD thật; phải khớp PySide2/6 với FreeCAD 1.1 (`TODO`). Ảnh cuối vẫn chụp trong FreeCAD 1 lần.

## 6. Accessibility & điện thoại cho học sinh

- **WCAG 2.2** ([W3C](https://www.w3.org/TR/WCAG22/)) – ngoài 1.4.3 (4,5:1) và 2.5.8 (24 px) đã ghi: **1.4.11 Non-text Contrast** 3:1 cho
  viền nút, joystick, thanh khớp; **2.5.7 Dragging Movements** (AA, mới ở 2.2) – thao tác kéo phải có cách một-điểm-chạm thay thế →
  joystick kèm nút ◀▲▼▶ hoặc STOP; **2.4.11 Focus Not Obscured (Minimum)** – thanh trên cùng `sticky` của Toolhub không được che ô đang focus.
- STLab đã kiểm tương phản bằng `build_tokens.py` (tính trên cặp token) – đủ cho màu. Không kiểm được: nhãn nút, thứ tự focus, vùng bấm.

| Công cụ | ★ / push [API] | License | Chạy | Ghi chú |
|---|---|---|---|---|
| [axe-core](https://github.com/dequelabs/axe-core) | 7 703 / 2026-10-22 | MPL-2.0 | 1 file JS tiêm vào trang | Lõi của pa11y/Lighthouse. Cách nhẹ nhất ở STLab: Playwright Python `channel="msedge"` (dùng Edge có sẵn, không tải trình duyệt) + tiêm `axe.min.js` (`TODO` thử) |
| `@axe-core/cli` 4.14.0 | — | MPL-2.0 | npm | Kéo `chromedriver` + `selenium-webdriver` → nặng |
| [pa11y](https://github.com/pa11y/pa11y) 10.0.0 | 4 582 / 2026-10-19 | LGPL-3.0 | npm | Kéo `puppeteer` (tải Chrome) |
| [Lighthouse](https://github.com/GoogleChrome/lighthouse) | 30 942 / 2026-10-24 | Apache-2.0 | npm/CLI | Gộp hiệu năng + a11y; trỏ Edge qua `CHROME_PATH` (`TODO`) |

Đề xuất: **chưa cài**. Thêm axe khi Toolhub có form nhập liệu nhiều hoặc mở cho học sinh dùng.

## 7. Xếp hạng lợi/công

| # | Việc | Lợi | Công | Đánh đổi |
|---|---|---|---|---|
| 1 | Mẫu HTML mockup dùng `tokens.css` + script chụp Edge headless (light/dark, 375 px, 1280 px, kích thước TFT) dùng chung | Cao | Thấp (~0,5 buổi; đã có `assembly-pdf.py` làm mẫu) | Không có "phong cách phác tay" để duyệt bố cục thô |
| 2 | Mẫu màn teleop ESP32 (JoyStick.js + STOP + thanh khớp + Gamepad API) | Cao (robot 4 chân, xe RC) | Thấp | Chưa đo độ trễ WebSocket thật |
| 3 | Mockup dialog PySide offscreen | Vừa–Cao (tránh GUI crash) | Thấp–Vừa | Ảnh khác FreeCAD thật chút ít |
| 4 | Bảng tham số RainMaker → `esp.ui.*` trong brief | Vừa | Rất thấp | Không có ảnh trước khi flash |
| 5 | Font tiếng Việt cho LVGL bằng `lv_font_conv` | Cao khi có màn TFT | Thấp | Tốn flash (`TODO` đo) |
| 6 | Project LVGL PC + screenshot test | Vừa | Vừa–Cao (SDL/MinGW/CMake) | Chỉ đáng khi chốt dùng LVGL |
| 7 | Thử LVGL Pro CLI (XML + screenshot) | Vừa | Vừa | License giáo dục chưa rõ; công cụ đóng |
| 8 | Mermaid cho luồng màn hình/chế độ robot | Vừa | Thấp (mmdc + Edge) | Thêm 1 công cụ npm |
| 9 | draw.io / Excalidraw cho Tuan tự phác | Thấp–Vừa | Thấp | Hai nguồn sự thật (bản vẽ ≠ code) |
| 10 | Penpot tự host + MCP | Thấp | Cao | Docker, không headless |

## 8. Bộ công cụ bước 0 giao diện đề xuất (≤ 4 thứ mỗi loại)

Nền chung (đã có, không tính): `tokens.json` → `tokens.css` + `DESIGN.md` + skill `frontend-design`; đầu ra `design/ui/*.png` + `contact-sheet.png`.

| Loại | Bộ công cụ | Đánh đổi |
|---|---|---|
| **(a1) Web trên ESP32** | ① 1 file HTML (CSS từ `tokens.css`, icon Tabler SVG nội tuyến, `system-ui`) ② Edge headless chụp 375 px light/dark ③ JoyStick.js khi cần điều khiển ④ ghi kích thước gzip vào brief | Mockup = code thật nên không phác thô; đổi bố cục lớn phải sửa HTML (Claude làm nhanh) |
| **(a2) App RainMaker** | ① bảng tham số → `esp.ui.*` → nhãn Việt ② chụp app thật sau khi flash | Không tùy biến màu/bố cục; duyệt muộn hơn |
| **(a3) Màn LVGL/TFT** | ① HTML đúng pixel màn (240×320…) + Edge chụp ② `lv_font_conv` + Be Vietnam Pro ③ LVGL PC + `LV_USE_TEST_SCREENSHOT_COMPARE` khi chốt ④ (tùy) LVGL Pro CLI | HTML không giống hệt LVGL (anti-alias, font bitmap); bước ③ tốn cài SDL/MinGW |
| **(b) Toolhub Flask** | ① template Jinja thật + dữ liệu giả ② Edge headless 1280/520 px light/dark ③ `build_tokens.py` (tương phản) ④ (sau) axe-core qua Playwright `msedge` | Không có kiểm a11y tự động cho tới khi thêm ④ |
| **(c) Workbench PySide** | ① dialog PySide thuần + `QT_QPA_PLATFORM=offscreen` + `grab()` ② màu từ `tokens.json`/`palette()` ③ icon Tabler/Lucide SVG đổi màu khi nạp | Font/DPI khác FreeCAD; vẫn cần 1 ảnh chụp trong FreeCAD thật |
| **(d) Điều khiển robot** | ① màn teleop HTML (như a1) + JoyStick.js/nipplejs + Gamepad API ② thanh khớp SVG (°, giới hạn) + STOP ③ Mermaid sơ đồ chế độ (idle/teleop/auto/lỗi) ④ LeLab nếu đi LeRobot | Không dùng Foxglove/Lichtblick cho tới khi có ROS 2; tự làm nghĩa là tự lo độ trễ/an toàn mất kết nối |

**An toàn (robot/thiết bị):** mockup phải có trạng thái **mất kết nối** và **STOP** – firmware tự dừng motor khi mất WebSocket (`TODO` thời gian
timeout cụ thể theo dự án). Không đưa mật khẩu Wi-Fi/khóa RainMaker vào HTML mẫu.

## Bảng xem lại khi thương mại

| Thành phần | License / điều kiện | Vấn đề khi thương mại |
|---|---|---|
| LVGL Pro | Community miễn phí cho maker/cá nhân/mã mở; Product 20 000 USD/sản phẩm [nguồn gốc] | Bán thiết bị có UI làm bằng Pro → cần gói trả phí (mã C sinh ra vẫn thuộc mình) |
| SquareLine Studio | Personal: không thương mại (thứ cấp) | Không dùng |
| tldraw | Cấm Production Environment, License Key | Không dùng |
| Foxglove 2.0 | Đóng, trả phí (miễn phí học thuật – thứ cấp) | Không dùng; Lichtblick (MPL-2.0) thay |
| EEZ Studio | GPL-3.0 (công cụ); mã sinh ra thuộc người dùng | Ổn nếu chỉ dùng công cụ |
| draw.io desktop | GPL-3.0 (công cụ) | Ổn – chỉ là công cụ |
| Lichtblick, axe-core, Penpot, D2 | MPL-2.0 | Sửa file của họ thì công bố phần sửa |
| pa11y | LGPL-3.0 | Ổn khi chỉ dùng CLI |
| QDarkStyleSheet | MIT + ảnh CC BY 4.0 | Ghi công nếu dùng ảnh (đã đề xuất không dùng) |
| USWDS | Public domain + icon Apache-2.0 + font OFL | Ổn |

## Điểm chưa xác nhận (TODO)
- Định dạng file `.penpot`, service exporter Penpot tự host; D2 xuất PNG có cần trình duyệt không; cờ CLI draw.io (`--help`).
- `mmdc` dùng Edge có sẵn qua `-p` puppeteer config; Lighthouse với `CHROME_PATH` = Edge; axe qua Playwright `msedge`.
- LVGL: dải ký tự font tích hợp bản 9.6; dung lượng font tiếng Việt; LVGL Pro Community có áp cho trung tâm giáo dục thu phí không.
- EEZ Studio `.eez-project` có phải JSON; JoyStick.js có hỗ trợ đa điểm chạm; Rerun chụp ảnh headless.
- RainMaker app có tùy biến màu/bố cục không; FreeCAD 1.1 Windows dùng PySide2 hay PySide6.
- Kích thước trang ESPUI / ESPHome `web_server` v3 trên flash.
- Quy ước 12 bậc Radix Colors – đọc lại docs chính chủ trước khi áp.

## Nguồn
**[nguồn gốc] repo/README/LICENSE (đọc 2026-10-25):**
[radix-ui/colors](https://github.com/radix-ui/colors) · [radix-ui/themes](https://github.com/radix-ui/themes) · [shadcn-ui/ui](https://github.com/shadcn-ui/ui) ·
[material-web](https://github.com/material-components/material-web) (README: maintenance mode) · [material-color-utilities](https://github.com/material-foundation/material-color-utilities) ·
[carbon](https://github.com/carbon-design-system/carbon) · [fluentui](https://github.com/microsoft/fluentui) · [primer/primitives](https://github.com/primer/primitives) ·
[primer/css](https://github.com/primer/css) · [uswds](https://github.com/uswds/uswds/blob/develop/LICENSE.md) ·
[penpot](https://github.com/penpot/penpot) · [penpot-mcp](https://github.com/penpot/penpot-mcp) · [penpot/mcp](https://github.com/penpot/penpot/tree/develop/mcp) ·
[excalidraw](https://github.com/excalidraw/excalidraw) · [excalidraw-mcp](https://github.com/excalidraw/excalidraw-mcp) ·
[excalidraw-brute-export-cli](https://github.com/realazthat/excalidraw-brute-export-cli) · [tldraw LICENSE](https://github.com/tldraw/tldraw/blob/main/LICENSE.md) ·
[drawio-desktop](https://github.com/jgraph/drawio-desktop) · [drawio](https://github.com/jgraph/drawio) · [mermaid](https://github.com/mermaid-js/mermaid) ·
[mermaid-cli](https://github.com/mermaid-js/mermaid-cli) · [plantuml](https://github.com/plantuml/plantuml) · [d2](https://github.com/d2lang/d2) · [kroki](https://github.com/yuzutech/kroki)

**Nhúng:** [lvgl](https://github.com/lvgl/lvgl) (`lv_conf_template.h`, release v9.6.0) · [lv_port_pc_vscode](https://github.com/lvgl/lv_port_pc_vscode) ·
[lv_web_emscripten](https://github.com/lvgl/lv_web_emscripten) · [lvgl_pro](https://github.com/lvgl/lvgl_pro) · [lv_font_conv](https://github.com/lvgl/lv_font_conv) ·
[eez-open/studio](https://github.com/eez-open/studio) · [ESPUI](https://github.com/s00500/ESPUI) · [esphome-webserver](https://github.com/esphome/esphome-webserver) ·
[esp-rainmaker `esp_rmaker_standard_types.h`](https://github.com/espressif/esp-rainmaker/blob/master/components/esp_rainmaker/include/esp_rmaker_standard_types.h)

**Robot:** [foxglove/studio](https://github.com/foxglove/studio) · [lichtblick](https://github.com/Lichtblick-Suite/lichtblick) · [roslibjs](https://github.com/RobotWebTools/roslibjs) ·
[webviz](https://github.com/cruise-automation/webviz) · [rerun](https://github.com/rerun-io/rerun) · [leLab](https://github.com/huggingface/leLab) · [lerobot README](https://github.com/huggingface/lerobot) ·
[nipplejs](https://github.com/yoannmoinet/nipplejs) · [JoyStick](https://github.com/bobboteck/JoyStick)

**Qt/icon:** [QDarkStyleSheet](https://github.com/ColinDuquesnoy/QDarkStyleSheet) · [qt-material](https://github.com/UN-GCPDS/qt-material) · [PyQtDarkTheme](https://github.com/5yutan5/PyQtDarkTheme) ·
[qtawesome](https://github.com/spyder-ide/qtawesome) · [lucide](https://github.com/lucide-icons/lucide) · [tabler-icons](https://github.com/tabler/tabler-icons) ·
[phosphor core](https://github.com/phosphor-icons/core) · [material-design-icons](https://github.com/google/material-design-icons) (bản PyPI tra pypi.org/pypi/*/json)

**A11y:** [WCAG 2.2](https://www.w3.org/TR/WCAG22/) · [axe-core](https://github.com/dequelabs/axe-core) · [pa11y](https://github.com/pa11y/pa11y) · [lighthouse](https://github.com/GoogleChrome/lighthouse)
(phiên bản/phụ thuộc tra registry.npmjs.org)

**(thứ cấp):** [Foxglove 2.0 – Open Robotics Discourse](https://discourse.openrobotics.org/t/foxglove-2-0-integrated-ui-new-pricing-and-open-source-changes/36583) ·
[SquareLine licenses](https://docs.squareline.io/docs/1.2.0/introduction/licences) · [SquareLine Vision limitations](https://docs.vision.squareline.io/docs/licenses_limitations)

**STLab:** `studio/design/{tokens.json,DESIGN.md,build_tokens.py}` · `studio/toolhub/static/style.css` · `maker/robotics-cad/scripts/assembly-pdf.py` ·
`maker/pump-control/firmware/main` (dùng `ESP_RMAKER_UI_*`) · [design-first-research.md](design-first-research.md)
