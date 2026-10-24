# Render anh DUYET (xi-lanh 030, bo thu, so khac) - chay FreeCAD GUI RIENG, tu thoat, khong dung phien cua Tuan:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode maker/pushrod-arm/freecad/scripts/render_review.py
# Ra: freecad/images/review/*.png + _render.json. Chi doi hien thi, KHONG Luu .FCStd. (mau theo render_car.py)
import fnmatch
import json
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.dirname(HERE)
OUT = os.path.join(FC, "images", "review")
COL = {"Housing_*": (0.78, 0.80, 0.84), "Worm_*": (0.95, 0.55, 0.10), "CB_030_gearbox_*": (0.20, 0.45, 0.85),
       "Pin_gearbox_*": (0.85, 0.15, 0.15), "Pinion_WormWheel_*": (0.20, 0.65, 0.30), "Rack_*": (0.60, 0.35, 0.75),
       "CB_XA003_XA004_receiver": (0.15, 0.55, 0.25), "Receiver_riser": (0.85, 0.15, 0.15),
       "Turntable_gear_m1_z60": (0.95, 0.60, 0.15), "CB_Servo9g_360_turntable": (0.20, 0.40, 0.85)}
SHOTS = [  # (ten, glob hien, huong nhin, trong suot {glob: %})
    ("01-cylinder-shoulder-iso", ["*_Shoulder", "Pin_gearbox_Shoulder"], "iso", {}),
    ("02-cylinder-shoulder-from-motor", ["*_Shoulder"], "rear", {}),
    ("03-housing-shoulder-number-2", ["Housing_Shoulder"], "front", {}),
    ("04-housing-elbow-number-5", ["Housing_Elbow"], "front", {}),
    ("05-cylinder-elbow-iso", ["*_Elbow", "Pin_gearbox_Elbow"], "iso", {}),
    ("06-gearbox-cradle-no-gearbox", ["Housing_Shoulder", "Worm_Shoulder", "Pinion_WormWheel_Shoulder"], "iso", {}),
    ("07-base-receiver", ["Base_housing", "CB_XA003_XA004_receiver", "Receiver_riser", "Turntable_gear_m1_z60",
                          "CB_Servo9g_360_turntable", "Battery_bay"], "iso", {"Base_housing": 70}),
    ("08-base-receiver-side", ["Base_housing", "Base_deck", "CB_XA003_XA004_receiver", "Receiver_riser",
                               "Turntable_gear_m1_z60"], "front", {"Base_housing": 70, "Base_deck": 70}),
    ("09-full-arm", ["*"], "iso", {}),
]


def match(lbl, pats):
    return any(fnmatch.fnmatch(lbl, p) for p in pats)


def run():
    shots = []
    try:
        os.makedirs(OUT, exist_ok=True)
        doc = App.openDocument(os.path.join(FC, "pushrod_arm.FCStd"))
        Gui.activateWorkbench("PartWorkbench")
        parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.ViewObject]
        for o in parts:
            c = next((v for k, v in COL.items() if fnmatch.fnmatch(o.Label, k)), None)
            if c:
                o.ViewObject.ShapeColor = c
            o.ViewObject.LineColor = (0.15, 0.15, 0.15)
        v = Gui.ActiveDocument.ActiveView
        for name, show, cam, transp in SHOTS:
            for o in parts:
                o.ViewObject.Visibility = match(o.Label, show) and not o.Label.startswith("M2_5")
                o.ViewObject.Transparency = next((t for k, t in transp.items() if fnmatch.fnmatch(o.Label, k)), 0)
            {"iso": v.viewIsometric, "front": v.viewFront, "rear": v.viewRear, "top": v.viewTop}[cam]()
            v.fitAll()
            f = os.path.join(OUT, name + ".png")
            v.saveImage(f, 1400, 1000, "White")
            shots.append(f)
        App.closeDocument(doc.Name)
    except Exception:
        shots.append("FAIL " + traceback.format_exc())
    json.dump(shots, open(os.path.join(OUT, "_render.json"), "w"), indent=1)
    QtCore.QTimer.singleShot(500, Gui.getMainWindow().close)


QtCore.QTimer.singleShot(1500, run)
