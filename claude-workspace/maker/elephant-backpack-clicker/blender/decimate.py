"""Giam luoi STL (Decimate collapse) de Bambu Studio cat lop khong ngon RAM.
  blender -b --factory-startup -P decimate.py -- <in.stl> <out.stl> <so_tam_giac_dich>
"""
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
src, out, target = a[0], a[1], int(a[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src)
o = bpy.context.selected_objects[0]
n0 = len(o.data.polygons)
md = o.modifiers.new("d", "DECIMATE")
md.decimate_type, md.ratio, md.use_collapse_triangulate = "COLLAPSE", min(1.0, target / n0), True
bpy.context.view_layer.objects.active = o
bpy.ops.object.modifier_apply(modifier=md.name)
print(f"decimate {n0} -> {len(o.data.polygons)}")
bpy.ops.wm.stl_export(filepath=out, export_selected_objects=True)
