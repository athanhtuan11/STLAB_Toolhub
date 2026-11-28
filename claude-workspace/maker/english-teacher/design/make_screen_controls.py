"""Mockup man cam ung co nut dieu khien cho Cu Bong (320 x 240) - 2026-11-29, Tuan: be dung, nut luon hien.
Chuc nang: am luong +/-, qua bai / lui bai / doi chu de, tat (ngu) / bat phien. 2026-11-29 Tuan bo man thong tin may.
Ra: concepts/controls-*.png + contact-sheet-controls.png. Emoji Segoe chi minh hoa (ban that: Twemoji CC-BY nhu the chu).
Chay: python make_screen_controls.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

import make_screen_literacy as L
from make_screen_literacy import K, W, H, BG, CARD, INK, BLUE, YEL, PINK, GREEN, ORANGE, LBL, f, emoji, mini_eyes, card, touch_ring

HERE = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(HERE, 'concepts')
BTN, BTN_ON, DIM = '#1E2A40', '#2C3D5E', '#5A6273'
VOL_MAX = 80          # tran am luong cho tai be (firmware) - TODO chot so cung Tuan


def eyes(d, cx, cy, r, col, look='open'):
    for ex in (cx - r * 1.55, cx + r * 1.55):
        x, y, rr = ex * K, cy * K, r * K
        if look == 'sleep':
            d.arc([x - rr, y - rr * .6, x + rr, y + rr * .6], 20, 160, fill=col, width=5 * K)
        elif look == 'happy':
            d.arc([x - rr, y - rr * .4, x + rr, y + rr * 1.4], 205, 335, fill=col, width=6 * K)
        else:
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
            d.ellipse([x - rr * .5, y - rr * .5 + 3 * K, x + rr * .5, y + rr * .5 + 3 * K], fill='#14203A')
            d.ellipse([x + rr * .25, y - rr * .6, x + rr * .6, y - rr * .25], fill='white')


def btn(d, x, y, w, h, icon, col=BTN, px=26, ring=None, sign=None):
    d.rounded_rectangle([x * K, y * K, (x + w) * K, (y + h) * K], 14 * K, fill=col,
                        outline=ring, width=3 * K if ring else 0)
    if sign is None:
        emoji(d, icon, x + w / 2, y + h / 2, px)
    else:   # loa nho ben trai + dau +/- to ben phai (be phan biet bang dau, khong bang so song)
        emoji(d, icon, x + w * .32, y + h / 2, px * .7)
        cx, cy, a, t = (x + w * .72) * K, (y + h / 2) * K, 9 * K, 3 * K
        d.rounded_rectangle([cx - a, cy - t, cx + a, cy + t], t, fill='white')
        if sign == '+':
            d.rounded_rectangle([cx - t, cy - a, cx + t, cy + a], t, fill='white')


def vol_bar(d, x, y, h, level, big=False):
    """Thanh doc: 5 vach, vach cao nhat = tran VOL_MAX."""
    n = 5; on = round(level / VOL_MAX * n)
    gap = 3; bh = (h - gap * (n - 1)) / n; w = 22 if big else 10
    for i in range(n):
        y1 = y + h - i * (bh + gap); y0 = y1 - bh
        col = [GREEN, GREEN, YEL, YEL, ORANGE][i] if i < on else '#2A3448'
        d.rounded_rectangle([x * K, y0 * K, (x + w) * K, y1 * K], 3 * K, fill=col)


def side_buttons(d, level=50, active=None, dim=False):
    """Bo cuc A: cot trai am luong, cot phai bai hoc, goc tren phai thong tin, goc duoi phai ngu."""
    c = lambda k: BTN_ON if active == k else (BTN if not dim else '#151C2B')
    btn(d, 6, 8, 56, 56, '\U0001F508', c('up'), sign='+')
    vol_bar(d, 28, 72, 92, level)
    btn(d, 6, 176, 56, 56, '\U0001F508', c('down'), sign='-')
    btn(d, 258, 8, 56, 56, '⏭️', c('next'))     # qua bai
    btn(d, 258, 70, 56, 56, '\U0001F4DA', c('topic'))     # doi chu de
    btn(d, 258, 132, 56, 40, '⏮️', c('prev'), px=20)   # lui bai (nho hon, it dung)
    btn(d, 258, 186, 56, 46, '\U0001F319', c('sleep'), px=24)    # ngu


def screen(name):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    if name == 'a-home':                  # Man chinh: mat o giua, nut 2 ben
        side_buttons(d, 50)
        eyes(d, 160, 112, 34, BLUE)
    elif name == 'b-volume':              # Cham + : thanh am luong lon hien 1,5 s, mat cuoi
        side_buttons(d, 70, active='up')
        eyes(d, 160, 80, 26, YEL, 'happy')
        vol_bar(d, 149, 120, 100, 70, big=True)
        touch_ring(d, 34, 36)
    elif name == 'c-vol-max':             # Cham + khi da o tran: vach cam nhap nhay, khong to them
        side_buttons(d, VOL_MAX, active='up')
        eyes(d, 160, 80, 26, ORANGE)
        vol_bar(d, 149, 120, 100, VOL_MAX, big=True)
        d.text((200 * K, 170 * K), 'MAX', font=f(LBL, 12), fill=ORANGE, anchor='mm')
        touch_ring(d, 34, 36)
    elif name == 'd-next-confirm':        # Cham qua bai: hoi lai bang hinh, be cham V hoac X (chong cham loan)
        side_buttons(d, 50, active='next', dim=True)
        mini_eyes(d, 26, BLUE)
        card(d, 70, 50, 250, 150)
        emoji(d, '\U0001F431', 125, 100, 44); emoji(d, '➡️', 160, 100, 22); emoji(d, '\U0001F34E', 195, 100, 44)
        d.text((160 * K, 138 * K), 'Bài mới?', font=f(LBL, 14), fill=INK, anchor='mm')
        btn(d, 76, 162, 76, 66, '✅', '#24543A', px=34)
        btn(d, 168, 162, 76, 66, '❌', '#5A2A2A', px=30)
    elif name == 'e-topic':               # Doi chu de: luoi 2 x 3 the chu de (hinh to, chu nho cho nguoi lon)
        mini_eyes(d, 20, BLUE)
        topics = [('\U0001F44B', 'Hello'), ('\U0001F3E0', 'Family'), ('\U0001F3A8', 'Colours'),
                  ('\U0001F436', 'Animals'), ('\U0001F34E', 'Food'), ('\U0001F333', 'Outside')]
        for i, (e, t) in enumerate(topics):
            x = 12 + (i % 3) * 100; y = 42 + (i // 3) * 96
            card(d, x, y, x + 92, y + 88, border=YEL if i == 3 else None, bw=4)
            emoji(d, e, x + 46, y + 38, 36)
            d.text(((x + 46) * K, (y + 76) * K), t, font=f(LBL, 11), fill=INK, anchor='mm')
        touch_ring(d, 158, 180)
        d.text((300 * K, 20 * K), '✕', font=f(LBL, 16), fill='#8FA3BF', anchor='mm')
    elif name == 'f-sleep-hold':          # Cham trang: GIU 2 s (vong chay) moi ngu - chong cham nham
        side_buttons(d, 50, active='sleep')
        eyes(d, 160, 112, 34, '#8E7CC3', 'sleep')
        x, y, r = 286 * K, 209 * K, 30 * K
        d.arc([x - r, y - r, x + r, y + r], -90, 150, fill=PINK, width=5 * K)
        touch_ring(d, 286, 209)
    elif name == 'g-asleep':              # Dang ngu: man toi, chi nut Bat to o giua (cham = bat phien)
        eyes(d, 160, 90, 30, '#4A3F6B', 'sleep')
        btn(d, 110, 150, 100, 70, '▶️', '#24543A', px=36)
    elif name == 'h-info':                # Thong tin may (nguoi lon), cham bat ky dau de dong
        mini_eyes(d, 20, BLUE)
        card(d, 20, 40, 300, 228, fill='#F4EFE6')
        rows = [('Wi-Fi', 'STLab'), ('Máy chủ', '192.168.1.56  OK'), ('Phiên bản', '2.5.2.9'),
                ('Bé', 'kay'), ('Bài', 's2-u1 How are you'), ('Âm lượng', '50 / tối đa 80')]
        for i, (k, v) in enumerate(rows):
            y = 62 + i * 27
            d.text((36 * K, y * K), k, font=f(LBL, 12), fill='#5A6273', anchor='lm')
            d.text((130 * K, y * K), v, font=f(LBL, 13), fill=INK, anchor='lm')
    elif name == 'i-card-with-buttons':   # Dang hien the chu: chi giu am luong (nho), cac nut khac an de khong che the
        btn(d, 4, 8, 44, 44, '\U0001F508', px=22, sign='+'); btn(d, 4, 188, 44, 44, '\U0001F508', px=22, sign='-')
        mini_eyes(d, 26, YEL)
        card(d, 52, 52, 300, 232)
        emoji(d, '\U0001F431', 176, 108, 60)
        L.word(d, 'cat', 176, 190, 46)
    return im


NAME = {
    'a-home': ('A. Màn chính', 'Trái: âm lượng. Phải: qua bài, chủ đề, lùi bài, ngủ'),
    'b-volume': ('B. Chạm âm lượng', 'Mỗi chạm ±30, hiện vạch to 1,5 s, mắt cười'),
    'c-vol-max': ('C. Chạm khi đã tối đa', 'Không to thêm (trần tai bé, TODO số), vạch cam nháy'),
    'd-next-confirm': ('D. Chạm qua bài', 'Hỏi lại bằng hình: xanh = đồng ý, đỏ = thôi'),
    'e-topic': ('E. Đổi chủ đề', 'Lưới thẻ hình to; chạm thẻ = Cú chuyển bài'),
    'f-sleep-hold': ('F. Chạm nút trăng', 'GIỮ 2 s (vòng chạy) mới ngủ; chạm nhanh không tính'),
    'g-asleep': ('G. Đang ngủ', 'Màn tối, nút chạy to giữa: chạm = bật phiên'),
    'i-card-with-buttons': ('I. Khi hiện thẻ chữ', 'Chỉ giữ âm lượng, ẩn nút bài để không che thẻ'),
}

if __name__ == '__main__':
    os.makedirs(C, exist_ok=True)
    tiles = []
    for n in NAME:
        im = screen(n); im.save(os.path.join(C, f'controls-{n}.png')); tiles.append((n, im))
    TW, TH, PAD, LH = 400, 300, 16, 58
    sheet = Image.new('RGB', (3 * TW + 4 * PAD, 3 * (TH + LH) + 4 * PAD + 50), '#F4EFE6')
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 14), 'Cú Bông – màn cảm ứng có nút điều khiển (mockup 320×240, chờ duyệt)', font=ImageFont.truetype(LBL, 24), fill='#22304A')
    for i, (n, im) in enumerate(tiles):
        x = PAD + (i % 3) * (TW + PAD); y = 50 + PAD + (i // 3) * (TH + LH + PAD)
        sheet.paste(im.resize((TW, TH), Image.LANCZOS), (x, y))
        t, s = NAME[n]
        d.text((x, y + TH + 6), t, font=ImageFont.truetype(LBL, 19), fill='#22304A')
        d.text((x, y + TH + 32), s, font=ImageFont.truetype(LBL, 13), fill='#5A6273')
    sheet.save(os.path.join(HERE, 'contact-sheet-controls.png'))
    print('ok', sheet.size)
