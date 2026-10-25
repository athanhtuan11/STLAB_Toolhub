"""Chinh mau + xuat Facebook bang LightCraft, roi tu kiem tra (QA) va lam contact sheet.

Chi DOC anh nguon. Moi anh: `lightcraft-cli render <nguon> -o <out>/<ten>.jpg --set k=v ...`
(khong can thu vien LightCraft). Preset dang khoa phang {"light.exposure": 0.1, ...} truyen bang --set:
`--settings` cua render KHONG ap file nay (thu 2026-10-21: anh ra giong het anh goc). Ket qua ghi vao --out:
  <ten>.jpg              anh da xuat (canh dai --size, sRGB, khong GPS)
  qa.csv                 moi anh: kich thuoc, GPS, ICC, % chay sang / bet den (so voi goc), canh bao
  contact-<n>.jpg        bang anh da xuat (40 anh/trang) de Tuan duyet truoc khi dang

Chay:  uv run scripts/develop.py <thu-muc-anh> --list <nguon>-edit/cull/dat --out <nguon>-edit/xuat
       (--list: thu muc anh xem truoc Tuan da duyet; ghep voi anh goc theo ten, bo duoi)
       Them kieu mau (presets/looks.json, chon tren Toolhub > Sua anh):
       --look portra160nc --strength 0.8 --local   (LUT 80% + nang sang nguoi bang PhotoCraft, xem looklib.py)
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageOps

import looklib

PRESETS = Path(__file__).resolve().parent.parent / "presets"
CLI = Path(r"C:\Program Files\LightCraft\lightcraft-cli.exe")
EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
PAGE = 40


@dataclass
class Result:
    file: str
    ok: bool = False
    size: str = ""
    kb: int = 0
    gps: bool = False
    icc: str = ""
    artist: str = ""
    clip_hi: float = 0.0  # % diem anh ca 3 kenh >= 250
    clip_lo: float = 0.0  # % diem anh ca 3 kenh <= 5
    src_hi: float = 0.0  # nhu tren, tren anh goc
    src_lo: float = 0.0
    change: float = 0.0  # chenh lech TB voi anh goc (0-255): ~0 -> preset khong ap
    warn: list[str] = field(default_factory=list)


def render(src: Path, out: Path, a: argparse.Namespace) -> str | None:
    cmd = [
        str(CLI), "render", str(src), "-o", str(out),
        *(x for k, v in a.values.items() for x in ("--set", f"{k}={v}")),
        "--size", str(a.size), "--quality", str(a.quality),
        "--opt", "colorSpace=srgb", "--opt", "removeLocation=true", "--opt", f"metadata={a.metadata}",
    ]  # fmt: skip
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return None if p.returncode == 0 else (p.stderr or p.stdout).strip()[-300:]


def clip(px: np.ndarray) -> tuple[float, float]:
    return round(float((px.min(axis=2) >= 250).mean() * 100), 2), round(float((px.max(axis=2) <= 5).mean() * 100), 2)


def check(src: Path, out: Path, a: argparse.Namespace) -> Result:
    r = Result(file=out.name)
    if not out.exists():
        r.warn.append("khong co file xuat")
        return r
    im = Image.open(out)
    exif = im.getexif()
    r.size, r.kb = f"{im.width}x{im.height}", out.stat().st_size // 1024
    r.gps = 0x8825 in exif and bool(exif.get_ifd(0x8825))
    r.artist = " / ".join(str(exif.get(t, "")).strip("\x00 ") for t in (315, 33432) if exif.get(t))
    icc = im.info.get("icc_profile")
    r.icc = ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(io.BytesIO(icc))).strip() if icc else ""
    px = np.asarray(im.convert("RGB").reduce(4))
    orig = Image.open(src)
    orig.draft("RGB", (im.width, im.width))
    orig = ImageOps.exif_transpose(orig).convert("RGB").resize(im.size).reduce(4)
    opx = np.asarray(orig)
    (r.clip_hi, r.clip_lo), (r.src_hi, r.src_lo) = clip(px), clip(opx)
    r.change = round(float(np.abs(px.astype(float) - opx.astype(float)).mean()), 1)
    if max(im.size) != a.size:
        r.warn.append(f"canh dai {max(im.size)} px != {a.size}")
    if r.gps:
        r.warn.append("CON GPS")
    if icc and "srgb" not in r.icc.lower():
        r.warn.append(f"ICC la {r.icc}")
    if a.values and r.change < 1.0:
        r.warn.append("preset khong ap (anh giong goc)")
    # Chi canh bao khi chinh mau lam chay/bet THEM (troi chay san trong anh goc thi khong cuu duoc)
    if r.clip_hi > a.max_clip and r.clip_hi > r.src_hi + 1:
        r.warn.append(f"chay sang {r.src_hi}% -> {r.clip_hi}%")
    if r.clip_lo > a.max_clip and r.clip_lo > r.src_lo + 1:
        r.warn.append(f"bet den {r.src_lo}% -> {r.clip_lo}%")
    r.ok = not r.warn
    return r


def contact(results: list[Result], out_dir: Path) -> list[Path]:
    tw, th, cols = 420, 280, 5
    pages = []
    for n, start in enumerate(range(0, len(results), PAGE), 1):
        chunk = results[start : start + PAGE]
        rows = (len(chunk) + cols - 1) // cols
        canvas = Image.new("RGB", (cols * tw, rows * (th + 34)), "white")
        d = ImageDraw.Draw(canvas)
        for i, r in enumerate(chunk):
            x0, y0 = (i % cols) * tw, (i // cols) * (th + 34)
            f = out_dir / r.file
            if f.exists():
                im = Image.open(f)
                im.draft("RGB", (tw * 2, th * 2))
                im = im.convert("RGB")
                im.thumbnail((tw - 6, th))
                canvas.paste(im, (x0, y0))
            d.text((x0 + 3, y0 + th + 2), r.file, fill="black")
            d.text((x0 + 3, y0 + th + 16), "; ".join(r.warn)[:70], fill=(200, 0, 0) if r.warn else "black")
        page = out_dir / f"contact-{n}.jpg"
        canvas.save(page, quality=85)
        pages.append(page)
    return pages


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path, help="thu muc anh goc (chi doc)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--list", type=Path, help="chi xuat anh co trong thu muc nay (vd. cull/dat)")
    ap.add_argument("--preset", type=Path, default=PRESETS / "outdoor-event.json")
    ap.add_argument("--size", type=int, default=2048, help="canh dai (px); Facebook: 2048")
    ap.add_argument("--quality", type=int, default=90)
    ap.add_argument(
        "--metadata",
        default="none",
        help="metadata cua app.export: none (xoa het EXIF, van giu ICC sRGB) | copyright | all",
    )
    ap.add_argument("--max-clip", type=float, default=3.0, help="%% diem chay sang/bet den toi da")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--force", action="store_true", help="xuat lai ca anh da co")
    ap.add_argument("--look", default="base", help="id kieu mau trong presets/looks.json (mac dinh: preset STLab)")
    ap.add_argument("--strength", type=float, default=1.0, help="do manh kieu 0..1")
    ap.add_argument("--local", action="store_true", help="nang sang nguoi (PhotoCraft) truoc khi ap LUT")
    a = ap.parse_args()
    looks = looklib.load_looks()
    if a.look not in looks:
        ap.error(f"khong co kieu {a.look!r}; co: {', '.join(looks)}")
    simple = a.look == "base" and a.strength >= 0.999 and not a.local

    if a.out.resolve() == a.src.resolve() or a.src.resolve() in a.out.resolve().parents:
        ap.error("--out phai nam ngoai thu muc anh goc")
    a.values = json.loads(a.preset.read_text(encoding="utf-8"))
    if not isinstance(a.values, dict) or any(isinstance(v, dict) for v in a.values.values()):
        ap.error("preset phai la JSON phang {\"light.exposure\": 0.1, ...}")
    if a.list:
        by_stem = {p.stem.lower(): p for p in a.src.iterdir() if p.suffix.lower() in EXTS}
        stems = sorted(p.stem for p in a.list.iterdir() if p.suffix.lower() in EXTS)
        files = [by_stem.get(s.lower(), a.src / s) for s in stems]
        missing = [f.name for f in files if not f.exists()]
        if missing:
            ap.error(f"{len(missing)} file trong --list khong co trong nguon, vd. {missing[:3]}")
    else:
        files = sorted(p for p in a.src.iterdir() if p.suffix.lower() in EXTS)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "kieu.json").write_text(json.dumps({"look": a.look, "label": looks[a.look]["label"],
        "strength": a.strength, "local": a.local}, ensure_ascii=False), encoding="utf-8")  # fmt: skip

    t0 = time.time()
    errors: dict[str, str] = {}

    def job(src: Path) -> None:
        out = a.out / (src.stem + ".jpg")
        if out.exists() and not a.force:
            return
        if simple:
            err = render(src, out, a)
            if err:
                errors[src.name] = err
            return
        work = a.out / ".tmp" / src.stem
        try:
            under, over = looklib.build(src, looks[a.look], a.local, work, a.size, a.values, a.quality)
            looklib.blend(under, over, a.strength, out, a.quality)
        except Exception as e:  # noqa: BLE001 - ghi loi tung anh, khong dung ca loat
            errors[src.name] = str(e)[-300:]
        finally:
            shutil.rmtree(work, ignore_errors=True)

    with ThreadPoolExecutor(a.jobs) as pool:
        for i, _ in enumerate(pool.map(job, files), 1):
            print(f"{i}/{len(files)} anh, {time.time() - t0:.0f} s", flush=True)
    shutil.rmtree(a.out / ".tmp", ignore_errors=True)

    results = [check(f, a.out / (f.stem + ".jpg"), a) for f in files]
    for r in results:
        src_name = next(f.name for f in files if f.stem + ".jpg" == r.file)
        if src_name in errors:
            r.warn.insert(0, "render loi: " + errors[src_name])
    with open(a.out / "qa.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "dat", "kich_thuoc", "kb", "gps", "icc", "artist_copyright", "chenh_goc",
                    "chay_sang_goc_%", "chay_sang_%", "bet_den_goc_%", "bet_den_%", "canh_bao"])  # fmt: skip
        for r in results:
            w.writerow([r.file, r.ok, r.size, r.kb, r.gps, r.icc, r.artist, r.change, r.src_hi, r.clip_hi,
                        r.src_lo, r.clip_lo, "; ".join(r.warn)])  # fmt: skip
    pages = contact(results, a.out)

    bad = [r for r in results if not r.ok]
    artists = sorted({r.artist for r in results if r.artist})
    print(f"Xong {len(results)} anh trong {time.time() - t0:.0f} s -> {a.out}")
    print(f"QA dat {len(results) - len(bad)}/{len(results)}; contact sheet: {len(pages)} trang")
    for r in bad:
        print(f"  ! {r.file}: {'; '.join(r.warn)}")
    if artists:
        print(f"Luu y: anh con Artist/Copyright {artists} (--metadata {a.metadata})")


if __name__ == "__main__":
    main()
