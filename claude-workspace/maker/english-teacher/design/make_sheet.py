"""Ghep contact-sheet.png (~1600 px rong) tu concepts/*.png - nhan tieng Viet + kich thuoc.
Chay: python make_sheet.py   (khong can Blender)"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(HERE, 'concepts')
FONTS = os.path.join(HERE, '..', '..', '..', 'studio', 'design', 'fonts')
F = lambda w, s: ImageFont.truetype(os.path.join(FONTS, 'BeVietnamPro-%s.ttf' % w), s)

INK = '#16231D'
BG = '#FBF6EE'
CARD = '#FFFFFF'

CONCEPTS = [
    dict(key='a-cu-bong', tag='A', name='Cú Bông', sub='con vật tròn – cú',
         dim='142 × 116 × 175 mm  (≈ 1,8 lần ly)',
         sw=[('#F6BE9A', 'mơ (thân)'), ('#FFF3DF', 'kem (bụng, viền mắt)'), ('#FFC857', 'bơ (mỏ, nút)')],
         pts=['Không màn hình: 2 mắt = đèn LED RGB mềm, đổi màu theo trạng thái',
              'Nút "nói" Ø50 mm trên đỉnh đầu; loa ở bụng; 3 lỗ micro trán',
              'Rẻ nhất, bền nhất; thu nhỏ bản 2 dễ (bỏ màn hình sẵn)']),
    dict(key='b-trung-bi', tag='B', name='Trứng Bi', sub='robot tròn kiểu "trứng"',
         dim='146 × 120 × 177 mm  (≈ 1,9 lần ly)',
         sw=[('#BFE6D5', 'bạc hà (vỏ)'), ('#FFF3E2', 'kem (đế, tay)'), ('#27364A', 'xanh đêm (mặt kính)'), ('#FF8F85', 'san hô (nút)')],
         pts=['CÓ màn hình 2,4" (cửa sổ 49 × 37 mm, TODO chọn module): mặt biểu cảm',
              'Đắt hơn + thêm firmware vẽ mặt; bé dễ nhìn chằm màn hình',
              'Nhìn "robot" nhất; 4 màu (đế + tay kem, kính tối)']),
    dict(key='c-ban-tai-nghe', tag='C', name='Bạn Tai Nghe', sub='nhân vật đeo tai nghe',
         dim='152 × 110 × 147 mm  (≈ 1,5 lần ly)',
         sw=[('#D7C6F3', 'tím lilac (thân)'), ('#FFDF86', 'vàng bơ (tai nghe)'), ('#FFF3DF', 'kem (miệng, viền mắt)'), ('#FF9DBB', 'hồng (nút)')],
         pts=['Không màn hình: mắt + vòng sáng tai nghe + vòng miệng',
              'Tai phải sáng = đang NGHE, miệng sáng = đang NÓI (bé hiểu ngay)',
              'Loa là cái "miệng"; thấp, vững, khó đổ nhất']),
]
STATES = [('listen', 'Nghe · xanh dương'), ('speak', 'Nói · vàng'), ('praise', 'Khen · hồng'), ('sleep', 'Ngủ · tím mờ')]

W, PAD = 1600, 25
CW = (W - 4 * PAD) // 3        # 500
H_TXT, SH = 270, 245


def fit(img, w, h):
    img = img.convert('RGB')
    r = min(w / img.width, h / img.height)
    return img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)


def wrap(d, text, font, width):
    out, cur = [], ''
    for w_ in text.split(' '):
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            out.append(cur)
            cur = w_
    out.append(cur)
    return out


def main():
    top = 100
    h_hero, h_back = CW, 330
    states_h = 2 * (SH + 26) + 8
    H = top + h_hero + H_TXT + states_h + h_back + 40 + 130
    sheet = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 22), 'english-teacher – 3 concept dáng sản phẩm (bước 0 giao diện)', font=F('Bold', 34), fill=INK)
    d.text((PAD, 66), 'Bé 2–5 tuổi · bo Ai-Thinker ESP32-A1S Audio Kit + loa Ø52 mm · bo cạnh R ≥ 3 mm · vít giấu đáy · nút to · render Blender Cycles',
           font=F('Regular', 18), fill='#4A5A52')
    for i, c in enumerate(CONCEPTS):
        x0 = PAD + i * (CW + PAD)
        y = top
        d.rounded_rectangle((x0 - 8, y - 8, x0 + CW + 8, H - 138), 18, fill=CARD)
        sheet.paste(fit(Image.open(os.path.join(C, c['key'] + '-hero.png')), CW, h_hero), (x0, y))
        d.rounded_rectangle((x0 + 8, y + 8, x0 + 52, y + 52), 12, fill='#C2577E')
        d.text((x0 + 30, y + 30), c['tag'], font=F('Bold', 28), fill='white', anchor='mm')
        y += h_hero + 6
        d.text((x0, y), c['name'], font=F('Bold', 30), fill=INK)
        d.text((x0 + d.textlength(c['name'], font=F('Bold', 30)) + 12, y + 10), c['sub'], font=F('Regular', 17), fill='#4A5A52')
        y += 42
        d.text((x0, y), 'Cỡ: ' + c['dim'], font=F('SemiBold', 18), fill='#1E5A45')
        y += 30
        sx = x0
        for hx, lb in c['sw']:
            wlb = 28 + int(d.textlength(lb, font=F('Regular', 13))) + 12
            if sx + wlb > x0 + CW + 6:
                sx = x0
                y += 26
            d.rounded_rectangle((sx, y, sx + 22, y + 22), 6, fill=hx, outline='#B9C2BD')
            d.text((sx + 28, y + 3), lb, font=F('Regular', 13), fill=INK)
            sx += wlb
        y += 34
        for p in c['pts']:
            ls = wrap(d, p, F('Regular', 15), CW - 18)
            d.text((x0, y), '•', font=F('Regular', 15), fill=INK)
            for ln in ls:
                d.text((x0 + 14, y), ln, font=F('Regular', 15), fill=INK)
                y += 19
            y += 3
        y = top + h_hero + H_TXT
        for k, (st, lb) in enumerate(STATES):
            im = fit(Image.open(os.path.join(C, '%s-state-%s.png' % (c['key'], st))), SH, SH)
            xx = x0 + (k % 2) * (SH + 10)
            yy = y + (k // 2) * (SH + 26)
            sheet.paste(im, (xx, yy))
            d.text((xx + 6, yy + SH + 2), lb, font=F('SemiBold', 15), fill=INK)
        y += states_h
        d.text((x0, y - 4), 'Mặt lưng: cổng USB (cáp 1 m) + 5 khe thoát nhiệt', font=F('SemiBold', 15), fill=INK)
        sheet.paste(fit(Image.open(os.path.join(C, c['key'] + '-back.png')), CW, h_back - 20), (x0, y + 18))
    y = H - 122
    notes = ['Thước đo trong ảnh: ly Ø80 × 95 mm và sách tranh 200 × 200 mm. Mọi số kích thước là ƯỚC LƯỢNG theo khối giả định (bo Audio Kit ≈ 75 × 65 × 25 mm và loa Ø52 × 20 mm: TODO đo bo thật).',
             'Hình chỉ để duyệt dáng/màu: lưới loa vẽ bằng chấm tối (bản in thật: lỗ Ø2,8 mm, bước 5,6 mm), đèn LED qua nắp khuếch tán 0,8 mm; màu nhựa thật TODO khớp cuộn Bambu PETG Basic.',
             'Khuyến nghị: A (Cú Bông) cho bản 1; B nếu Tuan muốn "mặt biểu cảm" ở bản 2 có màn hình; C hợp bé 4–5 tuổi thích nhân vật.']
    for n in notes:
        for ln in wrap(d, n, F('Regular', 15), W - 2 * PAD):
            d.text((PAD, y), ln, font=F('Regular', 15), fill='#4A5A52')
            y += 20
        y += 3
    sheet.save(os.path.join(HERE, 'contact-sheet.png'), optimize=True)
    print('OK', sheet.size)


if __name__ == '__main__':
    main()
