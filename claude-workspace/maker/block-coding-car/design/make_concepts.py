"""Buoc 0 – Giao dien block-coding-car: 3 dang xe A (xe hop mat cuoi) / B (bo rua) / C (cu con) tren DE CHUNG (Blender bpy).

Chay:  python make_concepts.py            (goi Blender nen, ve, chu thich, cmf.png)
Blender nen:  blender -b --factory-startup -P make_concepts.py -- render
Dua tren card-coding-robot/design/make_concepts.py (khong sua file do; phan ha tang chep sang).

Quy uoc: mm (1 BU = 1 mm), xe huong +X, san/tham z=0. De chung: 2x28BYJ-48 (tam banh y=±40, truc z=20, x=20) + banh O40 giau
trong than, hop 4xAA nam phang (z 5..21), bi do phia sau. Khoi ben trong chi la UOC LUONG (TODO do that o buoc 1).
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


    PRE = set()

    def mark():
        """Danh dau cac vat the vo ngoai (de do bao) - goi truoc khi them banh/noi that."""
        ROBOT[:] = [o for o in bpy.data.objects if o.name not in PRE and o.type in ("MESH", "CURVE")]

    def wheels(ax_=20):
        for s in (-1, 1):
            cyl("banh", 20, 7, (ax_, s * 40, 20), mat("#1B1C1E", .8), axis="y", rb=1.5, seg=48)
            cyl("banh-hub", 9, 8, (ax_, s * 40, 20), mat("#5E646B", .5), axis="y", seg=32)

    def internals():
        """UOC LUONG - TODO do bo that: ESP32-S3 DevKit ~65x26 (PCB+header), ULN2003 35x31x9, hop 4xAA 58x62x16."""
        dark, met, pcb = mat("#2B2D31", .5), mat("#B9BEC4", .3, metal=.8), mat("#2D4FA8", .5)
        bx, ax_ = -22, 20
        box("pin-4xAA", (58, 62, 16), (bx, 0, 13), dark, r=1.5)
        for i in range(4):
            cyl("AA", 7, 50, (bx, -23.2 + i * 15.5, 13.2), mat("#6C7480", .35, metal=.6), axis="x", seg=24)
        for s in (-1, 1):
            cyl("motor", 14, 19, (ax_, s * 27.5, 20), met, axis="y", seg=40)
            cyl("truc", 2.4, 10, (ax_, s * 40, 20), mat("#D7D9DB", .3, metal=.9), axis="y", seg=16)
            box("uln2003", (35, 31, 9), (bx - 3, s * 16.5, 28), pcb, r=1)
        box("esp32-s3", (65, 26, 3), (bx + 2, 0, 36), mat("#1C1F24", .5), r=.6)
        box("esp32-can", (22, 16, 3), (bx + 12, 0, 39), met, r=.6)
        box("esp32-usb", (9, 8, 3.5), (bx - 30, 0, 39), met, r=.5)
        superq("bi-do", 5, 5, 5, 1, 1, (-57, 0, 5), -999, 0, mat("#C9CCD0", .3, metal=.7), nu=24, nv=12,
               robot=False, shell=False)

    def stop_button(x, y, z, ring_r=19):
        """Nut Dung do O28 (>=25) tren vong trang. z = mat nong."""
        cyl("nut-vong", ring_r, 3.6, (x, y, z + 1.0), mat(WHITE, .45), rb=.8, seg=48)
        cyl("nut-dung", 14, 7, (x, y, z + 6.3), mat(RED, .3), rb=2.6, seg=48)

    def label_pill(x, y, z, team_hex, w=20, l=44):
        box("nhan-den", (w, l, 1.4), (x, y, z), mat(BLACK, .5, shell=True), r=.6)
        box("nhan-mau", (w - 6, l - 8, 1.8), (x, y, z + .2), mat(team_hex, .38), r=.8)

    # ---------------------------------------------------------- 3 dang xe
    def concept_a(team):
        body, blk = mat(team, .38, shell=True), mat(BLACK, .5, shell=True)
        box("than", (112, 110, 41), (-6, 0, 23.5), body, r=11)            # x -62..50, z 3..44
        box("cabin", (70, 96, 30), (-20, 0, 57), body, r=10)               # x -55..15, z 42..72
        box("kinh-mat", (3, 80, 22), (14.8, 0, 58), blk, r=1.2)
        for s in (-1, 1):
            disc("mat-led", 7.2, 3.0, (16.2, s * 17, 61), (1, 0, 0), mat("#D9F7FF", .3, emit=3.0))
            box("kinh-hong", (40, 1.6, 15), (-24, s * 47.8, 58), blk, r=.7)
        pts = [(16.4, t * 2.0, 53 - 5 * (1 - (t / 7) ** 2)) for t in range(-7, 8)]
        tube("mieng", pts, 1.3, mat("#8A9097", .5))
        box("can", (6, 102, 9), (48.5, 0, 12), blk, r=2)
        for s in (-1, 1):
            box("viem-hong", (84, 2.4, 6), (-8, s * 55, 11), blk, r=1.0)
        label_pill(34, 0, 44.6, team)
        stop_button(-20, 0, 72, 19)
        mark()
        wheels()
        internals()

    def concept_b(team):
        body, blk = mat(team, .38, shell=True), mat(BLACK, .5, shell=True)
        sh, bvh = superq("vo", 52, 58, 44, .4, .6, (-10, 0, 14), 3, .06, body, shell=True)
        xf, _ = front(bvh, 0, 27)
        mk, mb = superq("dau", 11, 36, 17, .6, .75, (xf.x - 2, 0, 27), 12, 0, blk, shell=True)
        for s in (-1, 1):
            p, n = front(mb, s * 14, 31)
            disc("mat-led", 7.2, 3.0, p, n, mat("#D9F7FF", .3, emit=3.0), seg=40)
        pts = []
        for x in range(-56, 36, 4):                                         # duong chia canh
            p, _ = top(bvh, x, 0)
            if p:
                pts.append((x, 0, p.z + .3))
        tube("chia-canh", pts, 1.0, blk)
        for x, y in ((-44, 30), (-44, -30), (-22, 44), (-22, -44), (12, 38), (12, -38)):  # cham lung
            p, n = top(bvh, x, y)
            if p:
                disc("cham", 7, 2.4, p, n, blk, emb=.5, seg=32)
        p, _ = top(bvh, -12, 0)
        cyl("nut-de", 20, 5, (-12, 0, p.z - 1.0), blk, rb=1.0, seg=48)
        cyl("nut-dung", 14, 7, (-12, 0, p.z + 4.0), mat(RED, .3), rb=2.6, seg=48)
        p, n = top(bvh, -46, 0)
        disc("nhan-den", 11, 2.6, p, n, blk, emb=.4, seg=40)
        disc("nhan-mau", 7.2, 3.2, p, n, mat(team, .38), emb=.3, seg=40)
        mark()
        wheels()
        internals()

    def concept_c(team):
        """Cu con = concept C card-coding-robot + nut Dung do tren noc + nhan mau. Doi so voi ban cu: than thap 5 mm de nut
        khong vuot 100 mm; canh = trang (bo nut Chay/Xoa); mo/chan DEN (<=3 mau)."""
        body, wht, blk = mat(team, .4, shell=True), mat(WHITE, .45, shell=True), mat(BLACK, .5, shell=True)
        sh, bvh = superq("vo", 56, 56, 41, .3, .6, (-4, 0, 44), 3, .34, body, shell=True)
        p, n = front(bvh, 0, 34)
        superq("bung", 5, 26, 19, 1, 1, (p.x - 1.2, 0, 32), 0, 0, mat(WHITE, .45, shell=True), nu=48, nv=24)
        for z in (39, 31, 23):                                              # khe loa chu V
            pts = [(p.x + 3.6, t * 2.0, z - abs(t * 2.0) * .45) for t in range(-6, 7)]
            tube("long", pts, 1.1, mat(team, .5, shell=True))
        for s in (-1, 1):
            q, n = front(bvh, s * 18.5, 63)
            disc("mat-vong", 16, 3, q, n, wht, seg=56)
            disc("mat-den", 10.5, 4, q + Vector(n) * .7, n, blk, seg=48)
            disc("mat-led", 5.2, 4.4, q + Vector(n) * 1.1, n, mat("#D9F7FF", .3, emit=3.2), seg=40)
        q, n = front(bvh, 0, 52)
        beak = cyl("mo", 8.5, 12, tuple(q + Vector((5.5, 0, 0))), blk, axis="x", rb=1.0, seg=3, r2=1.5)
        beak.rotation_euler = (0, math.radians(90), 0)
        for s in (-1, 1):
            cyl("chan", 7, 5, (q.x - 3, s * 15, 6), blk, rb=1.6)
        for s in (-1, 1):                                                   # canh trang tri
            q2, _ = hit(bvh, (-8, s * 300, 44), (0, -s, 0))
            ob, _ = superq("canh", 11, 6, 20, 1, 1, (0, 0, 0), -999, 0, wht, nu=56, nv=32)
            ob.location = (-8, q2.y + s * 1.5, 44)
            ob.rotation_euler = (math.radians(-s * 10), 0, 0)
        for s in (-1, 1):                                                   # tai coc
            p2, _ = top(bvh, 26, s * 27)
            c = cyl("tai", 7.5, 12, (26, s * 28, p2.z + 3.6), body, rb=.6, seg=24, r2=2.5)
            c.rotation_euler = (math.radians(-s * 12), math.radians(-8), 0)
        p, _ = top(bvh, -8, 0)
        stop_button(-8, 0, p.z - .6, 19)
        p, n = top(bvh, -42, 0)
        disc("nhan-den", 11, 2.6, p, n, blk, emb=.4, seg=40)
        disc("nhan-mau", 7.2, 3.2, p, n, mat(team, .38), emb=.3, seg=40)
        mark()
        wheels()
        internals()

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

    def bbox():
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in ROBOT for c in o.bound_box]
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        return lo, hi

    def scene(k, team):
        reset()
        floor()
        tile(0, 0)
        tile(150, 0, alt=True)
        hand()
        PRE.clear()
        PRE.update(o.name for o in bpy.data.objects)
        BUILD[k](team)

    def render_concept(k, only_alt=False):
        scene(k, RED)
        lo, hi = bbox()
        dims = {"x0": lo[0], "x1": hi[0], "y0": lo[1], "y1": hi[1], "z1": hi[2],
                "dai": hi[0] - lo[0], "rong": hi[1] - lo[1], "cao": hi[2]}
        print("DIMS", k, json.dumps({a: round(b, 1) for a, b in dims.items()}))
        for v in ("hong", "dinh", "3-4"):
            shot(OUT / f"concept-{k}-{v}.png", v)
        xray(True)
        shot(OUT / f"concept-{k}-trong.png", "trong")
        scene(k, BLUE)
        shot(OUT / f"concept-{k}-3-4-xanh.png", "3-4")
        return dims


# ------------------------------------------------------------------ PIL ----
INK, PINE, MIST = "#16231D", "#1E5A45", "#ECF1EF"
NOTE = {
    "a": ("A – Xe hộp mặt cười", "khuyến nghị"),
    "b": ("B – Bọ rùa", ""),
    "c": ("C – Cú con (+ nút Dừng, nhãn màu)", ""),
}
CMF = {
    "a": [("Thân + cabin + ô nhãn tên xe", "Đỏ / Xanh dương", "Red / Blue", RED),
          ("Kính-mặt, cản, viền hông, nền nhãn", "Đen", "Black", BLACK),
          ("Nắp khuếch tán mắt LED, vòng nút Dừng", "Trắng", "White", WHITE),
          ("Nút Dừng (điểm nhấn, luôn đỏ)", "Đỏ", "Red", RED)],
    "b": [("Vòm thân + nhãn tên xe", "Đỏ / Xanh dương", "Red / Blue", RED),
          ("Đầu, chấm lưng, đường chia cánh, đế nút", "Đen", "Black", BLACK),
          ("Nắp khuếch tán mắt LED (mỏng 0,8 mm)", "Trắng", "White", WHITE),
          ("Nút Dừng (điểm nhấn, luôn đỏ)", "Đỏ", "Red", RED)],
    "c": [("Thân, tai, nhãn tên xe", "Đỏ / Xanh dương", "Red / Blue", RED),
          ("Mỏ, chân, mắt đen, nền nhãn", "Đen", "Black", BLACK),
          ("Bụng, vòng mắt, cánh, vòng nút Dừng", "Trắng", "White", WHITE),
          ("Nút Dừng (điểm nhấn, luôn đỏ)", "Đỏ", "Red", RED)],
}


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
        hline(80, 202, yz(-3) + 38, "bàn tay bé 6 tuổi ≈ 120 mm", above=False)
    else:
        yy = lambda y: 400 - y * S
        hline(-75, 75, yy(75) - 22, "ô thảm 150 mm")
        hline(dm["x0"], dm["x1"], yy(-75) + 24, "xe %.0f × %.0f mm" % (dm["dai"], dm["rong"]), above=False)
        hline(80, 202, yy(-75) + 24, "bàn tay bé 6 tuổi ≈ 120 mm", above=False)
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


def build_pngs():
    from PIL import Image, ImageDraw
    dims = json.loads((OUT / "dims.json").read_text())
    for k in "abc":
        for v in ("hong", "dinh"):
            p = OUT / ("concept-%s-%s.png" % (k, v))
            _annotate(Image.open(p).convert("RGB"), v, dims[k]).save(p)
    W, colw = 3050, 1010
    cm = Image.new("RGB", (W, 760), MIST)
    d = ImageDraw.Draw(cm)
    d.rectangle([0, 0, W, 8], fill=PINE)
    d.text((16, 22), "block-coding-car – CMF (màu · vật liệu · bề mặt) – bản robot-đỏ và robot-xanh",
           font=_font("Bold", 36), fill=INK)
    y = 90
    for i, k in enumerate("abc"):
        x = 20 + i * colw
        d.rounded_rectangle([x, y, x + colw - 30, y + 640], 16, fill="white", outline="#C8D4CE", width=2)
        d.text((x + 20, y + 12), NOTE[k][0] + ("  [khuyến nghị]" if NOTE[k][1] else ""), font=_font("Bold", 28), fill=INK)
        for j, f in enumerate(("3-4", "3-4-xanh")):
            th = Image.open(OUT / ("concept-%s-%s.png" % (k, f))).convert("RGB").crop((100, 60, 900, 640)).resize((300, 218))
            d.text((x + 20 + j * 310, y + 52), "robot-đỏ" if j == 0 else "robot-xanh", font=_font("SemiBold", 18), fill=PINE)
            cm.paste(th, (x + 20 + j * 310, y + 76))
        yy = y + 310
        for part, vn, en, hexc in CMF[k]:
            d.rounded_rectangle([x + 20, yy, x + 80, yy + 50], 10, fill=hexc, outline="#9AA8A1", width=2)
            if "Xanh" in vn:
                d.polygon([(x + 80, yy), (x + 80, yy + 50), (x + 50, yy + 50)], fill=BLUE)
            d.text((x + 94, yy - 2), part, font=_font("SemiBold", 21), fill=INK)
            d.text((x + 94, yy + 25), "%s – Bambu PETG Basic %s" % (vn, en), font=_font("Regular", 18), fill=INK)
            yy += 62
        for n in ("Đỏ + Đen + Trắng = 3 cuộn; bản xanh thay thân bằng Xanh dương, nút Dừng vẫn đỏ (thêm 1 cuộn nhỏ).",
                  "Mỗi part đơn sắc rồi ráp lại (hạn chế AMS). Mặt dưới in trên Textured PEI.",
                  "Mắt LED: nắp khuếch tán trắng mỏng 0,8 mm (TODO thử ánh sáng). Tên màu hãng: TODO xác nhận khi mua cuộn."):
            yy = _wrap(d, x + 20, yy + 4, "• " + n, _font("Regular", 17), colw - 80, 22)
    cm.save(HERE / "cmf.png")
    print("OK", HERE / "cmf.png")


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
    dims = {}
    for k in "abc":
        if only and only != k:
            continue
        dims[k] = render_concept(k)
    p = OUT / "dims.json"
    old = json.loads(p.read_text()) if p.exists() else {}
    old.update(dims)
    old["noi_that_uoc_luong"] = {
        "ghi_chu": "UOC LUONG, TODO do bo that; chua co datasheet/do thuc",
        "esp32_s3_devkit": "65 x 26 x ~13 mm (PCB + header)", "uln2003_x2": "35 x 31 x 9 mm moi tam",
        "hop_4xAA": "58 x 62 x 16 mm, z 5..21", "28BYJ-48": "than O28 x 19, tam banh y=+-40 z=20 x=20",
        "banh": "O40 x 7 giau trong than", "bi_do": "O10 phia sau x=-57 (TODO vi tri/trong tam)"}
    old["gioi_han"] = "120 x 120 x 100 mm"
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
