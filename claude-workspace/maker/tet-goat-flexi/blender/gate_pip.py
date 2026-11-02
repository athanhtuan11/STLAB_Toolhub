# Gate hinh hoc cho mau in-place (Claude viet, executor KHONG sua).
# Chay: blender -b --python-exit-code 1 -P gate_pip.py -- <stl_dir> <expect.json>
# expect.json: {"<ten>.stl": {"islands": N, "linked_pairs_min": K}, ...}; nguong chung o "_": {...}
# Kiem moi STL: tach cac khoi roi (island) -> moi khoi kin (0 canh non-manifold), cham ban (min z = 0),
# khong khoi nao chong lan nhau, khoang cach nho nhat giua 2 khoi bat ky >= min_gap (khe in duoc),
# so cap khoi "lien ket" (khoang cach <= link_max: khop in-place) >= linked_pairs_min.
import bpy, bmesh, json, sys
from pathlib import Path
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]
D, EXP = Path(argv[0]), json.loads(Path(argv[1]).read_text(encoding="utf-8"))
G = {"min_gap": 0.38, "link_max": 0.70, "z_tol": 0.02, **EXP.pop("_", {})}
fails = []


def islands(bm):
    seen, out = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack, comp = [f], []
        seen.add(f.index)
        while stack:
            x = stack.pop()
            comp.append(x)
            for e in x.edges:
                for g in e.link_faces:
                    if g.index not in seen:
                        seen.add(g.index)
                        stack.append(g)
        out.append(comp)
    return out


for name, exp in EXP.items():
    p = D / name
    if not p.exists():
        fails.append(f"{name}: khong co file")
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(p))
    ob = bpy.context.selected_objects[0]
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.faces.ensure_lookup_table()
    comps = islands(bm)
    if len(comps) != exp["islands"]:
        fails.append(f"{name}: {len(comps)} khoi, can {exp['islands']}")
    zmin_all = min(v.co.z for v in bm.verts)
    if abs(zmin_all) > G["z_tol"]:
        fails.append(f"{name}: day khong o z=0 (min z {zmin_all:.3f})")
    trees, verts = [], []
    for i, comp in enumerate(comps):
        es = {e for f in comp for e in f.edges}
        nm = sum(1 for e in es if len(e.link_faces) != 2)
        if nm:
            fails.append(f"{name}: khoi {i} co {nm} canh non-manifold (khong kin)")
        vs = list({v for f in comp for v in f.verts})
        zmin = min(v.co.z for v in vs)
        if zmin > G["z_tol"]:
            fails.append(f"{name}: khoi {i} khong cham ban (min z {zmin:.3f}) -> in lo lung")
        vi = {v.index: k for k, v in enumerate(vs)}
        trees.append(BVHTree.FromPolygons([v.co.copy() for v in vs],
                                          [[vi[v.index] for v in f.verts] for f in comp]))
        verts.append([v.co.copy() for v in vs])
    linked, gmin = 0, 1e9
    for i in range(len(comps)):
        for j in range(i + 1, len(comps)):
            if trees[i].overlap(trees[j]):
                fails.append(f"{name}: khoi {i} va {j} chong lan")
                continue
            d = min(min((trees[j].find_nearest(v)[3] or 1e9) for v in verts[i]),
                    min((trees[i].find_nearest(v)[3] or 1e9) for v in verts[j]))
            gmin = min(gmin, d)
            if d < G["min_gap"]:
                fails.append(f"{name}: khoi {i}-{j} cach {d:.3f} mm < {G['min_gap']} (dinh khi in)")
            if d <= G["link_max"]:
                linked += 1
    if linked < exp.get("linked_pairs_min", 0):
        fails.append(f"{name}: chi {linked} cap khoi lien ket, can >= {exp['linked_pairs_min']}")
    print(f"{name}: {len(comps)} khoi, khe nho nhat {gmin:.3f} mm, {linked} cap lien ket")
    bm.free()

if fails:
    print("FAIL", len(fails))
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS gate_pip")
