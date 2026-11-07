# Cú Bông – cách dạy tốt hơn cho bé 2–5 tuổi (cô Lily, chỉ giọng nói)

Ngày tra cứu: 2026-11-07. Trạng thái: nghiên cứu, chờ Tuan duyệt. Không sửa `maker/english-teacher/lessons/`, `server/` hay mã nguồn.
Liên quan: `cu-bong-chu-de-tieng-anh-2-5-tuoi.md` (chọn chủ đề và từ, không trùng nội dung file này). Hiện trạng bài: `maker/english-teacher/lessons/README.md`, `ROADMAP.md`.

## Tóm tắt 5 dòng

1. Lỗi chính của cô Lily nằm ở cách nói và cách đáp, chưa phải nội dung từ vựng: câu dài, hỏi dồn, lặp khuôn "Con nói theo cô", không đáp lại việc bé vừa làm.
2. Nghiên cứu về tương tác có đáp ứng (Roseberry 2014) và số lượt qua lại (Romeo 2018) đều chỉ về hướng: đáp lại trước, dạy sau, và đếm lượt bé thay vì đếm số từ cô nói.
3. Đề xuất cho bé 2 tuổi: cô nói tối đa 4 từ mỗi câu, mỗi lượt một yêu cầu, chờ đếm thầm 5 giây (Hanen). Từ mới đi trong câu chuyện và vè có động tác, không lặp kiểu drill.
4. Tín hiệu "Đến lượt con!", các ngưỡng số, và thứ tự nghi thức là quyết định thiết kế, chưa có nguồn đo hiệu quả. Phải thử trên bé thật rồi mới giữ.
5. Bằng chứng riêng cho AI voice tutor với bé 2 tuổi còn rất mỏng. Báo cáo này là khung để thử nghiệm có đo, không phải kết luận khoa học.

## Phát hiện

### 1. Đối chiếu từng triệu chứng với nguồn

| Quan sát (của Tuan) | Nguyên nhân gợi ý | Căn cứ |
|---|---|---|
| Nói câu dài, nhiều câu một lượt | Bé 2 tuổi chưa xử lý được. Hai con số đang mâu thuẫn: `prompt-teacher.md` ghi 8 từ/câu, `curriculum.py` (TODDLER_MODE) ghi 3–5 từ/câu | Hanen: câu ngắn, đúng ngữ pháp, khớp đúng lúc (nguồn 2). Con số cụ thể là quyết định thiết kế |
| "Con nói theo cô: X! X!" lặp nhiều lần | Giống luyện đọc theo mẫu, không giống trao đổi | Roseberry 2014 (theo README): học từ khi người lớn đáp lại, video phát sẵn thì không. Hanen: theo lead của bé, bắt chước bé (nguồn 2) |
| Hỏi dồn, ít thời gian chờ | Bé chưa kịp xử lý và trả lời | Hanen: đếm thầm đến 5 trước khi nói (nguồn 2). Harvard CDC: serve and return, chờ phản ứng rồi đáp (nguồn 1) |
| Bé im thì im luôn hoặc nhắc theo lịch | Thiếu tín hiệu "tới lượt" và không có bước dự phòng | Không có nguồn đo. Quyết định thiết kế (mục (a)) |
| Mở đầu và câu biệt danh lặp y hệt | Kịch bản cố định | README: bài là mục tiêu, Gemini tự chọn cách dạy. Cần thêm biến thể có kiểm soát (mục (a) quy tắc 6) |
| Giọng ngọng bị nhận dạng sai, cô đáp lệch | ASR cho trẻ nhỏ còn yếu | Kennedy et al. 2017 (HRI): ASR trẻ em chưa đủ để tương tác hoàn toàn bằng giọng (nguồn 6, chỉ đọc tóm tắt) |
| Chưa có câu chuyện liền mạch | Từ đứng rời, không có ngữ cảnh | Horst 2011 (lặp truyện có ngữ cảnh, README nguồn 5). Hanen: đọc lại, dùng từ trong sinh hoạt (nguồn 2) |

### 2. Theo cấp học

**Mầm non 2–3 tuổi (nhịp của bé nhà Tuan)**

- Nghe và làm theo trước, nói là tùy bé. Khớp ROADMAP mục 1 và Thông tư 50/2020 (mục tiêu nghe và làm theo, áp dụng cho 3–5 tuổi, không có quy định riêng cho 2 tuổi).
- **Giọng hướng về trẻ (infant-directed speech):** Graf Estes & Hurley (2013), 17 tháng tuổi, 3 thí nghiệm (28, 26, 28 bé): bé học nhãn vật khi nói bằng ngữ điệu hướng trẻ (cao hơn, rộng hơn, dài hơn), không học khi nói giọng người lớn. Học kém khi lặp đúng một mẫu giọng, học tốt khi giọng thay đổi (nguồn 3, đã mở). Ma et al. (2011), qua trích dẫn: 21 tháng học từ giọng hướng trẻ, 27 tháng học được cả giọng người lớn (nguồn 4, chưa mở bản gốc). Gợi ý: giọng ấm, chậm, ngữ điệu rõ ở bé 2–2,5 tuổi. Bằng chứng về đến mức nào thì chưa rõ.
- **Số lượt quan trọng hơn số từ:** Romeo et al. (2018), 36 trẻ 4–6 tuổi, nghiên cứu tương quan: số lượt hội thoại qua lại liên quan đến ngôn ngữ và hoạt động não, số từ người lớn nói thì không (nguồn 5, chỉ đọc tóm tắt). Chưa kiểm với bé 2 tuổi.
- **Serve and return:** bé "phát" tín hiệu (nhìn, cười, bập bẹ), người lớn đáp lại, chờ phản ứng, rồi đáp tiếp. Harvard CDC gọi đây là "trò chơi bóng bàn" của trẻ nhỏ (nguồn 1, đã mở trang podcast, không có số giây chờ).
- **Hanen OWL (quan sát, chờ, lắng nghe):** tìm xem bé đang chú ý vào gì, chờ bé gửi tín hiệu, đếm thầm đến 5 trước khi nói. Đáp nhanh, bắt chước âm/từ/hành động của bé. Lặp từ khoảng 3–5 lần trong một tương tác nhưng không dồn một lúc. Diễn giải nỗ lực của bé ("buh" → "Boom!") rồi nói câu đầy đủ hơn (nguồn 2, đã mở). Hanen là tài liệu hướng dẫn phụ huynh, không phải thử nghiệm đối chứng.
- **TPR (Asher):** không tìm được nghiên cứu mạnh cho bé 2–5 tuổi (tìm kiếm 2026-11-07 chỉ thấy bài nhỏ và blog). Vẫn có thể dùng vì hợp với việc "nghe và làm theo". Không coi là đã chứng minh.

**Mẫu giáo 4–5 tuổi**

- Bài hát có động tác: Ludke, Ferreira & Overy (2014) cho thấy "nghe rồi hát" giúp nhớ cụm tiếng nước ngoài tốt hơn nói (đối tượng là người lớn học tiếng Hungary, nguồn 13, chỉ đọc tóm tắt). Good et al. (2015), với trẻ Guatemala, chỉ thấy trích dẫn thứ cấp (nguồn 14, TODO).
- Kể chuyện có điều chỉnh độ khó: Kory-Westlund & Breazeal (robot Tega, 17 bé, 8 buổi trong 2 tháng) cho thấy robot điều chỉnh lời kể theo trình độ bé giúp học tốt hơn, nhưng đây là tiếng mẹ đẻ, không phải tiếng Anh (nguồn 12, chỉ tóm tắt).

**Voice AI cho trẻ nhỏ (tổng quát, bằng chứng yếu)**

- Druga et al. (2017), IDC: trẻ tương tác với trợ lý giọng nói. Chỉ có trang danh mục, chưa đọc nội dung (nguồn 8).
- Phân tích tương tác trẻ–voice app (CHI 2021, DOI 10.1145/3411764.3445271): theo mục lục, có các mục về tương tác hai chiều và "giả tương tác". Không đọc được nội dung, TODO tên tác giả và kết luận (nguồn 9).
- StoryPal (IDC 2025, nhóm 23 trẻ 4–7 tuổi, kể chuyện có hỏi đáp và phản hồi) và ELLA (arXiv 2026, 10 trẻ, 8 ngày, đồng thiết kế với phụ huynh): chỉ đọc được tóm tắt từ tìm kiếm, PDF không mở được (nguồn 10, 11, TODO).
- Không tìm được bộ hướng dẫn thiết kế chính thức cho LLM tutor cho trẻ ≤5 tuổi, và không tìm được prompt mã nguồn mở cho cô giáo tiếng Anh trẻ em trong cộng đồng xiaozhi (tìm kiếm 2026-11-07).

## Đề xuất

Quy ước nhãn: **[NGUỒN n]** = có căn cứ nguồn (số theo mục Nguồn), **[THIẾT KẾ]** = quyết định của STLab, chưa có nguồn đo.

### (a) Bộ quy tắc persona mới cho cô Lily (8 quy tắc, ưu tiên)

1. **Câu ngắn:** mỗi câu tiếng Anh tối đa 4 từ cho bé 2–3 tuổi (6 từ cho 4–5 tuổi). Mỗi lượt tối đa 2 câu. Câu tiếng Việt, nếu có, là 1 câu ngắn. [NGUỒN 2 cho ý câu ngắn; con số 4 là THIẾT KẾ]. Cần thống nhất với prompt-teacher.md (8 từ).
2. **Đáp trước, dạy sau:** câu đầu mỗi lượt phản hồi việc bé vừa làm (âm, từ, động tác, hoặc nhìn). Sau đó mới dạy. [NGUỒN 1, 2, 5]
3. **Một yêu cầu mỗi lượt:** làm một hành động, hoặc chọn một trong hai. Không hỏi mở với bé 2 tuổi. [NGUỒN 2 cho ý một yêu cầu; cách làm là THIẾT KẾ]
4. **Chờ:** sau mỗi câu hỏi hoặc gợi ý, cô im và đếm thầm 5 giây. Không hỏi lại ngay. Nếu bé im, cô làm mẫu một động tác (vẫy tay), đếm thầm 5 giây nữa rồi chuyển sang hành động không cần nói. [NGUỒN 2 cho 5 giây; phần sau là THIẾT KẾ]
5. **Báo đến lượt:** mỗi lần chờ bé nói, cô mở đầu bằng câu cố định "Đến lượt con!" kèm âm chuông ngắn. Đây là tín hiệu cho bé biết lúc nào nói. [THIẾT KẾ; chưa có nguồn đo hiệu quả]
6. **Không drill:** một từ mới tối đa 2 lần cô nói liên tiếp trong lượt. Bé bắt chước 1 lần. Từ còn lại xuất hiện trong câu chuyện, vè, động tác, và tái xuất hiện trong buổi sau. [NGUỒN 2 cho lặp 3–5 lần rải ra; con số 2 lần/lượt là THIẾT KẾ, khác README (2 lần) và ROADMAP (2 lần) ở chỗ tính gộp]
7. **Nói sai hoặc không nghe rõ:** không sửa, không chấm đúng sai. Đáp lại ý, rồi nói lại từ đúng trong câu ngắn ("Ồ, hello! Hello, Bear!"). Nếu không chắc bé nói gì, nói "Cô chưa nghe rõ, con vẫy cho cô nhé!" và chuyển sang hành động. [NGUỒN 2 cho "diễn giải nỗ lực"; NGUỒN 6 cho lý do dự phòng ASR]
8. **Khen việc nhìn thấy, không khen câu nói:** "Con vẫy tay rồi!", "Con cười!". Không khen theo câu nói vì ASR có thể nhận sai. [NGUỒN 6 cho ASR; ý khen việc làm là THIẾT KẾ, README đã có]

Cũng giữ nguyên: không hỏi tên, tuổi, trường, ba mẹ, gia đình, đồ ăn. Không tự kết thúc buổi (máy chủ quyết định). Người lớn ngồi cạnh bé để làm động tác cùng (nhắc phụ huynh ở đầu buổi). [NGUỒN 1, 5 cho vai trò người lớn có mặt; câu nhắc là THIẾT KẾ]

### (b) Khung buổi học mới

**Bé 2–3 tuổi, 3–4 phút** (một từ mới mỗi tuần, ôn tối đa 3 từ, theo ROADMAP)

| Thời gian | Bước | Cô nói (tiếng Anh, Việt khi cần) | Bé làm | Chờ |
|---|---|---|---|---|
| 0:00–0:30 | Nghi thức mở | "Hello! Hello!" + vẫy tay. "Chào con!" | Vẫy, hoặc nhìn cô | 5 giây |
| 0:30–1:30 | Từ mới (1 từ) | Cô vẫy, "Hello!" hai lần. "Con vẫy nào!" | Vẫy, bắt chước âm | 5 giây, rồi đáp lại trong 1 câu |
| 1:30–2:30 | Câu chuyện 2–3 câu | "Bear says hello. Bear is happy." | Làm động tác của Bear | Đếm thầm 5 giây |
| 2:30–3:30 | Vè có động tác, một dòng mỗi lần | "Wave, wave!" | Vẫy | 5 giây, không hỏi lại |
| 3:30–4:00 | Kết | "Bye bye! Hẹn gặp con!" + vẫy | Vẫy | Không cần chờ |

Nghi thức mở và kết giữ cố định một câu, thay phần còn lại theo biến thể để tránh lặp máy móc. [THIẾT KẾ]

**Bé 4–5 tuổi, khoảng 5 phút** (thêm đố chọn hai lựa chọn và một câu hai từ): mở, 2 từ mới trong câu chuyện, đố "Hello or goodbye?" hoặc "Happy or sad?", bắt chước một cụm hai từ, kết. [THIẾT KẾ, theo ROADMAP và README]

### (c) Ba ví dụ hội thoại (bài 04, hello/goodbye, bé 2 tuổi)

Bé không có màn hình, nên hành động và âm thanh là kênh chính. Ghi chú: "Chờ 5" là đếm thầm 5 giây.

**Ví dụ 1: bé nói gần đúng**
- Cô: "Hello! Hello!" (vẫy)
- Bé: "hê-lô" (gần đúng)
- Cô: "Ồ, hello! Con chào cô rồi!" (đáp trước, không sửa)
- Cô: "Goodbye! Con vẫy nào." (vẫy mẫu)
- Chờ 5. Bé vẫy hoặc im. Dù bé làm gì, cô khen việc làm: "Con vẫy rồi!"

**Ví dụ 2: bé im**
- Cô: "Hello! Hello!" (vẫy)
- Chờ 5. Bé im.
- Cô: vẫy mẫu, không nói. Chờ 5.
- Vẫn im: cô không hỏi lại. Cô nói "Mình vẫy nào! Bye bye!" và chuyển sang vè có động tác để bé làm theo mà không cần nói.
- Ghi nhận: hai lần im liên tiếp là dấu hiệu chuyển hướng, không phải lỗi của bé.

**Ví dụ 3: bé nói tiếng Việt hoặc máy không nghe rõ**
- Bé: "chào cô" (tiếng Việt)
- Cô: "Chào con! Xin chào là hello." (một câu Việt, một từ Anh, theo quy tắc cũ được giữ)
- Cô: "Hello! Con vẫy nào." (vẫy)
- Nếu tiếng bé không rõ: "Cô chưa nghe rõ, con vẫy cho cô nhé!" rồi chuyển sang vẫy tay, không chấm đúng sai.
- Không dạy goodbye trong cùng lượt này để bé không bị quá tải.

### (d) Chỉ số đánh giá buổi học tốt

Ngưỡng là THIẾT KẾ, chưa có nguồn. Dùng để so sánh các phiên bản prompt nội bộ, không dùng để kết luận khoa học. Đo bằng log đếm lượt, không lưu giọng ghi âm, không ghi tên bé.

| Chỉ số | Cách đo | Ngưỡng đề xuất (THIẾT KẾ) |
|---|---|---|
| Tỉ lệ lượt bé (có tiếng hoặc hành động) / tổng lượt | Đếm từ log | ≥ 40% với bé 2 tuổi |
| Số từ trung bình mỗi câu của cô | Đếm từ kịch bản | ≤ 4 từ (2–3 tuổi), ≤ 6 từ (4–5 tuổi) |
| Số lượt cô liên tiếp không có phản hồi từ bé | Đếm | ≤ 2 (đã có trong bài 04) |
| Thời gian chờ thực tế sau câu hỏi hoặc gợi ý | Đo bằng log | ≥ 4–5 giây |
| Số lần cô nói một từ mới trong buổi | Đếm | ≤ 2 lần liên tiếp, 3–5 lần cả buổi |
| Tỉ lệ lượt bé "không nghe rõ" / tổng lượt bé | Log ASR | Theo dõi. Nếu cao, tăng tỉ lệ hành động |
| Dấu hiệu bé: làm theo, nhìn cô, quay đi | Người lớn ngồi cạnh ghi 3 dấu | Tăng dần qua 4 tuần |
| Số buổi/tuần | Quy ước tuần có học trong ROADMAP | ≥ 2 buổi/tuần |

### (e) Đánh đổi

- **Câu ngắn (4 từ):** ít nội dung, bé lớn có thể thấy nhàm. Nên có hai phiên bản: 2–3 tuổi và 4–5 tuổi.
- **Chờ 5 giây:** buổi dài hơn một chút. Im lặng trên loa dễ gây khó chịu, nên luôn có "Đến lượt con!" để báo.
- **Đáp trước, dạy sau:** làm kịch bản kém cố định hơn, LLM dễ lệch khỏi kế hoạch bài. Cần kiểm tra log.
- **Giảm phụ thuộc giọng nói:** giảm rủi ro ASR, nhưng ít thông tin hơn để đo tiến bộ bằng lời. Không có camera (vì lý do riêng tư và an toàn), nên hành động chỉ đo được bằng quan sát người lớn.
- **Người lớn ngồi cạnh:** tăng hiệu quả rõ hơn cả, nhưng giảm ý nghĩa "thiết bị tự dạy". Đây là lựa chọn sản phẩm cho Tuan.
- **Bằng chứng yếu:** các nghiên cứu trên có cỡ mẫu nhỏ (36, 28, 10 trẻ). Không có thử nghiệm đối chứng nào cho AI voice tutor với bé 2 tuổi.

## Việc tiếp theo (không làm trong báo cáo này)

1. Tuan duyệt 8 quy tắc (a) và khung buổi (b).
2. Thống nhất con số câu ngắn (8 từ trong `prompt-teacher.md` và 3–5 từ trong `TODDLER_MODE`). Việc này thuộc lập trình viên.
3. Thử 3 buổi thật với bé 2 tuổi, ghi quan sát bằng đếm (không ghi tên), so với bảng (d).
4. Mở bản gốc để kiểm: Ma et al. 2011; Kennedy et al. 2017; Romeo et al. 2018 (PDF); Harvard "5 Steps"; StoryPal; ELLA (bản HTML); CHI 2021 (DOI ở nguồn 9).
5. Tìm thêm (TODO): nghiên cứu về thời gian chờ với trẻ dưới 3 tuổi; recast trong học từ mới ở trẻ nhỏ; xác nhận Janssens et al. 2024 về ASR trẻ em.

## Nguồn

Ngày truy cập là 2026-11-07 trừ khi ghi khác. Mục "đã mở" nghĩa là đọc được nội dung trang. Mục "tóm tắt" nghĩa là chỉ đọc được đoạn tìm kiếm hoặc trích dẫn thứ cấp.

1. Harvard Center on the Developing Child, "The Brain Architects Podcast: Serve and Return" (đã mở; trang ghi ngày 2020-03-09): https://developingchild.harvard.edu/resources/the-brain-architects-podcast-serve-and-return-supporting-the-foundation/ . Trang không liệt kê 5 bước; bản "5 Steps" chưa mở.
2. Hanen Centre, "How to Help Your Child Learn New Words" (đã mở): https://hanen.org/information-tips/how-to-help-your-child-learn-new-words . Có OWL, đếm thầm 5, lặp 3–5 lần, diễn giải nỗ lực. Trang không nói về recast, bài hát, hay thói quen.
3. Graf Estes, K. & Hurley, K. (2013), "Infant-directed prosody helps infants map sounds to meanings", Infancy 18(5), DOI 10.1111/infa.12006 (đã mở qua PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC3828035 . Trang không có số trang.
4. Ma, W., Golinkoff, R. M., Houston, D. & Hirsh-Pasek, K. (2011), Language Learning and Development (tóm tắt, qua trích dẫn và kết quả tìm kiếm; chưa mở bản gốc): https://hellolab-speech-language-hearing.media.uconn.edu/wp-content/uploads/sites/3733/2024/12/Word-Learning-in-Infant-and-Adult-Directed-Speech.pdf . TODO: kiểm tập, trang, DOI.
5. Romeo, R. R. et al. (2018), "Beyond the 30-Million-Word Gap", Psychological Science 29(5):700–710 (tóm tắt): https://news.mit.edu/2018/conversation-boost-childrens-brain-response-language-0214 và https://www.gse.harvard.edu/ideas/usable-knowledge/18/02/brain-changing-power-conversation . Tương quan, 36 trẻ 4–6 tuổi.
6. Kennedy, J. et al. (2017), "Child Speech Recognition in Human-Robot Interaction: Evaluations and Recommendations", HRI 2017, DOI 10.1145/2909824.3020229 (tóm tắt; PDF không đọc được): https://james-kennedy.github.io/publications/KennedyEtAl2017HRIFull.pdf . TODO: lấy con số lỗi từ bản đầy đủ.
7. Janssens et al. (2024), theo tóm tắt của kết quả tìm kiếm: TODO xác nhận DOI và con số.
8. Druga, S. et al. (2017), "Hey Google is it OK if I eat you?", IDC 2017 (chỉ trang danh mục): https://www-prod.media.mit.edu/publications/hey-google-is-it-ok-if-i-eat-you-initial-explorations-in-child-agent-interaction/
9. Phân tích tương tác trẻ–voice app, CHI 2021, DOI 10.1145/3411764.3445271 (không đọc được nội dung). TODO: tên tác giả và kết luận.
10. StoryPal, IDC 2025 (tóm tắt): https://par.nsf.gov/servlets/purl/10615882 . TODO: đọc bản gốc.
11. Antony, V. N. et al. (2026), "ELLA: Generative AI-Powered Social Robots for Early Language Development at Home", arXiv:2603.12508 (tóm tắt; PDF không đọc được): https://arxiv.org/pdf/2603.12508v1 . TODO: đọc bản HTML.
12. Kory-Westlund, J. & Breazeal, C. (Tega, kể chuyện với trẻ mẫu giáo; tóm tắt): https://www.media.mit.edu/publications/the-interplay-of-robot-language-level-with-childrens-language-learning-during-storytelling/
13. Ludke, K. M., Ferreira, F. & Overy, K. (2014), "Singing can facilitate foreign language learning", Memory & Cognition 42:41–52 (tóm tắt; đối tượng là người lớn): https://ferreiralab.faculty.ucdavis.edu/wp-content/uploads/sites/222/2015/05/Ludke-et-al.-2014_SingingForeignLanguage_Mem-Cog.pdf
14. Good et al. (2015), trẻ Guatemala, chỉ có trích dẫn thứ cấp. TODO: tìm bản gốc.
15. Tìm kiếm 2026-11-07 về TPR với trẻ 2–5 tuổi: không tìm được RCT. Không dẫn nguồn riêng. Xem thêm README mục 7.
16. Nguồn cũ trong `maker/english-teacher/lessons/README.md` (Horst 2011, Roseberry 2014, Kuhl 2003, Thông tư 50/2020, WHO, AAP): giữ nguyên, không lặp lại ở đây.
17. Không tìm được prompt mã nguồn mở cho cô giáo tiếng Anh trẻ em trong cộng đồng xiaozhi. British Council "My AI teacher lesson plan" (https://www.teachingenglish.org.uk/sites/teacheng/files/2025-05/My%20AI%20teacher%20lesson%20plan.pdf): PDF không đọc được, không dùng.
