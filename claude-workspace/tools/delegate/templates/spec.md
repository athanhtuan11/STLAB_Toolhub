---
# Đặc tả giao việc – Claude viết, executor (Codex/OpenCode/agy) làm.
# Đường dẫn tương đối tính từ claude-workspace/.
task: ten-viec-kebab-case
cwd: maker/<du-an>/firmware          # executor chỉ làm việc trong thư mục này
allow:                                # file được tạo/sửa (glob, tương đối theo cwd)
  - "src/*.py"
  - "tests/test_*.py"
gate: "python -m pytest -q tests"     # lệnh kiểm, chạy trong cwd; exit 0 = PASS
timeout_min: 15                       # mỗi vòng executor
max_rounds: 2                         # gate FAIL thì giao lại kèm lỗi, tối đa N vòng
executor: auto                        # auto | codex | opencode | agy
---

# Mục tiêu
<1–3 câu: làm gì, để làm gì>

# Đầu vào
- <file đọc được, dữ liệu, API>

# Yêu cầu
- <hành vi cụ thể, số liệu do Claude chốt – executor KHÔNG tự chọn kích thước/thông số>

# Không làm
- <phạm vi loại trừ>

# Tiêu chí PASS
- Lệnh gate exit 0.
- <tiêu chí bổ sung Claude sẽ tự kiểm>
