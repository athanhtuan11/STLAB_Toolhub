"""Chuan bi in bang 1 lenh: KIEM HET TRUOC, SACH MOI CAT LOP (Tuan 2026-10-23: "xong xuoi tat ca roi hay ra file in").

  1) song song: kiem nhanh tang 1 (check.py) | xuat STL theo huong in (export-stl.py) | metrics.py
  2) kha nang in tren STL (printability: mat nho ra -> WARN "to support trong Bambu Studio" + KIEM THEO LOP: cum roi) - vai giay
  3) CHI KHI 1) khong FAIL va 2) khong co cum roi -> cat lop Bambu (slice.py) ra file in .3mf
     (co loi -> dung, khong cat: tiet kiem thoi gian, khong de lai file in sai). Ep cat: them `force` sau print.yaml.

Chay (Python di kem FreeCAD):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/prepare-print.py <project>/print/print.yaml

Doc print.yaml: `fcstd`, `check` (tham so check.py), `export` (huong in), `plates` (ban in)
- xem export-stl.py, slice.py.
Chi DOC file .FCStd da luu (sua trong FreeCAD xong phai Luu truoc khi chay).
Kem theo (2026-10-23): metrics.py (chi so hoi quy, freecad/metrics.json - LEN GIT, so voi commit truoc)
va bom.py (BOM.csv + BOM.md, kiem bang vit trong ASSEMBLY.md) - chi canh bao, khong lam FAIL.
Ra: tom tat + duong dan anh overview.png (tang 1) va print-overview.png (tang 2). Exit 1 neu co FAIL.
"""

import hashlib
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


def doc_moi(f, t0, log):
    """Doc JSON ket qua cua tien trinh con - CHI khi file ghi SAU t0. freecadcmd loi van tra exit 0 (do 2026-10-24),
    file cu cua lan truoc con nam do -> neu khong kiem, quy trinh chay tiep voi ket qua/STL CU ma khong bao."""
    f = Path(f)
    if not f.exists() or f.stat().st_mtime < t0 - 1:
        log = Path(log)
        tail = "".join(log.read_text(encoding="utf-8", errors="replace").splitlines(True)[-15:]) if log.exists() else ""
        raise SystemExit(f"LOI: {f.name} khong duoc tao moi (script con loi?) - xem {log}\n{tail}")
    return json.loads(f.read_text(encoding="utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # dong thay doi/BOM co tieng Viet
    t0 = time.time()
    cfg_p = Path(sys.argv[1]).resolve()
    ep_cat = "force" in sys.argv[2:]
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
    # thao lap (assembly_paths, Tuan 2026-10-26: "in roi khong lap vao nhau duoc") - chi khi print.yaml co `assembly:`;
    # cache theo noi dung FCStd + allow + ma assembly_paths (pushrod-arm ~53 s -> 0 s khi model khong doi)
    asm, p5, a5 = cfg.get("assembly"), None, None
    if asm is not None:
        allow = ",".join((asm or {}).get("allow", []))
        f_ky, f_js = logs / "assembly.sig", logs / "assembly.json"
        ky = hashlib.sha1(fcstd.read_bytes() + allow.encode() + (HERE / "assembly_paths.py").read_bytes()).hexdigest()
        if f_ky.exists() and f_js.exists() and f_ky.read_text() == ky:
            a5 = json.loads(f_js.read_text(encoding="utf-8"))
        else:
            p5 = chay([FCC, "--safe-mode", HERE / "fc_cli.py", "--pass", HERE / "assembly_paths.py", fcstd,
                       f"allow={allow}", f"json={f_js}"], logs / "assembly.txt")
    p2.wait()
    t_xuat = time.time() - t0
    xs = doc_moi(goc / cfg["stl"] / "_export-stl.json", t0, logs / "export-stl.txt")
    print(f"  xuat STL: {xs['so_stl']} file, {t_xuat:.0f} s"
          + (f"; QUY TAC KHONG KHOP: {xs['quy_tac_khong_khop']}" if xs["quy_tac_khong_khop"] else ""), flush=True)
    # 2) kha nang in tren STL theo huong in (trong luc check.py van chay)
    import printability
    tng = yaml.safe_load((HERE.parent / "thresholds.yaml").read_text(encoding="utf-8"))
    ngp = dict(tng.get("print") or {}, overhang_deg=tng.get("overhang_deg", 45))
    t1 = time.time()
    loi_in, cb_in = [], []
    for f in sorted((goc / cfg["stl"]).glob("*.stl")):
        r = printability.phan_tich(f, ngp)
        if r["can_support"]:  # Tuan 2026-10-25: Tuan tu to support trong Bambu Studio -> WARN, khong chan cat lop
            cb_in.append(f"{f.name}: CAN SUPPORT (to trong Bambu Studio) " + ", ".join(
                f"{c['mm2']} mm2 o z {c['z_mm']}" for c in r["cum_nho"][:2]))
        for x in printability.kiem_lop(f):
            if x["loai"].startswith("roi") and r["can_support"]:  # cum roi o chi tiet da bao can support = Tuan to support
                cb_in.append(f"{f.name}: cum ROI {x['mm2']} mm2 o z {x['z_mm']} -> to support tu ban (xy {x['bao_xy']})")
            elif x["loai"].startswith("roi"):
                loi_in.append(f"{f.name}: cum ROI {x['mm2']} mm2 o z {x['z_mm']} (xy {x['bao_xy']})")
            elif x["loai"] == "vuon ra" and x.get("mm2", 0) > 20:
                cb_in.append(f"{f.name}: vuon ra {x['mm2']} mm2 o z {x['z_mm']} (bac cau? xy {x['bao_xy']})")
            elif x["loai"] != "vuon ra":  # vd. "luoi khong kin": KHONG kiem duoc theo lop -> phai bao, khong im lang PASS
                cb_in.append(f"{f.name}: {x['loai']}")
    print(f"  kha nang in: {len(loi_in)} loi, {len(cb_in)} canh bao ({time.time() - t1:.1f} s)", flush=True)
    p1.wait()
    kq = []
    b1 = doc_moi(out_kt / "report.json", t0, logs / "check.txt")
    loi1 = [f"{c['nhan']}: {k} {v['tom_tat']}" for c in b1["chi_tiet"] for k, v in c["ket_qua"].items()
            if v["trang_thai"] == "FAIL"]
    loi1 += [f"{x['a']} ~ {x['b']}: {x['tom_tat']}" for x in b1["va_cham"]["cap"] if x["trang_thai"] == "FAIL"]
    kq.append(("Tang 1 kiem nhanh", b1["ket_luan"], f"{b1['thoi_gian_chay_s']} s", loi1, out_kt / "overview.png"))
    kq.append(("Kha nang in (STL)", "FAIL" if loi_in else ("WARN" if cb_in else "PASS"),
               f"{xs['so_stl']} STL", loi_in + cb_in, ""))
    if asm is not None:
        if p5 is not None:
            p5.wait()
            a5 = doc_moi(f_js, t0, logs / "assembly.txt")
            f_ky.write_text(ky)
        kq.append(("Thao lap (assembly_paths)", "WARN" if a5["trapped"] else "PASS",
                   f"{a5['pairs']} cap cham, {len(a5['trapped'])} cap KET",
                   [f"KET: {a} | {b} {n}" for a, b, n in a5["trapped"]], ""))

    # 3) chi cat lop khi da sach
    b2 = None
    if (b1["ket_luan"] != "FAIL" and not loi_in) or ep_cat:
        print("Tang 2 (cat lop Bambu) ...", flush=True)
        t2 = time.time()
        p3 = chay([sys.executable, HERE / "slice.py", cfg_p], logs / "slice.txt")
        p3.wait()
        t_cat = time.time() - t2
        b2 = doc_moi(ra / "print-report.json", t2, logs / "slice.txt")
    else:
        kq.append(("Tang 2 cat lop", "INFO", "CHUA CAT - sua loi o tren truoc (file in cu trong plates/ KHONG con dung)",
                   [], ""))
    if b2 is not None:
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
    # returncode freecadcmd luon 0; metrics.json KHONG ghi lai khi so lieu khong doi -> kiem dong xac nhan trong log
    if f_m.exists() and "METRICS " in (logs / "metrics.txt").read_text(encoding="utf-8", errors="replace"):
        if b2 is not None:
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
    if b2 is not None:
        print(f"File in (mo bang Bambu Studio): {ra}\\<ban>\\<ban>.3mf")
    else:
        print("CHUA RA FILE IN: sua loi tang 1 / kha nang in roi chay lai (ep cat: them `force`).")
    # tom tat canh print.yaml cho Toolhub (trang Du an) doc; file sinh, khong len git
    tom = {"thoi_gian": time.strftime("%Y-%m-%d %H:%M"), "tong_s": round(time.time() - t0), "thu_muc_in": str(ra),
           "tang": [{"ten": ten, "ket_luan": tt, "chi_tiet": tg, "loi": loi, "anh": str(anh)}
                    for ten, tt, tg, loi, anh in kq]}
    f_tom = cfg_p.parent / "_prepare-print-result.json"
    f_tom.write_text(json.dumps(tom, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if any(tt == "FAIL" for _, tt, _, _, _ in kq) else 0


sys.exit(main())
