# Anh huong dan lap cho HOC SINH (Tuan 2026-10-25: "hoc sinh lop 6 lap se kho lam. chi tiet tung bo phan").
# Moi buoc 1 thao tac, 3 anh: c = chi tiet can lay (chi hien chi tiet moi), a = toan canh (phan da lap mo, chi tiet moi
# to xanh), b = phong to chi tiet moi. Chay trong FreeCAD GUI RIENG (khong dung phien cua Tuan), KHONG Luu file:
#   set FC_FILE=...\pushrod_arm.FCStd  set FC_SCRIPT=...\render_assembly_steps.py  set FC_OUT=<log>
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode maker/robotics-cad/scripts/gui_run.py
# Thu tu buoc = ASSEMBLY.md (dong ma buoc o dau moi "## Buoc"). Ra: freecad/images/assembly/step-XX-{c,a,b}.png + steps.json
import fnmatch
import json
import time
import os

import FreeCAD as App
import FreeCADGui as Gui

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
OUT = P + "images/assembly/"
W, H = 1200, 900
STEPS = [  # (ma buoc, [glob Label chi tiet MOI]) - buoc khong co chi tiet moi: [] (chi chup toan canh)
    ("01", ["Base_foot", "Base_housing"]),
    ("02", ["Battery_bay"]),
    ("03", ["Receiver_riser"]),
    ("04", ["CB_XA003_XA004_receiver"]),
    ("05", ["CB_Servo9g_360_turntable"]),
    ("06", ["Pinion_m1_z10_turntable"]),
    ("07", ["Base_deck", "Slide_ring"]),
    ("08", ["Turntable"]),
    ("09", ["Turntable_gear_m1_z60", "M2_5x10_gear*"]),
    ("10", ["M2_5x8_deck*"]),
    ("11", ["Turret_one_piece", "M2_5x6_turret*"]),
    ("12", ["Housing_Shoulder", "Pinion_WormWheel_Shoulder"]),
    ("13", ["Washer_shaft_Shoulder", "M2_5x6_shaft_Shoulder"]),
    ("14", ["Rack_Shoulder"]),
    ("15", ["Housing_Elbow", "Pinion_WormWheel_Elbow"]),
    ("16", ["Washer_shaft_Elbow", "M2_5x6_shaft_Elbow"]),
    ("17", ["Rack_Elbow"]),
    ("18", ["Boom001", "Spacer_S", "Spacer_S001", "Pin_S", "Pin_S_washer", "Pin_S_M2_5x6"]),
    ("19", ["Spacer_A", "Spacer_A001", "Pin_A", "Pin_A_washer", "Pin_A_M2_5x6"]),
    ("20", ["Pin_B", "Pin_B_washer", "Pin_B_M2_5x6"]),
    ("21", ["Forearm_plate_L", "Forearm_plate_R", "Wrist_spacer", "M2_5x6_wrist_spacer*"]),
    ("22", ["Spacer_D", "Spacer_E"]),
    ("23", ["Pin_E", "Pin_E_washer", "Pin_E_M2_5x6"]),
    ("24", ["Pin_C", "Pin_C_washer", "Pin_C_M2_5x6"]),
    ("25", ["Pin_D", "Pin_D_washer", "Pin_D_M2_5x6"]),
    ("26", []),
    ("27", ["CB_030_gearbox_Shoulder", "Worm_Shoulder", "Pin_gearbox_Shoulder"]),
    ("28", ["CB_030_gearbox_Elbow", "Worm_Elbow", "Pin_gearbox_Elbow"]),
    ("29", ["Gripper_frame", "CB_Servo9g_180_gripper"]),
    ("30", ["Servo_horn", "Jaw_1_driven_by_servo"]),
    ("31", ["Pin_jaw2", "Spacer_jaw2", "Jaw_2_idler"]),
    ("32", ["Gripper_top_plate", "M2_5x6_top*", "Washer_pin", "M2_5x6_pin"]),
    ("33", ["*_TPU_pad"]),
    ("34", ["M2_5x6_wrist", "M2_5x6_wrist00*"]),
]

doc = App.ActiveDocument
gd = Gui.getDocument(doc.Name)
view = gd.ActiveView
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.Shape.Solids
         and not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
groups = [g for g in doc.Objects if g.isDerivedFrom("App::DocumentObjectGroup")]
step_of = {}
for code, globs in STEPS:
    for o in parts:
        if o.Name not in step_of and any(fnmatch.fnmatch(o.Label, g) for g in globs):
            step_of[o.Name] = code
missing = [o.Label for o in parts if o.Name not in step_of]
os.makedirs(OUT, exist_ok=True)
for g in groups:  # bat nhom TRUOC: bat/tat nhom FreeCAD bat/tat moi con (skill robotics-cad)
    g.ViewObject.Visibility = True
info = []


def blank(path):
    """Anh trang tron (khong co chi tiet nao trong khung)? Lay mau luoi 40x30 diem."""
    from PySide import QtGui
    img = QtGui.QImage(path)
    for i in range(40):
        for j in range(30):
            c = QtGui.QColor(img.pixel(int(img.width() * (i + 0.5) / 40), int(img.height() * (j + 0.5) / 30)))
            if min(c.red(), c.green(), c.blue()) < 235:
                return False
    return True


def settle():
    for _ in range(3):
        Gui.updateGui()
        time.sleep(0.05)


def shot(name, fit_sel):
    # Hien/an moi doi chua kip ve thi fitAll lay khung cu -> anh trang NGAU NHIEN (lan 1: 6 anh, lan 2: 6 anh khac).
    # -> cho ve xong, chup, kiem anh trang thi can khung + chup lai.
    for attempt in range(4):
        settle()
        view.viewIsometric()
        if fit_sel:
            Gui.SendMsgToActiveView("ViewSelection")
        else:
            view.fitAll()
        settle()
        view.saveImage(OUT + name, W, H, "White")
        if not blank(OUT + name):
            return attempt
    print("ANH TRANG sau 4 lan:", name)
    return attempt


try:
    for code, _ in STEPS:
        new = [o for o in parts if step_of.get(o.Name) == code]
        done = [o for o in parts if step_of.get(o.Name, "99") < code]
        Gui.Selection.clearSelection()
        imgs = []
        if new:  # c: chi chi tiet moi (dat dung cho, de hoc sinh nhan dang)
            for o in parts:
                o.ViewObject.Visibility = o in new
                o.ViewObject.Transparency = 0
            light = []  # chi tiet mau qua sang (washer trang) -> tam to cam, khong thi chim vao nen trang (buoc 13 lan dau)
            for o in new:
                col = o.ViewObject.ShapeColor
                if 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2] > 0.75:
                    light.append((o, col))
                    o.ViewObject.ShapeColor = (0.88, 0.44, 0.13)
            shot("step-%s-c.png" % code, False)
            for o, col in light:
                o.ViewObject.ShapeColor = col
            imgs.append("c")
        for o in parts:  # a/b: da lap mo + moi dac va chon (to xanh)
            vis = o in new or o in done
            o.ViewObject.Visibility = vis
            o.ViewObject.Transparency = 0 if o in new else 75
        for o in new:
            Gui.Selection.addSelection(o)
        shot("step-%s-a.png" % code, False)
        imgs.append("a")
        if new:
            shot("step-%s-b.png" % code, True)
            imgs.append("b")
        info.append({"step": code, "new": sorted(o.Label for o in new), "images": imgs})
finally:
    Gui.Selection.clearSelection()
    for o in parts:
        o.ViewObject.Visibility = True
        o.ViewObject.Transparency = 0
with open(OUT + "steps.json", "w", encoding="utf-8") as f:
    json.dump({"steps": info, "parts_without_step": missing}, f, ensure_ascii=False, indent=1)
