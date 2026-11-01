# claude-workspace – workspace Claude Code của STLab

Quy ước chung đặt ở file này (mẫu shanraisshan/claude-code-best-practice); mỗi dự án con có `CLAUDE.md` riêng và tự nạp file này theo cây thư mục cha.

## Cấu trúc
- `community/`: repo cộng đồng detached ở điểm ghim. **Chỉ đọc, KHÔNG sửa.** `pins.tsv` (ghim), `links.tsv` (liên kết), `update-community.sh` (xem `docs/COMMUNITY.md`).
- `custom/skills/`: skill tự viết, chỉ khi không có nguồn cộng đồng phù hợp (ghi lý do).
- `studio/`: giao diện STLAB Toolhub (Flask) + mở FreeCAD/Blender/LightCraft/PhotoCraft kèm MCP; xem `studio/CLAUDE.md`. Tính năng mới thì thêm trang vào Toolhub.
- `video-ai/`: tự dựng video ngắn từ clip tự quay (FilmCraft); xem `video-ai/CLAUDE.md`.
- `stlab/`: giáo án (`lesson-plans/`); `parent-reports/` là dữ liệu cá nhân, không lên git.
- `maker/`: **chỉ dự án**, mỗi thư mục một dự án (`CLAUDE.md` + `README.md`). CAD: `design/` (bước 0), `freecad/`, `print/`; điện tử: `firmware/`, `hardware/`, `docs/`.
- `tools/`: công cụ dùng chung: `robotics-cad/` (kiểm model, STL, cắt lớp, workbench STLab, `project-template/`), `prompt-library/`.
- `tools/backup/`: sao lưu .FCStd ra G: + OneDrive (lịch hằng ngày 21:00).
- `photo-ai/`: LightCraft – **tạm dừng** (chờ bản tạo ảnh AI).
- `harness-lab/`: sổ lỗi `inbox.md` + lệnh `/lesson`.
- `docs/`: nghiên cứu, quy trình, `reports/`, `research-notes/`, `COMMUNITY.md`, `model-routing.md` (phân việc model, chi tiết).

## Đặt tên (Tuan 2026-10-23, chuẩn hóa 2026-10-25)
- Thư mục, file, script, khóa YAML, tham số CLI, URL Toolhub, tên skill/lệnh: **tiếng Anh, kebab-case, không dấu**. Ngoại lệ: module Python và file model dùng `_`; file chuẩn viết hoa (`CLAUDE.md`, `README.md`, `SKILL.md`, `ASSEMBLY.md`, `BOM.md`); tên riêng giữ nguyên.
- Nội dung tài liệu viết **tiếng Việt**. Tên cũ trong lịch sử git/memory là lịch sử, không sửa.

## Một nguồn duy nhất cho skill
- Skill chỉ nằm trong workspace (`custom/skills/`, `community/...`); nơi khác là **symlink** theo `links.tsv`. Skill dùng chung → `~/.claude/skills/`; không liên kết một skill ở cả cấp dự án lẫn cấp dùng chung (bị trùng tên).
- **Không tải skill lên claude.ai** (thành bản sao thứ hai). Tab **Code** của Claude Desktop đọc skill; tab Chat/Cowork không đọc.
- **Quy trình lặp lại ≥ 2 lần → lưu thành skill** (Tuan 2026-10-30) + dòng `links.tsv`; quy trình đổi thì sửa skill, không để memory và skill nói khác. Nhận việc → giao → kiểm → commit → memory: `stlab-workflow`; phát hành OTA: `stlab-ota-release`.

## Quy tắc với nguồn cộng đồng
- Muốn dùng skill/agent mới: thêm dòng vào `community/links.tsv`, rồi `bash community/update-community.sh link`. Không copy để sửa trực tiếp; tùy biến thì tạo file riêng trong `custom/`, không đè bản gốc.
- **Không bao giờ** tự chạy `apply` hay `rollback` khi Tuan chưa xác nhận repo đó trong hội thoại.
- Trước khi thêm nguồn: đọc mã, liệt kê những gì nó chạy/truy cập, ghi license vào `docs/COMMUNITY.md`.
- Chọn nguồn ưu tiên **nhiều sao GitHub**. License không phải lý do loại (STLab phi thương mại); nguồn ràng buộc (NC, trả phí khi thương mại, AGPL, không license) ghi bảng "Xem lại khi làm thương mại". An toàn (mã chạy gì, gửi dữ liệu đi đâu) vẫn bắt buộc.
- `.claude/skills/`, `.claude/agents/` của dự án chỉ chứa symlink, không đưa lên git.

## Phân việc theo model (chỉ trả Claude Pro, còn lại free – Tuan 2026-10-26)
Chi tiết, cài đặt, gỡ bỏ, bảng mô tả công việc, cơ chế delegate: `docs/model-routing.md`.

- **Phân quyền 3 tầng (Tuan 2026-10-27):** tổng giám đốc (Claude) quyết định, viết spec + gate, giao cấp dưới; Haiku (`check-runner`, `doc-writer`, `git-scribe`) quản lý; executor free qua `tools/delegate/delegate.py` làm việc.
- Phiên chính **không** tự đọc tài liệu/BOM/log/file mẫu, không tự viết tài liệu, không tự commit: đọc/tóm tắt → `ask-gemini`; tra web → `ask-gpt`; viết tài liệu → `doc-writer`; kiểm → `check-runner`; commit → `git-scribe`. Chỉ tự làm CAD (dựng hình, khe, động học), an toàn, quyết định; đọc tối đa vài dòng khi viết code CAD.
- Giao code: spec từ `tools/delegate/templates/spec.md`, viết gate **trước**, chạy nền `delegate.py`, chỉ đọc dòng JSON cuối. Phiên chính tự viết code chỉ khi việc ≲ 30 dòng hoặc là hình học/khe/an toàn.
- Hết 429/hạn mức: `delegate.py` tự chuyển executor (Codex → OpenCode → Kilo → agy-sonnet → Copilot → agy). Hết hạn mức free thì làm tiếp bằng Haiku/phiên chính, **không** đổi sang dịch vụ trả phí.
- Gemini (`ask-gemini`, chỉ đọc): chỉ thấy bản chép trong `D:\04_Stlab\agy-scratch\<ten-viec>\` (ngoài repo), `cwd` = thư mục đó, xong xóa; **không** dùng tham số `files`. Đọc mã/repo giao Gemini; `ask-gpt` chỉ tra web hoặc nhận đoạn mã dán vào prompt.
- `/codex:rescue` (Codex được ghi file) chỉ khi Tuan đồng ý. Không bật stop review gate của `/codex:setup`.
- **Sổ nhân sự `org/agents.yaml` + `org/policy.yaml` là nguồn duy nhất** về agent (vai trò, model, chi phí, quyền, mức dữ liệu, người duyệt). Thêm/đổi agent: chỉ phiên chính sửa sổ (Tuan duyệt) → `python tools/org/check_org.py` phải PASS. Agent mới vào `thu-viec`, qua gate mới lên `chinh-thuc`. Executor **không** được sửa `org/`.
- **Báo lên trên (Tuan 2026-10-27):** không có quyền / không phải việc mình → dừng, báo `bao_cao_cho` (nhân viên → quản lý/giám đốc → Tuan), không tự làm thay, không nhờ agent khác. Báo cáo ghi `BÁO LÊN TRÊN:` ở dòng đầu. Phiên chính gặp việc vượt quyền → hỏi Tuan.

Sổ nhân sự (sinh tự động – sửa `org/agents.yaml` rồi chạy `python tools/org/gen_table.py --write`):

<!-- org-table:start -->
| Tầng | Chức danh | Agent | Model | Chi phí | Kỹ năng | Báo cáo cho | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 – Giám đốc | Tổng giám đốc | `claude-main` | opus | claude-quota | quyet-dinh, spec, gate, cad-hinh-hoc, an-toan, duyet | tuan | chinh-thuc |
| 1 – Quản lý | Quản lý kiểm tra | `check-runner` | haiku | claude-quota | test, kiem-in, doc-log | claude-main | chinh-thuc |
| 1 – Quản lý | Quản lý tài liệu | `doc-writer` | haiku | claude-quota | tai-lieu | claude-main | chinh-thuc |
| 1 – Quản lý | Quản lý git | `git-scribe` | haiku | claude-quota | commit, push | claude-main | chinh-thuc |
| 2 – Nhân viên | Nhân viên lập trình (chính) | `codex` | codex-chatgpt-free | free | code, cad-script, doc-ma, bao-cao | claude-main | chinh-thuc |
| 2 – Nhân viên | Nhân viên lập trình | `opencode` | opencode/deepseek-v4.1-flash-free | free | code, cad-script | claude-main | chinh-thuc |
| 2 – Nhân viên | Nhân viên lập trình | `kilo` | kilo/kilo-auto/free | free | code, cad-script | claude-main | chinh-thuc |
| 2 – Nhân viên | Nhân viên lập trình | `agy-sonnet` | claude-sonnet-4-6 | free | code, cad-script, doc-ma | claude-main | chinh-thuc |
| 2 – Nhân viên | Nhân viên lập trình | `copilot` | auto | free | code, doc-ma | claude-main | chinh-thuc |
| 2 – Nhân viên | Nhân viên lập trình (dự phòng) | `agy` | gemini-3.8-flash-high | free | doc-ma | claude-main | chinh-thuc |
| Tư vấn | Tư vấn tra web | `ask-gpt` | codex-chatgpt-free | free | tra-web | claude-main | chinh-thuc |
| Tư vấn | Tư vấn đọc tài liệu | `ask-gemini` | gemini-3.8-flash-medium | free | doc-tai-lieu, tom-tat, dich | claude-main | chinh-thuc |
_Sinh tự động từ org/agents.yaml bằng tools/org/gen_table.py – không sửa tay._
<!-- org-table:end -->

Nguyên tắc cứng (model free: Gemini, Codex, OpenCode, Kilo, agy-sonnet, Copilot):
- **Không quyết** kích thước, khe, thông số linh kiện, an toàn điện/pin/nhiệt. Số liệu phải từ phiên chính hoặc script kiểm; không có nguồn → `TODO`.
- **Không gửi** `stlab/parent-reports/`, thông tin cá nhân của khách (tên, địa chỉ, SĐT, mật khẩu Wi-Fi/tài khoản; dự án trong `maker/` là việc bình thường, Tuan 2026-10-27), `.env`/key/mật khẩu, ảnh có người. Chỉ tài liệu kỹ thuật, mã nguồn workspace.
- Chỉ một phiên điều khiển FreeCAD GUI; agent chỉ chạy `freecadcmd`/`python.exe` trên file đã Lưu.
- Không chạy `/deliberation:setup` (cài luật tự giao việc vào `~/.claude/rules/`); server `deliberation-gemini/-grok/-openrouter` bị `deny`.

## Git
- Repo định đưa lên GitHub. Không đưa bản clone cộng đồng và bí mật vào repo (xem `.gitignore`).
- Kiểm ổn (test/kiểm tra đạt) thì tự commit + push GitHub, không cần hỏi (Tuan 2026-10-23) – việc commit giao `git-scribe`; thay đổi lớn làm trên nhánh rồi gộp.
