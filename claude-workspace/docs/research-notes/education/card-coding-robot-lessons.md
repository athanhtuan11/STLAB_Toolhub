# Robot lập trình bằng thẻ (card-coding-robot) cho trẻ 4–7 tuổi: căn cứ, giáo án 8 buổi, an toàn

Ngày truy cập nguồn: 2026-11-09. Dự án: `maker/card-coding-robot/` (brief: `design/brief.md`).
Mọi khẳng định có link. Mục nào chỉ có nguồn thứ cấp hoặc chưa kiểm được văn bản gốc được ghi `TODO`.

## Tóm tắt 5 dòng

1. Chương trình GDMN đang áp dụng là Thông tư 17/2009 (sửa 28/2016, 51/2020). Chương trình GDMN mới được phê duyệt thí điểm bằng Quyết định 388/QĐ-BGDĐT (12/02/2026) cho 510 cơ sở từ năm học 2026–2027. Nội dung lĩnh vực nhận thức của bản mới chưa kiểm được (`TODO`).
2. Bộ chuẩn 5 tuổi cũ (TT 23/2010, có chỉ số "xác định vị trí … phải, trái") đã bị bãi bỏ từ 14/01/2025 bởi TT 21/2024; thay bằng QĐ 4222/QĐ-BGDĐT (27/12/2024), áp dụng 60–71 tháng.
3. Trái/phải: 4 tuổi chưa đáng tin; 5 tuổi bắt đầu; 6–7 tuổi phần lớn làm được (nguồn thứ cấp, cần thử thực địa). Robot học chuỗi tuần tự từ 4–5 tuổi có tiến bộ có đo (Kazakoff, Sullivan & Bers 2013).
4. Đề xuất bộ thẻ v1: giữ 8 thẻ nhưng đổi cặp "Lặp ×N / Kết thúc lặp" thành một thẻ lặp đơn cho bé 4–5 tuổi (đánh đổi: ít khái niệm hơn); mã màu theo nhóm thẻ; mọi thẻ ghi mũi tên theo hướng robot.
5. An toàn: QCVN 3:2019/BKHCN yêu cầu cơ lý theo TCVN 6238-1:2017 (ISO 8124-1:2014), nguồn ≤24 V, công bố hợp quy trước khi lưu thông. Ống thử chi tiết nhỏ đường kính trong 31,7 mm (nguồn phòng thử nghiệm). Cần kiểm mẫu với ống này trước khi bán (`TODO` độ sâu, chi tiết pin).

---

## 1. Căn cứ giáo dục

### 1.1 Chương trình GDMN hiện hành và chương trình mới

- Chương trình GDMN nền (TT 17/2009, sửa bởi TT 28/2016 và TT 51/2020): nhiều kế hoạch năm học của trường vẫn dẫn TT 17/2009 là căn cứ. Nguồn: [thuvienphapluat – TT 17/2009](https://thuvienphapluat.vn/van-ban/giao-duc/circular-17-2009-tt-bgddt-promulgating-early-childhood-education-curricula-458713.aspx) (trang bị chặn khi truy cập, chỉ xác nhận được tên và số hiệu); [caselaw – TT 51/2020](https://caselaw.vn/van-ban-phap-luat/369183-thong-tu-so-51-2020-tt-bgddt-ngay-31-12-2020-cua-bo-truong-bo-giao-duc-va-dao-tao-sua-doi-chuong-trinh-giao-duc-mam-non-kem-theo-thong-tu-17-2009-tt-bgddt-da-duoc-sua-doi-boi-thong-tu-28-2016-tt-bgddt) (sửa đổi TT 17/2009, hiệu lực 31/03/2021 theo nguồn này).
- **Chưa xác nhận được** nội dung chi tiết lĩnh vực phát triển nhận thức (định hướng không gian, đếm, sắp xếp) trong TT 17/2009 và 51/2020. Các trang tôi truy cập không hiển thị phần này. `TODO` đọc mục C Phần ba của TT 17/2009 bản gốc.
- Chương trình GDMN mới: Quyết định 388/QĐ-BGDĐT ngày 12/02/2026 phê duyệt chương trình thí điểm áp dụng từ năm học 2026–2027. Nguồn thứ cấp: [hoatieu – QĐ 388](https://hoatieu.vn/phap-luat/quyet-dinh-388-qd-bgddt-phe-duyet-chuong-trinh-giao-duc-mam-non-thi-diem-ap-dung-tu-nam-hoc-2026-2027-262347) (không mở được toàn văn, 403); [luatvietnam – 510 cơ sở](https://luatvietnam.vn/tin-van-ban-moi/chinh-thuc-thi-diem-chuong-trinh-giao-duc-moi-tai-truong-mam-non-186-108975-article.html) (xác nhận QĐ 388 ngày 12/02/2026, 510 cơ sở, một năm học).
- Theo báo Lào Cai, chương trình mới giữ 35 tuần/năm và yêu cầu không dạy trước chương trình lớp 1; [baolaocai.vn](https://baolaocai.vn/lao-cai-doi-moi-giao-duc-mam-non-tu-nhung-lop-hoc-thi-diem-post912363.html). Nguồn báo, cần đối chiếu văn bản (`TODO`).
  - **Hệ quả cho STLab:** nếu bán kit cho mầm non, nên đóng gói là hoạt động làm quen/khám phá chơi, không gọi là "môn tin học", để không đụng quy định "không dạy trước lớp 1".
- Công văn 2595/BGDĐT-GDMN hướng dẫn thí điểm (`TODO` đọc bản gốc): xem thông tin qua [hoatieu – CV 2595](https://hoatieu.vn/phap-luat/cong-van-2595-bgddt-gdmn-huong-dan-trien-khai-thi-diem-chuong-trinh-giao-duc-mam-non-moi-nam-hoc-2026-2027-251096) (chỉ thấy tiêu đề qua tìm kiếm).

### 1.2 Bộ chuẩn phát triển trẻ 5 tuổi (đã thay thế)

- TT 23/2010/TT-BGDĐT (Bộ chuẩn phát triển trẻ em năm tuổi) nằm trong danh sách bãi bỏ của TT 21/2024/TT-BGDĐT, hiệu lực 14/01/2025. Nguồn: [caselaw – TT 21/2024](https://caselaw.vn/van-ban-phap-luat/412026-thong-tu-so-21-2024-tt-bgddt-ngay-28-11-2024-cua-bo-truong-bo-giao-duc-va-dao-tao-bai-bo-van-ban-quy-pham-phap-luat-do-bo-truong-bo-giao-duc-va-dao-tao-ban-hanh-va-lien-tich-ban-hanh-trong-linh-vuc-giao-duc) (đã đọc được bảng bãi bỏ, truy cập 2026-11-09).
- Chỉ số cũ (tham khảo lịch sử, không còn hiệu lực): chỉ số 108 (chuẩn 24) "Xác định được vị trí (trong, ngoài, trên, dưới, trước, sau, phải, trái) của một vật so với một vật khác"; chỉ số 116 (chuẩn 27) "Nhận ra quy tắc sắp xếp đơn giản và tiếp tục thực hiện theo qui tắc"; chỉ số 62 (chuẩn 14) "Nghe hiểu và thực hiện được các chỉ dẫn liên quan đến 2, 3 hành động". Nguồn: [caselaw – TT 23/2010](https://caselaw.vn/van-ban-phap-luat/268824-thong-tu-23-2010-tt-bgddt-ban-hanh-quy-dinh-ve-bo-chuan-phat-trien-tre-em-nam-tuoi-do-bo-giao-duc-va-dao-tao-ban-hanh) (truy cập 2026-11-09).
- Bộ chuẩn mới: Quyết định 4222/QĐ-BGDĐT ngày 27/12/2024 (60–71 tháng; 22 chuẩn, 70 chỉ số, 6 lĩnh vực). Nguồn: [nhandan](https://nhandan.vn/ban-hanh-bo-chuan-phat-trien-tre-em-5-tuoi-post853856.html), [hethongphapluat](https://hethongphapluat.com/phap-luat/chinh-sach-phap-luat/bo-chuan-phat-trien-tre-5-tuoi-moi-nhat-22-chuan-va-70-chi-so-vang-cha-me-can-biet.html) (chỉ thấy qua tìm kiếm). `TODO` đọc chỉ số lĩnh vực nhận thức về phải/trái, thứ tự, đếm trong bản gốc.

### 1.3 Tin học và Công nghệ, lớp 1–3 (GDPT 2018)

- Thông tư 32/2018/TT-BGDĐT (ban hành 26/12/2018, hiệu lực 15/02/2019) là văn bản GDPT 2018. Nguồn: [luatminhkhue – TT 32/2018](https://luatminhkhue.vn/van-ban/thong-tu-32-2018-tt-bgddt.aspx) (trang bị chặn, chỉ xác nhận được tiêu đề).
- Môn Tin học và Công nghệ ở tiểu học bắt đầu từ lớp 3 (nguồn thứ cấp, mục tiêu từ tìm kiếm). Công văn Sở GDĐT Khánh Hòa (2025) ghi việc giáo dục tin học lớp 1–2 là hoạt động làm quen, không đánh giá, xếp loại: [CV 616/2025 Khánh Hòa](https://bangoi.khanhhoa.gov.vn/Resources/Docs/SubDomain/HomePage/2025/CV%20616_2025.signed.pdf). `TODO` đối chiếu điều khoản gốc của TT 32/2018 và phụ lục.
- Kết luận: không có môn Tin học chính thức cho 4–6 tuổi; với lớp 1–2 là hoạt động làm quen. Robot thẻ phù hợp làm hoạt động trải nghiệm/làm quen, không thay thế nội dung môn.

### 1.4 Nghiên cứu về tangible/unplugged coding cho trẻ 4–7

- **KIBO (Bers, Tufts DevTech):** robot cho 4–7 tuổi, lập trình bằng khối vật lý, không màn hình. Nguồn: [sites.bc.edu – KIBO EDUCON](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/05/EDUCON.pdf) (chỉ thấy tiêu đề và tóm tắt qua tìm kiếm).
- **Kazakoff, Sullivan & Bers (2013), Early Childhood Education Journal 41(4):245–255**, DOI 10.1007/s10643-012-0554-5: 27 trẻ, một tuần workshop robot + lập trình, trường mầm non STEM ở Harlem (New York); tăng điểm kỹ năng sắp xếp chuỗi tranh có ý nghĩa so với nhóm đối chứng. Nguồn: [Springer](https://link.springer.com/doi/10.1007/s10643-012-0554-5), [bản PDF BC](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/02/kazsullbers2013.pdf) (chỉ đọc được mục lục; số liệu chi tiết `TODO`).
  - Bản hội nghị AERA 2011 (cùng nhóm) báo cáo 34 trẻ 4,5–6,5 tuổi (nguồn thứ cấp qua tìm kiếm).
  - Con số "tăng 20–35%" thường được trích lại, nhưng tôi chưa kiểm được nguồn gốc. `TODO` không dùng cho đến khi kiểm.
- **Pugnali, Sullivan & Bers (2017), JITE: Innovations in Practice 16:171–193:** so sánh ScratchJr (đồ họa) và KIBO (vật lý) trên 28 trẻ 4–7 tuổi; kết luận giao diện có ảnh hưởng đến tư duy tính toán của trẻ. Số liệu chi tiết `TODO`. Nguồn: [BC PDF](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/02/pugnali-sullivan-bers-interface.pdf), DOI 10.28945/3768 (chỉ đọc được tóm tắt).
- **CS Unplugged** (Đại học Canterbury, New Zealand): hoạt động không máy tính, dùng thẻ, dây, bút màu, vận động; nội dung mở theo giấy phép CC BY-SA. Nguồn: [csunplugged.org/en/about](https://www.csunplugged.org/en/about/) (truy cập 2026-11-09). Trang này không nêu độ tuổi cụ thể; `TODO` tìm bản dành cho bậc mầm non.
- Cảnh báo từ nghiên cứu KIBO (thứ cấp): đo tư duy tính toán ở trẻ 4–5 tuổi khó hơn đáng kể so với trẻ lớn. Nguồn: tổng hợp tìm kiếm trên [sites.bc.edu – Pugnali/Bers](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/02/pugnali-sullivan-bers-interface.pdf); `TODO` xác minh trích dẫn gốc.

### 1.5 Khả năng thực tế theo độ tuổi (tóm tắt có mức tin cậy)

| Độ tuổi | Trái/phải | Chuỗi lệnh | Lặp | Mức tin cậy |
|---|---|---|---|---|
| 4 tuổi | Chưa đáng tin; dùng tay in đặt trên robot/thảm | Ước 2–3 thẻ (giả thuyết thiết kế, `TODO` đo) | Chưa có nguồn; giả định không hiểu cấu trúc "bao lặp" | Thấp |
| 5 tuổi | Bắt đầu; bộ chuẩn cũ kỳ vọng nhận vị trí phải/trái (đã bãi bỏ) | Ước 3–5 thẻ; có sắp xếp theo quy tắc (chỉ số 116 cũ) | Có thể hiểu "lặp" khi đếm cụ thể (`TODO` nguồn) | Trung bình |
| 6–7 tuổi | Phần lớn làm được (`TODO` tỉ lệ đúng theo tuổi) | Ước 5–8 thẻ; làm theo 2–3 hành động (chỉ số 62 cũ) | Hiểu lặp đơn giản, có thể gỡ lỗi chuỗi | Trung bình–thấp |

Trái/phải theo tuổi: nghiên cứu Benton và cộng sự cho thấy kỹ năng phân biệt trái/phải cải thiện dần từ 5 đến 10 tuổi, nhưng tôi chỉ đọc được tóm tắt qua tìm kiếm ([Royal Holloway repository](https://repository.royalholloway.ac.uk/items/ff4ee212-3ade-4844-a5ec-4aa964b09f1b/1/), truy cập bị lỗi chứng chỉ; `TODO` đọc số liệu theo tuổi). Vì vậy, thiết kế chắc không cần bé phải phân biệt trái/phải trên người. Thay vào đó, dùng **mũi tên trên thẻ và hướng mặt robot** (đã đề xuất ở mục 3).

---

## 2. Khung giáo án 8 buổi × 30–40 phút

Gợi ý chung: nhóm 2–4 bé, 1 người lớn. Thảm 900 × 900 mm (6 × 6 ô 150 mm). Mỗi buổi có một chủ đề thảm. Từ vựng tiếng Anh là 3–5 từ/buổi, nói trước, bé nhắc lại bằng hành động.

| Buổi | Mục tiêu chính | Hoạt động (≈35 phút) | Thẻ dùng | Thử thách trên thảm | Câu hỏi gỡ lỗi | Chủ đề thảm | Từ vựng EN |
|---|---|---|---|---|---|---|---|
| 1 | Làm quen robot, bấm Chạy, hiểu "đi một ô" | Chơi tự do 10′; quẹt 1 thẻ; so sánh robot đi và thẻ | Tiến | Đi 1 ô đến vườn dâu | "Robot có đi đúng 1 ô không?" | Nông trại Lâm Đồng (vườn dâu) | robot, go, stop, start |
| 2 | Tiến/lùi, đếm bước | Đặt 2–3 thẻ; đếm bước bằng tay | Tiến, Lùi | Đi từ chuồng gà đến ruộng bắp (3 ô) | "Robot dừng ở ô nào? Thừa hay thiếu?" | Nông trại (chuồng, ruộng bắp) | forward, backward, one, two |
| 3 | Rẽ trái/phải theo mũi tên trên thẻ | Đứng sau robot, cùng quay; bé chọn chiều bằng mũi tên | Rẽ trái, Rẽ phải | Đường vòng quanh hồ Xuân Hương (mô phỏng) | "Thẻ nào làm robot quay sai hướng?" | Đà Lạt (hồ, đồi thông) | turn left, turn right, lake, pine tree |
| 4 | Chuỗi 3–4 thẻ, đọc hết chuỗi trước khi chạy | Bé đoán kết quả trước khi bấm Chạy | Tiến, Rẽ, Lùi | Đường về nhà qua chợ | "Trước khi chạy, con đoán robot dừng ở đâu?" | Đà Lạt (chợ, nhà) | market, home, check |
| 5 | Nhóm 2 bé: người xếp, người kiểm tra | Luân phiên; mỗi người sửa 1 thẻ | Tất cả thẻ 1–4 | Hai robot cùng đến một đích | "Ai đã kiểm tra chuỗi? Lỗi ở đâu?" | Nông trại (chợ nông sản) | check, fix, try again |
| 6 | Thẻ lặp đơn (xem mục 3): lặp hành động | Lặp "đi 1 ô" 2 lần; so sánh với xếp tay | Lặp ×2 (đơn) + thẻ kế tiếp | Đi zigzag 2 lần trên ruộng | "Thẻ nào được lặp? Lặp mấy lần?" | Nông trại (ruộng bậc thang) | repeat, twice |
| 7 | Lặp ×3, đọc cấu trúc lặp | Thử vòng tròn quanh bãi; so sánh lặp và viết dài | Lặp ×3 (đơn) | Đi vòng quanh hồ 3 lần | "Nếu muốn 4 lần, đổi thẻ nào?" | Đà Lạt (hồ, công viên) | three times, circle |
| 8 | Trình diễn: kể chuyện chuỗi lệnh | Mỗi nhóm kể 1 chuyện bằng chuỗi; "nhảy múa" khi xong | Tất cả thẻ + Nhảy múa | Trình diễn "Một ngày ở Đà Lạt" | "Chuỗi của nhóm mình có mấy bước? Ai sửa được lỗi?" | Đà Lạt (tổng hợp) | dance, show, story |

Ghi chú:
- Buổi 6–7 dùng khối thẻ lặp theo mục 3. Với nhóm 4 tuổi, có thể bỏ buổi 7 và lặp bằng cách đặt 2 thẻ giống nhau (thủ công).
- Tất cả thử thách có thể chơi trên thảm giấy in được (chưa cần robot) để giảm rủi ro khi thử.
- Hiệu quả của cấu trúc giáo án (ví dụ thứ tự buổi) **chưa có nguồn thực nghiệm** `TODO` thử thực địa.

---

## 3. Đề xuất chỉnh bộ thẻ v1

Bộ thẻ hiện tại (brief): Tiến, Lùi, Rẽ trái, Rẽ phải, Lặp ×2, Lặp ×3, Kết thúc lặp, Nhảy múa/âm thanh.

1. **Đổi cấu trúc lặp (khuyến nghị).** Thay cặp "Lặp ×N" + "Kết thúc lặp" bằng **một thẻ lặp đơn**: thẻ "Lặp ×2" hoặc "Lặp ×3" lặp đúng thẻ kế tiếp. Lý do: giảm từ 2 thẻ ghép thành 1 và không cần hiểu khối đóng/mở. Đánh đổi: ít diễn đạt được lặp nhiều thẻ; không lặp được cả đoạn. Bằng chứng trực tiếp chưa có (`TODO` thử với 5 tuổi).
   - Phương án giữ nguyên cặp có ích cho 6–7 tuổi. Có thể làm 2 bộ thẻ (bé nhỏ và bé lớn), tăng chi phí in.
2. **Mũi tên trên mọi thẻ hướng tới robot.** Thẻ Tiến mũi tên lên, Lùi mũi tên xuống, Rẽ trái/phải mũi tên quay theo. Giảm phụ thuộc phải/trái trên người.
3. **Mã màu theo nhóm** (bé mù chữ): chuyển động (xanh), rẽ (vàng), lặp (tím), hành động (hồng). Đây là giả thuyết thiết kế, không có nguồn riêng.
4. **Giữ "Nhảy múa/âm thanh"** cho buổi cuối và làm phần thưởng; không tính vào quãng đường.
5. **Không thêm thẻ "Chờ"/"Bắt đầu"** trong v1; nút Chạy đã đủ. Chỉ xét lại nếu thử thực địa cho thấy trẻ cần dừng giữa chừng.
6. **Thẻ phải an toàn:** NTAG213 nằm kín giữa hai lớp (đúng brief); không để sticker lộ ra. Xem mục 4.

---

## 4. An toàn đồ chơi (nếu STLab bán kit)

Nguồn chính: QCVN 3:2019/BKHCN (ban hành kèm TT 09/2019/TT-BKHCN). Các nguồn truy cập được là văn bản đầy đủ một phần; ghi rõ phần đã đọc được.

- **Phạm vi:** đồ chơi cho trẻ dưới 16 tuổi (Điều 1.3.1 theo [luatvietnam – TT 09/2019](https://luatvietnam.vn/khoa-hoc/thong-tu-09-2019-tt-bkhcn-quy-chuan-ky-thuat-quoc-gia-ve-an-toan-do-choi-tre-em-178552-d1.html)). Một nguồn khác ghi 14 tuổi ([hethongphapluat](https://hethongphapluat.com/quy-chuan-ky-thuat-quoc-gia-qcvn-3-2019-bkhcn-ve-an-toan-do-choi-tre-em.html)). `TODO` xác nhận bản chính thức.
- **Ngày hiệu lực:** nguồn cho biết ban hành 30/09/2019 hoặc 30/12/2019 (hai ngày khác nhau); Mục 2 áp dụng từ 01/01/2021 (Điều 4.1). `TODO` xác nhận ngày trên Công báo.
- **Cơ lý và chi tiết nhỏ:** Điều 2.1.1 dẫn chiếu TCVN 6238-1:2017 (ISO 8124-1:2014) cho yêu cầu cơ lý. Nguồn: [luatvietnam – TT 09/2019](https://luatvietnam.vn/khoa-hoc/thong-tu-09-2019-tt-bkhcn-quy-chuan-ky-thuat-quoc-gia-ve-an-toan-do-choi-tre-em-178552-d1.html).
  - Ống thử chi tiết nhỏ: đường kính trong (31,7 ± 0,1) mm, theo danh mục phòng thử nghiệm được công nhận (BOA VILAS): [boa.gov.vn – VILAS 403](https://boa.gov.vn/sites/default/files/2026-01/vilas-403-tt0126.pdf) (truy cập qua tìm kiếm). Chiều sâu, góc đáy, điều kiện thử `TODO` đọc TCVN 6238-1:2017.
  - Theo TCVN 6238-1:2008 mục 4.4 (bản cũ), chi tiết nhỏ áp dụng cho đồ chơi dưới 36 tháng: [thuvienphapluat – TCVN 6238-1:2008](https://thuvienphapluat.vn/TCVN/Linh-vuc-khac/TCVN-6238-1-2008-an-toan-do-choi-tre-em-phan-1-cac-khia-canh-an-toan-902355.aspx). Yêu cầu nhãn cảnh báo cho 36–96 tháng chưa xác nhận (`TODO`).
- **Điện:** Điều 2.1.4: nguồn không vượt 24 V; dây dẫn và cáp nối đến bộ phận phải cách điện và bảo vệ thích hợp. Pin 4 × AA NiMH (4,8 V) thấp hơn ngưỡng 24 V. Nguồn: [luatvietnam – TT 09/2019](https://luatvietnam.vn/khoa-hoc/thong-tu-09-2019-tt-bkhcn-quy-chuan-ky-thuat-quoc-gia-ve-an-toan-do-choi-tre-em-178552-d1.html).
- **Ngăn pin:** chưa đọc được yêu cầu vít/khóa cho ngăn pin trong văn bản Việt Nam (`TODO`). Brief đã đặt yêu cầu mở bằng tua vít; giữ theo đó và kiểm lại với TCVN 6238 bản gốc.
- **Hợp quy để bán:** Điều 4.1: công bố hợp quy trước khi lưu thông, gắn dấu CR; Điều 4.4.2: phương thức chứng nhận 5 hoặc 7; Điều 4.4.4: giấy chứng nhận hiệu lực không quá 3 năm; Điều 5.3: đăng ký công bố với cơ quan quản lý địa phương (`TODO` xác nhận). Nguồn: [luatvietnam – TT 09/2019](https://luatvietnam.vn/khoa-hoc/thong-tu-09-2019-tt-bkhcn-quy-chuan-ky-thuat-quoc-gia-ve-an-toan-do-choi-tre-em-178552-d1.html).
- **Formaldehyde:** áp dụng đồ chơi dưới 3 tuổi (Điều 2.1.3.2.2). Kit cho 4–7 tuổi không thuộc nhóm này nếu nhãn đúng `TODO` xác nhận.

### Rủi ro cụ thể của thiết kế hiện tại (theo brief)

- **Sticker NTAG213:** nếu bong ra, có thể lọt ống 31,7 mm. Thiết kế kín và thử bóc tay.
- **Bánh xe, nắp, nút và vít:** kiểm lọt ống sau khi lắp và sau khi chơi (rơi, va đập).
- **Thẻ 60 × 60 mm:** kích thước này không lọt ống, nhưng cạnh thẻ và mép in cần kiểm.
- **Động cơ 28BYJ-48 và ULN2003:** kiểm nhiệt độ sau thời gian chạy dài (`TODO` đo, brief đã ghi).

---

## Gợi ý cho STLab

1. **Cấp học:** ưu tiên mầm non lớn (5–6 tuổi) và lớp 1 (6–7 tuổi); 4 tuổi dùng bản thẻ đơn giản. Ghi rõ "hoạt động làm quen" để không xung đột với quy định không dạy trước lớp 1 của chương trình GDMN mới.
2. **Thử nghiệm trước khi in hàng loạt:** chạy buổi 1–3 với 1 nhóm 4 tuổi và 1 nhóm 5–6 tuổi (đề xuất 4 buổi thử, `TODO` lịch). Ghi lại số thẻ đúng, số lần gỡ lỗi, và bé nào cần người lớn hỗ trợ. Đây là cách duy nhất kiểm được giả thuyết trong mục 1.5.
3. **Ràng buộc an toàn cần chốt trước khi in:** ống 31,7 mm cho toàn bộ chi tiết nhỏ, ngăn pin có vít, thử nhiệt. Chi phí thử nghiệm với phòng được chỉ định `TODO` (chưa có nguồn báo giá).
4. **Đánh đổi chính:** thẻ lặp đơn dễ hiểu hơn nhưng diễn đạt ít; bộ thẻ hai cấp độ giúp dạy được nhiều tuổi nhưng tăng chi phí in và quản lý.

## Các mục `TODO` chính

- Nội dung lĩnh vực nhận thức trong TT 17/2009 (mục C Phần ba) và QĐ 388/2026 (bản gốc).
- Chỉ số về phải/trái, đếm, sắp xếp trong QĐ 4222/QĐ-BGDĐT 27/12/2024 (bản gốc).
- Điều khoản gốc TT 32/2018 về Tin học lớp 1–2.
- Số liệu Kazakoff 2013 (bảng kết quả), Pugnali 2017, và tỉ lệ trái/phải theo tuổi (Benton).
- Độ sâu ống thử, nhãn cảnh báo 36–96 tháng, yêu cầu ngăn pin trong TCVN 6238-1:2017 bản chính thức.
- Phạm vi tuổi (14 hay 16) và ngày ban hành QCVN 3:2019.

## Nguồn

- [thuvienphapluat – TT 17/2009 (GDMN)](https://thuvienphapluat.vn/van-ban/giao-duc/circular-17-2009-tt-bgddt-promulgating-early-childhood-education-curricula-458713.aspx), truy cập 2026-11-09 (chỉ tiêu đề).
- [caselaw – TT 51/2020 (sửa GDMN)](https://caselaw.vn/van-ban-phap-luat/369183-thong-tu-so-51-2020-tt-bgddt-ngay-31-12-2020-cua-bo-truong-bo-giao-duc-va-dao-tao-sua-doi-chuong-trinh-giao-duc-mam-non-kem-theo-thong-tu-17-2009-tt-bgddt-da-duoc-sua-doi-boi-thong-tu-28-2016-tt-bgddt), truy cập 2026-11-09.
- [luatvietnam – 510 cơ sở GDMN thí điểm](https://luatvietnam.vn/tin-van-ban-moi/chinh-thuc-thi-diem-chuong-trinh-giao-duc-moi-tai-truong-mam-non-186-108975-article.html), truy cập 2026-11-09.
- [hoatieu – QĐ 388/QĐ-BGDĐT](https://hoatieu.vn/phap-luat/quyet-dinh-388-qd-bgddt-phe-duyet-chuong-trinh-giao-duc-mam-non-thi-diem-ap-dung-tu-nam-hoc-2026-2027-262347), truy cập 2026-11-09 (không mở được toàn văn).
- [baolaocai.vn – thí điểm GDMN mới](https://baolaocai.vn/lao-cai-doi-moi-giao-duc-mam-non-tu-nhung-lop-hoc-thi-diem-post912363.html), truy cập 2026-11-09 (nguồn báo).
- [caselaw – TT 23/2010 (bộ chuẩn 5 tuổi, đã bãi bỏ)](https://caselaw.vn/van-ban-phap-luat/268824-thong-tu-23-2010-tt-bgddt-ban-hanh-quy-dinh-ve-bo-chuan-phat-trien-tre-em-nam-tuoi-do-bo-giao-duc-va-dao-tao-ban-hanh), truy cập 2026-11-09.
- [caselaw – TT 21/2024 (danh sách bãi bỏ)](https://caselaw.vn/van-ban-phap-luat/412026-thong-tu-so-21-2024-tt-bgddt-ngay-28-11-2024-cua-bo-truong-bo-giao-duc-va-dao-tao-bai-bo-van-ban-quy-pham-phap-luat-do-bo-truong-bo-giao-duc-va-dao-tao-ban-hanh-va-lien-tich-ban-hanh-trong-linh-vuc-giao-duc), truy cập 2026-11-09.
- [nhandan – QĐ 4222/QĐ-BGDĐT](https://nhandan.vn/ban-hanh-bo-chuan-phat-trien-tre-em-5-tuoi-post853856.html), truy cập 2026-11-09 (qua tìm kiếm).
- [hethongphapluat – bộ chuẩn 5 tuổi mới](https://hethongphapluat.com/phap-luat/chinh-sach-phap-luat/bo-chuan-phat-trien-tre-5-tuoi-moi-nhat-22-chuan-va-70-chi-so-vang-cha-me-can-biet.html), truy cập 2026-11-09 (qua tìm kiếm).
- [luatminhkhue – TT 32/2018 (GDPT 2018)](https://luatminhkhue.vn/van-ban/thong-tu-32-2018-tt-bgddt.aspx), truy cập 2026-11-09 (bị chặn 403).
- [Khánh Hòa – CV 616/2025](https://bangoi.khanhhoa.gov.vn/Resources/Docs/SubDomain/HomePage/2025/CV%20616_2025.signed.pdf), truy cập 2026-11-09.
- [Springer – Kazakoff, Sullivan & Bers 2013](https://link.springer.com/doi/10.1007/s10643-012-0554-5), truy cập 2026-11-09.
- [BC DevTech – Kazakoff 2013 (PDF)](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/02/kazsullbers2013.pdf), truy cập 2026-11-09 (chỉ mục lục).
- [BC DevTech – Pugnali, Sullivan & Bers (PDF)](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/02/pugnali-sullivan-bers-interface.pdf), truy cập 2026-11-09 (chỉ tóm tắt).
- [BC DevTech – KIBO EDUCON (PDF)](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/05/EDUCON.pdf), truy cập 2026-11-09 (qua tìm kiếm).
- [CS Unplugged – About](https://www.csunplugged.org/en/about/), truy cập 2026-11-09.
- [Royal Holloway repository – Left-right discrimination](https://repository.royalholloway.ac.uk/items/ff4ee212-3ade-4844-a5ec-4aa964b09f1b/1/), truy cập 2026-11-09 (bị lỗi chứng chỉ, chỉ tóm tắt qua tìm kiếm).
- [luatvietnam – TT 09/2019 (QCVN 3:2019)](https://luatvietnam.vn/khoa-hoc/thong-tu-09-2019-tt-bkhcn-quy-chuan-ky-thuat-quoc-gia-ve-an-toan-do-choi-tre-em-178552-d1.html), truy cập 2026-11-09 (một phần).
- [hethongphapluat – QCVN 3:2019](https://hethongphapluat.com/quy-chuan-ky-thuat-quoc-gia-qcvn-3-2019-bkhcn-ve-an-toan-do-choi-tre-em.html), truy cập 2026-11-09 (một phần, mâu thuẫn về tuổi và ngày).
- [BOA VILAS 403 – danh mục thử nghiệm đồ chơi](https://boa.gov.vn/sites/default/files/2026-01/vilas-403-tt0126.pdf), truy cập 2026-11-09 (qua tìm kiếm, ống 31,7 mm).
- [thuvienphapluat – TCVN 6238-1:2008](https://thuvienphapluat.vn/TCVN/Linh-vuc-khac/TCVN-6238-1-2008-an-toan-do-choi-tre-em-phan-1-cac-khia-canh-an-toan-902355.aspx), truy cập 2026-11-09 (qua tìm kiếm).
