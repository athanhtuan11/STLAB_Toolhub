"""Tu chay prepare-print.py moi khi file .FCStd duoc LUU (GD D - khong phai nho chay tay).

Chay (de cua so nay mo trong luc lam CAD; Ctrl+C de tat), hoac bat tu Toolhub (trang Du an):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/watch.py <print.yaml>

- Doc `fcstd` trong print.yaml, 3 s xem thoi diem sua 1 lan; file doi va dung yen 5 s (FreeCAD ghi xong) -> chay.
- Dang chay ma lai Luu: chay xong lan nay roi chay them 1 lan (khong chay chong).
- Ket qua: <thu muc print.yaml>/_prepare-print-result.json + anh overview (Toolhub hien).
"""

import subprocess
import sys
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent


def main():
    cfg_p = Path(sys.argv[1]).resolve()
    cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))
    goc = (cfg_p.parent / cfg.get("data_dir", ".")).resolve()
    fc = (goc / cfg["fcstd"]).resolve()
    print(f"Theo doi {fc} (Ctrl+C de tat)", flush=True)
    da_chay = fc.stat().st_mtime
    while True:
        time.sleep(3)
        m = fc.stat().st_mtime
        if m == da_chay:
            continue
        time.sleep(5)
        if fc.stat().st_mtime != m:  # van dang ghi
            continue
        da_chay = fc.stat().st_mtime
        print(f"[{time.strftime('%H:%M:%S')}] file vua Luu -> chuan bi in ...", flush=True)
        r = subprocess.run([sys.executable, str(HERE / "prepare-print.py"), str(cfg_p)])
        print(f"[{time.strftime('%H:%M:%S')}] xong (exit {r.returncode})", flush=True)


try:
    main()
except KeyboardInterrupt:
    pass
