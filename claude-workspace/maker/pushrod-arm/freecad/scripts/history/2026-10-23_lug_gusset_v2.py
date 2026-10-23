# Vat 45 do duoi 4 vau deck - lan 2: lay DUNG z mat day vau tu B-rep (lan 1 dat thap 0.74 mm -> khong cham vau).
import FreeCAD as App, Part, json, time
V = App.Vector
P = r"D:/06_FreeCAD/pushrod_arm/"
doc = App.getDocument("pushrod_arm")
assert doc.UndoCount == 0, "co thao tac chua luu - dung lai"
bk = P + "_backup/pushrod_arm.%s.truoc-vat-vau-2.FCStd" % time.strftime("%Y%m%d-%H%M%S")
doc.saveCopy(bk)
bh = doc.getObjectsByLabel("Base_housing")[0]
plc = App.Placement(bh.Placement)
assert plc.isSame(App.Placement(), 1e-9), "Base_housing co Placement khac goc - xem tay"
s = bh.Shape
ra = {"backup": bk, "vau": []}
them = None
for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
    x0, x1 = sorted((sx * 31.94, sx * 38.74)); y0, y1 = sorted((sy * 31.94, sy * 38.74))
    day = []
    for f in s.Faces:
        if f.Surface.__class__.__name__ != "Plane":
            continue
        b = f.BoundBox
        if abs(b.ZMax - b.ZMin) > 1e-6 or not (24.0 < b.ZMin < 28.0):
            continue
        c = f.CenterOfMass
        if not (x0 - 0.5 < c.x < x1 + 0.5 and y0 - 0.5 < c.y < y1 + 0.5):
            continue
        u, v = f.Surface.parameter(c)
        if f.normalAt(u, v).z < -0.99:
            day.append((round(b.ZMin, 4), round(f.Area, 2)))
    zt = min(z for z, a in day)
    cot = Part.makeBox(x1 - x0, y1 - y0, 11, V(x0, y0, zt - 11))
    u = V(sx, sy, 0); u.normalize()
    n = u + V(0, 0, 1); n.normalize()
    t = V(-sy, sx, 0); t.normalize()
    e1 = t.cross(n)
    p0 = V(sx * 31.94, sy * 31.94, zt)
    nua = Part.makeBox(200, 200, 200)
    nua.Placement = App.Placement(p0 - e1 * 100 - t * 100, App.Rotation(e1, t, n, "ZXY"))
    w = cot.common(nua)
    them = w if them is None else them.fuse(w)
    ra["vau"].append({"goc": [sx, sy], "mat_day": day, "zt": zt})
res = s.fuse(them).removeSplitter()
O = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
cham = [o.Label for o in O.values() if o.Label != "Base_housing" and o.Shape.BoundBox.intersect(them.BoundBox)
        and o.Shape.common(them).Volume > 0.01]
them_v = res.Volume - s.Volume
ok = res.isValid() and len(res.Solids) == 1 and 0 < them_v < 1000 and not cham
ra.update({"them_mm3": round(them_v, 1), "cham": cham, "valid": res.isValid(), "solid": len(res.Solids)})
if ok:
    bh.Shape = res
    doc.recompute()
    doc.save()
ra["da_luu"] = ok
print(json.dumps(ra, ensure_ascii=False))
