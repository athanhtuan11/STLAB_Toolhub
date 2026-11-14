# Gộp /projects + /robotics và trang "Hướng dẫn làm" cho học sinh

2026-11-14 · đề xuất, CHỜ TUAN DUYỆT ảnh trước khi làm. Mockup: `projects-merge/mockup-list.png`, `projects-merge/mockup-guide.png`.

## Hiện trạng
- `/projects`: 24 thẻ kiểu dev (CLAUDE.md, VS Code, skill), không ảnh, không trạng thái. Học sinh/giáo viên không dùng được.
- `/robotics`: thẻ có ảnh, trạng thái, cấp học, bước tiếp (dữ liệu `studio/toolhub/robotics.json`), nhưng chỉ có 7 dự án robotics.
- Sơ đồ đấu dây: mới có bảng chữ trong `maker/english-teacher/hardware/wiring-s3.md` và `maker/pump-control/docs/power-and-wiring.md`. Chưa có hình.

## Đề xuất
1. **Một trang Dự án** (`/projects`), dùng thẻ kiểu Robotics. Lọc bằng chip: Robotics, Thiết bị thông minh, Mẫu in, Công cụ, Khách hàng. Thêm lọc cấp học, trạng thái. `/robotics` chuyển hướng sang `/projects?nhom=robotics`. Mô phỏng (GearsBot, Erebus) giữ thành một mục.
2. **Mục "Chạy được – làm theo được"** đứng đầu. Chỉ dự án đã thử thật trên mạch, có nút xanh "Hướng dẫn làm". Nút dev thu thành 1 dòng nhỏ.
3. **Trang hướng dẫn 7 bước**, cùng khung cho mọi dự án: Linh kiện → An toàn (khung đỏ, luôn đứng trước sơ đồ) → Sơ đồ đấu dây → Hàn & nối → In & lắp vỏ → Nạp chương trình → Kiểm tra & sửa lỗi. Mỗi bước có ô "Em làm xong". Có PDF để in phát lớp.
4. **Sơ đồ đấu dây sinh từ 1 file `hardware/wiring.yaml`** mỗi dự án. Từ một nguồn này sinh ra cả hình SVG, bảng dây có ô tích và PDF, nên hình và bảng không thể lệch nhau. Màu dây cố định: đỏ 5V, cam 3V3, đen GND. Có nút lọc theo nhóm dây (nguồn, mic, ampli).

## Chọn công cụ vẽ sơ đồ
| Cách | Ưu | Nhược |
|---|---|---|
| **Tự sinh SVG từ wiring.yaml (khuyến nghị)** | Đúng giao diện Toolhub; agent viết được; một nguồn cho hình + bảng + PDF | Phải tự viết script (~vài trăm dòng); hình khối chữ nhật, không giống ảnh bo thật |
| WireViz (YAML → Graphviz) | Có sẵn, text-based | Dạng sơ đồ bó dây kỹ thuật, khó đọc với học sinh nhỏ; thêm phụ thuộc Graphviz |
| Fritzing (hình breadboard) | Giống ảnh thật nhất | Vẽ tay bằng GUI, không tự động; linh kiện như INMP441 phải tìm part cộng đồng. TODO: kiểm giá/bản quyền tải hiện tại |
| Wokwi | Đẹp, chạy mô phỏng được | Phụ thuộc web; thiếu một số module (TODO kiểm INMP441, MAX98357A) |

Sau này có thể thêm ảnh chụp thật từng bước, đặt cạnh sơ đồ.

## Dự án đủ điều kiện "Chạy được"
- **english-teacher (Cú Bông S3)**: đã chạy thật. Đã sửa `wiring-s3.md` (+ PDF) cho khớp firmware `stlab-s3/config.h`: nút nói = switch MX GPIO1 → GND, BOOT GPIO0 chạy song song khi thử trên bàn; GPIO39/40 âm lượng là tùy chọn, vỏ S3 không có.
- **esp32-s3-cam**: đã chạy, camera cắm sẵn trên bo, gần như không có dây.
- **pump-control**: chạy thật nhưng điện **220 V**, là công trình cho khách. **Không** đưa vào hướng dẫn học sinh; chỉ để trong nhóm Khách hàng.
- Các dự án robotics chưa có bản chạy thử, nên chưa vào mục này.

## Cần Tuan
- Duyệt 2 ảnh mockup.
- Điền cấp học, thời gian cho Cú Bông và camera.
