# Seed – tiếng Anh cho bé mẫu giáo 3–6 tuổi (hướng dẫn dạy)

Chặng đầu của [giáo trình tiếng Anh STLab](../README.md). Tuan quyết 2026-11-11: làm cả 2 mức Core + Plus, buổi 30 phút,
soạn mới từ đầu, Tuan dạy trước, sau này có giáo viên khác. Vì vậy mọi giáo án ghi sẵn **câu giáo viên nói**.

| File | Nội dung |
|---|---|
| `units.yaml` | Nguồn duy nhất: 3 cấp × 8 chủ đề (từ, mẫu câu, bài hát, sản phẩm, "bé làm được") |
| `scope-and-sequence.md` | Bảng nội dung 3 năm, sinh tự động từ `units.yaml` |
| `check_seed.py` | Kiểm số từ theo Thông tư 50/2020 và sinh lại bảng: `python check_seed.py --write` |
| `lesson-plans/<id>-<ten>.md` | Giáo án 8 buổi của từng chủ đề; mẫu chuẩn: `s1-u1-hello.md` (Tuan duyệt 2026-11-11) |
| `check_plans.py` | Kiểm giáo án đúng khuôn: `python check_plans.py [s1|s2-u3]` |

## 1. Ba cấp

| Cấp | Tuổi | Từ Core (Bộ) | Từ Plus thêm | Đếm tới | Mẫu câu tới mức |
|---|---|---|---|---|---|
| Seed 1 | 3–4 | 35 | 16 | 3 | Chào, nói tên, It's…, I like… |
| Seed 2 | 4–5 | 70 | 30 | 5 | How are you?, What is it?, How many?, I have…, I don't like… |
| Seed 3 | 5–6 | 100 | 50 | 10 | Can you…?, Do you like…?, Where is…?, It lives in… |

Mỗi cấp tự đứng được: bé vào ở tuổi nào cũng học được, từ của cấp dưới được ôn lại trong trò chơi.

## 2. Nguyên tắc

1. **Chỉ nghe và nói.** Không dạy đọc, viết, không chép chữ (Thông tư 50/2020). Chữ chỉ xuất hiện trên thẻ cho giáo viên.
2. **Ngắn và đổi nhịp.** Mỗi hoạt động 3–8 phút, xen ngồi – đứng – vận động.
3. **Nghe trước, nói sau, không ép.** Bé được im lặng nghe vài buổi; làm đúng theo lệnh đã là hiểu.
4. **Lặp lại có chủ ý.** Mỗi từ Core được ghi rõ trong ít nhất 3 buổi của chủ đề (`check_plans.py` kiểm), cộng các lần
   ôn qua chant và trò chơi, rồi quay lại ở chủ đề sau.
5. **Tiếng Anh cho bài học, tiếng Việt cho an toàn.** Lệnh lớp học và nội dung bài nói bằng tiếng Anh kèm cử chỉ;
   dặn dò an toàn và dỗ bé nói tiếng Việt.
6. **Cú Bông là bạn cùng lớp.** Rối cú (cùng nhân vật với thiết bị english-teacher) chỉ "nói" tiếng Anh, là lý do để
   bé phải dùng tiếng Anh.

## 3. Một buổi 30 phút

| Phút | Bước | Việc |
|---|---|---|
| 0–3 | Hello | Vòng tròn, chant chào, Cú Bông chào từng bé |
| 3–7 | Review | Trò chơi thẻ ôn từ buổi trước |
| 7–13 | New | Giới thiệu 2–3 từ hoặc 1 mẫu câu mới bằng đồ thật, rối, thẻ |
| 13–19 | Move | Bài hát hoặc trò vận động dùng từ mới |
| 19–27 | Table | Hoạt động tại bàn: tô, dán, xếp, làm sản phẩm |
| 27–30 | Bye-bye | Dọn đồ, chant tạm biệt, sticker |

Từ Plus dạy ở bước Review và Move cho nhóm đã vững từ Core; không kiểm tra từ Plus ở mức Core.

## 4. Một chủ đề 8 buổi (4 tuần), một năm 70 buổi

| Buổi | Tên | Trọng tâm |
|---|---|---|
| 1 | Meet | Nửa đầu từ Core |
| 2 | Meet more | Nửa sau từ Core + mẫu câu 1 |
| 3 | Sing | Bài hát / chant của chủ đề |
| 4 | Story | Truyện ngắn với Cú Bông + mẫu câu 2 |
| 5 | Play | Trò chơi ôn toàn bộ, thêm từ Plus |
| 6 | Make | Làm sản phẩm |
| 7 | Tell | Bé giới thiệu sản phẩm |
| 8 | Party | Ôn, giáo viên ghi sổ quan sát |

Một năm: 8 chủ đề × 8 buổi = 64 buổi, cộng 6 buổi ôn và trình diễn (sau chủ đề 4 và chủ đề 8) = 70 buổi = 35 tuần × 2 buổi.

## 5. Lệnh lớp học (bé chỉ cần hiểu, không tính vào số từ)

Stand up · Sit down · Make a circle · Listen · Look · Come here · Hands up · Quiet, please · Tidy up · Well done! · Your turn.

## 6. Đánh giá: sổ quan sát, không chấm điểm

Mỗi chủ đề có đúng 2 mục "bé làm được" (trong `units.yaml`). Buổi 7–8 giáo viên ghi cho từng bé một trong ba mức:
**chưa** (cần làm cùng cô) · **đang** (làm được khi có gợi ý) · **được** (tự làm). Cuối chủ đề gửi phụ huynh 2 mục này
kèm tên bài hát để hát ở nhà. Không xếp hạng, không so bé với bé.

## 7. An toàn (đọc trước mỗi buổi Make)

- Chi tiết in 3D và đồ rời phải **to hơn ống thử chi tiết nhỏ** (đường kính 31,7 mm, chuẩn đồ chơi cho trẻ dưới 3 tuổi),
  cạnh bo tròn, không gãy thành mảnh nhỏ. Áp dụng cho cả lớp 5–6 tuổi.
- **Không dùng pin cúc áo** trong bất kỳ sản phẩm nào của Seed (nguy hiểm khi nuốt). Robot dùng pin phải có nắp bắt vít.
- Kéo, đinh ghim giấy, dao rọc: chỉ giáo viên dùng; Seed 1–2 dùng hình cắt sẵn, Seed 3 dùng kéo đầu tròn có người kèm.
- Sản phẩm có đinh ghim giấy (nhỏ, chân nhọn): giáo viên bấm ghim và dán băng keo phủ chân ghim; **không cho bé mang về
  nhà**, trưng bày ở góc lớp và gửi ảnh cho phụ huynh.
- Đất nặn, bút màu, keo: loại ghi rõ dùng cho trẻ em.
- Chủ đề Food: không cho nếm đồ ăn thật khi chưa có xác nhận dị ứng của phụ huynh.
- Trò vận động: dọn trống sàn, không chạy khi đang cầm đồ.

## 8. Lớp học và giáo viên (đề xuất STLab)

- Tối đa 12 bé một lớp; từ 9 bé trở lên có thêm 1 trợ giảng.
- Giáo viên mới: đọc mục 2–7, dự 2 buổi, dạy thử 1 buổi theo giáo án có sẵn câu nói.

## 9. Nối với thiết bị english-teacher

Máy sẽ đọc `units.yaml` để ở nhà bé nghe và nói đúng những từ, mẫu câu của chủ đề đang học trên lớp (kể cả từ Plus).
Phần xuất dữ liệu sang máy chưa làm. Lưu ý đã biết: điều khoản Gemini API với người dưới 18 tuổi, Tuan chưa quyết.

## 10. Việc pháp lý cần kiểm trước khi mở lớp

- **Trong trường mầm non (Cây Nhỏ):** Thông tư 50/2020 yêu cầu tài liệu làm quen tiếng Anh phải được Bộ thẩm định và
  giáo viên có bằng tiếng Anh + 120 tiết bồi dưỡng, hoặc bằng mầm non + chứng chỉ B2. Bộ Seed tự soạn chưa qua thẩm định,
  nên hiện chỉ dùng được như hoạt động bổ trợ. Thủ tục thẩm định tài liệu: chưa tra (`TODO`).
- **Tại trung tâm STLab:** điều kiện để một trung tâm STEAM mở lớp tiếng Anh thu phí (giấy phép, chuẩn giáo viên): chưa tra (`TODO`).
