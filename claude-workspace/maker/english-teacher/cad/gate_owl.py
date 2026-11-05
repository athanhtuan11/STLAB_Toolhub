# Gate CAD vo Cu Bong (Claude viet, executor KHONG sua).
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl.py -- out
import bpy, bmesh, json, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
fails = []
PARTS = ["shell-front", "shell-back", "belly", "beak", "button-cap", "eye-diffuser"]
BED = 250.0


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not path.exists():
        fails.append(f"{path.name}: khong co file")
        return None
    bpy.ops.wm.stl_import(filepath=str(path))
    bm = bmesh.new()
    bm.from_mesh(bpy.context.selected_objects[0].data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    return bm


def islands(bm):
    bm.faces.ensure_lookup_table()
    seen, n = set(), 0
    for f in bm.faces:
        if f.index in seen:
            continue
        n += 1
        st = [f]; seen.add(f.index)
        while st:
            x = st.pop()
            for e in x.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index); st.append(g)
    return n


p = json.loads((OUT / "owl-params.json").read_text(encoding="utf-8")) if (OUT / "owl-params.json").exists() else {}
if not p:
    fails.append("out/owl-params.json khong co")
for k, want in [("wall", 2.4), ("speaker_pocket_d", 52.6), ("grille_hole_d", 2.8), ("mic_hole_d", 2.0), ("m3_clear_d", 3.4),
                ("m3_nut_s", 5.8), ("button_cap_d", 50.0), ("button_hole_d", 50.8), ("diffuser_t", 0.8), ("vent_w", 2.0)]:
    v = p.get(k)
    if v is None or abs(float(v) - want) > 0.01:
        fails.append(f"params {k} = {v}, can {want}")

for name in PARTS:
    bm = load(OUT / f"{name}.stl")
    if not bm:
        continue
    bad = [e for e in bm.edges if not e.is_manifold]
    if bad:
        fails.append(f"{name}: {len(bad)} canh khong kin (non-manifold)")
    if islands(bm) != 1:
        fails.append(f"{name}: phai la 1 khoi ({islands(bm)})")
    zs = [v.co.z for v in bm.verts]; xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]
    if abs(min(zs)) > 0.05:
        fails.append(f"{name}: STL phai dat dung huong in, z min = 0 (dang {min(zs):.2f})")
    if max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)) > BED:
        fails.append(f"{name}: qua ban in {BED}")
    # dien tich mat day (z < 0.3) du lon de khong do khi in
    base = sum(f.calc_area() for f in bm.faces if all(v.co.z < 0.3 for v in f.verts) and f.normal.z < -0.9)
    print(f"{name}: kich thuoc {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} x {max(zs)-min(zs):.1f}, mat day {base:.0f} mm2")
    if base < 150:
        fails.append(f"{name}: mat day in {base:.0f} mm2 qua nho (< 150) – dat lai huong in")

# lap rap: kich thuoc tong + khoang loa / bo mach khong cham vo
bm = load(OUT / "owl-assembled.stl")
if bm:
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    W, D, H = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    print(f"lap rap: {W:.1f} x {D:.1f} x {H:.1f}")
    for lab, got, want in (("rong", W, 142), ("sau", D, 116), ("cao", H, 175)):
        if abs(got - want) > 6:
            fails.append(f"lap rap {lab} {got:.1f}, can ~{want} (+-6)")
    tree = BVHTree.FromBMesh(bm)

    def dummy(kind, c, size):
        b = bmesh.new()
        if kind == "box":
            bmesh.ops.create_cube(b, size=1.0)
            for v in b.verts:
                v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2])) + Vector(c)
        else:  # tru loa, truc theo size[2] = "x" | "y" (mat loa huong ra ngoai theo truc do)
            bmesh.ops.create_cone(b, cap_ends=True, segments=48, radius1=size[0] / 2, radius2=size[0] / 2, depth=size[1])
            for v in b.verts:
                x, y, z = v.co.x, v.co.y, v.co.z  # cone: truc Z
                v.co = (Vector((z, x, y)) if size[2] == "x" else Vector((x, z, -y))) + Vector(c)
        return BVHTree.FromBMesh(b)

    sps = p.get("speakers"); pcb = p.get("pcb_center")
    # 2 loa trai/phai (Tuan 2026-11-05): [{"center":[x,y,z],"axis":"x"|"y"}, ...], 1 loa x < 0 va 1 loa x > 0
    if not sps or len(sps) != 2 or not pcb:
        fails.append("params can speakers (2 loa trai/phai) + pcb_center (toa do lap rap, mm)")
    else:
        if not (min(s["center"][0] for s in sps) < -20 and max(s["center"][0] for s in sps) > 20):
            fails.append("2 loa phai nam 2 ben trai/phai (x < -20 va x > 20)")
        for i, s in enumerate(sps):
            if s.get("axis") not in ("x", "y"):
                fails.append(f"loa {i}: axis phai la x hoac y")
            elif tree.overlap(dummy("cyl", s["center"], (52.0, 26.0, s["axis"]))):
                fails.append(f"loa {i} O52 x 26 cham vo tai {s['center']}")
        import itertools
        for a_, b_ in itertools.combinations(sps, 2):
            if (Vector(a_["center"]) - Vector(b_["center"])).length < 53:
                fails.append("2 loa qua gan nhau (tam cach < 53 mm)")
        # bo 82 x 73, de du 25 mm chieu day linh kien (dung dung: 82 rong X, 25 day Y, 73 cao Z)
        dims = p.get("pcb_box", [82.0, 25.0, 73.0])
        if sorted(round(x) for x in dims) != [25, 73, 82]:
            fails.append(f"pcb_box phai la 82 x 73 x 25 (theo truc bat ky), dang {dims}")
        elif tree.overlap(dummy("box", pcb, dims)):
            fails.append("khoi bo mach 82 x 73 x 25 cham vo tai pcb_center")
for f in ("owl-preview.png", "owl-exploded.png"):
    if not (OUT / f).exists():
        fails.append(f"out/{f} khong co")
if fails:
    print("FAIL gate_owl:"); [print(" -", x) for x in fails]; sys.exit(1)
print("PASS gate_owl")
