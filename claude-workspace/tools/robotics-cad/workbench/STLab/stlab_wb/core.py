"""Phan KHONG giao dien cua workbench STLab: duong dan, du an (print.yaml), phan loai Label, ket qua tung buoc.

Test duoc bang freecadcmd (khong can Qt). Logic phan loai dung lai cua scripts/bom.py + export-stl.py
de workbench va pipeline CLI khong lech nhau.
"""

import fnmatch
import json
import re
import shutil
import sys
from pathlib import Path

import FreeCAD as App
import yaml

WB = Path(__file__).resolve().parents[1]      # workbench/STLab (resolve: di qua junction trong Mod/)
RCAD = WB.parents[1]                           # tools/robotics-cad
SCRIPTS = RCAD / "scripts"
MAKER = RCAD.parent
WS = MAKER.parent                              # claude-workspace
TEMPLATE = RCAD / "project-template"
CATALOG = RCAD / "library" / "components.yaml"
TOKENS = WS / "studio" / "design" / "tokens.json"   # mau/chu dung chung voi Toolhub (studio/design/DESIGN.md)
ICONS = WB / "stlab_wb" / "icons"
BIN = Path(App.getHomePath()) / "bin"
FCC = BIN / "freecadcmd.exe"
PY = BIN / "python.exe"
BAMBU = Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")
BED_MM = (256.0, 256.0, 256.0)                 # Bambu A1: 256 x 256 x 256 mm (trang san pham Bambu Lab)

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

NAME_OK = re.compile(r"^[A-Za-z0-9_.\-]+$")
PROJECT_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def tokens():
    return json.loads(TOKENS.read_text(encoding="utf-8"))


def icon(name):
    return str(ICONS / f"{name}.svg")


# ---------------------------------------------------------------- du an

class Project:
    """1 du an maker/<name>/ co print/print.yaml (cau truc chuan: robotics-cad/CLAUDE.md muc "Du an")."""

    def __init__(self, cfg_p):
        self.cfg_p = Path(cfg_p).resolve()
        self.dir = self.cfg_p.parents[1]
        self.name = self.dir.name
        self.reload()

    def reload(self):
        self.cfg = yaml.safe_load(self.cfg_p.read_text(encoding="utf-8")) or {}
        self.root = (self.cfg_p.parent / self.cfg.get("data_dir", ".")).resolve()
        self.fcstd = (self.root / self.cfg.get("fcstd", "")).resolve()
        self.stl_dir = (self.root / self.cfg.get("stl", "stl")).resolve()
        self.plates_dir = (self.root / self.cfg.get("plates_dir", "plates")).resolve()

    # tham so check.py: out=<tuong doi> -> tuyet doi (giong prepare-print.py)
    def check_args(self):
        return [f"out={(self.root / x[4:]).resolve()}" if x.startswith("out=") else x
                for x in self.cfg.get("check", [])]

    def check_dir(self):
        return next((Path(x[4:]) for x in self.check_args() if x.startswith("out=")),
                    self.fcstd.parent / "check" / self.fcstd.stem)

    def components(self):
        return [g.strip() for x in self.cfg.get("check", []) if x.startswith("components=")
                for g in x[11:].split(",") if g.strip()]

    def rule_for(self, label):
        return next((q for q in (self.cfg.get("export") or {}).get("rules", [])
                     if any(fnmatch.fnmatch(label, g) for g in q["names"])), None)

    def is_open(self):
        return next((d for d in App.listDocuments().values()
                     if d.FileName and Path(d.FileName).resolve() == self.fcstd), None)

    def results(self):
        """Trang thai tung buoc tu file ket qua -> {buoc: (ket_luan, tom_tat, anh)}."""
        r = {}
        rp = self.check_dir() / "report.json"
        if rp.exists():
            b = _json(rp)
            if b:
                r["check"] = (b.get("ket_luan", "?"), f"{b.get('thoi_gian', '')}, {b.get('thoi_gian_chay_s', '?')} s",
                              str(self.check_dir() / "overview.png"))
        ep = self.stl_dir / "_export-stl.json"
        if ep.exists():
            b = _json(ep)
            if b:
                kk = b.get("quy_tac_khong_khop") or []
                r["export"] = ("WARN" if kk else "PASS",
                               f"{b.get('so_stl', 0)} STL" + (f", {len(kk)} quy tắc không khớp" if kk else ""), "")
        sp = self.plates_dir / "print-report.json"
        if sp.exists():
            b = _json(sp)
            if b:
                r["slice"] = (b.get("ket_luan", "?"),
                              f"in {b.get('tong_thoi_gian_in', '?')}, {b.get('tong_gam', '?')} g",
                              str(self.plates_dir / "print-overview.png"))
        pp = self.cfg_p.parent / "_prepare-print-result.json"
        if pp.exists():
            b = _json(pp)
            if b:
                tt = [t["ket_luan"] for t in b.get("tang", [])]
                kl = "FAIL" if "FAIL" in tt else ("WARN" if "WARN" in tt else "PASS")
                r["prepare"] = (kl, f"{b.get('thoi_gian', '')}, {b.get('tong_s', '?')} s", "")
        bp = self.cfg_p.parent / "_bom.json"
        if bp.exists():
            b = _json(bp)
            if b:
                r["bom"] = ("WARN" if b.get("lech_assembly") or b.get("chua_phan_loai") else "PASS",
                            f"{b.get('chi_tiet_in', 0)} chi tiết in, {b.get('linh_kien_mua', 0)} linh kiện mua", "")
        return r

    def plates(self):
        return sorted(self.plates_dir.glob("*/*.3mf"))


def _json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def list_projects():
    return [Project(p) for p in sorted(MAKER.glob("*/print/print.yaml")) if p.parents[1] != RCAD]


def project_for_doc(doc):
    if doc is None or not doc.FileName:
        return None
    f = Path(doc.FileName).resolve()
    return next((p for p in list_projects() if p.fcstd == f), None)


def new_project(name, desc, create_model=True):
    """Chep project-template -> maker/<name>/ (giong lenh /new-project). Tra ve Project. Khong ghi de."""
    if not PROJECT_NAME.match(name):
        raise ValueError("Tên dự án: tiếng Anh, chữ thường, kebab-case (vd. line-follower)")
    d = MAKER / name
    if d.exists():
        raise FileExistsError(f"{d} đã tồn tại – không ghi đè")
    model = name.replace("-", "_")
    shutil.copytree(TEMPLATE, d)
    for f in (d / "CLAUDE.md", d / "README.md", d / "print" / "print.yaml"):
        if f.exists():
            t = f.read_text(encoding="utf-8")
            t = t.replace("<project-name>", name).replace("<model>", model).replace("<mô tả 1 dòng>", desc or "TODO")
            f.write_text(t, encoding="utf-8")
    for sub in ("freecad/scripts", "freecad/images"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    p = Project(d / "print" / "print.yaml")
    if create_model and not p.fcstd.exists():
        doc = App.newDocument(model)
        doc.saveAs(str(p.fcstd))
    return p


# ---------------------------------------------------------------- Label

def parts(doc):
    """Chi tiet "la" giong metrics.py: Part::Feature co solid, dang hien, khong lam dau vao cho feature khac."""
    out = []
    for o in doc.Objects:
        if (not o.isDerivedFrom("Part::Feature") or not getattr(o, "Visibility", True)
                or any(p.isDerivedFrom("Part::Feature") for p in o.InList)):
            continue
        try:
            if not o.Shape.Solids:
                continue
        except Exception:
            continue
        out.append(o)
    return out


def classify(label, project):
    """-> (loai, chi_tiet, canh_bao). Thu tu nhu bom.py: vit > linh kien mua > chi tiet in > chua phan loai."""
    import bom
    canh = []
    if not NAME_OK.match(label):
        canh.append("tên có dấu/khoảng trắng")
    v = bom.co_vit(label)
    if v:
        return "vít", v[0], canh
    if project and any(fnmatch.fnmatch(label, g) for g in project.components()):
        return "linh kiện mua", "", canh
    if project:
        q = project.rule_for(label)
        if q:
            b = bom.ban_in(label, project.cfg)
            rot = ", ".join(f"{k} {v}°" for k, v in (q.get("rotate") or {}).items()) or "giữ hướng"
            return "in 3D", f"{q['group']} · {rot} · {b[0] if b else '?'}", canh
    canh.append("chưa phân loại: đổi Label hoặc thêm vào print.yaml")
    return "chưa phân loại", "", canh


# ---------------------------------------------------------------- huong in (giong export-stl.py)

def _frame(spec, objs):
    V = App.Vector
    if spec is None:
        return App.Placement()
    if isinstance(spec, str):
        return App.Placement(objs[spec].Placement)
    x, y, z, ax, ay, az, goc = spec
    return App.Placement(V(x, y, z), App.Rotation(V(ax, ay, az), goc))


def _rotate(spec):
    V = App.Vector
    p = App.Placement()
    for truc, goc in (spec or {}).items():
        p = App.Placement(V(), App.Rotation({"x": V(1, 0, 0), "y": V(0, 1, 0), "z": V(0, 0, 1)}[truc], goc)).multiply(p)
    return p


def print_shape(obj, project):
    """Shape cua chi tiet theo HUONG IN (quy tac export dau tien khop), dat giua ban, day Z = 0. None neu khong xuat."""
    q = project.rule_for(obj.Label) if project else None
    if q is None:
        return None, None
    objs = {o.Label: o for o in obj.Document.Objects if o.isDerivedFrom("Part::Feature")}
    s = obj.Shape.copy()
    s.Placement = _rotate(q.get("rotate")).multiply(_frame(q.get("frame"), objs).inverse()).multiply(s.Placement)
    bb = s.BoundBox
    s.translate(App.Vector(-bb.Center.x, -bb.Center.y, -bb.ZMin))
    return s, q


def backup(doc, note):
    import safe_edit
    note = re.sub(r"[^A-Za-z0-9_-]+", "-", note).strip("-") or "manual"
    return safe_edit.backup(doc, note)
