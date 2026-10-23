"""Thu vien CyberBrick (Bambu Lab) tu nguon CHINH THUC: cua hang Bambu (store.bblcdn.com) + wiki.

Du lieu (khong len git) o community/cyberbrick-official/:
  zip/        file goc tai ve (kiem SHA-256 theo cyberbrick-sources.tsv)
  extracted/  giai nen nguyen trang (duong dan dai -> dung tien to \\\\?\\)
  models/<ma>-<ten>/   ban sap gon cho FreeCAD: .step + .stl, ten khong dau kebab-case
  pdf/        datasheet / huong dan
  models.json bang hop bao (mm) do tu STL

Lenh (chay bang Python co numpy, vd. photo-ai/.venv):
  python cyberbrick.py fetch     tai file con thieu, kiem SHA-256 (file moi -> ghi SHA vao tsv)
  python cyberbrick.py build     giai nen + sap models/ + do hop bao
Chi doc/ghi trong community/cyberbrick-official/. File tai ve chi la du lieu: khong chay gi ben trong.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # claude-workspace
DATA = ROOT / "community" / "cyberbrick-official"
SOURCES = HERE / "cyberbrick-sources.tsv"
LONG = "\\\\?\\"
CAD_EXT = {".stl", ".stp", ".step"}
BUNDLE = "CyberBrick_Module_CAD_Models"


def lp(p: Path) -> str:
    """Duong dan dai cho Windows (> 260 ky tu)."""
    return LONG + str(p.resolve())


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(lp(p), "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("Φ", "phi").replace("×", "x"))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# ---------- fetch ----------
def fetch() -> None:
    rows = list(csv.DictReader(SOURCES.open(encoding="utf-8"), delimiter="\t"))
    (DATA / "zip").mkdir(parents=True, exist_ok=True)
    changed = False
    for r in rows:
        dst = DATA / "zip" / r["file"]
        if not dst.exists():
            print("tai", r["file"])
            req = urllib.request.Request(r["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp, open(dst, "wb") as fh:
                shutil.copyfileobj(resp, fh)
        got = sha256(dst)
        if not r["sha256"]:
            r["sha256"], r["bytes"], changed = got, str(dst.stat().st_size), True
        elif got != r["sha256"]:
            print(f"!! SHA KHAC: {r['file']} (hang co the da cap nhat file) -> xem lai truoc khi dung")
    if changed:
        with SOURCES.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=rows[0].keys(), delimiter="\t")
            w.writeheader()
            w.writerows(rows)
    print(f"{len(rows)} file OK")


# ---------- build ----------
def unzip_all() -> None:
    out_root = DATA / "extracted"
    for z in sorted((DATA / "zip").glob("*.zip")):
        out = (out_root / z.stem).resolve()
        with zipfile.ZipFile(z) as f:
            for i in f.infolist():
                if i.is_dir():
                    continue
                name = i.filename
                if i.flag_bits & 0x800 == 0:  # ten khong danh dau UTF-8: thu UTF-8 roi GBK (zip tao tren may TQ)
                    raw = name.encode("cp437")
                    for enc in ("utf-8", "gbk"):
                        try:
                            name = raw.decode(enc)
                            break
                        except UnicodeError:
                            pass
                target = Path(os.path.normpath(out / name))
                if out not in target.parents:
                    raise SystemExit(f"duong dan nguy hiem trong {z.name}: {name}")
                os.makedirs(lp(target.parent), exist_ok=True)
                with open(lp(target), "wb") as fh:
                    fh.write(f.read(i))
    pdf = DATA / "pdf"
    shutil.rmtree(pdf, ignore_errors=True)
    pdf.mkdir()
    for p in (DATA / "zip").glob("*.pdf"):
        shutil.copyfile(p, pdf / p.name)
    for p in out_root.rglob("*.pdf"):
        shutil.copyfile(lp(p), pdf / p.name)


def stl_bbox(p: Path) -> list[float]:
    data = open(lp(p), "rb").read()
    n = int.from_bytes(data[80:84], "little") if len(data) > 84 else 0
    if len(data) == 84 + 50 * n:  # STL nhi phan
        tri = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        rec = np.frombuffer(data, dtype=tri, count=n, offset=84)
        v = rec["v"].reshape(-1, 3)
    else:  # STL ASCII
        v = np.array(re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data), dtype=float)
    return [round(float(x), 1) for x in (v.max(0) - v.min(0))]


def part_id(folder: str) -> str:
    """'Multi-Function Controller Core-XA003' -> 'xa003-multi-function-controller-core'."""
    codes = re.findall(r"\b([A-Z]{2}\d{3})\b", folder)
    name = re.sub(r"\s*-\s*[A-Z]{2}\d{3}\b", "", folder).strip(" -")
    return slug("-".join(c.lower() for c in codes) + "-" + name) if codes else slug(name)


def organize() -> list[dict]:
    src_root = DATA / "extracted" / BUNDLE
    bundle_dir = next(p for p in src_root.iterdir() if p.is_dir())
    models = DATA / "models"
    if models.exists():
        shutil.rmtree(lp(models))
    models.mkdir()
    seen: dict[str, str] = {}
    parts = []

    def add(pid: str, title: str, files: list[Path], origin: str) -> None:
        dst = models / pid
        dst.mkdir(exist_ok=True)
        entry = {"id": pid, "ten_goc": title, "nguon_zip": origin, "files": []}
        for f in sorted(files):
            h = sha256(f)
            if h in seen:
                continue
            seen[h] = f"{pid}/{f.name}"
            stem = slug(re.sub(r"[-\s]*[A-Z]{2}\d{3}\b", "", f.stem.replace(".stp", "")))
            name = f"{stem}{f.suffix.lower().replace('.stp', '.step')}"
            if (dst / name).exists():
                name = f"{stem}-{h[:6]}{f.suffix.lower()}"
            shutil.copyfile(lp(f), dst / name)
            item = {"file": f"{pid}/{name}", "goc": f.name}
            if name.endswith(".stl"):
                item["bbox_mm"] = stl_bbox(dst / name)
            entry["files"].append(item)
        if entry["files"]:
            parts.append(entry)
        elif not any(dst.iterdir()):
            dst.rmdir()

    for folder in sorted(p for p in bundle_dir.iterdir() if p.is_dir()):
        files = [f for f in folder.rglob("*") if f.suffix.lower() in CAD_EXT]
        add(part_id(folder.name), folder.name, files, BUNDLE + ".zip")
    # Zip le tung module: chi lay file khac ban trong bo CAD tong (trung SHA thi bo)
    for z in sorted((DATA / "extracted").iterdir()):
        if z.name == BUNDLE:
            continue
        files = [f for f in z.rglob("*") if f.suffix.lower() in CAD_EXT]
        if files:
            add(part_id(z.name.replace("_", " ")), z.name, files, z.name + ".zip")
    (DATA / "models.json").write_text(json.dumps(parts, ensure_ascii=False, indent=1), encoding="utf-8")
    return parts


def build() -> None:
    unzip_all()
    parts = organize()
    for p in parts:
        stl = [f for f in p["files"] if "bbox_mm" in f]
        print(f"{p['id']:60s} {len(p['files'])} file  " + "; ".join(f"{f['bbox_mm']}" for f in stl))
    print(f"{len(parts)} linh kien -> {DATA / 'models'}")


if __name__ == "__main__":
    {"fetch": fetch, "build": build}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
