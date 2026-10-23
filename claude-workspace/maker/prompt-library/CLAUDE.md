# prompt-library – FreeCAD và Blender

## Mục tiêu
Thư viện prompt tái sử dụng để dựng model FreeCAD/Blender bằng Claude qua MCP.

## Cấu trúc
- `freecad/<chu-de>.md`, `blender/<chu-de>.md`: mỗi file một prompt, theo mẫu `_mau-prompt.md`.
- Chỉ lưu prompt đã chạy thử thành công; ghi phiên bản MCP/ứng dụng đã dùng.

## Đã cài (2026-10-21, theo điểm ghim trong `community/pins.tsv`)
- FreeCAD 1.1: `%APPDATA%\FreeCAD\v1-1\Mod\FreeCADMCP` là symlink → freecad-mcp v0.1.27.
  Bản 0.1.26 cũ đã chuyển sang `%APPDATA%\FreeCAD\v1-1\Mod-backup\`.
- Blender 5.1: `scripts\addons\blender_mcp.py` là symlink → mcp-for-blender @5a3618fccb2d,
  đã bật trong Preferences, "Allow Telemetry" = tắt. Bản sao lưu prefs: `userpref.blend.bak-2026-10-21`.
- Biến môi trường người dùng: `BLENDERMCP_NO_UPDATE_CHECK=1` (addon không tự kiểm tra bản mới từ `main`).
- `.mcp.json` chạy server bằng `uvx --from <ban-ghim>`. Claude Code hỏi duyệt ở lần đầu.

## Mỗi lần dùng
1. FreeCAD: chọn workbench **MCP Addon** → **Start RPC Server** (cổng 9875, chỉ 127.0.0.1).
2. Blender: phím `N` → tab **MCP for Blender** → **Start MCP Server** (cổng 9876).
3. Mở Claude Code tại thư mục này. `/mcp` để kiểm tra cả hai server đã kết nối.

## An toàn
- Cả hai server **chạy Python tùy ý** trong ứng dụng. Lưu file trước khi cho AI sửa model.
- FreeCAD: không bật "remote"/`0.0.0.0`. Blender: `BLENDER_MCP_SAFE_MODE=1` (sandbox).
  Nếu sandbox chặn việc cần làm thì tắt tạm trong `.mcp.json`, và ghi lại lý do.
- Các tích hợp API ngoài của Blender (Poly Haven, Sketchfab, Hyper3D…) mặc định tắt: chỉ bật khi cần.
- Không chạy `uvx mcp-for-blender setup/update`: lệnh này tự sửa cấu hình và nâng lên bản mới nhất,
  vượt qua điểm ghim. Nâng cấp thì dùng `community/update-community.sh`.

## Quy ước
- Kích thước mm. Sau khi sinh model, kiểm tra lại kích thước và kiểu ghép (dung sai).
