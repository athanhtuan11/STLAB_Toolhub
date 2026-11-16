# Xe lập trình kéo thả (block-coding-car) cho lớp 1–3: chương trình, bằng chứng, bộ khối, 8 buổi

Ngày truy cập nguồn: 2026-11-16. Dự án: `maker/block-coding-car/` (brief: `design/brief.md`).
Nền đã có, không lặp lại: [card-coding-robot-lessons.md](d:\04_Stlab\04_STLAB_Toolhub\claude-workspace\docs\research-notes\education\card-coding-robot-lessons.md) (GDMN, bộ chuẩn 5 tuổi, QCVN 3:2019).
Phần lớn nguồn chưa đọc được toàn văn (PDF bị chặn 403 hoặc ảnh quét). Mọi chỗ chỉ có tóm tắt tìm kiếm được ghi rõ, số liệu chưa kiểm được ghi `TODO`.

## Tóm tắt 5 dòng

1. GDPT 2018 (TT 32/2018): môn Tin học và Công nghệ ở tiểu học bắt đầu từ lớp 3 (nguồn thứ cấp, chưa đối chiếu được văn bản gốc). Lớp 1–2 là hoạt động làm quen/trải nghiệm, không có yêu cầu cần đạt thuật toán chính thức (`TODO` đọc Phụ lục TT 32/2018).
2. Bằng chứng trực tiếp về bé 6–7 tuổi với khối lệnh hoặc robot sàn còn ít và phần lớn chưa đọc được số liệu. Không tìm được nghiên cứu nào đo độ dài chuỗi, số ô, hay lặp cho lớp 1 với Bee-Bot/ScratchJr (`TODO`).
3. Điểm rõ nhất từ nguồn: trẻ 6–8 tuổi kéo thả chính xác còn khó; bấm chuột và kéo đơn giản thì làm được (NN/g, nguồn UX). Trái/phải theo tuổi chưa có số liệu đáng tin, nên hướng khối phải gắn với hướng mặt xe.
4. Đề xuất bộ khối: bỏ "Kết thúc" và "Chờ" khỏi v1; "Bắt đầu" là ô cố định; Lặp là một khối đơn (chưa kiểm cho 6–7 tuổi); "Khi bấm nút trên xe" hoãn sang sau.
5. Đề xuất 8 buổi × 30 phút đi từ 1 khối → chuỗi 3–4 khối → lặp → số ô; mỗi buổi có thử thách trên thảm 6 × 6 ô và câu hỏi gỡ lỗi. Mức tin cậy: thấp, cần thử thực địa với 1–2 nhóm trước khi in.

---

## 1. GDPT 2018: khớp chỗ nào

- **Văn bản:** Thông tư 32/2018/TT-BGDĐT ban hành Chương trình GDPT tổng thể (ban hành 26/12/2018), được sửa một phần bởi TT 13/2022. Nguồn: [caselaw – TT 32/2018](https://caselaw.vn/van-ban-phap-luat/341253-thong-tu-so-32-2018-tt-bgddt-ngay-26-12-2018-cua-bo-truong-bo-giao-duc-va-dao-tao-ve-chuong-trinh-giao-duc-pho-thong), truy cập 2026-11-16 (tiêu đề). Các trang toàn văn ([luatminhkhue](https://luatminhkhue.vn/chuong-trinh-giao-duc-pho-thong-tong-the-mon-cong-nghe.aspx), [hoatieu](https://hoatieu.vn/tai-lieu/chuong-trinh-giao-duc-pho-thong-mon-tin-hoc-1277), [thuvienphapluat](https://thuvienphapluat.vn/van-ban/Giao-duc/Thong-tu-32-2018-TT-BGDDT-Chuong-trinh-giao-duc-pho-thong-tong-the-377224.aspx)) trả về HTTP 403 khi truy cập, nên chưa đọc được yêu cầu cần đạt.
- **Tin học và Công nghệ từ lớp 3:** nguồn thứ cấp thống nhất (tài liệu giới thiệu chương trình trên Coggle; bài tạp chí [vjol – TCTBGD](https://vjol.info.vn/tctbgd/article/download/103307/87104)): cấp tiểu học dạy qua môn "Tin học và Công nghệ" từ lớp 3, khoảng 1 tiết/tuần (35 tiết/năm). Tài liệu tập huấn SGK Tin học 3 ([IIG](https://iigvietnam.com/wp-content/uploads/2023/12/Tai-lieu-tap-huan-mon-Tin-hoc-3.pdf)) nhắc "6 chủ đề" của lớp 3 nhưng PDF không đọc được. `TODO` liệt kê 6 chủ đề và xác nhận có "thuật toán" hay không.
- **Lớp 1–2:** Hoạt động trải nghiệm là bắt buộc từ lớp 1 (nguồn: bài tạp chí vjol, truy cập 2026-11-16). Với Tin học lớp 1–2, ghi chú trước ([card-coding-robot-lessons.md](d:\04_Stlab\04_STLAB_Toolhub\claude-workspace\docs\research-notes\education\card-coding-robot-lessons.md), mục 1.3) dẫn Công văn 616/2025 của Sở GDĐT Khánh Hòa: giáo dục tin học lớp 1–2 là hoạt động làm quen, không đánh giá, xếp loại. Chưa mở lại được văn bản để kiểm (`TODO`).
- **Lớp 4–5 (tham chiếu):** một nghiên cứu sư phạm mô tả Scratch ở lớp 4 (5 bài) và lớp 5 (6 bài, có lệnh lặp và rẽ nhánh). Nguồn: [vjol – Tạp chí Thiết bị giáo dục](https://vjol.info.vn/tdm/article/view/113405), truy cập 2026-11-16 (tóm tắt tìm kiếm, không mở toàn văn). Đây không phải chương trình chính thức.

**Kết luận cho dự án:**
- Đóng gói cho lớp 1–2 là **hoạt động làm quen/trải nghiệm** (STEM/HĐTN), không gọi là "môn Tin học". Lớp 3 mới khớp với môn Tin học và Công nghệ.
- Thuật toán (tuần tự, lặp, rẽ) xuất hiện rõ hơn ở lớp 4–5 theo thực tế sách giáo khoa. Vì vậy 8 buổi lớp 1 nên được coi là chuẩn bị cho tư duy tuần tự, không phải chương trình chính thức. `TODO` đối chiếu với Phụ lục TT 32/2018.

## 2. Bằng chứng về bé 6–7 tuổi

Phần lớn bằng chứng dưới đây là **trẻ 4–6 tuổi**, không đúng độ tuổi 6–7. Nhớ điều này khi suy ra.

| Nguồn | Công cụ | Đối tượng | Kết quả chính (đã kiểm) | Mức tin cậy |
|---|---|---|---|---|
| Angeli & Georgiou (2023), [Frontiers in Education](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2022.757627/full) | Bee-Bot | 170 trẻ 5–6 tuổi | Hiệu ứng gợi ý (scaffolding) rõ: F(2,164)=64,60, p<0,01 ở giai đoạn 2. Trẻ trai đạt điểm cao hơn ở mọi nhóm (tác giả báo cáo). Độ tin cậy liên người chấm 0,87. | Trung bình (độ tuổi thấp hơn mục tiêu) |
| Relkin, de Ruiter & Bers (2021), Computers & Education | TechCheck (15 thử thách không cắm máy, 6 lĩnh vực tư duy máy tính); chương trình CAL | Trẻ K–lớp 2 | Lớp 1 tăng điểm rõ; lớp 2 ít rõ hơn. Số liệu chi tiết chưa đọc được. Nguồn: [PDF BC](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2023/10/1-s2.0-S0360131521000993-main.pdf) (ảnh quét), [Relkin 2020](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2020/05/Relkin2020_Article_TechCheckDevelopmentAndValidat.pdf) (không đọc được). | Trung bình, **đúng độ tuổi 6–7**, cần đọc số liệu (`TODO`) |
| Strawhacker & Bers (2019), ETR&D, [DOI 10.1007/s11423-018-9622-x](https://link.springer.com/article/10.1007/s11423-018-9622-x) | ScratchJr; bài Solve It về chuỗi, gỡ lỗi, lập trình theo mục tiêu | Mô tả 6 giáo viên / 222 trẻ K–lớp 2 (tóm tắt tìm kiếm) | Trẻ làm được các bài chuỗi và gỡ lỗi cơ bản; số phần trăm chưa lấy được (`TODO`). | Trung bình |
| Kazakoff (2014), luận án, [PDF BC](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/04/EKazakoff_2014.pdf) | ScratchJr, 8 buổi | 38 trẻ, thí điểm | Số liệu chưa đọc được (`TODO`). | Thấp |
| Caballero-González et al. (2021), RIED, [bài báo](https://revistas-pre.uned.es/index.php/ried/article/view/27508/22032) | Robot, có nhóm đối chứng | 40 trẻ (Salamanca), tuổi chưa xác nhận | Nhóm có robot nắm chuỗi hành động tốt hơn (tóm tắt). Không có tỉ lệ. | Thấp–trung bình |
| Hall et al. (2022), TechTrends | Bee-Bot, chơi có hướng dẫn | 29 trẻ mầm non (tóm tắt) | Định tính: xuất hiện tư duy tính toán khi chơi. | Thấp (định tính) |
| Kazakoff, Sullivan & Bers (2013) | Robot KIBO, 1 tuần | 27 trẻ mầm non | Xem [card-coding-robot-lessons.md](d:\04_Stlab\04_STLAB_Toolhub\claude-workspace\docs\research-notes\education\card-coding-robot-lessons.md) mục 1.4; không lặp lại. | (xem file trước) |

**Trả lời 5 câu hỏi của brief:**

- **Độ dài chuỗi:** không có số liệu đáng tin cho trẻ 6–7 tuổi. Mục 2 của ghi chú card-coding ước 5–8 thẻ là **giả thuyết, không có nguồn**. `TODO` đo thực địa: số khối đúng liên tiếp của mỗi bé ở buổi 1–3.
- **Khái niệm lặp:** trẻ 4–5 tuổi khó hiểu cấu trúc "bao lặp" (ước tính, không có số liệu). Bee-Bot không có lệnh lặp sẵn, phải viết lại từng bước (nguồn: [Barefoot Computing – Repetition](https://www.barefootcomputing.org/concepts-and-approaches/repetition), truy cập 2026-11-16, tài liệu giáo viên). Trẻ 6–7 có thể hiểu lặp đơn khi đếm cụ thể, nhưng chưa có nguồn đo.
- **Số ô:** không có nguồn cho việc đếm ô của bé 6–7 trên thảm. Mục đo của brief (1–4 ô) là hợp lý theo tư duy thông thường; `TODO` kiểm bằng thử thực địa.
- **Trái/phải:** nghiên cứu Angeli & Georgiou (dẫn Sarama & Clements 2009) ghi trẻ gặp khó khi phân biệt trái/phải; có gợi ý (scaffolding) thì cải thiện (Shusterman & Spelke 2005). Số theo tuổi chưa đọc được (`TODO` Benton). Thiết kế nên dùng **mũi tên theo hướng mặt xe**, không dựa vào trái/phải của bé.
- **Chuột và kéo thả:** NN/g (ngày 2018-07-08, [nngroup.com](https://www.nngroup.com/articles/children-ux-physical-development/), truy cập 2026-11-16, là blog UX, không phải nghiên cứu đồng cấp) ghi: với nhóm 6–8 tuổi, bấm chuột làm được, nhưng **kéo, cuộn và bấm vật nhỏ bằng chuột/trackpad vẫn khó**; kéo đến đích chính xác (qua đường hầm, đúng điểm) khó với trẻ 5 tuổi. Nghiên cứu Donker & Reitsma (2007) với 104 trẻ mẫu giáo và lớp 1 (tóm tắt tìm kiếm, `TODO` link bản gốc) ghi kéo thả nhanh hơn và ít lỗi hơn bấm-di chuyển-bấm, và trẻ có thể dùng chuột với phần mềm giáo dục. Hai nguồn không mâu thuẫn: **bấm được, kéo chính xác thì khó**.

**Hệ quả thiết kế rút ra:** trẻ 6–7 có thể học khối bằng bấm chuột hoặc chạm; kéo thả là thao tác khó hơn, nên làm cả hai (xem mục 4). Mọi số liệu tuổi/độ dài chuỗi trên đều cần thử thực địa, không dùng làm thông số cứng.

## 3. Đề xuất bộ khối Cấp 1/2/3 (sửa brief)

Brief hiện tại: Cấp 1 gồm Bắt đầu, Tiến, Lùi, Quay trái, Quay phải, Kết thúc; Cấp 2 thêm Lặp ×2/×3, Âm thanh, Đèn mắt, Chờ; Cấp 3 thêm số ô 1–4, Khi bấm nút trên xe.

**Đề xuất (chưa được Tuan duyệt; không sửa brief):**

| Cấp | Khối | Thay đổi so với brief | Lý do | Đánh đổi |
|---|---|---|---|---|
| 1 | Bắt đầu | Giữ, nhưng là **ô cố định** ở đầu dải, không kéo | Giảm 1 khối kéo; chuỗi luôn có điểm bắt đầu rõ | Không dạy được "thêm bắt đầu" (không cần) |
| 1 | Tiến, Lùi | Giữ | Khối cơ bản nhất | Lùi có thể dạy sau Tiến |
| 1 | Quay trái, Quay phải | Giữ; mũi tên xoay theo **hướng mặt xe** | Không dựa trái/phải của bé | Bé phải hiểu mặt xe |
| 1 | Kết thúc | **Bỏ khỏi dải**; xe dừng khi hết chuỗi | Ít khối hơn; "Dừng" đỏ đã có | Bé ít gặp khái niệm kết thúc |
| 2 | Lặp ×2, Lặp ×3 | Giữ, dạng **khối lặp đơn** lặp khối kế tiếp (như ghi chú card-coding mục 3) | Giảm từ cặp mở/đóng xuống 1 khối | Không lặp được cả đoạn; chưa kiểm cho 6–7 (`TODO`) |
| 2 | Âm thanh, Đèn mắt | Giữ, không tính vào quãng đường | Phản hồi vui, không có khái niệm mới | Thêm chi tiết phần cứng (WS2812, MAX98357A) |
| 2 | Chờ | **Chuyển sang sau v1** hoặc bỏ | Khái niệm thời gian khó với lớp 1, không cần cho thảm 6 × 6 | Ít một lựa chọn sửa lỗi |
| 3 | Số ô 1–4 trên khối Tiến/Lùi | Giữ | Đọc số là mục tiêu Toán lớp 1 (`TODO` nguồn) | Cần khối có nhãn số và thử đếm được |
| 3 | Khi bấm nút trên xe | **Hoãn sang v2** | Khái niệm "sự kiện" khó; dễ nhầm với nút Dừng | Mất một tương tác hay |

**Số khối trên dải:** brief đặt ≤ 12 khối. Đề xuất ≤ 8 khối ở Cấp 1–2 và ≤ 10 ở Cấp 3, vì trẻ 6–7 làm chuỗi dài dễ mệt trong 30 phút với 2 bé. Đây là giả thuyết; `TODO` đo buổi 1–3.

**Số khối kéo được sau khi sửa:** Tiến, Lùi, Quay trái, Quay phải (Cấp 1); thêm Lặp, Âm thanh, Đèn (Cấp 2). Tổng 7 loại, dễ nhớ hơn 11 loại trong brief.

## Lộ trình 8 buổi × 30 phút

Phân bổ cho mỗi buổi (≈30 phút): khởi động 5′ (cho xe đi thử, nói tên khối); thử thách trên thảm 15′ (2 bé, 1 xe); đổi vai và kể lại 5′; dọn và gỡ lỗi 5′. Thảm 6 × 6 ô (900 × 900 mm), xuất phát ở ô (1,1).

| Buổi | Mục tiêu | Khối | Thử thách trên thảm (ô bắt đầu → đích) | Câu hỏi gỡ lỗi |
|---|---|---|---|---|
| 1 | Bấm Chạy, hiểu "đi 1 ô" | Tiến | (1,1) → (1,2): đến "vườn dâu" | "Xe có dừng đúng ô không?" |
| 2 | Tiến/lùi, đếm ô | Tiến, Lùi | (1,1) → (4,1): 3 ô tới "ruộng bắp", rồi lùi 1 ô | "Xe dừng ở ô nào? Thừa hay thiếu mấy ô?" |
| 3 | Quay trái/phải tại chỗ | Quay trái, Quay phải | Xe quay mặt về "hồ" rồi đi 2 ô | "Khối nào làm xe quay sai hướng?" |
| 4 | Chuỗi 3–4 khối, đoán trước | Tiến, Quay, Lùi | (1,1) → (3,4): đường vòng tránh "đống rơm" | "Trước khi chạy, con đoán xe dừng ở đâu?" |
| 5 | Nhóm 2 bé: người xếp, người kiểm | Tất cả khối cấp 1 | Hai xe cùng đến một đích không đụng nhau | "Ai kiểm tra? Lỗi ở khối số mấy?" |
| 6 | Khối lặp đơn: lặp một hành động | Lặp ×2 + Tiến/Quay | Đi zigzag 2 lần qua 2 ô | "Khối nào được lặp? Lặp mấy lần?" |
| 7 | Lặp ×3, âm thanh/đèn báo đến đích | Lặp ×3, Âm thanh, Đèn | Vòng quanh "hồ" (8 ô), đèn sáng khi tới đích | "Muốn 4 lần thì đổi số nào?" |
| 8 | Trình diễn: kể chuyện chuỗi, số ô (tùy chọn) | Tất cả; Số ô (nếu lớp đã quen) | Đường về nhà có 2 đích; nhóm kể lại bằng khối | "Chuỗi có mấy bước? Sửa bước nào?" |

Ghi chú:
- Thử thách vẽ trên thảm giấy in được (chưa cần xe) để cứu buổi khi xe hỏng.
- Buổi 8 chỉ dùng số ô nếu buổi 2 và 4 cho thấy bé đếm được. Nếu không, bỏ số ô.
- Mọi thứ tự buổi và thời lượng là giả thuyết, chưa có nguồn thực nghiệm (`TODO`).
- Với bé 6 tuổi chưa đọc được, mỗi buổi chỉ dùng 3–5 từ tiếng Anh/tiếng Việt cho khối (xem mục 4).

## 4. Điểm thiết kế UI cho trẻ chưa đọc thạo

1. **Icon trước, chữ sau.** Mỗi khối có icon một nghĩa (mũi tên theo hướng mặt xe). Chữ chỉ là nhãn phụ. Giữ chuột lên khối → đọc tên tiếng Việt bằng TTS (VieNeu, theo brief). Không dựa vào chữ để hiểu khối.
2. **Màu theo nhóm (theo brief):** xanh dương di chuyển, vàng điều khiển, tím âm thanh/đèn, đỏ kết thúc. Thêm hình dạng hoặc viền để không chỉ phụ thuộc màu (`TODO` kiểm bé mù màu; không có nguồn riêng trong ghi chú này).
3. **Kích thước.** Khối ≥ 64 px (brief). NN/g cho thấy vật nhỏ khó bấm với 6–8 tuổi, nên đề xuất ≥ 96 px cho khối trong dải và vùng thả rộng hơn khối (≈ 1,5 lần). `TODO` đo trên màn lab thật, khoảng cách ngồi thực tế.
4. **Kéo thả và bấm-chạm, làm cả hai.** Bấm khối → thêm vào cuối dải (không cần kéo). Kéo để sắp xếp lại. Đề xuất không bắt buộc kéo chính xác vào vị trí giữa hai khối; dải tự căn chỗ (snap). Đánh đổi: thêm nút "xóa khối" lớn (kéo khối ra ngoài dải hoặc bấm vào thùng rác) — cần thử với bé.
5. **Âm thanh xác nhận.** Mỗi lần thêm khối có âm ngắn; khi Chạy có tiếng bắt đầu; khi xe dừng có tiếng khác. Một khối đang chạy sáng viền và phát âm ngắn. Tránh âm thanh giống nhau cho các khối khác nhau.
6. **Phản hồi sai không chữ.** Khi xe đi sai chuỗi, dải lệnh rung nhẹ hoặc khối đỏ, kèm câu hỏi TTS "Xe đi đúng chưa?" — không hiện thông báo chữ dài.
7. **Nút Dừng đỏ luôn hiện** (brief), đặt ở nóc xe và trên màn; bé nhận ra ngay.

## Gợi ý cho STLab

1. **Cấp học:** đóng gói là hoạt động làm quen/STEM cho lớp 1–2; dùng tên "Tin học" cho lớp 3 trở lên.
2. **Trước khi chốt bộ khối:** thử 2 nhóm lớp 1 (mỗi nhóm 2 bé), 3 buổi đầu, ghi số khối đúng liên tiếp, số lần gỡ lỗi, và thao tác kéo thất bại. Đây là cách duy nhất kiểm được giả thuyết ở mục 2.
3. **Đánh đổi chính:** bỏ "Kết thúc" và "Chờ" làm app đơn giản hơn nhưng bé ít gặp khái niệm; giữ đủ khối làm bé học sâu hơn nhưng chậm hơn. Đề xuất giữ bộ đơn giản cho v1.
4. **Kiểm nguồn trước khi nói với phụ huynh hoặc trường:** mục Tin học lớp 3 (6 chủ đề) và mục hoạt động làm quen lớp 1–2 phải đối chiếu TT 32/2018 gốc. Hiện nay chỉ dựa vào tóm tắt thứ cấp.

## Các mục `TODO` chính

- Đọc Phụ lục TT 32/2018 (Tin học và Công nghệ lớp 3, 6 chủ đề; có "thuật toán" hay không; lớp 1–2).
- Số liệu Relkin, de Ruiter & Bers (2021) theo lớp 1, và TechCheck-K.
- Số liệu Strawhacker & Bers (2019) theo kỹ năng (chuỗi, gỡ lỗi, lặp).
- Donker & Reitsma (2007): link bản gốc và tỉ lệ lỗi theo tuổi.
- Tuổi và số liệu của Caballero-González (2021).
- Độ dài chuỗi, số ô, lặp cho bé 6–7 tuổi: chưa có nghiên cứu đo trực tiếp; cần thử thực địa.
- Trái/phải theo tuổi (Benton và cộng sự).
- Kích thước khối và vùng thả trên màn lab.

## Nguồn

- [caselaw – TT 32/2018 (tiêu đề)](https://caselaw.vn/van-ban-phap-luat/341253-thong-tu-so-32-2018-tt-bgddt-ngay-26-12-2018-cua-bo-truong-bo-giao-duc-va-dao-tao-ve-chuong-trinh-giao-duc-pho-thong), truy cập 2026-11-16.
- [luatminhkhue – CT Công nghệ](https://luatminhkhue.vn/chuong-trinh-giao-duc-pho-thong-tong-the-mon-cong-nghe.aspx), [hoatieu – CT Tin học](https://hoatieu.vn/tai-lieu/chuong-trinh-giao-duc-pho-thong-mon-tin-hoc-1277), [thuvienphapluat – TT 32/2018](https://thuvienphapluat.vn/van-ban/Giao-duc/Thong-tu-32-2018-TT-BGDDT-Chuong-trinh-giao-duc-pho-thong-tong-the-377224.aspx): truy cập 2026-11-16, HTTP 403, không đọc được.
- [vjol – TCTBGD, bài về Tin học lớp 3](https://vjol.info.vn/tctbgd/article/download/103307/87104), truy cập 2026-11-16 (tóm tắt tìm kiếm).
- [IIG – Tài liệu tập huấn Tin học 3](https://iigvietnam.com/wp-content/uploads/2023/12/Tai-lieu-tap-huan-mon-Tin-hoc-3.pdf), truy cập 2026-11-16 (PDF không đọc được).
- [vjol – Tạp chí Thiết bị giáo dục (Scratch lớp 4–5)](https://vjol.info.vn/tdm/article/view/113405), truy cập 2026-11-16 (tóm tắt).
- [Khánh Hòa – CV 616/2025](https://bangoi.khanhhoa.gov.vn/Resources/Docs/SubDomain/HomePage/2025/CV%20616_2025.signed.pdf), truy cập 2026-11-09 (qua ghi chú card-coding).
- [MIT Media Lab – ScratchJr overview](https://www.media.mit.edu/projects/scratchjr/overview/), truy cập 2026-11-16: ScratchJr dành cho trẻ 5–7 tuổi (tóm tắt tìm kiếm). App Store ghi "6 đến 8 tuổi" (tìm kiếm, `TODO` xác nhận).
- [Tufts Now – ScratchJr for kindergarten](https://now.tufts.edu/2014/07/30/scratchjr-coding-kindergarten), truy cập 2026-11-16 (tóm tắt).
- [Angeli & Georgiou (2023), Frontiers in Education](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2022.757627/full), truy cập 2026-11-16 (đọc được phần đầu, số liệu đã trích).
- [Strawhacker & Bers (2019), ETR&D](https://link.springer.com/article/10.1007/s11423-018-9622-x), truy cập 2026-11-16 (bị chuyển hướng đăng nhập, chỉ tóm tắt tìm kiếm).
- [Relkin, de Ruiter & Bers (2021)](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2023/10/1-s2.0-S0360131521000993-main.pdf) và [Relkin (2020), TechCheck](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2020/05/Relkin2020_Article_TechCheckDevelopmentAndValidat.pdf), truy cập 2026-11-16 (PDF ảnh quét, chỉ tóm tắt tìm kiếm).
- [Kazakoff (2014), luận án ScratchJr](https://sites.bc.edu/devtech/wp-content/uploads/sites/181/2018/04/EKazakoff_2014.pdf), truy cập 2026-11-16 (tóm tắt tìm kiếm).
- [Caballero-González et al. (2021), RIED](https://revistas-pre.uned.es/index.php/ried/article/view/27508/22032), truy cập 2026-11-16 (tóm tắt tìm kiếm).
- [Hall et al. (2022), TechTrends – Bee-Bot guided play (PDF Terrapin)](https://resources.terrapinlogo.com/stories/view_pdf/2022_hall_guided_play_BeeBots.pdf), truy cập 2026-11-16 (tóm tắt tìm kiếm).
- [Barefoot Computing – Repetition](https://www.barefootcomputing.org/concepts-and-approaches/repetition), truy cập 2026-11-16 (tài liệu giáo viên).
- [NN/g – Children's UX and physical development (2018-07-08)](https://www.nngroup.com/articles/children-ux-physical-development/), truy cập 2026-11-16.
- Donker & Reitsma (2007): tóm tắt tìm kiếm, link bản gốc `TODO`.
- [card-coding-robot-lessons.md](d:\04_Stlab\04_STLAB_Toolhub\claude-workspace\docs\research-notes\education\card-coding-robot-lessons.md): nền GDMN, Kazakoff 2013, QCVN 3:2019 (không lặp lại).
