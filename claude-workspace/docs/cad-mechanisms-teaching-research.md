# Nghiên cứu: cơ cấu cánh tay robot in 3D, nối trục – trục vít, kiểm lắp trước khi in, dạy CAD (STLab)

Viết 2026-10-25 để tham khảo cho `maker/pushrod-arm` và việc dạy CAD ở STLab. **Chỉ là nghiên cứu và đề xuất.**
Tuan quyết có cải tiến hay không. File này không sửa code hay model nào.

**Phạm vi:** 4 chủ đề mới:
- (1) cơ cấu từng khớp của các cánh tay in 3D mã nguồn mở;
- (2) nối trục, trục vít, thanh răng in (tự hãm, hiệu suất, mòn, bôi trơn);
- (3) kiểm khớp lắp **trước** khi in;
- (4) dạy CAD cho học sinh.

**Không lặp lại:** những phần dưới đây đã có, ở đây chỉ trỏ link:
- dung sai Prusa/Bambu, bù lỗ, insert Ruthex, hướng sợi và TDS PETG, bánh răng in (Gears WB), cách SO-ARM100/Thor tổ chức repo và `Gauge_0`, ngưỡng brim, vòng đo thước kẹp: [cad-community-gaps-research.md](cad-community-gaps-research.md);
- FreeCAD CLI, test, CI: [freecad-automation-research.md](freecad-automation-research.md), [reports/freecad-community-automation.md](reports/freecad-community-automation.md);
- quy trình, release: [cad-standard-workflow.md](cad-standard-workflow.md);
- bước 0 hình dáng: [design-first-research.md](design-first-research.md).

**Nhãn nguồn:**
- **[nguồn gốc]**: repo, tài liệu hãng/dự án, paper, datasheet.
- **[máy]**: đọc file trên máy, không chạy gì.
- **[tính]**: Claude tự tính theo công thức có nguồn và tham số lấy từ script của STLab.
- **(thứ cấp)**: blog, forum, đại lý.
- `TODO`: chưa xác nhận.

Số sao và ngày push gần nhất tra bằng GitHub REST API ngày **2026-10-25**.

## 0. Kết luận nhanh

1. **Trục vít của pushrod-arm tự hãm "sát ngưỡng", chưa chắc chắn.** Trục vít m1, 1 mối ren, Ø vòng chia 8 mm,
   nên góc xoắn λ ≈ **7,1°** [tính]. Theo công thức của MathWorks, bộ truyền tự hãm khi hệ số ma sát
   **k > cos20°·tan λ ≈ 0,12**. KHK (hãng bánh răng Nhật) cho biết tự hãm dựa vào ma sát nên "thiếu ổn định": rung có thể
   làm quay ngược, và nếu cần chặn quay ngược hoàn toàn thì nên kết hợp thêm cách khác. Một nguồn chép lại tài liệu KHK
   (thứ cấp) ghi ngưỡng kinh nghiệm **< 4°** cho trục vít 1 mối. **Bôi mỡ làm giảm k, nên có thể làm mất tự hãm.**
   Hệ số k của cặp PETG–PETG: `TODO` (chưa có nguồn).
2. **Hiệu suất trục vít nhựa thấp và tỏa nhiệt.** KHK ghi trục vít trụ thường đạt khoảng **30–60 %**. Với λ = 7,1° thì
   η ≈ 53 % (k = 0,10) đến 31 % (k = 0,25) [tính]. KHK cũng ghi nhiệt ở vùng trượt làm bộ truyền **giảm bền nhanh và mòn bất thường**.
   KHK nói bôi trơn "là sống còn" với cặp trục vít nhựa khi tải cao và chạy liên tục. Vậy tự hãm và bôi trơn kéo ngược nhau,
   cần thử thật để chọn.
3. **Trong 7 cánh tay mở đã đọc, không cánh tay phổ biến nào dùng trục vít in cho khớp chính.**
   - SO-ARM100 và low_cost_robot: servo bus gắn thẳng vào khớp, servo đã có hộp số kim loại.
   - PAROL6: đai (4–6,4:1) + planetary (10–20:1).
   - Faze4: cycloid in.
   - Thor và Moveo: đai GT2/T5 + động cơ bước có hộp số planetary.

   Mẫu duy nhất dùng trục vít để giữ tay khi mất điện là bài báo **Howard 2023**. Bài này dùng **động cơ DC có hộp số
   trục vít mua sẵn** (tỉ số 280), không in trục vít, và vẫn ghi nhận rơ ở hộp số trục vít.
4. **Lỗ in thường nhỏ hơn thiết kế, nên khe nối trục phải lấy từ mẫu đo.** Nophead (polyholes) giải thích lỗ co vì 4 cơ chế
   và đưa ra công thức `n = 2·d`, `r = (d/2)/cos(180/n)`. Không tìm được bài báo hay tài liệu hãng nào cho số "khe ép" cho PETG.
   Số cụ thể duy nhất từ hãng: Prusa đề xuất **0,15 mm mọi phía** cho đai ốc/nam châm nhét giữa lúc in
   (MK3S, đầu phun 0,4 mm, lớp 0,15 mm). STLab đang dùng khe hướng kính 0,32 mm cho lỗ trục D Ø5,3 mm. Số này hợp lý
   nhưng chưa có mẫu đo (đã nêu trong tài liệu cũ, mục 2).
5. **Mỡ cho nhựa: chọn loại mà hãng ghi rõ dùng được cho nhựa.**
   - MOLYKOTE EM-30L (DuPont) ghi "Compatible with most plastics", dùng cho bánh răng/hộp số, gốc dầu PAO + PTFE, −45…150 °C, NLGI 1.
   - TDS Super Lube 21030 **không** nói gì về nhựa.
   - KHK nhắc: dầu mỡ dùng cho bánh răng kim loại có thể làm hỏng nhựa.
   - Hướng dẫn lắp hộp số 030 của Bambu chỉ ghi "bôi lượng mỡ thích hợp", không nêu loại mỡ (`TODO`).
6. **Lỗ trục ở Worm bị lấp không phải lỗi riêng của STLab.** Slicer của Bambu có sẵn công cụ cho tình huống này:
   - `max_bridge_length` (mặc định 10 mm): cầu ngắn hơn mức này thì không cần support;
   - `support_type = normal(manual)/tree(manual)`: chỉ sinh support ở chỗ được tô;
   - support blocker (tô chặn support).

   SO-ARM100 có một luật cấm tương tự: "không support trong lỗ vít trục ngang". Bước kiểm còn thiếu là **đọc G-code
   theo lớp** (`; FEATURE: Support`) xem có đường support nào nằm trong vùng lỗ chức năng không. Cách này bắt được
   mọi nguồn support, kể cả support tự vẽ.
7. **Dạy CAD có công cụ miễn phí cho cả 3 cấp, nhưng điều kiện license khác nhau.**
   - Tinkercad: lớp học bằng mã, không cần email, có chứng nhận kidSAFE (COPPA).
   - Onshape Education: miễn phí; dưới 13 tuổi phải có người lớn đủ điều kiện tạo/cho phép tài khoản; chỉ dùng phi thương mại.
   - Fusion Education: phải là **cơ sở giáo dục được công nhận** (accredited), xác minh qua SheerID.
     Trung tâm tư nhân như STLab có đủ điều kiện không: `TODO`, phải hỏi Autodesk.
   - FreeCAD (LGPL-2.1): không ràng buộc gì.

   Khung tiến trình theo độ tuổi có nguồn mở: NGSS ETS1 (K-2 / 3-5 / THCS / THPT).
8. **Mẫu bài đáng học nhất cho STLab là "đồng hồ đo trước, chi tiết sau".** SO-ARM100 làm như vậy. Học sinh cũng có thể làm
   bài reverse engineering: đo một linh kiện thật (servo, hộp số 030), dựng lại hốc lắp, in mẫu đo, sửa lại.
   Bài này vừa dạy CAD vừa sinh dữ liệu khe cho STLab.

## 1. Cơ cấu khớp của cánh tay robot in 3D mã nguồn mở

### 1.1 Cộng đồng làm gì

| Dự án (sao, push gần nhất, license) | Truyền động từng khớp | Ổ bi / trượt | Chống rơ | Giữ tay khi mất điện | Dây qua khớp |
|---|---|---|---|---|---|
| [SO-ARM100/101](https://github.com/TheRobotStudio/SO-ARM100) (7 866★, 2026-10-06, Apache-2.0) [nguồn gốc] | Cả 6 khớp gắn **thẳng servo bus STS3215** có hộp số trong servo. Tay theo (follower): 6 × 1/345 (7,4 V, 16,5 kg·cm ở 6 V) hoặc bản 12 V (30 kg·cm). Tay dẫn (leader): 3 × 1/147, 2 × 1/191, 1 × 1/345 | README không nêu | Dựa vào hộp số servo | README không nêu (`TODO`; servo thường không tự hãm) | README không nêu |
| [low_cost_robot](https://github.com/AlexanderKoch-Koch/low_cost_robot) (3 423★, 2024-09-21, MIT) [nguồn gốc] | Servo Dynamixel gắn thẳng: 2 × XL430-W250 cho 2 khớp đầu, 4 × XL330-M288 (18 g) cho các khớp còn lại | Không nêu | Không nêu | Không nêu | Không nêu |
| [PAROL6](https://github.com/Source-Robotics/PAROL6-Desktop-robot-arm) (3 400★, 2026-10-22, GPL-3.0) [nguồn gốc, [docs](https://docs.source-robotics.com/PAROL-docs/page2_2/)] | Động cơ bước. J1 đai 6,4:1; J2 planetary 20:1; J3 planetary × đai 38:42 = 18,095:1; J4, J5 đai 4:1; J6 planetary 10:1 | Không nêu | Lặp lại vị trí 0,1 mm (hãng công bố) | Không nêu phanh (`TODO`) | Không nêu |
| [Thor](https://github.com/AngelLM/Thor) (1 627★, 2025-05-09, **CC-BY-SA-4.0**) [nguồn gốc, [Hackaday](https://hackaday.io/project/12989)] | Động cơ bước có hộp số cho khớp 2–3; GT2 cho khớp 3, 5, 6; cổ tay "bán vi sai" (2 bánh nhỏ đẩy 1 bánh lớn); NEMA 17 39,22 N·cm. Tỉ số từng khớp: `TODO` | Khớp 4: **ổ bi tự in dùng bi airsoft 6 mm** | Tác giả nói ổ bi khớp 4 "gần như không rơ" | Không nêu | Không nêu; cảm biến quang cho phép quay > 360° |
| [BCN3D Moveo](https://github.com/BCN3D/BCN3D-Moveo) (2 010★, 2022-03-01, MIT; mục tiêu giáo dục) [nguồn gốc, BOM PDF] | Đai **T5** (bánh đai 10/14 răng, đai Breco rộng 16 mm); 1 NEMA 17 có planetary 5:1 (17HS19-1684S-PG5); 1 NEMA 23; servo 13 kg·cm cho kẹp | **608ZZ** ×1, 625ZZ ×1, **624ZZ ×8**, 623ZZ ×1, bạc tự bôi trơn 5×8×10 và 8×12×20 mm | Không nêu | Không nêu | Không nêu |
| [Faze4](https://github.com/Source-Robotics/Faze4-Robotic-arm) (912★, 2025-12-28; API ghi CERN-OHL-S-2.0, README ghi MIT, `TODO` xác nhận) [nguồn gốc] | **Hộp số cycloid in** ("ít rơ, dễ sửa"); tỉ số `TODO` | Có ổ bi (loại `TODO`) | Nhờ cycloid | Không nêu | "Mọi dây đều giấu kín" |
| Arctos (CAD **bán**; [web](https://arctosrobotics.com/), [GitHub ROS](https://github.com/Arctos-Robotics) 103★) [nguồn gốc] | Động cơ bước NEMA 17/23 (driver CLMD vòng kín); tỉ số không công bố | – | Hãng nói độ chính xác phụ thuộc chủ yếu vào độ cứng nhựa | – | – |
| EEZYbotARM MK2 (Carlo Franciscone) | Servo hobby + **hình bình hành** (kẹp luôn song song đế; tỉ lệ 1:7 so với ABB IRB460 (thứ cấp)); khớp xoay trên vít M4 + đai ốc tự hãm (thứ cấp) | Không | – | – | – |
| **Howard 2023**, ASTESJ 8(5) ([paper](https://www.astesj.com/v08/i05/p09/), CC BY-SA 4.0) [nguồn gốc] | **Động cơ DC có hộp số trục vít mua sẵn** (giảm tốc 280, 24 V, 5 N·m, 28 vòng/phút), truyền ra khớp bằng **đai HTD 5M** 24→40 răng; hình bình hành kép | Đế: ổ bi 50×90×20 mm; khớp bình hành: 8×22×7 mm; khớp nhỏ: 3×10×4 mm ×16 | Ghi nhận "hơi rơ ở hộp số trục vít"; encoder trên động cơ không thấy được rơ/uốn | **Có**: trục vít không quay ngược nên **giữ tư thế không cần cấp điện** | Dây giới hạn khớp 1 ở ±45° |

Ghi chú: trang chính thức eezyrobots.it hiện chỉ có trang chờ, còn Thingiverse chặn truy cập tự động. Vì vậy loại servo
và license của EEZYbotARM là `TODO`. easyEEZYbotARM (120★) chỉ ghi license MIT cho **phần mềm**.

**Mẫu rút ra**
- **Robot giáo dục nhỏ (SO-ARM, low_cost_robot):** servo bus gắn thẳng vào khớp, chi tiết in chỉ là khung. Rơ và mòn nằm
  trong hộp số kim loại của servo, nên phần in gần như không bị mòn. Đổi lại, giá servo cao và tay rơi khi mất điện (`TODO` xác nhận).
- **Robot lớn hơn (PAROL6, Thor, Moveo):** động cơ bước + đai, cộng planetary ở vai. Ổ bi tiêu chuẩn 608/62x, hoặc ổ bi tự in cho khớp xoay lớn.
- **Cycloid in (Faze4):** cách cộng đồng giảm rơ mà vẫn in được, nhưng phức tạp, không hợp với robot cỡ 9g.
- **Giữ tay khi mất điện bằng trục vít:** chỉ thấy ở Howard 2023, mà dùng hộp số trục vít **mua sẵn**.

### 1.2 STLab đang làm gì (pushrod-arm)
- Đế: servo 9g 360° → pinion m1 z10 → vành z60 (6:1), mâm xoay **trượt trên `Slide_ring` in**, không ổ bi.
- Vai/khuỷu: động cơ 030 + hộp số nhựa 1 trục (STEP hãng ≈ 45,5:1) → **trục vít in m1 × 16:1** → bánh vít + pinion → thanh răng.
  Đây là "xi-lanh điện" kiểu đòn đẩy, gần với các tay đòn thủy lực.
- Kẹp: servo 180° gắn thẳng.
- Khớp chốt: chốt in + washer + vít M2.5, không ổ bi, không bạc.
- Giữ tay khi mất điện: dựa vào **trục vít in tự hãm**.
- Dây qua khớp: chưa thiết kế (ASSEMBLY bước cuối: cổng nào cho khớp nào là `TODO`).

### 1.3 Khoảng trống
- **Tự hãm chưa có số kiểm:** λ ≈ 7,1° lớn hơn ngưỡng kinh nghiệm < 4° (thứ cấp). Xem mục 2.3.
  Chưa có bài thử "tắt điện, treo tải ở đầu tay, đo độ trôi".
- **Trục vít chỉ được đỡ một đầu:** moay-ơ cắm vào trục ra của hộp số, đầu kia là gối chặn hở 0,3 mm.
  Khi tải lớn, lực tách răng đẩy trục vít lệch. Lực dọc trục dồn vào hộp số nhựa, và ASSEMBLY đã cảnh báo điều này.
  Các thiết kế trong bảng đều đỡ trục bằng ổ bi ở cả hai phía: `TODO` xác nhận từng dự án, đây là quan sát chung.
- **Khớp chốt in trượt nhựa trên nhựa:** Moveo dùng bạc tự bôi trơn hoặc ổ bi 62x ở những khớp tương đương.
  Ổ bi 623 (3×10×4 mm) hợp với cỡ chốt của pushrod-arm, nhưng phải đo ổ bi thật trước.
- **Chưa có quy ước đi dây.**

## 2. Nối trục và truyền động in 3D

### 2.1 Cộng đồng làm gì – nối trục
- **Lỗ in co nhỏ** [nguồn gốc, nophead/HydraRaptor]. Có 4 nguyên nhân: đa giác hóa (`cos(π/n)`), đầu phun chảy nhựa khi dừng
  ở các đoạn ngắn, sợi nhựa uốn cong, và đầu phun đi tắt ở góc (tác giả cho là nguyên nhân chính). Giải pháp polyhole:
  dùng `n = max(round(2·d), 3)` cạnh, bán kính `r = (d/2)/cos(180/n)`. Tác giả nói số đo của mình "thô".
- **Khe ép (press-fit) cho FDM: không có số chuẩn từ nguồn gốc.**
  - Bài báo Tribology in Industry 2025 (vỏ PETG ép vào ổ bi thép): lực ép **giảm sau mỗi lần tháo lắp** do biến dạng dẻo và mòn,
    nhưng không đưa ra độ dôi theo mm.
  - Các số "0,1–0,2 mm ép nhẹ" lưu truyền trên mạng chỉ là hướng dẫn của đại lý (thứ cấp).
  - Kết luận: **phải in mẫu đo** (đã đề xuất ở [tài liệu cũ, mục 2](cad-community-gaps-research.md)).
- **Đai ốc/nam châm chìm** [nguồn gốc, blog Prusa]:
  - khe "phù hợp nhất 0,15 mm mọi phía" (MK3S, đầu phun 0,4 mm, lớp 0,15 mm);
  - dừng in ở đúng lớp **trước** lớp phủ hốc, kiểm trong preview vì người dùng hay đặt lệch 1 lớp;
  - nam châm phải chặt hoặc nhỏ keo, nếu không đầu phun sẽ hút nó ra.
- **Heat-set insert:** đã có ở tài liệu cũ, mục 3.
- **D / double-D / lục giác / then hoa (spline):**
  - SO-ARM100 và low_cost_robot dùng **horn của servo** (then hoa kim loại + vít) và không làm lỗ trục in → đây là cách bền nhất.
  - Moveo dùng **bánh đai kim loại** (lỗ 5 hoặc 8 mm) bắt vào trục động cơ: trục thép nối với nhôm, không qua nhựa.
  - **Không tìm được nguồn gốc nào cho số khe của lỗ double-D in.** Bambu đã có chi tiết in khớp đúng trục 030 này
    (vỏ hộp số in trong `community/cyberbrick-official/.../single axis/3D Printed Parts.3mf`), nhưng đó là vỏ, không phải
    moay-ơ trên trục ra. Chi tiết chính hãng có lỗ khớp trục ra (bánh xe Mini tank): `TODO` tìm file. Đây sẽ là nguồn số khe tốt nhất.
- **Set screw, kẹp trục (clamp):** cách làm cộng đồng hay dùng là hốc đai ốc vuông/lục giác + vít M3 chạm mặt vát D, hoặc moay-ơ xẻ rãnh có vít kẹp.
  Không có số khe từ nguồn gốc (`TODO`).

### 2.2 Cộng đồng làm gì – trục vít, bánh răng nhựa, bôi trơn
- **KHK, Worm Gears** [nguồn gốc]:
  - "Góc xoắn càng nhỏ, xu hướng tự hãm càng lớn". Tự hãm "dựa vào hệ số ma sát nên thiếu ổn định": ma sát nhỏ thì khó tự hãm,
    rung có thể làm quay ngược. Muốn chặn quay ngược hoàn toàn thì "nên kết hợp với cách khác".
  - Hiệu suất trục vít trụ khoảng **30–60 %**.
  - **Không khuyên khe răng bằng 0**, vì cần khe để giữ màng dầu.
  - Trục vít thường làm bằng vật liệu **cứng hơn** bánh vít. Bánh vít MC nylon "dùng được không bôi trơn".
  - Hệ số ma sát (cặp kim loại): sắt/sắt ≈ 0,3, sắt/đồng nhôm ≈ 0,2, sắt/đồng phốt pho ≈ 0,15.
- **KHK, Design of Plastic Gears** [nguồn gốc]:
  - nhựa giãn nở nhiệt và trương nở khi hút ẩm, nên **cần khe răng lớn hơn** bánh răng kim loại;
  - nếu một bánh trong cặp là kim loại thì nó tản nhiệt giúp cặp;
  - đa số bánh răng nhựa không cần bôi trơn, **nhưng cặp trục vít nhựa thì bôi trơn là sống còn** khi tải cao và chạy liên tục;
  - trục vít trượt nhiều nên nóng, dẫn tới **"giảm bền nhanh và mòn bất thường"**.
- **KHK Q&A:** mỡ không hợp với trục vít vì nóng mà khả năng làm mát thấp, KHK nghiêng về dầu.
  Dầu mỡ dành cho bánh răng kim loại có thể làm hỏng nhựa (trích qua tìm kiếm, `TODO` đọc nguyên trang).
- **MathWorks Simscape Worm Gear** [nguồn gốc], với λ = góc xoắn, α = góc áp lực pháp tuyến, k = hệ số ma sát:
  - hiệu suất khi trục vít dẫn: `η_WG = (cos α − k·tan λ)/(cos α + k/tan λ)`;
  - hiệu suất khi bánh vít dẫn ngược: `η_GW = (cos α − k/tan λ)/(cos α + k·tan λ)`;
  - tự hãm khi `cos α < k/tan λ`.
- **Mòn nhựa in** [nguồn gốc, igus, số do hãng tự công bố]:
  - filament tribo iglidur mòn ít hơn "tới 50 lần" vật liệu in thường. Số này đo trên tấm trượt, bạc và đai ốc, **không phải bánh răng**;
  - thử hành trình dài: i180 (FDM) mòn ít hơn **15 lần** so với ABS;
  - igus nêu trục vít là ứng dụng được, nhưng không có số đo cho trục vít.
- **Nhiệt:** HDT ở 0,45 MPa: PLA Basic 57 °C, PETG Basic 71 °C (TDS Bambu, đã chép ở `tools/robotics-cad/model-checks.md` 4.4).
  Hệ số ma sát và tốc độ mòn của PETG/PETG: `TODO`.
- **Mỡ** [nguồn gốc]:
  - MOLYKOTE EM-30L: "Compatible with most plastics", dùng cho "Gears, gear boxes", PAO + lithium + PTFE, −45…150 °C, NLGI 1.
  - Super Lube 21030 (TDS 08/2024): tổng hợp + Syncolon, NSF H1, không silicone, −43…232 °C, **không có dòng nào về nhựa**.
  - Hướng dẫn lắp hộp số 030 của Bambu: "nên bôi lượng mỡ thích hợp lên từng bánh răng", **không nêu loại mỡ**.
- **Module, biên dạng răng:** không có nguồn gốc nào cho module tối thiểu khi in FDM (đã ghi `TODO` ở tài liệu cũ, mục 5).

### 2.3 STLab đang làm gì – đối chiếu số thật [máy + tính]
Tham số đọc từ `freecad/scripts/history/2026-10-22_build_pushrods_v3.py`, `2026-10-24_cylinder_030_gearbox.py` và `2026-10-25_worm_socket_chamfer.py`:
- Trục vít: m1, 1 mối, bước ren = π mm, Ø đỉnh 10 mm, Ø vòng chia **8 mm**, α = 20°, khe răng `bl` 0,15 mm.
  Bánh vít z16, bl 0,25 mm, khoảng cách tâm 12 mm (khớp với (8 + 16)/2).
- Góc xoắn: `λ = atan(π / (π·8)) = atan(0,125) ≈ 7,1°`.
- Ngưỡng tự hãm: `k > cos20°·tan λ = 0,940 × 0,125 ≈ 0,117`.

| k (giả định) | η_WG (trục vít dẫn) | η_GW (bánh vít dẫn ngược) | Tự hãm? |
|---|---|---|---|
| 0,10 (có mỡ? `TODO`) | ≈ 53 % | ≈ +15 % → **quay ngược được** | Không |
| 0,15 | ≈ 43 % | < 0 | Có, sát ngưỡng |
| 0,25 (khô? `TODO`) | ≈ 31 % | < 0 | Có |

- Số trong bảng là [tính]. Hệ số k thật của PETG/PETG, khô và có mỡ, **chưa có nguồn**, phải đo.
  Cách đo đơn giản: mặt nghiêng, góc trượt φ → `k = tan φ`.
- Nối trục: lỗ D trên `Worm_*` có khe hướng kính 0,32 mm trên trục Ø5,3 mm (mặt vát cách nhau 3,6 mm).
  Miệng lỗ được vát 0,4 mm × 45° để bù elephant foot. Lỗ in đứng, nên đường tròn nằm trong mặt X-Y, đúng như nophead khuyên.
- Bôi trơn: ASSEMBLY chỉ ghi "bôi mỡ bánh răng" cho hộp số. Trục vít in chưa có chỉ dẫn loại mỡ.

### 2.4 Khoảng trống
- **Chưa biết pushrod-arm có thật sự tự hãm hay không.** Bôi mỡ để giảm nhiệt và mòn (theo khuyên của KHK) lại có thể làm mất tự hãm.
  Phương án dự phòng, chọn sau khi thử:
  - (a) giảm λ: trục vít Ø vòng chia lớn hơn hoặc module nhỏ hơn, giữ 1 mối. Ví dụ Ø16 mm cho λ ≈ 3,6° [tính],
    nhưng xi-lanh to ra và hiệu suất tụt xuống ≈ 22–37 % [tính, k 0,2–0,1];
  - (b) thêm phanh hoặc chốt cơ khí ở tư thế nghỉ;
  - (c) dùng động cơ có hộp số trục vít mua sẵn như Howard 2023.
- Trục vít PETG chạy trên bánh vít PETG: hai vật liệu như nhau, trái với lời khuyên "trục vít cứng hơn" của KHK.
  Phương án rẻ là in bánh vít bằng nhựa khác (PETG/PLA/TPU?, `TODO`). Phương án đúng sách hơn là trục vít kim loại, nhưng không in được.
- Chưa có **thử nhiệt**: chạy liên tục N chu kỳ, đo nhiệt vỏ và trục vít (nhiệt kế IR), so với HDT PETG 71 °C.

## 3. Kiểm khớp lắp trước khi in

### 3.1 Cộng đồng làm gì
- **Đồng hồ đo (gauge) và mẫu dung sai:** SO-ARM100 có `STL/Gauges`, mẫu Orca Tolerance Test, mẫu lỗ M3–M6 của Bambu.
  Đã có ở [tài liệu cũ, mục 2](cad-community-gaps-research.md).
- **Luật trong hướng dẫn in:** SO-ARM100 ghi "**không support trong lỗ vít trục ngang**", support ở mọi chỗ nhưng bỏ qua dốc > 45°.
- **Tùy chọn của slicer** [nguồn gốc, `PrintConfig.cpp` của Bambu Studio]:
  - `max_bridge_length`, mặc định **10 mm**: "cầu ngắn hơn mức này không cần support".
    Luật "mái lỗ kín ≤ 8 mm" (TẠM) của STLab nằm dưới số này.
  - `bridge_no_support`;
  - `support_on_build_plate_only`: support chỉ mọc từ bàn;
  - `support_remove_small_overhang`, mặc định bật;
  - `support_type = normal(manual) / tree(manual)`: "chỉ sinh support ở vùng enforcer".
  - Wiki Bambu có trang "Support Painting" (tô enforcer/blocker) nhưng chặn truy cập tự động. Nội dung chi tiết: `TODO` đọc bằng tay.
- **Preview theo lớp:** G-code của Bambu Studio đánh dấu loại đường in bằng chú thích `; FEATURE: <type>`, có loại `Support`
  [nguồn gốc, `GCodeProcessor.cpp`]. Nhờ đó máy đọc được "support nằm ở đâu, lớp nào".
- **In một phần (partial print):** công cụ Cut của PrusaSlicer cắt model ngay trong slicer, thêm chốt nối (plug, dowel,
  snap-fit) [nguồn gốc, Prusa KB]. Cộng đồng thường cắt riêng vùng lắp (hốc servo, lỗ trục) để in thử vài phút.
  Bambu Studio có công cụ Cut tương tự (`TODO` đọc wiki).
- **Mặt cắt trong CAD:** FreeCAD 1.1 có `Std_ToggleClipPlane` và BIM `SectionPlane` [máy: `Mod/BIM/ArchSectionPlane.py`].
  Wiki FreeCAD chặn bot nên chưa trích. Onshape/Fusion có Section View. Mặt cắt chỉ để người duyệt xem, không tự động.
- **Checklist DFM:** Prusa, Hubs (đã trích ở tài liệu cũ). Không tìm được checklist "design review" chuẩn nào từ dự án robot mở.
  Phần lớn dự án chỉ ghi thông số in tối thiểu + mẫu đo.

### 3.2 STLab đang làm gì
Mức tự động của STLab đã **vượt** những gì các repo robot mở công bố:
- `check.py`: va chạm, khe, `mesh-pair`;
- `printability.py`: nhô ra < 43°, cầu ≤ 5 mm, mái lỗ kín ≤ 8 mm, brim;
- `slice.py`: cắt thật bằng profile A1;
- test STL sau bài học Worm.

Support: chính sách "không để slicer sinh". Support tự vẽ (`Support_*`, khe Z 0,2 mm) chỉ ở bàn P4 và Worm. **Chính support
tự vẽ này đã lấp lỗ trục**, và slicer không biết đó là support.

### 3.3 Khoảng trống
- **Chưa kiểm "vùng chức năng" ở mức G-code:** chưa có danh sách lỗ/khe chức năng (`keep_clear`: trục, rãnh trượt, hốc ổ bi)
  để so với đường in `Support` theo từng lớp. Support tự vẽ là **mesh của chi tiết**, nên kiểm kiểu này phải chạy ở tầng STL
  (đã có test) hoặc trên mặt cắt từng lớp.
- **Chưa có ảnh mặt cắt** trong bộ ảnh duyệt (contact sheet). Ví dụ: cắt qua tâm lỗ trục Worm + hộp số, thấy khe 0,32 mm.
  Tuan duyệt bằng ảnh nên đây là dạng hợp nhất.
- **Chưa có "bàn in thử vùng lắp":** cắt riêng moay-ơ Worm + một đoạn vỏ, in khoảng 10 phút, thử với hộp số thật trước khi in cả xi-lanh.

## 4. Dạy CAD cho học sinh

### 4.1 Cộng đồng làm gì
| Công cụ | Điều kiện (nguồn gốc) | Hợp cấp | Ghi chú cho STLab |
|---|---|---|---|
| **Tinkercad** (Autodesk) | Miễn phí. Lớp học: giáo viên tạo **Class Seat**, học sinh đăng nhập bằng mã, **không cần email**. Dưới 13 tuổi hiện là "Child account". Có chứng nhận kidSAFE (COPPA). Autodesk không thu dữ liệu cá nhân khi học sinh vào lớp | Cấp 1 → đầu cấp 2 | Khối ghép, không có ràng buộc tham số. Hợp làm "thiết kế đầu tiên → in". Giáo án miễn phí chính thức: `TODO` (trang Teachers chưa đọc) |
| **Onshape Education** | Miễn phí cho học sinh và giáo viên (gồm homeschool, huấn luyện viên đội thi), **chỉ phi thương mại**. Dưới 13 tuổi được dùng nếu người lớn đủ điều kiện tạo/cho phép tài khoản (FAQ mới; trang help cũ ghi ≥ 13, mâu thuẫn). Có Classes & Assignments, thống kê, tài nguyên FRC/FTC | Cấp 2–3 | Tham số, sketch ràng buộc, chạy trên trình duyệt (máy yếu chạy được). Học phí của STLab có tính là "thương mại" không: `TODO` hỏi Onshape |
| **Fusion (Education)** | Phải đang học/làm ở **cơ sở giáo dục được công nhận** (THCS, THPT, đại học, homeschool), xác minh qua SheerID, gia hạn hằng năm, chỉ dùng cho học tập/nghiên cứu. Tuổi tối thiểu: trang chính thức chỉ ghi "minimum age"; số 13 là từ forum (thứ cấp) | Cấp 3 | Trung tâm tư nhân có thể **không đủ điều kiện**, học sinh phải tự đăng ký qua trường. `TODO` |
| **FreeCAD** (34 746★, LGPL-2.1, push 2026-10-24) | Không ràng buộc | Cấp 3 / CLB nâng cao | Cùng công cụ với pipeline STLab. Khó cho người mới. Tài liệu dạy chính thức cho trường học: `TODO` |
| Prusa Academy | Khóa học trả phí theo license, giao được license cho học viên (CSV) | Giáo viên | Không phải giáo trình CAD |

**Lộ trình theo tuổi** [nguồn gốc, NGSS ETS1]:
- K-2 → 3-5 → THCS → THPT.
- Ví dụ mức 3-5 (lớp 3–5):
  - ETS1-1: nêu bài toán thiết kế đơn giản có **tiêu chí và ràng buộc** (vật liệu, thời gian, chi phí);
  - ETS1-2: đưa ra **nhiều phương án** rồi so với tiêu chí;
  - ETS1-3: **thử công bằng**, kiểm soát biến, xét điểm hỏng để cải tiến mẫu.
- Khung này khớp với vòng in-thử-sửa của STLab và không ràng buộc phần mềm.

**Việt Nam:** Chương trình GDPT 2018 môn Công nghệ 10 (Thiết kế và Công nghệ) có mạch **vẽ kĩ thuật**, gồm cả vẽ kĩ thuật
có trợ giúp của máy tính (thứ cấp: bài báo trên vjol.info.vn). Yêu cầu cần đạt nguyên văn (Thông tư 32/2018/TT-BGDĐT): `TODO`.

**Dạng bài cộng đồng hay dùng** (tổng hợp, không có một nguồn chuẩn duy nhất):
- **Reverse engineering:** đo vật thật bằng thước kẹp → dựng CAD → in → so.
- **Thiết kế theo ràng buộc:** cho trước linh kiện + khe + giới hạn bàn in.
- **In-thử-sửa** với mẫu đo nhỏ.

### 4.2 STLab đang làm gì
Pipeline CAD là của Tuan và Claude, chưa có giáo trình cho học sinh. `docs/design-first-research.md` có bước duyệt bằng ảnh.
`GarethManning/education-agent-skills` (CC BY-SA 4.0) đã có trong COMMUNITY.

### 4.3 Khoảng trống
- Chưa có khung bài theo cấp.
- Chưa quyết công cụ cho từng cấp.
- Chưa rõ STLab (trung tâm có thu phí) có thuộc diện "giáo dục phi thương mại" của Onshape/Autodesk không.
- Gợi ý khung (chờ Tuan quyết):
  - **Cấp 1:** Tinkercad, bài "móc khóa tên → hộp có nắp lắp khít" (học khe 0,2/0,3 mm bằng tay).
  - **Cấp 2:** Tinkercad → Onshape, bài reverse engineering "giá servo 9g" (đo servo thật, in mẫu đo, sửa).
  - **Cấp 3:** Onshape/FreeCAD, bài nhỏ trong pushrod-arm, ví dụ thiết kế lại `Washer_shaft` hoặc moay-ơ trục vít có
    tiêu chí (khe, thời gian in < 15 phút).
- Kết quả đo của học sinh có thể đổ vào `measurements.yaml`, đã đề xuất ở tài liệu cũ.

## Đề xuất xếp theo lợi/công

**Chỉ là đề xuất, chờ Tuan quyết.** Công: 1 buổi ≈ 3–4 giờ làm cùng Claude (ước lượng). Không tính thời gian in.

| # | Việc | Lợi | Công | Đánh đổi |
|---|---|---|---|---|
| 1 | **Thử tự hãm + ma sát:** đo góc trượt PETG/PETG (khô, có mỡ) → k. Thử "tắt điện + treo tải" trên xi-lanh in thật, đo độ trôi sau 10 phút | biết pushrod-arm có giữ tay được không trước khi làm tiếp | 0,5 buổi + in 1 xi-lanh | cần tải và cân; kết quả có thể buộc phải đổi thiết kế trục vít |
| 2 | **Bàn in thử vùng lắp** (cắt riêng moay-ơ Worm + đoạn vỏ, cổ trục) qua `print.yaml` | thử khớp trục D với hộp số thật trong khoảng 10 phút thay vì in cả bàn | 0,5 buổi | thêm 1 loại "bàn thử"; phải giữ đồng bộ với model |
| 3 | **Ảnh mặt cắt** qua lỗ/khe chức năng trong contact sheet duyệt (`Shape.slice`/`common` với hộp, render) | Tuan thấy khe bằng mắt, đúng cách duyệt bằng ảnh | 0,5 buổi | thêm ảnh; phải khai các mặt cắt cần xem |
| 4 | Khai `keep_clear:` (lỗ trục, rãnh trượt) trong `print.yaml`, test: không mesh support / không đường `; FEATURE: Support` nào lọt vào | chặn đúng loại lỗi Worm cho mọi dự án | 1 buổi | thêm khai báo; đọc G-code tốn thời gian chạy |
| 5 | Chọn và ghi **loại mỡ** vào ASSEMBLY (ứng viên: mỡ có ghi "plastic compatible" như EM-30L), cùng cảnh báo mỡ có thể làm mất tự hãm | tránh hỏng nhựa, giảm nhiệt và mòn | 0,25 buổi | phải mua mỡ; mâu thuẫn với #1 nên làm sau #1 |
| 6 | Phương án dự phòng giữ tay: λ < 4° (trục vít to hơn) / chốt cơ khí / động cơ có hộp số trục vít mua sẵn | chắc chắn giữ tay khi mất điện | 1–2 buổi | xi-lanh to hơn, hiệu suất thấp hơn, hoặc thêm chi phí. **Chỉ làm nếu #1 trượt** |
| 7 | Ổ bi 623/624 hoặc bạc cho chốt khuỷu/vai và mâm xoay, theo mẫu Moveo | giảm rơ và mòn chốt nhựa | 1 buổi | thêm linh kiện mua; phải đo ổ bi thật (`components.yaml` mới có 608ZZ) |
| 8 | Khung bài CAD 3 cấp (Tinkercad → Onshape → FreeCAD) + bài reverse engineering "giá servo 9g" | dạy và sinh dữ liệu khe cùng lúc | 1–2 buổi soạn | phải xác nhận license EDU cho trung tâm trước |
| 9 | Quy ước đi dây qua khớp (rãnh/kẹp dây, bán kính uốn) | lắp gọn, dây không kẹt khi quay | 0,5–1 buổi | sửa nhiều chi tiết; nên gộp vào lần vẽ lại sau |

## Điểm chưa xác nhận (TODO)
- Hệ số ma sát PETG/PETG, khô và có mỡ. **Quyết định cho #1, #5, #6.**
- Ngưỡng tự hãm < 4° chỉ có từ bản chép lại tài liệu KHK (thứ cấp). Trang KHK chính thức không ghi số.
- Loại mỡ Bambu dùng cho hộp số 030; mỡ nào an toàn cho PETG theo bảng tương thích của hãng (Super Lube có "Compatibility Charts" chưa đọc).
- Chi tiết in chính hãng CyberBrick có lỗ lắp trục ra 030 (bánh xe Mini tank, …) và kích thước lỗ của nó.
- Servo, license của EEZYbotARM; tỉ số từng khớp của Thor và Faze4; license thật của Faze4 (MIT hay CERN-OHL-S-2.0).
- SO-ARM100 / PAROL6: tay có rơi khi mất điện không, phanh, cách đi dây.
- Nội dung trang Bambu wiki "Support Painting" và công cụ Cut của Bambu Studio (wiki chặn truy cập tự động).
- Điều kiện Onshape/Autodesk EDU cho trung tâm tư nhân có thu phí; tuổi tối thiểu chính thức của Fusion.
- Yêu cầu cần đạt về CAD trong Thông tư 32/2018/TT-BGDĐT (Công nghệ 8, 10).
- Giáo án Tinkercad chính thức và license của giáo án.

## Xem lại khi thương mại
STLab hiện phi thương mại nên các nguồn dưới đây vẫn dùng để tham khảo. Rà lại khi chuyển sang thương mại.

| Nguồn | License / ràng buộc |
|---|---|
| Thor (AngelLM) | CC-BY-SA-4.0: ghi công, phái sinh cùng license |
| PAROL6 | GPL-3.0: phái sinh phải mở cùng license |
| Faze4 | CERN-OHL-S-2.0 (strongly reciprocal) theo GitHub; README ghi MIT, `TODO` |
| Howard 2023 (paper) | CC BY-SA 4.0 |
| freecad.gears | GPL-3.0 |
| Arctos | CAD **trả phí**, license không ghi |
| EEZYbotARM | License thiết kế `TODO` (MyMiniFactory yêu cầu ghi công) |
| Onshape Education | Chỉ phi thương mại; dữ liệu độc quyền/thương mại cần gói trả phí |
| Fusion Education | Chỉ học tập/nghiên cứu; phải là cơ sở giáo dục được công nhận |
| Tinkercad | Điều khoản dùng cho dạy học có thu phí: `TODO` |

## Nguồn
Cánh tay robot:
- SO-ARM100 README: https://github.com/TheRobotStudio/SO-ARM100
- low_cost_robot: https://github.com/AlexanderKoch-Koch/low_cost_robot
- PAROL6 repo: https://github.com/Source-Robotics/PAROL6-Desktop-robot-arm · thông số: https://docs.source-robotics.com/PAROL-docs/page2_2/
- Thor: https://github.com/AngelLM/Thor · Hackaday (tác giả): https://hackaday.io/project/12989
- BCN3D Moveo: https://github.com/BCN3D/BCN3D-Moveo · BOM: https://raw.githubusercontent.com/BCN3D/BCN3D-Moveo/master/BOM/BCN3D%20Moveo%20BOM.pdf
- Faze4: https://github.com/Source-Robotics/Faze4-Robotic-arm
- Arctos: https://arctosrobotics.com/ · https://github.com/Arctos-Robotics
- easyEEZYbotARM: https://github.com/meisben/easyEEZYbotARM · MyMiniFactory (thứ cấp, trích qua tìm kiếm): https://www.myminifactory.com/object/3d-print-eezybotarm-mk2-46620
- Howard, I. S. (2023), Design and Prototyping of a 3DOF Worm-drive Robot Arm, ASTESJ 8(5), 77–93, DOI 10.25046/aj080509: https://www.astesj.com/v08/i05/p09/
- Số sao, license, ngày push: GitHub REST API `api.github.com/repos/<owner>/<repo>`, tra 2026-10-25.

Truyền động, nối trục, bôi trơn:
- KHK Worm Gears: https://khkgears.net/new/worm_gear.html
- KHK Design of Plastic Gears: https://khkgears.net/new/gear_knowledge/gear_technical_reference/design-of-plastic-gears.html
- KHK Q&A (trích qua tìm kiếm): https://khkgears.net/new/gear_knowledge/q_and_a_about_gears.html
- KHK catalog (thứ cấp, ngưỡng < 4°): https://pdf.directindustry.com/pdf/khk/khk-worm-gears-catalogue/18644-84670.html
- MathWorks Simscape Worm Gear (công thức hiệu suất, tự hãm): https://www.mathworks.com/help/sdl/ref/wormgear.html
- nophead, Polyholes: https://hydraraptor.blogspot.com/2011/02/polyholes.html
- Prusa blog, khe 0,15 mm cho đai ốc/nam châm: https://blog.prusa3d.com/practical-uses-of-color-change-in-prusaslicer_59563/ · Prusa KB, Insert pause: https://help.prusa3d.com/article/insert-pause-or-custom-g-code-at-layer_120490
- Tribology in Industry 2025, vỏ PETG ép ổ bi: https://www.tribology.rs/journals/2025/2025-2/2025-2-15.html
- igus, filament tribo / phòng thử: https://www.igus.eu/3d-printing/material/test-laboratory · https://www.igus.eu/linear-technology/test-laboratory/tribo-filament-and-plastic-rod-products-in-comparison
- MOLYKOTE EM-30L: https://www.dupont.com/products/molykote-em-30l-grease.html
- Super Lube 21030 TDS: https://www.super-lube.com/wp-content/uploads/2025/05/Technical_Data_Sheet_Multi_Purpose_Grease.pdf
- [máy] Hướng dẫn lắp hộp số 030 của Bambu: `community/cyberbrick-official/extracted/Cyber_Brick_Hardware_Kit_Application_Instruction/2-Part Application/030 Reduction Motor/single axis/Assembly_Guide_of_Single_Axis_030_Reduction_Motor.pdf`
- [máy] Tham số trục vít: `maker/pushrod-arm/freecad/scripts/history/2026-10-22_build_pushrods_v3.py`, `2026-10-24_cylinder_030_gearbox.py`, `2026-10-25_worm_socket_chamfer.py`

Kiểm trước khi in:
- Bambu Studio `PrintConfig.cpp` (`max_bridge_length`, `support_type`, `support_on_build_plate_only`, `bridge_no_support`): https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp
- Bambu Studio `GCodeProcessor.cpp` (`; FEATURE:`): https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/GCode/GCodeProcessor.cpp
- Bambu wiki Support Painting (chặn bot): https://wiki.bambulab.com/en/software/bambu-studio/support-painting
- Prusa KB Cut tool: https://help.prusa3d.com/article/cut-tool_1779
- [máy] FreeCAD 1.1: `C:/Program Files/FreeCAD 1.1/Mod/BIM/ArchSectionPlane.py`

Dạy CAD:
- Onshape Education: https://www.onshape.com/en/education/ · gói: https://www.onshape.com/en/education/plans · Terms: https://www.onshape.com/en/legal/terms-of-use
- Autodesk Education: https://www.autodesk.com/education/edu-software/overview · forum tuổi 13 (thứ cấp): https://forums.autodesk.com/t5/fusion-educators-read-only/minimum-age-of-13-years-old-to-use-fusion/td-p/12697645
- Tinkercad Classrooms: https://www.tinkercad.com/help/classrooms/official-guide-to-tinkercad-classrooms · https://www.tinkercad.com/help/classrooms/add-students-to-a-class · Children's Privacy: https://www.autodesk.com/company/legal-notices-trademarks/privacy-statement/childrens-privacy-statement
- FreeCAD: https://github.com/FreeCAD/FreeCAD
- Prusa Academy license: https://help.prusa3d.com/article/purchasing-and-managing-licenses-for-prusa-academy-courses_665149
- NGSS 3-5 Engineering Design: https://www.nextgenscience.org/topic-arrangement/3-5engineering-design
- Công nghệ 10, mạch vẽ kĩ thuật (thứ cấp, tạp chí Thiết bị Giáo dục; `TODO` xác nhận đúng bài trong 3 kết quả): https://vjol.info.vn/tctbgd/article/download/96578/81589 · https://vjol.info.vn/tctbgd/article/download/86642/73691 · https://vjol.info.vn/tctbgd/article/download/98390/83117
