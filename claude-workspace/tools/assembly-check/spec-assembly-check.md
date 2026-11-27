---
# Đặc tả giao việc – Claude viết 2026-11-27, executor làm. Đường dẫn tương đối tính từ claude-workspace/.
task: assembly-check
cwd: tools/assembly-check
allow:
  - "assembly_check.py"
  - "README.md"
gate: "python -X utf8 -m unittest discover -s tests -v"
timeout_min: 25
max_rounds: 2
executor: auto
---

# Mục tiêu
Công cụ dùng chung kiểm **lắp ráp thật** cho mọi dự án tách part: va chạm mọi cặp part, đường đưa từng part vào chỗ,
part lắp xong có bị giữ đủ hướng không, file khai báo hợp lệ. Lý do: gate cũ chỉ kiểm từng part → Cú Bông
có tấm bụng + mỏ chồng vào vỏ, đường lắp bị chặn, 2 nửa vỏ không có mối nối mà gate vẫn PASS.

# Đầu vào
- Thư mục STL lắp ráp (mỗi file = 1 part, **đã đặt ở tọa độ lắp**, đơn vị mm), tên part = tên file bỏ `.stl`.
- File cấu hình `assembly.json` (JSON, không YAML – Python của Blender không có PyYAML).
- Gate: `tests/test_assembly_check.py` (KHÔNG sửa). Đọc kỹ fixture + kỳ vọng trong đó.

# Cách chạy (Blender 5.2, chỉ dùng bpy/bmesh/mathutils + thư viện chuẩn)
```
blender -b --factory-startup --python-exit-code 1 -P assembly_check.py -- <assembly.json>
blender -b --factory-startup --python-exit-code 1 -P assembly_check.py -- --auto <asm_dir> [--report <file.json>]
```
Đối số lấy sau `--` trong `sys.argv`. Chế độ cấu hình: báo cáo ghi ra `<thư mục chứa assembly.json>/assembly-report.json`.
Chế độ `--auto`: chỉ chạy kiểm cặp (mục 2), không có cặp chạm được phép; báo cáo ghi ra `--report` (mặc định `<asm_dir>/assembly-report.json`).
Exit code 1 khi verdict FAIL (dùng `sys.exit(1)` cuối script), 0 khi PASS.

# Định dạng assembly.json
```json
{
  "asm_dir": "out/asm",                       // tương đối theo thư mục chứa assembly.json
  "tol": {"penetration": 0.2, "contact": 0.05, "path_step": 0.5, "seat_stop": 0.5, "probe": 2.0},
  "order": ["shell-front", "belly", "..."],   // thứ tự lắp, phải chứa MỌI part khai báo
  "parts": {
    "shell-front": {"fixed": true},           // part mốc: không kiểm đường lắp, không kiểm giữ
    "belly": {"insert": {"dir": [0, -1, 0], "from": 60}},          // đi thẳng theo dir (hướng chuyển động VÀO chỗ) quãng from mm
    "beak":  {"insert": {"moves": [[0, 30, 0], [0, 0, -20]]}}      // hoặc đường gấp khúc: các đoạn dịch chuyển nối tiếp, kết thúc tại chỗ lắp
  },
  "allowed_contacts": [["shell-front", "shell-back"]],
  "joints": [{"type": "screw", "parts": ["shell-back", "shell-front"], "blocks": ["+y"], "note": "4 vít M3 tấm đế"}]
}
```
Giá trị `tol` mặc định (Claude chốt) = đúng các số trong ví dụ trên; thiếu khóa nào dùng mặc định đó.

# Yêu cầu – hình học
Nạp STL bằng `bpy.ops.wm.stl_import`, chuyển sang bmesh, `bmesh.ops.recalc_face_normals`. **KHÔNG** `remove_doubles`.
Hàm `offset_tree(bm, d, move=Vector())`: tạo BVHTree từ các tam giác, **mỗi tam giác dịch theo pháp tuyến mặt của chính nó**
một khoảng `d` (d < 0 = co vào trong, d > 0 = nở ra) rồi tịnh tiến `move`. Dùng `BVHTree.FromPolygons(verts, polys)`.
Cache cây đứng yên theo (part, d); cây tịnh tiến dựng mới mỗi bước.
- `pen_tree(p, move)` = offset_tree(p, −penetration/2, move); `contact_tree(p)` = offset_tree(p, +contact/2).
- **chồng** giữa A, B ⇔ `pen_tree(A).overlap(pen_tree(B))` khác rỗng. **chạm** ⇔ contact_tree giao nhau nhưng không chồng.

# Yêu cầu – 4 nhóm kiểm (mỗi nhóm 1 hàm, tên đúng như sau)
1. `check_config(cfg, stl_names)`:
   - STL có trong thư mục mà không khai báo trong `parts` → FAIL, `parts=[tên]`. Part khai báo mà thiếu STL → FAIL.
   - `order` thiếu/thừa part so với `parts` → FAIL. Part không `fixed` mà không có `insert` (dir+from hoặc moves) → FAIL.
   - `joints[].type` ∉ {screw, bayonet, snap, press, pin, glue} → FAIL, `msg` chứa tên type sai.
   - `type: pin` phải có `pin_part` là một part có khai báo (chốt phải được vẽ) → thiếu → FAIL, `msg` chứa tên `pin_part`.
   - `blocks` chỉ gồm {"+x","-x","+y","-y","+z","-z","*"}; part trong joint phải tồn tại; `note` bắt buộc → sai → FAIL.
2. `check_pairs(parts, allowed)`: mọi cặp (tổ hợp 2): chồng → FAIL `check:"pair"`, `parts:[a,b]`, `where:[x,y,z]` = tâm trung bình
   các mặt giao (làm tròn 1 chữ số), `n` = số cặp mặt. Chạm mà cặp không có trong `allowed_contacts` (không phân biệt thứ tự) →
   WARN `check:"contact"`. Bỏ qua nhanh cặp có hộp bao (nở thêm contact) không giao nhau.
3. `check_paths(cfg, parts)`: duyệt theo `order`; vật cản = các part đứng trước trong `order`. Với part có `insert`:
   chỗ lắp = vị trí STL; điểm xuất phát = chỗ lắp − tổng các đoạn (`dir` chuẩn hóa × `from` coi là 1 đoạn).
   Đi dọc đường từ điểm xuất phát, mỗi bước `path_step` mm theo chiều dài cung, dừng khi quãng còn lại < `seat_stop`;
   tại mỗi điểm kiểm **chồng** (pen_tree) với từng vật cản. Lần đầu bị chặn → FAIL `check:"path"`, `parts:[part, vật_cản]`,
   `at` = quãng đường còn lại tới chỗ lắp (mm, 1 chữ số), dừng kiểm part đó.
4. `check_retention(cfg, parts)`: ở trạng thái lắp xong (mọi part), với mỗi part không `fixed`, thử tịnh tiến `probe` mm theo
   6 hướng ±x ±y ±z; hướng không chồng với part nào khác = **tự do**. Hướng tự do được che nếu có joint mà `parts[0]` là part đó
   và `blocks` chứa hướng đó hoặc `"*"`. Còn hướng tự do không che → FAIL `check:"retention"`, `parts:[part]`,
   `free_dirs` = danh sách hướng tự do chưa che. (Chỉ tịnh tiến, chưa xét xoay – ghi trong README.)
   Joint `type: glue` → WARN `check:"joint"`, `parts` = joint.parts (keo = không tháo được, Tuan cần biết).

# Báo cáo
`assembly-report.json` (UTF-8, `ensure_ascii=False`, indent 2):
`{"verdict": "PASS"|"FAIL", "parts": [tên đã sắp xếp], "issues": [{"level": "FAIL"|"WARN", "check": "...", "parts": [...], "msg": "tiếng Việt ngắn", ...}], "tol": {...}}`.
verdict = FAIL nếu có ít nhất 1 issue FAIL. In ra stdout mỗi issue 1 dòng `ASM <level> <check> <parts> <msg>` và dòng cuối `ASSEMBLY <verdict> fail=<n> warn=<n>`.

# README.md (ngắn, tiếng Việt CÓ DẤU, viết UTF-8)
Mục đích, 2 lệnh chạy, định dạng assembly.json (copy ví dụ), ý nghĩa 4 nhóm kiểm, giới hạn (chỉ tịnh tiến; STL phải ở tọa độ lắp;
part mềm/biến dạng như lẫy gài khi ép vào sẽ bị báo chặn đường → khai báo đường lắp đi qua chỗ lẫy hoặc ghi joint snap).

# Không làm
- Không sửa `tests/`, không sửa file nào ngoài `allow`. Không thêm thư viện ngoài (trimesh, numpy…) – chỉ những gì có sẵn trong Blender.
- Không tự đổi số `tol` mặc định. Không đụng `maker/`.

# Tiêu chí PASS
- Lệnh gate exit 0 (12 test, gồm test hồi quy Cú Bông `test_20_owl_regression`).
- Claude tự kiểm thêm: chạy `--auto` trên asm Cú Bông, đọc báo cáo.
