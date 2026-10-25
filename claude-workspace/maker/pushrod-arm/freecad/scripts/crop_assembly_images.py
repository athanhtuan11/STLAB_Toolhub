"""Cat khung + thu nho anh huong dan lap: images/assembly/raw/step-XX.png (2400x1800) -> images/assembly/step-XX.png (1200x900).
Chay (moi truong co Pillow, vd. video-ai):  uv run python <file nay>
Tu cat khoang trang thua (le 8 %, ti le 4:3) - chup 2x roi thu nho cho net min (docs/assembly-instructions-style-research.md).
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

A = Path(__file__).resolve().parents[1] / "images" / "assembly"


def autocrop(im, pad=0.08, aspect=4 / 3, size=(1200, 900)):
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    x0, y0, x1, y1 = bbox
    w2, h2 = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    w2, h2 = (h2 * aspect, h2) if w2 / h2 < aspect else (w2, w2 / aspect)
    o = int(max(w2, h2))
    big = ImageOps.expand(im, border=o, fill="white")  # dem trang: cat khong vuot anh (lan dau co dai den)
    cx, cy = (x0 + x1) / 2 + o, (y0 + y1) / 2 + o
    return big.crop((int(cx - w2 / 2), int(cy - h2 / 2), int(cx + w2 / 2), int(cy + h2 / 2))).resize(size, Image.LANCZOS)


if __name__ == "__main__":
    for old in A.glob("step-*-[abc].png"):  # anh kieu cu (3 anh/buoc) - da thay
        old.unlink()
    n = 0
    for p in sorted((A / "raw").glob("step-*.png")) + sorted((A / "raw").glob("cover.png")):
        autocrop(Image.open(p).convert("RGB")).save(A / p.name, optimize=True)
        n += 1
    print(n, "anh ->", A)
