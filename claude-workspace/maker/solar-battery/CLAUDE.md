# solar-battery

## Mục tiêu
TODO: tải cần cấp (W, giờ/ngày), số ngày dự phòng.

## Thành phần
- TODO: tấm pin (Wp, Voc, Isc), bộ sạc (MPPT/PWM), pin (hóa học, Ah, V), BMS, inverter.
- TODO: vị trí lắp và số giờ nắng tại Đức Trọng (lấy số liệu có nguồn, không đoán).

## Quy ước
- Tính toán hiển thị đủ bước: Wh/ngày → dung lượng pin → công suất tấm.
- Có cầu chì/CB cho từng nhánh; chọn tiết diện dây theo dòng và chiều dài.
- Pin lithium: bắt buộc có BMS; không sạc dưới 0 °C nếu datasheet không cho phép.

## Agent
`embedded-systems` (giám sát bằng ESP32, nếu có).
