---
task: pre-commit-ci
cwd: tools
allow:
  - "git-hooks/pre_commit.py"
  - "git-hooks/pre-commit"
  - "git-hooks/README.md"
  - "ci/run_ci.py"
  - "ci/ci.yml"
gate: "python git-hooks/tests/test_pre_commit.py && ../studio/.venv/Scripts/python.exe ci/run_ci.py"
timeout_min: 25
max_rounds: 2
executor: opencode
---

# Mục tiêu
Chặn lỡ commit file không được lên git (model, bí mật, bản clone cộng đồng, media dự án, file lớn) và lỗi Python cơ
bản, bằng hook git tự viết (không dùng framework `pre-commit` – khỏi cài thêm). Thêm bộ chạy test nhẹ dùng chung cho máy
và GitHub Actions.

# Đầu vào
- Gate `tools/git-hooks/tests/test_pre_commit.py` (Claude viết, KHÔNG sửa) – đặc tả chính xác luật chặn.
- Gốc git = thư mục cha của claude-workspace (`D:\04_Stlab\04_STLAB_Toolhub`); đường dẫn trong git có tiền tố
  `claude-workspace/`.

# Yêu cầu
## tools/git-hooks/pre_commit.py (stdlib + lệnh `ruff` nếu có)
- Chạy ở bất kỳ thư mục nào trong repo; lấy gốc bằng `git rev-parse --show-toplevel`.
- Mặc định: xét file **đã stage** (`git diff --cached --name-only --diff-filter=ACMR`, đọc nội dung từ index bằng
  `git show :<path>`, không đọc bản trên đĩa). `--all`: xét mọi file `git ls-files` (đọc trên đĩa) – dùng cho CI.
- Luật (đường dẫn tính từ gốc repo, `WS = claude-workspace/`, so khớp không phân biệt hoa thường cho đuôi file):
  1. `WS/maker/**.FCStd` → chặn (FCStd ở nơi khác, vd. `tools/cad-delegation/**/context.FCStd`, được phép).
  2. Tên file `.env` hoặc bắt đầu `.env.` ở bất kỳ đâu → chặn.
  3. `WS/community/<thư mục con>/...` → chặn, TRỪ `WS/community/reports/**`. File nằm thẳng trong `WS/community/`
     (pins.tsv, links.tsv, *.sparse, update-community.sh) được phép.
  4. Media trong `WS/maker/**`: đuôi png, jpg, jpeg, gif, webp, mp4, mov, mkv, mp3, wav, m4a, pdf → chặn
     (svg được phép).
  5. File > 2 MiB (2 097 152 byte) → chặn.
  6. File `.py`: `ruff check --select E9,F63,F7,F82 --no-cache --quiet` trên nội dung staged (ghi ra thư mục tạm giữ
     tên file). Không có `ruff` trên PATH → in cảnh báo, bỏ qua luật này (không chặn).
  7. Bí mật trong nội dung văn bản (bỏ qua file nhị phân – có byte 0): `sk-[A-Za-z0-9_-]{20,}`,
     `gh[pousr]_[A-Za-z0-9]{36,}`, `AKIA[0-9A-Z]{16}`, `-----BEGIN [A-Z ]*PRIVATE KEY-----`. Chỉ in tên file + luật, KHÔNG
     in chuỗi bí mật ra màn hình.
- In mỗi vi phạm 1 dòng `CHAN <luật>: <đường dẫn>`, dòng cuối hướng dẫn ngắn tiếng Việt không dấu. Exit 1 nếu có vi
  phạm, 0 nếu không. Bỏ qua file đã xóa.
- Nhanh: không chạy ruff khi không có file .py; tổng thời gian commit thường < 3 s.

## tools/git-hooks/pre-commit (shell, LF, không đuôi)
`#!/bin/sh` → `exec python "$(git rev-parse --show-toplevel)/claude-workspace/tools/git-hooks/pre_commit.py" "$@"`.

## tools/git-hooks/README.md (tiếng Việt, ngắn)
Cài: `git config core.hooksPath claude-workspace/tools/git-hooks` (chạy ở gốc repo). Liệt kê luật. Không hướng dẫn
cách bỏ qua hook.

## tools/ci/run_ci.py
- Tự `os.chdir` về claude-workspace (`Path(__file__).resolve().parents[2]`) – chạy được từ bất kỳ đâu, bằng Python của `studio/.venv` (có Flask, yaml). Lần lượt chạy (mỗi cái subprocess
  `sys.executable <file>`, cwd như ghi chú đầu file test đó yêu cầu, hạn 300 s), in `PASS/FAIL <tên> <giây>`, cuối in
  tổng; exit 1 nếu có FAIL:
  - `tools/git-hooks/pre_commit.py --all`
  - `tools/git-hooks/tests/test_pre_commit.py`, `tools/backup/tests/test_backup.py`
  - `tools/org/tests/*.py`, `tools/delegate/tests/test_*.py`
  - `studio/tests/`: test_quote.py, test_quote_bulk.py, test_quote_model_extras.py, test_org_board.py,
    test_library_pages.py, test_pinout.py
- KHÔNG chạy test cần FreeCAD, Bambu Studio, Graphviz hay thư mục `community/` (vd. test_quote_slice, test_pin_diagram,
  tools/robotics-cad, tools/model-study). Nếu một test trong danh sách trên cần thứ đó (đọc mã để biết), loại nó ra và
  ghi lý do thành chú thích trong `run_ci.py`.
- Tham số `--list`: chỉ in danh sách.

## tools/ci/ci.yml (GitHub Actions – Claude sẽ chép vào `.github/workflows/` ở gốc repo)
- Trên `push` và `pull_request` nhánh main; `runs-on: windows-latest`; `permissions: contents: read`.
- Bước: checkout → `astral-sh/setup-uv` → `uv sync` trong `claude-workspace/studio` → `uv pip install ruff` vào
  venv đó → chạy `studio/.venv/Scripts/python.exe tools/ci/run_ci.py` với working-directory `claude-workspace`.
- Ghim action theo tag phiên bản chính (vd. `@v4`), không dùng secret nào.

# Lần 1 (Codex) FAIL
`pre_commit.py` chỉ 1 dòng, KHÔNG chặn `maker/**.FCStd`; chưa có `tools/ci/`. Viết lại đầy đủ.

# Không làm
- Không chạy `git config` trên repo thật, không commit, không tạo `.github/` (Claude làm).
- Không sửa file test nào, không sửa test có sẵn để cho qua.

# Tiêu chí PASS
- Gate exit 0 (gồm `pre_commit.py --all` trên repo thật phải sạch).
