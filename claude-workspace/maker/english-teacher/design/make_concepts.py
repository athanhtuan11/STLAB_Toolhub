"""english-teacher - buoc 0 giao dien: 3 concept dang san pham (Blender 5.2, Cycles).

Chay (Python thuong, khong can bpy):
    python make_concepts.py all            # 3 concept x (hero, back, 4 trang thai) -> concepts/*.png
    python make_concepts.py a              # chi concept A (a|b|c)
    python make_concepts.py a --samples 24 --scale 0.5   # ban nhap nhanh
Roi: python make_sheet.py  -> contact-sheet.png

Don vi trong file: mm (doi sang m khi tao). Mat truoc = -Y, +Z len tren.
Kich thuoc bo Audio Kit/loa la GIA DINH (xem design-spec.md): chi dung de kiem khoang chua, khong ve bo.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'concepts')
BLENDER = os.environ.get('BLENDER', r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')

# ------------------------------------------------------------------ BANG MAU CMF (hex render; cuon that: TODO)
PAL = {
    'a': dict(body='#F6BE9A', cream='#FFF3DF', accent='#FFC857', dark='#4A3F4F'),   # Cu Bong: mo / kem / bo
    'b': dict(body='#BFE6D5', cream='#FFF3E2', accent='#FF8F85', dark='#27364A'),   # Trung Bi: bac ha / kem / san ho
    'c': dict(body='#D7C6F3', cream='#FFF3DF', accent='#FF9DBB', band='#FFDF86', dark='#4A3F4F'),  # Ban Tai Nghe
}
STATE_COL = {'listen': '#4FC3F7', 'speak': '#FFC83D', 'praise': '#FF7FB0', 'sleep': '#A99BE0'}
STATE_STR = {'listen': 1.3, 'speak': 1.3, 'praise': 1.3, 'sleep': 0.3}
STATES = ['listen', 'speak', 'praise', 'sleep']

try:
    import bpy
    import bmesh
    from mathutils import Vector
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False

M = 0.001


def hexc(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c]
    return (lin[0], lin[1], lin[2], 1.0)


# ================================================================== helpers bpy
def mat(name, color, rough=0.5, emit=None, strength=0.0, coat=0.0, sss=0.0, trans=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = hexc(color)
    b.inputs['Roughness'].default_value = rough
    for k, v in (('Coat Weight', coat), ('Subsurface Weight', sss), ('Transmission Weight', trans)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    if sss > 0 and 'Subsurface Radius' in b.inputs:
        b.inputs['Subsurface Radius'].default_value = (0.01, 0.006, 0.004)
    if emit:
        b.inputs['Emission Color'].default_value = hexc(emit)
        b.inputs['Emission Strength'].default_value = strength
    return m


def set_emit(m, color, strength):
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = hexc(color)
    b.inputs['Emission Strength'].default_value = strength
    if True:
        b.inputs['Base Color'].default_value = hexc(color)


def link(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)
    return obj


def blob(name, m, c, radii, n_top=2.0, n_bot=2.0, taper=0.0, rot=(0, 0, 0), seg=72, rings=36):
    """Mat cau bien dang (superellipsoid) - tam c (mm), ban kinh radii (mm). n>2: day/dinh phang hon."""
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    except TypeError:
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, diameter=1.0)
    for v in bm.verts:
        x, y, z = v.co
        n = n_top if z >= 0 else n_bot
        ln = math.hypot(x, y)
        nl = ln ** (2.0 / n) if ln > 1e-9 else 0.0
        nz = math.copysign(abs(z) ** (2.0 / n), z)
        f = (nl / ln) if ln > 1e-9 else 0.0
        s = 1.0 - taper * nz
        v.co = Vector((x * f * radii[0] * s, y * f * radii[1] * s, nz * radii[2])) * M
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    o.location = tuple(k * M for k in c)
    link(o, m)
    return o


def surf(obj, x, z, direction=(0, 1, 0), origin_y=None):
    """Ray cast vao vat the: (x, z) mm [tren xuong: (x, y)]. Tra ve (diem mm the gioi, phap tuyen)."""
    d = Vector(direction)
    if d.z != 0:
        o = Vector((x * M, z * M, 0.6))
    else:
        o = Vector((x * M, -0.5 if d.y > 0 else 0.5, z * M))
    inv = obj.matrix_basis.inverted()
    ok, loc, nor, _ = obj.ray_cast(inv @ o, (inv.to_3x3() @ d).normalized())
    if not ok:
        raise RuntimeError('ray miss %s %s %s' % (obj.name, x, z))
    wl = obj.matrix_basis @ loc
    wn = (obj.matrix_basis.to_3x3() @ nor).normalized()
    return wl / M, wn


def put(o, loc_mm, nor, sink=0.0):
    nor = Vector(nor).normalized()
    o.location = (Vector(loc_mm) - nor * sink) * M
    o.rotation_euler = nor.to_track_quat('Z', 'Y').to_euler()


def dome(name, m, loc_mm, nor, r, h, sink=0.3):
    o = blob(name, m, (0, 0, 0), (r, r, h))
    put(o, loc_mm, nor, sink)
    return o


_HOLE = {}


def hole_obj(name, m, loc_mm, nor, r):
    key = r
    if key not in _HOLE:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=r * M, depth=0.7 * M)
        t = bpy.context.active_object
        _HOLE[key] = t.data
        bpy.data.objects.remove(t)
    o = bpy.data.objects.new(name, _HOLE[key])
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.clear()
    o.data.materials.append(m)
    put(o, loc_mm, nor, -0.05)
    return o


def grille(host, m, cx, cz, R, pitch, r, prefix='grille'):
    """Luoi loa: lo tron do hoa hoang, ban kinh vung R (mm), buoc pitch, lo ban kinh r."""
    n = int((math.pi * R * R) / (pitch * pitch * 0.866))
    ga = math.pi * (3 - math.sqrt(5))
    cnt = 0
    for i in range(n):
        rr = R * math.sqrt((i + 0.5) / n)
        a = i * ga
        p, nor = surf(host, cx + rr * math.cos(a), cz + rr * math.sin(a))
        hole_obj('%s-%d' % (prefix, i), m, p, nor, r)
        cnt += 1
    return cnt


def polyline(name, m, pts_mm, w, closed=False):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = w * 0.5 * M
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts_mm) - 1)
    for i, p in enumerate(pts_mm):
        sp.points[i].co = (p[0] * M, p[1] * M, p[2] * M, 1)
    sp.use_cyclic_u = closed
    o = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(o)
    link(o, m)
    return o


def arc_pts(cx, y, cz, rx, rz, a0, a1, n=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), y,
             cz + rz * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def torus(name, m, loc_mm, major, minor, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major * M, minor_radius=minor * M,
                                     major_segments=64, minor_segments=14)
    o = bpy.context.active_object
    o.name = name
    o.location = tuple(k * M for k in loc_mm)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    bpy.ops.object.shade_smooth()
    link(o, m)
    return o


def box(name, m, c, size, bevel=2.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0] * M, size[1] * M, size[2] * M)
    o.location = tuple(k * M for k in c)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new('bv', 'BEVEL')
    bv.width = bevel * M
    bv.segments = 4
    bpy.ops.object.shade_smooth()
    link(o, m)
    return o


def cylinder(name, m, c, r, h, bevel=2.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=r * M, depth=h * M)
    o = bpy.context.active_object
    o.name = name
    o.location = tuple(k * M for k in c)
    bv = o.modifiers.new('bv', 'BEVEL')
    bv.width = bevel * M
    bv.segments = 4
    bpy.ops.object.shade_smooth()
    link(o, m)
    return o


# ================================================================== BO PHAN CHUNG (back: USB + khe thoat nhiet)
def back_features(host, zc_usb, zc_vent, dark, vent_w=34):
    p, nor = surf(host, 0, zc_usb, direction=(0, -1, 0))
    o = blob('usb', dark, (0, 0, 0), (7.5, 1.2, 4.0), n_top=4, n_bot=4)
    put(o, p, nor, -0.2)
    for i in range(5):                                  # 5 khe thoat nhiet 18 x 2 mm
        x = (i - 2) * 7.0
        p, nor = surf(host, x, zc_vent, direction=(0, -1, 0))
        o = blob('vent-%d' % i, dark, (0, 0, 0), (1.0, 0.9, 9.0), n_top=4, n_bot=4)
        put(o, p, nor, -0.1)


# ================================================================== CONCEPT A: CU BONG
def build_a(P):
    mb = mat('body', P['body'], 0.55, sss=0.15)
    mc = mat('cream', P['cream'], 0.5, sss=0.1)
    ma = mat('accent', P['accent'], 0.4, sss=0.1)
    md = mat('dark', P['dark'], 0.8)
    glow = mat('eye', '#FFFFFF', 0.3, emit='#FFFFFF', strength=3)
    body = blob('body', mb, (0, 0, 80), (66, 56, 80), n_top=2.2, n_bot=4.2, taper=0.05)
    for s in (-1, 1):
        blob('ear%d' % s, mb, (s * 44, 0, 150), (17, 15, 26), n_top=2, n_bot=2, rot=(0, s * 24, 0))
        blob('wing%d' % s, mb, (s * 60, 8, 78), (11, 26, 36), rot=(0, s * 8, 0))
        p, nor = surf(body, s * 31, 108)
        ring = blob('ring%d' % s, mc, (0, 0, 0), (27, 27, 5))
        put(ring, p, nor, 1.5)
        eye = blob('eye%d' % s, glow, (0, 0, 0), (17, 17, 4))
        put(eye, p, nor, -1.5)
    p, nor = surf(body, 0, 92)
    beak = blob('beak', ma, (0, 0, 0), (9, 9, 13))
    put(beak, p, nor, -2.0)
    beak.rotation_euler.x += math.radians(18)
    plate = blob('belly', mc, (0, -46, 54), (47, 14, 44), n_top=2.4, n_bot=2.4)
    cnt = grille(plate, md, 0, 54, 26, 5.6, 1.4)
    for dx, dz in ((-9, 132), (0, 134), (9, 132)):      # 3 lo micro
        p, nor = surf(body, dx, dz)
        hole_obj('mic', md, p, nor, 1.0)
    p, nor = surf(body, 0, 0, direction=(0, 0, -1))
    top = Vector(p)
    btn = dome('button', ma, top, nor, 25, 12, sink=3.0)
    torus('btn-groove', md, (0, top.y, top.z - 1.2), 26, 0.9)
    back_features(body, 24, 82, md)
    return dict(body=body, glow=glow, rings=[], extra={})


def state_a(h, st):
    set_emit(h['glow'], STATE_COL[st], STATE_STR[st])


# ================================================================== CONCEPT B: TRUNG BI (co man hinh)
def build_b(P):
    mb = mat('body', P['body'], 0.45, coat=0.15, sss=0.1)
    mc = mat('cream', P['cream'], 0.5, sss=0.1)
    ma = mat('accent', P['accent'], 0.4, sss=0.1)
    md = mat('dark', '#3C4A5E', 0.8)
    mbez = mat('bezel', P['dark'], 0.3, coat=0.5)
    mscr = mat('screen', '#0B0F14', 0.12, coat=1.0)
    egg = blob('egg', mb, (0, 0, 90), (62, 57, 78), n_top=2.0, n_bot=3.6, taper=0.10)
    blob('plinth', mc, (0, 0, 13), (64, 59, 14), n_top=4, n_bot=4)
    for s in (-1, 1):
        blob('arm%d' % s, mc, (s * 63, 2, 82), (10, 17, 25), rot=(0, s * 8, 0))
    p, nor = surf(egg, 0, 104)
    vis = blob('visor', mbez, (0, p.y + 4, 104), (40, 11, 31), n_top=2.6, n_bot=2.6)
    sp, sn = surf(vis, 0, 104)
    win = box('window', mscr, (0, sp.y + 0.8, 104), (49.0, 3, 37.0), bevel=3.0)
    fy = sp.y - 0.6                                     # y ve khuon mat
    mem = {}
    def emat(n):
        return mat(n, '#FFFFFF', 0.3, emit='#FFFFFF', strength=1.3)
    f = {k: [] for k in STATES}
    ml = emat('face-listen'); mspk = emat('face-speak'); mpr = emat('face-praise'); mz = emat('face-sleep')
    for col, m_ in ((STATE_COL['listen'], ml), (STATE_COL['speak'], mspk), (STATE_COL['praise'], mpr), (STATE_COL['sleep'], mz)):
        set_emit(m_, col, 1.5 if col != STATE_COL['sleep'] else 0.35)
    ez = 106
    for s in (-1, 1):
        # nghe: mat to tron
        e = blob('l-eye%d' % s, ml, (s * 14, fy, ez), (6.5, 1.0, 8.0)); f['listen'].append(e)
        # noi: mat tron + mieng o
        e = blob('s-eye%d' % s, mspk, (s * 14, fy, ez + 1), (5.5, 1.0, 6.5)); f['speak'].append(e)
        # khen: mat cuoi ^ ^ + ma hong
        e = polyline('p-eye%d' % s, mpr, arc_pts(s * 14, fy, ez - 3, 6.5, 6.5, 30, 150), 2.6); f['praise'].append(e)
        e = blob('p-chk%d' % s, mpr, (s * 21, fy, ez - 11), (4.0, 0.8, 2.4)); f['praise'].append(e)
        # ngu: mat nham u
        e = polyline('z-eye%d' % s, mz, arc_pts(s * 14, fy, ez + 2, 6.5, 4.5, 210, 330), 2.2); f['sleep'].append(e)
    f['speak'].append(blob('s-mouth', mspk, (0, fy, ez - 13), (6.0, 1.0, 3.8)))
    f['listen'].append(polyline('l-mouth', ml, arc_pts(0, fy, ez - 12, 4.0, 3.0, 200, 340, 12), 1.8))
    f['praise'].append(polyline('p-mouth', mpr, arc_pts(0, fy, ez - 8, 7.0, 6.0, 215, 325, 16), 2.2))
    f['sleep'].append(polyline('z-z1', mz, [(18, fy, 118), (24, fy, 118), (18, fy, 112), (24, fy, 112)], 1.4))
    f['sleep'].append(polyline('z-mouth', mz, arc_pts(0, fy, ez - 11, 3.0, 1.5, 200, 340, 8), 1.4))
    grille(egg, md, 0, 52, 26, 5.6, 1.4)
    for dx in (-9, 0, 9):
        p, nor = surf(egg, dx, 142)
        hole_obj('mic', md, p, nor, 1.0)
    p, nor = surf(egg, 0, 0, direction=(0, 0, -1))
    top = Vector(p)
    dome('button', ma, top, nor, 25, 12, sink=3.0)
    torus('btn-groove', md, (0, top.y, top.z - 1.2), 26, 0.9)
    back_features(egg, 26, 90, md)
    return dict(body=egg, face=f, extra={})


def state_b(h, st):
    for k, objs in h['face'].items():
        for o in objs:
            o.hide_render = (k != st)


# ================================================================== CONCEPT C: BAN TAI NGHE
def build_c(P):
    mb = mat('body', P['body'], 0.55, sss=0.15)
    mc = mat('cream', P['cream'], 0.5, sss=0.1)
    ma = mat('accent', P['accent'], 0.4, sss=0.1)
    mh = mat('band', P['band'], 0.45, sss=0.1)
    md = mat('dark', P['dark'], 0.8)
    glow = mat('eye', '#FFFFFF', 0.3, emit='#FFFFFF', strength=3)
    ringm = mat('ring', '#FFFFFF', 0.3, emit='#FFFFFF', strength=3)
    mouthm = mat('mring', '#FFFFFF', 0.3, emit='#FFFFFF', strength=3)
    body = blob('body', mb, (0, 0, 66), (58, 54, 66), n_top=2.0, n_bot=3.6)
    cups = []
    for s in (-1, 1):
        blob('cup%d' % s, mh, (s * 60, 2, 72), (16, 33, 33), n_top=2.4, n_bot=2.4)
        cups.append(torus('cup-ring%d' % s, ringm, (s * (60 + 14.8), 2, 72), 21, 2.6, rot=(0, 90, 0)))
    pts = [(62 * math.cos(math.radians(a)), 6, 64 + 76 * math.sin(math.radians(a))) for a in range(0, 181, 6)]
    polyline('band', mh, pts, 14)
    for s in (-1, 1):
        p, nor = surf(body, s * 22, 88)
        ring = blob('ering%d' % s, mc, (0, 0, 0), (17, 17, 4))
        put(ring, p, nor, 1.2)
        eye = blob('eye%d' % s, glow, (0, 0, 0), (11, 11, 4))
        put(eye, p, nor, -1.2)
    mp = blob('mouthplate', mc, (0, -44, 40), (36, 12, 36), n_top=2.4, n_bot=2.4)
    grille(mp, md, 0, 40, 26, 5.6, 1.4)
    pm, nm = surf(mp, 0, 40)
    pr_, _n = surf(mp, 31.5, 40)
    torus('mouth-ring', mouthm, (0, pr_.y + 0.4, 40), 31.5, 1.7, rot=(90, 0, 0))
    for dx in (-9, 0, 9):
        p, nor = surf(body, dx, 112)
        hole_obj('mic', md, p, nor, 1.0)
    p, nor = surf(body, 0, -12, direction=(0, 0, -1))   # chieu tu tren xuong tai y=-12
    nor = Vector((0, 0, 1))
    top = Vector(p)
    dome('button', ma, top, nor, 25, 12, sink=3.0)
    torus('btn-groove', md, (0, top.y, top.z - 1.2), 26, 0.9)
    back_features(body, 22, 80, md)
    return dict(body=body, glow=glow, ringm=ringm, mouthm=mouthm, cups=cups)


def state_c(h, st):
    c, s = STATE_COL[st], STATE_STR[st]
    set_emit(h['glow'], c, s)
    off = ('#FFF3DF', 0.0)
    set_emit(h['ringm'], *((c, s) if st in ('listen', 'praise') else off))
    set_emit(h['mouthm'], *((c, s) if st in ('speak', 'praise') else off))
    h['cups'][0].hide_render = False
    h['cups'][1].hide_render = False


# ================================================================== CANH, ANH SANG, MAY ANH
def scene_base(res, samples):
    sc = bpy.context.scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.view_settings.exposure = float(os.environ.get('EXPO', '-0.8'))
    sc.display_settings.display_device = 'sRGB'
    try:
        pr = bpy.context.preferences.addons['cycles'].preferences
        for t in ('OPTIX', 'CUDA'):
            try:
                pr.compute_device_type = t
                pr.get_devices()
                devs = [d for d in pr.devices if d.type == t]
                if devs:
                    for d in pr.devices:
                        d.use = (d.type == t)
                    sc.cycles.device = 'GPU'
                    break
            except Exception:
                pass
    except Exception:
        pass
    w = bpy.data.worlds.new('w') if not sc.world else sc.world
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = hexc('#FBF3E8')
    bg.inputs['Strength'].default_value = 0.55
    return sc


def lights():
    def area(name, loc, size, power, color='#FFF6EA'):
        d = bpy.data.lights.new(name, 'AREA')
        d.energy = power
        d.size = size * M
        d.color = hexc(color)[:3]
        o = bpy.data.objects.new(name, d)
        bpy.context.scene.collection.objects.link(o)
        o.location = tuple(k * M for k in loc)
        o.rotation_euler = (-Vector(o.location)).to_track_quat('-Z', 'Y').to_euler()
    area('key', (-420, -520, 520), 600, 6)
    area('fill', (520, -380, 260), 700, 2.2, '#EAF1FF')
    area('rim', (120, 480, 460), 500, 3)


def floor():
    """Phong cong lien (cyclorama): san + goc bo R 0,45 m + tuong."""
    m = mat('floor', '#F8F0E4', 0.9)
    prof = [(-3.0, 0.0), (0.3, 0.0)]
    R = 0.45
    for a in range(0, 91, 10):
        prof.append((0.3 + R * math.sin(math.radians(a)), R - R * math.cos(math.radians(a))))
    prof.append((0.3 + R, 4.0))
    bm = bmesh.new()
    rows = []
    for x in (-5.0, 5.0):
        rows.append([bm.verts.new((x, y, z)) for (y, z) in prof])
    for k in range(len(prof) - 1):
        bm.faces.new((rows[0][k], rows[1][k], rows[1][k + 1], rows[0][k + 1]))
    me = bpy.data.meshes.new('floor')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new('floor', me)
    bpy.context.scene.collection.objects.link(o)
    link(o, m)


def props(width):
    out = []
    mm = mat('mug', '#CFE3F5', 0.25, coat=0.4)
    mug = cylinder('mug', mm, (width / 2 + 62, -30, 47.5), 40, 95, bevel=3)
    h = torus('mug-handle', mm, (width / 2 + 62 + 40, -30, 50), 20, 5.0, rot=(90, 0, 0))
    inner = mat('coffee', '#8B6B4F', 0.3)
    cylinder('mug-in', inner, (width / 2 + 62, -30, 94.5), 35, 1.2, bevel=0.2)
    mk = mat('book', '#FBE3A8', 0.5)
    mp = mat('pages', '#FFFFFF', 0.8)
    bx = -20
    book = box('book', mp, (bx, -175, 6), (200, 200, 12), bevel=1.5, rot=(0, 0, 14))
    cover = box('book-cover', mk, (bx, -175, 12.4), (200, 200, 2.6), bevel=1.2, rot=(0, 0, 14))
    d1 = mat('art1', '#8FD3B6', 0.5)
    d2 = mat('art2', '#F59FB0', 0.5)
    c1 = cylinder('art1', d1, (bx - 6, -171, 14.2), 52, 1.0, bevel=0.3)
    c1.rotation_euler.z = 0
    c2 = cylinder('art2', d2, (bx + 28, -197, 14.6), 24, 1.0, bevel=0.3)
    out += [mug, h, book, cover, c1, c2]
    return [o for o in bpy.data.objects if o.name.startswith(('mug', 'book', 'art', 'coffee'))]


def fit_camera(sc, target_objs, az, el, lens, margin=0.08, pivot=None):
    from bpy_extras.object_utils import world_to_camera_view
    cd = bpy.data.cameras.new('cam')
    cd.lens = lens
    cd.sensor_width = 36
    cam = bpy.data.objects.new('cam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    bpy.context.view_layer.update()
    pts = []
    for o in target_objs:
        if o.hide_render:
            continue
        for c in o.bound_box:
            pts.append(o.matrix_world @ Vector(c))
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    tgt = pivot if pivot else (mn + mx) / 2
    d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)),
                -math.cos(math.radians(az)) * math.cos(math.radians(el)),
                math.sin(math.radians(el))))
    lo, hi = 0.15, 6.0
    for _ in range(30):
        mid = (lo + hi) / 2
        cam.location = tgt + d * mid
        cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.view_layer.update()
        ok = True
        for p in pts:
            v = world_to_camera_view(sc, cam, p)
            if not (margin < v.x < 1 - margin and margin < v.y < 1 - margin):
                ok = False
                break
        if ok:
            hi = mid
        else:
            lo = mid
    cam.location = tgt + d * hi
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    print('CAM', tuple(round(k, 3) for k in cam.location), 'tgt', tuple(round(k, 3) for k in tgt))


def render_to(sc, path):
    sc.render.filepath = path
    sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    print('RENDERED', path)


def run_blender(key, samples, scale, shots=('hero', 'back', 'states')):
    os.makedirs(OUT, exist_ok=True)
    P = PAL[key]
    names = {'a': 'a-cu-bong', 'b': 'b-trung-bi', 'c': 'c-ban-tai-nghe'}
    build = {'a': build_a, 'b': build_b, 'c': build_c}[key]
    stf = {'a': state_a, 'b': state_b, 'c': state_c}[key]
    sc = scene_base((int(1000 * scale), int(1000 * scale)), samples)
    lights()
    floor()
    h = build(P)
    body_objs = [o for o in bpy.data.objects if o.type in ('MESH', 'CURVE') and o.name != 'floor'
                 and not o.name.startswith(('grille', 'mic', 'vent'))]
    pr = props(h['body'].dimensions.x / M if False else {'a': 142, 'b': 126, 'c': 150}[key])
    prop_set = set(pr)
    prod = [o for o in body_objs if o not in prop_set]
    for o in pr:
        o.hide_render = True
    # --- hero: co ly + sach
    movers = [o for o in bpy.data.objects if o.type in ('MESH', 'CURVE') and o.name != 'floor' and o not in prop_set]
    for o in pr:
        o.hide_render = False
    stf(h, 'listen')
    fit_camera(sc, prod + [o for o in pr if o.name.startswith('mug')], -22, 22, 60, margin=0.13)
    if 'hero' in shots:
        render_to(sc, os.path.join(OUT, '%s-hero.png' % names[key]))
    # --- lung (USB + khe nhiet)
    for o in pr:
        o.hide_render = True
    sc.render.resolution_y = int(700 * scale)
    bpy.data.objects.remove(sc.camera)
    for o in movers:                                     # quay san pham 180 do quanh Z de thay mat lung (phong chi co tuong phia sau)
        o.location = (-o.location.x, -o.location.y, o.location.z)
        o.rotation_euler.z += math.pi
    fit_camera(sc, prod, -30, 14, 85, margin=0.08)
    if 'back' in shots:
        render_to(sc, os.path.join(OUT, '%s-back.png' % names[key]))
    for o in movers:
        o.location = (-o.location.x, -o.location.y, o.location.z)
        o.rotation_euler.z -= math.pi
    # --- 4 trang thai
    sc.render.resolution_y = int(720 * scale)
    sc.render.resolution_x = int(720 * scale)
    bpy.data.objects.remove(sc.camera)
    fit_camera(sc, prod, -6, 6, 85, margin=0.10)
    for st in (STATES if 'states' in shots else []):
        stf(h, st)
        render_to(sc, os.path.join(OUT, '%s-state-%s.png' % (names[key], st)))


# ================================================================== DRIVER
if __name__ == '__main__':
    if IN_BLENDER:
        a = sys.argv[sys.argv.index('--') + 1:]
        run_blender(a[0], int(a[1]), float(a[2]), tuple(a[3].split(',')) if len(a) > 3 else ('hero', 'back', 'states'))
    else:
        args = sys.argv[1:]
        which = args[0] if args else 'all'
        samples = int(args[args.index('--samples') + 1]) if '--samples' in args else 96
        scale = float(args[args.index('--scale') + 1]) if '--scale' in args else 1.0
        shots = args[args.index('--shots') + 1] if '--shots' in args else 'hero,back,states'
        keys = 'abc' if which == 'all' else which
        for k in keys:
            subprocess.run([BLENDER, '-b', '-noaudio', '-P', os.path.abspath(__file__), '--', k, str(samples), str(scale), shots],
                           check=True)
