# Bo chot thu (pin gauge) - in ~5 phut, cam vao lo Turret/Boom DA IN de chon duong kinh chot truoc khi in ca bo
# (Tuan 2026-10-25: chot O5,0 / lo O5,4 in ra khong nhet vao duoc). Cung kieu chot that: mu O9 x 1,6, vat dau 0,4,
# mat phang day cach truc 2,0 (in nam), than dai 10. So vach khac tren mu = thu tu kich thuoc (1 vach = nho nhat).
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" tools/robotics-cad/scripts/fc_cli.py --pass maker/pushrod-arm/freecad/scripts/make_pin_gauge.py
import Mesh
import MeshPart
import Part
from FreeCAD import Vector as V

OUT = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/print/gauges/"
SIZES = [4.6, 4.7, 4.8, 4.9]
for k, d in enumerate(SIZES):
    r = d / 2
    head = Part.makeCylinder(4.5, 1.6, V(0, 0, 0), V(0, 1, 0))
    shaft = Part.makeCylinder(r, 10 - 0.4, V(0, 1.59, 0), V(0, 1, 0))
    tip = Part.makeCone(r, r - 0.4, 0.4, V(0, 1.59 + 9.6, 0), V(0, 1, 0))
    pin = head.fuse([shaft, tip]).removeSplitter()
    pin = pin.cut(Part.makeBox(40, 40, 20, V(-20, -20, -22)))          # mat phang day z = -2
    for j in range(k + 1):                                               # vach danh dau tren mat mu
        pin = pin.cut(Part.makeBox(0.6, 0.5, 2.5, V(-3.0 + j * 1.2, -0.01, 1.2)))
    pin.translate(V(0, 0, 2))
    m = MeshPart.meshFromShape(Shape=pin, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    m.write(OUT + "gauge_pin_%02d__D%.1f.stl" % (k + 1, d))
print("OK", SIZES)
