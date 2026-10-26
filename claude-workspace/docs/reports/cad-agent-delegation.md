# Giao việc dùng model CAD cho agent rẻ - Claude đặc tả, agent khác thực thi (2026-10-26)

Ngày: 2026-10-26 · Người yêu cầu: Tuan · Trạng thái: **nghiên cứu, chờ Tuan duyệt** (chưa đổi workflow).

## 1. Yêu cầu và phạm vi
- Giữ FreeCAD làm công cụ CAD.
- Toàn bộ việc dựng/sửa model vẫn qua Claude về chất lượng; Claude viết spec/prompt chuẩn, agent khác thực thi để giảm token Claude.
- Máy local yếu → không chạy model local (bỏ Ollama).

## 2. Kết quả tìm kiếm
Tiêu chí: commit kiểm 2026-10-26 qua GitHub API; còn cập nhật < 6 tháng; nhiều người dùng.

| Repo | Sao | Commit gần nhất | Kết luận |
|---|---|---|---|
| `openai/codex-plugin-cc` | 34 599 | 2026-07-08 | **DÙNG** - đã cài (ghim v1.0.6; `/codex:rescue`, agent `codex:codex-rescue`). Codex sửa file, chạy lệnh, chạy nền; tính vào hạn mức Codex gói ChatGPT. |
| `musistudio/claude-code-router` | 37 857 | 2026-10-10 | **DỰ PHÒNG** - đổi Claude Code sang model khác (OpenRouter, DeepSeek...), cần API/provider, không tự có quota free. |
| `simplybychris/antigravity-plugin-cc` | 81 | 2026-05-27 | **KHÔNG** - gần 5 tháng, ít người dùng, cần Bash/WSL trên Windows. |
| `BeehiveInnovations/pal-mcp-server` (tên cũ zen-mcp) | 11 812 | 2025-12-15 | **KHÔNG** - cũ (10 tháng). |
| `artcar12/agent-delegation-mcp` (2026-10-20), `KZvilla/lagrange-agent-runtime` (2026-10-24), `hishamkaram/claude-code-router` (2026-10-26) | 1 / 1 / 12 | - | **KHÔNG** - quá ít người dùng. `agent-delegation-mcp` tự cảnh báo lệnh tự duyệt, có thể gom thao tác Git mạnh. |

Đã xem trước đó (agent CAD):

| Repo | Sao | Ghi chú | Kết luận |
|---|---|---|---|
| `earthtojake/text-to-cad` | 23 243 | Cập nhật 2026-10-26; bản v0.7.26 ghim ở `community/earthtojake-text-to-cad` | **Chỉ tham khảo** - dùng build123d, không phải FreeCAD; tham khảo cách viết skill, kiểm DfAM. |
| `ghbalf/freecad-ai` | 589 | 2026-10-16 | **Không dùng** - workbench FreeCAD alpha, tác giả ghi chưa kiểm trên Windows, dễ crash, cần API key Gemini riêng. |

## 3. Hạn mức free
| Nguồn | Hạn mức | Cách kiểm |
|---|---|---|
| Codex trong ChatGPT Free | OpenAI không công bố số lượt cố định | `/status` ([help.openai.com](https://help.openai.com/en/articles/11369540)) |
| Antigravity CLI free | Theo tài khoản - TODO | `/usage` |
| Gemini CLI cá nhân | Ngừng từ 18-06-2026 | [developers.googleblog.com](https://developers.googleblog.com) |

TODO: đo số lượt Codex thực tế khi chạy thử.

## 4. Kiến trúc đề xuất (dùng đồ đang có, không cài thêm)

| Vai trò | Ai làm | Việc cụ thể |
|---|---|---|
| Đặc tả, duyệt | Claude (phiên chính) | Viết `spec.yaml` cho từng chi tiết; duyệt ảnh và kết quả cuối. Không viết script. |
| Thực thi | `codex:codex-rescue` (Codex Free) | Viết/sửa script FreeCAD trong thư mục staging, chạy `freecadcmd`. |
| Cổng kiểm (gate) | Script sẵn có | `tools/robotics-cad/scripts/check.py` (va chạm), `printability.py` (kiểm lớp), `test_model.py` (hợp lệ, 1 solid, thảo lắp), `prepare-print.py` (cắt lớp Bambu). |
| Chạy gate dài | check-runner (Haiku) | Chạy gate, tóm tắt. |
| Commit | git-scribe | Commit khi đạt gate. |

Nội dung `spec.yaml` đề xuất:
- Đơn vị mm; hệ trục (X tiến, Y trái, Z lên, góc).
- Tham số có min/max.
- Linh kiện mua: tham chiếu STEP trong `community/`.
- Khe lắp: clr 0,2 mm; trượt 0,3 mm.
- Quy tắc in: không support, trần hướng lên, lỗ thoát giọt nước, PETG Bambu.
- Tiêu chí nghiệm thu: valid, 1 solid, không chồng, khe trong khoảng, cắt lớp PASS.
- Lệnh kiểm và file đầu ra.

Vòng lặp: executor sửa → gate → lỗi (TODO: xuất JSON ngắn để executor tự đọc) → executor sửa tiếp, tối đa N vòng (đề xuất 5) rồi trả Claude.

Phần giữ cho Claude: boolean trên loft B-spline (bài học `safe_edit`), quyết định khe/dung sai, động học, an toàn.

## 5. Rủi ro
- Hạn mức Codex Free không rõ → có thể hết giữa vòng lặp.
- Codex đọc file máy trên Windows: TODO kiểm. Qua deliberation trước đây không đọc được; `codex:rescue` chưa thử.
- Chất lượng script FreeCAD của Codex chưa có benchmark → phải thử thực tế.

## 6. Bước tiếp theo (chờ Tuan duyệt)
Thử nghiệm 2 chi tiết:
1. `cyberbrick-car` Knuckle_L.
2. 1 chi tiết `pushrod-arm` có lỗ trục + khe trượt 0,3 mm.

Claude viết spec → `codex:codex-rescue` thực thi → so với bản Claude theo 4 tiêu chí: đúng kích thước, qua gate, số vòng sửa, token Claude tiêu tốn.

## Nguồn
- Codex limit/status: https://help.openai.com/en/articles/11369540
- Gemini CLI cá nhân ngừng: https://developers.googleblog.com
- Repo: openai/codex-plugin-cc, musistudio/claude-code-router, simplybychris/antigravity-plugin-cc, BeehiveInnovations/pal-mcp-server, artcar12/agent-delegation-mcp, KZvilla/lagrange-agent-runtime, hishamkaram/claude-code-router, earthtojake/text-to-cad, ghbalf/freecad-ai (kiểm qua GitHub API 2026-10-26).

Ghi chú: license các repo chưa kiểm lại trong báo cáo này (theo chính sách phi thương mại, xem trước khi dùng mã).
