import os
import FreeCAD as App
import Part

# Dimensions and coordinates (mm)
X_TAIL = 27.38
X_SHOULDER_END = 94.78
X_EYE = 99.78
ROD_Y = 6.0
ROD_Z = 8.0
ROD_CORNER = 1.5
EYE_RADIUS = 6.0
PIN_HOLE_RADIUS = 2.7
THREAD_RADIUS = 1.8
THREAD_DEPTH = 34.5
NUT_X0 = 30.03
NUT_X1 = 32.73
NUT_AF = 5.7
NUT_FLAT_Y = NUT_AF / 2.0
NUT_VERTEX_Z = NUT_AF / (3.0 ** 0.5)
SLOT_Y_TOP = 4.0

V = App.Vector
rod = Part.makeBox(X_SHOULDER_END-X_TAIL, ROD_Y, ROD_Z, V(X_TAIL, -ROD_Y/2, -ROD_Z/2))
long_edges = [e for e in rod.Edges if e.Length > X_SHOULDER_END-X_TAIL-0.01]
rod = rod.makeFillet(ROD_CORNER, long_edges)
eye = Part.makeCylinder(EYE_RADIUS, ROD_Y, V(X_EYE, -ROD_Y/2, 0), V(0,1,0))
part = rod.fuse(eye)
pin = Part.makeCylinder(PIN_HOLE_RADIUS, ROD_Y+2, V(X_EYE, -ROD_Y/2-1, 0), V(0,1,0))
part = part.cut(pin)
axial = Part.makeCylinder(THREAD_RADIUS, THREAD_DEPTH, V(X_TAIL, 0, 0), V(1,0,0))
part = part.cut(axial)
yz = [(0,NUT_VERTEX_Z), (NUT_FLAT_Y,NUT_VERTEX_Z/2), (NUT_FLAT_Y,-NUT_VERTEX_Z/2), (0,-NUT_VERTEX_Z), (-NUT_FLAT_Y,-NUT_VERTEX_Z/2), (-NUT_FLAT_Y,NUT_VERTEX_Z/2)]
verts = [V(NUT_X0, y, z) for y,z in yz]
wire = Part.makePolygon(verts + [verts[0]])
face = Part.Face(Part.Wire(wire.Edges))
nut_seat = face.extrude(V(NUT_X1-NUT_X0, 0, 0))
part = part.cut(nut_seat)
slot = Part.makeBox(NUT_X1-NUT_X0, SLOT_Y_TOP, 2*NUT_VERTEX_Z, V(NUT_X0, 0, -NUT_VERTEX_Z))
part = part.cut(slot).removeSplitter()
doc = App.newDocument("Piston_rod_Shoulder")
obj = doc.addObject("PartDesign::Feature", "PistonRod")
obj.Label = "Piston_rod_Shoulder"
obj.Shape = part
doc.recompute()
out_dir = os.path.dirname(os.path.abspath(__file__))
Part.export([obj], os.path.join(out_dir, "part.step"))
