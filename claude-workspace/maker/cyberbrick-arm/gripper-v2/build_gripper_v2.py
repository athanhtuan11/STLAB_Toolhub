"""Tay gap 3 ngon v2 cho CyberBrick robotic arm (tipflow) – sua loi 'lap sat servo quay khong noi, lap long roi ra' (Tuan 2026-11-12).

Nguyen nhan (do tu luoi goc, xem README.md):
  - lo khia noi servo o dau vit me 02 chi sau 2,28 mm ~ truc servo CyberBrick (~2,3) -> truc cham day, day vit me doc truc,
    vanh O9,7 ep vao mieng con dau 09 -> ma sat, servo ket. Hang ne bang khe tay 0,5-1 mm -> dau kep long, tuot.
  - chot ngon 20/22/24 chi giu bang go ma sat O5,07 trong lo O4,4.
Sua (chi chi tiet nay; dau 09, khung 06, ngon giu nguyen; ban in dung rieng, KHONG dang lai):
  1. worm-v2: khoet sau lo noi servo them 1,0 mm (O5,2, truc servo khong cham day) + lui mat vat vanh phia dau kep 0,3 mm
     (them khe doc truc) -> cam dau 09 HET vao khung 06, khong can canh khe.
  2. pin-v2 x3: than O5,07 nhu goc, dau O4,2 tron (bo go ma sat) co lo moi O2,2 cho vit M2.5x6 BHCS (co trong kit) + long den in.
  3. washer x3: O7 x O2,8 x 1,0 (dau vit O4,7 qua nho so voi lo O4,4).
Nguon luoi goc: tools/model-study/_out/arm/parts (tach tu community/makerworld-tipflow-cyberbrick-robotic-arm bang study_3mf.py).
Chay: uv run --no-project --with trimesh --with manifold3d --with numpy --with scipy --with networkx python build_gripper_v2.py
"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
WS = HERE.parents[2]
SRC = WS / "tools" / "model-study" / "_out" / "arm" / "parts"
OUT = HERE / "out"
P = json.loads((HERE / "params.json").read_text(encoding="utf-8"))
OUT.mkdir(exist_ok=True)


def revolve(rz):
    """Khoi tron xoay quanh Z tu da giac (r, z) kin."""
    rz = [tuple(p) for p in rz]
    if rz[0][0] > 0 and rz[0] != rz[-1]:
        rz.append(rz[0])                     # vong kin khong cham truc -> dong lai
    m = trimesh.creation.revolve(np.array(rz, float), sections=128)
    m.merge_vertices(); m.fix_normals()
    if m.volume < 0:
        m.invert()
    assert m.is_volume, "revolve khong kin"
    return m


def cyl(d, z0, z1):
    c = trimesh.creation.cylinder(radius=d / 2, height=z1 - z0, sections=96)
    c.apply_translation([0, 0, (z0 + z1) / 2])
    return c


# ---------- 1. vit me ----------
W = P["worm"]
worm = trimesh.load(SRC / "02-document-solid-25.stl", force="mesh")
assert worm.is_watertight
v0 = worm.volume
# 1a. khoet sau lo noi servo: tru tron tu day lo khia cu xuong them socket_extra
z_top_spline = W["spline_bottom_z"]           # day lo khia cu (z goc)
worm = worm.difference(cyl(W["socket_extra_d"], z_top_spline - W["socket_extra_depth"], z_top_spline + 0.1), engine="manifold")
# 1b. lui mat vat duoi cua vanh (phia dau kep) them collar_relief theo z, giu goc 45 do
r0, zc, rp, s = W["collar_r_root"], W["collar_chamfer_z0"], W["collar_r_peak"], W["collar_relief"]
z_peak = zc + (rp - r0) + s                    # mat vat moi cham ban kinh dinh
relief = revolve([(r0 + 0.01, zc - 0.3), (rp + 0.8, zc - 0.3), (rp + 0.8, z_peak), (rp, z_peak), (r0 + 0.01, zc + s)])
worm = worm.difference(relief, engine="manifold")
assert worm.is_watertight
worm.export(OUT / "worm-v2.stl")

# ---------- 2. chot ngon ----------
C = P["pin"]
L = C["length"]
pin = revolve([(0, 0), (C["head_d"] / 2 - C["chamfer"], 0), (C["head_d"] / 2, C["chamfer"]), (C["head_d"] / 2, C["head_len"]),
               (C["body_d"] / 2, C["head_len"]), (C["body_d"] / 2, C["body_end"]), (C["tip_d"] / 2, C["body_end"]),
               (C["tip_d"] / 2, L - C["chamfer"]), (C["tip_d"] / 2 - C["chamfer"], L), (0, L)])
pin = pin.difference(cyl(C["screw_hole_d"], L - C["screw_hole_depth"], L + 0.1), engine="manifold")
# mat phang D de in nam (truc // ban, lop chay doc chot – ben theo tho)
cut = trimesh.creation.box(extents=[20, 20, 40]); cut.apply_translation([0, -10 - C["flat_y"], L / 2])
pin = pin.difference(cut, engine="manifold")
assert pin.is_watertight
# xoay nam: truc Z -> X, mat D (y = -flat_y) xuong ban
pin_print = pin.copy()
pin_print.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))   # -y (mat D) -> -z
pin_print.apply_translation(-pin_print.bounds[0])
for k in "abc":
    pin_print.export(OUT / f"pin-v2-{k}.stl")

# ---------- 3. long den ----------
Wa = P["washer"]
washer = cyl(Wa["od"], 0, Wa["t"]).difference(cyl(Wa["id"], -0.1, Wa["t"] + 0.1), engine="manifold")
for k in "abc":
    washer.export(OUT / f"washer-{k}.stl")

rep = {"worm_volume_mm3": [round(v0, 1), round(worm.volume, 1)], "worm_bbox": worm.extents.round(2).tolist(),
       "pin_volume_mm3": round(pin.volume, 1), "pin_bbox_print": pin_print.extents.round(2).tolist(),
       "washer_volume_mm3": round(washer.volume, 1)}

# ---------- 4. file CAD mo do duoc (SolidCraft .sc, moi chi tiet 1 component) ----------
CLI = os.environ.get("SOLIDCRAFT_CLI", r"C:\Program Files\SolidCraft\solidcraft-cli.exe")
if Path(CLI).exists():
    names = ["worm-v2.stl", "pin-v2-a.stl", "washer-a.stl"]
    ref = SRC / "09-document-solid-11.stl"
    cmds = [{"command": "file.insert_mesh", "params": {"path": str(OUT / n).replace(os.sep, "/"), "name": n[:-4]}} for n in names]
    cmds.append({"command": "file.insert_mesh", "params": {"path": str(ref).replace(os.sep, "/"), "name": "head-09-goc (tham khao)"}})
    jp = OUT / "assembly.json"; jp.write_text(json.dumps({"commands": cmds}), encoding="utf-8")
    r = subprocess.run([CLI, "run", str(jp), "--save", str(OUT / "gripper-v2.sc"), "--quiet"], capture_output=True, text=True)
    rep["sc"] = "ok" if r.returncode == 0 else ("loi: " + (r.stderr or r.stdout)[-300:])
(OUT / "build-report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
print("GRIPPER-V2 OK", json.dumps(rep))
