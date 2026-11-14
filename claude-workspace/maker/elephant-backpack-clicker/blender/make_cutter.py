"""Sinh khoi cat (cutter) de goi chu noi ELEPHANT tren tam nhan balo.

Day khoi cat = mat tam nhan noi suy tu chinh luoi (khong fit), tru 0,02 mm,
nen sau khi cat mat tam nhan gan nhu nguyen ven (khong de lai bac).
Chay bang venv tools/model-study (trimesh + scipy):
  python -I make_cutter.py <backpack.stl> <cutter.stl> <info.json>
"""
import json, sys
import numpy as np, trimesh
from scipy.interpolate import griddata

src, out, info_path = sys.argv[1:4]
m = trimesh.load(src)
c0 = (m.bounds[0] + m.bounds[1]) / 2
off = np.array([c0[0], c0[1], 0.0])          # toa do tuong doi tam balo (xy)
n = m.face_normals
fc = m.triangles_center - off

# Chu noi: mat tren phang z ~ 34.18, nam tren tam nhan y < -15
top_z = float(m.bounds[1][2])
letter = (n[:, 2] > 0.999) & (fc[:, 2] > top_z - 0.02) & (fc[:, 1] < -15)
lv = m.vertices[np.unique(m.faces[letter])] - off
lmin, lmax = lv.min(0), lv.max(0)

# Mat tam nhan (giua cac chu): mat huong len, thap hon dinh chu > 0.3 mm
plate = (n[:, 2] > 0.95) & (np.abs(fc[:, 0]) < 20) & (fc[:, 1] < -17) & (fc[:, 1] > -31) \
        & (fc[:, 2] > top_z - 1.2) & (fc[:, 2] < top_z - 0.3)
pv = m.vertices[np.unique(m.faces[plate])] - off
pmin, pmax = pv.min(0), pv.max(0)

margin = 0.35
x0, x1 = lmin[0] - margin, lmax[0] + margin
y0, y1 = lmin[1] - margin, lmax[1] + margin
nx, ny = 80, 30
gx, gy = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
zl = griddata(pv[:, :2], pv[:, 2], (gx, gy), method="linear")
zn = griddata(pv[:, :2], pv[:, 2], (gx, gy), method="nearest")
zb = np.where(np.isnan(zl), zn, zl) - 0.02
zt = top_z + 1.0

# Luoi kin: mat day theo zb, mat tren phang zt, 4 vach
idx = lambda i, j: j * nx + i
V = [(gx.flat[k], gy.flat[k], zb.flat[k]) for k in range(nx * ny)]
V += [(gx.flat[k], gy.flat[k], zt) for k in range(nx * ny)]
T = nx * ny
F = []
for j in range(ny - 1):
    for i in range(nx - 1):
        a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
        F += [(a, c, b), (a, d, c)]                  # day (huong xuong)
        F += [(a + T, b + T, c + T), (a + T, c + T, d + T)]  # dinh
ring = [idx(i, 0) for i in range(nx)] + [idx(nx - 1, j) for j in range(1, ny)] \
     + [idx(i, ny - 1) for i in range(nx - 2, -1, -1)] + [idx(0, j) for j in range(ny - 2, 0, -1)]
for k in range(len(ring)):
    a, b = ring[k], ring[(k + 1) % len(ring)]
    F += [(a, b, b + T), (a, b + T, a + T)]
cut = trimesh.Trimesh(np.array(V) + off, np.array(F), process=True)
cut.fix_normals()
assert cut.is_watertight and cut.volume > 0, "cutter khong kin"
cut.export(out)
info = dict(offset=off.tolist(), top_z=top_z,
            letters_min=lmin.tolist(), letters_max=lmax.tolist(),
            plate_min=pmin.tolist(), plate_max=pmax.tolist(),
            plate_z_range=[float(pv[:, 2].min()), float(pv[:, 2].max())],
            cutter_xy=[x0, x1, y0, y1])
json.dump(info, open(info_path, "w"), indent=1)
print(json.dumps(info, indent=1))
