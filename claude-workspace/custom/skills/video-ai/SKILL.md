---
name: video-ai
description: Tu dung video ngan (TikTok/Reels/Shorts) cho STLab tu clip tu quay bang FilmCraft - phan tich clip (chep loi tieng Viet, canh, anh), lap ke hoach dung theo brief va template, dung + xuat video, tu kiem tra. Dung khi Tuan dua clip va noi muon dung video, cat clip, lam reel, them phu de.
---

# Video AI (STLab + FilmCraft)

> Tự viết: chưa có công cụ cộng đồng nào cho Windows + tiếng Việt + template STLab. Tham khảo kiến trúc
> `juan52878911/filmcraft-studio` (chỉ macOS). Lệnh FilmCraft: skill `filmcraft` (cộng đồng).

Thư mục làm việc: `D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/video-ai` (đọc `CLAUDE.md` ở đó trước).

## Các bước
1. **Dự án**: `projects/<ten>/inbox/` có clip. Chưa có `brief.md` → hỏi Tuan theo `projects/_brief-template.md`
   (tối thiểu: mục tiêu, nơi đăng, thời lượng, CTA). Clip có học sinh → hỏi có cần ghi vào `rieng-tu.txt`.
2. **Phân tích**: `uv run python scripts/analyze.py projects/<ten>` (chạy tại `video-ai/`).
   Đọc `analysis/tom-tat.md`; xem `analysis/<clip>/contact.jpg` (trừ clip riêng tư).
   Tên riêng sai lặp lại → thêm vào `corrections.txt`/`vocabulary.txt` rồi chạy lại.
3. **Kế hoạch** `plan.json` (cấu trúc ở đầu `scripts/build.py`):
   - Chọn đoạn theo **câu nói trọn vẹn** (mốc `tu`/`den` lấy từ tóm tắt, lề 0,1–0,2 s), đúng thứ tự kể.
   - Câu đầu phải "móc" người xem trong 3 s; bỏ đoạn lặp, nói vấp, ngoài lề; tổng thời lượng theo brief
     (cắt từ đệm + khoảng lặng sẽ ngắn thêm 20–35%).
   - `mo_dau` ≤ 5 từ, VIẾT HOA; `cuoi` = CTA trong brief. Không bịa thông tin không có trong clip/brief.
   - Trình bày kế hoạch ngắn gọn cho Tuan (đoạn nào, vì sao, thời lượng dự kiến) trước khi dựng, trừ khi
     Tuan bảo cứ làm.
4. **Dựng**: `uv run python scripts/build.py projects/<ten>`.
5. **Tự kiểm tra**: xem `build/kiem-tra-*.png` (khung có phủ kín? chủ thể trong khung? phụ đề đọc được,
   không che mặt? chữ mở đầu/CTA đúng?), đọc `build/captions.srt` (sai chính tả, tên riêng).
   Sửa `plan.json`/từ điển → dựng lại. Báo Tuan: đường dẫn `out/<ten>.mp4`, thời lượng, các điểm chưa chắc.

## Giới hạn hiện tại
- `auto_reframe` của FilmCraft bám "chủ thể nổi bật" – với cảnh nhiều người cần Tuan kiểm tra.
- Chưa có nhạc nền (template `am_thanh.nhac_nen` = TODO) và màu/logo STLab.
- Không dùng `transcript.generate` của FilmCraft (bản phát hành không có Whisper).
