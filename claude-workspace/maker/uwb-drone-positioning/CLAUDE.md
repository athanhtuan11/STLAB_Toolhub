# uwb-drone-positioning

## Mục tiêu
TODO: định vị drone trong nhà bằng UWB (độ chính xác mong muốn, tính bằng mm).

## Thành phần
- TODO: module UWB (vd. DW1000/DW3000?), số anchor, tag, vi điều khiển.
- TODO: flight controller và giao thức gửi vị trí.
- Bố trí anchor ghi tọa độ (mm) trong `docs/anchors.md`.

## Quy ước
- Thuật toán (TWR/TDoA, lọc Kalman): ghi giả định và đơn vị.
- Thử nghiệm bay: tháo cánh khi test trên bàn; có kill-switch.

## Agent
`embedded-systems`, `cpp-pro`.
