# Cú Bông – mở rộng giáo trình Seed (mẫu giáo 3–6 tuổi)

Ngày tra cứu: **2026-11-17**. Người viết: edu-researcher. Yêu cầu của Tuan (2026-11-17): tìm hiểu giáo trình để tăng bài học lên; chỉ viết báo cáo, không sửa `units.yaml` hay code.

Ký hiệu: **[VB]** đã đọc nội dung văn bản; **[TÓM TẮT]** chỉ đọc được đoạn tóm tắt hoặc trích dẫn thứ cấp; **[THIẾT KẾ]** quyết định của STLab, chưa có nguồn đo; **TODO** chưa kiểm được, không dùng làm số liệu.

## Tóm tắt 5 dòng

1. **Vấn đề lớn nhất là cách hiểu số từ.** Thông tư 50/2020 ghi 35 / 70 / 100 từ theo độ tuổi, kiểu "70 (thêm 35 so với 3–4 tuổi)" [VB, bản tổng hợp]: đây là số **lũy kế**. `units.yaml` lại coi mỗi cấp là **70 và 100 từ mới** (ghi "không tính lại"), tức gấp khoảng 2–3 lần Bộ. Tuan cần chọn cách hiểu trước khi thêm bài.
2. Nếu theo lũy kế, Bộ tăng khoảng **35, 35, 30 từ mới ở mỗi cấp** (khoảng 1 từ mới mỗi tuần học). Trung bình **4–5 từ mỗi chủ đề**; bản hiện tại có 8,75 từ/chủ đề ở cấp 4–5 và 12,5 ở cấp 5–6.
3. Cambridge Starters (dành cho khoảng 6–12 tuổi [TÓM TẮT]) **không cho số từ kiểm được** trong phiên này (PDF quá 10 MB). Chủ đề dùng tham khảo được, số đếm để TODO. Không có danh sách chủ đề đã kiểm của SSS, LearnEnglish Kids hay Oxford Phonics World.
4. Đề xuất 12 chủ đề mới (52 từ): 3 chủ đề cho cấp 3–4 (Plus), 5 cho 4–5 và 4 cho 5–6, bám Việt Nam và Lâm Đồng, không trùng từ cũ (mục 3).
5. Xen kẽ Plus theo chủ đề có điều kiện; bé xin chủ đề: giữ lộ trình, đáp ngay bằng từ đã có trong bảng, từ ngoài bảng ghi vào hộp "bé hỏi". Bằng chứng về "follow the child" còn yếu.

## 1. Số từ hợp lý cho học ở nhà hằng ngày

### 1.1 Mốc của Bộ (đã kiểm)
- Thông tư 50/2020/TT-BGDĐT, hiệu lực 31/03/2021 (ký 31/12/2020) [VB, bản tổng hợp luatvietnam]:
  - Thời lượng: 35 tuần/năm, tối thiểu 2 hoạt động/tuần, mỗi hoạt động khoảng 25–35 phút.
  - Từ/cụm từ: 3–4 tuổi khoảng 35 (đếm 1–3); 4–5 tuổi khoảng 70, "thêm 35 từ so với trẻ 3–4 tuổi" (đếm 1–5); 5–6 tuổi khoảng 100, "tăng thêm 35 từ so với trẻ 4–5 tuổi" (đếm 1–10).
  - Nghe và làm theo: 4–5 tuổi làm theo 2 yêu cầu đơn giản; 5–6 tuổi làm theo 2–3 yêu cầu liên tiếp.
  - Nguồn: https://luatvietnam.vn/giao-duc/thong-tu-50-2020-tt-bgddt-chuong-trinh-lam-quen-voi-tieng-anh-danh-cho-tre-em-mau-giao-200155-d1.html (truy cập 2026-11-17). **TODO:** đối chiếu công báo hoặc vbpl.vn; thuvienphapluat trả 403 khi truy cập.
  - Thông tư 09/2025/TT-BGDĐT sửa đổi 50/2020; bản tổng hợp ghi việc sửa liên quan phân cấp thẩm quyền (áp dụng Điều 10 từ 01/07/2025). Có đụng tới số từ hay không – **TODO**.

### 1.2 Đối chiếu với `seed/units.yaml` (đã đếm)
| Cấp | Bộ (lũy kế) | Bộ (mức tăng) | units.yaml Core (từ mới trong cấp) | Chênh |
|---|---|---|---|---|
| Seed 1 (3–4) | 35 | 35 | 35 (8 chủ đề) | khớp |
| Seed 2 (4–5) | 70 | +35 | 70 (8 chủ đề, 8,75 từ/chủ đề) | gấp 2 nếu lũy kế |
| Seed 3 (5–6) | 100 | +30 | 100 (8 chủ đề, 12,5 từ/chủ đề) | gấp khoảng 3 nếu lũy kế |

- Đầu file `units.yaml` ghi: "Mỗi cấp tự đứng được ... không tính lại". Hiểu theo cách này thì một bé học hết cả 3 cấp có khoảng **205 từ**, trong khi Bộ ghi khoảng 100 cho 5–6 tuổi.
- Hệ quả: README đã định nghĩa **Core = chuẩn Bộ** (quyết định 2026-11-11). Core hiện tại vượt chuẩn, không khớp định nghĩa đó.
- **Khuyến nghị [THIẾT KẾ]:** Tuan chọn một trong hai cách.
  - **A. Giữ nguyên `units.yaml`**, ghi rõ Core là "lũy kế STLab" và không gọi là chuẩn Bộ. Đánh đổi: mục tiêu Plus dễ đạt hơn nhưng bé 2–3 tuổi chịu tải lớn hơn và tài liệu không khớp Thông tư khi trường mầm non hỏi.
  - **B. (khuyến nghị)** Coi số Bộ là Core lũy kế: S2 giữ khoảng 35 từ mới Core, S3 khoảng 30 từ mới Core; phần còn lại chuyển sang Plus (không xóa). Đánh đổi: Core ngắn lại, Plus dài ra, và cần soạn lại buổi trong `lessons-seed/` – việc này thuộc lập trình viên/Tuan, không làm trong báo cáo này.

### 1.3 Nhịp học ở nhà
- Bộ: khoảng 1 từ mới mỗi tuần (35 từ/35 tuần). Máy hiện đặt 2 từ mới mỗi tuần theo ROADMAP (`lessons/ROADMAP.md`, bảng 4–5 tuổi). Với 2 từ/tuần, Core 35 từ hết trong khoảng 18 tuần (đúng như Tuan đã đo).
- Học hằng ngày ở nhà nhiều hơn 2 buổi/tuần ở trường, nên áp lực không nằm ở số từ mà ở **số lần ôn**. Không có nguồn nào cho biết tốc độ tối đa mà bé 2–5 tuổi học được ở nhà; TODO.
- **Khuyến nghị [THIẾT KẾ]:** giữ 2 từ mới/tuần cho cấp 4–6 (ROADMAP đã có), và khi hết Core của cấp thì chuyển sang ôn cách quãng + Plus, không thêm Core mới. Đánh đổi: bé đi nhanh hơn Bộ nên cần Plus sớm; nếu chậm hơn thì Core kéo dài qua năm học.

### 1.4 Cambridge và các chương trình khác
- **Cambridge Pre A1 Starters:** trang chính thức chỉ ghi nhóm "Pre A1 to A2", "a child's first steps in English", không có số tuổi hay số từ [VB, trang Cambridge]: https://www.cambridgeenglish.org/exams-and-tests/young-learners-english/ (truy cập 2026-11-17). Danh sách từ 2018 (https://www.cambridgeenglish.org/images/351849-pre-a1-starters-word-list-2018.pdf) **không mở được** (quá 10 MB). Số từ: **TODO**. Nguồn phụ ghi Starters cho 6–12 tuổi [TÓM TẮT, xem báo cáo 2026-11-07].
- **Oxford Phonics World:** dành cho 4–8 tuổi, dạy 44 âm; không tìm được danh sách chủ đề hay số từ công khai [TÓM TẮT]: https://eltpreprod.oup.com/parent/oxfordphonicsworld . **TODO:** lấy scope-and-sequence trong Teacher's Book.
- **Super Simple Songs:** bài theo chủ đề (giới từ, hình, bộ phận cơ thể, nhạc cụ...) [TÓM TẮT]: https://supersimple.com/content-type/songs/page/23 . Không có số từ theo tuổi.
- **LearnEnglish Kids (British Council):** nhóm bài theo chủ đề truyện, bài hát cổ, chant ngữ pháp [TÓM TẮT]: https://learnenglishkids.britishcouncil.org/en/songs . Không có số từ.
- Kết luận: không có chương trình nào trong nhóm này cho số từ theo tuổi có nguồn. Thông tư 50/2020 vẫn là mốc duy nhất kiểm được.

## 2. Phát hiện theo cấp học (bổ sung)

- **Mầm non 3–4 tuổi:** mục tiêu là chào hỏi, tạm biệt, hỏi tên. Chủ đề nên là danh từ đơn (đồ vật, sự vật), có động tác [VB, Thông tư 50/2020].
- **4–5 tuổi:** hỏi về bản thân và gia đình; làm theo 2 yêu cầu [VB]. Chủ đề có địa danh và văn hóa quen (Tết, Trung thu, Đà Lạt) hợp với "câu hỏi về bản thân".
- **5–6 tuổi:** hỏi khả năng và sở thích; làm theo 2–3 yêu cầu liên tiếp [VB]. Có thể đưa câu hỏi "Can you…?" và "What's the…?" và cảm xúc phức tạp hơn.
- **Trùng lặp giữa các cấp trong `units.yaml`** (để tránh đếm đôi khi mở rộng): ví dụ `happy`, `sad` (S1 Core → S2 Core); `teddy`, `robot`, `cake`, `water`, `hot`, `circle`, `star`, `grandpa`, `family` (S1 Plus → S2 Core); `tiger`, `frog` (S2 Plus → S3 Core).

### 2.1 Từ đã dùng (để không trùng khi thêm bài)
- Seed hiện tại: toàn bộ từ trong `seed/units.yaml` (Core và Plus, 3 cấp).
- Bài Cú Bông cũ 01–12 (`maker/english-teacher/lessons/`), chưa có trong Seed: `watermelon`, `strawberry`, `grape` (S3 có `grapes`), `cloud`, `wind`, `sit`, `stand`, `kite` (S2 có), `block` (S2 có `blocks`), `teddy bear` (S1 có `teddy`).
- Mục 3 dưới đây đã loại các từ trên.

## 3. Đề xuất chủ đề mới (mở rộng)

Quy ước: [THIẾT KẾ] cho toàn bộ danh sách. Từ đã kiểm không trùng với Seed và bài 01–12. Số từ mỗi chủ đề 4–5. Cấp 3–4 không thêm Core (Core đã đủ 35), nên đây là nhóm **Plus**.

### Seed 1 (3–4 tuổi) – nhóm Plus, 3 chủ đề
| Chủ đề (tiếng Việt) | Từ gợi ý | Mẫu câu / hành động | Gắn với đời sống |
|---|---|---|---|
| Bữa ăn gia đình | cup, plate, spoon, glass | "I drink water." / Cầm cốc, nói tên | Bữa cơm ở nhà |
| Trái cây Việt Nam | coconut, papaya, durian, jackfruit | "I like papaya." | Trái cây bé thấy ở chợ |
| Sân chơi | swing, slide, sand, bubble | "Go on the swing!" | Sân trường, công viên |

### Seed 2 (4–5 tuổi) – 5 chủ đề
| Chủ đề | Từ gợi ý | Mẫu câu / hành động | Gắn với đời sống |
|---|---|---|---|
| Tết | new year, gift, lucky money, dragon, peach blossom | "Happy new year!" / "I have a gift." | Tết Nguyên đán ("lì xì" = lucky money) |
| Trung thu | moon, lantern, mooncake, bright | "Look at the moon!" | Rước đèn, bánh trung thu |
| Đà Lạt và rừng thông | pine tree, mist, lake, flower garden | "The pine tree is tall." | Lâm Đồng: rừng thông, sương, hồ |
| Vườn rau | cabbage, corn, pumpkin, onion, peas | "I like corn." | Vườn rau quanh trung tâm |
| Trong bếp | pot, pan, bowl, chopsticks | "Pass the bowl, please." | Bữa ăn cơm Việt |

### Seed 3 (5–6 tuổi) – 4 chủ đề
| Chủ đề | Từ gợi ý | Mẫu câu / hành động | Gắn với đời sống |
|---|---|---|---|
| Lớp học thủ công | scissors, glue, paint, paper, sticker | "Can you cut the paper?" | Hoạt động Make của STLab |
| Thiên nhiên Việt Nam | field, bamboo, waterfall, hill, cave | "Is it tall or short?" | Cánh đồng, tre, thác |
| Đường an toàn | traffic light, helmet, taxi, zebra crossing | "Wear a helmet!" / "Stop at the light." | An toàn xe máy, dạy trẻ qua đường |
| Cảm xúc nâng cao | worried, surprised, proud, bored | "I'm proud of my robot." | Nói về cảm xúc sau sản phẩm Make |

Ghi chú:
- Tổng: 12 chủ đề mới (3 + 5 + 4), 52 từ mới (12 + 22 + 18). Số này **chỉ có nghĩa khi Tuan chọn cách A hoặc B ở mục 1.2**. Nếu chọn B, các từ này vào Plus hoặc thay phần Core đã chuyển đi.
- Từ `helmet`, `taxi`, `dragon`, `lantern` là từ thông dụng, nhưng chưa đối chiếu với danh sách Cambridge (TODO).
- Chủ đề Tết, Trung thu có dịp cụ thể nên có thể đổi theo lịch lớp. Lưu ý văn hóa: không dùng mô-típ tôn giáo hay chính trị.
- Chủ đề "gia đình" không đề xuất thêm: Seed đã có "My family" và Cú Bông đã cảnh báo về hoàn cảnh gia đình khác nhau (`cu-bong-chu-de-tieng-anh-2-5-tuoi.md`).

## 4. Xen kẽ Plus vào chủ đề hay đợi hết Core cấp

**Khuyến nghị [THIẾT KẾ]:** xen kẽ **có điều kiện theo chủ đề**.
- Từ Plus của chủ đề N chỉ đưa vào khi bé đã đạt "bé làm được" của Core chủ đề N (ít nhất 2 buổi ôn).
- Mỗi chủ đề đưa tối đa 1–2 từ Plus, và Plus được ôn lại ở chủ đề N+1 hoặc N+2 (ôn cách quãng).
- Plus là từ tùy chọn: không tính vào "bé làm được" và không kiểm tra.

Căn cứ:
- **Ôn cách quãng tốt hơn ôn dồn** với trẻ nhỏ. Vlach, Ankowski & Sandhofer (2012) trên trẻ 2 tuổi: nhóm học cách quãng cho kết quả tốt hơn sau khoảng 15 phút trễ, trong khi nhóm học dồn cho kết quả tốt ngay lúc học [TÓM TẮT, PDF không đọc được: https://babytalk.psych.ucla.edu/wp-content/uploads/sites/271/2021/03/Vlach_Ankowski_Sandhofer-2012.pdf ; tên tạp chí: TODO].
- Thông tư không cấm dạy từ ngoài Core (đây là ước lượng của STLab).

Đánh đổi:
- **Xen kẽ:** Plus đến sớm, ôn cách quãng tốt hơn, bé không chán. Nhưng bé thấy nhiều từ hơn trong một tuần và máy phải theo dõi điều kiện.
- **Hết Core cấp rồi mới Plus:** đơn giản, khớp cấu trúc hiện tại. Nhưng với học hằng ngày, Plus đến sau 18 tuần hoặc hơn, bé giỏi có thể chán.

## 5. Bé xin chủ đề giữa buổi

Bằng chứng:
- **Tương tác có đáp ứng là điều kiện học từ** (Roseberry, Hirsh-Pasek & Golinkoff 2014, 36 trẻ 24–30 tháng; video phát sẵn không học được) [TÓM TẮT từ báo cáo 2026-11-06: https://pmc.ncbi.nlm.nih.gov/articles/PMC3962808].
- **Can thiệp đáp ứng có kết quả nhỏ:** Girolametto, Pearce & Weitzman (1996), JSHR 39(6), RCT khoảng 25 trẻ 1;11–2;11 tuổi, 11 tuần, 150 phút/tuần, phụ huynh được huấn luyện. Nhóm can thiệp có vốn từ lớn hơn [TÓM TẮT, Cochrane table: https://pmc.ncbi.nlm.nih.gov/articles/PMC8407295/table/CD004110-tblf-0016]. Số liệu do Hanen (đơn vị phát triển chương trình) trình bày nên cần cẩn trọng; cỡ mẫu nhỏ, chưa có bản sao độc lập.
- **Guided play** (Weisberg, Hirsh-Pasek & Golinkoff 2013, Mind, Brain, and Education 7(2), DOI 10.1111/mbe.12015) [TÓM TẮT]: người lớn đặt mục tiêu, trẻ giữ quyền chọn trong khuôn đã chuẩn bị. Nghiên cứu hình học sơ bộ cho thấy trẻ học tốt hơn so với chơi tự do và dạy trực tiếp.
- **Montessori "follow the child"** [TÓM TẮT]: Marshall (2017), npj Science of Learning 2:11, kết luận đánh giá Montessori còn ít và có hạn chế phương pháp, thiếu thử nghiệm ngẫu nhiên có đối chứng; Lillard & Else-Quest (2006) là nghiên cứu bốc thăm nhỏ, cho thấy kết quả tốt nhưng không tách riêng nguyên lý "follow the child" [TÓM TẮT: https://news.virginia.edu/node/133410 ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6161506/]. **Không có nguồn nào chứng minh "chuyển chủ đề theo bé" tốt hơn giữ lộ trình.**

**Khuyến nghị [THIẾT KẾ], theo 4 bậc:**
1. Bé nói hoặc chỉ vào bất kỳ đồ vật nào: cô đáp ngay bằng từ đó (đáp ứng, không đổi chủ đề).
2. Bé gọi từ đã có trong bảng (chủ đề đã qua hoặc sắp tới): dạy ngắn 1 từ, đưa vào hàng ôn.
3. Bé gọi từ ngoài bảng: cô đáp bằng câu có sẵn, ghi vào "hộp bé hỏi" để soạn sau, không dạy thêm trong buổi.
4. Cho bé chọn trong khuôn 2 lựa chọn (guided play): ví dụ "Ball or car?" trong chủ đề đang học.

Đánh đổi: giữ lộ trình thì ôn cách quãng được đảm bảo và cuối năm đạt mục tiêu; cho bé "nhảy" thì bé hào hứng hơn nhưng lộ trình gãy và khó đo tiến bộ. Chọn bậc 1–4 vừa phải để không làm vỡ lộ trình.

## 6. Việc tiếp theo (không làm trong báo cáo này)

1. Tuan chọn cách A hoặc B (mục 1.2). Đây là quyết định trước khi thêm bất kỳ từ nào.
2. Đối chiếu Thông tư 50/2020 trên công báo hoặc vbpl.vn (hiện chỉ có bản tổng hợp).
3. Tải danh sách Pre A1 Starters bằng tay (PDF lớn) và đếm số từ, đối chiếu từng từ trong mục 3.
4. Lấy scope-and-sequence của Oxford Phonics World Teacher's Book (TODO).
5. Mở bản gốc Vlach et al. 2012, Girolametto 1996, Marshall 2017 để kiểm con số.

## Nguồn

Ngày truy cập mọi nguồn: 2026-11-17 trừ khi ghi khác.

1. Thông tư 50/2020/TT-BGDĐT, bản tổng hợp luatvietnam [VB, thứ cấp]: https://luatvietnam.vn/giao-duc/thong-tu-50-2020-tt-bgddt-chuong-trinh-lam-quen-voi-tieng-anh-danh-cho-tre-em-mau-giao-200155-d1.html . Bản thuvienphapluat (https://thuvienphapluat.vn/van-ban/Giao-duc/Thong-tu-50-2020-TT-BGDDT-Chuong-trinh-lam-quen-voi-tieng-Anh-danh-cho-tre-em-mau-giao-468715.aspx) trả 403.
2. Cambridge Young Learners, trang chính (không có số từ): https://www.cambridgeenglish.org/exams-and-tests/young-learners-english/
3. Cambridge Pre A1 Starters word list 2018 (không mở được, quá 10 MB): https://www.cambridgeenglish.org/images/351849-pre-a1-starters-word-list-2018.pdf
4. Languageadvisor, trang wordlist (không có danh sách): https://languageadvisor.net/pre-a1-starters-a1-movers-and-a2-flyers-wordlist/
5. Oxford Phonics World, OUP (không có danh sách chủ đề): https://eltpreprod.oup.com/parent/oxfordphonicsworld [TÓM TẮT]
6. Super Simple Songs (danh sách bài): https://supersimple.com/content-type/songs/page/23 [TÓM TẮT]
7. LearnEnglish Kids, British Council (bài theo chủ đề): https://learnenglishkids.britishcouncil.org/en/songs [TÓM TẮT]
8. Vlach, Ankowski & Sandhofer (2012), PDF không đọc được: https://babytalk.psych.ucla.edu/wp-content/uploads/sites/271/2021/03/Vlach_Ankowski_Sandhofer-2012.pdf [TÓM TẮT; tạp chí: TODO]
9. Girolametto, Pearce & Weitzman (1996), JSHR 39(6):1274–1283; bảng RCT trong Cochrane: https://pmc.ncbi.nlm.nih.gov/articles/PMC8407295/table/CD004110-tblf-0016 [TÓM TẮT]
10. Roseberry, Hirsh-Pasek & Golinkoff (2014), Child Development 85(3):956–970: https://pmc.ncbi.nlm.nih.gov/articles/PMC3962808 [TÓM TẮT, từ báo cáo 2026-11-06]
11. Weisberg, Hirsh-Pasek & Golinkoff (2013), Mind, Brain, and Education 7(2):104–112, DOI 10.1111/mbe.12015 [TÓM TẮT]
12. Hirsh-Pasek và cộng sự (2015), Psychological Science in the Public Interest 16(1):3–34, DOI 10.1177/1529100615569721: https://www.psychologicalscience.org/publications/educational-apps.html [TÓM TẮT]
13. Marshall (2017), npj Science of Learning 2:11: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6161506/ [TÓM TẮT]
14. Lillard & Else-Quest (2006), Science, tóm tắt báo chí Đại học Virginia: https://news.virginia.edu/node/133410 [TÓM TẮT; số trang: TODO]
15. Hanen, cách giúp trẻ học từ mới (từ báo cáo 2026-11-07): https://hanen.org/information-tips/how-to-help-your-child-learn-new-words [TÓM TẮT]
16. Dữ liệu nội bộ: `stlab/english-curriculum/seed/units.yaml`, `stlab/english-curriculum/README.md`, `maker/english-teacher/lessons/01–12`, `maker/english-teacher/lessons/ROADMAP.md`.
