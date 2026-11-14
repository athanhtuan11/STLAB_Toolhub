"""Dung chi tiet chu (mau xam) cho 3mf balo, toa do object balo (Y = huong ra truoc, Z = len khi dung balo).
Mat truoc chu phang y = FRONT_Y nhu chu ELEPHANT goc; mat sau keo vao tam nhan roi TRU tam nhan -> om sat mat cong,
khong chong lan voi chi tiet trang.
  blender -b --factory-startup -P make_text_part.py -- <plate.stl> <out.stl> "<TEXT>" <font.ttf> <cap_h> <max_w>
"""
import bpy, bmesh, sys, json
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]
plate_p, out_p, text, font_p = a[:4]; cap_h, max_w = float(a[4]), float(a[5])
FRONT_Y, BACK_Y = -17.093, -15.9          # mat chu goc; mat sau ngam vao tam nhan (tam day 3,6 mm)
CX, CZ = 0.0, -23.985                     # tam vung chu goc (x -15.405..15.405, z -26.163..-21.806)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.wm.stl_import(filepath=plate_p); plate = bpy.context.selected_objects[0]
cu = bpy.data.curves.new("txt", "FONT"); cu.body = text; cu.font = bpy.data.fonts.load(font_p)
cu.align_x, cu.align_y, cu.extrude = "CENTER", "CENTER", 0.5
to = bpy.data.objects.new("txt", cu); sc.collection.objects.link(to)
bpy.ops.object.select_all(action="DESELECT"); to.select_set(True); bpy.context.view_layer.objects.active = to
bpy.ops.object.convert(target="MESH"); to = bpy.context.view_layer.objects.active
co = [v.co.copy() for v in to.data.vertices]
mn = Vector([min(c[i] for c in co) for i in range(3)]); mx = Vector([max(c[i] for c in co) for i in range(3)])
s = min(cap_h / (mx.y - mn.y), max_w / (mx.x - mn.x))
for v in to.data.vertices:          # chu trong mat XZ: x->x, y(chu)->z, z(dun)->-y (huong ra truoc)
    x, y, zz = v.co
    t = (zz - mn.z) / (mx.z - mn.z)
    v.co = Vector(((x - (mn.x + mx.x) / 2) * s + CX, BACK_Y + t * (FRONT_Y - BACK_Y), (y - (mn.y + mx.y) / 2) * s + CZ))
bm = bmesh.new(); bm.from_mesh(to.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(to.data); bm.free()
md = to.modifiers.new("b", "BOOLEAN"); md.operation, md.object, md.solver = "DIFFERENCE", plate, "EXACT"
bpy.context.view_layer.objects.active = to; bpy.ops.object.modifier_apply(modifier=md.name)
vs = [v.co for v in to.data.vertices]
bb = [[round(min(v[i] for v in vs), 3) for i in range(3)], [round(max(v[i] for v in vs), 3) for i in range(3)]]
bpy.ops.object.select_all(action="DESELECT"); to.select_set(True)
bpy.ops.wm.stl_export(filepath=out_p, export_selected_objects=True)
info = dict(text=text, font=font_p, width=round((mx.x - mn.x) * s, 2), cap_height=round((mx.y - mn.y) * s, 2),
            faces=len(to.data.polygons), bbox=bb)
json.dump(info, open(out_p[:-4] + ".json", "w"), indent=1); print("TEXTPART", info)
