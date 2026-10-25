# Nghiên cứu: video marketing từ dự án maker (STLab)

Ngày: 2026-10-24 · Người làm: Claude (agent nghiên cứu) · Trạng thái: **chỉ nghiên cứu**, chưa cài/chạy gì.

**Mục đích:** tìm nguồn, công cụ, agent và cộng đồng để biến dữ liệu dự án (model FreeCAD, ảnh render, các bước ASSEMBLY,
timelapse in 3D, clip robot chạy) thành video ngắn đăng Facebook/TikTok/Shorts/Reels nhằm kéo tương tác.
**Liên kết:** `video-ai/` (FilmCraft, dựng từ clip tự quay, template `reel-9x16`), `photo-ai/` (ảnh), `studio/` (Toolhub,
Blender MCP), `maker/*/freecad/scripts/render_*.py`, `docs/design-first-research.md` (render concept).

Ký hiệu: (thứ cấp) = nguồn không phải hãng/repo chính · `TODO` = chưa xác minh · ★ = sao GitHub đọc ngày 2026-10-24.

## 0. Kết luận nhanh
- **Khoảng trống thật:** `video-ai` chỉ dựng *clip tự quay*. Dự án đã có sẵn nguyên liệu máy làm được mà chưa thành video:
  ảnh render FreeCAD (`cyberbrick-car/freecad/images`, `pushrod-arm/freecad/images/assembly/step-XX-{a,b}.png`), macro sim
  (`pushrod_arm_sim.FCMacro`), và timelapse của **Bambu A1** (A1 có camera live view tích hợp, làm được timelapse – xem §2.2).
- **Không cần SaaS:** FFmpeg (đã có tại `C:\ffmpeg-master-latest-win64-gpl-shared`) + `saveImage` của FreeCAD + script Python
  đủ làm 3 trong 4 mẫu video đề xuất. FilmCraft tiếp tục lo phần clip người thật + phụ đề.
- **Khuyến nghị công cụ:** (1) FreeCAD `ActiveView.saveImage` → chuỗi PNG (turntable/exploded/từng bước lắp) – dùng ngay;
  (2) FFmpeg ghép ảnh/timelapse/chữ – dùng ngay; (3) Blender 5.2 (đã thấy cài ở `C:\Program Files\Blender Foundation\Blender 5.2`)
  cho bản render đẹp – thử sau; (4) Remotion (66,8k★) chỉ nếu muốn template chữ/hiệu ứng kiểu "motion graphics" – free cho
  cá nhân/tổ chức ≤ 3 nhân viên, nhưng thêm Node/Chromium; **chưa cần**.
- **Rủi ro lớn nhất là học sinh trong video**, không phải công cụ: Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 (hiệu lực
  01/01/2026) yêu cầu đồng ý của **trẻ từ đủ 7 tuổi và người đại diện** khi công bố thông tin riêng tư. Cần mẫu đồng ý phụ huynh
  trước khi đăng clip có mặt học sinh.
- **Nhạc:** nhạc thư viện nền tảng bị giới hạn theo nền tảng (Facebook Sound Collection chỉ cho FB/IG; TikTok CML chỉ trong
  TikTok). Một video đăng 4 nơi → nên **xuất bản không nhạc** + thêm nhạc trong app từng nền tảng, hoặc dùng nhạc có license
  đa nền tảng (Pixabay – vẫn phải tự kiểm Content ID).
- **Không tự đăng:** API đăng Reels của Meta cần token trang + quyền `pages_manage_posts`; công cụ lập lịch (Postiz, AGPL) có MCP.
  Chỉ ghi nhận, giữ quy trình Tuan duyệt rồi tự đăng.

## 1. Video gì kéo tương tác

### 1.1 Thông số nền tảng (nguồn chính thức trước)
| Nền tảng | Tỉ lệ / độ phân giải | Độ dài | Ghi chú | Nguồn |
|---|---|---|---|---|
| Facebook Reels (Page, qua API) | 9:16, 1080×1920 khuyến nghị, tối thiểu 540×960 | 3–90 s (reel đăng làm story ≤ 60 s) | MP4 H.264/H.265, 24–60 fps cố định, AAC 48 kHz stereo ≥ 128 kbps, closed GOP 2–5 s | [Meta Reels Publishing API](https://developers.facebook.com/docs/video-api/guides/reels-publishing) |
| Facebook Reels (app, trang creators) | dọc hoặc ngang, .mp4 | tối thiểu 3 s, trang VN ghi "không giới hạn tối đa" | Mâu thuẫn với 90 s ở API → **giữ ≤ 90 s** cho an toàn | [creators.facebook.com/tools/reels](https://creators.facebook.com/tools/reels) |
| Instagram Reels | 9:16 1080×1920 | tới 3 phút (từ 01/2025) | Trước đó 90 s | (thứ cấp) [Social Media Today](https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-3-minutes/737766/) |
| YouTube Shorts | vuông hoặc dọc | tới 3 phút (upload từ 15/10/2024) | Short > 1 phút có **bất kỳ claim Content ID** → bị chặn toàn cầu; ≤ 1 phút không bị | [YouTube Help 15424877](https://support.google.com/youtube/answer/15424877?hl=en) |
| TikTok | 9:16 1080×1920 khuyến nghị | quay trong app ~10 phút; upload dài hơn tùy tài khoản | Giới hạn dung lượng/độ dài các nguồn mâu thuẫn → `TODO` đọc support.tiktok.com (trang không tải được bằng công cụ) | (thứ cấp) [ayrshare](https://ayrshare.com/docs/media-guidelines/tiktok) |
| Zalo (Video/OA) | `TODO` | `TODO` | Chưa tìm được tài liệu chính thức | — |

**Chuẩn xuất chung đề xuất** (thỏa mọi nền tảng trên): 1080×1920, 30 fps cố định, H.264 + AAC 48 kHz stereo, **15–45 s**,
≤ 60 s nếu có nhạc (tránh luật Content ID > 1 phút của Shorts), −14 LUFS (template `reel-9x16` đã dùng).

### 1.2 Hook, phụ đề, nhạc – điều nền tảng nói
- **3 giây đầu:** TikTok nói "hơn 63 % video có CTR cao nhất nêu thông điệp/sản phẩm chính trong 3 giây đầu" và gợi ý nhạc
  > 120 BPM giúp tỉ lệ xem hết cao hơn ([TikTok Business blog](https://ads.tiktok.com/business/nl-NL/blog/66),
  [Auction Ads Creative Tips PDF](https://ads.tiktok.com/business/library/Auction_Ads_Creative_Tips.pdf)). Lưu ý: số liệu là
  **quảng cáo** (CTR), không phải bài tự nhiên.
- **Meta:** Reels "nên xem có tiếng", cần hook trong vài giây đầu, giữ chữ/CTA trong **vùng an toàn** để không bị nút che
  (thứ cấp, tóm tắt hướng dẫn Reels Ads của Meta: [Social Media Today](https://www.socialmediatoday.com/news/meta-publishes-reels-ads-guide-instagram-facebook-video-marketing/752771/)).
- **Phụ đề:** nhiều người xem tắt tiếng → phụ đề in cứng + chữ lớn đầu video (thứ cấp; tỉ lệ cụ thể không có nguồn gốc → không ghi số).
  Template `reel-9x16` đã đặt phụ đề cách đáy 20 % – khớp lời khuyên vùng an toàn.
- **Tần suất đăng:** không tìm được con số chính thức. Trang creators của Meta chỉ nói "sự nhất quán". → **Gợi ý** (không nguồn):
  2–3 video/tuần, cùng khung giờ, theo series.

### 1.3 Series gợi ý cho STLab (gợi ý, chưa có số liệu tương tác)
| Series | Nguyên liệu đã có | Hook 3 s (ví dụ) |
|---|---|---|
| "Từ CAD ra vật thật" | Render FreeCAD + ảnh/clip vật in | Chia đôi màn hình: model ↔ vật thật, chữ "Học sinh 12 tuổi thiết kế cái này" (chỉ khi có đồng ý) |
| Timelapse in 3D | Timelapse A1 (SD) | Kết quả cuối hiện 0,5 s trước, rồi tua từ lớp đầu |
| Lắp ráp từng bước / exploded | `step-XX-a.png` pushrod-arm, ASSEMBLY.md | "13 bước để có cánh tay robot" + bộ đếm bước |
| Robot/xe chạy thật, đua xe | Clip tự quay (FilmCraft) | Pha va chạm/về đích trước, giải thích sau |
| Lỗi in & cách sửa | Ảnh lỗi (stringing, warping), `printability.py` (support/brim) | "Sai lầm này làm hỏng 3 giờ in" |
| Before–after | Bản v0.1 ↔ v0.2 (cyberbrick-car) | Ghép 2 bản cạnh nhau, quay 360° |

## 2. Công cụ tạo video từ dự án

### 2.1 CAD → video
- **FreeCAD `Gui.ActiveDocument.ActiveView.saveImage(path, w, h, "Current")`** – chụp khung nhìn từ Python, wiki có ví dụ vòng lặp
  đổi camera và lưu ảnh đánh số ([Std ViewScreenShot](https://wiki.freecad.org/Std_ViewScreenShot)). STLab đã dùng cách này trong
  `render_car.py`, `render_assembly.py` → mở rộng thành: xoay camera N độ/khung (turntable), dịch `Placement` dần (exploded),
  hiện từng nhóm chi tiết (lắp ráp). Ảnh 1080×1920 trực tiếp. Chạy cục bộ, không mạng. Nhớ tắt animation camera trước khi chụp
  (ví dụ `Automation.py` của FreeCAD làm vậy, [nguồn](https://free-cad.sourceforge.net/SrcDocu/d3/d31/Automation_8py_source.html)).
- **Macro Screen Wiki** (FreeCAD ≥ 0.19, sửa 2023-06): lưu khung nhìn khi xoay vật/khung nhìn, cần app ngoài ghép thành video
  ([wiki](https://wiki.freecad.org/Macro_Screen_Wiki)). Tham khảo, không cần cài – tự viết trong script dự án gọn hơn.
- **ExplodedAssembly** (JMG1, 141★, LGPL-2.1): workbench exploded có `CameraAnimation.py`; README nhắc FreeCAD 0.17, không thấy
  hỗ trợ 1.1 → **không dùng** (cũ; tự dịch `Placement` bằng script là đủ) ([repo](https://github.com/JMG1/ExplodedAssembly)).
- **Assembly4 animation:** repo `Zolko-123/FreeCAD_Assembly4` trả 404 ngày 2026-10-24 → `TODO` tìm vị trí mới; STLab không dùng A4.
- **Blender** (bản đẹp: vật liệu nhựa, HDRI, chuyển động mượt). Blender 5.2 **đã có trên máy** (studio/CLAUDE.md còn ghi 5.1 chưa cài
  → cần cập nhật ghi chú, `TODO` kiểm addon MCP có trong 5.2 không).
  - Nhập model: xuất từ FreeCAD sang **glTF/STL** (không cần addon), hoặc **STEP Importer** (Clonephaze, GPL-3.0+, v1.2.1 16/06/2026,
    Blender ≥ 5.1, dùng thư viện Cascadio → glTF; có báo lỗi trên 5.2 – thứ cấp) ([extensions.blender.org](https://extensions.blender.org/add-ons/step-importer/)).
  - Turntable/exploded: script `bpy` qua Blender MCP đã cài (`mcp-for-blender`, telemetry đã tắt). Render EEVEE trên GTX 1660 SUPER
    đủ cho 1080×1920 (ước lượng, `TODO` đo thời gian/khung).
  - Đánh đổi: đẹp hơn FreeCAD nhiều nhưng thêm bước xuất/gán vật liệu; dùng cho video "khoe" sản phẩm, không cho mọi video.

### 2.2 Timelapse in 3D (Bambu A1)
- A1 có **camera live view tích hợp** với hai chức năng "Remote Livestream và Time-lapse"; cảm biến 1928×1088, lấy nét cố định 15 cm
  (trang phụ tùng thay thế của Bambu: [store.bambulab.com](https://eu.store.bambulab.com/products/live-view-camera-a1)).
  Camera gắn cố định nhìn bàn in, khung ngang → cần crop 9:16.
- Wiki Bambu: hai chế độ – **Smooth** (đầu in ra máng thải mỗi lớp, cần prime tower, in lâu hơn) và **Traditional**; video lưu vào
  thẻ SD, tải qua Bambu Studio ([wiki Timelapse](https://wiki.bambulab.com/en/software/bambu-studio/Timelapse); trang trả 402 khi
  đọc tự động – nội dung theo bản tóm tắt tìm kiếm, `TODO` Tuan mở xác nhận bước A1).
- Thứ cấp (forum): file ở thư mục `cam`/timelapse trên microSD; một người báo thẻ 64 GB không lưu, 32 GB được; nên format thẻ trên máy
  in ([forum 5042](https://forum.bambulab.com/t/timelapse-videos-with-sd-cards-32-gb/5042)).
- **Octolapse/OctoPrint:** dành cho máy chạy OctoPrint; A1 dùng firmware Bambu → **không áp dụng**.
- Bản đẹp hơn: điện thoại trên giá cố định quay timelapse (app camera) + ánh sáng đều; dựng bằng FFmpeg. Rủi ro: không có trigger theo
  lớp → bàn in/đầu in rung trong video (chấp nhận được cho Reels).

### 2.3 Dựng tự động bằng code
| Công cụ | ★ / license | Hợp STLab? |
|---|---|---|
| **FFmpeg** (đã cài, bản GPL shared) | LGPL/GPL | **Dùng**: ghép chuỗi ảnh (`-framerate`), crop 9:16, tăng tốc timelapse (`setpts`), `drawtext`/`subtitles` (cần file font có dấu tiếng Việt – analyze.py đã giải quyết lỗi đường dẫn font trên Windows), `loudnorm`. |
| **MoviePy** | 15,0k★, MIT ([repo](https://github.com/Zulko/moviepy)) | Thử nếu cần ghép nhiều lớp bằng Python; bản chất gọi FFmpeg. Chưa cần. |
| **Remotion** | 66,8k★, license riêng: free cho cá nhân, công ty ≤ 3 nhân viên, phi lợi nhuận ([LICENSE.md](https://raw.githubusercontent.com/remotion-dev/remotion/main/LICENSE.md)) | Template video bằng React; có **skill chính thức cho Claude Code** (`remotion-dev/skills`, [docs](https://www.remotion.dev/docs/ai/skills)). Đánh đổi: thêm Node + Chromium headless, có telemetry (`TODO` đọc mục telemetry trong trang license). Ghi vào "Xem lại khi thương mại". |
| **Motion Canvas** | 19,4k★, MIT ([repo](https://github.com/motion-canvas/motion-canvas)) | Animation bằng TypeScript, editor trên trình duyệt; xuất không cần editor? `TODO`. Không cần. |
| **Manim (Community)** | 41,8k★, MIT ([repo](https://github.com/ManimCommunity/manim)) | Hợp video giải thích toán/cơ cấu (động học pushrod). Tiếng Việt cần LaTeX/Pango + font. Để sau. |

### 2.4 Phụ đề, giọng đọc, nhạc
- **Phụ đề:** đã có `faster-whisper 1.2.1` (26,1k★, MIT) + `large-v3-turbo` trong video-ai. Video từ dự án thường **không có lời** →
  phụ đề là chữ kịch bản (Claude viết từ ASSEMBLY.md/README) → `.srt` → burn-in FFmpeg. PhoWhisper đã loại (COMMUNITY.md).
- **Giọng đọc tiếng Việt (TTS):**
  - `edge-tts` (12,4k★, license `TODO` – repo có `gpl-3.0.txt`) **gửi văn bản lên dịch vụ TTS online của Microsoft Edge**, không có hợp
    đồng dịch vụ chính thức; bản 7.2.8 từng bị 403 ([repo](https://github.com/rany2/edge-tts)). Chỉ hợp thử nghiệm.
  - **VieNeu-TTS** (2,9k★, Apache-2.0, chạy CPU qua ONNX, clone giọng từ 3–8 s; README không ghi license trọng số; v4 là đóng/API)
    ([repo](https://github.com/pnnbao97/VieNeu-TTS)) → **ứng viên thử** chạy cục bộ. **Không clone giọng người khác/học sinh.**
  - **Đã thử 2026-10-25 – CHỌN VieNeu-TTS v3 Turbo** (`video-ai/scripts/tts_vi.py`, venv riêng `%LOCALAPPDATA%/stlab-studio/venvs/vieneu`):
    - Trọng số `pnnbao-ump/VieNeu-TTS-v3-Turbo` trên Hugging Face: **license apache-2.0** (hết `TODO`). 25 giọng có sẵn (Bắc/Trung/Nam).
    - i5-13400F CPU: tải model 10 s; RTF 0,62–0,70 (câu 11–17 s đọc mất 7–12 s). Không cần GPU, không gửi văn bản đi đâu.
    - Bẫy: onnxruntime 1.31 báo "External data path escapes model directory" (cache HF dùng symlink) → ghim `onnxruntime==1.22.1`;
      `infer(voice=...)` nhận MÃ giọng ("Mai Anh"), không nhận nhãn.
    - Whisper nghe lại 6 giọng: rõ nhất Mai Anh, Ngọc Huyền (nữ Bắc); Quang Sơn (Trung) bị nghe sai nhiều nhất. Giọng Bắc đọc
      "ráp" thành "dáp", "turret" thành "tu-rít". Mẫu nghe: `maker/pushrod-arm/marketing/voice-samples/*.mp3` – **Tuan chọn giọng**.
    - Gắn vào `make_reel.py`: cảnh có `say:` → giọng đúng cảnh (lệch < 0,02 s), −14 LUFS, kèm `<ten>.srt` sinh từ kịch bản.
      Mẫu: `maker/pushrod-arm/marketing/reel-13-steps-voice.yaml` (37,8 s, ~3 phút dựng).
  - viXTTS: Coqui Public Model License (phi thương mại) (thứ cấp, [HF](https://huggingface.co/dotyfake/Doty_viXTTS)) → bảng thương mại.
  - Khuyến nghị: **giọng thật của Tuan/giáo viên** cho video thương hiệu (tương tác tin cậy hơn – gợi ý), TTS chỉ cho series kỹ thuật.
- **Nhạc nền:**
  - Facebook Sound Collection: "chỉ dùng trên nền tảng Facebook" (FB + IG) (thứ cấp, [TechCrunch 2017](https://techcrunch.com/2017/12/08/facebook-sound-collection/)).
  - TikTok Commercial Music Library: tài khoản doanh nghiệp chỉ thấy CML; nhạc **chỉ dùng trong TikTok**; dùng nhạc thư viện chung từ
    tài khoản cá nhân để quảng bá kinh doanh có rủi ro vi phạm ([TikTok Business](https://ads.tiktok.com/business/en-US/blog/audio-library-royalty-free-music)).
  - YouTube Audio Library: điều khoản theo **từng bài** (một số cần ghi công) – nguồn thứ cấp mâu thuẫn, `TODO` đọc trang Help chính thức.
  - Pixabay: dùng miễn phí, không cần ghi công, không bán lại nguyên bản; bản tóm tắt không nói về Content ID → tự kiểm
    ([license summary](https://pixabay.com/service/license-summary/)).
  - → **Quy trình:** xuất `*-nomusic.mp4` (chỉ tiếng gốc/giọng) + `*-music.mp4` với nhạc Pixabay đã ghi nguồn vào `nhac.txt`; thêm nhạc
    thịnh hành trong app nếu muốn.

### 2.5 AI/SaaS dựng video (chỉ ghi nhận)
| Công cụ | Gửi dữ liệu | Ghi chú |
|---|---|---|
| CapCut (auto-caption, template) | Có (cloud khi đồng bộ/xử lý) | Điều khoản 06/2025 bị phê phán: cấp license rộng trên nội dung + tên/hình ảnh người dùng, kể cả sau khi xóa (thứ cấp, [SmartCompany](https://www.smartcompany.com.au/opinion/what-business-needs-to-know-capcut-new-user-terms)) → **không đưa clip học sinh**. |
| Descript, OpusClip, Runway | Có (upload clip lên cloud) | Giá/điều khoản `TODO`; OpusClip hợp video dài → cắt ngắn (STLab chưa có video dài). Không dùng với clip học sinh. |
| MoneyPrinterTurbo | Gọi LLM + stock (Pexels) + TTS online tùy cấu hình | 134,6k★, MIT ([repo](https://github.com/harry0703/MoneyPrinterTurbo)). Tạo video từ *chủ đề + stock footage* → nội dung chung chung, không phải dự án thật → **không dùng**. |
| Postiz (lập lịch đăng) | Có (token mạng xã hội) | 37,7k★, **AGPL-3.0**, tự host Docker, có MCP ([repo](https://github.com/gitroomhq/postiz-app)) → chỉ ghi nhận. |
| Meta Reels Publishing API | Có | Cần page token + `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`; 30 bài/24 h; có `is_ai_generated`; kiểm bản quyền khi upload ([docs](https://developers.facebook.com/docs/video-api/guides/reels-publishing)). Rủi ro: token toàn quyền đăng trang. **Không dùng lúc này.** |

## 3. Pháp lý & an toàn
- **Hình ảnh học sinh (Việt Nam):**
  - Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15, hiệu lực 01/01/2026: công bố thông tin đời sống riêng tư của trẻ **từ đủ 7 tuổi** cần
    đồng ý của **trẻ và người đại diện theo pháp luật**; rút đồng ý → phải dừng xử lý
    ([lsvn.vn](https://lsvn.vn/cong-bo-du-lieu-ca-nhan-cua-tre-tu-07-tuoi-phai-duoc-nguoi-dai-dien-dong-y-a167752.html),
    [hatinh.gov.vn](https://hatinh.gov.vn/vi/bai-viet/luat-bao-ve-du-lieu-ca-nhan-chinh-thuc-co-hieu-luc-thi-hanh-tu-ngay-112026)).
  - Nghị định 13/2023 (trước Luật) xếp **hình ảnh cá nhân** là dữ liệu cá nhân cơ bản và Điều 20 yêu cầu đồng ý của cha mẹ/giám hộ
    ([Điều 20](https://hethongphapluat.com/nghi-dinh-13-2023-nd-cp-ve-bao-ve-du-lieu-ca-nhan/dieu-20)). Quan hệ NĐ13 ↔ Luật 91 và nghị định
    hướng dẫn mới: `TODO` (không phải tư vấn pháp lý).
  - Bộ luật Dân sự 2015 Điều 32 (quyền đối với hình ảnh) – `TODO` đọc văn bản gốc.
  - **Thực hành đề xuất:** phiếu đồng ý phụ huynh (+ chữ ký trẻ ≥ 7 tuổi) ghi rõ nền tảng, mục đích, quyền rút lại; danh sách học sinh
    "không lên hình" → `video-ai/projects/<x>/rieng-tu.txt` (đã có cơ chế); không ghi họ tên đầy đủ/trường/lớp trên video; quay tay/sản phẩm
    thay mặt khi không chắc; gỡ video trong 24 h khi phụ huynh yêu cầu.
- **Chính sách nền tảng:** TikTok yêu cầu tài khoản ≥ 13 tuổi, tài khoản 13–15 mặc định riêng tư
  ([TikTok youth safety](https://ads.tiktok.com/help/article/tiktok-ads-policy-youth-safety?lang=en)); YouTube tắt bình luận trên nhiều video
  có trẻ vị thành niên từ 2019 ([YouTube blog](https://blog.youtube/news-and-events/more-updates-on-our-actions-related-to)) → video có
  học sinh trên YouTube có thể mất bình luận; chính sách hiện hành `TODO`.
- **Bản quyền nhạc:** xem §2.4. Shorts > 1 phút có claim → bị chặn.
- **Dữ liệu gửi ra ngoài:** pipeline đề xuất chạy **cục bộ** (FreeCAD, FFmpeg, faster-whisper, Blender). Ảnh khung hình + kịch bản Claude đọc
  = gửi lên Claude (như video-ai đã ghi). Cấm đưa clip học sinh lên CapCut/Descript/OpusClip/Runway; `is_ai_generated`/nhãn AI khi dùng giọng
  TTS hoặc ảnh sinh AI (Meta có trường này trong API).

## 4. Bảng nguồn
| Tên | Link | ★/cập nhật | License | Chạy gì/gọi mạng | Dùng cho | Khuyến nghị |
|---|---|---|---|---|---|---|
| FreeCAD `saveImage` | [wiki](https://wiki.freecad.org/Std_ViewScreenShot) | lõi FreeCAD 1.1 | LGPL-2.1 | Cục bộ | Chuỗi ảnh turntable/exploded/lắp ráp | **Dùng** |
| FFmpeg | [ffmpeg.org](https://ffmpeg.org) | đã cài | LGPL/GPL | Cục bộ | Ghép, crop, chữ, loudnorm | **Dùng** |
| FilmCraft 0.9.0 | [repo](https://github.com/storytold/filmcraft) | 15k★ | Apache-2.0 | Cục bộ, cổng 7920 không token | Clip người thật + phụ đề | **Dùng** (đã có) |
| faster-whisper | [repo](https://github.com/SYSTRAN/faster-whisper) | 26,1k★ | MIT | Tải model HF 1 lần | Phụ đề lời nói | **Dùng** (đã có) |
| Bambu A1 timelapse | [wiki](https://wiki.bambulab.com/en/software/bambu-studio/Timelapse) | firmware hãng | — | Ghi SD; Bambu Studio | Timelapse in | **Dùng** |
| Blender 5.2 + MCP | [mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | đã cài | GPL / MIT | Cục bộ (telemetry tắt) | Render đẹp, turntable | **Thử** |
| STEP Importer (Clonephaze) | [extensions](https://extensions.blender.org/add-ons/step-importer/) | v1.2.1, 06/2026 | GPL-3.0+ | Cục bộ (`TODO` kiểm) | STEP → Blender | **Thử** (hoặc glTF từ FreeCAD) |
| Remotion + skills | [repo](https://github.com/remotion-dev/remotion), [skills](https://www.remotion.dev/docs/ai/skills) | 66,8k★ | Remotion License (free ≤ 3 NV) | Node, Chromium, telemetry `TODO` | Template motion graphics | **Để sau** |
| MoviePy | [repo](https://github.com/Zulko/moviepy) | 15,0k★ | MIT | Gọi FFmpeg | Ghép nhiều lớp Python | Để sau |
| Motion Canvas | [repo](https://github.com/motion-canvas/motion-canvas) | 19,4k★ | MIT | Node, trình duyệt | Animation TS | Không cần |
| Manim Community | [repo](https://github.com/ManimCommunity/manim) | 41,8k★ | MIT | Cục bộ, LaTeX | Giải thích cơ cấu | Để sau |
| ExplodedAssembly | [repo](https://github.com/JMG1/ExplodedAssembly) | 141★, cũ (0.17) | LGPL-2.1 | Cục bộ | Exploded FreeCAD | **Không** |
| VieNeu-TTS v3 | [repo](https://github.com/pnnbao97/VieNeu-TTS) | 2,9k★ | Apache-2.0 (trọng số `TODO`) | Tải model lần đầu; cục bộ CPU | Giọng Việt | **Thử** |
| edge-tts | [repo](https://github.com/rany2/edge-tts) | 12,4k★ | `TODO` (GPL-3?) | Gửi văn bản tới Microsoft | Giọng Việt thử | Chỉ thử |
| viXTTS | [HF](https://huggingface.co/dotyfake/Doty_viXTTS) | — | Coqui CPML (NC) | Cục bộ GPU | Giọng Việt | Không (VieNeu đủ) |
| Pixabay Music | [license](https://pixabay.com/service/license-summary/) | — | Pixabay Content License | Tải tay | Nhạc đa nền tảng | **Dùng** (ghi nguồn) |
| FB Sound Collection / TikTok CML | [TikTok](https://ads.tiktok.com/business/en-US/blog/audio-library-royalty-free-music) | — | Chỉ trong nền tảng | Trong app | Nhạc trong app | **Dùng** trong app |
| CapCut / Descript / OpusClip / Runway | — | — | Điều khoản dịch vụ | Upload cloud | Caption/AI | **Không** cho clip học sinh |
| MoneyPrinterTurbo | [repo](https://github.com/harry0703/MoneyPrinterTurbo) | 134,6k★ | MIT | LLM + Pexels + TTS online | Video từ stock | **Không** |
| Postiz | [repo](https://github.com/gitroomhq/postiz-app) | 37,7k★ | AGPL-3.0 | Token MXH, Docker | Lập lịch đăng | Không (ghi nhận) |
| Meta Reels API | [docs](https://developers.facebook.com/docs/video-api/guides/reels-publishing) | — | Meta Platform Terms | Token trang | Tự đăng | Không (ghi nhận) |

Ngày cập nhật repo: chưa đọc được (API GitHub giới hạn lượt, 2026-10-24) → `TODO` khi thêm vào `COMMUNITY.md`.

## 5. Đề xuất pipeline dự án → video

### 5.1 Luồng
```
maker/<project>/ (FCStd, images/, ASSEMBLY.md, README)  +  timelapse SD  +  clip tự quay (video-ai)
   │ 1. Claude viết video/brief.md theo mẫu (series, hook, CTA, có học sinh? đồng ý?)
   │ 2. render-frames.py (FreeCAD, chạy nền qua fc_job.py): turntable | exploded | steps → frames/*.png 1080×1920
   │ 3. Claude viết script.srt (chữ trên màn hình) từ README/ASSEMBLY
   │ 4. make-reel.py (FFmpeg): ghép frames + timelapse + clip FilmCraft out/ + chữ hook/CTA + phụ đề + logo
   │ 5. QA: contact sheet 12 khung (kiem-tra.jpg) + độ dài/LUFS/độ phân giải; Tuan xem .mp4
   ▼
maker/<project>/video/<yyyy-mm-dd>-<mau>/out/{reel-nomusic.mp4, reel-music.mp4, caption.txt, nhac.txt}
```
- Đặt script chung ở `video-ai/scripts/` (tên tiếng Anh), template mới cạnh `templates/reel-9x16/`; đầu ra trong thư mục dự án
  (quy tắc "1 dự án 1 thư mục"). Toolhub: thêm nút "Tạo video" vào trang Dự án (sau khi chạy ổn bằng lệnh).
- `caption.txt`: Claude soạn caption + hashtag cho từng nền tảng; **Tuan tự đăng**.

### 5.2 Bốn mẫu video chuẩn (15–30 s, 9:16)
| Mẫu | Cấu trúc (giây) | Nguồn | Công cụ |
|---|---|---|---|
| **A. CAD → vật thật** | 0–2 vật thật + chữ hook · 2–12 turntable model · 12–20 exploded · 20–26 vật thật chạy · 26–30 CTA | FCStd + clip điện thoại | FreeCAD saveImage + FFmpeg (+ FilmCraft cho clip) |
| **B. Timelapse in** | 0–1 vật in xong · 1–15 timelapse tăng tốc, crop 9:16 · 15–20 gỡ khỏi bàn in · chữ: thời gian in, g nhựa (lấy từ `slice.py`) | Timelapse A1 + clip gỡ | FFmpeg |
| **C. Lắp ráp N bước** | 0–2 thành phẩm · mỗi bước 1,5–2 s ảnh `step-XX-a/b` + số bước · cuối robot chạy | `images/assembly/` + clip | FFmpeg (zoom nhẹ Ken Burns) |
| **D. Lỗi in & cách sửa** | 0–3 ảnh lỗi phóng to + "Vì sao?" · 3–15 nguyên nhân (chữ) · 15–25 sau khi sửa · CTA | Ảnh/clip lỗi + `printability.py` | FFmpeg + giọng Tuan/TTS |

### 5.3 Ước lượng thời gian (ước lượng, buổi ≈ 3–4 giờ)
| Việc | Ước |
|---|---|
| `render-frames.py` (turntable + exploded + steps) dựa trên `render_*.py` có sẵn | 1 buổi |
| `make-reel.py` + template `project-reel` (chữ, phụ đề, logo, 2 bản nhạc/không nhạc) + QA contact sheet | 1–1,5 buổi |
| Thử 4 mẫu trên cyberbrick-car và pushrod-arm, chỉnh theo Tuan duyệt | 1 buổi |
| Blender turntable đẹp (tùy chọn) | 1 buổi |
| Sau khi xong: mỗi video mới | 20–40 phút máy + Tuan duyệt (ước) |

## 6. Top 5 việc nên làm
1. **Soạn phiếu đồng ý phụ huynh** (trẻ ≥ 7 tuổi ký cùng) theo Luật 91/2025 + danh sách "không lên hình" – làm trước mọi video có học sinh.
2. **Viết `render-frames.py`** (FreeCAD, headless qua `fc_job.py`): turntable/exploded/steps 1080×1920 – tái dùng `render_car.py`, `render_assembly.py`.
3. **Viết `make-reel.py`** (FFmpeg) + template `project-reel`: dựng mẫu A và C từ dữ liệu có sẵn, xuất kèm contact sheet để Tuan duyệt.
4. **Bật timelapse A1** (Smooth, thẻ ≤ 32 GB format trên máy in) cho 3 lần in tới → mẫu B.
5. **Nhật ký tương tác** `stlab/marketing/video-log.csv`: ngày, nền tảng, mẫu, độ dài, hook, lượt xem, thời gian xem TB, % xem hết, chia sẻ, lưu,
   bình luận, tin nhắn hỏi khóa học; xem lại 2 tuần/lần, giữ mẫu tốt. Meta Insights có plays, reach, watch time/average watch time, shares, saves
   (Meta đổi tên sang Minutes Viewed/Average Minutes Viewed – thứ cấp, [TipRanks](https://www.tipranks.com/news/the-fly/meta-says-views-to-become-primary-metric-on-facebook));
   chỉ số TikTok Analytics chính thức `TODO`.

## 7. Cần Tuan quyết
1. **Nền tảng ưu tiên:** đề xuất Facebook Page (phụ huynh Đức Trọng) + TikTok; Shorts/IG đăng lại cùng file. Zalo OA? (chưa có tài liệu).
2. **Học sinh lên hình:** có/không, từ độ tuổi nào; ai giữ phiếu đồng ý.
3. **Giọng:** giọng Tuan thu âm vs TTS (VieNeu cục bộ) vs không lời + chữ.
4. **Nhạc:** chỉ nhạc trong app từng nền tảng, hay thư viện Pixabay của STLab.
5. **Thương hiệu:** màu chữ, logo, câu CTA (template đang `TODO` màu vàng `#FFD400`).
6. Có cần Blender (đẹp hơn, thêm 1 buổi) hay FreeCAD render là đủ cho giai đoạn đầu.
7. Remotion (license ≤ 3 nhân viên) – STLab có bao nhiêu nhân viên? Nếu > 3 và thu phí thì cần license công ty.

## Điểm chưa xác nhận (TODO)
- Giới hạn upload TikTok chính thức; thông số Zalo Video; điều khoản YouTube Audio Library chính thức; chính sách hiện hành của YouTube/Meta
  với video có trẻ vị thành niên; Điều 32 BLDS và nghị định hướng dẫn Luật 91/2025.
- Bước timelapse A1 trong wiki (trang chặn đọc tự động), thẻ 64 GB; chất lượng camera A1 khi crop dọc (chỉ ~1088 px chiều cao gốc → crop 9:16
  còn ~612×1088, phải phóng to – có thể mờ).
- Blender 5.2: addon MCP, STEP Importer có chạy được không; thời gian render EEVEE/khung trên GTX 1660 SUPER.
- Ngày cập nhật/release các repo; license edge-tts; license trọng số VieNeu-TTS; telemetry Remotion; Assembly4 repo 404.
- Không có số liệu tương tác gốc cho các series ở §1.3 – tất cả là gợi ý.

## Nguồn
- Meta: [Reels Publishing API](https://developers.facebook.com/docs/video-api/guides/reels-publishing) · [Creators – Reels](https://creators.facebook.com/tools/reels) ·
  [Instagram Media Insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/)
- YouTube: [Understand three-minute Shorts](https://support.google.com/youtube/answer/15424877?hl=en) · [Create Shorts](https://support.google.com/youtube/answer/10343433?hl=en) ·
  [Minors safety 2019](https://blog.youtube/news-and-events/more-updates-on-our-actions-related-to)
- TikTok: [Creative tips (63 %, 120 BPM)](https://ads.tiktok.com/business/nl-NL/blog/66) · [Auction Ads Creative Tips PDF](https://ads.tiktok.com/business/library/Auction_Ads_Creative_Tips.pdf) ·
  [Commercial Music Library](https://ads.tiktok.com/business/en-US/blog/audio-library-royalty-free-music) · [Youth safety](https://ads.tiktok.com/help/article/tiktok-ads-policy-youth-safety?lang=en)
- Bambu Lab: [Timelapse wiki](https://wiki.bambulab.com/en/software/bambu-studio/Timelapse) · [Live View Camera A1](https://eu.store.bambulab.com/products/live-view-camera-a1) ·
  (thứ cấp) [forum SD 32/64 GB](https://forum.bambulab.com/t/timelapse-videos-with-sd-cards-32-gb/5042)
- FreeCAD: [Std ViewScreenShot](https://wiki.freecad.org/Std_ViewScreenShot) · [Macro Screen Wiki](https://wiki.freecad.org/Macro_Screen_Wiki) · [Automation.py](https://free-cad.sourceforge.net/SrcDocu/d3/d31/Automation_8py_source.html)
- Blender: [STEP Importer](https://extensions.blender.org/add-ons/step-importer/)
- Repo: [Remotion](https://github.com/remotion-dev/remotion) ([LICENSE](https://raw.githubusercontent.com/remotion-dev/remotion/main/LICENSE.md), [skills](https://www.remotion.dev/docs/ai/skills)) ·
  [Motion Canvas](https://github.com/motion-canvas/motion-canvas) · [MoviePy](https://github.com/Zulko/moviepy) · [Manim](https://github.com/ManimCommunity/manim) ·
  [faster-whisper](https://github.com/SYSTRAN/faster-whisper) · [edge-tts](https://github.com/rany2/edge-tts) · [VieNeu-TTS](https://github.com/pnnbao97/VieNeu-TTS) ·
  [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) · [Postiz](https://github.com/gitroomhq/postiz-app) · [ExplodedAssembly](https://github.com/JMG1/ExplodedAssembly)
- Nhạc: [Pixabay license summary](https://pixabay.com/service/license-summary/) · (thứ cấp) [Facebook Sound Collection – TechCrunch](https://techcrunch.com/2017/12/08/facebook-sound-collection/)
- Pháp lý VN: [Luật 91/2025 – trẻ ≥ 7 tuổi (lsvn.vn)](https://lsvn.vn/cong-bo-du-lieu-ca-nhan-cua-tre-tu-07-tuoi-phai-duoc-nguoi-dai-dien-dong-y-a167752.html) ·
  [Hiệu lực 01/01/2026 (hatinh.gov.vn)](https://hatinh.gov.vn/vi/bai-viet/luat-bao-ve-du-lieu-ca-nhan-chinh-thuc-co-hieu-luc-thi-hanh-tu-ngay-112026) ·
  [NĐ 13/2023 Điều 20](https://hethongphapluat.com/nghi-dinh-13-2023-nd-cp-ve-bao-ve-du-lieu-ca-nhan/dieu-20)
- Thứ cấp khác: [Social Media Today – IG 3 phút](https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-3-minutes/737766/) ·
  [Social Media Today – Meta Reels Ads guide](https://www.socialmediatoday.com/news/meta-publishes-reels-ads-guide-instagram-facebook-video-marketing/752771/) ·
  [SmartCompany – CapCut terms](https://www.smartcompany.com.au/opinion/what-business-needs-to-know-capcut-new-user-terms) ·
  [TipRanks – Meta views metric](https://www.tipranks.com/news/the-fly/meta-says-views-to-become-primary-metric-on-facebook) · [ayrshare – TikTok media](https://ayrshare.com/docs/media-guidelines/tiktok)
