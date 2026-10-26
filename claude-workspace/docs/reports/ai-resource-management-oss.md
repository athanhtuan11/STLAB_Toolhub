# Quản lý & phân bổ hạn mức giữa Claude Code và agent free – phần mềm mã nguồn mở

Ngày: 2026-10-26 · Người yêu cầu: Tuan · Trạng thái: **nghiên cứu, chưa cài**

Số sao, ngày push, bản phát hành lấy từ GitHub API ngày 2026-10-26. License lấy từ GitHub API (npm ghi chú riêng nếu khác).

## 1. Hiện trạng + khoảng trống

Đang dùng (xem `docs/model-routing.md`): Opus phiên chính → 3 agent Haiku (`check-runner`, `doc-writer`, `git-scribe`)
→ deliberation v3.31.0 (Gemini qua `agy` 1.4.7, GPT qua Codex CLI 0.164.0) + `codex-plugin-cc` v1.0.6.
Quy tắc "hết hạn mức → làm bằng Haiku/phiên chính" nằm trong CLAUDE.md, nhưng **không có số liệu** để biết lúc nào sắp hết.

Kiểm trên máy (chỉ đọc): `~/.claude/settings.json` **chưa có** `statusLine` và chưa có `hooks`;
`~/.gemini/antigravity-cli/` chưa có `settings.json`; config deliberation để `sessions.persist: false`, dashboard tắt.

| Nhu cầu | Có chưa? |
|---|---|
| % cửa sổ 5 giờ / tuần của Claude Pro | Có sẵn trong `/usage` (VS Code: hộp Account & usage) – phải mở tay |
| Haiku subagent tốn bao nhiêu | Có sẵn: `/usage` → Attribution theo skill/subagent/plugin/MCP server |
| "Chi phí tương đương" theo ngày/model | **Chưa** – cần công cụ đọc log (ccusage…) |
| Hạn mức Codex (ChatGPT Free) | Có sẵn trong Codex (`/status`, `/usage`, `/statusline`) – nhưng gọi qua plugin thì Tuan không nhìn thấy |
| Hạn mức Gemini (`agy`, Google free) | Có sẵn `/usage` trong agy – gọi headless qua deliberation thì không thấy |
| 1 chỗ xem cả 3 + cảnh báo khi gần hết | **Chưa** – không có công cụ OSS nào đạt đủ ràng buộc (mục 2) |
| Tự chuyển việc sang agent khác khi gần hết | **Chưa** – không orchestrator nào đọc hạn mức để chuyển (mục 2) |

## 2. Bảng ứng viên

Ký hiệu hỗ trợ: C = Claude Code, X = Codex CLI, G = Gemini CLI, A = Antigravity (`agy`).

### 2a. Đọc log usage / dashboard

| Công cụ | Làm gì | ★ | Push / release | License | Windows | Gửi ra ngoài | Hỗ trợ | Kết luận |
|---|---|---|---|---|---|---|---|---|
| [ccusage/ccusage](https://github.com/ccusage/ccusage) | Báo cáo token + USD theo ngày/tuần/tháng/phiên; `blocks` = cửa sổ 5 giờ Claude | 19 177 | 2026-10-26 / v20.0.44 (2026-10-24) | GitHub: NOASSERTION; README + npm: MIT | Có (npm kèm binary `win32-x64`) | Giá nhúng lúc build; có `--offline`. Gọi mạng lúc chạy: TODO | C, X, G, A (+ ~15 CLI khác) | **Đề xuất** – báo cáo "chi phí tương đương", chạy tay |
| [getagentseal/codeburn](https://github.com/getagentseal/codeburn) | Token/chi phí theo tool, model, project, task, nhánh git; TUI, web, tray Windows, MCP | 11 578 | 2026-10-26 / npm 0.9.27 | MIT | Có (CLI Node ≥ 22.13 – máy có 24.15; app tray Windows) | CLI "sends nothing"; tải giá LiteLLM 1 lần/ngày; `codeburn quota` đăng nhập từng nhà cung cấp bằng credential sẵn có; app desktop có telemetry (hỏi đồng ý) | C, X, G, A (42 tool) | **Để sau** – thay ccusage nếu cần chia theo project/task. Không dùng `quota` |
| [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) | Token/chi phí nhiều agent; "Subscription Usage" hiện hạn mức nhà cung cấp trả về | 5 741 | 2026-10-26 / v4.20.1 (2026-10-23) | MIT | Có (binary Windows x64) | Giá LiteLLM; leaderboard chỉ khi `submit`; Subscription Usage **tự dò** credential OAuth rồi gọi endpoint hạn mức (tắt bằng `usage.disabledProviders` / `--offline`) | C, X, G, A (đọc thẳng `~/.gemini/antigravity-cli/conversations/*.db` – thư mục này có trên máy) | **Để sau** |
| [Piebald-AI/splitrail](https://github.com/Piebald-AI/splitrail) | Theo dõi token/chi phí thời gian thực, có MCP server | 225 | 2026-10-26 / v3.12.0 (2026-10-15) | MIT | Có (zip x86_64 msvc) | Splitrail Cloud opt-in (`auto_upload = false`) | C, X, G; A ghi trong mô tả repo nhưng README không liệt kê – TODO | **Để sau** – ít sao |
| [xiufengsun/TokenTracker](https://github.com/xiufengsun/TokenTracker) | Dashboard localhost:7680 + app tray | 2 130 | 2026-10-26 / v1.4.12 (2026-10-26) | MIT | Có | **Telemetry bật mặc định** (heartbeat + PostHog; tắt bằng `DO_NOT_TRACK=1`); kiểm hạn mức bằng credential; **tự cài hook** vào `settings.json` và `config.toml` của Codex | C, X, G, A | **Loại** – telemetry mặc định + tự sửa config |
| [Maciek-roboblog/Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) | TUI dự báo hết hạn mức Claude | 8 766 | 2026-07-05 / v4.0.0 (2026-06-27) | MIT | Có hướng dẫn cài PowerShell, không ghi đã test | `--api` (opt-in) gọi OAuth usage API | Chỉ C | **Loại** – Pro dùng **số ước tính cố định** 19 000 token / 18 USD (README tự mâu thuẫn ~44 000); số chính thức chỉ có qua statusline – trùng tính năng sẵn có |
| [ColeMurray/claude-code-otel](https://github.com/ColeMurray/claude-code-otel) | Stack OpenTelemetry + Grafana | 513 | 2025-06-17 | MIT | Docker | – | C | **Loại** – không cập nhật 2026 |
| [chiphuyen/sniffly](https://github.com/chiphuyen/sniffly) | Dashboard log Claude | 1 277 | 2025-08-08 | MIT | – | – | C | **Loại** – không cập nhật 2026 |
| [steipete/CodexBar](https://github.com/steipete/CodexBar) | Menu bar hạn mức Codex/Claude | 22 805 | 2026-10-24 / v0.81.0 | MIT | **Chỉ macOS** (Swift) | – | C, X | **Loại** |

### 2b. Statusline Claude Code

| Công cụ | Làm gì | ★ | Push / release | License | Windows | Gửi ra ngoài | Kết luận |
|---|---|---|---|---|---|---|---|
| [jarrodwatts/claude-hud](https://github.com/jarrodwatts/claude-hud) | Plugin: context, tool đang chạy, agent đang chạy, todo; 5 giờ/7 ngày từ `rate_limits` trên stdin | 28 883 | 2026-10-26 / v0.13.1 (2026-10-26) | MIT | Có (Node 18+) | Không: "local-only… never reads credentials, and calls no undocumented APIs" | **Đề xuất có điều kiện** – chỉ thấy khi bật terminal mode (mục 3) |
| [Owloops/claude-powerline](https://github.com/Owloops/claude-powerline) | Powerline; segment 5 giờ/tuần từ `rate_limits`; ngân sách cảnh báo 80 % | 1 175 | 2026-10-25 / v1.32.5 (2026-10-24) | MIT | README không nêu – TODO | Không nêu | **Để sau** – thay claude-hud |
| [sirmalloc/ccstatusline](https://github.com/sirmalloc/ccstatusline) | Statusline nhiều widget | 13 411 | 2026-10-19 / v2.2.32 (2026-10-09) | MIT | Có (docs/WINDOWS.md) | Widget usage **gọi thẳng API Anthropic** bằng credential đăng nhập | **Loại** cho phần hạn mức (rủi ro điều khoản, xem dưới) |
| [Tespera/cc-usage-statusline](https://github.com/Tespera/cc-usage-statusline) | Script shell 5 giờ/7 ngày | 0 | 2026-05-28 | MIT | macOS + Linux | Không | **Loại** – ít người dùng; chỉ mượn ý |

**Lưu ý điều khoản (quan trọng):** docs Anthropic ghi OAuth của gói Pro dành cho "ordinary use of Claude Code and other native
Anthropic applications" và "developers may not collect, store, or intermediate Claude.ai credentials or session tokens"
([legal-and-compliance](https://code.claude.com/docs/en/legal-and-compliance)). Công cụ đọc `~/.claude/.credentials.json`
để gọi endpoint hạn mức không công bố (ccstatusline usage, `codeburn quota`, tokscale Subscription Usage, TokenTracker,
Claude-Code-Usage-Monitor `--api`) → **không dùng**. Lấy số chính thức qua `rate_limits` mà Claude Code tự đưa cho statusline.

### 2c. Điều phối đa agent / đa CLI

Không công cụ nào dưới đây **đọc hạn mức để tự chuyển agent** – chỉ chạy song song nhiều phiên (worktree/tmux).

| Công cụ | ★ | Push / release | License | Windows | Gửi ra ngoài | Hỗ trợ | Kết luận |
|---|---|---|---|---|---|---|---|
| [smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad) | 8 668 | 2026-08-20 / v1.0.20 | AGPL-3.0 | Có zip Windows nhưng **cần tmux + gh** → thực tế WSL (TODO) | Không nêu | C, X, G, Aider | **Loại** – tmux, không quota |
| [kbwo/ccmanager](https://github.com/kbwo/ccmanager) | 1 274 | 2026-10-26 / v4.4.9 (2026-10-18) | MIT | Không cần tmux; README có đường dẫn `%APPDATA%` nhưng không ghi rõ hỗ trợ – TODO | Không nêu | C, G, X, Cursor, Copilot… | **Để sau** – có hook đổi trạng thái phiên, không quota |
| [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) | 40 266 | 2026-10-26 / v5.7.15 (2026-10-25) | MIT | Có (psmux) | Mặc định không (callback Telegram/Discord nếu cấu hình) | C + worker Codex/agy qua tmux | **Loại** – cài 19 agent + hook + "smart routing" đè kiến trúc 3 tầng, giống lý do không chạy `/deliberation:setup`; `omc wait` (tự chạy lại khi hết hạn mức) Claude Code đã có sẵn |
| [OrchestratorInc/agent-orchestrator](https://github.com/OrchestratorInc/agent-orchestrator) | 13 649 | 2026-10-26 / v0.14.6 (2026-10-24) | Apache-2.0 | Có (installer) | **Telemetry bật mặc định**, kèm GitHub username | ~30 agent (C, X, G, "Agy") | **Loại** – telemetry, nặng, không quota |
| [BloopAI/vibe-kanban](https://github.com/BloopAI/vibe-kanban) | 28 456 | 2026-09-19 / 2026-04-24 | Apache-2.0 | Có installer | PostHog | C, X, G… | **Loại** – README: "Vibe Kanban is sunsetting" |
| [standardagents/dmux](https://github.com/standardagents/dmux) | 1 808 | 2026-08-16 / v5.11.1 | MIT | tmux | – | C, X, G… | **Loại** – tmux |
| [asheshgoplani/agent-deck](https://github.com/asheshgoplani/agent-deck) | 1 157 | 2026-10-25 / v1.16.34 | MIT | Release chỉ darwin/linux | – | C, G, X… | **Loại** |
| [agent-of-empires/agent-of-empires](https://github.com/agent-of-empires/agent-of-empires) | 3 384 | 2026-10-25 / v1.21.0 | MIT | Release chỉ darwin/linux | – | C, X, G… | **Loại** |

## 3. Tính năng có sẵn – dùng trước (không cần cài)

**Claude Code** (docs: [costs](https://code.claude.com/docs/en/costs), [vs-code](https://code.claude.com/docs/en/vs-code), [statusline](https://code.claude.com/docs/en/statusline), [hooks](https://code.claude.com/docs/en/hooks), [interactive-mode](https://code.claude.com/docs/en/interactive-mode), [sub-agents](https://code.claude.com/docs/en/sub-agents)):
- `/usage` trong VS Code → hộp **Account & usage**: thanh % phiên (5 giờ) và tuần + giờ reset; **Attribution** theo skill,
  subagent, plugin, MCP server (thấy ngay Haiku agent và deliberation chiếm bao nhiêu); **Recommendations** + nút Fix; Day/Week.
  Số liệu ước tính từ phiên trên máy này. Dòng USD của Session block = giá API list → đây chính là "chi phí tương đương", không phải tiền phải trả.
- **Statusline** nhận `rate_limits.five_hour/seven_day.used_percentage` + `resets_at` (chỉ Pro/Max, sau phản hồi đầu tiên).
  Trên Windows chạy qua Git Bash nếu có (đường dẫn dùng `/`). **Nhưng**: panel đồ họa VS Code không hiển thị statusline
  tùy biến (issue [#20207](https://github.com/anthropics/claude-code/issues/20207), [#21265](https://github.com/anthropics/claude-code/issues/21265),
  [77829](https://claudeissues.com/issue/77829-feature-request-render-the-custom-statusline-in-the-vs-code-extension-panel-pari)) – chỉ thấy ở
  **terminal mode** (`claudeCode.useTerminal`). Lệnh có chạy ngầm ở panel hay không: các báo cáo mâu thuẫn – TODO.
- **Tự chạy tiếp khi hạn mức reset** (mặc định bật từ v2.1.234), `/rate-limit-options` để chọn/hủy.
- **Hook** `StopFailure` matcher `rate_limit` (lượt bị dừng vì hạn mức) và `Notification` matcher `quota_auto_resume_*` →
  có thể bắn toast Windows hoặc ghi 1 dòng log. Input hook **không** có `rate_limits`.
- Subagent: `model: haiku` trong frontmatter (đang dùng). `CLAUDE_CODE_SUBAGENT_MODEL` chỉ là mặc định; **không** bật
  `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` (ép cả Explore/Plan xuống một model).
- `/context`, `/effort`, `/insights` (báo cáo HTML `~/.claude/usage-data/report.html`; tốn hạn mức khi chạy).

**Codex CLI 0.164.0** ([slash commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [pricing](https://learn.chatgpt.com/docs/pricing)):
`/status` (token phiên), `/usage daily|weekly|cumulative`, `/statusline` chọn item "limits" (lưu `tui.status_line` trong `config.toml`);
web: chatgpt.com/codex/settings/usage. OpenAI **không công bố** hạn mức gói Free.
Log cục bộ `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` có khối `rate_limits` – trên máy Tuan (2026-10-26):
`plan_type: "free"`, `primary.window_minutes: 43200` (= 30 ngày), `used_percent: 0.0`, `secondary: null`.
Trường này **không có trong docs** → có thể đổi.

**Antigravity CLI `agy` 1.4.7** ([/usage](https://antigravity.google/docs/cli/commands/usage), [statusline](https://antigravity.google/docs/cli/statusline)):
`/usage` (alias `/quota`) – hạn mức còn lại theo từng model. Statusline (`~/.gemini/antigravity-cli/settings.json`, Windows chạy `cmd /c`)
nhận object `quota` {`remaining_fraction`/`remaining_amount`, `reset_time`, `reset_in_seconds`}. Cộng đồng báo `/usage` có lúc
không cập nhật tới khi mở lại agy ([diễn đàn](https://discuss.ai.google.dev/t/the-usage-command-not-working/146647)).

**deliberation** `analyze` (latency/token theo model) – đang dùng; với `sessions.persist: false` có thể không có dữ liệu – TODO.

## 4. Đề xuất (xếp theo lợi/công)

| # | Việc | Lợi | Công | Đánh đổi |
|---|---|---|---|---|
| 1 | **Dùng đồ có sẵn**: `/usage` đầu + cuối buổi (xem Attribution); Codex `/statusline` bật "limits"; agy `/usage` khi mở tay. Thêm 1 hook `StopFailure: rate_limit` → toast PowerShell + 1 dòng log | Biết % thật, chính thức, 0 đồng, không rủi ro điều khoản | ~15 phút (hook phải sửa `~/.claude/settings.json`, có backup) | Vẫn thủ công, 3 nơi riêng; Codex/agy gọi qua plugin thì không ai nhìn statusline |
| 2 | **ccusage** ghim `20.0.44`, chạy tay: `npx ccusage@20.0.44 daily --offline`, `... codex daily` | 1 bảng "chi phí tương đương" theo ngày/model gồm Opus, Haiku, Codex, Antigravity → thấy tầng 2/3 tiết kiệm bao nhiêu | Thấp, không cài thường trú | USD theo giá API list, không phải hạn mức Pro; `blocks` 5 giờ chỉ ước tính. License GitHub NOASSERTION (README/npm ghi MIT). Muốn chia theo project/task → codeburn CLI (không dùng `quota`, không cài app desktop) |
| 3 | **Script STLab nhỏ** `tools/quota-snapshot/` (tự viết, không cài OSS): statusline Claude + statusline agy chỉ ghi `rate_limits`/`quota` ra JSON cục bộ; đọc thêm `rate_limits` trong log Codex; `quota.ps1` in 3 dòng; tùy chọn hook `UserPromptSubmit` chèn 1 câu khi Claude 5 giờ > 80 % để phiên chính tự đẩy việc chữ sang `doc-writer`/`ask-gemini` | Gần nhất với "điều phối theo hạn mức" mà không orchestrator OSS nào làm được | Trung bình (~1 buổi + kiểm) | Tự bảo trì; trường Codex không công bố; statusline Claude có chạy ở panel VS Code không – **phải thử trước** (TODO); agy headless có thể không chạy statusline |
| 4 | *(để sau)* **claude-hud** nếu Tuan chịu dùng terminal mode | Đẹp, local-only, thấy cả agent đang chạy | Thấp (plugin) | Mất panel đồ họa (diff inline, duyệt plan); chỉ Claude, không Codex/agy |

Điều phối đa agent: **giữ deliberation + quy tắc CLAUDE.md**. Orchestrator OSS hiện chỉ chạy song song phiên, không đọc hạn mức,
phần lớn cần tmux hoặc có telemetry mặc định. ccmanager là ứng viên duy nhất đáng xem lại nếu cần chạy song song nhiều phiên trên Windows.

## 5. Điểm chưa xác nhận (TODO)
- Statusline Claude Code có **chạy lệnh** trong panel VS Code (không hiển thị) không → quyết định đề xuất 3 làm được tới đâu.
- agy chạy headless (qua deliberation) có gọi statusline không; tên bucket `quota` thật của tài khoản free.
- Hạn mức Codex Free: cửa sổ 43 200 phút (30 ngày) chỉ là quan sát log 1 lần; OpenAI không công bố số.
- Hạn mức tuyệt đối gói Pro (số token/tin nhắn): Anthropic không công bố, chỉ có %.
- ccusage: có gọi mạng lúc chạy khi không `--offline` không; đường dẫn đọc của nguồn Antigravity.
- splitrail có hỗ trợ Antigravity CLI không (mô tả repo có, README không).
- claude-powerline, ccmanager chạy Windows native không.
- deliberation `analyze` có dữ liệu không khi `sessions.persist: false`.

## Nguồn
- Claude Code docs: https://code.claude.com/docs/en/costs · /statusline · /vs-code · /hooks · /interactive-mode · /sub-agents · /legal-and-compliance
- Codex: https://learn.chatgpt.com/docs/developer-commands?surface=cli · https://learn.chatgpt.com/docs/pricing
- Antigravity CLI: https://antigravity.google/docs/cli/commands/usage · https://antigravity.google/docs/cli/statusline
- Diễn đàn agy `/usage`: https://discuss.ai.google.dev/t/the-usage-command-not-working/146647 , https://discuss.ai.google.dev/t/gemini-cli-antigravity-cli-day-1-impressions-only-updates-usage-after-quit-and-reload/146374
- Issue statusline VS Code: https://github.com/anthropics/claude-code/issues/20207 , https://github.com/anthropics/claude-code/issues/21265
- README các repo trong bảng mục 2 (link ở cột tên); số liệu repo: `api.github.com/repos/<owner>/<repo>` và `/releases/latest`; npm: `registry.npmjs.org/<pkg>/latest`
