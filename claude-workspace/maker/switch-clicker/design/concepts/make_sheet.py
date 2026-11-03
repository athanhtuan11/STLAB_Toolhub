import sys
from PIL import Image, ImageDraw, ImageFont
d = sys.argv[1]
def font(s):
    for f in ("arial.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        try: return ImageFont.truetype(f, s)
        except Exception: pass
    return ImageFont.load_default()
cells = [("1. Nghieng (side)", "side", (1,1)), ("2. 3/4 (than A + hat ca phe)", "q34", (1,1)), ("3. Tu tren xuong (dau de)", "top", (1,1)),
         ("4. Anh no: nap day | switch (gia dinh) | keycap", "exploded", (1,1)), ("5. So co + thuoc mm", "size", (2,1)),
         ("6. Bo 4 keycap tren than A (Tet: do)", "set4", (3,1)), ("7. Ba huong than A / B / C", "variants", (3,1))]
W = 2400; cw = 780; pad = 12; head = 70; lab = 34
sheet = Image.new("RGB", (W, 6000), "#F7F2E6"); dr = ImageDraw.Draw(sheet)
dr.text((20, 18), "STLab - switch-clicker (Cherry MX) - Buoc 0: dang + keycap", fill="#222", font=font(34))
x = pad; y = head; rowh = 0
for title, name, (span, _) in cells:
    im = Image.open(f"{d}/{name}.png"); fr = 0.5 if name in ("set4","variants") else (0.8 if name in ("side","q34","exploded") else 1.0); im = im.crop((0,int(im.height*(0.52-fr/2)),im.width,int(im.height*(0.52+fr/2)))); w = cw*span + pad*(span-1)
    if x + w > W: x = pad; y += rowh + lab + pad; rowh = 0
    h = int(im.height * w / im.width); im = im.resize((w, h))
    dr.text((x, y), title, fill="#222", font=font(24)); sheet.paste(im, (x, y+lab)); rowh = max(rowh, h); x += w + pad
sheet = sheet.crop((0, 0, W, y+rowh+lab+pad)); sheet.save(f"{d}/../contact-sheet.png"); print(sheet.size)
