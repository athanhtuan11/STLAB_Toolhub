# Gate "han muc theo nguon" (Claude viet 2026-10-30, executor KHONG sua): agent-stats.json ghi them MOC THOI GIAN
# moi executor (last_run / last_pass / last_limited) lay tu ten run_dir "YYYYMMDD-HHMMSS-<task>".
#   python tests/test_stats_time.py      (chay tu tools/delegate)
import importlib.util, json, os, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("delegate", os.path.join(HERE, "..", "delegate.py"))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
TMP = tempfile.mkdtemp(prefix="delegate-stats-time-")
d.USAGE = TMP


def R(run, verdict, *rounds):
    return dict(task="t", verdict=verdict, run_dir=os.path.join(TMP, "delegate-runs", run),
                rounds=[dict(zip(("executor", "gate_exit", "seconds", "limited"), x)) for x in rounds])


runs = [
    R("20261029-080000-a", "PASS", ("codex", 0, 10, False)),
    R("20261030-091500-b", "FAIL", ("codex", 1, 20, False)),
    R("20261030-100422-c", "PASS", ("codex", None, 1, True), ("opencode", 0, 9, False)),
    R("20261028-070000-d", "PASS", ("opencode", 0, 5, False)),            # cu hon -> khong de moc moi hon
]
for r in runs:
    d.update_stats(r)
s = d.load_stats()
c, o = s["codex"], s["opencode"]
assert c.get("last_run") == "2026-10-30T10:04", c          # vong bi han muc van tinh la lan goi gan nhat
assert c.get("last_pass") == "2026-10-29T08:00", c
assert c.get("last_limited") == "2026-10-30T10:04", c
assert o.get("last_run") == "2026-10-30T10:04" and o.get("last_pass") == "2026-10-30T10:04", o
assert "last_limited" not in o, o
assert (c["rounds"], c["gate_pass"], c["limited"]) == (2, 1, 1), c   # dem cu khong doi

# run khong co run_dir / ten sai -> khong loi, khong ghi moc
d.update_stats(dict(task="t", verdict="PASS", rounds=[dict(executor="kilo", gate_exit=0, seconds=3)]))
d.update_stats(dict(task="t", verdict="PASS", run_dir="x/khong-dung-dang", rounds=[dict(executor="kilo", gate_exit=0)]))
k = d.load_stats()["kilo"]
assert k["rounds"] == 2 and "last_run" not in k, k

# rebuild_stats cho cung ket qua moc
root = os.path.join(TMP, "delegate-runs")
for r in runs:
    os.makedirs(r["run_dir"], exist_ok=True)
    json.dump(r, open(os.path.join(r["run_dir"], "result.json"), "w"))
d.rebuild_stats()
s2 = d.load_stats()
for name in ("codex", "opencode"):
    for f in ("last_run", "last_pass", "last_limited"):
        assert s2[name].get(f) == s[name].get(f), (name, f, s2[name], s[name])
print("PASS test_stats_time")
