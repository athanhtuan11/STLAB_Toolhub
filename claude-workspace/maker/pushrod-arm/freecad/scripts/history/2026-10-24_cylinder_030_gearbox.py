# CLI (freecadcmd --safe-mode): xi-lanh vai/khuyu doi N20 -> CyberBrick 030 + hop giam toc 1 truc (STEP hang),
# bo cuc B (motor chia ngang +Y). Tuan 2026-10-24: "khong phai N20 ma la motor cua cyber brick", "ve lai nhung ko
# lam thay doi bo phan khac qua nhieu vi toi da in het", "Tang do rong khi gan co cau banh rang va truot" (0,3 mm).
# Chi in lai: Housing_*, Worm_* (+ 2 chot Pin_gearbox_* moi ben). Rack, Pinion_WormWheel, Boom, Turret... GIU NGUYEN.
# He toa do RIENG xi-lanh = Placement cua Rack_<tag> o tu the goc: x doc thanh rang (goc = chot A/C),
# truc vit y 9.4, z = zs*20.25; banh vit truc // y tai x 60, z = zs*8.25 (zs = -1 vai, +1 khuyu).
import math
import sys
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
STEP = ("D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/community/cyberbrick-official/models/"
        "la024-030-micro-dc-motor-with-sh1-0/030-micro-dc-motor-with-sh1-0-reducer.step")
FIT = 0.3                 # khe lap banh rang / truot (Tuan 2026-10-24)
WALL = 2.0
YW = 9.4                  # truc vit (y)
WX0, WX1, WR = 56.2, 63.85, 5.0   # rang truc vit (giu nguyen)
FACE_X = 44.6             # mat hop so: truc ra Ø5,3 nho 8,1 mm -> dau truc 52,7, day lo 53,0, moay-o kin den 54
SHAFT_L, SHAFT_R, SHAFT_FLAT = 8.1, 2.65, 1.8   # do tren STEP hang: Ø5,3, 2 mat vat cach 3,6
HUB_R, HUB_X1 = 4.5, 54.0 # moay-o truc vit (r 4,5 den x 54: cach banh vit 0,6)
CASE = dict(x=(-11.0, 11.0), y=(-2.8, 15.2), z=(-32.2, 22.15))   # vo hop so (STEP hang), he hop so
OUT = V(0, 15.2, 11.15)   # tam truc ra tai mat vo (he hop so)
PIN_G = [(-9.0, -4.02), (9.0, -4.02)]   # 2 lo Ø4 tren nap hop so (he hop so x, z), truc // Y
PIN_R, PIN_HOLE_R = 1.95, 2.05
WHEEL_TIP_R = 9.0         # banh vit m1 z16

doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-cylinder-030-gearbox")
O = {o.Label: o for o in doc.Objects}
step = Part.read(STEP)


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def xcyl(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def to_world(shape, R):
    """He xi-lanh -> the gioi, GIU obj.Placement = I (rest.json): transformShape cung chi gan Placement cho shape,
    gan vao obj thi FreeCAD day Placement do sang obj -> mo phong dat sai. Goi trong compound de giu vi tri."""
    s = shape.copy(); s.transformShape(R.toMatrix())
    return s if s.Placement.isSame(App.Placement(), 1e-9) else Part.makeCompound([s])


def gearbox_local(zs):
    """Placement hop so trong he xi-lanh: Y hop so -> +x (truc ra huong truc vit), Z hop so -> -y (motor chia +Y)."""
    gx, gy, gz = V(0, 0, -1), V(1, 0, 0), V(0, -1, 0)
    rot = App.Rotation(App.Matrix(gx.x, gy.x, gz.x, 0, gx.y, gy.y, gz.y, 0, gx.z, gy.z, gz.z, 0, 0, 0, 0, 1))
    base = V(FACE_X, YW, zs * 20.25) - rot.multVec(OUT)
    return App.Placement(base, rot)


def flat_dir():
    """Phap tuyen mat vat truc ra (he hop so, trong mat X-Z): quet goc o r 2,4 tim 2 cung ngoai doi xung,
    lay trung binh goc NHAN DOI (khong loi khi cung vat qua 0 do)."""
    sol = [s for s in step.Solids if abs(s.BoundBox.YMax - 23.3) < 0.05][0]
    out = [math.radians(k) for k in range(360) if not sol.isInside(
        V(2.4 * math.cos(math.radians(k)), 20.0, 11.15 + 2.4 * math.sin(math.radians(k))), 1e-4, True)]
    assert out, "khong thay mat vat tren truc ra"
    a = math.atan2(sum(math.sin(2 * t) for t in out), sum(math.cos(2 * t) for t in out)) / 2
    return V(math.cos(a), 0, math.sin(a))


rep = {}
for tag, zs in (("Shoulder", -1), ("Elbow", 1)):
    R = O["Rack_" + tag].Placement          # he xi-lanh -> the gioi
    zc = zs * 20.25
    G = gearbox_local(zs)                   # he hop so -> he xi-lanh
    W = R.multiply(G)                       # he hop so -> the gioi

    # --- hop so (linh kien mua + vo in theo file CyberBrick) ---
    gb = doc.addObject("Part::Feature", "CB_030_gearbox_" + tag)
    gb.Label = "CB_030_gearbox_" + tag
    gb.Shape = step.copy()
    gb.Placement = W
    gb.Label2 = "CyberBrick 030 Micro DC Motor LA024 + Single-axis Reduction Gear Kit (vo in theo file hang)"

    # --- truc vit: giu rang, them moay-o + lo vat 2 mat cho truc ra ---
    wo = O["Worm_" + tag]
    wl = wo.Shape.copy(); wl.transformShape(R.inverse().toMatrix())       # ve he xi-lanh
    x_hub0 = FACE_X + FIT
    hub = xcyl(HUB_R, x_hub0, HUB_X1, YW, zc).fuse(xcyl(2.6, HUB_X1 - 0.5, WX0 + 0.5, YW, zc))
    fd = flat_dir()
    nd = G.Rotation.multVec(fd); nd.normalize()                            # phap tuyen mat vat (he xi-lanh)
    # do THAT phan truc nho khoi mat vo (B-rep, he hop so): ban kinh lon nhat + khoang cach lon nhat theo phap tuyen
    # (lan dau dung so uoc 2,65 / 1,8 -> khe that chi 0,2 o goc mat vat)
    sol = [q for q in step.Solids if abs(q.BoundBox.YMax - 23.3) < 0.05][0]
    # chan truc co go tron Ø5,3 dai ~0,1 mm -> do mat vat tu 0,5 mm tro len (lan 2: do ca go -> mat vat = 2,65 = lo tron!)
    pr = sol.common(Part.makeBox(30, 30, 30, V(-15, OUT.y + 0.5, OUT.z - 15)))
    pts = [p for e in pr.Edges for p in e.discretize(Deflection=0.005)]
    SHAFT_R = max(math.hypot(p.x, p.z - OUT.z) for p in pts)
    SHAFT_FLAT = max(abs(p.x * fd.x + (p.z - OUT.z) * fd.z) for p in pts)
    rep.setdefault("shaft", (round(SHAFT_R, 3), round(SHAFT_FLAT, 3)))
    assert SHAFT_FLAT < SHAFT_R - 0.3, ("khong do duoc mat vat", SHAFT_R, SHAFT_FLAT)
    collar = xcyl(SHAFT_R + FIT, x_hub0 - 1, FACE_X + 0.5, YW, zc)                  # go tron chan truc
    sock = xcyl(SHAFT_R + FIT, x_hub0 - 1, FACE_X + SHAFT_L + FIT, YW, zc)
    slab = box(x_hub0 - 1, FACE_X + SHAFT_L + FIT, -10, 10, -SHAFT_FLAT - FIT, SHAFT_FLAT + FIT)  # tam goc
    slab.rotate(V(0, 0, 0), V(1, 0, 0), math.degrees(math.atan2(-nd.y, nd.z)))  # quay x: (0,0,1) -> nd
    slab.translate(V(0, YW, zc))
    sock = sock.common(slab).fuse(collar)
    worm_new = wl.fuse(hub).removeSplitter().cut(sock)
    worm_new = to_world(worm_new, R)
    v0 = wo.Shape.Volume
    se.apply(wo, worm_new)

    # --- vo xi-lanh ---
    ho = O["Housing_" + tag]
    hl = ho.Shape.copy(); hl.transformShape(R.inverse().toMatrix())
    cx0, cx1 = FACE_X - (CASE["y"][1] - CASE["y"][0]) - FIT, FACE_X + FIT     # trong vo hop so + khe
    y_pin = YW - (PIN_G[0][1] - OUT.z)
    y_top = y_pin + PIN_HOLE_R + 3.0
    case_y0 = YW - (CASE["z"][1] - OUT.z) - FIT
    cradle = box(cx0 - WALL, cx1 + WALL, case_y0 - WALL, y_top, zc - 11.0 - FIT - WALL, zc + 11.0 + FIT + WALL)
    # goi chan dau truc vit: thanh doc theo day + tam chan (tranh banh vit: z cach truc banh vit >= tip + 0.5)
    zA, zB = sorted((zc + zs * 3.0, zs * (8.25 + WHEEL_TIP_R + 0.5)))   # tu phia xa banh vit -> bien banh vit + 0,5
    stop_x0 = WX1 + FIT
    bar = box(cx1 + WALL - 0.5, stop_x0 + 2.0, case_y0 - WALL, case_y0 - WALL + 3.0, zA, zB)
    plate = box(stop_x0, stop_x0 + 2.0, case_y0 - WALL, YW + 3.0, zA, zB)
    hl = hl.fuse([cradle, bar, plate]).removeSplitter()
    cuts = [
        box(cx0, cx1, case_y0, y_top + 1, zc - 11.0 - FIT, zc + 11.0 + FIT),             # vo hop so
        xcyl(HUB_R + FIT, cx1 - 0.1, HUB_X1 + FIT, YW, zc),                              # rang U cho moay-o
        box(cx1 - 0.1, HUB_X1 + FIT, YW, y_top + 1, zc - HUB_R - FIT, zc + HUB_R + FIT),
        xcyl(2.6 + FIT, HUB_X1, WX0, YW, zc),                                            # co truc + duong truot vao
        box(HUB_X1, WX0, YW, y_top + 1, zc - 2.6 - FIT, zc + 2.6 + FIT),
        xcyl(WR + FIT, WX0 - FIT, WX1 + FIT, YW, zc),                                    # rang truc vit + duong truot vao
        box(WX0 - FIT, WX1 + FIT, YW, y_top + 1, zc - WR - FIT, zc + WR + FIT),
        box(15.7, 75.0, -3.0 - FIT, 3.0 + FIT, -6.0 - FIT, 6.0 + FIT),                  # ranh thanh rang (0,3)
    ]
    for gxz in PIN_G:                                                                    # 2 lo chot qua thanh dau
        zz = zc - gxz[0]
        cuts.append(xcyl(PIN_HOLE_R, cx0 - WALL - 1, cx1 + WALL + 1, y_pin, zz))
    # banh vit + pinion quay: bao tron xoay (r(y) + 0,3) -> lo / hoc trong vo
    pw = O["Pinion_WormWheel_" + tag].Shape.copy(); pw.transformShape(R.inverse().toMatrix())
    ax = V(60, 0, zs * 8.25)
    yb = pw.BoundBox
    y = yb.YMin
    while y < yb.YMax:
        sl = pw.common(box(40, 80, y, y + 0.25, -40, 40))
        if not sl.isNull() and sl.Volume > 1e-6:
            r = max(math.hypot(p.X - ax.x, p.Z - ax.z) for p in sl.Vertexes) if sl.Vertexes else 0
            cuts.append(Part.makeCylinder(r + FIT, 0.25 + 2 * FIT, V(ax.x, y - FIT, ax.z), V(0, 1, 0)))
        y += 0.25
    h_new = hl.cut(cuts).removeSplitter()
    h_new = to_world(h_new, R)
    rep[tag] = {"housing_mm3": (round(ho.Shape.Volume), round(h_new.Volume)), "worm_mm3": (round(v0), round(worm_new.Volume)),
                "solids": len(h_new.Solids), "valid": h_new.isValid()}
    assert h_new.isValid() and len(h_new.Solids) == 1 and len(worm_new.Solids) == 1, rep[tag]
    assert ho.Placement.isSame(App.Placement(), 1e-6) and wo.Placement.isSame(App.Placement(), 1e-6), "Housing/Worm phai Placement = I"
    se.apply(ho, h_new)

    # --- 2 chot khoa hop so (in) ---
    pins = []
    for gxz in PIN_G:
        zz = zc - gxz[0]
        p = xcyl(PIN_R, FACE_X - 7.0, cx1 + WALL, y_pin, zz).fuse(xcyl(3.0, cx1 + WALL, cx1 + WALL + 1.5, y_pin, zz))
        pins.append(to_world(p, R))
    pg = doc.addObject("Part::Feature", "Pin_gearbox_" + tag)
    pg.Label = "Pin_gearbox_" + tag
    pg.Shape = Part.makeCompound(pins)
    pg.Label2 = "2 chot Ø3,9 khoa hop so 030 vao vo xi-lanh (dut tu ngoai vao lo Ø4 nap hop so)"

    # --- bo N20 ---
    grp = [g for g in O["CB_N20_" + tag].InList if g.isDerivedFrom("App::DocumentObjectGroup")]
    for g in grp:
        g.addObject(gb); g.addObject(pg)
    doc.removeObject(O["CB_N20_" + tag].Name)

doc.recompute()
for o in doc.Objects:  # Placement sau sua phai trung rest.json; them object moi vao rest.json (mo phong)
    if o.Label in ("Worm_Shoulder", "Worm_Elbow", "Housing_Shoulder", "Housing_Elbow"):
        assert o.Placement.isSame(App.Placement(), 1e-6), o.Label
import json  # noqa: E402
rp = P + "pushrod_arm_rest.json"
rest = json.load(open(rp))
for o in doc.Objects:
    if o.Label.startswith(("CB_030_gearbox_", "Pin_gearbox_", "CB_XA003_XA004_receiver", "Receiver_riser")):
        rest[o.Name] = [list(o.Placement.Base), list(o.Placement.Rotation.Q)]
for k in [k for k in rest if not doc.getObject(k)]:
    del rest[k]  # object da xoa (N20, XA004 cu...)
json.dump(rest, open(rp, "w"))
print("RES", rep)
print("RES saved", se.save(doc, gui_from=bk), "backup", bk)
