"""english-teacher - A2 Cu Bong co man TFT 2,8" cam ung (thay 2 vanh mat LED). Dung lai ham cua make_concepts.py.

Chay (Python thuong):
    python make_screen_concepts.py            # 2 phuong an (v1 mo duoi man, v2 mo chong mep duoi vien)
    python make_screen_concepts.py --samples 24 --scale 0.5
Roi: python make_sheet_screen.py -> contact-sheet-screen.png
Kich thuoc man: LCDWiki MSP2807 (PCB 50 x 86, vung hien thi 43,2 x 57,6 mm, dat NGANG). Day tong the/lo bat: TODO.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_concepts as mc  # noqa: E402

BLENDER = mc.BLENDER
OUT = mc.OUT
M = 0.001

if mc.IN_BLENDER:
    import bpy
    from mathutils import Matrix, Vector

# --- so lieu (mm)
DISP_W, DISP_H = 57.6, 43.2          # vung hien thi (LCDWiki)
OPEN_W, OPEN_H = DISP_W + 0.8, DISP_H + 0.8   # cua so vien: hien thi + 0,4/ben
GLASS_W, GLASS_H = 62.0, 47.0         # o giu cho kinh (TODO do that): vien de len kinh >= 1,5 ben
PLATE_W, PLATE_H, PLATE_T = 94.0, 58.0, 26.0  # "dia mat" kem: PCB 86 x 50 + thanh >= 3,5 ben
PROUD = 4.0                            # mat vien nho khoi be mat than o tam
RECESS = 1.0                           # mat kinh lui so voi mat vien

VAR = {
    'v1': dict(zc=112, zb=42, rzb=34, mic=148, beak='below'),
    'v2': dict(zc=104, zb=48, rzb=33, mic=141, beak='overlap'),
}


def frame(name, p, nor):
    nor = Vector(nor).normalized()
    x = Vector((1, 0, 0))
    x = (x - nor * x.dot(nor)).normalized()
    y = nor.cross(x)
    rot = Matrix((x, y, nor)).transposed()
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.matrix_world = Matrix.Translation(Vector(p) * M) @ rot.to_4x4()
    return e


def kid(o, parent):
    o.parent = parent
    return o


def arc_loc(cx, cy, rx, ry, a0, a1, zl, n=20):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)), zl) for i in range(n + 1)]


def emat(name, col, s):
    m = mc.mat(name, '#FFFFFF', 0.3, emit='#FFFFFF', strength=1.0)
    mc.set_emit(m, col, s)
    return m


def disc(name, m, x, y, r, z, rx=None, ry=None, h=0.3):
    return mc.blob(name, m, (x, y, z), (rx or r, ry or r, h), n_top=6, n_bot=6, seg=48, rings=12)


def build(var):
    cfg = VAR[var]
    P = mc.PAL['a']
    mb = mc.mat('body', P['body'], 0.55, sss=0.15)
    mcr = mc.mat('cream', P['cream'], 0.5, sss=0.1)
    ma = mc.mat('accent', P['accent'], 0.4, sss=0.1)
    md = mc.mat('dark', P['dark'], 0.8)
    glass = mc.mat('glass', '#0A0F18', 0.1, coat=1.0, emit='#0B1424', strength=0.5)
    pupil = mc.mat('pupil', '#14203A', 0.3)
    white = emat('hl', '#FFFFFF', 2.5)
    body = mc.blob('body', mb, (0, 0, 80), (66, 56, 80), n_top=3.4, n_bot=4.2, taper=0.05)
    for s in (-1, 1):
        mc.blob('ear%d' % s, mb, (s * 44, 0, 150), (17, 15, 26), n_top=2, n_bot=2, rot=(0, s * 24, 0))
        mc.blob('wing%d' % s, mb, (s * 60, 8, 78), (11, 26, 36), rot=(0, s * 8, 0))
    # ---- man hinh
    p, nor = mc.surf(body, 0, cfg['zc'])
    fr = frame('screen-frame', p, nor)
    plate = kid(mc.box('plate', mcr, (0, 0, PROUD - PLATE_T / 2), (PLATE_W, PLATE_H, PLATE_T), bevel=12.0), fr)
    cut = kid(mc.box('cut', md, (0, 0, 2.5), (OPEN_W, OPEN_H, 8), bevel=2.5), fr)
    cut.hide_render = True
    bm = plate.modifiers.new('open', 'BOOLEAN')
    bm.operation = 'DIFFERENCE'
    bm.object = cut
    bm.solver = 'EXACT'
    kid(mc.box('glass', glass, (0, 0, PROUD - RECESS - 1.0), (GLASS_W, GLASS_H, 2.0), bevel=1.0), fr)
    zf = PROUD - RECESS + 0.1          # mat kinh (local z)
    f = {k: [] for k in mc.STATES}

    def add(st, o):
        kid(o, fr)
        f[st].append(o)

    ex, er = 15.0, 13.5
    for s in (-1, 1):
        # nghe: mat to xanh, con ngươi, diem sang + vong "dang nghe"
        m = emat('l-eye', mc.STATE_COL['listen'], 1.6)
        add('listen', disc('l-eye%d' % s, m, s * ex, 0, er, zf + 0.3))
        add('listen', disc('l-pup%d' % s, pupil, s * ex, -1, 6.6, zf + 0.7))
        add('listen', disc('l-hl%d' % s, white, s * ex + 3.2, 3.5, 2.4, zf + 1.1))
        add('listen', mc.polyline('l-ring%d' % s, m, arc_loc(s * ex, 0, er + 1.6, er + 1.6, 20, 160, zf + 0.3, 20), 0.9))
        # noi: mat vang tron hoi cao, con ngươi to, 2 dau cham "am thanh"
        m = emat('s-eye', mc.STATE_COL['speak'], 1.6)
        add('speak', disc('s-eye%d' % s, m, s * ex, 1, 0, zf + 0.3, rx=12.0, ry=14.0))
        add('speak', disc('s-pup%d' % s, pupil, s * ex, 0, 0, zf + 0.7, rx=6.8, ry=8.0))
        add('speak', disc('s-hl%d' % s, white, s * ex + 3.0, 5, 2.4, zf + 1.1))
        # khen: mat cuoi ^ ^ + ma hong + lap lanh
        m = emat('p-eye', mc.STATE_COL['praise'], 1.6)
        add('praise', mc.polyline('p-eye%d' % s, m, arc_loc(s * ex, -5, 10, 11, 25, 155, zf + 0.4), 3.4))
        add('praise', disc('p-chk%d' % s, m, s * 22.5, -11, 0, zf + 0.3, rx=4.2, ry=2.4))
        # ngu: mat nham u, tim mo
        m = emat('z-eye', mc.STATE_COL['sleep'], 0.35)
        add('sleep', mc.polyline('z-eye%d' % s, m, arc_loc(s * ex, 3, 10, 6.5, 205, 335, zf + 0.4), 2.6))
    m = emat('p-sp', mc.STATE_COL['praise'], 1.6)
    for (sx, sy, sr) in ((0, 12, 3.2), (-27 + 3, 16, 2.0), (24, 15, 2.2)):
        pts = []
        for i in range(8):
            a = math.pi * i / 4
            rr = sr if i % 2 == 0 else sr * 0.3
            pts.append((sx + rr * math.sin(a), sy + rr * math.cos(a), zf + 0.4))
        pts.append(pts[0])
        add('praise', mc.polyline('p-star', m, pts, 0.6, True))
    m = emat('z-z', mc.STATE_COL['sleep'], 0.35)
    add('sleep', mc.polyline('z-z1', m, [(14, 7, zf + .4), (20, 7, zf + .4), (14, 1, zf + .4), (20, 1, zf + .4)], 1.4))
    add('sleep', mc.polyline('z-z2', m, [(23, 14, zf + .4), (26.5, 14, zf + .4), (23, 10.5, zf + .4), (26.5, 10.5, zf + .4)], 1.0))
    # ---- mo
    if cfg['beak'] == 'overlap':       # chong mep duoi vien, treo ben duoi cua so
        beak = mc.blob('beak', ma, (0, -31, 3), (9, 8, 13))
        beak.rotation_euler.x = math.radians(24)
        kid(beak, fr)
    else:                              # duoi vien, tren bung
        bp, bn = mc.surf(body, 0, 74)
        beak = mc.blob('beak', ma, (0, 0, 0), (9, 9, 13))
        mc.put(beak, bp, bn, 2.0)
        beak.rotation_euler.x += math.radians(18)
    # ---- bung + loa (ha thap de nhuong cho man)
    plate_b = mc.blob('belly', mcr, (0, -46, cfg['zb']), (47, 14, cfg['rzb']), n_top=2.4, n_bot=2.4)
    mc.grille(plate_b, md, 0, cfg['zb'], 26, 5.6, 1.4)
    for dx, dz in ((-9, cfg['mic'] - 2), (0, cfg['mic']), (9, cfg['mic'] - 2)):
        pm, nm = mc.surf(body, dx, dz)
        mc.hole_obj('mic', md, pm, nm, 1.0)
    pt, nt = mc.surf(body, 0, 0, direction=(0, 0, -1))
    top = Vector(pt)
    mc.dome('button', ma, top, nt, 25, 12, sink=3.0)
    mc.torus('btn-groove', md, (0, top.y, top.z - 1.2), 26, 0.9)
    mc.back_features(body, 24, 82, md)
    return dict(body=body, face=f, plate=plate, beak=beak, frame=fr)


def set_state(h, st):
    for k, objs in h['face'].items():
        for o in objs:
            o.hide_render = (k != st)


def run(var, samples, scale):
    os.makedirs(OUT, exist_ok=True)
    sc = mc.scene_base((int(1000 * scale), int(1000 * scale)), samples)
    mc.lights()
    mc.floor()
    h = build(var)
    pr = mc.props(142)
    pset = set(pr)
    for o in pr:
        o.hide_render = True
    skip = ('grille', 'mic', 'vent')
    prod = [o for o in bpy.data.objects if o.type in ('MESH', 'CURVE') and o.name != 'floor'
            and o not in pset and not o.name.startswith(skip)]
    name = 'a2-cu-bong-screen-%s' % var
    for o in pr:
        o.hide_render = False
    set_state(h, 'listen')
    mc.fit_camera(sc, prod + [o for o in pr if o.name.startswith('mug')], -22, 22, 60, margin=0.13)
    mc.render_to(sc, os.path.join(OUT, name + '-hero.png'))
    for o in pr:
        o.hide_render = True
    sc.render.resolution_x = sc.render.resolution_y = int(720 * scale)
    bpy.data.objects.remove(sc.camera)
    close = [h['plate'], h['beak']]
    mc.fit_camera(sc, close, -6, 6, 85, margin=0.07)
    for st in mc.STATES:
        set_state(h, st)
        mc.render_to(sc, os.path.join(OUT, '%s-state-%s.png' % (name, st)))
    bpy.data.objects.remove(sc.camera)
    set_state(h, 'listen')
    mc.fit_camera(sc, prod, -78, 6, 85, margin=0.08)
    mc.render_to(sc, os.path.join(OUT, name + '-side.png'))


if __name__ == '__main__':
    if mc.IN_BLENDER:
        a = sys.argv[sys.argv.index('--') + 1:]
        run(a[0], int(a[1]), float(a[2]))
    else:
        args = sys.argv[1:]
        samples = int(args[args.index('--samples') + 1]) if '--samples' in args else 64
        scale = float(args[args.index('--scale') + 1]) if '--scale' in args else 1.0
        for v in (args[0].split(',') if args and not args[0].startswith('--') else ['v1', 'v2']):
            subprocess.run([BLENDER, '-b', '-noaudio', '-P', os.path.abspath(__file__), '--', v, str(samples), str(scale)], check=True)
