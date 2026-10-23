# Chay trong FreeCAD GUI qua RPC: noi 5 khe < 0.2 mm len 0.2 mm (Tuan 2026-10-23: "khe ~0.2 mm la dep").
# Jaw_1~Jaw_2 la rang an khop -> khong sua. Giu Placement tung chi tiet (macro mo phong dung REST placement).
import FreeCAD as App, Part, time, json

KHE, MAX_BO = 0.2, 20.0  # mm, mm3 (bo nhieu hon = khoet nham -> hoan tac)
doc = App.getDocument("pushrod_arm")
assert doc.UndoCount == 0, "co thao tac chua luu (UndoCount > 0) - dung lai"  # isTouched() bat sau khi nap file, khong tin duoc
bk = r"D:\06_FreeCAD\pushrod_arm\_backup\pushrod_arm.%s.truoc-noi-khe-0.2.FCStd" % time.strftime("%Y%m%d-%H%M%S")
doc.saveCopy(bk)
O = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
V = App.Vector
ra = {"backup": bk, "sua": []}


def khoet(obj, tool_global, ly_do):
    plc = App.Placement(obj.Placement)
    goc = obj.Shape.copy()
    loc = goc.copy(); loc.Placement = App.Placement()
    t = tool_global.copy(); t.transformShape(plc.inverse().toMatrix())
    res = loc.cut(t)
    bo = loc.Volume - res.Volume
    ok = res.isValid() and len(res.Solids) == len(loc.Solids) and 0 < bo <= MAX_BO
    if ok:
        res.Placement = plc
        obj.Shape = res
        assert obj.Placement.isSame(plc, 1e-9)
    ra["sua"].append({"chi_tiet": obj.Label, "ly_do": ly_do, "bo_mm3": round(bo, 3), "ap_dung": ok,
                      "solid": len(res.Solids), "valid": res.isValid()})
    return ok


for t in ("Shoulder", "Elbow"):
    W = O["Pinion_WormWheel_" + t].Shape
    bb = W.BoundBox
    cx, cz, R = bb.Center.x, bb.Center.z, max(bb.XLength, bb.ZLength) / 2
    # 1) washer truc: mai mong phia banh vit
    wa = O["Washer_shaft_" + t]
    d, pts, _ = W.distToShape(wa.Shape)
    pw, pa = pts[0]
    s = 1 if pa.y > pw.y else -1
    wb = wa.Shape.BoundBox
    y0, y1 = sorted((pw.y, pw.y + s * KHE))
    khoet(wa, Part.makeBox(wb.XLength + 2, y1 - y0, wb.ZLength + 2, V(wb.XMin - 1, y0, wb.ZMin - 1)),
          f"khe {d:.2f} -> {KHE} mm: mai washer phia banh vit")
    # 2) housing: khoet lop KHE trong vung banh vit quay (tru ban kinh R + KHE quanh truc Y)
    ho = O["Housing_" + t]
    d, pts, _ = W.distToShape(ho.Shape)
    pw, ph = pts[0]
    s = 1 if ph.y > pw.y else -1
    y0, y1 = sorted((pw.y, pw.y + s * KHE))
    khoet(ho, Part.makeCylinder(R + KHE, y1 - y0, V(cx, y0, cz), V(0, 1, 0)),
          f"khe {d:.2f} -> {KHE} mm: khoet lop {KHE} mm vung banh vit quay (R {R:.2f} + {KHE})")

# 3) Gripper_frame: cat bang than servo dich KHE ve phia frame (chi bo dung phan trung servo)
sv, fr = O["CB_Servo9g_180_gripper"], O["Gripper_frame"]
d, pts, _ = sv.Shape.distToShape(fr.Shape)
ps, pf = pts[0]
huong = (pf - ps); huong.normalize()
tool = sv.Shape.copy(); tool.translate(huong * KHE)
tool = tool.fuse(sv.Shape)  # phu ca khoang giua
khoet(fr, tool, f"khe {d:.2f} -> {KHE} mm: noi hoc servo {KHE} mm theo huong {tuple(round(x, 2) for x in huong)}")

doc.recompute()
# do lai khe tren B-rep
kt = []
for a, b in (("Pinion_WormWheel_Shoulder", "Washer_shaft_Shoulder"), ("Pinion_WormWheel_Elbow", "Washer_shaft_Elbow"),
             ("Housing_Shoulder", "Pinion_WormWheel_Shoulder"), ("Housing_Elbow", "Pinion_WormWheel_Elbow"),
             ("CB_Servo9g_180_gripper", "Gripper_frame")):
    kt.append((a, b, round(O[a].Shape.distToShape(O[b].Shape)[0], 4)))
ra["khe_sau"] = kt
# Tuan 2026-10-23: sua xong tu luu (da co backup o tren); chi luu khi moi khe da dat
if all(x["ap_dung"] for x in ra["sua"]) and all(k[2] >= KHE - 1e-3 for k in kt):
    doc.save()
    ra["da_luu"] = doc.FileName
else:
    ra["da_luu"] = False  # de nguyen trong FreeCAD cho Tuan xem, khong luu
print(json.dumps(ra, ensure_ascii=False))
