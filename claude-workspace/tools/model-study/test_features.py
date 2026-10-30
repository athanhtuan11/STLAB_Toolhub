# Gate cho measure_features.py (Claude viet 2026-10-30, executor KHONG sua file nay).
#   .venv\Scripts\python.exe test_features.py        (chay trong tools/model-study, moi truong uv)
# Dung chi tiet mau bang trimesh + manifold3d voi kich thuoc BIET TRUOC, roi kiem measure_features do lai dung:
# lo/boss theo truc BAT KY, lo xuyen/lo kin, lo bac (counterbore), cung tru khong tron (arc) khong bi tinh la lo.
import json, os, shutil, subprocess, sys, time
import numpy as np
import trimesh
from trimesh.creation import box, cylinder
from trimesh.transformations import rotation_matrix, translation_matrix, random_rotation_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_out", "_features_test")
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
sys.path.insert(0, HERE)
import measure_features as mf  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def cyl(d, z0, z1, x=0.0, y=0.0, sections=96, R=None):
    """Tru duong kinh d, truc z tu z0 toi z1, tam (x, y); R = ma tran quay quanh tam (x, y, giua) neu co."""
    c = cylinder(radius=d / 2, height=z1 - z0, sections=sections)
    c.apply_translation([0, 0, (z0 + z1) / 2])
    if R is not None:
        c.apply_transform(R)
    c.apply_translation([x, y, 0])
    return c


# Tam 40 x 40 x 6 mm, z = -3..3
part = box(extents=[40, 40, 6])
TILT = rotation_matrix(np.radians(30), [1, 0, 0])
cutters = [
    cyl(3.2, -10, 10, 10, 10),                    # A: lo xuyen O3.2 truc z
    cyl(5.0, -15, 15, -10, -10, R=TILT),          # B: lo xuyen O5.0 nghieng 30 do quanh x
    cyl(3.4, -10, 10, -10, 10),                   # D: lo bac: O3.4 xuyen ...
    cyl(6.0, 0, 10, -10, 10),                     #    ... + O6.0 sau 3 mm tu mat tren
    cyl(4.0, -1, 10, 0, 0),                       # E: lo kin O4.0 sau 4 mm (z -1..3)
    cyl(10.0, -10, 10, 20, 0),                    # F: khuyet nua tru R5 o mep x = 20 -> arc, KHONG phai lo
    cyl(3.0, -10, 10, 10, -2, sections=24),       # G: lo O3.0 luoi tho 24 canh
]
for c in cutters:
    part = part.difference(c, engine="manifold")
part = part.union(cyl(8.0, 3, 8, 10, -12), engine="manifold")   # C: boss O8 cao 5 mm tren mat tren
check(part.is_watertight, "chi tiet mau phai kin")

EXPECT = [  # (ten, loai, d, truc, diem tren truc, through|None, length|None, tol_d)
    ("A", "hole", 3.2, [0, 0, 1], [10, 10, 0], True, 6.0, 0.05),
    ("B", "hole", 5.0, list(TILT[:3, 2]), [-10, -10, 0], True, None, 0.05),
    ("D1", "hole", 3.4, [0, 0, 1], [-10, 10, -1.5], True, 3.0, 0.05),
    ("D2", "hole", 6.0, [0, 0, 1], [-10, 10, 1.5], False, 3.0, 0.05),
    ("E", "hole", 4.0, [0, 0, 1], [0, 0, 1], False, 4.0, 0.05),
    ("G", "hole", 3.0, [0, 0, 1], [10, -2, 0], True, 6.0, 0.08),
    ("C", "boss", 8.0, [0, 0, 1], [10, -12, 5.5], None, 5.0, 0.05),
]


def line_dist(p, c, u):
    v = np.asarray(p, float) - np.asarray(c, float)
    u = np.asarray(u, float) / np.linalg.norm(u)
    return float(np.linalg.norm(v - v.dot(u) * u))


def find(feats, kind, d, axis, pt, tol):
    best = None
    for f in feats:
        if f.get("type") != kind or abs(f["d_mm"] - d) > tol:
            continue
        if abs(abs(np.dot(np.asarray(f["axis"]) / np.linalg.norm(f["axis"]), axis / np.linalg.norm(axis)))) < np.cos(np.radians(1)):
            continue
        dist = line_dist(pt, f["center"], f["axis"])
        if dist <= 0.1 and (best is None or dist < best[0]):
            best = (dist, f)
    return best[1] if best else None


def verify(res, T, tag):
    """T = bien doi da ap len chi tiet; tinh lai truc + diem ky vong."""
    feats = res.get("features") or []
    for f in feats:
        for k in ("type", "d_mm", "axis", "center", "length_mm", "coverage_deg", "rms_mm", "confidence"):
            check(k in f, f"{tag}: feature thieu khoa {k}: {f}")
        if "confidence" in f:
            check(0 <= f["confidence"] <= 1, f"{tag}: confidence ngoai [0,1]: {f}")
        if f.get("type") == "hole":
            check(isinstance(f.get("through"), bool), f"{tag}: lo phai co through bool: {f}")
    got = {}
    for name, kind, d, ax, pt, through, length, tol in EXPECT:
        axw = T[:3, :3] @ np.asarray(ax, float)
        ptw = (T @ np.append(pt, 1))[:3]
        f = find(feats, kind, d, axw, ptw, tol)
        check(f is not None, f"{tag}: khong tim thay {name} ({kind} O{d})")
        if f is None:
            continue
        got[name] = f
        if through is not None:
            check(f.get("through") is through, f"{tag}: {name} through={f.get('through')} (mong {through})")
        if length is not None:
            check(abs(f["length_mm"] - length) <= 0.1, f"{tag}: {name} length {f['length_mm']} (mong {length})")
        check(f["coverage_deg"] >= 300, f"{tag}: {name} coverage {f['coverage_deg']} < 300")
    full = [f for f in feats if f.get("type") in ("hole", "boss")]
    check(len(full) == len(EXPECT), f"{tag}: so lo+boss = {len(full)}, mong {len(EXPECT)}: "
          + str([(f['type'], round(f['d_mm'], 2)) for f in full]))
    arcs = [f for f in feats if f.get("type") == "arc" and abs(f["d_mm"] - 10.0) <= 0.1]
    check(len(arcs) == 1 and 150 <= arcs[0]["coverage_deg"] <= 210,
          f"{tag}: khuyet nua tru R5 phai la 1 'arc' ~180 do: {[(f['type'], f['d_mm'], f['coverage_deg']) for f in feats if abs(f['d_mm'] - 10) < .5]}")
    groups = res.get("groups") or []
    cb = [g for g in groups if g.get("type") == "counterbore"]
    ok = False
    if "D1" in got and "D2" in got:
        ids = {got["D1"].get("id"), got["D2"].get("id")}
        ok = any(set(g.get("members", [])) == ids and abs(g.get("depth_mm", -1) - 3.0) <= 0.1 for g in cb)
    check(ok, f"{tag}: lo bac D phai thanh group counterbore (members 2 id, depth_mm 3.0): {cb}")


# 1) API trong Python
t0 = time.time()
res = mf.measure_mesh(part)
verify(res, np.eye(4), "goc")
check(res.get("units") == "mm", "units = mm")

# 2) Quay + doi cho ngau nhien: ket qua khong doi (truc bat ky)
np.random.seed(7)
T = translation_matrix([13.0, -7.0, 21.0]) @ random_rotation_matrix(np.random.rand(3))
moved = part.copy()
moved.apply_transform(T)
verify(mf.measure_mesh(moved), T, "quay")
elapsed = time.time() - t0
check(elapsed < 60, f"2 lan do mat {elapsed:.1f} s (> 60 s)")

# 3) CLI: STL -> JSON; nhieu file -> 1 JSON danh sach
stl = os.path.join(OUT, "plate.stl")
part.export(stl)
stl2 = os.path.join(OUT, "moved.stl")
moved.export(stl2)
js = os.path.join(OUT, "plate.json")
r = subprocess.run([sys.executable, os.path.join(HERE, "measure_features.py"), stl, "--json", js],
                   capture_output=True, text=True, encoding="utf-8")
check(r.returncode == 0, f"CLI 1 file loi: {r.stderr[-400:]}")
if os.path.exists(js):
    j = json.load(open(js, encoding="utf-8"))
    check(os.path.basename(j.get("file", "")) == "plate.stl", f"JSON co 'file': {j.get('file')}")
    verify(j, np.eye(4), "cli")
js2 = os.path.join(OUT, "all.json")
r = subprocess.run([sys.executable, os.path.join(HERE, "measure_features.py"), stl, stl2, "--json", js2],
                   capture_output=True, text=True, encoding="utf-8")
check(r.returncode == 0 and os.path.exists(js2), f"CLI nhieu file loi: {r.stderr[-400:]}")
if os.path.exists(js2):
    j2 = json.load(open(js2, encoding="utf-8"))
    check(isinstance(j2, list) and len(j2) == 2, "nhieu file -> JSON la danh sach 2 phan tu")
r = subprocess.run([sys.executable, os.path.join(HERE, "measure_features.py"), os.path.join(OUT, "khong-co.stl"),
                    "--json", os.path.join(OUT, "x.json")], capture_output=True, text=True, encoding="utf-8")
check(r.returncode != 0, "file khong ton tai -> exit khac 0")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"PASS test_features ({elapsed:.1f} s)")
