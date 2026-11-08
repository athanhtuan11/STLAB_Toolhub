# Gate CAD vo Cu Bong (Claude viet, executor KHONG sua).
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl.py -- out
import bpy, bmesh, json, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
fails = []
PARTS = ["shell-front", "shell-back", "belly", "beak", "button-cap", "eye-diffuser", "speaker-bezel", "speaker-ring",
         "mx-cap-vol-up", "mx-cap-vol-down"]   # 2026-11-08 Tuan: nut = switch phim co MX (y tuong clicker)
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
# 2026-11-08 Tuan: "su dung clicker lam chan button de dieu khien GPIO: bat tat tang giam" -> 3 switch MX (khong PCB):
# talk (KEY4 GPIO23, duoi nap nut dau cu), vol_up (KEY5 GPIO18), vol_down (KEY6 GPIO5) - han song song nut tren bo (bam = noi GND).
# So o switch theo fit-library catpaw/mx-socket (lo vuong 14,00 press, sau 8,58, ranh V ngam) + catpaw/mx-keycap-cross (lo chu thap 4,19 x 1,25).
# Be < 3 tuoi: nap nut KHONG duoc rut ra tu ngoai -> co vanh trong lon hon lo vo (bi giu boi vo), lap tu trong truoc khi dong vo.
mx = p.get("mx")
if not mx:
    fails.append("params can mx (3 switch MX: talk / vol_up / vol_down)")
else:
    if abs(float(mx.get("hole", 0)) - 14.0) > 0.01: fails.append(f"mx.hole {mx.get('hole')} phai 14,00 (fit-library catpaw/mx-socket, press)")
    if float(mx.get("socket_depth", 0)) < 8.0: fails.append("mx.socket_depth >= 8,0 (catpaw 8,58)")
    if abs(float(mx.get("stem_cross_l", 0)) - 4.19) > 0.01 or abs(float(mx.get("stem_cross_w", 0)) - 1.25) > 0.01:
        fails.append("lo chu thap nap nut 4,19 x 1,25 (fit-library catpaw/mx-keycap-cross)")
    keys = {k.get("name"): k for k in mx.get("keys", [])}
    for nm, gp in (("talk", 23), ("vol_up", 18), ("vol_down", 5)):
        k = keys.get(nm)
        if not k or k.get("gpio") != gp:
            fails.append(f"mx.keys can {nm} gpio {gp}")
        elif float(k.get("flange_over", 0)) < 1.5:
            fails.append(f"nap nut {nm}: vanh trong phai rong hon lo vo >= 1,5 mm/ben (khong rut ra duoc)")
    # 2026-11-08 Tuan: "am luong dua ve lung" (25accf3 tu y doi len hai ben dau khi chua duyet).
    # Nut vol o LUNG nua sau: truc +y, cach mat rap >= 30, |x| 8..40, z 60..130 (tren khe cap z<=16), 2 tam cach >= 25.
    # Nap luon tu TRONG qua lo switch 14,00 -> vanh nap Ø <= 13,8 (van giu boi lo vo: flange_over >= 1,5 o tren).
    Y0_ = float(p.get("split_plane_y", 0.37))
    vks = [keys.get("vol_up"), keys.get("vol_down")]
    if all(vks):
        for k in vks:
            pos = [float(c) for c in k.get("pos", [0, 0, 0])]
            if k.get("axis") != "y" or pos[1] < Y0_ + 30:
                fails.append(f"nut {k.get('name')} phai o LUNG (truc y, y >= {Y0_ + 30:.1f}): axis={k.get('axis')} pos={pos}")
            if not (8 <= abs(pos[0]) <= 40 and 60 <= pos[2] <= 130):
                fails.append(f"nut {k.get('name')} ngoai vung lung |x| 8..40, z 60..130: pos={pos}")
            if 2 * float(k.get("flange_r", 99)) > 13.8:
                fails.append(f"nap {k.get('name')}: vanh Ø{2 * float(k.get('flange_r', 99)):.1f} > 13,8 -> khong luon qua lo switch 14,00 tu trong")
        # 2026-11-08 Tuan: "cong theo vo. ngoai lung neu giau vit duoc thi tot" -> vit M2.5 tu ren bat TU TRONG vao tru kin
        # (fit-library mec1/tipflow m2.5-self-tap 2,2-2,4; mec1/m2.5-clearance 2,8 + hoc dau O5,0), mat pod cong theo vo (lech <= 0,6).
        vp = p.get("vol_pod", {})
        sc = vp.get("screws", {}) if isinstance(vp.get("screws"), dict) else {}
        if sc.get("side") != "inside":
            fails.append(f"vit giu pod phai bat TU TRONG (giau vit), vol_pod.screws.side={sc.get('side')}")
        if not (2.2 <= float(sc.get("pilot_d", 0)) <= 2.4) or abs(float(sc.get("clear_d", 0)) - 2.8) > 0.01:
            fails.append(f"vit M2.5 tu ren: lo moi 2,2-2,4, lo xuyen 2,8 (fit-library): {sc}")
        if float(vp.get("flush_max_dev", 99)) > 0.6:
            fails.append(f"mat ngoai pod phai cong theo vo (lech <= 0,6 mm): flush_max_dev={vp.get('flush_max_dev')}")
        a_, b_ = ([float(c) for c in k.get("pos", [0, 0, 0])] for k in vks)
        if ((a_[0] - b_[0]) ** 2 + (a_[2] - b_[2]) ** 2) ** 0.5 < 25:
            fails.append("2 nut am luong cach nhau < 25 mm (de bam nham)")
    for nm, cap in (("talk", "button-cap"), ("vol_up", "mx-cap-vol-up"), ("vol_down", "mx-cap-vol-down")):
        sw_m, cp_m = load(OUT / "asm" / f"mx-switch-{nm}.stl"), load(OUT / "asm" / f"{cap}.stl")
        sh_m = load(OUT / "asm" / "shell-back.stl") or load(OUT / "asm" / "shell-front.stl")
        if not (sw_m and cp_m and sh_m):
            continue
        sw_t, cp_t, sh_t = BVHTree.FromBMesh(sw_m), BVHTree.FromBMesh(cp_m), BVHTree.FromBMesh(sh_m)
        # nap nut khong duoc cham vo o vi tri nghi (truot tu do), switch khong cham nap
        if cp_t.overlap(sh_t): fails.append(f"nap nut {nm} cham vo o vi tri nghi (can khe truot)")
        print(f"mx {nm}: switch + nap nut co trong lap rap")
# tat ca ban in phai cat lop PASS, khong can support (Tuan 2026-11-05: sua model cho het support, gui ban .3mf)
rep = OUT.parent.parent / "print" / "plates" / "print-report.json"
if rep.exists():
    try:
        r_ = json.loads(rep.read_text(encoding="utf-8"))
        bad_ = [b["ban"] for b in r_.get("ban", []) if b.get("trang_thai") != "PASS"]
        if bad_ or r_.get("stl_chua_xep"): fails.append(f"ban in chua PASS (can support/loi): {bad_} chua xep: {r_.get('stl_chua_xep')}")
        stl_dir = OUT.parent.parent / "print" / "stl"
        old = [f.name for f in stl_dir.glob("*.stl") if f.stat().st_mtime < (OUT / "owl-params.json").stat().st_mtime - 5]
        if old: fails.append(f"print/stl cu hon model (chep lai tu cad/out): {old}")
    except Exception as e:
        fails.append(f"doc print-report.json loi {type(e).__name__}")
else:
    fails.append("chua co print/plates/print-report.json - chay slice.py truoc")
for f in ("owl-preview.png", "owl-exploded.png"):
    if not (OUT / f).exists():
        fails.append(f"out/{f} khong co")
if fails:
    print("FAIL gate_owl:"); [print(" -", x) for x in fails]; sys.exit(1)
print("PASS gate_owl")
