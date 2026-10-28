"""Doc trang thai workspace cho giao dien Toolhub (chi thu vien chuan).

Nguon du lieu: community/pins.tsv, community/links.tsv, community/reports/, cac CLAUDE.md,
tools/prompt-library. Chi DOC, tru run_check (chay update-community.sh check: chi bao cao).
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

from . import pin_diagram, pinout

STUDIO = Path(__file__).resolve().parent.parent
ROOT = STUDIO.parent
COMM = ROOT / "community"
WIN = os.name == "nt"
NO_WINDOW = subprocess.CREATE_NO_WINDOW if WIN else 0
PIN_FIELDS = ["name", "url", "type", "ref", "sha", "prev_sha", "allowlist", "auto", "license"]


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                       creationflags=NO_WINDOW)
    return r.stdout.strip()


def _tsv(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            yield line.split("\t")


def pins():
    rows = []
    for f in _tsv(COMM / "pins.tsv"):
        p = dict(zip(PIN_FIELDS, f))
        d = COMM / p["name"]
        p["cloned"] = (d / ".git").exists()
        p["head"] = _git(d, "rev-parse", "HEAD") if p["cloned"] else ""
        p["clean"] = p["cloned"] and _git(d, "status", "--porcelain") == ""
        p["ok"] = p["cloned"] and p["clean"] and p["head"] == p["sha"]
        p["web"] = p["url"].removesuffix(".git")
        rows.append(p)
    return rows


def _resolve_dest(dest):
    return Path.home() / dest[2:] if dest.startswith("~/") else ROOT / dest


def links():
    rows = []
    for dest, src in _tsv(COMM / "links.tsv"):
        p = _resolve_dest(dest)
        if "/agents/" in dest:
            kind = "agent"
        elif "/skills/" in dest:
            kind = "skill"
        else:
            kind = "addon"
        if dest.startswith("~/.claude/"):
            scope = "Dùng chung (~/.claude)"
        elif dest.startswith("~/"):
            scope = "Addon ứng dụng"
        else:
            scope = dest.split("/.claude/")[0]
        parts = src.split("/")
        origin = parts[1] if parts[0] == "community" else "tự viết (custom)"
        rows.append({"dest": dest, "src": src, "name": Path(dest).name, "kind": kind, "scope": scope,
                     "origin": origin, "ok": p.is_symlink() and p.exists()})
    return rows


def _project_dirs():
    dirs = [ROOT / "stlab", ROOT / "studio"]
    dirs += sorted(d for d in (ROOT / "maker").iterdir() if d.is_dir())
    dirs += sorted(d for d in (ROOT / "tools").iterdir() if d.is_dir())  # cong cu dung chung (robotics-cad, prompt-library)
    return [d for d in dirs if (d / "CLAUDE.md").exists()]


def projects():
    lk = links()
    out = []
    for d in _project_dirs():
        rel = d.relative_to(ROOT).as_posix()
        text = (d / "CLAUDE.md").read_text(encoding="utf-8")
        title = next((ln.lstrip("# ").strip() for ln in text.splitlines() if ln.startswith("# ")), rel)
        mcp = []
        if (d / ".mcp.json").exists():
            import json
            mcp = list(json.loads((d / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"])
        out.append({
            "rel": rel, "slug": rel.replace("/", "--"), "title": title, "claude_md": text,
            "todo": len(re.findall(r"\bTODO\b", text)),
            "links": [x for x in lk if x["scope"] == rel], "mcp": mcp,
        })
    return out


def project(slug):
    return next((p for p in projects() if p["slug"] == slug), None)


def reports():
    d = COMM / "reports"
    return sorted((p.name for p in d.glob("*.md")), reverse=True) if d.exists() else []


def report(name):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", name):
        return None
    p = COMM / "reports" / name
    return p.read_text(encoding="utf-8") if p.exists() else None


def _bash():
    for c in (shutil.which("bash"), r"C:\Program Files\Git\bin\bash.exe"):
        if c and Path(c).exists():
            return c
    return None


def run_check(name=None):
    """Chay `update-community.sh check [ten]` (CHI BAO CAO, khong doi diem ghim)."""
    bash = _bash()
    if not bash:
        return {"ok": False, "msg": "Không tìm thấy Git Bash"}
    known = {p["name"] for p in pins()}
    if name and name not in known:
        return {"ok": False, "msg": f"Không có repo '{name}'"}
    args = [bash, str(COMM / "update-community.sh"), "check"] + ([name] if name else [])
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT),
                       creationflags=NO_WINDOW, timeout=900)
    changed = len(re.findall(r"^## .+ -> ", r.stdout, flags=re.M))
    ok = r.returncode == 0
    msg = (f"Đã kiểm tra{' ' + name if name else ' tất cả'}: {changed} repo có bản mới. Xem báo cáo hôm nay."
           if ok else f"Lỗi khi kiểm tra: {(r.stderr or r.stdout)[-300:]}")
    return {"ok": ok, "msg": msg}


def prompts():
    base = ROOT / "tools" / "prompt-library"
    rows = []
    for app in ("freecad", "blender"):
        for p in sorted((base / app).glob("*.md")):
            rows.append({"app": app, "name": p.stem, "rel": p.relative_to(ROOT).as_posix()})
    return rows


LIBRARY_YAML = ROOT / "tools" / "robotics-cad" / "library" / "components.yaml"
LIBRARY_DIR = LIBRARY_YAML.parent


LABELS = {
    'kich_thuoc_mm': 'Kích thước (mm)', 'khoi_luong_g': 'Khối lượng (g)', 'dien_ap_v': 'Điện áp (V)',
    'momen_stall_kgf_cm': 'Mô-men stall (kgf·cm)', 'toc_do': 'Tốc độ', 'mat_bich_mm': 'Mặt bích (mm)',
    'goc_buoc_deg': 'Góc bước (°)', 'buoc_moi_vong': 'Bước/vòng', 'dong_dinh_muc_a': 'Dòng định mức (A)',
    'momen_giu_n_cm': 'Mô-men giữ (N·cm)', 'dien_tro_pha_ohm': 'Điện trở pha (Ω)', 'truc_mm': 'Trục (mm)',
    'muc_logic_v': 'Mức logic (V)', 'ghi_chu': 'Ghi chú', 'bo_mach_mm': 'Bo mạch (mm)', 'lo_bat': 'Lỗ bắt',
    'dong_lam_viec_ma': 'Dòng làm việc (mA)', 'tam_do_cm': 'Tầm đo (cm)', 'goc_do_deg': 'Góc đo (°)',
    'tan_so_khz': 'Tần số (kHz)', 'dien_ap_toi_da_v': 'Điện áp tối đa (V)', 'dong_tong_a': 'Dòng tổng (A)',
    'trong_mm': 'Đường kính trong (mm)', 'ngoai_mm': 'Đường kính ngoài (mm)', 'day_mm': 'Bề dày (mm)',
    'spline': 'Spline / horn', 'ghi_chu_pg002': 'Ghi chú PG002', 'go_dinh_tam_mm': 'Gờ định tâm (mm)',
    'dien_cam_mh': 'Điện cảm pha (mH)', 'chieu_cao_mm': 'Chiều cao cổng (mm)', 'vai_truc_da_min_mm': 'Vai trục da min (mm)',
    'vai_lo_Da_max_mm': 'Vai lỗ Da max (mm)', 'dung_luong_mah': 'Dung lượng (mAh)', 'dong_toi_da_a': 'Dòng tối đa (A)',
    'gpio_ma': 'Dòng mỗi GPIO (mA)', 'tiep_diem': 'Tiếp điểm', 'cuon_day_v': 'Cuộn dây (V)',
    'relay': 'Relay', 'chan': 'Chân'}

THUMB_MAX = 60


def _enrich(c, roots, lib_root):
    root = roots.get(c.get("thu_vien"), lib_root)
    c["model_ok"] = bool(c.get("model")) and (root / c["model"]).exists()
    c["stl_ok"] = bool(c.get("stl")) and (root / c["stl"]).exists()
    c["thong_so"] = c.get("thong_so") or {}
    c["todo"] = c.get("todo") or []
    c["nguon"] = c.get("nguon") or []
    return c


def _load():
    import yaml
    data = yaml.safe_load(LIBRARY_YAML.read_text(encoding="utf-8")) if LIBRARY_YAML.exists() else {}
    lib_root = ROOT / data.get("library_root", "community/freecad-library")
    # Nhieu nguon model: thu_vien: <ten> -> library_roots[<ten>]; khong ghi -> library_root
    roots = {k: ROOT / v for k, v in (data.get("library_roots") or {}).items()}
    comps = [_enrich(c, roots, lib_root) for c in data.get("components", [])]
    return data, comps, lib_root, roots


def _key_specs(thong_so):
    out = []
    for k, v in list(thong_so.items())[:3]:
        s = str(v)
        if len(s) > THUMB_MAX:
            s = s[:THUMB_MAX] + "…"
        out.append((LABELS.get(k, k.replace("_", " ")), s))
    return out


def _pinout(c):
    rows = []
    if c.get("anh_chan"):
        svg = pin_diagram.photo_svg(c)
        if svg:
            rows.append({"title": "S\u01a1 \u0111\u1ed3 ch\u00e2n", "svg": svg})
        for sd in c.get("so_do") or []:
            wiring = pin_diagram.wiring_svg(c, sd)
            if not wiring:
                continue
            du_an = sd.get("du_an") or ""
            tieu_de = sd.get("tieu_de") or ""
            title = ("\u0110\u1ea5u cho %s: %s" % (du_an, tieu_de) if du_an
                     else "\u0110\u1ea5u cho %s" % tieu_de)
            rows.append({"title": title, "svg": wiring})
    elif c.get("chan"):
        rows.append({"title": "S\u01a1 \u0111\u1ed3 ch\u00e2n",
                     "svg": pinout.render_svg(c.get("ten", ""), c["chan"])})
        for sd in c.get("so_do") or []:
            rows.append({
                "title": "\u0110\u1ea5u cho %s" % (sd.get("du_an") or ""),
                "svg": pinout.render_svg(c.get("ten", ""), c["chan"], sd),
            })
        rows = [p for p in rows if p["svg"]]
    return rows


def _stats(lib_root, roots):
    stats = {"step": 0, "fcstd": 0, "stl": 0}
    for r in {lib_root, *roots.values()}:
        if not r.exists():
            continue
        for _dir, _sub, files in os.walk(r):
            if ".git" in _dir:
                continue
            for f in files:
                ext = f.lower().rsplit(".", 1)[-1]
                if ext in ("step", "stp"):
                    stats["step"] += 1
                elif ext == "fcstd":
                    stats["fcstd"] += 1
                elif ext == "stl":
                    stats["stl"] += 1
    return stats


def library():
    """Danh sach gon: ten + thong tin co ban; khong ve so do (xem library_item)."""
    data, comps, lib_root, roots = _load()
    for c in comps:
        anh_chan = c.get("anh_chan") or {}
        c["has_pinout"] = bool(c.get("chan"))
        c["thumb"] = "/library/img/" + anh_chan["file"] if anh_chan.get("file") else ""
        c["todo_count"] = len(c["todo"])
        c["key_specs"] = _key_specs(c["thong_so"])
    return {"components": comps, "updated": data.get("cap_nhat", ""), "stats": _stats(lib_root, roots),
            "types": sorted({c.get("loai", "") for c in comps}), "root": str(lib_root)}


def library_item(cid):
    """Mot linh kien day du (co so do chan/dau) hoac None."""
    _data, comps, _lib_root, _roots = _load()
    c = next((x for x in comps if x.get("id") == cid), None)
    if c is None:
        return None
    c["pinout"] = _pinout(c)
    return c


def open_in_vscode(slug):
    """Chi mo thu muc du an da biet (khong nhan duong dan tu do tu web)."""
    p = project(slug)
    target = ROOT if slug == "_root" else (ROOT / p["rel"] if p else None)
    if target is None:
        return {"ok": False, "msg": "Không có dự án này"}
    subprocess.Popen(["cmd", "/c", "code", str(target)], creationflags=NO_WINDOW)
    return {"ok": True, "msg": f"Đã mở VS Code tại {target}"}
