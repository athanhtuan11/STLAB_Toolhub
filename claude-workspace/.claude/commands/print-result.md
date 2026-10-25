---
description: Ghi kết quả 1 lần in thật (pass/fail) vào README dự án + harness-lab/inbox.md – vòng học từ bản in (GĐ E)
argument-hint: "<project> <plate> pass|fail [mô tả lỗi]"
---

Ghi kết quả in thật – nguồn dữ liệu để chỉnh ngưỡng kiểm tra (`docs/cad-standard-workflow.md` GĐ E).

1. Từ `$ARGUMENTS` lấy: dự án (`maker/<project>/`), bàn in (tên trong `print/print.yaml`, vd. `P3_Forearm_Housings`
   hoặc `P3`), `pass` hoặc `fail`, mô tả. Thiếu thì hỏi Tuan (1 câu, gộp mọi chỗ thiếu). Có ảnh bản in thì hỏi đường dẫn
   (chép vào `maker/<project>/print/photos/YYYY-MM-DD_<plate>.jpg`).
2. Thêm 1 dòng vào mục `## Lịch sử in` của `maker/<project>/README.md` (xóa dòng "(chưa in)" nếu còn):
   `- YYYY-MM-DD | <plate> | PASS/FAIL | <mô tả> | <ảnh>`
3. Nếu `fail`: phân loại và thêm vào `harness-lab/inbox.md` (định dạng của file đó), mục "Đề xuất" chọn 1:
   - lỗi kích thước/lắp không vừa → `tools/robotics-cad/thresholds.yaml` (min_clearance_mm, min_wall_mm…)
   - lơ lửng/support/cong vênh/bong bàn → `print/print.yaml` (profile bàn) hoặc thiết kế
   - lỗi bộ kiểm không bắt được → bước kiểm mới trong `check.py`/`slice.py`
   KHÔNG tự sửa ngưỡng/quy tắc: chỉ đề xuất. Lỗi cùng loại lặp ≥ 2 lần (đếm trong inbox) thì nói rõ để Tuan duyệt sửa.
4. Commit + push README + inbox + ảnh (theo memory "tự lưu + tự push").
