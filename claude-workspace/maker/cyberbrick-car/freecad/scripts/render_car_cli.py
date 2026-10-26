# Render anh xe bang CLI (khong mo GUI FreeCAD - Tuan 2026-10-25: "mac dinh CLI de khong bi crash"):
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" freecad/scripts/render_car_cli.py
# Ra: freecad/images/car-*.png (mau theo colors.json). Chi DOC .FCStd. Ban GUI cu: render_car.py.
import json, os, sys
import FreeCAD as App

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FC, "..", "..", "..", "tools", "robotics-cad", "scripts"))
from mpl_render import render  # noqa: E402

OUT = os.path.join(FC, "images")
doc = App.openDocument(os.path.join(FC, "cyberbrick_car.FCStd"))
colors = json.load(open(os.path.join(FC, "colors.json")))
items = [(o.Label, o.Shape, tuple(colors.get(o.Label, (0.6, 0.6, 0.6))))
         for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Solids]
body = [s for k, s, c in items if k == "Body_coupe"][0]
pts = body.tessellate(0.1)[0]                                                # bao that (BoundBox B-spline phong to)
bb = [round(f(getattr(p, a) for p in pts), 1) for a in "xyz" for f in (min, max)]
print("BODY_BB", bb, "dai x rong x cao", round(bb[1] - bb[0], 1), round(bb[3] - bb[2], 1), round(bb[5] - bb[4], 1))
shots = []
for name, view, hide_body in (("car-iso", "iso", False), ("car-side", (0.0, -90.0), False),
                              ("car-front-34", (20.0, 35.0), False), ("car-rear-34", (25.0, -150.0), False),
                              ("car-front", "front", False), ("car-top", "top", False), ("chassis-iso", "iso", True),
                              ("chassis-top", "top", True)):
    its = [(s, c) for k, s, c in items if not (hide_body and k == "Body_coupe")]
    f = os.path.join(OUT, name + ".png")
    render(its, f, view=view, fit=[body], tol=0.2)
    shots.append(f)
json.dump(shots, open(os.path.join(OUT, "_render.json"), "w"))
App.closeDocument(doc.Name)
print("OUT", shots)
