# Gate sao luu FCStd (Claude viet, executor KHONG sua). Chay tu claude-workspace:
#   python tools/backup/tests/test_backup.py
# Chi dung thu muc tam (bien STLAB_BACKUP_CONFIG + STLAB_BACKUP_STATE), khong dung o G:/OneDrive that.
import json, os, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "backup_fcstd.py"
TMP = Path(tempfile.mkdtemp(prefix="stlab-backup-test-"))
SRC = TMP / "ws"
D1, D2 = TMP / "dest1", TMP / "dest2"
MISSING = TMP / "khong-co-o" / "dest3"   # o rut ra: thu muc goc khong ton tai


def cfg(dests, keep=3):
    p = TMP / "backup.json"
    p.write_text(json.dumps({"source_root": str(SRC), "include": ["maker/**/*.FCStd"],
                             "destinations": [str(d) for d in dests], "keep_versions": keep}), encoding="utf-8")
    return p


def run(c):
    env = dict(os.environ, STLAB_BACKUP_CONFIG=str(c), STLAB_BACKUP_STATE=str(TMP / "state"), PYTHONUTF8="1")
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env, timeout=120)
    last = [l for l in r.stdout.strip().splitlines() if l.startswith("{")]
    assert last, f"khong co dong JSON cuoi\nstdout={r.stdout}\nstderr={r.stderr}"
    return r.returncode, json.loads(last[-1])


def write(rel, data):
    p = SRC / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


a = write("maker/du-an-a/freecad/a.FCStd", b"A1" * 1000)
write("maker/du-an-b/freecad/sub/b.FCStd", b"B1")
write("maker/du-an-a/freecad/khong-lay.FCBak", b"x")
write("maker/du-an-a/README.md", b"x")

# 1) lan dau: chep 2 file vao current/ cua ca 2 dich, giu duong dan tuong doi
code, j = run(cfg([D1, D2]))
assert code == 0, j
assert j["copied"] == 2 and j["unchanged"] == 0, j
for d in (D1, D2):
    assert (d / "current/maker/du-an-a/freecad/a.FCStd").read_bytes() == b"A1" * 1000
    assert (d / "current/maker/du-an-b/freecad/sub/b.FCStd").read_bytes() == b"B1"
    assert not list(d.rglob("*.FCBak")) and not list(d.rglob("README.md"))
    assert not (d / "versions").exists() or not list((d / "versions").rglob("*.FCStd"))
assert {x["path"]: x["status"] for x in j["destinations"]} == {str(D1): "ok", str(D2): "ok"}, j

# 2) chay lai khong doi gi -> khong chep
code, j = run(cfg([D1, D2]))
assert code == 0 and j["copied"] == 0 and j["unchanged"] == 2, j

# 3) sua a -> ban cu vao versions/, current la ban moi (cung kich thuoc van phai nhan ra: so sha256)
for k in range(5):
    a.write_bytes(f"A{k + 2}".encode() * 1000)   # cung kich thuoc voi ban truoc
    time.sleep(1.1)                              # ten version theo giay
    code, j = run(cfg([D1, D2]))
    assert code == 0 and j["copied"] == 1, j
for d in (D1, D2):
    assert (d / "current/maker/du-an-a/freecad/a.FCStd").read_bytes() == b"A6" * 1000
    vs = sorted((d / "versions/maker/du-an-a/freecad").glob("a.*.FCStd"))
    # keep_versions = 3: chi giu 3 ban cu moi nhat (A3, A4, A5)
    assert len(vs) == 3, vs
    assert [v.read_bytes()[:2] for v in vs] == [b"A3", b"A4", b"A5"], [v.name for v in vs]
assert "versions_pruned" in j, j

# 4) xoa file nguon -> KHONG xoa ban sao luu
(SRC / "maker/du-an-b/freecad/sub/b.FCStd").unlink()
code, j = run(cfg([D1, D2]))
assert code == 0, j
assert (D1 / "current/maker/du-an-b/freecad/sub/b.FCStd").exists()

# 5) mot dich mat (o USB rut ra) -> bo qua dich do, van chep dich con lai, exit 0
a.write_bytes(b"A7" * 1000)
code, j = run(cfg([MISSING, D1]))
assert code == 0, j
st = {x["path"]: x["status"] for x in j["destinations"]}
assert st[str(MISSING)] == "missing" and st[str(D1)] == "ok", st
assert not MISSING.parent.exists(), "khong duoc tu tao o/thu muc goc cua dich bi mat"
assert (D1 / "current/maker/du-an-a/freecad/a.FCStd").read_bytes() == b"A7" * 1000

# 6) moi dich deu mat -> exit 1
code, j = run(cfg([MISSING]))
assert code == 1, (code, j)

# 7) file trang thai cho Toolhub
last = json.loads((TMP / "state" / "last.json").read_text(encoding="utf-8"))
assert {"time", "copied", "unchanged", "destinations"} <= set(last), last

# 8) khong de lai file tam trong dich
for d in (D1, D2):
    assert not [p for p in d.rglob("*") if p.is_file() and (p.suffix in (".tmp", ".part") or p.name.startswith("."))]

print("test_backup PASS")
