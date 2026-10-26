# Tao context.FCStd cho 1 lan giao viec: CHI chi tiet lan can (khong co chi tiet mau), doi sang he toa do cua spec.
#   freecadcmd make_context.py <du_an.FCStd> <frame: Label (he rieng cua no) | global> <out.FCStd> <Label1> [Label2 ...]
import sys
import FreeCAD as App, Part

a = [x for x in sys.argv[1:] if not x.endswith(".py")]
src, frame, dst, labels = a[0], a[1], a[2], a[3:]
d = App.openDocument(src)
O = {o.Label: o for o in d.Objects if hasattr(o, "Shape") and o.Shape.Solids}
inv = O[frame].Placement.inverse().toMatrix() if frame != "global" else App.Matrix()
n = App.newDocument("context")
for lb in labels:
    s = O[lb].Shape.copy()
    s.transformShape(inv)
    f = n.addObject("Part::Feature", "c")
    f.Label, f.Shape = lb, Part.Shape(s)
    b = s.BoundBox
    print("CTX", lb, [round(x, 2) for x in (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)])
n.saveAs(dst)
print("SAVED", dst)
