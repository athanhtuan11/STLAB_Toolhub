"""Chuan bi in bang 1 lenh: [kiem nhanh tang 1] song song [xuat STL theo huong in -> cat lop tang 2].

Chay (Python di kem FreeCAD):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/chuan-bi-in.py <du-an>/in_3d/ban-in.yaml

Doc ban-in.yaml: `fcstd`, `kiem_tra` (tham so kiem-tra.py), `xuat` (huong in), `ban` (ban in)
- xem xuat-stl.py, cat-lop.py.
Chi DOC file .FCStd da luu (sua trong FreeCAD xong phai Luu truoc khi chay).
Ra: tom tat + duong dan anh tong-quan.png (tang 1) va tong-quan-in.png (tang 2). Exit 1 neu co FAIL.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FCC = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
NO_WINDOW = 0x08000000


def chay(lenh, log):
    return subprocess.Popen([str(x) for x in lenh], stdout=open(log, "w", encoding="utf-8"), stderr=subprocess.STDOUT,
                            cwd=HERE.parent, creationflags=NO_WINDOW)


def main():
    t0 = time.time()
    cfg_p = Path(sys.argv[1]).resolve()
    cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))
    goc = cfg_p.parent
    fcstd = (goc / cfg["fcstd"]).resolve()
    ra = (goc / cfg["ra"]).resolve()
    logs = ra / "_log"
    logs.mkdir(parents=True, exist_ok=True)

    # tham so kiem-tra: out=<tuong doi> -> tuyet doi theo file yaml
    kt = [f"out={(goc / x[4:]).resolve()}" if x.startswith("out=") else x for x in cfg.get("kiem_tra", [])]
    out_kt = next((Path(x[4:]) for x in kt if x.startswith("out=")), fcstd.parent / "kiem-tra" / fcstd.stem)
    print(f"Tang 1 (kiem nhanh) + xuat STL song song: {fcstd.name}", flush=True)
    p1 = chay([FCC, HERE / "kiem-tra.py", "--pass", fcstd, *kt], logs / "kiem-tra.txt")
    p2 = chay([FCC, HERE / "xuat-stl.py", "--pass", cfg_p], logs / "xuat-stl.txt")
    p2.wait()
    t_xuat = time.time() - t0
    xs = json.loads((goc / cfg["stl"] / "_xuat-stl.json").read_text(encoding="utf-8"))
    print(f"  xuat STL: {xs['so_stl']} file, {t_xuat:.0f} s"
          + (f"; QUY TAC KHONG KHOP: {xs['quy_tac_khong_khop']}" if xs["quy_tac_khong_khop"] else ""), flush=True)
    print("Tang 2 (cat lop Bambu) ...", flush=True)
    p3 = chay([sys.executable, HERE / "cat-lop.py", cfg_p], logs / "cat-lop.txt")
    p3.wait()
    t_cat = time.time() - t0 - t_xuat
    p1.wait()

    kq = []
    b1 = json.loads((out_kt / "bao-cao.json").read_text(encoding="utf-8"))
    loi1 = [f"{c['nhan']}: {k} {v['tom_tat']}" for c in b1["chi_tiet"] for k, v in c["ket_qua"].items()
            if v["trang_thai"] == "FAIL"]
    loi1 += [f"{x['a']} ~ {x['b']}: {x['tom_tat']}" for x in b1["va_cham"]["cap"] if x["trang_thai"] == "FAIL"]
    kq.append(("Tang 1 kiem nhanh", b1["ket_luan"], f"{b1['thoi_gian_chay_s']} s", loi1, out_kt / "tong-quan.png"))
    b2 = json.loads((ra / "bao-cao-in.json").read_text(encoding="utf-8"))
    loi2 = [f"{b['ban']}: {x}" for b in b2["ban"] for x in b["loi"]]
    loi2 += [f"STL chua xep ban: {n}" for n in b2["stl_chua_xep"]]
    xl = "; ".join(f"{k}: support {v['support']}" + (f", xoay {v['xoay']}" if v["xoay"] else "")
                   for k, v in b2.get("xu_ly_lo_lung", {}).items() if v["xoay"] or v["support"])
    kq.append(("Tang 2 cat lop", b2["ket_luan"], f"{t_cat:.0f} s, in {b2['tong_thoi_gian_in']}, {b2['tong_gam']} g",
               loi2 + ([f"tu xu ly lo lung -> {xl}"] if xl else []), ra / "tong-quan-in.png"))

    print(f"\n=== CHUAN BI IN: {time.time() - t0:.0f} s ===")
    for ten, tt, tg, loi, anh in kq:
        print(f"{ten}: {tt} ({tg})  anh: {anh}")
        for x in loi:
            print(f"   - {x}")
    print(f"File in (mo bang Bambu Studio): {ra}\\<ban>\\<ban>.3mf")
    return 1 if any(tt == "FAIL" for _, tt, _, _, _ in kq) else 0


sys.exit(main())
