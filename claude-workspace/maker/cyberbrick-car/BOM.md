# BOM – cyberbrick-car

Sinh tự động từ `freecad/cyberbrick_car.FCStd` bằng `tools/robotics-cad/scripts/bom.py` – **không sửa tay** (sửa Label trong model rồi chạy lại *Chuẩn bị in*).

## Vít
| Vít | SL | Dùng ở |
|---|---|---|
| M2 × 6 | 2 | switch 2 |
| M2 × 8 | 3 | horn_pin 1, servo 2 |
| M2.5 × 16 | 2 | kingpin_L 1, kingpin_R 1 |
| M2.5 × 6 | 10 | axle_L 1, axle_R 1, receiver 4, strap_L 1, strap_R 1, tierod_L 1, tierod_R 1 |

## Linh kiện mua
| Tên (Label) | SL |
|---|---|
| `CB_Battery_PC003` | 1 |
| `CB_Gearbox_030_dual_axis` | 1 |
| `CB_Gearbox_shaft_left` | 1 |
| `CB_Magnet_CA001 (nam cham 4 x 2 mm)` | 8 |
| `CB_Servo9g_180_steering` | 1 |
| `CB_Switch_XA007` | 1 |
| `CB_Tire_LA027 (lop cao su D33.7 x 13.85)` | 4 |
| `CB_XA004_receiver` | 1 |
| `LK_Servo_horn` | 1 |

## Chi tiết in 3D
| Chi tiết | Bàn in | Nhựa | Thể tích (cm³) |
|---|---|---|---|
| `Body_coupe` | P1_Body__0.20_PETG | Bambu PETG Basic @BBL A1 | 80.18 |
| `Chassis` | P2_Chassis_Steering__0.20_PETG | Bambu PETG Basic @BBL A1 | 31.09 |
| `Gearbox_strap` | P2_Chassis_Steering__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.32 |
| `Knuckle_L` | P2_Chassis_Steering__0.20_PETG | Bambu PETG Basic @BBL A1 | 1.34 |
| `Knuckle_R` | P2_Chassis_Steering__0.20_PETG | Bambu PETG Basic @BBL A1 | 1.34 |
| `Tie_rod` | P2_Chassis_Steering__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.36 |
| `Washer_axle_L` | P2_Chassis_Steering__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.04 |
| `Washer_axle_R` | P2_Chassis_Steering__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.04 |
| `Wheel_FL` | P3_Wheels__0.16_PETG | Bambu PETG Basic @BBL A1 | 4.52 |
| `Wheel_FR` | P3_Wheels__0.16_PETG | Bambu PETG Basic @BBL A1 | 4.52 |
| `Wheel_RL` | P3_Wheels__0.16_PETG | Bambu PETG Basic @BBL A1 | 5.07 |
| `Wheel_RR` | P3_Wheels__0.16_PETG | Bambu PETG Basic @BBL A1 | 5.07 |

## Bàn in (số liệu slicer)
| Bàn | Thời gian | Nhựa (g) | Support |
|---|---|---|---|
| P1_Body__0.20_PETG | 4h18 | 59.9 | – |
| P2_Chassis_Steering__0.20_PETG | 1h30 | 34.3 | – |
| P3_Wheels__0.16_PETG | 1h26 | 20.4 | – |
| **Tổng** | **7h15** | **114.6** | |
