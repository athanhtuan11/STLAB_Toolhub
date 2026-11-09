# Bước 0 – Giao diện: card-coding-robot (robot lập trình bằng thẻ)

Tuan 2026-11-09: "đồng ý. chạy từ A" – robot lập trình không màn hình kiểu Plobot/Cubetto, **thiết kế mới của STLab**
(không chép hình dáng, tên, nhân vật của sản phẩm nào). Mức **A** (có vỏ nhìn thấy). Hệ thiết kế: `studio/design/DESIGN.md`.
Chưa chọn concept thì chưa dựng cơ khí. CAD = **SolidCraft** (mẫu `maker/esp32-s3-cam/solidcraft/build_cam_d.py`).

## Brief
- **Sản phẩm:** robot nhỏ đi trên thảm ô vuông. Bé xếp thẻ lệnh thành chuỗi, quẹt từng thẻ qua lưng robot (robot kêu
  + đọc tên lệnh song ngữ Việt–Anh), bấm nút **Chạy** → robot đi đúng chuỗi. Dạy tư duy tuần tự, lặp, gỡ lỗi – không màn hình.
- **Cho ai:** trẻ **4–7 tuổi** (mầm non lớn, lớp 1–2), nhóm 2–4 bé + 1 giáo viên/phụ huynh. Dùng ở lớp STLab, mầm non, nhà.
- **Cảm giác:** dễ thương – chắc tay – "nói chuyện được".
- **Kích thước bao (Claude chốt):** robot ≤ 120 × 120 × 100 mm (nằm gọn trong ô thảm **150 × 150 mm**, quay tại chỗ không
  lấn ô). Thẻ lệnh ~ 60 × 60 mm (bé 4 tuổi cầm chắc). Thảm 6 × 6 ô = 900 × 900 mm.
- **Linh kiện dự kiến (giai đoạn 1 chốt + thêm thư viện Toolhub):**
  - MCU: `esp32-doit-devkit-v1` (có trong thư viện; STLab dùng ESP32-D quen).
  - Đọc thẻ: RC522 13,56 MHz (SPI) + thẻ/sticker NTAG213 – chỉ đọc UID. `TODO` thêm thư viện, đo module thật.
  - Truyền động: **2 × 28BYJ-48 5 V + ULN2003** (khuyến nghị) – đi đúng 1 ô / quay đúng 90° không cần encoder, chậm = an
    toàn cho bé, rẻ. Đánh đổi: chậm, mô-men nhỏ (thảm phẳng thì đủ – `TODO` đo). Phương án B: N20 có encoder (nhanh hơn,
    phải tự dò bước). `TODO` thêm thư viện.
  - Âm thanh: MAX98357A I2S + loa nhỏ, câu đọc lưu flash (TTS VieNeu đã có). `TODO` chọn loa, đo.
  - Hiển thị: 1–2 LED WS2812 làm "mắt"/trạng thái; nút Chạy to (≥ 25 mm) + nút Xóa.
  - Nguồn: **4 × AA NiMH (4,8 V) hộp pin khóa vít** – khuyến nghị cho đồ chơi trẻ 4–7. Đánh đổi: chạy ngắn hơn 18650,
    nặng hơn; đổi lại không có Li-ion trong tay bé. `TODO` kiểm ổn áp 3,3 V khi pin yếu.
- **Nhựa:** Bambu PETG Basic @BBL A1. Hạn chế AMS → nhiều màu = part đơn sắc ráp lại. In không vẽ support vào STL.

## Bộ thẻ lệnh (v1)
Tiến · Lùi · Rẽ trái · Rẽ phải · Lặp ×2 · Lặp ×3 · Kết thúc lặp · Nhảy múa/âm thanh · (Chạy và Xóa là nút trên robot).
Thẻ = tấm in 3D có biểu tượng nổi (bé mù chữ vẫn đọc được bằng hình + màu theo nhóm) + sticker NTAG213 ép giữa 2 lớp
(dừng in ở lớp, nhét sticker). Phương án rẻ: thẻ giấy ép plastic dán sticker.
Theo `docs/research-notes/education/card-coding-robot-lessons.md` (2026-11-09): bé 4 tuổi chuỗi 2–3 thẻ, chưa chắc trái/phải;
5 tuổi chuỗi 3–5; 6–7 tuổi 5–8 (giả thuyết, cần thử thật). → Gói **Mầm** (4–5 tuổi): bỏ cặp Lặp/Kết thúc lặp, dùng 1 thẻ
"Lặp lại lệnh trước" (đánh đổi: ít diễn đạt); gói **Mở rộng** (6–7 tuổi) giữ đủ 8 thẻ. Mũi tên trên thẻ vẽ theo hướng robot.

## 3 hướng concept (Tuan chọn bằng ảnh)
| | A – Bọ rùa | B – Khối vuông mặt cười | C – Cú con (họ hàng Cú Bông) |
|---|---|---|---|
| Dáng | Vòm tròn thấp, bánh giấu dưới vòm, khe quẹt thẻ ở lưng | Khối vuông bo tròn, mặt LED phía trước, nắp trên quẹt thẻ | Thân trứng đứng, mắt to LED, cánh = 2 nút |
| Hợp với | Bé nhỏ nhất (không kẹp tay, khó lật) | Thảm ô vuông – hướng mặt rõ, dễ hiểu "rẽ trái" | Cùng thương hiệu STLab kids với Cú Bông, kể chuyện |
| Đổi lại | Khó thấy hướng mặt → cần mắt/mũi rõ | Dễ giống sản phẩm thương mại có sẵn → phải làm khác hẳn | Cao → dễ lật khi quay, khó giấu pin thấp |

**Khuyến nghị: A – Bọ rùa** (trọng tâm thấp, bánh giấu = an toàn ngón tay, vòm in nhanh). Mắt + hoa văn bọ rùa cho hướng rõ.

## An toàn trẻ 4–7 (ghi vào ASSEMBLY.md)
- Không chi tiết nhỏ tháo rời được (thẻ, nắp, bánh) – thẻ ≥ 60 mm; vít không lộ. Kiểm theo ống thử chi tiết nhỏ (`TODO`
  tra tiêu chuẩn đồ chơi TCVN 6238 / EN 71-1 trước khi bán).
- Hộp pin phải mở bằng tua vít; NiMH, không Li-ion. Không có mép sắc, khe kẹp ngón tay ở bánh (bánh nằm trong vòm).
- Robot chậm (28BYJ-48), nhẹ; không có nhiệt đáng kể (`TODO` đo ULN2003 + motor khi chạy liên tục).

## Đầu ra bước 0 (ảnh – Tuan duyệt)
- `concepts/` – 3 concept: bóng hông, bóng đỉnh, phối cảnh 3/4, đặt trên ô thảm 150 mm, kèm bàn tay trẻ 5 tuổi làm thước.
- Mockup bộ thẻ lệnh (8 thẻ) + 1 ô thảm.
- `cmf.png`, `contact-sheet.png`.

## Quyết định
<!-- Tuan chọn: ngày | concept | ghi chú → chép 1 dòng vào README "Lịch sử sửa" -->

## Ghi chú thiết kế
- Bước 0 dựng bằng Blender (`design/make_concepts.py`): ảnh trong `design/concepts/`, `design/cmf.png`, `design/contact-sheet.png`. Khối bên trong chỉ là ước lượng (hộp pin 62×58×16 chưa đo).
- Cả 3 concept cùng bố cục đáy: pin phía sau, 2 motor 28BYJ-48 + bánh Ø40 phía trước; mỗi concept dùng 3 màu + vàng nhấn (Bambu PETG Basic, TODO xác nhận tên màu).
