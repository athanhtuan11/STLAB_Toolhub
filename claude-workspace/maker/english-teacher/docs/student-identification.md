# Nhận ra từng bé để cá nhân hóa bài học – phương án (2026-11-06)

Mục tiêu: cô Lily (Cú Bông) dần nhận ra từng học sinh rồi dạy đúng trình độ của bé đó.
Hiện đang làm bước 1: biệt danh con vật, tiến độ bài học lưu tại máy lab.

## Khuyến nghị

- **Làm ngay: bước 1** (biệt danh con vật).
- **Bước 2: thẻ NFC/RFID** mỗi bé, không sinh trắc học.
- **Bước 3 (tùy chọn, sau cùng): nhận diện giọng tại máy.** Chỉ làm khi đã có đồng ý của phụ huynh, đã đổi nhà cung cấp AI và đã đo độ chính xác trên chính lớp học.

## So sánh phương án

| Cách làm | Ưu | Nhược | Pháp lý | Công sức |
|---|---|---|---|---|
| **1. Biệt danh con vật** (đang làm): bé nói "Con là bạn Thỏ", tiến độ theo biệt danh | Không có dữ liệu nhạy cảm; làm được ngay | Trùng hoặc nhầm tên; bé khác có thể nói hộ | Không thuộc dữ liệu sinh trắc học | Rất thấp |
| **2. Thẻ NFC/RFID** mỗi bé: chạm thẻ vào Cú Bông khi bắt đầu | Ít nhầm; không dùng giọng nói | Thêm đầu đọc và thẻ; cần chỗ trên vỏ | Không thuộc dữ liệu sinh trắc học | Trung bình. Đầu đọc I2C có thể chung bus với codec Audio Kit (TODO: kiểm địa chỉ I2C và chân trống trước khi mua) |
| **3. Nhận diện giọng tại máy**: lưu embedding trên máy chủ trường, dùng kèm biệt danh/thẻ để sửa nhầm | Tự nhiên, không cần cầm thẻ | Độ chính xác với trẻ 2–5 tuổi chưa rõ; nhạy với ồn và micro | Dữ liệu nhạy cảm (NĐ 13/2023). Cần văn bản đồng ý của cha mẹ, nút xóa | Cao: tích hợp, đo tại phòng học, làm chức năng xóa |

## Căn cứ pháp lý

- **Dữ liệu nhạy cảm:** Điều 2(1) coi "âm thanh" là dữ liệu cá nhân khi giúp xác định một người. Điều 2(4)(đ): dữ liệu sinh trắc học là dữ liệu nhạy cảm. Mẫu giọng hoặc embedding dùng nhận diện bé thuộc loại này.
- **Trẻ em:** Điều 20: phải vì lợi ích tốt nhất của trẻ. Dưới 7 tuổi cần đồng ý của cha, mẹ hoặc người giám hộ; từ 7 tuổi cần thêm sự đồng ý của chính trẻ.
- **Điều kiện đồng ý:** Điều 11: tự nguyện, biết loại dữ liệu, mục đích và bên xử lý. Khi cha mẹ rút đồng ý phải xóa dữ liệu.
- **Luật mới:** Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15, hiệu lực 01/01/2026. TODO: đọc toàn văn trước khi thu mẫu giọng.
- **Nhà cung cấp AI:** điều khoản Gemini API (hiệu lực 23/3/2026) cấm dịch vụ hướng tới người dưới 18 tuổi. Mọi thử nghiệm với bé thật phải chuyển sang nhà cung cấp khác trước (Azure OpenAI, OpenAI hoặc LLM chạy tại máy).

## Khả năng kỹ thuật (chạy CPU tại máy)

| Thư viện / mô hình | License | Ghi chú |
|---|---|---|
| 3D-Speaker CAM++/ERes2Net | Apache-2.0 | https://github.com/modelscope/3D-Speaker |
| WeSpeaker (ONNX) | Apache-2.0; trọng số VoxCeleb CC BY 4.0 | https://github.com/wenet-e2e/wespeaker |
| sherpa-onnx speaker embedding | Apache-2.0; nhẹ, hợp CPU | https://github.com/k2-fsa/sherpa-onnx |
| SpeechBrain ECAPA-TDNN | Apache-2.0; nặng hơn do PyTorch | Kiểm license trọng số riêng |
| Máy chủ xiaozhi | Đã có mục voiceprint, chưa bật | https://github.com/xinnan-tech/xiaozhi-esp32-server |

**Độ chính xác với trẻ nhỏ:** chưa có nghiên cứu đo EER cho trẻ 2–5 tuổi với câu 1–3 giây. Safavi và cộng sự (WoCCI 2014) thấy EER ở trẻ em gần gấp 4 lần người lớn, với mô hình GMM cũ: https://www.isca-archive.org/wocci_2014/safavi14_wocci.html.
→ Không cam kết độ chính xác. Chỉ dùng làm tín hiệu phụ và phải đo trên chính trẻ, micro và phòng học của lab.

## Việc Tuan cần quyết

1. **Nhà cung cấp AI cho bé thật:** Azure OpenAI, OpenAI hay LLM tại máy.
2. **Có làm thẻ NFC không:** nếu có, kiểm địa chỉ I2C và chân trống trước khi mua linh kiện.
3. **Có thử nhận diện giọng không:** nếu có, cần mẫu đơn đồng ý của phụ huynh (TODO: soạn mẫu).

## Cập nhật 2026-11-08: hồ sơ từng bé + ESP32-CAM

### Đã chạy

- **Hồ sơ theo biệt danh:** 19 con vật + "kay" cho bé Kay (con Tuan, Tuan đồng ý).
- **Nhớ biệt danh theo mã thiết bị** (`server/data/devices.json`): thiết bị đã quen thì chào thẳng tên.
- **Nhận giọng tại máy** (sherpa-onnx CAM++, https://github.com/k2-fsa/sherpa-onnx): chỉ lưu đặc trưng giọng, có lệnh xóa, cần `consent.json`.
- **Lộ trình tuần theo độ tuổi:** chỉnh bằng `--set-age`.

### So sánh cách nhận ra bé

| Cách làm | Ưu | Nhược | Pháp lý | Công sức |
|---|---|---|---|---|
| **Biệt danh lời** (đã làm) | Không cần thiết bị thêm; làm được ngay | Trùng hoặc nhầm tên | Không thuộc dữ liệu sinh trắc học | Rất thấp |
| **Nhớ theo thiết bị** (đã làm) | Thiết bị quen thì chào thẳng tên | Gắn với thiết bị, không gắn với bé (TODO: kiểm khi nhiều bé dùng chung) | Không thuộc dữ liệu sinh trắc học | Thấp (đã chạy) |
| **Giọng tại máy** (đã chạy) | Tự nhiên, không cần cầm thẻ | Chưa đo với trẻ 2–5 tuổi; nhạy với ồn và micro | Dữ liệu sinh trắc học; cần đồng ý cha mẹ và xóa được | Đã làm; cần đo tại lớp |
| **Thẻ NFC / thẻ hình con vật** | Ít nhầm; không dùng giọng nói | Cần thẻ và đầu đọc | Không thuộc dữ liệu sinh trắc học | Trung bình (xem bảng phương án trên) |
| **Camera nhận diện mặt trên bo** (ESP-WHO, https://github.com/espressif/esp-who) | Chạy ngay trên ESP32-S3, có ví dụ sẵn | Repo không công bố độ chính xác hay số người tối đa. ESP-DL đo bước nhận diện ~287 ms (8-bit) / ~554 ms (16-bit) trên S3 (https://docs.espressif.com/projects/esp-dl/en/release-v1.1/esp32s3/performance.html). OV3660 + bộ nhớ: phải thử trên bo | Ảnh mặt là dữ liệu sinh trắc học nhạy cảm; cần đồng ý cha mẹ | TODO: 1 buổi dò khả thi |
| **Camera gửi ảnh về máy chủ nhận diện CPU** | Có nhiều model chạy CPU để chọn | OpenCV YuNet + SFace (Apache-2.0, https://github.com/opencv/opencv_zoo) cần kiểm license từng model. InsightFace: trọng số pretrained chỉ cho nghiên cứu phi thương mại (https://github.com/deepinsight/insightface/blob/master/server/LICENSING.md). face_recognition/dlib: 99,38% là trên LFW người lớn | Như trên; ảnh rời bo gửi sang máy chủ | Cao hơn |

**Mặt trẻ nhỏ:** nghiên cứu YFA (https://arxiv.org/abs/2204.01760) đo MagFace TAR 98,3% khi cách nhau 6 tháng và 94,9% khi cách 36 tháng (FAR 0,1%). Nhóm 3–5 tuổi giảm rõ khi khoảng cách thời gian tăng. Đây không phải cam kết cho camera lớp học, nên phải cập nhật ảnh mẫu định kỳ.

**Lợi ích thêm của camera:** cô "thấy" bé làm động tác. Hiện cô không có camera nên không khen được việc bé làm. Nhưng đây là ghi hình trẻ, rủi ro riêng tư cao hơn hẳn giọng nói.

### Pháp lý camera

- Ảnh mặt dùng để nhận diện là dữ liệu sinh trắc học nhạy cảm: NĐ 13/2023 và Luật 91/2025/QH15, hiệu lực 01/01/2026 (https://congbao.chinhphu.vn/van-ban/luat-so-91-2025-qh15-45578/57730.htm).
- Trẻ em cần: đồng ý của cha mẹ, thông báo mục đích, giới hạn người truy cập, xóa khi rút đồng ý.
- Camera trong lớp: chưa xác minh hướng dẫn chính thức. TODO.

### Khuyến nghị

1. **Nhà chỉ có bé Kay:** hiện tại đủ (nhớ theo thiết bị + giọng).
2. **Lớp nhiều bé:** thẻ NFC/thẻ hình con vật là cách CHÍNH. Giọng làm xác nhận phụ. Hỏi lại khi không chắc.
3. **Camera nhận diện mặt:** chỉ thử sau, khi làm bản ESP32-S3 (có thể tích hợp camera + AEC). Cần đồng ý phụ huynh bằng văn bản, xử lý tại máy, không lưu ảnh, chỉ lưu đặc trưng. Ưu tiên dùng camera để "thấy động tác" hơn là định danh.

### Việc Tuan cần quyết

1. Có làm thẻ NFC/thẻ hình cho lớp không.
2. Có muốn thử ESP-WHO trên bo ESP32-S3-CAM (1 buổi dò khả thi) không.
