# Gate KEYCAP tron khac ten (Claude viet, executor KHONG sua). Chay: blender -b --python-exit-code 1 -P gate_keycap.py -- out
# So lay tu fit-library catpaw/mx-keycap-cross (4,19 x 1,25, sau 5,6, ong O5,71, day ong lui 4,3 vao vay, vay day 1,5).
# Huong in: UP – mat tren keycap nam sat ban (z = 0), mieng vay o tren (z = 11,3).
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_lib import *  # noqa

H = 11.3
bm = load("keycap-round.stl")
if bm:
    zmax = check_solid("keycap-round.stl", bm, 1)
    if abs(zmax - H) > 0.05:
        fails.append(f"keycap: cao {zmax:.2f}, can {H}")
    z_tube = H - 4.3 - 2.8          # giua ong chu thap
    bx = loops_at(bm, z_tube)
    sizes = sorted(round(max(b[1]-b[0], b[3]-b[2]), 2) for b in bx)
    print("loops z=%.2f:" % z_tube, sizes)
    def has(v, tol):
        return any(abs(s - v) <= tol for s in sizes)
    for v, tol, what in ((26.0, 0.08, "vay ngoai O26,0"), (23.0, 0.08, "vay trong O23,0"), (5.71, 0.06, "ong O5,71"), (4.19, 0.03, "chu thap 4,19")):
        if not has(v, tol):
            fails.append(f"keycap: thieu {what} o z={z_tube:.2f}")
    deep = sorted(round(max(b[1]-b[0], b[3]-b[2]), 2) for b in loops_at(bm, H - 4.3 - 5.4))
    if not any(abs(s - 4.19) <= 0.03 for s in deep):
        fails.append("keycap: lo chu thap phai sau 5,6 (tu day ong)")
    near_rim = sorted(round(max(b[1]-b[0], b[3]-b[2]), 2) for b in loops_at(bm, H - 2.0))
    if any(s < 20 for s in near_rim):
        fails.append("keycap: day ong phai lui 4,3 vao trong vay (gan mieng vay khong co ong)")
    top = [b for b in inner(loops_at(bm, 0.7)) if b[1] - b[0] > 8]
    if top:
        fails.append("keycap: mat tren (z 0..1,4) phai kin")
    bm.free()
done("gate_keycap")
