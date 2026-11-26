"""english-teacher - A2 Cu Bong co man V2 + 2 LOA ben suon (V2-2L). Dung lai make_screen_concepts.build('v2').

Chay: python make_screen_2l.py [h0,h25] [--samples 48 --scale 1.0]
  -> concepts/a2-cu-bong-screen-v2-2l-{h0,h25}-{hero,side,back}.png + ...-xray-{front,top}.png
Roi:  python make_sheet_screen_2l.py -> contact-sheet-screen-2l.png
Bien the: h0 = loa huong ngang 0 do; h25 = chech truoc 25 do. So do: xem design-spec.md muc 10.9.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_concepts as mc          # noqa: E402
import make_screen_concepts as sc2  # noqa: E402

M = 0.001
if mc.IN_BLENDER:
    import bpy
    from mathutils import Vector

SPK_Z = 50.0                  # tam loa (z). Bezel 86 x 86 -> z 7..93 (khong cham san)
SPK_D, SPK_L, SPK_FLANGE, SPK_REAR_D = 52.0, 26.0, 5.0, 38.0
GRILLE_R, PITCH, HOLE_R = 28.0, 5.6, 1.4
BEZEL_R = 34.0               # vanh kem concept (CAD: bezel 86 x 86 x 15 dat ben trong)
VAR = {'h0': 0.0, 'h25': 25.0}


def axis_of(sx, ang):
    a = math.radians(ang)
    return Vector((sx * math.cos(a), -math.sin(a), 0.0))


def hit_side(body, sx, ang):
    d = axis_of(sx, ang)
    o = Vector((0, 0, SPK_Z * M))
    inv = body.matrix_basis.inverted()
    ok, loc, nor, _ = body.ray_cast(inv @ o, (inv.to_3x3() @ d).normalized())
    assert ok
    return (body.matrix_basis @ loc) / M, d


def orient(o, p, d, sink=0.0):
    o.location = (Vector(p) - d * sink) * M
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()


def build(ang):
    h = sc2.build('v2')
    for o in list(bpy.data.objects):
        if o.name.startswith(('grille', 'wing')):
            bpy.data.objects.remove(o)
    P = mc.PAL['a']
    mb = mc.mat('body2', P['body'], 0.55, sss=0.15)
    mcr = mc.mat('cream2', P['cream'], 0.5, sss=0.1)
    md = mc.mat('dark2', P['dark'], 0.8)
    line = mc.mat('feather', '#EBD3AE', 0.6)
    for s in (-1, 1):   # canh nho, doi len cao + ra sau (nhuong cho loa suon)
        mc.blob('wing%d' % s, mb, (s * 60, 22, 112), (10, 22, 28), rot=(0, s * 8, 0))
    info = {}
    for s in (-1, 1):
        p, d = hit_side(h['body'], s, ang)
        proud = 1.5 if ang == 0 else 3.5
        face = Vector(p) + d * proud
        bz = mc.cylinder('bezel%d' % s, mcr, (0, 0, 0), BEZEL_R, 8.0, bevel=2.0)
        orient(bz, face, d, 4.0)
        u = Vector((0, 0, 1))
        v = d.cross(u).normalized()
        n = int(math.pi * GRILLE_R ** 2 / (PITCH * PITCH * 0.866))
        ga = math.pi * (3 - math.sqrt(5))
        for i in range(n):
            rr = GRILLE_R * math.sqrt((i + 0.5) / n)
            a = i * ga
            q = face + u * (rr * math.cos(a)) + v * (rr * math.sin(a))
            mc.hole_obj('grille-%d-%d' % (s, i), md, q, d, HOLE_R)
        info[s] = (Vector(p), d)
    belly = bpy.data.objects['belly']
    for zc, xs in ((60, (-24, -12, 0, 12, 24)), (48, (-18, -6, 6, 18)), (36, (-12, 0, 12))):
        for x in xs:
            pts = []
            for dx, dz in ((-5, 3), (0, 0), (5, 3)):
                p, nr = mc.surf(belly, x + dx, zc + dz)
                pts.append(tuple(Vector(p) + nr * 0.3))
            mc.polyline('feather', line, pts, 1.2)
    p, nr = mc.surf(belly, 0, 22)
    logo = mc.blob('logo', md, (0, 0, 0), (13, 3.2, 0.6), n_top=4, n_bot=4)
    mc.put(logo, p, nr, -0.1)
    h['info'] = info
    return h


def mic_dist(h, info):
    pm, _ = mc.surf(h['body'], 0, 141)
    out = []
    for s, (p, d) in info.items():
        c = p - d * (4.5 + SPK_L / 2)      # tam khoi loa
        out.append(((Vector(pm) - p).length, (Vector(pm) - c).length))
    return out


def run(var, samples, scale):
    ang = VAR[var]
    sc = mc.scene_base((int(1000 * scale), int(1000 * scale)), samples)
    mc.lights()
    mc.floor()
    h = build(ang)
    print('MICDIST', var, [tuple(round(k, 1) for k in t) for t in mic_dist(h, h['info'])])
    pr = mc.props(142)
    pset = set(pr)
    for o in pr:
        o.hide_render = True
    prod = [o for o in bpy.data.objects if o.type in ('MESH', 'CURVE') and o.name != 'floor' and o not in pset
            and not o.name.startswith(('mic', 'vent', 'grille'))]
    name = 'a2-cu-bong-screen-v2-2l-%s' % var
    sc2.set_state(h, 'listen')
    for o in pr:
        o.hide_render = False
    mc.fit_camera(sc, prod + [o for o in pr if o.name.startswith('mug')], -35, 22, 60, margin=0.13)
    mc.render_to(sc, os.path.join(mc.OUT, name + '-hero.png'))
    for o in pr:
        o.hide_render = True
    bpy.data.objects.remove(sc.camera)
    mc.fit_camera(sc, prod, -88, 8, 85, margin=0.08)
    mc.render_to(sc, os.path.join(mc.OUT, name + '-side.png'))
    bpy.data.objects.remove(sc.camera)
    mc.fit_camera(sc, prod, 160, 22, 85, margin=0.08)
    mc.render_to(sc, os.path.join(mc.OUT, name + '-back.png'))
    bpy.data.objects.remove(sc.camera)
    xray(sc, h, name, scale)


def xray(sc, h, name, scale):
    for o in bpy.data.objects:
        if o.name == 'floor':
            o.hide_render = True
    shell = mc.mat('xshell', '#F6BE9A', 0.4)
    shell.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.13
    for o in list(bpy.data.objects):
        if o.type in ('MESH', 'CURVE') and o.name != 'floor':
            if o.name.startswith(('grille', 'mic', 'feather', 'l-', 's-', 'p-', 'z-', 'logo', 'btn', 'vent', 'usb', 'glass', 'cut')):
                o.hide_render = True
            elif o.name.startswith(('body', 'ear', 'wing', 'belly', 'plate', 'beak', 'bezel', 'button')):
                o.data.materials.clear()
                o.data.materials.append(shell)
    cs = mc.mat('x-spk', '#4F5560', 0.5)
    cm = mc.mat('x-mag', '#2A2D33', 0.6)
    cp = mc.mat('x-pcb', '#2E8B57', 0.5)
    ca = mc.mat('x-amp', '#E4572E', 0.5)
    cd = mc.mat('x-disp', '#2B6CB0', 0.5)
    for s in (-1, 1):
        p, d = h['info'][s]
        F = p - d * 4.5
        fl = mc.cylinder('x-fl%d' % s, cs, (0, 0, 0), SPK_D / 2, SPK_FLANGE, bevel=0.5)
        orient(fl, F - d * SPK_FLANGE / 2, d)
        bd = mc.cylinder('x-bd%d' % s, cm, (0, 0, 0), SPK_REAR_D / 2, SPK_L - SPK_FLANGE, bevel=1.0)
        orient(bd, F - d * (SPK_FLANGE + (SPK_L - SPK_FLANGE) / 2), d)
        mc.box('x-amp%d' % s, ca, (s * 30, 16, SPK_Z), (10, 22, 22), bevel=0.6)
    mc.box('x-pcb', cp, (0, 34, 64), (29, 16, 72), bevel=0.6)
    pcbd = mc.box('x-disp', cd, (0, 0, -3.0), (86, 50, 8), bevel=0.5)   # day PCB man 8 mm = TODO
    pcbd.parent = h['frame']
    bpy.context.view_layer.update()
    res = int(1000 * scale)
    for tag in ('front', 'top'):
        cd_ = bpy.data.cameras.new('c' + tag)
        cd_.type = 'ORTHO'
        cd_.ortho_scale = 0.24 if tag == 'front' else 0.19
        cam = bpy.data.objects.new('c' + tag, cd_)
        sc.collection.objects.link(cam)
        sc.camera = cam
        if tag == 'front':
            cam.location = (0, -1.0, 0.09)
            cam.rotation_euler = (math.radians(90), 0, 0)
        else:
            cam.location = (0, 0.0, 1.0)
            cam.rotation_euler = (0, 0, 0)
        sc.render.resolution_x = sc.render.resolution_y = res
        mc.render_to(sc, os.path.join(mc.OUT, '%s-xray-%s.png' % (name, tag)))
        bpy.data.objects.remove(cam)


if __name__ == '__main__':
    if mc.IN_BLENDER:
        a = sys.argv[sys.argv.index('--') + 1:]
        run(a[0], int(a[1]), float(a[2]))
    else:
        args = sys.argv[1:]
        samples = int(args[args.index('--samples') + 1]) if '--samples' in args else 48
        scale = float(args[args.index('--scale') + 1]) if '--scale' in args else 1.0
        vs = args[0].split(',') if args and not args[0].startswith('--') else ['h0', 'h25']
        for v in vs:
            subprocess.run([mc.BLENDER, '-b', '-noaudio', '-P', os.path.abspath(__file__), '--', v, str(samples), str(scale)], check=True)
