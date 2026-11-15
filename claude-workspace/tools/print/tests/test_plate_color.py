# Gate MAU BAN IN THEO THIET KE (Claude viet 2026-11-15, executor KHONG sua).
# Tuan 2026-11-15: "cac mau tu thiet ke in 3D nhu cu nhoi bong tu set mau cho ban in de giong voi thiet ke 3D nhat co the.
# toi khong can set mau lai tranh sai lech". Truoc: moi ban in 3MF mang mau mac dinh profile (#00AE42 xanh la).
# Chay: "C:\Program Files\FreeCAD 1.1\bin\python.exe" tools\print\tests\test_plate_color.py
# Can Bambu Studio CLI (cat lop that 1 khoi 10 mm, ~1 phut).
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
fails = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg, flush=True)
    if not cond:
        fails.append(msg)


def cube(path, s=10.0, x0=0.0):
    v = [(x0 + a * s, b * s, c * s) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    f = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    out = ["solid c"]
    for q in f:
        for tri in ((q[0], q[1], q[2]), (q[0], q[2], q[3])):
            out += ["facet normal 0 0 0", " outer loop"] + [" vertex %g %g %g" % v[i] for i in tri] + [" endloop", "endfacet"]
    out.append("endsolid c")
    path.write_text("\n".join(out), encoding="ascii")


# ---------- A. ham chon mau (slice.mau_ban) ----------
try:
    import slice as sl
    mau_ban = sl.mau_ban
except Exception as e:  # noqa: BLE001
    mau_ban = None
    ok(False, "slice.py co ham mau_ban(cfg, ten_ban, b, stl_ban, stl_dir) (%s)" % e)

if mau_ban:
    d = Path(tempfile.mkdtemp(prefix="stlab-color-"))
    (d / "colors.json").write_text(json.dumps({"a.stl": "#F6BE9A", "b.stl": "#f6be9a", "c.stl": "#FFC857"}), encoding="utf-8")
    A, B, C, Z = d / "a.stl", d / "b.stl", d / "c.stl", d / "z.stl"
    ok(mau_ban({}, "P", {"color": "#FFF3DF"}, [A, C], d) == "#FFF3DF", "color khai trong ban thang colors.json")
    ok(mau_ban({}, "P", {}, [A, B], d) == "#F6BE9A", "colors.json: cac STL cung mau -> mau do (chuan hoa HOA)")
    ok(mau_ban({}, "P", {}, [Z], d) is None, "STL khong co trong colors.json, ban khong khai -> None (giu profile, bao WARN)")
    try:
        mau_ban({}, "P", {}, [A, C], d)
        ok(False, "1 ban 2 mau phai ValueError")
    except ValueError as e:
        ok("tách" in str(e) or "tach" in str(e), "1 ban 2 mau -> ValueError bao tach ban theo mau")
    for bad in ("F6BE9A", "#F6BE9", "red", "#GGGGGG"):
        try:
            mau_ban({}, "P", {"color": bad}, [A], d)
            ok(False, "mau sai '%s' phai ValueError" % bad)
        except ValueError:
            ok(True, "mau sai '%s' -> ValueError" % bad)
    ok(mau_ban({"colors": {"z.stl": "#6B6F78"}}, "P", {}, [Z], d) == "#6B6F78", "print.yaml 'colors' (cap du an) theo ten STL")
    ok(mau_ban({"colors": {"a.stl": "#000000"}}, "P", {}, [A], d) == "#000000", "print.yaml 'colors' thang colors.json")

# ---------- B. cat lop that: 3MF mang dung mau ----------
if mau_ban:
    p = Path(tempfile.mkdtemp(prefix="stlab-color-run-"))
    (p / "stl").mkdir()
    cube(p / "stl" / "peach.stl")
    cube(p / "stl" / "butter.stl")
    (p / "stl" / "colors.json").write_text(json.dumps({"peach.stl": "#F6BE9A"}), encoding="utf-8")
    (p / "print.yaml").write_text(
        "machine: Bambu Lab A1 0.4 nozzle\nfilament: Bambu PETG Basic @BBL A1\nstl: stl\nplates_dir: plates\n"
        "plates:\n  p1-peach: {process: 0.20mm Standard @BBL A1, stl: [peach.stl]}\n"
        "  p2-butter: {process: 0.20mm Standard @BBL A1, color: '#FFC857', stl: [butter.stl]}\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPTS / "slice.py"), str(p / "print.yaml")], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    ok(r.returncode in (0, 1), "slice.py chay xong (exit %s)" % r.returncode)
    if r.returncode not in (0, 1):
        print((r.stdout or "")[-1500:], (r.stderr or "")[-1500:])
    for ban, mau in (("p1-peach", "#F6BE9A"), ("p2-butter", "#FFC857")):
        f = p / "plates" / ban / (ban + ".3mf")
        if not f.exists():
            ok(False, "%s.3mf duoc tao" % ban)
            continue
        cfg = json.loads(zipfile.ZipFile(f).read("Metadata/project_settings.config"))
        got = [str(x).upper() for x in cfg.get("filament_colour", [])]
        ok(got[:1] == [mau], "%s.3mf filament_colour = %s (co %s)" % (ban, mau, got))
    rep = p / "plates" / "print-report.json"
    if rep.exists():
        js = json.loads(rep.read_text(encoding="utf-8"))
        txt = json.dumps(js, ensure_ascii=False)
        ok("#F6BE9A" in txt.upper() and "#FFC857" in txt.upper(), "print-report.json ghi mau tung ban")
    else:
        ok(False, "co print-report.json")

    # 1 ban 2 mau -> slice.py bao loi ro, khong cat
    (p / "stl" / "colors.json").write_text(json.dumps({"peach.stl": "#F6BE9A", "butter.stl": "#FFC857"}), encoding="utf-8")
    (p / "print2.yaml").write_text(
        "machine: Bambu Lab A1 0.4 nozzle\nfilament: Bambu PETG Basic @BBL A1\nstl: stl\nplates_dir: plates2\n"
        "plates:\n  p1-mix: {process: 0.20mm Standard @BBL A1, stl: [peach.stl, butter.stl]}\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SCRIPTS / "slice.py"), str(p / "print2.yaml")], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    out = (r.stdout or "") + (r.stderr or "")
    ok(r.returncode != 0 and ("tách" in out or "tach" in out), "ban tron 2 mau -> slice.py exit != 0, bao tach ban")

# ---------- C. du an mau: Cu Bong S3 co colors.json ----------
WS = HERE.parent.parent.parent
cj = WS / "maker" / "english-teacher" / "print" / "stl-s3" / "colors.json"
ok(cj.exists(), "maker/english-teacher/print/stl-s3/colors.json ton tai")
if cj.exists():
    m = json.loads(cj.read_text(encoding="utf-8"))
    stls = {f.name for f in cj.parent.glob("*.stl")}
    ok(stls and stls <= set(m), "colors.json phu het STL Cu Bong S3 (thieu %s)" % sorted(stls - set(m)))

print("\n%s test_plate_color (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
