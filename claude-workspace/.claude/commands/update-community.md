---
description: Kiem tra cap nhat nguon cong dong va bao cao (khong tu ap dung)
argument-hint: "[ten-repo]"
---

Chạy `bash community/update-community.sh check $ARGUMENTS` tại thư mục gốc claude-workspace,
rồi đọc báo cáo mới nhất trong `community/reports/`.

Tóm tắt bằng tiếng Việt cho từng repo có thay đổi:
1. Phiên bản hiện tại → phiên bản mới, số commit.
2. Thay đổi chính (3–5 ý), đặc biệt các phần đang liên kết vào dự án.
3. **Thay đổi nhạy cảm**: hook, lệnh shell mới/đổi, quyền truy cập, MCP server, phụ thuộc mới.
   Mở diff đúng các file bị đánh dấu và giải thích chúng làm gì.
4. Khuyến nghị: áp dụng / chờ / bỏ qua, kèm lý do.

KHÔNG chạy `apply`, `rollback` hay `--auto`. Chỉ in sẵn lệnh `apply` cho từng repo
để Tuan tự xác nhận.
