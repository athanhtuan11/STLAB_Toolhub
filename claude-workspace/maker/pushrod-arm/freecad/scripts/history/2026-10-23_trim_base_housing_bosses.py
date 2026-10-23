# Base_housing: 2 tru bat vit (r 2.3, x 15.8 / 43.5) lan 0.1 mm qua mep khe day (x 18..41.3, |y| <= 6.2)
# -> 2 mat up xuong 0.09 mm2 treo tren khe (Bambu bao "floating regions"). Got phan tru nam tren khe.
import FreeCAD as App, Part, json, time
V = App.Vector
P = r"D:/06_FreeCAD/pushrod_arm/"
doc = App.getDocument("pushrod_arm")
assert doc.UndoCount == 0, "co thao tac chua luu - dung lai"
bk = P + "_backup/pushrod_arm.%s.truoc-sua-base-housing.FCStd" % time.strftime("%Y%m%d-%H%M%S")
doc.saveCopy(bk)
o = doc.getObjectsByLabel("Base_housing")[0]
plc = App.Placement(o.Placement)
loc = o.Shape.copy(); loc.Placement = App.Placement()
bb = o.Shape.BoundBox
z_day = bb.ZMin + 3.0                         # mat tren khe (z STL = 3)
khe = Part.makeBox(41.3 - 18.0, 12.4, 13.2, V(18.0, -6.2, z_day))   # lang tru khe, len het chieu cao tru (z 3..16.08 STL)
tru = Part.makeCylinder(2.35, 13.2, V(15.8, 0, z_day)).fuse(Part.makeCylinder(2.35, 13.2, V(43.5, 0, z_day)))
tool = khe.common(tru)
t = tool.copy(); t.transformShape(plc.inverse().toMatrix())
res = loc.cut(t)
bo = loc.Volume - res.Volume
def mat_treo(sh):
    n = 0
    for f in sh.Faces:
        if f.Surface.__class__.__name__ == "Plane" and f.Area < 0.5:
            u, v = f.Surface.parameter(f.CenterOfMass)
            if f.normalAt(u, v).z < -0.99:
                n += 1
    return n
ra = {"backup": bk, "bo_mm3": round(bo, 3), "valid": res.isValid(), "solid": len(res.Solids),
      "mat_treo_nho_truoc": mat_treo(loc), "mat_treo_nho_sau": mat_treo(res)}
ok = res.isValid() and len(res.Solids) == 1 and 0 < bo < 5 and ra["mat_treo_nho_sau"] < ra["mat_treo_nho_truoc"]
if ok:
    res.Placement = plc
    o.Shape = res
    doc.recompute()
    doc.save()
ra["da_luu"] = ok
print(json.dumps(ra, ensure_ascii=False))
