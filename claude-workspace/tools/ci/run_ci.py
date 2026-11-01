#!/usr/bin/env python3
"""Chay bo test nhe cua claude-workspace (dung cho may va GitHub Actions).

Chay bang Python cua studio/.venv (co Flask, yaml). Tu chdir ve claude-workspace
nen goi tu dau cung duoc. Moi test la mot subprocess `sys.executable <file>`,
cwd theo ghi chu dau file test, han 300 giay.
"""
import glob
import os
import subprocess
import sys
import time
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
TIMEOUT = 300

# Test bo qua co chu y:
# - studio/tests/test_quote.py: kiem tra file 3MF that do Bambu Studio cat lop
#   (maker/pushrod-arm/print/plates/...), file nam trong .gitignore va doi so
#   moi lan cat lop -> khong on dinh tren may, khong co trong CI.
STUDIO_TESTS = [
    "studio/tests/test_quote_bulk.py",
    "studio/tests/test_quote_model_extras.py",
    "studio/tests/test_org_board.py",
    "studio/tests/test_library_pages.py",
    "studio/tests/test_pinout.py",
    "studio/tests/test_ops.py",
]


def build_tests():
    """Tra ve [(ten, script, args_them, cwd_tuong_doi)]. Goi sau khi da chdir."""
    tests = [
        ("tools/git-hooks/pre_commit.py --all", "tools/git-hooks/pre_commit.py", ["--all"], "."),
        ("tools/git-hooks/tests/test_pre_commit.py", "tools/git-hooks/tests/test_pre_commit.py", [], "."),
        ("tools/backup/tests/test_backup.py", "tools/backup/tests/test_backup.py", [], "."),
    ]
    for path in sorted(glob.glob("tools/org/tests/*.py")):
        cwd = "." if os.path.basename(path) == "test_events.py" else "tools/org"
        tests.append((path, path, [], cwd))
    for path in sorted(glob.glob("tools/delegate/tests/test_*.py")):
        tests.append((path, path, [], "tools/delegate"))
    for path in STUDIO_TESTS:
        tests.append((path, path, [], "studio"))
    return tests


def run_one(name, script, extra, cwd):
    cmd = [sys.executable, str(WS / script), *extra]
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd, cwd=str(WS / cwd), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=TIMEOUT,
        )
        ok = proc.returncode == 0
        output = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        ok = False
        output = "TIMEOUT sau %d giay" % TIMEOUT
    seconds = time.perf_counter() - start
    print("%s %s %.2fs" % ("PASS" if ok else "FAIL", name, seconds), flush=True)
    if not ok and output.strip():
        print(output.rstrip(), flush=True)
        if os.environ.get("GITHUB_ACTIONS"):
            # log job can dang nhap moi doc duoc; annotation thi cong khai -> dua 8 dong cuoi len annotation
            tail = output.strip().splitlines()[-8:]
            print("::error title=FAIL %s::%s" % (name, "%0A".join(tail)), flush=True)
    return ok


def main(argv):
    os.chdir(WS)
    # ruff cai trong venv (CI) khong nam tren PATH -> them thu muc Scripts cua python nay de hook khong bo qua ruff
    os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")
    # runner Windows dung cp1252: test in/doc tieng Viet se loi -> ep UTF-8 cho moi test con
    os.environ["PYTHONUTF8"] = "1"
    tests = build_tests()
    if "--list" in argv:
        for name, _script, _extra, _cwd in tests:
            print(name)
        return 0

    passed = 0
    failed = 0
    for name, script, extra, cwd in tests:
        if run_one(name, script, extra, cwd):
            passed += 1
        else:
            failed += 1

    print("TONG: %d PASS, %d FAIL" % (passed, failed), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
