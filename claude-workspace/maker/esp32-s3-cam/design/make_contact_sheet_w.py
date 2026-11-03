"""contact-sheet-W.png: mau W treo tuong. Chay: python make_contact_sheet_w.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parents[2] / "studio" / "design" / "fonts"
BG, INK, MUTED, PINE = "#ECF1EF", "#16231D", "#56655E", "#1E5A45"


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ("BeVietnamPro-Bold.ttf" if bold else "BeVietnamPro-Regular.ttf")), size)


items = [("W-treo-truoc", "Trước (3/4): hộp + khung U + đĩa + vành như D, đặt trên tay đỡ"), ("W-treo-ben", "Cạnh: tay đỡ nhô 70 mm, gân tăng cứng"),
         ("W-treo-tuong", "Trên mảng tường cạnh ổ điện 86 × 86 mm"), ("W-treo-no", "Tách rời: giá W · vành · đĩa+khung U · hộp")]
CW, CH, PAD = 520, 390, 18
W = 3 * CW + 4 * PAD
H = 70 + 2 * (CH + 40) + 2 * PAD
sh = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(sh)
d.rectangle((PAD, PAD + 4, PAD + 6, PAD + 34), fill="#E8B33A")
d.text((PAD + 16, PAD), "Mẫu W – treo tường (chung hộp + khung U với D, chỉ đổi đế bằng giá treo)", font=font(24, True), fill=INK)
d.text((PAD + 16, PAD + 32), "Khối minh họa, chưa phải CAD. Màu chỉ để tham khảo. Khối mạch ước 27 × 40,5 × 20–25 mm (research-notes mục 5–6).", font=font(14), fill=MUTED)
for i, (k, cap) in enumerate(items):
    im = Image.open(HERE / "concepts" / f"{k}.png").convert("RGB")
    im = im.resize((CW, int(CW * im.height / im.width)), Image.LANCZOS)
    x = PAD + (i % 3) * (CW + PAD)
    y = 70 + (i // 3) * (CH + 40)
    sh.paste(im, (x, y)); d.text((x + 6, y + im.height + 3), cap, font=font(13), fill=MUTED)
x, y = PAD + (CW + PAD), 70 + CH + 40
w2 = 2 * CW + PAD
d.rectangle((x, y, x + w2, y + CH), fill="#FBFCFB", outline="#D3DDD8")
L = ["Cơ cấu W", "",
     "• Tấm tường 70 × 130 mm: 2 vít đầu chìm (hoặc dán 3M mặt sau). Tay đỡ chữ L nhô 70 mm + gân.",
     "• Đầu tay đỡ có mâm Ø90: vành đế của D bắt lên bằng 2 vít (dùng lại 2 lỗ đáy) thành chốt giữ, đĩa xoay.",
     "• Pan quanh trục THẲNG ĐỨNG; tilt = vít M3 như D. Khe/ma sát: fit-library khi CAD.",
     "• Dây USB: kẹp trên tay đỡ thành dọc tường; chừa vòng dây, giới hạn pan (TODO) để không kéo dây.",
     "• Lật ngược (treo dưới kệ/mép trần): camera nằm dưới tay đỡ, firmware lật ảnh 180°.",
     "", "Dùng chung với D: hộp + khung mặt trước + khung U/đĩa + vành + 2 vít M3.",
     "Riêng W: giá treo (tấm tường + tay đỡ + mâm) + 2 kẹp dây."]
for i, t in enumerate(L):
    d.text((x + 16, y + 16 + i * 30), t, font=font(16, i == 0), fill=PINE if i == 0 else INK)
sh.save(HERE / "contact-sheet-W.png")
print("OK", sh.size)
