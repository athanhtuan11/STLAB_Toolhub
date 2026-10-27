# Bước 0 – Giao diện: cyberbrick-arm

Làm TRƯỚC cơ khí (Tuan 2026-10-24). Mức **A** (robot có vỏ nhìn thấy). Hệ thiết kế: `studio/design/DESIGN.md`.

## Nguồn tham khảo (chỉ học, KHÔNG phân phối)
- "Robotic Arm CyberBrick" – tipflow, MakerWorld, **Standard Digital File License = chỉ dùng cá nhân**.
  File gốc: `community/makerworld-tipflow-cyberbrick-robotic-arm/` (git bỏ qua). Ảnh tham khảo:
  `design/reference/reference-board.png` (chỉ trên máy, không lên GitHub).
- → Bản STLab **vẽ lại từ đầu** bằng FreeCAD có tham số; giữ dáng tổng thể, không chép lưới STL của tác giả.
- Số đo đã học: `docs/research-notes/tipflow-robotic-arm-fits.md` (khe khớp quay 0,40 mm theo Ø: Ø5,068 trong
  Ø5,467 và Ø8,468 trong Ø8,868; lỗ vít servo Ø1,8; lỗ M2.5 Ø2,4). Cấu hình in tác giả (support theo chi tiết):
  `tools/model-study/study_3mf.py` → `summary.md` mục "Cau hinh in cua tac gia".

## Brief
- **Sản phẩm:** tay máy 3 khớp + kẹp 3 ngón, điều khiển bằng remote CyberBrick. Dùng ở STLab (Open Lab, lớp robot).
  Đối tượng học sinh: `TODO` (Tuan chọn cấp học).
- **Cảm giác:** gọn – chắc – dễ tháo lắp (học sinh tự ráp, nhìn thấy cơ cấu).
- **Cơ cấu (theo bản gốc):** đế xoay = motor 030 + hộp số CyberBrick (cổng M2) đi quanh vành răng trong cố định;
  vai/khuỷu = 2 servo 9g 180° có ly hợp (S1, S2); kẹp = servo 9g 360° (S3) quay trục vít, ăn bánh răng 3 ngón L/R/D
  (tác giả dặn khe quanh trục vít 0,5–1 mm).
- **Kích thước bao (bản gốc):** đế Ø70,6 mm, khung đế 74×74 mm; chiều cao/tầm với: `TODO` đo khi dựng lắp ráp.
- **Linh kiện bắt buộc:** motor 030 + hộp số, 2× servo 9g 180° ly hợp, 1× servo 9g 360° ly hợp, bộ thu CyberBrick,
  module công tắc nguồn (XH2.54), pin Li-ion 14500 7,4 V 800 mAh, vít M2.5×6 BHCS.
- **Nhựa:** Bambu PETG Basic (mặc định STLab). Màu (≤ 3 cuộn có thật): `TODO` – bản gốc trắng/xám/cam.

## An toàn (ghi vào ASSEMBLY.md)
- Pin Li-ion 7,4 V: không để chập 2 cực khi luồn dây qua lỗ vỏ; khoang pin không ép dây vào mép nhựa; không sạc khi
  máy đang chạy hay không có người trông.
- Servo có ly hợp nhưng motor đế 030 **không** có bảo vệ kẹt → khi đế bị chặn phải nhả cần L1 ngay (nóng motor).
- Ngón kẹp: lực nhỏ nhưng kẹp được ngón tay trẻ nhỏ – nhắc học sinh.

## 3 hướng để chọn (đánh đổi) – Claude khuyên **A**
| Hướng | Nội dung | Được | Mất |
|---|---|---|---|
| **A** – giữ dáng, làm lại có tham số | FreeCAD tham số, khe theo PETG Bambu + in coupon thử khe, khắc dấu lắp, in không/ít support | Sửa kích thước dễ, khe đúng máy STLab, nhanh nhất | Không thêm tính năng |
| B – A + ổ bi đế xoay | Thêm ổ bi (vd. 6705/6805 – `TODO` chọn theo kích thước) dưới mâm | Đế quay êm, ít lắc | Thêm linh kiện mua, đế cao hơn |
| C – A + trục kim loại các khớp | Trục thép/đinh Ø3 thay chốt nhựa ở khớp vai/khuỷu | Bền, ít mòn khi học sinh dùng nhiều | Thêm linh kiện, phải khoan/doa lỗ chuẩn |

## Đầu ra (duyệt bằng ảnh)
- Đã có: `reference/reference-board.png` (ảnh thật + 33 chi tiết gốc).
- Sau khi chọn hướng: dựng lắp ráp khung (khối chính) → `concepts/` (hông, đỉnh, 3/4) + `cmf.png` → `contact-sheet.png`.

## Quyết định
<!-- Tuan chọn: ngày | hướng A/B/C | màu | cấp học -->
