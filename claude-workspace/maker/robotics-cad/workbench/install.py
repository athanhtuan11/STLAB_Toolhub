"""Cai workbench STLab vao FreeCAD 1.1: tao JUNCTION %APPDATA%/FreeCAD/v1-1/Mod/STLab -> workbench/STLab (mot nguon).

Chay: python workbench/install.py            (kiem / tao)
      python workbench/install.py remove     (go junction; khong xoa ma nguon)
Khong ghi de: Mod/STLab da co va KHONG phai junction toi day -> dung, bao.
"""

import os
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "STLab"
DST = Path(os.environ["APPDATA"]) / "FreeCAD" / "v1-1" / "Mod" / "STLab"


def is_junction(p):
    try:
        return p.is_junction() if hasattr(p, "is_junction") else bool(os.readlink(p))
    except OSError:
        return False


def main():
    if sys.argv[1:] == ["remove"]:
        if is_junction(DST):
            os.rmdir(DST)  # rmdir junction chi go lien ket, khong dung toi thu muc dich
            print(f"Da go {DST}")
        else:
            print(f"{DST} khong phai junction - khong lam gi")
        return 0
    if DST.exists() or is_junction(DST):
        if is_junction(DST) and DST.resolve() == SRC:
            print(f"OK: {DST} -> {SRC}")
            return 0
        print(f"DUNG: {DST} da ton tai va khong tro toi {SRC} - kiem tra bang tay")
        return 1
    DST.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cmd", "/c", "mklink", "/J", str(DST), str(SRC)], check=True)
    print(f"Da tao {DST} -> {SRC}. Mo lai FreeCAD, chon workbench STLab.")
    return 0


sys.exit(main())
