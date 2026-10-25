# Nghiên cứu: video hướng dẫn, hashtag/SEO và quy trình nội dung cho mỗi dự án FreeCAD (STLab)

Ngày: 2026-10-24 · Người làm: Claude (agent nghiên cứu) · Trạng thái: **chỉ nghiên cứu**, chưa cài/chạy/commit gì.

**Mục đích:** với mỗi dự án `maker/<project>/` tạo ra (a) clip giới thiệu, (b) video hướng dẫn học sinh, (c) caption + hashtag.
Trả lời: cộng đồng có mã nguồn mở nào hỗ trợ, và luồng làm việc chuẩn.
**Không lặp lại** (xem file kia): thông số Reels/Shorts/TikTok, hook 3 s, FFmpeg, Blender, Remotion/MoviePy/Manim, TTS, nhạc, pháp lý học sinh,
4 mẫu A–D → `docs/project-video-marketing-research.md` (§1–§5). Trend/series/lịch → `docs/trend-content-ideas.md`. Reel từ ảnh →
`video-ai/scripts/make_reel.py` (`video-ai/CLAUDE.md`). Chạy FreeCAD CLI/GUI → `docs/freecad-automation-research.md` §7.

Ký hiệu: (thứ cấp) = không phải nguồn hãng/repo chính · `TODO` = chưa xác minh · ★ = sao GitHub đọc ngày 2026-10-24 · **GỢI Ý** = không có số liệu.

## 0. Kết luận nhanh
- **Không có công cụ cộng đồng nào làm trọn "dự án FreeCAD → video hướng dẫn"**. Ghép từ khối có sẵn: OBS Studio (quay màn hình) +
  obs-websocket (đã kèm OBS ≥ 28, script bắt đầu/dừng quay **và đánh dấu chương**) + Keyviz (hiện phím/chuột) + script FreeCAD tự viết
  (build-replay, mô phỏng) + `make_reel.py`/FFmpeg đã có.
- **"Build replay" (dựng lại từng feature) – không tìm thấy macro/workbench cộng đồng.** Tự viết được: duyệt `Body.Group`, mỗi feature PartDesign
  mang hình khối tích lũy đến bước đó → hiện từng feature + `ActiveView.saveImage` → chuỗi PNG. Chạy qua `gui_run.py` (cần GUI để chụp). Đây là
  phần có giá trị nhất cho video học sinh: không cần quay tay, tự cập nhật khi model đổi.
- **Assembly Simulation trong FreeCAD 1.1 không có nút xuất video** (chỉ phát trong task panel). Nút xuất MP4/GIF/AVI có ở nhánh `main` (26.3,
  chưa phát hành) và mã của nó chỉ là vòng `updateForFrame(i)` + `saveImage` → **chép đúng mẫu này vào script của STLab chạy được trên 1.1**.
- **Render workbench (FreeCAD-render) đã ngừng bảo trì từ 12/11/2025** → không đầu tư; ảnh đẹp dùng Blender (file kia §2.1).
- **Hashtag không đưa video "lên top".** Nguồn chính thức: TikTok xếp hạng theo tương tác + xem hết video (tín hiệu mạnh), hashtag/caption chỉ là
  "thông tin video"; `#fyp` không có tác dụng đặc biệt. YouTube đề xuất theo click, thời gian xem, khảo sát hài lòng, chia sẻ, like. → Ưu tiên
  **hook + giữ chân + từ khóa đúng trong tiêu đề/caption/lời nói**, hashtag 3–5 cái đúng chủ đề.
- **Giới hạn hashtag hiện hành:** Instagram **5/bài** (từ 12/2025, @creators – thứ cấp, Help Center chưa đọc được); YouTube > 60 hashtag → bỏ qua tất
  cả, 3 cái hiện trên tiêu đề; Facebook: chỉ là liên kết chủ đề, không có giới hạn/khuyến nghị chính thức tìm được.
- **Luồng chuẩn = 1 nội dung gốc → nhiều phái sinh:** bài hướng dẫn dài 16:9 trên YouTube (chương, file FCStd, phiếu bài tập) là gốc; Shorts/Reels/TikTok
  cắt từ build-replay/mô phỏng trỏ về video dài bằng tính năng **"Related video" chính thức của YouTube Shorts**.
- Công cụ trend/hashtag mã nguồn mở hầu hết **scrape TikTok – vi phạm ToS mục 5** ("automated scripts to collect information"). Không dùng; Tuan tra
  Creative Center/Creator Search Insights bằng tay, Claude soạn caption.

## 1. Video hướng dẫn học sinh từ dự án FreeCAD

### 1.1 Quay màn hình (FreeCAD thao tác thật)
| Việc | Công cụ | Ghi chú đã kiểm |
|---|---|---|
| Quay | **OBS Studio** (GPL-2.0) | Bản 32.1 (02/04/2026) thêm "partial support for Canvases to obs-websocket" ([RN 32.1](https://obsproject.com/blog/obs-studio-32-1-release-notes)). **Lõi OBS chưa có canvas dọc thứ hai** – không thấy trong RN 32.1/32.2 (32.2 nhắc copy/paste cho "users from the vertical plugin", thứ cấp). |
| Canvas dọc song song | **Aitum Vertical** (`Aitum/obs-vertical-canvas`, 328★, GPL-2.0) | Forum OBS: v1.6.4, tối thiểu OBS 29; 1.6.3 sửa lỗi cho OBS 32.1; có báo crash với OBS 31.0.3 + plugin 1.5.2 ([forum](https://obsproject.com/forum/resources/aitum-vertical.1715/)). **Không cần cho STLab**: giao diện FreeCAD là ngang → quay **16:9 1920×1080**; bản dọc lấy từ ảnh build-replay xuất thẳng 1080×1920. |
| Script điều khiển | **obs-websocket 5** (4,4k★, GPL-2.0) – "included by default with OBS Studio 28.0.0 and above" ([repo](https://github.com/obsproject/obs-websocket)) | Request có trong [protocol.md](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md): `StartRecord`, `StopRecord` (trả `outputPath`), `PauseRecord`, `SetCurrentProgramScene`, `SaveSourceScreenshot`, **`CreateRecordChapter`** – "only file format supporting this feature is Hybrid MP4" (OBS ≥ 30.2). → Script vừa quay vừa ghi mốc chương → sinh `chapters.txt` cho YouTube. |
| Client Python | `obsws-python` (Python ≥ 3.10, đồng bộ) hoặc `simpleobsws` (asyncio) – cả hai do README obs-websocket liệt kê | Mật khẩu websocket để trong biến môi trường (`OBS_WS_PASSWORD`), không ghi vào file. Cổng mặc định 4455 – `TODO` xác nhận trong Settings của máy. |
| Hiện phím + chuột | **Keyviz** (`mulaRahul/keyviz`, 9,7k★, GPL-3.0) | Có bản cài Windows/macOS; "Display mouse clicks and scroll wheel movements" ([repo](https://github.com/mulaRahul/keyviz)). Ngày release `TODO`. **Khuyến nghị.** |
| | Carnac (`Code52/carnac`, 4,6k★, MS-PL) | Chỉ phím; trang repo không cho thấy ngày commit/release → mức bảo trì `TODO`. Dự phòng. |
| | KeyCastOW (`brookhong/KeyCastOW`, MIT theo README) | Ngừng phát triển (~2017–2019, thứ cấp: [AlternativeTo](https://alternativeto.net/software/keycastow/about)). Không dùng. |

**Mẹo FreeCAD khi quay (GỢI Ý):** cửa sổ FreeCAD cố định 1920×1080, scale font UI ≥ 125 %, tắt panel không dùng, bật Keyviz chỉ cho phím tắt
(Sketcher: G-L, K-D…), dùng Window Capture (không Display Capture) để không lộ thông báo/tin nhắn. Rủi ro: GUI FreeCAD hay crash (memory
`freecad-cli-truoc`) → lưu file trước khi quay, quay từng đoạn ngắn (khớp nguyên tắc segmenting §1.4).

### 1.2 Build replay – video "dựng từng bước" không cần quay tay
- **Tìm cộng đồng:** không thấy macro/workbench nào chụp lần lượt từng feature thành video (tìm wiki Macros, forum, GitHub, kết quả chỉ có
  PDWrapper – không liên quan). Một trả lời trên forum lưu ý "FreeCAD doesn't actually keep track of a timeline… the tree fully represents your state"
  (thứ cấp, qua tìm kiếm). → **Không tìm thấy, tự viết được bằng API PartDesign + saveImage.**
- **API (nguồn wiki chính thức qua bản GitHub [PartDesign_Body.md](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/PartDesign_Body.md)):**
  - `Body.Group` (LinkList) – các feature theo thứ tự; `Body.Tip` (Link) – "the final representation of the Body"; `Body.BaseFeature`.
  - "Changing the Tip in effect rolls back its history" (đặt Tip = feature trước). Chế độ `Display Mode Body` = `Through` (mặc định): chỉ một solid
    feature hiện tại một thời điểm; ẩn/hiện feature **không đổi Tip**.
  - Chụp: `Gui.ActiveDocument.ActiveView.saveImage(path, w, h, "Current"|"White"|"Black"|"Transparent")` ([Std_ViewScreenShot](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Std_ViewScreenShot.md)).
- **Cách làm đề xuất (không đổi Tip → không recompute, không làm hỏng file):**
  ```python
  # chạy qua tools/robotics-cad/scripts/gui_run.py (FC_FILE, FC_SCRIPT); KHÔNG lưu file
  for i, f in enumerate(f for f in body.Group if f.isDerivedFrom("PartDesign::Feature")):
      for g in body.Group: g.ViewObject.Visibility = False
      f.ViewObject.Visibility = True          # f.Shape = khối tích lũy tới bước i
      # tùy chọn: hiện sketch nguồn của f (f.Profile) 1 khung trước để học sinh thấy "vẽ rồi pad"
      Gui.updateGui(); view.saveImage(f"{out}/step-{i:02d}.png", 1920, 1080, "White")
  ```
  Kèm `steps.json` (tên feature `f.Label`, loại `f.TypeId`, kích thước chính như `Length` của Pad) → Claude viết chú thích/phụ đề từng bước.
  **Đã làm 2026-10-25: `tools/robotics-cad/scripts/build_replay.py`** (chạy qua `gui_run.py`). Thử thật:
  - `pushrod_arm.FCStd` = 86 `Part::Feature`, **0 PartDesign Body** (model sinh/sửa bằng script) → không có lịch sử feature;
    chế độ `parts` hiện dần theo 9 nhóm cây (Base → … → Pins_printed). Thứ tự LẮP thật vẫn là `render_assembly.py` (13 bước).
    `TODO`: khung hình còn rộng (tay nhỏ, lệch góc) – tìm vật thể phụ làm `fitAll` rộng ra.
  - File PartDesign mẫu (Pad → Pocket 2 lỗ → Fillet): 5 ảnh, có khung sketch trước Pad/Pocket, `steps.json` kèm `Length`/`Radius`.
  - Bẫy: bật/tắt `App::DocumentObjectGroup` bật/tắt luôn mọi con → bật nhóm TRƯỚC rồi mới ẩn chi tiết;
    file lưu từ CLI mở ra ẩn hết → hiện trạng thái cuối rồi mới `fitAll`.
- **cyberbrick-car** sinh từ `build_car.py` (Part, không phải lịch sử PartDesign) → replay theo **từng giai đoạn trong script** (ghi ảnh sau mỗi
  khối/boolean) thay vì `Body.Group`. `TODO` kiểm cấu trúc file.
- Ảnh 1920×1080 cho video dài; chạy lần 2 ở 1080×1920 (camera zoom gần) cho Shorts. Ghép bằng FFmpeg/`make_reel.py` (cảnh `step`).

### 1.3 Chuyển động/animation trong FreeCAD
| Công cụ | Trạng thái (đã kiểm) | Khuyến nghị |
|---|---|---|
| **Assembly → Create Simulation** (lõi, 1.1) | RN 1.1: "Create Simulation tool was added making it possible to add motions to joints and create animations" ([RN 1.1](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Release_notes_1.1.md)). Wiki: Motion Angular/Linear, `Formula` (vd. `1.0*time`), FPS mặc định 30, phát bằng player trong task panel; **không nhắc xuất ảnh/video** ([Assembly_CreateSimulation](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Assembly_CreateSimulation.md)). Đã đối chiếu: `CommandCreateSimulation.py` trên máy (1.1) **không có** hàm xuất. | **Dùng** để tạo chuyển động; tự chụp khung (dưới). |
| Xuất video Simulation (`main`/26.3) | `saveAnimation()`: chọn MP4/GIF/AVI(/WebM), lặp `self.assembly.updateForFrame(i)` → `Gui.updateGui()` → `view.saveImage(frame, w, h, "Current")`, ghép bằng PyAV + Pillow ([mã main](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/Mod/Assembly/CommandCreateSimulation.py)); RN 26.3 "Simulations now offer export to video format", 26.3 **chưa phát hành** ([RN 26.3](https://github.com/Reqrefusion/FreeCAD-Documentation-Project/blob/main/wiki/Release_notes_26.3.wikitext)). | **Chép mẫu** vào script STLab (chạy 1.1 qua `gui_run.py`, ghép bằng FFmpeg). Lưu ý: pushrod-arm đã chọn kinematics closed-form (`render_sim_poses.py`) – xem `docs/reports/freecad-community-automation.md`. |
| **Animate** (`jirivalasek/animate`, 4★, LGPL) | Trajectory/Server/Control/CollisionDetector, "record… series of images and export as a video"; Camera tool còn là kế hoạch; phiên bản FreeCAD hỗ trợ không ghi ([repo](https://github.com/jirivalasek/animate)). | Không (ít người dùng, không rõ hỗ trợ 1.1). |
| **Inbetweening / i10g** (PyPI `freecad-i10g`) | Theo mô tả tìm kiếm: lưu placement/visibility/màu thành bước, nội suy, xuất ảnh/video/gif (thứ cấp – trang PyPI không tải được). | `TODO` đọc repo; tiềm năng cho exploded animation. |
| Animation Workbench (microelly2) | Wiki ghi "under construction" (thứ cấp qua tìm kiếm; wiki chặn bot). | Không. |
| ExplodedAssembly | Đã loại (file kia §2.1). | — |
| **FreeCAD-render** (`FreeCAD/FreeCAD-render`, 239★, LGPL-2.1+; plugin help/materialx GPL-3+) | Pov-Ray, LuxCore, Appleseed, Cycles standalone, Ospray, Pbrt v4 (thử nghiệm); README: maintainer "discontinuing maintenance" từ **12/11/2025**; không nhắc animation/1.x ([repo](https://github.com/FreeCAD/FreeCAD-render)). | **Không** – dùng Blender. |

### 1.4 Thiết kế bài học dạng video (có bằng chứng)
- **Guo, Kim & Rubin (2014)**, ACM Learning@Scale, 6,9 triệu phiên xem edX: "median engagement time is at most 6 minutes, regardless of total video
  length"; video > 9 phút học viên thường xem chưa tới nửa; khuyến nghị "segment videos into chunks shorter than 6 minutes"; tutorial vẽ tay
  (Khan-style) được xem lâu gấp 1,5–2 lần slide/screencast; nói nhanh, nhiệt tình tốt hơn; tutorial cần hỗ trợ xem lại/tua
  ([PDF](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf), đã đọc bản đầy đủ). Lưu ý: dữ liệu MOOC người lớn, không phải học sinh THCS.
- **Mayer – nguyên tắc đa phương tiện**, tóm tắt cho video bởi **Brame (2016)**, CBE–Life Sciences Education 15(4) es6
  ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5132380/)), dẫn Mayer & Moreno (2003), Mayer (2008):
  - *Signaling*: chữ/mũi tên/màu làm nổi điểm chính → trong FreeCAD: khoanh nút lệnh, Keyviz phím tắt.
  - *Segmenting*: chia đoạn ngắn → mỗi chương = 1 feature/1 nhóm feature, ≤ 6 phút/video.
  - *Weeding*: bỏ chi tiết thừa, **nhạc nền** → khớp quyết định "xuất không nhạc".
  - *Modality*: hình + lời nói, không nhồi chữ dài cùng animation → giọng Tuan đọc, chữ chỉ là từ khóa.
  - *Personalization*: giọng trò chuyện; *câu hỏi chèn giữa* giảm lơ đãng → "Dừng video, tự làm Pad 10 mm".
  - Bản gốc sách Mayer *Multimedia Learning* chưa đọc → `TODO` nếu cần trích nguyên văn.
- **YouTube chapters** ([Help 9884579](https://support.google.com/youtube/answer/9884579?hl=en)): timestamp đầu "starts with 00:00", "at least three
  timestamps… in ascending order", "minimum length for video chapters is 10 seconds"; chương tự động bật mặc định, không có nếu kênh có gậy.
- **Định dạng đề xuất (GỢI Ý):** mỗi dự án = 1 playlist YouTube 16:9, mỗi video 4–6 phút = 1 cụm chi tiết; mô tả có chương + link tải
  `FCStd` khởi đầu/kết thúc + phiếu bài tập PDF (nhiệm vụ, kích thước mm, tiêu chí đạt, câu hỏi mở rộng). Phiếu có thể sinh như `ASSEMBLY.pdf`
  (`assembly-pdf.py` đã có).

### 1.5 Tài liệu/khóa FreeCAD mở để tham khảo cấu trúc bài
| Nguồn | Ghi chú | License |
|---|---|---|
| Wiki FreeCAD – Tutorials; **Basic Part Design Tutorial 019** (Dormeletti, Williams, Roy_043; FreeCAD ≥ 0.19; ~1 giờ; Beginner) | Cấu trúc: Startup → Master sketch → Main profile → Corner cutouts → Sides → Center hole → Result ([md](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Basic_Part_Design_Tutorial_019.md)) – mẫu tốt "1 chi tiết, 6 bước". wiki.freecad.org chặn bot (Anubis) khi đọc. | Nội dung wiki: `TODO` (thường ghi CC-BY 3.0 – chưa xác nhận); bản Markdown `FreeCAD-documentation` (105★) gắn CC0-1.0, **đã archive 01/04/2026** |
| Wiki – Video tutorials for product design | Danh sách kênh (Joko Engineering, TheMarkster…) – tham khảo nhịp/chương, không tái dùng nội dung ([trang](https://wiki.freecad.org/Video_tutorials_for_product_design)) | Bản quyền từng kênh |
| Khóa CC-BY trên GitHub cho học sinh | **Không tìm thấy** (kết quả toàn khóa trả phí Udemy/Ko-fi). STLab tự làm sẽ là khoảng trống thật. | — |

## 2. Hashtag + SEO (chỉ dùng nguồn chính thức cho quy tắc)

### 2.1 Quy tắc từng nền tảng
| Nền tảng | Quy tắc chính thức | Nguồn |
|---|---|---|
| **YouTube** | Hashtag trong tiêu đề hoặc mô tả; "up to three hashtags that are considered most engaging will appear by your video title"; "more than 60 hashtags, we'll ignore each hashtag"; không dấu cách; hashtag không liên quan/quá nhiều → có thể bị gỡ khỏi tìm kiếm | [Help 6390658](https://support.google.com/youtube/answer/6390658?hl=en) |
| YouTube – đề xuất | Tín hiệu: clicks, watch time ("valued watchtime"), khảo sát 1–5 sao (chỉ 4–5 sao tính), shares, likes, dislikes (Goodrow, 15/09/2021); Help: lịch sử xem, like, khảo sát "satisfaction, not just watch time", "Not interested" | [Blog YouTube](https://blog.youtube/inside-youtube/on-youtubes-recommendation-system/), [Help 16089387](https://support.google.com/youtube/answer/16089387?hl=en) |
| YouTube – Shorts → video dài | "Related video": Studio → Content → chọn Short → Related video từ kênh mình → Save; video đích public/unlisted; **cần "advanced feature access"**; không làm được qua API công khai (thứ cấp) | [Help 14075157](https://support.google.com/youtube/answer/14075157?hl=en), [Blog 14/07/2026](https://blog.youtube/creator-and-artist-stories/youtube-related-videos-traffic-guide/) |
| **TikTok** – đề xuất | Tín hiệu: tương tác (like, share, follow, comment), **thông tin video ("captions, sounds, and hashtags")**, thiết bị/ngôn ngữ (trọng số thấp); tín hiệu mạnh: "whether a user finishes watching a longer video from beginning to end"; "neither follower count nor… previous high-performing videos are direct factors" (18/06/2020) | [Newsroom](https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you) |
| TikTok – hashtag | "#FYP, #ForYou, and #ForYouPage work just like all other hashtags… won't necessarily improve your chances"; dùng caption để thêm ngữ cảnh (30/07/2020) | [Newsroom 5 tips](https://newsroom.tiktok.com/5-tips-for-tiktok-creators?lang=en) |
| TikTok – tìm kiếm | **Creator Search Insights** (gõ tên trong ô tìm kiếm): chủ đề được tìm nhiều, lọc "content gap" (ít video), chỉ số search views/impressions/CTR/thứ hạng (theo bản tóm tắt tìm kiếm trang Creator Academy – trang không tải được → `TODO` xác nhận, điều kiện tài khoản/khu vực VN). Từ khóa trong **lời nói/chữ trên màn hình** được index: chỉ có nguồn thứ cấp → không khẳng định. | [Creator Academy](https://www.tiktok.com/creator-academy/en/article/Creator-Search-Insights) |
| TikTok – Creative Center | Trang Trends/Hashtag tồn tại; bộ lọc quốc gia (có Việt Nam không) chưa đọc được (trang render JS) → `TODO` Tuan mở xem | [Creative Center](https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en) |
| **Instagram** | **Tối đa 5 hashtag/bài và Reel**, thông báo qua @creators trên Threads ngày 18/12/2025 (trước là 30); Instagram nói hashtag chung chung như #reels #explore không giúp, có thể hại (thứ cấp: [Social Media Today](https://www.socialmediatoday.com/news/instagrams-implementing-new-limits-on-hashtag-use/808309/)). Không xác nhận được Mosseri công bố trực tiếp. Help Center không tải được. | `TODO` đọc help.instagram.com |
| **Facebook** | Hashtag biến chủ đề thành liên kết bấm được, mở feed bài cùng hashtag; một từ, không dấu cách; số được, ký tự đặc biệt không; chỉ thấy bài được chia sẻ với mình. **Không có** tuyên bố chính thức về ảnh hưởng tới phân phối/số lượng khuyến nghị (con số "1–3" chỉ ở blog thứ cấp). | [Facebook Help](https://www.facebook.com/help/587836257914341) |

### 2.2 Kết luận thẳng
- Hashtag **không đảm bảo lên top**. Yếu tố được nền tảng nêu đích danh: **xem hết/thời gian xem có giá trị, tương tác (share, comment, like), hài lòng,
  và phù hợp người xem**. Hashtag/caption chỉ giúp hệ thống hiểu video nói về gì + xuất hiện khi người ta tìm.
- Thực hành: (1) 3 s đầu nêu kết quả (file kia §1.2); (2) **từ khóa người ta gõ** đặt ở tiêu đề/câu đầu caption và nói ra miệng ("cách vẽ bánh răng
  trong FreeCAD"); (3) 3–5 hashtag đúng chủ đề, không #fyp/#xuhuong; (4) video dài có chương; (5) đo retention rồi sửa hook.

### 2.3 Bộ hashtag mẫu STLab – **GỢI Ý, không có số liệu lượt dùng**
| Nhóm | Tiếng Việt | Tiếng Anh |
|---|---|---|
| Rộng (chọn 1) | #STEM #HocLapTrinh #InBaChieu | #STEM #3DPrinting #Robotics |
| Ngách (chọn 1–2) | #FreeCADTiengViet #ThietKe3D #RobotTuLam #SuaLoiIn3D | #FreeCAD #PartDesign #BambuLabA1 #CyberBrick #MakerEducation |
| Địa phương (chọn 1) | #DucTrong #LamDong #DaLat | — |
| Thương hiệu (luôn có, 1–2) | #STLab + series: #BanVeRaRobot #SuaLoiIn3D #HoiThayTuan (đã đặt trong `trend-content-ideas.md` §4) | #STLab |
- Công thức mỗi bài: **thương hiệu 1 + ngách 1–2 + địa phương 1 (+ rộng 1)** → ≤ 5 (khớp giới hạn Instagram, dùng chung mọi nền tảng).
  YouTube video dài: 3 hashtag trong mô tả (hiện trên tiêu đề) + tiêu đề chứa từ khóa tìm kiếm.
- `TODO` Tuan tra Creator Search Insights/Creative Center (VN) và ô gợi ý tìm kiếm YouTube với "FreeCAD", "in 3D", "robot" trước khi chốt bộ.

### 2.4 Công cụ mã nguồn mở về hashtag/trend
| Công cụ | ★ / license | Cách chạy | Đánh giá |
|---|---|---|---|
| bellingcat/tiktok-hashtag-analysis | 378★, MIT | TikTokApi + Playwright + yt-dlp, tải bài/video theo hashtag, đếm hashtag đi kèm ([repo](https://github.com/bellingcat/tiktok-hashtag-analysis)) | Công cụ nghiên cứu OSINT; **scrape** → trái ToS TikTok |
| Actor Apify "TikTok Trends/Hashtag Scraper" | Đóng, trả phí | Scrape Creative Center | Không |
| "Hashtag generator" (Ahrefs, Inro, Submagic…) | Đóng | Web | Nhiều trang còn ghi 25–30 hashtag IG → **lỗi thời** |
- ToS TikTok mục 5 cấm "use automated scripts to collect information from or otherwise interact with the Services" và "bypass any measures…"
  ([ToS](https://www.tiktok.com/legal/page/row/terms-of-service/en)). Rủi ro: khóa tài khoản cá nhân của Tuan (đang là tài khoản đăng).
- **Khuyến nghị:** không cài; Tuan tra tay 10 phút/tuần (Creative Center, Creator Search Insights, gợi ý tìm kiếm YouTube/TikTok) → dán từ khóa vào
  `marketing/keywords.md`; Claude soạn caption + hashtag theo công thức §2.3.

## 3. Workflow chuẩn

### 3.1 Mô hình 1 gốc → nhiều phái sinh
- Gốc: **bài hướng dẫn dài 16:9** (YouTube, 4–6 phút/video, có chương) + gói học liệu (FCStd, phiếu bài tập).
- Phái sinh: reel giới thiệu 15–30 s (mẫu A/C file kia §5.2), Short "1 bước 1 mẹo" (cắt 1 chương), ảnh carousel các bước, bài Facebook phụ huynh.
- Liên kết chính thức: Short → video dài bằng **Related video** (§2.1); video dài có chương; mô tả YouTube link playlist.
- Nguồn "pillar/repurposing" chính thức (Creator Academy) chưa tìm được bản hiện hành → mô hình này là **thực hành phổ biến + tính năng Related video**,
  không có số liệu hiệu quả chính thức.

### 3.2 Các bước (pre → post → publish → analytics)
| Giai đoạn | Đầu ra | Ai làm |
|---|---|---|
| Pre-production | `tutorial/brief.md` (mục tiêu học, độ tuổi, thời lượng), `script.md` (từng chương: nói gì, thao tác gì, câu hỏi chèn), shot list (đoạn quay OBS vs ảnh replay vs vật thật) | Claude soạn từ README/ASSEMBLY/`steps.json`, Tuan duyệt |
| Production | Build-replay PNG, frames mô phỏng (FreeCAD qua `gui_run.py`); quay OBS theo chương (script obs-websocket đánh dấu chương); clip vật thật (FilmCraft) | Máy + Tuan |
| Post | Video dài (FFmpeg/FilmCraft), phụ đề (faster-whisper), `chapters.txt`, thumbnail; reel/Short (`make_reel.py`) | Máy, Claude QA bằng contact sheet |
| Publish | `caption.md` từng nền tảng, lịch đăng, Related video, nhạc chọn trong app | **Tuan tự đăng** |
| Analytics | YouTube Studio: impressions, impressions CTR, average view duration, key moments for audience retention, so "typical performance" ([Help 9002587](https://support.google.com/youtube/answer/9002587?hl=en), [1715072](https://support.google.com/youtube/answer/1715072?hl=en)); TikTok Studio: average watch time, watched full video, traffic source (thứ cấp – `TODO` trang chính thức) | Tuan nhập `video-log.csv` (file kia §6) |

**Công cụ quản lý/lập lịch mã nguồn mở (chỉ ghi nhận):** Postiz (AGPL-3.0, file kia §2.5); **Mixpost Lite** (`inovector/mixpost`, ~3,9k★, MIT,
tự host; bản Pro thương mại; mạng xã hội hỗ trợ `TODO` đọc docs.mixpost.app). Cả hai cần token tài khoản → không dùng lúc này (Claude không tự đăng).
Thay bằng: thư mục dự án + `video-log.csv` + checklist trong `caption.md` là đủ cho quy mô STLab.

### 3.3 Gói nội dung cho mỗi dự án `maker/<project>/`
```
maker/<project>/
├─ marketing/
│  ├─ intro.yaml          # reel giới thiệu 9:16 → video-ai/scripts/make_reel.py (đã có)
│  ├─ keywords.md         # từ khóa Tuan tra tay (Creative Center, gợi ý tìm kiếm)
│  └─ caption.md          # caption + hashtag: TikTok / Reels-FB / Shorts / YouTube dài, CTA "Open Lab tham quan"
└─ tutorial/
   ├─ brief.md, script.md # mục tiêu, chương, lời, câu hỏi chèn
   ├─ replay/             # build-replay: step-XX.png (16:9 + 9:16), steps.json   ← build_replay.py (mới)
   ├─ sim/                # khung mô phỏng                                      ← sim_frames.py (mới)
   ├─ obs/record.py       # điều khiển OBS: scene, Start/Stop, CreateRecordChapter → chapters.txt
   ├─ chapters.txt        # 00:00 … (≥ 3 chương, ≥ 10 s)
   ├─ exercises/          # phiếu bài tập .md/.pdf + start.FCStd / done.FCStd
   └─ out/ (KHÔNG lên git: video lớn → video-ai/projects/<name>/out/ như make_reel)
```
```
FCStd + README/ASSEMBLY ──► build_replay.py / sim_frames.py (FreeCAD GUI qua gui_run.py) ──► replay/*.png, sim/*.png, steps.json
          │                                                                                   │
          ├──► Claude: brief.md, script.md, exercises/ ──► Tuan duyệt (ảnh contact sheet)     │
          │                                                                                   ▼
          ├──► OBS + Keyviz + obs/record.py (quay theo chương) ──► raw.mp4 + chapters.txt ──► FFmpeg/FilmCraft ──► bài dài 16:9
          │                                                                                   │
          └──► intro.yaml ──► make_reel.py ──► reel 9:16 ───────────────► Short/Reel/TikTok ◄─┘ (cắt 1 chương)
                                                                         │ Related video → bài dài
   Claude: caption.md (≤ 5 hashtag, từ khóa đầu caption) ──► Tuan tự đăng ──► video-log.csv ──► 2 tuần xem lại hook/retention
```

### 3.4 Ước lượng công sức (**ước lượng**, buổi ≈ 3–4 giờ)
| Việc | Ước |
|---|---|
| `build_replay.py` (PartDesign `Body.Group` + saveImage, 2 khổ, `steps.json`) thử trên pushrod-arm | 1 buổi |
| `sim_frames.py` (mẫu `updateForFrame` + saveImage, hoặc tái dùng `render_sim_poses.py`) | 0,5 buổi |
| `obs/record.py` (obsws-python: scene, record, chapter → `chapters.txt`) + cấu hình OBS/Keyviz | 0,5–1 buổi |
| Template `script.md`, `caption.md`, phiếu bài tập + 1 bài mẫu hoàn chỉnh (pushrod-arm chương 1) | 1 buổi |
| Mỗi dự án mới sau khi có công cụ: máy chạy + Claude soạn | ~1 giờ máy/soạn + **thời gian Tuan quay/đọc lời** (chưa ước được – `TODO` đo lần đầu) |

## 4. Bảng nguồn
| Tên | Link | ★/cập nhật | License | Chạy gì/gọi mạng | Dùng cho | Khuyến nghị |
|---|---|---|---|---|---|---|
| OBS Studio | [obsproject.com](https://obsproject.com) | 32.1 (02/04/2026), 32.2 (07/2026, thứ cấp) | GPL-2.0 | Cục bộ | Quay màn hình FreeCAD | **Dùng** |
| obs-websocket 5 | [repo](https://github.com/obsproject/obs-websocket) | 4,4k★, kèm OBS ≥ 28 | GPL-2.0 | Cục bộ (localhost) | Script quay + chương | **Dùng** |
| obsws-python / simpleobsws | [PyPI](https://pypi.org/project/obsws-python) / [repo](https://github.com/IRLToolkit/simpleobsws) | `TODO` | `TODO` | Cục bộ | Client Python | **Dùng** obsws-python |
| Aitum Vertical | [repo](https://github.com/Aitum/obs-vertical-canvas) | 328★, v1.6.4 | GPL-2.0 | Cục bộ | Canvas dọc song song | Không cần |
| Keyviz | [repo](https://github.com/mulaRahul/keyviz) | 9,7k★, release `TODO` | GPL-3.0 | Cục bộ (hook bàn phím) | Hiện phím + chuột | **Dùng** |
| Carnac | [repo](https://github.com/Code52/carnac) | 4,6k★, bảo trì `TODO` | MS-PL | Cục bộ | Hiện phím | Dự phòng |
| KeyCastOW | [repo](https://github.com/brookhong/KeyCastOW) | ngừng ~2017–19 (thứ cấp) | MIT (README) | Cục bộ | Hiện phím | Không |
| FreeCAD PartDesign Body API + saveImage | [PartDesign_Body](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/PartDesign_Body.md), [Std_ViewScreenShot](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Std_ViewScreenShot.md) | lõi 1.1 | LGPL-2.1 | Cục bộ, cần GUI | Build replay | **Dùng** (tự viết) |
| Assembly Create Simulation | [wiki md](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Assembly_CreateSimulation.md), [mã main](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/Mod/Assembly/CommandCreateSimulation.py) | 1.1 (xuất video ở 26.3 dev) | LGPL-2.1 | Cục bộ, cần GUI | Chuyển động | **Dùng** + tự chụp |
| Animate | [repo](https://github.com/jirivalasek/animate) | 4★ | LGPL (WB), MIT (ví dụ) | Cục bộ | Animation quỹ đạo | Không |
| i10g (Inbetweening) | [PyPI](https://pypi.org/project/freecad-i10g/) | `TODO` | `TODO` | Cục bộ | Exploded animation | `TODO` xem |
| FreeCAD-render | [repo](https://github.com/FreeCAD/FreeCAD-render) | 239★, ngừng bảo trì 11/2025 | LGPL-2.1+ / GPL-3+ | Renderer ngoài | Ảnh đẹp | **Không** |
| Guo et al. 2014 | [PDF](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf) | L@S 2014 | Bài báo | — | Độ dài/kiểu video | Căn cứ |
| Brame 2016 (Mayer) | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC5132380/) | CBE-LSE 15(4) | CC BY-NC-SA (`TODO` xác nhận) | — | Nguyên tắc video học | Căn cứ |
| Basic Part Design Tutorial 019 | [md](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Basic_Part_Design_Tutorial_019.md) | FreeCAD ≥ 0.19 | wiki `TODO` | — | Mẫu cấu trúc bài | Tham khảo |
| YouTube Help (hashtag, chapters, related video, analytics) | xem §2.1, §1.4, §3.2 | đọc 2026-10-24 | — | — | Quy tắc | **Theo** |
| TikTok Newsroom / Creator Academy / ToS | xem §2.1, §2.4 | 2020; ToS hiện hành | — | — | Quy tắc, rủi ro scrape | **Theo** |
| Creative Center / Creator Search Insights | [CC](https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en) | — | Dịch vụ TikTok | Tra tay | Từ khóa/trend | **Dùng tay** |
| bellingcat/tiktok-hashtag-analysis | [repo](https://github.com/bellingcat/tiktok-hashtag-analysis) | 378★ | MIT | Scrape TikTok | Phân tích hashtag | **Không** (ToS) |
| Mixpost Lite | [repo](https://github.com/inovector/mixpost) | ~3,9k★ | MIT (Pro thương mại) | Token MXH, tự host | Lập lịch | Ghi nhận |
| Postiz | [repo](https://github.com/gitroomhq/postiz-app) | 37,7k★ (file kia) | AGPL-3.0 | Token MXH | Lập lịch | Ghi nhận |

**Xem lại khi thương mại:** Keyviz GPL-3.0, OBS/obs-websocket/Aitum GPL-2.0 (chỉ là công cụ dùng, không phân phối lại → thường không ảnh hưởng – `TODO`
nếu đóng gói kèm sản phẩm); Postiz AGPL-3.0 (nếu tự host cho khách); Mixpost Pro trả phí; nội dung wiki FreeCAD (ghi công khi trích); Brame 2016 nếu NC.

## 5. Top 5 việc nên làm
1. **Viết `build_replay.py`** (PartDesign `Body.Group` + `saveImage`, chạy qua `gui_run.py`, xuất 16:9 + 9:16 + `steps.json`) – thử trên pushrod-arm;
   kèm contact sheet để Tuan duyệt.
2. **Cài cấu hình OBS (16:9) + Keyviz + `obs/record.py`** (obsws-python: Start/Stop + `CreateRecordChapter`, Hybrid MP4) → `chapters.txt` tự động.
3. **Bài mẫu hoàn chỉnh "pushrod-arm – chương 1"**: `script.md` theo Mayer/Guo (≤ 6 phút, câu hỏi chèn, không nhạc) + phiếu bài tập + `start/done.FCStd`.
4. **Template `caption.md`** (4 nền tảng, ≤ 5 hashtag theo công thức §2.3, từ khóa đầu caption, CTA Open Lab) – Claude điền cho mỗi video.
5. **Tuan tra từ khóa** (Creator Search Insights, Creative Center VN, gợi ý tìm kiếm YouTube) 1 lần → `keywords.md`; bật Related video cho Shorts
   (kiểm kênh có advanced feature access).

## 6. Cần Tuan quyết
1. Video hướng dẫn đăng **YouTube** (kênh nào – cá nhân hay STLab)? TikTok/Facebook chỉ đăng bản ngắn?
2. Giọng: Tuan đọc lời từng chương, hay quay thao tác im lặng + chữ (Guo: nói nhiệt tình xem lâu hơn)?
3. Phát file FCStd/phiếu bài tập công khai (Drive/GitHub) hay chỉ cho học sinh lớp? License nội dung (gợi ý CC BY-NC 4.0).
4. Độ tuổi học sinh mục tiêu của bài video (ảnh hưởng độ dài, tốc độ, từ vựng).
5. Có cần mô phỏng/chuyển động trong bài, hay build-replay + vật thật là đủ cho giai đoạn đầu?
6. Có thử i10g (exploded animation) không, hay giữ script tự viết.

## Điểm chưa xác nhận (TODO)
- Instagram 5 hashtag: chỉ nguồn thứ cấp (help.instagram.com không tải được); Facebook không có khuyến nghị số lượng chính thức.
- TikTok: Creator Search Insights (điều kiện, có ở VN?), Creative Center lọc Việt Nam, chỉ số TikTok Studio chính thức, việc index lời nói/chữ trên màn hình
  (support.tiktok.com và Creator Academy render JS – không đọc được).
- Ngày release Keyviz, Carnac; ★/license obsws-python, simpleobsws; repo và trạng thái i10g; cổng obs-websocket trên máy.
- `build_replay.py`: chưa chạy; giả định `Feature.Shape` tích lũy theo chế độ Through (theo wiki) cần thử; cấu trúc cyberbrick-car (Part, không PartDesign).
- License nội dung wiki FreeCAD (wiki.freecad.org chặn bot); license bài Brame 2016; sách Mayer gốc chưa đọc.
- Nguồn chính thức về "repurposing/pillar" của YouTube Creator Academy hiện hành.

## Nguồn
- OBS: [RN 32.1](https://obsproject.com/blog/obs-studio-32-1-release-notes) · [obs-websocket](https://github.com/obsproject/obs-websocket) ([protocol.md](https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md)) ·
  [Aitum Vertical forum](https://obsproject.com/forum/resources/aitum-vertical.1715/) · [obs-vertical-canvas](https://github.com/Aitum/obs-vertical-canvas) · (thứ cấp) [ubuntuhandbook OBS 32.2](https://ubuntuhandbook.org/index.php/2026/07/obs-studio-32-2-0-released-with-sdr-to-hdr-composer-ubuntu-26-04-deb/)
- Phím/chuột: [Keyviz](https://github.com/mulaRahul/keyviz) · [Carnac](https://github.com/Code52/carnac) · (thứ cấp) [KeyCastOW – AlternativeTo](https://alternativeto.net/software/keycastow/about)
- FreeCAD: [PartDesign_Body](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/PartDesign_Body.md) · [Std_ViewScreenShot](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Std_ViewScreenShot.md) ·
  [Assembly_CreateSimulation](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Assembly_CreateSimulation.md) · [Release notes 1.1](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Release_notes_1.1.md) ·
  [CommandCreateSimulation.py (main)](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/Mod/Assembly/CommandCreateSimulation.py) · [Release notes 26.3](https://github.com/Reqrefusion/FreeCAD-Documentation-Project/blob/main/wiki/Release_notes_26.3.wikitext) ·
  [FreeCAD-render](https://github.com/FreeCAD/FreeCAD-render) · [Animate](https://github.com/jirivalasek/animate) · [i10g](https://pypi.org/project/freecad-i10g/) · [Basic Part Design Tutorial 019](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Basic_Part_Design_Tutorial_019.md) ·
  [FreeCAD-documentation](https://github.com/FreeCAD/FreeCAD-documentation) · [Video tutorials for product design](https://wiki.freecad.org/Video_tutorials_for_product_design)
- Học tập: [Guo, Kim, Rubin 2014](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf) · [Brame 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5132380/)
- YouTube: [Hashtags 6390658](https://support.google.com/youtube/answer/6390658?hl=en) · [Chapters 9884579](https://support.google.com/youtube/answer/9884579?hl=en) · [Related video 14075157](https://support.google.com/youtube/answer/14075157?hl=en) ·
  [Recommendations 16089387](https://support.google.com/youtube/answer/16089387?hl=en) · [Analytics 9002587](https://support.google.com/youtube/answer/9002587?hl=en) · [Engagement 1715072](https://support.google.com/youtube/answer/1715072?hl=en) ·
  [Blog: recommendation system 2021](https://blog.youtube/inside-youtube/on-youtubes-recommendation-system/) · [Blog: related videos 2026](https://blog.youtube/creator-and-artist-stories/youtube-related-videos-traffic-guide/)
- TikTok: [How TikTok recommends #ForYou](https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you) · [5 tips for creators](https://newsroom.tiktok.com/5-tips-for-tiktok-creators?lang=en) ·
  [Creator Search Insights](https://www.tiktok.com/creator-academy/en/article/Creator-Search-Insights) · [Creative Center](https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en) · [Terms of Service](https://www.tiktok.com/legal/page/row/terms-of-service/en)
- Meta: [Facebook Help – hashtag](https://www.facebook.com/help/587836257914341) · (thứ cấp) [Social Media Today – IG 5 hashtag](https://www.socialmediatoday.com/news/instagrams-implementing-new-limits-on-hashtag-use/808309/)
- Công cụ: [bellingcat/tiktok-hashtag-analysis](https://github.com/bellingcat/tiktok-hashtag-analysis) · [Mixpost](https://github.com/inovector/mixpost) · [Postiz](https://github.com/gitroomhq/postiz-app)
