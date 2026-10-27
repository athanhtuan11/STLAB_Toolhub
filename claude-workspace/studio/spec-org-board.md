---
task: toolhub-org-board
cwd: studio
allow: ["toolhub/usage.py", "toolhub/views.py", "toolhub/templates/overview.html", "toolhub/static/style.css"]
read: ["org", "tools/delegate", "docs/reports/ui-design-repos-study.md"]
gate: '.venv\Scripts\python.exe tests\test_org_board.py'
ky_nang: [code]
timeout_min: 25
max_rounds: 2
---

# Mục tiêu
Làm lại ô "Hạn mức AI" trên trang chính Toolhub thành **"Nhân sự AI"** lấy từ sổ nhân sự `org/agents.yaml` (Tuan
2026-10-27: trang chưa cập nhật org). Đọc `tests/test_org_board.py` để biết đúng dữ liệu. Tuân `studio/design/DESIGN.md`
(chỉ `var(--…)`, không hex; trạng thái bằng chữ + màu; ngôn ngữ người dùng; sáng/tối theo hệ thống) và checklist mục 6
`docs/reports/ui-design-repos-study.md` (focus nhìn thấy, không lệ thuộc hover, `prefers-reduced-motion`, không gradient/
shadow trang trí). Flask + HTML + JS thuần, KHÔNG thêm thư viện/build.

# Backend – `toolhub/usage.py` (CHỈ ĐỌC file trên máy, không gọi mạng, không import tools/delegate)
`org_board()` → `{providers, tiers, attention}`; route `GET /api/org` trong `views.py`. Giữ `all_agents()` + `/api/usage`.
- Đường dẫn: sổ = `<claude-workspace>/org/agents.yaml` (tính từ file); dữ liệu chạy = `%LOCALAPPDATA%/stlab-usage/`
  (`executors.json` {id: {limited_until ISO, reason}}, `agent-stats.json` {id: {rounds, gate_pass, pass_round1, …}},
  `delegate-runs/<run>/` có `state.json` {pid}, `result.json`). Đọc biến môi trường lúc GỌI (không đóng băng lúc import).
- `providers` (thứ tự claude, codex, gemini, opencode): `{id, name, plan, bars, note, updated, agents[], limited_until}`.
  Gán agent: `chi_phi: claude-quota` → claude; model/id chứa "codex"/"gpt" → codex; "gemini"/"agy" → gemini;
  "opencode" → opencode. `bars/plan/note/updated` lấy từ hàm claude()/codex()/gemini() sẵn có; opencode: bars rỗng,
  note "Zen free – chưa có số hạn mức". `limited_until`: giờ muộn nhất còn hiệu lực trong executors.json của các agent nguồn đó.
- `tiers`: 4 nhóm theo `tang` (0 "Giám đốc", 1 "Quản lý", 2 "Nhân viên", "tu-van" "Tư vấn"), mỗi agent:
  `{id, chuc_danh, model, chi_phi, ky_nang, bao_cao_cho, status, status_text, stats?}`.
  status: `nghi` / `thu-viec` theo trang_thai; `het-han-muc` nếu executors.json còn hạn (status_text "Hết hạn mức tới dd/mm HH:MM");
  ngược lại `san-sang` ("Sẵn sàng"). `stats` (nếu có trong agent-stats.json): các trường + `pass_rate` = gate_pass/rounds.
- `attention`: list `{level: warn|bad, text}`: mỗi run thiếu result.json mà pid chết/thiếu → "Việc <tên> bị cắt ngang –
  chạy `python tools/delegate/delegate.py --resume <tên>`" (bad); mỗi executor đang hết hạn mức → "<id> hết hạn mức tới …" (warn).
  Kiểm pid Windows: OpenProcess/GetExitCodeProcess (KHÔNG os.kill).

# Giao diện – `overview.html` + `style.css`
Thay khối "Hạn mức AI" bằng `<h2>Nhân sự AI</h2>`, gọi `fetch("/api/org")`:
1. **Hạn mức theo nguồn**: lưới thẻ (dùng lại kiểu `.u-card/.u-bar`): tên + plan, thanh "còn x%", dòng "Dùng cho:
   <agent>" (chip nhỏ), badge `warn` "Hết hạn mức tới …" nếu có.
2. **Cần chú ý**: chỉ hiện khi `attention` không rỗng; danh sách có nhãn chữ (Cảnh báo/Lỗi) + màu.
3. **Sơ đồ nhân sự**: `<details>` (mặc định đóng) "Sơ đồ nhân sự (N)"; 4 cột theo tầng (≤ 520 px: 1 cột); mỗi agent thẻ
   nhỏ: chức danh (đậm), `id` + model (muted), badge trạng thái bằng chữ, chip kỹ năng, nếu có stats: "N vòng · đạt x% ·
   vòng 1 đạt y". Không tràn ngang ở 480 px; nút/summary có viền focus.

# Không làm
- Không sửa `tests/`, `org/`, `tools/`, `design/tokens.json`, file khác ngoài allow. Không thêm hex.
