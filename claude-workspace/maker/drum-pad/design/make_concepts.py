"""Buoc 0 – Giao dien drum-pad: 3 dang hop trong 4 pad (Blender bpy) + cmf.png + contact-sheet.png.

  A  Phim trong  – 4 pad so le 1 hang ngang, bang loa + 6 nut doc phia sau
  B  Vong quanh loa – 4 pad o 4 goc, loa o giua, 6 nut 2 ben loa (khuyen nghi)
  C  Rua trong   – nhan vat rua, 4 pad tren mai, loa = mom/dau

Chay (tu claude-workspace):
  python tools/print/scripts/memjob.py 3 -- python maker/drum-pad/design/make_concepts.py
Chi mot buoc:  ... make_concepts.py --only render | sheet     (render: Blender nen; sheet: PIL)
Quy uoc: mm (1 BU = 1 mm), mat truoc = -Y, san z=0.
Cac so ben trong (loa O52x26, bo 82x73, piezo, khe, lo vit) chi la HINH MINH HOA – TODO buoc 1, KHONG phai thong so chot.
"""
from pathlib import Path
import json
import math
import subprocess
import sys

HERE = Path(__file__).resolve().parent
OUT = HERE / "concepts"
FONTS = HERE.parents[2] / "studio" / "design" / "fonts"
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
SIZE = (1200, 800)
try:
    import bpy
    import bmesh
    from mathutils import Vector, Matrix
    from mathutils.bvhtree import BVHTree
    import numpy as np
except ImportError:
    bpy = None

# Mau (xap xi sRGB de render). Ten mau hang Bambu PETG Basic: TODO xac nhan khi chon cuoc.
PINE, WHITE, LGREEN, YELLOW = "#1E5A45", "#F2F2EE", "#3FAE6B", "#E8B33A"
TPU = "#2A2E33"
SKIN = "#E9B79A"
BG = "#ECF1EF"
TOP_C, TOP_ORTHO = (-80, -25), 520
LEDS = ["#FF5A4F", "#FFC83A", "#46D68C", "#4FA8FF"]  # kick, snare, hi-hat, tom

# =============================================================== BLENDER ==
if bpy:
    MC = {}
    ALL = []

    def lin(h):
        v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in v)

    def mat(h, rough=.42, emit=0.0):
        key = (h, rough, emit)
        if key in MC:
            return MC[key]
        m = bpy.data.materials.new(h)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*lin(h), 1)
        b.inputs["Roughness"].default_value = rough
        if emit:
            b.inputs["Emission Color"].default_value = (*lin(h), 1)
            b.inputs["Emission Strength"].default_value = emit
        MC[key] = m
        return m

    def link(name, bm, m, loc=(0, 0, 0), rot=None, sharp=40, smooth=True):
        for f in bm.faces:
            f.smooth = smooth
        if smooth:
            for e in bm.edges:
                if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(sharp):
                    e.smooth = False
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        if m:
            me.materials.append(m)
        ob.location = loc
        if rot is not None:
            if hasattr(rot, "to_euler"):
                ob.rotation_mode = "QUATERNION"
                ob.rotation_quaternion = rot
            else:
                ob.rotation_euler = rot
        return ob

    def box(name, size, loc, m, r=0.0, seg=3):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= size[0]; v.co.y *= size[1]; v.co.z *= size[2]
        if r > 0:
            bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=seg, affect="EDGES")
        return link(name, bm, m, loc)

    def cyl(name, r, h, loc, m, axis="z", rb=0.0, seg=48, r2=None):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
        if rb > 0:
            rim = [e for e in bm.edges if abs(abs(e.verts[0].co.z) - h / 2) < 1e-4 and abs(abs(e.verts[1].co.z) - h / 2) < 1e-4]
            bmesh.ops.bevel(bm, geom=rim, offset=rb, segments=3, affect="EDGES")
        rot = {"z": (0, 0, 0), "x": (0, math.pi / 2, 0), "y": (math.pi / 2, 0, 0)}[axis]
        return link(name, bm, m, loc, rot)

    def sp(a, e):
        return np.sign(a) * np.abs(a) ** e

    def superq(name, rx, ry, rz, e1, e2, c, z0, taper, m, nu=96, nv=56):
        ztop = c[2] + rz
        vs, faces = [(c[0], c[1], max(c[2] - rz, z0))], []
        for j in range(1, nv):
            v = -math.pi / 2 + math.pi * j / nv
            for i in range(nu):
                u = 2 * math.pi * i / nu
                cv = sp(math.cos(v), e1)
                x, y, z = rx * cv * sp(math.cos(u), e2), ry * cv * sp(math.sin(u), e2), c[2] + rz * sp(math.sin(v), e1)
                t = min(max((z - z0) / (ztop - z0), 0), 1)
                s = 1 - taper * t ** 1.3
                vs.append((c[0] + x * s, c[1] + y * s, max(z, z0)))
        vs.append((c[0], c[1], ztop))
        top = len(vs) - 1
        for i in range(nu):
            faces.append((0, 1 + (i + 1) % nu, 1 + i))
        for j in range(nv - 2):
            a, b = 1 + j * nu, 1 + (j + 1) * nu
            for i in range(nu):
                k = (i + 1) % nu
                faces.append((a + i, a + k, b + k, b + i))
        a = 1 + (nv - 2) * nu
        for i in range(nu):
            faces.append((a + i, a + (i + 1) % nu, top))
        bm = bmesh.new()
        bv = [bm.verts.new(p) for p in vs]
        for f in faces:
            try:
                bm.faces.new([bv[i] for i in f])
            except ValueError:
                pass
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bvh = BVHTree.FromPolygons(vs, faces)
        return link(name, bm, m, sharp=70), bvh

    def rrect_pts(w, h, r, n=10):
        pts = []
        for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                           (w / 2 - r, -h / 2 + r, 270)):
            for k in range(n + 1):
                a = math.radians(a0 + 90 * k / n)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts

    def slab(name, w, d, rp, h, rt, m, z0=0.0, rb=0.8):
        """Khoi bo goc mat bang rp, bo canh tren rt, vat canh day rb (0,6-1 mm: in tren ban khong support)."""
        bm = bmesh.new()
        f = bm.faces.new([bm.verts.new((x, y, 0)) for x, y in rrect_pts(w, d, rp)])
        res = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, verts=[g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)], vec=(0, 0, h))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        if rt > 0:
            te = [e for e in bm.edges if all(abs(v.co.z - h) < 1e-4 for v in e.verts)]
            bmesh.ops.bevel(bm, geom=te, offset=rt, segments=5, affect="EDGES")
        if rb > 0:
            be = [e for e in bm.edges if all(abs(v.co.z) < 1e-4 for v in e.verts)]
            bmesh.ops.bevel(bm, geom=be, offset=rb, segments=1, affect="EDGES")
        return link(name, bm, m, (0, 0, z0), sharp=35)

    def wedge(name, pts_yz, x0, x1, m, rb=3):
        bm = bmesh.new()
        f = bm.faces.new([bm.verts.new((x0, y, z)) for y, z in pts_yz])
        res = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, verts=[g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)], vec=(x1 - x0, 0, 0))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=rb, segments=3, affect="EDGES")
        return link(name, bm, m, sharp=35)

    def oriented(ob, n):
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = Vector(n).normalized().to_track_quat("Z", "Y")
        return ob

    def disc(name, r, h, p, n, m, emb=0.35, seg=48, rb=0.0):
        n = Vector(n).normalized()
        ob = cyl(name, r, h, tuple(Vector(p) + n * (h / 2 - emb * h)), m, rb=rb, seg=seg)
        return oriented(ob, n)

    def torus(name, R, r, loc, m):
        bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=72, minor_segments=8, location=loc)
        ob = bpy.context.active_object
        ob.name = name
        ob.data.materials.append(m)
        bpy.ops.object.shade_smooth()
        return ob

    def text(s, size, loc, m, font, rot=(0, 0, 0), ext=0.8):
        cu = bpy.data.curves.new("t", "FONT")
        cu.body, cu.font, cu.size, cu.extrude = s, font, size, ext / 2
        cu.align_x = cu.align_y = "CENTER"
        ob = bpy.data.objects.new("chu", cu)
        bpy.context.scene.collection.objects.link(ob)
        cu.materials.append(m)
        ob.location, ob.rotation_euler = loc, rot
        return ob

    def grille(name, c, n, r=26):
        """Luoi loa O52 (hinh minh hoa): dia den + cham luc giac."""
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=r, radius2=r, depth=2.4)
        pitch = 5.0
        for i in range(-6, 7):
            for j in range(-6, 7):
                x, y = (i + .5 * (j % 2)) * pitch, j * pitch * .866
                if math.hypot(x, y) < r - 3.5:
                    g = bmesh.new()
                    bmesh.ops.create_cone(g, cap_ends=True, segments=10, radius1=1.5, radius2=1.5, depth=1.0)
                    for v in g.verts:
                        bm.verts.new((v.co.x + x, v.co.y + y, v.co.z + 1.15))
                    g.free()
        # cham: tao lai bang cone rieng (don gian, tranh noi dinh thu cong)
        bm.free()
        ob = cyl(name, r, 2.6, (0, 0, 0), mat("#15181B", .6))
        for i in range(-6, 7):
            for j in range(-6, 7):
                x, y = (i + .5 * (j % 2)) * 5.0, j * 5.0 * .866
                if math.hypot(x, y) < r - 4:
                    d = cyl("cham", 1.35, .5, (x, y, 1.35), mat("#5B646B", .5), seg=8)
                    d.parent = ob
                    d.location = (x, y, 1.3)
        nn = Vector(n).normalized()
        ob.location = Vector(c) + nn * (1.3 - .35 * 2.6)
        return oriented(ob, nn)

    # ---------------------------------------------------------------- canh
    def reset():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        MC.clear()
        sc = bpy.context.scene
        ids = {i.identifier for i in sc.render.bl_rna.properties["engine"].enum_items}
        sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in ids else "BLENDER_EEVEE_NEXT"
        sc.render.resolution_x, sc.render.resolution_y = SIZE
        sc.render.image_settings.file_format = "PNG"
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.exposure = -0.95
        w = bpy.data.worlds.new("w")
        w.use_nodes = True
        w.node_tree.nodes["Background"].inputs[0].default_value = (*lin(BG), 1)
        w.node_tree.nodes["Background"].inputs[1].default_value = 1.45
        sc.world = w
        for nm, d, en, ang in (("key", (-.5, .7, -1), 3.6, .12), ("fill", (1, .35, -.5), 1.1, .9),
                               ("rim", (.6, -.8, -.7), 2.2, .3)):
            ld = bpy.data.lights.new(nm, "SUN")
            ld.energy, ld.angle = en, ang
            ob = bpy.data.objects.new(nm, ld)
            sc.collection.objects.link(ob)
            ob.rotation_mode = "QUATERNION"
            ob.rotation_quaternion = Vector(d).to_track_quat("-Z", "Y")
        return sc

    def floor():
        box("ban", (3000, 3000, 2), (0, 0, -1.4), mat("#D3DCD8", .9))

    HAND_LEN = 140.0

    def hand(tip_x=-166, yc=-12):
        """Ban tay tre ~140 mm nam tren ban, ngon huong +X (ve phia hop) - khoi tham chieu ti le."""
        m = mat(SKIN, .6)
        objs = []
        objs.append(superq("ban-tay-long", 31, 30, 8, .7, .8, (182, 0, 8), 0, 0, m, nu=48, nv=24)[0])
        objs.append(superq("ban-tay-co", 24, 25, 7, .8, .9, (218, 0, 7), 0, 0, m, nu=48, nv=24)[0])
        for y, L in ((21, 52), (7, 58), (-7, 54), (-21, 44)):
            objs.append(superq("ngon", L / 2, 6.2, 5.6, 1, 1, (156 - L / 2, y, 5.6), 0, 0, m, nu=32, nv=16)[0])
        th, _ = superq("ngon-cai", 21, 6.8, 6.2, 1, 1, (0, 0, 6.2), 0, 0, m, nu=32, nv=16)
        th.location = (176, 34, 0)
        th.rotation_euler = (0, 0, math.radians(-26))
        objs.append(th)
        bpy.context.view_layer.update()
        xs = [(o.matrix_world @ Vector(c)).x for o in objs for c in o.bound_box]
        x0, x1 = min(xs), max(xs)
        s = HAND_LEN / (x1 - x0)
        M = (Matrix.Translation((tip_x, yc, 0)) @ Matrix.Rotation(math.pi, 4, "Z") @ Matrix.Scale(s, 4)
             @ Matrix.Translation((-x0, 0, 0)))
        for o in objs:
            o.matrix_world = M @ o.matrix_world

    PRE = set()

    def collect():
        ALL[:] = [o for o in bpy.data.objects if o.name not in PRE and o.type in ("MESH", "CURVE", "FONT")]

    def pad(x, y, zd, led):
        """Mat pad mem (TPU/EVA) O71, vong LED quanh chan pad (khuech tan), dia day toi."""
        cyl("pad-de", 39.4, 1.4, (x, y, zd + .5), mat("#17191C", .7), seg=64)
        torus("led", 37.4, 1.15, (x, y, zd + 1.5), mat(led, .3, emit=5.0))
        cyl("pad", 35.5, 9, (x, y, zd + 1.7), mat(TPU, .85), rb=2.6, seg=64)
        torus("pad-van", 22, .8, (x, y, zd + 6.2), mat("#3B4046", .8))

    def port_side(x, y_usb, y_jack, z):
        """Cong USB (khe det) + tai nghe 3,5 mm tren canh +X."""
        box("usb", (1.6, 10.5, 4.4), (x, y_usb, z), mat("#0E1012", .5), r=1.0)
        cyl("tai-nghe", 4.0, 1.6, (x, y_jack, z), mat("#0E1012", .5), axis="x", seg=32)

    # ----------------------------------------------------------- 3 dang
    def concept_a(font):
        g, w, blk = mat(PINE, .4), mat(WHITE, .42), mat("#1B1D20", .5)
        slab("than", 300, 200, 26, 40, 8, g)
        wedge("bang-loa", [(34, 40), (74, 80), (92, 80), (92, 30), (34, 30)], -142, 142, w, rb=3.5)
        n = (0, -1, 1)
        grille("loa", (0, 54, 60), n)
        for s in (-1, 1):
            for x in (70, 92, 114):
                disc("nut", 7.5, 6.5, (s * x, 54, 60), n, g, emb=.3, rb=1.2)
        for i, (x, y) in enumerate(((-102, -52), (-34, -8), (34, -52), (102, -8))):
            pad(x, y, 40, LEDS[i])
        text("STLAB", 8, (-8, 83, 80.2), g, font)
        box("dau-vang", (12, 3.2, .9), (22, 83, 80.3), mat(YELLOW, .4), r=.3)
        port_side(150, -20, 12, 22)

    def concept_b(font):
        g, w = mat(PINE, .4), mat(WHITE, .42)
        slab("chan", 232, 220, 70, 10, 0, g, rb=.8)
        slab("than", 230, 218, 69, 50, 8, w, z0=10, rb=0)
        for i, (x, y) in enumerate(((-60, -56), (60, -56), (-60, 56), (60, 56))):
            pad(x, y, 60, LEDS[i])
        cyl("loa-vong", 33, 3.0, (0, 0, 60.8), g, rb=1.0, seg=72)
        grille("loa", (0, 0, 62), (0, 0, 1))
        for s in (-1, 1):
            for x in (46, 66, 86):
                cyl("nut", 7.5, 6.5, (s * x, 0, 62.2), g, rb=1.2)
        text("STLAB", 9, (-6, -102, 60.2), g, font)
        box("dau-vang", (12, 3.2, .9), (21, -102, 60.3), mat(YELLOW, .4), r=.3)
        port_side(115, -16, 14, 28)

    def concept_c(font):
        g, lg, w = mat(PINE, .4), mat(LGREEN, .42), mat(WHITE, .42)
        for sx in (-1, 1):
            for sy in (-1, 1):
                cyl("chan", 15, 16, (sx * 96, sy * 58, 8), lg, rb=2.5)
        slab("vien", 252, 176, 56, 14, 3, w, z0=12, rb=.8)
        slab("mai", 244, 168, 52, 32, 8, g, z0=26, rb=0)
        for i, (x, y) in enumerate(((-62, -40), (62, -40), (-62, 40), (62, 40))):
            pad(x, y, 58, LEDS[i])
        for x in (-11, 11):
            for y in (-24, 0, 24):
                cyl("nut", 6.5, 6.0, (x, y, 60), w, rb=1.2)
        text("STLAB", 8, (-4, 62, 58.2), w, font)
        box("dau-vang", (11, 3.0, .9), (15, 62, 58.3), mat(YELLOW, .4), r=.3)
        head, bvh = superq("dau", 34, 28, 26, .6, .7, (0, -98, 32), 12, 0, lg, nu=96, nv=48)
        r = bvh.ray_cast(Vector((0, -400, 30)), Vector((0, 1, 0)))
        grille("loa", r[0], r[1] * -1 if False else (0, -1, 0), r=26)
        for s in (-1, 1):
            r = bvh.ray_cast(Vector((s * 15, -98, 200)), Vector((0, 0, -1)))
            disc("mat-vong", 6.5, 3, r[0], r[1], w, emb=.5, seg=40)
            disc("mat-den", 3.6, 3.6, r[0] + Vector(r[1]) * .8, r[1], mat("#15181B", .5), emb=.5, seg=32)
        t = cyl("duoi", 2, 12, (0, 88, 22), lg, axis="y", seg=32, r2=9)
        port_side(122, -14, 12, 42)

    BUILD = {"a": concept_a, "b": concept_b, "c": concept_c}

    def camera(loc, rot=None, target=None, ortho=None, lens=50):
        cd = bpy.data.cameras.new("cam")
        cd.clip_start, cd.clip_end = 1, 6000
        if ortho:
            cd.type, cd.ortho_scale = "ORTHO", ortho
        else:
            cd.lens = lens
        ob = bpy.data.objects.new("cam", cd)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = loc
        if target is not None:
            ob.rotation_mode = "QUATERNION"
            ob.rotation_quaternion = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y")
        else:
            ob.rotation_euler = rot
        bpy.context.scene.camera = ob

    # tam anh nhin tren xuong (khop _annotate)

    def shot(path, view, samples=48):
        sc = bpy.context.scene
        eevee = getattr(sc, "eevee", None)
        if eevee is not None and hasattr(eevee, "taa_render_samples"):
            eevee.taa_render_samples = samples
        for o in [o for o in bpy.data.objects if o.type == "CAMERA"]:
            bpy.data.objects.remove(o)
        if view == "dinh":
            camera((TOP_C[0], TOP_C[1], 1000), rot=(0, 0, 0), ortho=TOP_ORTHO)
        else:
            camera((230, -400, 270), target=(-55, -10, 18), lens=42)
        sc.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)

    def scene(k):
        reset()
        floor()
        font = bpy.data.fonts.load(str(FONTS / "BeVietnamPro-Bold.ttf"))
        hand()
        PRE.clear()
        PRE.update(o.name for o in bpy.data.objects)
        BUILD[k](font)
        collect()

    def bbox():
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in ALL for c in o.bound_box]
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        return lo, hi

    def render_concept(k):
        scene(k)
        lo, hi = bbox()
        dims = {"dai": hi[0] - lo[0], "rong": hi[1] - lo[1], "cao": hi[2], "x0": lo[0], "x1": hi[0], "y0": lo[1], "y1": hi[1]}
        print("DIMS", k, json.dumps({a: round(b, 1) for a, b in dims.items()}))
        for v in ("3-4", "dinh"):
            shot(OUT / f"concept-{k}-{v}.png", v)
        return dims


# ------------------------------------------------------------------ PIL ----
INK, PINEH, MIST = "#16231D", "#1E5A45", "#ECF1EF"
NOTE = {
    "a": "A – Phím trống (4 pad so le, bảng loa dốc phía sau)",
    "b": "B – Vòng quanh loa (loa ở giữa, 4 pad ở 4 góc)",
    "c": "C – Rùa trống (4 pad trên mai, loa là cái mõm)",
}
# (de go, de in tren ban 256x256, ti le loa, tre lop 2-5 thich) 0..3
SCORE = {"a": (3, 1, 1, 2), "b": (3, 3, 3, 2), "c": (2, 2, 2, 3)}
CRIT = ("Dễ gõ", "Dễ in (bàn 256)", "Tỉ lệ loa", "Trẻ 2–5 thích")
PROS = {
    "a": ("Quen như đàn phím, 2 tay gõ tự nhiên; khối thấp, in không support.",
          "Dài 300 mm > bàn in 256 nên phải cắt 2 nửa; loa nhỏ nằm nghiêng trên bảng sau; 3 bé khó ngồi chung."),
    "b": ("Vừa 1 bàn in (232 × 220); 2–3 bé ngồi quanh; loa trung tâm cân đối, góc tròn an toàn.",
          "Hơi trung tính, ít 'nhân vật'; sát lề bàn in 256 (TODO brim); pad sau với xa bé ngồi trước."),
    "c": ("Dễ thương, gợi nhớ Cú con/mascot; mõm = loa Ø52; nhớ 4 pad theo màu LED.",
          "Nhiều part (mai, viền, đầu, 4 chân, đuôi); 4 pad sát nhau (rãnh 3 mm) dễ gõ nhầm; dài 220 mm gồm đầu."),
}
CMF = {
    "a": [("Thân + núm nút", "Xanh thông", "Green (Bambu PETG Basic – TODO tên màu hãng)", PINE),
          ("Bảng loa dốc phía sau", "Trắng", "White", WHITE),
          ("Mặt pad mềm (đen)", "TPU / EVA đen", "TODO chọn vật liệu + độ cứng", TPU),
          ("Nhãn STLAB (điểm nhấn, 0,8 mm)", "Vàng", "Yellow", YELLOW)],
    "b": [("Chân (viền đáy) + vòng loa + núm nút", "Xanh thông", "Green (TODO tên màu hãng)", PINE),
          ("Thân trên", "Trắng", "White", WHITE),
          ("Mặt pad mềm (đen)", "TPU / EVA đen", "TODO chọn vật liệu + độ cứng", TPU),
          ("Nhãn STLAB (điểm nhấn, 0,8 mm)", "Vàng", "Yellow", YELLOW)],
    "c": [("Mai rùa", "Xanh thông", "Green (TODO tên màu hãng)", PINE),
          ("Đầu, 4 chân, đuôi", "Xanh lá nhạt", "Light green / Bright Green (TODO)", LGREEN),
          ("Viền mai + núm nút + mắt", "Trắng", "White", WHITE),
          ("Mặt pad mềm (đen)", "TPU / EVA đen", "TODO chọn vật liệu + độ cứng", TPU)],
}
GENERIC = ("Mỗi part đơn sắc rồi ráp lại (hạn chế AMS); mặt đáy in trên Textured PEI, mặt nhìn thấy là mặt in.",
           "Vòng LED quanh chân mỗi pad: phần chắn sáng mỏng 0,8 mm màu trắng/trong (TODO thử ánh sáng); màu LED đỏ/vàng/xanh lá/xanh dương = kick/snare/hi-hat/tom.",
           "Tối đa 3 màu nhựa + TPU đen + 1 điểm nhấn vàng chỉ ở nhãn STLAB (DESIGN.md).")


def _font(w, size):
    from PIL import ImageFont
    return ImageFont.truetype(str(FONTS / ("BeVietnamPro-%s.ttf" % w)), size)


def _annotate(im, dm):
    """Thuoc do tren anh nhin tren xuong: be rong hop, ban tay 140 mm."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    fb = _font("SemiBold", 26)
    S = 1200 / TOP_ORTHO
    px = lambda x: 600 + (x - TOP_C[0]) * S
    py = lambda y: 400 - (y - TOP_C[1]) * S
    col = (22, 35, 29)

    def hline(x0, x1, y, text):
        d.line([(px(x0), py(y)), (px(x1), py(y))], fill=col, width=2)
        for x in (x0, x1):
            d.line([(px(x), py(y) - 7), (px(x), py(y) + 7)], fill=col, width=2)
        w = d.textlength(text, font=fb)
        d.text(((px(x0) + px(x1)) / 2 - w / 2, py(y) + 8), text, font=fb, fill=col)

    hline(dm["x0"], dm["x1"], dm["y0"] - 14, "hộp %.0f × %.0f × %.0f mm" % (dm["dai"], dm["rong"], dm["cao"]))
    hline(-166 - 140, -166, -50, "tay bé ≈ 140 mm")
    return im


def _wrap(d, x, y, text, font, width, step, fill=INK):
    cur = ""
    for w in text.split():
        if d.textlength(cur + " " + w, font=font) > width:
            d.text((x, y), cur, font=font, fill=fill)
            y += step
            cur = w
        else:
            cur = (cur + " " + w).strip()
    d.text((x, y), cur, font=font, fill=fill)
    return y + step


def build_cmf():
    from PIL import Image, ImageDraw
    W, colw = 1800, 600
    cm = Image.new("RGB", (W, 640), MIST)
    d = ImageDraw.Draw(cm)
    d.rectangle([0, 0, W, 8], fill=PINEH)
    d.text((16, 20), "drum-pad – CMF (màu · vật liệu · bề mặt)", font=_font("Bold", 34), fill=INK)
    for i, k in enumerate("abc"):
        x, y = 16 + i * colw, 76
        d.rounded_rectangle([x, y, x + colw - 24, y + 556], 16, fill="white", outline="#C8D4CE", width=2)
        d.text((x + 16, y + 10), NOTE[k][:2] + NOTE[k].split("(")[0][2:].strip(), font=_font("Bold", 24), fill=INK)
        th = Image.open(OUT / ("concept-%s-3-4.png" % k)).convert("RGB").crop((150, 80, 1050, 700)).resize((330, 227))
        cm.paste(th, (x + 16, y + 48))
        yy = y + 285
        for part, vn, en, hexc in CMF[k]:
            d.rounded_rectangle([x + 16, yy, x + 70, yy + 44], 10, fill=hexc, outline="#9AA8A1", width=2)
            d.text((x + 82, yy - 4), part, font=_font("SemiBold", 18), fill=INK)
            d.text((x + 82, yy + 18), "%s – %s" % (vn, en), font=_font("Regular", 15), fill=INK)
            yy += 52
        for n in GENERIC[:1]:
            yy = _wrap(d, x + 16, yy + 2, "• " + n, _font("Regular", 15), colw - 60, 19)
    d.text((16, 612), GENERIC[2], font=_font("Regular", 15), fill=INK)
    cm.save(HERE / "cmf.png")


def build_pngs():
    from PIL import Image, ImageDraw
    dims = json.loads((OUT / "dims.json").read_text())
    for k in "abc":
        p = OUT / ("concept-%s-dinh.png" % k)
        _annotate(Image.open(p).convert("RGB"), dims[k]).save(OUT / ("concept-%s-dinh-ghi-chu.png" % k))
    build_cmf()
    W, iw = 1200, 570
    ih = int(iw * 800 / 1200)
    rowh = ih + 190
    cmf = Image.open(HERE / "cmf.png").convert("RGB")
    cmf = cmf.resize((W - 40, int(cmf.height * (W - 40) / cmf.width)))
    H = 78 + 3 * rowh + cmf.height + 20
    sh = Image.new("RGB", (W, H), MIST)
    d = ImageDraw.Draw(sh)
    d.rectangle([0, 0, W, 8], fill=PINEH)
    d.text((20, 20), "drum-pad – 3 dáng hộp trống (bước 0 Giao diện)", font=_font("Bold", 34), fill=INK)
    d.text((20, 62), "Bao ≤ 300 × 220 × 80 mm · pad Ø70 · loa Ø52 × 26 · 6 nút bo ra mặt hộp · USB + tai nghe ở cạnh · LED quanh mỗi pad",
           font=_font("Regular", 15), fill=INK)
    y = 90
    for k in "abc":
        d.rounded_rectangle([10, y, W - 10, y + rowh - 14], 16, fill="white", outline="#C8D4CE", width=2)
        t = NOTE[k] + ("   [khuyến nghị]" if k == "b" else "")
        d.text((26, y + 8), t, font=_font("Bold", 26), fill=INK)
        a = Image.open(OUT / ("concept-%s-3-4.png" % k)).convert("RGB").resize((iw, ih))
        b = Image.open(OUT / ("concept-%s-dinh-ghi-chu.png" % k)).convert("RGB").resize((iw, ih))
        sh.paste(a, (22, y + 46))
        sh.paste(b, (22 + iw + 14, y + 46))
        yy = y + 46 + ih + 8
        for j, c in enumerate(CRIT):  # 4 tieu chi, cham tron 0..3
            x = 26 + j * 290
            d.text((x, yy), c, font=_font("SemiBold", 16), fill=INK)
            for q in range(3):
                cx = x + 14 + q * 28 if False else x + 130 + q * 22
                d.ellipse([cx, yy + 5, cx + 14, yy + 19], fill=PINEH if q < SCORE[k][j] else "white", outline=PINEH, width=2)
        yy += 30
        yy = _wrap(d, 26, yy, "Ưu: " + PROS[k][0], _font("Regular", 16), W - 70, 21)
        _wrap(d, 26, yy, "Nhược: " + PROS[k][1], _font("Regular", 16), W - 70, 21)
        y += rowh
    sh.paste(cmf, (20, y))
    sh.save(HERE / "contact-sheet.png")
    print("OK", HERE / "contact-sheet.png", sh.size)


# ============================================================ ORCHESTRATOR ==
def run_blender():
    OUT.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", str(Path(__file__).resolve()), "--", "render"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    sys.stdout.write("\n".join(l for l in r.stdout.splitlines() if l.startswith(("DIMS", "Error", "Traceback", "RENDER"))
                               or "Error" in l) + "\n")
    if r.returncode != 0 or "Traceback" in r.stdout + r.stderr:
        sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:])
        raise SystemExit("Blender loi")


def blender_entry():
    OUT.mkdir(parents=True, exist_ok=True)
    args = sys.argv[sys.argv.index("--") + 1:]
    only = args[1] if len(args) > 1 else None
    p = OUT / "dims.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    for k in "abc":
        if only and only != k:
            continue
        old[k] = render_concept(k)
        p.write_text(json.dumps(old, indent=1, ensure_ascii=False))
    old["ghi_chu"] = ("Loa O52x26, bo 82x73, piezo, khe, lo vit: TODO buoc 1; hinh chi minh hoa. Gioi han 300 x 220 x 80 mm.")
    p.write_text(json.dumps(old, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    if bpy:
        blender_entry()
    else:
        only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
        if only in (None, "render"):
            run_blender()
        if only in (None, "sheet"):
            build_pngs()
