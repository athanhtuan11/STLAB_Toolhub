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
- `stlab/`: giáo án (`lesson-plans/`), báo cáo phụ huynh (`parent-reports/`, dữ liệu cá nhân – không lên git).
- `maker/`: **chỉ dự án** (mỗi thư mục một dự án, có `CLAUDE.md` + `README.md`). Dự án CAD: `design/` (bước 0),
  `freecad/`, `print/`; điện tử: `firmware/`, `hardware/`, `docs/`.
- `tools/`: công cụ dùng chung cho nhiều dự án – `robotics-cad/` (kiểm model, xuất STL, cắt lớp, workbench STLab,
  `project-template/`), `prompt-library/` (prompt FreeCAD/Blender + MCP).
- `photo-ai/`: sửa ảnh LightCraft – **tạm dừng** (chờ bản LightCraft tạo ảnh AI).
- `harness-lab/`: sổ lỗi `inbox.md` + lệnh `/lesson` để cải thiện cách làm việc với Claude.
- `docs/`: nghiên cứu (`*-research.md`), quy trình (`cad-standard-workflow.md`), `reports/`, `research-notes/`,
  `COMMUNITY.md` (bảng quản lý nguồn cộng đồng).

## Đặt tên (Tuan 2026-10-23, chuẩn hóa toàn repo 2026-10-25)
- Thư mục, file, script, khóa YAML, tham số CLI, URL Toolhub, tên skill/lệnh: **tiếng Anh, kebab-case, không dấu**.
  Ngoại lệ theo ngôn ngữ: module Python và file model dùng `_` (`safe_edit.py`, `pushrod_arm.FCStd`); file chuẩn viết
  hoa (`CLAUDE.md`, `README.md`, `SKILL.md`, `ASSEMBLY.md`, `BOM.md`); tên riêng giữ nguyên (giọng `mai-anh.mp3`).
- Nội dung tài liệu viết tiếng Việt. Tên cũ trong lịch sử git/memory là lịch sử, không sửa.

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

## Phân việc theo model (Tuan 2026-10-26: chỉ trả Claude Pro, còn lại free)
Chi tiết, cài đặt, gỡ bỏ: `docs/model-routing.md`.

| Ai | Làm gì |
|---|---|
| Phiên chính (Opus) | Hình học, khe/dung sai, động học, va chạm, `safe_edit.py`, script FreeCAD tham số, hướng in/support trong `print.yaml`, thứ tự lắp, ghi chú an toàn, duyệt ảnh, quyết định cuối |
| Agent `check-runner` (Haiku) | Sau mỗi lần sửa model đã Lưu: chạy `prepare-print.py` + test, trả tóm tắt ≤ 15 dòng. **Không tự đọc log dài trong phiên chính** |
| Agent `doc-writer` (Haiku + Gemini free qua PAL) | README, văn xuôi ASSEMBLY.md, ghi chú nghiên cứu, caption, lịch sử sửa – từ gạch đầu dòng phiên chính đưa |
| Agent `git-scribe` (Haiku) | Soạn commit + push khi kiểm đạt (đưa kèm phạm vi file + kết quả kiểm) |
| PAL `chat` (`flash`/`lite`) | Tóm tắt tài liệu/trang web dài (> ~300 dòng) trước khi Claude đọc; dịch; đổi giọng văn |
| PAL `codereview`, `/codex:review` (ChatGPT Free) | Review lần 2 script Python/FreeCAD lớn trước khi commit; `/codex:adversarial-review` khi phân vân thiết kế code |

Nguyên tắc cứng:
- Model free (Gemini, Codex) **không quyết** kích thước, khe, thông số linh kiện, an toàn điện/pin/nhiệt. Số liệu từ chúng
  phải được phiên chính hoặc script kiểm; không có nguồn → `TODO`.
- **Không gửi ra ngoài** (PAL/Gemini, Codex): `stlab/parent-reports/`, dữ liệu khách (`maker/pump-control/` phần khách),
  `.env`/key/mật khẩu, ảnh có người. Chỉ tài liệu kỹ thuật, mã nguồn của workspace.
- `/codex:rescue` (Codex được ghi file, sandbox `workspace-write`) chỉ dùng khi Tuan đồng ý; cấm cho đụng `.FCStd`,
  `print.yaml`, `community/`. Không bật cổng review khi dừng (`/codex:setup` → stop gate giữ **tắt**).
- Chỉ một phiên điều khiển FreeCAD GUI; agent chỉ chạy `freecadcmd`/`python.exe` trên file đã Lưu.
- Hết hạn mức free (lỗi 429/quota) → làm tiếp bằng Haiku/phiên chính, không đổi sang dịch vụ trả phí.

## Git
- Repo này định đưa lên GitHub. Không đưa bản clone cộng đồng và bí mật vào repo (xem `.gitignore`).
- Kiểm ổn (test/kiểm tra đạt) thì tự commit + push lên GitHub (Tuan 2026-10-23); thay đổi lớn làm trên nhánh rồi gộp.
