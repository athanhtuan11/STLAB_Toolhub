# tools/cad-delegation

Quy trình giao việc dựng model CAD cho agent rẻ. Không dùng AI local.

## Mục đích

- Claude viết `spec.yaml` và duyệt kết quả.
- Codex (ChatGPT Free) viết và chạy script FreeCAD trên máy (`freecadcmd`) tới khi qua gate.

## File

- `features.py`: trích đặc trưng hình học 1 chi tiết từ FCStd. Thêm từ khóa `local` để đo theo hệ tọa độ riêng của chi tiết.
- `make_context.py`: tạo `context.FCStd` CHỈ chứa chi tiết lân cận, không có chi tiết mẫu. Đổi sang hệ tọa độ của spec.
- `gate.py`: đọc mục `gate` trong `spec.yaml`, kiểm:
  - bbox, vùng rỗng/đặc;
  - khe với chi tiết lân cận;
  - chuyển động lắp/thảo/xoay;
  - kiểm in theo hướng đặt bàn bằng `printability.py`.
  Ghi kết quả ra `gate.json`. Kiểm "vươn ra" theo lớp chỉ là cảnh báo.
- `compare.py`: chấm với chi tiết mẫu. Báo phần thừa/thiếu (mm3) và % lệch.
- `render_pilot.py`: ảnh review `review-iso` và `review-solo`.

## Quy trình 6 bước

1. `features.py` đọc chi tiết và neighbors.
2. `make_context.py` tạo context.
3. Claude viết `spec.yaml`: `frame`, `design`, `print`, `neighbors_info`, `deliverable`, `gate`.
4. Hiệu chuẩn gate trên chi tiết mẫu: mẫu phải PASS, khối hợp sai phải FAIL. Mẫu để NGOÀI thư mục giao.
5. Giao Codex.
6. Claude tự chạy lại `gate.py` + `compare.py` và xem ảnh.

## Lệnh giao Codex

Trên Windows phải truyền tham số sandbox. Nếu không, mọi lệnh bị "blocked by policy":

```bash
cd <thư mục giao>
codex exec --sandbox workspace-write --skip-git-repo-check -c features.prefer_mxc=true - < ../prompt.txt
```

- `pilot/prompt.txt` là mẫu prompt.
- Plugin `/codex:rescue` hiện KHÔNG dùng được cho việc này vì không truyền được tham số sandbox.

## Mẫu

- `pilot/knuckle`
- `pilot/piston-rod`
