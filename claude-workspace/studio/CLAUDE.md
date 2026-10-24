# studio – mở ứng dụng và nối MCP

Một chỗ để mở FreeCAD, Blender, LightCraft, PhotoCraft (đã bật cổng MCP) và làm việc với Claude Code
qua cả 4 MCP server trong `.mcp.json`.

> Tự viết vì chưa tìm thấy launcher cộng đồng nào cho bộ 4 ứng dụng này (2026-10-21).
> Chỉ dùng thư viện chuẩn và Flask (`uv.lock` ghim 3.1.3).

## Thành phần
- `apps.json`: **nguồn cấu hình duy nhất** (đường dẫn exe, tham số, cổng). Đổi cổng thì sửa ở đây
  **và** trong `.mcp.json`.
- `launcher.py`: `status`, `start <id|all>`, `mcp-check <ten|all>`, `claude`.
- `toolhub/`: giao diện web **STLAB Toolhub** (Flask app factory). Chạy `uv run flask run`
  tại `studio/`; cấu hình trong `.flaskenv` (127.0.0.1:5050). Menu gọn (Tuan 2026-10-24: "quá nhiều điểm"):
  **Trang chính · Dự án · Linh kiện · Sửa ảnh** + "Thêm ▾" (Ứng dụng & MCP, Nguồn cộng đồng – chỉ kiểm tra/báo cáo,
  apply/rollback chỉ hiện lệnh –, Skills & agents, Prompt library). Trang chính chỉ có: dòng "Cần chú ý" (chỉ hiện lỗi,
  nạp sau qua `/api/health`), hàng ứng dụng (đèn + Mở), thẻ dự án in 3D (kết quả Chuẩn bị in + nút), dự án khác thu gọn.
  Thêm trang mới: đặt vào "Thêm" trừ khi dùng hằng ngày. Trang chính phải hiện ngay – việc chậm (git, tasklist) nạp bằng JS.
  - `toolhub/photolab.py` (trang Sửa ảnh): gọi `photo-ai/scripts/looklab.py` / `develop.py` bằng Python của
    photo-ai (`.venv` riêng, Toolhub không cài Pillow). Chỉ đọc thư mục ảnh gốc; ghi vào `<nguon>-edit/lab/`
    (xem trước) và `<nguon>-edit/xuat-<kieu>[-local]-<do-manh>/` (kết quả, không ghi đè). `/anh/file` chỉ trả `.jpg`
    trong `lab/` và `xuat-*`. Mọi lệnh tạo ảnh là POST (cần `X-Studio`).
  - `toolhub/workspace.py`: đọc pins/links/reports/CLAUDE.md (chỉ đọc). `toolhub/views.py`: trang + API.
  - `toolhub/printprep.py` (trang Dự án, dự án có `print/print.yaml`): nút **Chuẩn bị in** và **Tự chạy khi Lưu**
    gọi `maker/robotics-cad/scripts/prepare-print.py` / `watch.py` bằng Python của FreeCAD, chạy nền (PID ở
    `print/_*.pid`). Chỉ đọc file FreeCAD đã lưu; ảnh chỉ trả `.png` mà `_prepare-print-result.json` trỏ tới. POST cần `X-Studio`.
- `bat/`: nhấp đúp để chạy (`mo-toolhub`, `mo-freecad`, `mo-blender`, `mo-lightcraft`, `mo-photocraft`,
  `mo-tat-ca`, `mo-claude`, `kiem-tra-mcp`).
- `scripts/freecad_start_rpc.py`: bật RPC server cho phiên FreeCAD do launcher mở.
- MCP `freecad` chạy với `--freecadcmd "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe"` (`freecadcmd` không có trong
  PATH → thiếu cờ này thì `execute_code_headless` không chạy). Việc nặng phải ra headless, xem skill `robotics-cad`
  mục "Chống treo FreeCAD". Sửa `.mcp.json` xong: chạy lại `bat/dong-bo-claude-desktop.bat` cho Claude Desktop.
- `scripts/fc_job.py`: chạy script FreeCAD nặng trong `freecadcmd` riêng, chạy nền (giao việc + hỏi tiến độ, mỗi lệnh
  < 0,1 s). Dùng khi Claude web/app điều khiển máy từ xa (giới hạn 60 s/lệnh). Job lưu ở `%LOCALAPPDATA%\stlab-fc-jobs\`.

## Ứng dụng + Claude Desktop cạnh nhau
- `launcher.py start <id>` mở app, chờ cổng MCP, rồi `winlayout.py` xếp app một bên và Claude Desktop
  (bản MSIX, tự mở nếu chưa chạy) bên còn lại. Cấu hình ở `apps.json` → `layout`.
- `launcher.py layout <id>`: chỉ xếp lại. `desktop-status` / `desktop-sync`: so sánh và đồng bộ 4 MCP server
  sang `claude_desktop_config.json` của Desktop. Desktop **phải thoát hẳn** trước khi sync (nó có thể ghi đè file);
  sync luôn sao lưu và không đụng tới server/cài đặt khác.
- MCP server bắt tay được cả khi app đang tắt và chỉ nối vào app khi có lệnh gọi, nên mở app sau Desktop vẫn được.

## Cổng và bảo mật (chỉ 127.0.0.1)
| App | Cổng | Ghi chú |
|---|---|---|
| FreeCAD | 9875 | RPC chạy Python tùy ý; chỉ bật khi mở qua launcher |
| Blender | 9876 | Addon tự bật mỗi lần mở Blender; sandbox `BLENDER_MCP_SAFE_MODE=1` |
| LightCraft | 7980 | **Không có token**: mọi tiến trình trên máy đều điều khiển được khi app mở bằng launcher |
| PhotoCraft | 7878 | Dùng cấu hình có sẵn của Tuan: token `~\.photocraft\control.token` (ngoài repo); chỉ đọc/ghi `%USERPROFILE%\Pictures\stlab-studio` |
| Web Toolhub | 5050 | Kiểm tra Host + header `X-Studio` (chống DNS rebinding/CSRF); "Mở VS Code" chỉ nhận dự án đã biết |

## Quy tắc
- Không thêm nút "tắt app" tự động: có thể mất bài đang làm dở. Tắt trong app.
- PhotoCraft chỉ chạy một bản: nếu đang mở bằng cách thường thì đóng đi, rồi mở lại bằng launcher.
- Trước khi cho AI sửa model hoặc ảnh: lưu file. Không đưa token vào file nào trong repo.
