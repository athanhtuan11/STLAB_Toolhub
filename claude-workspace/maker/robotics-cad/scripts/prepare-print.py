"""Chuan bi in bang 1 lenh: [kiem nhanh tang 1] song song [xuat STL theo huong in -> cat lop tang 2].

Chay (Python di kem FreeCAD):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/prepare-print.py <project>/print/print.yaml

Doc print.yaml: `fcstd`, `check` (tham so check.py), `export` (huong in), `plates` (ban in)
- xem export-stl.py, slice.py.
Chi DOC file .FCStd da luu (sua trong FreeCAD xong phai Luu truoc khi chay).
Kem theo (2026-10-23): metrics.py (chi so hoi quy, freecad/metrics.json - LEN GIT, so voi commit truoc)
va bom.py (BOM.csv + BOM.md, kiem bang vit trong ASSEMBLY.md) - chi canh bao, khong lam FAIL.
Ra: tom tat + duong dan anh overview.png (tang 1) va print-overview.png (tang 2). Exit 1 neu co FAIL.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metrics  # noqa: E402
FCC = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
NO_WINDOW = 0x08000000


def chay(lenh, log):
    return subprocess.Popen([str(x) for x in lenh], stdout=open(log, "w", encoding="utf-8"), stderr=subprocess.STDOUT,
                            cwd=HERE.parent, creationflags=NO_WINDOW)


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # dong thay doi/BOM co tieng Viet
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
    p4 = chay([FCC, HERE / "metrics.py", "--pass", cfg_p], logs / "metrics.txt")
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
               loi2 + ([f"tu xu ly nho ra / lo lung -> {xl}"] if xl else [])
               + [f"brim: {k} ({len(v)} chi tiet nho)" for k, v in b2.get("brim", {}).items()],
               ra / "print-overview.png"))

    # hoi quy: metrics.json (+ gio/gam ban in) so voi git HEAD; BOM tu Label. Chi bao, khong FAIL.
    p4.wait()
    *_, f_m = metrics.cau_hinh(cfg_p)
    if p4.returncode == 0 and f_m.exists():
        metrics.them_ban_in(cfg_p, b2)
        lk = next((x[11:].split(",") for x in cfg.get("check", []) if x.startswith("components=")), [])
        tt, tom, dong = metrics.so_sanh(metrics.ban_git(f_m), json.loads(f_m.read_text(encoding="utf-8")), lk)
        kq.append(("So voi commit truoc", tt, tom, dong, ""))
        p5 = subprocess.run([sys.executable, HERE / "bom.py", cfg_p], capture_output=True, text=True,
                            encoding="utf-8", creationflags=NO_WINDOW)
        f_bom = cfg_p.parent / "_bom.json"
        if p5.returncode == 0 and f_bom.exists():
            bom = json.loads(f_bom.read_text(encoding="utf-8"))
            vit = ", ".join(f"{k}: {n}" for k, n in bom["vit"].items())
            loi5 = bom["lech_assembly"] + [f"chua phan loai: {x}" for x in bom["chua_phan_loai"]]
            kq.append(("BOM", "WARN" if bom["lech_assembly"] else "PASS",
                       f"vit {vit}; {bom['linh_kien_mua']} linh kien mua; {bom['chi_tiet_in']} chi tiet in", loi5,
                       ""))
        else:
            kq.append(("BOM", "WARN", "bom.py loi", [p5.stderr[-300:]], ""))
    else:
        kq.append(("So voi commit truoc", "WARN", f"metrics.py loi, xem {logs / 'metrics.txt'}", [], ""))

    print(f"\n=== CHUAN BI IN: {time.time() - t0:.0f} s ===")
    for ten, tt, tg, loi, anh in kq:
        print(f"{ten}: {tt} ({tg})" + (f"  anh: {anh}" if anh else ""))
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
