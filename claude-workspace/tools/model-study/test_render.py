# Gate cho render.py (z-buffer) – Claude viet, executor KHONG sua file nay.
#   python test_render.py
import os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from render import render_iso  # noqa: E402


def cube(n):
    """Lap phuong 20 mm, moi mat chia n x n o (2 tam giac/o) -> 12 n^2 tam giac, tam giac (k,3,3) mm."""
    g = np.linspace(-10, 10, n + 1)
    faces = []
    for ax in range(3):
        for s in (-10.0, 10.0):
            for i in range(n):
                for j in range(n):
                    q = [(g[i], g[j]), (g[i + 1], g[j]), (g[i + 1], g[j + 1]), (g[i], g[j + 1])]
                    p = []
                    for a, b in q:
                        v = [0.0, 0.0, 0.0]
                        v[ax], v[(ax + 1) % 3], v[(ax + 2) % 3] = s, a, b
                        p.append(v)
                    if s < 0:
                        p = p[::-1]
                    faces += [[p[0], p[1], p[2]], [p[0], p[2], p[3]]]
    return np.array(faces, float)


lo, hi = cube(1), cube(92)  # 12 vs ~101k tam giac
assert len(hi) > 100000
t = time.time()
a = render_iso(lo, 360)
b = render_iso(hi, 360)
dt = time.time() - t
for img in (a, b):
    assert img.shape == (360, 360, 3) and img.dtype == np.uint8, (img.shape, img.dtype)
ma = (a < 250).any(axis=2)
mb = (b < 250).any(axis=2)
iou = (ma & mb).sum() / (ma | mb).sum()
print("iou %.4f  render %.1f s  phu %.2f" % (iou, dt, ma.mean()))
assert 0.15 < ma.mean() < 0.85, "hinh qua nho/qua lon trong khung"
assert iou > 0.99, "luoi day bi thung/khac luoi thua (khong duoc lay mau con tam giac)"
# khong co lo trang ben trong silhouette luoi day
ys, xs = np.nonzero(mb)
inner = mb[ys.min() + 8:ys.max() - 8, xs.min() + 8:xs.max() - 8]
assert inner.mean() > 0.97 or (mb == ma).mean() > 0.995, "co diem trang ben trong lap phuong"
# 3 mat nhin thay phai co 3 do sang khac nhau (do bong theo phap tuyen)
lum = b.astype(float).mean(axis=2)[mb]
levels = np.unique(np.round(lum / 8))
assert len(levels) >= 3, "can >= 3 muc sang cho 3 mat"
assert np.abs(a.astype(int) - b.astype(int)).max(axis=2)[ma & mb].mean() < 6, "mau luoi day khac luoi thua"
assert dt < 20, "render qua cham"
print("gate render OK")
