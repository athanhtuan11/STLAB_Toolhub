"""Buoc 0 – Giao dien card-coding-robot: 3 concept A/B/C (Blender bpy) + bo 8 the lenh + cmf + contact sheet.

Chay (python thuong, tu goi Blender nen):  python make_concepts.py [--only render|sheet]
Blender che do nen:  blender -b --factory-startup -P make_concepts.py -- render

Quy uoc: don vi mm (1 BU = 1 mm), robot huong +X, thang dung +Z, san/thảm z=0 (mat tham).
Khoi ben trong chi la UOC LUONG de nhin ty le (xem brief): ESP32 DevKit 55x28, 28BYJ-48 than O28 x 19,
hop 4xAA 62x58x16 (uoc luong), loa O30-36, RC522 60x40, ULN2003 35x31. Kich thuoc that chot o buoc 1.
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
except ImportError:  # chay bang python thuong
    bpy = None

# Mau nhua Bambu PETG Basic (xap xi sRGB de render; TODO xac nhan ten mau hang khi mua cuon)
PETG = {
    "Đỏ": ("Red", "#C8312B"), "Đen": ("Black", "#25272A"), "Trắng": ("White", "#F2F2EE"),
    "Vàng": ("Yellow", "#F2C230"), "Xanh dương": ("Blue", "#2B66C4"), "Cam": ("Orange", "#EE7F2B"),
    "Xanh lá": ("Green", "#2F9E57"),
}
RED, BLACK, WHITE, YELLOW, BLUE, ORANGE, GREEN = (PETG[k][1] for k in
                                                   ("Đỏ", "Đen", "Trắng", "Vàng", "Xanh dương", "Cam", "Xanh lá"))
SKIN = "#E9B79A"
BG = "#ECF1EF"   # "suong" – studio/design/DESIGN.md

# =============================================================== BLENDER ==
if bpy:
    MC, SHELL, ROBOT = {}, [], []

    def lin(h):
        v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in v)

    def mat(h, rough=.42, emit=0.0, metal=0.0, shell=False):
        key = (h, rough, emit, metal, shell)
        if key in MC:
            return MC[key]
        m = bpy.data.materials.new(h)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*lin(h), 1)
        b.inputs["Roughness"].default_value = rough
        b.inputs["Metallic"].default_value = metal
        if emit:
            b.inputs["Emission Color"].default_value = (*lin(h), 1)
            b.inputs["Emission Strength"].default_value = emit
        if shell:
            SHELL.append(m)
        MC[key] = m
        return m

    def link(name, bm, m, loc=(0, 0, 0), rot=None, sharp=40, robot=False, smooth=True):
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
        if robot:
            ROBOT.append(ob)
        return ob

    def box(name, size, loc, m, r=0.0, seg=4, rot=None, robot=False):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= size[0]
            v.co.y *= size[1]
            v.co.z *= size[2]
        if r > 0:
            bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=seg, affect="EDGES")
        return link(name, bm, m, loc, rot, robot=robot)

    def cyl(name, r, h, loc, m, axis="z", rb=0.0, seg=40, robot=False, r2=None):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
        if rb > 0:
            rim = [e for e in bm.edges if abs(abs(e.verts[0].co.z) - h / 2) < 1e-4 and abs(abs(e.verts[1].co.z) - h / 2) < 1e-4]
            bmesh.ops.bevel(bm, geom=rim, offset=rb, segments=3, affect="EDGES")
        rot = {"z": (0, 0, 0), "x": (0, math.pi / 2, 0), "y": (math.pi / 2, 0, 0)}[axis]
        return link(name, bm, m, loc, rot, robot=robot)

    def sp(a, e):
        return np.sign(a) * np.abs(a) ** e

    def superq(name, rx, ry, rz, e1, e2, c, z0, taper, m, nu=96, nv=56, robot=True, shell=True, zhi=None):
        """Sieu elip: e<1 vuong hon, e=1 elip. Cat day o z0, thu nho dan len dinh (taper)."""
        ztop = c[2] + rz
        vs, faces = [], []
        vs.append((c[0], c[1], max(c[2] - rz, z0)))  # cuc duoi
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
        ob = link(name, bm, m, robot=robot, sharp=70)
        return ob, bvh

    def prism(name, pts, h, z, m, ofs=(0, 0), rot=None, loc=None):
        bm = bmesh.new()
        f = bm.faces.new([bm.verts.new((x + ofs[0], y + ofs[1], 0)) for x, y in pts])
        res = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, verts=[g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)], vec=(0, 0, h))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        return link(name, bm, m, loc if loc else (0, 0, z), rot, sharp=30, smooth=False)

    def ell_pts(cx, cy, rx, ry, phi=0.0, n=28):
        return [(cx + rx * math.cos(t) * math.cos(phi) - ry * math.sin(t) * math.sin(phi),
                 cy + rx * math.cos(t) * math.sin(phi) + ry * math.sin(t) * math.cos(phi))
                for t in (2 * math.pi * i / n for i in range(n))]

    def rrect_pts(w, h, r, n=8):
        pts = []
        for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                           (w / 2 - r, -h / 2 + r, 270)):
            for k in range(n + 1):
                a = math.radians(a0 + 90 * k / n)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts

    def tube(name, pts, r, m, robot=True):
        cu = bpy.data.curves.new(name, "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = r
        cu.bevel_resolution = 3
        cu.use_fill_caps = True
        s = cu.splines.new("POLY")
        s.points.add(len(pts) - 1)
        for p, q in zip(s.points, pts):
            p.co = (q[0], q[1], q[2], 1)
        ob = bpy.data.objects.new(name, cu)
        bpy.context.scene.collection.objects.link(ob)
        cu.materials.append(m)
        if robot:
            ROBOT.append(ob)
        return ob

    def hit(bvh, o, d):
        r = bvh.ray_cast(Vector(o), Vector(d))
        return (r[0], r[1]) if r[0] is not None else (None, None)

    def top(bvh, x, y):
        return hit(bvh, (x, y, 400), (0, 0, -1))

    def front(bvh, y, z):
        return hit(bvh, (400, y, z), (-1, 0, 0))

    def disc(name, r, h, p, n, m, emb=0.35, seg=40, robot=True, rb=0.0):
        n = Vector(n).normalized()
        ob = cyl(name, r, h, tuple(Vector(p) + n * (h / 2 - emb * h)), m, rb=rb, seg=seg, robot=robot)
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = n.to_track_quat("Z", "Y")
        return ob

    def oriented(ob, n):
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = Vector(n).normalized().to_track_quat("Z", "Y")
        return ob

    def text(name, s, size, loc, m, font, ext=0.8, bold=True):
        cu = bpy.data.curves.new(name, "FONT")
        cu.body = s
        cu.font = font
        cu.size = size
        cu.extrude = ext / 2
        cu.align_x = cu.align_y = "CENTER"
        ob = bpy.data.objects.new(name, cu)
        bpy.context.scene.collection.objects.link(ob)
        cu.materials.append(m)
        ob.location = loc
        return ob

    # ------------------------------------------------------------ canh chung
    def reset():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        MC.clear(); SHELL.clear(); ROBOT.clear()
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
        box("san", (3000, 3000, 2), (0, 0, -4), mat("#D3DCD8", .9))

    def tile(cx, cy, alt=False):
        box("tham-vien", (150, 150, 3), (cx, cy, -1.5), mat("#8DB3A5", .8), r=.8, seg=2)
        box("tham-trong", (140, 140, 3.2), (cx, cy, -1.45), mat("#CFE6DC" if alt else "#EFE6C8", .85), r=.6, seg=2)
        for s in (-1, 1):  # vach giua o + (huong dan 150 mm)
            box("tham-vach", (100, .8, .3), (cx, cy + s * 0, .16), mat("#BFD2CB", .9)) if False else None
        box("tham-chu-thap-x", (22, 1.2, .3), (cx, cy, .17), mat("#B9CFC6", .9))
        box("tham-chu-thap-y", (1.2, 22, .3), (cx, cy, .17), mat("#B9CFC6", .9))

    def hand():
        m = mat(SKIN, .6)
        superq("ban-tay-long", 31, 30, 8, .7, .8, (182, 0, 8), 0, 0, m, nu=48, nv=24, robot=False, shell=False)
        superq("ban-tay-co", 24, 25, 7, .8, .9, (218, 0, 7), 0, 0, m, nu=48, nv=24, robot=False, shell=False)
        for y, L in ((21, 52), (7, 58), (-7, 54), (-21, 44)):
            superq("ngon", L / 2, 6.2, 5.6, 1, 1, (156 - L / 2, y, 5.6), 0, 0, m, nu=32, nv=16, robot=False, shell=False)
        ob, _ = superq("ngon-cai", 21, 6.8, 6.2, 1, 1, (0, 0, 6.2), 0, 0, m, nu=32, nv=16, robot=False, shell=False)
        ob.location = (176, 34, 0)
        ob.rotation_euler = (0, 0, math.radians(-26))
        for o in bpy.data.objects:
            if o.name.startswith(("ban-tay", "ngon")):
                o.location.x -= 14

    def internals(c):
        """Khoi ben trong uoc luong. c: rc_z, esp_z, spk=(loc, axis, d, depth)."""
        dark, met, pcb = mat("#2B2D31", .5), mat("#B9BEC4", .3, metal=.8), mat("#2D4FA8", .5)
        bx, ax_ = c.get("bx", -27), c.get("ax", 18)
        box("pin-4xAA", (58, 62, 16), (bx, 0, 5 + 8), dark, r=1.5)
        for i in range(4):  # 4 vien AA nam doc theo x
            cyl("AA", 7, 50, (bx, -23.2 + i * 15.5, 5 + 8.2), mat("#6C7480", .35, metal=.6), axis="x", seg=24)
        for s in (-1, 1):
            cyl("motor", 14, 19, (ax_, s * 27.5, 20), met, axis="y", seg=40)
            cyl("truc", 2.4, 10, (ax_, s * 40, 20), mat("#D7D9DB", .3, metal=.9), axis="y", seg=16)
            box("uln", (35, 31, 9), (bx - 3, s * 16.5, 28), pcb, r=1)
        box("esp32", (55, 28, 3), (bx - 1, 0, c["esp_z"]), mat("#1C1F24", .5), r=.6)
        box("esp32-can", (22, 18, 3), (bx + 14, 0, c["esp_z"] + 3), met, r=.6)
        box("esp32-usb", (9, 8, 3.5), (bx - 29, 0, c["esp_z"] + 3), met, r=.5)
        box("rc522", (40, 60, 3), (c.get("rc_x", -34), 0, c["rc_z"]), mat("#1E4FA0", .5), r=.8)
        (lx, ly, lz), ax, d, dep = c["spk"]
        cyl("loa", d / 2, dep, (lx, ly, lz), mat("#303236", .6), axis=ax, seg=40)
        cyl("loa-non", d / 2 - 4, dep + 1.2, (lx, ly, lz), mat("#C9CCD0", .5), axis=ax, seg=40)

    def wheels(ax_=18):
        for s in (-1, 1):
            cyl("banh", 20, 7, (ax_, s * 40, 20), mat("#1B1C1E", .8), axis="y", rb=1.5, seg=48)
            cyl("banh-hub", 9, 8, (ax_, s * 40, 20), mat("#5E646B", .5), axis="y", seg=32)

    def play_tri(x, y, z, s, m, name="play"):
        pts = [(-.55 * s, -.7 * s), (-.55 * s, .7 * s), (.8 * s, 0)]
        return prism(name, pts, .9, z, m, ofs=(x, y))

    def x_mark(x, y, z, s, m):
        for a in (45, -45):
            box("x", (s, s * .22, .9), (x, y, z + .45), m, robot=True, rot=(0, 0, math.radians(a)))

    # ---------------------------------------------------------- 3 concept
    def concept_a():
        red, blk, wht = mat(RED, .38, shell=True), mat(BLACK, .5, shell=True), mat(WHITE, .45)
        sh, bvh = superq("vo", 51, 58, 44, .55, .6, (-10, 0, 14), 3, .06, red, shell=True)
        # mat na/dau den o phia truoc
        xf, _ = front(bvh, 0, 27)
        mk, mb = superq("dau", 11, 36, 17, .6, .75, (xf.x - 2, 0, 27), 12, 0, blk)
        for s in (-1, 1):  # mat LED
            p, n = front(mb, s * 14, 31)
            disc("mat", 7.2, 3.0, p, n, mat("#D9F7FF", .3, emit=3.0), seg=40)
        for k in range(5):  # mieng = luoi loa
            t = (k - 2) / 2
            p, n = front(mb, t * 14, 19.5 + 4 * t * t)
            if p:
                disc("loa-lo", 1.4, 2, p, n, mat("#0E0F10"), seg=16)
        for x, y in ((-46, 42), (-46, -42), (-14, 47), (-14, -47), (14, 41), (14, -41)):  # cham bo rua
            p, n = top(bvh, x, y)
            if p:
                disc("cham", 8, 2.4, p, n, blk, emb=.5, seg=32)
        # vung quet the + nut
        p, _ = top(bvh, -36, 0)
        box("khe-quet", (12, 56, 1.4), (-36, 0, p.z - .3), mat("#111214"), r=.5, robot=True)
        for dx in (-3.4, 3.4):
            box("khe-vach", (1.2, 50, .5), (-36 + dx, 0, p.z + .6), mat("#D8D8D2", .5), robot=True)
        p, _ = top(bvh, -4, 0)
        cyl("nut-chay", 15, 7, (-4, 0, p.z + 2.6), mat(YELLOW, .35), rb=2.4, robot=True)
        play_tri(-4, 0, p.z + 6.1, 10, blk, "chay-tam-giac")
        ROBOT.append(bpy.data.objects["chay-tam-giac"])
        p, _ = top(bvh, 25, 0)
        cyl("nut-xoa", 9, 5, (25, 0, p.z + 1.8), wht, rb=1.6, robot=True)
        x_mark(25, 0, p.z + 4.3, 8, blk)
        wheels()
        internals({"esp_z": 36, "rc_z": 46.5, "rc_x": -30, "spk": ((22, 0, 41), "z", 30, 7)})
        return {"duoi": 0}

    def concept_b():
        blu, blk, wht = mat(BLUE, .4, shell=True), mat(BLACK, .5, shell=True), mat(WHITE, .45, shell=True)
        sh, bvh = superq("vo", 57, 57, 40, .28, .38, (-3, 0, 41), 3, .0, blu, shell=True)
        # nap tren (mau trang) co ngan quet the
        lid = box("nap", (100, 96, 2.6), (-5, 0, 81.3), wht, r=1.2, robot=True)
        SHELL_OBJ = [lid]
        # mat LED phia truoc
        xf, _ = front(bvh, 0, 52)
        panel = box("mat-tam", (2.4, 74, 40), (xf.x - .2, 0, 52), blk, r=1.6, robot=True)
        for s in (-1, 1):
            box("mat-mat", (3, 13, 18), (xf.x + 1.4, s * 17, 57), mat("#D9F7FF", .3, emit=3.0), r=3.2, robot=True)
        pts = [(xf.x + 1.9, 13 * t / 5 * 1, 42 - 7 * (1 - (t / 5) ** 2)) for t in range(-5, 6)]
        for k in range(-3, 4):  # mieng cuoi = cac khe loa
            t = k / 3
            box("khe-loa", (2.2, 2.4, 5.5), (xf.x + 1.5, t * 15, 40 + 6.5 * t * t), mat("#E8EEF0", .5), r=.7, robot=True)
        # khay quet the + nut
        box("khe-quet", (13, 62, 1.2), (-33, 0, 82.4), mat("#111214"), r=.5, robot=True)
        for dx in (-4.3, 4.3):
            box("khe-vach", (1.2, 54, .5), (-33 + dx, 0, 83.1), mat(YELLOW, .5), robot=True)
        box("nut-chay", (32, 32, 7), (6, 0, 85.2), mat(YELLOW, .35), r=3.4, robot=True)
        play_tri(6, 0, 88.5, 11, blk, "chay-tam-giac")
        ROBOT.append(bpy.data.objects["chay-tam-giac"])
        cyl("nut-xoa", 9.5, 5, (38, 0, 84.5), mat(WHITE, .4), rb=1.6, robot=True)
        x_mark(38, 0, 87, 8.5, blk)
        wheels()
        internals({"esp_z": 36, "rc_z": 76.5, "spk": ((43, 0, 52), "x", 34, 10)})
        return {"shell_extra": SHELL_OBJ}

    def concept_c():
        grn, wht, blk = mat(GREEN, .4, shell=True), mat(WHITE, .45), mat(BLACK, .5)
        sh, bvh = superq("vo", 56, 56, 46, .5, .6, (-4, 0, 47), 3, .34, grn, shell=True)
        # bung trang + khe loa hinh chu V
        p, n = front(bvh, 0, 36)
        ob = superq("bung", 5, 26, 21, 1, 1, (p.x - 1.2, 0, 35), 0, 0, mat(WHITE, .45, shell=True), nu=48, nv=24)[0]
        for k, z in enumerate((42, 34, 26)):
            pts = []
            for t in range(-6, 7):
                y = t * 2.0
                zz = z - abs(y) * .45
                q, nn = front(bvh, y, zz)
                pts.append(tuple(Vector((p.x + 3.6, y, zz))))
            tube("long", pts, 1.1, mat(GREEN, .5, shell=True))
        # mat to: vong trang + vong den + LED
        for s in (-1, 1):
            q, n = front(bvh, s * 18.5, 68)
            e = disc("mat-vong", 16, 3, q, n, wht, seg=56)
            disc("mat-den", 10.5, 4, q + Vector(n) * .7, n, blk, seg=48)
            disc("mat-led", 5.2, 4.4, q + Vector(n) * 1.1, n, mat("#D9F7FF", .3, emit=3.2), seg=40)
        # mo
        q, n = front(bvh, 0, 57)
        beak = cyl("mo", 8.5, 12, tuple(q + Vector((5.5, 0, 0))), mat(YELLOW, .45), axis="x", rb=1.0, seg=3, r2=1.5, robot=True)
        beak.rotation_euler = (0, -math.pi / 2, math.pi)  # dinh nhon huong +x
        beak.rotation_euler = (0, math.radians(90), 0)
        for s in (-1, 1):  # chan trang tri
            cyl("chan", 7, 5, (q.x - 3, s * 15, 6), mat(YELLOW, .45), rb=1.6, robot=True)
        # tai coc: 2 chop nhon tren dinh
        for s in (-1, 1):
            p2, _ = top(bvh, 24, s * 27)
            c = cyl("tai", 8, 13, (24, s * 28, p2.z + 4.2), grn, rb=.6, seg=24, r2=2.5, robot=True)
            c.rotation_euler = (math.radians(-s * 12), math.radians(-8), 0)
            SHELL.append(c.data.materials[0])
        # khe quet the tren dinh + 2 canh = nut
        p, _ = top(bvh, -12, 0)
        box("khe-quet", (12, 50, 1.4), (-12, 0, p.z - .3), mat("#111214"), r=.5, robot=True)
        for dx in (-3.4, 3.4):
            box("khe-vach", (1.2, 44, .5), (-12 + dx, 0, p.z + .6), mat("#D8D8D2", .5), robot=True)
        for s, col, nm in ((1, YELLOW, "canh-chay"), (-1, WHITE, "canh-xoa")):
            q, n = hit(bvh, (-8, s * 300, 52), (0, -s, 0))
            w, wh = (22, 46) if s == 1 else (16, 30)
            wz = 52 if s == 1 else 50
            q, n = hit(bvh, (-8, s * 300, wz), (0, -s, 0))
            ob, _ = superq(nm, w / 2, 6, wh / 2, 1, 1, (0, 0, 0), -999, 0, mat(col, .38), nu=56, nv=32)
            ob.location = (-8, q.y + s * 1.5, wz)
            ob.rotation_euler = (math.radians(-s * 10), 0, 0)
            ROBOT.append(ob)
            lp = Vector((-8, q.y + s * 7.3, wz))
            if s == 1:
                pt = play_tri(0, 0, 0, 9, blk, "chay-tam-giac")
                pt.rotation_euler = (math.radians(-90), 0, 0)
                pt.location = (-8 + .0, q.y + s * 7.2, wz)
                ROBOT.append(pt)
            else:
                for a in (45, -45):
                    xb = box("x", (7, 1.9, .9), (-8, q.y + s * 6.2, wz), blk, robot=True, rot=(0, 0, 0))
                    xb.rotation_euler = (math.radians(90), math.radians(a), 0)
        wheels(22)
        internals({"bx": -24, "ax": 22, "esp_z": 38, "rc_z": 80, "rc_x": -12, "spk": ((38, 0, 52), "x", 34, 10)})
        return {}

    BUILD = {"a": concept_a, "b": concept_b, "c": concept_c}

    # ---------------------------------------------------------------- render
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
        return ob

    def shot(path, view, size=SIZE, samples=48):
        sc = bpy.context.scene
        sc.render.resolution_x, sc.render.resolution_y = size
        eevee = getattr(sc, "eevee", None)
        if eevee is not None and hasattr(eevee, "taa_render_samples"):
            eevee.taa_render_samples = samples
        for o in [o for o in bpy.data.objects if o.type == "CAMERA"]:
            bpy.data.objects.remove(o)
        cx = 82
        if view == "hong":
            camera((cx, -1000, 45), rot=(math.pi / 2, 0, 0), ortho=320)
        elif view == "dinh":
            camera((cx, 0, 1000), rot=(0, 0, 0), ortho=320)
        elif view == "3-4":
            camera((285, -330, 220), target=(78, 0, 20), lens=38)
        elif view == "trong":
            camera((215, -245, 285), target=(5, 0, 35), lens=52)
        elif view == "cards-top":
            camera((150, 0, 1000), rot=(0, 0, 0), ortho=500)
        elif view == "cards-34":
            camera((150, -450, 400), target=(150, 0, 0), lens=36)
        sc.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)

    def xray(on):
        for m in SHELL:
            b = m.node_tree.nodes["Principled BSDF"]
            b.inputs["Alpha"].default_value = .13 if on else 1.0
            if on:
                m["_c"] = list(b.inputs["Base Color"].default_value)
                b.inputs["Base Color"].default_value = (.55, .62, .68, 1)
            elif "_c" in m:
                b.inputs["Base Color"].default_value = m["_c"]
            try:
                m.surface_render_method = "BLENDED" if on else "DITHERED"
            except Exception:
                pass

    def silhouette(path, view):
        sc = bpy.context.scene
        black = bpy.data.materials.new("sil")
        black.use_nodes = True
        nt = black.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs[0].default_value = (0, 0, 0, 1)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs[0], out.inputs[0])
        bpy.context.view_layer.material_override = black
        sc.world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
        sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
        sc.view_settings.exposure = 0
        hide = [o for o in bpy.data.objects if o.type not in ("CAMERA", "LIGHT") and o not in ROBOT]
        for o in hide:
            o.hide_render = True
        shot(path, view, samples=8)
        for o in hide:
            o.hide_render = False
        bpy.context.view_layer.material_override = None

    def bbox():
        bpy.context.view_layer.update()
        pts = []
        for o in ROBOT:
            for c in o.bound_box:
                pts.append(o.matrix_world @ Vector(c))
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        return lo, hi

    def render_concept(k, only=None):
        sc = reset()
        floor()
        tile(0, 0)
        tile(150, 0, alt=True)
        hand()
        BUILD[k]()
        lo, hi = bbox()
        dims = {"x0": lo[0], "x1": hi[0], "y0": lo[1], "y1": hi[1], "z1": hi[2],
                "dai": hi[0] - lo[0], "rong": hi[1] - lo[1], "cao": hi[2]}
        print("DIMS", k, json.dumps({a: round(b, 1) for a, b in dims.items()}))
        for v in ("hong", "dinh", "3-4"):
            shot(OUT / f"concept-{k}-{v}.png", v)
        xray(True)
        shot(OUT / f"concept-{k}-trong.png", "trong")
        xray(False)
        silhouette(OUT / f"concept-{k}-bong-hong.png", "hong")
        silhouette(OUT / f"concept-{k}-bong-dinh.png", "dinh")
        return dims

    # --------------------------------------------------------------- the lenh
    def card_icons(kind, m, font, cx, cy0, z):
        """Bieu tuong noi trong the (toa do cuc bo, goc giua the; y len = huong tien cua the)."""
        P = []
        cy = cy0 + 6
        if kind in ("tien", "lui"):
            sg = 1 if kind == "tien" else -1
            P.append([(-5, sg * -14), (5, sg * -14), (5, sg * 7), (-5, sg * 7)])
            P.append([(-15, sg * 5), (15, sg * 5), (0, sg * 23)])
        elif kind in ("trai", "phai"):
            dx = -1 if kind == "trai" else 1
            P.append([(-5, -16), (5, -16), (5, 9), (-5, 9)])
            P.append([(-dx * 5, -1), (dx * 12, -1), (dx * 12, 9), (-dx * 5, 9)])
            P.append([(dx * 10, -9), (dx * 10, 19), (dx * 26, 5)])
        elif kind.startswith("lap") or kind == "het":
            R, r = 17.5, 11
            a0, a1 = 60, 330
            n = 40
            outer = [(R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), R * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
            inner = [(r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n, -1, -1)]
            P.append(outer + inner)
            ang = math.radians(a1)
            rm = (R + r) / 2
            bx, by = rm * math.cos(ang), rm * math.sin(ang)
            tx, ty = -math.sin(ang), math.cos(ang)
            nx, ny = math.cos(ang), math.sin(ang)
            P.append([(bx + nx * 9.5, by + ny * 9.5), (bx - nx * 9.5, by - ny * 9.5), (bx + tx * 14, by + ty * 14)])
            if kind == "het":
                P.append([(-5, -5), (5, -5), (5, 5), (-5, 5)])
        elif kind == "nhay":
            P.append(ell_pts(-9, -8, 8.5, 6, math.radians(20)))
            P.append([(-2, -8), (2.4, -8), (2.4, 21), (-2, 21)])
            P.append([(2.4, 21), (16, 13), (16, 19.5), (2.4, 28)])
            st = []
            for i in range(10):
                rr = 7.5 if i % 2 == 0 else 3.2
                a = math.radians(90 + 36 * i)
                st.append((14 + rr * math.cos(a), -11 + rr * math.sin(a)))
            P.append(st)
        K = .82
        for i, pts in enumerate(P):
            pts = [(x * K, y * K) for x, y in pts]
            prism(f"icon-{kind}-{i}", pts, 1.6, z, m, ofs=(cx, cy))
        if kind in ("lap2", "lap3"):
            text("so", "×" + kind[-1], 9.0, (cx - 1.2, cy - 0.4, z), m, font, ext=1.6)

    def cards():
        sc = reset()
        floor()
        tile(0, 0)
        reg = bpy.data.fonts.load(str(FONTS / "BeVietnamPro-Regular.ttf"))
        bold = bpy.data.fonts.load(str(FONTS / "BeVietnamPro-Bold.ttf"))
        spec = [("tien", "Tiến", "Forward", BLUE), ("lui", "Lùi", "Back", BLUE),
                ("trai", "Rẽ trái", "Turn left", BLUE), ("phai", "Rẽ phải", "Turn right", BLUE),
                ("lap2", "Lặp 2 lần", "Repeat 2", ORANGE), ("lap3", "Lặp 3 lần", "Repeat 3", ORANGE),
                ("het", "Hết lặp", "End loop", ORANGE), ("nhay", "Nhảy múa", "Dance", YELLOW)]
        wht, blk = mat(WHITE, .4), mat(BLACK, .45)
        for i, (k, vi, en, col) in enumerate(spec):
            cy = 38 * (1 if i < 4 else -1)
            cx = 150 + 72 * (i % 4)
            ink = blk if col == YELLOW else wht
            base = prism(f"the-{k}", rrect_pts(60, 60, 8), 4.0, -3.0, mat(col, .38), ofs=(0, 0), loc=(cx, cy, -3.0))
            card_icons(k, ink, bold, cx, cy, 1.0)
            t1 = text(f"vi-{k}", vi, 6.4, (cx, cy - 19.5, 1.0), ink, bold, ext=.9)
            t2 = text(f"en-{k}", en, 4.3, (cx, cy - 25.7, 1.0), ink, reg, ext=.9)
        shot(OUT / "the-lenh-tren.png", "cards-top", size=(2000, 700))
        shot(OUT / "the-lenh-3-4.png", "cards-34", size=(1600, 640))


# ------------------------------------------------------------------ PIL ----
NOTE = {
    "a": ("A – Bọ rùa", "khuyến nghị",
          ["Vòm thấp 65 mm, trọng tâm thấp, bánh giấu hẳn dưới vỏ.",
           "Mặt nạ đen + 2 mắt LED chỉ hướng đi; khe quẹt ở lưng, nút Chạy vàng Ø30.",
           "Đổi lại: nếu mắt tắt thì khó thấy hướng – cần mắt luôn sáng."]),
    "b": ("B – Khối mặt cười", "rủi ro giống đồ có sẵn",
          ["Khối bo 114 × 117 mm cao 89 mm, mặt LED phía trước, nắp trắng quẹt thẻ.",
           "Dễ hiểu 'rẽ trái/phải' trên thảm ô vuông; nút Chạy vuông 32 mm.",
           "Đổi lại: thẳng cạnh nên dễ giống sản phẩm khối vuông thương mại, cao hơn A."]),
    "c": ("C – Cú con", "cùng nhà Cú Bông",
          ["Thân trứng cao 98 mm, mắt to LED, mỏ vàng chỉ hướng; cánh = 2 nút.",
           "Kể chuyện tốt, cùng thương hiệu Cú Bông; nút Chạy = cánh vàng 22 × 46 mm.",
           "Đổi lại: cao nhất, dễ lật khi quay/va; pin phải dồn sát đáy."]),
}
CARD_GROUPS = [("Di chuyển", "Xanh dương (Blue)", BLUE, "Tiến · Lùi · Rẽ trái · Rẽ phải"),
               ("Lặp", "Cam (Orange)", ORANGE, "Lặp ×2 · Lặp ×3 · Hết lặp"),
               ("Vui", "Vàng (Yellow)", YELLOW, "Nhảy múa / âm thanh")]
CMF = {
    "a": [("Vỏ vòm", "Đỏ", "Red", RED), ("Mặt nạ đầu, chấm, bánh", "Đen", "Black", BLACK),
          ("Nút Chạy (điểm nhấn)", "Vàng", "Yellow", YELLOW), ("Nút Xóa, mắt LED (khuếch tán)", "Trắng", "White", WHITE)],
    "b": [("Thân", "Xanh dương", "Blue", BLUE), ("Nắp trên, khe loa miệng, nút Xóa", "Trắng", "White", WHITE),
          ("Tấm mặt LED, dấu X", "Đen", "Black", BLACK), ("Nút Chạy (điểm nhấn)", "Vàng", "Yellow", YELLOW)],
    "c": [("Thân, tai", "Xanh lá", "Green", GREEN), ("Bụng, vòng mắt, cánh Xóa", "Trắng", "White", WHITE),
          ("Mắt đen, khe quẹt, dấu X", "Đen", "Black", BLACK), ("Mỏ, chân, cánh Chạy (nhấn)", "Vàng", "Yellow", YELLOW)],
}
INK, PINE, MIST, FIL = "#16231D", "#1E5A45", "#ECF1EF", "#E8B33A"


def _font(w, size):
    from PIL import ImageFont
    return ImageFont.truetype(str(FONTS / ("BeVietnamPro-%s.ttf" % w)), size)


def _annotate(im, view, dm):
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    fb = _font("SemiBold", 22)
    S, cx = 3.75, 82
    px = lambda x: 600 + (x - cx) * S
    col = (22, 35, 29)

    def hline(x0, x1, y, text, above=True):
        d.line([(px(x0), y), (px(x1), y)], fill=col, width=2)
        for x in (x0, x1):
            d.line([(px(x), y - 7), (px(x), y + 7)], fill=col, width=2)
        w = d.textlength(text, font=fb)
        d.text(((px(x0) + px(x1)) / 2 - w / 2, y - 32 if above else y + 10), text, font=fb, fill=col)

    if view == "hong":
        yz = lambda z: 400 - (z - 45) * S
        hline(-75, 75, yz(-3) + 38, "ô thảm 150 mm", above=False)
        hline(dm["x0"], dm["x1"], yz(dm["cao"]) - 24, "dài %.0f mm" % dm["dai"])
        x = px(dm["x0"]) - 22
        d.line([(x, yz(0)), (x, yz(dm["cao"]))], fill=col, width=2)
        for z in (0, dm["cao"]):
            d.line([(x - 7, yz(z)), (x + 7, yz(z))], fill=col, width=2)
        t = "cao %.0f mm" % dm["cao"]
        d.text((x - 8 - d.textlength(t, font=fb), (yz(0) + yz(dm["cao"])) / 2 - 12), t, font=fb, fill=col)
        hline(80, 202, yz(-3) + 38, "bàn tay bé 5 tuổi ≈ 120 mm", above=False)
    else:
        yy = lambda y: 400 - y * S
        hline(-75, 75, yy(75) - 22, "ô thảm 150 mm")
        hline(dm["x0"], dm["x1"], yy(-75) + 24, "robot %.0f × %.0f mm" % (dm["dai"], dm["rong"]), above=False)
        hline(80, 202, yy(-75) + 24, "bàn tay bé 5 tuổi ≈ 120 mm", above=False)
    return im


def _wrap(d, x, y, text, font, width, step):
    cur = ""
    for w in text.split():
        if d.textlength(cur + " " + w, font=font) > width:
            d.text((x, y), cur, font=font, fill=INK)
            y += step
            cur = w
        else:
            cur = (cur + " " + w).strip()
    d.text((x, y), cur, font=font, fill=INK)
    return y + step


def cmf_png(img, y, d):
    from PIL import Image
    colw = 1010
    for i, k in enumerate("abc"):
        x = 20 + i * colw
        d.rounded_rectangle([x, y, x + colw - 30, y + 440], 16, fill="white", outline="#C8D4CE", width=2)
        d.text((x + 20, y + 12), NOTE[k][0], font=_font("Bold", 28), fill=INK)
        th = Image.open(OUT / ("concept-%s-3-4.png" % k)).convert("RGB").crop((100, 60, 900, 640)).resize((300, 218))
        img.paste(th, (x + colw - 30 - 320, y + 56))
        yy = y + 64
        for part, vn, en, hexc in CMF[k]:
            d.rounded_rectangle([x + 20, yy, x + 80, yy + 50], 10, fill=hexc, outline="#9AA8A1", width=2)
            d.text((x + 94, yy - 2), part, font=_font("SemiBold", 21), fill=INK)
            d.text((x + 94, yy + 25), "%s – Bambu PETG Basic %s" % (vn, en), font=_font("Regular", 18), fill=INK)
            yy += 62
        notes = ["Mỗi part đơn sắc rồi ráp lại (hạn chế AMS); 3 màu + 1 điểm nhấn vàng.",
                 "Mặt dưới in trên Textured PEI (nhám, chống trượt trên thảm); mặt trên nhìn thấy: bóng vừa.",
                 "Mắt LED: nắp khuếch tán trắng mỏng 0,8 mm (TODO thử ánh sáng).",
                 "Khoang pin 4×AA NiMH: nắp khóa vít, không Li-ion."]
        yy = max(yy, y + 300)
        for n in notes:
            yy = _wrap(d, x + 20, yy, "• " + n, _font("Regular", 17), colw - 80, 22) + 2


def build_sheet():
    from PIL import Image, ImageDraw
    dims = json.loads((OUT / "dims.json").read_text())
    W, CW, CH, LW = 3050, 560, 373, 250
    rows = []
    for k in "abc":
        ims = [_annotate(Image.open(OUT / ("concept-%s-%s.png" % (k, v))).convert("RGB"), v, dims[k])
               for v in ("hong", "dinh")]
        ims.append(Image.open(OUT / ("concept-%s-3-4.png" % k)).convert("RGB"))
        ims.append(Image.open(OUT / ("concept-%s-trong.png" % k)).convert("RGB"))
        a = Image.open(OUT / ("concept-%s-bong-hong.png" % k)).convert("RGB").crop((0, 150, 700, 650))
        b = Image.open(OUT / ("concept-%s-bong-dinh.png" % k)).convert("RGB").crop((0, 100, 700, 700))
        sil = Image.new("RGB", (1200, 800), "white")
        sil.paste(a.resize((560, 400)), (20, 20))
        sil.paste(b.resize((467, 400)), (640, 20))
        ims.append(sil)
        rows.append(ims)
    HEAD, GAP = 150, 14
    cards_t = Image.open(OUT / "the-lenh-tren.png").convert("RGB")
    cards_3 = Image.open(OUT / "the-lenh-3-4.png").convert("RGB")
    t = cards_t.resize((1930, int(700 * 1930 / 2000)))
    c3 = cards_3.resize((1090, int(640 * 1090 / 1600)))
    sec_h = t.height + 190
    H = HEAD + 3 * (CH + GAP) + 40 + 50 + sec_h + 40 + 52 + 460 + 30
    sh = Image.new("RGB", (W, H), MIST)
    d = ImageDraw.Draw(sh)
    d.rectangle([0, 0, W, 8], fill=PINE)
    d.rectangle([40, 40, 52, 92], fill=FIL)
    d.text((72, 30), "card-coding-robot – Bước 0 Giao diện", font=_font("Bold", 46), fill=INK)
    d.text((74, 90), "Robot lập trình bằng thẻ cho bé 4–7 tuổi · 3 concept · ô thảm 150 mm · bàn tay bé 5 tuổi làm thước · "
           "robot quay mặt sang phải · khuyến nghị: A – Bọ rùa", font=_font("Regular", 24), fill=INK)
    for c, tt in enumerate(["Bóng hông (nhìn ngang)", "Bóng đỉnh (nhìn từ trên)", "Phối cảnh 3/4",
                            "Bên trong (khối ước lượng)", "Bóng đen: hông + đỉnh"]):
        d.text((LW + c * CW + 8, HEAD - 34), tt, font=_font("SemiBold", 22), fill=PINE)
    for r, (k, ims) in enumerate(zip("abc", rows)):
        y = HEAD + r * (CH + GAP)
        title, tag, lines = NOTE[k]
        d.text((16, y + 4), title, font=_font("Bold", 28), fill=INK)
        tw = d.textlength(tag, font=_font("SemiBold", 18))
        d.rounded_rectangle([16, y + 44, 16 + tw + 20, y + 74], 8, fill=PINE if k == "a" else "#7F8F88")
        d.text((26, y + 48), tag, font=_font("SemiBold", 18), fill="white")
        yy = y + 90
        for ln in lines:
            yy = _wrap(d, 16, yy, ln, _font("Regular", 17), LW - 28, 22) + 4
        for c, im in enumerate(ims):
            sh.paste(im.resize((CW - 6, CH - 4)), (LW + c * CW, y))
    y = HEAD + 3 * (CH + GAP) + 40
    d.text((16, y), "Bộ 8 thẻ lệnh ~ 60 × 60 mm + 1 ô thảm 150 mm (biểu tượng nổi, màu theo nhóm, chữ song ngữ nhỏ)",
           font=_font("Bold", 30), fill=INK)
    y += 50
    sh.paste(t, (10, y))
    sh.paste(c3, (1950, y))
    gy = y + t.height + 14
    for i, (g, cn, col, lst) in enumerate(CARD_GROUPS):
        gx = 30 + i * 640
        d.rounded_rectangle([gx, gy, gx + 60, gy + 60], 12, fill=col)
        d.text((gx + 76, gy - 2), "Nhóm %s – %s" % (g, cn), font=_font("SemiBold", 24), fill=INK)
        d.text((gx + 76, gy + 30), lst, font=_font("Regular", 21), fill=INK)
    _wrap(d, 1950, y + c3.height + 14,
          "Thẻ = đế màu 2,0 mm + biểu tượng nổi 1,6 mm (đổi màu giữa chừng, không cần AMS); sticker NTAG213 ép giữa 2 lớp; "
          "góc bo 8 mm; không có chi tiết rời nhỏ.", _font("Regular", 20), 1070, 26)
    y = gy + 100
    d.text((16, y), "CMF – chỉ nhựa Bambu PETG Basic thông dụng, mỗi part một màu (TODO xác nhận tên màu hãng khi mua cuộn)",
           font=_font("Bold", 30), fill=INK)
    cmf_png(sh, y + 52, d)
    sh.save(HERE / "contact-sheet.png")
    cm = Image.new("RGB", (W, 640), MIST)
    dd = ImageDraw.Draw(cm)
    dd.rectangle([0, 0, W, 8], fill=PINE)
    dd.text((16, 22), "card-coding-robot – CMF (màu · vật liệu · bề mặt)", font=_font("Bold", 36), fill=INK)
    cmf_png(cm, 90, dd)
    cm.save(HERE / "cmf.png")
    print("OK", HERE / "contact-sheet.png", HERE / "cmf.png")



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
    dims = {}
    only = args[1] if len(args) > 1 else None
    for k in "abc":
        if only and only != k and only != "cards":
            continue
        if only == "cards":
            break
        dims[k] = render_concept(k)
    if only in (None, "cards"):
        cards()
    if dims:
        p = OUT / "dims.json"
        old = json.loads(p.read_text()) if p.exists() else {}
        old.update(dims)
        p.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    if bpy:
        blender_entry()
    else:
        only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
        if only in (None, "render"):
            run_blender()
        if only in (None, "sheet"):
            build_sheet()
