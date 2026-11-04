# Tiết kiệm token Claude – rà phiên 2026-11-02/03 + agent miễn phí mới

Tuan 2026-11-03: 'Claude xài nhiều thế, tìm thêm agent hoặc phân bố việc'. Báo cáo – chưa đổi cấu hình, chờ Tuan duyệt.

## 1. Token Claude tốn vào đâu (phiên vừa rồi, Claude tự rà – định tính, không có số đo)

| Nguồn tốn | Ví dụ trong phiên | Mức |
|---|---|---|
| Ngữ cảnh phiên rất dài | 1 phiên làm 6 việc: nghiên cứu thị trường, Toolhub, dê flexi, clicker, ESP32-S3-CAM… → mỗi lượt trả lời phải đọc lại toàn bộ | Cao nhất |
| Đọc output lệnh dài | efuse summary, log khởi động ESP32, log cắt lớp, vòng cắt lát đo hình học nhiều lần | Cao |
| Xem ảnh | contact sheet, preview (~10 ảnh lớn) | Vừa–cao |
| Làm lại do sai | spec hình học khớp dê lần 1 mâu thuẫn; đoán sai nguyên nhân 3MF lỗi (first_layer_time) trước khi tìm ra lật 180° | Vừa |
| Tự chạy thay vì ủy thác | Tự chạy đo/cắt lớp/nạp + đọc log thay vì giao check-runner | Vừa |
| Viết spec + gate | Việc đúng vai Claude | Cần thiết |
| Đã giao đúng | code → delegate.py (OpenCode), tra web → Codex, tài liệu → doc-writer, commit → git-scribe | Tốt |

## 2. Đề xuất xếp lợi/công

| # | Đề xuất | Lợi | Công | Ghi chú |
|---|---|---|---|---|
| 1 | ★ **1 việc = 1 phiên**: xong mỗi dự án/việc lớn → mở phiên mới (memory + CLAUDE.md đã đủ để tiếp); dùng /compact khi phiên dài | Cao | 0 | Tuan chỉ cần mở chat mới |
| 2 | ★ **check-runner làm hết việc "chạy + đọc log"**: nạp firmware + đọc serial, cắt lớp/printability, chạy script đo hình học → trả ≤ 15 dòng tóm tắt; Claude chỉ đọc tóm tắt | Cao | Thấp | Sửa CLAUDE.md mục phân việc |
| 3 | ★ **Lọc output**: mọi lệnh có thể > 40 dòng phải grep/tail; không in cả efuse/log | Vừa | 0 | Quy tắc cho Claude |
| 4 | Ảnh: product-designer tự duyệt vòng trong; Claude chỉ xem contact sheet cuối, thu nhỏ ~1200 px | Vừa | Thấp | |
| 5 | Checklist kiểm trước khi gửi file in (transform, --info exit 0) đã vào skill stlab-workflow – tránh làm lại | Vừa | Xong | |
| 6 | **Thêm executor Goose + Groq free** vào chuỗi delegate (thứ 7) | Vừa | Vừa | Cần Tuan tạo Groq API key free; selftest trước |
| 7 | Cloudflare Workers AI (10.000 Neurons/ngày) làm nguồn model cho OpenCode/Goose | Thấp–vừa | Vừa | Một số model cần trả phí – kiểm trước |

## 3. Agent/nguồn miễn phí mới (Codex tra 2026-11-03, Claude kiểm GitHub API)

| Tên | Repo / nguồn | Miễn phí | Headless | Kết luận |
|---|---|---|---|---|
| Goose | https://github.com/aaif-goose/goose – 56.152 sao, push 2026-11-03 (Claude kiểm API); repo cũ block/goose đã chuyển | Agent miễn phí, tự chọn nguồn model; Groq free theo từng model (https://console.groq.com/docs/rate-limits), xem hạn mức ở console + header | `goose run -t` hoặc stdin; cài Windows native; quyền allow/ask/deny từng tool | ★ Ứng viên tốt nhất cho delegate |
| Kiro CLI | https://github.com/kirodotdev/Kiro – 4.433 sao, cập nhật 2026-10-18 | Free 50 credit, có Claude Sonnet 4.5 (https://kiro.dev/pricing/) | Headless cần KIRO_API_KEY – chỉ gói trả phí (https://kiro.dev/docs/cli/headless/) | Chỉ dùng tương tác, không vào chuỗi tự động |
| Amazon Q Developer CLI | https://github.com/aws/amazon-q-developer-cli – không còn bảo trì, chuyển sang Kiro | 50 lượt/tháng (https://aws.amazon.com/q/developer/pricing/) | TODO | Loại |
| Cloudflare Workers AI | https://developers.cloudflare.com/workers-ai/platform/pricing/ | 10.000 Neurons/ngày, reset 00:00 UTC | Là nguồn model, không phải agent | Dự phòng |
| NVIDIA NIM | https://docs.api.nvidia.com/nim/docs/product | Miễn phí để prototype, hạn mức TODO | Nguồn model | Dự phòng |

Loại thêm: GitHub Models (ngừng 30/07/2026 – https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/), Cursor CLI (hạn mức free không rõ), DeepSeek/Kimi API (trả theo dùng), Cerebras (free hay trial chưa rõ).

## 4. Việc chờ Tuan duyệt

- Duyệt mục 2 (#1–#4 Claude áp dụng ngay được, chỉ là quy tắc).
- Có muốn thử Goose + Groq không (Tuan tạo key free tại console.groq.com, Claude cài + selftest).
