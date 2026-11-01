# Git hooks STLab

Hook `pre-commit` tự viết (không dùng framework `pre-commit`) để chặn lỡ commit file không được lên git và lỗi Python cơ bản.

## Cài

Chạy ở gốc repo (`D:\04_Stlab\04_STLAB_Toolhub`):

```sh
git config core.hooksPath claude-workspace/tools/git-hooks
```

## Luật chặn

- `claude-workspace/maker/**/*.FCStd`: file model FreeCAD của dự án (FCStd ở nơi khác được phép).
- File tên `.env` hoặc bắt đầu bằng `.env.` ở bất kỳ đâu.
- `claude-workspace/community/<thư mục con>/...`: bản clone nguồn cộng đồng (trừ `community/reports/**`; file nằm thẳng trong `community/` như `pins.tsv`, `links.tsv`, `update-community.sh` được phép).
- Media trong `claude-workspace/maker/**`: png, jpg, jpeg, gif, webp, mp4, mov, mkv, mp3, wav, m4a, pdf (svg được phép).
- File lớn hơn 2 MiB (2 097 152 byte).
- File `.py`: lỗi cú pháp và lỗi nghiêm trọng theo `ruff check --select E9,F63,F7,F82` (không có `ruff` trên PATH thì bỏ qua, chỉ cảnh báo).
- Bí mật trong file văn bản: token dạng `sk-...`, token GitHub dạng `ghp_...`/`gho_...`, khóa AWS dạng `AKIA...`, khóa riêng (chuỗi bắt đầu bằng `-----BEGIN ... PRIVATE KEY-----`). Hook chỉ in tên file, không in chuỗi bí mật.

Hook xét file **đã stage** và đọc nội dung từ index. Chạy `python tools/git-hooks/pre_commit.py --all` để xét toàn bộ file đã theo dõi (dùng cho CI).

Khi có vi phạm, hook in `CHAN <luật>: <đường dẫn>` rồi dừng commit.
