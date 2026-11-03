"""Ghep contact-sheet.png: 3 phuong an x 3 anh + hang giao dien web. Chay: python make_contact_sheet.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parents[2] / "studio" / "design" / "fonts"
BG, CARD, INK, MUTED, PINE = "#ECF1EF", "#FBFCFB", "#16231D", "#56655E", "#1E5A45"


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ("BeVietnamPro-Bold.ttf" if bold else "BeVietnamPro-Regular.ttf")), size)


ROWS = [
    ("A  Sỏi – mặt xanh thông, khớp cầu pan/tilt", "A-soi", ["Trước (3/4)", "Sau: khe nhiệt + cổng USB", "Cỡ so với ổ điện 86 × 86 mm"]),
    ("B  Hộp bo tròn – khung chữ U, đế = tấm treo tường", "B-hop", ["Trước (3/4)", "Sau: khe nhiệt + cổng USB", "Cỡ so với ổ điện 86 × 86 mm"]),
    ("C  Mắt – cầu cụt trên vành đế xoay (mắt robot)", "C-mat", ["Trước (3/4)", "Sau: mặt phẳng + khe nhiệt", "Cỡ so với ổ điện 86 × 86 mm"]),
]
SUFFIX = ["truoc", "sau", "tile"]
CW, CH, PAD, HEAD = 520, 390, 18, 52
W = 3 * CW + 4 * PAD
ui = [("ui/ui-desktop-sang.png", "Desktop 1280×800 – sáng"), ("ui/ui-desktop-toi.png", "Desktop – tối"),
      ("ui/ui-phone-sang.png", "Phone 390×844 sáng"), ("ui/ui-phone-toi-canhbao.png", "Phone tối, nóng 67,8 °C")]
UI_H = 330
H = PAD + 60 + 3 * (HEAD + CH + 24 + PAD) + HEAD + UI_H + 24 + 2 * PAD
sheet = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(sheet)
d.rectangle((PAD, PAD + 4, PAD + 6, PAD + 34), fill="#E8B33A")
d.text((PAD + 16, PAD), "STLab · esp32-s3-cam · bước 0 Giao diện", font=font(26, True), fill=INK)
d.text((PAD + 16, PAD + 34), "Khối minh họa (chưa phải CAD). Ảnh A/B/C vẽ theo khối cũ 27 × 40,5 × 12 mm; D dùng 27 × 40,5 × 20–25 mm (cộng đồng).", font=font(14), fill=MUTED)
y = PAD + 60
for title, key, caps in ROWS:
    d.text((PAD, y), title, font=font(20, True), fill=PINE)
    y += HEAD - 8
    for i, suf in enumerate(SUFFIX):
        fs = sorted((HERE / "concepts").glob(f"{key}*-{suf}.png"))
        im = Image.open(fs[0]).convert("RGB")
        im = im.resize((CW, int(CW * im.height / im.width)), Image.LANCZOS)
        x = PAD + i * (CW + PAD)
        sheet.paste(im, (x, y))
        d.text((x + 8, y + im.height + 2), caps[i], font=font(13), fill=MUTED)
    y += CH + 24 + PAD
d.text((PAD, y), "Giao diện web (mockup tĩnh, dữ liệu mẫu)", font=font(20, True), fill=PINE)
y += HEAD - 8
x = PAD
for path, cap in ui:
    im = Image.open(HERE / path).convert("RGB")
    sc = UI_H / im.height
    im = im.resize((int(im.width * sc), UI_H), Image.LANCZOS)
    sheet.paste(im, (x, y))
    d.rectangle((x, y, x + im.width, y + UI_H), outline="#D3DDD8")
    d.text((x, y + UI_H + 4), cap, font=font(13), fill=MUTED)
    x += im.width + PAD
sheet = sheet.crop((0, 0, W, y + UI_H + 30))
sheet.save(HERE / "contact-sheet.png")
print("OK", sheet.size)
