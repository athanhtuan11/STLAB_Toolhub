# BOM – pushrod-arm

Sinh tự động từ `freecad/pushrod_arm.FCStd` bằng `maker/robotics-cad/scripts/bom.py` – **không sửa tay** (sửa Label trong model rồi chạy lại *Chuẩn bị in*).

## Vít
| Vít | SL | Dùng ở |
|---|---|---|
| M2.5 × 10 | 2 | gear 2 |
| M2.5 × 6 | 21 | Pin_A 1, Pin_B 1, Pin_C 1, Pin_D 1, Pin_E 1, Pin_S 1, pin 1, shaft_Elbow 1, shaft_Shoulder 1, top 2, turret 4, wrist 4, wrist_spacer 2 |
| M2.5 × 8 | 4 | deck 4 |

## Linh kiện mua
| Tên (Label) | SL |
|---|---|
| `CB_N20_Elbow` | 1 |
| `CB_N20_Shoulder` | 1 |
| `CB_Servo9g_180_gripper` | 1 |
| `CB_Servo9g_360_turntable` | 1 |
| `CB_XA003_core` | 1 |
| `CB_XA004_receiver` | 1 |
| `Socket_2x8` | 1 |

## Chi tiết in 3D
| Chi tiết | Bàn in | Nhựa | Thể tích (cm³) |
|---|---|---|---|
| `Base_deck` | P1_Base__0.24Draft_PETG | Bambu PETG Basic @BBL A1 | 24.43 |
| `Base_foot` | P1_Base__0.24Draft_PETG | Bambu PETG Basic @BBL A1 | 10.68 |
| `Base_housing` | P1_Base__0.24Draft_PETG | Bambu PETG Basic @BBL A1 | 66.50 |
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
| `Boom001` | P4_Boom_Gripper_Housings__0.20_PETG_support | Bambu PETG Basic @BBL A1 | 74.01 |
| `Gripper_frame` | P4_Boom_Gripper_Housings__0.20_PETG_support | Bambu PETG Basic @BBL A1 | 12.70 |
| `Housing_Elbow` | P4_Boom_Gripper_Housings__0.20_PETG_support | Bambu PETG Basic @BBL A1 | 13.01 |
| `Housing_Shoulder` | P4_Boom_Gripper_Housings__0.20_PETG_support | Bambu PETG Basic @BBL A1 | 13.01 |
| `Jaw_1_driven_by_servo` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 2.34 |
| `Jaw_2_idler` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 2.57 |
| `Pin_A` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.99 |
| `Pin_A_washer` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_B` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.47 |
| `Pin_B_washer` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_C` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.47 |
| `Pin_C_washer` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_D` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.62 |
| `Pin_D_washer` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_E` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.62 |
| `Pin_E_washer` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_S` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.99 |
| `Pin_S_washer` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.07 |
| `Pin_jaw2` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.43 |
| `Pinion_WormWheel_Elbow` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 1.80 |
| `Pinion_WormWheel_Shoulder` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 1.80 |
| `Pinion_m1_z10_turntable` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.33 |
| `Rack_Elbow` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 3.34 |
| `Rack_Shoulder` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 3.34 |
| `Spacer_jaw2` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.27 |
| `Washer_pin` | P5_Gears_Racks_Pins__0.16_PETG | Bambu PETG Basic @BBL A1 | 0.07 |
| `Jaw_1_driven_by_servo_TPU_pad` | P6_GripperPads__TPU95A | Bambu TPU 95A @BBL A1 | 0.18 |
| `Jaw_2_idler_TPU_pad` | P6_GripperPads__TPU95A | Bambu TPU 95A @BBL A1 | 0.18 |
| `Worm_Elbow` | P7_Worms__0.12_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.31 |
| `Worm_Shoulder` | P7_Worms__0.12_PETG_100pct | Bambu PETG Basic @BBL A1 | 0.31 |

## Bàn in (số liệu slicer)
| Bàn | Thời gian | Nhựa (g) | Support |
|---|---|---|---|
| P1_Base__0.24Draft_PETG | 2h27 | 92.9 | – |
| P2_Turret_Turntable__0.20_PETG | 2h48 | 74.3 | – |
| P3_Forearm_Plates__0.20_PETG | 0h41 | 21.3 | – |
| P4_Boom_Gripper_Housings__0.20_PETG_support | 2h40 | 69.3 | có |
| P5_Gears_Racks_Pins__0.16_PETG | 1h28 | 21.8 | – |
| P6_GripperPads__TPU95A | 0h04 | 0.5 | – |
| P7_Worms__0.12_PETG_100pct | 0h14 | 0.9 | – |
| **Tổng** | **10h26** | **281.0** | |

## Chưa phân loại (TODO)
Label không khớp quy ước vít / `components=` / `export.rules`:

- `Battery_bay`
- `Servo_horn`
