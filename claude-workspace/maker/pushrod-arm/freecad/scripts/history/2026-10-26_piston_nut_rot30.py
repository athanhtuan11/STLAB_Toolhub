# CLI (fc_cli.py): sau 2026-10-26_cylinder_assemblable.py, kiem tang 1 (da bo ignore-pair LK_*|*) bao:
#   LK_Nut_M3_piston_* ~ Housing_*: khe 0,12 mm - goc dai oc luc giac (r 3,18) LO ra khoi mat ty (3,0) -> goc dai oc
#   gan nhu ca long ong khi ty truot (lo in ra nho hon -> ket).
# Sua: XOAY dai oc 30 do quanh truc ty -> 2 GOC len/xuong (z, 3,18 < 4,0), 2 MAT PHANG ra 2 ben (y, 2,75 < 3,0): dai oc
#   nam gon trong tiet dien ty -> khe voi ong = khe ty 0,3. Hoc: luc giac xoay 30 (nua duoi giu chong xoay, ghe chu V) +
#   ranh ho mat +y rong qua 2 goc (z +-3,275). Dai oc truot xuong tu mat tren vao ghe (kiem hinh hoc ben duoi).
#   usage: FreeCADCmd --safe-mode fc_cli.py --pass <script> [file.FCStd] [nosave]
import math
import sys

sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
FCSTD = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".FCStd") else P + "pushrod_arm.FCStd"
SAVE = "nosave" not in sys.argv
LOG = open(P + "check/cylinder-assemblable-2026-10-26.log", "a", encoding="utf-8")
FIT, GW, PIST_L, NUT_AF, NUT_T = 0.3, 4.5, 8.0, 5.5, 2.4
ROD_Y, ROD_Z, ROD_R, BORE_SCREW = 3.0, 4.0, 1.5, 1.8
CFG = {"Elbow": dict(x0=18.0, Lmin=92.0, L0=121.59676825402742),
       "Shoulder": dict(x0=11.0, Lmin=92.0, L0=99.7764836463904)}


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def xcyl(r, x0, x1, y=0.0, z=0.0): return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def rrect(hy, hz, r, x0, x1):
    s = box(x0, x1, -hy + r, hy - r, -hz, hz).fuse(box(x0, x1, -hy, hy, -hz + r, hz - r))
    for sy in (-1, 1):
        for sz in (-1, 1):
            s = s.fuse(xcyl(r, x0, x1, sy * (hy - r), sz * (hz - r)))
    return s.removeSplitter()


def hexagon(af, x0, x1, rot=0.0):
    rc = af / math.sqrt(3)
    ang = [math.radians(rot + 60 * k) for k in range(6)]
    pts = [V(x0, rc * math.cos(t), rc * math.sin(t)) for t in ang]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(x1 - x0, 0, 0))


def local(obj, F):
    s = obj.Shape.copy(); s.Placement = F.inverse().multiply(s.Placement); return s


def put(obj, shape, F):
    pl = shape.Placement; obj.Placement = App.Placement(); obj.Shape = shape; obj.Placement = F.multiply(pl)


doc = App.openDocument(FCSTD)
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-piston-nut-rot30") if SAVE else None
O = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
for tag, c in CFG.items():
    rod_o, hs_o, nut_o = O["Piston_rod_" + tag], O["Housing_" + tag], O["LK_Nut_M3_piston_" + tag]
    F = rod_o.Placement
    xw1 = c["x0"] + 1.5 + GW + 2 * FIT + 1.5
    xp = xw1 + 0.5 + (c["L0"] - c["Lmin"])
    xc = xp + PIST_L / 2
    xn0, xn1 = xc - (NUT_T + 0.3) / 2, xc + (NUT_T + 0.3) / 2
    rod, hs = local(rod_o, F), local(hs_o, F)
    nut_old = local(nut_o, F)
    assert abs((nut_old.BoundBox.XMin + nut_old.BoundBox.XMax) / 2 - xc) < 0.01, (tag, "dai oc lech")
    # lap lai hoc cu (luc giac goc y + ranh z +-2,85) trong tiet dien ty, roi khoet hoc moi
    env = rrect(ROD_Y, ROD_Z, ROD_R, xn0 - 0.01, xn1 + 0.01).cut(xcyl(BORE_SCREW, xn0 - 1, xn1 + 1))
    rc_hole = (NUT_AF + 0.2) / math.sqrt(3)
    pocket = hexagon(NUT_AF + 0.2, xn0, xn1, 30.0).fuse(box(xn0, xn1, 0.0, ROD_Y + 1, -rc_hole, rc_hole))
    rod2 = rod.fuse(env).removeSplitter().cut(pocket).cut(xcyl(BORE_SCREW, xp - 0.1, xn1 + 1)).removeSplitter()
    assert rod2.isValid() and len(rod2.Solids) == 1, (tag, "rod")
    nut = hexagon(NUT_AF, xc - NUT_T / 2, xc + NUT_T / 2, 30.0).cut(xcyl(1.5, xc - 2, xc + 2))
    # kiem: dai oc gon trong tiet dien ty, khe voi ong >= 0,25; truot vao ghe tu +y; khong chong
    bbn = nut.BoundBox
    assert bbn.YMax < ROD_Y and bbn.ZMax < ROD_Z, (tag, "dai oc lo khoi ty", bbn)
    assert nut.common(rod2).Volume < 0.01 and nut.common(hs).Volume < 0.01, tag
    d = nut.distToShape(hs)[0]
    assert d >= 0.25, (tag, "khe dai oc - ong %.3f" % d)
    for k in range(0, 9):
        m = nut.copy(); m.translate(V(0, k * 0.5, 0))
        assert m.common(rod2).Volume < 0.01, (tag, "dai oc ket khi truot +y %.1f" % (k * 0.5))
    print(tag, "dai oc xoay 30: khe ong %.3f mm, rod V %.1f -> %.1f" % (d, rod.Volume, rod2.Volume),
          file=LOG, flush=True)
    assert rod2.Placement.isIdentity()
    put(rod_o, rod2, F)
    put(nut_o, nut, F)
    assert rod_o.Placement.isSame(F, 1e-9)
doc.recompute()
print("nut rot30 FCSTD", FCSTD, "save", SAVE, file=LOG, flush=True)
if SAVE:   # Placement dai oc doi (= he xi-lanh) -> cap nhat tu the goc nhu script 2026-10-25
    import json
    rp = P + "pushrod_arm_rest.json"
    rest = json.load(open(rp))
    for tag in CFG:
        for lbl in ("Piston_rod_" + tag, "LK_Nut_M3_piston_" + tag, "Housing_" + tag):
            o = O[lbl]
            rest[o.Name] = [list(o.Placement.Base), list(o.Placement.Rotation.Q)]
    json.dump(rest, open(rp, "w"))
    print("saved", se.save(doc, gui_from=bk), "backup", bk, file=LOG, flush=True)
else:
    doc.saveAs(FCSTD)
