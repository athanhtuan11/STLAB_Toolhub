# CONCEPT xi-lanh PISTON (Tuan 2026-10-25: "thich co che dang piston, rat gon cho xe muc") thay thanh rang (Rack_Elbow lech).
# Hoc tu Cyberbrick Excavator (MakerWorld 2371626): ong + piston kep dai oc M3 + ty rong, ty ren M3 tu ham.
# Tuan KHONG co N20 (LA006) -> dung motor CyberBrick 030 + hop so dang co, dat CANH ong: z28 (truc ra O5,3) -> z12 (dau ty ren M3 roi).
# Ly do canh ong: dong truc thi khong du hanh trinh 36 mm trong L_min 92 mm (may xuc ~26 mm / ~100 mm).
# CHAY CLI (Tuan: mac dinh FreeCAD CLI de khong crash), anh render matplotlib (tools/robotics-cad/scripts/mpl_render.py):
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode tools/robotics-cad/scripts/fc_cli.py --pass <file nay> [ban_sao.FCStd]
# KHONG Luu pushrod_arm.FCStd; doi so 2 = luu BAN SAO concept (CLI: mat mau hien thi, hinh hoc du).
# He toa do xi-lanh = Placement Rack_<tag> tu the goc: x doc truc (goc = chot A/C), y // chot, z trong mat phang tay.
# Ra: freecad/images/concept-piston-030/*.png + _concept.json (va cham 9 tu the).
import json
import math
import os
import sys
import types

import FreeCAD as App
import Part
from FreeCAD import Vector as V

sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
from mpl_render import render  # noqa: E402

FC = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad"
OUT = os.path.join(FC, "images", "concept-piston-030")
os.makedirs(OUT, exist_ok=True)
doc = App.openDocument(os.path.join(FC, "pushrod_arm.FCStd"))
src = open(os.path.join(FC, "pushrod_arm_sim.FCMacro"), encoding="utf-8").read().split("class Panel", 1)[0]
sys.modules.setdefault("FreeCADGui", types.ModuleType("FreeCADGui"))     # macro chi dung Gui khi update=True
src = src.replace("from PySide import QtCore, QtGui", "raise ImportError").replace(
    "from PySide2 import QtCore, QtWidgets as QtW", "QtCore = QtW = None")
G = {"__name__": "sim"}
exec(compile(src, "pushrod_arm_sim.FCMacro", "exec"), G)
set_pose, OBJ, REST = G["set_pose"], G["OBJ"], G["REST"]
LMIN, LMAX, L1MAX, L1_0, L2_0 = G["LMIN"], G["LMAX"], G["L1MAX"], G["L1_0"], G["L2_0"]
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


# Va cham: fast_collide (luoi manifold3d chia 1 lan, ~ms/cap) thay B-rep common (0,1-12 s/cap, STEP hop so cham nhat).
# Lan dau 2026-10-25 dung common: > 10 phut chua xong 9 tu the (Tuan: "buoc testing qua lau").
# Them: cap co vi tri TUONG DOI khong doi (cung 1 khoi cung, vd. vo + hop so) chi tinh 1 lan.
import time  # noqa: E402
import fast_collide  # noqa: E402
t0 = time.time()
PAIRS = []
for lbl, (o, tag, grp) in NEW.items():
    PAIRS += [(lbl, ob.Label) for ob in obstacles(tag)]
for tag in CFG:   # ben trong: ty/piston khong cham vo, banh rang
    PAIRS += [("%s_%s" % (a, tag), "%s_%s" % (b, tag)) for a, b in (
        ("Piston_rod", "Cyl_Housing"), ("Piston_rod", "Screw_M3"), ("Gear_z28", "Cyl_Housing"),
        ("Gear_z12_screw", "Cyl_Housing"), ("Gear_z28", "Gear_z12_screw"), ("Piston_rod", "Gear_z12_screw"))]
ALLO = dict({l: o for l, o in OBJ.items()}, **{l: o for l, (o, t, g) in NEW.items()})
FCOL = fast_collide.Collider({l: ALLO[l] for p in PAIRS for l in p}, min_mm3=0.05)
t_mesh = time.time() - t0
REL = {}   # (a, b, vi tri tuong doi lam tron) -> the tich


def rel_key(a, b):
    r = ALLO[a].Placement.inverse().multiply(ALLO[b].Placement)
    return (a, b) + tuple(round(x, 4) for x in (*r.Base, *r.Rotation.Q))


POSES = [(a, b) for a in (LMIN, L1_0, L1MAX) for b in (LMIN, L2_0, LMAX)]
log = {"info": INFO, "poses": [], "n_pairs": len(PAIRS), "mesh_s": round(t_mesh, 1), "hull": sorted(FCOL.hull)}
n_calc = 0
for L1, L2 in POSES:
    pose(L1, L2); hits = []
    for a, b in PAIRS:
        k = rel_key(a, b)
        if k not in REL:
            REL[k] = FCOL.volume(a, b); n_calc += 1
        v = REL[k]
        if v is not None and v > 0.05: hits.append([a, b, round(v, 1)])
    log["poses"].append({"L1": round(L1, 1), "L2": round(L2, 1), "hits": hits})
log["collide_s"] = round(time.time() - t0 - t_mesh, 1); log["pairs_calc"] = n_calc; log["pairs_total"] = len(PAIRS) * len(POSES)
json.dump(log, open(os.path.join(OUT, "_concept.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------------- render (matplotlib, CLI) ----------------
COL = {"Cyl_Housing": (0.78, 0.80, 0.84), "CB_030_gearbox_new": (0.20, 0.45, 0.85), "Gear_z28": (0.85, 0.15, 0.15),
       "Gear_z12_screw": (0.98, 0.76, 0.10), "Nut_M3": (0.35, 0.35, 0.38), "Screw_M3": (0.55, 0.55, 0.60),
       "Piston_rod": (0.60, 0.35, 0.75), "Boom": (0.80, 0.42, 0.15), "Forearm": (0.80, 0.42, 0.15),
       "Turret": (0.85, 0.45, 0.15), "Base": (0.25, 0.26, 0.28), "Gripper": (0.20, 0.20, 0.22), "CB_": (0.20, 0.20, 0.22)}
HIDE = OLD | {l for l in OBJ if l.startswith("M2_5")}


def col(lbl): return next((c for k, c in COL.items() if lbl.startswith(k)), (0.70, 0.70, 0.72))


def cutaway(tag):   # giu nua y >= 0 (he xi-lanh) -> nhin tu -Y thay mat cat; hop so STEP de nguyen (trong suot)
    out = []
    for lbl, (o, t, g) in NEW.items():
        if t != tag: continue
        if lbl.startswith("CB_030"): out.append((o.Shape, col(lbl), 0.25)); continue
        cut = box(-50, 220, 0, 100, -100, 100); cut.transformShape(o.Placement.multiply(REST[OBJ["Rack_" + tag].Name]).toMatrix())
        out.append((o.Shape.common(cut), col(lbl)))
    return out


n = 1
for tag in ("Elbow", "Shoulder"):
    own = [(o.Shape, col(l)) for l, (o, t, g) in NEW.items() if t == tag]
    for nm, L in (("retracted", CFG[tag]["Lmin"]), ("extended", CFG[tag]["Lmax"])):
        pose(L if tag == "Shoulder" else L1_0, L if tag == "Elbow" else L2_0)
        own = [(o.Shape, col(l)) for l, (o, t, g) in NEW.items() if t == tag]
        render(own, os.path.join(OUT, "%02d-%s-%s-iso.png" % (n, tag.lower(), nm)), "iso",
               title="%s - %s (L = %.0f mm)" % (tag, nm, L)); n += 1
        render(cutaway(tag), os.path.join(OUT, "%02d-%s-%s-cutaway.png" % (n, tag.lower(), nm)), "front",
               title="%s - %s - mat cat" % (tag, nm)); n += 1
ALL = lambda: [(o.Shape, col(l)) for l, o in OBJ.items() if l not in HIDE] + [(o.Shape, col(l)) for l, (o, t, g) in NEW.items()]
for nm, L1, L2 in (("rest", L1_0, L2_0), ("both-in", LMIN, LMIN), ("both-out", L1MAX, LMAX)):
    pose(L1, L2); render(ALL(), os.path.join(OUT, "%02d-full-%s.png" % (n, nm)), "front", size=(1200, 900), tol=0.3,
                         title="Toan canh - %s" % nm); n += 1
pose(L1_0, L2_0)
render(ALL(), os.path.join(OUT, "%02d-arm-iso.png" % n), "iso", fit=[o.Shape for o, t, g in NEW.values()], tol=0.3); n += 1
if len(sys.argv) > 1:   # BAN SAO concept de Tuan xem (file goc khong doi)
    for l in HIDE:
        doc.removeObject(OBJ[l].Name)
    doc.saveAs(sys.argv[1])
