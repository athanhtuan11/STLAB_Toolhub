"""Tach chi tiet balo tu 3mf goc ra STL (toa do object balo, da cong offset component).
  python -I extract_parts.py <3mf> <thu muc ra> <objectid,...>
Vd: 16 = tam nhan trang; 26,34-40 = 8 chu ELEPHANT xam.
"""
import re, struct, sys, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
src, out = sys.argv[1], Path(sys.argv[2]); want = set(sys.argv[3].split(","))
out.mkdir(parents=True, exist_ok=True)
z = zipfile.ZipFile(src)
top = ET.fromstring(z.read("3D/3dmodel.model"))
off = {}
for o in top.iter(NS + "object"):
    if o.get("id") == "41":
        for c in o.iter(NS + "component"):
            off[c.get("objectid")] = np.array([float(x) for x in c.get("transform").split()[9:12]])
def save(path, v, t):
    tri = v[t]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(t), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", 9), ("a", "<u2")]))
    rec["n"], rec["v"] = n, tri.reshape(-1, 9)
    with open(path, "wb") as f:
        f.write(b"\0" * 80 + struct.pack("<I", len(t))); f.write(rec.tobytes())
with z.open("3D/Objects/object_12.model") as fh:
    verts, tris, oid = [], [], None
    for ev, el in ET.iterparse(fh, events=("start", "end")):
        t = el.tag.replace(NS, "")
        if ev == "start" and t == "object":
            oid, verts, tris = el.get("id"), [], []
        elif ev == "end" and t == "vertex" and oid in want:
            verts.append((float(el.get("x")), float(el.get("y")), float(el.get("z")))); el.clear()
        elif ev == "end" and t == "triangle" and oid in want:
            tris.append((int(el.get("v1")), int(el.get("v2")), int(el.get("v3")))); el.clear()
        elif ev == "end" and t == "object":
            if oid in want:
                v = np.array(verts) + off[oid]
                save(out / f"part-{oid}.stl", v, np.array(tris))
                print(oid, len(tris), v.min(0).round(3), v.max(0).round(3))
            el.clear()
