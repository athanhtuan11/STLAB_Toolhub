"""Buoc 0 esp32-s3-cam: render concept 3 phuong an vo camera (A soi / B hop / C mat) bang Blender.
Khoi minh hoa, KHONG phai CAD. Chay: blender -b -P make_concepts.py -- <thu-muc-ra> [eevee|cycles] [samples]
"""
import math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = Path(argv[0]); OUT.mkdir(parents=True, exist_ok=True)
ENGINE = argv[1] if len(argv) > 1 else "cycles"
SAMPLES = int(argv[2]) if len(argv) > 2 else 64
ONLY = argv[3] if len(argv) > 3 else "ABC"
FONT = r"D:\04_Stlab\04_STLAB_Toolhub\claude-workspace\studio\design\fonts\BeVietnamPro-Bold.ttf"
S = 0.001  # mm -> m


def lin(h):
    v = int(h, 16) / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def rgb(hx):
    return tuple(lin(hx[i:i + 2]) for i in (1, 3, 5))


MATS = {}


def mat(name, hx, rough=0.45, emit=None):
    key = (name, hx, rough, emit)
    if key in MATS:
        return MATS[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb(hx), 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb(emit), 1)
        b.inputs["Emission Strength"].default_value = 3.0
    MATS[key] = m
    return m


# Mau PETG (TODO: xac nhan ten mau hang cho tung cuon)
def WHITE(): return mat("Trang", "#CBD1CD", 0.5)
def BLACK(): return mat("Den", "#1B1E1F", 0.5)
def GLASS(): return mat("Kinh", "#07090A", 0.08)
def PINE(): return mat("Thong", "#1E5A45", 0.5)
def SAND(): return mat("Cat", "#CBB997", 0.5)
def GREEN_LED(): return mat("LED", "#4DFF9A", 0.3, emit="#4DFF9A")
def RED_LED(): return mat("LEDdo", "#FF3B2F", 0.3, emit="#FF3B2F")
def FLOOR(): return mat("San", "#BFCEC7", 0.9)
def WALLPLATE(): return mat("Oca", "#F4F5F3", 0.4)
def HOLE(): return mat("Lo", "#222629", 0.6)


def finish(ob, m, smooth=True):
    ob.data.materials.clear()
    ob.data.materials.append(m)
    if smooth:
        for p in ob.data.polygons:
            p.use_smooth = True


def sel(ob):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def apply_mods(ob):
    sel(ob)
    for md in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=md.name)


def bevel(ob, r, seg=6):
    md = ob.modifiers.new("bv", "BEVEL")
    md.width = r * S
    md.segments = seg
    md.limit_method = "ANGLE"
    md.angle_limit = math.radians(30)
    apply_mods(ob)


def box(size, loc, r=0, m=None, seg=6, name="box"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(v * S for v in loc))
    ob = bpy.context.object
    ob.name = name
    ob.scale = tuple(v * S for v in size)
    sel(ob); bpy.ops.object.transform_apply(scale=True)
    if r > 0:
        bevel(ob, r, seg)
    finish(ob, m or WHITE())
    return ob


def cyl(d, h, loc, axis="z", m=None, r=0, name="cyl", verts=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=d / 2 * S, depth=h * S, vertices=verts, location=tuple(v * S for v in loc))
    ob = bpy.context.object
    ob.name = name
    if axis == "y":
        ob.rotation_euler = (math.radians(90), 0, 0)
    elif axis == "x":
        ob.rotation_euler = (0, math.radians(90), 0)
    sel(ob); bpy.ops.object.transform_apply(rotation=True)
    if r > 0:
        bevel(ob, r, 4)
    finish(ob, m or WHITE())
    return ob


def sphere(d, loc, m=None, name="sph"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=d / 2 * S, segments=96, ring_count=48, location=tuple(v * S for v in loc))
    ob = bpy.context.object
    ob.name = name
    finish(ob, m or WHITE())
    return ob


def cut(ob, cutter):
    md = ob.modifiers.new("cut", "BOOLEAN")
    md.operation = "DIFFERENCE"
    md.object = cutter
    md.solver = "EXACT"
    apply_mods(ob)
    bpy.data.objects.remove(cutter, do_unlink=True)


def common(ob, other):
    md = ob.modifiers.new("int", "BOOLEAN")
    md.operation = "INTERSECT"
    md.object = other
    md.solver = "EXACT"
    apply_mods(ob)
    bpy.data.objects.remove(other, do_unlink=True)


def slots(ob, n, pitch, w, l, x0, y0, z0, depth):
    """n khe, dai l theo Y, rong w theo X, tam khoet o z0."""
    for i in range(n):
        c = box((w, l, depth), (x0 + (i - (n - 1) / 2) * pitch, y0, z0), r=min(w / 2 - 0.05, 0.9), name="slot")
        cut(ob, c)


def text_cut(ob, txt, size, loc, depth=0.6):
    """Chu khac sau 'depth' vao mat huong -Y; loc = tam chu tren mat (mm)."""
    bpy.ops.object.text_add(location=(loc[0] * S, loc[1] * S, loc[2] * S), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object
    t.data.body = txt
    t.data.font = bpy.data.fonts.load(FONT)
    t.data.size = size * S
    t.data.extrude = depth * S
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.offset_x = 0
    sel(t)
    bpy.ops.object.convert(target="MESH")
    # text voi rot X=90: do day keo ve phia +-Y; dat sao cho 2*depth cat vao be mat
    t.location.y += depth * S * 0.0
    cut(ob, t)


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MATS.clear()


LIGHTS = (("Key", (-0.30, -0.35, 0.45), 28, 0.30), ("Fill", (0.40, -0.25, 0.20), 8, 0.4), ("Rim", (0.10, 0.30, 0.35), 10, 0.3))


def set_lights(flip):
    for name, loc, pw, sz in LIGHTS:
        l = bpy.data.objects[name]
        x, y, z = loc
        if flip:
            x, y = -x * 0.8, -y * 0.9
        l.location = (x, y, z)
        l.data.energy = pw * (0.55 if flip else 1.0)
        l.rotation_euler = (Vector((0, 0, 0.04)) - l.location).to_track_quat("-Z", "Y").to_euler()


def setup_scene(size=(1500, 1125)):
    sc = bpy.context.scene
    if ENGINE == "cycles":
        sc.render.engine = "CYCLES"
        sc.cycles.samples = SAMPLES
        sc.cycles.use_denoising = True
    else:
        ids = {i.identifier for i in sc.render.bl_rna.properties["engine"].enum_items}
        sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in ids else next(iter(ids))
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = -0.8
    for look in ("AgX - Medium High Contrast", "AgX - Medium Contrast"):
        try:
            sc.view_settings.look = look
            break
        except Exception:
            pass
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*rgb("#ECF1EF"), 1)
    bg.inputs["Strength"].default_value = 0.4
    verts = [(-2, -2, 0), (2, -2, 0), (2, 0.25, 0), (-2, 0.25, 0), (2, 0.37, 0.12), (-2, 0.37, 0.12), (2, 0.40, 1.5), (-2, 0.40, 1.5)]
    faces = [(0, 1, 2, 3), (3, 2, 4, 5), (5, 4, 6, 7)]
    me = bpy.data.meshes.new("cyc"); me.from_pydata(verts, [], faces); me.update()
    cy = bpy.data.objects.new("cyc", me); sc.collection.objects.link(cy)
    cy.data.materials.append(FLOOR())
    for p in cy.data.polygons:
        p.use_smooth = True
    for name, loc, pw, sz in LIGHTS:
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object
        l.name = name
        l.data.energy = pw
        l.data.size = sz
        l.rotation_euler = (Vector((0, 0, 0.04)) - l.location).to_track_quat("-Z", "Y").to_euler()
    return sc


def smooth_all():
    for ob in list(bpy.data.objects):
        if ob.type == "MESH" and ob.name != "cyc":
            bm = bmesh.new(); bm.from_mesh(ob.data)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(ob.data); bm.free()
            sel(ob)
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))


def shoot(sc, name, target, cam_loc, lens=70):
    smooth_all()
    cam = bpy.data.objects.get("Cam")
    if cam is None:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
        cam.name = "Cam"
    sc.camera = cam
    cam.data.lens = lens
    cam.location = cam_loc
    cam.rotation_euler = (Vector(target) - Vector(cam_loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(OUT / name)
    bpy.ops.render.render(write_still=True)


def lens_assembly(cx, cz, yf, d_ring=24, d_glass=11):
    """Ong kinh: vong den + kinh, nhin ve -Y. yf = mat truoc."""
    cyl(d_ring, 1.6, (cx, yf - 0.2, cz), "y", BLACK(), r=0.5, name="ring")
    cyl(d_ring * 0.62, 1.0, (cx, yf - 1.0, cz), "y", mat("Kinh2", "#2B3033", 0.2), name="ring2")
    cyl(d_glass, 1.0, (cx, yf - 1.5, cz), "y", GLASS(), name="glass")
    cyl(d_glass * 0.3, 0.3, (cx - d_glass * 0.18, yf - 2.1, cz + d_glass * 0.18), "y", mat("Phanxa", "#3C4A63", 0.1), name="glint", verts=20)


def leds(cx, cz, yf):
    cyl(3.4, 1.0, (cx, yf - 0.1, cz), "y", GREEN_LED(), name="led_g", verts=24)
    cyl(3.4, 1.0, (cx + 7, yf - 0.1, cz), "y", RED_LED(), name="led_r", verts=24)


# ---------------------------------------------------------------- A: SOI
def build_A():
    D, W, H = 40, 60, 66
    zc = 54
    body = box((W, D, H), (0, 0, zc), r=9, m=WHITE(), name="A_body", seg=8)
    yf = -D / 2
    # mat truoc (mau 2) = lat cat truoc 8 mm cua chinh vien soi, nho hon thoi 0,3 mm de lo duong chia mau
    cap = box((W + 0.5, D + 0.6, H + 0.5), (0, -0.3, zc), r=9, m=PINE(), name="A_cap", seg=8)
    common(cap, box((100, 8, 120), (0, yf - 0.3 + 4 - 0.25, zc), name="slab"))
    lens_assembly(0, zc + 9, yf, d_ring=26, d_glass=12)
    leds(-3.5, zc - 12, yf)
    text_cut(cap, "STLAB", 5.0, (0, yf - 0.0, zc - 19.5))
    slots(body, 6, 5.0, 2.0, 18, 0, 4, zc + H / 2 - 1, 8)
    slots(body, 6, 5.0, 2.0, 18, 0, 4, zc - H / 2 + 1, 8)
    cut(body, box((13, 8, 8), (0, D / 2 - 2, zc - H / 2 + 5), r=1.5, name="usb"))
    cyl(70, 9, (0, 6, 4.5), "z", SAND(), r=3, name="A_base")
    cyl(18, 22, (0, 18, 18), "z", SAND(), r=2, name="A_neck")
    sphere(22, (0, 18, zc - 8), SAND(), "A_ball")
    return dict(center=(0, 0, zc))


# ---------------------------------------------------------------- B: HOP
def build_B():
    W, D, H = 56, 40, 64
    zc = 8 + 14 + H / 2
    body = box((W, D, H), (0, 0, zc), r=5, m=WHITE(), name="B_body", seg=5)
    yf = -D / 2
    bez = box((W - 6, 3.0, H - 8), (0, yf - 0.9, zc), r=3.5, m=BLACK(), name="B_bezel", seg=4)
    cyl(26, 1.6, (0, yf - 2.6, zc + 8), "y", mat("Kinh3", "#2B3033", 0.2), name="B_ring")
    cyl(12, 1.2, (0, yf - 3.4, zc + 8), "y", GLASS(), name="B_glass")
    cyl(3.6, 0.3, (-2.3, yf - 4.1, zc + 10.3), "y", mat("Phanxa", "#3C4A63", 0.1), name="glint", verts=20)
    leds(-3.5, zc - 14, yf - 2.4)
    text_cut(bez, "STLAB", 4.4, (0, yf - 2.4, zc - 22))
    slots(body, 7, 5.0, 2.0, 20, 0, 4, zc + H / 2 - 1, 8)
    slots(body, 7, 5.0, 2.0, 20, 0, 4, zc - H / 2 + 1, 8)
    cut(body, box((13, 8, 8), (0, D / 2 - 2, zc - H / 2 + 5), r=1.5, name="usb"))
    base = box((72, 48, 7), (0, 4, 3.5), r=2.5, m=PINE(), name="B_base", seg=4)
    for sx in (-1, 1):
        box((7, 30, 56), (sx * (W / 2 + 4.0), 8, 7 + 28), r=3, m=PINE(), name="B_arm", seg=4)
        cyl(10, 2.0, (sx * (W / 2 + 8.2), 8, zc), "x", BLACK(), r=0.6, name="B_pivot")
    for sx in (-1, 1):
        cut(base, cyl(4.2, 10, (sx * 29, 16, 4), "z", name="kh", verts=24))
    return dict(center=(0, 0, zc))


# ---------------------------------------------------------------- C: MAT
def build_C():
    R = 29.0
    zc = 12 + R + 3
    ball = sphere(2 * R, (0, 0, zc), WHITE(), "C_ball")
    ya = 20.5
    common(ball, box((100, 2 * ya, 100), (0, 0, zc), name="slab"))
    for p in ball.data.polygons:
        p.use_smooth = True
    yf = -ya
    cyl(40, 1.6, (0, yf - 0.6, zc), "y", PINE(), r=0.6, name="C_iris")
    cyl(22, 1.4, (0, yf - 1.6, zc), "y", BLACK(), r=0.5, name="C_pupilring")
    cyl(11, 1.0, (0, yf - 2.3, zc), "y", GLASS(), name="C_glass")
    cyl(3.5, 0.3, (-2.2, yf - 2.9, zc + 2.2), "y", mat("Phanxa", "#3C4A63", 0.1), name="glint", verts=16)
    leds(-3.5, zc - 14.5, yf - 1.4)
    slots(ball, 5, 5.0, 2.0, 16, 0, 4, zc + R - 2, 7)
    slots(ball, 5, 5.0, 2.0, 16, 0, 4, zc - R + 2, 7)
    cut(ball, box((13, 8, 8), (0, ya - 3, zc - R + 6), r=1.5, name="usb"))
    base = cyl(72, 8, (0, 0, 4), "z", BLACK(), r=2.5, name="C_base")
    ring = cyl(52, 12, (0, 0, 14), "z", BLACK(), r=2, name="C_cradle")
    cut(ring, sphere(2 * R + 0.6, (0, 0, zc), name="seat"))
    text_cut(base, "STLAB", 5.5, (0, -36, 4))
    return dict(center=(0, 0, zc))



def make_ring(col, x=0, flip=False):
    """De tron (vanh) D86 x 10: loi lom D77 sau 4, chot giua D8, 3 tai ma sat, 2 lo khoa + vung dan 3M o day."""
    ring = cyl(86, 10, (x, 0, 5), "z", col, r=2.0, name="D_ring")
    cut(ring, cyl(77, 4.2, (x, 0, 10 - 2 + 0.1), "z", name="recess"))
    cut(ring, cyl(50, 0.6, (x, 0, 0.3), "z", name="tape"))
    for sx in (-1, 1):
        cut(ring, cyl(4.2, 12, (x + sx * 29, 0, 4), "z", name="kh", verts=24))
        cut(ring, box((8.5, 3.0, 1.2), (x + sx * 29, 7, 0.6), r=1.0, name="khslot"))
    cyl(8, 5.7, (x, 0, 5.8 + 2.85), "z", col, name="D_pin", verts=32)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        box((10, 3, 1.4), (x + 31 * math.cos(a), 31 * math.sin(a), 6.7), r=0.6, m=col, name="D_tab", seg=2).rotation_euler = (0, 0, a + math.pi / 2)
    if flip:
        for ob in [o for o in bpy.data.objects if o.name.startswith(("D_ring", "D_pin", "D_tab"))]:
            pass
    return ring


def build_D(color="pine", tilt=0.0, pan=0.0, explode=0.0, flipring=False):
    col = PINE() if color == "pine" else BLACK()
    W, D, H = 56, 40, 64
    zc = 64
    make_ring(col)
    before = set(bpy.data.objects)
    disc = cyl(76, 6, (0, 0, 10 - 4 + 3 + explode), "z", col, r=1.2, name="D_disc")
    cut(disc, cyl(8.8, 8, (0, 0, 9 + explode), "z", name="pinhole", verts=32))
    yoke = [disc]
    for sx in (-1, 1):
        yoke.append(box((7, 36, 70), (sx * (W / 2 + 0.6 + 3.5), 0, 12 + 35 + explode), r=3, m=col, name="D_arm", seg=4))
    yoke_set = set(bpy.data.objects) - before
    before2 = set(bpy.data.objects)
    zc2 = zc + explode
    body = box((W, D, H), (0, 0, zc2), r=5, m=WHITE(), name="D_body", seg=5)
    yf = -D / 2
    bez = box((W - 6, 3.0, H - 8), (0, yf - 0.9, zc2), r=3.5, m=BLACK(), name="D_bezel", seg=4)
    cyl(26, 1.6, (0, yf - 2.6, zc2 + 8), "y", mat("Kinh3", "#2B3033", 0.2), name="D_lring")
    cyl(12, 1.2, (0, yf - 3.4, zc2 + 8), "y", GLASS(), name="D_glass")
    cyl(3.6, 0.3, (-2.3, yf - 4.1, zc2 + 10.3), "y", mat("Phanxa", "#3C4A63", 0.1), name="glint", verts=20)
    leds(-3.5, zc2 - 14, yf - 2.4)
    text_cut(bez, "STLAB", 4.4, (0, yf - 2.4, zc2 - 22))
    slots(body, 7, 5.0, 2.0, 20, 0, 0, zc2 + H / 2 - 1, 8)
    slots(body, 7, 5.0, 2.0, 20, 0, 0, zc2 - H / 2 + 1, 8)
    cut(body, box((13, 8, 8), (0, D / 2 - 2, zc2 - H / 2 + 5), r=1.5, name="usb"))
    for sx in (-1, 1):
        xo = sx * (W / 2 + 0.6 + 7)
        cyl(8.5, 0.8, (xo + sx * 0.4, 0, zc2), "x", mat("Vong", "#8A9490", 0.3), name="D_washer", verts=40)
        hd = cyl(5.6, 2.0, (xo + sx * 1.8, 0, zc2), "x", mat("VitM3", "#2A2D2F", 0.35), r=0.6, name="D_m3head", verts=40)
        cut(hd, box((0.9, 4.4, 1.0), (xo + sx * 2.7, 0, zc2), name="slotv"))
        cut(hd, box((0.9, 1.0, 4.4), (xo + sx * 2.7, 0, zc2), name="slotv2"))
    head = set(bpy.data.objects) - before2
    # nghieng quanh truc X tai tam chot; xoay pan quanh Z
    bpy.context.view_layer.update()
    if tilt:
        em = bpy.data.objects.new("tilt", None); bpy.context.scene.collection.objects.link(em)
        em.location = (0, 0, zc2 * S)
        bpy.context.view_layer.update()
        for o in head:
            o.parent = em; o.matrix_parent_inverse = em.matrix_world.inverted()
        em.rotation_euler = (math.radians(tilt), 0, 0)
    if pan:
        ep = bpy.data.objects.new("pan", None); bpy.context.scene.collection.objects.link(ep)
        bpy.context.view_layer.update()
        movers = [o for o in (yoke_set | head) if o.parent is None] + [o for o in bpy.data.objects if o.name == "tilt"]
        for o in movers:
            o.parent = ep; o.matrix_parent_inverse = ep.matrix_world.inverted()
        ep.rotation_euler = (0, 0, math.radians(pan))
    return dict(center=(0, 0, zc2))


def shoot_set(key, tag, fn, extra=()):
    clear()
    sc = setup_scene()
    info = fn()
    cz = info["center"][2] * S
    k = 1.3 if key == "D" else 1.0
    tgt = (0, 0, cz * (0.72 if key == "D" else 0.9))
    shoot(sc, f"{key}-{tag}-truoc.png", tgt, (-0.19 * k, -0.30 * k, cz + 0.07), lens=75)
    set_lights(True)
    shoot(sc, f"{key}-{tag}-sau.png", tgt, (0.17 * k, 0.24 * k, cz + 0.10), lens=75)
    set_lights(False)
    outlet(-120, 10)
    shoot(sc, f"{key}-{tag}-tile.png", (-0.050, 0.0, 0.045 if key == "D" else 0.035), (-0.09, -0.46 if key == "D" else -0.40, 0.19), lens=50)


def run_D():
    shoot_set("D", "ghep", lambda: build_D("pine"))
    for name, kw, cam in (("conhieu", dict(color="pine", tilt=-24, pan=35), None),
                          ("no", dict(color="pine", explode=34), "no")):
        clear()
        sc = setup_scene()
        info = build_D(**kw)
        cz = info["center"][2] * S
        if cam == "no":
            b0 = set(bpy.data.objects)
            make_ring(PINE(), x=118)  # day de lat de thay lo treo + vung 3M
            new = set(bpy.data.objects) - b0
            em = bpy.data.objects.new("flip", None); bpy.context.scene.collection.objects.link(em)
            em.location = (118 * S, 0, 5 * S)
            for o in new:
                o.parent = em; o.matrix_parent_inverse = em.matrix_world.inverted()
            em.rotation_euler = (math.pi, 0, 0)
            em.location.z = 5 * S
            sc_cam = ((-0.34, -0.55, 0.24), (0.05, 0.0, 0.06), 55)
            shoot(sc, f"D-ghep-{name}.png", sc_cam[1], sc_cam[0], lens=sc_cam[2])
        else:
            shoot(sc, f"D-ghep-{name}.png", (0, 0, cz * 0.72), (-0.25, -0.39, cz + 0.07), lens=75)
    print("D OK")


def outlet(x, y):
    p = box((86, 86, 9), (x, y, 4.5), r=5, m=WALLPLATE(), name="outlet", seg=5)
    cyl(66, 0.5, (x, y, 9.1), "z", mat("Oca2", "#E7EAE8", 0.4), name="rec", verts=64)
    for dx in (-12, 12):
        cyl(7.0, 1.0, (x + dx, y, 9.3), "z", HOLE(), name="pin", verts=24)
    for dy in (-33, 33):
        cyl(3.4, 0.8, (x, y + dy, 9.2), "z", mat("Vit", "#BDC3C0", 0.3), name="screw", verts=20)
    return p



# ---------------------------------------------------------------- W: TREO TUONG (dung chung hop + khung U + dia + vanh voi D)
DZ = 85  # do cao mat sau cua tam tuong len khoi chan (mm)


def group_under(objs, loc):
    em = bpy.data.objects.new("grp", None)
    bpy.context.scene.collection.objects.link(em)
    em.location = (loc[0] * S, loc[1] * S, loc[2] * S)
    bpy.context.view_layer.update()
    for o in objs:
        o.parent = em
    return em


def build_W(tilt=0.0, pan=0.0, explode=0.0, ring_lift=0.0, cable=True):
    blk = BLACK()
    # mang tuong + o dien
    wall = box((760, 30, 380), (-80, 15, 190), r=0, m=mat("Tuong", "#C9C3B6", 0.9), name="wall")
    b0 = set(bpy.data.objects)
    outlet(0, 0)
    ob = [o for o in set(bpy.data.objects) - b0 if o.parent is None]
    group_under(ob, (-150, 0, 150)).rotation_euler = (math.pi / 2, 0, 0)
    # gia treo W
    box((70, 6, 130), (0, -3, DZ + 65), r=2.5, m=blk, name="W_plate", seg=4)
    for z in (12, 118):
        cyl(8.6, 1.0, (0, -6.4, DZ + z), "y", mat("DauVit", "#8A9490", 0.3), name="W_screw", verts=32)
        box((6.0, 0.4, 1.0), (0, -7.0, DZ + z), name="W_slot")
    box((40, 70, 5.6), (0, -35, DZ + 22.8), r=1.5, m=blk, name="W_arm", seg=3)
    cyl(90, 6, (0, -70, DZ + 23), "z", blk, r=1.2, name="W_pad")
    rib = box((6, 38, 6), (0, -19.5, DZ + 11), r=1.0, m=blk, name="W_rib", seg=2)
    rib.rotation_euler = (math.radians(-29), 0, 0)
    for y in (-14, -44):
        box((12, 8, 4.5), (0, y, DZ + 28.2), r=1.0, m=PINE(), name="W_clip", seg=2)
    # hop + khung U + dia + vanh (cung part voi D)
    b = set(bpy.data.objects)
    build_D("pine", tilt, pan, explode)
    new = [o for o in set(bpy.data.objects) - b if o.parent is None]
    rg = [o for o in new if o.name.startswith(("D_ring", "D_pin", "D_tab"))]
    group_under([o for o in new if o not in rg], (0, -70, DZ + 26))
    group_under(rg, (0, -70, DZ + 26 + ring_lift))
    # day USB: tu cong USB sau-duoi, qua mep vanh, doc tay do, xuong tuong
    if cable and not explode:
        pts = [(-52, 62), (-55, 50), (-36, 44), (-26, 36), (-16, 30.2), (-3, 30.2), (-9, 26), (-9, 8)]
        cu = bpy.data.curves.new("cable", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 1.7 * S; cu.bevel_resolution = 4
        sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(pts) - 1)
        for p, (y, z) in zip(sp.bezier_points, pts):
            p.co = (0, y * S, (DZ + z) * S); p.handle_left_type = p.handle_right_type = "AUTO"
        co = bpy.data.objects.new("cable", cu); bpy.context.scene.collection.objects.link(co)
        co.data.materials.append(mat("Day", "#1B1E1F", 0.4))
    return dict(center=(0, -0.07, 0.19))


def w_lights():
    for name, loc, pw, sz in LIGHTS:
        l = bpy.data.objects[name]
        x, y, z = loc
        l.location = (x * 1.3, y * 1.5, z + 0.2)
        l.data.energy = pw * 1.5
        l.data.size = sz * 2
        l.rotation_euler = (Vector((0, -0.05, 0.19)) - l.location).to_track_quat("-Z", "Y").to_euler()


def run_W():
    T = (0, -0.05, 0.17)
    for name, kw, cam, lens in (
            ("truoc", dict(), (-0.24, -0.50, 0.25), 62),
            ("ben", dict(pan=0), (0.70, -0.06, 0.18), 70),
            ("tuong", dict(), (-0.10, -0.95, 0.30), 55),
            ("no", dict(explode=44, ring_lift=22), (-0.36, -0.62, 0.34), 60)):
        clear()
        sc = setup_scene()
        w_lights()
        build_W(**kw)
        tgt = T if name != "tuong" else (-0.06, -0.02, 0.20)
        if name == "no":
            tgt = (0, -0.07, 0.22)
        shoot(sc, f"W-treo-{name}.png", tgt, cam, lens=lens)
    print("W OK")


if "W" in ONLY:
    run_W()
if "D" in ONLY:
    run_D()
for key, fn, tag in (("A", build_A, "soi"), ("B", build_B, "hop"), ("C", build_C, "mat")):
    if key not in ONLY:
        continue
    clear()
    sc = setup_scene()
    info = fn()
    cz = info["center"][2] * S
    k = 1.3 if key == "D" else 1.0
    tgt = (0, 0, cz * (0.72 if key == "D" else 0.9))
    shoot(sc, f"{key}-{tag}-truoc.png", tgt, (-0.19 * k, -0.30 * k, cz + 0.07), lens=75)
    set_lights(True)
    shoot(sc, f"{key}-{tag}-sau.png", tgt, (0.17 * k, 0.24 * k, cz + 0.10), lens=75)
    set_lights(False)
    outlet(-120, 10)
    shoot(sc, f"{key}-{tag}-tile.png", (-0.050, 0.0, 0.045 if key == "D" else 0.035), (-0.09, -0.46 if key == "D" else -0.40, 0.19), lens=50)
print("CONCEPTS OK")
