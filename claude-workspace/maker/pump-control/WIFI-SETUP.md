# Kết nối Wi-Fi nhà khách + app ESP RainMaker (máy bơm)

## Chuẩn bị
- Điện thoại cài app **ESP RainMaker** (CH Play / App Store), bật **Bluetooth** + **vị trí (GPS)**.
- Tên + mật khẩu **Wi-Fi 2,4 GHz** nhà khách (không dùng mạng 5 GHz). Viết ra giấy, **không** lưu vào file.
- Laptop + cáp micro-USB để xem mã QR / mã PoP của ESP32.
- **Ngắt nguồn 5 V của tủ khi cắm USB** vào ESP32 (chỉ 1 nguồn cho bo tại 1 lúc).

## 1. Đăng nhập app
1. Mở app ESP RainMaker → **Sign up** (tạo tài khoản bằng email) hoặc đăng nhập Google / Apple.
2. Tài khoản nào thêm thiết bị thì thiết bị thuộc tài khoản đó → nên **đăng nhập tài khoản của khách** trên điện thoại khách.

## 2. Xóa Wi-Fi cũ trên ESP32
Chỉ làm khi ESP32 đã từng nối Wi-Fi khác (vd. Wi-Fi STLab). ESP32 mới thì bỏ qua.
1. Cấp điện cho ESP32.
2. Giữ nút **BOOT** trên bo **3 s** rồi thả → ESP32 xóa Wi-Fi, khởi động lại, chờ kết nối.
3. **Không giữ 10 s** (10 s = reset nhà máy).

## 3. Lấy mã QR / PoP
1. Cắm USB vào laptop, mở log: chạy `flash.ps1` phần monitor hoặc `idf.py -p COM5 monitor` (đổi COM theo máy).
2. Bấm nút **EN** trên bo → log in **mã QR**, tên `PROV_xxxx` và mã **PoP**.
3. ESP32 chờ kết nối **30 phút**; quá giờ thì bấm **EN** lại.

## 4. Thêm thiết bị vào app
1. App → **Add Device** (dấu +) → quét **mã QR** trên màn hình laptop.
   Không quét được: chọn **I don't have a QR code** → chọn `PROV_xxxx` → nhập **PoP**.
2. Chọn **Wi-Fi 2,4 GHz** nhà khách → nhập mật khẩu → chờ các bước báo xanh.
3. Rút USB, cấp lại nguồn 5 V tủ → app hiện thiết bị **"May bom"** online.

## 5. Kiểm tra
1. Mục **"Giờ thiết bị"** trùng giờ Việt Nam.
2. Công tắc tủ ở **TỰ ĐỘNG** → bấm **Bật** trên app → contactor hút; **Tắt** → nhả.
3. Tắt xong bật lại ngay → app báo chờ **5 s** (bình thường).
4. Đặt **"Chạy tối đa (phút)"** theo nhu cầu khách (mặc định 30 phút).

**Kiểm tra:** app bật/tắt được, giờ thiết bị đúng.

## Lỗi hay gặp
| Hiện tượng | Cách xử lý |
|---|---|
| App không thấy `PROV_xxxx` | Bật Bluetooth + GPS; điện thoại đứng gần tủ; bấm EN chạy lại |
| Báo sai mật khẩu / không vào mạng | Kiểm mật khẩu; chắc chắn là mạng **2,4 GHz**; giữ BOOT 3 s làm lại từ mục 2 |
| Thiết bị báo đã thuộc tài khoản khác | Đăng nhập đúng tài khoản đã thêm trước đó, hoặc xóa thiết bị khỏi tài khoản cũ rồi thêm lại |
| Thiết bị offline sau khi đổi modem / mật khẩu Wi-Fi | Làm lại từ mục 2 |
