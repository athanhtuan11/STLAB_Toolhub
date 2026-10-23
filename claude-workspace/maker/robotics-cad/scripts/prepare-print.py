"""Chuan bi in bang 1 lenh: [kiem nhanh tang 1] song song [xuat STL theo huong in -> cat lop tang 2].

Chay (Python di kem FreeCAD):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/prepare-print.py <project>/print/print.yaml

Doc print.yaml: `fcstd`, `check` (tham so check.py), `export` (huong in), `plates` (ban in)
- xem export-stl.py, slice.py.
Chi DOC file .FCStd da luu (sua trong FreeCAD xong phai Luu truoc khi chay).
Ra: tom tat + duong dan anh overview.png (tang 1) va print-overview.png (tang 2). Exit 1 neu co FAIL.
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
    goc = (cfg_p.parent / cfg.get("data_dir", ".")).resolve()  # FCStd/STL co the o ngoai repo
    fcstd = (goc / cfg["fcstd"]).resolve()
    ra = (goc / cfg["plates_dir"]).resolve()
    logs = ra / "_log"
    logs.mkdir(parents=True, exist_ok=True)

    # tham so kiem-tra: out=<tuong doi> -> tuyet doi theo file yaml
    kt = [f"out={(goc / x[4:]).resolve()}" if x.startswith("out=") else x for x in cfg.get("check", [])]
    out_kt = next((Path(x[4:]) for x in kt if x.startswith("out=")), fcstd.parent / "check" / fcstd.stem)
    print(f"Tang 1 (kiem nhanh) + xuat STL song song: {fcstd.name}", flush=True)
    p1 = chay([FCC, HERE / "check.py", "--pass", fcstd, *kt], logs / "check.txt")
    p2 = chay([FCC, HERE / "export-stl.py", "--pass", cfg_p], logs / "export-stl.txt")
    p2.wait()
    t_xuat = time.time() - t0
    xs = json.loads((goc / cfg["stl"] / "_export-stl.json").read_text(encoding="utf-8"))
    print(f"  xuat STL: {xs['so_stl']} file, {t_xuat:.0f} s"
          + (f"; QUY TAC KHONG KHOP: {xs['quy_tac_khong_khop']}" if xs["quy_tac_khong_khop"] else ""), flush=True)
    print("Tang 2 (cat lop Bambu) ...", flush=True)
    p3 = chay([sys.executable, HERE / "slice.py", cfg_p], logs / "slice.txt")
    p3.wait()
    t_cat = time.time() - t0 - t_xuat
    p1.wait()

    kq = []
    b1 = json.loads((out_kt / "report.json").read_text(encoding="utf-8"))
    loi1 = [f"{c['nhan']}: {k} {v['tom_tat']}" for c in b1["chi_tiet"] for k, v in c["ket_qua"].items()
            if v["trang_thai"] == "FAIL"]
    loi1 += [f"{x['a']} ~ {x['b']}: {x['tom_tat']}" for x in b1["va_cham"]["cap"] if x["trang_thai"] == "FAIL"]
    kq.append(("Tang 1 kiem nhanh", b1["ket_luan"], f"{b1['thoi_gian_chay_s']} s", loi1, out_kt / "overview.png"))
    b2 = json.loads((ra / "print-report.json").read_text(encoding="utf-8"))
    loi2 = [f"{b['ban']}: {x}" for b in b2["ban"] for x in b["loi"]]
    loi2 += [f"STL chua xep ban: {n}" for n in b2["stl_chua_xep"]]
    xl = "; ".join(f"{k}: support {v['support']}" + (f", xoay {v['xoay']}" if v["xoay"] else "")
                   for k, v in b2.get("xu_ly_lo_lung", {}).items() if v["xoay"] or v["support"])
    kq.append(("Tang 2 cat lop", b2["ket_luan"], f"{t_cat:.0f} s, in {b2['tong_thoi_gian_in']}, {b2['tong_gam']} g",
               loi2 + ([f"tu xu ly lo lung -> {xl}"] if xl else []), ra / "print-overview.png"))

    print(f"\n=== CHUAN BI IN: {time.time() - t0:.0f} s ===")
    for ten, tt, tg, loi, anh in kq:
        print(f"{ten}: {tt} ({tg})  anh: {anh}")
        for x in loi:
            print(f"   - {x}")
    print(f"File in (mo bang Bambu Studio): {ra}\\<ban>\\<ban>.3mf")
    # tom tat canh print.yaml cho Toolhub (trang Du an) doc; file sinh, khong len git
    tom = {"thoi_gian": time.strftime("%Y-%m-%d %H:%M"), "tong_s": round(time.time() - t0), "thu_muc_in": str(ra),
           "tang": [{"ten": ten, "ket_luan": tt, "chi_tiet": tg, "loi": loi, "anh": str(anh)}
                    for ten, tt, tg, loi, anh in kq]}
    f_tom = cfg_p.parent / "_prepare-print-result.json"
    f_tom.write_text(json.dumps(tom, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if any(tt == "FAIL" for _, tt, _, _, _ in kq) else 0


sys.exit(main())
