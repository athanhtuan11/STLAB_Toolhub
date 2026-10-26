# Phân việc theo model – Claude làm CAD khó, model free làm việc dễ

Quyết định của Tuan (2026-10-26): **chỉ trả Claude Pro**, mọi thứ khác miễn phí. Gemini nếu cần chỉ mua gói
Google AI Pro (thuê bao người dùng), không trả tiền API. Không chạy model local. Chọn nguồn cộng đồng **còn cập nhật
đều** (PAL MCP bị loại vì dừng từ 2025-12).

Quy tắc ngắn (ai làm gì, cấm gửi gì) nằm trong `claude-workspace/CLAUDE.md` mục "Phân việc theo model".
File này ghi cách cài, cách dùng, lý do chọn và cách gỡ.

## Kiến trúc

| Tầng | Công cụ | Tốn gì | Việc |
|---|---|---|---|
| 1 | Claude Opus (phiên chính) | Quota Claude Pro | CAD, khe/dung sai, động học, quyết định |
| 2 | Subagent `check-runner`, `doc-writer`, `git-scribe` (`model: haiku`) | Quota Claude Pro, ít hơn Opus nhiều | Chạy kiểm, viết file, commit – giữ log/diff dài ngoài phiên chính |
| 3a | Plugin **deliberation** → Gemini qua **Antigravity CLI `agy`** (đăng nhập tài khoản Google) | 0 đ (hạn mức tuần của gói free; Google AI Pro thì nạp lại mỗi 5 giờ) | Viết nháp tiếng Việt, tóm tắt tài liệu dài, `consensus` Gemini + GPT |
| 3b | Plugin **Codex chính hãng** (`openai/codex-plugin-cc`) + tài khoản **ChatGPT Free** | 0 đ (hạn mức Codex gói Free, không công bố) | `/codex:review`, `/codex:adversarial-review` cho script Python/FreeCAD |

Phần tiết kiệm chính là **tầng 2**: phiên Opus không phải đọc log `prepare-print`, diff dài hay bản nháp tài liệu.
Tầng 3 bớt thêm phần viết chữ và review.

## An toàn – vì sao gọi Gemini kiểu này

- `agy` là agent. Trên **Windows không có sandbox hệ điều hành** (Seatbelt của deliberation chỉ có trên macOS);
  `--sandbox` của agy chỉ chặn lệnh terminal, không chặn công cụ sửa file (ghi chú trong `server/gemini/index.js`).
  Còn lại: lời nhắc "READ-ONLY", xóa biến môi trường dạng key/token, **phát hiện** thay đổi git (không tự hoàn tác).
- Lớp thêm của STLab:
  1. Bộ điều phối deliberation (`ask-gemini`, `consensus`, `ask-all`…) **luôn chỉ đọc** – khóa `allowImplement`
     không bật ở đâu cả.
  2. Đường ghi duy nhất (tool `gemini` của server `deliberation-gemini`, `sandbox: workspace-write` →
     `--dangerously-skip-permissions`) bị chặn bằng `permissions.deny` trong `~/.claude/settings.json`,
     cùng server grok/openrouter không dùng.
  3. agy chỉ thấy **bản chép**: file cần đọc chép vào `D:\04_Stlab\agy-scratch\<ten-viec>\` (ngoài repo), `cwd` = thư
     mục đó, xong xóa. Không dùng tham số `files` cho Gemini: mô tả tool ghi "inlined" nhưng mã
     (`core/providers/antigravity.js`) chỉ chuyển `dir` thành `--add-dir`, bỏ qua `path` → agy cố chạy lệnh tìm file,
     bị chặn ở chế độ headless, không trả kết quả (thử 2026-10-26). Prompt dài cũng không nhét được vì Windows giới
     hạn dòng lệnh ~32.000 ký tự.
  4. **Không** chạy `/deliberation:setup`: nó cài `~/.claude/rules/deliberation/` bắt Claude "quét MỌI tin nhắn và
     tự giao việc" → tốn token, tự gửi dữ liệu ra ngoài. Config tự viết (dưới).
- Bản free của Gemini/ChatGPT: dữ liệu có thể được dùng để cải tiến dịch vụ → chỉ gửi tài liệu kỹ thuật/mã nguồn.

## Việc Tuan tự làm (một lần)

1. ~~**Gemini (agy)**: `agy` → đăng nhập Google → `/exit`~~ – **xong 2026-10-26**. agy ở
   `%LOCALAPPDATA%\agy\bin\agy.exe` 1.4.7 (đã thêm PATH; cửa sổ cmd mở trước đó phải mở lại), **tự cập nhật ngầm**.
   Tài khoản free có: Gemini 3.8 Flash (low/medium/high), Claude Sonnet/Opus 4.6, GPT-OSS 120B (`agy models`).
2. ~~**Codex**: `codex login`~~ – **xong 2026-10-26** (ChatGPT). Trong Claude Code: `/codex:setup` để kiểm,
   **không bật** "stop review gate".
3. ~~Đóng hết VS Code / Claude Code rồi mở lại~~ – **xong 2026-10-26**.
4. ~~Kiểm tên tool~~ – **xong 2026-10-26**: tool thật là `mcp__plugin_deliberation_deliberation__<tool>` (vd. `ask-gemini`)
   → khớp dòng `tools:` của `doc-writer`; server `deliberation-gemini/-grok/-openrouter` không hiện trong phiên (luật
   `deny` có tác dụng).

Lỗi "agy (Antigravity CLI) not on PATH" khi gọi từ Claude Code (2026-10-26, `doc-writer`): VS Code mở bằng môi trường cũ,
chưa thấy PATH mà trình cài agy thêm vào → đã đặt biến người dùng `AGY_BIN=%LOCALAPPDATA%\agy\bin\agy.exe`
(deliberation đọc biến này). Cần **đóng hết VS Code rồi mở lại** một lần. Gỡ: xóa biến `AGY_BIN`.

Thử thật qua MCP (2026-10-26): `ask-gpt` 12 s đúng; `ask-gemini` không file 7 s; `ask-gemini` đọc bản chép
`model-routing.md` 20 s, tóm tắt đúng ý nhưng có câu nói quá ("an toàn tuyệt đối") → bản nháp luôn phải duyệt.
Repo và bản chép không bị ghi.
Sau khi mở lại VS Code (2026-10-26 chiều): `ask-gemini` 10 s (`gemini-3.8-flash-medium`), `ask-gpt` 16 s – gọi thẳng
từ Claude Code, không còn lỗi PATH; `agy-scratch` trống, repo không bị ghi. Kiểm phiên bản cùng ngày: deliberation
v3.31.0, codex-plugin-cc v1.0.6, Codex CLI 0.164.0, agy 1.4.7 – đều là bản mới nhất.

## Cách dùng hằng ngày

- Sửa model xong (đã Lưu) → Claude giao `check-runner`: nhận PASS/WARN/FAIL + đường dẫn ảnh.
- Cần viết README / phần văn xuôi ASSEMBLY / ghi chú → Claude đưa gạch đầu dòng cho `doc-writer`.
- Kiểm đạt → `git-scribe` commit + push.
- Script Python lớn trước khi commit → `/codex:review` (chỉ đọc).
- Phân vân thiết kế code → deliberation `consensus` (Gemini + GPT, `maxFanout` 2).
- Tài liệu/trang dài > ~300 dòng → `ask-gemini` tóm tắt trước, Claude chỉ đọc bản tóm tắt.
- Hết hạn mức (agy tuần, Codex) → làm bằng Haiku/phiên chính; không chuyển sang dịch vụ trả phí.

### Xem hạn mức (Tuan chọn 2026-10-26: dùng đồ có sẵn – báo cáo `docs/reports/ai-resource-management-oss.md`)

| Agent | Xem ở đâu | Khi nào |
|---|---|---|
| Claude Pro | `/usage` trong Claude Code → % cửa sổ 5 giờ + tuần, giờ reset; mục **Attribution** cho biết subagent/plugin nào tốn | Đầu và cuối buổi |
| Codex (ChatGPT Free) | `codex` → `/status`; `/statusline` bật mục *limits* (lưu `config.toml`) | Khi hay dùng `/codex:review` |
| Gemini (agy) | `agy` → `/usage` (hay `/quota`) – còn lại theo từng model | Khi `doc-writer`/`ask-gemini` chậm hoặc lỗi |

Statusline hiện hạn mức ngay dưới ô nhập (Tuan 2026-10-26; chỉ thấy khi mở **TUI** `codex` / `agy`, không áp dụng khi
Claude gọi qua plugin):
- **Codex**: `~/.codex/config.toml` → `[tui] status_line = ["model-with-reasoning", "context-remaining",
  "five-hour-limit", "daily-limit", "weekly-limit", "monthly-limit"]` (tên mục lấy từ chính Codex CLI 0.164.0; mục
  không áp dụng cho gói thì tự ẩn – gói Free hiện là cửa sổ 30 ngày). Đổi/sắp xếp: gõ `/statusline` trong `codex`.
- **agy**: `~/.gemini/antigravity-cli/settings.json` → `statusLine` chạy `custom/statusline/agy_statusline.py`,
  `stack_with_default: true` (giữ dòng mặc định, thêm dòng "con lại: ctx …% | <hạn mức> …% reset …"; xanh > 50 %,
  vàng > 20 %, đỏ ≤ 20 %). Chưa có dữ liệu hạn mức thì hiện "chưa có (gõ /usage)". Tắt: `/statusline` → disable.
- Claude Code: statusline tùy biến không hiện trong panel VS Code (TODO trong báo cáo) → dùng `/usage`.

Hook tự động (`~/.claude/settings.json`, bản lưu `settings.json.bak-2026-10-26-hooks`; mã `custom/hooks/usage_alert.py`):
- `StopFailure` matcher `rate_limit` → bong bóng thông báo Windows "Claude chạm hạn mức – chuyển việc chữ sang
  doc-writer / ask-gemini" + 1 dòng log.
- `Notification` matcher `^quota_auto_resume_` (tự chạy tiếp khi reset / bỏ chờ) → 1 dòng log.
- Log: `%USERPROFILE%\.claude\usage-log\rate-limit.log` (giờ, sự kiện, loại, thư mục). Chỉ ghi máy, không gọi mạng.
- Viết bằng Python vì Windows đang ở ExecutionPolicy mặc định (chặn file `.ps1`) – không nới chính sách.
- Gỡ: xóa 2 mục `StopFailure`/`Notification` trong `hooks` (hoặc chép lại bản `.bak`).

## Thành phần đã cài

| Thành phần | Nơi | Ghi chú |
|---|---|---|
| deliberation v3.31.0 | `community/antonbabenko-deliberation` (ghim `pins.tsv`) → marketplace cục bộ `antonbabenko-deliberation`, plugin `deliberation@antonbabenko-deliberation` (user) | MIT, Node thuần (không phụ thuộc npm), phát hành đều từ 2026-05 |
| Config deliberation | `%APPDATA%\deliberation\config.json` | Bật `codex` + `gemini` (ghim `gemini-3.8-flash-medium`: alias mặc định `auto-gemini-3` không còn trong `agy models`); tắt grok/openrouter/ollama/lmstudio, dashboard, `orientation` (tự đọc 6 file trong cwd), `sessions.persist` |
| Antigravity CLI 1.4.7 | `%LOCALAPPDATA%\agy\bin` | Script cài chính hãng (đã đọc, kiểm SHA-512), tự cập nhật |
| Thư mục nháp | `D:\04_Stlab\agy-scratch` | `cwd` cho agy, giữ trống |
| Codex CLI 0.164.0 | `npm install -g @openai/codex@0.164.0` | CLI chính hãng OpenAI |
| Plugin Codex v1.0.6 | `community/openai-codex-plugin-cc` → plugin `codex@openai-codex` (user) | Claude đọc thẳng từ bản ghim |
| Luật chặn | `~/.claude/settings.json` `permissions.deny` (bản lưu `settings.json.bak-2026-10-26`) | Server `deliberation-gemini/-grok/-openrouter` |
| 3 agent | `custom/agents/*.md` → symlink `~/.claude/agents/` (`links.tsv`) | `model: haiku` |

Config deliberation (dựng lại trên máy mới, chép nguyên):

```json
{
  "version": 1,
  "providers": {
    "defaults": { "timeout": 600000 },
    "codex": { "enabled": true },
    "gemini": { "enabled": true, "model": "gemini-3.8-flash-medium" },
    "grok": { "enabled": false, "apiKeyEnv": "XAI_API_KEY", "model": "grok-4.6" },
    "openrouter": { "enabled": false, "apiKeyEnv": "OPENROUTER_API_KEY", "apiBase": "https://openrouter.ai/api/v1", "defaultModel": "openrouter/auto" },
    "ollama": { "enabled": false, "apiBase": "http://localhost:11434/v1" },
    "lmstudio": { "enabled": false, "apiBase": "http://localhost:1234/v1" }
  },
  "routing": { "maxFanout": 2, "timeoutPolicy": "longest-peer" },
  "sessions": { "persist": false, "maxRecords": 200, "maxAgeDays": 30, "captureText": false },
  "orientation": { "enabled": false, "maxFiles": 6, "maxBytes": 16000 },
  "dashboard": { "enabled": false, "capture": "metadata", "showPII": false, "port": 7717, "maxRuns": 200, "maxAgeDays": 30 }
}
```

## Vì sao chọn như vậy (2026-10-26)

| Phương án | Kết luận |
|---|---|
| Gateway (claude-code-router, LiteLLM) | Loại: đổi `ANTHROPIC_BASE_URL` → Claude tính phí theo API, không dùng gói Pro |
| OpenRouter | Loại: trả theo token; bản `:free` chỉ 50 request/ngày |
| Model local (Ollama) | Loại theo Tuan; máy GTX 1660 Super 6 GB chỉ chạy tốt model ~4B |
| PAL MCP + Gemini API key free | Đã cài rồi **gỡ** cùng ngày: mã dừng từ 2025-12-15, lỗi bảo mật mới báo chưa ai vá; fork còn sống đều 0–3★ |
| deliberation + agy (**đang dùng**) | Cập nhật đều; Gemini qua tài khoản Google (khớp hướng mua Google AI Pro); bộ điều phối luôn chỉ đọc |
| Proxima | Loại: dùng phiên web (README tự nhận có thể vi phạm ToS), license chỉ cá nhân |
| ask-llm | Loại: chỉ Linux/macOS |
| Grok (Grok Build) | Để sau: hạn mức free không công bố; deliberation hỗ trợ Grok qua `XAI_API_KEY` (trả phí) |
| ChatGPT API, GitHub Models, Qwen OAuth, Cerebras free | Không có/đã dừng gói free |
| claude-delegator | Loại: đã archive |
| OmniRoute, gpt4free | Loại: có tuyến cookie web/giả vân tay TLS – rủi ro vi phạm điều khoản |

## Gỡ bỏ

```powershell
claude plugin uninstall deliberation@antonbabenko-deliberation
claude plugin marketplace remove antonbabenko-deliberation
claude plugin uninstall codex@openai-codex
claude plugin marketplace remove openai-codex
npm uninstall -g @openai/codex
Remove-Item -Recurse "$env:APPDATA\deliberation", "$env:LOCALAPPDATA\agy", "D:\04_Stlab\agy-scratch"
```

Rồi: xóa 3 luật `deny` `mcp__plugin_deliberation_*` trong `~/.claude/settings.json`, bỏ `%LOCALAPPDATA%\agy\bin`
khỏi PATH người dùng, xóa 3 dòng agent trong `community/links.tsv` + symlink trong `~/.claude/agents/`.
