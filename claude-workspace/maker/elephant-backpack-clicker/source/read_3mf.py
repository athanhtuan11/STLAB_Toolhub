"""Doc 3mf Bambu cua mau Elephant clicky: tung chi tiet balo (bbox, so tam giac, dau nhua/mau), voi (paint_color).
  python -I read_3mf.py <thu muc 3mf da giai nen> <color-map.json>
Doc tuan tu (iterparse) de it RAM: file mesh 40-60 MB.
"""
import json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
root, out = Path(sys.argv[1]), sys.argv[2]
NS = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
proj = json.loads((root / "Metadata/project_settings.config").read_text(encoding="utf-8"))
colors = proj["filament_colour"]; fil = proj["filament_settings_id"]

# model_settings: extruder theo object/part
ms = ET.parse(root / "Metadata/model_settings.config").getroot()
obj_cfg = {}
for o in ms.iter("object"):
    meta = {m.get("key"): m.get("value") for m in o.findall("metadata")}
    parts = {}
    for p in o.iter("part"):
        pm = {m.get("key"): m.get("value") for m in p.findall("metadata")}
        parts[p.get("id")] = dict(name=pm.get("name"), extruder=int(pm.get("extruder", meta.get("extruder", 1))))
    obj_cfg[o.get("id")] = dict(name=meta.get("name"), extruder=int(meta.get("extruder", 1)), parts=parts)

# 3dmodel.model: component transforms cua object balo dau tien (41)
top = ET.parse(root / "3D/3dmodel.model").getroot()
comp_tf = {}
for o in top.iter(NS + "object"):
    if o.get("id") == "41":
        for c in o.iter(NS + "component"):
            comp_tf[c.get("objectid")] = [float(x) for x in c.get("transform").split()]

def read_meshes(path):
    res, verts, tris, paint = {}, [], [], {}
    for ev, el in ET.iterparse(path, events=("start", "end")):
        t = el.tag.replace(NS, "")
        if ev == "start" and t == "object":
            verts, tris, paint = [], [], {}
            oid = el.get("id")
        elif ev == "end" and t == "vertex":
            verts.append((float(el.get("x")), float(el.get("y")), float(el.get("z")))); el.clear()
        elif ev == "end" and t == "triangle":
            tris.append((int(el.get("v1")), int(el.get("v2")), int(el.get("v3"))))
            pc = el.get("paint_color")
            if pc: paint[pc] = paint.get(pc, 0) + 1
            el.clear()
        elif ev == "end" and t == "object":
            v = np.array(verts) if verts else np.zeros((0, 3))
            res[oid] = dict(n_tri=len(tris), bbox=[v.min(0).round(3).tolist(), v.max(0).round(3).tolist()] if len(v) else None,
                            paint=dict(sorted(paint.items(), key=lambda x: -x[1])[:12]), n_paint=sum(paint.values()))
            el.clear()
    return res

bp = read_meshes(root / "3D/Objects/object_12.model")
parts = []
cfg41 = obj_cfg["41"]
for oid, r in bp.items():
    pc = cfg41["parts"].get(oid, {})
    ext = pc.get("extruder", cfg41["extruder"])
    tf = comp_tf.get(oid, [0] * 12)
    off = tf[9:12]
    bb = r["bbox"]
    wb = [[bb[0][i] + off[i] for i in range(3)], [bb[1][i] + off[i] for i in range(3)]] if bb else None
    parts.append(dict(object_id=oid, name=pc.get("name"), extruder=ext, color=colors[ext - 1], n_tri=r["n_tri"],
                      bbox_object=[[round(x, 2) for x in b] for b in wb] if wb else None,
                      size=[round(wb[1][i] - wb[0][i], 2) for i in range(3)] if wb else None))
el = read_meshes(root / "3D/Objects/object_7.model")
data = dict(source="Downloads/Elephant.3mf (MakerWorld, Bambu Studio)",
            filaments=[dict(slot=i + 1, color=c, profile=f) for i, (c, f) in enumerate(zip(colors, fil))],
            process=dict(print_settings_id=proj.get("print_settings_id"), layer_height=proj.get("layer_height"),
                         enable_support=proj.get("enable_support"), support_type=proj.get("support_type")),
            backpack_parts=parts,
            elephant={k: dict(v, extruder_default=obj_cfg["2"]["extruder"]) for k, v in el.items()})
json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for p in parts:
    print(p["object_id"], p["name"], "ext", p["extruder"], p["color"], "tri", p["n_tri"], "size", p["size"], "min", p["bbox_object"][0] if p["bbox_object"] else None)
print("elephant", {k: (v["n_tri"], v["n_paint"], v["paint"]) for k, v in el.items()})
