# Bước 0 – Giao diện: drum-pad

Tuan 2026-11-17: tận dụng bo **ESP32-A1S Audio Kit** (rảnh sau khi Cú Bông chuyển S3) làm **bộ trống STEAM** – hướng B.
Chốt: **tiểu học lớp 2–5**, **4 pad gõ**, **âm mẫu trống thật** (không synth). Thiết kế mới của STLab.
Tham khảo (chỉ đọc, không chép mã – không license): `community/jakubthedeveloper-rudebox` (bắt nhịp gõ qua ES8388 LINE IN, mạch bảo vệ pad).
Hệ thiết kế: `studio/design/DESIGN.md`. Chưa chọn dáng thì chưa làm cơ khí / firmware thật.

## Brief
- **Sản phẩm:** hộp trống để bàn, 4 mặt pad gõ bằng tay hoặc dùi ngắn; mỗi pad phát 1 tiếng trống thật (kick, snare, hi-hat, tom),
  gõ mạnh → to hơn (lực gõ). Có loa trong hộp + cổng tai nghe của bo. LED dưới mỗi pad sáng theo nhịp.
- **Cho ai:** học sinh **lớp 2–5** (7–11 tuổi), nhóm 2–3 bé / 1 bộ, giáo viên STLab. Buổi 30 phút.
- **Học gì (STEAM):** âm thanh là rung động (pad piezo biến rung thành điện), nhịp – phách – tiết tấu (đếm 1-2-3-4),
  chơi theo mẫu nhịp, ghép nhóm thành "ban nhạc". Bản sau: tự ghi nhịp và phát lại (sequencer đơn giản).
- **Cảm giác:** vui – chắc chắn (chịu gõ mạnh) – nhìn là biết gõ chỗ nào.
- **Kích thước bao:** để bàn ≤ 300 × 220 × 80 mm (đặt vừa bàn học). Pad ≥ Ø70 mm (tay bé gõ trúng). In trên Bambu A1 (bàn 256 × 256 mm)
  → hộp chia nhiều part ráp lại.
- **Linh kiện (chi tiết ở giai đoạn 1):** ESP32-A1S Audio Kit V2.2 (82 × 73 mm theo datasheet Ai-Thinker; độ dày, lỗ vít `TODO` đo bo thật),
  4 cảm biến piezo Ø27/Ø35 dưới mặt pad (`TODO` mã) + mạch bảo vệ đầu vào, loa 4 Ω 3 W Ø52 (loại Tuan đã có, cao 26 mm),
  4 LED, nút chọn bộ tiếng / âm lượng = 6 nút có sẵn trên bo (đưa ra mặt hộp bằng nắp nút). Nguồn: USB 5 V (`TODO` có pin không).
- **Chân cắm (rủi ro, kiểm ở giai đoạn 1):** 2 pad qua ES8388 LINE IN trái/phải (lực gõ chính xác như RudeBox; mic trên bo nối chung
  đường này – có thể phải tháo mic); 2 pad còn lại qua ADC1 của ESP32 (GPIO39/34?) – `TODO` kiểm chân trống trên A1S.
- **Nhựa:** Bambu PETG Basic @BBL A1, hạn chế AMS → part đơn sắc ráp lại. Mặt pad cần lớp đệm mềm (cao su/EVA/TPU – `TODO` chọn)
  để gõ êm tay và truyền rung tới piezo. Không vẽ support vào STL.

## An toàn (trẻ 7–11)
- Điện 5 V USB, không pin Li-ion ở v1. Âm lượng trần trong firmware (tai trẻ). Vỏ kín, vít giấu, không cạnh sắc, không chi tiết nhỏ rời.
- Dùi gõ (nếu có): đầu tròn, ngắn, mềm.

## Cần ra ở bước 0
1. 3 dáng hộp trống (render, cùng góc + có tay bé để so tỉ lệ) – khác nhau rõ về bố cục 4 pad và chỗ loa.
2. Bảng CMF (màu theo hệ thiết kế STLab, part đơn sắc).
3. `contact-sheet.png` để Tuan chọn.
