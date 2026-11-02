"""Print-in-place clearance coupon builder for the STLab flexi goat.

Run with:
    blender -b --python-exit-code 1 -P build_coupon.py -- out

Units: 1 Blender unit = 1 mm.  Z is up, print bed is z = 0.

Each coupon contains three parallel chains (spaced 6 mm apart along Y) and
each chain has three links along +X.  The only difference between the three
chains is the radial pin/hole clearance c = 0.4 / 0.5 / 0.6 mm.  Links are
built independently so the exported mesh has 9 disconnected, watertight
islands that interlock (print-in-place).

All dimensions come from spec-coupon.md; nothing here is guessed.
"""

import bpy
import bmesh
import json
import math
import os
import sys
from mathutils import Matrix, Vector

N_ARC = 160          # segments used for the body / blade / cavity arcs
N_CYL = 128          # cylinder facets (spec: >= 64)


CONFIG = {
    "desk": {
        "W": 16.0,
        "H": 8.0,
        "S": 20.0,
        "Ra": 8.4,
        "g": 0.6,
        "d": 4.0,
        "T": 3.0,
        "zg": 0.4,
        "Rt": 4.0,
        "sg": 0.6,
        "phi": 15.0,
        "text_h": 5.0,
        "text_depth": 0.6,
        "labels": ["0.4", "0.5", "0.6"],
    },
    "keychain": {
        "W": 10.0,
        "H": 5.0,
        "S": 12.0,
        "Ra": 5.2,
        "g": 0.6,
        "d": 3.0,
        "T": 2.0,
        "zg": 0.4,
        "Rt": 3.1,
        "sg": 0.6,
        "phi": 15.0,
        "text_h": 3.0,
        "text_depth": 0.4,
        "labels": ["4", "5", "6"],
    },
}

CLEARANCES = [0.4, 0.5, 0.6]
CHAIN_GAP = 6.0


# ----------------------------------------------------------------------------
# Blender helpers
# ----------------------------------------------------------------------------
def clean_poly(pts):
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) > 1e-9 or abs(p[1] - out[-1][1]) > 1e-9:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-9 and abs(out[0][1] - out[-1][1]) < 1e-9:
        out.pop()
    return out


def new_mesh_object(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def make_prism(name, poly, z0, z1):
    """Closed prism from a simple (possibly concave) planar polygon."""
    poly = clean_poly(poly)
    bm = bmesh.new()
    vb = [bm.verts.new((x, y, z0)) for (x, y) in poly]
    vt = [bm.verts.new((x, y, z1)) for (x, y) in poly]
    bm.verts.ensure_lookup_table()
    f_bottom = bm.faces.new(list(reversed(vb)))
    f_top = bm.faces.new(list(vt))
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bmesh.ops.triangulate(bm, faces=[f_bottom, f_top],
                          quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_mesh_object(name, bm)


def make_cylinder(name, radius, x, y, z0, z1, segments=N_CYL):
    depth = z1 - z0
    zc = 0.5 * (z0 + z1)
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius,
                                        depth=depth, end_fill_type="NGON",
                                        location=(x, y, zc))
    ob = bpy.context.object
    ob.name = name
    return ob


def apply_boolean(target, cutter, operation):
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new(name="bool", type="BOOLEAN")
    mod.operation = operation
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mesh = cutter.data
    bpy.data.objects.remove(cutter, do_unlink=True)
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)


# ----------------------------------------------------------------------------
# 2D profiles
# ----------------------------------------------------------------------------
def body_profile(k, C):
    W2 = 0.5 * C["W"]
    S = C["S"]
    Ra = C["Ra"]
    Rh = Ra + C["g"]
    Pp = (k - 1) * S
    Pk = k * S
    N = N_ARC

    pts = []
    if k == 0:
        x_head = -S + Ra + C["g"]
        x_head_b = x_head
    else:
        thmax = math.asin(W2 / Rh)
        x_head_b = Pp + Rh * math.cos(thmax)
    pts.append((x_head_b, -W2))

    if k < 2:
        thmax_t = math.asin(min(1.0, W2 / Ra))
        xt_b = Pk + Ra * math.cos(thmax_t)
        pts.append((xt_b, -W2))
        for i in range(1, N + 1):
            th = -thmax_t + 2.0 * thmax_t * i / N
            pts.append((Pk + Ra * math.cos(th), Ra * math.sin(th)))
        xt_t = Pk + Ra * math.cos(thmax_t)
    else:
        xt_t = 2.0 * S + Ra
        pts.append((xt_t, -W2))
        pts.append((xt_t, W2))

    if k == 0:
        x_head_t = x_head_b
    else:
        x_head_t = x_head_b
    pts.append((x_head_t, W2))

    if k > 0:
        thmax_h = math.asin(W2 / Rh)
        for i in range(1, N):
            th = thmax_h - 2.0 * thmax_h * i / N
            pts.append((Pp + Rh * math.cos(th), Rh * math.sin(th)))

    return pts


def blade_profile(k, C):
    P = (k - 1) * C["S"]
    Rt = C["Rt"]
    Rh = C["Ra"] + C["g"]
    x_right = P + Rh + 2.0
    N = N_ARC
    pts = [(x_right, -Rt), (x_right, Rt), (P, Rt)]
    for i in range(1, N + 1):
        ang = 0.5 * math.pi + math.pi * i / N
        pts.append((P + Rt * math.cos(ang), Rt * math.sin(ang)))
    return pts


def cavity_profile(k, C):
    P = k * C["S"]
    Rb = C["Rt"] + C["sg"]
    tphi = math.tan(math.radians(C["phi"]))
    Lc = C["Ra"] + 1.0
    xr = P + Lc
    yh = Rb + Lc * tphi
    N = N_ARC
    pts = [(xr, -yh), (xr, yh), (P, Rb)]
    for i in range(1, N + 1):
        ang = 0.5 * math.pi + math.pi * i / N
        pts.append((P + Rb * math.cos(ang), Rb * math.sin(ang)))
    return pts


# ----------------------------------------------------------------------------
# Engraved text
# ----------------------------------------------------------------------------
def make_text_cutter(label, height, depth, top_z, tx):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.object.text_add(location=(0.0, 0.0, 0.0))
    t = bpy.context.object
    t.data.body = label
    t.data.size = 10.0
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.extrude = 0.0
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    cx = 0.5 * (min(xs) + max(xs))
    cy = 0.5 * (min(ys) + max(ys))
    gy = max(ys) - min(ys)
    scale = height / gy

    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for v in bm.verts:
        v.co.x = (v.co.x - cx) * scale
        v.co.y = (v.co.y - cy) * scale
        v.co.z = 0.0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    res = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    new_verts = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, depth + 1.0))
    bmesh.ops.translate(bm, verts=list(bm.verts), vec=(tx, 0.0, top_z - depth))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    ob.name = "engrave_" + label
    return ob


# ----------------------------------------------------------------------------
# One link
# ----------------------------------------------------------------------------
def build_link(k, C, c, x_shift, y_shift):
    body = make_prism("link%d_body" % k, body_profile(k, C), 0.0, C["H"])

    if k > 0:
        blade = make_prism("link%d_blade" % k, blade_profile(k, C), 0.0, C["T"])
        apply_boolean(body, blade, "UNION")

    if k < 2:
        cav = make_prism("link%d_cavity" % k, cavity_profile(k, C),
                         -1.0, C["T"] + C["zg"])
        pin_void = make_cylinder("link%d_pinvoid" % k, 0.5 * C["d"],
                                 k * C["S"], 0.0, -1.0, C["T"] + C["zg"] + 2.0)
        apply_boolean(cav, pin_void, "DIFFERENCE")
        apply_boolean(body, cav, "DIFFERENCE")

    if k > 0:
        hole = make_cylinder("link%d_hole" % k,
                             0.5 * C["d"] + c,
                             (k - 1) * C["S"], 0.0, -1.0, C["T"] + 2.0)
        apply_boolean(body, hole, "DIFFERENCE")

    if k == 0:
        label = C["labels"][c_index(c)]
        W2 = 0.5 * C["W"]
        ytext = 0.5 * C["text_h"]
        x_tail = math.sqrt(max(0.0, C["Ra"] ** 2 - ytext ** 2))
        tx = 0.5 * ((-C["S"] + C["Ra"] + C["g"]) + x_tail)
        txt = make_text_cutter(label, C["text_h"], C["text_depth"],
                               C["H"], tx)
        apply_boolean(body, txt, "DIFFERENCE")

    body.data.transform(Matrix.Translation((x_shift, y_shift, 0.0)))
    body.name = "link%d" % k
    return body


def c_index(c):
    for i, val in enumerate(CLEARANCES):
        if abs(val - c) < 1e-9:
            return i
    raise ValueError("unknown clearance %r" % c)


# ----------------------------------------------------------------------------
# One coupon
# ----------------------------------------------------------------------------
def build_coupon(name, C):
    bpy.ops.object.select_all(action="DESELECT")
    S = C["S"]
    W = C["W"]
    Ra = C["Ra"]
    x_min = -S + Ra + C["g"]
    x_max = 2.0 * S + Ra
    x_shift = -0.5 * (x_min + x_max)

    links = []
    for ci, c in enumerate(CLEARANCES):
        y_shift = (ci - 1) * (W + CHAIN_GAP)
        for k in range(3):
            links.append(build_link(k, C, c, x_shift, y_shift))

    bpy.ops.object.select_all(action="DESELECT")
    for ob in links:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = links[0]
    bpy.ops.object.join()
    coupon = bpy.context.object
    coupon.name = "coupon-" + name
    coupon.data.name = "coupon-" + name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return coupon


# ----------------------------------------------------------------------------
# Export
# ----------------------------------------------------------------------------
def export_stl(ob, path):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.wm.stl_export(
        filepath=path,
        export_selected_objects=True,
        apply_modifiers=True,
        ascii_format=False,
        global_scale=1.0,
        use_scene_unit=False,
    )


# ----------------------------------------------------------------------------
# Preview
# ----------------------------------------------------------------------------
def render_preview(ob, path):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x = 1600
    sc.render.resolution_y = 1000
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    try:
        sc.eevee.taa_render_samples = 64
    except Exception:
        pass

    world = bpy.data.worlds.new("CouponWorld")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.92, 0.94, 0.97, 1.0)
    bg.inputs[1].default_value = 1.0

    mat = bpy.data.materials.new("CouponMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (0.86, 0.34, 0.12, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.45
    ob.data.materials.clear()
    ob.data.materials.append(mat)

    bpy.ops.mesh.primitive_plane_add(size=800.0, location=(0.0, 0.0, -0.05))
    ground = bpy.context.object
    gmat = bpy.data.materials.new("GroundMat")
    gmat.use_nodes = True
    gb = gmat.node_tree.nodes.get("Principled BSDF")
    if gb is not None:
        gb.inputs["Base Color"].default_value = (0.95, 0.95, 0.95, 1.0)
        gb.inputs["Roughness"].default_value = 0.9
    ground.data.materials.append(gmat)

    bpy.ops.object.light_add(type="SUN", location=(80.0, -120.0, 240.0))
    sun = bpy.context.object
    sun.data.energy = 3.5
    sun.data.angle = math.radians(8.0)
    sun.rotation_euler = Vector((0.45, 0.55, -1.0)).to_track_quat("-Z", "Y").to_euler()

    bpy.ops.object.light_add(type="AREA", location=(-140.0, -180.0, 180.0))
    fill = bpy.context.object
    fill.data.energy = 1200000.0
    fill.data.size = 220.0
    fill.rotation_euler = (Vector((0.0, 0.0, 4.0)) - fill.location).to_track_quat("-Z", "Y").to_euler()

    bb = [Vector(c) for c in ob.bound_box]
    lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    center = 0.5 * (lo + hi)

    direction = Vector((0.35, -1.0, 1.15)).normalized()
    cam_loc = center + direction * 300.0
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.object
    sc.camera = cam
    cam.data.type = "ORTHO"
    cam.data.clip_end = 2000.0
    cam.rotation_euler = (center - cam_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.view_layer.update()
    cam_mat = cam.matrix_world.copy()
    inv = cam_mat.inverted()
    px, py = [], []
    for corner in ob.bound_box:
        p = inv @ Vector(corner)
        px.append(p.x)
        py.append(p.y)
    x_ran = max(px) - min(px)
    y_ran = max(py) - min(py)
    aspect = sc.render.resolution_x / sc.render.resolution_y
    cam.data.ortho_scale = max(x_ran, y_ran * aspect) * 1.18
    off_x = 0.5 * (max(px) + min(px))
    off_y = 0.5 * (max(py) + min(py))
    cam.location = cam.location + cam_mat.to_3x3() @ Vector((off_x, off_y, 0.0))
    bpy.context.view_layer.update()

    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ----------------------------------------------------------------------------
# Parameters file
# ----------------------------------------------------------------------------
def write_params(path):
    data = {
        "unit": "mm",
        "note": "Clearance coupon for print-in-place flexi goat; three chains per coupon.",
        "chain_gap": CHAIN_GAP,
        "links_per_chain": 3,
        "clearances_c": CLEARANCES,
        "config": {},
    }
    for name, C in CONFIG.items():
        entry = dict(C)
        entry["Rh"] = C["Ra"] + C["g"]
        entry["Rb"] = C["Rt"] + C["sg"]
        entry["hole_diameter"] = [C["d"] + 2.0 * c for c in CLEARANCES]
        entry["blade_wall_remaining"] = [C["Rt"] - 0.5 * C["d"] - c for c in CLEARANCES]
        entry["min_gap_theoretical_per_chain"] = [min(c, C["g"], C["sg"], C["zg"])
                                                   for c in CLEARANCES]
        data["config"][name] = entry
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    argv = sys.argv
    out_dir = "out"
    if "--" in argv:
        rest = argv[argv.index("--") + 1:]
        if rest:
            out_dir = rest[0]
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)

    desk = build_coupon("desk", CONFIG["desk"])
    export_stl(desk, os.path.join(out_dir, "coupon-desk.stl"))

    keychain = build_coupon("keychain", CONFIG["keychain"])
    export_stl(keychain, os.path.join(out_dir, "coupon-keychain.stl"))

    write_params(os.path.join(out_dir, "coupon-params.json"))

    kmesh = keychain.data
    bpy.data.objects.remove(keychain, do_unlink=True)
    if kmesh.users == 0:
        bpy.data.meshes.remove(kmesh)

    render_preview(desk, os.path.join(out_dir, "coupon-preview.png"))
    print("BUILD_DONE", out_dir)


if __name__ == "__main__":
    main()
