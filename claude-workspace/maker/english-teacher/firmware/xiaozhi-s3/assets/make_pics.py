"""Sinh hình thẻ từ cho Cú Bông: Twemoji 14.0.2 (CC BY 4.0, (c) Twitter, Inc và người đóng góp) -> ảnh LVGL 9 RGB565A8.

Đọc từ mới Seed 1-3 trong ../../lessons-seed/ROADMAP.md (dòng `new:`), tra bảng pic-map.yaml (word -> mã emoji | null),
tải PNG 72x72 từ jsDelivr (cache assets/.cache/), ghi assets/pics/<word>.bin (khoảng trắng -> '_').
Định dạng .bin = lv_image_header_t (12 byte, little-endian) + RGB565 (w*h*2) + A8 (w*h).
Chạy: python make_pics.py            (sinh pics/)
      python make_pics.py --check    (chỉ kiểm file mã emoji tồn tại trên CDN)
"""
import re, struct, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROADMAP = HERE / ".." / ".." / ".." / "lessons-seed" / "ROADMAP.md"
MAP = HERE / "pic-map.yaml"
CACHE = HERE / ".cache"
OUT = HERE / "pics"
CDN = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/%s.png"
LV_MAGIC, CF_RGB565A8 = 0x19, 0x14


def new_words():
    ws = []
    for line in ROADMAP.resolve().read_text(encoding="utf-8").splitlines():
        m = re.search(r"\bnew:\s*([^|]*)", line)
        if not m:
            continue
        for w in m.group(1).split(","):
            w = w.strip()
            if w and w != "-" and w not in ws:
                ws.append(w)
    return ws


def read_map():
    mp = {}
    for w, code in re.findall(r"^\s*([a-z][a-z \-']*)\s*:\s*(\S+)", MAP.read_text(encoding="utf-8"), re.M):
        mp[w.strip()] = None if code == "null" else code.lower()
    return mp


def fetch(code):
    f = CACHE / (code + ".png")
    if f.exists() and f.stat().st_size > 0:
        return f
    CACHE.mkdir(exist_ok=True)
    try:
        with urllib.request.urlopen(CDN % code, timeout=30) as r:
            f.write_bytes(r.read())
    except urllib.error.URLError as e:
        print("LOI tai %s: %s" % (code, e))
        return None
    return f


def to_bin(png):
    im = Image.open(png).convert("RGBA")
    w, h = im.size
    px = im.load()
    rgb, alpha = bytearray(), bytearray()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            rgb += struct.pack("<H", ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3))
            alpha.append(a)
    hdr = struct.pack("<BBHHHHH", LV_MAGIC, CF_RGB565A8, 0, w, h, w * 2, 0)
    return hdr + bytes(rgb) + bytes(alpha)


def main():
    words, mp = new_words(), read_map()
    miss = [w for w in words if w not in mp]
    if miss:
        sys.exit("pic-map.yaml thieu tu: " + ", ".join(miss))
    codes = sorted({c for w in words for c in [mp[w]] if c})
    with ThreadPoolExecutor(8) as ex:
        files = dict(zip(codes, ex.map(fetch, codes)))
    bad = [c for c, f in files.items() if f is None]
    if bad:
        sys.exit("Thieu file Twemoji tren CDN: " + ", ".join(bad))
    if "--check" in sys.argv:
        print("OK: %d tu, %d ma emoji ton tai, %d null" % (len(words), len(codes), sum(1 for w in words if not mp[w])))
        return
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.bin"):
        old.unlink()
    n = 0
    for w in words:
        if mp[w]:
            (OUT / (w.replace(" ", "_") + ".bin")).write_bytes(to_bin(files[mp[w]]))
            n += 1
    print("make_pics: %d hinh (%d tu, %d null) -> %s" % (n, len(words), len(words) - n, OUT))


if __name__ == "__main__":
    main()
