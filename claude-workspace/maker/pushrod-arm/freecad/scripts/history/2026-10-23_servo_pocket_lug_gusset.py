# (1) Mai hoc servo Gripper_frame: dun 2 mat servo (noi rong 0.2 mm) day 0.2 mm lam dao -> khe 0.2.
# (2) Vat 45 do duoi 4 vau bat vit deck trong Base_housing (bo support ban P1).
import FreeCAD as App, Part, json, time, math
V = App.Vector
P = r"D:/06_FreeCAD/pushrod_arm/"
KHE = 0.2
doc = App.getDocument("pushrod_arm")
assert doc.UndoCount == 0, "co thao tac chua luu - dung lai"
rest = json.load(open(P + "pushrod_arm_rest.json"))
lech = [o.Label for o in doc.Objects if o.Name in rest and not o.Placement.isSame(
    App.Placement(V(*rest[o.Name][0]), App.Rotation(*rest[o.Name][1])), 1e-6)]
assert not lech, "khong o tu the goc: %s" % lech[:5]
bk = P + "_backup/pushrod_arm.%s.truoc-mai-servo-vat-vau.FCStd" % time.strftime("%Y%m%d-%H%M%S")
doc.saveCopy(bk)
O = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
ra = {"backup": bk}


def cat_cuc_bo(obj, tool, cong=False):
    plc = App.Placement(obj.Placement)
    loc = obj.Shape.copy(); loc.Placement = App.Placement()
    t = tool.copy(); t.transformShape(plc.inverse().toMatrix())
    res = (loc.fuse(t).removeSplitter() if cong else loc.cut(t))
    return loc, res, plc


# (1) servo
sv, fr = O["CB_Servo9g_180_gripper"], O["Gripper_frame"]
d, pts, _ = sv.Shape.distToShape(fr.Shape)
y = pts[0][0].y
h = 1 if pts[0][1].y > y else -1
mats = [f for f in sv.Shape.Faces if f.Surface.__class__.__name__ == "Plane"
        and abs(f.BoundBox.YMax - f.BoundBox.YMin) < 1e-6 and abs(f.BoundBox.YMin - y) < 0.01]
dao = None
for f in mats:
    fo = f.makeOffset2D(KHE + 0.05, 0)  # noi rong mat de mep cung dat khe
    s = fo.extrude(V(0, h * (KHE + 0.001), 0))
    dao = s if dao is None else dao.fuse(s)
loc, res, plc = cat_cuc_bo(fr, dao)
bo = loc.Volume - res.Volume
ok1 = res.isValid() and len(res.Solids) == 1 and 0 < bo < 20
if ok1:
    res.Placement = plc; fr.Shape = res
ra["servo"] = {"khe_truoc": round(d, 3), "so_mat": len(mats), "bo_mm3": round(bo, 3), "ap_dung": ok1,
               "khe_sau": round(sv.Shape.distToShape(fr.Shape)[0], 3)}

# (2) vat 45 do duoi vau: o moi goc, lang tru = day vau dun xuong 10 mm, giu phan "ngoai" mat phang 45 do
bh = O["Base_housing"]
zt = 24.5  # mat duoi vau (toa do mo hinh; STL = -4)
them = None
for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
    x0, x1 = sorted((sx * 31.94, sx * 38.74)); y0, y1 = sorted((sy * 31.94, sy * 38.74))
    cot = Part.makeBox(x1 - x0, y1 - y0, 10, V(x0, y0, zt - 10))
    u = V(sx, sy, 0); u.normalize()
    n = u + V(0, 0, 1); n.normalize()                   # phap tuyen mat 45 do (huong ra vach + len)
    t = V(-sy, sx, 0); t.normalize()
    e1 = t.cross(n)
    p0 = V(sx * 31.94, sy * 31.94, zt)                  # goc trong cua vau
    nua = Part.makeBox(200, 200, 200)
    nua.Placement = App.Placement(p0 - e1 * 100 - t * 100, App.Rotation(e1, t, n, "ZXY"))
    w = cot.common(nua)
    them = w if them is None else them.fuse(w)
loc2, res2, plc2 = cat_cuc_bo(bh, them, cong=True)
them_v = res2.Volume - loc2.Volume
ok2 = res2.isValid() and len(res2.Solids) == 1 and 0 < them_v < 800
if ok2:
    res2.Placement = plc2; bh.Shape = res2
ra["vau"] = {"them_mm3": round(them_v, 1), "ap_dung": ok2, "valid": res2.isValid(), "solid": len(res2.Solids)}

# kiem va cham phan them voi chi tiet khac
if ok2:
    cham = [o.Label for o in O.values() if o.Label != "Base_housing" and o.Shape.BoundBox.intersect(them.BoundBox)
            and o.Shape.common(them).Volume > 0.01]
    ra["vau"]["cham"] = cham
    ok2 = not cham
doc.recompute()
if ok1 and ok2 and ra["servo"]["khe_sau"] >= KHE - 1e-3:
    doc.save(); ra["da_luu"] = True
else:
    ra["da_luu"] = False  # de nguyen trong FreeCAD cho Tuan xem
print(json.dumps(ra, ensure_ascii=False))
