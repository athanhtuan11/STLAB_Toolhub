# Render anh 3D tu shape FreeCAD bang matplotlib - chay trong freecadcmd (KHONG GUI).
# Tuan 2026-10-25: "mac dinh chay FreeCAD CLI de khong bi crash" -> anh duyet/concept render bang file nay thay saveImage GUI.
#   import sys; sys.path.insert(0, ".../tools/robotics-cad/scripts"); from mpl_render import render
#   render([(shape, (r, g, b)), (shape2, (r, g, b), 0.4)], "out.png", view="iso"|"front"|"top"|(elev, azim), fit=[shapes])
# Chieu truc giao, to bong Lambert, ve ca tam giac 1 lan (sap xep do sau tung tam giac -> dung thu tu che khuat).
# "front" = nhin tu -Y (giong FreeCAD viewFront), "iso" ~ viewIsometric.
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

VIEWS = {"iso": (35.264, -45.0), "front": (0.0, -90.0), "top": (90.0, -90.0), "rear": (0.0, 90.0)}


def _tris(shape, tol):
    pts, tris = shape.tessellate(tol)
    return [[(pts[i].x, pts[i].y, pts[i].z) for i in t] for t in tris]


def render(items, out, view="iso", fit=None, size=(1400, 1000), tol=0.15, title=None, light=(0.35, -0.6, 0.72),
           edge=False):
    """items: [(shape, rgb) | (shape, rgb, alpha)]; fit: shapes dung de can khung (mac dinh = tat ca)."""
    elev, azim = VIEWS.get(view, view) if isinstance(view, str) else view
    fig = plt.figure(figsize=(size[0] / 100, size[1] / 100), dpi=100)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_proj_type("ortho")
    polys, cols = [], []
    ln = math.sqrt(sum(c * c for c in light)); L = [c / ln for c in light]
    for it in items:
        shape, rgb = it[0], it[1]; alpha = it[2] if len(it) > 2 else 1.0
        for t in _tris(shape, tol):
            a, b, c = t
            n = ((b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1]),
                 (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2]),
                 (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
            nn = math.sqrt(sum(k * k for k in n)) or 1.0
            k = abs(sum(n[i] / nn * L[i] for i in range(3))) * 0.65 + 0.35
            polys.append(t); cols.append((rgb[0] * k, rgb[1] * k, rgb[2] * k, alpha))
    pc = Poly3DCollection(polys, facecolors=cols, edgecolors=(0.1, 0.1, 0.1, 0.25) if edge else "none", linewidths=0.2)
    ax.add_collection3d(pc)
    bbs = [s.BoundBox for s in (fit or [it[0] for it in items])]
    lo = [min(getattr(b, a + "Min") for b in bbs) for a in "XYZ"]
    hi = [max(getattr(b, a + "Max") for b in bbs) for a in "XYZ"]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]; r = max(hi[i] - lo[i] for i in range(3)) / 2 * 1.05
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev, azim); ax.set_axis_off()
    if title: ax.set_title(title, fontsize=14)
    fig.subplots_adjust(0, 0, 1, 0.95 if title else 1)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out
