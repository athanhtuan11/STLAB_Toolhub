# Vo hop so 030 2 TRUC (LA013) de IN cho cyberbrick-car (Tuan 2026-10-26: "in CB_Gearbox_030_dual_axis, xuat ban in").
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode ../../../tools/robotics-cad/scripts/fc_cli.py --pass freecad/scripts/gearbox_housing_dual.py
# (cwd maker/cyberbrick-car). CHI DOC cyberbrick_car.FCStd. Ra: print/stl-gearbox/*.stl + freecad/images/gearbox-dual/*.png.
# Nguon hinh: CB_Gearbox_030_dual_axis = STEP hang "030 Micro DC Motor with SH1.0 - Reducer-LA024" (bo 1 TRUC, dung tam).
# Huong dan lap hang (Assembly_Guide_of_Dual_Axis_030_Reduction_Motor.pdf) ghi vo la "3D Printed Parts" nhung file in vo
# 2 truc KHONG co trong goi tai, Codex tra web cung khong thay file chinh hang (2026-10-26) -> TU DUNG tu vo 1 truc hang:
# Gemini doc 2 huong dan lap (1 truc / 2 truc): ban 2 truc dung TRUC RA KIM LOAI mat D 2 dau (ep vao banh rang lon nhat),
# than duoi co LO XUYEN doi xung voi nap; ban 1 truc than co lo CUT (ong giu chot thep Ø2,1 cho banh rang ra quay).
# Do tren STEP hang (truc ra x 0, z 16,8 he xe; truc Y): nap = lo xuyen Ø5,7 (truc Ø5,3, khe 0,2/ben) + go do huong vao
# Ø5,7/Ø8,5 cao 1,0 (nap: ban y 8..9, go y 7..8); than = thanh kin 1,0 (y -9..-8) + ong chot Ø2,5/Ø4,8 toi y -2,9.
# Sua THAN: bo ong chot, khoan lo xuyen Ø5,7, them go do Ø5,7/Ø8,5 day 1,0 doi xung nap. Nap giu nguyen.
# TODO doi chieu bo LA013 that: duong kinh / mat D truc kim loai, vi tri doc truc banh rang ra.
# Solid 12/13 (Ø5,1 x 7,7 o x 22) chua ro chot hay vit ghep -> KHONG in.
import json
import os
import sys

import FreeCAD as App
import MeshPart
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJ, "..", "..", "tools", "robotics-cad", "scripts"))
import cad_lib as cl  # noqa: E402
from mpl_render import render  # noqa: E402

V = App.Vector
AX = (0.0, 16.8)             # truc ra (x, z) he xe - tam lo nap
R_LO, R_GO = 2.85, 4.25      # do tren nap: lo Ø5,7, go Ø8,5
Y_THANH_TRONG = -8.0         # mat trong thanh than (do isInside: thanh y -9,0..-8,0 day 1,0 = ban nap y 8,0..9,0)
GO_DAY = 1.0                 # go do nap cao 1,0 (y 7,0..8,0)
STL_DIR = os.path.join(PROJ, "print", "stl-gearbox")
IMG_DIR = os.path.join(PROJ, "freecad", "images", "gearbox-dual")

def dual_housing(doc):
    """(than 2 truc, nap, truc_ra_mau, cac solid con lai cua hop so) trong he xe - dung chung cho ban in + anh lap."""
    gb = [o for o in doc.Objects if o.Label == "CB_Gearbox_030_dual_axis"][0].Shape
    # than / nap = 2 solid dai > 50 mm (motor 49,4 mm); than day hon (Y 15,9 vs 7,7)
    vo = sorted([s for s in gb.Solids if s.BoundBox.XLength > 50], key=lambda s: -s.BoundBox.YLength)
    assert len(vo) == 2, [round(s.BoundBox.XLength, 1) for s in gb.Solids]
    than, nap = vo[0].copy(), vo[1].copy()
    assert than.isValid() and nap.isValid() and len(than.Solids) == len(nap.Solids) == 1
    v0 = than.Volume
    # 1) lo xuyen Ø5,7 qua thanh + bo ong chot (ong Ø4,8 < Ø5,7 nam gon trong dao) - dao lo ra ngoai 1 mm, toi het ong (-2,9)
    than = than.cut(cl.cyl(R_LO, "y", (than.BoundBox.YMin - 1, -2.5), AX))
    v1 = than.Volume
    # 2) go do huong vao doi xung nap: vanh Ø5,7/Ø8,5 day 1,0 tu mat trong thanh
    # long vo o phia +Y (thanh y -9..-8) -> go tu -8,05 (an 0,05 vao thanh) toi -7,0 = doi xung go nap
    go = cl.cyl(R_GO, "y", (Y_THANH_TRONG - 0.05, Y_THANH_TRONG + GO_DAY), AX).cut(
        cl.cyl(R_LO, "y", (Y_THANH_TRONG - 1, Y_THANH_TRONG + GO_DAY + 1), AX))
    than = than.fuse(go).removeSplitter()
    print("THAN V %.1f -> cat %.1f -> them go %.1f" % (v0, v1, than.Volume))
    assert than.isValid() and len(than.Solids) == 1, (than.isValid(), len(than.Solids))
    assert 30 < v0 - v1 < 150 and 15 < than.Volume - v1 < 40, (v0 - v1, than.Volume - v1)
    # kiem: truc Ø5,3 di xuyen than + nap khong cham (khe 0,2/ben)
    truc = cl.cyl(2.65, "y", (-20, 20), AX)
    assert truc.common(than).Volume < 1e-3 and truc.common(nap).Volume < 1e-3, "truc ra cham vo"
    rest = [s for s in gb.Solids if s.BoundBox.XLength <= 50]
    return than, nap, truc, rest


if __name__ == "__main__":
    doc = App.openDocument(os.path.join(PROJ, "freecad", "cyberbrick_car.FCStd"))
    than, nap, truc, _ = dual_housing(doc)

    # huong in: mat ngoai phang up xuong ban (than: mat -Y; nap: mat +Y) -> lo truc dung, khong can do
    out, info = {}, {}
    for ten, s, goc in (("Gearbox_030_dual_housing", than, 90), ("Gearbox_030_cover", nap, -90)):
        p = s.copy()
        p.rotate(V(0, 0, 0), V(1, 0, 0), goc)
        bb = p.BoundBox
        p.translate(V(-bb.Center.x, -bb.Center.y, -bb.ZMin))
        out[ten] = p
        bb = p.BoundBox
        info[ten] = {"hop_bao_mm": [round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2)],
                     "the_tich_mm3": round(p.Volume, 1)}
    os.makedirs(STL_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    for ten, p in out.items():
        m = MeshPart.meshFromShape(Shape=p, LinearDeflection=0.03, AngularDeflection=0.2618, Relative=False)
        m.write(os.path.join(STL_DIR, ten + ".stl"))
    json.dump(info, open(os.path.join(STL_DIR, "_gearbox.json"), "w"), indent=1)

    # anh duyet: than (lo moi do), nap, va ca bo trong he xe
    render([(out["Gearbox_030_dual_housing"], (0.95, 0.80, 0.10))], os.path.join(IMG_DIR, "print-housing.png"), view="iso",
           title="Than vo 2 truc - huong in (mat ngoai up xuong)")
    render([(than, (0.95, 0.80, 0.10)), (truc, (0.55, 0.55, 0.6))], os.path.join(IMG_DIR, "housing-shaft-through.png"),
           view=(20.0, -60.0), title="Than vo 2 truc + truc ra Ø5,3 xuyen (xam)")
    render([(out["Gearbox_030_cover"], (0.95, 0.80, 0.10))], os.path.join(IMG_DIR, "print-cover.png"), view="iso",
           title="Nap vo - huong in (mat ngoai up xuong)")
    App.closeDocument(doc.Name)
    print("GEARBOX_OK", json.dumps(info))
