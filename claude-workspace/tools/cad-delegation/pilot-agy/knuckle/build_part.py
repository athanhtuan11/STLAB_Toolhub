"""
Build script for Knuckle_L (cyberbrick-car front left steering knuckle).
Uses FreeCAD Part module.
"""
import math
import os
import FreeCAD as App
import Part

# ==========================================
# DESIGN PARAMETERS (from spec.yaml)
# ==========================================

# 1. Than chot lai (Kingpin body)
KINGPIN_X = 147.0
KINGPIN_Y = 20.0
KINGPIN_R = 4.0
KINGPIN_Z_MIN = 10.6
KINGPIN_Z_MAX = 22.8

# 2. Khoi giu truc (Axle housing)
HOUSING_X_MIN = 136.0
HOUSING_X_MAX = 147.5
HOUSING_Y_MIN = 24.0
HOUSING_Y_MAX = 29.05
HOUSING_Z_MIN = 10.6
HOUSING_Z_MAX = 22.8

# 3. Vach noi (Connecting wall)
WALL_X_MIN = 144.4
WALL_X_MAX = 147.0
WALL_Y_MIN = 20.0
WALL_Y_MAX = 24.0
WALL_Z_MIN = 10.6
WALL_Z_MAX = 22.8

# 4. Dai duoi (Bottom flange)
FLANGE_BOT_X_MIN = 136.0
FLANGE_BOT_X_MAX = 144.4
FLANGE_BOT_Y_MIN = 20.0
FLANGE_BOT_Y_MAX = 24.0
FLANGE_BOT_Z_MIN = 10.6
FLANGE_BOT_Z_MAX = 12.4

# 5. Dai tren (Top flange)
FLANGE_TOP_X_MIN = 136.0
FLANGE_TOP_X_MAX = 144.4
FLANGE_TOP_Y_MIN = 20.0
FLANGE_TOP_Y_MAX = 24.0
FLANGE_TOP_Z_MIN = 21.2
FLANGE_TOP_Z_MAX = 22.8

# 6. Tay lai (Steering arm)
ARM_Z_MIN = 20.5
ARM_Z_MAX = 22.8
ARM_WIDTH = 4.0
ARM_START_X = 147.0
ARM_START_Y = 20.0
ARM_END_X = 135.110
ARM_END_Y = 18.381
ARM_TIP_R = 3.0

# Holes (Cac lo)
# a. Lo chot lai
HOLE_KINGPIN_D = 2.7
HOLE_KINGPIN_X = 147.0
HOLE_KINGPIN_Y = 20.0

# b. Lo moi vit thanh giang
HOLE_TIEROD_D = 2.1
HOLE_TIEROD_X = 135.110
HOLE_TIEROD_Y = 18.381
HOLE_TIEROD_Z_MIN = 15.0

# c. Lo truc banh (Teardrop axle hole)
AXLE_HOLE_X = 140.0
AXLE_HOLE_Z = 16.8
AXLE_HOLE_R = 2.7
AXLE_HOLE_Y_MIN = 23.0
AXLE_HOLE_Y_MAX = 30.05
AXLE_HOLE_TIP_Z = AXLE_HOLE_Z - AXLE_HOLE_R * math.sqrt(2)


def build_knuckle():
    # 1. Than chot lai
    kingpin = Part.makeCylinder(
        KINGPIN_R,
        KINGPIN_Z_MAX - KINGPIN_Z_MIN,
        App.Vector(KINGPIN_X, KINGPIN_Y, KINGPIN_Z_MIN),
        App.Vector(0, 0, 1),
    )

    # 2. Khoi giu truc
    housing = Part.makeBox(
        HOUSING_X_MAX - HOUSING_X_MIN,
        HOUSING_Y_MAX - HOUSING_Y_MIN,
        HOUSING_Z_MAX - HOUSING_Z_MIN,
        App.Vector(HOUSING_X_MIN, HOUSING_Y_MIN, HOUSING_Z_MIN),
    )

    # 3. Vach noi
    wall = Part.makeBox(
        WALL_X_MAX - WALL_X_MIN,
        WALL_Y_MAX - WALL_Y_MIN,
        WALL_Z_MAX - WALL_Z_MIN,
        App.Vector(WALL_X_MIN, WALL_Y_MIN, WALL_Z_MIN),
    )

    # 4. Dai duoi
    flange_bot = Part.makeBox(
        FLANGE_BOT_X_MAX - FLANGE_BOT_X_MIN,
        FLANGE_BOT_Y_MAX - FLANGE_BOT_Y_MIN,
        FLANGE_BOT_Z_MAX - FLANGE_BOT_Z_MIN,
        App.Vector(FLANGE_BOT_X_MIN, FLANGE_BOT_Y_MIN, FLANGE_BOT_Z_MIN),
    )

    # 5. Dai tren
    flange_top = Part.makeBox(
        FLANGE_TOP_X_MAX - FLANGE_TOP_X_MIN,
        FLANGE_TOP_Y_MAX - FLANGE_TOP_Y_MIN,
        FLANGE_TOP_Z_MAX - FLANGE_TOP_Z_MIN,
        App.Vector(FLANGE_TOP_X_MIN, FLANGE_TOP_Y_MIN, FLANGE_TOP_Z_MIN),
    )

    # 6. Tay lai
    # Vector centerline
    dx = ARM_END_X - ARM_START_X
    dy = ARM_END_Y - ARM_START_Y
    arm_len = math.hypot(dx, dy)
    ux = dx / arm_len
    uy = dy / arm_len
    nx = -uy
    ny = ux
    hw = ARM_WIDTH / 2.0

    p1 = App.Vector(ARM_START_X + hw * nx, ARM_START_Y + hw * ny, ARM_Z_MIN)
    p2 = App.Vector(ARM_END_X + hw * nx, ARM_END_Y + hw * ny, ARM_Z_MIN)
    p3 = App.Vector(ARM_END_X - hw * nx, ARM_END_Y - hw * ny, ARM_Z_MIN)
    p4 = App.Vector(ARM_START_X - hw * nx, ARM_START_Y - hw * ny, ARM_Z_MIN)

    e1 = Part.makeLine(p1, p2)
    e2 = Part.makeLine(p2, p3)
    e3 = Part.makeLine(p3, p4)
    e4 = Part.makeLine(p4, p1)
    arm_wire = Part.Wire([e1, e2, e3, e4])
    arm_face = Part.Face(arm_wire)
    arm_bar = arm_face.extrude(App.Vector(0, 0, ARM_Z_MAX - ARM_Z_MIN))

    arm_tip = Part.makeCylinder(
        ARM_TIP_R,
        ARM_Z_MAX - ARM_Z_MIN,
        App.Vector(ARM_END_X, ARM_END_Y, ARM_Z_MIN),
        App.Vector(0, 0, 1),
    )

    # Hop tat ca cac khoi dac
    solids = [kingpin, housing, wall, flange_bot, flange_top, arm_bar, arm_tip]
    fused = solids[0]
    for s in solids[1:]:
        fused = fused.fuse(s)

    # ------------------------------------------
    # Khoet cac lo
    # ------------------------------------------
    # a. Lo chot lai: tron duong kinh 2.7, truc Z qua (147, 20), xuyen het
    hole_kingpin = Part.makeCylinder(
        HOLE_KINGPIN_D / 2.0,
        15.0,
        App.Vector(HOLE_KINGPIN_X, HOLE_KINGPIN_Y, 9.0),
        App.Vector(0, 0, 1),
    )

    # b. Lo moi vit thanh giang: tron duong kinh 2.1, truc Z qua (135.110, 18.381), tu z 15 len
    hole_tierod = Part.makeCylinder(
        HOLE_TIEROD_D / 2.0,
        10.0,
        App.Vector(HOLE_TIEROD_X, HOLE_TIEROD_Y, HOLE_TIEROD_Z_MIN),
        App.Vector(0, 0, 1),
    )

    # c. Lo truc banh tiet dien giot nuoc
    y_cut_start = AXLE_HOLE_Y_MIN - 1.0
    y_cut_len = (AXLE_HOLE_Y_MAX + 1.0) - y_cut_start

    t1_x = AXLE_HOLE_X - AXLE_HOLE_R / math.sqrt(2)
    t1_z = AXLE_HOLE_Z - AXLE_HOLE_R / math.sqrt(2)
    t2_x = AXLE_HOLE_X + AXLE_HOLE_R / math.sqrt(2)
    t2_z = AXLE_HOLE_Z - AXLE_HOLE_R / math.sqrt(2)
    top_x = AXLE_HOLE_X
    top_z = AXLE_HOLE_Z + AXLE_HOLE_R

    p_t1 = App.Vector(t1_x, y_cut_start, t1_z)
    p_top = App.Vector(top_x, y_cut_start, top_z)
    p_t2 = App.Vector(t2_x, y_cut_start, t2_z)
    p_tip = App.Vector(AXLE_HOLE_X, y_cut_start, AXLE_HOLE_TIP_Z)

    arc = Part.Arc(p_t2, p_top, p_t1).toShape()
    l1 = Part.makeLine(p_t1, p_tip)
    l2 = Part.makeLine(p_tip, p_t2)
    td_wire = Part.Wire([arc, l1, l2])
    td_face = Part.Face(td_wire)
    hole_axle = td_face.extrude(App.Vector(0, y_cut_len, 0))

    # Cut all holes
    part = fused.cut(hole_kingpin)
    part = part.cut(hole_tierod)
    part = part.cut(hole_axle)

    part = part.removeSplitter()
    return part


knuckle = build_knuckle()
here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
out_path = os.path.join(here, "part.step")
knuckle.exportStep(out_path)
print("Exported 1 solid to:", out_path, flush=True)
print("BoundBox:", knuckle.BoundBox, flush=True)
print("Solids count:", len(knuckle.Solids), flush=True)

