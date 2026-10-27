---
task: selftest-calc
cwd: tools/delegate/selftest/work
allow: ["calc.py"]
gate: "python test_calc.py"
timeout_min: 5
max_rounds: 2
executor: auto
---

# Mục tiêu
Tạo `calc.py` với 2 hàm: `add(a, b)` trả tổng, `clamp(x, lo, hi)` giới hạn x trong [lo, hi].

# Không làm
- Không sửa `test_calc.py`.
