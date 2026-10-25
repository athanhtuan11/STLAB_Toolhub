---
name: robotics-cad
description: Thiet ke co khi robot trong FreeCAD cho STLab - chon linh kien tu danh muc (servo, stepper, ESP32, Raspberry Pi, cam bien, o bi, CyberBrick), chen model STEP tu thu vien da ghim, tao ga/khung, chuan bi xuat URDF bang RobotCAD. Dung khi lam robot, ga dong co, khung robot, hop so trong FreeCAD.
---

# Robotics CAD (FreeCAD)

> Tự viết vì chưa có skill cộng đồng nào gắn với thư viện linh kiện và quy trình in A1 của STLab.
> Viết script FreeCAD thì theo skill `freecad-scripts` (cộng đồng).

## Nguồn dữ liệu
- Danh mục linh kiện: `D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/robotics-cad/library/components.yaml`
  (nguồn duy nhất – không có bản sao). Đọc **trước** khi dùng thông số linh kiện; không có trong danh mục
  → nói rõ là chưa có nguồn, ghi `TODO`.
- Linh kiện có `thu_vien: cyberbrick` (CyberBrick của Bambu Lab): model nằm ở
  `D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/community/cyberbrick-official/models/<model>` (STEP + STL chính thức,
  datasheet trong `../pdf/`). Bộ thu XA004 cần 7,4–12,6 V; hộp pin 3 × AAA (4,5 V) chỉ đủ cho bộ phát.
- Linh kiện có `thu_vien: boards` / `espressif`: đường dẫn tính từ `library_roots` trong `components.yaml`
  (board Arduino + module ESP32 chính hãng; Pi 5, Pi Zero 2 W, ESP32-DevKitC V4, ESP32-S3-DevKitC-1, STM32 Nucleo-64,
  Blue Pill, D1 mini, ESP32-CAM **dựng từ bản vẽ**).
  Mục có `dung_tu_ban_ve: true`: lỗ bắt + vị trí cổng tin được; chiều cao linh kiện là ước → chừa khe, nhắc đo hàng thật.
- Model STEP nằm trong thư viện đã ghim; **không tự vẽ lại linh kiện chuẩn**. Chèn qua MCP `freecad`
  (`execute_code`, code chạy bên trong FreeCAD nên đọc được ổ đĩa):
  ```python
  import FreeCAD, Part, os
  lib = FreeCAD.ParamGet("User parameter:Plugins/parts_library").GetString("destination")
  doc = FreeCAD.ActiveDocument or FreeCAD.newDocument("robot")
  o = doc.addObject("Part::Feature", "SG90")
  o.Shape = Part.read(os.path.join(lib, "Electrical Parts/Servos/SG-90/Servo-sg90.step"))
  doc.recompute()
  ```
- `bbox_mm` là hộp bao **gồm cả chân/cổng nhô ra**; khoảng cách lỗ bắt lấy từ `thong_so`, không suy từ bbox.

## Chống treo FreeCAD (bắt buộc)
`execute_code` chạy trên **luồng giao diện**: lệnh nặng làm FreeCAD "Not Responding" → Windows đóng, mất bài
(5 lần AppHang 21–22/10/2026). Chọn công cụ theo khối lượng việc:

| Việc | Công cụ |
|---|---|
| Tạo/sửa vài đối tượng, đọc thuộc tính, recompute tài liệu nhỏ | `execute_code` |
| Đọc STEP lớn (> 2 MB hoặc > 100 solid: GIGA, UNO R4, Nano ESP32, module ESP32, Pi), boolean/fillet nhiều cạnh, loft/sweep/ren, đo hàng loạt, FEM | `execute_code_headless` (tiến trình `freecadcmd` riêng; crash cũng không mất tài liệu đang mở) |
| Sửa chi tiết có boolean trong tài liệu đang mở (vd. đổi motor N20 → cắt lại vỏ/gá) | headless: mở bản `.FCStd` đã lưu, cắt, `saveAs` → `reload_document` |

- **Claude web/app điều khiển máy từ xa** (lỗi `Device 'typc' did not respond within 60s`): mỗi lệnh chỉ được
  chờ 60 s → `execute_code_headless` cũng bị cắt nếu lâu. Mọi việc có thể > 30 s chạy bằng job nền:
  ```python
  # execute_code (vài ms): giao việc
  import runpy; J = runpy.run_path(r"D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/studio/scripts/fc_job.py")
  print(J["start"](r"D:/.../viec.py"))      # -> thư mục job
  # execute_code mỗi ~10–20 s: hỏi tiến độ
  print(J["status"](r"<thư mục job>"))      # state running/done/failed, elapsed_s, log_tail, error
  ```
  `viec.py` tự import, tự mở/lưu file; có biến `JOB_DIR` để ghi kết quả. Xong → `reload_document` / chèn `.brep`.
  Gặp lỗi 60 s: KHÔNG gửi lại lệnh ngay – gọi `get_rpc_status` xem FreeCAD còn bận lệnh nào (`operation`).
- **Không dùng `execute_code_async` để tránh đơ**: lệnh hình học C++ của FreeCAD giữ GIL suốt lúc tính
  (đo 22/10: boolean 10,8 s → luồng Python khác đứng 10,9 s). Luồng nền vẫn làm GUI đứng, và `get_rpc_status`
  cũng phải chờ tới khi lệnh xong. Chỉ tiến trình riêng (headless) mới tách được.

- Headless: script tự `import`, tự mở/lưu (`doc.saveAs(...)` hoặc `shape.exportBrep(...)`); xong thì
  `reload_document` hoặc chèn file `.brep` (nhẹ) bằng `execute_code`.
- Model linh kiện nhiều solid: trong headless, gộp thành **1 shape** rồi `exportBrep` → chèn bản gộp vào GUI
  (giảm hàng trăm đối tượng hiển thị). Giữ STEP gốc để tra chi tiết.
- Bắt buộc phải chạy trên GUI và lâu (vd. xuất STEP lắp ráp lớn): truyền `timeout=` (tối đa 1800 s), báo Tuan trước.
- Chi tiết sinh bằng mô phỏng cắt (bánh vít "hob", ren…) toàn mặt B-spline: boolean chậm ~7 lần
  (đo 22/10: bánh vít z16 2.002 mặt → `common` 12,7 s; bản 354 mặt → 1,7 s). Giữ bản nặng chỉ để xuất STL;
  lắp ráp, kiểm va chạm, mô phỏng dùng bản nhẹ.
- Sửa chi tiết bằng boolean (cắt hốc, thêm gân): dùng `maker/robotics-cad/scripts/safe_edit.py`
  (`guard` → `backup` → `safe_cut`/`safe_fuse` → `apply` → `save`), không gọi `shape.cut()` trần – STEP linh kiện
  lỗi BOP làm cut "thành công" mà bỏ 0 mm³. Chi tiết: `maker/robotics-cad/CLAUDE.md` mục Quy ước.
- Trước lệnh dài: **lưu tài liệu** (`doc.save()`). Báo `GUI_DISPATCH_STUCK` → gọi `get_rpc_status`, không gửi thêm lệnh GUI.

## Khi thiết kế gá/khung
1. Hỏi (nếu chưa rõ): linh kiện nào, gắn vào đâu, vật liệu in, có cần tháo lắp không.
2. Lấy kích thước từ danh mục; chỗ nào nguồn mâu thuẫn (vd. SG90) → thiết kế có rãnh/khe chỉnh,
   và nhắc đo hàng thật.
3. Tham số hóa: Spreadsheet `params` (độ dày thành, dung sai, đường kính lỗ).
4. Kiểm tra: in được không cần support không? thành ≥ 2 đường in? lỗ M3 chừa dung sai (giá trị trong
   chưa có số đo in thử → TODO)?
   **Support (Tuan 2026-10-25): KHÔNG vẽ/dựng support vào model hay STL** (không `Support_*`, `support: true` chỉ là
   ghi chú) – Tuan tự tô support trong Bambu Studio. Support tự vẽ từng lấp lỗ trục Worm và rãnh thanh răng Housing của
   pushrod-arm. Việc của mình: báo rõ chi tiết/vùng nào CẦN support (printability WARN: mm², z) và **lỗ/khe/rãnh chức
   năng nào phải giữ trống** (để Tuan không tô support vào đó). Ưu tiên vẽ để khỏi cần support (vát 45°, giọt nước).
5. Báo lại: kích thước chính (mm), khối lượng ước tính (vật liệu PLA/PETG), các giả định.

## Chốt / trục khớp quay (cập nhật 2026-10-25 – Tuan: chốt pushrod-arm "quá khít", "rỗng sẽ yếu lực")
**Ca thật pushrod-arm:** chốt xuyên nhiều chi tiết (`Pin_S`: Turret_one_piece ↔ Spacer_S ↔ Boom001) in Ø5,0 trong lỗ Ø5,4
= khe **0,2 mm/bên** → in ra **không nhét vào được**; ruột chốt **rỗng vì in infill 40 %** (model đặc); `Pin_jaw2` in
**đứng**; lỗ vít M2.5 sâu đúng bằng phần vít ăn vào (vít chạm đáy). Đã sửa (`freecad/scripts/history/
2026-10-25_pins_clearance_solid.py <D>`): thân Ø4,8 (0,3 mm/bên), vát đầu 0,4, mặt phẳng đáy, lỗ vít sâu 5,5, bàn in
P8 đặc 100 %, bộ chốt thử `print/print-pin-gauge.yaml`, test `T7Pins`.

**Quy trình chốt / trục cho mọi dự án:**
- Chốt xuyên **nhiều** chi tiết: khe tính với **MỌI** lỗ dọc chốt (lỗ nhỏ nhất quyết định), không chỉ 1 lỗ.
- Chi tiết có lỗ đã in, chỉ sai khe → **sửa (thu nhỏ) chốt, in lại chốt**, không in lại chi tiết lớn.
- **In bộ chốt thử trước** (vài cỡ cách 0,1 mm, vạch đánh dấu trên mũ, ~10 phút) cắm vào lỗ thật → chọn cỡ → chạy script với cỡ đó.
- Lỗ vít ở đầu chốt: Ø mồi theo vít (M2.5 tự ren trong PETG: Ø2,2), **sâu = chiều dài vít − washer + 0,5–1 mm**; không khoan sâu hơn.
- Chi tiết nhỏ **chịu lực** (chốt, trục, then, vấu) → bàn in riêng **100 % infill**; ghi trong print.yaml, không để chung bàn 40 %.
- Script đổi chốt trong hệ riêng (Placement ≠ I, vd. chốt đi theo cụm kẹp): dựng hình trong hệ riêng rồi gán `Shape` +
  đặt lại `Placement`; **không dùng `transformShape` để đổi hệ** (FreeCAD chỉ gán Placement → bị áp 2 lần, lỗi thật 2026-10-25).
- `BoundBox` của mặt cong có thể rộng hơn thật (~0,4 mm) → kiểm vị trí bằng `isInside` / mặt cắt, không tin hộp bao.
1. **Ưu tiên trục kim loại cho khớp chịu lực:** bu lông/chốt thép (vd. M5 hoặc chốt Ø5 xuyên lỗ in Ø5,4–5,6) + đai ốc
   khóa nylon hoặc phe/vít đầu. Thép không gãy theo lớp, không mòn, không cần in lại khi hỏng. Cánh tay mở dùng ổ bi /
   bạc ở khớp (BCN3D Moveo: 608ZZ, 62x, bạc tự bôi trơn – `docs/cad-mechanisms-teaching-research.md` mục 1).
   Chỉ dùng chốt IN cho khớp nhẹ hoặc khi Tuan muốn toàn bộ in.
2. **Chốt in (nếu dùng):**
   - In **NẰM** (trục song song bàn) để lớp chạy dọc chốt: PETG Basic σ kéo XY 51 MPa, theo Z chỉ 35 MPa (TDS, −31 %) →
     chốt in đứng gãy ngang theo lớp. Thêm **mặt phẳng D ~0,5 mm** ở đáy để nằm vững, không cần support.
   - **Đặc 100 %** (infill 100 % hoặc đủ vòng tường); Ø ≥ 5 mm; không khoét lỗ dọc suốt thân (lỗ vít chỉ ở đầu, sâu tối thiểu).
   - Vát 0,3–0,5 mm hai đầu chốt và miệng lỗ (dễ luồn, bù elephant foot).
3. **Khe theo kiểu lắp** (ghi rõ trong script + test, không dùng một số chung):
   | Kiểu | Khe mỗi bên | Ví dụ |
   |---|---|---|
   | Ép / cố định | 0–0,1 mm | chốt hộp số Ø3,9 / Ø4,0 |
   | Trượt chặt (không quay) | 0,2 mm | — |
   | **Quay / trượt nhiều** | **≥ 0,3 mm** (Prusa KB: chi tiết chuyển động ≥ 0,3 mm – `TODO` nguồn không nói rõ mỗi bên hay tổng → lấy mỗi bên cho chắc) | chốt khớp tay, bánh răng, rãnh trượt |
   | Trục kim loại trong lỗ in | 0,2–0,3 mm | bu lông M5 trong lỗ Ø5,4–5,6 |
   Lỗ in nhỏ hơn bản vẽ (nophead polyholes); lỗ NGANG (trục song song bàn) còn bị dẹt đỉnh → dùng lỗ giọt nước / vát đỉnh.
   Số cuối cùng chốt bằng **mẫu thử** trên máy thật: chốt → bộ chốt thử (`make_pin_gauge.py` của pushrod-arm làm mẫu);
   lỗ/hốc khác → coupon 0,1–0,4 mm (`TODO` chưa có coupon chuẩn STLab).
4. **Kiểm bằng hình học, đưa vào test:** với mỗi chốt, đo đường kính thân + mọi lỗ đồng trục trên chi tiết lắp → khe ≥ ngưỡng
   theo kiểu lắp; báo chốt in đứng / chốt < 5 mm / thân bị khoét dọc (`WARN`).

## Hướng dẫn lắp cho học sinh (Tuan 2026-10-25: "học sinh lớp 6 lắp sẽ khó lắm. chi tiết từng bộ phận")
Mẫu: `maker/pushrod-arm/ASSEMBLY.md` (34 bước) + `freecad/scripts/render_assembly_steps.py` + `robotics-cad/scripts/assembly-pdf.py`.
- **Mỗi bước 1 việc**, gom theo cụm (Đế, Mâm, Tháp, …); lắp cụm con trên bàn rồi mới gắn lên máy.
- Mỗi bước: **Cụm** · **Cần lấy** (tên dễ hiểu + `Label` × SL + "bàn Px" / "mua") · 3 ảnh · các bước đánh số (câu ngắn) ·
  **Kiểm tra** (làm đúng mới sang bước sau) · **[Cần người lớn]** ở tiêu đề khi có mạch/động cơ/pin/đo tư thế.
- Ảnh: `c` = chỉ chi tiết cần lấy (chi tiết màu sáng tạm tô cam), `a` = toàn cảnh (đã lắp mờ, mới tô xanh), `b` = phóng to.
  Render qua `gui_run.py`; **tự kiểm ảnh trắng và chụp lại** (fitAll chạy trước khi kịp vẽ → ảnh trắng ngẫu nhiên).
  `steps.json` báo chi tiết chưa thuộc bước nào → phải rỗng.
- Phần kỹ thuật (tự hãm, tỉ số, TODO) để mục **Ghi chú cho thầy/cô** cuối file. Lưu ý BẮT BUỘC (pin, servo không bảo vệ
  kẹt, mỏ hàn…) – xem `maker/robotics-cad/CLAUDE.md`.
- **Sai kích thước linh kiện → sửa chi tiết gốc** (vd. trụ đế đúng chiều cao bộ thu), không thêm ống kê/đệm tạm. Chỉ kê tạm khi
  chi tiết gốc đã in và Tuan đồng ý; khi đó ghi ngay việc "làm lại chuẩn" vào README mục nâng cấp (pushrod-arm
  `Receiver_riser` 2026-10-25).
- Thứ tự lắp phải xét **hành vi cơ cấu** (tự hãm, chỉ vào được 1 hướng) – quét đường lắp từng cụm trên model, không chỉ tiếp xúc.

## Điện (nhắc khi ghép linh kiện)
- ESP32/Pico là logic 3.3 V: HC-SR04 Echo (5 V) cần chia áp; servo/động cơ cấp nguồn riêng, chung GND.

## URDF (RobotCAD)
- Mỗi link một Part/Body; khớp quay đặt trục trùng tâm trục động cơ. Gán vật liệu để tính khối lượng/quán tính.
- Không dùng tính năng gửi dự án ra ngoài (robotcad.ru) hoặc LLM provider ngoài.
