# Nghiên cứu: "Giao diện trước" – hình dáng sản phẩm + giao diện phần mềm (STLab)

2026-10-24 · Mục đích: Tuan quyết định **mọi dự án bắt đầu bằng "giao diện"** theo 2 nghĩa:
(A) hình dáng sản phẩm (dáng, vỏ, màu nhựa, render concept), (B) giao diện phần mềm (workbench STLab trong FreeCAD,
Toolhub web, màn hình điều khiển robot). File này tìm công cụ/skill/cộng đồng giúp 2 loại giao diện **đẹp hơn** và đề xuất
**bước 0** trong quy trình. Không lặp lại: `docs/cad-community-gaps-research.md` (dung sai, insert, hướng in),
`docs/freecad-automation-research.md` (code-CAD, Render WB ngừng bảo trì, build123d), `docs/COMMUNITY.md`.
Số sao / ngày đẩy code gần nhất lấy từ GitHub API ngày 2026-10-24. Không cài, không clone, không chạy gì.

## 0. Kết luận nhanh
- **Đã có sẵn, chỉ chưa nối:** `frontend-design`, `theme-factory`, `canvas-design`… nằm trong bản ghim `community/anthropics-skills`
  nhưng `links.tsv` chỉ link docx/pptx/xlsx. Link `frontend-design` = thêm 1 dòng, chỉ markdown, không mạng.
- **Hình dáng:** khoảng trống lớn nhất không phải công cụ mà là **quy trình**: hiện dáng được dựng thẳng trong `build_car.py`
  rồi chụp ảnh FreeCAD (xe cyberbrick-car "dáng còn đơn giản", ảnh màu nhựa bóng, nền trắng). Cần: brief → 3 concept bóng
  (silhouette) → chọn → khối → bảng màu từ **cuộn nhựa có thật** → render Blender (HDRI CC0 Poly Haven qua MCP đã cài).
- **UI phần mềm:** Toolhub đã có token màu + dark mode; workbench STLab **tự đặt màu cứng** (`dialogs.py`, `make_icons.py`) và icon
  là chữ trên ô màu. FreeCAD 1.1 có **hệ token theme** (`@PrimaryColor`, `@AccentColor`…) → workbench nên theo palette/theme.
  Đề xuất một file `DESIGN.md` STLab (token màu/chữ/icon) làm nguồn duy nhất cho Toolhub, workbench, web ESP32.
- **Skill UI cộng đồng:** `nextlevelbuilder/ui-ux-pro-max-skill` (MIT, ~139k★) – phần lõi chỉ đọc CSV cục bộ; **bỏ** các skill con
  gọi Gemini/AtlasCloud/MuAPI. Không có stack Qt/PySide → chỉ hữu ích cho web.
- **AI tạo dáng 3D:** không đáng dùng lúc này (TRELLIS cần ≥ 16 GB VRAM, máy có GTX 1660 SUPER 6 GB; lưới không sửa được trong FreeCAD;
  bản cloud gửi dữ liệu ra ngoài).
- **MakerWorld (thứ cấp):** từ 2026-02-05 ảnh mẫu phải có **ảnh in thật**; render chỉ là phụ → bước 0 làm render để *chọn dáng*,
  không thay ảnh thật.

## 1. Hình dáng sản phẩm

### 1.1 Cộng đồng làm gì
- Quy trình thiết kế chuẩn: **Double Diamond** của Design Council – Discover → Define → Develop → Deliver, mở rộng rồi thu hẹp
  hai lần, không tuyến tính ([Design Council](https://www.designcouncil.org.uk/our-resources/framework-for-innovation/), CC BY 4.0).
  Áp vào STLab: kim cương 1 = brief (ai dùng, 3 từ khóa cảm giác); kim cương 2 = nhiều concept → chọn 1 → hoàn thiện.
- Industrial design cho vật in nhỏ (kinh nghiệm chung, **chưa có nguồn gốc riêng – TODO tìm tài liệu đào tạo ID**):
  phác bóng 2D (hông + đỉnh) trước khi dựng 3D; khối thô (blockout) kiểm tỉ lệ; CMF = Color/Material/Finish; render để chọn.
- **Đa màu trên A1:** AMS lite tối đa 4 cuộn; AMS đầy đủ không dùng được với A1 (FAQ cửa hàng Bambu, tổng hợp – thứ cấp
  [stacksheriff](https://stacksheriff.com/3d-printing/bambu-lab-multicolor-printing/)). Đổi màu phải xả nhựa (prime tower / flush) →
  tốn nhựa ([wiki Bambu – giảm lãng phí](https://wiki.bambulab.com/en/software/bambu-studio/reduce-wasting-during-filament-change),
  chưa đọc được trực tiếp). → STLab: ưu tiên **đổi màu theo chi tiết** (mỗi part 1 màu, lắp lại) thay vì đổi màu trong 1 part.
- **Hoàn thiện bề mặt** trong Bambu Studio: ironing (mặt trên phẳng), fuzzy skin (giấu vân lớp), sơn vị trí seam – forum có
  báo lỗi/vết (thứ cấp: [fuzzy skin seam](https://forum.bambulab.com/t/print-artifacts-when-using-fuzzy-skin/168660),
  [ironing quanh lỗ](https://forum.bambulab.com/t/drag-marks-around-holes-on-ironing-surface/188409)). TODO in mẫu trước khi dùng.
- **Màu PETG Basic:** Bambu ghi mã màu (vd. Black 30105, Red 30201 – forum, thứ cấp
  [forum](https://forum.bambulab.com/t/any-way-to-distinguish-between-old-and-new-petg-basic/257322)); **không tìm được bảng hex
  chính hãng** cho PETG → bảng CMF lấy màu từ **ảnh chụp cuộn thật** trong kho STLab (TODO danh sách cuộn).
- **MakerWorld:** quy định ảnh mẫu – bắt buộc ảnh in thật khớp file, render chỉ chấp nhận khi đúng hình dạng/tỉ lệ
  (thứ cấp: [3Druck](https://3druck.com/en/programs/bambu-lab-takes-stronger-action-against-ai-slop-on-3d-model-platform-makerworld-57153725/),
  [Fabbaloo](https://www.fabbaloo.com/?p=234795); wiki [Featured Model Guidelines](https://wiki.bambulab.com/en/makerworld/tutorials/featured-model-guidelines)
  không tải được – TODO đọc bản gốc).

### 1.2 STLab đang có
- FreeCAD 1.1 + `build_car.py` (dáng sinh từ tham số), `render_car.py` (ảnh FreeCAD, màu từ `colors.json`, nền trắng).
- Blender 5.1 + `ahujasid/mcp-for-blender` (ghim `5a3618f`): đọc mã 2026-10-24 – có tool chụp viewport, tích hợp Poly Haven
  (bật bằng ô `blendermcp_use_polyhaven`, tải từ `api.polyhaven.com`), Sketchfab/Hyper3D/Hunyuan3D (cloud, cần khóa – **không bật**).
- Kiểm in: `printability.py` (không support), quy tắc bề dày vỏ = bội số đường in (0,42 / 0,87 / 1,3 mm).

### 1.3 Khoảng trống
1. **Không có bước concept** – dáng đi thẳng vào mã CAD, nên sửa dáng = sửa hình học thật (đắt, dễ hỏng printability).
2. **Ảnh duyệt chưa "đẹp"**: ảnh FreeCAD (đổ bóng phẳng, màu bão hòa) không cho cảm giác sản phẩm thật → khó chọn dáng.
3. **Không có bảng màu nhựa thật** → render có thể ra màu không in được.
4. **Không có tiêu chí "đẹp" kiểm được** (hiện chỉ có tiêu chí in được).

### 1.4 Công cụ đề xuất cho hình dáng
| Việc | Công cụ | Ghi chú |
|---|---|---|
| Concept bóng 2D (hông/đỉnh/trước) | Script Python (matplotlib/SVG) do Claude sinh từ tham số, hoặc Tuan phác tay rồi chụp | Rẻ nhất; 3 concept trong < 1 giờ |
| Khối thô | FreeCAD Part (loft/fillet) hoặc build123d (đã đánh giá trong `freecad-automation-research.md`) | Không kiểm in ở bước này |
| Bề mặt cong | Loft/Sweep sẵn của FreeCAD | **Không** dùng CurvesWB: README tự ghi "EXPERIMENTAL… should NOT be used for any serious work", cần scipy |
| Render | Blender 5.1 qua MCP đã có: Cycles, view transform mặc định (AgX từ Blender 4.0 – TODO đọc manual 5.1), HDRI studio **CC0** của [Poly Haven](https://polyhaven.com/license) | Một script render chuẩn dùng lại mọi dự án |
| Skill Blender | `RobLe3/cc-blender-skill` (MIT, 120★): ~30 skill thuần markdown + `wireframe_analyzer.py`, chạy qua `execute_blender_code`; cần opencv/numpy/scipy/Pillow; README: thử thật trên Blender 5.1.1, **chưa kiểm** với Claude Code | **Thử sau**; đọc mã trước khi ghim |
| MCP Blender chính thức | [Blender Lab MCP](https://www.blender.org/lab/mcp-server/) (cần Blender ≥ 5.1, add-on v1.0.3; chạy Python do LLM sinh "without any guards") | Theo dõi; license TODO; **trùng cổng 9876** với addon đang dùng |
| AI concept ảnh/3D | ComfyUI cục bộ (GPL-3.0, 142k★) / TripoSR (MIT, ~6 GB VRAM) / Hunyuan3D-2 (license Tencent riêng, 6 GB chỉ hình khối) / TRELLIS (≥ 16 GB, Linux) | **Không** lúc này: lưới AI không thành CAD tham số; cloud (Hyper3D, Gemini) gửi dữ liệu + cần khóa API; license ảnh/model phải xem riêng |

## 2. Giao diện phần mềm

### 2.1 Skill/agent Claude cho UI
- **anthropics/skills** (bản ghim `dbd4588`, commit 2026-10-09; Apache-2.0 từng skill): đọc mã 2026-10-24.
  - `frontend-design`: chỉ `SKILL.md`. Quy trình 2 lượt: lập token (4–6 màu hex, chữ, layout ASCII) → soát với brief → mới viết code →
    tự chụp màn hình phê bình; liệt kê "dấu hiệu UI do AI sinh" cần tránh; sàn chất lượng: responsive, focus bàn phím,
    reduced motion. **Dùng** cho Toolhub, web ESP32, mockup.
  - `theme-factory`: 10 theme màu/chữ + `theme-showcase.pdf`, chỉ markdown → **thử** cho tài liệu/slide STLab.
  - `canvas-design`: markdown + font OFL, ra PNG/PDF (đã có sẵn dạng plugin `anthropic-skills:canvas-design`) → thử cho bảng mood/CMF.
  - `web-artifacts-builder`: `init-artifact.sh` chạy `npm install -g pnpm`, `pnpm create vite`, cài React/Tailwind/shadcn + ~25 gói Radix
    từ npm → **không** (Toolhub là Flask không build; ESP32 cần trang nhỏ).
  - `webapp-testing`: Playwright (cài pip + tải trình duyệt), `with_server.py` dùng `subprocess` → **không cần**: STLab đã chụp bằng
    Edge headless (`assembly-pdf.py`).
- **nextlevelbuilder/ui-ux-pro-max-skill** (MIT, 139 460★, đẩy 2026-10-23, release v2.15.0, commit `d14efff8ed1f`). Đọc mã 2026-10-24:
  - `.claude/skills/ui-ux-pro-max/`: `search.py`, `core.py`, `design_system.py` chỉ dùng thư viện chuẩn (csv, re, json) đọc CSV cục bộ
    (79 style, 192 bảng màu, 74 cặp font, 119 quy tắc UX). **Không mạng, không subprocess.** Stack có html-tailwind, react, flutter…
    **không có Qt/PySide**.
  - `design/scripts/{logo,icon,cip}/generate.py`: gọi **Gemini** (`GEMINI_API_KEY`), **AtlasCloud**, **MuAPI**, đọc `.env` → không dùng.
  - `design-system/scripts/fetch-background.py`: tải ảnh Pexels → không dùng.
  - CLI npm `ui-ux-pro-max-cli` tải từ GitHub → không dùng; nếu ghim thì **sparse chỉ thư mục `ui-ux-pro-max`**.
  - Lưu ý: số sao tăng rất nhanh, README nhiều quảng bá/donate → tin cậy "cộng đồng", không phải chính thức. → **Thử**.
- **VoltAgent/awesome-design-md** (MIT, 123k★): bộ `DESIGN.md` phân tích từ website các hãng. Khái niệm DESIGN.md (file markdown mô tả
  hệ thiết kế cho agent, từ Google Stitch) **đáng lấy**; nội dung là nhận diện hãng khác → **không ghim**, STLab tự viết DESIGN.md.
- `google-labs-code/stitch-skills` (Apache-2.0, 8,5k★): gắn với dịch vụ Google Stitch (cloud) → không.

### 2.2 Workbench STLab trong FreeCAD (PySide)
- **FreeCAD 1.1** (bản mới nhất 1.1.4, 2026-09-28) có sẵn pack `FreeCAD Light`, `FreeCAD Dark`, `FreeCAD Classic`, `Dark behave`
  ([mã nguồn PreferencePacks](https://github.com/FreeCAD/FreeCAD/tree/releases/FreeCAD-1-1/src/Gui/PreferencePacks)) và hệ **style
  parameters**: `FreeCAD.qss` dùng token `@PrimaryColor`, `@AccentColor`, `@GeneralBorderColor`…, giá trị trong
  `Stylesheets/parameters/FreeCAD Light.yaml` (vd. `GeneralBorderColor: "@PrimaryColorDarken4"`)
  ([FreeCAD.qss](https://github.com/FreeCAD/FreeCAD/blob/releases/FreeCAD-1-1/src/Gui/Stylesheets/FreeCAD.qss)).
  Chưa tìm thấy API Python đọc token (`ApplicationPy.cpp` không có) → TODO; cách chắc chắn: dùng `palette(...)` của Qt trong stylesheet.
- **Workbench hiện tại**: `dialogs.py` đặt cứng `COLOR = {"FAIL": "#d9534f", …}` và `color:#b07000`; `make_icons.py` sinh icon = **chữ trên ô
  bo tròn màu theo bước** ("LK", "BOM", "45°"). Trên theme tối, chữ/nền cứng dễ lệch; icon chữ khó phân biệt ở 16 px (cây đối tượng).
- **Quy chuẩn icon FreeCAD** (wiki [Artwork Guidelines](https://wiki.freecad.org/Artwork_Guidelines) – wiki chặn bot, tóm tắt từ kết quả
  tìm kiếm, **thứ cấp**): vẽ SVG 64 × 64 px (vùng dùng 60 × 60, lề 2 px), hiển thị 64/32/16 px; bảng màu phỏng theo Tango, viền là tông
  rất tối của màu nền (không đen); quy ước màu: vàng = tạo đối tượng, xanh dương = sửa, xanh mòng két = xem, đỏ = ràng buộc.
- **OpenTheme** (obelisk79, LGPL-2.1, 134★, đẩy 2026-10-20, bản v2026.10.05): theme OpenLight/OpenDark dựa trên Open-Color, kiểm
  WCAG/APCA, **dùng token của FreeCAD 1.1** (stylesheet không chứa màu). Chỉ là `.qss/.yaml/.cfg/.svg`; `tools/` là script build cho dev.
  README cảnh báo áp preference pack là **một chiều** → sao lưu `user.cfg`. → **Thử** (để Tuan dễ nhìn), không bắt buộc.
- ProDark: là nguồn gốc stylesheet mặc định 1.1 ("based on … Pablo Gil Fernández made by MisterMaker" trong `FreeCAD.qss`) → không cần cài riêng.

### 2.3 Web: Toolhub (Flask) và trang điều khiển ESP32
- Toolhub đã có token CSS (`--bg`, `--accent`, `--ok`, `--warn`…) + `prefers-color-scheme: dark`, ít ký hiệu (vài mũi tên ← →, ⏳, ✓).
  Thiếu: bộ icon SVG thống nhất, ảnh concept/render trên thẻ dự án.
- **Pico CSS: không** – repo đã archive, README: "Pico CSS is no longer maintained", v2.1.1 là bản cuối ([README](https://github.com/picocss/pico)).
- **Open Props** (MIT, 5,5k★, release cuối v1.6.0 năm 2023, vẫn có commit 2026-10): bộ biến CSS → chỉ tham khảo thang khoảng cách/bóng;
  Toolhub đã có token riêng → không cần.
- **Icon:** [Tabler Icons](https://github.com/tabler/tabler-icons) (MIT, 22k★, v3.49.0) hoặc [Lucide](https://github.com/lucide-icons/lucide)
  (ISC, 25k★, 1.61.0): SVG nét đơn, chép **từng file cần** vào repo (không CDN – ESP32/LAN không có mạng). Dùng chung cho Toolhub,
  web ESP32 và làm hình vẽ trên icon workbench.
- **ESP32:**
  - Dự án ESPHome: `web_server` có `version: 3` (giao diện kiểu Home Assistant), `local: true` nhúng CSS/JS vào flash (không cần internet),
    `auth` khuyên `type: digest` (basic gửi mật khẩu Base64) ([ESPHome docs](https://esphome.io/components/web_server/)). → **Dùng**.
  - Arduino/ESP-IDF tự viết: một file HTML (token từ DESIGN.md + icon SVG nội tuyến) gzip vào flash, phục vụ bằng
    `ESP32Async/ESPAsyncWebServer` (LGPL-3.0, 666★). → **Dùng** (mẫu do Claude viết theo `frontend-design`).
  - `ayushsharma82/ESP-DASH` (GPL-3.0, 1,4k★): dashboard dựng sẵn, có bản **Pro trả phí** → thử nếu cần nhanh; ghi bảng "thương mại".
  - App CyberBrick: ứng dụng hãng, chỉ chọn cấu hình kênh; chưa thấy cách tùy biến giao diện → TODO (`CyberBrick_Controller_Core` 234★).
- Chuẩn kiểm được: tương phản chữ ≥ 4,5:1 (WCAG 2.2 SC 1.4.3, [W3C](https://www.w3.org/TR/WCAG22/#contrast-minimum)); vùng bấm ≥ 24 × 24 px
  (SC 2.5.8 AA; 44 px là mức AAA 2.5.5 – nên dùng cho màn hình điện thoại điều khiển robot).

## 3. Bảng đề xuất nguồn
| Tên | Link | ★ / cập nhật | License | Chạy gì / gọi mạng? | Dùng cho | Khuyến nghị |
|---|---|---|---|---|---|---|
| frontend-design (anthropics/skills) | [link](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | 183k / ghim 2026-10-09 (đã có) | Apache-2.0 | Chỉ markdown, không mạng | Toolhub, web ESP32, mockup | **Dùng** (thêm 1 dòng links.tsv) |
| theme-factory, canvas-design | cùng repo | như trên | Apache-2.0 (font OFL) | Markdown + font/PDF, không mạng | Bảng mood/CMF, tài liệu | Thử |
| web-artifacts-builder | cùng repo | như trên | Apache-2.0 | `pnpm`/npm cài ~40 gói | — | Không |
| ui-ux-pro-max (chỉ thư mục lõi) | [link](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 139k / 2026-10-23 | MIT | Python stdlib đọc CSV, không mạng (skill con `design` gọi Gemini/AtlasCloud/MuAPI – loại) | Tra bảng màu/font/quy tắc UX web | Thử (sparse) |
| awesome-design-md | [link](https://github.com/VoltAgent/awesome-design-md) | 123k / 2026-10-14 | MIT | Chỉ markdown | Khái niệm DESIGN.md | Không ghim, học cách viết |
| FreeCAD Light/Dark + token 1.1 | [mã nguồn](https://github.com/FreeCAD/FreeCAD/tree/releases/FreeCAD-1-1/src/Gui/Stylesheets) | có sẵn 1.1.4 | LGPL-2.1 (FreeCAD) | Có sẵn | Workbench theo theme | **Dùng** |
| OpenTheme | [link](https://github.com/obelisk79/OpenTheme) | 134 / 2026-10-20 | LGPL-2.1 | qss/yaml/svg; pack ghi đè cài đặt (một chiều) | Theme FreeCAD dễ đọc | Thử (sao lưu user.cfg) |
| CurvesWB | [link](https://github.com/tomate44/CurvesWB) | 159 / 2026-10-12 | LGPL-2.1+ | Python + numpy/scipy | Mặt NURBS | Không (tác giả ghi thử nghiệm) |
| mcp-for-blender + Poly Haven | [link](https://github.com/ahujasid/mcp-for-blender) | 32k / 2026-10-20 (đã ghim) | MIT; asset **CC0** | Tải HDRI từ api.polyhaven.com (chỉ gửi truy vấn tìm) | HDRI studio cho render | **Dùng** (bật ô Poly Haven; giữ tắt Hyper3D/Sketchfab/Hunyuan) |
| Blender Lab MCP (chính thức) | [link](https://projects.blender.org/lab/blender_mcp) | v1.0.3 (thứ cấp) | TODO | Chạy Python do LLM sinh, không chặn | Thay MCP cộng đồng sau này | Theo dõi |
| cc-blender-skill | [link](https://github.com/RobLe3/cc-blender-skill) | 120 / TODO | MIT | Markdown + 1 script; cần opencv/scipy; dùng tool tải Poly Haven/Sketchfab/Hyper3D | Quy trình render sản phẩm | Thử sau (đọc mã trước) |
| Tabler Icons / Lucide | [Tabler](https://github.com/tabler/tabler-icons) · [Lucide](https://github.com/lucide-icons/lucide) | 22k / 25k, 2026-10-23 | MIT / ISC | SVG tĩnh | Icon Toolhub, ESP32, workbench | **Dùng** (chép file lẻ) |
| ESPHome web_server v3 | [docs](https://esphome.io/components/web_server/) | — | ESPHome (MIT/GPL – TODO) | Chạy trên ESP32, `local: true` không cần mạng | Web điều khiển dự án ESPHome | **Dùng** |
| ESPAsyncWebServer | [link](https://github.com/ESP32Async/ESPAsyncWebServer) | 666 / 2026-10-15 | LGPL-3.0 | Thư viện firmware | Web tự viết (Arduino) | Dùng |
| ESP-DASH | [link](https://github.com/ayushsharma82/ESP-DASH) | 1,4k / 2026-10-16 | GPL-3.0 (+ Pro trả phí) | Thư viện firmware | Dashboard nhanh | Thử |
| Pico CSS | [link](https://github.com/picocss/pico) | 16,8k, **archived** | MIT | — | — | Không (ngừng bảo trì) |
| Open Props | [link](https://github.com/argyleink/open-props) | 5,5k, release 2023 | MIT | CSS | Tham khảo thang token | Không cần |
| TRELLIS / TripoSR / Hunyuan3D-2 | [TRELLIS](https://github.com/microsoft/TRELLIS) · [TripoSR](https://github.com/VAST-AI-Research/TripoSR) · [Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) | 14k / 7k / 15k | MIT / MIT / Tencent (TODO) | Model PyTorch cục bộ, GPU ≥ 16 / ~6 / 6 GB | Ảnh → lưới 3D | Không (lưới ≠ CAD; GPU yếu) |
| ComfyUI | [link](https://github.com/Comfy-Org/ComfyUI) | 142k / 2026-10-24 | GPL-3.0 | Cục bộ; model tải riêng (license từng model) | Ảnh concept | Không lúc này (Tuan quyết) |

Thêm vào bảng "Xem lại khi làm thương mại" nếu dùng: ESP-DASH (GPL-3.0 + Pro), Hunyuan3D-2 (license Tencent), model ảnh AI (theo từng model).

## 4. Đề xuất bước 0 "Giao diện trước"

### 4.1 Đầu ra (thư mục mới `maker/<project>/design/`, ảnh là chính – Tuan duyệt bằng ảnh)
```
design/
  brief.md                 1 trang: dùng cho ai, ở đâu; 3 từ khóa cảm giác; ràng buộc (bàn 256 mm, không support, linh kiện chính)
  concepts/                A-*.png, B-*.png, C-*.png: mỗi concept = bóng hông + bóng đỉnh + phối cảnh 3/4
  cmf.png                  bảng màu: chỉ cuộn nhựa CÓ THẬT (ảnh cuộn + tên + mã Bambu), tối đa 3 màu/sản phẩm
  render/                  concept đã chọn: 3/4 trước, hông, sau – Blender, HDRI studio CC0
  ui/                      mockup: <screen>-light.png, <screen>-dark.png, <screen>-375px.png (điện thoại)
  contact-sheet.png        1 ảnh gom tất cả để Tuan chọn (đánh dấu A/B/C)
```
Quyết định ghi 1 dòng vào `README.md` mục "Lịch sử sửa" (vd. "2026-10-25: chọn concept B, màu Đen 30105 + Cam"), không tạo file .txt.

### 4.2 Hai phiên bản theo loại dự án
| Loại | Bước 0 gồm | Thời gian ước |
|---|---|---|
| Có vỏ/nhìn thấy (xe, robot, hộp smart home) | brief + 3 concept bóng + chọn + khối thô + cmf + render | 1–2 buổi |
| Có UI (web ESP32, trang Toolhub, lệnh workbench) | brief + token theo DESIGN.md + 2 mockup (light/dark, 375 px) | 0,5–1 buổi |
| Thuần cơ khí (gá, bracket) | rút gọn: 1 ảnh khối thô + màu | ≤ 30 phút |
(buổi ≈ 3–4 giờ; số ước, chưa đo – TODO ghi lại thời gian thật sau 2 dự án.)

### 4.3 Checklist "đẹp" duyệt bằng ảnh (kiểm được)
Hình dáng:
- [ ] Nhìn **bóng đen** ở hông/đỉnh vẫn nhận ra sản phẩm; 3 concept khác nhau rõ (không phải 3 biến thể 1 dáng).
- [ ] Tối đa 3 màu (chính / phụ / nhấn), mỗi màu là cuộn có trong kho; **mỗi chi tiết 1 màu** (không đổi màu giữa part nếu không cần).
- [ ] Đường chia chi tiết nằm ở cạnh/khe chủ ý, không cắt ngang mặt lớn; bo/vát dùng ≤ 2 kích thước lặp lại.
- [ ] Mặt lớn nhìn thấy không là mặt úp xuống/support; vết seam đặt phía sau hoặc ở cạnh (TODO in mẫu kiểm).
- [ ] Chi tiết nổi/chữ ≥ 1 đường in (0,42 mm); vỏ theo bội số đường in (quy ước `robotics-cad/CLAUDE.md`).
- [ ] Concept chọn xong vẫn qua `printability.py` khi sang CAD thật (bước 0 không được tạo dáng in không nổi).
Giao diện phần mềm:
- [ ] Màu chỉ lấy từ token DESIGN.md / palette FreeCAD; không hex cứng trong mã giao diện.
- [ ] Tương phản chữ ≥ 4,5:1; nút trên điện thoại ≥ 44 px; có trạng thái focus, lỗi, đang chạy, rỗng.
- [ ] Đúng ở light + dark và 375 px; icon SVG (Tabler/Lucide), không emoji.
- [ ] Web ESP32 chạy không cần internet (không CDN); có đăng nhập digest nếu điều khiển động cơ.

### 4.4 Ai làm, công cụ
| Việc | Ai | Công cụ |
|---|---|---|
| brief | Tuan nói 3–5 câu, Claude viết | `grill-me` (đã có) để hỏi ngược |
| 3 concept bóng + khối thô | Claude | script Python/SVG; FreeCAD loft (headless `freecadcmd`) |
| cmf | Tuan chụp cuộn nhựa 1 lần → Claude dựng `cmf.png` | ảnh thật |
| render | Claude | Blender MCP + HDRI Poly Haven; script render chuẩn dùng chung (đề xuất `tools/robotics-cad/scripts/render-concept.py`) |
| mockup UI | Claude | `frontend-design` → HTML → PNG bằng Edge headless (như `assembly-pdf.py`); workbench: `widget.grab()` (đã dùng 2026-10-24) |
| **chọn** | **Tuan** (có thể cho học sinh bình chọn) | `contact-sheet.png` |

### 4.5 Nối vào project-template và /new-project
- `project-template/design/brief.md` (mẫu có chỗ trống) + `design/README` ngắn trong `project-template/CLAUDE.md` mục "Bước 0".
- `/new-project` (`.claude/commands/new-project.md`): thêm bước "tạo `design/`, hỏi loại dự án (vỏ / UI / cơ khí) rồi đề nghị chạy bước 0
  trước khi dựng CAD". `tools/robotics-cad/CLAUDE.md` mục Quy trình: thêm **0. Giao diện trước** đứng trước bước 1.
- Toolhub › Dự án: thẻ dự án hiện `design/contact-sheet.png` (hoặc render đã chọn) thay ảnh FreeCAD.
- Workbench: thêm bước "0 Giao diện" (mở `design/`, xem contact sheet) – sau khi Tuan duyệt quy trình.
- Nếu lặp lại nhiều: viết skill riêng `custom/skills/design-first` (lý do: chưa có nguồn cộng đồng gộp ID + in FDM + Blender).

## 5. Top 5 việc nên làm
1. **Link `frontend-design`** từ bản ghim anthropics-skills vào `~/.claude/skills` (1 dòng `links.tsv` + `update-community.sh link`). 10 phút, không rủi ro.
2. **Viết `studio/DESIGN.md`** (token màu/chữ/khoảng cách/icon của STLab) và gom màu cứng về một nguồn: `style.css` Toolhub,
   `dialogs.py` + `make_icons.py` workbench (theo `palette()` của Qt), mẫu trang ESP32. Icon: Tabler/Lucide SVG. ~1 buổi.
3. **Thêm bước 0 vào quy trình**: `project-template/design/`, `/new-project`, `robotics-cad/CLAUDE.md` (mục 4.5). ~0,5 buổi.
4. **Thí điểm trên cyberbrick-car** (thân xe đang "tròn đơn giản"): 3 concept bóng → khối thô → `cmf.png` từ cuộn thật → render Blender
   → contact sheet cho Tuan chọn → mới sửa `build_car.py`. 1–2 buổi.
5. **Script render chuẩn** Blender (`render-concept.py`: nhập STL/STEP theo màu Label, HDRI studio CC0, 3 góc, nền trung tính) dùng lại
   cho bước 0 và ảnh tài liệu/MakerWorld (ảnh phụ – ảnh chính vẫn là ảnh in thật). ~1 buổi.

## 6. Cần Tuan quyết
1. Bước 0 **bắt buộc mọi dự án** hay theo 3 mức (vỏ / UI / cơ khí rút gọn ≤ 30 phút) như 4.2?
2. Danh sách **cuộn nhựa đang có** (màu, hãng, mã) để làm bảng CMF – hay mua thêm theo concept?
3. Ghim `ui-ux-pro-max` (sparse, chỉ lõi) hay chỉ dùng `frontend-design`?
4. Có cho dùng **AI tạo ảnh concept** (ComfyUI cục bộ, license từng model) không? Đề xuất: chưa – phác bóng bằng script đủ dùng.
5. Icon workbench: giữ **chữ + màu theo bước** (dễ đọc với học sinh) hay đổi sang **hình vẽ theo quy chuẩn FreeCAD** (màu theo chức năng)?
   Đề xuất: hình vẽ (Tabler) + giữ huy hiệu số bước.
6. Theme FreeCAD: mặc định FreeCAD Light/Dark hay thử OpenTheme (sao lưu `user.cfg` trước)?
7. Khi Blender Lab MCP chính thức ổn định: chuyển sang (cùng cổng 9876) hay giữ ahujasid?

## Điểm chưa xác nhận (TODO)
- Wiki FreeCAD chặn bot (Anubis): quy chuẩn icon và release notes 1.1 chỉ có qua kết quả tìm kiếm (thứ cấp); API Python đọc token theme chưa thấy.
- Quy định ảnh MakerWorld (2026-02-05) chỉ từ báo/forum (thứ cấp); wiki Bambu trả 402.
- Không có bảng mã hex chính hãng cho màu PETG Basic; license Blender Lab MCP; license Hunyuan3D-2; ngày commit cc-blender-skill.
- View transform mặc định Blender 5.1 (AgX?) – chưa đọc manual 5.1. Hiệu quả ironing/fuzzy skin trên PETG A1 – chưa in thử.
- App CyberBrick có tùy biến giao diện được không.

## Nguồn
- Design Council – Framework for Innovation (Double Diamond): https://www.designcouncil.org.uk/our-resources/framework-for-innovation/
- anthropics/skills: https://github.com/anthropics/skills (đọc bản ghim `community/anthropics-skills`)
- ui-ux-pro-max-skill: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (đọc `SKILL.md`, `scripts/*.py` ngày 2026-10-24)
- awesome-design-md: https://github.com/VoltAgent/awesome-design-md · stitch-skills: https://github.com/google-labs-code/stitch-skills
- FreeCAD 1.1 PreferencePacks / Stylesheets: https://github.com/FreeCAD/FreeCAD/tree/releases/FreeCAD-1-1/src/Gui
- FreeCAD Artwork Guidelines: https://wiki.freecad.org/Artwork_Guidelines (thứ cấp, qua tìm kiếm) · Preference Packs: https://wiki.freecad.org/Preference_Packs
- OpenTheme: https://github.com/obelisk79/OpenTheme · CurvesWB: https://github.com/tomate44/CurvesWB
- mcp-for-blender: https://github.com/ahujasid/mcp-for-blender (đọc `addon.py` bản ghim) · Poly Haven license: https://polyhaven.com/license
- Blender Lab MCP: https://www.blender.org/lab/mcp-server/ · https://projects.blender.org/lab/blender_mcp
- cc-blender-skill: https://github.com/RobLe3/cc-blender-skill
- TRELLIS: https://github.com/microsoft/TRELLIS · TripoSR: https://github.com/VAST-AI-Research/TripoSR · Hunyuan3D-2: https://github.com/Tencent-Hunyuan/Hunyuan3D-2 · ComfyUI: https://github.com/Comfy-Org/ComfyUI
- Pico CSS (archived): https://github.com/picocss/pico · Open Props: https://github.com/argyleink/open-props
- Tabler Icons: https://github.com/tabler/tabler-icons · Lucide: https://github.com/lucide-icons/lucide
- ESPHome web_server: https://esphome.io/components/web_server/ · ESPAsyncWebServer: https://github.com/ESP32Async/ESPAsyncWebServer · ESP-DASH: https://github.com/ayushsharma82/ESP-DASH
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Bambu (thứ cấp): https://stacksheriff.com/3d-printing/bambu-lab-multicolor-printing/ · https://wiki.bambulab.com/en/software/bambu-studio/reduce-wasting-during-filament-change ·
  https://forum.bambulab.com/t/any-way-to-distinguish-between-old-and-new-petg-basic/257322 · https://forum.bambulab.com/t/print-artifacts-when-using-fuzzy-skin/168660
- MakerWorld (thứ cấp): https://3druck.com/en/programs/bambu-lab-takes-stronger-action-against-ai-slop-on-3d-model-platform-makerworld-57153725/ ·
  https://www.fabbaloo.com/?p=234795 · https://wiki.bambulab.com/en/makerworld/tutorials/featured-model-guidelines
