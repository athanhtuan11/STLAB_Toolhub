# Phac dang switch-clicker (chi de duyet anh, KHONG phai CAD). 1 don vi = 1 mm.
# Chay: blender -b -P make_concepts.py -- <outdir> [ten-anh,...]
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index("--")+1:]
OUT = argv[0]; ONLY = argv[1].split(",") if len(argv) > 1 else None
BODY, PINE, BG, DARK = "#3B4046", "#1E5A45", "#DCE4E1", "#2A2E33"
BEAN, ARTI, CREAM, GOLD, RED = "#6B4A35", "#8CA66E", "#F2ECDC", "#E8B33A", "#C8372D"
BH = 14.0; Z0 = BH + 1.5          # chan keycap cach mat tren 1,5 (GIA DINH)
def hexc(h):
    h = h.lstrip('#'); return tuple(pow(int(h[i:i+2], 16)/255, 2.2) for i in (0, 2, 4)) + (1,)
MATS = {}
def mat(c, rough=0.45):
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
def bake(o):
    act(o); o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
def paint(o, color, rough=0.45):
    bake(o); o.data.materials.clear(); o.data.materials.append(mat(color, rough))
    act(o); bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40)); return o
def apply_all(o): act(o); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
def ell(h, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = h; apply_all(o); return o
def bevel(o, r, seg=8):
    md = o.modifiers.new("b", 'BEVEL'); md.width = r; md.segments = seg; md.limit_method = 'NONE'
    act(o); bpy.ops.object.modifier_apply(modifier="b"); return o
def rbox(d, r, loc):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.scale = d; apply_all(o); return bevel(o, r)
def cyl(r, h, loc, v=64, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=h, location=loc, rotation=rot); return bpy.context.object
def cut(o, c):
    act(o); md = o.modifiers.new("x", 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = c
    bpy.ops.object.modifier_apply(modifier="x"); bpy.data.objects.remove(c, do_unlink=True)
def slice_z(o, z, keep):
    bake(o); bm = bmesh.new(); bm.from_mesh(o.data)
    g = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=g, plane_co=(0, 0, z), plane_no=(0, 0, 1), clear_inner=(keep == 'above'), clear_outer=(keep == 'below'))
    ed = [e for e in bm.edges if e.is_boundary]
    if ed: bmesh.ops.triangle_fill(bm, use_beauty=True, edges=ed)
    bm.to_mesh(o.data); bm.free(); return o
def dup(o):
    n = o.copy(); n.data = o.data.copy(); bpy.context.scene.collection.objects.link(n); return n
def tube(pts, rads):
    cu = bpy.data.curves.new("t", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 1.0; cu.bevel_resolution = 8; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p, w, r in zip(sp.points, pts, rads): p.co = (w[0], w[1], w[2], 1); p.radius = r
    o = bpy.data.objects.new("t", cu); bpy.context.scene.collection.objects.link(o)
    act(o); bpy.ops.object.convert(target='MESH'); return bpy.context.view_layer.objects.active
def catmull(P, R, n=10):
    out = []; ro = []; P2 = [P[0]] + P + [P[-1]]; R2 = [R[0]] + R + [R[-1]]
    for i in range(1, len(P2)-2):
        for k in range(n):
            t = k/n
            def cr(a, b, c, d): return 0.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3)
            out.append(tuple(cr(P2[i-1][j], P2[i][j], P2[i+1][j], P2[i+2][j]) for j in range(3))); ro.append(cr(R2[i-1], R2[i], R2[i+1], R2[i+2]))
    out.append(P[-1]); ro.append(R[-1]); return out, ro

# ---------------- THAN ----------------
def make_body(kind):
    """tra ve (tam_switch_xy, [phan tren], [nap day])"""
    if kind == "A":   # da cuoi
        o = rbox((34, 30, BH), 4.8, (0, 0, BH/2)); ring = (-19.5, 17.0); sw = (0, 0)
    elif kind == "B": # luc giac bo
        o = cyl(20, BH, (0, 0, BH/2), v=6); bevel(o, 5.5); ring = (-16.8, 16.8); sw = (0, 0)
    else:             # C vien thuoc
        o = rbox((46, 26, BH), 6.2, (0, 0, BH/2)); ring = (-27.5, 0); sw = (5, 0)
    bot = dup(o); slice_z(o, 2.2, 'above'); slice_z(bot, 2.2, 'below')
    paint(o, BODY, 0.55); paint(bot, PINE, 0.55)
    r = cyl(6.2, 4, (ring[0], ring[1], BH-2)); cut(r, cyl(2.7, 8, (ring[0], ring[1], BH-2), v=48)); bevel(r, 1.0, 4); paint(r, BODY, 0.55)
    return sw, [o, r], [bot]

def make_switch(sw):
    """KHOI GIA DINH 15,6 x 15,6: duoi tam 5,5 | tren tam 5,5 | tru chu thap 4 (GIA DINH)"""
    x, y = sw; L = []
    L.append(paint(rbox((15.6, 15.6, 5.5), 0.5, (x, y, BH-1.5-2.75)), "#B9BEC2", 0.5))
    L.append(paint(rbox((15.6, 15.6, 5.5), 0.5, (x, y, BH+2.75)), "#C9CED1", 0.4))
    L.append(paint(rbox((4.0, 4.0, 4.0), 0.3, (x, y, BH+5.5+2.0)), "#2A2E33", 0.4))
    return L

# ---------------- KEYCAP (chan o z = Z0, tam tai x,y) ----------------
def cap_round(x, y, color=CREAM, text="TUAN"):
    o = cyl(11, 10+2.8, (x, y, Z0-1.4+5), v=96); bevel(o, 2.8, 8); slice_z(o, Z0, 'above')
    top = Z0+10
    bpy.ops.object.text_add(location=(x, y, top-0.6)); t = bpy.context.object
    t.data.body = text; t.data.size = 5.6; t.data.extrude = 0.6; t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'
    act(t); bpy.ops.object.convert(target='MESH'); t = bpy.context.object
    cut(o, t); return [paint(o, color, 0.4)]
def cap_bean(x, y):
    a, b, c, zc = 12.5, 10.4, 10.0, Z0+1.5
    o = ell((a, b, c), (x, y, zc)); slice_z(o, Z0, 'above')
    pts = []
    for i in range(25):
        u = -9.6 + i*0.8; v = 2.4*math.sin(u/9.6*math.pi)
        s = max(0.0, 1-(u/a)**2-(v/b)**2); pts.append((x+u, y+v, zc+c*math.sqrt(s)+0.1))
    cut(o, tube(pts, [1.15]*len(pts))); return [paint(o, BEAN, 0.35)]
def cap_arti(x, y):
    L = [cyl(11.2, 3.2, (x, y, Z0+1.6), v=64)]
    def ring(n, r, T, zp, hx, hy, hz, off):
        for k in range(n):
            ph = (k+off)*2*math.pi/n; T_ = math.radians(T)
            d = Vector((math.sin(T_)*math.cos(ph), math.sin(T_)*math.sin(ph), math.cos(T_)))
            xa = Vector((-math.sin(ph), math.cos(ph), 0)); ya = d.cross(xa)
            m = Matrix(((xa.x, ya.x, d.x), (xa.y, ya.y, d.y), (xa.z, ya.z, d.z)))
            L.append(ell((hx, hy, hz), (x+r*math.cos(ph), y+r*math.sin(ph), zp), m.to_euler()))
    ring(11, 7.6, 66, Z0+4.6, 3.4, 1.3, 5.0, 0)
    ring(9, 5.0, 42, Z0+6.4, 3.0, 1.3, 5.0, 0.5)
    ring(6, 2.5, 18, Z0+7.6, 2.6, 1.2, 4.6, 0.2)
    L.append(ell((2.4, 2.4, 3.0), (x, y, Z0+10.6)))
    return [paint(o, ARTI, 0.4) for o in L]
def cap_goat(x, y):
    zc = Z0+2.5; L = []; H = []
    head = ell((12.5, 11.0, 8.5), (x, y, zc)); slice_z(head, Z0, 'above'); L.append(head)
    L.append(ell((4.4, 3.2, 2.7), (x, y-9.4, zc-0.3)))
    for s in (-1, 1):
        L.append(ell((4.8, 1.6, 2.4), (x+s*12.4, y-0.5, Z0+6.2), (0, math.radians(s*22), math.radians(-s*14))))
    out = [paint(o, CREAM, 0.4) for o in L]
    for s in (-1, 1):
        pts, rads = catmull([(x+s*5.0, y+1.0, Z0+9.0), (x+s*7.2, y+2.2, Z0+12.2), (x+s*9.0, y+1.0, Z0+14.8), (x+s*8.6, y-1.6, Z0+15.8)], [2.4, 2.0, 1.4, 0.7])
        H.append(paint(tube(pts, rads), GOLD, 0.38))
        out.append(paint(ell((1.5, 1.0, 1.9), (x+s*4.8, y-9.0, Z0+6.6)), DARK, 0.3))
        out.append(paint(ell((0.8, 0.6, 0.9), (x+s*1.4, y-12.0, zc-0.4)), DARK, 0.3))
    return out + H

def build(kind, cap, loc=(0, 0), explode=False, text="TUAN", capcolor=CREAM):
    sw, top, bot = make_body(kind)
    swl = make_switch(sw)
    if cap == "round": cl = cap_round(sw[0], sw[1], capcolor, text)
    else: cl = {"bean": cap_bean, "arti": cap_arti, "goat": cap_goat}[cap](sw[0], sw[1])
    lift = 20 if explode else 0
    for objs, dz in [(top, lift), (bot, 0), (swl, lift+14 if explode else 0), (cl, lift+34 if explode else 0)]:
        for o in objs: o.location = (o.location.x+loc[0], o.location.y+loc[1], o.location.z+dz)

def reset():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
    for m in list(bpy.data.curves): bpy.data.curves.remove(m)
def stage(az, el, dist, target, lens=70, ortho=None, res=(1400, 1000), samples=40):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = hexc(BG); bg.inputs[1].default_value = 0.55
    bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, -0.02)); g = bpy.context.object; g.data.materials.append(mat(BG, 0.9))
    for rot, e in [((math.radians(48), math.radians(8), math.radians(40)), 1.7), ((math.radians(65), 0, math.radians(-130)), 0.5)]:
        d = bpy.data.lights.new("s", 'SUN'); d.energy = e; d.angle = math.radians(10)
        o = bpy.data.objects.new("s", d); sc.collection.objects.link(o); o.rotation_euler = rot
    cam = bpy.data.cameras.new("c"); cam.clip_end = 20000; co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
    t = Vector(target); a = math.radians(az); e = math.radians(el)
    if ortho: cam.type = 'ORTHO'; cam.ortho_scale = ortho
    else: cam.lens = lens
    if el >= 89: co.location = t + Vector((0, 0, dist)); co.rotation_euler = (0, 0, 0)
    else:
        co.location = t + Vector((math.cos(e)*math.sin(a), -math.cos(e)*math.cos(a), math.sin(e)))*dist
        co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
def shoot(name):
    bpy.context.scene.render.filepath = f"{OUT}/{name}.png"; bpy.ops.render.render(write_still=True); print("DONE", name)
def ruler(x0, y0, length, step=10, big=50):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x0+length/2, y0, 0.25)); b = bpy.context.object; b.scale = (length, 5, 0.5); b.data.materials.append(mat("#B7C2BE", 0.7))
    for i in range(0, int(length)+1, step):
        bg_ = (i % big == 0)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x0+i, y0+(0 if bg_ else 1.0), 0.7)); t = bpy.context.object
        t.scale = (0.7, 5 if bg_ else 3, 0.5); t.data.materials.append(mat(DARK, 0.7))
        if bg_:
            bpy.ops.object.text_add(location=(x0+i-2.5, y0-9, 0.3)); tx = bpy.context.object; tx.data.body = str(i); tx.data.size = 5.5; tx.data.materials.append(mat(DARK, 0.7))
def want(n): return (not ONLY) or n in ONLY

# camera: az=0 nhin tu -Y (mat truoc cua dau de o -Y); az>0 xoay sang +X
if want("variants"):
    reset(); stage(15, 38, 500, (0, 0, 8), res=(1800, 900))
    build("A", "round", (-62, 0), text="A"); build("B", "round", (0, 0), text="B"); build("C", "round", (66, 0), text="C"); shoot("variants")
if want("set4"):
    reset(); stage(10, 32, 540, (0, -6, 14), res=(2000, 900))
    for i, c in enumerate(["bean", "arti", "goat", "round"]): build("A", c, (-93+i*62, 0), text="TUAN", capcolor=RED)
    shoot("set4")
if want("side"): reset(); stage(0, 4, 400, (0, 0, 16), ortho=80, res=(1200, 1000)); build("A", "bean"); shoot("side")
if want("q34"): reset(); stage(38, 26, 190, (0, 0, 14), res=(1200, 1000)); build("A", "bean"); shoot("q34")
if want("top"): reset(); stage(0, 90, 330, (0, 0, 0), ortho=64, res=(1200, 1000)); build("A", "goat"); shoot("top")
if want("exploded"): reset(); stage(32, 16, 300, (0, 0, 40), res=(1200, 1000)); build("A", "bean", explode=True); shoot("exploded")
if want("size"):
    reset(); stage(0, 52, 600, (0, -16, 0), res=(1600, 800), ortho=150)
    build("A", "goat", (-30, 0)); build("A", "bean", (30, 0)); ruler(-60, -40, 120, 10, 50); shoot("size")
