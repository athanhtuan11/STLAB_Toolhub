# Workbench STLab cho FreeCAD 1.1

Giao diện trong FreeCAD cho pipeline `maker/robotics-cad/scripts/`. Workbench chỉ **gọi lại** các script có sẵn
(một nguồn logic), không tính lại theo cách riêng. Việc nặng chạy trong tiến trình riêng nên FreeCAD không bị treo.

## Cài (một lần)
```
python maker/robotics-cad/workbench/install.py         # tạo junction %APPDATA%\FreeCAD\v1-1\Mod\STLab -> workbench/STLab
python maker/robotics-cad/workbench/install.py remove  # gỡ junction (không xóa mã)
```
Mở lại FreeCAD → chọn workbench **STLab**. Bảng **STLab Workflow** hiện bên phải.
Mã nguồn chỉ nằm trong workspace; thư mục `Mod/STLab` là junction, không phải bản sao.

## Quy trình chuẩn → lệnh
| Bước | Lệnh | Làm gì | Gọi |
|---|---|---|---|
| 1 Dự án | Tạo dự án mới | `maker/<name>/` từ `project-template` + model trống đúng chỗ | (giống `/new-project`) |
| | Mở dự án | danh sách dự án + kết luận *Chuẩn bị in* gần nhất | |
| | Thư mục | mở `maker/<project>/` | |
| 2 Linh kiện | Thư viện linh kiện | tìm trong `library/components.yaml` (thông số có nguồn, TODO), chèn STEP với Label `CB_`/`LK_`, đặt cạnh model | |
| 3 Thiết kế | Kiểm tên Label | từng chi tiết → vít / linh kiện mua / in 3D (nhóm, hướng in, bàn) / **chưa phân loại**; sửa Label ngay trong bảng (có Undo) | logic `bom.py` |
| | Xem hướng in | chi tiết đang chọn → xoay theo `print.yaml`, đặt trên bàn A1 ảo (256 × 256 mm) cạnh model; **đỏ** = mặt nhô ra. Chỉ vẽ lớp phủ, **không sửa file**. Không chọn gì + bấm = tắt | logic `export-stl.py` |
| | Sao lưu | `freecad/backup/<model>.<thời gian>.<ghi chú>.FCStd` | `safe_edit.backup` |
| 4 Kiểm tra | Kiểm nhanh / đầy đủ | tầng 1, chạy nền; có FAIL/WARN → mở bảng lỗi | `check.py` |
| | Xem lỗi | bảng FAIL/WARN; nhấp một dòng → chọn và phóng to chi tiết lỗi trong 3D | `report.json` |
| 5 In 3D | Xuất STL / Khả năng in / Cắt lớp | từng bước riêng | `export-stl.py`, `printability.py`, `slice.py` |
| | **Chuẩn bị in (cả vòng)** – Ctrl+Shift+P | kiểm hết trước, sạch mới cắt lớp → hiện ảnh tổng quan | `prepare-print.py` |
| | Tự chuẩn bị in mỗi khi Lưu (ô chọn) | Lưu model → chạy cả vòng nền (thay `watch.py`) | |
| | Mở bàn in | danh sách `.3mf` (bàn cũ được đánh dấu) → mở bằng Bambu Studio | |
| 6 Tài liệu | BOM | `metrics.py` → `bom.py` → hiện `BOM.md` | |
| | So với commit trước | chi tiết đổi ngoài ý muốn so với git HEAD | `metrics.py diff` |
| | PDF lắp ráp | `ASSEMBLY.md` → `ASSEMBLY.pdf` | `assembly-pdf.py` |

## Lưu ý
- Script kiểm/xuất **chỉ đọc file đã Lưu**. Model có thay đổi chưa Lưu thì lệnh hỏi: Lưu / chạy bản đã lưu / Hủy.
  Trạng thái "đã lưu / CHƯA LƯU" hiện ở đầu bảng Workflow.
- Mỗi lần chỉ chạy 1 việc (các script ghi chung thư mục kết quả); việc mới sẽ xếp hàng. Nút **Dừng** hủy cả hàng chờ.
- "Xem hướng in" chỉ để xem nhanh (ngưỡng `overhang_deg - overhang_tol_deg`, bỏ qua mặt sát bàn). Kết quả chính
  vẫn là `printability.py` trong *Chuẩn bị in*.
- Quy tắc một phiên Claude giữ FreeCAD vẫn áp dụng: workbench do người dùng bấm, không mở cổng nào mới.

## Phát triển
```
workbench/
  install.py  make_icons.py         cài junction / sinh icon SVG (màu theo bước)
  STLab/InitGui.py                  workbench: 6 toolbar + menu STLab › <bước>, menu chuột phải trong 3D
  STLab/stlab_wb/core.py            không Qt: đường dẫn, dự án (print.yaml), phân loại Label, hướng in – test bằng freecadcmd
  STLab/stlab_wb/runner.py          QProcess xếp hàng, lọc nhiễu log của freecadcmd
  STLab/stlab_wb/commands.py        lệnh FreeCAD (STAGE_CMDS = thứ tự quy trình) + observer "tự chạy khi Lưu"
  STLab/stlab_wb/panel.py           bảng STLab Workflow
  STLab/stlab_wb/dialogs.py         hộp thoại
  STLab/stlab_wb/preview.py         lớp phủ Coin3D "Xem hướng in"
```
Thêm lệnh: viết class trong `commands.py` (tên `STLab_<Class>`), thêm vào `STAGE_CMDS` và `panel.STAGES`,
thêm icon vào `make_icons.py`, rồi chạy lại script đó. Test giao diện không cần mở cửa sổ: chạy `freecad.exe -u <bản sao user.cfg> test.py`
và chụp `widget.grab()` (cách đã dùng 2026-10-24).
