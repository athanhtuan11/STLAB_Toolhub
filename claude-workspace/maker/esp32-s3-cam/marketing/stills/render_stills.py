"""7 anh san pham chan thuc (Cycles) cho reel 30 s - esp32-s3-cam mau D.

Chay (Python thuong, KHONG can bpy):
    python render_stills.py all                 # xuat CAD -> render tat ca -> hau ky -> contact sheet
    python render_stills.py render k02 [--samples 160] [--scale 1.0]   # 1 anh (raw + hau ky)
    python render_stills.py post [k02 ...]      # chi hau ky lai tu raw/*.exr (vai giay)
    python render_stills.py sheet               # chi contact sheet
    python render_stills.py cad                 # xuat lai mesh vi tri lap tu solidcraft/cam_d.sc

Ben trong: Blender 5.2 (blender.exe -b -P render_stills.py -- stage ...) -> stage 'scene' dung + render raw (EXR + PNG),
stage 'post' dung compositor (glare, mau am, vignette, sharpen, hat phim) -> PNG.
Hinh hoc = CAD that (solidcraft/cam_d.sc, vi tri lap): khong them/bot chi tiet. Mau nhua = bien o dau file (TODO: Tuan chua bao mau).
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
CADDIR = os.path.join(HERE, 'assets', 'cad')
RAW = os.path.join(HERE, 'raw')
BLENDER = os.environ.get('BLENDER', r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe')
SC_CLI = os.environ.get('SOLIDCRAFT_CLI', r'C:\Program Files\SolidCraft\solidcraft-cli.exe')

# ---------------------------------------------------------------- MAU NHUA (doi nhanh o day) -- TODO: Tuan chua bao mau cuon
COL_FRAME = '#58A584'    # khung U + de xoay + de + nap chot (concept D: xanh bac ha). Bambu PETG Basic: TODO ten mau hang
COL_BODY = '#E6E6E1'     # hop (trang)
COL_BEZEL = '#222527'    # mat truoc (xam dam)
COL_PCB = '#1E6B3C'      # mach gia lap (hop Ref_Stack trong CAD)
COL_LENS = '#101010'     # vong/than ong kinh (kim loai den)

RES = (1188, 2112)
PARTS = ['Base', 'U_frame', 'Pin_cap', 'Body', 'Bezel', 'Ref_Stack', 'Ref_Cam']

# ---------------------------------------------------------------- CAU HINH ANH
# cam: (az do tu -Y sang +X, el do, khoang cach m, tam ngam (m), tieu cu mm, f-stop, diem lay net (m))
SHOTS = {
    'k01-macro-lens': dict(scene='desk', cam=(26, 9, 0.115, (0.0, -0.028, 0.0725), 100, 6.3, (0.0, -0.031, 0.0746)),
                           pan=-8, tilt=-6, bump=1.0, samples=200, sun='front', strip=True),
    'k02-desk-hero': dict(scene='desk', cam=(32, 17, 0.50, (0.0, -0.004, 0.040), 85, 11.0, (0.0, -0.02, 0.07)),
                          pan=-12, tilt=-7, bump=0.6, samples=160, sun='front'),
    'k03a-exploded': dict(pencil=False, scene='desk', cam=(24, 15, 0.56, (0.0, -0.045, 0.080), 62, 9.0, (0.0, -0.045, 0.09)),
                          pan=0, tilt=0, explode=True, bump=0.5, samples=160, sun='front'),
    'k03b-assembled': dict(pencil=False, scene='desk', cam=(24, 15, 0.56, (0.0, -0.045, 0.080), 62, 9.0, (0.0, -0.045, 0.09)),
                           pan=0, tilt=0, bump=0.5, samples=160, sun='front'),
    'k04-shelf-room': dict(scene='shelf', cam=(42, 12, 0.50, (0.0, 0.0, 0.050), 55, 4.5, (0.0, -0.02, 0.06)),
                           pan=-8, tilt=-8, bump=0.5, samples=200, sun='none', exposure=-0.5),
    'k05-tilt-pan': dict(scene='desk', cam=(15, 8, 0.58, (0.0, 0.0, 0.058), 75, 4.5, (0.0, -0.02, 0.066)),
                         pan=-35, tilt=-25, bump=0.6, samples=160, sun='front', pencil=False),
    'k06-low-hero': dict(scene='low', cam=(-20, 3.5, 0.58, (0.0, 0.0, 0.050), 85, 2.8, (0.0, -0.03, 0.07)),
                         pan=-14, tilt=-8, bump=0.6, samples=160, sun='low'),
}

# ====================================================================== DRIVER (Python thuong)
try:
    import bpy  # noqa
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


def export_cad():
    import json
    os.makedirs(CADDIR, exist_ok=True)
    cmds = [{"command": "file.export_stl", "params": {"path": os.path.join(CADDIR, n + '.stl').replace('\\', '/'),
                                                        "bodies": [n], "quality": "fine"}} for n in PARTS]
    js = os.path.join(HERE, 'assets', '_export.json')
    json.dump({"commands": cmds}, open(js, 'w'))
    r = subprocess.run([SC_CLI, 'run', js, '--in', os.path.join(PROJ, 'solidcraft', 'cam_d.sc')], capture_output=True, text=True)
    os.remove(js)
    print('export CAD rc', r.returncode)
    return r.returncode


def run_blender(*args):
    cmd = [BLENDER, '-b', '--factory-startup', '-P', os.path.abspath(__file__), '--'] + list(args)
    return subprocess.run(cmd).returncode


def sheet():
    from PIL import Image, ImageDraw, ImageFont
    names = list(SHOTS)
    th_w, th_h = 396, 704
    W = th_w * 4 + 20 * 5
    H = (th_h + 50) * 2 + 20
    im = Image.new('RGB', (W, H), (24, 26, 28))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)
    except Exception:
        f = ImageFont.load_default()
    for i, n in enumerate(names):
        p = os.path.join(HERE, n + '.png')
        if not os.path.exists(p):
            continue
        t = Image.open(p).convert('RGB').resize((th_w, th_h), Image.LANCZOS)
        # vien an toan 1080x1920 (cat giua) + vung chu 420 px duoi: nhat
        x = 20 + (i % 4) * (th_w + 20)
        y = 10 + (i // 4) * (th_h + 60)
        im.paste(t, (x, y))
        d.text((x, y + th_h + 6), n + '.png', fill=(235, 235, 230), font=f)
    im.save(os.path.join(HERE, 'contact-sheet.png'))
    print('contact-sheet.png')


def driver(argv):
    if not argv:
        argv = ['all']
    cmd = argv[0]
    if cmd == 'cad':
        sys.exit(export_cad())
    if cmd == 'sheet':
        sheet()
        return
    if cmd == 'post':
        names = argv[1:] or list(SHOTS)
        for n in names:
            run_blender('post', n)
        sheet()
        return
    if cmd == 'render':
        n = argv[1]
        n = [k for k in SHOTS if k.startswith(n)][0]
        run_blender('scene', n, *argv[2:])
        run_blender('post', n)
        return
    if cmd == 'all':
        if not os.path.exists(os.path.join(CADDIR, 'Body.stl')):
            export_cad()
        for n in SHOTS:
            run_blender('scene', n, *argv[1:])
            run_blender('post', n)
        sheet()


# ====================================================================== BLENDER
if IN_BLENDER:
    import bmesh
    import numpy as np
    from mathutils import Vector, Matrix, Euler

    def srgb(h):
        h = h.lstrip('#')
        c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
        return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)

    # ------------------------------------------------------------ mesh tu STL nhi phan (m, he toa do lap)
    def load_stl(name):
        raw = open(os.path.join(CADDIR, name + '.stl'), 'rb').read()
        n = int(np.frombuffer(raw, '<u4', 1, 80)[0])
        dt = np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
        t = np.frombuffer(raw, dt, n, 84)
        v = t['v'].reshape(-1, 3).astype(np.float64) * 0.001
        key = np.round(v / 1e-7).astype(np.int64)
        _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
        verts = v[idx]
        faces = inv.reshape(-1, 3)
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts.tolist(), [], faces.tolist())
        me.update()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob

    def smooth_by_angle(ob, deg=32, dissolve=False):
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        if dissolve:
            bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges)
        for e in bm.edges:
            if len(e.link_faces) == 2:
                e.smooth = e.calc_face_angle(0) < math.radians(deg)
        for f in bm.faces:
            f.smooth = True
        bm.to_mesh(ob.data)
        bm.free()
        ob.data.update()

    # ------------------------------------------------------------ vat lieu
    def new_mat(name):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        return m, nt

    def N(nt, t, **kw):
        n = nt.nodes.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def inp(node, name, val):
        for i in node.inputs:
            if i.name == name and not i.is_linked:
                try:
                    i.default_value = val
                except Exception:
                    pass
                return

    def L(nt, a, b):
        nt.links.new(a, b)

    def principled(nt):
        b = N(nt, 'ShaderNodeBsdfPrincipled')
        o = N(nt, 'ShaderNodeOutputMaterial')
        L(nt, b.outputs['BSDF'], o.inputs['Surface'])
        return b

    def petg(name, hexcol, axis=None, bump=0.2, rough=0.42, sss=0.0, coat=0.10, spec=0.5):
        """PETG in 3D: bong mo, van lop 0,2 mm (bump) theo truc in, bo cap 0,2 mm (bevel node)."""
        m, nt = new_mat(name)
        b = principled(nt)
        inp(b, 'Base Color', srgb(hexcol))
        inp(b, 'Roughness', rough)
        inp(b, 'IOR', 1.57)
        inp(b, 'Specular IOR Level', spec)
        inp(b, 'Coat Weight', coat)
        inp(b, 'Coat Roughness', 0.22)
        if sss:
            inp(b, 'Subsurface Weight', sss)
            inp(b, 'Subsurface Radius', (0.8, 0.5, 0.35))
            inp(b, 'Subsurface Scale', 0.004)
        tc = N(nt, 'ShaderNodeTexCoord')
        bev = N(nt, 'ShaderNodeBevel', samples=6)
        inp(bev, 'Radius', 0.0002)
        nrm = bev.outputs['Normal']
        if axis:
            wv = N(nt, 'ShaderNodeTexWave', wave_type='BANDS', bands_direction=axis, wave_profile='SIN')
            inp(wv, 'Scale', 1571.0)      # chu ky = 2*pi/(20*scale) = 0,2 mm
            inp(wv, 'Distortion', 0.0)
            inp(wv, 'Detail', 0.0)
            L(nt, tc.outputs['Object'], wv.inputs['Vector'])
            bp = N(nt, 'ShaderNodeBump')
            inp(bp, 'Strength', bump)
            inp(bp, 'Distance', 0.00006)
            L(nt, wv.outputs['Fac'], bp.inputs['Height'])
            L(nt, nrm, bp.inputs['Normal'])
            nrm = bp.outputs['Normal']
        nz = N(nt, 'ShaderNodeTexNoise')
        inp(nz, 'Scale', 2500.0)
        inp(nz, 'Detail', 4.0)
        L(nt, tc.outputs['Object'], nz.inputs['Vector'])
        bp2 = N(nt, 'ShaderNodeBump')
        inp(bp2, 'Strength', 0.10)
        inp(bp2, 'Distance', 0.00004)
        L(nt, nz.outputs['Fac'], bp2.inputs['Height'])
        L(nt, nrm, bp2.inputs['Normal'])
        L(nt, bp2.outputs['Normal'], b.inputs['Normal'])
        # do bong khong deu rat nhe
        mr = N(nt, 'ShaderNodeMapRange')
        inp(mr, 'To Min', rough - 0.04)
        inp(mr, 'To Max', rough + 0.05)
        L(nt, nz.outputs['Fac'], mr.inputs['Value'])
        L(nt, mr.outputs['Result'], b.inputs['Roughness'])
        return m

    def plain(name, hexcol, rough=0.6, metal=0.0, spec=0.5, coat=0.0, bevel=0.0003):
        m, nt = new_mat(name)
        b = principled(nt)
        inp(b, 'Base Color', srgb(hexcol))
        inp(b, 'Roughness', rough)
        inp(b, 'Metallic', metal)
        inp(b, 'Specular IOR Level', spec)
        inp(b, 'Coat Weight', coat)
        if bevel:
            bev = N(nt, 'ShaderNodeBevel', samples=4)
            inp(bev, 'Radius', bevel)
            L(nt, bev.outputs['Normal'], b.inputs['Normal'])
        return m

    def emissive(name, hexcol, strength):
        m, nt = new_mat(name)
        e = N(nt, 'ShaderNodeEmission')
        inp(e, 'Color', srgb(hexcol))
        inp(e, 'Strength', strength)
        o = N(nt, 'ShaderNodeOutputMaterial')
        L(nt, e.outputs['Emission'], o.inputs['Surface'])
        return m

    def wood_table(sc=1.1):
        m, nt = new_mat('wood_table')
        b = principled(nt)
        tc = N(nt, 'ShaderNodeTexCoord')
        mp = N(nt, 'ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (sc, sc, sc)
        mp.inputs['Rotation'].default_value = (0, 0, math.radians(90))
        L(nt, tc.outputs['Object'], mp.inputs['Vector'])

        def img(fn, cs):
            t = N(nt, 'ShaderNodeTexImage')
            t.image = bpy.data.images.load(os.path.join(HERE, 'assets', fn))
            t.image.colorspace_settings.name = cs
            L(nt, mp.outputs['Vector'], t.inputs['Vector'])
            return t
        d = img('wood_table_001_diff_2k.jpg', 'sRGB')
        r = img('wood_table_001_rough_2k.jpg', 'Non-Color')
        n = img('wood_table_001_nor_gl_2k.jpg', 'Non-Color')
        nm = N(nt, 'ShaderNodeNormalMap')
        L(nt, n.outputs['Color'], nm.inputs['Color'])
        hs = N(nt, 'ShaderNodeHueSaturation')
        inp(hs, 'Saturation', 0.6)
        inp(hs, 'Value', 2.4)
        L(nt, d.outputs['Color'], hs.inputs['Color'])
        L(nt, hs.outputs['Color'], b.inputs['Base Color'])
        L(nt, nm.outputs['Normal'], b.inputs['Normal'])
        inp(b, 'Specular IOR Level', 0.35)
        mr = N(nt, 'ShaderNodeMapRange')
        inp(mr, 'To Min', 0.45)
        inp(mr, 'To Max', 0.85)
        L(nt, r.outputs['Color'], mr.inputs['Value'])
        L(nt, mr.outputs['Result'], b.inputs['Roughness'])
        return m

    def lens_glass():
        m, nt = new_mat('lens_glass')
        b = principled(nt)
        inp(b, 'Roughness', 0.02)
        inp(b, 'IOR', 1.52)
        inp(b, 'Specular IOR Level', 0.7)
        inp(b, 'Coat Weight', 1.0)
        inp(b, 'Coat Roughness', 0.02)
        inp(b, 'Coat IOR', 1.7)
        # anh tim-xanh cua lop phu chong choi: gradient hinh cau quanh tam ong kinh (z = 74,6 mm)
        tc = N(nt, 'ShaderNodeTexCoord')
        mp = N(nt, 'ShaderNodeMapping')
        mp.inputs['Location'].default_value = (0.0, 0.0, -0.0746)
        mp.inputs['Scale'].default_value = (1 / 0.0045, 0.0, 1 / 0.0045)
        L(nt, tc.outputs['Object'], mp.inputs['Vector'])
        gr = N(nt, 'ShaderNodeTexGradient', gradient_type='SPHERICAL')
        L(nt, mp.outputs['Vector'], gr.inputs['Vector'])
        cr = N(nt, 'ShaderNodeValToRGB')
        el = cr.color_ramp.elements
        el[0].position = 0.0
        el[0].color = srgb('#020204')
        el[1].position = 1.0
        el[1].color = srgb('#10143a')
        e2 = el.new(0.35)
        e2.color = srgb('#2a1448')
        e3 = el.new(0.7)
        e3.color = srgb('#0e3d4a')
        L(nt, gr.outputs['Color'], cr.inputs['Fac'])
        L(nt, cr.outputs['Color'], b.inputs['Base Color'])
        return m

    # ------------------------------------------------------------ hinh hoc phu
    def add_box(name, size, loc, mat, bevel=0.0, rot=(0, 0, 0)):
        me = bpy.data.meshes.new(name)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.scale = size
        ob.location = loc
        ob.rotation_euler = rot
        ob.data.materials.append(mat)
        if bevel:
            # bake scale de bevel dung
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            md = ob.modifiers.new('bv', 'BEVEL')
            md.width = bevel
            md.segments = 3
            md.limit_method = 'ANGLE'
            ob.select_set(False)
        for p in ob.data.polygons:
            p.use_smooth = False
        return ob

    def add_prim(kind, name, loc, mat, rot=(0, 0, 0), **kw):
        bm = bmesh.new()
        if kind == 'cyl':
            bmesh.ops.create_cone(bm, cap_ends=True, segments=kw.get('seg', 48), radius1=kw['r'], radius2=kw.get('r2', kw['r']),
                                  depth=kw['d'])
            if kw.get('twist'):
                bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(kw['twist'], 3, 'Z'))
        elif kind == 'sphere':
            bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=kw['r'])
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = rot
        ob.data.materials.append(mat)
        for p in ob.data.polygons:
            p.use_smooth = True
        return ob

    def add_plane(name, size, loc, mat, rot=(0, 0, 0)):
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.scale = (size[0], size[1], 1)
        ob.location = loc
        ob.rotation_euler = rot
        ob.data.materials.append(mat)
        return ob

    def subsurf(ob, lv=2):
        md = ob.modifiers.new('ss', 'SUBSURF')
        md.levels = lv
        md.render_levels = lv

    def make_book(name, loc, size, cover_hex, rotz=0.0, pages_hex='#EFE6D2'):
        w, d, h = size   # x (rong), y (sau/ngang), z (day)
        t = 0.0022
        cm = plain(name + '_cover', cover_hex, rough=0.55, spec=0.4, bevel=0.0004)
        pm = plain(name + '_pages', pages_hex, rough=0.9, spec=0.2, bevel=0.0001)
        par = bpy.data.objects.new(name, None)
        bpy.context.scene.collection.objects.link(par)
        par.location = loc
        par.rotation_euler = (0, 0, rotz)
        parts = [
            add_box(name + '_bot', (w, d, t), (0, 0, t / 2), cm, 0.0006),
            add_box(name + '_top', (w, d, t), (0, 0, h - t / 2), cm, 0.0006),
            add_box(name + '_spine', (t, d, h), (-w / 2 + t / 2, 0, h / 2), cm, 0.0006),
            add_box(name + '_pg', (w - 0.006, d - 0.006, h - 2 * t - 0.0006), (0.001, 0, h / 2), pm, 0.0002),
        ]
        for p in parts:
            p.parent = par
        return par

    def make_mug(loc, rotz=0.0, hexcol='#E9E0D0'):
        mm = plain('mug', hexcol, rough=0.12, spec=0.6, coat=0.3, bevel=0.0005)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=0.036, radius2=0.040, depth=0.095)
        top = [f for f in bm.faces if f.calc_center_median().z > 0.04][0]
        r = bmesh.ops.inset_region(bm, faces=[top], thickness=0.0035)
        bmesh.ops.translate(bm, verts=top.verts, vec=(0, 0, -0.088))
        me = bpy.data.meshes.new('mug')
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new('mug', me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = (loc[0], loc[1], loc[2] + 0.0475)
        ob.rotation_euler = (0, 0, rotz)
        ob.data.materials.append(mm)
        for p in me.polygons:
            p.use_smooth = True
        md = ob.modifiers.new('ss', 'SUBSURF')
        md.levels = 1
        md.render_levels = 2
        # ca phe
        cm = plain('coffee', '#2A1A12', rough=0.06, spec=0.5)
        cof = add_prim('cyl', 'coffee', (0, 0, 0.0475 - 0.014), cm, r=0.0345, d=0.002, seg=64)
        cof.parent = ob
        cof.location = (0, 0, 0.034)
        # quai
        bpy.ops.mesh.primitive_torus_add(major_radius=0.021, minor_radius=0.0048, major_segments=40, minor_segments=14)
        h = bpy.context.active_object
        h.name = 'mug_handle'
        h.data.materials.append(mm)
        h.parent = ob
        h.rotation_euler = (math.radians(90), 0, 0)
        h.scale = (0.85, 1, 1.15)
        h.location = (0.0415, 0, 0.0)
        for p in h.data.polygons:
            p.use_smooth = True
        return ob

    def make_pencil(loc, rotz=0.0, length=0.175):
        flat = 0.0070                     # 7 mm giua 2 canh
        r = flat / math.sqrt(3.0)         # ban kinh ngoai tiep (luc giac)
        mat = plain('pencil_paint', '#E5B52A', rough=0.28, spec=0.5, coat=0.4, bevel=0.0003)
        wood = plain('pencil_wood', '#D9AE7E', rough=0.7, spec=0.3, bevel=0)
        lead = plain('pencil_lead', '#2B2B2D', rough=0.4, spec=0.4, bevel=0)
        met = plain('pencil_ferrule', '#B8B8B8', rough=0.25, metal=1.0, bevel=0.0002)
        era = plain('pencil_eraser', '#E58D8D', rough=0.8, spec=0.2, bevel=0.0003)
        par = bpy.data.objects.new('pencil', None)
        bpy.context.scene.collection.objects.link(par)
        par.location = (loc[0], loc[1], loc[2] + flat / 2)
        par.rotation_euler = (0, 0, rotz)
        y = math.radians(90)   # truc but doc theo X cuc bo
        def hexcyl(nm, x0, x1, rr, m, seg=6):
            o = add_prim('cyl', nm, ((x0 + x1) / 2, 0, 0), m, rot=(0, y, 0), r=rr, d=x1 - x0, seg=seg,
                         twist=math.radians(30) if seg == 6 else 0)
            if seg == 6:
                for p in o.data.polygons:
                    p.use_smooth = False
            o.parent = par
            return o
        L0 = length
        body = hexcyl('pc_body', 0.0, L0 - 0.025, r, mat)
        hexcyl('pc_ferrule', L0 - 0.025, L0 - 0.014, r * 0.98, met, 24)
        hexcyl('pc_eraser', L0 - 0.014, L0 - 0.0, r * 0.93, era, 24)
        # got ngot
        c = add_prim('cyl', 'pc_cone', (-0.0085 - 0.0005, 0, 0), wood, rot=(0, y, 0), r=r * 0.98, r2=0.0006, d=0.017, seg=24)
        c.parent = par
        c.location = (-0.0085, 0, 0)
        c.rotation_euler = (0, -y, 0)
        # r1 (day) o phia -X? bmesh cone: radius1 duoi (-z) -> sau xoay y=+90: -z -> -x ... ta dat lai ben duoi
        c2 = add_prim('cyl', 'pc_lead', (-0.0165, 0, 0), lead, rot=(0, y, 0), r=0.0006, d=0.0005, seg=12)
        c2.parent = par
        c2.location = (-0.0170, 0, 0)
        return par, c

    def add_bokeh_lights(rng, n, xr, yr, zr, strength=60.0, col='#FFC784', r=0.004):
        m = emissive('fairy', col, strength)
        for i in range(n):
            x = rng.uniform(*xr)
            z = rng.uniform(*zr)
            y = rng.uniform(*yr)
            o = add_prim('sphere', 'fl%d' % i, (x, y, z), m, r=r)
            o.visible_shadow = False

    # ------------------------------------------------------------ san pham
    def build_product(sc, cfg):
        mats = dict(
            Base=petg('m_base', COL_FRAME, 'Z', cfg['bump'], rough=0.45),
            U_frame=petg('m_u', COL_FRAME, 'Z', cfg['bump'], rough=0.45),
            Pin_cap=petg('m_pin', COL_FRAME, 'Z', cfg['bump'], rough=0.45),
            Body=petg('m_body', COL_BODY, 'Y', cfg['bump'], rough=0.40, sss=0.05),
            Bezel=petg('m_bezel', COL_BEZEL, 'Y', cfg['bump'], rough=0.42, coat=0.0, spec=0.25),
            Ref_Stack=plain('m_pcb', COL_PCB, rough=0.35, spec=0.5, bevel=0.0001),
        )
        obs = {}
        for n in PARTS:
            ob = load_stl(n)
            if n in mats:
                smooth_by_angle(ob, 32)
                ob.data.materials.append(mats[n])
            obs[n] = ob
        # ong kinh: vong kim loai den + mat kinh (inset mat truoc)
        lens = obs['Ref_Cam']
        metal = plain('m_lens_metal', COL_LENS, rough=0.30, metal=0.9, bevel=0.0002)
        glass = lens_glass()
        lens.data.materials.append(metal)
        lens.data.materials.append(glass)
        bm = bmesh.new()
        bm.from_mesh(lens.data)
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges)
        front = [f for f in bm.faces if f.normal.y < -0.99 and f.calc_center_median().y < -0.0295][0]
        r1 = bmesh.ops.inset_region(bm, faces=[front], thickness=0.0009)
        bmesh.ops.translate(bm, verts=front.verts, vec=(0, 0.0006, 0))    # mat kinh lom 0,6 mm
        for f in r1['faces']:
            f.material_index = 0
        front.material_index = 1
        for e in bm.edges:
            if len(e.link_faces) == 2:
                e.smooth = e.calc_face_angle(0) < math.radians(40)
        for f in bm.faces:
            f.smooth = True
        bm.to_mesh(lens.data)
        bm.free()
        # day chuyen: pan quanh Z goc, tilt quanh truc X qua (y=0, z=64 mm)
        pan = bpy.data.objects.new('pan', None)
        sc.collection.objects.link(pan)
        tilt = bpy.data.objects.new('tilt', None)
        sc.collection.objects.link(tilt)
        tilt.parent = pan
        tilt.location = (0, 0, 0.064)
        bpy.context.view_layer.update()
        for n in ('U_frame', 'Pin_cap'):
            obs[n].parent = pan
        for n in ('Body', 'Bezel', 'Ref_Stack', 'Ref_Cam'):
            obs[n].parent = tilt
            obs[n].matrix_parent_inverse = tilt.matrix_world.inverted()
        for n in ('U_frame', 'Pin_cap'):
            obs[n].matrix_parent_inverse = pan.matrix_world.inverted()
        pan.rotation_euler = (0, 0, math.radians(cfg['pan']))
        tilt.rotation_euler = (math.radians(cfg['tilt']), 0, 0)
        if cfg.get('explode'):
            def mv(n, d):
                obs[n].location = Vector(d) * 0.001
            mv('U_frame', (0, 0, 26))
            mv('Pin_cap', (0, 0, 26 + 30))
            for n in ('Body',):
                mv(n, (0, 0, 78))
            mv('Ref_Stack', (0, -52, 78))
            mv('Ref_Cam', (0, -52, 78))
            mv('Bezel', (0, -104, 78))
        # day de bong chong lech nhin giong de in that: khong can
        return obs

    # ------------------------------------------------------------ canh
    def build_desk(sc, cfg, kind):
        import random
        rng = random.Random(7)
        # ban go
        add_plane('table', (6, 6), (0, 0, 0), wood_table(6.7))
        # tuong sau + ke
        wall = plain('wall', '#E9DFCF', rough=0.85, spec=0.2, bevel=0)
        add_plane('wall_back', (6, 3), (0, 1.35, 1.0), wall, rot=(math.radians(90), 0, 0))
        # tuong trai co cua so (che nang -> hinh o cua so tren ban)
        wl = plain('wall_l', '#EFE7DA', rough=0.9, bevel=0)
        X = -0.95
        zs = [(-0.2, 0.25), (1.55, 2.2)]
        for z0, z1 in zs:
            add_box('wl_zone', (0.1, 4.0, z1 - z0), (X, 0, (z0 + z1) / 2), wl)
        for y0, y1 in [(-2.0, -1.2), (0.25, 2.0)]:
            add_box('wl_side', (0.1, y1 - y0, 1.3), (X, (y0 + y1) / 2, 0.9), wl)
        fm = plain('frame', '#F4F1EA', rough=0.5, bevel=0)
        add_box('mull_v', (0.06, 0.04, 1.3), (X, 0.02, 0.9), fm)
        add_box('mull_h', (0.06, 1.45, 0.04), (X, -0.475, 1.12), fm)
        # vat the: sach, coc, but chi
        make_book('book1', (-0.20, 0.27, 0.0), (0.150, 0.215, 0.026), '#2E4C6E', rotz=math.radians(16))
        make_book('book2', (-0.205, 0.265, 0.026), (0.140, 0.200, 0.020), '#B5573A', rotz=math.radians(2))
        make_mug((0.25, 0.30, 0.0), rotz=math.radians(40))
        if cfg.get('pencil', True):
            make_pencil((0.10, -0.20, 0.0), rotz=math.radians(163))
        if kind == 'low':
            pass
        # den day bokeh phia sau
        add_bokeh_lights(rng, 40, (-0.9, 1.0), (1.15, 1.25), (0.15, 0.95))
        # ke + hop mau (mo)
        shelf = plain('shelf', '#C79B6C', rough=0.55, bevel=0)
        add_box('shelf_top', (1.6, 0.30, 0.03), (0.3, 1.20, 0.30), shelf)
        bins = ['#4C9A8B', '#E0A83B', '#F1EDE4', '#D9694B', '#5E7FB5', '#F1EDE4']
        for i, c in enumerate(bins):
            w = rng.uniform(0.10, 0.18)
            h = rng.uniform(0.08, 0.16)
            add_box('bin%d' % i, (w, 0.22, h), (-0.25 + i * 0.22, 1.20, 0.315 + h / 2), plain('bin%d' % i, c, rough=0.6, bevel=0), bevel=0.004)
        # cay xanh
        leaf = plain('leaf', '#4E8F4A', rough=0.55, bevel=0)
        for i in range(9):
            a = rng.uniform(0, 2 * math.pi)
            o = add_prim('sphere', 'lf%d' % i, (0.75 + 0.05 * math.cos(a), 1.2 + 0.05 * math.sin(a), 0.40 + 0.04 * i), leaf, r=0.05)
            o.scale = (1.0, 0.25, 1.3)
            o.rotation_euler = (0, rng.uniform(-0.8, 0.8), a)
        add_prim('cyl', 'pot', (0.75, 1.2, 0.34), plain('pot', '#F1EDE4', rough=0.5), r=0.05, r2=0.04, d=0.07)

    def build_shelf_room(sc, cfg):
        import random
        _before0 = set(bpy.context.scene.objects)
        rng = random.Random(11)
        # ke go (san pham dat tren ke): mat ke z = 0
        shelf = plain('shelf_wood', '#C9A073', rough=0.5, spec=0.4, coat=0.1, bevel=0)
        # dung texture go
        before = set(bpy.context.scene.objects)
        sh = add_box('shelf', (1.0, 1.0, 0.03), (0, -0.3, -0.015), wood_table(), bevel=0.0015)
        shelf_obs = {sh}
        # phong hoc: san z=-0.95, tuong xa y=-5, tran z=2.0
        floor = plain('floor', '#B8B2A6', rough=0.5, spec=0.3, bevel=0)
        add_plane('floor', (12, 12), (0, -3, -0.95), floor)
        wallm = plain('rwall', '#EDE6D8', rough=0.9, bevel=0)
        add_plane('far_wall', (12, 5), (0, -6.0, 0.9), wallm, rot=(math.radians(90), 0, 0))
        add_plane('right_wall', (12, 5), (4.0, -3, 0.9), wallm, rot=(math.radians(90), 0, math.radians(90)))
        add_plane('left_wall', (12, 5), (-4.0, -3, 0.9), wallm, rot=(math.radians(90), 0, math.radians(90)))
        add_plane('ceiling', (12, 12), (0, -3, 2.2), plain('ceil', '#F2EEE6', rough=0.9, bevel=0))
        add_plane('back_wall', (12, 5), (0, 1.5, 0.9), wallm, rot=(math.radians(90), 0, 0))
        # cua so lon o tuong xa (phat sang)
        win = emissive('window', '#FFF1DA', 14.0)
        add_plane('window', (3.2, 1.3), (-1.2, -5.95, 0.85), win, rot=(math.radians(90), 0, 0))
        fm = plain('wframe', '#F4F1EA', rough=0.5, bevel=0)
        for i in range(0, 5):
            add_box('wm', (0.05, 0.05, 1.3), (-2.8 + i * 0.8, -5.92, 0.85), fm)
        add_box('wm2', (3.2, 0.05, 0.05), (-1.2, -5.92, 0.85), fm)
        # den tran (bokeh chu nhat)
        lamp = emissive('ceil_lamp', '#FFE2B8', 30.0)
        for i in range(3):
            for j in range(3):
                add_plane('cl', (0.7, 0.28), (-1.6 + j * 1.6, -1.5 - i * 1.7, 2.18), lamp)
        # ban hoc: mat go sang + chan
        top = plain('desk_top', '#D9C3A0', rough=0.5, bevel=0)
        legm = plain('desk_leg', '#6F7378', rough=0.4, metal=0.6, bevel=0)
        cols = ['#4C9A8B', '#E0A83B', '#D9694B', '#5E7FB5']
        k = 0
        for i in range(3):
            for j in range(3):
                x = -2.0 + j * 2.0
                y = -2.0 - i * 1.6
                add_box('dtop', (1.4, 0.7, 0.04), (x, y, -0.25 + 0.0), top)
                for dx in (-0.65, 0.65):
                    for dy in (-0.3, 0.3):
                        add_box('dleg', (0.04, 0.04, 0.7), (x + dx, y + dy, -0.6), legm)
                # ghe
                chair = plain('chair%d' % k, cols[k % 4], rough=0.5, bevel=0)
                add_box('seat', (0.4, 0.4, 0.05), (x + rng.uniform(-0.3, 0.3), y + 0.7, -0.5), chair, bevel=0.01)
                add_box('chb', (0.4, 0.05, 0.4), (x, y + 0.9, -0.3), chair, bevel=0.01)
                # thiet bi tren ban (hop robot mo)
                add_box('gad', (0.2, 0.15, 0.1), (x + rng.uniform(-0.4, 0.4), y, -0.18), plain('gad', cols[(k + 1) % 4], rough=0.5, bevel=0), bevel=0.01)
                k += 1
        # tu ke ben phai
        for i in range(4):
            add_box('cab', (0.5, 2.6, 0.04), (3.7, -3.0, -0.6 + i * 0.6), shelf)
            for j in range(5):
                add_box('cbin', (0.3, 0.35, 0.25), (3.7, -4.0 + j * 0.45, -0.45 + i * 0.6), plain('cb', cols[(i + j) % 4], rough=0.6, bevel=0), bevel=0.01)
        # bang trang KHONG chu tren tuong trai + khung
        add_plane('whiteboard', (2.4, 1.2), (-3.95, -3.0, 0.75), plain('wb', '#F6F6F2', rough=0.25, spec=0.6, bevel=0), rot=(math.radians(90), 0, math.radians(90)))
        add_box('wbframe', (0.03, 2.5, 0.05), (-3.97, -3.0, 0.16), plain('wbf', '#9AA0A5', rough=0.4, metal=0.7, bevel=0))
        # may in 3D dang khoi don gian tren mot ban (khung + truc + dau in + dem)
        px, py = -2.0, -3.6
        dk = plain('p3d_dark', '#2D3033', rough=0.5, bevel=0)
        og = plain('p3d_acc', '#E0A83B', rough=0.5, bevel=0)
        add_box('p3d_base', (0.34, 0.34, 0.06), (px, py, -0.20), dk, bevel=0.005)
        add_box('p3d_bed', (0.26, 0.26, 0.012), (px, py, -0.164), plain('bed', '#8C9296', rough=0.4, metal=0.6, bevel=0))
        add_box('p3d_l', (0.03, 0.03, 0.40), (px - 0.16, py + 0.14, 0.0), dk)
        add_box('p3d_r', (0.03, 0.03, 0.40), (px + 0.16, py + 0.14, 0.0), dk)
        add_box('p3d_top', (0.36, 0.05, 0.03), (px, py + 0.14, 0.20), dk)
        add_box('p3d_head', (0.07, 0.06, 0.06), (px, py + 0.08, -0.05), og, bevel=0.004)
        # hop linh kien tren ke (chu nhat nho, khong chu)
        for i in range(6):
            add_box('part%d' % i, (0.16, 0.12, 0.09), (3.5, -2.2 - i * 0.0, -0.57 + 0.0), plain('pt%d' % i, cols[i % 4], rough=0.6, bevel=0), bevel=0.005) if False else None
        # chuyen ca phong ra phia +Y (phia sau san pham), san pham nhin ve phia camera
        room = bpy.data.objects.new('room', None)
        bpy.context.scene.collection.objects.link(room)
        room.rotation_euler = (0, 0, math.pi)
        for o in list(bpy.context.scene.objects):
            if o not in _before0 and o is not room and o.name != 'shelf' and o.parent is None:
                o.parent = room

    # ------------------------------------------------------------ anh sang
    def build_world(strength=0.75, rot=0.0):
        w = bpy.data.worlds.new('w')
        bpy.context.scene.world = w
        w.use_nodes = True
        nt = w.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        env = N(nt, 'ShaderNodeTexEnvironment')
        env.image = bpy.data.images.load(os.path.join(HERE, 'assets', 'kloofendal_misty_morning_puresky_2k.hdr'))
        mp = N(nt, 'ShaderNodeMapping')
        mp.inputs['Rotation'].default_value = (0, 0, rot)
        tc = N(nt, 'ShaderNodeTexCoord')
        bg = N(nt, 'ShaderNodeBackground')
        bg.inputs['Strength'].default_value = strength
        o = N(nt, 'ShaderNodeOutputWorld')
        L(nt, tc.outputs['Generated'], mp.inputs['Vector'])
        L(nt, mp.outputs['Vector'], env.inputs['Vector'])
        L(nt, env.outputs['Color'], bg.inputs['Color'])
        L(nt, bg.outputs['Background'], o.inputs['Surface'])

    def add_light(kind, name, loc, target, energy, color=(1, 1, 1), size=1.0, size_y=None, spread=None):
        ld = bpy.data.lights.new(name, kind)
        ld.color = color
        if kind == 'SUN':
            ld.energy = energy
            ld.angle = math.radians(size)
        else:
            ld.energy = energy
            if kind == 'AREA':
                ld.shape = 'RECTANGLE'
                ld.size = size
                ld.size_y = size_y or size
        ob = bpy.data.objects.new(name, ld)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = loc
        d = Vector(target) - Vector(loc)
        ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return ob

    def build_lights(sc, cfg):
        kind = cfg['scene']
        s = cfg.get('sun')
        if kind in ('desk', 'low'):
            # nang som qua cua so trai
            d = Vector((0.9, 0.42, -0.62)) if s != 'low' else Vector((0.9, 0.55, -0.30))
            sun = add_light('SUN', 'sun', (0, 0, 2), tuple(d), 12.0 if s != 'low' else 10.0, color=(1.0, 0.80, 0.58), size=1.2)
            sun.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
            # tam phan xa/den bu mat truoc (ben phai may, mem)
            if not cfg.get('strip'):
              add_light('AREA', 'fill', (0.55, -0.9, 0.45), (0, 0, 0.06), 30.0, color=(1.0, 0.93, 0.85), size=0.9, size_y=0.6)
              add_light('AREA', 'kick', (-0.35, -0.7, 0.18), (0, -0.02, 0.07), 5.0, color=(0.85, 0.92, 1.0), size=0.5)
            if cfg.get('strip'):
                # dai den phan chieu tren kinh ong kinh (camera lech trai -> den o ben phai-truoc)
                add_light('AREA', 'strip', (-0.30, -0.55, 0.25), (0, -0.03, 0.074), 9.0, color=(1.0, 0.97, 0.92), size=0.05, size_y=0.30)
        else:   # shelf
            add_light('AREA', 'key', (0.55, -0.6, 0.55), (0, 0, 0.05), 22.0, color=(1.0, 0.88, 0.72), size=0.7, size_y=0.5)
            add_light('AREA', 'rim', (-0.3, 0.9, 0.40), (0, 0, 0.06), 45.0, color=(1.0, 0.95, 0.88), size=0.6, size_y=0.3)

    # ------------------------------------------------------------ camera + render
    def setup_camera(sc, cfg):
        az, el, dist, tgt, lens, fst, foc = cfg['cam']
        if os.environ.get('STILLS_CAM'):
            v = [float(x) for x in os.environ['STILLS_CAM'].split(',')]
            az, el, dist, tgt, lens, fst, foc = v[0], v[1], v[2], tuple(v[3:6]), v[6], v[7], tuple(v[3:6])
        a = math.radians(az)
        e = math.radians(el)
        t = Vector(tgt)
        loc = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
        cd = bpy.data.cameras.new('cam')
        cd.lens = lens
        cd.sensor_fit = 'VERTICAL'
        cd.sensor_height = 36.0
        cd.clip_start = 0.01
        cd.clip_end = 40
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fst
        cd.dof.aperture_blades = 8
        fe = bpy.data.objects.new('focus', None)
        fe.location = foc
        sc.collection.objects.link(fe)
        cd.dof.focus_object = fe
        ob = bpy.data.objects.new('cam', cd)
        sc.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = (t - loc).to_track_quat('-Z', 'Y').to_euler()
        sc.camera = ob

    def setup_cycles(sc, samples, scale):
        sc.render.engine = 'CYCLES'
        cp = bpy.context.preferences.addons['cycles'].preferences
        for typ in ('OPTIX', 'CUDA'):
            try:
                cp.compute_device_type = typ
                cp.get_devices()
                ok = [d for d in cp.devices if d.type == typ]
                if ok:
                    for d in cp.devices:
                        d.use = (d.type == typ)
                    break
            except Exception:
                continue
        sc.cycles.device = 'GPU'
        sc.cycles.samples = samples
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.adaptive_threshold = 0.01
        sc.cycles.use_denoising = True
        try:
            sc.cycles.denoiser = 'OPTIX'
        except Exception:
            sc.cycles.denoiser = 'OPENIMAGEDENOISE'
        sc.cycles.max_bounces = 10
        sc.cycles.diffuse_bounces = 5
        sc.cycles.glossy_bounces = 6
        sc.cycles.transmission_bounces = 4
        sc.cycles.sample_clamp_indirect = 3.0
        sc.cycles.blur_glossy = 0.3
        sc.cycles.caustics_reflective = False
        sc.cycles.caustics_refractive = False
        sc.render.resolution_x = RES[0]
        sc.render.resolution_y = RES[1]
        sc.render.resolution_percentage = int(100 * scale)
        sc.render.filter_size = 1.3
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'None'
        sc.view_settings.exposure = 0.0
        sc.display_settings.display_device = 'sRGB'

    def stage_scene(name, samples=None, scale=1.0, exposure=None):
        import time
        cfg = SHOTS[name]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        build_world(0.22)
        build_product(sc, cfg)
        if cfg['scene'] == 'shelf':
            build_shelf_room(sc, cfg)
        else:
            build_desk(sc, cfg, cfg['scene'])
        build_lights(sc, cfg)
        setup_camera(sc, cfg)
        setup_cycles(sc, samples or cfg['samples'], scale)
        if exposure is not None:
            sc.view_settings.exposure = exposure
        else:
            sc.view_settings.exposure = cfg.get('exposure', 0.0)
        os.makedirs(RAW, exist_ok=True)
        t0 = time.time()
        bpy.ops.render.render(write_still=False)
        dt = time.time() - t0
        img = bpy.data.images['Render Result']
        sc.render.image_settings.file_format = 'OPEN_EXR'
        sc.render.image_settings.color_depth = '16'
        sc.render.image_settings.exr_codec = 'ZIP'
        img.save_render(os.path.join(RAW, name + '.exr'))
        sc.render.image_settings.file_format = 'PNG'
        sc.render.image_settings.color_depth = '8'
        img.save_render(os.path.join(RAW, name + '.png'))
        open(os.path.join(RAW, name + '.time.txt'), 'w').write('%.1f\n' % dt)
        print('RENDER %s %.1f s' % (name, dt))
        if '--save-blend' in sys.argv:
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'assets', name + '.blend'))

    def stage_post(name):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        exr = os.path.join(RAW, name + '.exr')
        im = bpy.data.images.load(exr)
        w, h = im.size
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = 1
        sc.cycles.device = 'CPU'
        sc.render.resolution_x = w
        sc.render.resolution_y = h
        sc.render.resolution_percentage = 100
        cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
        sc.collection.objects.link(cam)
        sc.camera = cam
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'None'
        sc.display_settings.display_device = 'sRGB'
        # vignette + hat phim bang numpy (anh phu), nap vao compositor
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = (w - 1) / 2, (h - 1) / 2
        r = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2) / math.sqrt(2.0)
        vig = 1.0 - 0.30 * np.clip((r - 0.35) / 0.65, 0, 1) ** 1.8
        rng = np.random.default_rng(3)
        g = rng.normal(0.0, 1.0, (h, w)).astype(np.float32)
        # hat min: lam muot nhe de khong qua "so"
        g = (g + np.roll(g, 1, 0) * 0.5 + np.roll(g, 1, 1) * 0.5) / 1.5

        def mk(nm, rgb):
            i = bpy.data.images.new(nm, w, h, float_buffer=True, alpha=False)
            i.colorspace_settings.name = 'Linear Rec.709'
            px = np.empty((h, w, 4), np.float32)
            px[..., :3] = rgb[..., None]
            px[..., 3] = 1
            i.pixels.foreach_set(px.ravel())
            i.update()
            return i
        i_vig = mk('vig', vig)
        i_grain = mk('grain', 0.5 + g * 0.5 * 0.035)      # quanh 0,5 -> cong/tru
        ng = bpy.data.node_groups.new('post', 'CompositorNodeTree')
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        sc.compositing_node_group = ng
        nd = ng.nodes

        def node(t, **kw):
            n = nd.new(t)
            for k, v in kw.items():
                setattr(n, k, v)
            return n

        def sock(n, name, val):
            for s in n.inputs:
                if s.name == name:
                    try:
                        s.default_value = val
                    except Exception as ex:
                        print('sock', name, ex)
                    return
            print('no socket', name, 'on', n.name)
        src = node('CompositorNodeImage')
        src.image = im
        gl = node('CompositorNodeGlare')
        sock(gl, 'Type', 'Bloom')
        sock(gl, 'Quality', 'High')
        sock(gl, 'Threshold', 1.0)
        sock(gl, 'Strength', 0.28)
        sock(gl, 'Size', 0.45)
        sock(gl, 'Saturation', 1.0)
        sock(gl, 'Smoothness', 0.4)
        cb = node('CompositorNodeColorBalance')
        sock(cb, 'Type', 'Lift/Gamma/Gain')
        sock(cb, 'Gain', (1.035, 1.0, 0.955, 1.0))
        sock(cb, 'Gamma', (1.0, 1.0, 1.0, 1.0))
        sock(cb, 'Lift', (1.0, 1.0, 1.0, 1.0))
        hs = node('CompositorNodeHueSat')
        sock(hs, 'Saturation', 1.06)
        sock(hs, 'Value', 1.0)
        mvig = node('ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY')
        sock(mvig, 'Factor', 1.0)
        vi = node('CompositorNodeImage')
        vi.image = i_vig
        fl = node('CompositorNodeFilter')
        sock(fl, 'Type', 'Sharpen')
        sock(fl, 'Factor', 0.35)
        gi = node('CompositorNodeImage')
        gi.image = i_grain
        mg = node('ShaderNodeMix', data_type='RGBA', blend_type='LINEAR_LIGHT')
        sock(mg, 'Factor', 0.55)
        out = node('NodeGroupOutput')

        def A(n):   # input A/B cua Mix (RGBA) = socket thu tu 2 ('A','B' kieu mau)
            return [s for s in n.inputs if s.name == 'A' and s.type == 'RGBA'][0], [s for s in n.inputs if s.name == 'B' and s.type == 'RGBA'][0]
        link = ng.links.new
        link(src.outputs[0], gl.inputs['Image'])
        link(gl.outputs[0], cb.inputs['Image'])
        link(cb.outputs[0], hs.inputs['Image'])
        a, b = A(mvig)
        link(hs.outputs[0], a)
        link(vi.outputs[0], b)
        link(mvig.outputs['Result'] if 'Result' in mvig.outputs else mvig.outputs[2], fl.inputs['Image'])
        a2, b2 = A(mg)
        link(fl.outputs[0], a2)
        link(gi.outputs[0], b2)
        link(mg.outputs['Result'] if 'Result' in mg.outputs else mg.outputs[2], out.inputs[0])
        sc.render.image_settings.file_format = 'PNG'
        sc.render.image_settings.color_depth = '8'
        sc.render.filepath = os.path.join(HERE, name + '.png')
        bpy.ops.render.render(write_still=True)
        print('POST', name)

    def blender_main():
        a = sys.argv[sys.argv.index('--') + 1:]
        stage, name = a[0], a[1]
        opts = {}
        if '--samples' in a:
            opts['samples'] = int(a[a.index('--samples') + 1])
        if '--scale' in a:
            opts['scale'] = float(a[a.index('--scale') + 1])
        if '--exposure' in a:
            opts['exposure'] = float(a[a.index('--exposure') + 1])
        if stage == 'scene':
            stage_scene(name, **opts)
        else:
            stage_post(name)


if __name__ == '__main__':
    if IN_BLENDER:
        blender_main()
    else:
        driver(sys.argv[1:])
