# CLI (fc_cli.py): xi-lanh piston LAP DUOC (Tuan 2026-10-26: Housing_Elbow + Piston_rod_Elbow in rieng khong lap nhau).
# Kiem bang tools/robotics-cad/scripts/assembly_paths.py (moi): 4 loi, ca Elbow lan Shoulder:
#   1. piston 6 x 10,4 (Elbow; Shoulder 6 x 8,8) > bac dan huong mieng ong 6,6 x 8,6; dau kia ong la buong banh rang kin
#      -> piston bi nhot (mo phong chi DAT san vao trong, test va cham khong hoi "dua vao bang duong nao").
#   2. dai oc M3 trong piston: hoc luc giac kin -> khong nhet vao duoc.
#   3. ty ren M3 qua tuong truoc buong banh rang: ranh U chi tu tam len (z >= 0) + "web" fuse SAU lap mat
#      -> chong 8,8 mm3 (bi an vi print.yaml ignore-pair=LK_*|*).
#   (4. Pin_gearbox x CB_030_gearbox chong ~52 mm3/chot: STEP hang bit 2 dau kenh O4 - xem hop so that, KHONG sua.)
# Sua (giu he xi-lanh, hanh trinh, L0, vi tri moi chi tiet khac):
#   Housing_<tag>: lap phan long ong rong (bore) -> long ong THANG 6,6 x 8,6 (= lo bac cu) tu tuong truoc toi mieng;
#                  khoan lo O3,6 tron qua tuong truoc + web cho ty ren.
#   Piston_rod_<tag>: got piston ve dung tiet dien ty 6 x 8 (bo goc 1,5) -> ca ty truot vao tu mieng ong;
#                  hoc dai oc -> ranh ho mat +y (mat tren khi in) de truot dai oc vao; trong ong thanh +y 3,3 giu
#                  (goc dai oc 3,18).
#   usage: FreeCADCmd --safe-mode fc_cli.py --pass <script> [file.FCStd] [nosave]   (mac dinh: file du an, co Luu)
import sys

sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
FCSTD = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".FCStd") else P + "pushrod_arm.FCStd"
SAVE = "nosave" not in sys.argv
LOG = open(P + "check/cylinder-assemblable-2026-10-26.log", "a", encoding="utf-8")

FIT = 0.3
GW = 4.5
PIST_L, NUT_AF, NUT_T = 8.0, 5.5, 2.4
ROD_Y, ROD_Z, ROD_R = 3.0, 4.0, 1.5
BORE_SCREW = 1.8
BUSH_L = 6.0
CFG = {"Elbow": dict(x0=18.0, bore=11.0, Lmin=92.0, Lmax=128.0, L0=121.59676825402742),
       "Shoulder": dict(x0=11.0, bore=9.4, Lmin=92.0, Lmax=118.0, L0=99.7764836463904)}


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def xcyl(r, x0, x1, y=0.0, z=0.0): return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def rrect(hy, hz, r, x0, x1):   # nhu 2026-10-25_piston_cylinder_030.py
    s = box(x0, x1, -hy + r, hy - r, -hz, hz).fuse(box(x0, x1, -hy, hy, -hz + r, hz - r))
    for sy in (-1, 1):
        for sz in (-1, 1):
            s = s.fuse(xcyl(r, x0, x1, sy * (hy - r), sz * (hz - r)))
    return s.removeSplitter()


def local(obj, F):
    """Hinh trong he xi-lanh: chi doi Placement (hinh hoc giu nguyen)."""
    s = obj.Shape.copy()
    s.Placement = F.inverse().multiply(s.Placement)
    return s


def put(obj, shape, F):
    """Nhu put() 2026-10-25: obj.Shape = shape lay Placement cua shape -> GOP F·pl."""
    pl = shape.Placement
    obj.Placement = App.Placement()
    obj.Shape = shape
    obj.Placement = F.multiply(pl)


doc = App.openDocument(FCSTD)
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-cylinder-assemblable") if SAVE else None
O = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
for tag, c in CFG.items():
    rod_o, hs_o, nut_o = O["Piston_rod_" + tag], O["Housing_" + tag], O["LK_Nut_M3_piston_" + tag]
    F = rod_o.Placement                       # he xi-lanh (Piston_rod Placement = he xi-lanh, xem script 10-25)
    xg0 = c["x0"] + 1.5; xg1 = xg0 + GW + 2 * FIT; xw1 = xg1 + 1.5; xface = xw1 + 0.5
    xp_ret = xw1 + 0.5; stroke = c["Lmax"] - c["Lmin"]; xt1 = xp_ret + PIST_L + stroke + BUSH_L
    xp = xp_ret + (c["L0"] - c["Lmin"])
    hs, rod = local(hs_o, F), local(rod_o, F)
    assert abs(hs.BoundBox.XMax - xt1) < 0.05, (tag, "mieng ong", hs.BoundBox.XMax, xt1)
    v_h0, v_r0 = hs.Volume, rod.Volume
    # ---- Housing: long ong thang 6,6 x 8,6 (lo bac cu) tu tuong truoc toi mieng ----
    bore_new = rrect(ROD_Y + FIT, ROD_Z + FIT, ROD_R + FIT, xw1 - 0.01, xt1 + 0.1)
    fill = rrect(ROD_Y + FIT, c["bore"] / 2, 1.0, xw1, xt1 - BUSH_L).cut(bore_new)
    hs2 = hs.fuse(fill).removeSplitter()
    # lo ty ren tron qua tuong truoc + web (truoc chi co ranh U tu tam len, web lap mat)
    hs2 = hs2.cut(xcyl(BORE_SCREW, xg1 - 0.1, xw1 + 0.6)).removeSplitter()
    assert hs2.isValid() and len(hs2.Solids) == 1, (tag, "housing", hs2.isValid(), len(hs2.Solids))
    # ---- Piston_rod: got piston ve tiet dien ty; hoc dai oc -> ranh ho mat +y ----
    keep = rrect(ROD_Y, ROD_Z, ROD_R, xp - 0.2, xp + PIST_L + 0.2)
    trim = box(xp - 0.1, xp + PIST_L + 0.1, -6, 6, -10, 10).cut(keep)
    rod2 = rod.cut(trim)
    xn0, xn1 = xp + PIST_L / 2 - (NUT_T + 0.3) / 2, xp + PIST_L / 2 + (NUT_T + 0.3) / 2
    rod2 = rod2.cut(box(xn0, xn1, 0, ROD_Y + 1, -(NUT_AF + 0.2) / 2, (NUT_AF + 0.2) / 2)).removeSplitter()
    assert rod2.isValid() and len(rod2.Solids) == 1, (tag, "rod", rod2.isValid(), len(rod2.Solids))
    # ---- kiem hinh hoc ngay (khong chi tin script): ty truot het ra khoi ong theo +x, dai oc truot ra theo +y ----
    nut = local(nut_o, F)
    assert rod2.common(hs2).Volume < 0.01 and nut.common(rod2).Volume < 0.01 and nut.common(hs2).Volume < 0.01, tag
    for k in range(0, int(xt1 - xp_ret) + 2, 1):   # ty tu tu the goc ra het ong (buoc 1 mm; kiem ky: assembly_paths)
        m = rod2.copy(); m.translate(V(k, 0, 0))
        assert m.common(hs2).Volume < 0.01, (tag, "ty ket o +%d mm" % k)
    for k in range(0, 8):
        m = nut.copy(); m.translate(V(0, k, 0))
        assert m.common(rod2).Volume < 0.01, (tag, "dai oc ket o +%d mm" % k)
    print(tag, "housing V %.1f -> %.1f (+%.1f lap long ong, -lo ty ren)  rod V %.1f -> %.1f  mieng ong x %.1f" % (
        v_h0, hs2.Volume, hs2.Volume - v_h0, v_r0, rod2.Volume, xt1), file=LOG, flush=True)
    assert rod2.Placement.isIdentity(), "Piston_rod phai giu Placement = he xi-lanh (macro lay he toa do tu no)"
    put(hs_o, hs2, F)
    put(rod_o, rod2, F)
    assert rod_o.Placement.isSame(F, 1e-9), (tag, "Placement Piston_rod doi")
doc.recompute()
print("FCSTD", FCSTD, "save", SAVE, file=LOG, flush=True)
if SAVE:
    print("saved", se.save(doc, gui_from=bk), "backup", bk, file=LOG, flush=True)
else:
    doc.saveAs(FCSTD)   # ban sao thu nghiem
