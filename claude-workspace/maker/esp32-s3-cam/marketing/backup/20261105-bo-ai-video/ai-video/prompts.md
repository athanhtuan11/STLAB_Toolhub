# Hướng dẫn tạo clip AI – esp32-s3-cam (phương án A)

Ảnh khung đầu: `keyframes/` (Claude render bằng Blender, đúng hình CAD). Bạn đưa từng ảnh lên web AI để nó cho ảnh chuyển động,
tải clip về, chép vào `claude-workspace/video-ai/projects/esp32-s3-cam-intro-30s/inbox/` → Claude dựng 30 s.

## Cách làm trên Google Flow (labs.google/flow – đăng nhập Gmail)
1. Tạo dự án mới → chọn chế độ tạo video **từ ảnh** (Frames to Video / Ingredients – tên nút có thể khác theo phiên bản).
2. Chọn khổ **9:16 (dọc)**. Tải ảnh khung đầu lên (cảnh 3: tải `k03a` làm khung đầu + `k03b` làm khung cuối).
3. Dán câu lệnh tiếng Anh bên dưới (chép cả khối). Tắt/bỏ âm thanh nếu có tùy chọn (Claude lồng giọng sau).
4. Mỗi cảnh tạo **2 bản**, tải bản nào sản phẩm không bị méo. Đặt tên như cột "Tên clip".
Kling (klingai.com) làm tương tự: Image to Video → 9:16 → dán câu lệnh; cảnh 3 dùng "Start & End frame".
Hạn mức miễn phí mỗi web: chưa xác minh – hết lượt thì báo Claude.

**Loại bỏ clip nếu:** khung chữ U hoặc đế bị đổi hình, ống kính dịch chỗ, xuất hiện chữ/logo lạ, có người/tay, vật thể mọc thêm.

## Câu lệnh (giữ nguyên tiếng Anh – AI hiểu tốt hơn)

Đoạn chung đã nằm sẵn trong mỗi câu: giữ nguyên hình sản phẩm, chuyển động nhỏ, không chữ, không người.

| Cảnh | Ảnh | Tên clip | Giây |
|---|---|---|---|
| 1 | k01-macro-lens | c01.mp4 | 5 |
| 2 | k02-desk-hero | c02.mp4 | 5 |
| 3 | k03a → k03b | c03.mp4 | 5 |
| 4 | k04-shelf-room | c04.mp4 | 5 |
| 5 | k05-tilt-pan | c05.mp4 | 5 |
| 6 | k06-low-hero | c06.mp4 | 5 |

**c01 – đặc tả ống kính**
```
Extreme macro shot of the camera lens on a 3D-printed security camera. Very slow push-in toward the lens, a soft highlight glides across the glass, shallow depth of field, natural window light, realistic product cinematography. Keep the product shape, colors and proportions exactly as in the image. Static product, no extra objects, no text, no logos, no people, no hands.
```

**c02 – sản phẩm trên bàn**
```
Realistic product shot of a small 3D-printed home security camera on a wooden desk beside a window in the morning. Slow smooth dolly to the right with slight parallax, sunlight and soft shadows shift gently, dust particles in the light. Keep the product shape, colors and proportions exactly as in the image. The product does not move or change. No text, no logos, no people, no hands.
```

**c03 – lắp ráp (khung đầu k03a, khung cuối k03b)**
```
The separate 3D-printed parts float and slowly glide together along their assembly axes until they form the finished security camera, clean and precise, locked-off camera, soft studio light. Parts keep their exact shapes and colors; nothing new appears. No text, no logos, no people, no hands.
```

**c04 – canh phòng**
```
Wide realistic shot: a small security camera on a shelf overlooking a bright STEAM classroom with blurred background. Very slow push-in toward the camera, gentle natural light, calm atmosphere. Keep the product shape, colors and proportions exactly as in the image. Empty room, no people, no text, no logos, no screens with content.
```

**c05 – xoay nghiêng**
```
Medium realistic shot at product height. The camera head tilts slowly on its U-shaped bracket while the round base turns slightly, smooth mechanical motion, the bracket and base keep their exact shape. Locked-off camera, soft window light. Keep the product shape, colors and proportions exactly as in the image. No text, no logos, no people, no hands.
```
(Cảnh khó nhất với AI – nếu khung U bị méo, bỏ chuyển động sản phẩm, đổi câu đầu thành "The camera slowly orbits around the still product".)

**c06 – cảnh kết**
```
Low-angle hero shot of the 3D-printed security camera, warm blurred background with soft bokeh. Very slow push-in toward the lens, cinematic, realistic product lighting. Keep the product shape, colors and proportions exactly as in the image. No text, no logos, no people, no hands.
```

## Khi đăng
- Ghi chú thích **"Video có sử dụng AI"** (Luật Trí tuệ nhân tạo 134/2025, hiệu lực 01/03/2026) và bật nhãn AI của TikTok/YouTube.
- Hình ảnh chỉ minh họa đúng tính năng thật (xem trực tiếp qua Wi-Fi, xoay/nghiêng, phát hiện chuyển động khi có firmware v0.3.0).
