# Anh duyet ket qua giao viec: chi tiet nguoi thuc thi dung (cam) + chi tiet lan can trong context (xam).
#   freecadcmd render_pilot.py <thu muc giao viec>   -> <thu muc>/review-iso.png, review-top.png
import os, sys
import FreeCAD as App, Part
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "robotics-cad", "scripts"))
from mpl_render import render  # noqa: E402

run = [a for a in sys.argv[1:] if not a.endswith(".py")][0]
part = Part.read(os.path.join(run, "part.step"))
d = App.openDocument(os.path.join(run, "context.FCStd"))
ctx = [o.Shape for o in d.Objects if hasattr(o, "Shape") and o.Shape.Solids]
bb = part.BoundBox
near = [s for s in ctx if s.BoundBox.intersect(bb.enlarge(8) or bb)]
for name, view in (("review-iso", "iso"), ("review-solo", (25.0, -60.0))):
    its = [(part, (0.95, 0.45, 0.10))] + ([(s, (0.75, 0.75, 0.78)) for s in near] if name == "review-iso" else [])
    render(its, os.path.join(run, name + ".png"), view=view, fit=[part], tol=0.1)
print("RENDER_OK")
