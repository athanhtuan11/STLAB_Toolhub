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
