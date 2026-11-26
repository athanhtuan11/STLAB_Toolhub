# make_button_coupon.py - mau thu NHANH khop nut noi (Claude 2026-11-26, Tuan: "in nguyen de va button rat lau").
# Chi giu phan lap ghep cua mau clicky cat-paw da chay that (docs/research-notes/cat-paw-clicker-fits.md, fit-library catpaw/*):
#   mini-cap.stl   : nap thu O27,4 - hoc trong O24,4 (>= 24,2 cua mau) tran cao 9,80 tren mep vay, ong O5,71 dai 5,49,
#                    lo chu thap 4,19 x 1,25 xuyen het ong (dau ong o +4,31 tren mep vay). In mat tren xuong ban.
#   mx-socket-coupon.stl : tam 24 x 24 x 5 ho day, lo vuong 14,00 + ranh V ngam 1,94-3,44 duoi mieng (rong nhat 15,44 o 2,69).
# So lay tu owl-params (mx) neu co; khong co thi dung so mau. Hanh trinh + go chan nap: thu tren ban p2-button / vo that.
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P make_button_coupon.py -- <out_dir>
import bpy, bmesh, sys, json
from pathlib import Path
from mathutils import Vector

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve(); OUT.mkdir(parents=True, exist_ok=True)
mx = {}
pp = OUT / "owl-params.json"
if pp.exists():
    mx = json.loads(pp.read_text(encoding="utf-8")).get("mx", {})
HOLE = mx.get("hole", 14.0); CL = mx.get("stem_cross_l", 4.19); CW = mx.get("stem_cross_w", 1.25)
CD = mx.get("cross_depth", 5.49); TOD = mx.get("tube_od", 5.71); HD = mx.get("cap_hollow_depth", 9.8)
TUBE_UP = mx.get("tube_end_above_rim", 4.31)
G0, G1, G2, GW = 1.94, 2.69, 3.44, 15.44          # ranh V catpaw/mx-socket
TOP_T, WALL, HOLLOW_D = 1.5, 1.5, 24.4
PLATE, PLATE_T = 24.0, 5.0

bpy.ops.wm.read_factory_settings(use_empty=True)


def obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); return o


def cyl(name, r, z0, z1, seg=96):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, (z0 + z1) / 2)); return obj(name, bm)


def box(name, sx, sy, z0, z1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, z0 + (v.co.z + 0.5) * (z1 - z0)))
    return obj(name, bm)


def hull(name, rings):   # rings: [(canh_vuong, z)] -> khoi loi
    bm = bmesh.new()
    for s, z in rings:
        for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            bm.verts.new((x * s / 2, y * s / 2, z))
    bmesh.ops.convex_hull(bm, input=bm.verts); return obj(name, bm)


def diff(a, b, op="DIFFERENCE"):
    m = a.modifiers.new("b", "BOOLEAN"); m.operation = op; m.object = b; m.solver = "EXACT"
    bpy.context.view_layer.objects.active = a; bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(b, do_unlink=True)


def export(o, path):
    for x in bpy.context.scene.objects:
        x.select_set(x == o)
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, apply_modifiers=True)


# --- mini-cap (in mat tren xuong ban: z=0 la mat tren nap, vay huong len)
H = TOP_T + HD                                     # tong cao = 1,5 + 9,8 = 11,3 (giong mau)
cap = cyl("mini_cap", HOLLOW_D / 2 + WALL, 0, H)
diff(cap, cyl("hollow", HOLLOW_D / 2, TOP_T, H + 1))
tube_end = H - TUBE_UP                             # dau ong cach mep vay 4,31
tube = cyl("tube", TOD / 2, TOP_T - 0.01, tube_end, seg=48)
diff(cap, tube, "UNION")
for ang in (0.0, 90.0):
    c = box("cross", CL, CW, tube_end - CD, tube_end + 0.5)
    c.rotation_euler = (0, 0, ang * 3.14159265 / 180); bpy.context.view_layer.objects.active = c
    bpy.ops.object.transform_apply(rotation=True)
    diff(cap, c)
export(cap, OUT / "mini-cap.stl")

# --- mx-socket-coupon (mieng o mat tren z = PLATE_T, ho day de chan switch thong xuong)
pl = box("socket_coupon", PLATE, PLATE, 0, PLATE_T)
diff(pl, box("hole", HOLE, HOLE, -1, PLATE_T + 1))
diff(pl, hull("vgroove", [(HOLE, PLATE_T - G0), (GW, PLATE_T - G1), (HOLE, PLATE_T - G2)]))
export(pl, OUT / "mx-socket-coupon.stl")
print(f"OK mini-cap O{HOLLOW_D + 2 * WALL:.1f} x {H:.1f}, ong O{TOD} chu thap {CL} x {CW} sau {CD}; coupon {PLATE} x {PLATE} x {PLATE_T}")
