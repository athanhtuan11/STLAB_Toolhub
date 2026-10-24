"""Lop phu cho RobotCAD de sua loi khoi dong FreeCAD MA KHONG sua ban ghim trong community/.

Loi (RobotCAD v12.10.3, con o v12.10.4 va main 2026-10-24): package.xml khai
    <subdirectory>freecad/robotcad</subdirectory>
nhung ma that nam o freecad/cross. FreeCAD 1.1 goi os.add_dll_directory() cho thu muc nay -> FileNotFoundError
-> "Error in InitApplications" -> phan con lai cua InitApplications bi bo qua:
    - thu muc Macro KHONG vao sys.path (macro import file phu trong Macro/ se loi),
    - PATH khong them duong dan Mod, DLL dir cua cac Mod nap sau khong dang ky.
RobotCAD van chay (nap qua namespace freecad.cross), nhung loi anh huong MOI addon/macro.

Cach sua: custom/freecad/robotcad-overlay/ = junction toi tung muc cua ban clone + freecad/ that gom
junction cross -> ban clone va thu muc rong robotcad (dung cai package.xml doi). Mod/freecad.robotcad tro vao day
(community/links.tsv). Ban clone giu nguyen, cap nhat ban ghim thi chay lai script nay.

Chay: python custom/freecad/robotcad_overlay.py      (tao / kiem)
Bo khi upstream sua package.xml: doi links.tsv ve community/drfenixion-freecad-robotcad, xoa thu muc overlay.
"""

import os
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
SRC = WS / "community" / "drfenixion-freecad-robotcad"
DST = Path(__file__).resolve().parent / "robotcad-overlay"


def link(dst, src):
    if dst.exists() or dst.is_symlink():
        return False
    if src.is_dir():
        subprocess.run(["cmd", "/c", "mklink", "/J", str(dst), str(src)], check=True, capture_output=True)
    else:
        os.symlink(src, dst)  # can Developer Mode (da bat, docs/COMMUNITY.md)
    return True


def main():
    if not (SRC / "package.xml").exists():
        print(f"Thieu ban clone {SRC} - chay community/update-community.sh clone")
        return 1
    DST.mkdir(exist_ok=True)
    moi = []
    for p in sorted(SRC.iterdir()):
        if p.name in (".git", "freecad"):
            continue
        if link(DST / p.name, p):
            moi.append(p.name)
    fc = DST / "freecad"
    fc.mkdir(exist_ok=True)
    for p in sorted((SRC / "freecad").iterdir()):
        if link(fc / p.name, p):
            moi.append(f"freecad/{p.name}")
    rc = fc / "robotcad"
    if not rc.exists():
        rc.mkdir()
        moi.append("freecad/robotcad (rong)")
    thua = [p.name for p in DST.iterdir() if p.name != "freecad" and not (SRC / p.name).exists()]
    print(f"Overlay {DST}: them {moi or 'khong'}" + (f"; muc khong con trong ban clone: {thua}" if thua else ""))
    return 0


sys.exit(main())
