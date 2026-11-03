"""Build body v2 of the STLab switch-clicker keychain (Blender 5.2).

Run: blender -b --python-exit-code 1 -P build_body.py -- out
Units: 1 = 1 mm. The STL is in PRINT orientation == USE orientation:
    z = 0      -> bottom face when in use (engraved face on the bed)
    z = 15.31  -> top rim around the keycap pocket

All dimensions are variables at the top of this file.
"""

import json
import math
import sys
from pathlib import Path

import bmesh
import bpy

argv = sys.argv
OUT = Path(argv[argv.index("--") + 1]) if "--" in argv else Path("out")
OUT = OUT.resolve()
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- parameters ---

BODY_X = 34.0
BODY_Y = 30.0
BODY_Z = 15.31
CORNER_R = 4.8
TOP_FILLET_R = 2.0
BOT_CHAMFER = 0.6

POCKET_D = 27.0
POCKET_Z0 = 11.19
POCKET_MOUTH_R = 0.6

HOLE = 14.0
HOLE_Z0 = 2.61
HOLE_Z1 = 11.19

V_Z0 = 7.75
V_ZMID = 8.50
V_Z1 = 9.25
V_EXT = 0.72

RING_OD = 12.0
RING_HOLE = 5.4
RING_T = 4.0
RING_CX = -20.5
RING_CY = 14.0
RING_EDGE_R = 1.0
RING_BED_CHAMFER = 0.4
RING_SEG = 128

TEXT = "STLAB"
TEXT_H = 4.0
TEXT_DEPTH = 0.4
TEXT_CX = 0.0
TEXT_CY = -8.0
TEXT_STROKE_MIN = 0.8
TEXT_FONT = r"C:\Windows\Fonts\ariblk.ttf"

N_CORNER = 24
N_TOP_FILLET = 16
SEG = 128
N_MOUTH = 12

MX_SOURCE = (
    "fit-library catpaw/mx-socket (voxo3d Cat Paw Clicker, printed on "
    "Bambu A1 + PETG Basic): MX plate hole 14.00 square; switch sits "
    "in a 14.00 square opening with a 0.72 V-notch all around."
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


def rounded_outline(inset, z):
    """CCW rounded-rectangle outline, inset from the 34 x 30 wall."""
    hx = BODY_X / 2.0 - inset
    hy = BODY_Y / 2.0 - inset
    r = max(CORNER_R - inset, 1e-3)
    ax = hx - r
    ay = hy - r
    pts = []
    for cx, cy, a0 in (
        (ax, ay, 0.0),
        (-ax, ay, 90.0),
        (-ax, -ay, 180.0),
        (ax, -ay, 270.0),
    ):
        for k in range(N_CORNER + 1):
            a = math.radians(a0 + 90.0 * k / N_CORNER)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    return pts


def body_profile():
    """(inset, z) levels from the bed face (z=0) to the top face."""
    levels = [(BOT_CHAMFER, 0.0), (0.0, BOT_CHAMFER)]
    zc = BODY_Z - TOP_FILLET_R
    levels.append((0.0, zc))
    for k in range(1, N_TOP_FILLET + 1):
        t = math.radians(90.0 * k / N_TOP_FILLET)
        levels.append(
            (TOP_FILLET_R - TOP_FILLET_R * math.cos(t), zc + TOP_FILLET_R * math.sin(t))
        )
    return levels


def make_body():
    bm = bmesh.new()
    rings = []
    for inset, z in body_profile():
        rings.append([bm.verts.new(p) for p in rounded_outline(inset, z)])
    m = len(rings[0])
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(m):
            k = (j + 1) % m
            bm.faces.new((a[j], a[k], b[k], b[j]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm("body-v2", bm)


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
        segments=16,
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
    return obj_from_bm("ring-v2", bm)


def loft_rings(name, rings, close=True):
    """Closed loft through a list of equal-length vertex coordinate rings."""
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in ring] for ring in rings]
    m = len(vs[0])
    for i in range(len(vs) - 1):
        a, b = vs[i], vs[i + 1]
        for j in range(m):
            k = (j + 1) % m
            bm.faces.new((a[j], a[k], b[k], b[j]))
    if close:
        bm.faces.new(list(reversed(vs[0])))
        bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(name, bm)


def square_ring(side, z):
    h = side / 2.0
    return [(h, -h, z), (h, h, z), (-h, h, z), (-h, -h, z)]


def make_switch_cutter():
    """Square hole 14 -> V-notch 15.44 at z 8.5 -> 14, open above the floor."""
    rings = [
        square_ring(HOLE, HOLE_Z0),
        square_ring(HOLE, V_Z0),
        square_ring(HOLE + 2.0 * V_EXT, V_ZMID),
        square_ring(HOLE, V_Z1),
        square_ring(HOLE, HOLE_Z1 + 0.4),
    ]
    return loft_rings("switch-cutter", rings)


def pocket_profile():
    """(radius, z) of the keycap pocket, with the R0.6 mouth flare."""
    zc = BODY_Z - POCKET_MOUTH_R
    r = POCKET_D / 2.0
    levels = [(r, POCKET_Z0), (r, zc)]
    for k in range(1, N_MOUTH + 1):
        t = math.radians(90.0 * k / N_MOUTH)
        levels.append(
            (r + POCKET_MOUTH_R - POCKET_MOUTH_R * math.cos(t),
             zc + POCKET_MOUTH_R * math.sin(t))
        )
    levels.append((r + POCKET_MOUTH_R, BODY_Z + 0.7))
    return levels


def make_pocket_cutter():
    profile = pocket_profile()
    rings = []
    for rad, z in profile:
        rings.append(
            [
                (rad * math.cos(2.0 * math.pi * k / SEG),
                 rad * math.sin(2.0 * math.pi * k / SEG),
                 z)
                for k in range(SEG)
            ]
        )
    return loft_rings("pocket-cutter", rings)


def text_cutter(name, body, cx, cy, height, max_width, z0, z1, mirror_axis):
    """Cut the string into the face at z0..z1.

    mirror_axis 'x' or 'y' flips the glyphs so the text reads correctly
    when the finished face is viewed from its real side.
    """
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

body = make_body()
ring = make_ring()
apply_boolean(body, ring, "UNION")

switch = make_switch_cutter()
apply_boolean(body, switch, "DIFFERENCE")

pocket = make_pocket_cutter()
apply_boolean(body, pocket, "DIFFERENCE")

txt, text_w, text_h = text_cutter(
    "text-bottom-cutter", TEXT, TEXT_CX, TEXT_CY,
    TEXT_H, None, -0.5, TEXT_DEPTH, "x",
)
apply_boolean(body, txt, "DIFFERENCE")

clean(body)
export_stl(OUT / "body-v2.stl", [body])

# ------------------------------------------------------------------- params ---

params = {
    "unit": "mm",
    "orientation": "print == use: z=0 bottom (engraved), z=15.31 top rim",
    "body": {
        "x": BODY_X,
        "y": BODY_Y,
        "z": BODY_Z,
        "center_xy": [0.0, 0.0],
    },
    "vertical_corner_radius": CORNER_R,
    "top_edge_fillet_r": TOP_FILLET_R,
    "bottom_edge_chamfer_45": BOT_CHAMFER,
    "keycap_pocket": {
        "diameter": POCKET_D,
        "z0": POCKET_Z0,
        "z1": BODY_Z,
        "mouth_fillet_r": POCKET_MOUTH_R,
    },
    "switch_opening": {
        "square": HOLE,
        "z0": HOLE_Z0,
        "z1": HOLE_Z1,
        "closed_bottom_thickness": HOLE_Z0,
        "v_notch": {
            "z0": V_Z0,
            "z_mid": V_ZMID,
            "z1": V_Z1,
            "expansion_per_side": V_EXT,
            "width_at_mid": HOLE + 2.0 * V_EXT,
            "face_angle_deg": round(
                math.degrees(math.atan2(V_EXT, V_ZMID - V_Z0)), 2
            ),
        },
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
        "face_z": 0.0,
        "text": TEXT,
        "text_height": round(text_h, 3),
        "text_width": round(text_w, 3),
        "stroke_min": TEXT_STROKE_MIN,
        "text_center": [TEXT_CX, TEXT_CY],
        "depth": TEXT_DEPTH,
        "reads_from": "below",
        "font": TEXT_FONT,
    },
    "boolean_solver": "EXACT",
    "source_mx": MX_SOURCE,
}
with (OUT / "body-v2-params.json").open("w", encoding="utf-8") as fh:
    json.dump(params, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

print("BUILD OK", OUT / "body-v2.stl")
