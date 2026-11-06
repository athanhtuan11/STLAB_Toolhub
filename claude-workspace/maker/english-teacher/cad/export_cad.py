"""export_cad.py - gom out/asm/*.stl (moi chi tiet o dung vi tri lap, mm) thanh out/owl-assembly.sc (SolidCraft, mac dinh
cua Tuan 2026-11-06) de MO RA DO. Moi chi tiet = 1 component (than luoi), ten theo file. Chay sau build_owl.py:
    python export_cad.py out
Do trong SolidCraft: cong cu Measure, bat dinh/canh cua luoi. Vanh loa/vong ep la khoi co khi: muon mat phang/tru that de
do de hon thi chon than roi chay "Convert Mesh" (mesh.convert) trong SolidCraft.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

CLI = os.environ.get("SOLIDCRAFT_CLI", r"C:\Program Files\SolidCraft\solidcraft-cli.exe")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "out").resolve()
ASM = OUT / "asm"
stls = sorted(ASM.glob("*.stl"))
if not stls:
    sys.exit(f"Khong co {ASM}\\*.stl - chay build_owl.py truoc")
cmds = [{"command": "file.insert_mesh", "params": {"path": str(f).replace(os.sep, "/")}} for f in stls]
script = OUT / "owl-assembly.script.json"
script.write_text(json.dumps({"commands": cmds}, indent=1), encoding="utf-8")
sc = OUT / "owl-assembly.sc"
r = subprocess.run([CLI, "run", str(script), "--save", str(sc), "--quiet"], capture_output=True, text=True, encoding="utf-8", errors="replace")
if r.returncode != 0 or not sc.exists():
    print(r.stdout[-1500:], r.stderr[-1500:])
    sys.exit(f"SolidCraft loi (ma {r.returncode})")
script.unlink()
print(f"SAVED {sc.name} ({len(stls)} chi tiet: {', '.join(f.stem for f in stls)})")
