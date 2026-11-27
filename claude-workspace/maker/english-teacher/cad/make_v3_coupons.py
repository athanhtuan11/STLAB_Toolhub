# make_v3_coupons.py - ban thu nho Cu Bong v3 (spec-owl-v3-assembly.md, Gate 4): cat nguyen ven tu STL lap rap out-v3/asm
# (boolean giao voi hop), dat huong in giong part goc (vo: mat rap / mat sau xuong ban). Xuat vao print/stl-v3-test/.
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python-exit-code 1 -P make_v3_coupons.py
#  2026-11-27 mo + bung doi sang VIT GIAU TU TRONG, vanh loa them VIT DAY qua de, vong ep them NAC KHOA:
#  - belly-coupon: vach bung dac + chot chong xoay + duong tua vit (mo tu mat ban) -> bung that + 1 vit M2.5 x 12
#  - beak-coupon: lo mo O14 + tam chan 3,0 + duong tua vit -> mo that + 1 vit M2.5 x 12
#  - bezel-bot + base-bot: tru day vanh loa R + doan de (hoc dau vit) -> 1 vit M2.5 x 12 tu duoi
#  - speaker-ring-R (that, chep tu out-v3): thu nac khoa tren vanh loa Tuan DA IN (chot vanh khong doi)
#  - screw-front / screw-back: 1 vit noi 2 nua (52; 113) M2.5 x 12: tru + lo moi O2,4 / gieng O5,6 day 3,0
#  - fin-pocket + fin-tab: hoc vay vanh loa R tren vo truoc + doan vay (2 vit M2.5 x 6)
import bpy, bmesh, sys, math
from pathlib import Path
from mathutils import Vector, Matrix

HERE = Path(__file__).resolve().parent
ASM = HERE / "out-v3" / "asm"
OUT = HERE.parent / "print" / "stl-v3-test"
OUT.mkdir(parents=True, exist_ok=True)
Y0 = 0.37
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene


def imp(name):
    bpy.ops.wm.stl_import(filepath=str(ASM / f"{name}.stl"))
    o = bpy.context.selected_objects[0]; o.name = name
    return o


def cp(o, name):
    n = o.copy(); n.data = o.data.copy(); n.name = name; SC.collection.objects.link(n); return n


def boxo(mn, mx):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((mn[0] if v.co.x < 0 else mx[0], mn[1] if v.co.y < 0 else mx[1], mn[2] if v.co.z < 0 else mx[2]))
    me = bpy.data.meshes.new('b'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('b', me); SC.collection.objects.link(o); return o


def cylo(p0, p1, r, seg=96):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
    R = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2) @ R, verts=bm.verts)
    me = bpy.data.meshes.new('c'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('c', me); SC.collection.objects.link(o); return o


def bop(a, b, op):
    bpy.context.view_layer.update()
    m = a.modifiers.new('x', 'BOOLEAN'); m.operation = op; m.object = b; m.solver = 'MANIFOLD'
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(a.evaluated_get(dg)); a.modifiers.remove(m)
    old = a.data; a.data = me; bpy.data.meshes.remove(old); bpy.data.objects.remove(b)
    return a


def cut(src, name, mn, mx):
    return bop(cp(src, name), boxo(mn, mx), 'INTERSECT')


def export(o, T, fname):
    o.data.transform(T)
    xs = [v.co.x for v in o.data.vertices]; ys = [v.co.y for v in o.data.vertices]; zs = [v.co.z for v in o.data.vertices]
    o.data.transform(Matrix.Translation((-(max(xs) + min(xs)) / 2, -(max(ys) + min(ys)) / 2, -min(zs))))
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.wm.stl_export(filepath=str(OUT / fname), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
    print("COUPON %s %.1f x %.1f x %.1f" % (fname, max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))


# huong in vo truoc: mat rap (y = Y0) xuong ban, -y len (T_front trong build); vo sau: mat rap xuong, +y len
T_FRONT = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, Y0), (0, 0, 0, 1)))
T_BACK = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, -Y0), (0, 0, 0, 1)))
front = imp("shell-front"); back = imp("shell-back")

# --- lo bung (mat duoi coupon = mat sau vach y -44, cung la mat moc lay -> nam tren ban)
bel = cut(front, "belly_c", (-25.0, -70.0, 5.5), (25.0, -38.2, 50.5))
export(bel, T_FRONT, "belly-coupon.stl")
# --- lo mo
bk = cut(front, "beak_c", (-14.0, -62.0, 47.0), (14.0, -42.0, 70.4))
export(bk, T_FRONT, "beak-coupon.stl")
# --- vit noi 2 nua tai (52; 113)
sf = cut(front, "screw_f", (44.0, -12.0, 105.0), (60.0, Y0, 121.0))
export(sf, T_FRONT, "screw-front.stl")
sb = cut(back, "screw_b", (44.0, Y0, 105.0), (60.0, 45.0, 121.0))
export(sb, T_BACK, "screw-back.stl")
# --- vay vanh loa R: hoc tren vo truoc + doan vay (mat vay xuong ban)
fp_ = cut(front, "fin_p", (43.0, -10.0, 77.0), (58.0, Y0, 103.0))
export(fp_, T_FRONT, "fin-pocket.stl")
bz = imp("speaker-bezel-R")
ft = cut(bz, "fin_t", (45.0, -10.0, 79.0), (55.5, 0.4, 100.5))
export(ft, Matrix(((0, -1, 0, 0), (0, 0, 1, 0), (-1, 0, 0, 0), (0, 0, 0, 1))), "fin-tab.stl")   # huong in nhu vanh loa: mat ngoai (x lon) xuong ban
# --- vit day vanh loa R: doan day vanh (huong in nhu vanh: mat ngoai xuong ban) + doan de (in mat tren xuong ban nhu de that)
bb = cut(bz, "bz_bot_c", (52.0, -8.0, 4.0), (66.0, 8.0, 14.0))
export(bb, Matrix(((0, -1, 0, 0), (0, 0, 1, 0), (-1, 0, 0, 0), (0, 0, 0, 1))), "bezel-bot.stl")
pl = imp("base")
pb = cut(pl, "base_bot_c", (50.0, -8.0, -3.0), (64.0, 8.0, 4.5))
export(pb, Matrix(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1))), "base-bot.stl")
print("COUPONS OK")
