# cyberbrick-car

## Mục tiêu
TODO: mô tả xe (điều khiển tay / tự hành, tính năng).

## Thành phần
- Bộ CyberBrick (Bambu Lab): lõi XA003 = **ESP32-C3**, lập trình **MicroPython** (wiki hãng; mã nguồn
  github.com/CyberBrick-Official/CyberBrick_Controller_Core). Bộ thu XA004: 7,4–12,6 V, tối đa 3 A,
  2 động cơ DC + 4 servo + 2 LED. Thông số + model STEP/STL: Toolhub › Thư viện linh kiện (loại `cyberbrick`),
  danh mục `maker/robotics-cad/library/components.yaml`, file ở `community/cyberbrick-official/`.
- An toàn: pin PC003 là Li-ion 2S 7,4 V – không sạc khi không có người, không để chập cổng XH2.54.
- Khung/chi tiết in 3D trên Bambu A1 (xem `maker/in-3d`).
- TODO: động cơ, servo, pin (loại, điện áp).

## Cách làm
- Code trong `firmware/`; ghi rõ cách nạp code vào board.
- Chi tiết CAD trong `cad/`, đơn vị mm.

## Agent
`embedded-systems`, `python-pro`.
