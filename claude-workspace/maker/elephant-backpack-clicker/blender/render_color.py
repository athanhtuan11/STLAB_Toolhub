"""Anh duyet CO MAU + bo STL theo mau cho SolidCraft: balo goc / STLAB / SMALL TREE tu chi tiet 3mf (source/parts),
mau theo source/color-map.json. Toa do object balo (Z len), xep hang ngang cach 70 mm.
  blender -b --factory-startup -P render_color.py -- <thu muc du an>
Ra: blender/out/review-color/*.png, blender/out/color/asm/<balo>-<mau>.stl, blender/elephant-backpack-color.blend
"""
import bpy, sys, os, json
from mathutils import Vector, Matrix
root = sys.argv[sys.argv.index("--") + 1]
P = lambda *a: os.path.join(root, *a)
cm = json.load(open(P("source", "color-map.json"), encoding="utf-8"))
LET = {"26", "34", "35", "36", "37", "38", "39", "40"}
ext = {p["object_id"]: p["extruder"] for p in cm["backpack_parts"]}
cols = {f["slot"]: f["color"] for f in cm["filaments"]}
NAME = {1: "white", 2: "black", 3: "grey"}
variants = [("backpack-original", None), ("backpack-stlab", "text-stlab"), ("backpack-small-tree", "text-small-tree")]
os.makedirs(P("blender", "out", "review-color"), exist_ok=True); os.makedirs(P("blender", "out", "color", "asm"), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system, sc.unit_settings.scale_length, sc.unit_settings.length_unit = "METRIC", 0.001, "MILLIMETERS"
mats = {}
for s, hx in cols.items():
    m = bpy.data.materials.new(NAME[s]); h = hx.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    m.diffuse_color = (*lin, 1); mats[s] = m
def imp(path, slot, dx, coll):
    bpy.ops.wm.stl_import(filepath=path); o = bpy.context.selected_objects[0]
    o.data.transform(Matrix.Translation((dx, 0, 0))); o.data.materials.append(mats[slot])
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o); return o
for i, (vname, txt) in enumerate(variants):
    dx = i * 70.0
    coll = bpy.data.collections.new(vname); sc.collection.children.link(coll)
    for oid in sorted(ext, key=int):
        if txt and oid in LET: continue
        imp(P("source", "parts", f"part-{oid}.stl"), ext[oid], dx, coll).name = f"{vname}-{oid}"
    if txt: imp(P("source", "text", f"{txt}.stl"), 3, dx, coll).name = f"{vname}-{txt}"
    for s in cols:   # gop theo mau -> 1 STL / mau cho SolidCraft
        objs = [o for o in coll.objects if o.data.materials and o.data.materials[0] == mats[s]]
        if not objs: continue
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs: o.select_set(True)
        bpy.ops.wm.stl_export(filepath=P("blender", "out", "color", "asm", f"{i + 1}-{vname}-{NAME[s]}.stl"), export_selected_objects=True)
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light, sc.display.shading.color_type = "STUDIO", "MATERIAL"
sc.display.shading.show_cavity = True
sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("w"); sc.world = w
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
def shot(fn, target, d, scale, rx, ry):
    d = Vector(d).normalized(); sc.render.resolution_x, sc.render.resolution_y = rx, ry
    cam.location = Vector(target) + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = scale; sc.render.filepath = P("blender", "out", "review-color", fn); bpy.ops.render.render(write_still=True)
shot("0-overview.png", (70, 0, 0), (0.35, -1, 0.35), 205, 1800, 800)
for i, (vname, _) in enumerate(variants):
    shot(f"{i + 1}-{vname}-front.png", (i * 70, 0, 0), (0.25, -1, 0.2), 72, 900, 900)
    shot(f"{i + 1}-{vname}-plate.png", (i * 70, -17, -24), (0, -1, 0), 38, 1200, 500)
bpy.ops.wm.save_as_mainfile(filepath=P("blender", "elephant-backpack-color.blend"))
print("COLOR OK")
