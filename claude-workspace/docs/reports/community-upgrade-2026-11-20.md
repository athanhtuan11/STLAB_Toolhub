# Nâng cấp nguồn cộng đồng 2026-11-20

Kiểm tra: `bash community/update-community.sh check` → `community/reports/2026-11-20.md` (13 repo có bản mới).
Tuan cho phép "cần update thì update" (2026-11-20, vắng nhà) → chỉ apply repo đã đọc diff phần liên kết và rủi ro thấp.

## Đã apply (rollback: `bash community/update-community.sh rollback <ten>`)

| Repo | Ghim mới | Lý do an toàn |
| --- | --- | --- |
| ahujasid-mcp-for-blender | `a5a8acf2c6ae` | `addon.py` +24 dòng: bỏ lệnh khi client MCP đã ngắt (sửa Blender bận lâu sau lệnh dài, #430). Có hiệu lực lần mở Blender sau. |
| looooo-freecad-gears | `416407394628` | 1 commit, `timinggear.py` +11 dòng. FreeCAD là legacy. |
| github-awesome-copilot | `f10fdb8b2660` | Skill liên kết `freecad-scripts` không đổi. |
| remotion-dev-skills | `6f55706d1069` | Chỉ tài liệu/ví dụ skill (rút gọn 18k dòng), không hook/MCP. |

## Giữ lại – cần Tuan quyết

| Repo | Bản mới | Vì sao chưa |
| --- | --- | --- |
| 78-xiaozhi-esp32 | v2.5.2 → v2.6.0 (158 commit) | `english-teacher/xiaozhi-s3/sync.ps1` chép từ clone này → lần build sau sẽ lấy bản mới. Có đổi giao thức MCP (#2415), health check MQTT/UDP, OTA fallback. Cần việc riêng: build + gate + thử trên Cú Bông, kiểm patch STLab còn áp được. |
| heygen-com-hyperframes | 668 commit, CLI 0.9.72 | Skill mới nhắc `hyperframes@1.2.3`, lệch CLI đang ghim 0.8.214; thêm script dò exe Windows. Nâng thì nâng cả CLI + dựng thử 1 video. |
| antonbabenko-deliberation | v4.1.1 → v4.6.1 | Plugin đang dùng hằng ngày (ask-gemini/ask-gpt); thêm provider/doctor mới. Nâng plugin riêng, sau đó chạy `/deliberation:doctor`. |
| neka-nat-freecad-mcp | v0.1.30 → v0.1.32 | Thêm transport HTTP/SSE, nhiều script mới; FreeCAD đã là legacy → không cần. |
| espressif-kicad-libraries | 3.2.1 → 4.0.0 | Bản lớn (~1 triệu dòng), chỉ tham khảo, chưa dự án nào dùng. |
| mikedh-trimesh, quirkycort-gears | commit mới | Chỉ tham khảo, không liên kết. |
| arduino-docs-content | 0 commit mới | SHA khác nhưng không có commit → TODO kiểm tay (có thể bị force-push). |
| shaise-freecad-fasteners | lỗi lấy tag | TODO kiểm tay; FreeCAD legacy. |

## Đề xuất thứ tự
1. deliberation (lợi lớn, công nhỏ).
2. xiaozhi v2.6.0 trên nhánh riêng khi Tuan có thời gian thử Cú Bông.
3. HyperFrames khi có việc video tiếp theo.
