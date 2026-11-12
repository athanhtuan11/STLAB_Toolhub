"""Discover printable plates and their project CAD files."""
import json
import os
from pathlib import Path

from .workspace import ROOT

SKIP_DIRS = {"backup", ".venv", "venv", "env", "node_modules", ".git", "__pycache__", "build"}
MAX_DEPTH = 4
_cache_signature = None
_cache_prints = []


def _included_dirs(dirs):
    dirs[:] = [name for name in dirs if name not in SKIP_DIRS and not name.startswith("_")]


def _walk(root):
    for current, dirs, names in os.walk(root):
        relative = Path(current).relative_to(root)
        depth = len(relative.parts)
        _included_dirs(dirs)
        if depth >= MAX_DEPTH:
            dirs[:] = []
        yield Path(current), names


def _signature(roots):
    signature = []
    for root in roots:
        if not root.is_dir():
            signature.append((str(root), None))
            continue
        for current, dirs, _names in os.walk(root):
            relative = Path(current).relative_to(root)
            depth = len(relative.parts)
            _included_dirs(dirs)
            try:
                stat = Path(current).stat()
            except OSError:
                continue
            signature.append((str(current), stat.st_mtime_ns))
            if depth >= MAX_DEPTH:
                dirs[:] = []
    return tuple(signature)


def _title(directory):
    readme = directory / "README.md"
    if not readme.is_file():
        return ""
    try:
        return next((line[2:].strip() for line in readme.read_text(encoding="utf-8").splitlines()
                     if line.startswith("# ")), "")
    except OSError:
        return ""


def _stats_from_3mf(plate_dir):
    """Du phong khi khong co result.json: doc Metadata/slice_info.config trong <ban>.3mf (prediction s, weight g)."""
    import re
    import zipfile
    try:
        with zipfile.ZipFile(plate_dir / f"{plate_dir.name}.3mf") as z:
            txt = z.read("Metadata/slice_info.config").decode("utf-8", "replace")
    except (OSError, KeyError, zipfile.BadZipFile):
        return None, None
    sec = [float(x) for x in re.findall(r'key="prediction" value="([\d.]+)"', txt)]
    gr = [float(x) for x in re.findall(r'key="weight" value="([\d.]+)"', txt)]
    return (round(sum(sec) / 60) if sec else None), (round(sum(gr), 1) if gr else None)


def _slice_stats(plate_dir):
    result = plate_dir / "result.json"
    if not result.is_file():
        return _stats_from_3mf(plate_dir)
    try:
        data = json.loads(result.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None
    sliced = data.get("sliced_plates") or []
    seconds = []
    grams = []
    for plate in sliced:
        if not isinstance(plate, dict):
            continue
        prediction = plate.get("total_predication", plate.get("prediction"))   # Bambu CLI ghi sai chinh ta "predication"
        if isinstance(prediction, (int, float)):
            seconds.append(float(prediction))
        for filament in plate.get("filaments") or []:
            if isinstance(filament, dict):
                amount = filament.get("total_used_g")
                if isinstance(amount, (int, float)):
                    grams.append(float(amount))
    if not seconds and isinstance(data.get("prediction"), (int, float)):
        seconds.append(float(data["prediction"]))
    if not grams:
        for filament in data.get("filaments") or []:
            if isinstance(filament, dict) and isinstance(filament.get("total_used_g"), (int, float)):
                grams.append(float(filament["total_used_g"]))
    minutes = round(sum(seconds) / 60) if seconds else None
    total_grams = round(sum(grams), 1) if grams else None
    return minutes, total_grams


def _cad_files(project_dir):
    files = []
    for current, names in _walk(project_dir):
        names.sort()
        for name in names:
            path = Path(current) / name
            suffix = path.suffix.lower()
            if suffix not in (".sc", ".fcstd"):
                continue
            files.append((0 if suffix == ".sc" else 1, path.relative_to(ROOT).as_posix()))
    files.sort()
    return [rel for _rank, rel in files]


def _root_records(root, source, folder_prefix):
    if not root.is_dir():
        return []
    rows = []
    for project_dir in sorted(root.iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("_") or project_dir.name in SKIP_DIRS:
            continue
        for current, names in _walk(project_dir):
            names.sort()
            plate_parent = Path(current)
            if plate_parent.name != "plates":
                continue
            for plate_name in sorted(p.name for p in plate_parent.iterdir() if p.is_dir()):   # ban in = thu muc con
                if plate_name.startswith("_"):
                    continue
                plate_dir = plate_parent / plate_name
                if not plate_dir.is_dir():
                    continue
                model = plate_dir / f"{plate_name}.3mf"
                if not model.is_file():
                    continue
                try:
                    mtime = model.stat().st_mtime
                except OSError:
                    continue
                image = next((plate_dir / candidate for candidate in ("preview.png", "plate_1.png")
                              if (plate_dir / candidate).is_file()), None)
                minutes, grams = _slice_stats(plate_dir)
                relative_folder = (Path(folder_prefix) / project_dir.name).as_posix()
                rows.append({
                    "project": project_dir.name,
                    "plate": plate_name,
                    "title": _title(project_dir),
                    "minutes": minutes,
                    "grams": grams,
                    "image_url": f"/prints/img/{project_dir.name}/{plate_name}" if image else None,
                    "mtime": mtime,
                    "cad": _cad_files(project_dir),
                    "source": source,
                    "folder": relative_folder,
                    "_plate_dir": plate_dir,
                    "_project_dir": project_dir,
                })
    return rows


def list_prints():
    """Return all known plate prints, most recently modified first."""
    global _cache_signature, _cache_prints
    maker = ROOT / "maker"
    printables = ROOT / "tools" / "parts-library" / "printables"
    roots = (maker, printables)
    signature = _signature(roots)
    if signature != _cache_signature:
        rows = _root_records(maker, "du-an", "maker")
        rows.extend(_root_records(printables, "linh-kien", "tools/parts-library/printables"))
        rows.sort(key=lambda row: row["mtime"], reverse=True)
        _cache_prints = rows
        _cache_signature = signature
    return [{key: value for key, value in row.items() if not key.startswith("_")} for row in _cache_prints]


def _match(project, plate):
    list_prints()
    return next((row for row in _cache_prints
                 if row["project"] == project and row["plate"] == plate), None)


def resolve(project, plate, what):
    """Resolve a known print to its model, first CAD file, or plate directory."""
    if what not in ("3mf", "cad", "folder"):
        raise ValueError("Invalid print target")
    row = _match(project, plate)
    if row is None:
        return None
    project_dir = row["_project_dir"].resolve()
    plate_dir = row["_plate_dir"].resolve()
    if what == "folder":
        return plate_dir
    if what == "3mf":
        return plate_dir / f"{plate}.3mf"
    cad = row["cad"]
    if not cad:
        return None
    path = (ROOT / Path(cad[0])).resolve()
    if path != project_dir.resolve() and project_dir.resolve() not in path.parents:
        return None
    return path


def image_path(project, plate):
    row = _match(project, plate)
    if row is None or not row["image_url"]:
        return None
    plate_dir = row["_plate_dir"]
    return next((image.resolve() for image in
                 (plate_dir / "preview.png", plate_dir / "plate_1.png") if image.is_file()), None)
