"""Doi HaldCLUT (PNG) cua cong dong sang LUT .cube cho PhotoCraft (Color Lookup) va LightCraft (profile).

Chi DOC trong community/. Ghi ra luts/<ten>.cube (khong dua len git: tao lai bang lenh nay).
HaldCLUT cap L: anh (L^3 x L^3) px, luoi L^2 moi kenh, thu tu R nhanh nhat -> trung thu tu .cube.
Thu nho luoi ve --size bang noi suy 3 chieu (trilinear).

Chay:  uv run scripts/luts.py "<HaldCLUT.png>" ... [--size 33]
       uv run scripts/luts.py --default      # bo LUT da chon trong presets/looks.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
COMMUNITY = ROOT.parent / "community"
OUT = ROOT / "luts"


def hald_to_grid(path: Path) -> np.ndarray:
    """Tra mang (N, N, N, 3) float 0..1, chi so [b, g, r]."""
    im = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    side = im.shape[0]
    level = round(side ** (1 / 3))
    if level**3 != side or im.shape[1] != side:
        raise ValueError(f"{path.name}: khong phai HaldCLUT vuong ({im.shape[1]}x{side})")
    n = level * level
    return im.reshape(n, n, n, 3)


def resample(grid: np.ndarray, size: int) -> np.ndarray:
    n = grid.shape[0]
    x = np.linspace(0, n - 1, size)
    i0 = np.clip(np.floor(x).astype(int), 0, n - 2)
    f = x - i0
    b0, g0, r0 = np.ix_(i0, i0, i0)
    fb, fg, fr = (f[:, None, None, None], f[None, :, None, None], f[None, None, :, None])
    out = np.zeros((size, size, size, 3))
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (fb if db else 1 - fb) * (fg if dg else 1 - fg) * (fr if dr else 1 - fr)
                out += w * grid[b0 + db, g0 + dg, r0 + dr]
    return out


def write_cube(grid: np.ndarray, path: Path, title: str, source: str) -> None:
    size = grid.shape[0]
    lines = [
        f'TITLE "{title}"',
        f"# Nguon: {source}",
        "# Tao boi photo-ai/scripts/luts.py tu HaldCLUT",
        f"LUT_3D_SIZE {size}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
    ]
    flat = grid.reshape(-1, 3)  # [b][g][r] -> r nhanh nhat, dung chuan .cube
    lines += [f"{r:.6f} {g:.6f} {b:.6f}" for r, g, b in flat]
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("hald", nargs="*", type=Path)
    ap.add_argument("--size", type=int, default=33)
    ap.add_argument("--default", action="store_true", help="doi cac HaldCLUT ma presets/looks.json dung")
    a = ap.parse_args()

    files = list(a.hald)
    if a.default:
        looks = json.loads((ROOT / "presets" / "looks.json").read_text(encoding="utf-8"))
        files += [COMMUNITY / lk["hald"] for lk in looks["looks"] if "hald" in lk]
    if not files:
        ap.error("khong co HaldCLUT nao")
    OUT.mkdir(exist_ok=True)
    for f in files:
        dst = OUT / (slug(f.stem) + ".cube")
        grid = resample(hald_to_grid(f), a.size)
        src = f.relative_to(COMMUNITY).as_posix() if COMMUNITY in f.parents else f.name
        write_cube(grid, dst, f.stem, src)
        print(f"{f.name} -> {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
