# Gate CAD vo Cu Bong BAN S3 CO MAN + 2 LOA (Claude viet 2026-11-26, executor KHONG sua). Goc: gate_owl_s3.py.
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl_s3_screen.py -- out-s3-screen
# 2026-11-26 Tuan: dang A2 V2 (man TFT 2,8" MSP2807 cam ung lam mat, khong tam che, mo chong mep duoi vien) + 2 loa O52 4 ohm 3 W
# o 2 suon (2026-11-26 Tuan chon H0: truc NGANG +-X, thay H25), moi loa 1 MAX98357A. Bo eye-ring/eye-diffuser, bung tron.
# Ban S3 (Tuan 2026-11-12): ESP32-S3 N16R8 + INMP441 + MAX98357A, CHI 1 LOA 4 ohm 3 W (O52 x 26, mep 5) o BUNG quay ra truoc,
# mic o TRAN (xa loa, ngan kin), 1 switch MX: noi GPIO1 (dinh dau); 2026-11-12 bo 2 nut am luong + vol-pod.
import bpy, bmesh, json, sys, math, itertools
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
fails = []
PARTS = ["shell-front", "shell-back", "belly", "beak", "button-cap", "face-plate",
         "speaker-bezel-L", "speaker-bezel-R", "speaker-ring-L", "speaker-ring-R", "mic-clamp", "amp-tray"]
# man MSP2807 (ban ve LCDWiki LCM OUTLINE V1.0, tools/parts-library id tft-2-8-spi-ili9341-touch) - dat NGANG
SCR_PCB = (86.0, 50.0, 1.6); SCR_GLASS = (69.2, 50.0); SCR_AA = (57.6, 43.2); SCR_T = 5.6; SCR_T_HDR = 12.78
SCR_HOLES = (80.0, 44.0); SCR_HOLE_D = 3.2   # hang that V1.1 (Tuan do 2026-11-26), ban ve V1.0: 76,08
# 2026-11-12 Tuan: "chi can 1 SW khoi dong, tinh chinh dung voice" -> bo 2 nut am luong + vol-pod
BED = 250.0


def load(path, must=True):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not path.exists():
        if must:
            fails.append(f"{path.name}: khong co file")
        return None
    bpy.ops.wm.stl_import(filepath=str(path))
    bm = bmesh.new()
    bm.from_mesh(bpy.context.selected_objects[0].data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    return bm


def islands(bm):
    seen, n = set(), 0
    for f in bm.faces:
        if f.index in seen:
            continue
        n += 1; st = [f]; seen.add(f.index)
        while st:
            g = st.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index); st.append(h)
    return n


def dummy(kind, c, size):
    b = bmesh.new()
    if kind == "box":
        bmesh.ops.create_cube(b, size=1.0)
        for v in b.verts:
            v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2])) + Vector(c)
    else:  # tru truc Y
        bmesh.ops.create_cone(b, cap_ends=True, segments=48, radius1=size[0] / 2, radius2=size[0] / 2, depth=size[1])
        for v in b.verts:
            v.co = Vector((v.co.x, v.co.z, -v.co.y)) + Vector(c)
    t = BVHTree.FromBMesh(b); b.free()
    return t


def cyl_axis(c, axis, d, L):
    """tru O d dai L, tam c, truc theo vector axis"""
    b = bmesh.new()
    bmesh.ops.create_cone(b, cap_ends=True, segments=48, radius1=d / 2, radius2=d / 2, depth=L)
    R = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(b, matrix=Matrix.Translation(Vector(c)) @ R, verts=b.verts)
    t = BVHTree.FromBMesh(b); b.free()
    return t


p = json.loads((OUT / "owl-params.json").read_text(encoding="utf-8")) if (OUT / "owl-params.json").exists() else {}
if not p:
    fails.append("out-s3/owl-params.json khong co")
if p.get("variant") != "s3-screen":
    fails.append('params variant phai "s3-screen"')
for k, want in [("wall", 2.4), ("speaker_pocket_d", 52.6), ("grille_hole_d", 2.8), ("mic_hole_d", 2.0),
                ("button_cap_d", 50.0), ("button_hole_d", 50.8), ("vent_w", 2.0)]:
    v = p.get(k)
    if v is None or abs(float(v) - want) > 0.01:
        fails.append(f"params {k} = {v}, can {want}")

# ---- tung chi tiet in
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
    base = sum(f.calc_area() for f in bm.faces if all(v.co.z < 0.3 for v in f.verts) and f.normal.z < -0.9)
    print(f"{name}: {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} x {max(zs)-min(zs):.1f}, mat day {base:.0f} mm2")
    if base < (40 if name in ("mic-clamp",) else 150):
        fails.append(f"{name}: mat day in {base:.0f} mm2 qua nho – dat lai huong in")
for old in ("eye-ring", "eye-diffuser", "speaker-bezel", "speaker-ring"):
    if (OUT / f"{old}.stl").exists():
        fails.append(f"{old}.stl con trong out-s3-screen (ban co man: bo mat LED, loa bung)")

# ---- lap rap
bm = load(OUT / "owl-assembled.stl")
Y0 = float(p.get("split_plane_y", 0.0))
sps = p.get("speakers") or []
if bm:
    xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
    W, D, H = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    print(f"lap rap: {W:.1f} x {D:.1f} x {H:.1f}")
    for lab, got, lo, hi in (("rong", W, 115, 150), ("sau", D, 100, 125), ("cao", H, 165, 185)):
        if not lo <= got <= hi:
            fails.append(f"lap rap {lab} {got:.1f} ngoai {lo}..{hi}")
    tree = BVHTree.FromBMesh(bm)

    # 2 loa o 2 suon, truc chech truoc 20-30 do (H25); axis = vector phap mat loa huong RA NGOAI, [ax, ay, 0]
    spk_trees = []
    if len(sps) != 2:
        fails.append(f"ban co man can dung 2 loa (speakers co {len(sps)})")
    else:
        xs_ = sorted(q["center"][0] for q in sps)
        if not (xs_[0] < -30 and xs_[1] > 30):
            fails.append(f"2 loa phai o 2 suon trai/phai (|x| > 30): {sps}")
        for s in sps:
            c = Vector(s["center"]); a = Vector(s.get("axis") or (0, 0, 0))
            if not isinstance(s.get("axis"), list) or a.length < 0.5:
                fails.append(f"loa can axis la vector [ax, ay, 0]: {s}"); continue
            a.normalize()
            ang = math.degrees(math.atan2(-a.y, abs(a.x)))
            # 2026-11-26 Tuan chon H0: truc loa NGANG +-X (lech <= 3 do), khong con H25
            if a.x * c.x <= 0 or abs(ang) > 3.0 or abs(a.z) > 0.05:
                fails.append(f"loa {s}: mat loa phai huong NGANG ra ngoai suon (H0, lech <= 3 do; dang {ang:.1f})")
            if not 40 <= c.z <= 55:
                fails.append(f"loa tam z {c.z:.1f} ngoai 40..55")
            sc_ = p.get("speaker_clamp", {}); ft = sc_.get("flange_t", 5.0); bd = sc_.get("body_d_max", 39.0)
            face = c + a * 13.0                                  # mat loa (phia ngoai)
            if tree.overlap(cyl_axis(face - a * (ft / 2), a, 52.0, ft - 0.2)):
                fails.append(f"loa {c.x:+.0f}: mep O52 x {ft} cham vo/vanh loa")
            if tree.overlap(cyl_axis(face - a * (ft + (26.0 - ft) / 2), a, bd, 26.0 - ft - 0.2)):
                fails.append(f"loa {c.x:+.0f}: than O{bd} cham vong ep/vo")
            spk_trees.append(cyl_axis(c, a, 52.0, 26.0))

    # bo ESP32-S3 (thu vien: DevKitC-1 70,2 x 25,4 x 13,2 kem anten; clone N16R8 2 USB-C chua co so -> cho rong):
    # khoi giu cho >= 72 x 29 x 16 khong cham vo, cong USB (dau duoi) ngay tren khe cap
    pcb = p.get("pcb_center"); dims = p.get("pcb_box")
    if not pcb or not dims:
        fails.append("params can pcb_center + pcb_box")
    else:
        sd = sorted(float(x) for x in dims)
        if sd[0] < 16 or sd[1] < 29 or sd[2] < 72:
            fails.append(f"pcb_box phai >= 72 x 29 x 16 (bo S3 + khe), dang {dims}")
        elif tree.overlap(dummy("box", pcb, dims)):
            fails.append("khoi bo ESP32-S3 cham vo tai pcb_center")
    # 2 ampli MAX98357A (moi loa 1 ampli, KHONG ghep 2 loa 1 ampli): amps = [{center, box, pcb?: {center, box, parts_h}}]
    amps = p.get("amps") or []
    if len(amps) != 2:
        fails.append(f"params can amps 2 muc (moi loa 1 MAX98357A): {len(amps)}")
    for am in amps:
        ac, ad = am.get("center"), am.get("box")
        if not ac or not ad:
            fails.append(f"amps can center + box: {am}"); continue
        sd = sorted(float(x) for x in ad)
        if sd[0] < 10 or sd[1] < 22 or sd[2] < 22:
            fails.append(f"amp box phai >= 22 x 22 x 10, dang {ad}")
        ap_ = am.get("pcb")
        if ap_:
            c_, b_ = ap_["center"], ap_["box"]
            if tree.overlap(dummy("box", c_, (b_[0] - 0.1, b_[1] - 0.1, b_[2] - 0.1))):
                fails.append(f"PCB ampli {ac} cham khay/vo")
            hp = float(ap_.get("parts_h", 3.0))
            if tree.overlap(dummy("box", (c_[0], c_[1], c_[2] + b_[2] / 2 + hp / 2 + 0.05), (b_[0] - 3.0, b_[1] - 0.1, hp))):
                fails.append(f"vung linh kien PCB ampli {ac} cham khay/vo")
        elif tree.overlap(dummy("box", ac, ad)):
            fails.append(f"khoi ampli cham vo tai {ac}")
        for t_ in spk_trees:
            if dummy("box", ac, ad).overlap(t_):
                fails.append(f"khoi ampli {ac} cham than loa")
        if sps and min((Vector(ac) - Vector(q["center"])).length for q in sps) > 70:
            fails.append(f"ampli {ac} cach loa gan nhat > 70 mm")
    if len(amps) == 2 and len(sps) == 2 and all(am.get("center") for am in amps):
        near = {min(range(2), key=lambda i: (Vector(am["center"]) - Vector(sps[i]["center"])).length) for am in amps}
        if len(near) != 2:
            fails.append("2 ampli phai moi cai gan 1 loa khac nhau")
    # mic INMP441 (PCB tron ~14-15 / vuong 14 x 14; nguon: ask-gpt 2026-11-12) -> o giu cho >= 17 x 17 x 8 sau lo tran
    mic = p.get("mic") or {}
    mc, mb = mic.get("center"), mic.get("box")
    if not mc or not mb:
        fails.append("params can mic.center + mic.box")
    else:
        sd = sorted(float(x) for x in mb)
        if sd[0] < 8 or sd[1] < 17 or sd[2] < 17:
            fails.append(f"mic.box phai >= 17 x 17 x 8, dang {mb}")
        elif not mic.get("pcb") and tree.overlap(dummy("box", mc, mb)):
            fails.append("o mic cham vo tai mic.center")
        mp_ = mic.get("pcb")
        if mp_:   # 2026-11-18: PCB INMP441 tron O15 x 1,6 nam trong kep khong cham gi
            _ax = mic.get("axis", "y"); _ax = _ax if isinstance(_ax, list) else (0, -1, 0)   # 2026-11-26: mic nghieng theo vom
            if tree.overlap(cyl_axis(mp_["center"], _ax, float(mp_["d"]) - 0.1, float(mp_["t"]) - 0.1)):
                fails.append("PCB mic O15 x 1,6 cham kep/vo")
        if mc[1] > Y0 - 20 or mc[2] < 100 or abs(float(mc[0])) > 1.0:
            fails.append(f"mic phai o MAT TRUOC, chinh giua (|x| <= 1), tran z >= 100: {mc}")
        # 2026-11-26: mic tran duoc nghieng theo vom (truc = phap tuyen vo), lech len toi da 45 do so huong -y
        ax_ = mic.get("axis", "y")
        if ax_ != "y":
            v_ = Vector(ax_) if isinstance(ax_, list) else Vector((0, 0, 0))
            if v_.length < 0.5 or abs(v_.normalized().x) > 0.1 or v_.normalized().y > -math.cos(math.radians(45)):
                fails.append(f"mic phai huong ra truoc (axis 'y' hoac vector nghieng len <= 45 do): {ax_}")
        for q in sps:
            if (Vector(mc) - Vector(q["center"])).length < 60:
                fails.append(f"mic cach tam loa {q['center']} < 60 mm (vong nhieu)")
        if int(mic.get("holes", 0)) < 3:
            fails.append("tran can >= 3 lo mic O2")
        seal = mic.get("seal") or {}
        if seal.get("type") == "labyrinth":   # PETG: dau ong dan am cam vao go lom tren vach tran
            if float(seal.get("depth", 0)) < 0.8 or not 0.05 <= float(seal.get("clearance", 9)) <= 0.2:
                fails.append(f"mic khop me cung: go lom sau >= 0,8, khe 0,05-0,2 mm/ben: {seal}")
        elif float(mic.get("gasket_t", 0)) < 1.0:
            fails.append("mic can ron (gasket_t >= 1,0) hoac seal.type 'labyrinth' de tieng loa trong vo khong lot vao")

    # ---- man TFT 2,8" (mat dong + cam ung, KHONG tam che)
    # screen = {center (tam PCB), glass_front_y, header_side '+x'|'-x', window [w, h], window_offset_x, glass_recess,
    #           bezel_over, holes, hole_d, touch}
    sc = p.get("screen") or {}
    if not sc.get("center") or "glass_front_y" not in sc:
        fails.append("params can screen {center, glass_front_y, header_side, window, window_offset_x, glass_recess, bezel_over, holes, hole_d, touch}")
    else:
        c = Vector(sc["center"])
        if abs(c.x) > 1.0 or not 98 <= c.z <= 110 or c.y > Y0 - 30:
            fails.append(f"man: tam PCB phai |x| <= 1, z 98..110, o mat truoc: {sc['center']}")
        hs = {"+x": 1, "-x": -1}.get(sc.get("header_side"), 0)
        if not hs:
            fails.append("screen.header_side phai '+x' hoac '-x'"); hs = 1
        if [round(float(v), 2) for v in sc.get("holes", ())] != list(SCR_HOLES) or abs(float(sc.get("hole_d", 0)) - SCR_HOLE_D) > 0.01:
            fails.append(f"screen.holes phai {SCR_HOLES}, hole_d {SCR_HOLE_D} (ban ve MSP2807)")
        if sc.get("touch") is not True:
            fails.append("screen.touch phai true (Tuan dung cam ung)")
        # kinh 69,2 bat dau cach dau PCB DOI DIEN header 6,40; AA lech ve phia doi dien header 4,9 so tam PCB (ban ve)
        g0 = c.x - hs * (SCR_PCB[0] / 2 - 6.4)
        g_lo, g_hi = sorted((g0, g0 + hs * SCR_GLASS[0]))
        aa_c = c.x - hs * 4.9
        a_lo, a_hi = aa_c - SCR_AA[0] / 2, aa_c + SCR_AA[0] / 2
        w = [float(v) for v in (sc.get("window") or [0, 0])]; wo = float(sc.get("window_offset_x", 0.0))
        w_lo, w_hi = c.x + wo - w[0] / 2, c.x + wo + w[0] / 2
        if not (w_lo <= a_lo + 0.05 and w_hi >= a_hi - 0.05 and w[1] >= SCR_AA[1] - 0.05):
            fails.append(f"cua so {w} lech {wo} khong phu het vung hien thi AA (x {a_lo:.1f}..{a_hi:.1f})")
        over = min(w_lo - g_lo, g_hi - w_hi, (SCR_GLASS[1] - w[1]) / 2)
        print(f"man: vien de kinh nho nhat {over:.2f} mm, cua so x {w_lo:.1f}..{w_hi:.1f}, kinh {g_lo:.1f}..{g_hi:.1f}")
        if over < 1.2 or float(sc.get("bezel_over", 0)) < 1.2:
            fails.append(f"vien de len kinh {over:.2f} mm (can >= 1,2 moi ben, mep kinh khong lo)")
        if not 0.8 <= float(sc.get("glass_recess", 0)) <= 1.5:
            fails.append("mat kinh lui 0,8-1,5 mm so mat vien (glass_recess)")
        gy = float(sc["glass_front_y"])
        # module that: kinh+LCD+bang 4,0 (69,2 x 50) phia truoc, PCB 1,6 (86 x 50) phia sau; truoc 2 dau PCB KHONG co kinh (tru vit o do)
        g_t = SCR_T - SCR_PCB[2]
        glass = dummy("box", ((g_lo + g_hi) / 2, gy + g_t / 2, c.z), (SCR_GLASS[0] - 0.2, g_t - 0.2, SCR_GLASS[1] - 0.2))
        pcb_ = dummy("box", (c.x, gy + g_t + SCR_PCB[2] / 2, c.z), (SCR_PCB[0] - 0.2, SCR_PCB[2] - 0.1, SCR_PCB[1] - 0.2))
        if tree.overlap(glass):
            fails.append("kinh man 69,2 x 50 x 4,0 cham vo/face-plate (khe lap thieu)")
        if tree.overlap(pcb_):
            fails.append("PCB man 86 x 50 x 1,6 cham vo/face-plate")
        mod = dummy("box", (c.x, gy + SCR_T / 2, c.z), (SCR_PCB[0] - 0.2, SCR_T - 0.2, SCR_PCB[1] - 0.2))
        # header 14 chan buoc 2,54 doc canh 50 o dau phia header, nho sau PCB 7,2 -> hoc sau PCB >= 8 mm
        hdr = dummy("box", (c.x + hs * (SCR_PCB[0] / 2 - 2.0), gy + SCR_T + 4.0, c.z), (3.0, 7.8, 13 * 2.54 + 2.5))
        if tree.overlap(hdr):
            fails.append("hoc header man (sau PCB >= 8 mm, dai 35,5) bi vo che")
        for t_ in spk_trees:
            if mod.overlap(t_) or hdr.overlap(t_):
                fails.append("man/header cham loa")
        if mc and float(mc[2]) - (c.z + SCR_PCB[1] / 2) < 7.0:   # 2026-11-26: ha 1 mm de nap nut di du hanh trinh
            fails.append(f"lo mic z {mc[2]} phai cao hon canh tren PCB man >= 7 mm (vien dia mat + 3 mm)")

# ---- co cau kep loa (giu so da kiem ban A1S)
sc_ = p.get("speaker_clamp")
if not sc_:
    fails.append("params can speaker_clamp")
else:
    if abs(sc_["flange_t"] - 5.0) > 0.01: fails.append("flange_t phai 5,0 (Tuan do)")
    spr = sc_.get("petg_spring")   # 2026-11-12: chua co TPU -> lay lo xo PETG ep mep loa; ranh ron giu nguyen cho TPU sau nay
    if spr:
        if int(spr.get("n", 0)) < 3: fails.append("lay lo xo PETG >= 3")
        if not 1.0 <= float(spr.get("t", 0)) <= 1.6: fails.append("lay lo xo day 1,0-1,6 mm (PETG uon duoc, khong gay)")
        if not 0.5 <= float(spr.get("preload", 0)) <= 1.5: fails.append("lay lo xo ep truoc 0,5-1,5 mm khi khoa")
        if float(spr.get("len", 0)) < 8: fails.append("lay lo xo dai >= 8 mm (du mem)")
    elif not 1.0 <= sc_["gasket_t"] <= 1.8: fails.append("ron ep 1,0-1,8 (EVA/TPU 2 mm) hoac petg_spring")
    bay = sc_.get("bayonet")
    if not bay:
        fails.append("speaker_clamp can bayonet (vong ep ngam xoay, khong vit)")
    else:
        if bay["n"] < 3: fails.append("ngam xoay can >= 3 chot")
        if not 0.2 <= bay["sleeve_clr"] <= 0.6: fails.append("khe ong tay 0,2-0,6 (2026-11-26 Tuan: 0,25 qua khit khong xoay duoc)")
        if bay["pin_clr"] < 0.2: fails.append("khe dau chot >= 0,2")
        if bay["pin_h"] < 0.8: fails.append("chot nho ra >= 0,8 mm")
        if not 20 <= bay["twist"] <= 45: fails.append("goc xoay khoa 20-45 do")
        if bay["groove_clr"] < 0.2: fails.append("ranh ngang can khe doc truc >= 0,2")
    if not sc_.get("petg_spring") and not 0.8 <= sc_.get("gasket_locked", 0) <= 1.4: fails.append("ron 2 mm khi khoa con 0,8-1,4 mm")
    if sc_.get("gasket_slot_kept") is not True: fails.append("giu ranh ron (gasket_slot_kept: true) de sau nay lap ron TPU khong ve lai")
    if sc_["ring_id"] <= sc_["body_d_max"]: fails.append("lo vong ep phai lon hon than loa")
    # Tuan 2026-11-26: go giu loa phai O48 thi moi dua loa vo duoc (ban thu v2 O47 khong lot) -> O48,0..48,3, de mep O52 >= 1,85/ben
    if not 48.0 <= float(sc_["ring_id"]) <= 48.3: fails.append(f"go giu loa (ring_id) phai O48,0-48,3 (Tuan), dang {sc_['ring_id']}")

# 2026-11-18: kep mic + khay ampli (vi tri lap) khong cham vo / vanh / vong ep / nap
_shell = bmesh.new()
for _n in ("shell-front", "shell-back", "belly", "beak", "face-plate", "speaker-bezel-L", "speaker-bezel-R",
           "speaker-ring-L", "speaker-ring-R", "button-cap"):
    _m = load(OUT / "asm" / f"{_n}.stl")
    if _m:
        _me = bpy.data.meshes.new("t"); _m.to_mesh(_me); _shell.from_mesh(_me)
_sh_tree = BVHTree.FromBMesh(_shell)
for _n in ("mic-clamp", "amp-tray"):
    _m = load(OUT / "asm" / f"{_n}.stl")
    if not _m:
        fails.append(f"thieu asm/{_n}.stl")
    elif _sh_tree.overlap(BVHTree.FromBMesh(_m)):
        fails.append(f"{_n} cham vo/vanh/nap o vi tri lap")

# ngam xoay lap duoc that (moi loa): asm, truc = axis loa (huong ra ngoai)
bay = (sc_ or {}).get("bayonet")
for side in ("L", "R"):
    bz_m, rg_m = load(OUT / "asm" / f"speaker-bezel-{side}.stl"), load(OUT / "asm" / f"speaker-ring-{side}.stl")
    q = [x for x in sps if (x["center"][0] < 0) == (side == "L") and isinstance(x.get("axis"), list)]
    if not (bay and bz_m and rg_m and len(q) == 1):
        continue
    c = Vector(q[0]["center"]); a = Vector(q[0]["axis"]).normalized()
    bz_tree = BVHTree.FromBMesh(bz_m)

    def hit(d_out, ang_deg):   # d_out > 0: day vong ep ve phia mat loa (ra ngoai); < 0: lui vao trong vo
        b = rg_m.copy()
        T = Matrix.Translation(a * d_out) @ Matrix.Translation(c) @ Matrix.Rotation(math.radians(ang_deg), 4, a) @ Matrix.Translation(-c)
        bmesh.ops.transform(b, matrix=T, verts=b.verts)
        r_ = bz_tree.overlap(BVHTree.FromBMesh(b)); b.free()
        return bool(r_)

    if hit(0.1, 0.0):
        fails.append(f"vong ep {side} cham vanh loa o vi tri khoa")
    tw, press = bay["twist"], min(0.2, bay["groove_clr"] - 0.05)
    ok_dir = None
    for sg in (1, -1):
        entry = all(not hit(-d, sg * tw) for d in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0)) and not hit(press, sg * tw)
        turn = all(not hit(press, sg * tw * k / 6) for k in range(7))
        if entry and turn:
            ok_dir = sg
    if ok_dir is None:
        fails.append(f"ngam xoay loa {side} khong lap duoc")
    else:
        print(f"ngam xoay {side}: lap duoc ({tw:.0f} do)")

# ---- switch MX (1 nut noi) (fit-library catpaw), GPIO ban S3
mx = p.get("mx")
if not mx:
    fails.append("params can mx")
else:
    if abs(float(mx.get("hole", 0)) - 14.0) > 0.01: fails.append("mx.hole phai 14,00 (fit-library catpaw/mx-socket)")
    if float(mx.get("socket_depth", 0)) < 8.0: fails.append("mx.socket_depth >= 8,0")
    if abs(float(mx.get("stem_cross_l", 0)) - 4.19) > 0.01 or abs(float(mx.get("stem_cross_w", 0)) - 1.25) > 0.01:
        fails.append("lo chu thap nap nut 4,19 x 1,25")
    keys = {k.get("name"): k for k in mx.get("keys", [])}
    if "vol_up" in keys or "vol_down" in keys:
        fails.append("ban S3 chi 1 nut (talk) - bo vol_up/vol_down (Tuan 2026-11-12)")
    k = keys.get("talk")
    if not k or k.get("gpio") != 1:
        fails.append("mx.keys can talk gpio 1")
    elif float(k.get("flange_over", 0)) < 1.5:
        fails.append("nap nut talk: vanh trong rong hon lo vo >= 1,5 mm/ben")
    if k and (k.get("axis") != "z" or float(k["pos"][2]) < 125):
        fails.append(f"nut noi phai o dinh dau (axis z, z >= 125): {k}")
for f in ("vol-pod-up.stl", "vol-pod-down.stl", "mx-cap-vol-up.stl", "mx-cap-vol-down.stl"):
    if (OUT / f).exists():
        fails.append(f"{f} con trong out-s3 (da bo nut am luong)")
# cap USB-C THANG (Tuan 2026-11-12: cap be goc 90 do hau nhu khong co): cong USB cua bo quay ra LUNG, cach mat trong vach lung <= 4 mm,
# lo cap tren vo sau thang hang voi cong (lech x/z <= 3 mm), lo >= 14 x 9 (dau cam USB-C)
cs = p.get("cable_slot") or {}
usb = p.get("pcb_usb") or {}
if cs.get("side") != "back" or float(cs.get("w", 0)) < 14 or float(cs.get("h", 0)) < 9 or not cs.get("center"):
    fails.append(f"cable_slot can o lung, >= 14 x 9, co center: {cs}")
elif not usb.get("center") or usb.get("dir") != "+y":
    fails.append(f"params can pcb_usb {{center, dir: '+y'}} (cong USB quay ra lung): {usb}")
else:
    uc, sc2 = [float(v) for v in usb["center"]], [float(v) for v in cs["center"]]
    if abs(uc[0] - sc2[0]) > 3 or abs(uc[2] - sc2[2]) > 3:
        fails.append(f"lo cap khong thang hang cong USB (lech x {uc[0]-sc2[0]:.1f}, z {uc[2]-sc2[2]:.1f})")
    if not 0 <= sc2[1] - uc[1] <= float(cs.get("wall_t", 2.4)) + 4.0:
        fails.append(f"cong USB cach lo cap {sc2[1]-uc[1]:.1f} mm (can mat cong <= 4 mm sau vach) - cap thang cam khong toi")
# ---- ban in
rep = OUT.parent.parent / "print" / "plates-s3-screen" / "print-report.json"
if rep.exists():
    try:
        r_ = json.loads(rep.read_text(encoding="utf-8"))
        bad_ = [b["ban"] for b in r_.get("ban", []) if b.get("trang_thai") != "PASS"]
        if bad_ or r_.get("stl_chua_xep"): fails.append(f"ban in chua PASS: {bad_} chua xep: {r_.get('stl_chua_xep')}")
    except Exception as e:
        fails.append(f"doc print-report.json loi {type(e).__name__}")
else:
    fails.append("chua co print/plates-s3-screen/print-report.json - chay slice.py print/print-s3-screen.yaml")
for f in ("owl-preview.png", "owl-exploded.png"):
    if not (OUT / f).exists():
        fails.append(f"out-s3-screen/{f} khong co")
if fails:
    print("FAIL gate_owl_s3_screen:"); [print(" -", x) for x in fails]; sys.exit(1)
print("PASS gate_owl_s3_screen")
