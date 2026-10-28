---
task: new-executors
cwd: tools
allow: ["delegate/delegate.py", "delegate/tests/test_registry.py", "org/check_org.py", "org/tests/test_check_org.py"]
read: ["org"]
gate: "cd delegate && python tests/test_registry.py && python tests/test_delegate.py && cd ../org && python tests/test_check_org.py && python check_org.py"
timeout_min: 25
max_rounds: 2
executor: codex
---

# Mục tiêu
Tuan 2026-10-28 tuyển thêm 3 executor free, đã khai trong `claude-workspace/org/agents.yaml` (CHỈ ĐỌC – cấm sửa):
`kilo`, `agy-sonnet`, `copilot`, cả ba `trang_thai: thu-viec`. Chuỗi `khi_het_han_muc` mới:
codex → opencode → kilo → agy-sonnet → copilot → agy. Giữ phong cách file (chú thích tiếng Việt không dấu, gọn,
stdlib + yaml). Không đổi hành vi của codex/opencode/agy.

# Yêu cầu
1. `delegate/delegate.py` – thêm adapter vào `ADAPTERS` (giống mẫu `_opencode`/`_agy`; model lấy từ `ORG["model"][name]`):
   - `kilo`: exe = `shutil.which("kilo.cmd") or shutil.which("kilo")`;
     argv `[exe, "run", "--model", <model>]`, prompt qua stdin (giống opencode).
   - `agy-sonnet`: giống hệt `_agy` (cùng exe `agy`, cùng cờ) nhưng model của `agy-sonnet`.
     Gợi ý: một hàm dựng chung nhận `name`, tránh chép code.
   - `copilot`: exe = `shutil.which("copilot.cmd") or shutil.which("copilot")`; argv
     `[exe, "-p", prompt, "-s", "--no-ask-user", "--allow-all-tools", "--disable-builtin-mcps",`
     `"--deny-tool=shell(git commit)", "--deny-tool=shell(git push)", "--deny-tool=shell(git reset)",`
     `"--deny-tool=shell(git checkout)", "--deny-tool=shell(rm -rf)", "--deny-tool=shell(Remove-Item)"]`,
     thêm `"--model", <model>` chỉ khi model khác `"auto"`; stdin None. KHÔNG thêm `--allow-all-paths`/`--allow-all`.
   - Trong `run_task`, `env` thêm `KILO_CONFIG=os.path.join(HERE, "kilo.json")` (file đã có; Kilo không đọc
     OPENCODE_CONFIG – đã thử). Giữ nguyên OPENCODE_CONFIG.
   - Cập nhật dòng chú thích đầu file + `--executor` help nếu liệt kê tên executor.
2. `load_org`: hiện tại đã bỏ qua `thu-viec` trong `order` – giữ. Thêm: executor `thu-viec` cũng phải có trong
   ADAPTERS, thiếu → `ValueError` (để gọi đích danh được).
3. `org/check_org.py` (khối "doi chieu delegate.py"):
   - Tập executor `trang_thai: chinh-thuc` (không phải mọi người không `nghi`) phải bằng `set(ORDER)`.
   - Kiểm chuỗi: với executor thứ i trong ORDER, đi theo `khi_het_han_muc`, BỎ QUA người `thu-viec`/`nghi`, người
     chinh-thuc đầu tiên gặp phải là `ORDER[i+1]` (hoặc None nếu i cuối). Sai → E-DELEGATE như cũ. Vòng lặp/id lạ → E-DELEGATE.
   - Executor `thu-viec`/`chinh-thuc` không có trong `ADAPTERS` → E-DELEGATE.
   - `cooldown_h` kiểm cho mọi executor không `nghi` (COOLDOWN_H đã chứa mọi cli-executor).
4. Test:
   - `delegate/tests/test_registry.py`: sửa assert COOLDOWN_H theo sổ mới (codex 5, opencode 1, kilo 1,
     agy-sonnet 24, copilot 24, agy 24); ORDER vẫn `["codex", "opencode", "agy"]`; thêm assert
     `{"kilo","agy-sonnet","copilot"} <= set(ADAPTERS)`; `pick_queue(dict(executor="kilo"), "tools/x", org) == ["kilo"]`
     (thu-viec gọi đích danh được); `command("kilo","P")` → argv[1:4] == ["run","--model","kilo/kilo-auto/free"],
     stdin "P"; `command("agy-sonnet","P")[0]` chứa "claude-sonnet-4-6"; `command("copilot","P")[0]` chứa "-p", "P",
     "--deny-tool=shell(git push)", không chứa "--model" (model auto) và không chứa "--allow-all-paths".
     Khi exe không có trên máy (`which` trả None) test vẫn phải chạy được – chỉ kiểm phần argv sau exe.
   - `org/tests/test_check_org.py`: thêm ca sổ tạm có executor thu-viec chen giữa chuỗi → không lỗi; ca chuỗi bỏ qua
     thu-viec trỏ sai → có E-DELEGATE; ca executor thu-viec không có ADAPTERS → có E-DELEGATE.
5. Không sửa file nào khác. Không chạy kilo/copilot/agy thật.
