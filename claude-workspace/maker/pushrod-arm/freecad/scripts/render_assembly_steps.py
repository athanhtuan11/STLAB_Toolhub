# Anh huong dan lap cho HOC SINH - phong cach "action diagram" (Tuan duyet mau 2026-10-25).
# Nguyen tac (docs/assembly-instructions-style-research.md - Agrawala et al. SIGGRAPH 2003 + CyberBrick Mini T):
#   - chi tiet MOI vang STLab, da lap xam nhat dac, tat ca vien dam; chi hien CUM dang lap (boi canh), khong ca canh tay;
#   - tach chi tiet moi theo HUONG LAP + duong net dut toi cho gan; bo buoc lap lai (xi-lanh khuyu = 1 buoc);
#   - chup 2400x1800 roi tu cat khung + thu nho 1200x900 (freecad/scripts/crop_assembly_images.py).
# Chay trong FreeCAD GUI RIENG, KHONG Luu file:
#   set FC_FILE=...\pushrod_arm.FCStd  set FC_SCRIPT=...\render_assembly_steps.py  set FC_OUT=<log>
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode maker/robotics-cad/scripts/gui_run.py
# Ra: freecad/images/assembly/raw/step-XX.png (2400x1800, khong len git) + steps.json
import json
import os
import time

import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
RAW = P + "images/assembly/raw/"
W, H = 2400, 1800
DONE = (0.83, 0.87, 0.85)   # #D3DDD8 STLab "line"
NEW = (0.91, 0.70, 0.23)    # #E8B33A STLab "highlight"
EDGE = (0.09, 0.14, 0.11)   # #16231D

doc = App.ActiveDocument
view = Gui.getDocument(doc.Name).ActiveView
O = {o.Label: o for o in doc.Objects}
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.Shape.Solids
         and not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
R_sh = O["Rack_Shoulder"].Placement.Rotation
R_el = O["Rack_Elbow"].Placement.Rotation
Y = V(0, 1, 0)
UP = V(0, 0, 1)


def ctr(label):
    return O[label].Shape.BoundBox.Center


def away(label, ref, dist):
    """huong tu tam `ref` sang tam `label` (tach chi tiet ra xa cum)"""
    d = ctr(label) - ctr(ref)
    d.normalize()
    return d * dist


def pin(code):  # chot khop: than doc truc Y, mu o phia -Y -> chot vao tu -Y; washer + vit o +Y
    return [("Pin_%s" % code, Y * -50), ("Pin_%s_washer" % code, Y * 22), ("Pin_%s_M2_5x6" % code, Y * 38)]


SCREWS_TURRET = ["M2_5x6_turret", "M2_5x6_turret001", "M2_5x6_turret002", "M2_5x6_turret003"]
SCREWS_DECK = ["M2_5x8_deck", "M2_5x8_deck001", "M2_5x8_deck002", "M2_5x8_deck003"]
SCREWS_RX = ["M2_5x16_receiver", "M2_5x16_receiver001", "M2_5x16_receiver002", "M2_5x16_receiver003"]
DECK_ASM = ["Base_deck", "Slide_ring", "Turntable", "Turntable_gear_m1_z60", "M2_5x10_gear", "M2_5x10_gear001"]
GRIP_ASM = ["Gripper_frame", "CB_Servo9g_180_gripper", "Servo_horn", "Jaw_1_driven_by_servo", "Pin_jaw2", "Spacer_jaw2",
            "Jaw_2_idler", "Gripper_top_plate", "M2_5x6_top", "M2_5x6_top001", "Washer_pin", "M2_5x6_pin",
            "Jaw_1_driven_by_servo_TPU_pad", "Jaw_2_idler_TPU_pad"]
SCREWS_WRIST = ["M2_5x6_wrist", "M2_5x6_wrist001", "M2_5x6_wrist002", "M2_5x6_wrist003"]
BASE_DONE = ["Base_foot", "Base_housing", "Battery_bay", "Receiver_riser", "CB_XA003_XA004_receiver"] + SCREWS_RX + \
            ["CB_Servo9g_360_turntable", "Pinion_m1_z10_turntable"]


def steps():
    """(ma, boi canh (xam) | "ALL", [(chi tiet MOI, vector tach)], [(chi tiet cu di chuyen cung, vector)], huong nhin|None)"""
    cyl = {}
    for tag, R in (("Shoulder", R_sh), ("Elbow", R_el)):
        cyl[tag] = dict(
            wheel=("Pinion_WormWheel_" + tag, R.multVec(V(0, 30, 0))),           # vao tu mieng ranh U (+y xi-lanh)
            washer=("Washer_shaft_" + tag, away("Washer_shaft_" + tag, "Pinion_WormWheel_" + tag, 22)),
            screw=("M2_5x6_shaft_" + tag, away("M2_5x6_shaft_" + tag, "Pinion_WormWheel_" + tag, 40)),
            rack=("Rack_" + tag, R.multVec(V(45, 0, 0))),                        # luon qua ranh (ra/vao theo +x)
            motor=[("CB_030_gearbox_" + tag, R.multVec(V(0, 45, 0))), ("Worm_" + tag, R.multVec(V(0, 45, 0))),
                   ("Pin_gearbox_" + tag, R.multVec(V(30, 0, 0)))])
    s, e = cyl["Shoulder"], cyl["Elbow"]
    return [
        ("01", [], [("Base_foot", V()), ("Base_housing", UP * 30)], [], None),
        ("02", ["Base_foot", "Base_housing"], [("Battery_bay", UP * 40)], [], None),
        ("03", ["Base_foot", "Base_housing", "Battery_bay"], [("Receiver_riser", UP * 30)], [], None),
        ("04", ["Base_housing", "Battery_bay", "Receiver_riser"],
         [("CB_XA003_XA004_receiver", UP * 30)] + [(n, UP * 55) for n in SCREWS_RX], [], None),
        # 05/06: bo mach bo thu khoi boi canh - lan dau mach che servo va banh rang nho
        ("05", ["Base_foot", "Base_housing", "Battery_bay"], [("CB_Servo9g_360_turntable", UP * 45)], [], None),
        ("06", ["Base_housing", "CB_Servo9g_360_turntable"], [("Pinion_m1_z10_turntable", UP * 25)], [], None),
        ("07", [], [("Base_deck", V()), ("Slide_ring", UP * 15)], [], None),
        ("08", ["Base_deck", "Slide_ring"], [("Turntable", UP * 25)], [], None),
        ("09", ["Base_deck", "Slide_ring", "Turntable"],
         [("Turntable_gear_m1_z60", UP * -22), ("M2_5x10_gear", UP * -45), ("M2_5x10_gear001", UP * -45)], [],
         V(-1, 1, 0.8)),                                                            # nhin tu duoi: vit bat tu duoi
        ("10", BASE_DONE, [(n, UP * 70) for n in SCREWS_DECK], [(n, UP * 40) for n in DECK_ASM], None),
        ("11", ["Base_housing", "Base_deck", "Turntable"],
         [("Turret_one_piece", UP * 35)] + [(n, UP * 70) for n in SCREWS_TURRET], [], None),
        ("12", [], [("Housing_Shoulder", V()), s["wheel"]], [], None),
        ("13", ["Housing_Shoulder", "Pinion_WormWheel_Shoulder"], [s["washer"], s["screw"]], [], None),
        ("14", ["Housing_Shoulder", "Pinion_WormWheel_Shoulder", "Washer_shaft_Shoulder", "M2_5x6_shaft_Shoulder"],
         [s["rack"]], [], None),
        ("15", [], [("Housing_Elbow", V()), e["wheel"], e["washer"], e["screw"], e["rack"]], [], None),
        ("16", ["Turret_one_piece", "Turntable", "Base_deck"],
         [("Boom001", V()), ("Spacer_S", V()), ("Spacer_S001", V())] + pin("S"), [], None),
        ("17", ["Turret_one_piece", "Turntable", "Boom001", "Housing_Shoulder", "Rack_Shoulder"],
         [("Spacer_A", V()), ("Spacer_A001", V())] + pin("A"), [], None),
        ("18", ["Boom001", "Rack_Shoulder", "Housing_Shoulder"], pin("B"), [], None),
        ("19", [], [("Forearm_plate_L", away("Forearm_plate_L", "Wrist_spacer", 20)),
                    ("Forearm_plate_R", away("Forearm_plate_R", "Wrist_spacer", 20)), ("Wrist_spacer", V()),
                    ("M2_5x6_wrist_spacer", away("M2_5x6_wrist_spacer", "Wrist_spacer", 45)),
                    ("M2_5x6_wrist_spacer001", away("M2_5x6_wrist_spacer001", "Wrist_spacer", 45))], [], None),
        ("20", ["Forearm_plate_L", "Forearm_plate_R", "Wrist_spacer"],
         [("Spacer_D", UP * 25), ("Spacer_E", UP * 25)], [], None),
        ("21", ["Boom001", "Forearm_plate_L", "Forearm_plate_R", "Spacer_E"], pin("E"), [], None),
        ("22", ["Boom001", "Housing_Elbow", "Rack_Elbow"], pin("C"), [], None),
        ("23", ["Forearm_plate_L", "Forearm_plate_R", "Rack_Elbow", "Spacer_D"], pin("D"), [], None),
        ("24", "ALL", [("Pin_A", V()), ("Pin_B", V()), ("Pin_C", V()), ("Pin_D", V())], [], None),   # do tu the goc
        ("25", ["Housing_Shoulder", "Pinion_WormWheel_Shoulder", "Rack_Shoulder", "Boom001"], s["motor"], [], None),
        ("26", ["Housing_Elbow", "Pinion_WormWheel_Elbow", "Rack_Elbow", "Boom001"], e["motor"], [], None),
        ("27", [], [("Gripper_frame", V()),
                    ("CB_Servo9g_180_gripper", away("CB_Servo9g_180_gripper", "Gripper_frame", 35))], [], None),
        ("28", ["Gripper_frame", "CB_Servo9g_180_gripper"],
         [("Servo_horn", away("Servo_horn", "CB_Servo9g_180_gripper", 18)),
          ("Jaw_1_driven_by_servo", away("Jaw_1_driven_by_servo", "CB_Servo9g_180_gripper", 32))], [], None),
        ("29", ["Gripper_frame", "CB_Servo9g_180_gripper", "Servo_horn", "Jaw_1_driven_by_servo"],
         [("Pin_jaw2", away("Pin_jaw2", "Gripper_frame", 30)), ("Spacer_jaw2", away("Spacer_jaw2", "Gripper_frame", 18)),
          ("Jaw_2_idler", away("Jaw_2_idler", "Gripper_frame", 22))], [], None),
        ("30", ["Gripper_frame", "CB_Servo9g_180_gripper", "Servo_horn", "Jaw_1_driven_by_servo", "Pin_jaw2",
                "Spacer_jaw2", "Jaw_2_idler"],
         [("Gripper_top_plate", away("Gripper_top_plate", "Gripper_frame", 25)),
          ("M2_5x6_top", away("M2_5x6_top", "Gripper_frame", 45)),
          ("M2_5x6_top001", away("M2_5x6_top001", "Gripper_frame", 45)),
          ("Washer_pin", away("Washer_pin", "Gripper_frame", 35)), ("M2_5x6_pin", away("M2_5x6_pin", "Gripper_frame", 50))],
         [], None),
        ("31", ["Jaw_1_driven_by_servo", "Jaw_2_idler", "Gripper_frame"],
         [("Jaw_1_driven_by_servo_TPU_pad", away("Jaw_1_driven_by_servo_TPU_pad", "Jaw_2_idler_TPU_pad", 15)),
          ("Jaw_2_idler_TPU_pad", away("Jaw_2_idler_TPU_pad", "Jaw_1_driven_by_servo_TPU_pad", 15))], [], None),
        ("32", ["Forearm_plate_L", "Forearm_plate_R", "Wrist_spacer"],
         [(n, away(n, "Gripper_frame", 30)) for n in SCREWS_WRIST],
         [(n, away("Gripper_frame", "Wrist_spacer", 40)) for n in GRIP_ASM], None),
    ]


def settle():
    for _ in range(3):
        Gui.updateGui()
        time.sleep(0.05)


def blank(path):
    from PySide import QtGui
    img = QtGui.QImage(path)
    for i in range(40):
        for j in range(30):
            c = QtGui.QColor(img.pixel(int(img.width() * (i + 0.5) / 40), int(img.height() * (j + 0.5) / 30)))
            if min(c.red(), c.green(), c.blue()) < 235:
                return False
    return True


os.makedirs(RAW, exist_ok=True)
for g in doc.Objects:  # bat nhom TRUOC (bat/tat nhom FreeCAD bat/tat moi con)
    if g.isDerivedFrom("App::DocumentObjectGroup"):
        g.ViewObject.Visibility = True
saved = {o.Name: (o.ViewObject.Visibility, tuple(o.ViewObject.ShapeColor), o.ViewObject.DisplayMode, o.ViewObject.LineWidth,
                  tuple(o.ViewObject.LineColor), o.ViewObject.Transparency, App.Placement(o.Placement)) for o in parts}
info, tmp, covered = [], [], set()
try:
    for code, ctx, new, move, vdir in steps():
        newl = [n for n, _ in new]
        covered.update(newl)
        show = {o.Label for o in parts} if ctx == "ALL" else set(ctx) | set(newl) | {n for n, _ in move}
        for o in parts:
            vo = o.ViewObject
            vo.Visibility = o.Label in show
            vo.Transparency = 0
            vo.DisplayMode = "Flat Lines"
            vo.LineColor = EDGE
            vo.LineWidth = 4
            vo.ShapeColor = NEW if o.Label in newl else DONE
        for n, d in new + move:
            if d.Length > 1e-6:
                o = O[n]
                c0 = o.Shape.BoundBox.Center
                o.Placement = App.Placement(d, App.Rotation()).multiply(o.Placement)
                if n in newl:  # duong dan chi cho chi tiet moi
                    ln = doc.addObject("Part::Feature", "guide_tmp")
                    ln.Shape = Part.LineSegment(c0, c0 + d).toShape()
                    ln.ViewObject.LineColor = EDGE
                    ln.ViewObject.LineWidth = 6
                    ln.ViewObject.DrawStyle = "Dashed"
                    tmp.append(ln)
        for attempt in range(4):
            settle()
            if vdir is None:
                view.viewIsometric()
            else:
                view.setViewDirection((vdir.x, vdir.y, vdir.z))
            view.fitAll()
            settle()
            f = RAW + "step-%s.png" % code
            view.saveImage(f, W, H, "White")
            if not blank(f):
                break
        info.append({"step": code, "new": newl, "moved": [n for n, _ in move], "context": "ALL" if ctx == "ALL" else ctx})
        for n, _ in new + move:
            O[n].Placement = saved[O[n].Name][6]
        for ln in tmp:
            doc.removeObject(ln.Name)
        tmp = []
    # anh bia: ca canh tay, MAU THAT + vien (trang bia PDF)
    for o in parts:
        vo = o.ViewObject
        vo.Visibility, vo.Transparency, vo.DisplayMode, vo.LineColor, vo.LineWidth = True, 0, "Flat Lines", EDGE, 3
        vo.ShapeColor = saved[o.Name][1]
    settle()
    view.viewIsometric()
    view.fitAll()
    settle()
    view.saveImage(RAW + "cover.png", W, H, "White")
finally:
    for ln in tmp:
        doc.removeObject(ln.Name)
    for o in parts:
        v, col, dm, lw, lc, tr, pl = saved[o.Name]
        vo = o.ViewObject
        vo.Visibility, vo.ShapeColor, vo.DisplayMode, vo.LineWidth, vo.LineColor, vo.Transparency = v, col, dm, lw, lc, tr
        o.Placement = pl
missing = sorted(o.Label for o in parts if o.Label not in covered)
with open(RAW + "steps.json", "w", encoding="utf-8") as f:
    json.dump({"steps": info, "parts_without_step": missing}, f, ensure_ascii=False, indent=1)
