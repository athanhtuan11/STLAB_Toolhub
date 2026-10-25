# video-ai – tự dựng video ngắn từ clip tự quay (FilmCraft)

## Mục tiêu
Tuan đưa clip tự quay + vài dòng mong muốn → Claude phân tích, lập kế hoạch, FilmCraft dựng theo template
(kiểu CapCut) → dự án `.fcproj` chỉnh tiếp được + video xuất sẵn.

## Thư mục một dự án `projects/<ten-du-an>/` (KHÔNG lên git – clip riêng tư)
- `inbox/` clip gốc · `brief.md` mong muốn (mẫu: `projects/_mau-brief.md`) · `rieng-tu.txt` clip không trích ảnh
- `analysis/` (analyze.py): `tom-tat.md`, `<clip>/contact.jpg`, `transcript.fixed.json`, `info.json`
- `plan.json` (Claude viết) · `build/` (.fcproj, captions.srt, kiem-tra-*.png) · `out/` (.mp4 + .srt)

## Quy trình (skill `video-ai` hướng dẫn chi tiết)
1. `uv run python scripts/analyze.py projects/<ten>` – chép lời tiếng Việt trên máy (faster-whisper CPU,
   ~0,8× thời lượng clip), cắt cảnh, ảnh. Sửa tên riêng nghe sai: `tu-vung.txt`, `sua-loi.txt`.
2. Claude đọc `brief.md` + `analysis/tom-tat.md` + xem `contact.jpg` → viết `plan.json`.
3. `uv run python scripts/build.py projects/<ten>` – dựng trong FilmCraft (chạy nền), xuất video.
4. Claude xem `build/kiem-tra-*.png`, sửa plan nếu cần, dựng lại. Tuan mở `.fcproj` để chỉnh tay nếu muốn.

## Reel từ ẢNH CÓ SẴN của dự án – `scripts/make_reel.py` (2026-10-24, không cần clip quay)
- Kịch bản YAML đặt trong dự án: `maker/<project>/marketing/<ten>.yaml` (lên git); video ra `video-ai/projects/<ten>/out/`
  (KHÔNG lên git). Chạy: `uv run python scripts/make_reel.py ../maker/<project>/marketing/<ten>.yaml` (~2 phút / 27 s).
- Cảnh: `title` (câu mở đầu) · `step` (số bước to + tên + thanh tiến độ) · `end` (CTA nút vàng). `zoom` cho ảnh nhiều
  khoảng trắng. Màu/font: `studio/design/tokens.json` + Be Vietnam Pro (`studio/design/fonts/`).
- Chừa vùng an toàn Reels/TikTok: trên 160 px, dưới 420 px. Xuất 1080×1920 H.264 + AAC 48 kHz **im lặng, không nhạc**
  (tài khoản cá nhân → Tuan chọn nhạc trend trong app). Kèm `<ten>-contact.png` để duyệt bằng ảnh. Không tự đăng.
- Mẫu: `maker/pushrod-arm/marketing/reel-13-steps.yaml` (video #1 trong `docs/trend-content-ideas.md`).

- **Giọng đọc AI tiếng Việt (2026-10-25):** spec có `voice: "Mai Anh"` + cảnh có `say: "..."` → `scripts/tts_vi.py`
  (VieNeu-TTS, chạy trên máy, venv riêng – cài: docstring tts_vi.py) đọc; cảnh tự dài theo câu; ra thêm `<ten>.srt`.
  Cache trong `out/_<ten>-voice/` (sửa 1 câu chỉ đọc lại câu đó). Mẫu: `reel-13-steps-voice.yaml`. KHÔNG clone giọng người thật.

## Template (`templates/<id>/cau-hinh.yaml`)
- `reel-9x16`: TikTok/Reels/Shorts – khung dọc bám chủ thể, bỏ từ đệm + khoảng lặng > 0,35 s, phụ đề
  in cứng, chữ mở đầu/CTA, −14 LUFS. TODO: màu/logo/nhạc STLab.

## Sự thật đã kiểm chứng (2026-10-21, FilmCraft 0.9.0)
- Bản phát hành **không có Whisper** (`transcript.generate` không chạy) → chép lời ngoài, phụ đề tự tạo.
- `auto_reframe` chỉ dịch khung, phải phóng `motion` để phủ kín (build.py tự tính).
- `essentialSound.autoMatch` lệch ~3 LU sau khi cắt lặng → build.py đo EBU R128 trên bản dựng rồi chỉnh.
- Phụ đề chỉ có trong MP4 khi xuất với `burnCaptions`.

## Riêng tư
- Âm thanh/chép lời xử lý trên máy. Ảnh khung hình + chép lời được Claude đọc (gửi lên Claude).
- Clip có học sinh: cần đồng ý của phụ huynh; ghi tên clip vào `rieng-tu.txt` để không trích ảnh.
