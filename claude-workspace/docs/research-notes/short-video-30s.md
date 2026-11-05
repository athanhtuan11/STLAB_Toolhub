# Video short 30 s – điều đã tra (2026-11-05)

Tra qua Codex (web) cho video giới thiệu esp32-s3-cam, người xem phụ huynh + học sinh. Chỉ ghi điều có nguồn; còn lại ghi "không có nguồn".

## Có nguồn
- **Hook 3 s đầu:** đưa điều đáng xem vào 3 giây đầu, dùng tò mò/bất ngờ; không mở bằng logo, lời chào.
  https://ads.tiktok.com/resources/help/article/creative-best-practices · https://ads.tiktok.com/business/en/guides/video-advertising-guide
- **Cấu trúc:** hook – thân – kết; quảng cáo TikTok đề xuất 21–34 s. https://ads.tiktok.com/business/en-US/creative-codes
- **Khung:** dọc 9:16, tối thiểu 720p, chừa chỗ cho giao diện app (nút, chú thích). https://ads.tiktok.com/business/en-US/creative-codes
- **Chữ/phụ đề:** nên có phụ đề hoặc chữ trên hình để hiểu được khi tắt tiếng. Khảo sát Mỹ 2019: 69 % xem không tiếng nơi công cộng,
  25 % ở nhà (không phải số Việt Nam). https://www.markstudios.com/research/video-captions-statistics
- **Người thật + sản phẩm đang dùng** tăng sức thuyết phục. https://ads.tiktok.com/resources/help/article/creative-best-practices
- **Đo hiệu quả Shorts:** xem "Stayed to watch", thời lượng xem trung bình; cách đếm view đổi từ 31/3/2025.
  https://support.google.com/youtube/answer/12220281 · https://support.google.com/youtube/answer/10059070
- **Quay điện thoại:** 4K/30 fps là mặc định tốt; 60 fps cho cảnh muốn làm chậm; khóa nét + phơi sáng trước khi quay.
  https://support.apple.com/en-gb/102276 · https://arts.ucla.edu/uploads/content/Documents/Mobile-Video-Recording-Best-Practices.pdf
- **Trẻ em lên hình:** xin đồng ý bằng văn bản của phụ huynh + học sinh; tránh lộ tên, trường, đồng phục, vị trí. (VN: Luật 91/2025,
  xem memory marketing.) https://www.esafety.gov.au/parents/issues-and-advice/privacy-child

## Không có nguồn (chỉ là kinh nghiệm dựng)
- Tỉ lệ xem hết chuẩn cho video 30 s; số cảnh/độ dài cảnh tối ưu (dùng tạm 7–9 cảnh, 3–4 s/cảnh).
- Kết thúc vòng lặp về cảnh mở đầu làm tăng xem lại.
- Vùng an toàn tính bằng pixel chung cho mọi app (STLab dùng: chừa trên 160 px, dưới 420 px – theo video-ai/CLAUDE.md, kiểm lại bằng xem trước trong app).
- Tốc độ đọc tiếng Việt tối ưu (từ/giây).

## Video AI không cần quay (tra 2026-11-05 qua Codex)
- Giữ đúng hình sản phẩm → **ảnh → video** (khung đầu là ảnh render/ảnh thật), mỗi cảnh 5–6 s, chuyển động nhỏ, 1 hành động/cảnh.
  Chữ, logo, màn hình, xoay cơ khí, tay lắp chi tiết nhỏ: AI hay méo → ghép chữ/giao diện thật ở hậu kỳ.
- Công cụ có ảnh → video: Google Veo/Flow (ảnh tham chiếu, khung đầu/cuối) https://support.google.com/flow/answer/16526234 ;
  Runway Gen-4 Turbo clip 5/10 s, có 9:16, API $0,05/giây https://help.runwayml.com/hc/en-us/articles/37327109429011-Creating-with-Gen-4-Video https://dev.runwayml.com/pricing ;
  Kling, Hailuo, Seedance qua Runway API $0,09–0,20/giây (cùng link giá). Quota miễn phí, watermark, quyền thương mại bản free: chưa xác minh.
- **Sora đã ngừng** (app 26/04/2026, API 24/09/2026) https://openai.com/sora/
- Chạy trên máy: Wan 2.2 / LTX cần ~24 GB VRAM → máy STLab không chạy được. Thuê GPU 4090 ~$0,89/giờ https://www.runpod.io/pricing
- **Gắn nhãn:** Luật Trí tuệ nhân tạo 134/2025/QH15 hiệu lực 01/03/2026, Điều 11: nội dung AI dễ gây nhầm phải thông báo rõ
  https://congbao.chinhphu.vn/van-ban/luat-so-134-2025-qh15-468694.htm ; TikTok bắt gắn nhãn AI, cấm AI mô phỏng người < 18 tuổi
  https://support.tiktok.com/en/using-tiktok/creating-videos/ai-generated-content ; YouTube bắt khai báo
  https://support.google.com/youtube/blog/424874071/updates-to-ai-content-disclosure-and-labels . Meta: chưa xác minh.
