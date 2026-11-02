# Ve de flexi Tet vong 2: tu the C (nam phuc) + dau chibi. Chi de duyet anh, khong phai CAD.
# Chay: blender -b -P make_v2.py -- <outdir> [ten-anh,...]   (don vi: 1 don vi = 1 mm)
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index("--")+1:]
OUT = argv[0]; ONLY = argv[1].split(",") if len(argv) > 1 else None
CREAM, GOLD, RED, DARK, BG = "#F7F2E6", "#E8B33A", "#C8372D", "#2A2E33", "#DCE4E1"
def hexc(h):
    h = h.lstrip('#'); return tuple(pow(int(h[i:i+2], 16)/255, 2.2) for i in (0, 2, 4)) + (1,)
MATS = {}
def mat(c, rough=0.42):
    k = (c, rough)
    if k not in MATS:
        m = bpy.data.materials.new(c); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = hexc(c); b.inputs["Roughness"].default_value = rough
        MATS[k] = m
    return MATS[k]
def act(o):
    for x in bpy.context.selected_objects: x.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
def apply_scale(o):
    act(o); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
def finish(o, color, rough=0.42, clip=True):
    """bake transform, cat mat phang z=0, tro vat lieu, smooth"""
    act(o)
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
    if clip:
        bm = bmesh.new(); bm.from_mesh(o.data)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_inner=True)
        edges = [e for e in bm.edges if e.is_boundary]
        if edges: bmesh.ops.triangle_fill(bm, use_beauty=True, edges=edges)
        bm.to_mesh(o.data); bm.free()
    o.data.materials.clear(); o.data.materials.append(mat(color, rough))
    act(o); bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
    return o
def ell(h, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = h; apply_scale(o); return o
def rbox(dims, r, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = dims; apply_scale(o)
    md = o.modifiers.new("b", 'BEVEL'); md.width = r; md.segments = 8; md.limit_method = 'NONE'
    act(o); bpy.ops.object.modifier_apply(modifier="b"); return o
def cut(o, cutter):
    act(o); md = o.modifiers.new("x", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = cutter
    bpy.ops.object.modifier_apply(modifier="x")
    bpy.data.objects.remove(cutter, do_unlink=True)
def tube(pts, rads):
    """duong cong poly + ban kinh tung diem -> mesh"""
    cu = bpy.data.curves.new("t", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 1.0; cu.bevel_resolution = 8
    cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p, w, r in zip(sp.points, pts, rads): p.co = (w[0], w[1], w[2], 1); p.radius = r
    o = bpy.data.objects.new("t", cu); bpy.context.scene.collection.objects.link(o)
    act(o); bpy.ops.object.convert(target='MESH'); return bpy.context.view_layer.objects.active
def catmull(P, R, n=14):
    out = []; ro = []
    P2 = [P[0]] + P + [P[-1]]; R2 = [R[0]] + R + [R[-1]]
    for i in range(1, len(P2)-2):
        for k in range(n):
            t = k/n
            def cr(a, b, c, d): return 0.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3)
            out.append(tuple(cr(P2[i-1][j], P2[i][j], P2[i+1][j], P2[i+2][j]) for j in range(3)))
            ro.append(cr(R2[i-1], R2[i], R2[i+1], R2[i+2]))
    out.append(P[-1]); ro.append(R[-1])
    d = Vector(P[-1]) - Vector(P[-2]); d.normalize()
    for adv, rr in ((1.4, R[-1]*0.8), (2.4, R[-1]*0.45)):
        out.append(tuple(Vector(P[-1]) + d*adv)); ro.append(rr)
    return out, ro
def meta(elems, res=0.55):
    mb = bpy.data.metaballs.new("h"); mb.resolution = res; mb.render_resolution = res; mb.threshold = 0.6
    o = bpy.data.objects.new("h", mb); bpy.context.scene.collection.objects.link(o)
    for (c, h) in elems:
        e = mb.elements.new(type='ELLIPSOID'); e.co = c; e.radius = 10; e.stiffness = 2
        e.size_x, e.size_y, e.size_z = (h[0]/5.73, h[1]/5.73, h[2]/5.73)
    act(o); bpy.ops.object.convert(target='MESH'); return bpy.context.view_layer.objects.active

# ---- doan than: (x_trai, x_phai, rong_y, cao_z)
SEG = [(-55, -45, 26, 24), (-43, -29, 40, 32), (-27, -10, 48, 38), (-8, 10, 50, 40), (12, 28, 44, 38), (30, 44, 30, 30)]
# SEG[3] = hoa mai, SEG[2], SEG[4] = may
def build(variant="color", kc=False, explode=False, loc=(0, 0, 0), scale=1.0):
    """variant: color | mono (kem) | red. tra ve empty goc"""
    col = lambda c: {"color": c, "mono": CREAM, "red": RED}[variant]
    cream = col(CREAM); gold = col(GOLD); red = col(RED)
    dep = 1.6 if kc else 1.3; trad = 1.5 if kc else 1.05
    objs = []
    for i, (x0, x1, w, H) in enumerate(SEG):
        xm = (x0+x1)/2
        s = rbox((x1-x0, w, H), 5.5, (xm, 0, H/2))
        top = H
        if i == 3:  # hoa mai 5 canh khac chim tren lung
            for k in range(5):
                a = math.radians(90 + 72*k)
                cu = ell((3.3, 3.3, 3.3), (xm + 5.0*math.cos(a), 5.0*math.sin(a), top + 3.3 - dep)); cut(s, cu)
            cut(s, ell((2.0, 2.0, 2.0), (xm, 0, top + 2.0 - dep*1.1)))
        if i in (2, 4):  # may cuon (xoan oc) 2 ben lung
            for sgn in (1, -1):
                ph = 0 if sgn > 0 else math.pi
                pts = []
                for j in range(40):
                    th = j/39*2.4*math.pi; r = 1.2 + 0.52*th
                    pts.append((xm + r*math.cos(th+ph)*0.9, sgn*11 + r*math.sin(th+ph), top))
                t = tube(pts, [trad]*len(pts)); cut(s, t)
        objs.append(finish(s, cream))
        if i < len(SEG)-1:  # chot noi nhin thay trong khe
            xn = SEG[i+1][0]
            j = rbox((xn - x1 + 6, 14, H*0.55), 3, ((x1+xn)/2, 0, H*0.3))
            objs.append(finish(j, cream))
    head = meta([((66, 0, 38), (25, 27, 24)), ((64, 0, 19), (27, 25, 21)), ((87, 0, 26), (13, 15, 12.5)), ((98, 0, 29), (4, 8, 6)),
                 ((78, 0, 14), (14, 17, 12))])
    horns = []
    for sgn in (1, -1):
        P = [(63, sgn*12, 44), (63, sgn*12, 54), (60, sgn*15, 63), (52, sgn*19, 70), (43, sgn*22, 72), (34, sgn*23.5, 68), (28, sgn*23.5, 60), (25, sgn*23, 51)]
        R = [4.5, 5.0, 8.0, 7.6, 6.6, 5.4, 4.2, 3.0]
        if kc: R = [4.5, 5.0, 8.2, 8.0, 7.2, 6.2, 5.0, 3.8]
        pp, rr = catmull(P, R)
        horns.append(tube(pp, rr))
    if explode:
        for sgn in (1, -1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=5.3, depth=18, location=(62, sgn*12, 49)); cut(head, bpy.context.object)
    objs.append(finish(head, cream))
    for h in horns:
        finish(h, gold, clip=False)
        if explode: h.location = (0, 0, 46)
        objs.append(h)
    for sgn in (1, -1):
        objs.append(finish(ell((6.2, 6.2, 6.2), (82.5, sgn*17, 42.5)), DARK if variant == "color" else cream, 0.12 if variant == "color" else 0.42, clip=False))
        u = Vector((0.62, -sgn*0.3, 0.72)); u.normalize(); hp = Vector((82.5, sgn*17, 42.5)) + u*5.7
        objs.append(finish(ell((1.6, 1.6, 1.6), tuple(hp)), "#FFFFFF" if variant == "color" else cream, 0.3, clip=False))
        ear = ell((9, 19, 5), (60, sgn*37, 45), rot=(math.radians(-sgn*10), 0, math.radians(sgn*-18)))
        objs.append(finish(ear, cream, clip=False))
        objs.append(finish(ell((14, 7.5, 6.2), (88, sgn*24, 6.2)), cream))
        objs.append(finish(ell((15, 12, 16), (-26, sgn*27, 15)), cream))
        objs.append(finish(ell((13, 7, 6.2), (-8, sgn*31, 6.2)), cream))
    for sg in (1, -1):
        objs.append(finish(ell((2.2, 2.6, 3.8), (99.6, sg*5.2, 31.5), rot=(0, 0, math.radians(sg*-15))), DARK if variant == "color" else cream, 0.3, clip=False))
    objs.append(finish(ell((6, 5, 8), (-54, 0, 29)), cream))
    for c_, h_ in [((94, 0, 18), (6, 9, 8)), ((97.5, 0, 10), (5, 7.5, 7)), ((99.5, 0, 4), (3.8, 5, 5))]:
        objs.append(finish(ell(h_, c_), cream))  # rau de
    bpy.ops.mesh.primitive_torus_add(major_radius=19, minor_radius=6, major_segments=72, minor_segments=32, location=(37, 0, 17), rotation=(0, math.radians(90), 0))
    sc = bpy.context.object; sc.scale = (1, 1, 1.18); apply_scale(sc)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(37, 0, 3)); cb = bpy.context.object; cb.scale = (30, 10, 14); cut(sc, cb)
    sc = finish(sc, red)
    knot = finish(ell((6, 5, 6), (37, -26, 27)), red, clip=False)
    flap = finish(rbox((10, 4, 22), 1.6, (38, -29.5, 16), rot=(0, math.radians(6), math.radians(-6))), red)
    parts = [sc, knot, flap]
    if explode:
        for p in parts: p.location = (0, 0, 52)
    objs += parts
    if kc:
        bpy.ops.mesh.primitive_torus_add(major_radius=8.5, minor_radius=3.2, major_segments=64, minor_segments=24, location=(-63, 0, 1.8))
        rg = bpy.context.object; rg.scale = (1, 1, 0.75); apply_scale(rg); objs.append(finish(rg, cream))
    root = bpy.data.objects.new("root", None); bpy.context.scene.collection.objects.link(root)
    root.location = loc; root.scale = (scale,)*3
    for o in objs: o.parent = root
    return root

# ---- canh, anh sang, camera
def reset():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
    for m in list(bpy.data.curves): bpy.data.curves.remove(m)
    for m in list(bpy.data.metaballs): bpy.data.metaballs.remove(m)
def stage(az, el, dist, target=(25, 0, 25), lens=70, ortho=None, res=(1400, 1000), samples=40):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = hexc(BG); bg.inputs[1].default_value = 0.55
    bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, -0.02)); g = bpy.context.object
    g.data.materials.append(mat(BG, 0.9))
    for rot, e in [((math.radians(48), math.radians(8), math.radians(40)), 1.7), ((math.radians(65), 0, math.radians(-130)), 0.5)]:
        d = bpy.data.lights.new("s", 'SUN'); d.energy = e; d.angle = math.radians(10)
        o = bpy.data.objects.new("s", d); sc.collection.objects.link(o); o.rotation_euler = rot
    cam = bpy.data.cameras.new("c"); cam.clip_end = 20000; co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
    t = Vector(target); a = math.radians(az); e = math.radians(el)
    if ortho:
        cam.type = 'ORTHO'; cam.ortho_scale = ortho
    else:
        cam.lens = lens
    if el >= 89:
        co.location = t + Vector((0, 0, dist)); co.rotation_euler = (0, 0, 0)
    else:
        co.location = t + Vector((math.cos(e)*math.cos(a), -math.cos(e)*math.sin(a), math.sin(e)))*dist
        co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
def shoot(name):
    if ONLY and name not in ONLY: return
    bpy.context.scene.render.filepath = f"{OUT}/{name}.png"; bpy.ops.render.render(write_still=True); print("DONE", name)
def ruler(x0, y0, length, ticks_big=50):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x0+length/2, y0, 0.25)); b = bpy.context.object; b.scale = (length, 7, 0.5)
    b.data.materials.append(mat("#B7C2BE", 0.7))
    for i in range(0, int(length)+1, 10):
        big = (i % ticks_big == 0)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x0+i, y0+(0 if big else 1.2), 0.7)); t = bpy.context.object
        t.scale = (0.9, 7 if big else 4.5, 0.5); t.data.materials.append(mat(DARK, 0.7))
        if big:
            bpy.ops.object.text_add(location=(x0+i-3, y0-14, 0.3)); tx = bpy.context.object; tx.data.body = str(i); tx.data.size = 8
            tx.data.materials.append(mat(DARK, 0.7))

def want(n): return (not ONLY) or n in ONLY
if want("v2-side"): reset(); stage(90, 9, 400, target=(25, 0, 32), ortho=215); build("color"); shoot("v2-side")
if want("v2-3q"): reset(); stage(38, 24, 400, target=(25, 0, 30), lens=70); build("color"); shoot("v2-3q")
if want("v2-top"): reset(); stage(90, 90, 470, target=(25, 0, 0), lens=70); build("color"); shoot("v2-top")
if want("v2-mono-3q"): reset(); stage(38, 24, 400, target=(25, 0, 30), lens=70); build("mono"); shoot("v2-mono-3q")
if want("v2-red-3q"): reset(); stage(38, 24, 400, target=(25, 0, 30), lens=70); build("red"); shoot("v2-red-3q")
if want("v2-exploded"): reset(); stage(35, 24, 480, target=(30, 0, 55), lens=70); build("color", explode=True); shoot("v2-exploded")
if want("v2-size"):
    reset(); stage(90, 46, 760, target=(75, -30, 10), lens=70, res=(1600, 1000))
    build("mono"); build("color", kc=True, loc=(150, -70, 0), scale=0.4)
    ruler(-55, -62, 160); ruler(150-77.7*0.4, -105, 75)
    shoot("v2-size")
if want("v2-keychain"): reset(); stage(30, 28, 150, target=(8, -70, 8), lens=70, res=(1000, 800)); build("color", kc=True, loc=(0, -70, 0), scale=0.4); shoot("v2-keychain")
