"""Build MX switch fit coupon (plate + stem) for STLab keychain clicker.

Run: blender -b --python-exit-code 1 -P build_switch_coupon.py -- out
Units: 1 = 1 mm. STL files are in print orientation (bottom at z = 0).
"""

import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv
OUT = Path(argv[argv.index("--") + 1]) if "--" in argv else Path("out")
OUT = OUT.resolve()
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- geometry ---

PLATE_X = 66.0
PLATE_Y = 24.0
PLATE_Z = 10.5
PLATE_T = 1.5
HOLE_SIZES = (14.00, 14.10, 14.20)
HOLE_CX = (11.0, 33.0, 55.0)
HOLE_CY = 12.0
POCKET = 15.4
TEXT_TOP = 10.5
TEXT_HEIGHT = 2.8
TEXT_DEPTH = 0.6
TEXT_Y0 = 19.7
TEXT_Y1 = 24.0

STEM_D = 14.0
STEM_H = 6.0
STEM_SEG = 128
STEM_CX = (0.0, 20.0, 40.0)
CROSS_TOP = 2.0
CROSS_DEPTH = 4.0
CROSS_ARMS = ((4.33, 1.35), (4.43, 1.45), (4.53, 1.55))
NUM_HEIGHT = 2.5
NUM_DEPTH = 0.4
NUM_Y = 4.6

SOURCE = "Cherry MX datasheet; dennisleexyz/keycaps stem.scad (4.23/1.25 + Tol)"


def obj_from_bm(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def make_box(name, x0, x1, y0, y1, z0, z1):
    bm = bmesh.new()
    v = [
        bm.verts.new(p)
        for p in (
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
        )
    ]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
              (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


def stepped_cutter(name, cx, cy, inner, outer, z0, z1, z2):
    """Stepped square prism: inner hole below z1, wider pocket above z1."""
    bm = bmesh.new()
    sq = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    hi = inner / 2.0
    ho = outer / 2.0
    ai = [bm.verts.new((cx + sx * hi, cy + sy * hi, z0)) for sx, sy in sq]
    bi = [bm.verts.new((cx + sx * hi, cy + sy * hi, z1)) for sx, sy in sq]
    bo = [bm.verts.new((cx + sx * ho, cy + sy * ho, z1)) for sx, sy in sq]
    co = [bm.verts.new((cx + sx * ho, cy + sy * ho, z2)) for sx, sy in sq]
    bm.faces.new(ai[::-1])
    bm.faces.new(co)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((ai[i], ai[j], bi[j], bi[i]))
        bm.faces.new((bi[i], bi[j], bo[j], bo[i]))
        bm.faces.new((bo[i], bo[j], co[j], co[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


def cross_prism(name, cx, cy, length, thick, z0, z1):
    a = length / 2.0
    h = thick / 2.0
    pts = (
        (a, h), (h, h), (h, a), (-h, a), (-h, h), (-a, h),
        (-a, -h), (-h, -h), (-h, -a), (h, -a), (h, -h), (a, -h),
    )
    bm = bmesh.new()
    lo = [bm.verts.new((cx + x, cy + y, z0)) for x, y in pts]
    hi = [bm.verts.new((cx + x, cy + y, z1)) for x, y in pts]
    bm.faces.new(lo)
    bm.faces.new(hi)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


def text_cutter(name, body, cap_h, cx, cy, z0, z1):
    cu = bpy.data.curves.new(name + "-font", "FONT")
    cu.body = body
    cu.size = 10.0
    cu.extrude = 0.0
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
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

    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    cxs = (min(xs) + max(xs)) / 2.0
    cys = (min(ys) + max(ys)) / 2.0
    s = cap_h / (max(ys) - min(ys))
    bmesh.ops.translate(bm, vec=(-cxs, -cys, 0.0), verts=bm.verts[:])
    bmesh.ops.scale(bm, vec=(s, s, 1.0), verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=(cx, cy, z0), verts=bm.verts[:])

    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    top = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, z1 - z0), verts=top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


def apply_boolean(target, cutter):
    mod = target.modifiers.new("bool", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    new_me = bpy.data.meshes.new_from_object(
        target.evaluated_get(dg), depsgraph=dg
    )
    target.modifiers.clear()
    old = target.data
    target.data = new_me
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.context.view_layer.update()


def make_cylinder(name, cx, cy, radius, z0, z1, segments):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=z1 - z0,
    )
    bmesh.ops.translate(
        bm, vec=(cx, cy, (z0 + z1) / 2.0), verts=bm.verts[:]
    )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


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


# ------------------------------------------------------------------- plate ---

plate = make_box("plate-coupon", 0.0, PLATE_X, 0.0, PLATE_Y, 0.0, PLATE_Z)

for size, cx in zip(HOLE_SIZES, HOLE_CX):
    cut = stepped_cutter(
        "hole-cutter", cx, HOLE_CY, size, POCKET, -1.0, PLATE_T, PLATE_Z + 2.0
    )
    apply_boolean(plate, cut)

text_cy = (TEXT_Y0 + TEXT_Y1) / 2.0
for label, cx in zip(("14.0", "14.1", "14.2"), HOLE_CX):
    cut = text_cutter(
        "plate-text-" + label,
        label,
        TEXT_HEIGHT,
        cx,
        text_cy,
        TEXT_TOP - TEXT_DEPTH,
        TEXT_TOP + 1.5,
    )
    apply_boolean(plate, cut)

export_stl(OUT / "plate-coupon.stl", [plate])

# ------------------------------------------------------------------- stems ---

stems = []
for idx, (cx, (length, thick)) in enumerate(zip(STEM_CX, CROSS_ARMS)):
    stem = make_cylinder(
        "stem-%d" % (idx + 1), cx, 0.0, STEM_D / 2.0, 0.0, STEM_H, STEM_SEG
    )
    cross = cross_prism(
        "cross-cutter", cx, 0.0, length, thick, CROSS_TOP, STEM_H + 2.0
    )
    apply_boolean(stem, cross)
    num = text_cutter(
        "stem-num-%d" % (idx + 1),
        str(idx + 1),
        NUM_HEIGHT,
        cx,
        NUM_Y,
        STEM_H - NUM_DEPTH,
        STEM_H + 1.5,
    )
    apply_boolean(stem, num)
    stems.append(stem)

export_stl(OUT / "stem-coupon.stl", stems)

# ------------------------------------------------------------------ params ---

params = {
    "unit": "mm",
    "source": SOURCE,
    "plate": {
        "frame": {"x": PLATE_X, "y": PLATE_Y, "z": PLATE_Z},
        "plate_thickness": PLATE_T,
        "square_holes": [
            {"side": size, "cx": cx, "cy": HOLE_CY, "through": True}
            for size, cx in zip(HOLE_SIZES, HOLE_CX)
        ],
        "pockets": {"side": POCKET, "z0": PLATE_T, "z1": PLATE_Z},
        "engraved_labels": {
            "text": ["14.0", "14.1", "14.2"],
            "height": TEXT_HEIGHT,
            "depth": TEXT_DEPTH,
            "y_range": [TEXT_Y0, TEXT_Y1],
            "z_surface": TEXT_TOP,
        },
    },
    "stem": {
        "posts": {
            "diameter": STEM_D,
            "height": STEM_H,
            "segments": STEM_SEG,
            "centers": [[cx, 0.0] for cx in STEM_CX],
        },
        "cross_holes": {
            "z_top": STEM_H,
            "z_bottom": CROSS_TOP,
            "depth": CROSS_DEPTH,
            "arms": [
                {"length": length, "thickness": thick}
                for length, thick in CROSS_ARMS
            ],
        },
        "engraved_numbers": {
            "text": ["1", "2", "3"],
            "height": NUM_HEIGHT,
            "depth": NUM_DEPTH,
            "center_y": NUM_Y,
        },
    },
}
with (OUT / "switch-coupon-params.json").open("w", encoding="utf-8") as fh:
    json.dump(params, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

# ----------------------------------------------------------------- preview ---

mat_plate = bpy.data.materials.new("plate-pla")
mat_plate.use_nodes = True
bsdf = mat_plate.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.3, 0.32, 0.35, 1.0)
bsdf.inputs["Roughness"].default_value = 0.45
plate.data.materials.clear()
plate.data.materials.append(mat_plate)

mat_stem = bpy.data.materials.new("stem-orange")
mat_stem.use_nodes = True
bsdf = mat_stem.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.93, 0.48, 0.12, 1.0)
bsdf.inputs["Roughness"].default_value = 0.4
for stem in stems:
    stem.data.materials.clear()
    stem.data.materials.append(mat_stem)
    stem.location = (0.0, -30.0, 0.0)

floor = make_box("floor", -180.0, 240.0, -200.0, 200.0, -0.4, -0.2)
mat_floor = bpy.data.materials.new("floor")
mat_floor.use_nodes = True
bsdf = mat_floor.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.84, 1.0)
bsdf.inputs["Roughness"].default_value = 0.7
floor.data.materials.clear()
floor.data.materials.append(mat_floor)

world = bpy.data.worlds.new("preview-world")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)
bg.inputs[1].default_value = 0.12
scene.world = world

light_data = bpy.data.lights.new("sun", "SUN")
light_data.energy = 3.0
light_data.angle = math.radians(2.0)
sun = bpy.data.objects.new("sun", light_data)
sun.rotation_euler = (math.radians(38.0), math.radians(12.0), math.radians(25.0))
scene.collection.objects.link(sun)

fill_data = bpy.data.lights.new("fill", "SUN")
fill_data.energy = 0.5
fill_data.angle = math.radians(20.0)
fill = bpy.data.objects.new("fill", fill_data)
fill.rotation_euler = (math.radians(-45.0), math.radians(-20.0), math.radians(-30.0))
scene.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("preview-cam")
cam_data.lens = 40.0
cam = bpy.data.objects.new("preview-cam", cam_data)
target = Vector((33.0, -8.0, 3.0))
cam.location = Vector((98.0, -96.0, 84.0))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = 64
scene.eevee.use_fast_gi = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT / "switch-coupon-preview.png")
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"

bpy.ops.render.render(write_still=True)

print("BUILD OK", OUT)
