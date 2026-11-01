---
task: toolchain-versions
cwd: tools/toolchain
allow:
  - "versions.py"
  - "README.md"
gate: "python tests/test_versions.py"
timeout_min: 25
max_rounds: 2
executor: auto
---

# Mục tiêu
Một lệnh in ra phiên bản các công cụ STLab đang cài + dung lượng từng repo trong `community/`, ghi thành
`docs/toolchain.md`. Lần "tìm hiểu mới nhất" sau chỉ cần chạy lệnh này rồi so với bản phát hành mới.

# Đầu vào
- Gate `tests/test_versions.py` (Claude viết, KHÔNG sửa) – đặc tả chính xác khóa JSON + bảng markdown.
- `../../community/pins.tsv` (cột: name, url, type, ref, sha, ...), `../../community/links.tsv` (dest TAB source,
  source dạng `community/<repo>/...`; dòng `#` là chú thích).

# Yêu cầu
- `versions.py` (stdlib, Python 3.11+): tham số `--out` (mặc định `<workspace>/docs/toolchain.md`), `--json` (tùy chọn).
- Công cụ (id → cách lấy; mỗi lệnh subprocess hạn 20 s, `shell=False`, lỗi/không có → `version: null`, KHÔNG đoán):
  - `freecad`: `C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe --version` (dòng có `FreeCAD x.y.z`).
  - `bambu-studio`: đọc phiên bản từ thuộc tính file exe `C:/Program Files/Bambu Studio/bambu-studio.exe`
    (PowerShell `(Get-Item ...).VersionInfo.ProductVersion`) – nếu đường dẫn khác, tìm trong `slice.py` /
    `../robotics-cad/scripts/quote_slice.py` hằng số đường dẫn Bambu và dùng nó.
  - `esp-idf`: `IDF_PATH` hoặc thư mục `C:/Espressif/frameworks/esp-idf-v*` → file `version.txt` hoặc tên thư mục;
    nhiều bản → liệt kê hết, cách nhau dấu phẩy, `version` = bản mới nhất.
  - `python` (sys.version), `git`, `node`, `uv`, `codex`, `opencode`, `kilo`, `copilot`, `agy` (`<lệnh> --version`, tìm
    bằng `shutil.which`), `graphviz` (`dot -V`), `hyperframes` (đọc ghim `0.8.x` trong `../../video-ai/CLAUDE.md` hoặc
    `pins.tsv` – ghi rõ `source: "ghim"`).
  - `claude-code`: thư mục extension `~/.vscode/extensions/anthropic.claude-code-<ver>-*` mới nhất → `<ver>`.
  - `source`: chuỗi ngắn mô tả cách lấy (vd. `"freecadcmd --version"`), KHÔNG chứa đường dẫn home đầy đủ
    (thay `C:\Users\<tên>` bằng `~`).
- Community: mỗi thư mục con của `community/` trừ `reports` → `{name, size_mb (1 chữ số thập phân), linked (có dòng
  links.tsv trỏ vào), pin (sha 12 ký tự hoặc ref từ pins.tsv, không có → null), last_commit (ngày ISO của HEAD
  `git -C <dir> log -1 --format=%cs`, lỗi → null)}`. Dung lượng: cộng `st_size` file (os.scandir đệ quy, không theo
  symlink, bỏ qua lỗi quyền). `community_total_mb`.
- Markdown (tiếng Việt): tiêu đề `# Phiên bản công cụ (sinh tự động – <ngày giờ>)`, ghi chú "chạy
  `python tools/toolchain/versions.py` để cập nhật, không sửa tay"; bảng `| Công cụ | Phiên bản | Lấy từ |`; bảng
  `| Repo | MB | Liên kết | Ghim | Commit cuối |` (tên repo trong backtick, sắp MB giảm dần, dòng tổng cuối bảng không
  trong backtick); dưới bảng: danh sách repo `linked = false` và > 100 MB làm "ứng viên gỡ/sparse – Tuan quyết".
- `README.md` ngắn: chạy thế nào, ra file gì.

# Không làm
- Không xóa/sửa gì trong `community/`, không gọi mạng, không sửa `tests/`, không ghi `docs/toolchain.md` khi chạy gate
  (gate truyền `--out` vào thư mục tạm).

# Tiêu chí PASS
- Gate exit 0. Claude tự chạy lệnh thật để sinh `docs/toolchain.md`.
