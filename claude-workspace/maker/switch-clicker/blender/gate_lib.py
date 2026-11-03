# Ham chung cho gate (Claude viet, executor KHONG sua).
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




def done(name):
    if fails:
        print("FAIL", len(fails))
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("PASS", name)
