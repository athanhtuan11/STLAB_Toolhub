# Agent / nguồn model miễn phí mới – 2026-11-04

Tuan 2026-11-04: "tìm thêm agent free". Codex (ask-gpt) tra web, Claude kiểm GitHub API. Chưa cài gì mới ngoài Goose.

## 1. Goose – đã ghép vào delegate (thử việc)

- Goose 1.57.0 + Gemini API free (key AI Studio). Selftest tay 2026-11-04 trong `D:\04_Stlab\agy-scratch\goose-selftest`:
  - `gemini-2.5-flash`: **404 – đã ngừng cho người dùng mới**.
  - `gemini-3.8-flash`: **503 quá tải** (thử 1 lần).
  - `gemini-flash-latest`: lỗi sau 351 s.
  - `gemini-3.5-flash`: **PASS** (tạo `hello.py` in `STLAB OK`).
- Ghim `gemini-3.5-flash` trong `org/agents.yaml`, `trang_thai: thu-viec` → chỉ chạy khi spec ghi `executor: goose`,
  luôn trong git worktree (Goose không giới hạn thư mục).
- Hạn mức free Gemini API: `TODO` (xem ở AI Studio). Biến môi trường người dùng `GOOSE_MODEL=gemini-2.5-flash` đã lỗi thời
  – adapter truyền `--model` từ org nên không ảnh hưởng delegate; khi chạy Goose bằng tay nên đổi biến này.

## 2. Ứng viên mới

| Tên | Repo (kiểm API 2026-11-04) | Miễn phí | Headless | Kết luận |
|---|---|---|---|---|
| Pi coding agent | https://github.com/earendil-works/pi (cũ badlogic/pi-mono) – 119.852 sao, MIT, push 2026-11-03 | CLI miễn phí, **không kèm model** – cần nguồn model riêng | `pi --print "..."` (Codex tra, chưa thử) | Dự phòng cho Goose; nếu dùng Gemini API free thì **chung hạn mức key** với Goose → lợi ít |
| Agent Code | https://github.com/avala-ai/agent-code – 35 sao, MIT, push 2026-11-03 | CLI miễn phí, không kèm model | `agent -p "..."` | Loại: quá ít người dùng |
| Claude Code `-p` | anthropics/claude-code | Dùng chung quota Claude Pro | có | Không phải nguồn mới – không tiết kiệm |

## 3. Nguồn model miễn phí (cho OpenCode/Goose)

| Nguồn | Miễn phí | Kết luận |
|---|---|---|
| Cloudflare Workers AI | 10.000 Neurons/ngày, reset 00:00 UTC; một số model cần trả phí (https://developers.cloudflare.com/workers-ai/platform/pricing/) | ★ Ứng viên duy nhất có hạn mức free định kỳ rõ ràng. Cần Tuan tạo tài khoản + API token; tool-calling với OpenCode/Goose: `TODO` thử |
| NVIDIA NIM | "Miễn phí để prototype", hạn mức `TODO` (https://docs.api.nvidia.com/nim/docs/product) | Chờ, không rõ số |
| Hugging Face Inference | Tài khoản free: 0 credit (https://huggingface.co/docs/inference-providers/en/pricing) | Loại |
| Cerebras | Chỉ $5 khuyến mãi 1 lần, cần thẻ (https://www.cerebras.ai/pricing) | Loại |
| SambaNova | Phải nạp credit (https://cloud.sambanova.ai/plans) | Loại |

## 4. Đề xuất (chờ Tuan)

1. Cho Goose chạy thử 3–5 việc thật (`executor: goose`) → PASS ổn thì chuyển `chinh-thuc` (vào chuỗi sau Copilot, trước agy).
2. Nếu muốn thêm nguồn: tạo tài khoản Cloudflare + token Workers AI (để trong biến môi trường) → Claude thử với OpenCode/Goose.
3. Thêm vào danh sách loại (memory model-routing): Agent Code, HF Inference, Cerebras, SambaNova.
