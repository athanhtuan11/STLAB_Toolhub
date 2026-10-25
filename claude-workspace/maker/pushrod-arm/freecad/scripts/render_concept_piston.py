# CONCEPT xi-lanh PISTON (Tuan 2026-10-25: "thich co che dang piston, rat gon cho xe muc") thay thanh rang (Rack_Elbow lech).
# Hoc tu Cyberbrick Excavator (MakerWorld 2371626): ong + piston kep dai oc M3 + ty rong, ty ren M3 tu ham.
# Khac may xuc: motor CyberBrick 030 + hop so (khong N20 truc ren) dat CANH ong, banh rang z28 (truc hop so) -> z12 (dau ty ren).
# Ly do: dong truc thi khong du hanh trinh 36 mm trong L_min 92 mm (may xuc ~26 mm / ~100 mm).
# Hinh hoc tam trong bo nho, KHONG Luu pushrod_arm.FCStd (FC_SAVE_CONCEPT = luu BAN SAO de xem).
#   set FC_FILE=.../pushrod_arm.FCStd  set FC_SCRIPT=<file nay>  [set FC_SAVE_CONCEPT=<ban sao.FCStd>]
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode tools/robotics-cad/scripts/gui_run.py   (man hinh phu)
# He toa do xi-lanh = Placement Rack_<tag> tu the goc: x doc truc (goc = chot A/C), y // chot, z trong mat phang tay.
# Ra: freecad/images/concept-piston/*.png + _concept.json (va cham 9 tu the).
import json
import math
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector as V

FC = os.path.dirname(App.ActiveDocument.FileName)
OUT = os.path.join(FC, "images", "concept-piston")
os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(FC, "pushrod_arm_sim.FCMacro"), encoding="utf-8").read().split("class Panel", 1)[0]
G = {"__name__": "sim"}
exec(compile(src, "pushrod_arm_sim.FCMacro", "exec"), G)
set_pose, OBJ, REST = G["set_pose"], G["OBJ"], G["REST"]
LMIN, LMAX, L1MAX, L1_0, L2_0 = G["LMIN"], G["LMAX"], G["L1MAX"], G["L1_0"], G["L2_0"]
doc = App.ActiveDocument
STEP = ("D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/community/cyberbrick-official/models/"
        "la024-030-micro-dc-motor-with-sh1-0/030-micro-dc-motor-with-sh1-0-reducer.step")
OUT_G = V(0, 15.2, 11.15)   # tam truc ra tai mat vo hop so (he hop so, do tren STEP hang - xem 2026-10-24_cylinder_030_gearbox.py)
SHAFT_L, SHAFT_R, SHAFT_FLAT = 8.1, 2.65, 1.8
PIN_G = [(-9.0, -4.02), (9.0, -4.02)]   # 2 lo Ø4 nap hop so (he hop so x, z), truc // truc ra

FIT = 0.3                  # khe truot / an khop (Tuan 2026-10-24)
ZG, ZS_ = 28, 12           # banh rang truc hop so, banh rang ty ren (m1)
D = (ZG + ZS_) / 2         # 20 mm: hop so (nua rong 11) nam ngoai ong r 8,5
GW = 4.5                   # be rong banh rang
PIST_L, NUT_AF, NUT_T = 8.0, 5.5, 2.4    # piston dai, dai oc luc giac M3 (DIN 934)
ROD_Y, ROD_Z, ROD_R = 3.0, 4.0, 1.5      # ty: day 6 (= mat ty cu / rack, lot ranh Boom vai), cao 8, bo goc 1,5
BORE_SCREW = 1.8                         # lo ty ren M3 trong ty (Ø3,6)
BUSH_L = 6.0

CFG = {  # x0 = dau tuong sau buong banh rang; r_tube; bore = canh lo vuong piston; Lmin/L0/Lmax; zs = phia hop so
    "Elbow": dict(x0=18.0, r_tube=8.5, bore=11.0, Lmin=LMIN, L0=L2_0, Lmax=LMAX, zs=1, pins=("C", "D")),
    "Shoulder": dict(x0=11.0, r_tube=7.0, bore=9.4, Lmin=LMIN, L0=L1_0, Lmax=L1MAX, zs=-1, pins=("A", "B")),
}
A20 = math.radians(20)


def invf(a): return math.tan(a) - a


def gear_pts(cy, cz, z, m=1.0, ph=0.0, bl=0.15, n_=6):   # nhu 2026-10-22_build_pushrods_v3.py (x = 0), mat phang y-z
    rp = m * z / 2; rb = rp * math.cos(A20); ra = rp + m; rf = rp - 1.25 * m
    psi = (math.pi / 2) / z - bl / (2 * rp); r0 = max(rb, rf)
    def th(r): return psi + invf(A20) - invf(math.acos(min(1, rb / r)))
    pts = []
    for i in range(z):
        c = math.radians(ph) + 2 * math.pi * i / z; rs = [r0 + (ra - r0) * k / n_ for k in range(n_ + 1)]
        if rf < rb: pts.append((rf, c - th(rb)))
        pts += [(r, c - th(r)) for r in rs] + [(r, c + th(r)) for r in reversed(rs)]
        if rf < rb: pts.append((rf, c + th(rb)))
        a0 = c + th(r0); a1 = c + 2 * math.pi / z - th(r0); pts += [(rf, a0 + (a1 - a0) * k / 3) for k in range(1, 3)]
    return [(cy + r * math.cos(a), cz + r * math.sin(a)) for r, a in pts]


def prism_x(pts, x0, x1):   # da giac (y, z) dun doc x
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(x1 - x0, 0, 0))


def xcyl(r, x0, x1, y=0.0, z=0.0): return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def rrect(hy, hz, r, x0, x1):   # hinh chu nhat bo goc doc x, tam truc
    s = box(x0, x1, -hy + r, hy - r, -hz, hz).fuse(box(x0, x1, -hy, hy, -hz + r, hz - r))
    for sy in (-1, 1):
        for sz in (-1, 1):
            s = s.fuse(xcyl(r, x0, x1, sy * (hy - r), sz * (hz - r)))
    return s.removeSplitter()


def hexagon(af, x0, x1, rot=0.0):
    rc = af / math.sqrt(3)
    return prism_x([(rc * math.cos(math.radians(rot + 60 * k)), rc * math.sin(math.radians(rot + 60 * k))) for k in range(6)], x0, x1)


def build(tag, c):
    """Chi tiet trong he xi-lanh, tu the goc (L0). Tra dict ten -> (shape, nhom 'H' gan vo | 'R' theo ty)."""
    zs, x0, rt, bore = c["zs"], c["x0"], c["r_tube"], c["bore"]
    xg0, xg1 = x0 + 1.5, x0 + 1.5 + GW + 0.5           # khoang banh rang (khe 0,25 moi ben)
    xw1 = xg1 + 1.5                                      # het tuong truoc
    xface = xw1 + 0.5                                    # mat vo hop so (quay ve -x)
    xp_ret = xw1 + 0.5                                   # duoi piston khi rut het
    stroke = c["Lmax"] - c["Lmin"]
    xt1 = xp_ret + PIST_L + stroke + BUSH_L              # het ong
    off = c["L0"] - c["Lmin"]                            # ty o tu the goc lech khoi rut het
    gz = zs * D
    # ---- vo (Cyl_Housing): tai chot cu + co + buong banh rang + ong + bac dan huong + tam ga hop so ----
    old = OBJ["Housing_" + tag].Shape.copy(); old.transformShape(REST[OBJ["Rack_" + tag].Name].inverse().toMatrix())
    lug = old.common(box(-8, 9.5, -3.5, 3.5, -9, 9))
    neck = box(6, x0 + 0.5, -3, 3, -5.5, 5.5)
    cham = xcyl(8.7, x0, xw1).cut(xcyl(7.6, xg0, xg1)).fuse(xcyl(8.7, x0, xg0))     # vo buong + tuong sau dac
    cham = cham.cut(box(xg0, xg1, -9.5, 9.5, zs * 3.5, zs * 40))                     # cua so: z28 an vao + tha banh rang
    cham = cham.cut(box(xg1 - 0.1, xw1 + 0.1, -BORE_SCREW, BORE_SCREW, 0, zs * 20))  # rang chu U tuong truoc cho ty ren
    tube = xcyl(rt, xw1 - 0.5, xt1).cut(rrect(bore / 2, bore / 2, 2.0, xw1, xt1 - BUSH_L))
    tube = tube.cut(rrect(ROD_Y + FIT, ROD_Z + FIT, ROD_R + FIT, xt1 - BUSH_L - 0.1, xt1 + 0.1))
    tube = tube.cut(xcyl(BORE_SCREW, xg1, xw1 + 0.6))
    # tam ga hop so: mat vo hop so (STEP: x +-11, z -32,2..22,15 quanh truc ra z 11,15 -> he xi-lanh y -11..43, z gz+-11)
    plate = box(xface - 2.0, xface, -11, 43.3, gz - 11, gz + 11).cut(xcyl(3.2, xface - 2.1, xface + 0.1, 0, gz))
    pegs = [xcyl(1.95, xface, xface + 5, 15.17, gz + zs * px) for px, _ in PIN_G]   # 2 vau Ø3,9 vao lo Ø4 nap hop so
    web = box(xw1 - 0.5, xface, -3, 3, 0, gz)                                        # noi tam ga voi ong
    hous = lug.fuse([neck, cham, tube, plate, web] + pegs).removeSplitter()
    hous = hous.cut(xcyl(5.6, xg0 - 0.1, xg1 + 0.1, 0, gz))                           # khong cham z28 (dinh r 15)
    # ---- hop so 030 (STEP hang): he hop so -> he xi-lanh: c_x = -g_y, c_y = -g_z, c_z = g_x (det +1), truc ra quay -x ----
    gb = Part.read(STEP)
    M = App.Matrix(0, -1, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 1)
    gb = gb.transformGeometry(M)
    o = M.multiply(OUT_G); gb.translate(V(xface, 0, gz) - V(o.x, o.y, o.z))
    # ---- banh rang ----
    sock = xcyl(SHAFT_R + 0.32 / 2, xg0 - 1, xg1 + 1, 0, gz).common(box(xg0 - 1, xg1 + 1, -9, 9, gz - SHAFT_FLAT - 0.16, gz + SHAFT_FLAT + 0.16))
    g28 = prism_x(gear_pts(0, gz, ZG), xg0 + 0.25, xg1 - 0.25).cut(sock)   # truc ra 8,1 mm phu het be rong banh rang
    ph12 = min((prism_x(gear_pts(0, 0, ZS_, ph=k * 3.75), xg0 + 0.25, xg1 - 0.25).common(g28).Volume, k * 3.75)
               for k in range(8))[1]   # pha z12: it chong lan voi z28 nhat
    g12 = prism_x(gear_pts(0, 0, ZS_, ph=ph12), xg0 + 0.25, xg1 - 0.25).cut(hexagon(NUT_AF + 0.2, xg0, xg0 + 2.6)).cut(xcyl(1.6, xg0 - 1, xg1 + 1))
    nut_g = hexagon(NUT_AF, xg0 + 0.25, xg0 + 0.25 + NUT_T).cut(xcyl(1.5, xg0, xg0 + 3))
    nut_pos = xp_ret + PIST_L / 2
    screw_x1 = nut_pos + stroke + NUT_T / 2 + 2.5
    screw = xcyl(1.5, xg0 + 0.25, screw_x1)
    # ---- piston + ty (theo tu the goc: +off) ----
    xp = xp_ret + off
    sp = bore - 2 * FIT
    piston = rrect(sp / 2, sp / 2, 1.8, xp, xp + PIST_L)
    piston = piston.cut(hexagon(NUT_AF + 0.2, xp + PIST_L / 2 - (NUT_T + 0.3) / 2, xp + PIST_L / 2 + (NUT_T + 0.3) / 2, 30)
                        .fuse(box(xp + PIST_L / 2 - (NUT_T + 0.3) / 2, xp + PIST_L / 2 + (NUT_T + 0.3) / 2, -(NUT_AF + 0.2) / 2, (NUT_AF + 0.2) / 2, 0, -zs * sp)))
    L0 = c["L0"]
    rack = OBJ["Rack_" + tag].Shape.copy(); rack.transformShape(REST[OBJ["Rack_" + tag].Name].inverse().toMatrix())
    eye = rack.common(box(L0 - 6.5, L0 + 9, -3.5, 3.5, -9, 9))
    rod = piston.fuse([rrect(ROD_Y, ROD_Z, ROD_R, xp + PIST_L - 0.5, L0 - 5.0), eye]).removeSplitter()
    rod = rod.cut(xcyl(BORE_SCREW, xp - 0.1, screw_x1 + off + 0.8))
    nut_p = hexagon(NUT_AF, xp + PIST_L / 2 - NUT_T / 2, xp + PIST_L / 2 + NUT_T / 2, 30).cut(xcyl(1.5, xp, xp + PIST_L))
    info = dict(stroke=stroke, tube_end=round(xt1, 1), tube_od=2 * rt, screw_len=round(screw_x1 - xg0 - 0.25, 1),
                piston_ret=[round(xp_ret, 1), round(xp_ret + PIST_L, 1)], eye_clear_ret=round(c["Lmin"] - xt1, 1),
                rod_bore_end_rest=round(screw_x1 + off + 0.8, 1), mm_per_out_rev=round(0.5 * ZG / ZS_, 2))
    parts = {"Cyl_Housing": (hous, "H"), "CB_030_gearbox_new": (gb, "H"), "Gear_z28": (g28, "H"), "Gear_z12_screw": (g12, "H"),
             "Nut_M3_gear": (nut_g, "H"), "Screw_M3": (screw, "H"), "Piston_rod": (rod, "R"), "Nut_M3_piston": (nut_p, "R")}
    return parts, info


NEW = {}; INFO = {}
for tag, c in CFG.items():
    parts, INFO[tag] = build(tag, c)
    R = REST[OBJ["Rack_" + tag].Name]
    for name, (sh, grp) in parts.items():
        s = sh.copy(); s.transformShape(R.toMatrix())
        o = doc.addObject("Part::Feature", "%s_%s" % (name, tag)); o.Label = "%s_%s" % (name, tag); o.Shape = s
        NEW[o.Label] = (o, tag, grp)
OLD = {l for t in CFG for l in G["ROD" + ("1" if t == "Shoulder" else "2")]} | {"Pin_gearbox_Shoulder", "Pin_gearbox_Elbow"}
OLD = {l for l in OLD if l in OBJ}


def pose(L1, L2):
    ok = set_pose(0, L1, L2, 0, update=False)
    for lbl, (o, tag, grp) in NEW.items():
        H = OBJ["Housing_" + tag]; Mr = H.Placement.multiply(REST[H.Name].inverse())   # vo cu chi xoay quanh chot sau
        if grp == "R":
            L = L1 if tag == "Shoulder" else L2; u = Mr.Rotation.multVec(REST[OBJ["Rack_" + tag].Name].Rotation.multVec(V(1, 0, 0)))
            Mr = App.Placement(u * (L - CFG[tag]["L0"]), App.Rotation()).multiply(Mr)
        o.Placement = Mr
    return ok


def obstacles(tag):
    p0, p1 = CFG[tag]["pins"]
    out = [o for l, o in OBJ.items() if l not in OLD and not l.startswith(("Pin_" + p0, "Pin_" + p1, "M2_5"))]
    out += [o for l, (o, t, g) in NEW.items() if t != tag]
    return out


POSES = [(a, b) for a in (LMIN, L1_0, L1MAX) for b in (LMIN, L2_0, LMAX)]
log = {"info": INFO, "poses": []}
for L1, L2 in POSES:
    pose(L1, L2); hits = []
    for lbl, (o, tag, grp) in NEW.items():
        for ob in obstacles(tag):
            if not o.Shape.BoundBox.intersect(ob.Shape.BoundBox): continue
            v = o.Shape.common(ob.Shape).Volume
            if v > 0.05: hits.append([lbl, ob.Label, round(v, 1)])
    for tag in CFG:   # ben trong: ty/piston khong cham vo, banh rang
        own = {l: o for l, (o, t, g) in NEW.items() if t == tag}
        for a, b in (("Piston_rod", "Cyl_Housing"), ("Piston_rod", "Screw_M3"), ("Gear_z28", "Cyl_Housing"),
                     ("Gear_z12_screw", "Cyl_Housing"), ("Gear_z28", "Gear_z12_screw"), ("Piston_rod", "Gear_z12_screw")):
            v = own["%s_%s" % (a, tag)].Shape.common(own["%s_%s" % (b, tag)].Shape).Volume
            if v > 0.05: hits.append(["%s_%s" % (a, tag), "%s_%s" % (b, tag), round(v, 1)])
    log["poses"].append({"L1": round(L1, 1), "L2": round(L2, 1), "hits": hits})
json.dump(log, open(os.path.join(OUT, "_concept.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- render ----------------
COL = {"Cyl_Housing": (0.78, 0.80, 0.84), "CB_030_gearbox_new": (0.20, 0.45, 0.85), "Gear_z28": (0.85, 0.15, 0.15),
       "Gear_z12_screw": (0.98, 0.76, 0.10), "Nut_M3": (0.35, 0.35, 0.38), "Screw_M3": (0.55, 0.55, 0.60),
       "Piston_rod": (0.60, 0.35, 0.75)}
for o in doc.Objects:
    if o.isDerivedFrom("Part::Feature") and o.ViewObject:
        o.ViewObject.LineColor = (0.15, 0.15, 0.15)
        for k, cl in COL.items():
            if o.Label.startswith(k): o.ViewObject.ShapeColor = cl
v = Gui.ActiveDocument.ActiveView
v.setAnimationEnabled(False)
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.ViewObject]
HIDE = OLD | {l for l in OBJ if l.startswith("M2_5")}


def cutaway(tag):   # nua y < 0 cua chi tiet minh ve (hop so STEP giu nguyen) de nhin ben trong tu phia -Y
    out = []
    for lbl, (o, t, g) in NEW.items():
        if t != tag or lbl.startswith("CB_030"): continue
        H = o.Placement; R = REST[OBJ["Rack_" + tag].Name]
        cut = box(-50, 200, 0, 100, -100, 100); cut.transformShape(H.multiply(R).toMatrix())
        c = doc.addObject("Part::Feature", "cut_" + lbl); c.Shape = o.Shape.common(cut)
        c.ViewObject.ShapeColor = o.ViewObject.ShapeColor; c.ViewObject.LineColor = (0.15, 0.15, 0.15); out.append(c)
    return out


def shot(fn, fit, show, cam, transp=None, size=(1400, 1000)):
    transp = transp or {}
    allp = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.ViewObject]
    vis = lambda o, s: (s is None or o.Label in s) and o.Label not in HIDE
    {"iso": v.viewIsometric, "front": v.viewFront}[cam]()
    for o in allp: o.ViewObject.Visibility = vis(o, fit)
    Gui.updateGui(); v.fitAll(); Gui.updateGui()
    for o in allp:
        o.ViewObject.Visibility = vis(o, show); o.ViewObject.Transparency = transp.get(o.Label, 0)
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, fn + ".png"), size[0], size[1], "White")


n = 1
for tag in ("Elbow", "Shoulder"):
    own = {l for l, (o, t, g) in NEW.items() if t == tag}
    for nm, L in (("retracted", CFG[tag]["Lmin"]), ("extended", CFG[tag]["Lmax"])):
        pose(L if tag == "Shoulder" else L1_0, L if tag == "Elbow" else L2_0)
        shot("%02d-%s-%s-iso" % (n, tag.lower(), nm), own, own, "iso"); n += 1
        cs = cutaway(tag); names = {c.Label for c in cs} | {"CB_030_gearbox_new_" + tag}
        shot("%02d-%s-%s-cutaway" % (n, tag.lower(), nm), names, names, "front", {"CB_030_gearbox_new_" + tag: 70}); n += 1
        for c in cs: doc.removeObject(c.Name)
CTX = {l for l in NEW} | {"Boom001", "Turret_one_piece", "Forearm_plate_L", "Forearm_plate_R", "Pin_A", "Pin_B", "Pin_C", "Pin_D", "Pin_E"}
for nm, L1, L2 in (("rest", L1_0, L2_0), ("both-in", LMIN, LMIN), ("both-out", L1MAX, LMAX)):
    pose(L1, L2); shot("%02d-full-%s" % (n, nm), None, None, "front", {}, (1200, 900)); n += 1
pose(L1_0, L2_0)
shot("%02d-arm-iso" % n, CTX, None, "iso", {"Boom001": 40}); n += 1

SAVE = os.environ.get("FC_SAVE_CONCEPT")   # BAN SAO de Tuan xem (file goc khong doi)
if SAVE:
    for o in parts:
        o.ViewObject.Visibility = o.Label not in HIDE; o.ViewObject.Transparency = 0
    v.viewIsometric(); v.fitAll()
    doc.saveAs(SAVE)
