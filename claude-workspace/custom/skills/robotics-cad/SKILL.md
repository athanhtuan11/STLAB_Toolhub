---
name: robotics-cad
description: Thiet ke co khi robot trong FreeCAD cho STLab - chon linh kien tu danh muc (servo, stepper, ESP32, Raspberry Pi, cam bien, o bi, CyberBrick), chen model STEP tu thu vien da ghim, tao ga/khung, chuan bi xuat URDF bang RobotCAD. Dung khi lam robot, ga dong co, khung robot, hop so trong FreeCAD.
---

# Robotics CAD (FreeCAD)

> Tự viết vì chưa có skill cộng đồng nào gắn với thư viện linh kiện và quy trình in A1 của STLab.
> Viết script FreeCAD thì theo skill `freecad-scripts` (cộng đồng).

## Nguồn dữ liệu
- Danh mục linh kiện: `D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/library/components.yaml`
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
- Sửa chi tiết bằng boolean (cắt hốc, thêm gân): dùng `tools/robotics-cad/scripts/safe_edit.py`
  (`guard` → `backup` → `safe_cut`/`safe_fuse` → `apply` → `save`), không gọi `shape.cut()` trần – STEP linh kiện
  lỗi BOP làm cut "thành công" mà bỏ 0 mm³. Chi tiết: `tools/robotics-cad/CLAUDE.md` mục Quy ước.
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
   **Nới khe / khoét rãnh → kiểm lại thành bên ngoài** (Tuan 2026-10-25: Housing pushrod-arm "mất 1 bên thành phía
   ngoài, bật support hay không đều bị"): nới rãnh thanh răng lên ±6,3 mm trong khi mặt ngoài vỏ ở 6,5 mm → vách
   **0,2 mm** < 1 đường đùn → slicer bỏ hẳn, in ra hở thành (check/printability đều không báo). Mỗi lần cắt/nới hốc,
   đo vách còn lại tới mặt ngoài ≥ **2 đường in** (≈ 0,9 mm với profile classic 0,42 + 0,45). Đắp ra ngoài thì chạy
   `kinematics_test.py` – Housing chỉ đắp được 0,7 mm vì Boom001 vào tới cách 1,0 mm khi xi-lanh duỗi hết. Cách tìm:
   cắt lưới **theo hướng in** (lấy từ 3MF) từng lớp 0,2 mm, mặt cắt có 2·diện tích/chu vi < 0,45 mm = vách mỏng.
5. Báo lại: kích thước chính (mm), khối lượng ước tính (vật liệu PLA/PETG), các giả định.

## Tra kho thông số lắp ghép – BẮT BUỘC (Tuan 2026-10-30)
Trước khi chọn bất kỳ đường kính lỗ/chốt/khe nào: `tools/model-study/.venv/Scripts/python.exe
tools/model-study/fit-library/fit_lib.py recommend <interface>` (vd `rotate-joint-5mm`, `screw-M2.5`). `basis: verified`
= STLab in thử thật → dùng; `community` = số lấy từ **sản phẩm hoàn thiện đã chạy** (Tuan 2026-10-31) → dùng làm mặc
định, ghi nguồn trong spec. Xem `print` của mục: tác giả in **PLA, không bù lỗ** → số đã gồm co lỗ của PLA; STLab in PETG
thì chỉ mối **ép** (moay-ơ, nam châm) cần in 1 chi tiết trước khi in cả bộ. Không có trong kho → `TODO`, không đoán.
Số mới đo/in thử → thêm vào kho (skill `model-study`).
Lưu ý: khe 0,40 (tipflow) là khớp **1 lỗ**; chốt xuyên **nhiều** chi tiết STLab đã in thật 0,4 → kẹt, dùng 0,6 (mục dưới).

## Mẫu thiết kế đã chạy – học từ model cộng đồng (CyberBrick)
Chi tiết + số: `docs/research-notes/` (`tipflow-robotic-arm-fits.md`, `mec-1-forklift-fits.md`). Ưu tiên các mẫu này
thay vì tự nghĩ cách mới:
- **Bánh vào trục ra hộp số 030:** lỗ **double-D** ép chặt, không vít (MEC-1: tròn Ø5,53, phẳng cách 3,80; trục hãng
  Ø5,3 / 3,6). Vỏ đỡ trục ra Ø5,7 (2 tác giả cùng số). Tháo bánh dễ hỏng hộp số → ghi vào ASSEMBLY.md.
- **Hộp số tự in:** chỉ có motor + bộ bánh răng rời (vd 48:1 kit Ultimate) → in vỏ + nắp, M2.5 xuyên Ø2,7 + bậc đầu Ø5,0.
  Đã có vỏ hãng (LA024/LA013) thì không in.
- **Chốt in nằm ngang:** Ø4,7 vát 2 mặt còn 4,07 (in nằm, bền theo thớ), mũ Ø6, vào lỗ Ø5,0 (khe 0,3) – khớp nâng/xích.
- **Xích lắp bấm:** lưỡi lỗ Ø5,0 dày 3,4 trên chốt liền Ø4,4 dài 3,8, bóp nhẹ để lắp; in 100 % infill.
- **Vỏ trên không vít:** 4 trụ Ø7,5 (đầu Ø4,0 / vai Ø6,5) đẩy vào lỗ vỏ dưới rồi trượt ra sau để khóa + nam châm 4×2
  (ổ Ø4,1 sâu 2,1–2,2, nhỏ keo, đúng cực) → mở vỏ nhanh, hợp học sinh.
- **Vít:** M2.5×6 BHCS (lục giác 1,5) cho mọi mối ghép; tự ren Ø2,2–2,4, xuyên Ø2,7–2,8. Servo 9g: 2 lỗ cách 27,8, Ø1,8–2,0.
- **Support:** tác giả chỉ bật cho 1–2 khung lớn; còn lại thiết kế để in không support (đúng luật Tuan: không vẽ support vào STL).

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
- **Ảnh (phong cách Tuan duyệt 2026-10-25, `docs/assembly-instructions-style-research.md`):** 1 ảnh "thao tác" / bước –
  chi tiết **mới vàng STLab #E8B33A**, đã lắp **xám nhạt đặc #D3DDD8**, mọi chi tiết **viền #16231D** (FreeCAD `Flat Lines`);
  chỉ hiện **cụm đang lắp**; **tách chi tiết mới theo hướng lắp + đường nét đứt** tới chỗ gắn; chụp 2400×1800 → tự cắt
  khung → 1200×900; ảnh bìa màu thật. KHÔNG làm mờ (trong suốt) cả máy, KHÔNG dùng màu chọn xanh của FreeCAD.
  Bước lặp (vd. xi-lanh thứ 2) gộp 1 bước "làm giống bước …". Mẫu: `pushrod-arm/freecad/scripts/render_assembly_steps.py`
  (bảng bước: bối cảnh, chi tiết mới + vector tách, cụm di chuyển cùng, hướng nhìn) + `crop_assembly_images.py`.
  Render qua `gui_run.py`; **tự kiểm ảnh trắng và chụp lại**; `steps.json` báo chi tiết chưa thuộc bước nào → phải rỗng.
- Phần kỹ thuật (tự hãm, tỉ số, TODO) để mục **Ghi chú cho thầy/cô** cuối file. Lưu ý BẮT BUỘC (pin, servo không bảo vệ
  kẹt, mỏ hàn…) – xem `tools/robotics-cad/CLAUDE.md`.
- **Sai kích thước linh kiện → sửa chi tiết gốc** (vd. trụ đế đúng chiều cao bộ thu), không thêm ống kê/đệm tạm. Chỉ kê tạm khi
  chi tiết gốc đã in và Tuan đồng ý; khi đó ghi ngay việc "làm lại chuẩn" vào README mục nâng cấp (pushrod-arm
  `Receiver_riser` 2026-10-25).
- Thứ tự lắp phải xét **hành vi cơ cấu** (tự hãm, chỉ vào được 1 hướng) – quét đường lắp từng cụm trên model, không chỉ tiếp xúc.

## Điện (nhắc khi ghép linh kiện)
- ESP32/Pico là logic 3.3 V: HC-SR04 Echo (5 V) cần chia áp; servo/động cơ cấp nguồn riêng, chung GND.

## URDF (RobotCAD)
- Mỗi link một Part/Body; khớp quay đặt trục trùng tâm trục động cơ. Gán vật liệu để tính khối lượng/quán tính.
- Không dùng tính năng gửi dự án ra ngoài (robotcad.ru) hoặc LLM provider ngoài.
