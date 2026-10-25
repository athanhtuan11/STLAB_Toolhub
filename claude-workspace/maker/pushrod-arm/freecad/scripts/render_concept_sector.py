# Anh MO PHONG phuong an E bo cuc (2) (Tuan chon 2026-10-25): quat nho tai khop khuyu, kieu Cyberbrick Excavator,
# thay Rack_Elbow (Rack bi lech khi Tuan thu). Chi la concept: hinh hoc tam trong bo nho, KHONG Luu .FCStd.
#   set FC_FILE=.../pushrod_arm.FCStd  set FC_SCRIPT=<file nay>  [set FC_OUT=<log>]
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode tools/robotics-cad/scripts/gui_run.py
# Bo cuc:
#   - Quat m1 z50 (r 25) tam = chot E, bat ngoai Forearm_plate_R (y -20,25..-15), quay theo cang tay.
#   - Banh rang kep z30/z12 (cap giam toc moi) tren truc gan vo xi-lanh: z30 an z10 cu, z12 an quat. Thang hang E-kep-z10.
#   - Cum xi-lanh khuyu (vo, hop so 030, truc vit, banh vit + z10 DA IN) bat CUNG vao Boom: doi gan E 10,6 mm (z10 cach E
#     51 = 31 + 20) va doi ngang DY de z10 + z30 o mat phang ngoai (y -26..-21), banh vit roi vao mat phang quat.
#   - Ti so khuyu/z10 = 10/30 * 12/50 = 0,08 (28,8 deg/vong z10).
# Vi sao khong de o mat giua: Boom001 dac o goc 220..240 deg quanh E (r 40..58) -> quat quet vao khi gap khuyu.
# Ra: freecad/images/concept-e-sector/*.png + _concept.json (va cham + chong lan rang tung tu the).
import json
import math
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector as V

FC = os.path.dirname(App.ActiveDocument.FileName)
OUT = os.path.join(FC, "images", "concept-e-sector")
os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(FC, "pushrod_arm_sim.FCMacro"), encoding="utf-8").read().split("class Panel", 1)[0]
G = {"__name__": "sim"}
exec(compile(src, "pushrod_arm_sim.FCMacro", "exec"), G)
set_pose, rot, S, E, YAXIS, OBJ, REST = G["set_pose"], G["rot"], G["S"], G["E"], G["YAXIS"], G["OBJ"], G["REST"]
FORE, ST = G["FORE"], G["STATE"]
L1_0, L2_0, LMIN, L1MAX = G["L1_0"], G["L2_0"], G["LMIN"], G["L1MAX"]
doc = App.ActiveDocument

ZS, ZB, ZA, ZP = 50, 12, 30, 10           # quat, kep nho, kep lon, z10 cu (m1)
RS, RB, RA, RP = ZS / 2, ZB / 2, ZA / 2, ZP / 2
DC = RS + RB                              # E -> truc kep = 31
DP = DC + RA + RP                         # E -> z10 = 51 (cu 61,6)
YQ = (-20.25, -15.0)                      # mat phang quat + z12 (ap mat ngoai Forearm_plate_R y -15)
YO = (-26.0, -21.0)                       # mat phang z10 + z30
PC0 = OBJ["Rack_Elbow"].Placement.multVec(V(60, 0, 8.25))      # tam z10 hien tai (tu the goc)
U = PC0 - E; U.y = 0; U.normalize()
TH0 = math.degrees(math.atan2(U.z, U.x)) % 360                # ~198,5 deg
PC = E + U * DP; CC = E + U * DC
DY = (YO[0] + YO[1]) / 2                                       # z10 y -2,5..2,5 -> YO
SHIFT = V(PC.x - PC0.x, DY, PC.z - PC0.z)
PSI = (-63.5, 14.6)                                            # khoang goc khuyu (kinematics-test, L2 92..128)
T0, T1 = TH0 + PSI[0] - 8, TH0 + PSI[1] + 8                   # cung rang quat (he cang tay, tu the goc)
K_C, K_P = -ZS / ZB, ZS / ZB * ZA / ZP                         # goc kep, goc z10 theo goc khuyu psi

A20 = math.radians(20)


def invf(a): return math.tan(a) - a


def gear_pts(cx, cz, z, m=1.0, ph=0.0, bl=0.15, n_=6):   # nhu 2026-10-22_build_pushrods_v3.py (x = 0)
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
    return [(cx + r * math.cos(a), cz + r * math.sin(a)) for r, a in pts]


def prism(pts, y0, y1):
    w = Part.makePolygon([V(x, y0, z) for x, z in pts] + [V(pts[0][0], y0, pts[0][1])])
    return Part.Face(w).extrude(V(0, y1 - y0, 0))


def wedge(c, r0, r1, a0, a1, y0, y1, n=48):
    arc = lambda r: [(c.x + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), c.z + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
                     for k in range(n + 1)]
    return prism(arc(r1) + (arc(r0)[::-1] if r0 > 0 else [(c.x, c.z)]), y0, y1)


def ycyl(c, r, y0, y1): return Part.makeCylinder(r, y1 - y0, V(c.x, y0, c.z), V(0, 1, 0))


def sector(ph):
    y0, y1 = YQ
    teeth = prism(gear_pts(E.x, E.z, ZS, ph=ph), y0, y1).common(wedge(E, 0, RS + 2, T0, T1, y0 - 1, y1 + 1))
    s = teeth.fuse([wedge(E, 0, RS - 1.25, T0 - 4, T1 + 4, y0, y1), ycyl(E, 9, y0, y1)])
    s = s.cut(ycyl(E, 5.2, y0 - 1, y1 + 1))                       # chua dau chot E + long den
    for a in (150, 185):                                           # 2 vit M2.5 vao Forearm_plate_R (concept)
        s = s.cut(ycyl(E + V(14 * math.cos(math.radians(a)), 0, 14 * math.sin(math.radians(a))), 1.35, y0 - 1, y1 + 1))
    return s.removeSplitter()


def compound(ph_a, ph_b):
    g = prism(gear_pts(CC.x, CC.z, ZA, ph=ph_a), *YO).fuse(prism(gear_pts(CC.x, CC.z, ZB, ph=ph_b), YQ[0] + 0.25, YQ[1] - 0.25))
    g = g.fuse(ycyl(CC, 4.5, YO[1], YQ[0] + 0.25))                 # moay-o noi 2 tang
    return g.cut(ycyl(CC, 1.6, YO[0] - 1, YQ[1] + 1)).removeSplitter()   # lo truc Ø3,2 (chot in/ty M3 – concept)


ROD2 = [l for l in G["ROD2"] if l != "Rack_Elbow"]
PIN0 = OBJ["Pinion_WormWheel_Elbow"].Shape.copy(); PIN0.translate(SHIFT)
# pha: z30 theo z10 (it chong lan), roi quat theo z12
best_a = min(((prism(gear_pts(CC.x, CC.z, ZA, ph=k * 360 / ZA / 12), *YO).common(PIN0).Volume, k * 360 / ZA / 12) for k in range(12)))
ph_a = best_a[1]
best_b = None
for k in range(6):
    ph_b = k * 360 / ZB / 6
    for j in range(6):
        ph_s = j * 360 / ZS / 6
        v = sector(ph_s).common(prism(gear_pts(CC.x, CC.z, ZB, ph=ph_b), *YQ)).Volume
        if best_b is None or v < best_b[0]: best_b = (v, ph_b, ph_s)
SECT0 = sector(best_b[2]); COMP0 = compound(ph_a, best_b[1])
so = doc.addObject("Part::Feature", "Sector_Elbow_concept"); so.Shape = SECT0
co = doc.addObject("Part::Feature", "Gear_compound_concept"); co.Shape = COMP0
log = {"gears": {"sector": ZS, "compound": [ZA, ZB], "pinion": ZP, "module": 1}, "E_to_pinion_old": round((PC0 - E).Length, 2),
       "E_to_pinion_new": DP, "E_to_compound": DC, "shift_cylinder": [round(SHIFT.x, 2), round(SHIFT.y, 2), round(SHIFT.z, 2)],
       "elbow_deg_per_pinion_rev": round(360 * ZP / ZA * ZB / ZS, 2), "teeth_arc_deg": [round(T0, 1), round(T1, 1)],
       "rest_overlap_mm3": {"z30_z10": round(best_a[0], 3), "z12_sector": round(best_b[0], 3)}, "poses": []}

COLL = {"BOOM": ["Boom001", "Pin_C", "Pin_E", "Spacer_E", "Pin_E_washer"],
        "ROD1": [l for l in G["ROD1"] if l in OBJ], "TUR": ["Turret_one_piece", "Spacer_A", "Spacer_A001", "Spacer_S", "Spacer_S001"],
        "FORE": [l for l in FORE if l in OBJ and not l.startswith("Pin_D")],
        "ROD2": ROD2, "SECT": ["Sector_Elbow_concept"], "COMP": ["Gear_compound_concept"]}
EXTRA = {"Sector_Elbow_concept": so, "Gear_compound_concept": co}
MESH = {frozenset(("Sector_Elbow_concept", "Gear_compound_concept")): "z12_sector",
        frozenset(("Gear_compound_concept", "Pinion_WormWheel_Elbow")): "z30_z10"}
PAIRS = [("SECT", "BOOM"), ("SECT", "ROD1"), ("SECT", "TUR"), ("SECT", "ROD2"), ("SECT", "COMP"),
         ("COMP", "BOOM"), ("COMP", "FORE"), ("COMP", "ROD2"), ("COMP", "ROD1"),
         ("ROD2", "BOOM"), ("ROD2", "FORE"), ("ROD2", "ROD1"), ("ROD2", "TUR")]


def pose(L1, psi):
    set_pose(0, L1, L2_0, 0, update=False)                 # de + boom + xi-lanh vai nhu macro
    Mb = rot(S, YAXIS, ST["phi"]); E1 = Mb.multVec(E)
    Mf = rot(E1, YAXIS, psi).multiply(Mb)
    sh = Mb.multiply(App.Placement(SHIFT, App.Rotation()))
    pc = Mb.multVec(PC + V(0, DY, 0)); cc = Mb.multVec(CC)
    wc = Mb.multVec(G["WORM_C"]["Elbow"] + SHIFT); wd = Mb.Rotation.multVec(G["WORM_D"]["Elbow"])
    ang = K_P * psi
    for lbl in FORE:
        if lbl in OBJ and OBJ[lbl].Name in REST:
            OBJ[lbl].Placement = Mf.multiply(REST[OBJ[lbl].Name])
    for lbl in ROD2:
        P = sh
        if lbl.startswith("Pinion"): P = rot(pc, YAXIS, ang).multiply(sh)
        elif lbl.startswith("Worm"): P = rot(wc, wd, -16 * ang).multiply(sh)
        OBJ[lbl].Placement = P.multiply(REST[OBJ[lbl].Name])
    so.Placement = Mf
    co.Placement = rot(cc, YAXIS, K_C * psi).multiply(Mb)


def hits(ex):
    out = []
    for a, b in PAIRS:
        for na in COLL[a]:
            for nb in COLL[b]:
                oa, ob = EXTRA.get(na) or OBJ[na], EXTRA.get(nb) or OBJ[nb]
                sa, sb = oa.Shape, ob.Shape
                if not sa.BoundBox.intersect(sb.BoundBox): continue
                v = sa.common(sb).Volume
                key = MESH.get(frozenset((na, nb)))
                if key: ex[key] = round(v, 3); continue
                if v > 0.05: out.append([na, nb, round(v, 2)])
    return out


POSES = [("forearm-up", L1_0, PSI[0]), ("forearm-mid", L1_0, -30.0), ("rest", L1_0, 0.0), ("forearm-down", L1_0, PSI[1]),
         ("shoulder-in-up", LMIN, PSI[0]), ("shoulder-in-down", LMIN, PSI[1]),
         ("shoulder-out-down", L1MAX, PSI[1]), ("shoulder-out-up", L1MAX, PSI[0])]   # psi < 0 = cang tay nang len
for name, L1, psi in POSES:
    pose(L1, psi); ex = {}
    log["poses"].append({"pose": name, "L1": round(L1, 1), "psi": psi, "hits": hits(ex), "mesh_overlap_mm3": ex})
json.dump(log, open(os.path.join(OUT, "_concept.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --------- render ----------
COL = {"Sector_Elbow_concept": (0.98, 0.76, 0.10), "Gear_compound_concept": (0.85, 0.15, 0.15),
       "Pinion_WormWheel_Elbow": (0.20, 0.65, 0.30), "Worm_Elbow": (0.95, 0.45, 0.10), "Housing_Elbow": (0.78, 0.80, 0.84),
       "CB_030_gearbox_Elbow": (0.20, 0.45, 0.85), "Boom001": (0.80, 0.42, 0.15),
       "Forearm_plate_L": (0.80, 0.42, 0.15), "Forearm_plate_R": (0.80, 0.42, 0.15)}
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.ViewObject]
for o in parts:
    o.ViewObject.LineColor = (0.15, 0.15, 0.15)
    if o.Label in COL: o.ViewObject.ShapeColor = COL[o.Label]
MECH = set(ROD2 + ["Sector_Elbow_concept", "Gear_compound_concept", "Pin_E"])
CTX = MECH | {"Boom001", "Forearm_plate_L", "Forearm_plate_R", "Spacer_E", "Pin_C", "Spacer_D", "Pin_D"}
v = Gui.ActiveDocument.ActiveView
v.setAnimationEnabled(False)   # lan dau: anh 01-02 chup giua luc camera dang xoay


def shot(fn, fit, show, cam, transp=None, size=(1400, 1000)):
    """fit = chi tiet dung de can khung (zoom vao co cau), show = chi tiet hien trong anh."""
    transp = transp or {}
    vis = lambda o, s: (s is None or o.Label in s) and not o.Label.startswith("M2_5") and o.Label != "Rack_Elbow"
    {"iso": v.viewIsometric, "front": v.viewFront}[cam]()
    for o in parts: o.ViewObject.Visibility = vis(o, fit)
    Gui.updateGui(); v.fitAll(); Gui.updateGui()
    for o in parts:
        o.ViewObject.Visibility = vis(o, show)
        o.ViewObject.Transparency = transp.get(o.Label, 0)
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, fn + ".png"), size[0], size[1], "White")


TR = {"Boom001": 55, "Forearm_plate_L": 75}
for i, (name, L1, psi) in enumerate(POSES[:4]):
    pose(L1, psi)
    shot("%02d-elbow-%s" % (i + 1, name), MECH | {"Forearm_plate_R"}, CTX, "front", TR, (1200, 900))
pose(L1_0, 0.0)
shot("05-elbow-rest-iso", MECH, CTX, "iso", TR)
shot("06-gear-train-iso", MECH, MECH, "iso", {"Housing_Elbow": 60})
for i, (name, L1, psi) in enumerate((("forearm-up", L1_0, PSI[0]), ("rest", L1_0, 0.0), ("forearm-down", L1_0, PSI[1]))):
    pose(L1, psi); shot("%02d-full-%s" % (i + 7, name), None, None, "front", {}, (1200, 900))
pose(L1_0, 0.0)
SAVE = os.environ.get("FC_SAVE_CONCEPT")   # luu BAN SAO concept de Tuan xem (file goc khong doi: saveAs sang file khac)
if SAVE:
    for o in parts:
        o.ViewObject.Visibility = not o.Label.startswith("M2_5") and o.Label != "Rack_Elbow"
        o.ViewObject.Transparency = 0
    v.viewIsometric(); v.fitAll()
    doc.saveAs(SAVE)
else:
    doc.removeObject(so.Name); doc.removeObject(co.Name)
