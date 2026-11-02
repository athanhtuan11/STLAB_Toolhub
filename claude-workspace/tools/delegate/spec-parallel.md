---
task: delegate-parallel
cwd: tools/delegate
allow:
  - "delegate.py"
gate: "python tests/test_parallel.py && python tests/test_delegate.py && python tests/test_registry.py && python tests/test_stats.py && python tests/test_stats_time.py"
timeout_min: 40
max_rounds: 3
executor: opencode
---

# Mục tiêu (Tuan duyệt 2026-11-02, đề xuất #3 trong `docs/reports/delegate-pipeline-pain-2026-11.md`)
Cho nhiều việc giao chạy song song không bị FAIL oan, giữ tương thích mọi spec cũ. Sửa `delegate.py` (không viết lại).
Gate `tests/test_parallel.py` (Claude viết, KHÔNG sửa) đặc tả chính xác tên hàm/tham số; 4 test cũ phải vẫn PASS.

# (A) Khóa ghi allow – MẶC ĐỊNH
1. `take_lock(cwd_rel, task, run_dir, allow_ws=None)`: ghi thêm `cwd` và `allow_ws` (danh sách mẫu glob **tương đối WS**,
   = mỗi mẫu allow nối với cwd_rel) vào file khóa. main() truyền allow_ws.
2. `other_runs_claim(files, my_run_dir)`: đọc mọi khóa trong `USAGE/locks/*.json`; bỏ khóa có pid chết (`_pid_ok`) và khóa
   có run_dir trùng `my_run_dir` (`_same_dir`); trả các file (tương đối WS) khớp `fnmatch` một mẫu `allow_ws` của khóa
   còn sống.
3. Trong `run_task`: file thuộc `other_runs_claim(...)` **không** tính vào `outside_allow` (vẫn tính `forbidden`); ghi
   `result["other_runs"] = [...]`.

# (B) `worktree: true` trong front matter – TÙY CHỌN (mặc định false; spec cũ không đổi hành vi)
4. `make_worktree(run_dir) -> path`: `git -C WS rev-parse --show-toplevel` = top; tạo `git worktree add --detach
   <USAGE>/delegate-wt/<tên run_dir> HEAD`; chép đè vào worktree mọi file **chưa commit** (sửa + mới, không bị ignore –
   `git status --porcelain -uall`) của cả repo; tạo **junction** (`cmd /c mklink /J`) cho thư mục `<WS>/community` (nếu có);
   chép các file bị ignore cần cho gate khớp `*.FCStd` dưới WS (giữ đường dẫn). Trả thư mục tương ứng WS trong worktree.
5. `sync_back(wt_ws, allow_ws) -> (copied, skipped)`: file thay đổi/mới trong worktree (so với lúc tạo) khớp allow_ws → chép
   về WS; còn lại vào skipped (không chép). Không bao giờ git commit.
6. `remove_worktree(wt_ws)`: **gỡ junction bằng `os.rmdir` TRƯỚC** (không theo link, không rmtree vào community gốc), rồi
   `git worktree remove --force` + `git worktree prune`. Gate B9 kiểm community gốc còn nguyên – bắt buộc.
7. `run_task`: nếu `meta.get("worktree")` true → cwd thực thi + gate = thư mục tương ứng trong worktree; PASS thì
   `sync_back` theo allow (ghi `result["synced"]`, `result["not_synced"]`), luôn `remove_worktree` trong `finally`.
   Khóa vẫn theo cwd_rel. `parse_spec` chấp nhận khóa `worktree` (bool, mặc định False).

# Không làm
- Không sửa tests/, org/, file khác. Không đổi hành vi mặc định ngoài (A). Không xóa gì ngoài worktree tạm.
- Thiếu/mâu thuẫn → `ESCALATE: <cần gì>`.

# Tiêu chí PASS
Gate exit 0 (test_parallel + 4 test cũ).
