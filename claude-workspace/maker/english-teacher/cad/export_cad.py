"""export_cad.py - file CAD mo-ra-do cua Cu Bong: goi cong cu chung tools/cad-export/export_cad.py
(out-v3/asm/*.stl -> out-v3/owl-assembly.sc + .step + .blend). run_v3.py da tu goi; chay tay:
    python export_cad.py [out-v3]
"""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = HERE / (sys.argv[1] if len(sys.argv) > 1 else "out-v3")
sys.exit(subprocess.call([sys.executable, str(HERE.parents[2] / "tools" / "cad-export" / "export_cad.py"), str(out / "asm"), "owl-assembly"]))
