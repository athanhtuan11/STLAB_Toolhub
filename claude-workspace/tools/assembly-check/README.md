# assembly-check – kiểm lắp ráp thật

Công cụ dùng chung cho mọi dự án tách part: kiểm **va chạm giữa các part**, **đường đưa part vào chỗ**,
**part lắp xong có được giữ đủ hướng không** và **file khai báo hợp lệ**. Gate cũ chỉ kiểm từng part nên
không bắt được tấm bụng/mỏ chồng vào vỏ, đường lắp bị chặn hay hai nửa vỏ không có mối nối.

Chạy trong Blender 5.2 (chỉ dùng `bpy`/`bmesh`/`mathutils` + thư viện chuẩn):

```
blender -b --factory-startup --python-exit-code 1 -P assembly_check.py -- <assembly.json>
blender -b --factory-startup --python-exit-code 1 -P assembly_check.py -- --auto <asm_dir> [--report <file.json>]
```

- Chế độ cấu hình: báo cáo ghi ra `<thư mục chứa assembly.json>/assembly-report.json`.
- Chế độ `--auto`: chỉ kiểm cặp va chạm (không có cặp chạm nào được phép), báo cáo ghi ra `--report`
  (mặc định `<asm_dir>/assembly-report.json`).
- Exit code `1` khi verdict FAIL, `0` khi PASS.

## Đầu vào

- Thư mục STL lắp ráp: mỗi file là 1 part, **đã đặt ở tọa độ lắp**, đơn vị mm. Tên part = tên file bỏ `.stl`.
- File cấu hình `assembly.json` (JSON, không YAML vì Python của Blender không có PyYAML):

```json
{
  "asm_dir": "out/asm",
  "tol": {"penetration": 0.2, "contact": 0.05, "path_step": 0.5, "seat_stop": 0.5, "probe": 2.0},
  "order": ["shell-front", "belly", "beak"],
  "parts": {
    "shell-front": {"fixed": true},
    "belly": {"insert": {"dir": [0, -1, 0], "from": 60}},
    "beak":  {"insert": {"moves": [[0, 30, 0], [0, 0, -20]]}}
  },
  "allowed_contacts": [["shell-front", "shell-back"]],
  "joints": [{"type": "screw", "parts": ["shell-back", "shell-front"], "blocks": ["+y"], "note": "4 vít M3 tấm đế"}]
}
```

`asm_dir` tính tương đối theo thư mục chứa `assembly.json`. Thiếu khóa nào trong `tol` thì dùng mặc định
đúng như ví dụ trên.

Khóa thêm trong `insert` (2026-11-27, Cú Bông v3):
- `"flex": <mm>` (0 < flex ≤ 1,0): part có **lẫy snap** – trên đường lắp, part được co thêm `flex` mm (lẫy biến dạng khi ép).
  Chỉ hợp lệ khi có joint `snap` mà `parts[0]` là part đó. Ở vị trí lắp vẫn kiểm đầy đủ (không co).
- `"with": ["<part>"]`: **cụm lắp sẵn** (vd. vòng ép đã xoay khóa trên vành loa rồi mới đặt cả cụm vào vỏ) – các part trong
  `with` không tính là vật cản trên đường lắp của part này; chúng phải đứng trước trong `order`.

## Bốn nhóm kiểm

1. **config** – STL trong thư mục phải được khai báo trong `parts` (và ngược lại), `order` phải chứa đủ
   mọi part, part không `fixed` phải có `insert` (`dir`+`from` hoặc `moves`), joint phải có `type` hợp lệ
   (`screw`, `bayonet`, `snap`, `press`, `pin`, `glue`), `pin` phải có `pin_part` là part đã khai báo,
   `blocks` chỉ dùng `+x/-x/+y/-y/+z/-z/*`, part trong joint phải tồn tại và joint phải có `note`.
2. **pair** – mọi cặp part: chồng vật liệu → FAIL (kèm `where` là tâm vùng chồng và `n` số cặp mặt);
   chỉ chạm mà cặp không nằm trong `allowed_contacts` → WARN. Cặp có hộp bao (nở thêm contact) không
   giao nhau được bỏ qua nhanh.
3. **path** – duyệt theo `order`, vật cản là các part đứng trước. Đi từ điểm xuất phát
   (chỗ lắp trừ tổng các đoạn `dir`/`from` hoặc `moves`) tới chỗ lắp, mỗi bước `path_step` mm, dừng khi
   còn dưới `seat_stop` mm. Chồng với vật cản lần đầu → FAIL, kèm `at` là quãng còn lại tới chỗ lắp.
4. **retention** – ở trạng thái lắp xong, mỗi part không `fixed` được thử tịnh tiến `probe` mm theo 6 hướng
   ±x ±y ±z. Hướng không chồng với part nào là **tự do**; hướng tự do chỉ được che nếu có joint mà
   `parts[0]` là part đó và `blocks` chứa hướng đó hoặc `"*"`. Còn hướng tự do chưa che → FAIL (`free_dirs`).
   Joint `glue` → WARN (keo dán thì không tháo được).

Báo cáo `assembly-report.json` (UTF-8, `ensure_ascii=False`, indent 2) gồm `verdict`, `parts` (đã sắp xếp),
`issues` (`level`, `check`, `parts`, `msg` + chi tiết) và `tol`. Stdout in mỗi issue một dòng
`ASM <level> <check> <parts> <msg>` và dòng cuối `ASSEMBLY <verdict> fail=<n> warn=<n>`.

## Giới hạn

- Chỉ xét **tịnh tiến**, chưa xét xoay: part có thể xoay ra khỏi chỗ mà vẫn được báo là bị giữ.
- STL phải **đã ở tọa độ lắp**; công cụ không tự đặt lại vị trí.
- Part mềm/biến dạng (ví dụ lẫy gài khi ép vào) sẽ bị báo chặn đường: hãy khai báo đường lắp đi vòng
  qua chỗ lẫy, hoặc ghi joint `snap` để đánh dấu.
- Chồng vật liệu được phát hiện bằng cách co bề mặt mỗi part vào trong `penetration/2` rồi kiểm giao;
  chạm dùng nở ra `contact/2`. Đây là xấp xỉ, không phải phép trừ khối chính xác.
