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
5. Báo lại: kích thước chính (mm), khối lượng ước tính (vật liệu PLA/PETG), các giả định.

## Điện (nhắc khi ghép linh kiện)
- ESP32/Pico là logic 3.3 V: HC-SR04 Echo (5 V) cần chia áp; servo/động cơ cấp nguồn riêng, chung GND.

## URDF (RobotCAD)
- Mỗi link một Part/Body; khớp quay đặt trục trùng tâm trục động cơ. Gán vật liệu để tính khối lượng/quán tính.
- Không dùng tính năng gửi dự án ra ngoài (robotcad.ru) hoặc LLM provider ngoài.
