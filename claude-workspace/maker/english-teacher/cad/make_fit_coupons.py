# make_fit_coupons.py - mau thu LAP RAP NHANH cho Cu Bong ban man (Claude spec 2026-11-26; Tuan: "chay lai testing cac noi gan mic thu am, board esp32-s3").
# KHONG dung lai hinh: CAT NGUYEN VEN tu STL da xuat (out-s3-screen/shell-front.stl, shell-back.stl - da o HUONG IN that) bang boolean intersect voi hop,
# nen khe/ray/lo khop dung vo that. Huong in giu nguyen nhu vo that (mat ghep y = Y0 xuong ban) -> khong support nhu vo.
#   mic-seat-coupon.stl : vung tran quanh mic tren shell-front (52 x 27 quanh mic, tu mat ghep len; cua so rong 52 de co vach hai suon do mieng vom - slicer khong bao floating).
#                         + mic-clamp.stl (chep nguyen) -> Tuan dat module INMP441 O15 + ron xop 1,2 thu.
#   s3-rail-coupon.stl  : doan ray giu bo ESP32-S3 + khe cap USB-C o LUNG cat tu shell-back (y 18..58): ~18 mm ledge giu mep PCB (+ 9 mm hoc) giu boi ray, lo USB 14 x 9.
#                         Dau ray mo nam o MAT BAN (khong them de, bo truot vao tu mat ghep).
# So (tam mic, tam bo, khe cap) doc tu owl-params.json. Chay:
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P make_fit_coupons.py -- out-s3-screen print\stl-s3-test
import bpy, bmesh, sys, json, shutil, os
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
SRC = Path(args[0]).resolve(); DST = Path(args[1]).resolve(); DST.mkdir(parents=True, exist_ok=True)
P = json.loads((SRC / "owl-params.json").read_text(encoding="utf-8"))
Y0 = 0.37                         # mat ghep (world), phai khop build
mic_c = Vector(P["mic"]["center"])
pcb_c = Vector(P["pcb_center"]); pcb_box = P["pcb_box"]; usb_y = P["pcb_usb"]["center"][1]
cab = P["cable_slot"]


def zc_asm(name):   # tam z (world) cua hop bao vo = do export_obj can giua x,y huong in (y huong in = +-z world)
    o = load(SRC / "asm" / name)
    zs = [v.co.z for v in o.data.vertices]
    return (max(zs) + min(zs)) / 2


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=str(path))
    return bpy.context.selected_objects[0]


def add_box(lo, hi, name="cutbox"):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((lo[0] + hi[0]) / 2 + v.co.x * (hi[0] - lo[0]),
                       (lo[1] + hi[1]) / 2 + v.co.y * (hi[1] - lo[1]),
                       (lo[2] + hi[2]) / 2 + v.co.z * (hi[2] - lo[2])))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); return o


def bool_op(obj, other, op):
    m = obj.modifiers.new("b", "BOOLEAN"); m.operation = op; m.object = other; m.solver = "MANIFOLD"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=m.name)


def export(obj, path, z_to_bed=True):
    me = obj.data
    if z_to_bed:
        zmin = min(v.co.z for v in me.vertices)
        for v in me.vertices:
            v.co.z -= zmin
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True); bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    print("COUPON", path.name, "bbox", round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1), round(max(zs) - min(zs), 1))


ZC_F = zc_asm("shell-front.stl"); ZC_B = zc_asm("shell-back.stl")

# ---- 1) mau mic: shell-front (huong in: x' = x, y' = z world, z' = Y0 - y world; mat ghep z' = 0 xuong ban)
sh = load(SRC / "shell-front.stl")
my = mic_c.z - ZC_F                # y' cua mic = z world - tam (export_obj can giua)
mz = Y0 - mic_c.y                  # z' cua mic
# cua so da thu bang slicer (Bambu): XH < 26 -> 'floating' (mieng vom can vach hai suon de do), 26 PASS; khong de phang them vi de se roi roi voi mieng
MTOP = float(os.environ.get('MTOP', 7.0)); MBASE = float(os.environ.get('MBASE', 0.0))
XH = float(os.environ.get('XH', 26.0)); YLO = float(os.environ.get('YLO', 13.5)); YHI = float(os.environ.get('YHI', 13.5))
cut = add_box((-XH, my - YLO, float(os.environ.get('MZLO', 0.0))), (XH, my + YHI, mz + MTOP))   # MZLO > 0: cat sat cho mic (Tuan: mau vua du)
bool_op(sh, cut, "INTERSECT"); bpy.data.objects.remove(cut)
if MBASE > 0:
    base = add_box((-XH, my - YLO, -MBASE), (XH, my + YHI, 0.05), "base")
    bool_op(sh, base, "UNION"); bpy.data.objects.remove(base)
export(sh, DST / "mic-seat-coupon.stl")
shutil.copyfile(SRC / "mic-clamp.stl", DST / "mic-clamp.stl")

# ---- 2) mau ray bo S3 + khe cap USB: shell-back (huong in: x' = x, y' = -z world, z' = y world - Y0; mat ghep z' = 0 xuong ban)
sb = load(SRC / "shell-back.stl")
RX = float(os.environ.get('RX', 36.0)); y_lo, y_hi = float(os.environ.get('RYLO', 18.0)), cab["center"][1] + cab["wall_t"] / 2 + 1.5      # y world: 14 .. ~58 (22 mm ray + vach cap)
zc = pcb_c.z
RZT = float(os.environ.get('RZT', 12.0)); RZB = float(os.environ.get('RZB', 12.0))
cut = add_box((-RX, -(zc + RZT - ZC_B), y_lo - Y0), (RX, -(zc - RZB - ZC_B), y_hi - Y0))
bool_op(sb, cut, "INTERSECT"); bpy.data.objects.remove(cut)
export(sb, DST / "s3-rail-coupon.stl")
