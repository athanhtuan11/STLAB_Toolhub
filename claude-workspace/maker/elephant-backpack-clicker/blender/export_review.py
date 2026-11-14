"""Xuat bo duyet: out/asm/*.stl (xep hang ngang, mm) + elephant-backpack.blend + anh duyet (out/review/).
  blender -b --factory-startup -P export_review.py -- <thu muc du an>
Hang: balo goc | STLAB | SMALL TREE | voi. Sau do chay export_cad.py de ra .sc (SolidCraft).
"""
import bpy, sys, os
from mathutils import Vector
root = sys.argv[sys.argv.index("--") + 1]
P = lambda *a: os.path.join(root, *a)
parts = [("1-backpack-original", P("blender", "out", "backpack-original-150k.stl")),
         ("2-backpack-stlab", P("print", "stl", "backpack-stlab.stl")),
         ("3-backpack-small-tree", P("print", "stl", "backpack-small-tree.stl")),
         ("4-elephant", P("print", "stl", "elephant.stl"))]
os.makedirs(P("blender", "out", "asm"), exist_ok=True)
os.makedirs(P("blender", "out", "review"), exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system, sc.unit_settings.scale_length, sc.unit_settings.length_unit = "METRIC", 0.001, "MILLIMETERS"
x, objs = 0.0, []
for name, f in parts:
    bpy.ops.wm.stl_import(filepath=f)
    o = bpy.context.selected_objects[0]; o.name = name
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    mn = Vector([min(v[i] for v in vs) for i in range(3)])
    mx = Vector([max(v[i] for v in vs) for i in range(3)])
    o.data.transform(__import__("mathutils").Matrix.Translation(Vector((x - mn.x, -(mn.y + mx.y) / 2, -mn.z))))
    x += (mx.x - mn.x) + 10
    objs.append(o)
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True)
    bpy.ops.wm.stl_export(filepath=P("blender", "out", "asm", name + ".stl"), export_selected_objects=True)
# anh duyet
mat = bpy.data.materials.new("m"); mat.diffuse_color = (0.93, 0.80, 0.55, 1)
for o in objs: o.data.materials.append(mat)
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light, sc.display.shading.color_type = "STUDIO", "MATERIAL"
sc.display.shading.show_cavity = True
sc.world = bpy.data.worlds.new("w")
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
def shot(fn, loc, rot, scale, rx, ry):
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    cam.location, cam.rotation_euler, cam.data.ortho_scale = loc, rot, scale
    sc.render.filepath = P("blender", "out", "review", fn); bpy.ops.render.render(write_still=True)
# tam nhan: y = -24 so voi tam balo
for o in objs[:3]:
    vs = [v.co for v in o.data.vertices]
    cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2
    shot(f"{o.name}-plate.png", Vector((cx, -24.0, 120)), (0, 0, 0), 38, 1200, 500)
d = Vector((0.35, -1.0, 1.0)).normalized()
shot("0-overview.png", Vector((x / 2 - 5, 0, 17)) + d * 300, d.to_track_quat("Z", "Y").to_euler(), x + 5, 1800, 700)
bpy.ops.wm.save_as_mainfile(filepath=P("blender", "elephant-backpack.blend"))
print("REVIEW OK", [o.name for o in objs])
