# Gate CAD vo Cu Bong BAN S3 (Claude viet 2026-11-12, executor KHONG sua).
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl_s3.py -- out-s3
# Ban S3 (Tuan 2026-11-12): ESP32-S3 N16R8 + INMP441 + MAX98357A, CHI 1 LOA 4 ohm 3 W (O52 x 26, mep 5) o BUNG quay ra truoc,
# mic o TRAN (xa loa, ngan kin), 1 switch MX: noi GPIO1 (dinh dau); 2026-11-12 bo 2 nut am luong + vol-pod.
import bpy, bmesh, json, sys, math, itertools
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
fails = []
PARTS = ["shell-front", "shell-back", "belly", "beak", "button-cap", "eye-diffuser", "speaker-bezel", "speaker-ring",
         "mic-clamp", "amp-tray"]
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


p = json.loads((OUT / "owl-params.json").read_text(encoding="utf-8")) if (OUT / "owl-params.json").exists() else {}
if not p:
    fails.append("out-s3/owl-params.json khong co")
if p.get("variant") != "s3":
    fails.append('params variant phai "s3"')
for k, want in [("wall", 2.4), ("speaker_pocket_d", 52.6), ("grille_hole_d", 2.8), ("mic_hole_d", 2.0),
                ("button_cap_d", 50.0), ("button_hole_d", 50.8), ("diffuser_t", 0.8), ("vent_w", 2.0)]:
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
for old in ("speaker-bezel-L", "speaker-bezel-R", "speaker-ring-L", "speaker-ring-R"):
    if (OUT / f"{old}.stl").exists():
        fails.append(f"{old}.stl con trong out-s3 (ban S3 chi 1 loa)")

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

    # 1 loa o bung, truc y, mat loa huong -y (truoc)
    if len(sps) != 1:
        fails.append(f"ban S3 can dung 1 loa (speakers co {len(sps)})")
    else:
        s = sps[0]; c = Vector(s["center"])
        if s.get("axis") != "y" or abs(c.x) > 5 or c.y > Y0 - 25 or not 30 <= c.z <= 75:
            fails.append(f"loa phai o bung: axis y, |x|<=5, y <= {Y0-25:.1f}, z 30..75 (dang {s})")
        else:
            sc_ = p.get("speaker_clamp", {}); ft = sc_.get("flange_t", 5.0); bd = sc_.get("body_d_max", 39.0)
            face = c.y - 13.0                                    # mat loa phia -y
            if tree.overlap(dummy("cyl", (c.x, face + ft / 2, c.z), (52.0, ft - 0.2))):
                fails.append(f"loa: mep O52 x {ft} cham vo/vanh loa")
            if tree.overlap(dummy("cyl", (c.x, face + ft + (26.0 - ft) / 2, c.z), (bd, 26.0 - ft - 0.2))):
                fails.append(f"loa: than O{bd} cham vong ep/vo")

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
    # ampli MAX98357A (Adafruit 19,4 x 17,8; clone khac -> 22 x 22 x 10 kem cau dau + chan)
    amp = p.get("amp_center"); ad = p.get("amp_box")
    if not amp or not ad:
        fails.append("params can amp_center + amp_box")
    else:
        sd = sorted(float(x) for x in ad)
        if sd[0] < 10 or sd[1] < 22 or sd[2] < 22:
            fails.append(f"amp_box phai >= 22 x 22 x 10, dang {ad}")
        elif tree.overlap(dummy("box", amp, ad)):
            fails.append("khoi ampli cham vo tai amp_center")
    # mic INMP441 (PCB tron ~14-15 / vuong 14 x 14; nguon: ask-gpt 2026-11-12) -> o giu cho >= 17 x 17 x 8 sau lo tran
    mic = p.get("mic") or {}
    mc, mb = mic.get("center"), mic.get("box")
    if not mc or not mb:
        fails.append("params can mic.center + mic.box")
    else:
        sd = sorted(float(x) for x in mb)
        if sd[0] < 8 or sd[1] < 17 or sd[2] < 17:
            fails.append(f"mic.box phai >= 17 x 17 x 8, dang {mb}")
        elif tree.overlap(dummy("box", mc, mb)):
            fails.append("o mic cham vo tai mic.center")
        if mc[1] > Y0 - 20 or mc[2] < 100 or abs(float(mc[0])) > 1.0:
            fails.append(f"mic phai o MAT TRUOC, chinh giua (|x| <= 1), tran z >= 100: {mc}")
        if mic.get("axis", "y") != "y":
            fails.append("mic phai huong ra truoc (axis y)")
        if sps and (Vector(mc) - Vector(sps[0]["center"])).length < 60:
            fails.append("mic cach tam loa < 60 mm (vong nhieu)")
        if int(mic.get("holes", 0)) < 3:
            fails.append("tran can >= 3 lo mic O2")
        seal = mic.get("seal") or {}
        if seal.get("type") == "labyrinth":   # PETG: dau ong dan am cam vao go lom tren vach tran
            if float(seal.get("depth", 0)) < 0.8 or not 0.05 <= float(seal.get("clearance", 9)) <= 0.2:
                fails.append(f"mic khop me cung: go lom sau >= 0,8, khe 0,05-0,2 mm/ben: {seal}")
        elif float(mic.get("gasket_t", 0)) < 1.0:
            fails.append("mic can ron (gasket_t >= 1,0) hoac seal.type 'labyrinth' de tieng loa trong vo khong lot vao")
    if amp and sps and (Vector(amp) - Vector(sps[0]["center"])).length > 70:
        fails.append("ampli cach loa > 70 mm (day loa dai)")

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
        if not 0.2 <= bay["sleeve_clr"] <= 0.35: fails.append("khe ong tay 0,2-0,35")
        if bay["pin_clr"] < 0.2: fails.append("khe dau chot >= 0,2")
        if bay["pin_h"] < 0.8: fails.append("chot nho ra >= 0,8 mm")
        if not 20 <= bay["twist"] <= 45: fails.append("goc xoay khoa 20-45 do")
        if bay["groove_clr"] < 0.2: fails.append("ranh ngang can khe doc truc >= 0,2")
    if not sc_.get("petg_spring") and not 0.8 <= sc_.get("gasket_locked", 0) <= 1.4: fails.append("ron 2 mm khi khoa con 0,8-1,4 mm")
    if sc_.get("gasket_slot_kept") is not True: fails.append("giu ranh ron (gasket_slot_kept: true) de sau nay lap ron TPU khong ve lai")
    if sc_["ring_id"] <= sc_["body_d_max"]: fails.append("lo vong ep phai lon hon than loa")
    if sc_["ring_id"] >= 52.0 - 2 * 2.0: fails.append("vong ep phai de len mep loa >= 2 mm moi ben")

# ngam xoay lap duoc that: dung out-s3/asm (vi tri lap that), loa bung truc y, mat ra -y
bay = (sc_ or {}).get("bayonet")
bz_m, rg_m = load(OUT / "asm" / "speaker-bezel.stl"), load(OUT / "asm" / "speaker-ring.stl")
if bay and bz_m and rg_m and len(sps) == 1:
    c = Vector(sps[0]["center"])
    bz_tree = BVHTree.FromBMesh(bz_m)

    def hit(d_out, ang_deg):   # d_out > 0: day vong ep ve phia mat loa (-y); < 0: lui vao trong vo (+y)
        b = rg_m.copy()
        T = Matrix.Translation((0, -d_out, 0)) @ Matrix.Translation(c) @ Matrix.Rotation(math.radians(ang_deg), 4, 'Y') @ Matrix.Translation(-c)
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
        fails.append("ngam xoay khong lap duoc (khong co chieu vua lot ranh doc vua xoay het goc khoa)")
    else:
        print(f"ngam xoay: lap duoc (chieu {'+' if ok_dir > 0 else '-'}, {tw:.0f} do)")

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
rep = OUT.parent.parent / "print" / "plates-s3" / "print-report.json"
if rep.exists():
    try:
        r_ = json.loads(rep.read_text(encoding="utf-8"))
        bad_ = [b["ban"] for b in r_.get("ban", []) if b.get("trang_thai") != "PASS"]
        if bad_ or r_.get("stl_chua_xep"): fails.append(f"ban in chua PASS: {bad_} chua xep: {r_.get('stl_chua_xep')}")
    except Exception as e:
        fails.append(f"doc print-report.json loi {type(e).__name__}")
else:
    fails.append("chua co print/plates-s3/print-report.json - chay slice.py print/print-s3.yaml")
for f in ("owl-preview.png", "owl-exploded.png"):
    if not (OUT / f).exists():
        fails.append(f"out-s3/{f} khong co")
if fails:
    print("FAIL gate_owl_s3:"); [print(" -", x) for x in fails]; sys.exit(1)
print("PASS gate_owl_s3")
