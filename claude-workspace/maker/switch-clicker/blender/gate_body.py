# Gate THAN clicker v2 (Claude viet, executor KHONG sua). Chay: blender -b --python-exit-code 1 -P gate_body.py -- out
# So o switch lay tu fit-library catpaw/mx-socket (mau voxo3d Cat Paw Clicker, A1 + PETG Basic, da chay that).
# Huong in = huong dung: day z = 0, mieng hoc keycap o tren (z = 15,3).
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_lib import *  # noqa

MOUTH, FLOOR, H = 11.19, 2.61, 15.31
bm = load("body-v2.stl")
if bm:
    zmax = check_solid("body-v2.stl", bm, 1)
    if abs(zmax - H) > 0.05:
        fails.append(f"body: cao {zmax:.2f}, can {H}")
    def sq(z, lo, hi):
        return [b for b in inner(loops_at(bm, z)) if lo < b[1] - b[0] < hi and lo < b[3] - b[2] < hi]
    for z, want in ((MOUTH - 0.5, 14.00), (MOUTH - 1.5, 14.00), (MOUTH - 2.69, 15.44), (FLOOR + 1.0, 14.00), (FLOOR + 4.0, 14.00)):
        s = sq(z, 13, 16.5)
        print(f"o switch z={z:.2f}:", [(round(b[1]-b[0],3), round(b[3]-b[2],3)) for b in s])
        if len(s) != 1 or abs((s[0][1]-s[0][0]) - want) > 0.05 or abs((s[0][3]-s[0][2]) - want) > 0.05:
            fails.append(f"body: o switch o z={z:.2f} phai vuong {want} (+-0,05)")
    if sq(FLOOR - 0.8, 10, 30):
        fails.append("body: day duoi o switch phai kin (z < 2,61)")
    pk = [b for b in inner(loops_at(bm, MOUTH + 2.0)) if 25 < b[1] - b[0] < 29]
    print("hoc keycap:", [(round(b[1]-b[0],3), round(b[3]-b[2],3)) for b in pk])
    if len(pk) != 1 or abs((pk[0][1]-pk[0][0]) - 27.0) > 0.08 or abs((pk[0][3]-pk[0][2]) - 27.0) > 0.08:
        fails.append("body: hoc keycap tron O27,0 o tren mieng")
    if [b for b in inner(loops_at(bm, MOUTH - 0.3)) if b[1] - b[0] > 16.5]:
        fails.append("body: day hoc keycap phai o z = 11,19 (mieng o switch)")
    ring = [b for b in inner(loops_at(bm, 2.0)) if 5.0 < b[1] - b[0] < 5.8]
    if len(ring) != 1 or abs((ring[0][1]-ring[0][0]) - 5.4) > 0.08:
        fails.append("body: vong treo phai co lo ~5,4 o z = 2")
    bm.free()
done("gate_body")
