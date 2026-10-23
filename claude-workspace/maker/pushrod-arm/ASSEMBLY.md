# Hướng dẫn lắp ráp – pushrod-arm

Viết 2026-10-23 từ model hiện tại (`freecad/pushrod_arm.FCStd`). Thứ tự, vít, chốt lấy từ đo tiếp xúc giữa các chi tiết
trong model; chỗ model không thể hiện ghi **TODO**. Ảnh: `freecad/images/assembly/step-XX-a.png` (toàn cảnh) và
`-b.png` (phóng to) – phần đã lắp làm mờ, **chi tiết mới tô xanh**. Render lại khi sửa model:
gửi `freecad/scripts/render_assembly.py` qua RPC FreeCAD (xem đầu file).

## Trước khi lắp
- In đủ 7 bàn (`print/plates/`, PETG Basic + TPU). Gỡ chi tiết khi **bàn đã nguội** (PETG bám chặt PEI).
- Bàn P4 có support: gỡ sạch support ở Boom, khung kẹp và tai chốt 2 Housing.
- Thử lắp trước: mọi chốt in (`Pin_*`) phải xoay tự do trong lỗ (khe thiết kế 0,19 mm). Chặt thì làm sạch lỗ, không ép mạnh.
- **An toàn:** chưa cắm pin trong lúc lắp. Loại pin/điện áp khoang `Battery_bay`: TODO (xem datasheet CyberBrick XA003/XA004).

## Vít và linh kiện (tổng)
| Vít | SL | Dùng ở |
|---|---|---|
| M2.5 × 6 | 21 | turret 4, wrist spacer 2, nắp kẹp 2, chốt hàm 1, khung kẹp 4, trục bánh vít 2, khóa 6 chốt in 6 |
| M2.5 × 8 | 4 | deck → vỏ đế |
| M2.5 × 10 | 2 | bánh răng z60 → mâm xoay |
Linh kiện mua: CyberBrick XA003 + XA004 (+ socket 2×8), servo 9g 360° và 180°, 2 động cơ N20 – xem `README.md`.

## Bước 1 – Đế
![](freecad/images/assembly/step-01-a.png)
- Đặt `Base_housing` lên `Base_foot`. Cách cố định chân đế: **TODO** (model không có vít).

## Bước 2 – Điện tử và servo xoay đế (bên trong vỏ đế)
![](freecad/images/assembly/step-02-a.png)
- Đặt `Battery_bay` và mạch `CB_XA004_receiver` vào vỏ đế; cắm `Socket_2x8` lên XA004, cắm `CB_XA003_core` lên socket.
- Đặt `CB_Servo9g_360_turntable` vào hốc trong vỏ đế; ép `Pinion_m1_z10_turntable` (bánh răng 10 răng) lên trục servo.
- Cách giữ servo và mạch trong vỏ: **TODO** (model không có vít/kẹp).

## Bước 3 – Cụm mâm xoay (làm NGOÀI vỏ đế)
![](freecad/images/assembly/step-03-a.png)
- Đặt `Slide_ring` lên `Base_deck`, đặt `Turntable` lên vòng trượt.
- **Từ dưới deck**, áp `Turntable_gear_m1_z60` vào mâm xoay và bắt **2 vít M2.5 × 10 từ dưới lên**.
  Bánh răng và mâm kẹp deck ở giữa – phải làm bước này trước khi bắt deck vào vỏ (sau đó không với tới mặt dưới).

## Bước 4 – Gắn cụm mâm xoay lên đế
![](freecad/images/assembly/step-04-b.png)
- Hạ cụm bước 3 xuống vỏ đế sao cho **bánh răng z60 ăn khớp bánh răng 10 răng** của servo.
- Bắt **4 vít M2.5 × 8 từ trên xuống** qua deck vào 4 vấu trong vỏ đế. Xoay thử mâm bằng tay: phải êm, không kẹt.

## Bước 5 – Turret
![](freecad/images/assembly/step-05-a.png)
- Đặt `Turret_one_piece` lên mâm xoay; bắt **4 vít M2.5 × 6 từ trong turret xuống** mâm.

## Bước 6 – Hai cụm xi-lanh (vai và khuỷu, làm giống nhau)
![](freecad/images/assembly/step-06-b.png)
- Ép động cơ `CB_N20_*` vào vỏ `Housing_*`; lắp `Worm_*` (trục vít) lên trục N20.
- Đặt `Pinion_WormWheel_*` (bánh vít + bánh răng) vào vỏ, ăn khớp trục vít; từ phía ngoài lắp `Washer_shaft_*` rồi
  **vít M2.5 × 6** vào tâm bánh vít. Washer cố ý hở 0,1–0,2 mm – bánh vít phải quay tự do.
- Luồn thanh răng `Rack_*` qua vỏ, ăn khớp bánh răng. Đẩy kéo tay thử: chạy hết hành trình không kẹt.
- Cách giữ N20 và trục vít trên trục động cơ: **TODO** (kiểm khi lắp thật).

## Bước 7 – Cần chính (Boom) lên turret – chốt S
![](freecad/images/assembly/step-07-b.png)
- Đặt `Boom001` vào giữa 2 tai turret, mỗi bên một `Spacer_S`.
- Luồn `Pin_S` xuyên qua tai turret – đệm – Boom – đệm – tai turret; đầu kia lắp `Pin_S_washer` + **vít M2.5 × 6**.

## Bước 8 – Xi-lanh vai – chốt A và B
![](freecad/images/assembly/step-08-b.png)
- **Chốt A:** tai `Housing_Shoulder` vào giữa 2 tai turret, mỗi bên một `Spacer_A`; luồn `Pin_A`, khóa washer + vít M2.5 × 6.
- **Chốt B:** đầu thanh răng `Rack_Shoulder` vào Boom; luồn `Pin_B`, khóa washer + vít M2.5 × 6.

## Bước 9 – Cụm cẳng tay (Forearm)
![](freecad/images/assembly/step-09-a.png)
- Ghép `Forearm_plate_L` và `Forearm_plate_R` với `Wrist_spacer` ở giữa: **2 vít M2.5 × 6**, mỗi tấm một vít từ ngoài vào.
- Đặt sẵn `Spacer_D` và `Spacer_E` (mỗi cái gồm 2 miếng) vào lỗ chốt D và E giữa 2 tấm.

## Bước 10 – Cẳng tay lên Boom – chốt E (khuỷu)
![](freecad/images/assembly/step-10-b.png)
- Kẹp đầu Boom vào giữa 2 tấm cẳng tay (đệm `Spacer_E`); luồn `Pin_E`, khóa washer + vít M2.5 × 6.

## Bước 11 – Xi-lanh khuỷu – chốt C và D
![](freecad/images/assembly/step-11-b.png)
- **Chốt C:** tai `Housing_Elbow` vào Boom; luồn `Pin_C`, khóa washer + vít M2.5 × 6.
- **Chốt D:** đầu thanh răng `Rack_Elbow` vào giữa 2 tấm cẳng tay (đệm `Spacer_D`); luồn `Pin_D`, khóa washer + vít.

## Bước 12 – Cụm kẹp (làm riêng)
![](freecad/images/assembly/step-12-b.png)
- Đặt `CB_Servo9g_180_gripper` vào hốc `Gripper_frame` (khe 0,2 mm).
- Đưa servo về **vị trí giữa** trước khi gắn horn (khuyến nghị chung khi lắp servo), ép `Servo_horn` lên trục, gắn
  `Jaw_1_driven_by_servo` lên horn. Vít horn: TODO (thường đi kèm servo).
- Cắm `Pin_jaw2` vào khung, lồng `Spacer_jaw2` rồi `Jaw_2_idler`; răng của 2 hàm phải ăn khớp (khe răng 0,14 mm).
- Đậy `Gripper_top_plate`: **2 vít M2.5 × 6** vào khung; khóa đầu chốt hàm bằng `Washer_pin` + **vít M2.5 × 6**.
- Gắn 2 đệm TPU (`*_TPU_pad`) vào mặt kẹp của 2 hàm. Cách gắn: **TODO** (dán / ép).

## Bước 13 – Kẹp lên cẳng tay
![](freecad/images/assembly/step-13-a.png)
- Đưa khung kẹp vào giữa 2 tấm cẳng tay; **4 vít M2.5 × 6**, mỗi bên 2 vít.

## Sau khi lắp
- Xoay tay từng khớp bằng tay (chưa cấp điện): không kẹt, không cạ. Tầm hoạt động thiết kế: xem macro
  `freecad/pushrod_arm_sim.FCMacro` (xi-lanh vai 92–118 mm, khuỷu 92–128 mm, kẹp −55…+3°, đế ±170°).
- Đấu dây N20 ×2, servo ×2 vào XA004: **TODO** (cổng nào cho khớp nào – chưa có thông tin).
- Cấp điện lần đầu: chạy chậm, theo dõi nhiệt động cơ N20 (trục vít tự hãm – kẹt cơ khí sẽ tăng dòng).
- In xong và lắp xong: ghi kết quả bằng `/print-result pushrod-arm <plate> pass|fail`.
