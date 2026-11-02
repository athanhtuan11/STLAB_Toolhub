# PHAC dang san pham (KHONG phai CAD). Dung khoi minh hoa bo canh/vat de Tuan duyet dang.
# Chay: blender.exe -b --factory-startup -P sketch_forms.py -- <A|B|C> <outdir> [samples]
# Kich thuoc lay tu freecad/params.json (tu the 'nghi'), don vi mm; 1 BU = 100 mm.
import bpy, bmesh, math, sys, json
from mathutils import Vector, Matrix
from pathlib import Path

args = sys.argv[sys.argv.index("--") + 1:]
VAR = args[0]; OUT = Path(args[1]); SAMPLES = int(args[2]) if len(args) > 2 else 64
HERE = Path(__file__).resolve().parent
P = json.load(open(HERE.parent.parent / "freecad" / "params.json", encoding="utf-8"))
CMF = json.load(open(HERE.parent / ("cmf-%s.json" % VAR), encoding="utf-8"))
S = 0.01
COL = {}
for r in CMF["rules"]:
    for n in r["names"]:
        COL[n] = r["color"]

# ---- tham so dang theo phuong an ----
ST = {
 "A": dict(bev=1.5, seg=3, drum_bev=1.2, arm="stadium", head="rbox", head_r=4.0, fore_r=3.0, fin_r=2.0, dome=0, cut=7.0, band=True, hex=False),
 "B": dict(bev=1.8, seg=1, drum_bev=1.8, arm="chamfer", head="chamfer", head_r=2.0, fore_r=2.0, fin_r=1.5, dome=0, cut=6.0, band=False, hex=True),
 "C": dict(bev=5.0, seg=6, drum_bev=3.5, arm="stadium", head="cyl", head_r=15.0, fore_r=8.0, fin_r=3.9, dome=1, cut=9.0, band=False, hex=False),
}[VAR]

# ---- scene co ban ----
for ob in list(bpy.data.objects): bpy.data.objects.remove(ob, do_unlink=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1200, 900
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"

def lin(x):
    x = int(x, 16) / 255
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
def rgba(h): return (lin(h[1:3]), lin(h[3:5]), lin(h[5:7]), 1)

mats = {}
def mat(hexc, rough=0.45):
    k = (hexc, rough)
    if k not in mats:
        m = bpy.data.materials.new("m" + hexc); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = rgba(hexc); b.inputs["Roughness"].default_value = rough
        mats[k] = m
    return mats[k]

def finish(ob, hexc, bevel=0.0, seg=2, rough=0.45, smooth=True, parent=None):
    ob.data.materials.clear(); ob.data.materials.append(mat(hexc, rough))
    if bevel > 0:
        m = ob.modifiers.new("bev", "BEVEL"); m.width = bevel * S; m.segments = seg
        m.limit_method = "ANGLE"; m.angle_limit = math.radians(35); m.profile = 0.5
    for p in ob.data.polygons: p.use_smooth = smooth
    if bevel > 0:
        m = ob.modifiers.new("wn", "WEIGHTED_NORMAL"); m.keep_sharp = True
        ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons))
    if parent: ob.parent = parent
    return ob

def mesh_from(bm, name):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); return ob

def prism(poly, y0, y1, name):
    """poly: danh sach (x,z) mm trong mat XZ, day tu y0 den y1 (mm)."""
    bm = bmesh.new()
    v0 = [bm.verts.new((x * S, y0 * S, z * S)) for x, z in poly]
    f = bm.faces.new(v0)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    vs = [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vs, vec=(0, (y1 - y0) * S, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_from(bm, name)

def box(x0, y0, z0, x1, y1, z1, name="box"):
    return prism([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1, name)

def cyl(r, h, c, axis="Z", name="cyl", seg=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r * S, depth=h * S, location=(c[0] * S, c[1] * S, c[2] * S))
    ob = bpy.context.object; ob.name = name
    if axis == "Y": ob.rotation_euler = (math.pi / 2, 0, 0)
    if axis == "X": ob.rotation_euler = (0, math.pi / 2, 0)
    return ob

def stadium(a, b, r, n=14):
    ax = (b - a).normalized(); nn = Vector((-ax.y, ax.x))
    pts = []
    th0 = math.atan2(nn.y, nn.x)
    for i in range(n + 1):
        t = th0 - math.pi * i / n; pts.append(b + Vector((math.cos(t), math.sin(t))) * r)
    for i in range(n + 1):
        t = th0 + math.pi - math.pi * i / n; pts.append(a + Vector((math.cos(t), math.sin(t))) * r)
    return [(p.x, p.y) for p in pts]

def chamf_poly(a, b, r, c=4.0):
    ax = (b - a).normalized(); nn = Vector((-ax.y, ax.x))
    return [tuple(a - ax * (r - c) + nn * r - ax * 0), tuple(b + ax * (r - c) + nn * r), tuple(b + ax * r + nn * (r - c)),
            tuple(b + ax * r - nn * (r - c)), tuple(b + ax * (r - c) - nn * r), tuple(a - ax * (r - c) - nn * r),
            tuple(a - ax * r - nn * (r - c)), tuple(a - ax * r + nn * (r - c))]

# ---- hinh hoc lay tu params ----
d = P
x1, z1j = d["vai"]["J1"]
t1, phi = d["tu_the"]["nghi"]
a = math.radians(t1); b = math.radians(t1 + phi)
L = d["tay_tren"]["L"]; F = d["cang_tay"]["L"]
j1 = Vector((x1, z1j)); j2 = j1 + Vector((L * math.cos(a), L * math.sin(a)))
dv = Vector((math.cos(b), math.sin(b)))
yt = d["tay_tren"]["y_trong"]; th = d["tay_tren"]["day"]; rad = d["tay_tren"]["r_dau"]
R = d["de"]["trong"]["d_ngoai"] / 2

C = lambda k, dflt="#cccccc": COL.get(k, dflt)
ACC = C("Switch_holder")

# Foot_plate
fp = d["de"]["tam_day"]
foot = box(-fp["rong"] / 2, -fp["rong"] / 2, 0, fp["rong"] / 2, fp["rong"] / 2, fp["cao"], "Foot")
foot.rotation_euler = (0, 0, 0)
# box() ve XZ-prism: doi sang khoi thang dung bang cube
bpy.data.objects.remove(foot, do_unlink=True)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, fp["cao"] / 2 * S)); foot = bpy.context.object
foot.scale = (fp["rong"] * S, fp["rong"] * S, fp["cao"] * S); bpy.ops.object.transform_apply(scale=True)
finish(foot, C("Foot_plate"), bevel=0.8, seg=1)
foot.modifiers["bev"].angle_limit = math.radians(35)
# vanh loe duoi (hoc tron)
ring = cyl(fp["hoc_r"] + 0.0, 0.6, (0, 0, fp["cao"] + 0.2), name="FootRing"); finish(ring, C("Foot_plate"))

# Base_drum
z0, z1 = d["de"]["trong"]["z0"], d["de"]["trong"]["z1"]
drum = cyl(R, z1 - z0, (0, 0, (z0 + z1) / 2), name="Drum"); finish(drum, C("Base_drum"), bevel=ST["drum_bev"], seg=ST["seg"])
if ST["band"]:  # ranh chia mau (soi tren model: rang nho 0,8 mm)
    g = cyl(R + 0.1, 0.8, (0, 0, 30), name="DrumGroove"); finish(g, C("Turntable"), rough=0.6)
if ST["hex"]:  # dai toi mau cho khe thoat nhiet
    g = cyl(R + 0.15, 9, (0, 0, 18), name="DrumBand"); finish(g, "#1b1e21", rough=0.6)
# khe thoat nhiet motor/driver (phia +X hop so): 5 khe 1,6 x 12 mm, sau 0,6
for i in range(5):
    ang = math.radians(-24 + i * 12)
    sl = cyl(0.8, 12, (R * math.cos(ang), R * math.sin(ang), 20), name="Vent%d" % i, seg=12)
    sl.location = (R * math.cos(ang) * S, R * math.sin(ang) * S, 20 * S)
    finish(sl, "#222629", rough=0.7)
# Switch_holder phia sau (-X)
sh = d["bo_tri"]["gia_cong_tac"]
bpy.ops.mesh.primitive_cube_add(size=1, location=(((sh["x"][0] + sh["x"][1]) / 2 - 2) * S, 0, ((sh["z"][0] + sh["z"][1]) / 2) * S))
hold = bpy.context.object; hold.scale = ((sh["x"][1] - sh["x"][0] + 4) * S, (sh["y"][1] - sh["y"][0]) * S, (sh["z"][1] - sh["z"][0]) * S)
bpy.ops.object.transform_apply(scale=True); finish(hold, C("Switch_holder"), bevel=ST["bev"], seg=ST["seg"])

# Turntable
ma = d["mam"]; tw = ma["thap"]
disc = cyl(R, ma["day"], (0, 0, ma["z0"] + ma["day"] / 2), name="Disc"); finish(disc, C("Turntable"), bevel=ST["drum_bev"], seg=ST["seg"])
bpy.ops.mesh.primitive_cube_add(size=1, location=(((tw["x"][0] + tw["x"][1]) / 2) * S, 0, ((ma["z0"] + ma["day"] + tw["z1"]) / 2) * S))
tower = bpy.context.object
tower.scale = ((tw["x"][1] - tw["x"][0]) * S, (tw["y"][1] - tw["y"][0]) * S, (tw["z1"] - ma["z0"] - ma["day"]) * S)
bpy.ops.object.transform_apply(scale=True); finish(tower, C("Turntable"), bevel=ST["bev"] * 1.6, seg=ST["seg"])
if ST["dome"]:
    dm = cyl(R, 0.1, (0, 0, 60), name="x")  # (khong dung)
    bpy.data.objects.remove(dm, do_unlink=True)

# Arm_upper L/R
for y0, nm in ((yt, "Arm_upper_L"), (-yt - th, "Arm_upper_R")):
    poly = stadium(j1, j2, rad) if ST["arm"] == "stadium" else chamf_poly(j1, j2, rad, c=4.0)
    ob = prism(poly, y0, y0 + th, nm); finish(ob, C(nm), bevel=min(ST["bev"], 1.5), seg=ST["seg"])
    # lo truc (dai toi mau tai khop)
    for pj in (j1, j2):
        for yy, sg in ((y0 + th if y0 > 0 else y0, 1 if y0 > 0 else -1),):
            cap = cyl(7.2, 1.6, (pj.x, yy + sg * 0.8, pj.y), axis="Y", name="HornCap"); finish(cap, C("Switch_holder"), bevel=0.5, seg=2)
            sl = box(pj.x - 4.2, 0, pj.y - 0.5, pj.x + 4.2, 0.6, pj.y + 0.5, "slot")
            sl.location.y = (yy + sg * 1.5) * S; finish(sl, "#202326", rough=0.7)

# Forearm (khung cuc bo: x=s doc cang tay, y, z=n)
cf = d["cang_tay"]
pf = [(cf["s_sau"], cf["n_sau"][0]), (cf["s_doi"], cf["n_sau"][0]), (cf["s_doi"], cf["n_truoc"][0]), (F, cf["n_truoc"][0]),
      (F, cf["n_truoc"][1] - ST["cut"]), (F - ST["cut"], cf["n_truoc"][1]), (cf["s_doi"], cf["n_truoc"][1]), (cf["s_doi"], cf["n_sau"][1]), (cf["s_sau"], cf["n_sau"][1])]
fe = bpy.data.objects.new("Frame", None); sc.collection.objects.link(fe)
fe.location = (j2.x * S, 0, j2.y * S); fe.rotation_euler = (0, -b, 0)
fore = prism(pf, cf["y"][0], cf["y"][1], "Forearm"); finish(fore, C("Forearm"), bevel=ST["fore_r"], seg=ST["seg"] + 1, parent=fe)
# tai tri khop J2 (dai toi mau)
hc = cyl(7.2, 1.6, (0, 0, 0), axis="Y", name="HornJ2"); hc.location = (0, (cf["y"][0] - 0.8) * S, 0); finish(hc, C("Switch_holder"), bevel=0.5, seg=2, parent=fe)
# chu STLAB khac sau 0,6 (minh hoa: lap day mau toi)
bpy.ops.object.text_add(location=(0, 0, 0)); tx = bpy.context.object; tx.data.body = "STLAB"
tx.data.size = 6.0 * S; tx.data.extrude = 0.15 * S; tx.data.align_x = "CENTER"; tx.data.align_y = "CENTER"
tx.parent = fe
tx.location = (((cf["s_doi"] + F) / 2) * S, (cf["y"][0] - 0.12) * S, 5.5 * S)
tx.rotation_euler = (math.pi / 2, 0, 0)
tx.data.materials.append(mat("#202326", 0.7))
# Head
dk = d["dau_kep"]; hn = dk["nua"]
if ST["head"] == "cyl":
    head = cyl(hn, dk["dai"], (F + dk["dai"] / 2, 0, 0), axis="X", name="Head"); head.parent = fe
    head.location = ((F + dk["dai"] / 2) * S, 0, 0)
    finish(head, C("Head"), bevel=2.5, seg=4, parent=fe)
else:
    head = prism([(F, -hn), (F + dk["dai"], -hn), (F + dk["dai"], hn), (F, hn)], -hn, hn, "Head")
    finish(head, C("Head"), bevel=ST["head_r"], seg=ST["seg"] + 1, parent=fe)
# nap dau tron co khe (nhu ban tham khao) o mat tren/duoi khong - dat o dau tru 'nap truc vit' phia truoc
# Ngon kep: tiet dien 8, cac goc L/R/D tren vong ban kinh 9; thon dan ve dau (8 -> 5)
ng = d["ngon"]; s0 = F + dk["dai"] + 0.4; s1 = F + ng["L3"]
for key, deg in ng["goc"].items():
    an = math.radians(deg); yy = ng["ban_kinh"] * math.cos(an); nn = ng["ban_kinh"] * math.sin(an)
    w0, w1 = ng["tiet_dien"] / 2, 2.6
    bm = bmesh.new()
    lo = [bm.verts.new((s0 * S, (yy + sx * w0) * S, (nn + sz * w0) * S)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    hi = [bm.verts.new((s1 * S, (yy + sx * w1) * S, (nn + sz * w1) * S)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    for i in range(4): bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    fg = mesh_from(bm, "Finger_" + key); finish(fg, C("Finger_" + key, C("Finger_L")), bevel=ST["fin_r"], seg=ST["seg"], parent=fe)

# ---- anh sang + nen ----
BG = "#ECF1EF"
w = sc.world; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = rgba(BG); w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.002)); gr = bpy.context.object
gr.data.materials.append(mat(BG, 0.9)); gr.is_shadow_catcher = True; sc.render.film_transparent = True
cen = Vector((0.15, 0, 0.55))
for nm, loc, pw, sz in (("Key", (2.5, -3.5, 4.5), 380, 3.0), ("Fill", (-3.5, -2.0, 2.0), 160, 3.5), ("Rim", (-1.0, 3.5, 3.5), 300, 2.5)):
    bpy.ops.object.light_add(type="AREA", location=loc); li = bpy.context.object; li.data.energy = pw; li.data.size = sz
    li.rotation_euler = (cen - li.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.clip_end = 100

def shot(name, az, el, dist, lens=50, ortho=None, tgt=cen):
    az = math.radians(az); el = math.radians(el)
    dr = Vector((math.cos(el) * math.sin(az), -math.cos(el) * math.cos(az), math.sin(el)))
    cam.location = tgt + dr * dist; cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    if ortho: cam.data.type = "ORTHO"; cam.data.ortho_scale = ortho
    else: cam.data.type = "PERSP"
    OUT.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(OUT / ("raw-%s-%s.png" % (VAR, name))); bpy.ops.render.render(write_still=True)

shot("iso", 38, 24, 4.0)
shot("side", 0, 2, 6.0, ortho=2.5, tgt=Vector((0.3, 0, 0.62)))
shot("back34", 145, 22, 4.0)
