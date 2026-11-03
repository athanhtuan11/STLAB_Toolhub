"""contact-sheet-D.png: phuong an D (hop B + khung U tren de xoay C). Chay: python make_contact_sheet_d.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parents[2] / "studio" / "design" / "fonts"
BG, INK, MUTED, PINE = "#ECF1EF", "#16231D", "#56655E", "#1E5A45"


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ("BeVietnamPro-Bold.ttf" if bold else "BeVietnamPro-Regular.ttf")), size)


items = [("D-ghep-truoc", "Trước (3/4) – đầu vít M3 hai bên khung U"), ("D-ghep-sau", "Sau: khe nhiệt + cổng USB"),
         ("D-ghep-tile", "Cỡ so với ổ điện 86 × 86 mm"), ("D-ghep-conhieu", "Nghiêng −24° và xoay pan 35°"),
         ("D-ghep-no", "Tách rời: đế (chốt giữa + 3 tai ma sát) · đĩa xoay · đáy lật có 2 lỗ treo + vùng dán 3M")]
CW, CH, PAD = 520, 390, 18
W = 3 * CW + 4 * PAD
H = 60 + 2 * (CH + 40) + 2 * PAD
sh = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(sh)
d.rectangle((PAD, PAD + 4, PAD + 6, PAD + 34), fill="#E8B33A")
d.text((PAD + 16, PAD), "Phương án D – hộp B + khung U trên đế xoay (Tuan chọn 2026-11-03)", font=font(24, True), fill=INK)
d.text((PAD + 16, PAD + 32), "Khối minh họa, chưa phải CAD. Màu chỉ để tham khảo. Khối mạch ước 27 × 40,5 × 20–25 mm (số cộng đồng, research-notes mục 5).", font=font(14), fill=MUTED)
for i, (k, cap) in enumerate(items):
    im = Image.open(HERE / "concepts" / f"{k}.png").convert("RGB")
    im = im.resize((CW, int(CW * im.height / im.width)), Image.LANCZOS)
    x = PAD + (i % 3) * (CW + PAD)
    y = 70 + (i // 3) * (CH + 40)
    sh.paste(im, (x, y))
    d.text((x + 6, y + im.height + 3), cap, font=font(13), fill=MUTED)
x, y = PAD + 2 * (CW + PAD), 70 + CH + 40
d.rectangle((x, y, x + CW, y + CH), fill="#FBFCFB", outline="#D3DDD8")
lines = ["Cơ cấu xoay (pan)", "", "• Chốt giữa Ø8 trên đế, đĩa xoay lồng vào", "  lỗ giữa; đĩa nằm trong lõm Ø77 của đế.",
         "• Ma sát: 3 tai đàn hồi dưới đĩa tì lên", "  rãnh/nấc ở đế (khe lấy từ fit-library).",
         "• Giữ đĩa: nắp nhấn (snap) hoặc 1 vít –", "  quyết khi dựng CAD. Không support.", "",
         "Nghiêng (tilt): vít M3 + đai ốc/insert,", "ma sát; chiều dài vít, kiểu đai ốc, khe lỗ:", "lấy từ fit-library khi CAD.", "",
         "Treo tường: đáy đế 2 lỗ khóa + dán 3M;", "khung U vẫn thẳng."]
for i, t in enumerate(lines):
    d.text((x + 16, y + 16 + i * 24), t, font=font(15, i == 0), fill=PINE if i == 0 else INK)
sh.save(HERE / "contact-sheet-D.png")
print("OK", sh.size)
