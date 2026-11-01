# Render anh duyet line-bot bang CLI (khong mo GUI):
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" freecad/scripts/render_line_bot.py
# Ra: freecad/images/line-bot-{iso,front,top,parts}.png. Chi DOC line_bot.FCStd (sinh tu build_line_bot.py).
import os
import sys

import FreeCAD as App

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(FC, "..", "..", "..", "tools", "robotics-cad", "scripts"))
from mpl_render import render  # noqa: E402

OUT = os.path.join(FC, "images")
os.makedirs(OUT, exist_ok=True)
doc = App.openDocument(os.path.join(FC, "line_bot.FCStd"))

MAU = {"Ref_Mega": (0.12, 0.48, 0.35), "Ref_Wheel_L": (0.17, 0.17, 0.17), "Ref_Wheel_R": (0.17, 0.17, 0.17),
       "Ref_Battery": (0.79, 0.69, 0.23), "Ref_Sonar": (0.76, 0.29, 0.33), "Ref_Line_array": (0.49, 0.37, 0.83),
       "Ref_Driver": (0.85, 0.45, 0.15), "Ref_Ball": (0.7, 0.7, 0.7), "Ref_N20_L": (0.6, 0.64, 0.68),
       "Ref_N20_R": (0.6, 0.64, 0.68)}
IN = (0.23, 0.56, 0.85)
items, parts = [], []
for o in doc.Objects:
    if not (o.isDerivedFrom("Part::Feature") and o.Shape.Solids):
        continue
    if o.Label.startswith("Ref_"):
        items.append((o.Shape, MAU.get(o.Label, (0.6, 0.6, 0.6))))
    else:
        items.append((o.Shape, IN, 0.92 if o.Label == "Top_plate" else 1.0))
        parts.append(o)

for v in ("iso", "front", "top"):
    render(items, os.path.join(OUT, f"line-bot-{v}.png"), view=v, title=f"line-bot – concept A · {v}")

# chi tiet in xep canh nhau (de nhin tung con)
x = 0.0
lay = []
for o in parts:
    s = o.Shape.copy()
    b = s.BoundBox
    s.translate(App.Vector(x - b.XMin, -b.Center.y, -b.ZMin))
    lay.append((s, IN))
    x += b.XLength + 15
render(lay, os.path.join(OUT, "line-bot-parts.png"), view="iso", title="line-bot – 7 chi tiết in")
print("RENDER OK", OUT)
