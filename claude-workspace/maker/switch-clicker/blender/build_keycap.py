"""Build the round engraved keycap of the STLab switch-clicker (Blender 5.2).

Run: blender -b --python-exit-code 1 -P build_keycap.py -- out [NAME]
Units: 1 = 1 mm. The STL is in PRINT orientation (cap upside down):
    z = 0     -> top face of the keycap, on the bed
    z = 11.3  -> mouth of the skirt, opening up

The cross stem is an MX-compatible cross hole (fit-library
catpaw/mx-keycap-cross). All dimensions are variables at the top.
"""

import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv
if "--" in argv:
    rest = argv[argv.index("--") + 1:]
else:
    rest = []
OUT = Path(rest[0]) if rest else Path("out")
NAME = rest[1] if len(rest) > 1 else ""
OUT = OUT.resolve()
OUT.mkdir(parents=True, exist_ok=True)

suffix = "-" + NAME if NAME else ""
STL_PATH = OUT / ("keycap-round" + suffix + ".stl")
PARAM_PATH = OUT / ("keycap-round" + suffix + "-params.json")

# ---------------------------------------------------------------- parameters ---

KEY_D = 26.0
KEY_H = 11.3
TOP_CHAMFER = 1.2

SKIRT_ID = 23.0
TOP_PLATE = 1.4

STEM_OD = 5.71
STEM_Z0 = TOP_PLATE
STEM_Z1 = 7.0

CROSS_L = 4.19
CROSS_W = 1.25
CROSS_DEPTH = 5.6
CROSS_CHAMFER = 0.2

TEXT = "STLAB"
TEXT_H = 4.0
TEXT_MAX_W = 19.0
TEXT_DEPTH = 0.6
TEXT_STROKE_MIN = 0.8
TEXT_FONT = r"C:\Windows\Fonts\ariblk.ttf"

SEG = 128
N_CHAMFER = 12

# body-v2 keycap pocket floor, only used to seat the preview assembly
POCKET_Z0 = 11.19

MX_SOURCE = (
    "fit-library catpaw/mx-keycap-cross (printed on Bambu A1 + PETG "
    "Basic): cross 4.19 long x 1.25 wide, 5.6 deep; stem OD 5.71; "
    "stem end 4.3 inside the skirt mouth."
)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ------------------------------------------------------------------- helpers ---


def obj_from_bm(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def apply_boolean(target, tool, operation="DIFFERENCE"):
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = operation
    mod.solver = "EXACT"
    mod.object = tool
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    new_me = bpy.data.meshes.new_from_object(
        target.evaluated_get(dg), depsgraph=dg
    )
    target.modifiers.clear()
    old = target.data
    target.data = new_me
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(tool, do_unlink=True)
    bpy.context.view_layer.update()


def clean(ob, dist=1e-6):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    bpy.context.view_layer.update()


def revolve(name, profile, seg=SEG):
    """Closed solid of revolution. profile = [(radius, z), ...] bottom->top."""
    bm = bmesh.new()
    rings = []
    for rad, z in profile:
        ring = []
        for k in range(seg):
            a = 2.0 * math.pi * k / seg
            ring.append(bm.verts.new((rad * math.cos(a), rad * math.sin(a), z)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(seg):
            j = (k + 1) % seg
            bm.faces.new((a[k], a[j], b[j], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


def loft(name, rings_pts, triangulate=False):
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in ring] for ring in rings_pts]
    m = len(vs[0])
    for i in range(len(vs) - 1):
        a, b = vs[i], vs[i + 1]
        for j in range(m):
            k = (j + 1) % m
            bm.faces.new((a[j], a[k], b[k], b[j]))
    bm.faces.new(list(reversed(vs[0])))
    bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if triangulate:
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


def cross_outline(half_l, half_w, z):
    return [
        (half_w, -half_l, z), (half_w, -half_w, z),
        (half_l, -half_w, z), (half_l, half_w, z),
        (half_w, half_w, z), (half_w, half_l, z),
        (-half_w, half_l, z), (-half_w, half_w, z),
        (-half_l, half_w, z), (-half_l, -half_w, z),
        (-half_w, -half_w, z), (-half_w, -half_l, z),
    ]


def make_outer():
    r = KEY_D / 2.0
    return revolve(
        "keycap-outer",
        [(r - TOP_CHAMFER, 0.0), (r, TOP_CHAMFER), (r, KEY_H)],
    )


def make_skirt_cutter():
    return revolve(
        "skirt-cutter",
        [(SKIRT_ID / 2.0, TOP_PLATE), (SKIRT_ID / 2.0, KEY_H + 0.7)],
    )


def make_stem():
    return revolve(
        "stem",
        [(STEM_OD / 2.0, TOP_PLATE - 0.4), (STEM_OD / 2.0, STEM_Z1)],
    )


def make_cross_cutter():
    hl = CROSS_L / 2.0
    hw = CROSS_W / 2.0
    hl2 = hl + CROSS_CHAMFER
    hw2 = hw + CROSS_CHAMFER
    zc = STEM_Z1 - CROSS_CHAMFER
    rings = [
        cross_outline(hl, hw, STEM_Z1 - CROSS_DEPTH),
        cross_outline(hl, hw, zc),
        cross_outline(hl2, hw2, STEM_Z1),
        cross_outline(hl2, hw2, STEM_Z1 + 0.6),
    ]
    return loft("cross-cutter", rings, triangulate=True)


def text_cutter(name, body, cx, cy, height, max_width, z0, z1, mirror_axis):
    cu = bpy.data.curves.new(name + "-font", "FONT")
    cu.body = body
    cu.size = 10.0
    cu.extrude = 0.5
    cu.resolution_u = 8
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    try:
        cu.font = bpy.data.fonts.load(TEXT_FONT, check_existing=True)
    except Exception:
        pass
    ob = bpy.data.objects.new(name + "-text", cu)
    scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), depsgraph=dg)
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)

    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    if not bm.faces:
        bm.free()
        raise RuntimeError("empty text mesh for " + body)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    cxs = (min(xs) + max(xs)) / 2.0
    cys = (min(ys) + max(ys)) / 2.0
    zmin = min(zs)
    bmesh.ops.translate(bm, vec=(-cxs, -cys, -zmin), verts=bm.verts[:])

    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    s = height / h
    if max_width is not None and w * s > max_width:
        s = max_width / w

    if mirror_axis == "x":
        bmesh.ops.scale(bm, vec=(-s, s, 1.0), verts=bm.verts[:])
    elif mirror_axis == "y":
        bmesh.ops.scale(bm, vec=(s, -s, 1.0), verts=bm.verts[:])
    else:
        bmesh.ops.scale(bm, vec=(s, s, 1.0), verts=bm.verts[:])

    zs2 = [v.co.z for v in bm.verts]
    bmesh.ops.scale(
        bm,
        vec=(1.0, 1.0, (z1 - z0) / (max(zs2) - min(zs2))),
        verts=bm.verts[:],
    )
    bmesh.ops.translate(bm, vec=(cx, cy, z0), verts=bm.verts[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm), w * s, h * s


def export_stl(path, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.wm.stl_export(
        filepath=str(path),
        export_selected_objects=True,
        ascii_format=False,
        apply_modifiers=True,
        global_scale=1.0,
        use_scene_unit=False,
        forward_axis="Y",
        up_axis="Z",
    )


# -------------------------------------------------------------------- build ---

keycap = make_outer()
apply_boolean(keycap, make_skirt_cutter(), "DIFFERENCE")
apply_boolean(keycap, make_stem(), "UNION")
apply_boolean(keycap, make_cross_cutter(), "DIFFERENCE")

txt, text_w, text_h = text_cutter(
    "text-top-cutter", TEXT, 0.0, 0.0,
    TEXT_H, TEXT_MAX_W, -0.5, TEXT_DEPTH, "y",
)
apply_boolean(keycap, txt, "DIFFERENCE")

clean(keycap)
export_stl(STL_PATH, [keycap])

# ------------------------------------------------------------------- params ---

params = {
    "unit": "mm",
    "orientation": "print: cap upside down, top face on the bed (z=0), "
                   "skirt mouth up (z=11.3)",
    "body": {
        "diameter": KEY_D,
        "height": KEY_H,
        "top_edge_chamfer_45": TOP_CHAMFER,
    },
    "skirt": {
        "inner_diameter": SKIRT_ID,
        "outer_diameter": KEY_D,
        "wall": (KEY_D - SKIRT_ID) / 2.0,
        "top_plate": TOP_PLATE,
        "mouth_z": KEY_H,
    },
    "stem": {
        "outer_diameter": STEM_OD,
        "z0": STEM_Z0,
        "z1": STEM_Z1,
        "end_inside_mouth": round(KEY_H - STEM_Z1, 3),
    },
    "cross": {
        "length": CROSS_L,
        "width": CROSS_W,
        "depth": CROSS_DEPTH,
        "z_open": STEM_Z1,
        "z_bottom": round(STEM_Z1 - CROSS_DEPTH, 3),
        "mouth_chamfer_45": CROSS_CHAMFER,
    },
    "engraving": {
        "face_z": 0.0,
        "text": TEXT,
        "text_height": round(text_h, 3),
        "text_width": round(text_w, 3),
        "max_width": TEXT_MAX_W,
        "stroke_min": TEXT_STROKE_MIN,
        "depth": TEXT_DEPTH,
        "reads_from": "above, keycap in use",
        "font": TEXT_FONT,
    },
    "boolean_solver": "EXACT",
    "source_mx": MX_SOURCE,
}
with PARAM_PATH.open("w", encoding="utf-8") as fh:
    json.dump(params, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

# ------------------------------------------------------------------ preview ---

body_path = OUT / "body-v2.stl"
if body_path.exists():
    bpy.ops.wm.stl_import(filepath=str(body_path))
    body = bpy.context.selected_objects[0]
    body.name = "body-v2"
else:
    body = None
    print("WARN: body-v2.stl missing, keycap preview only")


def mat(name, color, rough=0.55):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    return m


mat_body = mat("body-charcoal", (0.10, 0.11, 0.13), 0.5)
mat_cap = mat("keycap-red", (0.52, 0.07, 0.05), 0.4)
mat_floor = mat("floor", (0.86, 0.85, 0.83), 0.75)

keycap.data.materials.clear()
keycap.data.materials.append(mat_cap)

if body is not None:
    body.data.materials.clear()
    body.data.materials.append(mat_body)

# assembled keycap: flip print->use, mouth sits on the pocket floor
T = POCKET_Z0 + KEY_H
kc_use = bpy.data.objects.new("keycap-use", keycap.data)
scene.collection.objects.link(kc_use)
kc_use.rotation_euler = (math.pi, 0.0, 0.0)
kc_use.location = (0.0, 0.0, T)

# flipped keycap display: print orientation, cross hole opens up
keycap.location = (54.0, 0.0, 0.0)

floor = bmesh.new()
fv = [
    floor.verts.new(p)
    for p in (
        (-260.0, -260.0, -0.3),
        (300.0, -260.0, -0.3),
        (300.0, 260.0, -0.3),
        (-260.0, 260.0, -0.3),
    )
]
floor.faces.new(fv)
floor_ob = obj_from_bm("floor", floor)
floor_ob.data.materials.append(mat_floor)

world = bpy.data.worlds.new("preview-world")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.90, 0.90, 0.90, 1.0)
bg.inputs[1].default_value = 0.55
scene.world = world

light_data = bpy.data.lights.new("sun", "SUN")
light_data.energy = 3.4
light_data.angle = math.radians(3.0)
sun = bpy.data.objects.new("sun", light_data)
sun.rotation_euler = (math.radians(38.0), math.radians(-14.0), math.radians(-38.0))
scene.collection.objects.link(sun)

fill_data = bpy.data.lights.new("fill", "SUN")
fill_data.energy = 1.0
fill_data.angle = math.radians(25.0)
fill = bpy.data.objects.new("fill", fill_data)
fill.rotation_euler = (math.radians(-46.0), math.radians(22.0), math.radians(30.0))
scene.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("preview-cam")
cam_data.lens = 55.0
cam = bpy.data.objects.new("preview-cam", cam_data)
target = Vector((18.0, 0.0, 9.0))
cam.location = Vector((24.0, -152.0, 118.0))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 96
scene.eevee.use_fast_gi = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT / "body-v2-preview.png")
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"

bpy.ops.render.render(write_still=True)

print("BUILD OK", STL_PATH)
