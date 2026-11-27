"""test_runlog.py - canh bao cham di cua runlog.py: 6 lan binh thuong -> lan cham thu 1 KHONG bao, lan cham thu 2 lien tiep BAO;
nhom khac (cache khac) khong bi tinh lan; buoc loi (rc != 0) bo qua; do RAM dinh tien trinh con > 0 tren Windows."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runlog import RunLog  # noqa: E402

fails = []
with tempfile.TemporaryDirectory() as td:
    def one(s, cache="miss", rc=0):
        rl = RunLog(td, "test/p", mode="fast", cwd=td)
        rl.add("cat lop", s, rc=rc, cache=cache)
        return rl.finish()
    for v in (10.0, 10.4, 9.8, 10.1, 10.2, 9.9):
        if one(v):
            fails.append("bao nham khi binh thuong")
    if one(20.0):
        fails.append("lan cham thu 1 da bao (phai cho 2 lan lien tiep)")
    w = one(21.0)
    if not any("CHAM DI: cat lop" in x for x in w):
        fails.append(f"lan cham thu 2 khong bao: {w}")
    if one(20.0, cache="hit"):
        fails.append("nhom cache khac bi so voi nhom miss")
    if one(99.0, rc=1):
        fails.append("buoc loi van bi canh bao")
    rl = RunLog(td, "test/mem", mode="fast", cwd=td)
    rl.run("python", [sys.executable, "-c", "x = bytearray(80 * 2**20); print(len(x))"])
    pk = rl.steps[-1]["peak_mem_mb"]
    if os.name == "nt" and not (pk and pk > 80):
        fails.append(f"RAM dinh tien trinh con sai: {pk}")
    print(f"RAM dinh tien trinh con (cap 80 MB): {pk} MB")
for f in fails:
    print("FAIL", f)
print("PASS test_runlog" if not fails else f"FAIL test_runlog ({len(fails)})")
sys.exit(1 if fails else 0)
