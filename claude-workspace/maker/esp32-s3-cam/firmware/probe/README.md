# probe – Firmware dò phần cứng ESP32-S3-CAM N16R8 + OV3660

Firmware ESP-IDF 5.5.4 dùng để **dò phần cứng** mạch ESP32-S3-CAM N16R8 và camera OV3660:
in thông tin chip/flash/PSRAM/MAC, thử bộ chân camera, đọc PID cảm biến, mở Wi-Fi AP và
trang web xem hình + trạng thái.

## Nạp firmware

1. Build (máy có ESP-IDF 5.5.4 trong `C:\Espressif`):

   ```bat
   powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1
   ```

2. Nạp và xem log serial (thay `COMx` bằng cổng thật, không truyền thì mặc định `COM5`):

   ```bat
   flash.bat COMx
   ```

   Nếu cổng USB-C của mạch là USB native thì log vẫn ra USB-Serial-JTAG; chọn đúng cổng COM
   trong Device Manager.

## Kết nối và xem hình

- Wi-Fi do mạch phát: SSID `STLAB-CAM-XXXX` (4 hex cuối MAC), mật khẩu là **8 ký tự hex cuối
  MAC viết hoa** – in ra log ở dòng `[DO] Wi-Fi AP: ...` (không có mật khẩu cố định trong mã).
- Kết nối điện thoại/máy tính vào Wi-Fi đó rồi mở <http://192.168.4.1>.
- Trang web có: ảnh stream, nút chụp ảnh, chọn độ phân giải (QVGA/VGA/SVGA/XGA/UXGA/QXGA),
  chọn chất lượng, và bảng trạng thái cập nhật mỗi 2 giây.

## Gửi lại gì cho Claude

- **Toàn bộ log serial** từ lúc cấp nguồn, nhất là các dòng bắt đầu bằng `[DO]`: chip, số lõi,
  revision, flash, PSRAM, MAC, kết quả từng lần thử bộ chân/XCLK, PID cảm biến, kích thước 5 khung,
  và địa chỉ I2C nếu quét.
- Nội dung trang `/status` (copy JSON hoặc ảnh chụp màn hình bảng trạng thái).
- Cho biết ảnh stream có hiện không, màu sắc/hình ảnh có đúng không.
- Ảnh chụp mặt trước/sau mạch và nhãn in trên board (nếu có) để đối chiếu chân.

## Ghi chú

- Bộ chân `FREENOVE_GOOUUU` lấy theo nguồn Freenove/GOOUUU, **chưa chắc** đúng cho mạch của
  Tuan. Firmware thử XCLK 20 MHz rồi 10 MHz; nếu tất cả đều lỗi sẽ quét I2C (SCCB) trên
  SIOD/SIOC từng bộ và vẫn bật Wi-Fi + trang `/status` để báo lỗi.
- Muốn thêm bộ chân khác: sửa mảng `s_pin_sets` trong `main/probe_main.c` (chỉ thêm khi có nguồn
  xác nhận, không tự đoán chân).

## Xem trên máy tính

Cài Wi-Fi nhà cho mạch một lần (mạch lưu trong NVS, không nằm trong mã), sau đó mở trình duyệt:

```bat
C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe wifi-setup.py --port COM6
```

- Mặc định lấy SSID mạng Windows đang kết nối và mật khẩu từ profile Windows; không đọc được thì hỏi (ẩn).
- Tùy chọn: `--ssid TEN` (mạng khác), `--ask` (tự nhập mật khẩu), `--status` (xem trạng thái), `--clear` (xóa Wi-Fi nhà).
- Xong script in `Mo: http://stlab-cam.local  (IP: x.x.x.x)`. Mật khẩu không bao giờ được in hay ghi file.
- Chỉ Wi-Fi 2,4 GHz (ESP32-S3 không có 5 GHz); router phát chung tên 2,4 + 5 GHz vẫn dùng được.
- Máy tính và mạch phải cùng một mạng.
- AP `STLAB-CAM-xxxx` vẫn bật để dự phòng (http://192.168.4.1).
- Khi mạch vào router, kênh của AP đổi theo kênh router (giới hạn của chế độ AP+STA), nên điện thoại đang nối AP có thể rớt vài giây.
