# Trung tâm điều hành Toolhub – thiết kế (Claude, tổng giám đốc) – chờ Tuan duyệt

Tuan 2026-10-27: "hoàn thiện khung chính phân cấp. R&D trước. Giao diện tùy biến để mở trang web lên thấy được tất cả
mình làm." Nghiên cứu: `docs/reports/agent-dashboard-study.md` (6 repo cộng đồng), sổ nhân sự `org/`.

## 1. Khung phân cấp còn thiếu (rà sau 1 ngày chạy thật)
| # | Thiếu | Đã gặp |
|---|---|---|
| 1 | Nhật ký chung – chỉ delegate có log; việc Haiku + quyết định phiên chính không ghi | Tuan chỉ thấy trong chat |
| 2 | Hàng chờ duyệt – ESCALATE, hộp hỏi hàng rào, quyết định thiết kế rải trong chat | Hỏi lại nhiều lần (A/B/C arm) |
| 3 | Bảng việc – spec rải nhiều thư mục, không có chờ/chạy/xong | Khó biết việc dở |
| 4 | Biết "ai đang làm gì" giữa các phiên Claude | 2 phiên trùng việc model-study |
| 5 | Tuyển nhân viên (mục 7.3 thiết kế sổ) chưa có mẫu + bài thử | – |

## 2. Dữ liệu (một nguồn, chỉ trên máy)
- **Kho sự kiện** `%LOCALAPPDATA%/stlab-usage/events.db` (SQLite stdlib): `events(id, ts, source, session, agent,
  parent, kind, title, ref, data)`; `approvals(id, ts, source, ref, question, state[cho|da-duyet|tu-choi], by, note)`.
  Không lưu nội dung prompt/mã – chỉ tiêu đề ngắn + đường dẫn tham chiếu (học `community/hoangsonww-claude-code-agent-monitor/server/db.js`).
- **Ai ghi:**
  - Hook Claude Code mới `custom/hooks/event_log.py` (async, không chặn): SessionStart, UserPromptSubmit (chỉ "Tuan gửi
    yêu cầu", không chép nội dung), PostToolUse (tên công cụ + file), SubagentStop (agent Haiku nào xong), Stop, Notification.
  - `tools/delegate/delegate.py`: bắt đầu/vòng/kết thúc run, ESCALATE → tạo 1 mục duyệt.
  - `custom/hooks/guard_paths.py`: chặn/hỏi → sự kiện (hỏi → mục duyệt).
  - Phiên chính hỏi Tuan quyết định → `python tools/org/approvals.py add "<câu hỏi>" --ref <file>`.
- **Không làm:** đọc credential để lấy hạn mức Claude (STLab đã cấm – giữ statusline); ingest toàn bộ transcript
  JSONL (để giai đoạn sau nếu cần cây subagent chi tiết).

## 3. Giao diện – trang "Điều hành" (`/ops`) + tóm tắt ở trang chính
Khung (widget), mỗi khung **bật/tắt + đổi thứ tự**, lưu trong trình duyệt (localStorage), làm mới 5 s (polling theo con trỏ):
1. **Cần anh duyệt** – mục `cho`: câu hỏi, nguồn (Claude/agent/hàng rào), link file; nút Duyệt / Từ chối + ghi chú
   (POST có header `X-Studio`, chỉ máy này).
2. **Đang chạy** – run delegate đang chạy + phiên Claude đang mở (theo SessionStart/Stop), ai làm, bao lâu.
3. **Bảng việc** – cột Chờ / Đang chạy / Xong / Lỗi / Báo lên trên (từ run delegate + spec); bấm xem handoff/log.
4. **Dòng thời gian** – sự kiện mới nhất, lọc theo tầng/agent/nguồn; mỗi dòng: giờ · ai · việc · kết quả.
5. **Nhân sự AI** – khung hiện có (hạn mức theo nguồn, sơ đồ, thành tích).
6. **Commit gần đây** – 10 commit cuối (git log), ai làm.
Trang chính: dải tóm tắt "N cần duyệt · N đang chạy · N lỗi hôm nay" → bấm vào `/ops`.

## 4. Lộ trình (mỗi bước có gate; giao executor theo sổ, Claude viết spec + duyệt)
1. Kho sự kiện + `approvals.py` + delegate ghi sự kiện + hook `event_log.py` – vừa.
2. API `/api/ops/*` + trang `/ops` 6 khung + tùy biến + duyệt – vừa.
3. Tóm tắt trang chính + mẫu "tuyển nhân viên" (thiếu #5) – nhỏ.
4. (Sau) ingest transcript cho cây subagent chi tiết – vừa.

## 5. Rủi ro
- Hook chạy mỗi lệnh gọi công cụ → Python khởi động trên máy yếu: đặt `async`, ghi 1 dòng SQLite, đo thời gian; chậm
  thì chỉ ghi SubagentStop/Stop.
- Dữ liệu nhạy cảm: không lưu prompt/mã/secret; chỉ loopback (Toolhub đã chặn Host lạ + CSRF).
