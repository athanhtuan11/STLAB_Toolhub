# Sổ ghi lỗi / bài học (inbox)

Định dạng mỗi mục:
`- [ ] YYYY-MM-DD | <sự việc> | Bài học: <...> | Đề xuất: <CLAUDE.md / memory / EXPERIENCE <skill> / hook>`

## 2026-10-23
- [ ] 2026-10-23 | Hai phiên (Desktop + VS Code) cùng làm FreeCAD, chạy lâu, không đồng bộ → Tuan phải dừng 1 phiên | Bài học: mỗi công cụ (FreeCAD, Blender…) chỉ 1 phiên phụ trách tại một thời điểm | Đề xuất: CLAUDE.md
- [ ] 2026-10-23 | Tuan từ chối 2 lệnh chạy dài/ngoài ý (chạy kiểm tra lâu; thử CADCraft khi chưa hỏi) | Bài học: việc chạy > 2 phút hoặc mở công cụ mới → hỏi trước | Đề xuất: CLAUDE.md
- [ ] 2026-10-23 | Memory/ngữ cảnh trỏ sai chỗ: pushrod_arm thật ở `D:\06_FreeCAD\pushrod_arm\`, bản trong Documents là cũ (21/10) | Bài học: ghi đường dẫn dự án đang làm vào memory | Đề xuất: memory
- [ ] 2026-10-23 | freecadcmd tự nuốt mọi tham số `--x` sau `--pass` (dùng `khoa=gia-tri`); script tên `inspect.py` chạy im lặng (trùng module chuẩn) | Bài học: tham số dạng khoa=gia-tri, tránh tên trùng module chuẩn | Đề xuất: EXPERIENCE robotics-cad
- [ ] 2026-10-23 | Assembly Revolute: Offset2 +x → yaw thực −x | Bài học: đảo dấu khi quét khớp | Đề xuất: EXPERIENCE robotics-cad (đã ghi trong kiem-tra-model.md mục 3.2)
- [ ] 2026-10-23 | Tuan không thấy tiến độ vì việc chạy ở phiên khác | Bài học: kết quả phải hiện ở phiên Tuan đang xem | Đề xuất: CLAUDE.md
- [ ] 2026-10-23 | pushrod_arm: job dựng xi-lanh v3 ghi hình mới theo toạ độ thế giới nhưng chỉ reset placement cho một phần chi tiết → Jaw_2 + 2 đệm TPU bị dời 2 lần, STL in nghiêng 30° | Bài học: script thay `Shape` phải đặt lại `Placement` cho MỌI chi tiết bị thay và cập nhật file tư thế gốc (rest.json); kiểm bằng ảnh toàn cảnh sau mỗi job | Đề xuất: EXPERIENCE robotics-cad
- [ ] 2026-10-23 | Đo thành mỏng lấy 2×2 điểm/mặt bỏ sót chỗ mỏng (báo 0,81 mm, thực có cạnh 0,12 mm); góc nhọn của rãnh khoét bị báo là "thành mỏng" | Bài học: đo ≥ 3×3 điểm; điểm mỏng phải xem mặt cắt trước khi kết luận lỗi | Đề xuất: EXPERIENCE robotics-cad
