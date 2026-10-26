import FreeCAD as App
import Part
import math

# Dimensions from spec.yaml (mm)
PIN_X, PIN_Y = 147.0, 20.0
PIN_R, PIN_Z0, PIN_Z1 = 4.0, 10.6, 22.8
BODY_X0, BODY_X1 = 136.0, 147.5
BODY_Y0, BODY_Y1 = 24.0, 29.05
BODY_Z0, BODY_Z1 = 10.6, 22.8
WALL_X0, WALL_X1, WALL_Y0, WALL_Y1 = 144.4, 147.0, 20.0, 24.0
LOWER_Z0, LOWER_Z1, UPPER_Z0, UPPER_Z1 = 10.6, 12.4, 21.2, 22.8
ARM_Z0, ARM_Z1, ARM_WIDTH = 20.5, 22.8, 4.0
ARM_START = (147.0, 20.0)
ARM_END = (135.110, 18.381)
END_R = 3.0
KING_HOLE_R = 1.35
ROD_HOLE_R = 1.05
AXLE_X, AXLE_Z = 140.0, 16.8
AXLE_BORE_R = 2.7
AXLE_Y0, AXLE_Y1 = 23.0, 30.05

V = App.Vector

def box(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0,y0,z0))

# Fuse all structural pieces into one continuous blank.
shapes = [
    Part.makeCylinder(PIN_R, PIN_Z1-PIN_Z0, V(PIN_X,PIN_Y,PIN_Z0), V(0,0,1)),
    box(BODY_X0,BODY_X1,BODY_Y0,BODY_Y1,BODY_Z0,BODY_Z1),
    box(WALL_X0,WALL_X1,WALL_Y0,WALL_Y1,BODY_Z0,BODY_Z1),
    box(BODY_X0, WALL_X0, 20.0,24.0, LOWER_Z0,LOWER_Z1),
    box(BODY_X0, WALL_X0, 20.0,24.0, UPPER_Z0,UPPER_Z1),
]
# Steering arm: rectangular strip along centerline, with a rounded terminal boss.
dx,dy = ARM_END[0]-ARM_START[0], ARM_END[1]-ARM_START[1]
length = math.hypot(dx,dy)
px,py = -dy/length*ARM_WIDTH/2, dx/length*ARM_WIDTH/2
corners = [V(ARM_START[0]+px,ARM_START[1]+py,ARM_Z0),
           V(ARM_END[0]+px,ARM_END[1]+py,ARM_Z0),
           V(ARM_END[0]-px,ARM_END[1]-py,ARM_Z0),
           V(ARM_START[0]-px,ARM_START[1]-py,ARM_Z0)]
wire = Part.makePolygon(corners+[corners[0]])
arm = Part.Face(wire).extrude(V(0,0,ARM_Z1-ARM_Z0))
shapes += [arm, Part.makeCylinder(END_R, ARM_Z1-ARM_Z0, V(ARM_END[0],ARM_END[1],ARM_Z0), V(0,0,1))]
part = shapes[0]
for s in shapes[1:]:
    part = part.fuse(s)
part = part.removeSplitter()

# Bolt holes.
part = part.cut(Part.makeCylinder(KING_HOLE_R, 13.5, V(PIN_X,PIN_Y,10.0), V(0,0,1)))
part = part.cut(Part.makeCylinder(ROD_HOLE_R, 2.7, V(ARM_END[0],ARM_END[1],20.3), V(0,0,1)))
# Axle bore along Y. The downward pointed relief is made as a triangular prism
# whose sides meet the circular bore tangentially at 45 degrees.
part = part.cut(Part.makeCylinder(AXLE_BORE_R, AXLE_Y1-AXLE_Y0, V(AXLE_X,AXLE_Y0,AXLE_Z), V(0,1,0)))
# Tangency points on the circle, at 45 degrees either side of its lower vertical.
tx = AXLE_X + AXLE_BORE_R/math.sqrt(2)
tz = AXLE_Z - AXLE_BORE_R/math.sqrt(2)
profile = [V(AXLE_X-AXLE_BORE_R/math.sqrt(2),AXLE_Y0,tz),
           V(AXLE_X,AXLE_Y0,AXLE_Z-AXLE_BORE_R*math.sqrt(2)),
           V(tx,AXLE_Y0,tz), V(AXLE_X,AXLE_Y0,AXLE_Z)]
# Triangle outside the circular opening; union it with bore cutter.
tri = Part.Face(Part.makePolygon(profile+[profile[0]])).extrude(V(0,AXLE_Y1-AXLE_Y0,0))
part = part.cut(tri).removeSplitter()

# Save diagnostic document and export exactly one STEP solid.
doc = App.newDocument('Knuckle_L')
obj = doc.addObject('PartDesign::Feature','Knuckle')
obj.Shape = part
doc.recompute()
Part.export([obj], 'part.step')
print('Exported part.step solids=%d valid=%s volume=%.3f' % (len(part.Solids), part.isValid(), part.Volume))
