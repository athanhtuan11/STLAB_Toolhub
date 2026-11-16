"""Gate: trinh thong dich firmware (main/prog.c) cho dung ket qua protocol/golden.json.

Bien dich prog.c + tests/run_golden.c + cJSON cua ESP-IDF tren may tinh bang zig (pip ziglang trong ../.venv-host).
run_golden.exe <file.json>  -> in 1 dong JSON: {"ok":true,"steps":[[id,"op",arg],...]} | {"ok":false,"code":"..."}
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

CAR = Path(__file__).resolve().parents[1]
GOLDEN = CAR.parents[1] / "protocol" / "golden.json"
CJSON = Path(r"C:\Espressif\frameworks\esp-idf-v5.5.4\components\json\cJSON")
OUT = CAR / ".host-build"
EXE = OUT / "run_golden.exe"


@pytest.fixture(scope="module")
def runner():
    OUT.mkdir(exist_ok=True)
    if EXE.exists():
        EXE.unlink()
    src = [CAR / "main" / "prog.c", CAR / "tests" / "run_golden.c", CJSON / "cJSON.c"]
    for s in src:
        assert s.exists(), f"thieu {s}"
    cmd = [sys.executable, "-m", "ziglang", "cc", "-std=c11", "-O1", "-Wall", "-Werror",
           "-Wno-unused-function", "-DPROG_HOST_TEST=1",
           f"-I{CAR / 'main'}", f"-I{CJSON}", *map(str, src), "-o", str(EXE)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, "bien dich loi:\n" + r.stderr[-3000:]
    return EXE


def cases():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", cases(), ids=lambda c: c["name"])
def test_case(runner, case, tmp_path):
    f = tmp_path / "doc.json"
    f.write_text(json.dumps(case["doc"]), encoding="utf-8")
    r = subprocess.run([str(runner), str(f)], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, r.stderr
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    assert len(lines) == 1, f"can dung 1 dong JSON, nhan: {r.stdout!r}"
    got = json.loads(lines[0])
    if case["ok"]:
        assert got == {"ok": True, "steps": case["steps"]}
    else:
        assert got == {"ok": False, "code": case["code"]}


def test_bad_json_text(runner, tmp_path):
    f = tmp_path / "x.json"
    f.write_text("{\"v\":1,\"prog\":[", encoding="utf-8")
    r = subprocess.run([str(runner), str(f)], capture_output=True, text=True, timeout=10)
    assert json.loads(r.stdout.strip()) == {"ok": False, "code": "bad_json"}


def test_golden_fresh():
    r = subprocess.run([sys.executable, str(GOLDEN.parent / "make_golden.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
