# CONCEPT xi-lanh PISTON dong truc kieu Cyberbrick Excavator (Tuan 2026-10-25: chon "N20 dong truc, doi chot").
# Motor: Bambu N20 M3 Threaded Shaft LA006 (M3 x 45, 1000 rpm, 6 V, SH1.0-2P cam thang XA004) - cong dong dung (May xuc
# 2371626, Wheel Loader 1745230). Kich thuoc ong/piston theo xi-lanh may xuc (do STL): ong O16,8, lo motor O12,6,
# buong piston chu D (cao 10,6) chong xoay, dai oc VUONG M3 kep trong piston, ty rong (ty ren chui vao khi rut).
# Khong doi chot: giu A/B/C/D, chi in lai Boom (got tai chot C, khoet ranh day Boom cho xi-lanh vai) - xem _concept.json.
# Ban dung motor 030 dat canh ong (khong chon): render_concept_piston_030.py.
# Hinh hoc tam trong bo nho, KHONG Luu pushrod_arm.FCStd (FC_SAVE_CONCEPT = luu BAN SAO de xem).
#   set FC_FILE=.../pushrod_arm.FCStd  set FC_SCRIPT=<file nay>  [set FC_SAVE_CONCEPT=<ban sao.FCStd>]
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode tools/robotics-cad/scripts/gui_run.py   (man hinh phu)
# He toa do xi-lanh = Placement Rack_<tag> tu the goc: x doc truc (goc = chot A/C), y // chot, z trong mat phang tay.
import json
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
LIB = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/community/n20-motor/models/"
N20_STEP = LIB + "n20-tieu-chuan/n20-tieu-chuan.step"            # than N20 (mat hop so o z = 9, truc +z) - nhu build v3
SHB_STEP = LIB + "bo-cam-jst-sh-phia-sau/bo-cam-jst-sh-phia-sau.step"

FIT = 0.3
TUBE_R = 8.4                 # ong O16,8 (may xuc)
BORE_R, FLAT_Z = 6.3, -4.3   # lo motor O12,6; buong piston chu D: tron r 6,3 cat phang z -4,3 (cao 10,6 nhu may xuc)
MOTOR_L = 29.0               # mat hop so -> het bo cam SH phia sau (STEP cong dong; TODO do LA006 that)
SHAFT_L = 45.0               # LA006 M3 x 45
PIST_L = 6.0
NUT = (5.5, 1.8)             # dai oc vuong M3 DIN 562
ROD_Y, ROD_Z, ROD_R = 3.0, 4.0, 1.5   # ty day 6 (= mat ty/rack cu, lot giua dem chot), cao 8
ROD_BORE = 1.8               # lo ty ren trong ty O3,6
X_CAP0, X_CAP1 = 6.5, 9.5    # nap sau (gan tai chot) ap duoi ong
SPACER_CLR = 7.3             # mat ong toan phan cach tam chot truoc (dem chot D r 7)

CFG = {"Elbow": dict(Lmin=LMIN, L0=L2_0, Lmax=LMAX, zs=1, pins=("C", "D")),
       "Shoulder": dict(Lmin=LMIN, L0=L1_0, Lmax=L1MAX, zs=-1, pins=("A", "B"))}


def xcyl(r, x0, x1, y=0.0, z=0.0): return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def dshape(r, flat, x0, x1): return xcyl(r, x0, x1).common(box(x0, x1, -r - 1, r + 1, flat, r + 1))


def rrect(hy, hz, r, x0, x1):
    s = box(x0, x1, -hy + r, hy - r, -hz, hz).fuse(box(x0, x1, -hy, hy, -hz + r, hz - r))
    for sy in (-1, 1):
        for sz in (-1, 1):
            s = s.fuse(xcyl(r, x0, x1, sy * (hy - r), sz * (hz - r)))
    return s.removeSplitter()


def n20(xface):
    m = Part.read(N20_STEP); b = Part.read(SHB_STEP)
    b.rotate(V(0, 0, 0), V(1, 0, 0), 180); b.translate(V(0, 0, -16.3))
    s = Part.makeCompound([m, b]).transformGeometry(App.Matrix(0, 0, 1, xface - 9.0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1))
    return s.common(box(xface - 40, xface + 0.8, -20, 20, -20, 20))   # bo truc D cua STEP; truc ren ve rieng


def build(tag, c):
    zs, L0, Lmin = c["zs"], c["L0"], c["Lmin"]
    stroke = c["Lmax"] - Lmin
    xm0 = X_CAP1 + 0.1                       # duoi bo cam SH
    xf = xm0 + MOTOR_L                       # mat hop so N20
    xp_ret = xf + 0.5                        # duoi piston khi rut het
    xt1 = Lmin - SPACER_CLR                  # het ong (toan phan)
    xbush = xp_ret + PIST_L + stroke         # dau piston khi duoi het = dau bac dan huong
    off = L0 - Lmin
    # ---- ong ----
    tube = xcyl(TUBE_R, X_CAP1, xt1)
    tube = tube.cut(xcyl(BORE_R, X_CAP1 - 0.1, xf))                                   # lo motor
    tube = tube.cut(dshape(BORE_R, FLAT_Z, xf - 0.1, xbush))                          # buong piston chu D (bac chan mat hop so)
    tube = tube.cut(rrect(ROD_Y + FIT, ROD_Z + FIT, ROD_R + FIT, xbush - 0.1, xt1 + 0.1))   # lo ty o bac dan huong
    zb = zs * (TUBE_R + 1.6)
    boss = xcyl(2.4, X_CAP1, X_CAP1 + 6, 0, zb).fuse(box(X_CAP1, X_CAP1 + 6, -2.4, 2.4, zs * TUBE_R * 0.8, zb))
    tube = tube.fuse(boss).cut(xcyl(1.05, X_CAP1 - 0.1, X_CAP1 + 6.1, 0, zb))       # lo ren M2.5 bat nap sau
    # ---- nap sau + tai chot (tai cu cua vo xi-lanh) ----
    old = OBJ["Housing_" + tag].Shape.copy(); old.transformShape(REST[OBJ["Rack_" + tag].Name].inverse().toMatrix())
    lug = old.common(box(-8, X_CAP0 + 0.5, -3.5, 3.5, -9, 9))
    cap = xcyl(TUBE_R, X_CAP0, X_CAP1).fuse([lug, xcyl(2.4, X_CAP0, X_CAP1, 0, zb),
                                            box(X_CAP0, X_CAP1, -2.4, 2.4, zs * TUBE_R * 0.8, zb)])
    cap = cap.cut(xcyl(1.4, X_CAP0 - 0.1, X_CAP1 + 0.1, 0, zb))                       # lo vit M2.5
    cap = cap.cut(box(X_CAP0 - 0.1, X_CAP1 + 0.1, 3.5, 6.5, -2.5, 2.5)).removeSplitter()   # khe ra day SH (canh tai chot)
    # ---- motor + truc ren ----
    mot = n20(xf)
    shaft = xcyl(1.5, xf, xf + SHAFT_L)
    # ---- piston + ty (tu the goc: + off) ----
    xp = xp_ret + off
    pist = dshape(BORE_R - FIT, FLAT_Z + FIT, xp, xp + PIST_L)
    xn = xp + PIST_L / 2
    pist = pist.cut(box(xn - (NUT[1] + 0.2) / 2, xn + (NUT[1] + 0.2) / 2, -(NUT[0] + 0.2) / 2, (NUT[0] + 0.2) / 2, -(NUT[0] + 0.2) / 2, BORE_R + 1))
    rack = OBJ["Rack_" + tag].Shape.copy(); rack.transformShape(REST[OBJ["Rack_" + tag].Name].inverse().toMatrix())
    eye = rack.common(box(L0 - 6.5, L0 + 9, -3.5, 3.5, -9, 9))
    rod = pist.fuse([rrect(ROD_Y, ROD_Z, ROD_R, xp + PIST_L - 0.5, L0 - 5.0), eye]).removeSplitter()
    bore_end = xf + SHAFT_L + off + 1.0
    rod = rod.cut(xcyl(ROD_BORE, xp - 0.1, bore_end))
    nut = box(xn - NUT[1] / 2, xn + NUT[1] / 2, -NUT[0] / 2, NUT[0] / 2, -NUT[0] / 2, NUT[0] / 2).cut(xcyl(1.5, xn - 2, xn + 2))
    info = dict(stroke=round(stroke, 1), motor_face=round(xf, 1), tube=[X_CAP1, round(xt1, 1)], bush_len=round(xt1 - xbush, 1),
                piston_ret=[round(xp_ret, 1), round(xp_ret + PIST_L, 1)], nut_max=round(xp_ret + PIST_L / 2 + stroke, 1),
                shaft_end=round(xf + SHAFT_L, 1), rod_wall_after_bore=round(L0 - 6.5 - bore_end, 1),
                speed_mm_s_at_1000rpm=round(1000 / 60 * 0.5, 1))
    if info["bush_len"] < 2.5: info["WARN"] = "bac dan huong < 2,5 mm"
    if info["rod_wall_after_bore"] < 1.0: info["WARN_ROD"] = "lo ty ren cham mat ty"
    return {"Cyl_Tube": (tube, "H"), "Cyl_RearCap": (cap, "H"), "N20_LA006": (mot, "H"), "Screw_M3x45": (shaft, "H"),
            "Piston_rod": (rod, "R"), "Nut_M3_square": (nut, "R")}, info


NEW = {}; INFO = {}
for tag, c in CFG.items():
    parts, INFO[tag] = build(tag, c)
    R = REST[OBJ["Rack_" + tag].Name]
    for name, (sh, grp) in parts.items():
        s = sh.copy(); s.transformShape(R.toMatrix())
        o = doc.addObject("Part::Feature", "%s_%s" % (name, tag)); o.Label = "%s_%s" % (name, tag); o.Shape = s
        NEW[o.Label] = (o, tag, grp)
OLD = {l for l in set(G["ROD1"]) | set(G["ROD2"]) | {"Pin_gearbox_Shoulder", "Pin_gearbox_Elbow"} if l in OBJ}


def pose(L1, L2):
    ok = set_pose(0, L1, L2, 0, update=False)
    for lbl, (o, tag, grp) in NEW.items():
        H = OBJ["Housing_" + tag]; Mr = H.Placement.multiply(REST[H.Name].inverse())
        if grp == "R":
            L = L1 if tag == "Shoulder" else L2
            u = Mr.Rotation.multVec(REST[OBJ["Rack_" + tag].Name].Rotation.multVec(V(1, 0, 0)))
            Mr = App.Placement(u * (L - CFG[tag]["L0"]), App.Rotation()).multiply(Mr)
        o.Placement = Mr
    return ok


def obstacles(tag):
    p0, p1 = CFG[tag]["pins"]
    out = [o for l, o in OBJ.items() if l not in OLD and not l.startswith(("Pin_" + p0, "Pin_" + p1, "M2_5"))]
    return out + [o for l, (o, t, g) in NEW.items() if t != tag]


POSES = [(a, b) for a in (LMIN, L1_0, L1MAX) for b in (LMIN, L2_0, LMAX)]
log = {"info": INFO, "poses": [], "boom_hits_max_mm3": {}}
for L1, L2 in POSES:
    pose(L1, L2); hits = []
    for lbl, (o, tag, grp) in NEW.items():
        for ob in obstacles(tag):
            if not o.Shape.BoundBox.intersect(ob.Shape.BoundBox): continue
            v = o.Shape.common(ob.Shape).Volume
            if v > 0.05:
                hits.append([lbl, ob.Label, round(v, 1)])
                if ob.Label == "Boom001": log["boom_hits_max_mm3"][lbl] = max(log["boom_hits_max_mm3"].get(lbl, 0), round(v, 1))
    for tag in CFG:
        own = {l: o for l, (o, t, g) in NEW.items() if t == tag}
        for a, b in (("Piston_rod", "Cyl_Tube"), ("Piston_rod", "Screw_M3x45"), ("Piston_rod", "N20_LA006"),
                     ("N20_LA006", "Cyl_Tube"), ("N20_LA006", "Cyl_RearCap"), ("Cyl_Tube", "Cyl_RearCap")):
            v = own["%s_%s" % (a, tag)].Shape.common(own["%s_%s" % (b, tag)].Shape).Volume
            if v > 0.05: hits.append(["%s_%s" % (a, tag), "%s_%s" % (b, tag), round(v, 1)])
    log["poses"].append({"L1": round(L1, 1), "L2": round(L2, 1), "hits": hits})
json.dump(log, open(os.path.join(OUT, "_concept.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- render ----------------
COL = {"Cyl_Tube": (0.78, 0.80, 0.84), "Cyl_RearCap": (0.62, 0.64, 0.70), "N20_LA006": (0.75, 0.62, 0.30),
       "Screw_M3x45": (0.55, 0.55, 0.60), "Piston_rod": (0.60, 0.35, 0.75), "Nut_M3_square": (0.30, 0.30, 0.33)}
for o in doc.Objects:
    if o.isDerivedFrom("Part::Feature") and o.ViewObject:
        o.ViewObject.LineColor = (0.15, 0.15, 0.15)
        for k, cl in COL.items():
            if o.Label.startswith(k): o.ViewObject.ShapeColor = cl
v = Gui.ActiveDocument.ActiveView
v.setAnimationEnabled(False)
HIDE = OLD | {l for l in OBJ if l.startswith("M2_5")}


def cutaway(tag):   # giu nua y >= 0 (he xi-lanh) -> nhin tu -Y thay mat cat
    out = []
    for lbl, (o, t, g) in NEW.items():
        if t != tag: continue
        cut = box(-50, 220, 0, 100, -100, 100); cut.transformShape(o.Placement.multiply(REST[OBJ["Rack_" + tag].Name]).toMatrix())
        c = doc.addObject("Part::Feature", "cut_" + lbl); c.Shape = o.Shape.common(cut)
        c.ViewObject.ShapeColor = o.ViewObject.ShapeColor; c.ViewObject.LineColor = (0.15, 0.15, 0.15); out.append(c)
    return out


def shot(fn, fit, show, cam, transp=None, size=(1400, 1000)):
    transp = transp or {}
    allp = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.ViewObject]
    vis = lambda o, s: (s is None or o.Label in s) and o.Label not in HIDE and not (s is None and o.Name.startswith("cut_"))
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
        cs = cutaway(tag); names = {c.Label for c in cs}
        shot("%02d-%s-%s-cutaway" % (n, tag.lower(), nm), names, names, "front"); n += 1
        for c in cs: doc.removeObject(c.Name)
for nm, L1, L2 in (("rest", L1_0, L2_0), ("both-in", LMIN, LMIN), ("both-out", L1MAX, LMAX)):
    pose(L1, L2); shot("%02d-full-%s" % (n, nm), None, None, "front", {}, (1200, 900)); n += 1
pose(L1_0, L2_0)
CTX = set(NEW) | {"Boom001", "Turret_one_piece", "Forearm_plate_L", "Forearm_plate_R"}
shot("%02d-arm-iso" % n, set(NEW), CTX, "iso", {"Boom001": 40}); n += 1

SAVE = os.environ.get("FC_SAVE_CONCEPT")   # BAN SAO de Tuan xem (file goc khong doi)
if SAVE:
    for o in doc.Objects:
        if o.isDerivedFrom("Part::Feature") and o.ViewObject:
            o.ViewObject.Visibility = o.Label not in HIDE; o.ViewObject.Transparency = 0
    v.viewIsometric(); v.fitAll()
    doc.saveAs(SAVE)
