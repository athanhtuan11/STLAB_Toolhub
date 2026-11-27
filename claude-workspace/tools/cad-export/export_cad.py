"""export_cad.py - XUAT FILE CAD MO-RA-DO-DUOC cho moi du an (Tuan 2026-11-06 + 2026-11-27: "CAD phai co file cho
Blender hay bat ki phan mem CAD nao"). Dau vao: thu muc asm/ - moi chi tiet 1 STL o DUNG VI TRI LAP, don vi mm.
Dau ra (cung thu muc cha cua asm/):
    <ten>.sc     SolidCraft lap rap, moi chi tiet 1 component, than da Convert Mesh -> solid (do mat/canh)  [mac dinh]
    <ten>.step   STEP AP lap rap (faceted solid) - mo bang Fusion 360, FreeCAD, Onshape, SolidWorks, Bambu Studio...
    <ten>.blend  Blender, moi chi tiet 1 object ten theo file, don vi mm (scale_length 0.001)
Chay:
    python tools/cad-export/export_cad.py <asm_dir> <ten>              # ca 3
    python tools/cad-export/export_cad.py <asm_dir> <ten> --no-step    # bo STEP (nhanh hon, STEP ~5-10 MB/chi tiet)
Chi tiet nao Convert Mesh loi (luoi ho/tu cat) -> giu luoi trong .sc, bo khoi STEP, in canh bao (khong im lang).
Bien moi truong: SOLIDCRAFT_CLI, BLENDER_EXE.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

CLI = os.environ.get("SOLIDCRAFT_CLI", r"C:\Program Files\SolidCraft\solidcraft-cli.exe")
BLENDER = os.environ.get("BLENDER_EXE", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")

BLEND_PY = r'''
import bpy, bmesh, sys, os
a = sys.argv[sys.argv.index("--") + 1:]
out, clean_dir, stls = a[0], a[1], a[2:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0   # khong sinh .blend1
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"; sc.unit_settings.length_unit = "MILLIMETERS"; sc.unit_settings.scale_length = 0.001
for p in stls:
    bpy.ops.wm.stl_import(filepath=p)
    o = bpy.context.selected_objects[0]
    o.name = o.data.name = os.path.splitext(os.path.basename(p))[0]
    bm = bmesh.new(); bm.from_mesh(o.data)          # lam sach cho SolidCraft Convert Mesh (luoi boolean Blender)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.0005)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_area() < 1e-9], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free()
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True)
    bpy.ops.wm.stl_export(filepath=os.path.join(clean_dir, o.name + ".stl"), export_selected_objects=True, apply_modifiers=False)
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print("BLEND_OK", len(stls))
'''


def sc_run(cmds, sc, step, tag):
    script = sc.with_suffix(f".{tag}.json")
    script.write_text(json.dumps({"commands": cmds}, indent=1), encoding="utf-8")
    args = [CLI, "run", str(script), "--save", str(sc), "--quiet"] + (["--out", str(step)] if step else [])
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    script.unlink()
    return r


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = [x for x in sys.argv[1:] if x.startswith("--")]
    if len(a) < 2:
        sys.exit(__doc__)
    asm, name = Path(a[0]).resolve(), a[1]
    out = asm.parent
    stls = sorted(asm.glob("*.stl"))
    if not stls:
        sys.exit(f"Khong co {asm}\\*.stl (moi chi tiet 1 STL o vi tri lap)")
    sc, step, blend = out / f"{name}.sc", out / f"{name}.step", out / f"{name}.blend"
    want_step = "--no-step" not in flags
    res, t0 = [], time.time()

    # 1) Blender: .blend + STL da lam sach (gop dinh trung, lap lo, phap tuyen) cho SolidCraft
    clean = out / "_cad_clean"; clean.mkdir(exist_ok=True)
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr", BLEND_PY, "--",
                        str(blend), str(clean)] + [str(f) for f in stls], capture_output=True, text=True, encoding="utf-8", errors="replace")
    res.append(blend.name if r.returncode == 0 and blend.exists() else "BLEND LOI: " + (r.stdout + r.stderr)[-400:])
    src = [clean / f.name if (clean / f.name).exists() else f for f in stls]

    # 2) SolidCraft: insert + convert; buoc convert loi -> bo convert chi tiet do (giu luoi), chay lai
    ins = lambda f: {"command": "file.insert_mesh", "params": {"path": str(f).replace(os.sep, "/")}}
    conv = lambda f: {"command": "mesh.convert", "params": {"body": f.stem}}
    bad = []
    while True:
        cmds, owner = [], []
        for f in src:
            cmds.append(ins(f)); owner.append(None)
            if f.stem not in bad:
                cmds.append(conv(f)); owner.append(f.stem)
        r = sc_run(cmds, sc, step if (want_step and not bad) else None, "asm")
        m = re.search(r"step (\d+) \(mesh\.convert\)", r.stderr + r.stdout)
        if r.returncode != 0 and m and owner[int(m.group(1)) - 1]:
            bad.append(owner[int(m.group(1)) - 1]); continue
        break
    if r.returncode != 0 or not sc.exists():
        print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit(f"SolidCraft loi (ma {r.returncode})")
    res.append(f"{sc.name} ({len(stls)} chi tiet{', luoi (khong convert duoc): ' + ', '.join(bad) if bad else ', tat ca solid'})")
    if want_step and bad:   # STEP chi nhan solid -> xuat rieng cac chi tiet da convert
        ok = [f for f in src if f.stem not in bad]
        r = sc_run([c for f in ok for c in (ins(f), conv(f))], out / "_step.sc", step, "step")
        (out / "_step.sc").unlink(missing_ok=True)
    if want_step:
        res.append(f"{step.name} ({step.stat().st_size / 1e6:.0f} MB)" if step.exists() else "STEP LOI")
        if bad:
            res.append("CANH BAO: STEP thieu " + ", ".join(bad) + " (luoi khong kin sau lam sach - xem .sc/.blend)")
    shutil.rmtree(clean, ignore_errors=True)

    print(f"CAD EXPORT ({time.time() - t0:.0f} s) -> {out}")
    for x in res:
        print("  " + x)
    if any("LOI" in x for x in res):
        sys.exit(1)


if __name__ == "__main__":
    main()
