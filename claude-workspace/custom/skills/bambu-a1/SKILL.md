---
name: bambu-a1
description: Ho tro in 3D tren may Bambu Lab A1 - kiem tra model truoc khi slice, chon vat lieu, xu ly loi in. Chi tu van va kiem tra file, khong dieu khien may in.
---

# In 3D – Bambu Lab A1

> Tự viết vì không có MCP/skill cộng đồng nào đạt yêu cầu (21/10/2026):
> `schwarztim/bambu-mcp` dùng khóa trích xuất từ Bambu Connect để vượt xác thực firmware,
> các repo khác không hỗ trợ A1 hoặc không có license. Skill này **không chạy lệnh**
> và không kết nối máy in.

## Thông số đã biết
- Vùng in: 256 × 256 × 256 mm, kiểu bàn trượt trục Y, khung hở (không buồng kín).
- Slicer: Bambu Studio (hoặc OrcaSlicer). Ưu tiên profile chính hãng của từng loại nhựa.
- **Mặc định: đầu phun 0,4 mm** (thép không gỉ, máy "Bambu Lab A1 0.4 nozzle") – Tuan chốt 2026-10-21.
  Mọi tính toán (độ dày thành, khe hở, chữ nổi) dùng 0,4 mm trừ khi Tuan nói đang lắp đầu khác.
- Process mặc định "0.20mm Standard @BBL A1" (profile Bambu Studio 02.07.00.07, đọc từ
  `C:\Program Files\Bambu Studio\resources\profiles\BBL\process\`, kế thừa `fdm_process_common`):

  | Thông số | Giá trị |
  |---|---|
  | Độ cao lớp / lớp đầu | 0,20 mm / 0,20 mm |
  | Độ rộng đường in (chung, tường ngoài) | 0,42 mm |
  | Tường trong / infill | 0,45 mm |
  | Lớp đầu | 0,50 mm |
  | Số vòng tường | 2 |
  | Mặt trên / dưới | 5 lớp (≥ 1,0 mm) / 3 lớp |
  | Infill | 15 %, grid |
  | Bù chân voi (elephant foot) | 0,075 mm |
  | Bù lỗ / bù biên XY | 0 / 0 mm |
  | Support | tắt; ngưỡng góc 30° |
- TODO: có AMS lite không.

## Kiểm tra trước khi slice
1. Đơn vị **mm**; model nằm gọn trong 256 × 256 × 256 mm, có khoảng hở mép bàn.
2. Mesh kín (manifold), độ dày thành ≥ 2 × độ rộng đường in = **≥ 0,84 mm** với đầu 0,4 mm
   (2 vòng tường ≈ 0,87 mm; thành chịu lực nên là bội số độ rộng đường, vd. 1,2–1,6 mm). Chữ nổi/khắc, gân: ≥ 0,4 mm.
3. Mặt đáy phẳng, đủ diện tích bám; chi tiết cao và mảnh dễ rung vì bàn trượt Y.
4. Phần nhô > 45° cần support, hoặc xoay model.
5. Lắp ghép: chừa dung sai, ghi rõ giá trị và để `TODO` nếu chưa in thử.

## Vật liệu
- PLA, PETG, TPU: phù hợp.
- ABS/ASA: không khuyến nghị (khung hở, dễ cong vênh, có mùi). Nếu vẫn in thì cần thông gió.
- Nhựa sợi carbon/thủy tinh: cần đầu phun thép cứng.
- Nhiệt độ: theo profile và nhãn cuộn nhựa, **không tự đoán**.

## Xử lý lỗi in
Hỏi đủ ba thông tin trước khi kết luận: ảnh lỗi, vật liệu/profile, lớp xảy ra lỗi.
Sau đó liệt kê nguyên nhân theo thứ tự khả năng và cách thử cho từng nguyên nhân.
