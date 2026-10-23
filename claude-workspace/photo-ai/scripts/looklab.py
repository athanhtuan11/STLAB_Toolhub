"""Phan chay phia sau cho trang Toolhub > Sua anh. In JSON ra stdout (duong dan tuong doi voi <nguon>-edit).

  looks                          danh sach kieu mau (presets/looks.json)
  photos <nguon>                 anh se xu ly (cull/dat neu co, khong thi ca thu muc nguon) + tao anh nho
  preview <nguon> <anh> <kieu> [--local]
                                 tao ban xem truoc 1600 px: orig (anh may anh), under, over (xem looklib.py)

Chi DOC thu muc nguon; moi file ghi vao <nguon>-edit/lab/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

import looklib
from looklib import EXTS

PREVIEW_EDGE = 1600
THUMB_EDGE = 320


def edit_dir(src: Path) -> Path:
    return src.parent / (src.name + "-edit")


def photo_list(src: Path) -> tuple[list[Path], str]:
    by_stem = {p.stem.lower(): p for p in src.iterdir() if p.suffix.lower() in EXTS}
    dat = edit_dir(src) / "cull" / "dat"
    if dat.is_dir():
        stems = sorted(p.stem for p in dat.iterdir() if p.suffix.lower() in EXTS)
        return [by_stem[s.lower()] for s in stems if s.lower() in by_stem], "cull/dat"
    return sorted(by_stem.values()), "nguon"


def cmd_looks(_: argparse.Namespace) -> dict:
    return {"looks": [{"id": k, "label": lk["label"], "kind": looklib.kind(lk)} for k, lk in looklib.load_looks().items()]}


def cmd_photos(a: argparse.Namespace) -> dict:
    files, origin = photo_list(a.src)
    ed = edit_dir(a.src)
    thumbs = ed / "lab" / "thumbs"
    thumbs.mkdir(parents=True, exist_ok=True)
    for f in files:
        t = thumbs / (f.stem + ".jpg")
        if not t.exists():
            im = Image.open(f)
            im.draft("RGB", (THUMB_EDGE * 2, THUMB_EDGE * 2))
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((THUMB_EDGE, THUMB_EDGE))
            im.save(t, quality=82)  # khong mang EXIF/GPS
    return {"edit": str(ed), "origin": origin, "photos": [f.stem for f in files]}


def cmd_preview(a: argparse.Namespace) -> dict:
    looks = looklib.load_looks()
    if a.look not in looks:
        raise SystemExit(f"khong co kieu {a.look}")
    by_stem = {p.stem.lower(): p for p in a.src.iterdir() if p.suffix.lower() in EXTS}
    src = by_stem.get(a.photo.lower())
    if not src:
        raise SystemExit(f"khong thay anh {a.photo}")
    ed = edit_dir(a.src)
    work = ed / "lab" / "preview" / src.stem
    under, over = looklib.build(src, looks[a.look], a.local, work, PREVIEW_EDGE, looklib.base_values())
    orig = looklib.build(src, looks["base"], False, work, PREVIEW_EDGE, looklib.base_values())[0]  # plain.jpg
    rel = lambda p: p.relative_to(ed).as_posix()  # noqa: E731
    return {"orig": rel(orig), "under": rel(under), "over": rel(over)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("looks")
    p = sub.add_parser("photos")
    p.add_argument("src", type=Path)
    p = sub.add_parser("preview")
    p.add_argument("src", type=Path)
    p.add_argument("photo")
    p.add_argument("look")
    p.add_argument("--local", action="store_true")
    a = ap.parse_args()
    if getattr(a, "src", None) and not a.src.is_dir():
        ap.error(f"khong co thu muc {a.src}")
    try:
        out = {"looks": cmd_looks, "photos": cmd_photos, "preview": cmd_preview}[a.cmd](a)
    except Exception as e:  # noqa: BLE001 - tra loi dang JSON cho Toolhub
        print(json.dumps({"ok": False, "msg": str(e)[-400:]}, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps({"ok": True, **out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
