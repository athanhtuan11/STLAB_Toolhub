# Render anh xe (mau theo colors.json) - chay FreeCAD GUI rieng, tu dong thoat:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" freecad/scripts/render_car.py
# Ra: freecad/images/car-*.png. Chi doi hien thi, KHONG luu file .FCStd.
import json, os
import FreeCAD as App, FreeCADGui as Gui
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.dirname(HERE)
OUT = os.path.join(FC, "images")


def run():
    os.makedirs(OUT, exist_ok=True)
    doc = App.openDocument(os.path.join(FC, "cyberbrick_car.FCStd"))
    Gui.activateWorkbench("PartWorkbench")
    colors = json.load(open(os.path.join(FC, "colors.json")))
    for o in doc.Objects:
        vo = o.ViewObject
        if vo is None:
            continue
        c = colors.get(o.Label)
        if c:
            vo.ShapeColor = tuple(c)
        vo.LineColor = (0.15, 0.15, 0.15)
        vo.Visibility = True                                                # file sinh headless: mac dinh an
    v = Gui.ActiveDocument.ActiveView
    body = doc.getObjectsByLabel("Body_coupe")[0]
    shots = []
    for name, cam, hide_body in (("car-iso", "iso", False), ("car-side", "left", False), ("car-front", "front", False),
                                 ("car-top", "top", False), ("chassis-iso", "iso", True), ("chassis-top", "top", True)):
        body.ViewObject.Visibility = not hide_body
        {"iso": v.viewIsometric, "left": v.viewLeft, "front": v.viewFront, "top": v.viewTop}[cam]()
        if cam == "iso":
            v.viewIsometric()
        v.fitAll()
        f = os.path.join(OUT, name + ".png")
        v.saveImage(f, 1600, 1100, "White")
        shots.append(f)
    body.ViewObject.Visibility = True
    json.dump(shots, open(os.path.join(OUT, "_render.json"), "w"))
    App.closeDocument(doc.Name)
    QtCore.QTimer.singleShot(500, Gui.getMainWindow().close)


QtCore.QTimer.singleShot(1500, run)
