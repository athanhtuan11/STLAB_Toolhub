# Gate CAD Cu Bong v3 LAP RAP THAT (Claude 2026-11-27, executor KHONG sua). Goc: gate_owl_s3_screen.py + muc V3 cuoi file
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl_v3.py -- out-v3  (spec-owl-v3-assembly.md)
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
         "speaker-bezel-L", "speaker-bezel-R", "speaker-ring-L", "speaker-ring-R", "mic-clamp", "s3-tray", "button-base", "base"]
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
if p.get("variant") != "v3":
    fails.append('params variant phai "v3"')
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
    if base < (40 if name in ("mic-clamp",) else 12 if name == "beak" else 150):   # v3: mo in lay xuong ban (vom len) -> BAT BUOC brim trong print yaml
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
        if sd[0] < 4.6 or sd[1] < 18.0 or sd[2] < 19.4:   # v3: ampli DUNG, khoi giu cho = PCB 1,6 + linh kien 3,0 (x) x 18 x 19,4
            fails.append(f"amp box phai >= 4,6 x 18 x 19,4 (PCB + linh kien), dang {ad}")
        ap_ = am.get("pcb")
        if ap_:
            c_, b_ = ap_["center"], ap_["box"]
            if tree.overlap(dummy("box", c_, (b_[0] - 0.1, b_[1] - 0.1, b_[2] - 0.1))):
                fails.append(f"PCB ampli {ac} cham khay/vo")
            hp = float(ap_.get("parts_h", 3.0))
            pd_ = ap_.get("parts_dir", [0, 0, 1]); ax_i = max(range(3), key=lambda i: abs(pd_[i])); sgn_ = 1 if pd_[ax_i] > 0 else -1
            pc_ = list(c_); pc_[ax_i] += sgn_ * (b_[ax_i] / 2 + hp / 2 + 0.05)
            ps_ = [b_[i] - 0.1 for i in range(3)]; ps_[ax_i] = hp
            oth = [i for i in range(3) if i != ax_i]; ps_[min(oth, key=lambda i: b_[i])] -= 2.9   # chua 1,5/ben mep han chan
            if tree.overlap(dummy("box", pc_, ps_)):
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
for _n in ("mic-clamp",):   # v3: khay/de nut/be tiep xuc chu y -> kiem bang tools/assembly-check (muc V3)
    _m = load(OUT / "asm" / f"{_n}.stl")
    if not _m:
        fails.append(f"thieu asm/{_n}.stl")
    else:
        # 2026-11-27 tam ep mic CO Y tua len 2 tru vo (vai chan) -> chi FAIL khi lan vao vo > 0,1 mm (co luoi 0,1 vao trong)
        _m.normal_update()
        _ix = {v: i for i, v in enumerate(_m.verts)}
        _shr = BVHTree.FromPolygons([v.co - v.normal * 0.1 for v in _m.verts], [tuple(_ix[v] for v in f.verts) for f in _m.faces])
        if _sh_tree.overlap(_shr):
            fails.append(f"{_n} lan vao vo/vanh/nap > 0,1 mm o vi tri lap")

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
    if bay.get("detent_h"):   # 2026-11-27 nac khoa: phai an vong ep (nen xop) qua go; go phai thap hon khe ranh moi qua duoc
        if bay["detent_h"] >= bay["groove_clr"] - 0.05:
            fails.append(f"nac khoa {bay['detent_h']} >= khe ranh {bay['groove_clr']} - 0,05: chot khong qua duoc")
        press = bay["detent_h"] + 0.05
        lim = min(bay["groove_clr"], bay.get("out_gap", 9)) - 0.03     # an qua out_gap -> vong ep cham day coc vanh
        if press > lim:
            fails.append(f"nac khoa {bay['detent_h']}: can an {press:.2f} > gioi han {lim:.2f} (khe ranh / out_gap)")
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
rep = OUT.parent.parent / "print" / "plates-v3" / "print-report.json"
if rep.exists():
    try:
        r_ = json.loads(rep.read_text(encoding="utf-8"))
        bad_ = [b["ban"] for b in r_.get("ban", []) if b.get("trang_thai") != "PASS"]
        if bad_ or r_.get("stl_chua_xep"): fails.append(f"ban in chua PASS: {bad_} chua xep: {r_.get('stl_chua_xep')}")
    except Exception as e:
        fails.append(f"doc print-report.json loi {type(e).__name__}")
else:
    fails.append("chua co print/plates-v3/print-report.json - chay slice.py print/print-v3.yaml")
for f in ("owl-preview.png", "owl-exploded.png"):
    if not (OUT / f).exists():
        fails.append(f"out-s3-screen/{f} khong co")
# ================================================================== V3 (spec-owl-v3-assembly.md, muc Gate)
v3 = p.get("v3") or {}
if not v3:
    fails.append("params thieu v3")
ASM_CFG = OUT.parent / "assembly.json"
ASM_REP = OUT.parent / "assembly-report.json"
cfg = json.loads(ASM_CFG.read_text(encoding="utf-8")) if ASM_CFG.exists() else {}
if not cfg or Path(cfg.get("asm_dir", "")).name != "asm" or (OUT.parent / cfg["asm_dir"]).resolve() != (OUT / "asm").resolve():
    fails.append(f"assembly.json phai tro toi {OUT.name}/asm")
# 1. tools/assembly-check PASS va moi hon STL asm (chay lai khi sua model)
if not ASM_REP.exists():
    fails.append("chua co assembly-report.json - chay tools/assembly-check/assembly_check.py -- assembly.json")
else:
    ar_ = json.loads(ASM_REP.read_text(encoding="utf-8"))
    newest = max(f.stat().st_mtime for f in (OUT / "asm").glob("*.stl"))
    if ar_.get("verdict") != "PASS":
        fails.append(f"assembly-check {ar_.get('verdict')}: {[i['msg'] for i in ar_.get('issues', []) if i['level'] == 'FAIL'][:6]}")
    if ASM_REP.stat().st_mtime < newest:
        fails.append("assembly-report.json cu hon STL asm - chay lai assembly-check")
    need = {"shell-front", "shell-back", "base", "s3-tray", "button-base", "button-cap", "face-plate", "beak", "belly", "mic-clamp",
            "speaker-bezel-L", "speaker-bezel-R", "speaker-ring-L", "speaker-ring-R"}
    if not need <= set(ar_.get("parts", [])):
        fails.append(f"assembly-check thieu part: {sorted(need - set(ar_.get('parts', [])))}")
    if any(j.get("type") == "pin" for j in cfg.get("joints", [])):
        fails.append("con joint pin (chot 2 nua chua ve) - v3 dung vit")


def _cyl_axis(c, ax, d, L):   # 2026-11-27: khoi tua vit theo truc bat ky (vit tam ep mic xien 45 do)
    b = bmesh.new()
    bmesh.ops.create_cone(b, cap_ends=True, segments=32, radius1=d / 2, radius2=d / 2, depth=L)
    R = Vector((0, 0, 1)).rotation_difference(Vector(ax).normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(b, matrix=Matrix.Translation(Vector(c)) @ R, verts=b.verts)
    return b


def _cyl_y(c, d, L):
    b = bmesh.new()
    bmesh.ops.create_cone(b, cap_ends=True, segments=32, radius1=d / 2, radius2=d / 2, depth=L)
    for v in b.verts:
        v.co = Vector((v.co.x, v.co.z, -v.co.y)) + Vector(c)
    return b


def mesh_of(name):
    m = load(OUT / "asm" / f"{name}.stl")
    return m


def tree_of(bm, d=0.0):
    if not d:
        return BVHTree.FromBMesh(bm)
    bm.normal_update()
    vs = [v.co + v.normal * d for v in bm.verts]; ix = {v: i for i, v in enumerate(bm.verts)}
    return BVHTree.FromPolygons(vs, [tuple(ix[v] for v in f.verts) for f in bm.faces])


def inside(tree, pt):
    n, o = 0, Vector(pt); d = Vector((0.0013, 1.0, 0.0007)).normalized()
    for _ in range(200):
        h = tree.ray_cast(o, d)
        if h[0] is None:
            break
        n += 1; o = h[0] + d * 1e-4
    return n % 2 == 1


order = cfg.get("order", [])
pinfo = cfg.get("parts", {})
MESH = {n: mesh_of(n) for n in order}
# 2. tua vit O8 x 80 doc truc moi vit M2.5 x 6 trong long, tai thoi diem bat (vo truoc nam ngua, part truoc do + chinh no + cum lap san)
drv = v3.get("driver", [8.0, 80.0])
s6 = v3.get("screws6", [])
if len(s6) < 8:
    fails.append(f"v3.screws6 can >= 8 vit (vanh loa 2 x 2, khay 2, de nut 2): {len(s6)}")
front_tree = tree_of(MESH["shell-front"]) if MESH.get("shell-front") else None
for sc6 in s6:
    part = sc6["part"]
    if part not in order:
        fails.append(f"vit {sc6['name']}: part {part} khong co trong order"); continue
    idx = order.index(part)
    obs = [n for n in order[:idx + 1]] + [n for n in order if part in (pinfo.get(n, {}).get("insert", {}).get("with") or [])]
    x_, y_, z_ = sc6["pos"]; hy = float(sc6.get("head_top_y", y_ + 1.7))
    dt = BVHTree.FromBMesh(_cyl_y((x_, hy + drv[1] / 2 + 0.05, z_), drv[0], drv[1]))
    hit = [n for n in obs if MESH.get(n) and dt.overlap(tree_of(MESH[n], -0.1))]
    if hit:
        fails.append(f"vit {sc6['name']}: tua vit O{drv[0]:g} x {drv[1]:g} vuong {hit}")
    # lo moi trong vo truoc phai co vat lieu bao quanh (an ren), duoi mat tai 1,0 va 4,0
    if front_tree:
        for dy in (1.0, 4.0):
            ring = [inside(front_tree, (x_ + 2.2 * math.cos(a), y_ - 3.0 - dy, z_ + 2.2 * math.sin(a))) for a in [k * math.pi / 4 for k in range(8)]]
            if not all(ring):
                fails.append(f"vit {sc6['name']}: lo moi M2.5 khong du vat lieu (sau mat tai {dy:g}: {sum(ring)}/8)")
print(f"V3 tua vit: {len(s6)} vit M2.5 x 6 kiem O{drv[0]:g} x {drv[1]:g}")
# 2b. vit giau (2026-11-27): mo/bung tu trong (+y), vit day vanh loa tu duoi (-z). Kiem: (a) tua vit O8 x 80 tu dinh dau vit
#     nguoc chieu vit khong vuong part da lap tai luc bat; (b) lo moi trong part dich co vat lieu bao quanh (an ren) suot doan an ren.
hs = v3.get("hidden_screws", [])
if len(hs) < 6:
    fails.append(f"v3.hidden_screws can 6 vit (mo, bung, 2 day vanh loa, 2 tam ep mic): {len(hs)}")
for h_ in hs:
    part = h_["part"]
    if part not in order:
        fails.append(f"vit {h_['name']}: part {part} khong co trong order"); continue
    ax = Vector(h_["axis"]).normalized(); hd = Vector(h_["head"])
    if abs(ax.z) > 0.95:     # thang dung tu duoi de: ngoai khong khi, chi kiem an ren
        pass
    else:
        at = h_.get("at", part)                     # part dang lap luc bat vit (vd. tam ep mic: vit an vao vo truoc)
        idx = order.index(at)
        obs = [n for n in order[:idx] if n not in (at, h_["part"] if at == part else at)]   # moi part da lap truoc (gom vo truoc)
        c0 = hd + ax * (1.9 + drv[1] / 2 + 0.05)     # tu dinh dau vit (~1,7) ra theo truc
        dt = BVHTree.FromBMesh(_cyl_axis(c0, ax, drv[0], drv[1]))
        hit = [n for n in obs if MESH.get(n) and dt.overlap(tree_of(MESH[n], -0.1))]
        if hit:
            fails.append(f"vit {h_['name']}: tua vit O{drv[0]:g} x {drv[1]:g} vuong {hit}")
    pt = tree_of(MESH[part]) if MESH.get(part) else None
    if pt:
        # doan an ren: tu 1,0 sau mat part toi 1,0 truoc dau vit (dau vit + chieu dai)
        tip = hd - ax * h_["length"]
        bad = 0; tot = 0
        eng = h_["length"] - h_.get("grip", 0.0)          # doan an ren that (bo phan xuyen qua chi tiet bi kep)
        for k in range(1, 6):
            c_ = tip + ax * (0.5 + (min(eng, 5.5) - 1.0) * k / 5.0)
            # 2 vecto vuong goc truc
            u_ = ax.orthogonal().normalized(); v_ = ax.cross(u_)
            for a in [j * math.pi / 4 for j in range(8)]:
                tot += 1
                if not inside(pt, c_ + (u_ * math.cos(a) + v_ * math.sin(a)) * (h_["pilot_d"] / 2 + 0.8)):
                    bad += 1
        if bad > 4:
            fails.append(f"vit {h_['name']}: lo moi trong {part} thieu vat lieu ({tot - bad}/{tot} diem quanh lo)")
print(f"V3 vit giau: {len(hs)} vit kiem tua vit + an ren")
# 3. 6 vit noi 2 nua: lo moi vo truoc trong vat lieu (an ren >= 6), gieng vo sau thong ra ngoai, do sau gieng (chon tua vit)
ss = v3.get("shell_screws", {})
back_tree = tree_of(MESH["shell-back"]) if MESH.get("shell-back") else None
Y0 = float(p.get("split_plane_y", 0.37))
wells = []
for (x_, z_) in ss.get("xz", []):
    if front_tree:
        for dy in (1.0, 4.0, 7.5):
            ring = [inside(front_tree, (x_ + 2.4 * math.cos(a), Y0 - dy, z_ + 2.4 * math.sin(a))) for a in [k * math.pi / 4 for k in range(8)]]
            if not all(ring):
                fails.append(f"vit noi ({x_:g}, {z_:g}): lo moi vo truoc thieu vat lieu o sau {dy:g} ({sum(ring)}/8)")
    if back_tree:
        h = back_tree.ray_cast(Vector((x_, Y0 + float(ss.get("well_floor", 3.0)) + 0.3, z_)), Vector((0, 1, 0)))
        if h[0] is not None:
            fails.append(f"vit noi ({x_:g}, {z_:g}): gieng vo sau bi chan tai y {h[0].y:.1f}")
        rw = float(ss.get("well_d", 5.6)) / 2 + 0.6
        skin = None
        for a in [k * math.pi / 4 for k in range(8)]:
            o_ = Vector((x_ + rw * math.cos(a), Y0 + 3.2, z_ + rw * math.sin(a)))
            if not inside(back_tree, o_):
                fails.append(f"vit noi ({x_:g}, {z_:g}): thanh gieng thung (goc {math.degrees(a):.0f})"); break
            hh = back_tree.ray_cast(o_, Vector((0, 1, 0)))
            if hh[0] is not None:
                skin = max(skin or 0, hh[0].y)
        if skin:
            wells.append(round(skin - Y0 - float(ss.get("well_floor", 3.0)), 1))
print(f"V3 gieng vit vo sau sau (mm, tu mat lung toi day): {wells} -> tua vit than <= O5 dai >= {max(wells or [0]) + 10:.0f}")
if wells and max(wells) > 45:
    fails.append(f"gieng vit sau {max(wells)} mm > 45 (tua vit thuong khong toi)")
# 4. goc lat >= 20 do theo moi huong
RHO = 1.27e-3   # g/mm3 PETG, dac (bao thu: dau dac, vo in that co infill -> trong tam thuc te thap hon)
COMP = [("loa L (TODO can)", 60.0, sps[0]["center"] if sps else (0, 0, 46)), ("loa R (TODO can)", 60.0, sps[1]["center"] if len(sps) > 1 else (0, 0, 46)),
        ("man MSP2807 (TODO can)", 35.0, (p.get("screen") or {}).get("center", (0, -50, 100))), ("bo ESP32-S3 (TODO)", 10.0, p.get("pcb_center", (0, 9, 34)))]


def vol_cent(bm):
    V, C = 0.0, Vector((0, 0, 0))
    for f in bm.faces:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            a, b, c = vs[0], vs[i], vs[i + 1]
            v = a.dot(b.cross(c)) / 6.0
            V += v; C += v * (a + b + c) / 4.0
    return V, (C / V if abs(V) > 1e-9 else C)


M_tot, Mc = 0.0, Vector((0, 0, 0))
for n, bm in MESH.items():
    if bm:
        V, C = vol_cent(bm); m_ = abs(V) * RHO; M_tot += m_; Mc += m_ * C
for nm, m_, c_ in COMP:
    M_tot += m_; Mc += m_ * Vector(c_)
com = Mc / M_tot
bb = MESH.get("base")
if bb:
    zmin = min(v.co.z for v in bb.verts)
    pts = sorted({(round(v.co.x, 3), round(v.co.y, 3)) for v in bb.verts if v.co.z < zmin + 0.05})
    def hull(P):
        def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        lo, up = [], []
        for q in P:
            while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0: lo.pop()
            lo.append(q)
        for q in reversed(P):
            while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0: up.pop()
            up.append(q)
        return lo[:-1] + up[:-1]
    H = hull(pts); h_ = com.z - zmin
    worst = (999, None)
    for i in range(len(H)):
        a, b = Vector((*H[i], 0)), Vector((*H[(i + 1) % len(H)], 0))
        e = (b - a); n2 = Vector((e.y, -e.x, 0)).normalized()
        d_ = (Vector((com.x, com.y, 0)) - a).dot(-n2) if (Vector((com.x, com.y, 0)) - a).dot(n2) < 0 else -1
        ang = math.degrees(math.atan2(d_, h_))
        if ang < worst[0]:
            worst = (ang, (round(n2.x, 2), round(n2.y, 2)))
    print(f"V3 lat: khoi luong ~{M_tot:.0f} g (vo dac + linh kien giu cho), trong tam ({com.x:.1f}, {com.y:.1f}, {com.z:.1f}), cao {h_:.1f} -> goc lat nho nhat {worst[0]:.1f} do huong {worst[1]}")
    v3["tip"] = dict(mass_g=round(M_tot), com=[round(com.x, 1), round(com.y, 1), round(com.z, 1)], min_angle=round(worst[0], 1), dir=worst[1])
    if worst[0] < 20.0:
        fails.append(f"goc lat {worst[0]:.1f} do < 20 do (huong {worst[1]})")
    (OUT / "tip-report.json").write_text(json.dumps(v3["tip"], indent=1), encoding="utf-8")
else:
    fails.append("thieu asm/base.stl")
if fails:
    print("FAIL gate_owl_v3:"); [print(" -", x) for x in fails]; sys.exit(1)
print("PASS gate_owl_v3")

