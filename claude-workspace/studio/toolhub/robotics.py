"""Trang Robotics: doc manifest + thu muc du an (chi doc)."""
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

from . import workspace as ws

MANIFEST = Path(__file__).resolve().parent / "robotics.json"
COVER_FIXED = ["solidcraft/images/assembly/cover.png", "freecad/images/assembly/cover.png", "design/cover.png"]
COVER_GLOBS = ["print/plates/*/preview.png", "design/concepts/*-3-4.png", "design/concepts/*.png"]


def _path():
    return Path(os.environ.get("STLAB_ROBOTICS_MANIFEST") or MANIFEST)


def load():
    m = json.loads(_path().read_text(encoding="utf-8"))
    statuses = m.get("statuses", {})
    for p in m.get("projects", []):
        rel = p.get("rel", "")
        if p.get("status") not in statuses:
            raise ValueError(f"{rel}: trạng thái '{p.get('status')}' không có trong danh sách statuses")
        if not rel.startswith("maker/") or ".." in rel:
            raise ValueError(f"{rel}: đường dẫn phải bắt đầu bằng maker/ và không chứa ..")
        if not (ws.ROOT / rel).is_dir():
            raise ValueError(f"{rel}: thư mục dự án không tồn tại")
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
        projects.append({
            "rel": rel, "slug": slug, "name": name, "title": p.get("title") or name,
            "summary": p.get("summary", ""), "audience": p.get("audience", ""), "status": p["status"],
            "status_label": statuses[p["status"]], "next": p.get("next", ""),
            "cover": _cover(slug, folder, p.get("cover")), "updated": _updated(rel, folder),
            "plates": plates, "assembly_pdf": (folder / "ASSEMBLY.pdf").is_file(),
            "bom": (folder / "BOM.md").is_file(), "todo": todo,
            "detail_url": f"/projects/{slug}" if claude.is_file() else "",
            "simulation": p.get("simulation", ""),
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
    return {"statuses": statuses, "projects": projects, "simulations": sims}
