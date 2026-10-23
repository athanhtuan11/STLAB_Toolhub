"""So sanh nhieu kieu mau (preset STLab, LUT phim, preset XMP cong dong) tren vai anh that.

Chi DOC anh nguon. Kieu mau doc tu presets/looks.json:
  base  preset STLab qua `lightcraft-cli render --set ...` (giong develop.py)
  lut   (hald -> luts/<slug>.cube, hoac cube) ap len base qua `photocraft-cli run ... colorLookup`
  xmp   preset Lightroom ap thang len anh goc qua `lightcraft-cli render --settings x.xmp`
Ket qua trong --out:
  <anh>/<kieu>.jpg        tung ban (canh dai --size)
  so-sanh-<anh>.jpg       bang so sanh co nhan de Tuan chon kieu

Chay:  uv run scripts/looks.py <thu-muc-anh> DSC_3043 DSC_3110 ... --out <nguon>-edit/looks
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import looklib
from looklib import EXTS

ROOT = Path(__file__).resolve().parent.parent


def sheet(name: str, looks: list[dict], out_dir: Path, dst: Path, local: bool = False) -> None:
    tw, cols = 640, 4
    first = Image.open(out_dir / "base.jpg")
    th = round(tw * first.height / first.width)
    rows = (len(looks) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tw, rows * (th + 40)), "white")
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    for i, lk in enumerate(looks):
        x0, y0 = (i % cols) * tw, (i // cols) * (th + 40)
        f = out_dir / f"{lk['id']}{'-local' if local else ''}.jpg"
        if f.exists():
            im = Image.open(f).convert("RGB")
            im.thumbnail((tw - 6, th))
            canvas.paste(im, (x0, y0))
        d.text((x0 + 6, y0 + th + 8), f"{i + 1}. {lk['label']}", fill="black", font=font)
    canvas.save(dst, quality=88)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    ap.add_argument("photos", nargs="+", help="ten anh (bo duoi), vd. DSC_3043")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--looks", type=Path, default=ROOT / "presets" / "looks.json")
    ap.add_argument("--base", type=Path, default=ROOT / "presets" / "su-kien-ngoai-troi.json")
    ap.add_argument("--only", nargs="*", help="chi lam cac id nay (base luon co)")
    ap.add_argument("--size", type=int, default=2048)
    ap.add_argument("--local", action="store_true", help="nang sang nguoi (PhotoCraft) truoc khi ap kieu")
    a = ap.parse_args()

    looks = json.loads(a.looks.read_text(encoding="utf-8"))["looks"]
    if a.only:
        looks = [lk for lk in looks if lk["id"] == "base" or lk["id"] in a.only]
    base_values = json.loads(a.base.read_text(encoding="utf-8"))
    by_stem = {p.stem.lower(): p for p in a.src.iterdir() if p.suffix.lower() in EXTS}

    for name in a.photos:
        src = by_stem.get(name.lower())
        if not src:
            ap.error(f"khong thay {name} trong {a.src}")
        out_dir = a.out / src.stem
        out_dir.mkdir(parents=True, exist_ok=True)
        looklib.build(src, looks[0], a.local, out_dir, a.size, base_values)  # base truoc: LUT ap len base
        errors = {}

        def job(lk: dict) -> None:
            try:
                looklib.build(src, lk, a.local, out_dir, a.size, base_values)
            except Exception as e:  # noqa: BLE001 - ghi loi tung kieu, khong dung ca loat
                errors[lk["id"]] = str(e)

        with ThreadPoolExecutor(4) as pool:
            list(pool.map(job, looks[1:]))
        sheet(src.stem, looks, out_dir, a.out / f"so-sanh-{src.stem}.jpg", a.local)
        print(f"{src.stem}: {len(looks) - len(errors)}/{len(looks)} kieu -> so-sanh-{src.stem}.jpg")
        for k, v in errors.items():
            print(f"  ! {k}: {v}")


if __name__ == "__main__":
    main()
