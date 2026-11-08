# Cú Bông – "học từng từ một" nghĩa là gì, và đổi bài thế nào

Ngày tra cứu: 2026-11-08. Trạng thái: nghiên cứu, chờ Tuan duyệt. Không sửa `maker/english-teacher/lessons/`, `server/`, `cu-bong-cach-day-tot-hon.md` hay mã nguồn.
Liên quan: `cu-bong-cach-day-tot-hon.md` (cách nói, cách đáp, chờ), `cu-bong-chu-de-tieng-anh-2-5-tuoi.md` (chọn từ), `maker/english-teacher/lessons/ROADMAP.md` (lịch tuần hiện tại).

Quy ước nhãn: **[NGUỒN n]** = có căn cứ (số theo mục Nguồn). **[THIẾT KẾ]** = quyết định của STLab, chưa có nguồn đo. **TODO** = chưa kiểm được.

## Tóm tắt

- "Từng từ một" có nguồn ủng hộ ở mức **từ mới được củng cố nhiều lần, rải theo thời gian**, không phải "mỗi buổi chỉ 1 từ". Nghiên cứu spacing ở trẻ 2 tuổi cho thấy học rải tốt hơn học dồn khi kiểm tra sau một khoảng nghỉ [NGUỒN 4, tóm tắt]. Không có nguồn nào cho số từ mới tối ưu trong 3–5 phút cho bé 2 tuổi.
- Hanen khuyên lặp từ mới 3–5 lần trong một tương tác, **nhưng không dồn cùng lúc** [NGUỒN 1]. Ý "không dồn" có nguồn. Con số "tối đa 2 lần liên tiếp" là THIẾT KẾ.
- Bé 2 tuổi nhớ từ kém nếu chỉ nghe một lần: trong một nghiên cứu, sau 5 phút, từ được gắn nhanh không cao hơn mức ngẫu nhiên [NGUỒN 6, tóm tắt thứ cấp]. Một lần nghe trong buổi là chưa đủ, buổi sau phải ôn lại.
- Chờ: Hanen khuyên chờ **tối đa 10 giây**, trẻ cần từ 1–2 giây đến 5–10 giây tùy bé [NGUỒN 2]. Báo cáo cũ `cu-bong-cach-day-tot-hon.md` ghi "đếm thầm 5 giây" và gán cho Hanen: chỉ đúng một phần, vì trang "learn new words" có "đếm đến năm" [NGUỒN 1] nhưng trang chờ ghi 10 giây [NGUỒN 2]. Đề xuất: 5 giây rồi làm mẫu, tổng không quá 10 giây.
- Đổi bài: Hanen khuyên theo lead của bé, phản hồi bằng câu ngắn đúng ngữ pháp [NGUỒN 1]. Không có nguồn cho số lần đổi tối đa. Đề xuất [THIẾT KẾ]: giữ con trỏ bài (không quay về đầu danh sách), cho đổi trò 1 lần mỗi buổi, lần thứ hai thì kết buổi.
- Lỗi "đổi bài là quay về one" nhiều khả năng là lỗi trạng thái (con trỏ bị reset), không phải lỗi sư phạm. Cần sửa ở `curriculum.py` (xem "Việc cho lập trình viên" trong mục Đề xuất).
- Thông tư 50/2020 là chương trình **làm quen tiếng Anh cho mẫu giáo** (35 tuần/năm, ≥2 hoạt động/tuần, 25–35 phút mỗi hoạt động, theo tóm tắt thứ cấp) [NGUỒN 8]. Không có quy định từ vựng cho bé 2 tuổi. Phiên 3–4 phút của Cú Bông là phần bổ trợ, không thay được hoạt động lớp.
- Đề xuất chính: 2–3 tuổi chuyển sang **2 từ mới mỗi tuần** (cùng chủ đề, dạy lần lượt), mỗi buổi 1 từ mới + tối đa 2 từ ôn. Đánh đổi: số từ/năm tăng gấp đôi, vượt xa ~35 từ của mục tiêu mẫu giáo 3–4 tuổi. Tuan chọn (xem "Đề xuất lịch ROADMAP").

## Phát hiện

### 1. "Từng từ một" nghĩa là gì

- **Tách rõ hai việc:** (a) từ mới cần được gặp nhiều lần, rải; (b) số từ mới trong một buổi. Nguồn ủng hộ (a), không có nguồn cụ thể cho (b).
- **Lặp có kiểm soát:** Hanen: lặp từ 3–5 lần trong tương tác, không dồn một lúc [NGUỒN 1]. Tương đương: mỗi từ mới được cô nói khoảng 3–5 lần trong 3–4 phút, rải theo các hoạt động [THIẾT KẾ cho cách rải].
- **Khoảng cách:** Vlach, Ankowski & Sandhofer (2012) so sánh học đồng thời, học dồn và học rải ở 144 trẻ 2 tuổi. Theo tóm tắt thứ cấp, nhóm học rải làm tốt hơn các nhóm khác (kết quả kiểm tra sau khoảng 15 phút, TODO xác nhận trong bản gốc) [NGUỒN 4]. Bản PDF không đọc được trong lần tra cứu này.
- **Học rải với trẻ 3 tuổi:** Vlach, Sandhofer & Kornell (2008) cho thấy học rải tốt hơn học dồn cả ở trí nhớ và ở khái niệm [NGUỒN 5, tóm tắt]. Kết quả này đẩy việc ôn sang buổi sau, không ủng hộ "dạy hết trong một buổi".
- **Bao nhiêu lần thì nhớ:** Không có con số đã kiểm cho bé 2 tuổi. Số 36 lần gặp (Storkel) là của trẻ mẫu giáo lớn có rối loạn ngôn ngữ, không áp dụng trực tiếp [NGUỒN 7, TODO tác giả và DOI]. Con số "9 từ mỗi ngày" hay gặp trên mạng không truy được về Carey (1978), không nên trích.
- **Ba bước dạy (Montessori):** đặt tên, nhận ra (chỉ đúng vật khi được hỏi), gọi tên (bé tự nói). Đây là cách sắp thứ tự trong mini-cycle cho một từ [NGUỒN 9, định nghĩa]. Không có RCT riêng cho kỹ thuật này và không có số từ mỗi buổi [NGUỒN 9].

**Ví dụ với bé 2 tuổi, 3–4 phút, 2 từ mới trong tuần [THIẾT KẾ]:**
- Buổi 1: "one" (đặt tên, nhận ra, bé làm theo bằng tay). Ôn 1 từ tuần trước.
- Buổi 2: "two" (đặt tên, nhận ra). Ôn "one". "One" xuất hiện lại ở đầu buổi và trong vè.
- Mỗi từ mới được gặp ở ít nhất 2 buổi trong tuần, rồi ôn ở các tuần sau. Đây là nhịp rải.

### 2. Gom theo chủ đề hay xen chủ đề

- Không tìm được nguồn đo trực tiếp "gom chủ đề" so với "xen chủ đề" ở trẻ 2–5 tuổi (TODO).
- Nguồn spacing [NGUỒN 4, 5] nói về khoảng thời gian giữa các lần gặp, không nói về việc từ có cùng chủ đề hay không.
- Super Simple dùng bài hát với vài từ đích mỗi bài, lặp qua bài hát và động tác [NGUỒN 10, tóm tắt]. Không có số từ mỗi bài đã kiểm (TODO).
- **Đề xuất [THIẾT KẾ]:** trong một tuần, các từ mới cùng chủ đề (số, màu, con vật) để bé có ngữ cảnh chung. Trong một buổi, không đưa hai từ mới gần nghĩa (ví dụ "cat" và "dog" trong cùng buổi). Từ ôn lấy từ các chủ đề trước, để bé gặp lại từ ở ngữ cảnh khác.

### 3. Khi bé đổi bài ("đổi bài đi cô", "chơi cái khác")

- Hanen khuyên theo lead của bé và phản hồi bằng câu ngắn, đúng ngữ pháp [NGUỒN 1]. Không có nguồn cho việc xử lý "đổi bài" khi đang dạy từ mới.
- Đưa hai lựa chọn là cách có cấu trúc, bé dễ trả lời hơn câu hỏi mở [NGUỒN 11, tóm tắt, chưa đọc đầy đủ]. Dùng lúc đổi bài: "Con muốn vẫy hay chỉ?".
- Chờ sau khi đưa lựa chọn để bé có thời gian đáp [NGUỒN 2].
- **Đề xuất [THIẾT KẾ]:**
  - Giữ con trỏ bài theo từ (không quay về đầu). Đổi trò thì giữ từ đang học trong trò mới, ví dụ "one" làm bằng tay thay vì bằng vẽ.
  - Cho đổi trò tối đa 1 lần mỗi buổi. Lần thứ hai thì kết buổi bằng nghi thức ("Bye bye! Hẹn gặp con!") và không ép.
  - Đổi bài không làm mất tính "buổi có tiếng bé" (quy tắc tuần ROADMAP vẫn đúng).
  - Số 1 lần đổi là giả định cần thử 3 buổi trên bé thật.

### 4. Dấu hiệu bé "đã có" một từ

Dùng ba tiêu chí, không đòi bé nói.

- **Nhận ra không cần mẫu:** làm đúng hành động khi nghe từ, ở buổi sau, mà cô không làm mẫu trước. Đây là kiểm tra trí nhớ sau khoảng nghỉ, như Horst & Samuelson (2008) [NGUỒN 6, tóm tắt].
- **Nói gần đúng tự phát:** bé nói âm hoặc từ, không được nhắc. Hanen coi việc bắt chước âm hoặc từ là dấu hiệu học [NGUỒN 1]. Không phải điều kiện để chuyển từ.
- **Dùng từ trong tình huống khác:** chỉ đúng vật khi cô hỏi "đâu là X?", hoặc đưa vật khi nghe tên [NGUỒN 9, bước nhận ra]. Mốc này đã có trong ROADMAP (mục 5, "nhận ra từ đã học").
- **Ngưỡng:** TODO. ROADMAP đang dùng "3/5 lần" cho bé 4–5 tuổi, đây là THIẾT KẾ.

### 5. Theo cấp học

**Mầm non 2–3 tuổi**
- Thông tư 50/2020 không có quy định từ vựng tiếng Anh cho bé 2 tuổi (phạm vi mẫu giáo, tóm tắt thứ cấp) [NGUỒN 8].
- Bằng chứng spacing có ở trẻ 2 tuổi (Vlach 2012) và trẻ 3 tuổi (Vlach 2008) [NGUỒN 4, 5]. Bằng chứng về số từ mỗi buổi thì chưa có.
- Thời lượng chú ý: không tìm được nguồn chính thống cho "2 tuổi tập trung bao lâu". Các con số "2–3 phút mỗi tuổi" là quy tắc ngón tay trên blog, không dùng làm căn cứ (TODO).

**Mẫu giáo 4–5 tuổi**
- Thông tư 50/2020: hoạt động 25–35 phút ở lớp, ≥2 hoạt động/tuần [NGUỒN 8]. Cú Bông ~5 phút là phần bổ trợ.
- Bằng chứng về số từ khó mỗi cuốn sách có ở trẻ có rối loạn ngôn ngữ: 4 từ khó mỗi cuốn cho kết quả tốt hơn [NGUỒN 7b, tóm tắt]. Không áp dụng trực tiếp cho trẻ khỏe mạnh (TODO).

### 6. Kiểm lại các con số đang dùng

| Con số trong báo cáo cũ | Kết quả kiểm lại | Hành động |
|---|---|---|
| Chờ "đếm thầm 5 giây" gán cho Hanen | Trang "learn new words" có "đếm đến năm"; trang "worth the wait" ghi tối đa 10 giây, đếm thầm đến 10 | Sửa thành: 5 giây, làm mẫu, tổng không quá 10 giây. Tuan quyết có sửa báo cáo cũ không |
| "Thông tư 50/2020 mục tiêu nghe và làm theo 3–5 tuổi" | Chưa xác nhận trong văn bản gốc (chỉ tóm tắt thứ cấp) | TODO kiểm trên thuvienphapluat hoặc công báo |
| Thông tư 50/2020 "35 tuần" (ROADMAP) | Khớp với tóm tắt thứ cấp | Giữ, ghi nguồn tóm tắt |
| Luật sửa đổi | Trang luatvietnam ghi văn bản được sửa bởi 09/2025/TT-BGDĐT (chưa kiểm nội dung) | TODO kiểm |
| "9 từ mỗi ngày" | Không truy được về Carey (1978) | Không trích |

## Đề xuất

Các số ở đây là đề xuất để thử, không phải kết luận khoa học.

### Bảng quy tắc đề xuất

| # | Quy tắc | Bé 2–3 tuổi (3–4 phút) | Bé 4–5 tuổi (~5 phút) | Nhãn |
|---|---|---|---|---|
| 1 | Từ mới mỗi buổi | 1 | 1 (tối đa 2 nếu tách rõ hai mini-cycle) | THIẾT KẾ, theo NGUỒN 1 |
| 2 | Từ mới mỗi tuần (cùng chủ đề) | 2 (khuyến nghị, xem đánh đổi) | 2 (giữ như hiện tại) | THIẾT KẾ |
| 3 | Số lần cô nói từ mới trong buổi | 3–5, không dồn | 3–5, không dồn | NGUỒN 1 (3–5, không dồn); "không quá 2 lần liên tiếp" là THIẾT KẾ |
| 4 | Từ ôn trong buổi | Tối đa 2 (tuần N-1 và N-3) | 2–3 | THIẾT KẾ, theo spacing NGUỒN 4, 5 |
| 5 | Thứ tự trong buổi | Nghi thức (chờ 10 giây tối đa) → từ mới (đặt tên, nhận ra, bé làm) → ôn 1 từ → vè có động tác → kết | Nghi thức → từ mới 1 → ôn 2 → đố chọn 2 lựa chọn → kết | Cấu trúc theo NGUỒN 9; thời lượng là THIẾT KẾ |
| 6 | Chờ | "Đến lượt con!" → chờ 5 giây → nếu im, làm mẫu động tác → chờ thêm 5 giây (tổng ≤10 giây), rồi chuyển hoạt động không cần nói | Giống | NGUỒN 2 (1–10 giây), làm mẫu là THIẾT KẾ |
| 7 | Đổi bài | Giữ con trỏ theo từ; đổi trò thì giữ từ đang học; tối đa 1 lần đổi/buổi; lần 2 kết buổi | Giống | THIẾT KẾ, NGUỒN 1 (theo lead) |
| 8 | Đưa lựa chọn khi đổi | Hai phương án, nói tên, chờ | Hai phương án | NGUỒN 11 (tóm tắt, chưa đọc đủ) |
| 9 | Coi là đã có một từ | Làm đúng hành động ở buổi sau không cần mẫu, hoặc chỉ đúng khi được hỏi | Thêm nói cụm 2 từ | THIẾT KẾ, NGUỒN 6 (kiểm trí nhớ sau khoảng nghỉ) |
| 10 | Tín hiệu kết buổi | Bye bye + vẫy, không hỏi lại | Giống | THIẾT KẾ |

### Đề xuất lịch ROADMAP (chờ Tuan duyệt)

**Hiện tại:** 2–3 tuổi, 1 từ mới/tuần, 35 hàng, khoảng 35 từ/năm (bảng máy đọc). 4–5 tuổi, 2 từ mới/tuần.

**Đề xuất A (khuyến nghị):**
- 2–3 tuổi: mỗi hàng 2 từ cùng chủ đề. Buổi đầu của tuần dạy từ thứ nhất, buổi sau dạy từ thứ hai. Tuần chỉ có 1 buổi thì từ thứ hai chuyển sang tuần sau, hàng không chuyển (giữ quy tắc "tuần có học ≥2 buổi").
- Hàng ví dụ: hàng 1 "one, two"; hàng 2 "three, four"; hàng 3 "five, hello". Bảng đầy đủ là việc của edu-researcher sau khi Tuan duyệt, không làm trong báo cáo này.
- 4–5 tuổi: giữ 2 từ/tuần, không đổi.
- Đánh đổi: khoảng 70 từ/năm cho bé 2–3 tuổi, nhiều hơn khoảng 35 từ của Thông tư cho 3–4 tuổi. Thông tư áp dụng cho lớp, không cho thiết bị, nên đây là lựa chọn sản phẩm. Tuan cần quyết có muốn tăng gấp đôi số từ hay không.

**Đề xuất B (giữ tổng số từ):**
- 2–3 tuổi giữ 1 từ/tuần, nhưng sửa trong buổi: mỗi buổi có 1 mini-cycle từ mới (3 lần) + ôn tối đa 2 từ, và sửa con trỏ để đổi bài không quay về đầu.
- Đánh đổi: không tăng số từ, nhưng mỗi tuần chỉ có một từ mới để bé làm quen. Nếu bé học 2 buổi/tuần, từ đó được gặp 2 lần trong tuần, rồi ôn tiếp các tuần sau.

**Không khuyến nghị:** 3–4 từ cùng chủ đề mỗi tuần cho bé 2 tuổi. Không có nguồn về tải nhận thức cho bé 2 tuổi, và rủi ro là bé không nhớ từ nào. Có thể thử cho 4–5 tuổi sau 4 tuần đầu (TODO).

### Việc cho lập trình viên (không làm trong báo cáo này)
1. `curriculum.py` đang chọn bài theo tên file và chuyển khi bé đã nhắc đủ từ. Lưu con trỏ theo biệt danh, không reset khi đổi bài.
2. Thêm bộ đếm "đổi bài trong buổi" (tối đa 1), reset theo mỗi phiên.
3. Chờ: 5 giây, làm mẫu, rồi 5 giây nữa (tổng ≤10 giây). Hiện có thể là 5 giây cố định.

### Đánh đổi chung
- Tăng số từ mới: bé học được nhiều hơn, nhưng mỗi từ được gặp ít lần hơn trong một tuần. Cần đo bằng quan sát người lớn.
- Chờ dài hơn: buổi dài hơn một chút, im lặng trên loa khó chịu. Phải có "Đến lượt con!" để báo.
- Đổi bài có giới hạn: giữ được tiến độ nhưng bé có thể thấy bị cắt ngang. Cần câu kết nhẹ nhàng.
- Bằng chứng yếu: cỡ mẫu nhỏ (144 trẻ ở nghiên cứu spacing 2 tuổi, 36 trẻ ở nghiên cứu cũ). Không có thử nghiệm đối chứng cho AI voice tutor với bé 2 tuổi.

## Việc tiếp theo (không làm trong báo cáo này)
1. Tuan chọn Đề xuất A hoặc B, và quyết có tăng số từ hay không.
2. Duyệt bảng quy tắc, và sửa điểm về chờ 10 giây trong `cu-bong-cach-day-tot-hon.md` nếu Tuan đồng ý.
3. Thử 3 buổi thật với bé 2 tuổi. Đếm: số lần bé đổi bài, số lần bé làm đúng không cần mẫu ở buổi sau, số giây chờ thực tế. Không ghi tên bé.
4. TODO kiểm: bản gốc Vlach, Ankowski & Sandhofer (2012, DOI 10.1037/a0025260); Horst & Samuelson (2008) và DOI; Storkel (36 lần); bản gốc Thông tư 50/2020 và điều khoản; nghiên cứu số từ mỗi buổi cho trẻ 2–3 tuổi; Cambridge Pre A1 Starters và Super Simple (số từ mỗi bài).

## Nguồn

Ngày truy cập là 2026-11-08 trừ khi ghi khác. "Đã đọc" = đọc được nội dung trang. "Tóm tắt" = chỉ đọc được kết quả tìm kiếm hoặc trích dẫn thứ cấp.

1. Hanen Centre, "How to Help Your Child Learn New Words" (đã đọc): https://hanen.org/information-tips/how-to-help-your-child-learn-new-words . Có: lặp 3–5 lần, không dồn cùng lúc; "count to five" (đếm đến năm, thầm); theo lead của bé; câu ngắn đúng ngữ pháp.
2. Hanen Centre, "It's Worth the Wait! The Power of Waiting During Interactions" (đã đọc): https://www.hanen.org/worththewait.aspx . Có: chờ tối đa 10 giây, đếm thầm đến 10; trẻ cần 1–2 giây hoặc 5–10 giây tùy bé; nếu sau 10 giây không có lượt, người lớn tự làm một lượt rồi chờ lại.
3. Hanen Centre, "The Power of Turn-taking" (tóm tắt): https://www.hanen.org/helpful-info/articles/power-turn-taking.aspx . Dùng để đối chiếu, không trích số liệu.
4. Vlach, Ankowski & Sandhofer (2012), "At the Same Time or Apart in Time? The Role of Presentation Timing and Retrieval Dynamics in Generalization", Journal of Experimental Psychology: Learning, Memory, and Cognition, DOI 10.1037/a0025260 (tóm tắt; PDF không đọc được): https://babytalk.psych.ucla.edu/wp-content/uploads/sites/271/2021/03/Vlach_Ankowski_Sandhofer-2012.pdf . TODO: số lần trình bày, khoảng cách, kết quả 15 phút. Cỡ mẫu 144 trẻ 2 tuổi (tóm tắt).
5. Vlach, Sandhofer & Kornell (2008), Cognition 109:163–167 (tóm tắt): https://babytalk.psych.ucla.edu/wp-content/uploads/sites/271/2021/03/Vlach_Sandhofer_Kornell_2008.pdf . Trẻ 3 tuổi, học rải tốt hơn học dồn ở trí nhớ và khái niệm.
6. Horst & Samuelson (2008), "Fast mapping but poor retention by 24-month-old infants" (TODO xác nhận tạp chí, DOI; tóm tắt qua trích dẫn thứ cấp): trẻ 2 tuổi chọn đúng vật khi nghe từ mới, nhưng nhớ kém sau 5 phút; lặp trước khi kiểm tra giúp nhớ tốt hơn.
7. Storkel và cộng sự (tóm tắt thứ cấp; TODO tác giả, năm, DOI): 36 lần gặp là đủ cho trẻ mẫu giáo lớn có rối loạn ngôn ngữ phát triển.
7b. Bài trên LSHSS 2020 (tóm tắt; TODO xác nhận đúng bài qua https://pubs.asha.org/doi/10.1044/2019_LSHSS-19-00029 hoặc https://pmc.ncbi.nlm.nih.gov/articles/PMC7213481 ): 4 từ khó mỗi cuốn sách cho kết quả tốt hơn, trung bình 17/36 từ được học trong 13 tuần.
8. Thông tư 50/2020/TT-BGDĐT, Chương trình làm quen với tiếng Anh dành cho trẻ em mẫu giáo (tóm tắt thứ cấp; trang Bộ GDĐT và thuvienphapluat chưa đọc được): https://luatvietnam.vn/tin-van-ban-moi/to-chuc-cho-tre-mau-giao-lam-quen-voi-tieng-anh-35-tuan-nam-186-29560-article.html và https://hoatieu.vn/phap-luat/thong-tu-50-2020-tt-bgddt-chuong-trinh-lam-quen-voi-tieng-anh-danh-cho-tre-em-mau-giao-207329 (trả 403 khi đọc). Nội dung: 35 tuần/năm; ≥2 hoạt động/tuần; 25–35 phút mỗi hoạt động. TODO: điều khoản, và kiểm tra sửa đổi 09/2025/TT-BGDĐT.
9. Montessori, "Three-Period Lesson" (định nghĩa; tóm tắt): https://archives.montessori-ami.org/help/glossary/three-period-lesson . Ghi chú: không tìm được nghiên cứu đối chứng riêng cho kỹ thuật này và không có số từ mỗi buổi.
10. Super Simple (tóm tắt; trang chính thức chưa đọc): https://supersimple.com/ . Ghi chú: lặp qua bài hát và động tác, mỗi bài có vài từ đích. Không có số từ mỗi bài đã kiểm.
11. Chiến lược đưa lựa chọn (tóm tắt, chưa đọc đầy đủ): https://www.asha.org/siteassets/early-intervention/ei-toolkit-strategy-spotlight-sheet-offering-choices.pdf . Không tìm được trang Hanen riêng về lựa chọn.

Ghi chú về nguồn không dùng:
- "Trẻ học 9 từ mỗi ngày" (gán cho Carey 1978): không truy được nguồn gốc. Không trích.
- "Rule of thumb 2–3 phút mỗi tuổi" cho thời lượng chú ý: chỉ là blog, không phải nghiên cứu. Không trích làm căn cứ.
- Nghiên cứu về thời gian chú ý của 49 trẻ 2 tuổi trong lớp học (chỉ thấy tiêu đề): chưa đọc số liệu. TODO.
