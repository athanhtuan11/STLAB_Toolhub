"""Anh tung buoc lap rap tu cam_d.sc (SolidCraft snapshot) -> images/assembly/step-XX.png.

Chay sau build_cam_d.py:  python render_assembly.py
Chi tiet MOI mau vang, da lap mau xam, chua lap thi an; chi tiet moi duoc keo ra (no) theo huong lap.
"""
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get('SOLIDCRAFT_CLI', r'C:\Program Files\SolidCraft\solidcraft-cli.exe')
SC = os.path.join(HERE, 'cam_d.sc')
OUT = os.path.join(HERE, 'images', 'assembly')
ALL = ["Body", "Bezel", "U_frame", "Base", "Pin_cap", "Ref_Stack", "Ref_Cam", "Coupon", "Coupon_ring"]
OCC = {"Body": "Body:1", "Bezel": "Bezel:1", "U_frame": "U_frame:1", "Base": "Base:1", "Pin_cap": "Pin_cap:1",
       "Ref_Stack": "Ref:1", "Ref_Cam": "Ref:1"}
VANG, XAM = "#f2c200", "#b4b4b4"
CAM, MACH = "#d9a400", "#3a7d44"

# (so buoc, chi tiet da lap, chi tiet moi, {occurrence: [dx,dy,dz]} keo ra, view)
STEPS = [
    (1, [], ["Base"], {}, "iso"),
    (2, ["Base"], ["U_frame"], {"U_frame:1": [0, 0, 25]}, "iso"),
    (3, ["Base", "U_frame"], ["Pin_cap"], {"Pin_cap:1": [0, 0, 18]}, "iso"),
    (4, [], ["Body"], {}, "iso"),
    (5, ["Body"], ["Ref_Stack", "Ref_Cam"], {"Ref:1": [0, -45, 0]}, "iso"),
    (6, ["Body", "Ref_Stack", "Ref_Cam"], ["Bezel"], {"Bezel:1": [0, -30, 0]}, "iso"),
    (7, ["Base", "U_frame", "Pin_cap"], ["Body", "Bezel", "Ref_Stack", "Ref_Cam"],
     {"Body:1": [0, 0, 45], "Bezel:1": [0, 0, 45], "Ref:1": [0, 0, 45]}, "iso"),
    (8, ["Base", "U_frame", "Pin_cap", "Body", "Bezel", "Ref_Stack", "Ref_Cam"], [], {}, "iso"),
]


def one(step):
    n, old, new, moves, view = step
    hide = [b for b in ALL if b not in old + new]
    cmds = [{"command": "browser.visibility", "params": {"visible": False, "items": hide}}] if hide else []
    for occ, t in moves.items():
        cmds.append({"command": "occurrence.move",
                     "params": {"occurrence": occ, "space": "world", "translate": t, "move_grounded": True}})
    fd, js = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w') as f:
        json.dump({"commands": cmds}, f)
    args = [CLI, "snapshot", js, "--in", SC, "--out", os.path.join(OUT, "step-%02d.png" % n), "--view", view,
            "--width", "1200", "--height", "900", "--no-grid", "--no-axes"]
    for b in old + new:
        if b == "Ref_Stack":
            col = MACH
        elif b == "Ref_Cam":
            col = CAM if b in new else XAM
        else:
            col = VANG if b in new else XAM
        if n == 8 and b not in ("Ref_Stack", "Ref_Cam"):
            col = "#8c8c8c"
        args += ["--body", "%s:color=%s" % (b, col)]
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    os.remove(js)
    return n, r.returncode, (r.stderr or '')[-400:]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(one, STEPS))
    bad = [x for x in res if x[1] != 0]
    for n, rc, err in bad:
        print("step %d loi: %s" % (n, err))
    print("ASSEMBLY IMAGES %d/%d -> %s" % (len(res) - len(bad), len(res), OUT))
    sys.exit(1 if bad else 0)
