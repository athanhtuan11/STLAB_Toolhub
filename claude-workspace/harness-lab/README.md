# harness-lab – cải thiện cách làm việc với Claude từ lỗi thực tế

Lấy ý tưởng từ Harness² (Google Research): không đổi model, chỉ sửa "vỏ" (CLAUDE.md, memory, skill, hook)
dựa trên lỗi gặp thật.

**Phạm vi hiện tại (Tuan chốt 2026-10-23): chỉ GĐ0–GĐ1.**
- GĐ0: sổ ghi lỗi `inbox.md` + lệnh `/lesson`.
- GĐ1: dùng hằng ngày, gom lỗi thực tế.
- CHƯA làm: bộ task, chấm A/B, tự động hoá song song.

## Cách dùng
1. Cuối phiên (hoặc ngay khi gặp lỗi), gõ `/lesson` (có thể kèm mô tả ngắn).
   Claude ghi 1 mục vào `inbox.md`: chuyện gì xảy ra, bài học, đề xuất nơi sửa.
2. Hàng tuần Tuan đọc `inbox.md`, chọn mục nào đưa vào đâu:
   - `CLAUDE.md` (quy tắc chung), memory (sự kiện/đường dẫn), `EXPERIENCE.md` của skill (mẹo kỹ thuật),
     hook (quy tắc bắt buộc, an toàn).
3. Mục đã xử lý: đổi `[ ]` thành `[x]` và ghi đã đưa vào đâu. Không xoá.
4. **In xong một bàn** (dự án CAD), gõ `/print-result <project> <plate> pass|fail [mô tả]` (2026-10-23, GĐ E của
   `docs/cad-standard-workflow.md`): ghi vào "Lịch sử in" của README dự án; lỗi thì thêm mục vào `inbox.md` kèm đề xuất
   chỉnh ngưỡng (`thresholds.yaml`), bàn in (`print/print.yaml`) hay bước kiểm. Lỗi cùng loại lặp ≥ 2 lần → Tuan duyệt sửa.

## Quy tắc
- Claude chỉ **ghi và đề xuất**. Sửa CLAUDE.md / skill / hook phải được Tuan duyệt.
- Mỗi mục ngắn: 1 dòng sự việc, 1 dòng bài học, 1 dòng đề xuất nơi sửa.
- Không ghi mật khẩu, token, thông tin học sinh.
