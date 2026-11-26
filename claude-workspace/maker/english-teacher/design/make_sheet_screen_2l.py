"""Ghep contact-sheet-screen-2l.png (1200 px). Khong can Blender."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(HERE, 'concepts')
FONTS = os.path.join(HERE, '..', '..', '..', 'studio', 'design', 'fonts')
F = lambda s: ImageFont.truetype(os.path.join(FONTS, 'BeVietnamPro-Bold.ttf'), s)
W, T, PAD, BG, INK = 1200, 228, 6, '#FBF6EE', '#16231D'
rows = (('h0', 'V2-2L · biến thể H0: loa hướng NGANG 0° (khuyến nghị: gọn, thân giữ 134,4)'),
        ('h25', 'V2-2L · biến thể H25: loa CHẾCH TRƯỚC 25° (mặt loa lộ ra trước, tiếng hướng bé)'))
tags = ('hero', 'side', 'back', 'xray-front', 'xray-top')
labels = ('3/4 trước', 'cạnh', 'lưng', 'X-ray trước', 'X-ray trên')
sh = Image.new('RGB', (W, len(rows) * (T + 56) + 8), BG); d = ImageDraw.Draw(sh); y = 6
for v, title in rows:
    d.text((10, y), title, font=F(18), fill=INK); y += 28
    for i, t in enumerate(tags):
        im = Image.open(os.path.join(C, 'a2-cu-bong-screen-v2-2l-%s-%s.png' % (v, t))).convert('RGB').resize((T, T), Image.LANCZOS)
        sh.paste(im, (10 + i * (T + PAD), y)); d.text((16 + i * (T + PAD), y + 4), labels[i], font=F(13), fill=INK)
    y += T + 6
sh.crop((0, 0, W, y + 4)).save(os.path.join(HERE, 'contact-sheet-screen-2l.png'))
