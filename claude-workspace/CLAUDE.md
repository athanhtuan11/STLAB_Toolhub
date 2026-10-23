# claude-workspace – workspace Claude Code của STLab

Cấu trúc theo mẫu cộng đồng (shanraisshan/claude-code-best-practice): quy ước chung đặt ở
file này; mỗi dự án con có CLAUDE.md riêng và tự nạp file này theo cây thư mục cha.

## Cấu trúc
- `community/`: repo cộng đồng đã clone, **detached ở điểm ghim**. Chỉ đọc, KHÔNG sửa.
  - `pins.tsv`: điểm ghim; `links.tsv`: skill/agent nào liên kết vào đâu.
  - `update-community.sh`: kiểm tra, áp dụng, rollback (xem `docs/COMMUNITY.md`).
- `custom/skills/`: skill tự viết (chỉ khi không có nguồn cộng đồng phù hợp, có ghi lý do).
- `studio/`: giao diện web **STLAB Toolhub** (Flask, `.flaskenv`) + mở FreeCAD/Blender/LightCraft/PhotoCraft
  kèm MCP (file .bat). Xem `studio/CLAUDE.md`. Thêm tính năng mới thì thêm trang vào Toolhub.
- `video-ai/`: tự dựng video ngắn từ clip tự quay bằng FilmCraft (phân tích → plan → dựng), xem `video-ai/CLAUDE.md`.
- `stlab/`: giáo án, báo cáo phụ huynh.
- `maker/`: các dự án maker (mỗi thư mục là một dự án).
- `docs/COMMUNITY.md`: bảng quản lý nguồn cộng đồng.

## Một nguồn duy nhất cho skill
- Skill chỉ nằm trong workspace (`custom/skills/`, `community/...`); mọi nơi khác là **symlink** theo `links.tsv`.
- Skill dùng chung → `~/.claude/skills/` (Claude Code + tab **Code** của Claude Desktop đều đọc).
  Không liên kết cùng một skill ở cả cấp dự án và cấp dùng chung (bị trùng tên).
- Claude Desktop làm việc với FreeCAD/Blender… → dùng tab **Code**. Tab Chat/Cowork không đọc skill trên máy.
- **Không tải skill lên tài khoản claude.ai** (sẽ thành bản sao thứ hai, tự đồng bộ xuống `~/.claude/skills/synced/`).

## Quy tắc với nguồn cộng đồng
- Muốn dùng skill/agent mới: thêm dòng vào `community/links.tsv` rồi chạy
  `bash community/update-community.sh link`. Không copy để sửa trực tiếp.
- Cần tùy biến thì tạo file riêng trong `custom/`; không đè lên bản gốc.
- **Không bao giờ** tự chạy `apply` hay `rollback` khi Tuan chưa xác nhận repo đó trong hội thoại.
- Trước khi thêm nguồn mới: đọc mã, liệt kê những gì nó chạy/truy cập, ghi license,
  ghi vào `docs/COMMUNITY.md`.
- Chọn nguồn: **ưu tiên nhiều sao GitHub**. STLab dùng phi thương mại → license **không phải lý do loại**;
  nguồn có ràng buộc (NC, trả phí khi thương mại, AGPL, không license) ghi vào bảng
  "Xem lại khi làm thương mại" trong `docs/COMMUNITY.md`. An toàn (mã chạy gì, gửi dữ liệu đi đâu) vẫn bắt buộc.
- `.claude/skills/` và `.claude/agents/` của các dự án chỉ chứa symlink và không đưa lên git.

## Git
- Repo này định đưa lên GitHub. Không đưa bản clone cộng đồng và bí mật vào repo (xem `.gitignore`).
- Chỉ commit/push khi Tuan yêu cầu.
