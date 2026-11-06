# Gate CAD vo Cu Bong (Claude viet, executor KHONG sua).
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl.py -- out
import bpy, bmesh, json, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
fails = []
PARTS = ["shell-front", "shell-back", "belly", "beak", "button-cap", "eye-diffuser", "speaker-bezel", "speaker-ring"]
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
            else:
                # loa that (2026-11-06): mep O52 x 5 phia truoc + than <= body_d_max phia sau; bot 0,1/dau de mat ep (vong ep, ron) khong tinh la cham
                sc_ = p.get("speaker_clamp", {}); ft = sc_.get("flange_t", 5.0); bd = sc_.get("body_d_max", 47.0)
                c = Vector(s["center"]); k = 0 if s["axis"] == "x" else 1; sg = 1 if c[k] > 0 else -1
                face = c[k] + sg * 13.0
                cf = c.copy(); cf[k] = face - sg * ft / 2
                cb = c.copy(); cb[k] = face - sg * (ft + (26.0 - ft) / 2)
                if tree.overlap(dummy("cyl", cf, (52.0, ft - 0.2, s["axis"]))):
                    fails.append(f"loa {i}: mep O52 x {ft} cham vo/vanh loa")
                if tree.overlap(dummy("cyl", cb, (bd, 26.0 - ft - 0.2, s["axis"]))):
                    fails.append(f"loa {i}: than O{bd} cham vong ep/vo")
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
# co cau kep loa (2026-11-06): so khe theo fit-library + so Tuan do
sc_ = p.get("speaker_clamp")
if not sc_:
    fails.append("params can speaker_clamp")
else:
    if abs(sc_["flange_t"] - 5.0) > 0.01: fails.append("flange_t phai 5,0 (Tuan do)")
    if not 1.0 <= sc_["gasket_t"] <= 1.8: fails.append("ron ep 1,0-1,8 (EVA 2 mm)")
    bay = sc_.get("bayonet")  # 2026-11-06 Tuan: khong vit -> vong ep ngam xoay
    if not bay:
        fails.append("speaker_clamp can bayonet (vong ep ngam xoay, khong vit)")
    else:
        if bay["n"] < 3: fails.append("ngam xoay can >= 3 chot")
        if not 0.2 <= bay["sleeve_clr"] <= 0.35: fails.append("khe ong tay 0,2-0,35 (truot)")
        if bay["pin_clr"] < 0.2: fails.append("khe dau chot >= 0,2")
        if bay["pin_h"] < 0.8: fails.append("chot nho ra >= 0,8 mm (an du)")
        if not 20 <= bay["twist"] <= 45: fails.append("goc xoay khoa 20-45 do")
        if bay["groove_clr"] < 0.2: fails.append("ranh ngang can khe doc truc >= 0,2 de xoay khi an")
    if not 0.8 <= sc_.get("gasket_locked", 0) <= 1.4: fails.append("ron EVA 2 mm khi khoa phai con 0,8-1,4 mm (ep 30-60 %)")
    if sc_["ring_id"] <= sc_["body_d_max"]: fails.append("lo vong ep phai lon hon than loa")
    if sc_["ring_id"] >= 52.0 - 2 * 2.0: fails.append("vong ep phai de len mep loa >= 2 mm moi ben")
    if abs(sc_["face_abs_x"] - sc_["flange_t"] - sc_["cup_end_abs_x"]) > 0.01: fails.append("mat truoc vong ep phai trung mat sau mep loa")
# ngam xoay lap duoc that (2026-11-06): vong ep phai (1) nam khit o vi tri khoa, (2) theo 1 chieu xoay: lot ranh doc khi dua vao
# va xoay het goc khoa khi an them - khong cham vanh loa. Dung out/asm (vi tri lap that), loa phai (truc +x qua (0,0,z_loa)).
bay = (p.get("speaker_clamp") or {}).get("bayonet")
bz_m, rg_m = load(OUT / "asm" / "speaker-bezel-R.stl"), load(OUT / "asm" / "speaker-ring-R.stl")
if bay and bz_m and rg_m and p.get("speakers"):
    import math
    from mathutils import Matrix
    c = Vector((0.0, 0.0, max(s["center"] for s in p["speakers"])[2]))
    bz_tree = BVHTree.FromBMesh(bz_m)

    def hit(dx, ang_deg):
        b = rg_m.copy()
        T = Matrix.Translation((dx, 0, 0)) @ Matrix.Translation(c) @ Matrix.Rotation(math.radians(ang_deg), 4, 'X') @ Matrix.Translation(-c)
        bmesh.ops.transform(b, matrix=T, verts=b.verts)
        r_ = bz_tree.overlap(BVHTree.FromBMesh(b)); b.free()
        return bool(r_)

    if hit(0.1, 0.0):
        fails.append("vong ep cham vanh loa o vi tri khoa")
    tw, press = bay["twist"], min(0.2, bay["groove_clr"] - 0.05)
    ok_dir = None
    for sg in (1, -1):
        entry = all(not hit(-d, sg * tw) for d in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0)) and not hit(press, sg * tw)
        turn = all(not hit(press, sg * tw * k / 6) for k in range(7))
        if entry and turn:
            ok_dir = sg
    if ok_dir is None:
        fails.append("ngam xoay khong lap duoc: khong co chieu xoay nao vua lot ranh doc vua xoay het goc khoa")
    else:
        print(f"ngam xoay: lap duoc (chieu {'+' if ok_dir > 0 else '-'}, xoay {tw:.0f} do)")
# cong tac 6 x 6 (KEY4 song song) phai DUNG TREN GIA trong nua sau (2026-11-06: ban cu lo nut cat mat gia -> lo lung)
sw_m, sb_m = load(OUT / "asm" / "switch-6x6-dummy.stl"), load(OUT / "asm" / "shell-back.stl")
if sw_m and sb_m:
    zmin = min(v.co.z for v in sw_m.verts)
    xs_ = [v.co.x for v in sw_m.verts]; ys_ = [v.co.y for v in sw_m.verts]
    sb_tree = BVHTree.FromBMesh(sb_m)
    for px_ in (min(xs_) + 0.3, max(xs_) - 0.3):
        for py_ in (min(ys_) + 0.3, max(ys_) - 0.3):
            hit_ = sb_tree.ray_cast(Vector((px_, py_, zmin + 0.05)), Vector((0, 0, -1)), 0.3)
            if hit_[0] is None:
                fails.append(f"cong tac 6x6 khong co gia do tai ({px_:.1f}, {py_:.1f}) - lo lung")
                break
    bc_m = load(OUT / "asm" / "button-cap.stl")
    if bc_m:
        gap = min(v.co.z for v in bc_m.verts) - max(v.co.z for v in sw_m.verts)
        if not 0.05 <= gap <= 1.0:
            fails.append(f"khe chan nut - dinh cong tac {gap:.2f} mm (can 0,05-1,0)")
for f in ("owl-preview.png", "owl-exploded.png"):
    if not (OUT / f).exists():
        fails.append(f"out/{f} khong co")
if fails:
    print("FAIL gate_owl:"); [print(" -", x) for x in fails]; sys.exit(1)
print("PASS gate_owl")
