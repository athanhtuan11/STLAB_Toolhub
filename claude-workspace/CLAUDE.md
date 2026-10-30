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
- **Quy trình lặp lại ≥ 2 lần → lưu thành skill** (Tuan 2026-10-30) trong `custom/skills/` + dòng `links.tsv`; quy trình
  đổi thì sửa skill, đừng để memory và skill nói khác nhau. Trình tự nhận việc → giao → kiểm → commit → memory:
  skill `stlab-workflow`; phát hành firmware OTA: skill `stlab-ota-release`.

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

**Phân quyền 3 tầng (Tuan 2026-10-27):** Claude = tổng giám đốc: quyết định + viết đặc tả/gate, giao cấp dưới làm.
**Sổ nhân sự `org/agents.yaml` + `org/policy.yaml` là nguồn duy nhất** về agent (vai trò, model, chi phí, quyền, mức dữ
liệu, người duyệt, chuyển khi hết hạn mức). Thêm/đổi agent: sửa sổ (chỉ phiên chính, Tuan duyệt) → `python
tools/org/check_org.py` phải PASS. Agent mới vào `thu-viec`, qua bài thử có gate mới `chinh-thuc`. Executor không được sửa `org/`.
Thiết kế + lộ trình: `docs/reports/agent-org-roles-permissions.md` mục 7 (đã xong bước 1).
**Báo lên trên (Tuan 2026-10-27):** không có quyền / không phải việc của mình → dừng, báo `bao_cao_cho` (nhân viên →
quản lý/giám đốc → Tuan); không tự làm thay, không nhờ agent khác làm hộ. Executor trả `ESCALATE: ...` → `delegate.py`
dừng, `verdict: ESCALATE` (exit 2) + `handoff.md`; agent Haiku ghi `BÁO LÊN TRÊN:` ở dòng đầu báo cáo. Phiên chính
gặp việc vượt quyền mình (quyền hệ thống, việc của phiên khác, quyết định của Tuan) → hỏi Tuan.

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

Mô tả công việc:

| Tầng | Ai | Làm gì |
|---|---|---|
| 0 – Tổng giám đốc | Phiên chính (Opus) | Kiến trúc, quyết định, **viết spec + gate** (tiêu chí nghiệm thu đo được), hình học/khe/động học khó, `safe_edit.py`, hướng in/support `print.yaml`, an toàn, duyệt ảnh + `result.json` |
| 2 – Thực thi (free) | `tools/delegate/delegate.py` → Codex (chính) → OpenCode → Kilo → agy-sonnet → Copilot → agy (dự phòng) | Viết + chạy code/script theo `spec.md` tới khi gate PASS: script Python, firmware, Toolhub, script FreeCAD theo spec (`tools/cad-delegation/`) |
| 1 – Quản lý | Agent `check-runner` (Haiku) | Sau mỗi lần sửa model đã Lưu: chạy `prepare-print.py` + test, trả tóm tắt ≤ 15 dòng. **Không tự đọc log dài trong phiên chính** |
| 1 – Quản lý | Agent `doc-writer` (Haiku + Gemini free) | README, văn xuôi ASSEMBLY.md, ghi chú nghiên cứu, caption, lịch sử sửa – từ gạch đầu dòng phiên chính đưa |
| 1 – Quản lý | Agent `git-scribe` (Haiku) | Soạn commit + push khi kiểm đạt (đưa kèm phạm vi file + kết quả kiểm) |
| Tư vấn | deliberation `ask-gemini` (Gemini qua Antigravity `agy`) | Tóm tắt tài liệu/trang web dài (> ~300 dòng) trước khi Claude đọc; dịch; đổi giọng văn |
| Tư vấn | `/codex:review` (ChatGPT Free); deliberation `consensus` (Gemini + GPT) | Review lần 2 script Python/FreeCAD lớn trước khi commit; `consensus`/`/codex:adversarial-review` khi phân vân thiết kế code |

Giao việc code (thay cho Claude tự viết code dài): chép `tools/delegate/templates/spec.md` → điền mục tiêu, `cwd`,
`allow`, `gate` (Claude viết test/gate TRƯỚC) → chạy nền `python tools/delegate/delegate.py <spec.md>` → chỉ đọc dòng
JSON cuối (`verdict`, `rounds`, `changed`, `forbidden_touched`). Log dài nằm ở `run_dir`, không đọc trừ khi FAIL.
`delegate.py` tự chuyển executor khi gặp 429/hết hạn mức (`--status` xem, `--mark-limit agy <ISO>` đánh dấu tay),
và báo FAIL nếu executor đụng `.FCStd`/`print.yaml`/`community/`/`.env`. OpenCode chạy với
`tools/delegate/opencode.json` (cấm ghi ngoài `cwd`, cấm `.FCStd`/git commit/push). Kilo nạp `tools/delegate/kilo.json`
qua `KILO_CONFIG`. Copilot nhận prompt qua stdin, có `--sandbox` và `--deny-tool` cho git commit/push/reset/checkout, `rm -rf`,
`Remove-Item`. `agy-sonnet` (chính thức 2026-10-28) nằm trong chuỗi tự động sau Kilo; sandbox agy không thấy python/ổ ngoài cwd nên `delegate.py` chạy gate thay (lời dặn AGY_NOTE trong prompt). Claude chỉ tự viết code khi
việc nhỏ hơn việc viết spec (≲ 30 dòng) hoặc là hình học/khe/an toàn.

**Quy tắc cứng (Tuan 2026-10-26, nhắc 2 lần):** phiên chính KHÔNG tự đọc tài liệu/BOM/log/file mẫu, KHÔNG tự viết tài
liệu, KHÔNG tự commit – đọc/tóm tắt → agy (`ask-gemini`), tra web → Codex (`ask-gpt`), viết tài liệu → `doc-writer`,
kiểm/test → `check-runner`, commit → `git-scribe`. Claude chỉ tự làm CAD (script dựng hình/ảnh, khe, động học), an toàn,
quyết định; tự đọc tối đa vài dòng khi đang viết code CAD.

Gọi Gemini qua deliberation: chép file cần đọc vào `D:\04_Stlab\agy-scratch\<ten-viec>\` (ngoài repo), `cwd` = thư
mục đó, prompt ghi "chỉ đọc file trong thư mục làm việc, không chạy lệnh terminal"; xong xóa thư mục. **Không** dùng
`files` cho Gemini (không được chèn nội dung; đã thử 2026-10-26). Lý do: trên Windows `agy` không có sandbox HĐH.
Codex `ask-gpt` (deliberation) trên Windows **không đọc được file** – sandbox chỉ đọc chặn mọi lệnh shell (thử 2026-10-26);
dùng nó để tra web hoặc dán đoạn mã vào prompt; đọc mã/repo giao Gemini (agy). `/codex:review`: `TODO` thử lại trên Windows.

Nguyên tắc cứng:
- Model free (Gemini, Codex, OpenCode, Kilo, agy-sonnet, Copilot) **không quyết** kích thước, khe, thông số linh kiện, an toàn điện/pin/nhiệt. Số liệu từ chúng
  phải được phiên chính hoặc script kiểm; không có nguồn → `TODO`.
- **Không gửi ra ngoài** (Gemini, Codex, OpenCode, Kilo, agy-sonnet, Copilot – chính sách dữ liệu gói free Kilo/Copilot còn TODO): `stlab/parent-reports/`, thông tin cá nhân của khách (tên, địa chỉ, SĐT, mật khẩu Wi-Fi/tài khoản – KHÔNG phải
  bản thân dự án: mọi dự án trong `maker/` là việc bình thường, giao executor được; Tuan 2026-10-27),
  `.env`/key/mật khẩu, ảnh có người. Chỉ tài liệu kỹ thuật, mã nguồn của workspace.
- `/codex:rescue` (Codex được ghi file, sandbox `workspace-write`) chỉ dùng khi Tuan đồng ý; cấm cho đụng `.FCStd`,
  `print.yaml`, `community/`. Không bật cổng review khi dừng (`/codex:setup` → stop gate giữ **tắt**).
- Không chạy `/deliberation:setup` (cài luật "tự giao việc trên MỌI tin nhắn" vào `~/.claude/rules/`). Server
  `deliberation-gemini/-grok/-openrouter` bị `deny` (đường ghi file duy nhất của Gemini); chỉ dùng bộ điều phối.
- Chỉ một phiên điều khiển FreeCAD GUI; agent chỉ chạy `freecadcmd`/`python.exe` trên file đã Lưu.
- Hết hạn mức free (lỗi 429/quota) → làm tiếp bằng Haiku/phiên chính, không đổi sang dịch vụ trả phí.

## Git
- Repo này định đưa lên GitHub. Không đưa bản clone cộng đồng và bí mật vào repo (xem `.gitignore`).
- Kiểm ổn (test/kiểm tra đạt) thì tự commit + push lên GitHub (Tuan 2026-10-23); thay đổi lớn làm trên nhánh rồi gộp.
