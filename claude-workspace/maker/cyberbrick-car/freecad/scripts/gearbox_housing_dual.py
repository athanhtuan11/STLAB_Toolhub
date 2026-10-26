# Vo hop so 030 2 TRUC (LA013) de IN cho cyberbrick-car (Tuan 2026-10-26: "in CB_Gearbox_030_dual_axis, xuat ban in").
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode ../../../tools/robotics-cad/scripts/fc_cli.py --pass freecad/scripts/gearbox_housing_dual.py
# (cwd maker/cyberbrick-car). CHI DOC cyberbrick_car.FCStd. Ra: print/stl-gearbox/*.stl + freecad/images/gearbox-dual/*.png.
# Nguon hinh: CB_Gearbox_030_dual_axis = STEP hang "030 Micro DC Motor with SH1.0 - Reducer-LA024" (bo 1 TRUC, dung tam).
# Huong dan lap hang (Assembly_Guide_of_Dual_Axis_030_Reduction_Motor.pdf) ghi vo la "3D Printed Parts" nhung file in vo
# 2 truc KHONG co trong goi tai (community/cyberbrick-official) -> IN NGUYEN than + nap cua vo trong model (vo 1 truc hang).
# Da thu khoan lo truc ra phia than (2026-10-26): KHONG duoc - trong than co ONG DO truc thep Ø2,1 tu thanh vao ~6 mm ngay
# tren truc ra; khoan Ø5,9 cat roi ong (than tach 2 manh) ma truc Ø5,3 van bi ong chan -> vo 2 truc do banh rang ra kieu
# khac, can file/so do bo LA013 that (TODO). Ban in nay: thu lap motor + banh rang, thu khop khung xe.
# Solid 12/13 (Ø5,1 x 7,7 o x 22) chua ro la chot hay vit ghep -> KHONG in (TODO xem bo that).
import json
import os
import sys

import FreeCAD as App
import MeshPart

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJ, "..", "..", "tools", "robotics-cad", "scripts"))
from mpl_render import render  # noqa: E402

V = App.Vector
STL_DIR = os.path.join(PROJ, "print", "stl-gearbox")
IMG_DIR = os.path.join(PROJ, "freecad", "images", "gearbox-dual")

doc = App.openDocument(os.path.join(PROJ, "freecad", "cyberbrick_car.FCStd"))
gb = [o for o in doc.Objects if o.Label == "CB_Gearbox_030_dual_axis"][0].Shape
# than / nap = 2 solid dai > 50 mm (motor 49,4 mm); than day hon (Y 15,9 vs 7,7)
vo = sorted([s for s in gb.Solids if s.BoundBox.XLength > 50], key=lambda s: -s.BoundBox.YLength)
assert len(vo) == 2, [round(s.BoundBox.XLength, 1) for s in gb.Solids]
than, nap = vo[0].copy(), vo[1].copy()
assert than.isValid() and nap.isValid() and len(than.Solids) == len(nap.Solids) == 1

# huong in: mat ngoai phang up xuong ban (than: mat -Y; nap: mat +Y) -> lo truc dung, khong can do
out, info = {}, {}
for ten, s, goc in (("Gearbox_030_housing", than, 90), ("Gearbox_030_cover", nap, -90)):
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
render([(out["Gearbox_030_housing"], (0.95, 0.80, 0.10))], os.path.join(IMG_DIR, "print-housing.png"), view="iso",
       title="Than vo - huong in (mat ngoai up xuong)")
render([(out["Gearbox_030_cover"], (0.95, 0.80, 0.10))], os.path.join(IMG_DIR, "print-cover.png"), view="iso",
       title="Nap vo - huong in (mat ngoai up xuong)")
App.closeDocument(doc.Name)
print("GEARBOX_OK", json.dumps(info))
