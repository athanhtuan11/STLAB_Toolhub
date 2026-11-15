"""Trang Robotics: doc manifest + thu muc du an (chi doc)."""
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path, PureWindowsPath

from . import workspace as ws

MANIFEST = Path(__file__).resolve().parent / "robotics.json"
COVER_FIXED = ["solidcraft/images/assembly/cover.png", "freecad/images/assembly/cover.png", "design/cover.png"]
COVER_GLOBS = ["print/plates/*/preview.png", "design/concepts/*-3-4.png", "design/concepts/*.png"]


def _path():
    return Path(os.environ.get("STLAB_ROBOTICS_MANIFEST") or MANIFEST)


def load():
    m = json.loads(_path().read_text(encoding="utf-8"))
    statuses = m.get("statuses", {})
    groups = m.get("groups", {})
    for p in m.get("projects", []):
        rel = p.get("rel", "")
        if p.get("status") not in statuses:
            raise ValueError(f"{rel}: tr\u1ea1ng th\u00e1i '{p.get('status')}' kh\u00f4ng c\u00f3 trong danh s\u00e1ch statuses")
        if not rel.startswith("maker/") or ".." in rel:
            raise ValueError(f"{rel}: \u0111\u01b0\u1eddng d\u1eabn ph\u1ea3i b\u1eaft \u0111\u1ea7u b\u1eb1ng maker/ v\u00e0 kh\u00f4ng ch\u1ee9a ..")
        if not (ws.ROOT / rel).is_dir():
            raise ValueError(f"{rel}: th\u01b0 m\u1ee5c d\u1ef1 \u00e1n kh\u00f4ng t\u1ed3n t\u1ea1i")
        grp = p.get("group")
        if grp not in groups:
            raise ValueError(f"{rel}: nh\u00f3m '{grp}' kh\u00f4ng c\u00f3 trong danh s\u00e1ch groups")
        folder = (ws.ROOT / rel).resolve()
        for key in ("guide", "wiring"):
            value = p.get(key)
            if not value:
                continue
            normalized = str(value).replace("\\", "/")
            windows_path = PureWindowsPath(normalized)
            if windows_path.is_absolute() or windows_path.drive or ".." in normalized.split("/"):
                raise ValueError(f"{rel}: '{key}' phải nằm trong thư mục dự án, không được chứa '..' hoặc đường dẫn tuyệt đối")
            target = (folder / normalized).resolve()
            if folder not in target.parents:
                raise ValueError(f"{rel}: '{key}' thoát khỏi thư mục dự án")
    return m


def slug_of(rel):
    return rel.replace("/", "--")


def project_dir(slug):
    for p in load().get("projects", []):
        if slug_of(p["rel"]) == slug:
            return (ws.ROOT / p["rel"]).resolve()
    return None


def sim_by_id(sim_id):
    return next((s for s in load().get("simulations", []) if s.get("id") == sim_id), None)


def sim_file(sim, key):
    rel = sim.get(key)
    if not rel:
        return None
    f = (ws.ROOT / rel).resolve()
    if ws.ROOT.resolve() not in f.parents or not f.is_file():
        return None
    return f


def _updated(rel, folder):
    try:
        r = subprocess.run(["git", "-C", str(ws.ROOT), "log", "-1", "--format=%cs", "--", rel],
                           capture_output=True, text=True, creationflags=ws.NO_WINDOW, timeout=10)
        out = r.stdout.strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", out):
            return out
    except (OSError, subprocess.SubprocessError):
        out = ""
    latest = 0.0
    for f in folder.rglob("*"):
        if f.is_file():
            latest = max(latest, f.stat().st_mtime)
    return datetime.fromtimestamp(latest or folder.stat().st_mtime).strftime("%Y-%m-%d")


def _cover(slug, folder, manifest_cover):
    cand = []
    if manifest_cover:
        cand.append(folder / manifest_cover)
    cand += [folder / c for c in COVER_FIXED]
    for g in COVER_GLOBS:
        cand += sorted(folder.glob(g), key=lambda x: x.as_posix())
    for f in cand:
        if f.is_file():
            return f"/robotics/img/{slug}/{f.relative_to(folder).as_posix()}"
    return ""


def data():
    m = load()
    statuses = m.get("statuses", {})
    groups = m.get("groups", {})
    projects = []
    for p in m.get("projects", []):
        rel = p["rel"]
        slug = slug_of(rel)
        folder = ws.ROOT / rel
        claude = folder / "CLAUDE.md"
        todo = 0
        if claude.is_file():
            todo = len(re.findall(r"\bTODO\b", claude.read_text(encoding="utf-8", errors="replace")))
        plates = (len(list(folder.glob("print/plates/*/*.3mf")))
                  + len(list(folder.glob("solidcraft/print/plates/*/*.3mf"))))
        name = rel.split("/")[-1]
        grp = p["group"]
        group_label = groups[grp]

        # guide_url: only if manifest has 'guide' AND file exists
        guide_rel = p.get("guide", "")
        if guide_rel and _project_file(folder, guide_rel).is_file():
            guide_url = f"/projects/{slug}/guide"
        else:
            guide_url = ""

        projects.append({
            "rel": rel, "slug": slug, "name": name, "title": p.get("title") or name,
            "summary": p.get("summary", ""), "audience": p.get("audience", ""), "status": p["status"],
            "status_label": statuses[p["status"]], "next": p.get("next", ""),
            "cover": _cover(slug, folder, p.get("cover")), "updated": _updated(rel, folder),
            "plates": plates, "assembly_pdf": (folder / "ASSEMBLY.pdf").is_file(),
            "bom": (folder / "BOM.md").is_file(), "todo": todo,
            "detail_url": f"/projects/{slug}" if claude.is_file() else "",
            "simulation": p.get("simulation", ""),
            # New fields
            "group": grp,
            "group_label": group_label,
            "works": bool(p.get("works", False)),
            "works_note": p.get("works_note", ""),
            "difficulty": p.get("difficulty", ""),
            "duration": p.get("duration", ""),
            "guide_url": guide_url,
        })
    sims = []
    for s in m.get("simulations", []):
        sid = s["id"]
        sims.append({
            "id": sid, "title": s.get("title", sid), "status": s.get("status", ""),
            "status_label": statuses.get(s.get("status", ""), ""), "note": s.get("note", ""),
            "links": s.get("links", []),
            "cover": f"/robotics/sim/{sid}/cover" if sim_file(s, "cover") else "",
            "readme_url": f"/robotics/sim/{sid}/readme" if sim_file(s, "readme") else "",
            "lesson_url": f"/robotics/sim/{sid}/lesson" if sim_file(s, "lesson") else "",
        })
    return {"statuses": statuses, "projects": projects, "simulations": sims, "groups": groups}


def _project_file(folder, relative):
    """Resolve a manifest path already validated by load()."""
    return (folder / str(relative).replace("\\", "/")).resolve()


def guide_info(slug):
    """Return (project_row, guide_path, wiring_path_or_None) for a project having a guide, else None."""
    row = next((p for p in data()["projects"] if p["slug"] == slug), None)
    if row is None or not row["guide_url"]:
        return None
    raw = next(p for p in load().get("projects", []) if slug_of(p["rel"]) == slug)
    folder = (ws.ROOT / raw["rel"]).resolve()
    guide = _project_file(folder, raw["guide"])
    wiring_rel = raw.get("wiring")
    wiring = _project_file(folder, wiring_rel) if wiring_rel else None
    if wiring is not None and not wiring.is_file():
        wiring = None
    return row, guide, wiring


def hub_projects():
    """Return manifest projects plus workspace projects not represented by the manifest."""
    d = data()
    rows = list(d["projects"])
    known = {p["rel"] for p in rows}
    for p in ws.projects():
        if p["rel"] in known:
            continue
        group = "khac" if p["rel"].startswith("maker/") else "tools"
        rows.append({
            "rel": p["rel"], "slug": p["slug"], "name": p["rel"].split("/")[-1],
            "title": p["title"], "summary": "", "audience": "", "status": "",
            "status_label": "", "next": "", "cover": "", "updated": "",
            "plates": 0, "assembly_pdf": False, "bom": False, "todo": p["todo"],
            "detail_url": f"/projects/{p['slug']}", "simulation": "", "group": group,
            "group_label": d["groups"][group], "works": False, "works_note": "",
            "difficulty": "", "duration": "", "guide_url": "",
        })
    return rows
