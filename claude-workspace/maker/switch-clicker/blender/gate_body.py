# Gate THAN clicker A (Claude viet, executor KHONG sua).
# Chay: blender -b --python-exit-code 1 -P gate_body.py -- <out_dir>
# Kiem (theo HUONG IN, day z = 0):
#  plate-coupon.stl: 1 khoi kin; cat ngang z = 0,75 (giua tam 1,5) co 3 lo vuong 14,00 / 14,10 / 14,20 (+-0,03);
#                    tam day dung 1,5: cat z = 1,6 thay hoc duoi rong >= 15,2 (khong con tam).
#  stem-coupon.stl : 3 khoi kin; cat ngang cach mat tren 2,0 mm co lo chu thap moi khoi:
#                    canh dai 4,33 / 4,43 / 4,53, be rong tay 1,35 / 1,45 / 1,55 (+-0,03); sau lo >= 3,8.
import bpy, bmesh, sys
from pathlib import Path

OUT = Path(sys.argv[sys.argv.index("--") + 1])
fails = []
TOL = 0.03


def load(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    p = OUT / name
    if not p.exists():
        fails.append(f"{name}: khong co file")
        return None
    bpy.ops.wm.stl_import(filepath=str(p))
    bm = bmesh.new()
    bm.from_mesh(bpy.context.selected_objects[0].data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return bm


def islands(bm):
    bm.faces.ensure_lookup_table()
    seen, out = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        st, comp = [f], []
        seen.add(f.index)
        while st:
            x = st.pop()
            comp.append(x)
            for e in x.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index)
                        st.append(g)
        out.append(comp)
    return out


def check_solid(name, bm, n):
    comps = islands(bm)
    if len(comps) != n:
        fails.append(f"{name}: {len(comps)} khoi, can {n}")
    nm = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    if nm:
        fails.append(f"{name}: {nm} canh non-manifold")
    zmin = min(v.co.z for v in bm.verts)
    if abs(zmin) > 0.02:
        fails.append(f"{name}: day khong o z = 0 ({zmin:.3f})")
    return max(v.co.z for v in bm.verts)


def loops_at(bm, z):
    """cac vong kin cua mat cat z -> list bbox (xmin,xmax,ymin,ymax)"""
    c = bm.copy()
    r = bmesh.ops.bisect_plane(c, geom=c.verts[:] + c.edges[:] + c.faces[:], plane_co=(0, 0, z), plane_no=(0, 0, 1))
    es = [e for e in r["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    adj = {}
    for e in es:
        a, b = e.verts
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    seen, boxes = set(), []
    for v in adj:
        if v in seen:
            continue
        st, pts = [v], []
        seen.add(v)
        while st:
            x = st.pop()
            pts.append(x.co)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    st.append(y)
        xs, ys = [p.x for p in pts], [p.y for p in pts]
        boxes.append((min(xs), max(xs), min(ys), max(ys)))
    c.free()
    return boxes


def inner(boxes):
    """bo vong ngoai cung (bbox lon nhat), con lai la lo"""
    if not boxes:
        return []
    big = max(boxes, key=lambda b: (b[1] - b[0]) * (b[3] - b[2]))
    return [b for b in boxes if b is not big]


# ---- than A (in lat: tam kep sat ban) ----
HOLE = 14.0
bm = load("body-a.stl")
if bm:
    zmax = check_solid("body-a.stl", bm, 1)
    if abs(zmax - 14.0) > 0.05:
        fails.append(f"body: cao {zmax:.2f}, can 14,0")
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]
    print("bbox XY: %.2f x %.2f" % (max(xs) - min(xs), max(ys) - min(ys)))
    sq = [b for b in inner(loops_at(bm, 0.75)) if 13 < b[1] - b[0] < 15.5]
    print("lo tam z=0.75:", [(round(b[1]-b[0],3), round(b[3]-b[2],3)) for b in sq])
    if len(sq) != 1 or any(abs((b[1]-b[0]) - HOLE) > TOL or abs((b[3]-b[2]) - HOLE) > TOL for b in sq):
        fails.append(f"body: can 1 lo vuong {HOLE} o z = 0,75")
    cav = [b for b in inner(loops_at(bm, 1.6)) if b[1] - b[0] > 13]
    if len(cav) != 1 or min(cav[0][1]-cav[0][0], cav[0][3]-cav[0][2]) < 15.2:
        fails.append("body: o z = 1,6 phai co hoc >= 15,2 (tam chi day 1,5)")
    deep = [b for b in inner(loops_at(bm, 10.5)) if b[1] - b[0] > 13]
    if len(deep) != 1:
        fails.append("body: hoc phai sau toi z >= 10,5 (cho vo duoi 5,0 + chan 3,3 + du)")
    top = [b for b in inner(loops_at(bm, 13.0)) if b[1] - b[0] > 8]
    if top:
        fails.append("body: day (z 11,8..14) phai kin tren vung switch")
    ring = [b for b in inner(loops_at(bm, 2.0)) if 5.0 < b[1] - b[0] < 5.8]
    print("lo vong treo z=2:", [round(b[1]-b[0],3) for b in ring])
    if len(ring) != 1 or abs((ring[0][1]-ring[0][0]) - 5.4) > 0.08:
        fails.append("body: vong treo phai co lo ~5,4 o z = 2")
    bm.free()

if fails:
    print("FAIL", len(fails))
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS gate_body")
