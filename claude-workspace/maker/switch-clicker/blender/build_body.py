"""Build body A of the STLab switch-clicker keychain (Blender 5.2).

Run: blender -b --python-exit-code 1 -P build_body.py -- out
Units: 1 = 1 mm. STL is in PRINT orientation:
    z = 0   -> top face when in use (switch plate face, sits on the bed)
    z = 14  -> bottom when in use (engraved face, points up while printing)
The part is printed flipped so the plate and the hanging ring touch the bed.
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

# ---------------------------------------------------------------- parameters ---

BODY_X = 34.0
BODY_Y = 30.0
BODY_Z = 14.0
CORNER_R = 4.8

TOP_FILLET_R = 3.0
TOP_CHAMFER_H = 0.8
BOTTOM_FILLET_R = 1.0

PLATE = 1.5
HOLE = 14.0
POCKET = 15.4
POCKET_Z1 = 11.8

RING_OD = 12.0
RING_HOLE = 5.4
RING_T = 4.0
RING_CX = -20.5
RING_CY = 14.0
RING_EDGE_R = 1.0
RING_BED_CHAMFER = 0.4
RING_SEG = 96

TEXT = "STLAB"
TEXT_H = 4.0
TEXT_DEPTH = 0.6
TEXT_CX = 0.0
TEXT_CY = -6.0
TEXT_FONT = r"C:\Windows\Fonts\ariblk.ttf"
ARROW_H = 3.0
ARROW_HALF_W = ARROW_H / math.sqrt(3.0)
ARROW_CX = 0.0
ARROW_CY = 6.0

N_CORNER = 12
N_TOP_FILLET = 10
N_BOTTOM_FILLET = 6

MX_SOURCE = (
    "Cherry MX datasheet: lo 14,0 +-0,05, tam 1,5; "
    "vo duoi tam 5,0 + chan 3,3"
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


def rounded_outline(inset, z, n_corner):
    """CCW rounded-rectangle outline inset from the nominal 34 x 30 wall."""
    hx = BODY_X / 2.0 - inset
    hy = BODY_Y / 2.0 - inset
    r = max(CORNER_R - inset, 0.02)
    ax = hx - r
    ay = hy - r
    pts = []
    corners = (
        (ax, ay, 0.0),
        (-ax, ay, 90.0),
        (-ax, -ay, 180.0),
        (ax, -ay, 270.0),
    )
    for cx, cy, a0 in corners:
        for k in range(n_corner + 1):
            a = math.radians(a0 + 90.0 * k / n_corner)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    return pts


def body_profile():
    """(inset, z) from the bed face up to the engraved face."""
    levels = [(TOP_CHAMFER_H + TOP_FILLET_R, 0.0), (TOP_FILLET_R, TOP_CHAMFER_H)]
    for k in range(1, N_TOP_FILLET + 1):
        th = math.radians(270.0 - 90.0 * k / N_TOP_FILLET)
        levels.append(
            (
                TOP_FILLET_R + TOP_FILLET_R * math.cos(th),
                TOP_CHAMFER_H + TOP_FILLET_R + TOP_FILLET_R * math.sin(th),
            )
        )
    levels.append((0.0, BODY_Z - BOTTOM_FILLET_R))
    for k in range(1, N_BOTTOM_FILLET + 1):
        th = math.radians(180.0 - 90.0 * k / N_BOTTOM_FILLET)
        levels.append(
            (
                BOTTOM_FILLET_R + BOTTOM_FILLET_R * math.cos(th),
                BODY_Z - BOTTOM_FILLET_R + BOTTOM_FILLET_R * math.sin(th),
            )
        )
    return levels


def make_body():
    bm = bmesh.new()
    rings = []
    for inset, z in body_profile():
        rings.append([bm.verts.new(p) for p in rounded_outline(inset, z, N_CORNER)])
    m = len(rings[0])
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(m):
            k = (j + 1) % m
            bm.faces.new((a[j], a[k], b[k], b[j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm("body-a", bm)


def make_ring():
    bm = bmesh.new()
    ro = RING_OD / 2.0
    ri = RING_HOLE / 2.0
    z0, z1 = 0.0, RING_T
    ob, ot, ib, it = [], [], [], []
    for k in range(RING_SEG):
        a = 2.0 * math.pi * k / RING_SEG
        ca, sa = math.cos(a), math.sin(a)
        ob.append(bm.verts.new((RING_CX + ro * ca, RING_CY + ro * sa, z0)))
        ot.append(bm.verts.new((RING_CX + ro * ca, RING_CY + ro * sa, z1)))
        ib.append(bm.verts.new((RING_CX + ri * ca, RING_CY + ri * sa, z0)))
        it.append(bm.verts.new((RING_CX + ri * ca, RING_CY + ri * sa, z1)))
    for k in range(RING_SEG):
        j = (k + 1) % RING_SEG
        bm.faces.new((ob[k], ob[j], ot[j], ot[k]))
        bm.faces.new((ib[k], it[k], it[j], ib[j]))
        bm.faces.new((ot[k], ot[j], it[j], it[k]))
        bm.faces.new((ob[k], ib[k], ib[j], ob[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    top = [e for e in bm.edges if all(abs(v.co.z - z1) < 1e-6 for v in e.verts)]
    bmesh.ops.bevel(
        bm,
        geom=top,
        offset=RING_EDGE_R,
        offset_type="OFFSET",
        segments=12,
        profile=0.5,
        affect="EDGES",
        clamp_overlap=True,
    )
    bed = [e for e in bm.edges if all(abs(v.co.z - z0) < 1e-6 for v in e.verts)]
    bmesh.ops.bevel(
        bm,
        geom=bed,
        offset=RING_BED_CHAMFER,
        offset_type="OFFSET",
        segments=1,
        profile=0.5,
        affect="EDGES",
        clamp_overlap=True,
    )
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm("ring", bm)


def stepped_cutter(name, cx, cy, inner, outer, z0, z1, z2):
    """Square hole below z1, wider pocket above z1."""
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


def text_cutter(name, body, cap_h, cx, cy, z0, z1, font_path):
    cu = bpy.data.curves.new(name + "-font", "FONT")
    cu.body = body
    cu.size = 10.0
    cu.extrude = 0.5
    cu.resolution_u = 8
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    try:
        cu.font = bpy.data.fonts.load(font_path, check_existing=True)
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
    sx = cap_h / (max(ys) - min(ys))
    sz = (z1 - z0) / (max(zs) - min(zs))
    bmesh.ops.translate(bm, vec=(-cxs, -cys, -zmin), verts=bm.verts[:])
    bmesh.ops.scale(bm, vec=(sx, sx, sz), verts=bm.verts[:])
    bmesh.ops.translate(bm, vec=(cx, cy, z0), verts=bm.verts[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


def triangle_cutter(name, cx, cy, height, half_w, z0, z1):
    bm = bmesh.new()
    pts = ((cx, cy + height / 2.0), (cx - half_w, cy - height / 2.0),
           (cx + half_w, cy - height / 2.0))
    lo = [bm.verts.new((x, y, z0)) for x, y in pts]
    hi = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(lo[::-1])
    bm.faces.new(hi)
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
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


# -------------------------------------------------------------------- build ---

body = make_body()
ring = make_ring()
apply_boolean(body, ring, "UNION")

cutter = stepped_cutter(
    "hole-cutter", 0.0, 0.0, HOLE, POCKET, -1.0, PLATE, POCKET_Z1
)
apply_boolean(body, cutter, "DIFFERENCE")

engrave_top = BODY_Z + 0.5
engrave_bottom = BODY_Z - TEXT_DEPTH

txt = text_cutter(
    "text-cutter", TEXT, TEXT_H, TEXT_CX, TEXT_CY,
    engrave_bottom, engrave_top, TEXT_FONT,
)
apply_boolean(body, txt, "DIFFERENCE")

arrow = triangle_cutter(
    "arrow-cutter", ARROW_CX, ARROW_CY, ARROW_H, ARROW_HALF_W,
    engrave_bottom, engrave_top,
)
apply_boolean(body, arrow, "DIFFERENCE")

# clean up tiny boolean seams so the mesh is a single watertight solid
bm = bmesh.new()
bm.from_mesh(body.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-6)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(body.data)
bm.free()
body.data.update()
bpy.context.view_layer.update()

export_stl(OUT / "body-a.stl", [body])

# ------------------------------------------------------------------- params ---

params = {
    "unit": "mm",
    "orientation": "print: z=0 = plate/top face on bed; z=14 = bottom when in use",
    "body": {"x": BODY_X, "y": BODY_Y, "z": BODY_Z, "center_xy": [0.0, 0.0]},
    "corner_radius_vertical": CORNER_R,
    "top_face_edge": {
        "fillet_r": TOP_FILLET_R,
        "bed_chamfer_45_height": TOP_CHAMFER_H,
    },
    "bottom_face_edge_fillet_r": BOTTOM_FILLET_R,
    "plate_thickness": PLATE,
    "hole": {"side": HOLE, "z0": 0.0, "z1": PLATE, "center": [0.0, 0.0]},
    "pocket": {
        "side": POCKET,
        "z0": PLATE,
        "z1": POCKET_Z1,
        "center": [0.0, 0.0],
        "closed_bottom_thickness": round(BODY_Z - POCKET_Z1, 3),
    },
    "hanging_ring": {
        "outer_diameter": RING_OD,
        "hole_diameter": RING_HOLE,
        "thickness": RING_T,
        "center": [RING_CX, RING_CY],
        "edge_fillet_r": RING_EDGE_R,
        "bed_chamfer": RING_BED_CHAMFER,
        "segments": RING_SEG,
    },
    "engraving": {
        "face_z": BODY_Z,
        "text": TEXT,
        "text_height": TEXT_H,
        "stroke_min": 0.8,
        "text_center": [TEXT_CX, TEXT_CY],
        "depth": TEXT_DEPTH,
        "font": TEXT_FONT,
        "arrow": {
            "shape": "equilateral filled triangle",
            "height": ARROW_H,
            "half_width": round(ARROW_HALF_W, 3),
            "center": [ARROW_CX, ARROW_CY],
            "direction": "+Y",
        },
    },
    "boolean_solver": "EXACT",
    "nguon_mx": MX_SOURCE,
}
with (OUT / "body-a-params.json").open("w", encoding="utf-8") as fh:
    json.dump(params, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

# ------------------------------------------------------------------ preview ---

mat_body = bpy.data.materials.new("body-charcoal")
mat_body.use_nodes = True
bsdf = mat_body.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.12, 0.13, 0.15, 1.0)
bsdf.inputs["Roughness"].default_value = 0.55
body.data.materials.clear()
body.data.materials.append(mat_body)

body_print = body
body_print.location = (-38.0, 0.0, 0.0)

body_use = bpy.data.objects.new("body-a-use", body.data)
scene.collection.objects.link(body_use)
body_use.rotation_euler = (math.pi, 0.0, 0.0)
body_use.location = (38.0, 0.0, BODY_Z)

floor = bmesh.new()
fv = [
    floor.verts.new(p)
    for p in (
        (-220.0, -220.0, -0.3), (220.0, -220.0, -0.3),
        (220.0, 220.0, -0.3), (-220.0, 220.0, -0.3),
    )
]
floor.faces.new(fv)
floor_ob = obj_from_bm("floor", floor)
mat_floor = bpy.data.materials.new("floor")
mat_floor.use_nodes = True
bsdf = mat_floor.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.84, 1.0)
bsdf.inputs["Roughness"].default_value = 0.7
floor_ob.data.materials.append(mat_floor)

world = bpy.data.worlds.new("preview-world")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)
bg.inputs[1].default_value = 0.14
scene.world = world

light_data = bpy.data.lights.new("sun", "SUN")
light_data.energy = 3.2
light_data.angle = math.radians(3.0)
sun = bpy.data.objects.new("sun", light_data)
sun.rotation_euler = (math.radians(42.0), math.radians(10.0), math.radians(28.0))
scene.collection.objects.link(sun)

fill_data = bpy.data.lights.new("fill", "SUN")
fill_data.energy = 0.6
fill_data.angle = math.radians(20.0)
fill = bpy.data.objects.new("fill", fill_data)
fill.rotation_euler = (math.radians(-48.0), math.radians(-18.0), math.radians(-32.0))
scene.collection.objects.link(fill)

cam_data = bpy.data.cameras.new("preview-cam")
cam_data.lens = 52.0
cam = bpy.data.objects.new("preview-cam", cam_data)
target = Vector((-4.0, 0.0, 8.0))
cam.location = Vector((-4.0, -215.0, 128.0))
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
scene.render.filepath = str(OUT / "body-a-preview.png")
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"

bpy.ops.render.render(write_still=True)

print("BUILD OK", OUT)
