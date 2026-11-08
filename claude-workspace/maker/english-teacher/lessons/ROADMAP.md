# Lộ trình học Cú Bông (cô Lily) – bé 2–5 tuổi

Trạng thái: **bản nháp 2026-11-06, chờ Tuan duyệt.** Soạn bởi edu-researcher. Bài 09–12 đã soạn cùng ngày (chờ duyệt).
Đi cùng: `README.md` (nguồn và nguyên tắc), `01–12` (nội dung từng bài), `docs/research-notes/education/cu-bong-chu-de-tieng-anh-2-5-tuoi.md`.

Lưu ý quan trọng: code hiện tại (`server/live/curriculum.py`) chạy bài theo **thứ tự tên file** và chuyển bài khi bé đã nhắc đủ từ. Chưa đọc lịch tuần. Mục 8 là đặc tả cho lập trình viên, **chưa có hiệu lực** cho đến khi curriculum.py được sửa.

## Quy ước "tuần có học" (mới 2026-11-06, chờ Tuan duyệt)

- **Tuần lịch** = 7 ngày từ thứ Hai đến Chủ nhật, giờ Việt Nam.
- **Buổi** = một phiên bé có ít nhất 1 lượt nói (giữ nút và nói). Phiên bé im hết không tính. TODO Tuan xác nhận.
- **Tuần có học** = tuần lịch có **từ 2 buổi trở lên**.
- Mỗi bé có một **hàng hiện tại** (số 1–35, bắt đầu từ 1). Cả tuần lịch dùng chung hàng đó.
- **Chốt tuần:** khi có phiên đầu tiên của một tuần lịch mới, hệ thống xét tuần trước. Nếu tuần trước có ≥ 2 buổi thì hàng tăng thêm 1; nếu < 2 buổi thì hàng giữ nguyên. Tối đa tăng 1 hàng mỗi tuần, dù bé học 3 hay 5 buổi.
- **Nghỉ:** bé nghỉ bao nhiêu tuần thì quay lại đúng hàng đó. Không lùi, không nhảy.
- **Hàng 35 xong** thì quay lại hàng 1 (chu kỳ mới).
- Đánh đổi: chốt theo tuần chậm hơn một chút so với chuyển ngay ở buổi thứ 2, nhưng bé không học nửa tuần trên hai hàng khác nhau. Nếu Tuan muốn chuyển ngay ở buổi thứ 2, đổi một dòng trong mục 8.
- "Tuần" trong các mục 4–7 bên dưới là **tuần có học**, không phải tuần lịch. Khung 35 tuần khớp với 35 tuần/năm của Thông tư 50/2020 (mục VII khoản 1), nhưng năm học thật kéo dài hơn khi bé nghỉ.

## 1. Triết lý

Bé 2–3 tuổi học tiếng Anh chủ yếu bằng **nghe và làm theo**; nói là quà, không phải yêu cầu. Bé 4–5 tuổi tăng dần phần nói, hỏi đáp và đố.

**Căn cứ (có nguồn):**
- **Tương tác có đáp ứng là điều kiện học.** Kuhl, Tsao & Liu (2003, PNAS): trẻ 9 tháng học được âm tiếng Quan Thoại sau 12 buổi tiếp xúc trực tiếp; băng ghi âm và DVD không có tác dụng. Tác giả: "learning is influenced by the presence of a live person". Nguồn: https://pmc.ncbi.nlm.nih.gov/articles/PMC166444 (truy cập 2026-11-06). Lưu ý: trẻ 9 tháng, học âm vị, không phải từ vựng.
- **Từ mới học qua tương tác có đáp ứng, không học qua video không đáp ứng.** Roseberry, Hirsh-Pasek & Golinkoff (2014, Child Development, DOI 10.1111/cdev.12166): 36 trẻ 24–30 tháng (gần tuổi bé 2 tuổi). Học được khi người lớn đáp lại trẻ (trực tiếp hoặc video chat); video phát sẵn thì không. Nguồn: https://pmc.ncbi.nlm.nih.gov/articles/PMC3962808 (truy cập 2026-11-06). Cỡ mẫu nhỏ, học động từ.
- **Lặp lại có ngữ cảnh** giúp giữ từ: Horst, Parsons & Bryan (2011), xem README mục 5.
- **Mục tiêu nghe – làm theo:** Thông tư 50/2020 (mẫu giáo, 3–5 tuổi), xem README mục 3. Thông tư là lớp học, không quy định cho bé 2 tuổi.

**Hệ quả thiết kế (quyết định của STLab, không phải kết luận của nguồn):**
1. Cô **đáp lại từng lượt nói** của bé. Bài hát phát sẵn (file ghi âm) chỉ làm nền, không thay cô.
2. **Người lớn ngồi gần** là kênh học chính; Cú Bông hỗ trợ. Đánh đổi: thiết bị không thay được người thật. Chưa đo được mức bù.
3. Bé 2–3 tuổi: nghe và làm theo trước, nói là tùy bé. Bé 4–5 tuổi: thêm nói cụm ngắn.

Giới hạn: các nghiên cứu trên chỉ cho thấy tương tác có đáp ứng là cần thiết. Không có nguồn nào cho biết "nghe bao nhiêu" hay "bao nhiêu từ mỗi tuần" là đúng. Các con số trong mục 2 và 4 là **thiết kế**.

## 2. Cấp độ theo tuổi

| | Bé 2 tuổi | Bé 3 tuổi | Bé 4–5 tuổi |
|---|---|---|---|
| Nghe | Làm theo 1 hành động (vẫy tay, ngồi, chỉ); chỉ đúng vật khi nghe từ | Làm theo 1–2 bước ("Touch red") | Làm theo 2 bước; chọn đáp án khi cô đưa 2 lựa chọn |
| Nói | Bắt chước âm hoặc từ, không bắt buộc. Nói tiếng Việt vẫn được cô đáp | Nhắc lại 1 từ hoặc cụm | Nói 1–2 từ; cụm "I am happy" |
| Từ mới | 1 từ/tuần (bảng 2–3 tuổi) | 1 từ/tuần (bảng 2–3 tuổi) | 2 từ/tuần (bảng 4–5 tuổi) |
| Phiên | 3–4 phút, 1 phiên/ngày | ~5 phút, 1 phiên/ngày | ~5 phút, 1–2 phiên/ngày |
| Ngày học | 5 ngày/tuần, nghỉ 2 ngày | 5 ngày/tuần | 5 ngày/tuần |
| Tổng từ mới trong năm (ước) | ~34 (bảng 2–3 tuổi, 18 hàng) | ~34 | 63 (32 hàng, gồm bài 09–12) |

Ghi chú:
- Phiên ngắn hơn cho bé 2 tuổi là **thiết kế**, không có nguồn. Tổng thời gian vẫn dưới mốc WHO/AAP trong README (≤ 1 giờ/ngày).
- Ước năm: Thông tư ghi khoảng 35 từ cho 3–4 tuổi, khoảng 70 cho 4–5 tuổi (bản tổng hợp luatvietnam, chưa đối chiếu công báo). Bảng 4–5 tuổi hiện chỉ có 47 từ, **thấp hơn ~70**. Mục 9 đề xuất thêm bài để đạt ~65. TODO Tuan quyết.
- Bảng 2–3 tuổi dùng 18 hàng đầu (34 từ), gần nhịp ~35 từ của Thông tư cho 3–4 tuổi.
- Sau khi thêm bài 09–12: bảng 4–5 tuổi có 63 từ (47 + 16), còn thấp hơn ~70 khoảng 7 từ. TODO Tuan quyết.
- Bảng 2–3 tuổi **chưa** thêm 09–12: bảng đã đủ 35 hàng và mới tới "ball" (bài 08). Thêm vào sẽ phải kéo dài chu kỳ hoặc bỏ bớt từ. TODO Tuan quyết (xem mục 9).

## 3. Quy tắc chung (mọi tuổi, mọi tuần)

- **Câu xuyên suốt (daily):** "Hello!", "Thank you!", "Good job!", "Bye bye!", "Let's sing!" dùng ở mọi buổi. Luân phiên: "Good morning!" (buổi sáng), "Wash your hands!" (nhắc trước ăn hoặc sau chơi; bé không làm trên thiết bị).
- Câu xuyên suốt **không phải là từ vựng**: không gọi `mark_word`, không tính vào số từ.
- Từ mới của tuần: cô nói đúng 2 lần, bé nhắc 1 lần. Không đưa từ mới khi bé chưa nhắc được từ trước (theo README).
- **Bé 2–3 tuổi:** tối đa 3 từ ôn mỗi buổi, ưu tiên từ mới nhất.
- Mọi hoạt động có chạm hoặc động tác: người lớn ở gần. Chỉ chạm chính mình hoặc đồ vật an toàn (README mục An toàn).
- Không chấm điểm, không thi. Không hỏi tên, tuổi, trường, ba mẹ, gia đình thật, đồ ăn.

## 4. Lộ trình 12 tuần đầu (nhịp bé 4–5 tuổi)

Bé 2–3 tuổi: cùng thứ tự, mỗi từ kéo dài 1 tuần (xem bảng máy đọc "Lịch tuần 2–3 tuổi" trong mục 8).

| Tuần | Bài | Từ mới | Ôn (tuần N-1, N-3) | Vè / hoạt động gợi ý (TPR an toàn) |
|---|---|---|---|---|
| 1 | 04 chào hỏi | hello, goodbye | – | Vẫy tay chào "Hello!", "Goodbye!" – ngồi yên. Vè bài 04 |
| 2 | 04 cảm xúc | happy, tired | hello, goodbye | Làm mặt vui (mirror face). Ngáp (tired) – vè bài 04 |
| 3 | 01 màu | red, blue | happy, tired | "Touch something red" – người lớn ở gần. Vè bài 01 |
| 4 | 01 màu | yellow, green | red, blue, hello, goodbye | Đố: "What color is the sun?" Mốc 1 (xem mục 5) |
| 5 | 01 màu | pink, orange | yellow, green, happy, tired | Truyện ngắn: "A pink flower. Pink, pink!" |
| 6 | 03 số | one, two | pink, orange, red, blue | Giơ ngón tay đếm "one, two" – bé không chạm người khác |
| 7 | 03 số | three, four | one, two, yellow, green | Vè số bài 03 |
| 8 | 03 số | five | three, four, pink, orange | Hát đếm 1–5 |
| 9 | 02 con vật | cat, dog | five, one, two | Tiếng kêu: "meow", "woof" (bài 02) |
| 10 | 02 con vật | duck, cow | cat, dog, three, four | Tiếng kêu: "quack", "moo" |
| 11 | 02 con vật | pig, bird | duck, cow, five | Tiếng kêu: "oink", "tweet" |
| 12 | 05 cơ thể | head, eyes | pig, bird, cat, dog | Chạm đầu, chạm mắt (chính mình, người lớn ở gần). Mốc 2 |

Tuần 13–24 (tóm tắt, chi tiết trong bảng máy đọc):

- Tuần 13–14: nose, mouth; hands, feet (bài 05).
- Tuần 15–17: apple, banana; grape, mango; watermelon, strawberry (bài 07).
- Tuần 18–20: ball, doll; car, teddy bear; block, kite (bài 08).
- Tuần 21–23: mom, dad; baby, sister; brother, grandma (bài 06). Đưa xuống gần cuối vì chủ đề gia đình nhạy cảm. Chỉ dùng vai trò chung, không hỏi gia đình bé.
- Tuần 24: sad, hungry (bài 04). Để cuối vì "hungry" kích hoạt câu "Con nói với ba mẹ nhé!" trong bài 04. Mốc 3 (bé 4–5).
- Tuần 25–32 (bé 4–5, bài 09–12): 09 clap, sit, stand, stop (tuần 25–26); 10 circle, square, star, heart (tuần 27–28); 11 sun, rain, cloud, wind (tuần 29–30); 12 horse, lion, elephant, monkey (tuần 31–32).
- Tuần 33–35: ôn (bé 4–5).

**Thứ tự** khác với tên file: bài 04 (chào hỏi) đứng đầu vì đây là câu đầu tiên bé nói với cô và khớp 3–4 tuổi. Các bài không đổi tên file (README mục 12 đã ghi TODO).

## 5. Cột mốc kiểm tra nhẹ (không thi, không điểm)

Cô quan sát và hỏi nhẹ trong buổi. Không ghi điểm. `mark_word` chỉ dùng để nhớ từ nào cần ôn, không dùng làm mốc.

| Mốc | Bé 4–5 tuổi | Bé 2–3 tuổi |
|---|---|---|
| Mốc 1 | Cuối tuần 4: làm đúng hành động khi nghe "hello" hoặc "red" (ít nhất 3/5 lần). Nói được 1 từ bất kỳ | Cuối tuần 8: như trên, chỉ cần 1 từ |
| Mốc 2 | Cuối tuần 12: nhận ra từ đã học khi cô hỏi "Which one is red?" (chỉ tay được là đủ). Nói được 3 từ | Cuối tuần 24: nhận ra 6 từ đã học, nói được 2 từ |
| Mốc 3 | Cuối tuần 24: nói được cụm ngắn ("I am happy") hoặc trả lời câu 2 lựa chọn | Cuối tuần 35: nói được 3–4 từ bất kỳ |

Nếu bé chưa đạt mốc: giữ nguyên bài, kéo dài ôn, không lùi bài. Đây là tín hiệu để xem lại nhịp (mục 9).

## 6. Ôn xoay vòng (spaced)

- **Tuần có từ mới (bé 4–5):** ôn từ hàng tuần N-1 và N-3. Ví dụ tuần 5 ôn "yellow, green" và "happy, tired".
- **Bé 2–3 tuổi:** ôn theo hàng (tuần thứ hai của một hàng cũng ôn từ đầu hàng đó). Số từ ôn có thể lên 5, nên cô chỉ nói 3, ưu tiên từ mới nhất.
- **Tuần 25–32 (bé 4–5):** có từ mới của bài 09–12 (2 từ/tuần). Ôn từ hàng N-1 và N-3 như trên.
- **Tuần 33–35 (bé 4–5):** chỉ ôn, không có từ mới. Mỗi tuần ôn 4 từ từ 2 hàng cách nhau 12 hàng. Vè dùng vè của bài đang ôn.
- Tổng cộng tuần 33–35 chỉ ôn được 12 từ. Các từ còn lại ôn tiếp ở chu kỳ hai (TODO thiết kế).

## 7. Khung 35 tuần

- Tuần 1–12: mục 4.
- Tuần 13–24: hàng từ mới theo mục 4 (bé 4–5 hết bài 01–08 vào tuần 24).
- Tuần 25–32: từ mới bài 09–12 (bé 4–5). Tuần 33–35: ôn xoay vòng, không từ mới. Bé 2–3 tuổi vẫn còn hàng mới đến tuần 35.
- Sau tuần 35: quay lại tuần 1 của chu kỳ mới. Bé 4–5 đã biết các từ; chu kỳ hai nên tập trung nói cụm và câu. TODO thiết kế.

Câu xuyên suốt và vè: mỗi tuần có vè (dùng vè của bài tương ứng, đã có trong 01–12). Không cần bài mới cho lộ trình này.

## 8. Cho máy chủ (đọc được bằng mã)

**Hai mục bảng:**
- `## Lịch tuần (máy đọc)`: nhịp bé 4–5 tuổi (1 hàng/tuần học).
- `## Lịch tuần 2–3 tuổi (máy đọc)`: nhịp bé 2–3 tuổi (mỗi từ kéo dài 1 tuần; mỗi tuần 1 từ mới, tuần 16 không có từ mới).

**Dạng mỗi dòng** (khoảng trắng quanh `|`, danh sách ngăn bằng `, `, `-` nghĩa là rỗng):

```text
Week N: <lesson-id> | new: <từ, ...> | review: <từ, ...> | daily: <cụm, ...> | song: <lesson-id>
```

- `lesson-id` là tên file không có `.md`, ví dụ `04-greetings-feelings`. **Mọi `lesson-id` phải có file thật** trong thư mục này. Tuần chỉ ôn không có tên bài riêng: `lesson-id` và `song` = bài của từ ôn đầu tiên trong `review`.
- Regex gợi ý: `^Week (\d+): (\S+) \| new: (.*?) \| review: (.*?) \| daily: (.*?) \| song: (\S+)$`
- `new` và `review` là từ vựng. `daily` không phải từ vựng.
- Từ trong `new` phải có trong `Vocabulary` của `lesson-id`. Từ trong `review` có thể thuộc bài khác (tuần ôn mục 6 trộn bài).
- `Week N` là **số hàng** (tuần có học thứ N), không phải số tuần lịch.

**Tính hàng hiện tại (quy ước tuần có học):**
- Lưu theo biệt danh (không lưu tên) trong `learners.json`: `row` (hàng hiện tại, bắt đầu 1), `week_start` (thứ Hai đầu tuần lịch đang tính), `sessions_in_week` (số buổi trong tuần đó). TODO thêm 3 trường vào `learners.json`.
- Khi có phiên mới: nếu ngày hôm nay thuộc tuần lịch khác `week_start`, xét tuần cũ trước. Nếu `sessions_in_week` ≥ 2 thì `row` += 1 (sau 35 → 1). Sau đó đặt `week_start` = thứ Hai của tuần hiện tại và `sessions_in_week` = 0. Rồi mới dạy phiên này theo `row`.
- Mỗi phiên có tiếng nói của bé thì `sessions_in_week` += 1. Phiên bé im hết không cộng.
- Chốt chỉ xảy ra khi có phiên mới. Bé nghỉ thì không cần chốt, hàng giữ nguyên.
- Ví dụ: tuần A bé học thứ Hai và thứ Tư (2 buổi) → phiên đầu tuần B dùng hàng + 1. Tuần A chỉ học thứ Hai (1 buổi) → phiên đầu tuần B dùng lại hàng cũ.
- Đổi tuổi (`--set-age`): giữ `row`, đổi sang bảng tương ứng.
- Phương án khác để Tuan chọn: (a) chuyển hàng ngay ở buổi thứ 2 trong tuần (nhanh hơn, nhưng bé có thể học buổi 1 và buổi 2 trên hai hàng khác nhau); (b) đếm buổi thay vì tuần (mỗi 2 buổi lên 1 hàng; bé nghỉ dài không bị nhảy bài nhưng không tính theo tuần).

**Việc cho lập trình viên (không làm trong bản này):**
1. `curriculum.py` đang chọn bài theo thứ tự tên file (`sorted(glob)`) và chuyển bài theo `passed`. Cần đọc bảng tuần, lưu `row`, `week_start`, `sessions_in_week` theo biệt danh, và chốt tuần theo mục 8.
2. `mark()` chỉ tìm từ trong bài hiện tại. Tuần ôn trộn bài nên cần tìm trong mọi bài.
3. Giữ file này và README.md không chứa tiêu đề phần hướng dẫn AI (dấu thăng hai, rồi "Chỉ dẫn cho AI"). Hàm nạp bài đang bỏ qua file không có tiêu đề này, nên chỉ cần tránh thêm đúng tiêu đề đó vào ROADMAP.md.
4. Trước commit: chạy gate `server/test_curriculum.py` (phiên chính làm).

## 9. Bài đã soạn và việc cần Tuan quyết

**Đã soạn 2026-11-06 (chờ Tuan duyệt):** bài 09–12 theo định dạng bài 01–08. Từ chưa đối chiếu Cambridge Pre A1 Starters (PDF word list lớn hơn 10 MB, không mở được lúc soạn: TODO). Đối chiếu trước khi đưa vào thiết bị (theo nguyên tắc README: TODO trước khi đưa vào thiết bị).

1. **09-actions**: clap, sit, stand, stop. Làm theo hành động tại chỗ. Vào lịch 4–5 tuổi, tuần 25–26. Tránh "jump", "run", "climb" (README mục An toàn). "clap", "sit", "stand" đã dùng làm lệnh TPR ở bài 03, 05, 06, 08, nhưng không có trong bảng từ của các bài đó.
2. **10-shapes**: circle, square, star, heart. Vào lịch 4–5 tuổi, tuần 27–28.
3. **11-weather**: sun, rain, cloud, wind. Vào lịch 4–5 tuổi, tuần 29–30. "sun" đã là ví dụ câu mẫu bài 01 (không có trong bảng từ bài 01). Nếu muốn tránh hẳn, đổi thành "rainbow".
4. **12-animals-2**: horse, lion, elephant, monkey. Vào lịch 4–5 tuổi, tuần 31–32. Tiếng kêu (neigh, roar, trumpet, ooh) là quy ước phổ biến, chưa có nguồn.

**Cần Tuan quyết:**
- Bảng 2–3 tuổi có thêm 09–12 hay không (xem mục 2). Bản này **không** thêm.
- Chốt tuần kiểu nào: cuối tuần (mục 8, bản này) hay chuyển ngay ở buổi thứ 2.
- Xác nhận định nghĩa "buổi" (có ít nhất 1 lượt nói của bé).
- Bảng 4–5 tuổi giờ 63 từ, còn thấp hơn ~70 của Thông tư khoảng 7 từ. Có thêm bài không, và bài nào.

Việc khác:
- Đối chiếu từ bài 01–12 với Cambridge Pre A1 Starters và bộ đã duyệt (TODO trong README).
- Thử thật với bé 2 tuổi: đánh giá sau tuần 4 (có làm theo hành động không; bé có thích không). Điều chỉnh độ dài phiên và số từ theo đó. Ghi quan sát vào file, không ghi tên bé.
- Vị trí câu xuyên suốt trong thiết bị: không thuộc file bài. TODO Tuan và lập trình viên chọn cách đưa vào prompt.

## Lịch tuần (máy đọc)

Nhịp bé 4–5 tuổi. Mỗi dòng là một hàng (tuần có học thứ N). Xem mục 8 để đọc.

```text
Week 1: 04-greetings-feelings | new: hello, goodbye | review: - | daily: hello, thank you, good job, bye bye, let's sing | song: 04-greetings-feelings
Week 2: 04-greetings-feelings | new: happy, tired | review: hello, goodbye | daily: hello, thank you, good job, bye bye, let's sing | song: 04-greetings-feelings
Week 3: 01-colors | new: red, blue | review: happy, tired | daily: hello, thank you, good job, bye bye, let's sing | song: 01-colors
Week 4: 01-colors | new: yellow, green | review: red, blue, hello, goodbye | daily: hello, thank you, good job, bye bye, let's sing | song: 01-colors
Week 5: 01-colors | new: pink, orange | review: yellow, green, happy, tired | daily: hello, thank you, good job, bye bye, let's sing | song: 01-colors
Week 6: 03-numbers-1-5 | new: one, two | review: pink, orange, red, blue | daily: hello, thank you, good job, bye bye, let's sing | song: 03-numbers-1-5
Week 7: 03-numbers-1-5 | new: three, four | review: one, two, yellow, green | daily: hello, thank you, good job, bye bye, let's sing | song: 03-numbers-1-5
Week 8: 03-numbers-1-5 | new: five | review: three, four, pink, orange | daily: hello, thank you, good job, bye bye, let's sing | song: 03-numbers-1-5
Week 9: 02-animals | new: cat, dog | review: five, one, two | daily: hello, thank you, good job, bye bye, let's sing | song: 02-animals
Week 10: 02-animals | new: duck, cow | review: cat, dog, three, four | daily: hello, thank you, good job, bye bye, let's sing | song: 02-animals
Week 11: 02-animals | new: pig, bird | review: duck, cow, five | daily: hello, thank you, good job, bye bye, let's sing | song: 02-animals
Week 12: 05-body | new: head, eyes | review: pig, bird, cat, dog | daily: hello, thank you, good job, bye bye, let's sing | song: 05-body
Week 13: 05-body | new: nose, mouth | review: head, eyes, duck, cow | daily: hello, thank you, good job, bye bye, let's sing | song: 05-body
Week 14: 05-body | new: hands, feet | review: nose, mouth, pig, bird | daily: hello, thank you, good job, bye bye, let's sing | song: 05-body
Week 15: 07-fruits | new: apple, banana | review: hands, feet, head, eyes | daily: hello, thank you, good job, bye bye, let's sing | song: 07-fruits
Week 16: 07-fruits | new: grape, mango | review: apple, banana, nose, mouth | daily: hello, thank you, good job, bye bye, let's sing | song: 07-fruits
Week 17: 07-fruits | new: watermelon, strawberry | review: grape, mango, hands, feet | daily: hello, thank you, good job, bye bye, let's sing | song: 07-fruits
Week 18: 08-toys | new: ball, doll | review: watermelon, strawberry, apple, banana | daily: hello, thank you, good job, bye bye, let's sing | song: 08-toys
Week 19: 08-toys | new: car, teddy bear | review: ball, doll, grape, mango | daily: hello, thank you, good job, bye bye, let's sing | song: 08-toys
Week 20: 08-toys | new: block, kite | review: car, teddy bear, watermelon, strawberry | daily: hello, thank you, good job, bye bye, let's sing | song: 08-toys
Week 21: 06-family | new: mom, dad | review: block, kite, ball, doll | daily: hello, thank you, good job, bye bye, let's sing | song: 06-family
Week 22: 06-family | new: baby, sister | review: mom, dad, car, teddy bear | daily: hello, thank you, good job, bye bye, let's sing | song: 06-family
Week 23: 06-family | new: brother, grandma | review: baby, sister, block, kite | daily: hello, thank you, good job, bye bye, let's sing | song: 06-family
Week 24: 04-greetings-feelings | new: sad, hungry | review: brother, grandma, mom, dad | daily: hello, thank you, good job, bye bye, let's sing | song: 04-greetings-feelings
Week 25: 09-actions | new: clap, sit | review: sad, hungry, baby, sister | daily: hello, thank you, good job, bye bye, let's sing | song: 09-actions
Week 26: 09-actions | new: stand, stop | review: clap, sit, brother, grandma | daily: hello, thank you, good job, bye bye, let's sing | song: 09-actions
Week 27: 10-shapes | new: circle, square | review: stand, stop, sad, hungry | daily: hello, thank you, good job, bye bye, let's sing | song: 10-shapes
Week 28: 10-shapes | new: star, heart | review: circle, square, clap, sit | daily: hello, thank you, good job, bye bye, let's sing | song: 10-shapes
Week 29: 11-weather | new: sun, rain | review: star, heart, stand, stop | daily: hello, thank you, good job, bye bye, let's sing | song: 11-weather
Week 30: 11-weather | new: cloud, wind | review: sun, rain, circle, square | daily: hello, thank you, good job, bye bye, let's sing | song: 11-weather
Week 31: 12-animals-2 | new: horse, lion | review: cloud, wind, star, heart | daily: hello, thank you, good job, bye bye, let's sing | song: 12-animals-2
Week 32: 12-animals-2 | new: elephant, monkey | review: horse, lion, sun, rain | daily: hello, thank you, good job, bye bye, let's sing | song: 12-animals-2
Week 33: 04-greetings-feelings | new: - | review: hello, goodbye, nose, mouth | daily: hello, thank you, good job, bye bye, let's sing | song: 04-greetings-feelings
Week 34: 04-greetings-feelings | new: - | review: happy, tired, hands, feet | daily: hello, thank you, good job, bye bye, let's sing | song: 04-greetings-feelings
Week 35: 01-colors | new: - | review: red, blue, apple, banana | daily: hello, thank you, good job, bye bye, let's sing | song: 01-colors
```

## Lịch tuần 2–3 tuổi (máy đọc)

Nhịp bé 2–3 tuổi: mỗi từ kéo dài 1 tuần, mỗi tuần 1 từ mới (tuần 16 không có từ mới, vì hàng "five" chỉ có 1 từ). Đơn vị "Week N" là hàng (tuần có học thứ N).

```text
> 2026-11-08 Tuan chọn phương án A (docs/research-notes/education/cu-bong-tung-tu-mot.md): 2 từ mới/tuần CÙNG CHỦ ĐỀ, mỗi buổi 1 từ mới (từng từ một) + tối đa 2 từ ôn. Tiến độ theo CON TRỎ TỪ (nhớ bé/máy đã học tới đâu), không quay lại từ đầu khi khởi động; tuần chỉ giới hạn tối đa 2 từ mới.
Week 1: 03-numbers-1-5 | new: one, two | review: - | daily: hello, thank you, good job, bye bye, let's sing | song: 03-numbers-1-5
Week 2: 03-numbers-1-5 | new: three, four | review: one, two | daily: hello, thank you, good job, bye bye, let's sing | song: 03-numbers-1-5
Week 3: 03-numbers-1-5 | new: five | review: three, four | daily: hello, thank you, good job, bye bye, let's sing | song: 03-numbers-1-5
Week 4: 04-greetings-feelings | new: hello, goodbye | review: five | daily: hello, thank you, good job, bye bye, let's sing | song: 04-greetings-feelings
Week 5: 04-greetings-feelings | new: happy, tired | review: hello, goodbye | daily: hello, thank you, good job, bye bye, let's sing | song: 04-greetings-feelings
Week 6: 01-colors | new: red, blue | review: happy, tired | daily: hello, thank you, good job, bye bye, let's sing | song: 01-colors
Week 7: 01-colors | new: yellow, green | review: red, blue | daily: hello, thank you, good job, bye bye, let's sing | song: 01-colors
Week 8: 02-animals | new: cat, dog | review: yellow, green | daily: hello, thank you, good job, bye bye, let's sing | song: 02-animals
Week 9: 02-animals | new: duck, cow | review: cat, dog | daily: hello, thank you, good job, bye bye, let's sing | song: 02-animals
Week 10: 05-body | new: head, eyes | review: duck, cow | daily: hello, thank you, good job, bye bye, let's sing | song: 05-body
Week 11: 05-body | new: nose, mouth | review: head, eyes | daily: hello, thank you, good job, bye bye, let's sing | song: 05-body
Week 12: 05-body | new: hands, feet | review: nose, mouth | daily: hello, thank you, good job, bye bye, let's sing | song: 05-body
Week 13: 07-fruits | new: apple, banana | review: hands, feet | daily: hello, thank you, good job, bye bye, let's sing | song: 07-fruits
Week 14: 08-toys | new: ball, car | review: apple, banana | daily: hello, thank you, good job, bye bye, let's sing | song: 08-toys
Week 15: 06-family | new: mom, dad | review: ball, car | daily: hello, thank you, good job, bye bye, let's sing | song: 06-family
Week 16: 06-family | new: baby | review: mom, dad | daily: hello, thank you, good job, bye bye, let's sing | song: 06-family
Week 17: 09-actions | new: clap, sit | review: baby | daily: hello, thank you, good job, bye bye, let's sing | song: 09-actions
Week 18: 09-actions | new: stand | review: clap, sit | daily: hello, thank you, good job, bye bye, let's sing | song: 09-actions
Week 19: 11-weather | new: sun, star | review: stand | daily: hello, thank you, good job, bye bye, let's sing | song: 11-weather
```
## Nguồn

- Kuhl, Tsao & Liu (2003), PNAS 100(15):9096–9101: https://pmc.ncbi.nlm.nih.gov/articles/PMC166444 (truy cập 2026-11-06)
- Roseberry, Hirsh-Pasek & Golinkoff (2014), Child Development 85(3):956–970, DOI 10.1111/cdev.12166: https://pmc.ncbi.nlm.nih.gov/articles/PMC3962808 (truy cập 2026-11-06)
- Nguồn khác (Thông tư 50/2020, Horst 2011, WHO, AAP, Cambridge): xem `README.md` mục Tóm tắt nguồn.
