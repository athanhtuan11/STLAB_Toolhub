---
task: toolhub-ui-gap-review
cwd: .
allow: ["docs/reports/toolhub-ui-gap-review.md"]
read: ["studio", "tools", "maker", "docs/reports", "docs/research-notes", "CLAUDE.md", "custom"]
gate: 'python tools/delegate/check_report.py docs/reports/toolhub-ui-gap-review.md "## 1. Hien trang Toolhub" "## 2. Tinh nang repo chua len web" "## 3. Van de giao dien hien tai" "## 4. Mau in dang cong dong va ban" "## 5. De xuat xep loi/cong" --max-todo 10 --min-files 12'
ky_nang: [bao-cao]
timeout_min: 60
max_rounds: 3
executor: copilot
---

# Mục tiêu
Viết `docs/reports/toolhub-ui-gap-review.md` (tiếng Việt có dấu, ≤ 260 dòng): **rà toàn repo** xem cần đưa gì lên giao diện web
Toolhub (`studio/`, Flask) và giao diện hiện tại cần cải thiện gì (Tuan 2026-11-02). **Chỉ ĐỌC, không sửa code/không chạy server**
– Tuan duyệt rồi mới làm. Mọi nhận định phải trỏ file cụ thể (`đường/dẫn:dòng` hoặc `đường/dẫn`).

# Bối cảnh
- Toolhub: `studio/launcher.py`, `studio/toolhub/views.py` + các module (quote, ops, research, usage, pinout, pin_diagram,
  printprep, workspace, opener), `templates/`, `static/`, `apps.json`, test ở `studio/tests/`, các spec `studio/spec-*.md`.
  Đọc `studio/CLAUDE.md` trước. Trang hiện có (route GET): `/`, `/apps`, `/projects`, `/projects/<slug>`, `/library`, `/community`,
  `/research`, `/skills`, `/prompt`, `/quote`, `/ops`.
- Công cụ trong repo: `tools/` (backup, cad-delegation, ci, delegate, git-hooks, model-study + fit-library, org, prompt-library,
  render, research-scout, robotics-cad, toolchain); dự án `maker/*` (có `print.yaml`, ASSEMBLY.md, BOM…); báo cáo `docs/reports/`.
- Tuan là chủ trung tâm, không phải lập trình viên: thích bấm nút trên web thay vì gõ lệnh; duyệt bằng ảnh (contact sheet).

# Mục bắt buộc (đúng tiêu đề)
- `## 1. Hien trang Toolhub`: bảng trang/route → chức năng → module/template → có trong menu điều hướng không → có test không.
- `## 2. Tinh nang repo chua len web`: công cụ/script/quy trình đang chỉ chạy bằng dòng lệnh mà nên có nút/trang (ví dụ: fit-library
  tra khe, model-study contact sheet, render Blender, prepare-print/check, delegate.py --status, OTA release pump-control, research-scout,
  backup, báo cáo docs/reports). Mỗi dòng: công cụ | lệnh hiện tại (trích file) | lợi khi lên web | rủi ro (lệnh nguy hiểm, ghi file,
  dữ liệu khách) | nên/không nên.
- `## 3. Van de giao dien hien tai`: lỗi/thiếu nhất quán đọc được từ mã: route không có link menu, template trùng lặp, chữ Việt
  không dấu/lẫn, nút gọi lệnh không xác nhận, đường dẫn cứng, xử lý lỗi thiếu, trang chậm (quét đĩa mỗi request), bảo mật
  (route POST chạy lệnh có bind ngoài localhost không, CSRF), test thiếu. Chỉ ghi điều thấy trong mã, kèm file:dòng.
- `## 4. Mau in dang cong dong va ban`: dựa trên `docs/reports/print-products-market-research.md`, đề xuất trang/tính năng phục vụ
  quy trình mẫu in (danh mục mẫu STLab, trạng thái thiết kế→in thử→đăng→bán, nối `/quote`, checklist gói MakerWorld). Tận dụng trang
  sẵn có thay vì tạo mới khi được.
- `## 5. De xuat xep loi/cong`: bảng ≤ 15 dòng: đề xuất | mục | lợi (cao/vừa/thấp) | công (giờ) | rủi ro | file liên quan.
  Xếp giảm dần, đánh dấu 3–5 việc nên làm trước.

# Quy tắc
- Không bịa route/hàm: chỉ nêu cái thấy trong file. Không chắc → `TODO`. Không chép dữ liệu khách (SQLite quote ở ngoài repo, không đọc).

# Tiêu chí PASS
Gate exit 0.
