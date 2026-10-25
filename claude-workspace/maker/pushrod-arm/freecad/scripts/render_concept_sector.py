# Anh MO PHONG phuong an E (2026-10-25): banh rang quat tai khop khuyu thay Rack_Elbow (Rack bi lech khi Tuan thu).
# Chi la concept: dung hinh hoc tam trong bo nho, KHONG Luu .FCStd. Chay qua gui_run (GUI rieng, tu thoat):
#   set FC_FILE=.../pushrod_arm.FCStd  set FC_SCRIPT=<file nay>  [set FC_OUT=<log>]
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode tools/robotics-cad/scripts/gui_run.py
# Bo cuc: quat m1 z113 (ban kinh lan 56,5) bat ngoai Forearm_plate_R (y -20,25..-15), tam = chot E, quay theo cang tay.
# Cum xi-lanh khuyu (vo, hop so, truc vit, banh vit + z10) bat CUNG vao Boom, dich ngang -17,75 mm de z10 cung mat quat.
# Vi sao khong de quat o mat giua: Boom001 dac o goc 220..240 deg quanh E (r 40..58) -> quat quet vao khi gap khuyu.
# Ra: freecad/images/concept-e-sector/*.png + _concept.json (va cham + an khop tung tu the).
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
FORE, ROD2_ALL, ST = G["FORE"], G["ROD2"], G["STATE"]
L1_0, L2_0, LMIN, L1MAX = G["L1_0"], G["L2_0"], G["LMIN"], G["L1MAX"]
doc = App.ActiveDocument

M, Z, RS, RPIN = 1.0, 113, 56.5, 5.0      # quat m1 z113 -> ban kinh lan 56,5; banh rang z10 r 5
DY = -17.75                               # dich cum xi-lanh: z10 y -2,5..2,5 -> -20,25..-15,25
Y0, Y1 = -20.25, -15.0                    # quat ap mat ngoai Forearm_plate_R (y -15) -> nhin "front" (tu -Y) thay quat
PC = OBJ["Rack_Elbow"].Placement.multVec(V(60, 0, 8.25))   # tam z10 (tu the goc)
TH0 = math.degrees(math.atan2(PC.z - E.z, PC.x - E.x)) % 360   # ~198,5 deg
PSI = (-63.5, 14.6)                       # khoang goc khuyu (kinematics-test, L2 92..128)
T0, T1 = TH0 + PSI[0] - 7, TH0 + PSI[1] + 7   # cung rang (he cang tay, tu the goc) + 7 deg du

A20 = math.radians(20)


def invf(a): return math.tan(a) - a


def gear_pts(cx, cz, z, m, ph=0.0, bl=0.15, n_=6):   # nhu 2026-10-22_build_pushrods_v3.py (x = 0)
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


def wedge(r0, r1, a0, a1, y0, y1, n=48):
    arc = lambda r, rev: [(E.x + r * math.cos(math.radians(a)), E.z + r * math.sin(math.radians(a)))
                          for a in ([a0 + (a1 - a0) * k / n for k in range(n + 1)][::-1 if rev else 1])]
    return prism(arc(r1, False) + (arc(r0, True) if r0 > 0 else [(E.x, E.z)]), y0, y1)


def ycyl(x, z, r, y0, y1): return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def sector(ph):
    teeth = prism(gear_pts(E.x, E.z, Z, M, ph), Y0, Y1).common(wedge(0, RS + 2, T0, T1, Y0 - 1, Y1 + 1))
    s = teeth.fuse([wedge(0, RS - 1.25 * M, T0 - 4, T1 + 4, Y0, Y1), ycyl(E.x, E.z, 11, Y0, Y1)])
    s = s.cut(ycyl(E.x, E.z, 5.2, Y0 - 1, Y1 + 1))                    # chua dau chot E + long den
    s = s.cut(wedge(20, RS - 9, T0 + 8, T1 - 8, Y0 - 1, Y1 + 1))      # cua so giam nhua, chua 2 nan
    for a in (TH0 - 25, TH0 + 5):                                      # 2 vit M2.5 vao Forearm_plate_R (concept)
        s = s.cut(ycyl(E.x + 15 * math.cos(math.radians(a)), E.z + 15 * math.sin(math.radians(a)), 1.35, Y0 - 1, Y1 + 1))
    return s.removeSplitter()


ROD2 = [l for l in ROD2_ALL if l != "Rack_Elbow"]
PIN_SHAPE = OBJ["Pinion_WormWheel_Elbow"].Shape.copy()   # tu the goc
PIN_SHAPE.translate(V(0, DY, 0))
# pha quat: thu 12 pha trong 1 buoc rang, chon pha it chong lan voi z10 nhat o tu the goc
best = None
for k in range(12):
    ph = k * 360.0 / Z / 12
    sh = sector(ph); v = sh.common(PIN_SHAPE).Volume
    if best is None or v < best[0]: best = (v, ph, sh)
SECT0 = best[2]
log = {"z": Z, "module": M, "pitch_r": RS, "center_dist_model": round((PC - E).Length, 3), "center_dist_gear": RS + RPIN,
       "dy_cylinder": DY, "teeth_arc_deg": [round(T0, 1), round(T1, 1)], "phase_overlap_mm3": round(best[0], 3),
       "ratio_pinion_per_elbow": RS / RPIN, "poses": []}
so = doc.addObject("Part::Feature", "Sector_Elbow_concept"); so.Shape = SECT0

COLL = {"BOOM": ["Boom001", "Pin_C", "Pin_E", "Spacer_E"],
        "ROD1": [l for l in G["ROD1"] if l in OBJ], "TUR": ["Turret_one_piece", "Spacer_A", "Spacer_A001", "Spacer_S", "Spacer_S001"],
        "FORE": [l for l in FORE if l in OBJ and not l.startswith("Pin_D")]}


def pose(L1, psi):
    set_pose(0, L1, L2_0, 0, update=False)                 # dat de + boom + xi-lanh vai nhu macro
    Mb = rot(S, YAXIS, ST["phi"]); E1 = Mb.multVec(E)
    Mf = rot(E1, YAXIS, psi).multiply(Mb)
    sh = App.Placement(V(0, DY, 0), App.Rotation())
    pc = Mb.multVec(PC + V(0, DY, 0))
    wc = Mb.multVec(G["WORM_C"]["Elbow"] + V(0, DY, 0)); wd = Mb.Rotation.multVec(G["WORM_D"]["Elbow"])
    ang = -(RS / RPIN) * psi                               # an khop ngoai: z10 quay nguoc, ti so 11,3
    for lbl in FORE:
        if lbl in OBJ and OBJ[lbl].Name in REST:
            OBJ[lbl].Placement = Mf.multiply(REST[OBJ[lbl].Name])
    for lbl in ROD2:
        o = OBJ[lbl]; R = REST[o.Name]; P = Mb.multiply(sh)
        if lbl.startswith("Pinion"): P = rot(pc, YAXIS, ang).multiply(P)
        elif lbl.startswith("Worm"): P = rot(wc, wd, -16 * ang).multiply(P)
        o.Placement = P.multiply(R)
    so.Placement = Mf


def hits(extra):
    out = []
    groups = dict(COLL); groups["ROD2"] = ROD2; groups["SECT"] = ["Sector_Elbow_concept"]
    pairs = [("SECT", "BOOM"), ("SECT", "ROD1"), ("SECT", "TUR"), ("SECT", "ROD2"), ("ROD2", "BOOM"), ("ROD2", "FORE"),
             ("ROD2", "ROD1"), ("ROD2", "TUR")]
    for a, b in pairs:
        for na in groups[a]:
            for nb in groups[b]:
                oa = so if na == "Sector_Elbow_concept" else OBJ[na]; ob = OBJ[nb]
                sa, sb = oa.Shape, ob.Shape
                if not sa.BoundBox.intersect(sb.BoundBox): continue
                if {na, nb} == {"Sector_Elbow_concept", "Pinion_WormWheel_Elbow"}:
                    extra["mesh_overlap_mm3"] = round(sa.common(sb).Volume, 3); continue
                v = sa.common(sb).Volume
                if v > 0.05: out.append([na, nb, round(v, 2)])
    return out


POSES = [("elbow-fold", L1_0, PSI[0]), ("elbow-mid", L1_0, -30.0), ("rest", L1_0, 0.0), ("elbow-open", L1_0, PSI[1]),
         ("shoulder-in-fold", LMIN, PSI[0]), ("shoulder-out-open", L1MAX, PSI[1]), ("shoulder-out-fold", L1MAX, PSI[0])]
for name, L1, psi in POSES:
    pose(L1, psi); ex = {}
    log["poses"].append({"pose": name, "L1": round(L1, 1), "psi": psi, "hits": hits(ex), **ex})

# --------- render ----------
COL = {"Sector_Elbow_concept": (0.98, 0.76, 0.10), "Pinion_WormWheel_Elbow": (0.20, 0.65, 0.30), "Worm_Elbow": (0.95, 0.45, 0.10),
       "Housing_Elbow": (0.78, 0.80, 0.84), "CB_030_gearbox_Elbow": (0.20, 0.45, 0.85), "Boom001": (0.80, 0.42, 0.15),
       "Forearm_plate_L": (0.80, 0.42, 0.15), "Forearm_plate_R": (0.80, 0.42, 0.15)}
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.ViewObject]
for o in parts:
    o.ViewObject.LineColor = (0.15, 0.15, 0.15)
    if o.Label in COL: o.ViewObject.ShapeColor = COL[o.Label]
ELBOW = set(ROD2 + ["Sector_Elbow_concept", "Boom001", "Forearm_plate_L", "Forearm_plate_R", "Pin_E", "Spacer_E", "Pin_C"])
v = Gui.ActiveDocument.ActiveView


def shot(fn, show, cam, transp=None, size=(1400, 1000)):
    transp = transp or {}
    for o in parts:
        o.ViewObject.Visibility = (show is None or o.Label in show) and not o.Label.startswith("M2_5") and o.Label != "Rack_Elbow"
        o.ViewObject.Transparency = transp.get(o.Label, 0)
    {"iso": v.viewIsometric, "front": v.viewFront, "rear": v.viewRear}[cam]()
    v.fitAll()
    v.saveImage(os.path.join(OUT, fn + ".png"), size[0], size[1], "White")


for name, L1, psi in POSES[:4]:
    pose(L1, psi)
    shot("elbow-%s-side" % name, ELBOW, "front", {"Forearm_plate_L": 70, "Boom001": 45}, (1200, 900))
pose(L1_0, 0.0)
shot("01-elbow-iso", ELBOW, "iso", {"Forearm_plate_L": 60})
for name, L1, psi in (("02-full-fold", L1_0, PSI[0]), ("03-full-rest", L1_0, 0.0), ("04-full-open", L1_0, PSI[1])):
    pose(L1, psi); shot(name, None, "front", {}, (1200, 900))
pose(L1_0, 0.0)
json.dump(log, open(os.path.join(OUT, "_concept.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
doc.removeObject(so.Name)
