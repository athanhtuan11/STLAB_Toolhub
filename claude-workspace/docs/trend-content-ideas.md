# Trend và ý tưởng video ngắn cho STLab

Ngày: 2026-10-24 (thứ Bảy) · Người làm: Claude (agent nghiên cứu) · Trạng thái: **chỉ nghiên cứu**, chưa quay/dựng/đăng gì.

**Phạm vi:** video ngắn 15–30 s cho Facebook Page + TikTok (đăng lại YouTube Shorts / Instagram Reels). Mục tiêu: tương tác, rồi
tin nhắn hỏi khóa học từ phụ huynh. Kỹ thuật dựng, thông số nền tảng, 4 mẫu A/B/C/D, pháp lý ảnh học sinh và nhạc: xem
[project-video-marketing-research.md](project-video-marketing-research.md). File này **không lặp lại**, chỉ tham chiếu (vd. "§3 bài kia").

Ký hiệu: (thứ cấp) = blog/aggregator, không phải nền tảng · `TODO` = chưa xác nhận · ⚠ = trend > 6 tháng hoặc ngày không rõ, có thể đã hết.

**Tình trạng dự án thật (đọc ngày 2026-10-24):**
| Dự án | Có sẵn để làm video | Chưa có |
|---|---|---|
| pushrod-arm | 13 ảnh lắp `freecad/images/assembly/step-01..13-{a,b}.png`, ASSEMBLY.pdf 15 trang, `print-overview.png`, số liệu in 7 bàn **10 h 26, ~289 g PETG**, lịch sử lỗi in thử 23/10 (phần nhô không support, chi tiết nhỏ bong) | Ảnh/clip lần in thử lỗi (không thấy trong repo, `TODO` hỏi Tuan có ảnh điện thoại không), bản in hoàn chỉnh, clip chạy |
| cyberbrick-car | 6 ảnh render (`car-front/iso/side/top`, `chassis-iso/top`), 3 bàn **~7 h 17, ~118 g**, mẹo "không support" (đuôi ≤ 45°, mái 50°), v0.2 | Chưa in, chưa chạy, tốc độ chỉ ước tính 0,6–0,9 m/s (chưa đo) |
| smart-home, solar-battery, uwb-drone-positioning, diy-audio-amp, pi4-dslr-control | Chỉ có `CLAUDE.md` mục tiêu `TODO` | Chưa có gì để quay → **không dùng** trong 8 tuần tới |
| stlab/ (giáo án, báo cáo phụ huynh) | Thư mục trống | — |

## 0. Tóm tắt
- **Trend nóng nhất lúc này là Halloween** (đến 31/10): costume reveal góc thấp (Ramalama), Pumpkin Head Illusion, "Day vs Night"
  ([New Engen 14/10/2026](https://newengen.com/insights/halloween-tiktok-reels-trends/)) + **#MWHalloween2026** của MakerWorld (hạn 25/10, quá gấp).
- **Ngách 3D in đang chạy bằng "vật in khớp động/fidget"** (gear fidget, bạch tuộc cơ khí – [VelocitySpy 19/10/2026](https://www.velocityspy.com/trending/3d-printing/), thứ cấp)
  và **clip quy trình/thỏa mãn** (process, close-up) – hợp với timelapse A1 + gỡ chi tiết.
- **Âm thanh trend phần lớn là nhạc có license, tài khoản doanh nghiệp không dùng được** → STLab nên bám **format**, dùng giọng Tuan/nhạc thư viện.
- **Lịch VN 8 tuần:** Halloween 31/10 · mùa dã quỳ Đà Lạt (cuối 10–giữa 11) · **20/11 Ngày Nhà giáo** · Black Friday 27/11 (gợi ý quà STEM) ·
  FTC Vietnam 2026 chủ đề "BIOBUZZ" (phát động 09/10) · Festival Hoa Đà Lạt 18/12/2026–03/01/2027 · Tết 06/02/2027.
- **Làm được ngay không cần học sinh:** 7 ý tưởng từ ảnh lắp ráp pushrod-arm và render cyberbrick-car (mẫu C + "đoán xem").
- **Lịch đề xuất:** 3 video/tuần (T3, T5, T7, 19:30–20:30, **giả thuyết cần đo**), 11 video trong 4 tuần, 3 series có nhận diện STLab.
- **Cần Tuan quyết trước:** có quay mặt Tuan không, mua/in thêm vật Halloween/20/11 không, phiếu đồng ý phụ huynh khi nào xong.

## 1. Trend đang chạy

| # | Trend | Nền tảng | Ngày / nguồn | Phù hợp STLab vì sao | Còn nóng? |
|---|---|---|---|---|---|
| T1 | **Ramalama Costume Walk** – camera sát đất, "bàn chân" tiến lại gần rồi lộ trang phục; nhạc Róisín Murphy "Ramalama (Bang Bang)" | TikTok, Reels | [New Engen TikTok 01/10, cập nhật 14/10/2026](https://newengen.com/insights/october-tiktok-trends/); [New Engen Halloween 14/10/2026](https://newengen.com/insights/halloween-tiktok-reels-trends/) | **Xe RC vốn chạy sát đất** → "costume walk" của xe/robot là góc quay tự nhiên. Nhạc là bản có license, nguồn ghi "creator accounts only" ([SocialPilot](https://www.socialpilot.co/blog/instagram-reels-trends)) | Nóng đến 31/10, hết sau Halloween |
| T2 | **Pumpkin Head Illusion** – phối cảnh ép, quả bí che đầu người ở xa | TikTok, Reels | New Engen 14/10/2026 (như trên) | Thay người bằng **cánh tay robot "cầm" bí** hoặc bí in 3D → không cần học sinh | Đến 31/10 |
| T3 | **"Day vs Night" decor** – cùng một góc, ngày ↔ đêm, chuyển theo beat | TikTok, Reels | New Engen 14/10/2026 | Góc phòng lab ngày ↔ đêm có đèn LED/ESP32 → mở màn cho smart-home sau này | Đến 31/10 |
| T4 | **31 Days of Halloween** – series đánh số theo ngày | TikTok | SocialPilot, tháng 10/2026 (ngày cập nhật `TODO`), [link](https://www.socialpilot.co/blog/tiktok-trends) (thứ cấp) | Cấu trúc "Ngày X/N" dùng cho series **"8 tuần làm xe RC"** (đánh số kéo người xem tập tiếp) | Format bền; bản Halloween hết 31/10 |
| T5 | **Satisfying process / close-up** – âm "Where To Find Me", "Autumn Minute", "Hello, October" (nhãn process, handmade) | TikTok | SocialPilot tháng 10/2026 (thứ cấp) | Timelapse A1, gỡ chi tiết PETG khỏi PEI, trục vít in đứng, bánh răng ăn khớp | Format bền; âm thanh theo mùa thu, hết ~cuối 11 |
| T6 | **Vật in khớp động / fidget** (gear fidget spinner 673K view, fidget toy 943K, mechanical octopus 165K – xếp theo tốc độ view/giờ, tuần) | TikTok | [VelocitySpy cập nhật 19/10/2026](https://www.velocityspy.com/trending/3d-printing/) (thứ cấp, dữ liệu TikTok Shop) | Bánh răng/thanh răng/trục vít của pushrod-arm **là** "fidget cơ khí"; print-in-place trên trang TikTok Discover ([link](https://www.tiktok.com/discover/3d-printing-trend), không đọc được tự động) | Nóng (rising) |
| T7 | **Answer in One Word** – hỏi ChatGPT/bạn bè, chỉ được trả lời 1 từ | TikTok | New Engen 01/10/2026 | "Hỏi thầy Tuan, trả lời 1 từ" về robot/in 3D – dễ quay, kéo bình luận | Đang chạy (tháng 10) |
| T8 | **Two Fishes** – nhép audio Love Island, bảo vệ một ý kiến "gây tranh cãi" | TikTok | New Engen 01/10/2026 | Ý kiến thật kiểu "Trẻ 10 tuổi nên học in 3D trước lập trình" → tranh luận phụ huynh. Audio có thể bị khóa cho tài khoản doanh nghiệp | Đang chạy, dễ hết nhanh |
| T9 | **Before/after đổi camera** – "Upside Down" (Diana Ross) | Reels | [Buffer 14/10/2026](https://buffer.com/resources/trending-audio-instagram/) | Cuộn nhựa → chi tiết in; render → vật thật (mẫu A) | Đang chạy |
| T10 | **Fan Transition** – quay từ trên xuống, vật che lướt qua để đổi | TikTok | New Engen 01/10/2026 | Nhìn từ trên bàn in: bàn trống → bàn đầy chi tiết (tay lướt che) | Đang chạy |
| T11 | **#MWHalloween2026 "Print Your Spook"** – đăng ảnh/clip vật in Halloween + gắn model | MakerWorld + Instagram | Nộp 24/09–**25/10/2026**, công bố 30/10 (theo tóm tắt tìm kiếm; trang [MakerWorld](https://makerworld.com/en/community/tag?name=MWHalloween2026) trả 403 → `TODO` xác nhận) | Lên được cộng đồng Bambu toàn cầu | **Hạn mai** → gần như bỏ lỡ |
| T12 | **AI ảnh → mô hình 3D** – Meshy-6 image-to-3D trong MakerLab (từ 17/03/2026), xuất STL/3MF | MakerWorld | [Abduzeedo](https://www.abduzeedo.com/meshy-6-ai-image-3d-now-live-makerworld-0), [Utusan/PR 03/2026](https://www.utusan.com.my/pr-newswire-en/2026/03/how-to-turn-any-image-into-a-full-color-3d-print-in-one-click-meshys-multi-color-printing-powered-by-meshy-6-is-now-live-on-makerworld/) (thứ cấp) | "Tranh vẽ của con → AI → đồ chơi in 3D": phụ huynh hiểu ngay. Gửi ảnh lên dịch vụ ngoài, tốn credit | ⚠ ra mắt 7 tháng trước; chủ đề "AI" vẫn nóng nhưng chưa có số liệu VN |
| T13 | **CyberBrick làm đồ chơi STEM mùa quà** ("STEM toy to beat this Christmas") | Báo maker | [All3DP](https://all3dp.com/4/bambu-labs-cyberbrick-is-the-stem-toy-to-beat-this-christmas/) – trang 403, **ngày `TODO`**; bản kit Standard tháng 03/2026 ([forum Bambu](https://forum.bambulab.com/t/new-makers-supply-parts/115013?page=7)) | STLab dùng đúng CyberBrick → video "quà STEM tự làm" mùa Black Friday/Noel | ⚠ ngày bài chưa xác nhận |
| T14 | **20/11 Ngày Nhà giáo VN** – thư pháp tri ân, vẽ tranh tri ân, múa "Lời Ca Tri Ân", ghép ảnh | TikTok VN | [TikTok Discover "trend thầy cô"](https://www.tiktok.com/discover/trend-th%E1%BA%A7y-c%C3%B4), [video thư pháp @klong_official](https://www.tiktok.com/@klong_official/video/7438461166118030599) – video năm 2024–2026, số liệu 2026 `TODO` | "Thư pháp" phiên bản maker: **chữ tri ân in 3D** / cánh tay robot cầm bút | Theo mùa: từ ~10/11 đến 20/11 |
| T15 | **Mùa dã quỳ Đà Lạt** – cuối 10 đến hết 11, đẹp nhất giữa 11 | Facebook/TikTok du lịch VN | [Tiim 2026](https://tiim.com.vn/chuyen-muc/song/festival-hoa-da-lat-2026-khi-cao-nguyen-goi-mua-hoa.html), [iVIVU 2025](https://www.ivivu.com/blog/2025/10/du-lich-da-lat-thang-10-11-me-man-mua-hoa-da-quy-ruc-ro/) (thứ cấp) | Màu dã quỳ ≈ vàng sợi nhựa `#E8B33A`; nhận diện "STLab – Lâm Đồng"; hút người địa phương (phụ huynh gần trung tâm) | Theo mùa: đến cuối 11 |
| T16 | **FIRST Tech Challenge Vietnam 2026** – chủ đề "BIOBUZZ" (cảm hứng thiên nhiên), lớp 7–12, ~40 đội | Báo VN | [Vietnam+ 09/10/2026](https://www.vietnamplus.vn/phat-dong-cuoc-thi-robotics-quoc-te-danh-cho-hoc-sinh-tu-lop-7-den-lop-12-post1141092.vnp); [VTV](https://vtv.vn/phat-dong-cuoc-thi-robotics-quoc-te-first-tech-challenge-vietnam-2026-100261010091131126.htm) | Video giải thích "robot học từ thiên nhiên" (xi-lanh đẩy ≈ cơ bắp) → phụ huynh có con lớp 7–12 quan tâm thi | Mới (2 tuần), lịch thi `TODO` |
| T17 | **Phụ huynh VN quan tâm STEM/AI/Robotics** – Chung kết QG STEM, AI và Robotics 2026; Robotics Lâm Đồng lần I (vòng 30/06/2026, >124 đội) | Báo VN | [Tiền Phong](https://hoahoctro.tienphong.vn/khai-mac-chung-ket-quoc-gia-stem-ai-va-robotics-2026-nang-luong-cho-tuong-lai-post1842101.tpo), [ĐH Đà Lạt](https://itc.dlu.edu.vn/cuoc-thi-sang-tao-robotics-tinh-lam-dong-lan-thu-i-nam-2026/) | Bằng chứng nhu cầu tại chính tỉnh Lâm Đồng | ⚠ sự kiện đã qua (mùa hè 2026); dùng làm bối cảnh |
| T18 | **YouTube: Shorts dẫn về video dài**; người xem đánh giá theo "tham gia/hiểu/thấy" (46 %/41 %/41 %) | YouTube | [AIR tóm tắt YouTube Culture & Trends 2026, cập nhật 18/09/2026](https://air.io/en/trending/youtubes-2026-culture-trends-report-decoded-for-creators) (thứ cấp; khảo sát **Mỹ**, N=939) | Ủng hộ format "giải thích ngắn + để ngỏ câu hỏi" và series; không phải số liệu VN | Bối cảnh, không phải trend |

**Chưa xác nhận được (bị chặn đọc tự động 2026-10-24):** TikTok Creative Center (lọc VN/Education – trang chỉ trả khung đăng nhập), trang TikTok Discover,
MakerWorld contest/campaign (403), All3DP (403), Google Trends VN (không có công cụ đọc). → **Không có số liệu trend riêng Việt Nam tháng 10/2026**.
`TODO` Tuan mở Creative Center trong app (Trends → Hashtag → Việt Nam → Education, 7 ngày) và Google Trends (VN, 12 tháng: "robot", "in 3D",
"STEM", "lập trình cho trẻ", "Bambu Lab") rồi chụp màn hình gửi lại.
⚠ "3D printed 67 trend" (meme "6-7") xuất hiện trên trang TikTok Discover cập nhật cuối 09/2026, gốc meme từ 2025 → **có thể đã hết**, không đề xuất.

## 2. Ý tưởng

Cột: **Mẫu** A/B/C/D (bài kia §5.2) hoặc mới · **HS** = có học sinh (cần phiếu đồng ý, bài kia §3) · **Thời gian** = ước lượng Tuan + máy ·
**Mục tiêu**: V view, S chia sẻ, L lưu, B bình luận, T tin nhắn. Mọi video: 9:16, 1080×1920, phụ đề cứng, CTA cuối.

### (a) Làm được NGAY với tài liệu có sẵn, không quay học sinh

**1. "13 bước ra cánh tay robot"** · Mẫu C · bám T6 (vật cơ khí) + T4 (đếm số) · dự án pushrod-arm
- Hook 0–3 s: ảnh `step-13-b` + chữ **"Cánh tay robot này có 13 bước lắp. Bước 9 khó nhất."**
- Cảnh: 0–3 thành phẩm · 3–24 mỗi bước 1,6 s (`step-XX-a` → `-b`, bộ đếm "Bước 4/13") · 24–28 ảnh `print-overview.png` "7 bàn in · 10 h 26 · 289 g" · 28–30 CTA.
- Công cụ: FFmpeg (Ken Burns nhẹ). Không quay. ~1 buổi lần đầu (viết `make-reel.py`), ~30 ph các lần sau.
- Mục tiêu: L, S. CTA: **"Lưu lại – học sinh STLab tự lắp cái này. Nhắn 'ROBOT' để nhận lịch học thử."**
- `TODO` kiểm bước 9 có thật là khó nhất (đọc ASSEMBLY.md) – nếu không, đổi câu hook.

**2. "Đoán xem: chiếc xe này chạy được bao nhiêu km/h?"** · Mới (quiz) · bám T18 (tham gia) · cyberbrick-car
- Hook: render `car-iso.png` xoay chậm + **"Xe RC học sinh tự thiết kế. Đoán tốc độ – đúng thì tặng 1 buổi học thử."**
- Cảnh: 0–3 hook · 3–15 turntable (4 render ghép hoặc `render-frames.py`) · 15–22 chữ "222,5 mm · 118 g nhựa · 7 h in" · 22–25 "Đáp án khi xe chạy thật" · CTA.
- Lưu ý: **không nói số tốc độ** (chỉ ước tính 0,6–0,9 m/s, chưa đo). Câu "học sinh tự thiết kế" chỉ đúng nếu có học sinh tham gia – nếu không, dùng **"STLab thiết kế"**.
- 1–2 h. Mục tiêu: B. CTA: "Bình luận số của bạn" (không quà nếu chưa sẵn sàng tặng thật).

**3. "Thiết kế để KHÔNG cần support: 4 mẹo"** · Mới (giải thích) · bám T5 · cyberbrick-car
- Hook: **"Xe này in 7 tiếng mà không có 1 cây support nào. Đây là 4 mẹo."**
- Cảnh: 4 mẹo × 5 s trên render `car-side`/`chassis-iso` có mũi tên: đuôi ≤ 45° · mái trong dốc 50° · hốc bánh nhọn 45° · gân nam châm 50° · CTA.
- FFmpeg + chữ; giọng Tuan (khuyến nghị) hoặc chỉ chữ. 2 h. Mục tiêu: L (dân maker lưu), S.

**4. "Trục vít in đứng hay nằm?"** · Mẫu D (biến thể) · bám T6 · pushrod-arm (P7_Worms)
- Hook: **"In nằm thì hỏng. In đứng thì được. Vì sao?"**
- Cảnh: ảnh lát cắt/preview Bambu Studio 2 hướng (chụp màn hình) · chữ "ren lơ lửng khi nằm ngang" · "dựng đứng: 14 phút, 0,9 g" · CTA.
- Cần chụp màn hình preview slicer (Tuan, 10 ph). 2 h. Mục tiêu: L, B.

**5. "Hỏi thầy Tuan – trả lời 1 từ"** · Mới, bám **T7 Answer in One Word** · không dự án cụ thể
- Hook (chữ to): **"Hỏi thầy dạy robot. Chỉ được trả lời 1 từ."**
- Cảnh: 6–8 câu hỏi × 3 s ("Mấy tuổi học được?" – "Tám." `TODO` Tuan tự chọn tuổi thật · "Khó nhất?" – "Kiên nhẫn." · "Máy in yêu thích?" – "A1."…) · CTA.
- Quay Tuan bằng điện thoại 10 ph (không học sinh). FilmCraft cắt + phụ đề. 1,5 h. Mục tiêu: B, T. CTA: "Hỏi thêm ở bình luận, mình trả lời 1 từ."

**6. "Từ bản vẽ đến bàn in"** · Mẫu A (nửa đầu) · bám T9 before/after · pushrod-arm
- Hook: **"Hôm qua là bản vẽ. Hôm nay là 7 bàn in."** · cảnh: render các bước → `print-overview.png` → (khi có) ảnh bàn in thật.
- Chỉ dùng ảnh có sẵn + 1 ảnh điện thoại bàn in. 1 h. Mục tiêu: V. CTA: "Theo dõi để xem nó cử động."

**7. "Cánh tay robot tốn bao nhiêu tiền nhựa?"** · Mới (con số) · pushrod-arm, cyberbrick-car
- Hook: **"289 gam nhựa = 1 cánh tay robot. Tốn bao nhiêu tiền?"**
- Cảnh: cân/cuộn nhựa → bảng 7 bàn → con số tiền (giá cuộn **`TODO` Tuan điền giá thật**, không đoán) → "linh kiện điện tử mới là phần đắt" → CTA.
- 1 h khi có giá. Mục tiêu: S, T (phụ huynh hay hỏi chi phí).

### (b) Cần quay thêm (vật in, máy in, có thể có học sinh)

**8. "Timelapse 10 tiếng trong 20 giây"** · Mẫu B · T5, T10 · pushrod-arm P1/P4 · không HS
- Hook: thành phẩm 0,5 s rồi **"10 tiếng 26 phút. Xem lại trong 20 giây."** · Fan Transition (T10): tay lướt che bàn trống → bàn đầy.
- Cần: bật timelapse A1 (bài kia §2.2) hoặc điện thoại trên giá. Máy chạy sẵn, Tuan ~1 h dựng. Mục tiêu: V, S.

**9. "Chờ nguội rồi mới gỡ" (satisfying)** · Mới · T5 · bất kỳ bàn PETG · không HS
- Hook: **"Gỡ PETG lúc nóng là mất mặt bàn PEI. Đợi 10 phút rồi xem."** · close-up uốn bàn, chi tiết bật ra, âm thanh thật (ASMR, không cần nhạc).
- Đúng lưu ý TDS Bambu PETG Basic (README pushrod-arm). 30 ph quay + 30 ph dựng. Mục tiêu: L, V.

**10. "Lần in đầu thất bại – và cách sửa"** · Mẫu D · pushrod-arm, lỗi thật 23/10 · không HS
- Hook: ảnh lỗi phóng to + **"Lần in đầu của tụi mình hỏng thế này."**
- Cảnh: lỗi phần nhô không support · chi tiết nhỏ bong bàn → nguyên nhân → sửa: support tự vẽ + brim + `printability.py` → bản in lại.
- Cần: ảnh lỗi thật (`TODO` Tuan còn giữ chi tiết hỏng không?) + bản in lại. 2 h. Mục tiêu: L, B. Rất hợp uy tín giáo dục (thật thà về lỗi).

**11. "Lần đầu cử động"** · Mẫu A (đủ) · pushrod-arm sau khi in thật · không HS
- Hook: **"Không servo ở vai. Không servo ở khuỷu. Vậy nó nâng bằng gì?"** → cận cảnh trục vít N20 + thanh răng chạy.
- Cần in đủ 7 bàn + lắp + điều khiển CyberBrick. Chạy lần đầu tốc độ thấp (README: N20 kẹt → nóng). Mục tiêu: V, S.

**12. "Xe RC đi Halloween"** · T1 Ramalama low-angle walk · cyberbrick-car (khi có) hoặc **xe CyberBrick chính hãng** · không HS
- Hook: camera sát sàn, bánh xe tiến lại + **"Khách mời Halloween năm nay…"** → lộ thân xe đội mũ phù thủy/bí ngô in 3D.
- Âm: bản gốc có license, **tài khoản doanh nghiệp có thể không chọn được** → dùng tiếng động cơ thật + giọng. 2–3 h (in mũ nhỏ ~1 h). Mục tiêu: V, S.

**13. "Tranh của con thành đồ chơi"** · Mới, T12 AI image-to-3D · HS (tranh vẽ, **không mặt**) · phiếu đồng ý (tranh là sản phẩm của trẻ)
- Hook: tranh vẽ tay + **"Con vẽ. AI dựng 3D. Máy in làm thật."** · cảnh: tranh → màn hình MakerLab → timelapse → đồ chơi cạnh tranh.
- Rủi ro: gửi ảnh tranh lên Meshy/MakerWorld (dữ liệu ra ngoài); tốn credit; nhãn "có dùng AI". 1 buổi. Mục tiêu: S, T.

**14. "POV: buổi đầu ở STLab"** · Mới · HS (tay, không mặt; vẫn cần đồng ý vì là buổi học thật) · lớp học thử
- Hook: **"Buổi 1: chưa biết vặn vít. Buổi 8: …"** · cảnh tay học sinh lắp/điều khiển · không tên, không trường lớp.
- FilmCraft (bài kia; clip HS **không** đưa lên CapCut). Mục tiêu: T. Chỉ làm khi đã có phiếu.

**15. "Đua xe RC trong lab"** · Mẫu mới (pha nổi bật trước) · HS · cyberbrick-car ×2
- Hook: pha về đích sát nút + **"Ai thắng? Xe in 7 tiếng hay xe in 5 tiếng?"** → giải thích tỉ số truyền 1:21 vs 1:37 (khi có đo thật).
- Chỉ làm khi xe chạy thật + có đồng ý. Mục tiêu: V, B.

**16. "Phụ huynh hỏi – thầy trả lời"** · Mới (giải đáp) · không HS · Tuan nói 20 s
- Câu hỏi thật từ tin nhắn/bình luận (ẩn tên): "Con 9 tuổi học được không?", "Có cần máy tính ở nhà?" · hook là câu hỏi in to.
- Dùng để trả lời bình luận dạng video (TikTok "reply with video"). 30 ph/video. Mục tiêu: T. Bền, không phụ thuộc trend.

### (c) Theo mùa / sự kiện (8 tuần tới: 26/10–20/12/2026)

| # | Ý tưởng | Trend/nguồn | Hook 3 s | Kịch bản 15–30 s | Quay / dự án / công cụ | Ngày đăng đề xuất | Mục tiêu · CTA |
|---|---|---|---|---|---|---|---|
| 17 | **Robot cầm bí ngô** (Pumpkin Head Illusion) | T2, New Engen 14/10 | "Đầu của robot năm nay là…" | phối cảnh ép: bí in 3D nhỏ sát camera, cánh tay robot/khung xe phía sau → lộ mẹo phối cảnh → "học sinh học phối cảnh + thiết kế" | Không HS; in bí ~1–2 h (model MakerWorld, **kiểm license**); điện thoại | **Thứ Năm 29/10** | V, S · "Tag người cần xem" |
| 18 | **Lab ban ngày vs ban đêm** | T3 | "Lab robot lúc 8 h sáng… và 8 h tối" | 2 góc giống nhau, chuyển theo beat, đêm có đèn LED/ESP32 nhấp nháy màu cam | Không HS; 30 ph quay | **Thứ Bảy 31/10** | V · "Theo dõi – tháng 11 tụi mình làm nhà thông minh" (chỉ nói nếu thật sự làm) |
| 19 | **Bông dã quỳ in 3D** | T15 | "Dã quỳ Đà Lạt nở rồi. Bông này thì không bao giờ tàn." | timelapse in hoa vàng → đặt cạnh dã quỳ thật bên đường Đức Trọng → logo STLab | Không HS; model hoa (tự vẽ FreeCAD hoặc MakerWorld, kiểm license); cảnh ngoài trời buổi sáng sương | **Thứ Năm 12/11** | S (người địa phương) · "Lưu lại – mùa dã quỳ chỉ đến cuối tháng 11" |
| 20 | **Robot viết chữ "Tri ân thầy cô"** / chữ tri ân in 3D | T14 (thư pháp tri ân) | "Năm nay học sinh không viết thiệp. Tụi mình in." | timelapse chữ nổi "Cảm ơn thầy cô" in 3D (màu xanh thông + vàng) → học sinh trao (tay) → chữ CTA | Có HS (tay) → cần đồng ý, hoặc không HS chỉ vật; Blender/FreeCAD text → STL | **Thứ Tư 18/11** (trước 20/11 2 ngày) | S, T · "Phụ huynh muốn con tự làm quà 20/11? Nhắn tin – xưởng mở thứ Bảy" (`TODO` có mở xưởng không) |
| 21 | **"Robot học từ thiên nhiên"** – xi-lanh đẩy ≈ cơ bắp | T16 FTC "BIOBUZZ", Vietnam+ 09/10 | "Cánh tay robot này dùng 'cơ bắp', không phải khớp quay." | so sánh cánh tay người ↔ pushrod (render + clip chạy) → "chủ đề FTC 2026 là thiên nhiên" → CTA | Không HS; cần clip chạy (#11) | **Thứ Bảy 21/11** (hoặc lùi nếu chưa in xong) | L, S · "Con lớp 7–12 muốn thi robotics? Nhắn tin." |
| 22 | **Gợi ý quà STEM: mua sẵn hay tự làm?** | T13 + Black Friday **27/11/2026** | "Quà Noel cho con: 1 hộp đồ chơi hay 1 chiếc xe con tự in?" | xe CyberBrick chính hãng vs xe STLab tự thiết kế: thời gian in, nhựa, cái con học được | Không HS; cyberbrick-car khi đã in | **Thứ Năm 26/11** | T · "Khóa 'Làm xe RC trong 4 buổi' dịp Noel" (`TODO` có khóa không) |
| 23 | **Xe RC kéo xe trượt tuyết** | Noel 25/12 (ngoài 8 tuần, chuẩn bị trước) | "Ông già Noel năm nay đổi xe." | xe RC kéo hộp quà in 3D qua phòng, low-angle | Không HS; cyberbrick-car | Thứ Ba 22/12 | V, S |
| 24 | **Robot tặng hoa Festival Hoa Đà Lạt** | Festival Hoa Đà Lạt 18/12/2026–03/01/2027 (Tiim, thứ cấp) | "Festival Hoa Đà Lạt có thêm một 'bông' biết cử động." | cánh tay robot gắp hoa in 3D → đặt vào giỏ | Không HS; pushrod-arm | Thứ Bảy 19/12 | S (địa phương) |
| 25 | **Đếm ngược khai giảng khóa Tết/học kỳ 2** | Tết 06/02/2027 (lịch nghỉ công chức đang đề xuất, [Viettel Store](https://viettelstore.vn/tin-tuc/dem-ngay-den-tet-2027-con-bao-nhieu-ngay-nua-lich-nghi-tet-dinh-mui-chi-tiet), thứ cấp) | "Nghỉ Tết 7 ngày – con định làm gì?" | ghép 3 dự án đã quay → lịch khóa | Không HS | Tháng 1/2027 (ngoài 4 tuần) | T |

## 3. Lịch 4 tuần (26/10–22/11/2026)

Tần suất: **3 video/tuần** cho 1 người (bài kia gợi ý 2–3, không có nguồn chính thức). Một video đăng cả 4 nơi (bản không nhạc + thêm âm trong app).
Giờ: **19:30–20:30 tối T3/T5, 9:00 sáng T7** – là **giả thuyết**: các nghiên cứu toàn cầu nói buổi tối 18–22 h tốt cho TikTok/Reels
([Buffer](https://buffer.com/resources/best-time-to-post-social-media/), [Sprout Social](https://sproutsocial.com/insights/best-times-to-post-on-social-media/), [XRoad: chưa có nghiên cứu riêng SEA](https://xroadstudio.com/blog/best-time-to-post-on-tiktok)),
**không có nguồn cho phụ huynh VN**. Đo 4 tuần bằng Insights rồi chỉnh. Ghi số vào `stlab/marketing/video-log.csv` (bài kia §6).

| Tuần | Thứ Ba 19:30 | Thứ Năm 19:30 | Thứ Bảy 9:00 | Việc nền trong tuần |
|---|---|---|---|---|
| **1** (26/10–01/11) | 27/10 · **#1 13 bước ra cánh tay robot** | 29/10 · **#17 Robot cầm bí ngô** (Halloween) | 31/10 · **#18 Lab ngày vs đêm** (Halloween) | Viết `make-reel.py`; bật timelapse A1; **in đủ 7 bàn pushrod-arm**; soạn phiếu đồng ý |
| **2** (02–08/11) | 03/11 · **#3 4 mẹo không support** | 05/11 · **#5 Hỏi thầy Tuan – 1 từ** | 07/11 · **#8 Timelapse 10 h trong 20 s** | Lắp pushrod-arm; ảnh lỗi in cũ |
| **3** (09–15/11) | 10/11 · **#10 Lần in đầu thất bại** | 12/11 · **#19 Bông dã quỳ in 3D** | 14/11 · **#2 Đoán tốc độ xe** (quiz) | In cyberbrick-car; chữ tri ân |
| **4** (16–22/11) | 17/11 · **#9 Chờ nguội rồi gỡ** | **Thứ Tư 18/11** · **#20 Tri ân thầy cô** (đổi ngày vì 20/11) | 21/11 · **#11 Lần đầu cử động** (hoặc #21 nếu đã quay) | Tổng kết số liệu 4 tuần |

Dự phòng nếu chưa có vật in/clip: #6 (bản vẽ → bàn in), #7 (chi phí nhựa), #16 (giải đáp phụ huynh).

## 4. Series

Nhận diện chung (theo `studio/design/DESIGN.md`): nền **xanh thông `#1E5A45`** cho thẻ mở/đóng, chữ trắng hoặc sương `#ECF1EF`; **vàng sợi nhựa `#E8B33A`
chỉ ở dấu nhận diện cạnh chữ STLAB** (đúng nguyên tắc "một điểm nhấn" – không tô vàng cả khung); font **Be Vietnam Pro** 700 tiêu đề, 600 phụ đề.
Khung chuẩn: chữ hook ở 1/3 trên, phụ đề cách đáy 20 % (template `reel-9x16`), logo góc trên trái nhỏ, CTA thẻ cuối 2 s.
`TODO` thêm template `project-reel` vào `video-ai/templates/` với các giá trị trên (khi làm `make-reel.py`).

| Series | Tên hiển thị / hashtag riêng | Nội dung | Nhận diện riêng | Tần suất | Ý tưởng thuộc series |
|---|---|---|---|---|---|
| **S1. Từ bản vẽ ra robot** | "Bản vẽ → Robot · Tập N" · #BanVeRaRobot | 1 dự án thật đi từ CAD → in → lắp → chạy; mỗi tập 1 giai đoạn, đánh số kiểu "31 days" (T4) | thanh tiến trình 7 bước quy trình STLab ở đáy (màu bước: 3 Thiết kế `#1E5A45`, 5 In 3D `#B87A00`…) | 1/tuần | #1, #6, #8, #11, #21; sau đó cyberbrick-car (#2, #22) |
| **S2. Sửa lỗi in 30 giây** | "Lỗi in #N" · #SuaLoiIn3D | 1 lỗi thật → vì sao → sửa (support, brim, PETG nguội, hướng in) | thẻ đầu chữ "LỖI" trên nền xanh, nhãn PASS/FAIL theo màu `#257A45`/`#B3341F` kèm chữ (DESIGN.md: trạng thái bằng chữ + màu) | 1/tuần | #3, #4, #9, #10 |
| **S3. Hỏi thầy Tuan** | "Hỏi thầy Tuan" · #HoiThayTuan | trả lời câu hỏi phụ huynh/học sinh, trả lời bình luận bằng video | khung Tuan nói, câu hỏi trên thẻ sương `#ECF1EF` | 1/tuần | #5, #16 |

Hashtag chung (gọn 3–5/bài): #STLab #DucTrong #LamDong + 1–2 chủ đề (#3dprinting #bambulab #cyberbrick #robotics #STEM). TikTok VN từng có
#HocCungTikTok / #LearnOnTikTok ([Newsroom TikTok VN](https://newsroom.tiktok.com/vi-vn/ky-niem-1-nam-learnontiktok), ⚠ số liệu cũ) – thêm khi video có tính dạy học.

## 5. Rủi ro

| Rủi ro | Chi tiết | Cách tránh |
|---|---|---|
| **Nhạc trend có bản quyền** | Ramalama, Patient Zero, Two Fishes… phần lớn là nhạc thương mại; nguồn ghi "creator accounts only" / "most popular songs off-limits for business accounts" ([SocialPilot](https://www.socialpilot.co/blog/tiktok-trends)). TikTok CML chỉ dùng trong TikTok; FB Sound Collection chỉ FB/IG (bài kia §2.4). Shorts > 1 phút có claim bị chặn | Bám **format** không bám nhạc; xuất `-nomusic.mp4`; thêm nhạc trong app nếu tài khoản cho phép; giọng Tuan/tiếng động thật thay nhạc; nhạc Pixabay ghi nguồn |
| **Trend không hợp trẻ em** | "Nicole Kidman" (ADÉLA) bị ghi NSFW ([Buffer](https://buffer.com/resources/trending-audio-instagram/)); Halloween hù dọa, máu me; prank (Shaving Cream Prank có trẻ em làm "trò đùa"); "Stop the wedding"; nội dung nhảy nhót đưa học sinh lên làm "diễn viên" | Chỉ bám trend trung tính (phối cảnh, before/after, process). Halloween = dễ thương, không kinh dị. Không dùng học sinh làm đối tượng trêu chọc |
| **Clickbait làm mất uy tín** | Hook "học sinh 10 tuổi tự thiết kế" khi thực tế thầy/AI làm; nói tốc độ xe khi chưa đo; "tặng buổi học" rồi không tặng; hứa khóa học chưa mở | Mỗi con số lấy từ README/BOM (ghi rõ "ước tính" nếu chưa đo); hook gây tò mò nhưng **đúng sự thật**; quà/khóa chỉ hứa khi Tuan xác nhận |
| **Ảnh học sinh** | Luật 91/2025 – đồng ý của trẻ ≥ 7 tuổi + người đại diện (bài kia §3); clip HS không đưa lên CapCut/cloud | Phiếu đồng ý trước tuần 3; ưu tiên quay tay/vật; `rieng-tu.txt` |
| **AI image-to-3D** | Ảnh gửi lên Meshy/MakerWorld; credit trả phí; có thể bị xem là "AI làm hộ" | Chỉ tranh vẽ (không ảnh mặt); ghi rõ "có dùng AI"; nhấn phần học sinh tự làm (vẽ, chỉnh, in, sơn) |
| **License model MakerWorld** | Bí ngô/hoa tải về có thể cấm dùng thương mại/quảng bá | Ưu tiên tự vẽ FreeCAD; nếu tải: ghi license + tác giả trong caption (chính sách Tuan: ghi chú, đưa vào bảng "xem lại khi thương mại") |
| **An toàn khi quay** | Pin Li-ion 2S 7,4 V xe RC; bàn in nóng 70 °C, đầu in 245 °C; N20 kẹt → nóng | Không quay cận tay trẻ gần đầu in; không sạc pin khi không trông; thử robot tốc độ thấp |
| **Trend hết nhanh** | Halloween hết sau 31/10; âm mùa thu hết ~cuối 11 | Video Halloween dựng xong **trước 29/10**; nếu trễ, chuyển thành "behind the scenes" thường |

## 6. Cần Tuan quyết
1. **Mặt Tuan lên video** (S3 "Hỏi thầy Tuan", #5, #16)? Khuyến nghị: có – video người thật tăng tin cậy với phụ huynh. Đánh đổi: tốn thời gian quay, cần thoải mái trước camera.
2. **In thêm vật theo mùa** (bí ngô ~1–2 h, hoa dã quỳ, chữ tri ân) trong tuần 1–3? Khuyến nghị: có cho #17 và #20 (2 dịp chắc chắn nóng). Đánh đổi: chiếm máy A1 khi đang in pushrod-arm 10 h 26.
3. **Phiếu đồng ý phụ huynh** xong khi nào? Lịch 4 tuần cố ý **không có học sinh** cho đến #20 (18/11). Nếu không kịp, #20 chỉ quay vật.
4. **CTA và ưu đãi thật:** từ khóa nhắn tin ("ROBOT"), buổi học thử miễn phí?, khóa Noel/xưởng thứ Bảy có mở không? (#2, #20, #22 phụ thuộc).
5. **Giá cuộn nhựa** để làm #7 (không đoán số).
6. **Tài khoản TikTok/Facebook là cá nhân hay doanh nghiệp** – quyết định được dùng nhạc trend nào (doanh nghiệp: chỉ thư viện thương mại).
7. **Có làm #13 (AI image-to-3D)** – gửi tranh học sinh lên dịch vụ ngoài, tốn credit MakerLab.
8. Bỏ qua **#MWHalloween2026** (hạn 25/10)? Khuyến nghị: bỏ, không kịp làm chỉn chu.

## Nguồn
Ngày trong ngoặc = ngày bài/cập nhật theo trang; "đọc 24/10" = ngày agent đọc.
- New Engen – TikTok Trends October 2026 (đăng 01/10, cập nhật 14/10/2026): https://newengen.com/insights/october-tiktok-trends/
- New Engen – Halloween TikTok & Reels Trends 2026 (14/10/2026): https://newengen.com/insights/halloween-tiktok-reels-trends/
- Buffer – 13 Trending Sounds on Instagram, October 2026 (14/10/2026): https://buffer.com/resources/trending-audio-instagram/
- SocialPilot – TikTok trends October 2026 (ngày cập nhật `TODO`): https://www.socialpilot.co/blog/tiktok-trends · Instagram: https://www.socialpilot.co/blog/instagram-reels-trends
- VelocitySpy – Trending 3D printing products on TikTok (cập nhật 19/10/2026, thứ cấp): https://www.velocityspy.com/trending/3d-printing/
- TikTok Discover "3d printing trend" (không đọc được tự động): https://www.tiktok.com/discover/3d-printing-trend
- TikTok Creative Center (chặn, chưa xác nhận): https://ads.tiktok.com/business/creativecenter/
- MakerWorld #MWHalloween2026 (403, theo tóm tắt tìm kiếm): https://makerworld.com/en/community/tag?name=MWHalloween2026 · contest: https://makerworld.com/en/contests/166
- Meshy-6 image-to-3D trên MakerWorld (03/2026, thứ cấp): https://www.abduzeedo.com/meshy-6-ai-image-3d-now-live-makerworld-0 · https://www.utusan.com.my/pr-newswire-en/2026/03/how-to-turn-any-image-into-a-full-color-3d-print-in-one-click-meshys-multi-color-printing-powered-by-meshy-6-is-now-live-on-makerworld/
- All3DP – CyberBrick STEM toy (403, ngày `TODO`): https://all3dp.com/4/bambu-labs-cyberbrick-is-the-stem-toy-to-beat-this-christmas/
- Bambu forum – CyberBrick Standard kits (03/2026, thứ cấp): https://forum.bambulab.com/t/new-makers-supply-parts/115013?page=7
- AIR – YouTube Culture & Trends 2026 decoded (cập nhật 18/09/2026, thứ cấp, khảo sát Mỹ): https://air.io/en/trending/youtubes-2026-culture-trends-report-decoded-for-creators
- Vietnam+ – FIRST Tech Challenge Vietnam 2026 (09/10/2026): https://www.vietnamplus.vn/phat-dong-cuoc-thi-robotics-quoc-te-danh-cho-hoc-sinh-tu-lop-7-den-lop-12-post1141092.vnp · VTV: https://vtv.vn/phat-dong-cuoc-thi-robotics-quoc-te-first-tech-challenge-vietnam-2026-100261010091131126.htm
- ĐH Đà Lạt – Cuộc thi Sáng tạo Robotics Lâm Đồng lần I 2026: https://itc.dlu.edu.vn/cuoc-thi-sang-tao-robotics-tinh-lam-dong-lan-thu-i-nam-2026/
- Tiền Phong – Chung kết QG STEM, AI và Robotics 2026: https://hoahoctro.tienphong.vn/khai-mac-chung-ket-quoc-gia-stem-ai-va-robotics-2026-nang-luong-cho-tuong-lai-post1842101.tpo
- TikTok Discover "trend thầy cô" (20/11): https://www.tiktok.com/discover/trend-th%E1%BA%A7y-c%C3%B4 · video thư pháp: https://www.tiktok.com/@klong_official/video/7438461166118030599
- Tiim – Festival Hoa Đà Lạt 2026 + mùa dã quỳ (thứ cấp): https://tiim.com.vn/chuyen-muc/song/festival-hoa-da-lat-2026-khi-cao-nguyen-goi-mua-hoa.html · iVIVU (2025): https://www.ivivu.com/blog/2025/10/du-lich-da-lat-thang-10-11-me-man-mua-hoa-da-quy-ruc-ro/
- Viettel Store – Tết 2027 (06/02/2027, đề xuất lịch nghỉ, thứ cấp): https://viettelstore.vn/tin-tuc/dem-ngay-den-tet-2027-con-bao-nhieu-ngay-nua-lich-nghi-tet-dinh-mui-chi-tiet
- TikTok Newsroom VN – #LearnOnTikTok 1 năm (cũ): https://newsroom.tiktok.com/vi-vn/ky-niem-1-nam-learnontiktok
- Giờ đăng (toàn cầu, không riêng VN): https://buffer.com/resources/best-time-to-post-social-media/ · https://sproutsocial.com/insights/best-times-to-post-on-social-media/ · https://xroadstudio.com/blog/best-time-to-post-on-tiktok
- Nội bộ: `docs/project-video-marketing-research.md`, `maker/pushrod-arm/README.md`, `maker/cyberbrick-car/README.md`, `studio/design/DESIGN.md`, `video-ai/CLAUDE.md`.
