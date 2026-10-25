"""BOM tu Label trong model: BOM.csv + BOM.md canh print/ (thu muc du an) va kiem bang vit trong ASSEMBLY.md.

Chay (Python thuong, sau metrics.py; prepare-print.py goi tu dong):
    python scripts/bom.py <project>/print/print.yaml
Doc: freecad/metrics.json (Label, the tich, so solid) + print.yaml (`check: components=` = linh kien mua,
`export.rules` + `plates` = chi tiet in o ban nao, nhua gi). Quy uoc Label (robotics-cad/CLAUDE.md):
    vit: chua M<d>[_<d>]x<L> (M2_5x6_turret001, Pin_S_M2_5x6)  -> dem theo co "M2.5 × 6"
    linh kien mua: khop `components=` (CB_*, LK_*, ...)         -> gop ten bo hau to 001/002
    chi tiet in: khop `export.rules`                           -> ban in + nhua tu `plates`
    con lai -> "Chua phan loai" (TODO: dat lai Label hoac them vao print.yaml)
ASSEMBLY.md: bang co dong "| M2.5 × 6 | 21 | ..." -> so SL voi model, lech thi bao (KHONG tu sua file viet tay).
"""

import csv
import fnmatch
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metrics  # noqa: E402

VIT = re.compile(r"(?:^|_)M(\d+)(?:_(\d+))?x(\d+)(?=_|$|\d{3}$)")


def co_vit(label):
    m = VIT.search(label)
    if not m:
        return None
    d = m.group(1) + (f".{m.group(2)}" if m.group(2) else "")
    return f"M{d} × {m.group(3)}", (label[:m.start()] + label[m.end():]).strip("_")


def goc_ten(label, tat_ca=()):
    """Bo hau to trung ten cua FreeCAD (Spacer_S001 -> Spacer_S) CHI KHI ten goc cung co trong model
    (khong cat ma linh kien: CB_Battery_PC003, CB_Switch_XA007)."""
    g = re.sub(r"\d{3}$", "", label).rstrip("_")
    return g if (not tat_ca or g in tat_ca) else label


def ban_in(label, cfg):
    """(ban, nhua) cua chi tiet in, theo quy tac xuat STL dau tien khop + glob STL cua ban."""
    x = cfg.get("export", {})
    qt = next((q for q in x.get("rules", []) if any(fnmatch.fnmatch(label, g) for g in q["names"])), None)
    if qt is None:
        return None
    ten = f"{qt['group']}__{label}{qt.get('suffix', '')}.stl"
    ten_tach = f"{qt['group']}__{label}_1{qt.get('suffix', '')}.stl"  # split_solids -> <Label>_1.stl ...
    for b, p in (cfg.get("plates") or {}).items():
        for f in (ten, ten_tach):
            if any(fnmatch.fnmatch(f, g) for g in p.get("stl", [])) and not any(
                    fnmatch.fnmatch(f, g) for g in p.get("exclude", [])):
                return b, p.get("filament", cfg.get("filament", "TODO"))
    return "(chưa xếp bàn)", cfg.get("filament", "TODO")


def lap(cfg_p):
    cfg_p, cfg, _, _, f_m = metrics.cau_hinh(cfg_p)
    m = json.loads(f_m.read_text(encoding="utf-8"))
    lk = next((x[11:].split(",") for x in cfg.get("check", []) if x.startswith("components=")), [])
    nhom = cfg.get("bom_groups") or {}   # {glob Label: ten hien thi} - gop vd. 4 lop, 8 nam cham
    tat_ca = set(m["parts"])
    vit, vit_o = Counter(), defaultdict(Counter)
    mua, in3d, chua = Counter(), [], []
    for label, p in m["parts"].items():
        v = co_vit(label)
        if v:
            vit[v[0]] += 1
            vit_o[v[0]][goc_ten(v[1]) or "?"] += 1  # vi tri dung: gop truot001 -> truot
        elif any(fnmatch.fnmatch(label, g.strip()) for g in lk if g.strip()):
            mua[next((ten for g, ten in nhom.items() if fnmatch.fnmatch(label, g)), goc_ten(label, tat_ca))] += 1
        else:
            b = ban_in(label, cfg)
            if b:
                in3d.append((label, *b, p["solids"], p["volume_mm3"]))
            else:
                chua.append(label)
    return cfg_p, cfg, m, vit, vit_o, mua, sorted(in3d, key=lambda r: (r[1], r[0])), chua


def kiem_assembly(f, vit):
    """So SL vit trong bang ASSEMBLY.md voi model -> danh sach lech."""
    if not f.exists():
        return []
    ghi = {}
    for d in f.read_text(encoding="utf-8").splitlines():
        r = re.match(r"^\|\s*(M[\d.]+)\s*[×x]\s*(\d+)\s*\|\s*(\d+)\s*\|", d)
        if r:
            ghi[f"{r.group(1)} × {r.group(2)}"] = int(r.group(3))
    if not ghi:
        return []
    return [f"{k}: ASSEMBLY.md ghi {ghi.get(k, 0)}, model có {vit.get(k, 0)}"
            for k in sorted(ghi.keys() | vit.keys()) if ghi.get(k, 0) != vit.get(k, 0)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cfg_p, cfg, m, vit, vit_o, mua, in3d, chua = lap(sys.argv[1])
    du_an = cfg_p.parent.parent
    rows = [("Loai", "Ten", "SL", "Ban in", "Nhua", "Ghi chu")]
    rows += [("vit", k, n, "", "", ", ".join(f"{u} {c}" for u, c in sorted(vit_o[k].items())))
             for k, n in sorted(vit.items())]
    rows += [("linh kien mua", k, n, "", "", "") for k, n in sorted(mua.items())]
    rows += [("in 3D", lb, 1, b, nh, f"{s} miếng; {v / 1000:.2f} cm³" if s > 1 else f"{v / 1000:.2f} cm³")
             for lb, b, nh, s, v in in3d]
    rows += [("chua phan loai", lb, 1, "", "", "TODO: đặt lại Label hoặc thêm vào print.yaml") for lb in chua]
    with open(du_an / "BOM.csv", "w", encoding="utf-8-sig", newline="") as fh:  # utf-8-sig: Excel doc dung dau
        csv.writer(fh).writerows(rows)

    md = [f"# BOM – {du_an.name}", "",
          f"Sinh tự động từ `freecad/{m['fcstd']}` bằng `tools/robotics-cad/scripts/bom.py` – **không sửa tay** "
          "(sửa Label trong model rồi chạy lại *Chuẩn bị in*).", ""]
    md += ["## Vít", "| Vít | SL | Dùng ở |", "|---|---|---|"]
    md += [f"| {k} | {n} | {', '.join(f'{u} {c}' for u, c in sorted(vit_o[k].items()))} |"
           for k, n in sorted(vit.items())]
    md += ["", "## Linh kiện mua", "| Tên (Label) | SL |", "|---|---|"]
    md += [f"| `{k}` | {n} |" for k, n in sorted(mua.items())]
    pl = m.get("plates", {})
    md += ["", "## Chi tiết in 3D", "| Chi tiết | Bàn in | Nhựa | Thể tích (cm³) |", "|---|---|---|---|"]
    md += [f"| `{lb}`{f' ({s} miếng)' if s > 1 else ''} | {b} | {nh} | {v / 1000:.2f} |" for lb, b, nh, s, v in in3d]
    if pl:
        md += ["", "## Bàn in (số liệu slicer)", "| Bàn | Thời gian | Nhựa (g) | Support |", "|---|---|---|---|"]
        md += [f"| {k} | {metrics._gio(v['time_s'])} | {v['grams']} | {'có' if v['support'] else '–'} |"
               for k, v in sorted(pl.items())]
        md += [f"| **Tổng** | **{metrics._gio(sum(v['time_s'] for v in pl.values()))}** | "
               f"**{round(sum(v['grams'] for v in pl.values()), 1)}** | |"]
    if chua:
        md += ["", "## Chưa phân loại (TODO)", "Label không khớp quy ước vít / `components=` / `export.rules`:", ""]
        md += [f"- `{lb}`" for lb in chua]
    (du_an / "BOM.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    lech = kiem_assembly(du_an / "ASSEMBLY.md", vit)
    kq = {"vit": dict(sorted(vit.items())), "linh_kien_mua": sum(mua.values()), "chi_tiet_in": len(in3d),
          "chua_phan_loai": chua, "lech_assembly": lech}
    (cfg_p.parent / "_bom.json").write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")
    print("BOM", json.dumps(kq, ensure_ascii=False))


if __name__ == "__main__":
    main()
