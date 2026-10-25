# Khảo sát tại chỗ khách (GĐ0)

Mang theo: điện thoại (chụp ảnh, đo sóng Wi-Fi), thước, bút thử điện / đồng hồ vạn năng (đo khi đã cắt nguồn; đo có điện thì cẩn thận, 1 tay).
**Không mở nắp hay chạm dây đang có điện.**

## Motor / máy bơm (chụp rõ nhãn)
- [ ] Ảnh **nhãn motor**: hãng, model, kW/HP, **1 pha hay 3 pha**, điện áp (V), **dòng định mức (A)**, cos φ, tụ (µF)
- [ ] Loại bơm: giếng khoan / bơm tưới / đẩy lên bồn / khác: ______
- [ ] Hiện bật tắt bằng gì (cầu dao, CB, phao điện…)? Ảnh chỗ đấu hiện tại
- [ ] Khoảng cách từ nguồn điện đến máy bơm (m), tiết diện dây đang dùng (mm²) nếu ghi trên vỏ dây

## Tủ điện nhà khách (quyết định có cần MCB/RCD riêng không)
- [ ] Nhánh cấp cho máy bơm có **MCB riêng** không? Bao nhiêu A (ghi trên CB)? Nếu chỉ có CB tổng: ghi số A của CB tổng
- [ ] Có **RCD/ELCB (chống giật)** không? Ghi **mA** (cần 30 mA) – bấm nút **TEST** xem có nhảy không (báo khách trước: mất điện cả nhà vài giây)

## Nước
- [ ] Có nguy cơ chạy khô không (giếng cạn, bồn hết nước)? → cần phao / cảm biến áp / ngưỡng công suất
- [ ] Muốn tự động theo mực nước hay hẹn giờ không, hay chỉ bật/tắt từ xa?

## Chỗ đặt tủ
- [ ] Trong nhà / mái che / ngoài trời (nắng, mưa trực tiếp?) → cấp bảo vệ tủ
- [ ] **Đo sóng Wi-Fi tại chỗ đặt tủ** (app đo sóng, ghi dBm), tên mạng 2,4 GHz (ESP32 không dùng 5 GHz)
- [ ] Có dây nối đất (PE) không

## Khách dùng
- [ ] Điện thoại iOS hay Android, mấy người cần điều khiển
- [ ] Cần thông báo gì: bơm bật/tắt, lỗi chạy khô, quá tải, mất kết nối

Ghi kết quả vào `README.md` mục "Khảo sát" (không ghi mật khẩu Wi-Fi vào file).
