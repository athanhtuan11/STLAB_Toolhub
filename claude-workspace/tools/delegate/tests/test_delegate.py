# Gate cho 3 cai tien delegate.py (Claude viet, executor KHONG sua file nay). Khong goi executor that.
#   python tests/test_delegate.py      (chay tu tools/delegate)
import importlib.util, inspect, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "delegate.py")
spec = importlib.util.spec_from_file_location("delegate", SRC)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

tmp = tempfile.mkdtemp(prefix="delegate-test-")
d.USAGE = tmp
runs = os.path.join(tmp, "delegate-runs")
os.makedirs(os.path.join(tmp, "locks"))


def mk_run(name, state=None, files=None):
    rd = os.path.join(runs, name)
    os.makedirs(rd)
    if state is not None:
        json.dump(state, open(os.path.join(rd, "state.json"), "w"))
    for f, t in (files or {}).items():
        open(os.path.join(rd, f), "w", encoding="utf-8").write(t)
    return rd


# 1) --status xet ca file khoa: run cu KHONG co state.json nhung pid trong khoa con song -> "running"
rd_old = mk_run("20260101-000000-old-alive")
json.dump(dict(pid=os.getpid(), task="old-alive", start="x", run_dir=rd_old),
          open(os.path.join(tmp, "locks", "tools_x.json"), "w"))
mk_run("20260101-000001-dead")                                   # khong state, khong khoa -> interrupted
st = {r["run"]: r["state"] for r in d.run_states()}
assert st.get("20260101-000000-old-alive") == "running", f"run con song (theo khoa) bi bao sai: {st}"
assert st.get("20260101-000001-dead") == "interrupted", st

# 2) resume: build_resume(run_dir) -> (spec_path, context) ; context chua duoi log executor + gate vong truoc
spec_path = os.path.join(HERE, "..", "selftest", "spec.md")
rd_cut = mk_run("20260101-000002-cut", state=dict(state="running", pid=999999, spec=os.path.abspath(spec_path)),
                files={"prompt-1.txt": "P", "codex-1.log": "...\nLASTLOG-MARK", "gate-1.log": "GATEFAIL-MARK"})
sp, ctx = d.build_resume(rd_cut)
assert os.path.samefile(sp, spec_path), sp
assert "LASTLOG-MARK" in ctx and "GATEFAIL-MARK" in ctx, "context resume phai co duoi log executor va gate"
rd_done = mk_run("20260101-000003-done", state=dict(state="running", pid=999999, spec=os.path.abspath(spec_path)),
                 files={"result.json": "{}"})
try:
    d.build_resume(rd_done)
    raise AssertionError("run da co result.json phai bi tu choi resume")
except (ValueError, SystemExit):
    pass
assert "--resume" in open(SRC, encoding="utf-8").read(), "thieu tuy chon CLI --resume"
r = subprocess.run([sys.executable, SRC, "--resume", "khong-ton-tai-xyz"], capture_output=True, text=True,
                   env=dict(os.environ, LOCALAPPDATA=tmp))
assert r.returncode != 0, "--resume run khong ton tai phai exit != 0"

# 3) handoff.md khi FAIL
rd_fail = mk_run("20260101-000004-fail")
res = dict(task="t-fail", verdict="FAIL", passed=False, changed=["tools/x/a.py"], forbidden_touched=[],
           outside_allow=[], rounds=[dict(round=1, executor="opencode", exit=0, seconds=5, last_line="BLOCKED: thieu so",
                                         gate_exit=1, gate_tail="AssertionError: GATE-TAIL-MARK")])
d.write_handoff(rd_fail, res)
h = open(os.path.join(rd_fail, "handoff.md"), encoding="utf-8").read()
for must in ("t-fail", "FAIL", "opencode", "GATE-TAIL-MARK", "BLOCKED: thieu so", "tools/x/a.py"):
    assert must in h, f"handoff.md thieu '{must}'"
assert "write_handoff(" in inspect.getsource(d.run_task), "run_task phai goi write_handoff khi khong PASS"

subprocess.run([sys.executable, "-m", "py_compile", SRC], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print("gate OK")
