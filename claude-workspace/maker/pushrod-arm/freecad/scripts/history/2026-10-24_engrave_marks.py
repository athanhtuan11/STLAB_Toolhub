# CLI (freecadcmd --safe-mode): khac chim dau lap len 2 vo xi-lanh (chi tiet in lai).
# Tuan 2026-10-24: "Danh dau vi tri gan voi nhau. Huong dan lap dat se tot hon." -> sau do: "thay vi khac chu thi
# nen khac so. 1 se khop voi lo 1 ... cac khop cung so se lap vao voi nhau".
# So khop (thu tu lap ASSEMBLY.md): 1 S Turret-Boom, 2 A Turret-Housing_Shoulder, 3 B Boom-Rack_Shoulder,
# 4 E Boom-Forearm, 5 C Boom-Housing_Elbow, 6 D Forearm-Rack_Elbow. Chi khac tren chi tiet IN LAI (2 vo xi-lanh).
# Mat ngoai phang y = -6 (he xi-lanh) cua ong truot = mat up xuong ban in (print.yaml rotate x 90) -> chu chim in ro.
import sys
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
FONT = "C:/Windows/Fonts/arialbd.ttf"
DEPTH, SIZE, FACE_Y = 0.4, 6.0, -6.0
# vi tri: ban do mat y=-6 (2026-10-24) - phang + dac o x 16..70, z -4..4 (x < 16 la tai chot, co bac)
MARKS = {"Shoulder": [("2", 17.0)],   # canh tai chot A (x 0): khop so 2
         "Elbow": [("5", 17.0)]}      # canh tai chot C: khop so 5

doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-engrave-marks")
O = {o.Label: o for o in doc.Objects}


def text_solid(txt, x0):
    """Chu trong mat y = FACE_Y, doc tu phia -y (x -> phai, z -> len), dun 0,4 mm vao +y."""
    faces = []
    for ch in Part.makeWireString(txt, FONT, SIZE, 0.0):
        ws = [w for w in ch]
        if not ws:
            continue
        ws.sort(key=lambda w: -Part.Face(w).Area)
        f = Part.Face(ws[0])
        for h in ws[1:]:  # lo ben trong chu (A, B, D...) : wire nam trong wire ngoai
            hf = Part.Face(h)
            f = f.cut(hf) if f.common(hf).Area > 1e-6 else f.fuse(hf)
        faces.append(f)
    sh = Part.makeCompound(faces)
    bb = sh.BoundBox
    sh.translate(V(-bb.XMin, -bb.YMin - bb.YLength / 2, 0))
    sh.rotate(V(0, 0, 0), V(1, 0, 0), 90)              # Y chu -> +z, Z -> -y
    sh.translate(V(x0, FACE_Y - 0.1, 0))
    return sh.extrude(V(0, DEPTH + 0.1, 0)), sh.BoundBox


rep = {}
for tag, marks in MARKS.items():
    R = O["Rack_" + tag].Placement
    ho = O["Housing_" + tag]
    hl = ho.Shape.copy(); hl.transformShape(R.inverse().toMatrix())
    tools = []
    for txt, x0 in marks:
        sol, bb = text_solid(txt, x0)
        # vung chu phai nam tren mat phang, dac (khong vat, khong lo): luoi diem ngay duoi mat / ngay ngoai mat
        for i in range(9):
            for k in range(5):
                x = bb.XMin + (bb.XMax - bb.XMin) * i / 8
                z = bb.ZMin + (bb.ZMax - bb.ZMin) * k / 4
                assert hl.isInside(V(x, FACE_Y + DEPTH + 0.3, z), 1e-4, True), (tag, txt, "khong dac", x, z)
                assert not hl.isInside(V(x, FACE_Y - 0.05, z), 1e-4, True), (tag, txt, "khong phai mat ngoai", x, z)
        tools.append(sol)
    new = hl.cut(tools).removeSplitter()
    rm = hl.Volume - new.Volume
    assert new.isValid() and len(new.Solids) == 1 and 1.0 < rm < 60.0, (tag, rm)
    s = new.copy(); s.transformShape(R.toMatrix())
    if not s.Placement.isSame(App.Placement(), 1e-9):
        s = Part.makeCompound([s])
    se.apply(ho, s)
    if "STLab_Marks" not in ho.PropertiesList:
        ho.addProperty("App::PropertyString", "STLab_Marks", "STLab", "Dau khac chim (huong dan lap)")
    ho.STLab_Marks = ", ".join(t for t, _ in marks) + "  (so khop, mat ngoai y=-6 canh tai chot, sau 0,4 mm)"
    rep[tag] = round(rm, 1)

doc.recompute()
print("RES removed mm3", rep)
print("RES saved", se.save(doc, gui_from=bk))
