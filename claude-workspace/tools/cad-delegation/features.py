# Trich dac trung hinh hoc 1 chi tiet trong FCStd (de Claude viet spec giao viec, khong doc ca script dung hinh).
#   freecadcmd features.py <file.FCStd> <Label> [out.json] [local]
#   local: do trong he toa do rieng cua chi tiet (Placement cua no) - ca lan can cung doi sang he do
# In: bao, the tich, cac mat tru (r, truc, tam, chieu dai), mat phang (phap tuyen, vi tri, dien tich),
#     chi tiet lan can (khoang cach < 1 mm) + khoang cach nho nhat.
import json, sys
import FreeCAD as App

LOCAL = "local" in sys.argv[1:]
args = [a for a in sys.argv[1:] if not a.endswith(".py") and a != "local"]
fc, label = args[0], args[1]
out = args[2] if len(args) > 2 else None
doc = App.openDocument(fc)
objs = {o.Label: o for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Solids}
INV = objs[label].Placement.inverse().toMatrix() if LOCAL else App.Matrix()


def shp(o):
    """hinh trong he do; transformShape giu mat giai tich (transformGeometry bien thanh B-spline)"""
    c = o.Shape.copy()
    if LOCAL:
        c.transformShape(INV)
    return c


s = shp(objs[label])
r3 = lambda v: [round(v.x, 2), round(v.y, 2), round(v.z, 2)]
bb = s.BoundBox
res = dict(label=label, frame="local" if LOCAL else "global", volume=round(s.Volume, 1), solids=len(s.Solids), valid=s.isValid(),
           bbox=[round(x, 2) for x in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)], cylinders=[], planes=[])
seen = set()
for f in s.Faces:
    srf = f.Surface
    t = type(srf).__name__
    if t == "Cylinder":
        a = srf.Axis
        c = srf.Center
        # chieu dai doc truc
        ts = [(v.Point - c).dot(a) for v in f.Vertexes] or [0]
        key = (round(srf.Radius, 2), tuple(r3(a)), tuple(r3(c - a * (c.dot(a)))))
        hole = f.Orientation == "Reversed"
        res["cylinders"].append(dict(r=round(srf.Radius, 3), axis=r3(a), center=r3(c), along=[round(min(ts), 2), round(max(ts), 2)],
                                     hole=hole, area=round(f.Area, 1)))
    elif t == "Plane":
        n = f.normalAt(0, 0)
        res["planes"].append(dict(normal=r3(n), at=round(f.CenterOfMass.dot(n), 2), area=round(f.Area, 1), com=r3(f.CenterOfMass)))
    else:
        res.setdefault("other", {}).setdefault(t, 0)
        res["other"][t] += 1
res["planes"] = sorted(res["planes"], key=lambda p: -p["area"])[:25]
nb = []
for k, o in objs.items():
    if k == label or o.TypeId != "Part::Feature":
        continue
    os_ = shp(o)
    ob = os_.BoundBox
    if not bb.intersect(ob) and bb.Center.distanceToPoint(ob.Center) > (bb.DiagonalLength + ob.DiagonalLength) / 2 + 1:
        continue
    try:
        d = s.distToShape(os_)[0]
    except Exception:
        continue
    if d < 1.0:
        nb.append(dict(label=k, dist=round(d, 3), bbox=[round(x, 2) for x in (ob.XMin, ob.YMin, ob.ZMin, ob.XMax, ob.YMax, ob.ZMax)]))
res["neighbors"] = sorted(nb, key=lambda x: x["dist"])
txt = json.dumps(res, indent=1)
if out:
    open(out, "w").write(txt)
print("FEATURES_JSON_BEGIN"); print(txt); print("FEATURES_JSON_END")
