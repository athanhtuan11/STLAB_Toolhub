"""Thay chu tren tam nhan balo clicky (mau cong dong Elephant backpack).

Goi chu noi cu bang cutter (make_cutter.py) roi dap chu noi moi, dinh chu phang
cung cao do chu cu (top_z), chan chu ngam 0,4 mm vao tam nhan.
  blender -b --factory-startup -P build_text.py -- <bag.stl> <cutter.stl> <info.json>
      <out.stl> "<TEXT>" <font.ttf> <cap_h_mm> <max_w_mm> <render_prefix>
"""
import bpy, bmesh, json, sys, math
from mathutils import Vector

a = sys.argv[sys.argv.index("--") + 1:]
bag_p, cut_p, info_p, out_p, text, font_p = a[:6]
cap_h, max_w = float(a[6]), float(a[7])
rprefix = a[8]
info = json.load(open(info_p))
off = Vector(info["offset"])
top_z = info["top_z"]
plate_zmin = info["plate_z_range"][0]
cx = (info["plate_min"][0] + info["plate_max"][0]) / 2
cy = (info["plate_min"][1] + info["plate_max"][1]) / 2

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def imp(p):
    bpy.ops.wm.stl_import(filepath=p)
    return bpy.context.selected_objects[0]

def boolean(obj, tool, op):
    for solver in ("MANIFOLD", "EXACT"):
        nf = len(obj.data.polygons)
        md = obj.modifiers.new("b", "BOOLEAN")
        md.operation, md.object, md.solver = op, tool, solver
        dg = bpy.context.evaluated_depsgraph_get()
        ev = obj.evaluated_get(dg)
        n_after = len(ev.data.polygons)
        if n_after > 1000 and n_after != nf:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=md.name)
            print(f"boolean {op} solver={solver} faces {nf} -> {len(obj.data.polygons)}")
            return solver
        obj.modifiers.remove(md)
        print(f"boolean {op} solver={solver} FAIL ({n_after} faces), thu solver khac")
    raise SystemExit("boolean that bai")

bag = imp(bag_p)
bm = bmesh.new(); bm.from_mesh(bag.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bm.to_mesh(bag.data); bm.free()
cut = imp(cut_p)
s1 = boolean(bag, cut, "DIFFERENCE")
bpy.data.objects.remove(cut)

# Chu moi
cu = bpy.data.curves.new("txt", "FONT")
cu.body = text
cu.font = bpy.data.fonts.load(font_p)
cu.align_x, cu.align_y = "CENTER", "CENTER"
cu.extrude = 0.5
to = bpy.data.objects.new("txt", cu); sc.collection.objects.link(to)
bpy.ops.object.select_all(action="DESELECT")
to.select_set(True); bpy.context.view_layer.objects.active = to
bpy.ops.object.convert(target="MESH")
to = bpy.context.view_layer.objects.active
co = [v.co for v in to.data.vertices]
mn = Vector([min(c[i] for c in co) for i in range(3)])
mx = Vector([max(c[i] for c in co) for i in range(3)])
w, h = mx.x - mn.x, mx.y - mn.y
s = min(cap_h / h, max_w / w)
z0 = plate_zmin - 0.4                       # chan chu ngam vao tam nhan
for v in to.data.vertices:
    v.co.x = (v.co.x - (mn.x + mx.x) / 2) * s + cx + off.x
    v.co.y = (v.co.y - (mn.y + mx.y) / 2) * s + cy + off.y
    v.co.z = z0 + (v.co.z - mn.z) / (mx.z - mn.z) * (top_z - z0)
tw, th = w * s, h * s
print(f"text '{text}' {tw:.2f} x {th:.2f} mm, z {z0:.2f}..{top_z:.2f}")
bm = bmesh.new(); bm.from_mesh(to.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(to.data); bm.free()
s2 = boolean(bag, to, "UNION")
bpy.data.objects.remove(to)

bpy.ops.object.select_all(action="DESELECT")
bag.select_set(True)
bpy.ops.wm.stl_export(filepath=out_p, export_selected_objects=True, ascii_format=False)
json.dump(dict(text=text, font=font_p, width=tw, height=th, z0=z0, top_z=top_z,
               solvers=[s1, s2]), open(out_p[:-4] + "-params.json", "w"), indent=1)

# Anh duyet: can canh tam nhan (nhin tu tren, +Y huong len) + toan canh
mat = bpy.data.materials.new("m")
mat.diffuse_color = (0.93, 0.80, 0.55, 1)
bag.data.materials.append(mat)
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
sc.display.shading.show_cavity = True; sc.display.shading.cavity_type = "BOTH"
sc.world = bpy.data.worlds.new("w")
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
def shot(name, loc, rot, scale, rx=1200, ry=900):
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    cam.location, cam.rotation_euler, cam.data.ortho_scale = loc, rot, scale
    sc.render.filepath = f"{rprefix}-{name}.png"
    bpy.ops.render.render(write_still=True)
c = off + Vector((cx, cy, 0))
shot("plate", c + Vector((0, 0, 100)), (0, 0, 0), 38, 1200, 500)
shot("top", off + Vector((0, 0, 100)), (0, 0, 0), 80, 900, 900)
d = Vector((0.0, -1.0, 1.1)).normalized()
shot("iso", off + Vector((0, 0, 17)) + d * 150, d.to_track_quat("Z", "Y").to_euler(), 85, 900, 900)
