"""Knuckle_L - steering knuckle, left front wheel (cyberbrick-car). Units: mm.

Vehicle frame: X forward, Y left, Z up. Origin = rear axle center on ground.
Build from spec.yaml (design blocks 1..6, holes a..c), export part.step (1 solid).
"""
import math
import os

import FreeCAD as App
import Part

# ---------------------------------------------------------------- parameters
KING_X = 147.0
KING_Y = 20.0
KING_R = 4.0

Z_BOT = 10.6
Z_TOP = 22.8

HOLDER_X0, HOLDER_X1 = 136.0, 147.5
HOLDER_Y0, HOLDER_Y1 = 24.0, 29.05

WALL_X0, WALL_X1 = 144.4, 147.0
WALL_Y0, WALL_Y1 = 20.0, 24.0

STRIP_X0, STRIP_X1 = 136.0, 144.4
STRIP_Y0, STRIP_Y1 = 20.0, 24.0
STRIP_BOT_Z0, STRIP_BOT_Z1 = 10.6, 12.4
STRIP_TOP_Z0, STRIP_TOP_Z1 = 21.2, 22.8

ARM_X0 = KING_X
ARM_Y0 = KING_Y
ARM_END_X = 135.110
ARM_END_Y = 18.381
ARM_HALF_W = 2.0
ARM_Z0, ARM_Z1 = 20.5, 22.8
ARM_END_R = 3.0

KING_HOLE_R = 1.35      # M2.5 kingpin, D2.7
KING_HOLE_Z0, KING_HOLE_Z1 = 10.0, 23.5

TIE_HOLE_R = 1.05       # tie-rod screw, D2.1
TIE_HOLE_Z0, TIE_HOLE_Z1 = 15.0, 23.5

AXLE_CX, AXLE_CZ = 140.0, 16.8
AXLE_R = 2.7            # D5.0 shaft + 0.2 clearance
AXLE_Y0, AXLE_Y1 = 23.0, 30.05

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "part.step")

V = App.Vector


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, z0, z1, cx, cy):
    return Part.makeCylinder(r, z1 - z0, V(cx, cy, z0), V(0, 0, 1))


# block 1: kingpin body
king = Part.makeCylinder(KING_R, Z_TOP - Z_BOT, V(KING_X, KING_Y, Z_BOT), V(0, 0, 1))

# block 2: axle holder
holder = box(HOLDER_X0, HOLDER_X1, HOLDER_Y0, HOLDER_Y1, Z_BOT, Z_TOP)

# block 3: connecting wall
wall = box(WALL_X0, WALL_X1, WALL_Y0, WALL_Y1, Z_BOT, Z_TOP)

# blocks 4/5: bottom and top strips (gap between = den + screw head)
strip_bot = box(STRIP_X0, STRIP_X1, STRIP_Y0, STRIP_Y1, STRIP_BOT_Z0, STRIP_BOT_Z1)
strip_top = box(STRIP_X0, STRIP_X1, STRIP_Y0, STRIP_Y1, STRIP_TOP_Z0, STRIP_TOP_Z1)

# block 6: steering arm (flat bar + round end boss)
dx = ARM_END_X - ARM_X0
dy = ARM_END_Y - ARM_Y0
length = math.hypot(dx, dy)
ux, uy = dx / length, dy / length
nx, ny = -uy, ux  # unit normal
hw = ARM_HALF_W
poly = [
    V(ARM_X0 + hw * nx, ARM_Y0 + hw * ny, ARM_Z0),
    V(ARM_END_X + hw * nx, ARM_END_Y + hw * ny, ARM_Z0),
    V(ARM_END_X - hw * nx, ARM_END_Y - hw * ny, ARM_Z0),
    V(ARM_X0 - hw * nx, ARM_Y0 - hw * ny, ARM_Z0),
]
arm_face = Part.Face(Part.Wire([Part.LineSegment(poly[i], poly[(i + 1) % 4]).toShape() for i in range(4)]))
arm = arm_face.extrude(V(0, 0, ARM_Z1 - ARM_Z0))
arm_end = Part.makeCylinder(ARM_END_R, ARM_Z1 - ARM_Z0, V(ARM_END_X, ARM_END_Y, ARM_Z0), V(0, 0, 1))

# ---------------------------------------------------------------- fuse body
body = king
for s in (holder, wall, strip_bot, strip_top, arm, arm_end):
    body = body.fuse(s)
body = body.removeSplitter()

# ---------------------------------------------------------------- holes
hole_king = cyl(KING_HOLE_R, KING_HOLE_Z0, KING_HOLE_Z1, KING_X, KING_Y)
hole_tie = cyl(TIE_HOLE_R, TIE_HOLE_Z0, TIE_HOLE_Z1, ARM_END_X, ARM_END_Y)

# teardrop axle hole: circle r=AXLE_R + 45 deg tip pointing -Z, extruded along +Y
tz_off = AXLE_R
tip_z = AXLE_CZ - AXLE_R * math.sqrt(2.0)
tang = AXLE_R * math.sqrt(0.5)  # 45 deg tangent points
t1 = V(AXLE_CX - tang, AXLE_Y0, AXLE_CZ - tang)
t2 = V(AXLE_CX + tang, AXLE_Y0, AXLE_CZ - tang)
top = V(AXLE_CX, AXLE_Y0, AXLE_CZ + AXLE_R)
apex = V(AXLE_CX, AXLE_Y0, tip_z)
arc = Part.Arc(t1, top, t2).toShape()
e_t2a = Part.LineSegment(t2, apex).toShape()
e_at1 = Part.LineSegment(apex, t1).toShape()
td_face = Part.Face(Part.Wire([arc, e_t2a, e_at1]))
hole_axle = td_face.extrude(V(0, AXLE_Y1 - AXLE_Y0, 0))

part = body.cut(hole_king).cut(hole_tie).cut(hole_axle)
part = part.removeSplitter()

solids = part.Solids
if len(solids) != 1 or not part.isValid() or part.Volume <= 0:
    raise RuntimeError("expected 1 valid solid, got %d solids, valid=%s, vol=%.1f"
                       % (len(solids), part.isValid(), part.Volume))

part.exportStep(OUT)
bb = part.BoundBox
print("SOLIDS %d  VOL %.1f" % (len(solids), part.Volume))
print("BBOX [%.2f %.2f %.2f] [%.2f %.2f %.2f]" % (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax))
print("WROTE", OUT, flush=True)
