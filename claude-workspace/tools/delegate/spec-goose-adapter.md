---
task: delegate-goose-adapter
cwd: tools/delegate
allow:
  - "delegate.py"
  - "README.md"
gate: 'python tests/test_goose_adapter.py && python tests/test_watchdog_rr.py && python tests/test_stats.py && python tests/test_registry.py && python tests/test_delegate.py'
timeout_min: 20
max_rounds: 2
ky_nang: code
---

# Mục tiêu
Thêm executor **Goose** (CLI `goose`, v1.57.0, nguồn model Gemini API free) vào `delegate.py` (Tuan duyệt 2026-11-04).
Goose **không giới hạn thư mục** → mọi lần chạy có Goose trong hàng đợi phải dùng git worktree sẵn có (`make_worktree`).
Gate `tests/test_goose_adapter.py` do Claude viết – **KHÔNG sửa tests/**, không sửa `org/`. Giữ mọi hành vi cũ.

# Yêu cầu
1. `_goose(prompt)`: exe = `shutil.which("goose")` hoặc `%USERPROFILE%\.local\goose\goose-package\goose.exe` nếu có.
   argv = `[exe, "run", "--no-session", "-i", "-", "--provider", "google", "--model", ORG["model"]["goose"]]`,
   trả `(argv, prompt)` (prompt qua **stdin**). Không dùng `-s`/`--interactive`. Không hằng số model trong code.
   Đăng ký trong `ADAPTERS.update(...)` cùng chỗ các adapter khác.
2. `NEED_WORKTREE = {"goose"}` (cấp module) và `needs_worktree(meta, queue, fallback_queue=None)` → `True` nếu
   `meta.get("worktree")` là True hoặc bất kỳ executor nào trong `queue` / `fallback_queue` thuộc `NEED_WORKTREE`; ngược lại `False`
   (luôn trả bool).
3. Trong `run_task`: thay `use_wt = bool(meta.get("worktree"))` bằng `use_wt = needs_worktree(meta, queue, fallback_queue)`.
4. Cập nhật dòng chú thích đầu file (chuỗi executor + `--executor ...|goose`) và help của `--executor`.
5. README: thêm 3–5 dòng (tiếng Việt có dấu) về Goose: thử việc, gọi đích danh `executor: goose`, luôn chạy trong worktree,
   model lấy từ org/agents.yaml.

# Không làm
- Không sửa `tests/`, `org/`, các adapter khác. Không đổi định dạng spec. Không đặt biến môi trường/API key trong code.
