"""Render 3D tach lop 1 canh: khung rieng / lam rieng / no (exploded). Mo wardrobe.blend da build.

Chay: blender -b wardrobe.blend -P render_door_exploded.py
Xuat: renders/17-canh-C2-*.png, renders/18-canh-C1-*.png
"""
import bpy, math, os

M = 0.001
HERE = os.path.dirname(bpy.data.filepath)
OUT = os.path.join(HERE, "renders")
sc = bpy.context.scene
sc.frame_set(1)
sc.render.resolution_x, sc.render.resolution_y = 1000, 1500


def objs(door):
    return [o for o in bpy.data.objects if o.name.startswith(f"C{door}-")]


def bbox(objs_):
    xs, ys, zs = [], [], []
    for o in objs_:
        for c in o.bound_box:
            w = o.matrix_world @ __import__("mathutils").Vector(c)
            xs.append(w.x); ys.append(w.y); zs.append(w.z)
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def cam_look(name, loc, target, lens=35):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_end = 100
    c = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(c)
    c.location = loc
    t = bpy.data.objects.new(name + "-t", None)
    sc.collection.objects.link(t)
    t.location = target
    con = c.constraints.new("TRACK_TO")
    con.target = t
    con.track_axis, con.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    return c


def render(path):
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def is_lam(o):
    return "-lam" in o.name


def is_frame(o):
    return not is_lam(o)


for door, tag in ((2, "17-canh-C2"), (1, "18-canh-C1")):
    # an het, chi hien canh nay + san
    for col in bpy.data.collections:
        col.hide_render = col.name not in (f"Canh {door}", "Moi truong")
    for o in bpy.data.objects:
        if o.name.startswith("Tuong"):
            o.hide_render = True
    mine = objs(door)
    (x0, x1), (y0, y1), (z0, z1) = bbox(mine)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    tgt = (cx, (y0 + y1) / 2, cz)
    back = cam_look(f"cam-sau-{door}", (cx + 1.9, 4.3, cz + 0.4), tgt, lens=50)        # nhin tu sau (trong tu)
    front = cam_look(f"cam-truoc-{door}", (cx - 2.2, -4.0, cz + 0.4), tgt, lens=50)
    lam = [o for o in mine if is_lam(o)]
    frame = [o for o in mine if is_frame(o)]
    # 1. khung rieng (nhin tu sau thay giang, cang banh, tan rut)
    for o in lam:
        o.hide_render = True
    sc.camera = back
    render(os.path.join(OUT, f"{tag}-1-khung-nhin-sau.png"))
    sc.camera = front
    render(os.path.join(OUT, f"{tag}-2-khung-nhin-truoc.png"))
    # 2. lam rieng
    for o in lam:
        o.hide_render = False
    for o in frame:
        o.hide_render = True
    render(os.path.join(OUT, f"{tag}-3-lam-rieng.png"))
    # 3. no: lam keo ra truoc 0.45 m, banh + cang keo xuong 0.25 m
    for o in frame:
        o.hide_render = False
    saved = {}
    for o in mine:
        saved[o.name] = o.location.copy()
        if is_lam(o):
            o.location.y -= 0.7
        if "banh-duoi" in o.name or "bat-banh" in o.name:
            o.location.z -= 0.25
        if "banh-tren" in o.name or "bulong-tren" in o.name:
            o.location.z += 0.2
    front2 = cam_look(f"cam-no-{door}", (cx - 4.4, -2.3, cz + 0.5), (cx, -0.3, cz), lens=45)
    sc.camera = front2
    render(os.path.join(OUT, f"{tag}-4-no.png"))
    for o in mine:
        o.location = saved[o.name]
print("EXPLODED OK")
