"""Dung reel 9:16 tu ANH CO SAN cua du an (khong can clip quay) - mau "C. Lap rap N buoc" / "A. Tu CAD ra vat that".

Chay: uv run python scripts/make_reel.py <spec.yaml>
spec.yaml (vd. maker/pushrod-arm/marketing/reel-13-steps.yaml):
    out: video-ai/projects/<ten>/out          # tuong doi theo claude-workspace; KHONG len git
    fps: 30
    scenes:
      - {type: title, image: <png>, seconds: 2.5, text: "...", sub: "..."}
      - {type: step,  image: <png>, seconds: 1.6, n: 1, total: 13, text: "De"}
      - {type: end,   image: <png>, seconds: 3.5, text: "Open Lab tham quan", sub: "..."}
    voice: "Mai Anh"                          # tuy chon: giong VieNeu (scripts/tts_vi.py); canh co `say:` duoc doc
    # canh: say: "cau doc"  -> canh keo dai cho du cau (LEAD + cau + TAIL), them giong + <ten>.srt (phu de tu kich ban)
Ra: <out>/<ten>.mp4 (1080x1920, H.264 yuv420p, AAC 48 kHz im lang - Facebook can track am thanh; KHONG nhac:
Tuan chon nhac trong app vi tai khoan ca nhan) + <out>/<ten>-contact.png (1 khung moi canh de duyet bang anh).
Mau/chu: studio/design/tokens.json + font Be Vietnam Pro (studio/design/fonts, OFL).
"""

import json
import os
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
VIENEU = Path(os.environ.get("LOCALAPPDATA", "")) / "stlab-studio" / "venvs" / "vieneu" / "Scripts" / "python.exe"
LEAD, TAIL = 0.25, 0.45   # giay lang truoc / sau cau doc trong canh


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


def narrate(spec, out, name):
    """Canh co `say:` -> giong doc tieng Viet tren may (tts_vi.py, venv VieNeu) -> {chi so canh: (wav, giay)}."""
    lines = [{"id": f"s{i:02d}", "text": sc["say"]} for i, sc in enumerate(spec["scenes"]) if sc.get("say")]
    if not lines:
        return {}
    vd = out / f"_{name}-voice"  # giu lai: cache, sua 1 cau chi doc lai cau do
    vd.mkdir(parents=True, exist_ok=True)
    (vd / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
    cmd = [str(VIENEU), str(Path(__file__).with_name("tts_vi.py")), str(vd / "lines.json"), str(vd)]
    subprocess.run(cmd + (["--voice", spec["voice"]] if spec.get("voice") else []), check=True)
    d = json.loads((vd / "durations.json").read_text(encoding="utf-8"))
    return {int(k[1:]): (vd / f"{k}.wav", v) for k, v in d.items()}


def srt_time(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


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
    voice = narrate(spec, out, name)
    k, thumbs, cues = 0, [], []
    for j, sc in enumerate(spec["scenes"]):
        sc["image"] = str((base / sc["image"]).resolve())
        if j in voice:  # canh dai it nhat bang cau doc
            sc["seconds"] = max(sc["seconds"], LEAD + voice[j][1] + TAIL)
            cues.append((j, k / fps + LEAD, k / fps + LEAD + voice[j][1], sc["say"]))
        n = max(1, round(sc["seconds"] * fps))
        for i in range(n):
            im = frame(sc, i / max(1, n - 1))
            im.save(tmp / f"{k:05d}.png", compress_level=1)
            if i == n // 2:
                thumbs.append(im.resize((W // 4, H // 4)))
            k += 1
    mp4 = out / f"{name}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "%05d.png")]
    if cues:  # giong dat dung luc canh, chuan -14 LUFS (Reels/TikTok), dem lang toi het video
        for j, *_ in cues:
            cmd += ["-i", str(voice[j][0])]
        f = ";".join(f"[{i + 1}:a]adelay={round(t0 * 1000)}:all=1[v{i}]" for i, (_, t0, _, _) in enumerate(cues))
        f += ";" + "".join(f"[v{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,"
        f += "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=stereo,apad[a]"
        cmd += ["-filter_complex", f, "-map", "0:v", "-map", "[a]", "-shortest"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps),
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(mp4)]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp)
    cols = 6
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W // 4 + 12) + 12, rows * (H // 4 + 12) + 12), C["card"])
    for i, th in enumerate(thumbs):
        sheet.paste(th, (12 + (i % cols) * (W // 4 + 12), 12 + (i // cols) * (H // 4 + 12)))
    sheet.save(out / f"{name}-contact.png")
    if cues:  # phu de tu chinh kich ban (khoi nhan dang lai) - tai len Facebook cung video
        (out / f"{name}.srt").write_text("".join(f"{i + 1}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n\n"
                                                 for i, (_, a, b, t) in enumerate(cues)), encoding="utf-8")
    print(f"{mp4} ({k / fps:.1f} s, {k} khung) + {name}-contact.png"
          + (f" + {name}.srt ({len(cues)} cau)" if cues else ""))


if __name__ == "__main__":
    main()
