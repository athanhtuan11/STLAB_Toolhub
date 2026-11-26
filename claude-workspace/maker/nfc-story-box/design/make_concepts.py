"""Buoc 0 – Giao dien nfc-story-box: 3 dang hop ke chuyen Cu con (Blender bpy) + the truyen + cmf.png + contact-sheet.png.

  A  Cu tren goc cay – Cu ngoi sau mat goc cay thap, the dat len mat goc cay phia truoc (khuyen nghi cua brief)
  B  Cu om sach      – Cu dung, 2 canh om cuon sach, the dat len trang sach nghieng 15 do
  C  To cu           – To tron, Cu con lo dau o sau, the dat vao long to

Chay (tu claude-workspace):
  python tools/print/scripts/memjob.py 3 -- python maker/nfc-story-box/design/make_concepts.py
Chi mot buoc:  ... make_concepts.py --only render | sheet     (render: Blender nen; sheet: PIL)
Quy uoc: mm (1 BU = 1 mm), mat truoc = -Y, san z=0.
Cac so ben trong (bo 82x73, loa O52x26, module NFC 43x41x5, nut O25+, vung the O60+) la UOC LUONG
(brief.md), chua do bo that – TODO buoc 1; KHONG phai thong so chot.
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
PINE, WHITE, GREEN, LGREEN, YELLOW = "#1E5A45", "#F2F2EE", "#2FA05A", "#3FAE6B", "#E8B33A"
BLACK = "#17191C"
SKIN = "#E9B79A"
BG = "#ECF1EF"
TOP_C, TOP_ORTHO = (-80, -22), 520
CARD_R, CARD_H = 25.0, 5.0       # the truyen O50 x 5
ZONE_R = 34.0                    # vung dat the O68 (>= O60)
TILT = 15.0                      # do nghieng trang sach (B)

# =============================================================== BLENDER ==
if bpy:
    MC = {}
    ALL = []
    PRE = set()

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

    def hit(bvh, o, d):
        r = bvh.ray_cast(Vector(o), Vector(d))
        n = Vector(r[1])
        if n.dot(Vector(d)) > 0:
            n = -n
        return Vector(r[0]), n.normalized()

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

    def wedge(name, pts_yz, x0, x1, m, rb=2.5):
        bm = bmesh.new()
        f = bm.faces.new([bm.verts.new((x0, y, z)) for y, z in pts_yz])
        res = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, verts=[g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)], vec=(x1 - x0, 0, 0))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=rb, segments=3, affect="EDGES")
        return link(name, bm, m, sharp=35)

    def oriented(ob, n):
        n = Vector(n).normalized()
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = n.to_track_quat("Z", "Y")
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
        """Luoi loa (hinh minh hoa): dia den O2r + cham. Loa that O52 x 26 (uoc luong)."""
        nn = Vector(n).normalized()
        ob = cyl(name, r, 2.6, (0, 0, 0), mat("#C5CFC9", .55))
        for i in range(-6, 7):
            for j in range(-6, 7):
                x, y = (i + .5 * (j % 2)) * 5.0, j * 5.0 * .866
                if math.hypot(x, y) < r - 4.5:
                    d = cyl("cham", 1.3, .5, (x, y, 1.3), mat("#3E474D", .5), seg=8)
                    d.parent = ob
                    d.location = (x, y, 1.3)
        ob.location = Vector(c) + nn * (1.3 - .35 * 2.6)
        return oriented(ob, nn)

    # ----------------------------------------------------------- icon nut
    def bar(w, h, t=1.0):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= w; v.co.y *= h; v.co.z *= t
            v.co.z += t / 2
        return bm

    def tri(s, t=1.0):
        bm = bmesh.new()
        f = bm.faces.new([bm.verts.new(p) for p in ((-s * .45, -s * .6, 0), (s * .65, 0, 0), (-s * .45, s * .6, 0))])
        res = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, verts=[g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)], vec=(0, 0, t))
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        return bm

    def put(ob, p, n, spin=0.0):
        """Dat doi tuong (cao tu z=0 len) len be mat tai p, phap tuyen n. Mat tren: spin quanh Z."""
        n = Vector(n).normalized()
        if n.z > .999:
            ob.location = p
            ob.rotation_euler = (0, 0, spin)
        else:
            ob.location = p
            oriented(ob, n)
        return ob

    def button(name, p, n, r, m, kind, icon_m, h=8.0, spin=0.0):
        """Nut tron O2r cao h (loi 0,7h), icon: play / plus / minus (nut >= O25)."""
        n = Vector(n).normalized()
        disc(name, r, h, p, n, m, emb=.3, rb=1.4, seg=56)
        top = Vector(p) + n * (h * .7 + .15)
        sc = r * 0.9
        if kind == "play":
            put(link("play", tri(sc * 1.05), icon_m, sharp=60), top, n, spin)
        else:
            put(link("tru", bar(sc * 1.1, 3.4), icon_m, sharp=60), top, n, spin)
            if kind == "plus":
                put(link("cong", bar(3.4, sc * 1.1), icon_m, sharp=60), top, n, spin)

    # ---------------------------------------------------------------- Cu con
    def owl_face(bvh, ze, zb, dx=19.0, led_h="#FFD98A"):
        """Mat to (vong trang + long den + LED am), mo vang – cung ho Cu Bong / card-coding C."""
        wht, blk = mat(WHITE, .45), mat(BLACK, .5)
        for s in (-1, 1):
            q, n = hit(bvh, (s * dx, -400, ze), (0, 1, 0))
            disc("mat-vong", 16, 3, q, n, wht, seg=56)
            disc("mat-den", 10.5, 4, q + n * .7, n, blk, seg=48)
            disc("mat-led", 5.4, 4.4, q + n * 1.1, n, mat(led_h, .3, emit=3.4), seg=40)
        q, n = hit(bvh, (0, -400, zb), (0, 1, 0))
        cyl("mo", 8, 12, (q.x, q.y - 3.2, zb), mat(YELLOW, .45), axis="y", rb=0, seg=24, r2=1.6)

    def ears(bvh, cy, dx, g, hgt=15):
        for s in (-1, 1):
            q = Vector(bvh.ray_cast(Vector((s * dx, cy, 600)), Vector((0, 0, -1)))[0])
            c = cyl("tai", 8.5, hgt, (s * (dx + 2), cy, q.z + hgt * .28), g, rb=.6, seg=24, r2=2.5)
            c.rotation_euler = (0, math.radians(s * 13), 0)

    def belly(bvh_body, zc, rx, rz, w, ypush=0.0, speaker=True):
        """Bung trang noi + (tuy chon) luoi loa O52 (hinh)."""
        q, n = hit(bvh_body, (0, -400, zc), (0, 1, 0))
        bl, bb = superq("bung", rx, 5.2, rz, 1, 1, (0, q.y + 1.6 + ypush, zc), 0, 0, w, nu=64, nv=32)
        if speaker:
            q2, n2 = hit(bb, (0, -400, zc), (0, 1, 0))
            grille("loa", q2, (0, -1, 0), r=26)
        return bl

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
        box("ban", (30000, 30000, 2), (0, 0, -1.4), mat("#D3DCD8", .9))


    HAND_LEN = 140.0

    def hand(tip_x=-100, yc=-30):
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
        return objs

    def collect():
        ALL[:] = [o for o in bpy.data.objects if o.name not in PRE and o.type in ("MESH", "CURVE", "FONT")]

    # ------------------------------------------------------- the truyen
    THEMES = {
        "rung": ("#3FAE6B", "Rừng xanh"),
        "bien": ("#4C8FD1", "Biển"),
        "trang": ("#2B3A67", "Trăng sao"),
        "trai": ("#E9855E", "Nông trại"),
    }

    def card(theme, p, n=(0, 0, 1), spin=0.0, z_base=None):
        """The O50 x 5 mm, hinh noi 1,2 mm. p = diem tren mat dat the; n = phap tuyen mat."""
        n = Vector(n).normalized()
        base = THEMES[theme][0]
        wht = mat(WHITE, .45)
        ctr = Vector(p) + n * (CARD_H / 2)
        top = Vector(p) + n * CARD_H
        parts = [disc("the", CARD_R, CARD_H, Vector(p) + n * CARD_H * .0, n, mat(base, .42), emb=0.0, rb=1.2, seg=72)]
        loc = Matrix.Translation(top) @ (n.to_track_quat("Z", "Y").to_matrix().to_4x4() if n.z <= .999 else Matrix.Identity(4))
        loc = loc @ Matrix.Rotation(spin, 4, "Z")

        def on(ob, x, y, z=0.0):
            ob.matrix_world = loc @ Matrix.Translation((x, y, z))
            return ob
        # vanh the (gan the, chong tron)
        t = torus("vanh", CARD_R - 3.2, .6, (0, 0, 0), wht)
        on(t, 0, 0, .3)
        if theme == "rung":
            for x, y, s in ((0, 0, 1.0), (-11, 4, .6), (11, 5, .65)):
                c = cyl("cay", 9.5 * s, 1.2, (0, 0, 0), wht, seg=3)
                c.rotation_euler = (0, 0, math.pi / 2)
                on(c, x, y + 1.5, .6)
                on(box("than", (3.2 * s + .8, 5 * s, 1.2), (0, 0, 0), wht, r=.2), x, y - 8.4 * s, .6)
        elif theme == "bien":
            for x, y, r in ((-6, 6, 6.5), (7, -2, 4.5), (-2, -9, 3.2), (12, 10, 2.4)):
                tt = torus("bong-bong", r, .75, (0, 0, 0), wht)
                on(tt, x, y, .6)
        elif theme == "trang":
            on(cyl("trang", 11, 1.2, (0, 0, 0), mat("#F2F2EE", .45), seg=48), -1, 0, .6)
            on(cyl("cat", 9.2, 1.4, (0, 0, 0), mat(base, .42), seg=48), 3.4, 2.4, .7)
            for x, y, r in ((9, 9, 2.4), (13, -4, 1.8), (-12, -10, 2.0)):
                on(cyl("sao", r, 1.2, (0, 0, 0), mat("#F2F2EE", .45), seg=5), x, y, .6)
        elif theme == "trai":
            on(box("nha", (15, 11, 1.4), (0, 0, 0), wht, r=.3), 0, -3.5, .7)
            r = cyl("mai", 9.5, 1.4, (0, 0, 0), mat("#B33A2A", .5), seg=3)
            r.rotation_euler = (0, 0, math.pi / 2)
            on(r, 0, 3.2, .7)
            on(box("cua", (3.4, 5, 1.6), (0, 0, 0), mat(base, .42), r=.2), 0, -6, .8)
        return parts

    # ----------------------------------------------------------- 3 dang
    def zone(cx, cy, z, n=(0, 0, 1)):
        """Vung dat the O68 (dia trang, lom 1,2 mm khi in; render dang noi 0,8 mm) + vach nhan tam."""
        disc("vung-the", ZONE_R, 1.2, (cx, cy, z), n, mat(WHITE, .45), emb=.35, seg=96)

    def logo(font, loc, rot, mt, mk):
        text("STLAB", 8, loc, mt, font, rot=rot)

    def concept_a(font):
        g, pn, w, blk = mat(GREEN, .4), mat(PINE, .42), mat(WHITE, .45), mat(BLACK, .5)
        ycd = -30
        slab("goc-cay", 156, 148, 40, 30, 5, pn, rb=.8)
        zone(0, ycd, 30)
        for R in (14, 24):   # vong nam go nhe (khac 0,8 mm)
            torus("nam", R, .45, (0, ycd, 30.55), mat("#D3D8D3", .6))
        body, bvh = superq("than", 54, 33, 62, .55, .62, (0, 40, 92), 30, .2, g)
        belly(bvh, 72, 36, 30, w)
        owl_face(bvh, 122, 110)
        ears(bvh, 36, 33, g)
        bt = mat(WHITE, .4)
        ic = mat(BLACK, .5)
        button("nut-giam", (-57, -44, 30), (0, 0, 1), 13, bt, "minus", ic)
        button("nut-tang", (-57, -10, 30), (0, 0, 1), 13, bt, "plus", ic)
        button("nut-choi", (57, -30, 30), (0, 0, 1), 16, mat(YELLOW, .38), "play", ic)
        text("STLAB", 8, (-6, -74.2, 14), w, font, rot=(math.pi / 2, 0, 0))
        box("dau-vang", (12, .8, 3.2), (14, -74.2, 14), mat(YELLOW, .4), r=.3)
        card("rung", (0, ycd, 30.8))
        return {"card": (0, ycd, 30.8), "zone_c": (0, ycd), "nut": "3 nút trên mặt gốc cây (− +  ▶)"}

    def concept_b(font):
        g, pn, w = mat(GREEN, .4), mat(PINE, .42), mat(WHITE, .45)
        ic = mat(BLACK, .5)
        slab("de", 150, 148, 40, 10, 3, pn, rb=.8)
        # cuon sach nghieng 15 do
        tn = math.tan(math.radians(TILT))
        z_f = 22.0
        wedge("bia-sach", [(-69, 10), (-69, z_f), (9, z_f + 78 * tn), (9, 10)], -75, 75, pn, rb=2.2)
        zc = z_f + 39 * tn
        O = Vector((0, -30, zc))
        M = Matrix.Translation(O) @ Matrix.Rotation(math.radians(TILT), 4, "X")
        R3 = M.to_3x3()
        nrm = R3 @ Vector((0, 0, 1))
        pg = slab("trang", 144, 74, 8, 3, 0.8, w, rb=0)
        pg.matrix_world = M
        sp_ = box("gay-sach", (1.6, 74, .8), (0, 0, 0), g, r=.2)
        sp_.matrix_world = M @ Matrix.Translation((0, 0, 3.3))
        lip = box("go-chan", (74, 2.6, 3.2), (0, 0, 0), g, r=.5)
        lip.matrix_world = M @ Matrix.Translation((38, -35.6, 4.2))
        dp = M @ Vector((38, 0, 3))
        disc("vung-the", ZONE_R, 1.2, dp, nrm, w, emb=.35, seg=96)
        card("trang", dp + nrm * .8, nrm)
        for i, yy in enumerate((-18, -9, 0, 9, 18)):   # dong chu gia tren trang trai
            lnn = box("dong-chu", (34 - (i % 2) * 6, 1.6, .7), (0, 0, 0), mat("#C9D3CD", .6), r=.2)
            lnn.matrix_world = M @ Matrix.Translation((-38, yy, 3.35))
        button("nut-choi", M @ Vector((-38, 30, 3)) + Vector((0, 0, 0)) if False else M @ Vector((-38, -6, 3)), nrm, 17,
               mat(YELLOW, .38), "play", ic)
        # than cu
        body, bvh = superq("than", 50, 37, 76, .55, .62, (0, 37, 86), 10, .2, g)
        belly(bvh, 90, 36, 30, w)
        owl_face(bvh, 134, 122)
        ears(bvh, 36, 31, g)
        for s in (-1, 1):
            wg, wb = superq("canh", 17, 24, 40, 1, 1, (s * 47, 22, 90), 40, 0, pn, nu=64, nv=40)
            q, n = hit(wb, (s * 47, -400, 92), (0, 1, 0))
            button("nut-tang" if s > 0 else "nut-giam", q, n, 13, w, "plus" if s > 0 else "minus", ic)
        text("STLAB", 8, (-6, -74.2, 5), w, font, rot=(math.pi / 2, 0, 0))
        box("dau-vang", (12, .8, 3.2), (14, -74.2, 5), mat(YELLOW, .4), r=.3)
        return {"card": tuple(dp), "nut": "− + ở hai cánh, ▶ ở trang trái"}

    def concept_c(font):
        g, pn, w = mat(GREEN, .4), mat(PINE, .42), mat(WHITE, .45)
        ic = mat(BLACK, .5)
        zt = 64.0
        slab("to", 154, 146, 42, zt, 9, pn, rb=.8)
        slab("vanh-to", 158, 148, 44, 5, 1.6, mat(LGREEN, .45), z0=54.5, rb=0)
        # vanh to: dai canh nho quanh mep (trang tri, in lien than)
        ycd = -30
        zone(0, ycd, zt)
        torus("go-the", ZONE_R + 1.6, 1.6, (0, ycd, zt + .9), mat("#D3D8D3", .6))
        head, bvh = superq("dau", 52, 36, 44, .55, .62, (0, 36, 94), 56, .08, g)
        owl_face(bvh, 102, 89)
        ears(bvh, 32, 34, g, hgt=14)
        # loa o thanh truoc cua to
        grille("loa", (0, -73.2, 28), (0, -1, 0), r=26)
        button("nut-giam", (-56, -42, zt), (0, 0, 1), 13, w, "minus", ic)
        button("nut-tang", (-56, -8, zt), (0, 0, 1), 13, w, "plus", ic)
        button("nut-choi", (57, -30, zt), (0, 0, 1), 16, mat(YELLOW, .38), "play", ic)
        text("STLAB", 8, (77.2, -22, 30), w, font, rot=(math.pi / 2, 0, math.pi / 2))
        box("dau-vang", (.8, 12, 3.2), (77.2, -4, 30), mat(YELLOW, .4), r=.3)
        card("bien", (0, ycd, zt + .8))
        return {"card": (0, ycd, zt + .8), "nut": "3 nút trên mặt tổ (− +  ▶)"}

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

    def shot(path, view, size=SIZE, samples=48):
        sc = bpy.context.scene
        sc.render.resolution_x, sc.render.resolution_y = size
        eevee = getattr(sc, "eevee", None)
        if eevee is not None and hasattr(eevee, "taa_render_samples"):
            eevee.taa_render_samples = samples
        for o in [o for o in bpy.data.objects if o.type == "CAMERA"]:
            bpy.data.objects.remove(o)
        if view == "dinh":
            camera((TOP_C[0], TOP_C[1], 1000), rot=(0, 0, 0), ortho=TOP_ORTHO)
        elif view == "hong":
            wl = box("ban-tuong", (2, 4000, 2000), (700, 0, 500), mat("#E3EBE7", .95))
            wl.visible_shadow = False
            camera((-1000, 0, 95), target=(0, 0, 95), ortho=340)
        elif view == "the":
            camera((0, 0, 1000), rot=(0, 0, 0), ortho=300)
        elif view == "the-34":
            camera((120, -220, 150), target=(0, 0, 0), lens=45)
        else:
            camera((300, -450, 280), target=(-68, 5, 62), lens=50)
        sc.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)

    def scene(k, with_hand=True):
        reset()
        floor()
        font = bpy.data.fonts.load(str(FONTS / "BeVietnamPro-Bold.ttf"))
        hobjs = hand() if with_hand else []
        PRE.clear()
        PRE.update(o.name for o in bpy.data.objects)
        info = BUILD[k](font)
        collect()
        return info, hobjs

    def bbox():
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in ALL for c in o.bound_box if o.name != "ban"]
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        return lo, hi

    def render_concept(k):
        info, hobjs = scene(k)
        lo, hi = bbox()
        dims = {"rong": hi[0] - lo[0], "sau": hi[1] - lo[1], "cao": hi[2], "de_rong": None,
                "x0": lo[0], "x1": hi[0], "y0": lo[1], "y1": hi[1]}
        base = [o for o in ALL if o.name in ("goc-cay", "de", "to")][0]
        bb = [base.matrix_world @ Vector(c) for c in base.bound_box]
        dims["de_rong"] = max(p.x for p in bb) - min(p.x for p in bb)
        print("DIMS", k, json.dumps({a: (round(b, 1) if b is not None else None) for a, b in dims.items()}))
        shot(OUT / f"concept-{k}-3-4.png", "3-4")
        shot(OUT / f"concept-{k}-dinh.png", "dinh")
        for o in hobjs:
            bpy.data.objects.remove(o)
        shot(OUT / f"concept-{k}-hong.png", "hong")
        dims["ghi_chu_nut"] = info["nut"]
        return dims

    def render_cards():
        reset()
        floor()
        font = bpy.data.fonts.load(str(FONTS / "BeVietnamPro-Bold.ttf"))
        for i, th in enumerate(THEMES):
            card(th, ((i - 1.5) * 62, 0, 0), spin=0)
        shot(OUT / "the-truyen-raw.png", "the", size=(1600, 640))


# ------------------------------------------------------------------ PIL ----
INK, PINEH, MIST = "#16231D", "#1E5A45", "#ECF1EF"
NOTE = {
    "a": "A – Cú trên gốc cây",
    "b": "B – Cú ôm sách",
    "c": "C – Tổ cú",
}
# (dễ đặt thẻ, vững/không lật, dễ in, giống Cú Bông/dễ thương) 0..3
SCORE = {"a": (3, 3, 2, 3), "b": (2, 2, 2, 3), "c": (3, 3, 2, 2)}
CRIT = ("Đặt thẻ dễ (bé 3 tuổi)", "Vững, khó lật", "Dễ in (bàn 256)", "Giống Cú Bông / dễ thương")
PROS = {
    "a": ("Mặt gốc cây phẳng ≥ Ø68, đế 156 × 150 vững nhất; loa ở bụng, anten NFC dưới mặt gốc cách xa loa; nút ở hai bên vùng đọc, dễ thấy.",
          "Đế dài ra phía trước nên tốn nhựa; thân cú chỉ sâu ~66 mm nên hơi dẹt nhìn từ hông; 3 nút trên mặt gốc cây chưa gắn với nhân vật."),
    "b": ("Ý 'đọc sách' rõ nhất, nút nằm trên 2 cánh (tự nhiên, không lẫn với vùng thẻ); trang sách mở là chỗ đặt thẻ hợp lý.",
          "Mặt nghiêng 15° nên thẻ có thể trượt (cần gờ chặn 2,6 mm); thẻ lệch phải, anten lệch tâm; cao 166 mm và nặng phía sau, kém vững hơn."),
    "c": ("Trọng tâm thấp nhất, vùng thẻ lõm giữ thẻ không trượt; loa ở thành tổ nên hướng ra trước, xa anten.",
          "Cú chỉ có đầu nên ít 'nhân vật'; tổ cao 64 mm (loa nằm thành trước) nên thẻ đặt cao hơn bé 3 tuổi mong đợi; nhiều chi tiết vân nếu thêm cành tổ."),
}
CMF = {
    "a": [("Thân cú + tai", "Xanh lá", "Green (Bambu PETG Basic – TODO tên màu hãng)", GREEN),
          ("Gốc cây + vành ngoài", "Xanh thông", "Dark Green (TODO tên màu hãng)", PINE),
          ("Mắt, bụng, vùng đọc thẻ, núm − +", "Trắng", "White", WHITE),
          ("Mỏ, núm Chơi/Dừng, dấu STLAB (điểm nhấn)", "Vàng", "Yellow", YELLOW)],
    "b": [("Thân cú + tai", "Xanh lá", "Green (TODO tên màu hãng)", GREEN),
          ("Đế, bìa sách, 2 cánh", "Xanh thông", "Dark Green (TODO)", PINE),
          ("Mắt, bụng, trang sách, núm cánh", "Trắng", "White", WHITE),
          ("Mỏ, núm Chơi/Dừng, dấu STLAB (điểm nhấn)", "Vàng", "Yellow", YELLOW)],
    "c": [("Đầu cú + tai", "Xanh lá", "Green (TODO tên màu hãng)", GREEN),
          ("Tổ", "Xanh thông", "Dark Green (TODO)", PINE),
          ("Mắt, vùng lõm đọc thẻ, núm − +", "Trắng", "White", WHITE),
          ("Mỏ, núm Chơi/Dừng, dấu STLAB (điểm nhấn)", "Vàng", "Yellow", YELLOW)],
}
GENERIC = ("Mỗi part đơn sắc rồi ráp lại (hạn chế AMS: không in nhiều màu 1 part); mặt đáy in trên Textured PEI, mặt nhìn thấy là mặt in; không support.",
           "Mắt = LED ấm (đang kể): lớp chắn sáng 0,8 mm trắng/trong mờ (TODO thử ánh sáng). Thẻ truyện Ø50 × 5 mm đổi màu theo chủ đề (Rừng, Biển, Trăng sao, Nông trại).",
           "Tối đa 3 màu nhựa (xanh lá, xanh thông, trắng) + 1 điểm nhấn vàng (mỏ, núm Chơi/Dừng, dấu STLAB). Tên màu hãng: TODO xác nhận khi chọn cuộn.")


def _font(w, size):
    from PIL import ImageFont
    return ImageFont.truetype(str(FONTS / ("BeVietnamPro-%s.ttf" % w)), size)


def _arrow_h(d, x0, x1, y, text, fnt, col, above=False):
    d.line([(x0, y), (x1, y)], fill=col, width=2)
    for x in (x0, x1):
        d.line([(x, y - 7), (x, y + 7)], fill=col, width=2)
    w = d.textlength(text, font=fnt)
    d.text(((x0 + x1) / 2 - w / 2, y - 34 if above else y + 8), text, font=fnt, fill=col)


def _annotate_top(im, dm):
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    fb = _font("SemiBold", 34)
    S = 1200 / TOP_ORTHO
    px = lambda x: 600 + (x - TOP_C[0]) * S
    py = lambda y: 400 - (y - TOP_C[1]) * S
    col = (22, 35, 29)
    _arrow_h(d, px(dm["x0"]), px(dm["x1"]), py(dm["y0"]) + 22, "%.0f × %.0f mm" % (dm["rong"], dm["sau"]), fb, col)
    _arrow_h(d, px(-100 - 140), px(-100), py(-30 - 50), "tay bé 140", fb, col)
    return im


def _annotate_side(im, dm):
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    fb = _font("SemiBold", 34)
    S = 1200 / 340
    # nhin tu -X: phai = -Y (mat truoc ben phai)
    px = lambda y: 600 - y * S
    py = lambda z: 400 - (z - 95) * S
    col = (22, 35, 29)
    x = px(dm["y1"]) - 40
    d.line([(x, py(0)), (x, py(dm["cao"]))], fill=col, width=2)
    for z in (0, dm["cao"]):
        d.line([(x - 7, py(z)), (x + 7, py(z))], fill=col, width=2)
    d.text((x - 120, (py(0) + py(dm["cao"])) / 2 - 16), "cao %.0f" % dm["cao"], font=fb, fill=col)
    _arrow_h(d, px(dm["y1"]), px(dm["y0"]), py(0) + 24, "sâu %.0f mm" % dm["sau"], fb, col)
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
    cm = Image.new("RGB", (W, 700), MIST)
    d = ImageDraw.Draw(cm)
    d.rectangle([0, 0, W, 8], fill=PINEH)
    d.text((16, 20), "nfc-story-box – CMF (màu · vật liệu · bề mặt) – Bambu PETG Basic, part đơn sắc ráp lại", font=_font("Bold", 30), fill=INK)
    for i, k in enumerate("abc"):
        x, y = 16 + i * colw, 76
        d.rounded_rectangle([x, y, x + colw - 24, y + 540], 16, fill="white", outline="#C8D4CE", width=2)
        d.text((x + 16, y + 10), NOTE[k], font=_font("Bold", 24), fill=INK)
        th = Image.open(OUT / ("concept-%s-3-4.png" % k)).convert("RGB").crop((260, 60, 960, 700)).resize((260, 238))
        cm.paste(th, (x + 16, y + 48))
        yy = y + 292
        for part, vn, en, hexc in CMF[k]:
            d.rounded_rectangle([x + 16, yy, x + 70, yy + 44], 10, fill=hexc, outline="#9AA8A1", width=2)
            d.text((x + 82, yy - 4), part, font=_font("SemiBold", 17), fill=INK)
            d.text((x + 82, yy + 18), "%s – %s" % (vn, en), font=_font("Regular", 14), fill=INK)
            yy += 52
        d.text((x + 290, y + 56), "Mặt đáy: Textured PEI", font=_font("Regular", 15), fill=INK)
        d.text((x + 290, y + 78), "Mặt thấy: mặt in (mịn)", font=_font("Regular", 15), fill=INK)
    yy = 628
    for g in GENERIC:
        yy = _wrap(d, 16, yy, "• " + g, _font("Regular", 15), W - 40, 19)
    cm.crop((0, 0, W, yy + 4)).save(HERE / "cmf.png")


def build_pngs():
    from PIL import Image, ImageDraw
    dims = json.loads((OUT / "dims.json").read_text(encoding="utf-8"))
    for k in "abc":
        _annotate_top(Image.open(OUT / ("concept-%s-dinh.png" % k)).convert("RGB"), dims[k]).save(OUT / ("concept-%s-dinh-ghi-chu.png" % k))
        _annotate_side(Image.open(OUT / ("concept-%s-hong.png" % k)).convert("RGB"), dims[k]).save(OUT / ("concept-%s-hong-ghi-chu.png" % k))
    # the truyen co nhan
    im = Image.open(OUT / "the-truyen-raw.png").convert("RGB")
    d = ImageDraw.Draw(im)
    S = 1600 / 300
    names = ["Rừng xanh", "Biển", "Trăng sao", "Nông trại"]
    for i, nm in enumerate(names):
        cx = 800 + (i - 1.5) * 62 * S
        w = d.textlength(nm, font=_font("SemiBold", 30))
        d.text((cx - w / 2, 320 + 25 * S + 8 - 40 + 40), nm, font=_font("SemiBold", 30), fill=INK)
    d.text((24, 520), "Thẻ truyện Ø50 × 5 mm · hình nổi 1,2 mm · NTAG213 ép giữa 2 lớp · không lọt ống thử chi tiết nhỏ (TODO tra TCVN 6238 / EN 71-1)",
           font=_font("Regular", 22), fill=INK)
    im = im.crop((0, 120, 1600, 580))
    im.save(OUT / "the-truyen.png")
    build_cmf()
    W = 1200
    cmf = Image.open(HERE / "cmf.png").convert("RGB")
    cmf = cmf.resize((W - 40, int(cmf.height * (W - 40) / cmf.width)))
    cards = Image.open(OUT / "the-truyen.png").convert("RGB")
    cards = cards.resize((W - 40, int(cards.height * (W - 40) / cards.width)))
    ha = 337
    wa, wh, wd = 505, 239, 380
    rowh = ha + 168
    H = 100 + 3 * rowh + cards.height + 20 + cmf.height + 20
    sh = Image.new("RGB", (W, H), MIST)
    d = ImageDraw.Draw(sh)
    d.rectangle([0, 0, W, 8], fill=PINEH)
    d.text((20, 18), "nfc-story-box – 3 dáng hộp kể chuyện Cú con (bước 0 Giao diện)", font=_font("Bold", 32), fill=INK)
    d.text((20, 58), "Bao ≤ 160 × 150 × 190 mm, đế ≥ 130 · bo 82 × 73 · loa Ø52 × 26 · NFC 43 × 41 × 5 (ước lượng, chưa đo) · thẻ Ø50 × 5 · vùng đặt thẻ Ø68 · nút ≥ Ø25 · USB 5 V",
           font=_font("Regular", 15), fill=INK)
    y = 86
    for k in "abc":
        dm = dims[k]
        d.rounded_rectangle([10, y, W - 10, y + rowh - 12], 16, fill="white", outline="#C8D4CE", width=2)
        t = "%s   –   bao %.0f × %.0f × %.0f mm (rộng × sâu × cao), đế %.0f mm" % (NOTE[k], dm["rong"], dm["sau"], dm["cao"], dm["de_rong"])
        if k == "a":
            t += "   [khuyến nghị]"
        d.text((26, y + 8), t, font=_font("Bold", 22), fill=INK)
        a = Image.open(OUT / ("concept-%s-3-4.png" % k)).convert("RGB").crop((190, 90, 1090, 690)).resize((wa, ha))
        b = Image.open(OUT / ("concept-%s-hong-ghi-chu.png" % k)).convert("RGB").crop((330, 0, 870, 760)).resize((wh, ha))
        c = Image.open(OUT / ("concept-%s-dinh-ghi-chu.png" % k)).convert("RGB").crop((190, 70, 1010, 797)).resize((wd, ha))
        sh.paste(a, (22, y + 42))
        sh.paste(b, (22 + wa + 8, y + 42))
        sh.paste(c, (22 + wa + wh + 16, y + 42))
        yy = y + 42 + ha + 6
        for j, cr in enumerate(CRIT):
            x = 26 + j * 292
            d.text((x, yy), cr, font=_font("SemiBold", 14), fill=INK)
            for q in range(3):
                cx = x + 4 + q * 20
                d.ellipse([cx, yy + 22, cx + 13, yy + 35], fill=PINEH if q < SCORE[k][j] else "white", outline=PINEH, width=2)
        yy += 44
        yy = _wrap(d, 26, yy, "Ưu: " + PROS[k][0], _font("Regular", 15), W - 60, 19)
        _wrap(d, 26, yy, "Nhược: " + PROS[k][1], _font("Regular", 15), W - 60, 19)
        y += rowh
    sh.paste(cards, (20, y))
    y += cards.height + 20
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
    old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    for k in "abc":
        if only and only not in (k, "all"):
            continue
        old[k] = render_concept(k)
        p.write_text(json.dumps(old, indent=1, ensure_ascii=False), encoding="utf-8")
    if not only or only in ("the", "all"):
        render_cards()
    old["uoc_luong_ben_trong"] = {
        "bo_a1s_mm": "82 x 73 (datasheet Ai-Thinker; do day, lo vit, cao linh kien TODO do bo that)",
        "loa_mm": "O52 cao 26 (loai Tuan co; TODO xac nhan con hang)",
        "module_nfc_pn532_mm": "43 x 41 x 5 – UOC LUONG, CHUA DO (TODO)",
        "nut_mm": ">= O25 (ve: -/+ O26, Choi/Dung O32-34)",
        "vung_dat_the_mm": ">= O60 (ve: O68)",
        "the_truyen_mm": "O50 x 5",
        "gioi_han_bao_mm": "<= 160 x 150 x 190, de rong >= 130",
    }
    old["ghi_chu"] = ("Kich thuoc bao la kich thuoc dung trong ban ve minh hoa (bbox, khong gom ban tay/ban). "
                      "Moi thong so ben trong chi la uoc luong tu brief.md – chua do bo/loa/NFC that.")
    p.write_text(json.dumps(old, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    if bpy:
        blender_entry()
    else:
        only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
        if only in (None, "render"):
            run_blender()
        if only in (None, "sheet"):
            build_pngs()
