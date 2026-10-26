# CONCEPT than GT bo tron (Tuan 2026-10-26: "GT bo tron" + "kinh khac chim") - CHI dung vo ngoai + render, KHONG luu FCStd.
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" freecad/scripts/concept_gt_body.py
# Ra: freecad/images/concept-gt/*.png. Duyet xong moi dua section_gt() + cua kinh vao build_car.py.
# Mat cat moi: nua tren = B-spline (suon dung toi vai zb -> vai bo tron -> kinh nghieng vao -> mep mai wr -> dinh h)
# thay vom sieu-ellipse cu (vom tu giua suon len mai -> than tron nhu vien thuoc, khong co duong vai).
import math, os, sys
import FreeCAD as App, Part

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJ, "..", "..", "tools", "robotics-cad", "scripts"))
from mpl_render import render  # noqa: E402

V = App.Vector
OUT = os.path.join(PROJ, "freecad", "images", "concept-gt")
os.makedirs(OUT, exist_ok=True)

# cung so voi build_car.py (P, ST) - concept khong doi kich thuoc tong
WR, FX, Z0 = 16.8, 140.0, 4.0 + 2.4 + 0.2
ST = [(-41.5, 24, 17, 21.0, 19), (-35, 30, 22, 26.0, 25), (-28, 36, 27, 31.5, 31), (-21, 42, 33, 37.0, 36.5),
      (0, 44, 39, 42.0, 40), (18, 44, 37.5, 45, 31),
      (38, 43.5, 37, 55, 26), (66, 43.5, 37, 56, 26), (88, 43.5, 37, 48, 30), (108, 43.5, 37.5, 41.0, 37),
      (FX, 43.5, 39.5, 43.0, 40), (FX + 20, 42, 34, 36.0, 37),
      (FX + 39, 26, 16.5, 19.0, 21), (FX + 41, 17, 13.5, 15.5, 13)]
WIN_D = 0.4          # sau khac kinh (vo 1,3 -> con 0,9 = 2 duong Bambu 0,42 + 0,45)


def section_old(x, w, zb, h, wr, z0, t=0.0, n=48):
    w, zb, h, wr = w - t, zb - t, h - t, wr - t
    zc = (z0 + zb) / 2.0
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        if sa < 0:
            y = w * math.copysign(abs(ca) ** (2 / 6.0), ca)
            z = zc - (zc - z0) * abs(sa) ** (2 / 6.0)
        else:
            k = 1.0 - min(wr, w) / w
            y = w * math.copysign(abs(ca) ** (2 / 3.2), ca) * (1.0 - k * sa ** 4)
            z = zc + (h - zc) * sa ** (2 / 3.5)
        pts.append(V(x, y, z))
    bs = Part.BSplineCurve()
    bs.interpolate(pts, PeriodicFlag=True)
    return Part.Wire(bs.toShape())


def upper_curve(w, zb, h, wr, zc):
    """1/4 tren phai (y >= 0): (w, zc) -> suon dung -> vai bo -> kinh nghieng -> mep mai (wr) -> dinh (0, h)."""
    wr = min(wr, w - 1.0)
    sh = min(1.4, max(0.6, (h - zb) * 0.2))                                  # ban kinh vai (thap o vom chan bun)
    poles = [V(w, zc, 0), V(w, zb - sh, 0), V(w - 0.3, zb + sh * 0.6, 0),
             V(wr + 1.5, h - 2.5, 0), V(wr * 0.55, h, 0), V(0, h, 0)]
    bs = Part.BSplineCurve()
    bs.buildFromPoles(poles, False, 3)
    return bs


def section_gt(x, w, zb, h, wr, z0, t=0.0, n=48):
    w, zb, h, wr = w - t, zb - t, h - t, wr - t
    zc = (z0 + zb) / 2.0
    uc = upper_curve(w, zb, h, wr, zc)
    u0, u1 = uc.FirstParameter, uc.LastParameter
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        if sa < 0:                                                           # nua duoi giu nguyen (san, hoc banh)
            y = w * math.copysign(abs(ca) ** (2 / 6.0), ca)
            z = zc - (zc - z0) * abs(sa) ** (2 / 6.0)
        else:
            f = (a if ca >= 0 else math.pi - a) / (math.pi / 2)              # 0 o suon -> 1 o dinh
            p = uc.value(u0 + (u1 - u0) * min(max(f, 0.0), 1.0))
            y, z = math.copysign(p.x, ca) if abs(ca) > 1e-9 else 0.0, p.y
        pts.append(V(x, y, z))
    bs = Part.BSplineCurve()
    bs.interpolate(pts, PeriodicFlag=True)
    return Part.Wire(bs.toShape())


def loft(fn, t=0.0, z0=Z0, st=ST):
    return Part.makeLoft([fn(x, w, zb, h, wr, z0, t) for x, w, zb, h, wr in st], True, False)


def lerp_st(x, k):
    """noi suy cot k cua ST theo x"""
    for (xa, *a), (xb, *b) in zip(ST, ST[1:]):
        if xa <= x <= xb:
            f = (x - xa) / (xb - xa)
            return a[k - 1] + (b[k - 1] - a[k - 1]) * f
    return None


def rounded(pts_xy, r, plane):
    """da giac -> mat bo goc r. plane 'xz' (dun theo Y) hoac 'xy' (dun theo Z)."""
    vs = [V(p[0], 0, p[1]) if plane == "xz" else V(p[0], p[1], 0) for p in pts_xy]
    f = Part.Face(Part.makePolygon(vs + [vs[0]]))
    return f.makeOffset2D(-r).makeOffset2D(r)


def windows():
    """3 dao kinh (lang tru) - giao voi lop da 0..WIN_D o mat ngoai -> vung khac chim."""
    # kinh hong: tu vai+2,5 toi mep mai-3,5 (theo x), A-pillar nghieng theo kinh lai
    xs = [x for x in range(26, 93, 2)]
    bot = [(x, lerp_st(x, 2) + 2.5) for x in xs]
    top = [(x, min(lerp_st(x, 3) - 3.5, 52.5)) for x in reversed(xs)]
    side = [p for p in bot + top if p[1] is not None]
    side = [p for p in side if True]
    fs = rounded(side, 2.5, "xz")
    side_l = fs.extrude(V(0, 70, 0))
    side_r = fs.extrude(V(0, -70, 0))
    # kinh lai: x 89..106, rong +-(wr - 4)
    ws_x = [89, 93, 97, 101, 105]
    ws = [(x, lerp_st(x, 4) - 5) for x in ws_x] + [(x, -(lerp_st(x, 4) - 5)) for x in reversed(ws_x)]
    fw = rounded(ws, 2.0, "xy")
    fw.translate(V(0, 0, 38))
    wind = fw.extrude(V(0, 0, 40))
    # kinh sau (fastback): x 4..34
    rw_x = [4, 10, 16, 22, 28, 34]
    rw = [(x, lerp_st(x, 4) - 7) for x in rw_x] + [(x, -(lerp_st(x, 4) - 7)) for x in reversed(rw_x)]
    fr = rounded(rw, 3.0, "xy")
    fr.translate(V(0, 0, 41))
    rear = fr.extrude(V(0, 0, 40))
    return side_l.fuse(side_r), wind, rear


FCSTD = os.path.join(PROJ, "freecad", "cyberbrick_car.FCStd")
doc = App.openDocument(FCSTD)                                                 # chi DOC: lay than cu + banh, khong luu
O = {o.Label: o.Shape for o in doc.Objects if hasattr(o, "Shape")}
old = O["Body_coupe"]
wheels = [O[k] for k in O if k.startswith(("CB_Tire_", "Wheel_"))]
App.closeDocument(doc.Name)
new = loft(section_gt)
skin_out = loft(section_gt, -1.0)                                            # loi ra 1 mm: dao khong trung mat vo
skin_in = loft(section_gt, WIN_D)
skin = skin_out.cut(skin_in)
cut_flat = Part.makeBox(400, 200, 20, V(-100, -100, Z0 - 20))
new = new.cut(cut_flat)
for x, r, dx in ((0, 18.3, 0), (FX, 18.8, 5.0)):                            # hoc banh nhu build_car.py (rear/front_arch_r)
    for sgn in (1, -1):
        y0, y1 = sorted((sgn * 25.0, sgn * 60.0))
        arch = Part.makeCylinder(r, y1 - y0, V(x - dx, y0, WR), V(0, 1, 0))
        if dx:
            arch = arch.fuse(Part.makeCylinder(r, y1 - y0, V(x + dx, y0, WR), V(0, 1, 0))).fuse(
                Part.makeBox(2 * dx, y1 - y0, 2 * r, V(x - dx, y0, WR - r)))
        new = new.cut(arch)
tools = windows()
glass = [skin.common(t) for t in tools]
eng = new
for g in glass:
    eng = eng.cut(g)
print("VALID new", new.isValid(), "engraved", eng.isValid(), "V", round(old.Volume), round(new.Volume),
      round(eng.Volume), "glass", [round(g.Volume, 1) for g in glass])

ORANGE, GLASS = (0.92, 0.35, 0.05), (0.18, 0.22, 0.30)
for view, tag in (("iso", "iso"), ((0.0, -90.0), "side"), ((20.0, 35.0), "front-34"), ((25.0, -150.0), "rear-34")):
    W = [(w, (0.15, 0.15, 0.15)) for w in wheels]
    render([(old, ORANGE)] + W, os.path.join(OUT, "before-%s.png" % tag), view=view, fit=[new], title="TRUOC (v0.2)")
    render([(eng, ORANGE)] + [(g, GLASS) for g in glass] + W, os.path.join(OUT, "after-%s.png" % tag), view=view, fit=[new],
           title="SAU: GT duong vai + kinh khac chim 0,4 mm (kinh to dam de de nhin; in 1 mau)")
# mat cat so sanh tai cabin x = 66
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
fig, axs = plt.subplots(1, 3, figsize=(15, 5))
for ax, xs in zip(axs, (18, 66, 120)):
    st = [s for s in ST if s[0] == xs] or [(xs, lerp_st(xs, 1), lerp_st(xs, 2), lerp_st(xs, 3), lerp_st(xs, 4))]
    x, w, zb, h, wr = st[0]
    for fn, c, lab in ((section_old, "0.6", "truoc"), (section_gt, "C1", "GT")):
        e = fn(x, w, zb, h, wr, Z0).Edges[0]
        pp = e.discretize(200)
        ax.plot([p.y for p in pp], [p.z for p in pp], color=c, label=lab)
    ax.axhline(Z0, color="k", lw=0.5); ax.set_aspect("equal"); ax.set_title("mat cat x = %d mm" % xs); ax.legend()
    ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "sections.png")); plt.close(fig)
print("OUT", OUT)
