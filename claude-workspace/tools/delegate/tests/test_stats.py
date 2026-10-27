# Gate buoc 3 so nhan su: thong ke thanh tich executor (Claude viet, executor KHONG sua).
#   python tests/test_stats.py      (chay tu tools/delegate)
import importlib.util, inspect, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "delegate.py")
spec = importlib.util.spec_from_file_location("delegate", SRC)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
TMP = tempfile.mkdtemp(prefix="delegate-stats-test-")
d.USAGE = TMP


def R(verdict, *rounds):
    return dict(task="t", verdict=verdict, rounds=[dict(zip(("executor", "gate_exit", "seconds", "limited"), x))
                                                   for x in rounds])


runs = [
    R("PASS", ("codex", 0, 10, False)),                                   # codex dat ngay vong 1
    R("FAIL", ("codex", 1, 20, False), ("codex", 1, 30, False)),          # codex 2 vong deu truot
    R("PASS", ("opencode", 1, 5, False), ("opencode", 0, 7, False)),      # opencode dat vong 2
    R("PASS", ("codex", None, 1, True), ("opencode", 0, 9, False)),       # codex het han muc -> opencode dat
    R("ESCALATE", ("opencode", None, 3, False)),                          # opencode bao len tren
]
for r in runs:
    d.update_stats(r)
s = d.load_stats()
c, o = s["codex"], s["opencode"]
assert (c["rounds"], c["gate_pass"], c["pass_round1"], c["limited"], c["seconds"]) == (3, 1, 1, 1, 60), c
assert (o["rounds"], o["gate_pass"], o["pass_round1"], o["escalate"], o["seconds"]) == (4, 2, 0, 1, 24), o
assert "update_stats(" in inspect.getsource(d.run_task), "run_task phai goi update_stats sau moi run"

# rebuild tu result.json trong delegate-runs: idempotent, = cong don
root = os.path.join(TMP, "delegate-runs")
for i, r in enumerate(runs):
    os.makedirs(os.path.join(root, f"r{i}"))
    json.dump(r, open(os.path.join(root, f"r{i}", "result.json"), "w"))
for _ in range(2):
    d.rebuild_stats()
    assert d.load_stats()["codex"] == c and d.load_stats()["opencode"] == o, "rebuild phai ra dung so lieu, chay lai khong cong don"

# xep hang khi spec uu_tien: thanh-tich: ty le gate_pass/rounds giam dan, < 3 vong xep sau, giu thu tu goc khi bang
st = {"codex": dict(rounds=10, gate_pass=5), "opencode": dict(rounds=10, gate_pass=9), "agy": dict(rounds=1, gate_pass=1)}
assert d.rank_by_stats(["codex", "opencode", "agy"], st) == ["opencode", "codex", "agy"]
assert d.rank_by_stats(["codex", "agy"], {}) == ["codex", "agy"]

# CLI --stats in JSON co ty le
r = subprocess.run([sys.executable, SRC, "--stats"], capture_output=True, text=True, encoding="utf-8",
                   env=dict(os.environ, LOCALAPPDATA=TMP))
assert r.returncode == 0, r.stderr[-500:]
out = json.loads(r.stdout)
assert abs(out["opencode"]["pass_rate"] - 0.5) < 1e-9, out
shutil.rmtree(TMP, ignore_errors=True)
print("gate OK")
