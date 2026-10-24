"""Dung reel 9:16 tu ANH CO SAN cua du an (khong can clip quay) - mau "C. Lap rap N buoc" / "A. Tu CAD ra vat that".

Chay: uv run python scripts/make_reel.py <spec.yaml>
spec.yaml (vd. maker/pushrod-arm/marketing/reel-13-steps.yaml):
    out: video-ai/projects/<ten>/out          # tuong doi theo claude-workspace; KHONG len git
    fps: 30
    scenes:
      - {type: title, image: <png>, seconds: 2.5, text: "...", sub: "..."}
      - {type: step,  image: <png>, seconds: 1.6, n: 1, total: 13, text: "De"}
      - {type: end,   image: <png>, seconds: 3.5, text: "Open Lab tham quan", sub: "..."}
Ra: <out>/<ten>.mp4 (1080x1920, H.264 yuv420p, AAC 48 kHz im lang - Facebook can track am thanh; KHONG nhac:
Tuan chon nhac trong app vi tai khoan ca nhan) + <out>/<ten>-contact.png (1 khung moi canh de duyet bang anh).
Mau/chu: studio/design/tokens.json + font Be Vietnam Pro (studio/design/fonts, OFL).
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

WS = Path(__file__).resolve().parents[2]
TOK = json.loads((WS / "studio" / "design" / "tokens.json").read_text(encoding="utf-8"))
C = TOK["light"]
FONTS = WS / "studio" / "design" / "fonts"
W, H = 1080, 1920
MARGIN = 72


def font(weight, size):
    return ImageFont.truetype(str(FONTS / f"BeVietnamPro-{weight}.ttf"), size)


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        t = f"{cur} {word}".strip()
        if draw.textlength(t, font=fnt) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    return lines + ([cur] if cur else [])


def text_block(draw, xy, text, fnt, fill, width, gap=1.15):
    x, y = xy
    for ln in wrap(draw, text, fnt, width):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += int(fnt.size * gap)
    return y


def brand(draw, y=MARGIN):
    """Dau nhan dien: vach vang soi nhua + STLAB (DESIGN.md: diem nhan duy nhat)."""
    draw.rounded_rectangle((MARGIN, y + 4, MARGIN + 16, y + 40), radius=5, fill=C["highlight"])
    draw.text((MARGIN + 30, y), "STLAB", font=font("Bold", 36), fill=C["accent"])


# Vung an toan Reels/TikTok: tren cung (~160 px) co tab, duoi (~420 px) co chu thich + nut -> noi dung chinh o giua
TOP, SAFE_BOTTOM = 160, H - 420


def cover(path, cw, ch, zoom):
    """Anh phu kin khung cw x ch (cat giua), phong them `zoom`."""
    pic = Image.open(path).convert("RGB")
    s = max(cw / pic.width, ch / pic.height) * zoom
    pic = pic.resize((int(pic.width * s), int(pic.height * s)), Image.LANCZOS)
    left, top = (pic.width - cw) // 2, (pic.height - ch) // 2
    return pic.crop((left, top, left + cw, top + ch))


def paste_card(img, path, py, ch, zoom):
    cw = W - 2 * MARGIN
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw, ch), radius=TOK["radius"]["card"] * 3, fill=255)
    img.paste(cover(path, cw, ch, zoom), (MARGIN, py), mask)


def frame(scene, t):
    """t: 0..1 trong canh."""
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)
    brand(d, TOP - 60)
    zoom = scene.get("zoom", 1.0) * (1.0 + 0.05 * t)  # zoom: anh nhieu khoang trang; them phong cham
    card_w = W - 2 * MARGIN
    typ = scene["type"]
    if typ == "step":
        n, total = scene["n"], scene["total"]
        gy, gap = TOP + 20, 10  # tien do 13 doan (noi dung LA trinh tu)
        seg = (card_w - gap * (total - 1)) / total
        for i in range(total):
            x0 = MARGIN + i * (seg + gap)
            d.rounded_rectangle((x0, gy, x0 + seg, gy + 14), radius=7, fill=C["accent"] if i < n else C["line"])
        y = TOP + 50
        d.text((MARGIN, y), f"{n}", font=font("Bold", 200), fill=C["accent"])
        nw = d.textlength(f"{n}", font=font("Bold", 200))
        d.text((MARGIN + nw + 16, y + 118), f"/ {total}", font=font("SemiBold", 60), fill=C["muted"])
        text_block(d, (MARGIN, y + 250), scene["text"], font("Bold", 68), C["text"], card_w)
        py = y + 360
        paste_card(img, scene["image"], py, SAFE_BOTTOM - py, zoom)
    elif typ == "title":
        y = text_block(d, (MARGIN, TOP + 40), scene["text"], font("Bold", 92), C["text"], card_w, 1.12)
        if scene.get("sub"):
            y = text_block(d, (MARGIN, y + 20), scene["sub"], font("SemiBold", 52), C["accent"], card_w)
        py = y + 50
        paste_card(img, scene["image"], py, SAFE_BOTTOM - py, zoom)
    else:  # end: CTA - nut vang soi nhua
        y = text_block(d, (MARGIN, TOP + 40), scene.get("lead", ""), font("Bold", 76), C["text"], card_w, 1.12)
        py, ch = y + 40, 560
        paste_card(img, scene["image"], py, ch, zoom)
        by = py + ch + 60
        d.rounded_rectangle((MARGIN, by, MARGIN + card_w, by + 150), radius=40, fill=C["highlight"])
        tw = d.textlength(scene["text"], font=font("Bold", 72))
        d.text((MARGIN + (card_w - tw) / 2, by + 30), scene["text"], font=font("Bold", 72), fill=C["on-highlight"])
        if scene.get("sub"):
            text_block(d, (MARGIN, by + 190), scene["sub"], font("SemiBold", 46), C["muted"], card_w)
    return img


def main():
    spec_p = Path(sys.argv[1]).resolve()
    spec = yaml.safe_load(spec_p.read_text(encoding="utf-8"))
    base = spec_p.parent
    out = (WS / spec["out"]).resolve()
    name = spec.get("name", spec_p.stem)
    fps = spec.get("fps", 30)
    tmp = out / f"_{name}-frames"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    k, thumbs = 0, []
    for sc in spec["scenes"]:
        sc["image"] = str((base / sc["image"]).resolve())
        n = max(1, round(sc["seconds"] * fps))
        for i in range(n):
            im = frame(sc, i / max(1, n - 1))
            im.save(tmp / f"{k:05d}.png", compress_level=1)
            if i == n // 2:
                thumbs.append(im.resize((W // 4, H // 4)))
            k += 1
    mp4 = out / f"{name}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "%05d.png"),
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-shortest",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps),
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(mp4)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp)
    cols = 6
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W // 4 + 12) + 12, rows * (H // 4 + 12) + 12), C["card"])
    for i, th in enumerate(thumbs):
        sheet.paste(th, (12 + (i % cols) * (W // 4 + 12), 12 + (i // cols) * (H // 4 + 12)))
    sheet.save(out / f"{name}-contact.png")
    print(f"{mp4} ({k / fps:.1f} s, {k} khung) + {name}-contact.png")


if __name__ == "__main__":
    main()
