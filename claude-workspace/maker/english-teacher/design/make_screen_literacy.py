"""Mockup man tuong tac chu viet cho Cu Bong (320 x 240, cam ung) - 2026-11-28.
Ra: concepts/literacy-*.png (x2) + contact-sheet-literacy.png. Chi la mockup de duyet: emoji Segoe (Windows) chi dung minh hoa,
ban that dung bo hinh giay phep mo (Twemoji/OpenMoji CC-BY); phong Comic Sans chi minh hoa chu 'a' 1 tang - ban that Andika (OFL).
Chay: python make_screen_literacy.py
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(HERE, 'concepts')
FONTS = os.path.join(HERE, '..', '..', '..', 'studio', 'design', 'fonts')
K = 2                                   # phong to 2 lan de xem
W, H = 320 * K, 240 * K
BG, CARD, INK = '#0A0F18', '#FFF3DF', '#22304A'
BLUE, YEL, PINK, GREEN, ORANGE = '#4FC3F7', '#FFC83D', '#FF7FB0', '#5BD27A', '#FF8A3D'
EMO = 'C:/Windows/Fonts/seguiemj.ttf'
KID = 'C:/Windows/Fonts/comicbd.ttf'
LBL = os.path.join(FONTS, 'BeVietnamPro-Bold.ttf')


def f(path, px):
    return ImageFont.truetype(path, int(px * K))


def emoji(d, ch, cx, cy, px):
    fo = f(EMO, px)
    b = d.textbbox((0, 0), ch, font=fo, embedded_color=True)
    d.text((cx * K - (b[0] + b[2]) / 2, cy * K - (b[1] + b[3]) / 2), ch, font=fo, embedded_color=True)


def word(d, txt, cx, cy, px, first=ORANGE, rest=INK, hi=0, hi_col=YEL):
    """Chu thuong, chu cai dau to mau; hi = so chu da doc (gach chan vang chay theo loi co)."""
    fo = f(KID, px)
    tw = d.textlength(txt, font=fo)
    x = cx * K - tw / 2
    asc, desc = fo.getmetrics()
    y = cy * K - (asc + desc) / 2
    for i, ch in enumerate(txt):
        d.text((x, y), ch, font=fo, fill=first if i == 0 else rest)
        cw = d.textlength(ch, font=fo)
        if i < hi:
            d.rounded_rectangle([x, y + asc + 4 * K, x + cw, y + asc + 9 * K], 3 * K, fill=hi_col)
        x += cw


def mini_eyes(d, cy, col, look='open'):
    """Mat cu thu nho o dai tren (cu van 'song' khi hien chu)."""
    for ex in (160 - 26, 160 + 26):
        x, y, r = ex * K, cy * K, 17 * K
        if look == 'happy':
            d.arc([x - r, y - r * 0.4, x + r, y + r * 1.4], 205, 335, fill=col, width=5 * K)
        else:
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
            d.ellipse([x - r * .5, y - r * .5 + 2 * K, x + r * .5, y + r * .5 + 2 * K], fill='#14203A')
            d.ellipse([x + 4 * K, y - 10 * K, x + 10 * K, y - 4 * K], fill='white')


def speaker(d, x, y, col='#8FA3BF', waves=1):
    s = K
    x, y = x * K, y * K
    d.polygon([(x, y - 5 * s), (x + 6 * s, y - 5 * s), (x + 13 * s, y - 11 * s), (x + 13 * s, y + 11 * s), (x + 6 * s, y + 5 * s), (x, y + 5 * s)], fill=col)
    for i in range(waves):
        r = (17 + 7 * i) * s
        d.arc([x + 13 * s - r, y - r, x + 13 * s + r, y + r], -40, 40, fill=col, width=3 * s)


def card(d, x0, y0, x1, y1, border=None, bw=0, fill=CARD, dim=False):
    d.rounded_rectangle([x0 * K, y0 * K, x1 * K, y1 * K], 18 * K, fill='#5A6273' if dim else fill,
                        outline=border, width=bw * K if border else 0)


def stars(d, pts, col=YEL):
    for (sx, sy, sr) in pts:
        p = [(sx * K + (sr if i % 2 == 0 else sr * .35) * K * math.sin(math.pi * i / 4),
              sy * K - (sr if i % 2 == 0 else sr * .35) * K * math.cos(math.pi * i / 4)) for i in range(8)]
        d.polygon(p, fill=col)


def touch_ring(d, cx, cy, r=16):
    """Vong tron = ngon tay be cham (chi minh hoa)."""
    d.ellipse([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], outline='white', width=3 * K)
    d.ellipse([(cx - 5) * K, (cy - 5) * K, (cx + 5) * K, (cy + 5) * K], fill='white')


def screen(name):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    if name == 'a-word-card':            # The tu: hinh + chu, cham = nghe lai
        mini_eyes(d, 26, YEL)
        card(d, 34, 52, 286, 232)
        emoji(d, '\U0001F431', 160, 108, 64)
        word(d, 'cat', 160, 190, 50)
        speaker(d, 252, 214, waves=1)
    elif name == 'a-word-reading':       # Co dang doc: gach chan chay theo tieng
        mini_eyes(d, 26, YEL)
        card(d, 34, 52, 286, 232, border=YEL, bw=4)
        emoji(d, '\U0001F431', 160, 108, 64)
        word(d, 'cat', 160, 190, 50, hi=2)
        speaker(d, 252, 214, col=YEL, waves=2)
    elif name == 'b-pick-two':           # Chon 1 trong 2 theo loi co "Where is the cat?"
        mini_eyes(d, 26, BLUE)
        for x0, ch, w in ((10, '\U0001F431', 'cat'), (166, '\U0001F436', 'dog')):
            card(d, x0, 52, x0 + 144, 232)
            emoji(d, ch, x0 + 72, 118, 60)
            word(d, w, x0 + 72, 196, 34)
        touch_ring(d, 82, 130)
    elif name == 'b-pick-right':         # Dung: the sang xanh + sao, the kia mo; mat cuoi
        mini_eyes(d, 26, PINK, 'happy')
        card(d, 10, 52, 154, 232, border=GREEN, bw=6)
        emoji(d, '\U0001F431', 82, 118, 60); word(d, 'cat', 82, 196, 34)
        card(d, 166, 52, 310, 232, dim=True)
        emoji(d, '\U0001F436', 238, 118, 60); word(d, 'dog', 238, 196, 34, first='#3A4150', rest='#3A4150')
        stars(d, [(30, 62, 12), (140, 70, 9), (120, 222, 8)])
    elif name == 'c-first-letter':       # Chu cai dau (4-5 tuoi): cham chu -> "c says /k/ - cat"
        mini_eyes(d, 26, YEL)
        card(d, 18, 52, 162, 232, border=ORANGE, bw=4)
        word(d, 'c', 90, 136, 120, first=ORANGE)
        card(d, 172, 52, 302, 232)
        emoji(d, '\U0001F431', 237, 112, 54)
        word(d, 'cat', 237, 190, 36)
        touch_ring(d, 130, 200)
    elif name == 'd-sticker-review':     # Cuoi buoi: sticker tu da hoc, cham tung cai de nghe
        mini_eyes(d, 26, PINK, 'happy')
        for i, (ch, w) in enumerate((('\U0001F431', 'cat'), ('\U0001F436', 'dog'), ('\U0001F426', 'bird'))):
            cx = 58 + i * 102
            d.ellipse([(cx - 46) * K, 66 * K, (cx + 46) * K, 158 * K], fill=CARD, outline=YEL, width=4 * K)
            emoji(d, ch, cx, 112, 50)
            word(d, w, cx, 190, 30, first=ORANGE, rest='white')
        stars(d, [(160, 222, 9), (40, 224, 6), (282, 222, 7)])
    return im


NAME = {
    'a-word-card': ('A. Thẻ từ', 'cô dạy từ – hiện hình + chữ; bé chạm thẻ = cô đọc lại'),
    'a-word-reading': ('A. Cô đang đọc', 'gạch chân vàng chạy theo tiếng cô (chữ – âm)'),
    'b-pick-two': ('B. Chọn 1 trong 2', 'cô hỏi "Where is the cat?" – bé chạm thẻ to'),
    'b-pick-right': ('B. Đúng rồi', 'thẻ đúng viền xanh + sao, mắt cười; sai = rung nhẹ, cô gợi ý'),
    'c-first-letter': ('C. Chữ cái đầu (4–5 t)', 'chạm "c" – "c says /k/… cat"'),
    'd-sticker-review': ('D. Sticker cuối buổi', 'từ đã học thành sticker, chạm để nghe lại'),
}

if __name__ == '__main__':
    os.makedirs(C, exist_ok=True)
    tiles = []
    for n in NAME:
        im = screen(n); im.save(os.path.join(C, f'literacy-{n}.png')); tiles.append((n, im))
    # contact sheet 3 x 2, moi o 400 x 300 + nhan
    TW, TH, PAD, LH = 400, 300, 16, 58
    sheet = Image.new('RGB', (3 * TW + 4 * PAD, 2 * (TH + LH) + 3 * PAD + 50), '#F4EFE6')
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 14), 'Cú Bông – màn tương tác chữ viết (mockup 320×240, chờ duyệt)', font=ImageFont.truetype(LBL, 24), fill='#22304A')
    for i, (n, im) in enumerate(tiles):
        x = PAD + (i % 3) * (TW + PAD); y = 50 + PAD + (i // 3) * (TH + LH + PAD)
        sheet.paste(im.resize((TW, TH), Image.LANCZOS), (x, y))
        t, s = NAME[n]
        d.text((x, y + TH + 6), t, font=ImageFont.truetype(LBL, 19), fill='#22304A')
        d.text((x, y + TH + 32), s, font=ImageFont.truetype(LBL, 14), fill='#5A6273')
    sheet.save(os.path.join(HERE, 'contact-sheet-literacy.png'))
    print('ok', sheet.size)
