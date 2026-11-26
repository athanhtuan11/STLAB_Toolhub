"""Ghep contact-sheet-screen.png (1200 px) + concepts/a2-cu-bong-screen-ui.png (mockup UI phang 320x240). Khong can Blender."""
import math, os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(HERE, 'concepts')
FONTS = os.path.join(HERE, '..', '..', '..', 'studio', 'design', 'fonts')
F = lambda s: ImageFont.truetype(os.path.join(FONTS, 'BeVietnamPro-Bold.ttf'), s)
COL = {'listen': '#4FC3F7', 'speak': '#FFC83D', 'praise': '#FF7FB0', 'sleep': '#A99BE0'}
NAME = {'listen': 'Nghe · xanh dương', 'speak': 'Nói · vàng', 'praise': 'Khen · hồng', 'sleep': 'Ngủ · tím mờ'}

def ui(st, k=3):
    W, H = 320 * k, 240 * k
    im = Image.new('RGB', (W, H), '#0A0F18'); d = ImageDraw.Draw(im)
    c = COL[st]; cx = (W // 2 - 62 * k // 1 * 0)
    ex = [W // 2 - 85 * k // 1 * 0 - 83 * k, W // 2 + 83 * k]; ex = [W // 2 - 83 * k // 1 * 1, W // 2 + 83 * k]
    cy = H // 2 + (0 if st != 'sleep' else 10 * k); r = 72 * k // 1
    for x in ex:
        if st in ('listen', 'speak'):
            ry = r + (10 * k if st == 'speak' else 0); rx = r - (10 * k if st == 'speak' else 0)
            d.ellipse([x - rx, cy - ry, x + rx, cy + ry], fill=c)
            pr = rx * 0.5; d.ellipse([x - pr, cy - pr * (1.15 if st == 'speak' else 1) + 6 * k, x + pr, cy + pr * (1.15 if st == 'speak' else 1) + 6 * k], fill='#14203A')
            d.ellipse([x + 14 * k, cy - 34 * k, x + 34 * k, cy - 14 * k], fill='white')
            if st == 'listen':
                d.arc([x - r - 12 * k, cy - r - 12 * k, x + r + 12 * k, cy + r + 12 * k], 200, 340, fill=c, width=5 * k)
        elif st == 'praise':
            d.arc([x - 62 * k, cy - 30 * k, x + 62 * k, cy + 70 * k], 205, 335, fill=c, width=16 * k)
            d.ellipse([x + (-1 if x < W // 2 else 1) * 50 * k - 22 * k, cy + 52 * k - 12 * k, x + (-1 if x < W // 2 else 1) * 50 * k + 22 * k, cy + 52 * k + 12 * k], fill=c)
        else:
            d.arc([x - 62 * k, cy - 62 * k, x + 62 * k, cy + 28 * k], 25, 155, fill=c, width=14 * k)
    if st == 'sleep':
        for (zx, zy, s) in ((W - 80 * k, 40 * k, 22 * k), (W - 52 * k, 20 * k, 14 * k)):
            d.line([zx, zy, zx + s, zy, zx, zy + s, zx + s, zy + s], fill=c, width=3 * k)
    if st == 'praise':
        for (sx, sy, sr) in ((W // 2, 40 * k, 16 * k), (30 * k, 50 * k, 10 * k), (W - 30 * k, 45 * k, 11 * k)):
            pts = [(sx + (sr if i % 2 == 0 else sr * .3) * math.sin(math.pi * i / 4), sy - (sr if i % 2 == 0 else sr * .3) * math.cos(math.pi * i / 4)) for i in range(8)]
            d.polygon(pts, fill=c)
    if st == 'sleep':   # lam mo
        im = Image.blend(Image.new('RGB', (W, H), '#0A0F18'), im, 0.55)
    return im

if __name__ == '__main__':
    tiles = [ui(s, 1) for s in COL]
    sheet = Image.new('RGB', (640 * 1, 480), '#0A0F18')
    big = Image.new('RGB', (2 * 320 * 2 + 30, 2 * 240 * 2 + 30), '#FBF6EE')
    for i, s in enumerate(COL):
        im = ui(s, 2); big.paste(im, (10 + (i % 2) * (640 + 10), 10 + (i // 2) * (480 + 10)))
        ImageDraw.Draw(big).text((26 + (i % 2) * 650, 20 + (i // 2) * 490), NAME[s], font=F(26), fill=COL[s])
    big = big.resize((big.width // 2, big.height // 2), Image.LANCZOS)
    big.save(os.path.join(C, 'a2-cu-bong-screen-ui.png'))
    # contact sheet
    W, T, PAD = 1200, 228, 6
    BG = '#FBF6EE'; INK = '#16231D'
    def rd(n, w): return Image.open(os.path.join(C, n)).convert('RGB').resize((w, w), Image.LANCZOS)
    rows = []
    for v, title in (('v1', 'V1 · màn cao, MỎ DƯỚI MÀN (trên bụng)'), ('v2', 'V2 · màn thấp, MỎ CHỒNG MÉP DƯỚI VIỀN')):
        rows.append((title, [rd('a2-cu-bong-screen-%s-hero.png' % v, T)] + [rd('a2-cu-bong-screen-%s-state-%s.png' % (v, s), T) for s in COL]))
    H = 3 * (T + 34) + 20
    sh = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(sh)
    y = 8
    for title, ims in rows:
        d.text((10, y), title, font=F(18), fill=INK); y += 28
        for i, im in enumerate(ims): sh.paste(im, (i * (T + PAD) + 10, y))
        y += T + 6
    d.text((10, y), 'Cạnh bên (mép vỏ) V1 · V2   |   Mockup UI 4 trạng thái (320×240, nằm ngang)', font=F(18), fill=INK); y += 28
    sh.paste(rd('a2-cu-bong-screen-v1-side.png', T), (10, y)); sh.paste(rd('a2-cu-bong-screen-v2-side.png', T), (10 + T + PAD, y))
    ui_img = Image.open(os.path.join(C, 'a2-cu-bong-screen-ui.png')); ui_img = ui_img.resize((int(ui_img.width * T / ui_img.height), T))
    sh.paste(ui_img, (10 + 2 * (T + PAD), y))
    sh.crop((0, 0, W, y + T + 10)).save(os.path.join(HERE, 'contact-sheet-screen.png'))
