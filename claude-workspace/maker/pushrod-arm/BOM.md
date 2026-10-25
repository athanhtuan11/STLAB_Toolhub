# BOM – pushrod-arm

Sinh tự động từ `freecad/pushrod_arm.FCStd` bằng `maker/robotics-cad/scripts/bom.py` – **không sửa tay** (sửa Label trong model rồi chạy lại *Chuẩn bị in*).

## Vít
| Vít | SL | Dùng ở |
|---|---|---|
| M2.5 × 10 | 2 | gear 2 |
| M2.5 × 16 | 4 | receiver 4 |
| M2.5 × 6 | 21 | Pin_A 1, Pin_B 1, Pin_C 1, Pin_D 1, Pin_E 1, Pin_S 1, pin 1, shaft_Elbow 1, shaft_Shoulder 1, top 2, turret 4, wrist 4, wrist_spacer 2 |
| M2.5 × 8 | 4 | deck 4 |

## Linh kiện mua
| Tên (Label) | SL |
|---|---|
| `CB_030_gearbox_Elbow` | 1 |
| `CB_030_gearbox_Shoulder` | 1 |
| `CB_Servo9g_180_gripper` | 1 |
| `CB_Servo9g_360_turntable` | 1 |
| `CB_XA003_XA004_receiver` | 1 |

## Chi tiết in 3D
| Chi tiết | Bàn in | Nhựa | Thể tích (cm³) |
|---|---|---|---|
| `Base_deck` | P1_Base__0.24Draft_PETG | Bambu PETG Basic @BBL A1 | 24.43 |
| `Base_foot` | P1_Base__0.24Draft_PETG | Bambu PETG Basic @BBL A1 | 10.68 |
| `Base_housing` | P1_Base__0.24Draft_PETG | Bambu PETG Basic @BBL A1 | 66.50 |
| `Receiver_riser` (4 miếng) | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.70 |
| `Slide_ring` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 2.09 |
| `Spacer_A` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 1.28 |
| `Spacer_A001` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 1.28 |
| `Spacer_D` (2 miếng) | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 1.94 |
| `Spacer_E` (2 miếng) | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.14 |
| `Spacer_S` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.97 |
| `Spacer_S001` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.97 |
| `Turntable` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 33.20 |
| `Turntable_gear_m1_z60` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 10.38 |
| `Turret_one_piece` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 54.94 |
| `Washer_shaft_Elbow` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.06 |
| `Washer_shaft_Shoulder` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 0.06 |
| `Wrist_spacer` | P2_Turret_Turntable__0.20_PETG | Bambu PETG Basic @BBL A1 | 1.68 |
| `Forearm_plate_L` | P3_Forearm_Plates__0.20_PETG | Bambu PETG Basic @BBL A1 | 12.86 |
| `Forearm_plate_R` | P3_Forearm_Plates__0.20_PETG | Bambu PETG Basic @BBL A1 | 12.84 |
| `Gripper_top_plate` | P3_Forearm_Plates__0.20_PETG | Bambu PETG Basic @BBL A1 | 1.69 |
| `Boom001` | P4_Boom_Gripper_Housings__0.20_PETG | Bambu PETG Basic @BBL A1 | 74.01 |
| `Gripper_frame` | P4_Boom_Gripper_Housings__0.20_PETG | Bambu PETG Basic @BBL A1 | 12.70 |
| `Housing_Elbow` | P4_Boom_Gripper_Housings__0.20_PETG | Bambu PETG Basic @BBL A1 | 15.01 |
| `Housing_Shoulder` | P4_Boom_Gripper_Housings__0.20_PETG | Bambu PETG Basic @BBL A1 | 15.01 |
| `Jaw_1_driven_by_servo` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 2.34 |
| `Jaw_2_idler` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 2.57 |
| `Pinion_WormWheel_Elbow` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 1.80 |
| `Pinion_WormWheel_Shoulder` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 1.80 |
| `Pinion_m1_z10_turntable` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.33 |
| `Rack_Elbow` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 3.34 |
| `Rack_Shoulder` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 3.34 |
| `Spacer_jaw2` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.27 |
| `Washer_pin` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.07 |
| `Jaw_1_driven_by_servo_TPU_pad` | P6_GripperPads__TPU95A | Bambu TPU 95A @BBL A1 | 0.18 |
| `Jaw_2_idler_TPU_pad` | P6_GripperPads__TPU95A | Bambu TPU 95A @BBL A1 | 0.18 |
| `Worm_Elbow` | P7_Worms__0.12_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.76 |
| `Worm_Shoulder` | P7_Worms__0.12_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.76 |
| `Pin_A` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.93 |
| `Pin_A_washer` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_B` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.44 |
| `Pin_B_washer` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_C` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.44 |
| `Pin_C_washer` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_D` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.58 |
| `Pin_D_washer` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_E` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.58 |
| `Pin_E_washer` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_S` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.93 |
| `Pin_S_washer` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_gearbox_Elbow` (2 miếng) | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.31 |
| `Pin_gearbox_Shoulder` (2 miếng) | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.31 |
| `Pin_jaw2` | P8_Pins__0.16_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.37 |

## Bàn in (số liệu slicer)
| Bàn | Thời gian | Nhựa (g) | Support |
|---|---|---|---|
| P1_Base__0.24Draft_PETG | 2h27 | 92.9 | – |
| P2_Turret_Turntable__0.20_PETG | 2h56 | 76.3 | – |
| P3_Forearm_Plates__0.20_PETG | 0h41 | 21.3 | – |
| P4_Boom_Gripper_Housings__0.20_PETG | 2h29 | 71.5 | – |
| P5_Gears_Racks_Pins__0.16_PETG | 1h13 | 16.9 | – |
| P6_GripperPads__TPU95A | 0h05 | 0.6 | – |
| P7_Worms__0.12_PETG_100pct | 0h34 | 1.9 | – |
| P8_Pins__0.16_PETG_100pct | 0h29 | 6.8 | – |
| **Tổng** | **10h58** | **288.2** | |

## Chưa phân loại (TODO)
Label không khớp quy ước vít / `components=` / `export.rules`:

- `Battery_bay`
- `Servo_horn`
