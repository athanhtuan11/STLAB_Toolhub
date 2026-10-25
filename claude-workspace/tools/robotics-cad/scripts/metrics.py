"""Chi so hoi quy cua model: freecad/metrics.json (LEN GIT) - so voi commit truoc de bat thay doi ngoai y muon.

1) Thu thap (freecadcmd, thuong goi qua prepare-print.py; chi DOC file da Luu, ve tu the goc `rest_pose`):
    "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" scripts/metrics.py --pass <print.yaml>
   -> moi chi tiet (Label): the tich (mm3, B-rep), hop bao [xmin ymin zmin xmax ymax zmax] (mm), trong tam (mm),
      so solid.
2) So sanh (Python thuong): python scripts/metrics.py diff <print.yaml>
   -> so freecad/metrics.json voi ban trong git HEAD: chi tiet moi/xoa/doi the tich/doi vi tri,
      ban in doi gio/gam.
prepare-print.py lam ca 2 va them muc `plates` (gio/gam tung ban, tu print-report.json).
`git diff freecad/metrics.json` = nhat ky thay doi hinh hoc cho Release. File khong co thoi gian chay -> khong doi thi
git khong thay doi.
"""

import fnmatch
import json
import subprocess
import sys
from pathlib import Path

V_TOL_MM3 = 0.1    # nho hon = lam tron, khong bao
POS_TOL_MM = 0.01


def cau_hinh(cfg_p):
    import yaml
    cfg_p = Path(cfg_p).resolve()
    cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))
    goc = (cfg_p.parent / cfg.get("data_dir", ".")).resolve()
    fcstd = (goc / cfg["fcstd"]).resolve()
    out = (cfg_p.parent / cfg["metrics"]).resolve() if cfg.get("metrics") else fcstd.parent / "metrics.json"
    return cfg_p, cfg, goc, fcstd, out


def thu_thap(cfg_p):
    import FreeCAD as App
    _, cfg, goc, fcstd, out = cau_hinh(cfg_p)
    doc = App.openDocument(str(fcstd))
    if cfg.get("rest_pose"):  # chi doi trong bo nho, khong luu (giong export-stl.py)
        rest = json.loads((goc / cfg["rest_pose"]).read_text(encoding="utf-8"))
        for o in doc.Objects:
            if o.Name in rest:
                b, q = rest[o.Name]
                o.Placement = App.Placement(App.Vector(*b), App.Rotation(*q))
    parts = {}
    for o in doc.Objects:
        # chi tiet "la": Part::Feature co solid, dang hien, khong bi feature khac dung lam dau vao
        if (not o.isDerivedFrom("Part::Feature") or not getattr(o, "Visibility", True) or not o.Shape.Solids
                or any(p.isDerivedFrom("Part::Feature") for p in o.InList)):
            continue
        s = o.Shape
        vt = sum(x.Volume for x in s.Solids) or 1.0
        com = [sum(getattr(x.CenterOfMass, k) * x.Volume for x in s.Solids) / vt for k in "xyz"]
        bb = s.BoundBox
        parts[o.Label] = {"volume_mm3": round(s.Volume, 1),
                          "bbox_mm": [round(v, 2) for v in (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)],
                          "com_mm": [round(v, 2) for v in com], "solids": len(s.Solids)}
    App.closeDocument(doc.Name)
    cu = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    m = {"fcstd": fcstd.name, "freecad": ".".join(App.Version()[:3]), "parts": dict(sorted(parts.items())),
         "plates": cu.get("plates", {})}
    ghi(out, m)
    print(f"METRICS {len(parts)} chi tiet -> {out}", flush=True)


def ghi(out, m):
    txt = json.dumps(m, ensure_ascii=False, indent=1) + "\n"
    if not out.exists() or out.read_text(encoding="utf-8") != txt:
        out.write_text(txt, encoding="utf-8")


def them_ban_in(cfg_p, print_report):
    """Ghi gio/gam tung ban (tu print-report.json cua slice.py) vao metrics.json."""
    *_, out = cau_hinh(cfg_p)
    m = json.loads(out.read_text(encoding="utf-8"))
    m["plates"] = {b["ban"]: {"time_s": b["thoi_gian_s"], "grams": b["gam"], "support": b["support"]}
                   for b in print_report["ban"]}
    ghi(out, m)


def ban_git(out):
    """metrics.json o commit HEAD (None neu chua tung commit)."""
    r = subprocess.run(["git", "show", f"HEAD:./{out.name}"], cwd=out.parent, capture_output=True, text=True,
                       encoding="utf-8")
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


def _gio(s):
    return f"{int(s) // 3600}h{int(s) % 3600 // 60:02d}"


def so_sanh(cu, moi, components=()):
    """-> (trang_thai, tom_tat, dong[]). WARN: linh kien mua doi hinh dang, hoac so solid doi; INFO: co thay doi."""
    if cu is None:
        return "INFO", "chưa có mốc so (lần đầu) – commit metrics.json để làm mốc", []
    dong, canh_bao = [], []
    pc, pm = cu.get("parts", {}), moi.get("parts", {})
    for k in sorted(pm.keys() - pc.keys()):
        dong.append(f"+ {k} (mới, {pm[k]['volume_mm3']} mm³)")
    for k in sorted(pc.keys() - pm.keys()):
        dong.append(f"− {k} (đã xóa / đổi tên)")
    for k in sorted(pm.keys() & pc.keys()):
        a, b, ly = pc[k], pm[k], []
        dv = b["volume_mm3"] - a["volume_mm3"]
        if abs(dv) > V_TOL_MM3:
            ly.append(f"V {a['volume_mm3']} → {b['volume_mm3']} mm³ ({dv:+.1f})")
        dbb = max(abs(x - y) for x, y in zip(a["bbox_mm"], b["bbox_mm"]))
        dcm = max(abs(x - y) for x, y in zip(a["com_mm"], b["com_mm"]))
        if dbb > POS_TOL_MM or dcm > POS_TOL_MM:
            ly.append(f"hộp bao/trọng tâm lệch tới {max(dbb, dcm):.2f} mm")
        if a["solids"] != b["solids"]:
            ly.append(f"solid {a['solids']} → {b['solids']}")
            canh_bao.append(k)
        if ly:
            if abs(dv) > V_TOL_MM3 and any(fnmatch.fnmatch(k, g) for g in components):
                canh_bao.append(k)
            dong.append(f"{k}: " + ", ".join(ly))
    bc, bm = cu.get("plates", {}), moi.get("plates", {})
    for k in sorted(bm.keys() | bc.keys()):
        a, b = bc.get(k), bm.get(k)
        if a is None or b is None:
            dong.append(f"bàn {k}: {'mới' if a is None else 'bỏ'}")
        elif abs(a["time_s"] - b["time_s"]) > 60 or abs(a["grams"] - b["grams"]) > 0.5 or a["support"] != b["support"]:
            dong.append(f"bàn {k}: {_gio(a['time_s'])} → {_gio(b['time_s'])}, {a['grams']} → {b['grams']} g"
                        + (f", support {a['support']} → {b['support']}" if a["support"] != b["support"] else ""))
    if canh_bao:
        dong.insert(0, f"KIỂM LẠI (linh kiện mua đổi hình / số solid đổi): {', '.join(canh_bao)}")
    if not dong:
        return "PASS", "không đổi so với commit trước", []
    return ("WARN" if canh_bao else "INFO"), f"{len(dong)} thay đổi so với commit trước (git diff metrics.json)", dong


def main():
    if "--pass" in sys.argv:  # freecadcmd
        thu_thap(sys.argv[sys.argv.index("--pass") + 1])
        return 0
    if len(sys.argv) >= 3 and sys.argv[1] == "diff":
        sys.stdout.reconfigure(encoding="utf-8")
        _, cfg, _, _, out = cau_hinh(sys.argv[2])
        lk = next((x[11:].split(",") for x in cfg.get("check", []) if x.startswith("components=")), [])
        tt, tom, dong = so_sanh(ban_git(out), json.loads(out.read_text(encoding="utf-8")), lk)
        print(f"{tt}: {tom}")
        for d in dong:
            print(f"   - {d}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__" or "--pass" in sys.argv:  # freecadcmd chay script voi __name__ khac "__main__"
    code = main()
    if code:
        sys.exit(code)
