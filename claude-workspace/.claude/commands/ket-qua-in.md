---
description: Ghi kết quả 1 lần in thật (đạt/lỗi) vào README dự án + harness-lab/inbox.md – vòng học từ bản in (GĐ E)
argument-hint: "<du-an> <ban> dat|loi [mô tả lỗi]"
---

Ghi kết quả in thật – nguồn dữ liệu để chỉnh ngưỡng kiểm tra (`docs/quy-trinh-chuan-hoa-cad.md` GĐ E).

1. Từ `$ARGUMENTS` lấy: dự án (`maker/<du-an>/`), bàn in (vd. `P3`), `dat` hoặc `loi`, mô tả. Thiếu thì hỏi Tuan
   (1 câu, gộp mọi chỗ thiếu). Có ảnh bản in thì hỏi đường dẫn ảnh (chép vào `maker/<du-an>/anh/in-YYYY-MM-DD-<ban>.jpg`).
2. Thêm 1 dòng vào mục `## Lịch sử in` của `maker/<du-an>/README.md` (xóa dòng "(chưa in)" nếu còn):
   `- YYYY-MM-DD | <ban> | ĐẠT/LỖI | <mô tả> | <ảnh>`
3. Nếu `loi`: phân loại và thêm vào `harness-lab/inbox.md` (định dạng của file đó), mục "Đề xuất" chọn 1:
   - lỗi kích thước/lắp không vừa → `nguong-kiem-tra.yaml` (khe_ho_min_mm, do_day_thanh_min_mm…)
   - lơ lửng/support/cong vênh/bong bàn → `ban-in.yaml` (profile bàn) hoặc thiết kế
   - lỗi bộ kiểm không bắt được → bước kiểm mới trong `kiem-tra.py`/`cat-lop.py`
   KHÔNG tự sửa ngưỡng/quy tắc: chỉ đề xuất. Lỗi cùng loại lặp ≥ 2 lần (đếm trong inbox) thì nói rõ để Tuan duyệt sửa.
4. Commit + push README + inbox (theo memory "tự lưu + tự push").
