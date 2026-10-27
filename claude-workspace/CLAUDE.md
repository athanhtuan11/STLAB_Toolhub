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

**Phân quyền 3 tầng (Tuan 2026-10-27):** Claude = tổng giám đốc: quyết định + viết đặc tả/gate, giao cấp dưới làm.

| Tầng | Ai | Làm gì |
|---|---|---|
| 0 – Tổng giám đốc | Phiên chính (Opus) | Kiến trúc, quyết định, **viết spec + gate** (tiêu chí nghiệm thu đo được), hình học/khe/động học khó, `safe_edit.py`, hướng in/support `print.yaml`, an toàn, duyệt ảnh + `result.json` |
| 2 – Thực thi (free) | `tools/delegate/delegate.py` → Codex exec (chính) → OpenCode Zen free → agy (dự phòng) | Viết + chạy code/script theo `spec.md` tới khi gate PASS: script Python, firmware, Toolhub, script FreeCAD theo spec (`tools/cad-delegation/`) |
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
`tools/delegate/opencode.json` (cấm ghi ngoài `cwd`, cấm `.FCStd`/git commit/push). Claude chỉ tự viết code khi
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
- Model free (Gemini, Codex, OpenCode) **không quyết** kích thước, khe, thông số linh kiện, an toàn điện/pin/nhiệt. Số liệu từ chúng
  phải được phiên chính hoặc script kiểm; không có nguồn → `TODO`.
- **Không gửi ra ngoài** (Gemini, Codex, OpenCode): `stlab/parent-reports/`, dữ liệu khách (`maker/pump-control/` phần khách),
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
