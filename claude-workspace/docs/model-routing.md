# Phân việc theo model – Claude làm CAD khó, model free làm việc dễ

Quyết định của Tuan (2026-10-26): **chỉ trả Claude Pro**, mọi thứ khác miễn phí. Gemini nếu cần chỉ mua gói
Google AI Pro (thuê bao người dùng), không trả tiền API. Không chạy model local.

Quy tắc ngắn (ai làm gì, cấm gửi gì) nằm trong `claude-workspace/CLAUDE.md` mục "Phân việc theo model".
File này ghi cách cài, cách dùng, lý do chọn và cách gỡ.

## Kiến trúc

| Tầng | Công cụ | Tốn gì | Việc |
|---|---|---|---|
| 1 | Claude Opus (phiên chính) | Quota Claude Pro | CAD, khe/dung sai, động học, quyết định |
| 2 | Subagent `check-runner`, `doc-writer`, `git-scribe` (`model: haiku`) | Quota Claude Pro, ít hơn Opus nhiều | Chạy kiểm, viết file, commit – giữ log/diff dài ngoài phiên chính |
| 3a | PAL MCP → **Gemini API key free** (`gemini-3.8-flash`, `gemini-3.5-flash-lite`) | 0 đ (hạn mức free của Google) | Viết nháp tiếng Việt, tóm tắt tài liệu dài, review lần 2 |
| 3b | Plugin **Codex chính hãng** (`openai/codex-plugin-cc`) + tài khoản **ChatGPT Free** | 0 đ (hạn mức Codex của gói Free) | `/codex:review`, `/codex:adversarial-review` cho script Python/FreeCAD |

Phần tiết kiệm chính là **tầng 2**: phiên Opus không phải đọc log `prepare-print`, diff dài hay bản nháp tài liệu.
Tầng 3 bớt thêm phần viết chữ và review.

## Việc Tuan tự làm (một lần)

Key và đăng nhập **không** đi qua chat hay file trong repo.

1. **Gemini API key free**
   - Vào <https://aistudio.google.com> → *Get API key* → tạo key (không cần thẻ).
   - Đặt biến môi trường người dùng (PowerShell):
     `[Environment]::SetEnvironmentVariable('GEMINI_API_KEY','<key>','User')`
   - Đóng hết VS Code / Claude Code rồi mở lại (tiến trình cũ không thấy biến mới).
   - Kiểm: trong Claude Code gõ `/mcp` → `pal` phải là *connected*.
   - Hạn mức thật của project xem tại <https://aistudio.google.com/rate-limit> (Google không công bố số chung;
     nguồn bên thứ ba 2026-10 nói khoảng 10 request/phút, vài trăm–1.500 request/ngày cho bản Flash – `TODO` xác nhận).
2. **Codex (ChatGPT Free)**
   - Mở terminal: `codex login` → đăng nhập bằng tài khoản ChatGPT trong trình duyệt.
   - Trong Claude Code: `/codex:setup` để kiểm. **Không bật** "stop review gate" (mặc định tắt).
   - Hạn mức gói Free OpenAI không công bố; hết thì đợi hoặc bỏ qua bước review.

## Cách dùng hằng ngày

- Sửa model xong (đã Lưu) → Claude giao `check-runner`: nhận PASS/WARN/FAIL + đường dẫn ảnh.
- Cần viết README / phần văn xuôi ASSEMBLY / ghi chú → Claude đưa gạch đầu dòng cho `doc-writer`.
- Kiểm đạt → `git-scribe` commit + push.
- Script Python lớn trước khi commit → `/codex:review` (chỉ đọc), hoặc PAL `codereview`.
- Tài liệu/trang dài > ~300 dòng → PAL `chat` tóm tắt trước, Claude chỉ đọc bản tóm tắt.

## Thành phần đã cài

| Thành phần | Nơi | Ghi chú |
|---|---|---|
| PAL MCP v9.8.2 | `community/beehiveinnovations-pal-mcp-server` (ghim `pins.tsv`) | Bản cuối 2025-12-15, repo không cập nhật từ đó |
| Python env cho PAL | `custom/pal-mcp/.venv` (không lên git) | Thư viện khóa theo ngày phát hành: `custom/pal-mcp/requirements.lock.txt` (`uv pip compile --exclude-newer 2025-12-16`) |
| Danh mục Gemini | `custom/pal-mcp/gemini-models.json` | Thay danh mục cũ trong bản ghim (chỉ có Gemini 2.x) |
| Đăng ký MCP `pal` | `~/.claude.json` (cấp user) | Bật chỉ `chat`, `consensus`, `codereview` (+ `listmodels`, `version`) |
| Codex CLI 0.164.0 | `npm install -g @openai/codex@0.164.0` | CLI chính hãng OpenAI |
| Plugin Codex v1.0.6 | `community/openai-codex-plugin-cc` → marketplace cục bộ `openai-codex`, plugin `codex@openai-codex` (user) | Claude đọc thẳng từ bản ghim |
| 3 agent | `custom/agents/*.md` → symlink `~/.claude/agents/` (`links.tsv`) | `model: haiku` |

Lệnh đăng ký PAL (để dựng lại trên máy mới; `<W>` = đường dẫn `claude-workspace`):

```powershell
claude mcp add -s user pal `
  -e DEFAULT_MODEL=flash `
  -e "GEMINI_MODELS_CONFIG_PATH=<W>\custom\pal-mcp\gemini-models.json" `
  -e "GOOGLE_ALLOWED_MODELS=gemini-3.8-flash,gemini-3.5-flash-lite" `
  -e "DISABLED_TOOLS=clink,thinkdeep,planner,precommit,debug,secaudit,docgen,analyze,refactor,tracer,testgen,challenge,apilookup" `
  -e LOG_LEVEL=WARNING -e PYTHONIOENCODING=utf-8 `
  -- "<W>\custom\pal-mcp\.venv\Scripts\python.exe" "<W>\community\beehiveinnovations-pal-mcp-server\server.py"
```

Dựng lại venv: `uv venv --python 3.12 custom/pal-mcp/.venv` rồi
`uv pip install --python custom/pal-mcp/.venv/Scripts/python.exe -r custom/pal-mcp/requirements.lock.txt`.

## Đổi model

- Google ra Flash mới: thêm mục vào `custom/pal-mcp/gemini-models.json` (ID lấy ở
  <https://ai.google.dev/gemini-api/docs/models>), sửa `GOOGLE_ALLOWED_MODELS` (gỡ + đăng ký lại MCP), mở lại Claude Code.
- Giữ `supports_extended_thinking: false` (PAL bản 2025 gửi `thinking_budget` kiểu Gemini 2.x).

## Vì sao chọn như vậy (2026-10-26)

| Phương án | Kết luận |
|---|---|
| Gateway (claude-code-router, LiteLLM) | Loại: đổi `ANTHROPIC_BASE_URL` → Claude tính phí theo API, không dùng gói Pro |
| OpenRouter | Loại: trả theo token; bản `:free` chỉ 50 request/ngày |
| Model local (Ollama) | Loại theo Tuan; máy GTX 1660 Super 6 GB chỉ chạy tốt model ~4B |
| Gemini qua Antigravity CLI (`agy`) + gemini-mcp-tool | Để sau (khi mua Google AI Pro): bridge còn thử nghiệm, chế độ `-p` **không sandbox** (agent tự chạy lệnh trong workspace CAD), hạn mức tuần không công bố |
| Grok (Grok Build qua cc-multi-cli-plugin, 193★) | Để sau: hạn mức free không công bố, repo tích hợp nhỏ |
| ChatGPT API, GitHub Models, Qwen OAuth, Cerebras free | Không có/đã dừng gói free |
| claude-delegator | Loại: đã archive |
| OmniRoute, gpt4free | Loại: có tuyến dùng cookie web/giả vân tay TLS – rủi ro vi phạm điều khoản |

Khi mua Google AI Pro: cài `agy` (`irm https://antigravity.google/cli/install.ps1 | iex`) + gemini-mcp-tool,
chỉ cho chạy trong thư mục nháp tách khỏi workspace.

## Gỡ bỏ

```powershell
claude mcp remove pal -s user
claude plugin uninstall codex@openai-codex
claude plugin marketplace remove openai-codex
npm uninstall -g @openai/codex
[Environment]::SetEnvironmentVariable('GEMINI_API_KEY',$null,'User')
```

Agent: xóa 3 dòng trong `community/links.tsv` rồi xóa symlink trong `~/.claude/agents/`.
