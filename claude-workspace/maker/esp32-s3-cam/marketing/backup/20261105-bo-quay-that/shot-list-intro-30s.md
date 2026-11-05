# Kịch bản + danh sách cảnh quay – "Camera an ninh tự làm" (30 s, 9:16)

Người xem: phụ huynh + học sinh. Mục tiêu: thấy sản phẩm thật chạy được → tin STLab dạy làm thật → đăng ký Open Lab.
Cơ sở: `docs/research-notes/short-video-30s.md`. Tuan ít lên hình → tay + sản phẩm + máy in.

## Quay nhanh (~15 phút)
- Không cần đúng thứ tự, không cần cắt gọn: quay dư, Claude tự cắt cảnh + chọn đoạn đẹp. Không cần thu tiếng (giọng AI lồng sau).
- Lười đặt tên cũng được: chép hết clip vào `inbox/`, Claude tự nhận cảnh nào qua ảnh khung hình.
- Cảnh 4 (máy in) có thể dùng clip cũ đã quay A1 nếu có.

## Cài đặt điện thoại (mọi cảnh)
- Quay **dọc**, **4K 30 fps** (cảnh 6 quay **4K 60 fps** để làm chậm). Lau ống kính điện thoại.
- Chạm giữ vào chủ thể để **khóa nét + phơi sáng** (AE/AF Lock) trước khi bấm quay.
- Ánh sáng: cạnh cửa sổ, sáng chiếu chếch 45° từ phía trước; tắt đèn vàng lẫn màu. Nền bàn gọn, một màu (gỗ hoặc thảm cắt).
- Mỗi cảnh quay **3 lượt**, dư **2 s trước và sau** động tác. Giữ máy bằng 2 tay hoặc tì lên chồng sách (không cần gimbal).
- Chủ thể chính đặt ở **giữa khung**, tránh mép trên ~1/10 và mép dưới ~1/5 (chữ + nút của app che).

## Cảnh quay
| # | Thời gian | Cỡ cảnh | Nội dung | Cách quay | Chữ trên hình | Lời đọc (giọng AI) |
|---|---|---|---|---|---|---|
| 1 | 0–2 s | **Đặc tả** | Ống kính camera, ngón tay xoay vòng chỉnh nét | Máy cách ống kính ~10 cm, ngang tầm ống kính, đứng yên | – | "Camera an ninh này…" |
| 2 | 2–5 s | **Cận** | Tay cầm điện thoại, màn hình đang hiện hình trực tiếp từ camera (`stlab-cam.local`) | Qua vai, camera STLab nằm mờ phía sau; trong hình điện thoại thấy chính tay đang cầm | **Học sinh tự làm** | "…do học sinh tự làm ra." |
| 3 | 5–9 s | **Trung** (từ trên xuống) | Bày linh kiện rời: mạch ESP32-S3, camera, đế nạp, các chi tiết in, vít | Máy song song mặt bàn, cao ~50 cm, tay đưa từng món vào khung | **Mạch ESP32 + camera** | "Từ bo mạch nhỏ bằng ngón tay…" |
| 4 | 9–13 s | **Cận** | Máy in A1 đang in vỏ (đầu phun, lớp nhựa) | Đặt máy cố định ~20 cm, quay 60 s → dựng tua nhanh | **Tự thiết kế – in 3D** | "…tự thiết kế vỏ và in 3D…" |
| 5 | 13–17 s | **Cận** | Tay đặt mạch vào vỏ, đóng mặt trước, vặn vít khung chữ U | Chếch 45° từ trên, đi theo tay thật chậm | – | "…rồi tự lắp ráp." |
| 6 | 17–21 s | **Trung** | Sản phẩm trên bàn: tay xoay đế (pan) rồi gật camera (tilt) | **60 fps**, máy quay vòng nửa vòng quanh sản phẩm thật chậm (orbit), ngang tầm sản phẩm | **Xoay – nghiêng mọi hướng** | "Xoay, nghiêng theo ý muốn," |
| 7 | 21–25 s | **Toàn** | Camera đặt trên kệ nhìn ra phòng lab; một người đi ngang qua → cắt sang điện thoại hiện ảnh "Phát hiện chuyển động" | Cảnh rộng thấy cả phòng; người đi qua quay lưng/không lộ mặt | **Có người là biết ngay** | "có người đi qua là báo ngay." |
| 8 | 25–30 s | **Toàn** | Góc làm việc STLab: bàn, máy in, sản phẩm ở tiền cảnh; kết bằng đẩy chậm vào ống kính (nối lại cảnh 1 để video lặp) | Đi bộ chậm tiến về sản phẩm (push-in) | **Open Lab – Đến xem tận nơi** + logo | "Ghé Open Lab STLab để cùng làm nhé!" |

Cảnh phụ (có thì dùng): **cảnh nhìn từ chính camera STLab** – quay màn hình luồng video khi camera nhìn tay đang lắp ráp. Claude ghi
trực tiếp từ `/stream` trên máy tính, Tuan không phải quay.

## Ghi chú
- Cảnh 7 cần firmware v0.3.0 (đang làm). Chưa có thì quay người đi qua + hình trực tiếp trên điện thoại, chữ đổi thành "Xem mọi lúc qua Wi-Fi".
- Học sinh lên hình (tay/lưng): cần phiếu đồng ý phụ huynh trước khi đăng. Không để lộ tên, đồng phục, bảng tên.
- Không nhạc (Tuan chọn nhạc trong app); có giọng AI + phụ đề cứng. Lời đọc ~55 từ – đọc thử rồi chỉnh cho vừa 30 s.
- Gửi clip: chép vào `video-ai/projects/esp32-s3-cam-intro-30s/inbox/`, đặt tên `c01.mp4` … `c08.mp4` (lượt khác: `c05-b.mp4`).
