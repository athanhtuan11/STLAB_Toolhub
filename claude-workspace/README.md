# claude-workspace – workspace Claude Code của STLab

Workspace cho các dự án STLab và maker, ưu tiên tái sử dụng skill/agent/MCP của cộng đồng.
Mọi nguồn cộng đồng đều được ghim phiên bản và cập nhật theo kiểu kiểm tra rồi duyệt.

## Mở giao diện
Nhấp đúp `mo-toolhub.bat` ở thư mục gốc repo `STLAB_Toolhub`, trình duyệt sẽ mở http://127.0.0.1:5050.
Đóng cửa sổ đen để tắt giao diện.

## Dựng lại trên máy mới (Windows, bật Developer Mode, có Git Bash)
```bash
git clone <repo-nay> claude-workspace && cd claude-workspace
bash community/update-community.sh clone    # clone repo cong dong dung diem ghim
bash community/update-community.sh link     # tao symlink skill/agent
bash community/update-community.sh verify
```
Đường dẫn tuyệt đối trong `maker/prompt-library/.mcp.json` cần sửa nếu đặt workspace ở chỗ khác.

## Tài liệu
- `CLAUDE.md`: quy ước của workspace.
- `docs/COMMUNITY.md`: nguồn cộng đồng, giấy phép, rủi ro, lệnh cập nhật/rollback.
