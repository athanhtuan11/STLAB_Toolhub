# Gate cho measure_holes.py – Claude viet, executor KHONG sua file nay.
#   python test_holes.py
import csv, json, os, shutil, struct, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_out", "_holes_test")
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
N = 96


def ring(cx, cy, r, z):
    a = np.linspace(0, 2 * np.pi, N, endpoint=False)
    return np.column_stack((cx + r * np.cos(a), cy + r * np.sin(a), np.full(N, z)))


def square(cx, cy, h, z):
    """N diem tren bien hinh vuong canh 2h, cung goc voi ring (de noi dai voi vong tron)."""
    a = np.linspace(0, 2 * np.pi, N, endpoint=False)
    c, s = np.cos(a), np.sin(a)
    k = h / np.maximum(np.abs(c), np.abs(s))
    return np.column_stack((cx + k * c, cy + k * s, np.full(N, z)))


def strip(p, q, flip=False):
    t = []
    for i in range(N):
        j = (i + 1) % N
        f = [[p[i], p[j], q[j]], [p[i], q[j], q[i]]]
        t += [x[::-1] for x in f] if flip else f
    return t


def cap(c, ring_pts, up):
    t = []
    for i in range(N):
        j = (i + 1) % N
        t.append([c, ring_pts[i], ring_pts[j]] if up else [c, ring_pts[j], ring_pts[i]])
    return t


def tube(outer_lo, outer_hi, inner_lo, inner_hi):
    return (strip(outer_lo, outer_hi) + strip(inner_lo, inner_hi, flip=True)
            + strip(outer_hi, inner_hi) + strip(inner_lo, outer_lo))


def pin(cx, cy, r, z0, z1):
    lo, hi = ring(cx, cy, r, z0), ring(cx, cy, r, z1)
    return strip(lo, hi) + cap([cx, cy, z1], hi, True) + cap([cx, cy, z0], lo, False)


tris = []
# khoi vuong 20x20x6 tai (20,0) co lo xuyen D6,10
tris += tube(square(20, 0, 10, 0), square(20, 0, 10, 6), ring(20, 0, 3.05, 0), ring(20, 0, 3.05, 6))
# ong D10 / lo D5,70 cao 8 tai goc
tris += tube(ring(0, 0, 5.0, 0), ring(0, 0, 5.0, 8), ring(0, 0, 2.85, 0), ring(0, 0, 2.85, 8))
# chot dung D3,00 cao 5 tai (-15,0)
tris += pin(-15, 0, 1.5, 0, 5)
# chot nam ngang D2,40 dai 12, truc X, tam (0,15,3): quay chot truc z -> truc x
h = np.array(pin(0, 0, 1.2, -6, 6), float)
h = h[:, :, [2, 1, 0]]  # hoan x<->z (phep doi xung -> dao thu tu dinh)
h = h[:, ::-1, :] + [0, 15, 3]
tris += list(h)
tris = np.array(tris, float)

stl = os.path.join(OUT, "fixture.stl")
with open(stl, "wb") as f:
    f.write(b"\0" * 80 + struct.pack("<I", len(tris)))
    for t in tris:
        nrm = np.cross(t[1] - t[0], t[2] - t[0])
        nrm = nrm / (np.linalg.norm(nrm) or 1)
        f.write(struct.pack("<12fH", *nrm, *t.ravel(), 0))

r = subprocess.run([sys.executable, os.path.join(HERE, "measure_holes.py"), stl, "--json", os.path.join(OUT, "f.json")],
                   capture_output=True, text=True)
print(r.stdout[-2000:], r.stderr[-2000:])
assert r.returncode == 0, "measure_holes.py exit != 0"
feats = json.load(open(os.path.join(OUT, "f.json"), encoding="utf-8"))["features"]


def find(kind, axis, d, c):
    for ft in feats:
        if ft["type"] == kind and ft["axis"] == axis and abs(ft["d_mm"] - d) <= 0.03 \
                and np.hypot(*(np.array(ft["center"]) - c)) <= 0.1:
            return ft
    return None


exp = [("hole", "z", 6.10, (20, 0), (0, 6)), ("hole", "z", 5.70, (0, 0), (0, 8)), ("boss", "z", 10.00, (0, 0), (0, 8)),
       ("boss", "z", 3.00, (-15, 0), (0, 5)), ("boss", "x", 2.40, (15, 3), (-6, 6))]
for kind, axis, d, c, (a0, a1) in exp:
    ft = find(kind, axis, d, c)
    assert ft, f"khong thay {kind} {axis} D{d} tai {c}: {feats}"
    assert ft["from_mm"] <= a0 + 0.6 and ft["to_mm"] >= a1 - 0.6, f"doan truc sai {ft}"
# canh vuong 20x20 khong duoc coi la tron
assert not any(abs(ft["d_mm"] - 20) < 2 for ft in feats), "nhan nham hinh vuong la tron"

# chay hang loat tren 33 chi tiet that (can _out/arm tu test_study.py)
parts = os.path.join(HERE, "_out", "arm", "parts")
assert os.path.isdir(parts), "chay python test_study.py truoc"
t = time.time()
r = subprocess.run([sys.executable, os.path.join(HERE, "measure_holes.py"), parts, "--csv",
                    os.path.join(HERE, "_out", "arm", "holes.csv")], capture_output=True, text=True)
dt = time.time() - t
print(r.stdout[-1500:], r.stderr[-1500:], "batch %.0f s" % dt)
assert r.returncode == 0 and dt < 240, "batch loi hoac qua 240 s"
rows = list(csv.DictReader(open(os.path.join(HERE, "_out", "arm", "holes.csv"), encoding="utf-8")))
need = {"file", "type", "axis", "d_mm", "center_a", "center_b", "from_mm", "to_mm", "length_mm"}
assert rows and need <= set(rows[0]), f"holes.csv thieu cot {need - set(rows[0]) if rows else 'rong'}"
assert len({r['file'] for r in rows}) >= 15, "qua it chi tiet co lo/truc tron"
print("gate holes OK", len(rows), "features")
