# Công cụ nguồn mở tính giá thành in 3D (tìm 2026-10-28)

Ngày: 2026-10-28 · Người yêu cầu: Tuan · Trạng thái: **đã duyệt hướng, chưa làm tab Báo giá**

Số sao, số commit, ngày phát hành và license lấy từ GitHub/docs.rs ngày 2026-10-28. Kiểm lại khi ghim vào `community/`.

## 1. Mục đích

Tính giá thành phẩm in 3D để gửi báo giá cho khách. Máy: Bambu Lab A1. Nhựa mặc định: Bambu PETG Basic.

## 2. Bảng so sánh

| Công cụ | Làm gì | Đầu vào | License | Sao / commit / bản | Kết luận |
|---|---|---|---|---|---|
| [Gunderson3d/printcalc](https://github.com/Gunderson3d/printcalc) | Rust CLI + thư viện `libprintcalc` + bản web | Đọc file đã cắt lớp: Bambu Studio `.gcode.3mf`, `.gcode`, PrusaSlicer `.bgcode`, SLA `.sl1/.sl1s`. Tính nhựa, thời gian, hao mòn máy, điện, công, phụ kiện. Giá bán gợi ý theo **biên** lợi nhuận 50/60/70 % (không phải markup) | Apache-2.0 | 0 sao / 59 commit / v0.2.0 (2026-10-15) | **Tham chiếu công thức.** Không chạy trực tiếp: cần Rust/cargo, dự án mới, mặc định USD |
| [jkga/3dpcalc](https://github.com/jkga/3dpcalc) | TypeScript, có bản chạy [3dpcalc.vercel.app](https://3dpcalc.vercel.app) | Nhập tay (không đọc gcode/3mf). Giá nhựa/gam, điện/giờ, hồ sơ máy, SLA, phí cài đặt/đóng gói/giao hàng, markup, xuất PDF | MIT | 22 sao / 40 commit | **Tham chiếu công thức** |
| [8bits1beard-io/PrintCost](https://github.com/8bits1beard-io/PrintCost) | HTML/JS thuần, Chart.js, lưu localStorage | Nhập tay (v1.1.0 đã bỏ đọc G-code). Nhựa nhiều màu, điện, khấu hao, công, % hỏng, markup | MIT | 0 sao | Loại: không xuất PDF |
| [maziggy/bambuddy](https://github.com/maziggy/bambuddy) | Quản lý máy Bambu tự host (MQTT/FTPS, không cloud), archive 3MF, chi phí nhựa theo giá cuộn, điện qua ổ cắm thông minh | 3MF, MQTT | AGPL-3.0 | 3,2k sao | Loại: **không có báo giá**. Nếu sau này dùng, ghi vào bảng "Xem lại khi thương mại" trong `docs/COMMUNITY.md` |
| [Blb3D/filaops](https://github.com/Blb3D/filaops) | ERP xưởng in, đọc 3MF Bambu theo màu | 3MF | TODO kiểm | TODO | Theo bài Reddit 12/2025, cổng báo giá cho khách dự kiến thuộc bản trả phí. Chưa chọn |

Không chọn: OctoPrint-CostEstimation (cần OctoPrint, A1 không dùng), PrintPrice WooCommerce (tính giá qua cloud của họ), Printforge/MakerQuote (thương mại).

## 3. Công thức chung

Các công cụ trên dùng chung cấu trúc sau:

- Nhựa = gam × (giá cuộn / khối lượng cuộn)
- Điện = công suất máy (kW) × giờ in × giá điện (đ/kWh)
- Khấu hao = giá máy / số giờ đời máy × giờ in
- Công = giờ công (chuẩn bị + gỡ + hậu xử lý) × đơn giá giờ
- Dự phòng hỏng = % × tổng các mục trên
- Giá bán, hai cách khác nhau:
  - Markup: giá vốn × (1 + m)
  - Biên: giá vốn / (1 − b)
  - Lưu ý: biên 50 % = markup 100 %

## 4. Quyết định (Tuan duyệt 2026-10-28)

- Không chạy printcalc trực tiếp. Dùng printcalc và 3dpcalc làm tham chiếu công thức.
- Làm tab **Báo giá** trong Toolhub (`/quote`):
  - Đọc `.3mf` của Bambu bằng Python. Repo đã đọc `Metadata/slice_info.config` trong `tools/robotics-cad/scripts/slice.py`.
  - Bảng giá nằm trong `studio/quote/pricing.yaml` (Tuan điền).
  - Ra báo giá tiếng Việt, đơn vị VND.
  - Xuất PDF bằng Edge headless.
- Dữ liệu khách (tên, SĐT) chỉ nhập trên trang, lưu ngoài repo. Không gửi cho agent ngoài.

## 5. Việc tiếp theo

- Tuan điền giá trong `studio/quote/pricing.yaml`.
- Tuan duyệt mockup trang báo giá bằng ảnh.
- Tuan đồng ý ghim printcalc và 3dpcalc vào `community/` làm tham chiếu.

## Nguồn

- https://github.com/Gunderson3d/printcalc
- https://docs.rs/crate/printcalc
- https://github.com/jkga/3dpcalc
- https://3dpcalc.vercel.app
- https://github.com/8bits1beard-io/PrintCost
- https://github.com/maziggy/bambuddy
- https://github.com/Blb3D/filaops
