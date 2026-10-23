# cyberbrick-car

## Mục tiêu
Xe điều khiển tay kiểu thể thao (coupé gầm thấp), cầu sau hộp số 2 trục (không vi sai), lái servo Ackermann.
Xem `README.md`. Model sinh từ tham số: `freecad/scripts/build_car.py` – **sửa tham số rồi chạy lại**, không sửa tay
trong FreeCAD (file .FCStd là file sinh). Chuẩn bị in: `maker/robotics-cad/scripts/prepare-print.py print/print.yaml`.

## Thành phần
- Bộ CyberBrick (Bambu Lab): lõi XA003 = **ESP32-C3**, lập trình **MicroPython** (wiki hãng; mã nguồn
  github.com/CyberBrick-Official/CyberBrick_Controller_Core). Bộ thu XA004: 7,4–12,6 V, tối đa 3 A,
  2 động cơ DC + 4 servo + 2 LED. Thông số + model STEP/STL: Toolhub › Thư viện linh kiện (loại `cyberbrick`),
  danh mục `maker/robotics-cad/library/components.yaml`, file ở `community/cyberbrick-official/`.
- An toàn: pin PC003 là Li-ion 2S 7,4 V – không sạc khi không có người, không để chập cổng XH2.54.
- Khung/chi tiết in 3D trên Bambu A1, PETG Basic, **không support** (vẽ để tự in được – xem README mục In).
- Động cơ 030 LA024 + bánh răng 2 trục LA013 1:21; servo lái PG001 hoặc MG90S (`servo_type`); pin PC003 2S 7,4 V.

## Cách làm
- Code trong `firmware/`; ghi rõ cách nạp code vào board.
- Chi tiết CAD trong `cad/`, đơn vị mm.

## Agent
`embedded-systems`, `python-pro`.
