# build_owl.py - CAD vo "Cu Bong" ban 1 (ESP32-A1S Audio Kit, 2 loa trai/phai). Blender 5.2 bpy/bmesh, chay nen.
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_owl.py -- out
# He lap rap: mm, +Z len, mat truoc = -Y, x ngang. Mat ranh gioi hai nua vo: mat phang y = Y0.
import bpy, bmesh, math, json, sys
from pathlib import Path
from mathutils import Vector, Matrix

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================ THAM SO (mm)
WALL = 2.4                 # thanh vo
SPEAKER_POCKET_D = 52.6    # loa O52 + khe 0,3/ben
SPEAKER_D, SPEAKER_L = 52.0, 26.0
# 2026-11-06 giu loa bang MEP truoc (Tuan do mep day 5, than < O39) - KHONG VIT (Tuan: khong cho bat vit):
# ron EVA 2 giua mat tam luoi va mat loa; vong ep NGAM XOAY (bayonet): 3 chot tren ong om vanh loa, 3 ranh chu L trong ong tay vong ep;
# an vong ep vao (ep them ron) roi xoay BAY_TWIST, nha ra -> ron day vong ep lui, mat tren chot ty vao vach ranh -> khoa.
FLANGE_T, GASKET_T = 5.0, 1.5          # GASKET_T: khe danh nghia mat luoi - mat loa khi chua ep them
BODY_D_MAX = 39.0          # Tuan 2026-11-06: lo O39 giu duoc mep, than loa lot -> than < O39
SRING_T, RING_ID = 2.4, 42.0   # vong ep loa (SRING_T: RING_T da dung cho vong mat)
BAY_ANG = (90.0, 210.0, 330.0)         # goc 3 chot (vi tri da khoa)
BAY_TWIST = 30.0                       # goc xoay khoa
BPIN_W, BPIN_H, BPIN_T = 4.0, 1.1, 1.5    # chot: rong tiep tuyen, nho ra (ban kinh), day doc truc
BPIN_DZ = 2.5                           # mat duoi chot cach mat cuoi ong om
SLEEVE_CLR, BPIN_CLR, GROOVE_CLR = 0.25, 0.25, 0.3   # khe ong tay / dau chot / ranh doc truc (bang khe: truot 0,2-0,3)
SLEEVE_T, SLEEVE_LEN = 2.4, 5.0        # ong tay: day, dai qua mat cuoi ong om
LIP_PRE, OUT_GAP = 0.3, 0.3            # moi vong ep vao sau mat cuoi ong om (ep ron them); vanh ngoai vong ep cach mat cuoi
GRILLE_HOLE_D, GRILLE_PITCH, GRILLE_ZONE_D = 2.8, 5.6, 56.0
MIC_HOLE_D = 2.0
M3_CLEAR_D, M3_NUT_S, NUT_DEPTH = 3.4, 5.8, 2.8
BUTTON_CAP_D, BUTTON_HOLE_D = 50.0, 50.8
DIFFUSER_T = 0.8
VENT_W, VENT_L = 2.0, 18.0
PCB_BOX = (25.0, 82.0, 73.0)      # x (day linh kien), y (82 theo chieu sau), z
FIT, SLIDE = 0.3, 0.2
Y0 = 0.37                  # mat phang ranh gioi 2 nua
BZ, BR, NT, NB, TAPER = 78.0, (66.0, 56.0, 80.0), 2.2, 4.2, 0.05
FLOOR_CUT = 4.0           # vo cat phang o z = 4; tam de (base plate) day 4 mm dut z 0..4
CZ, CRAD = 81.0, (BR[0] - WALL, BR[1] - WALL, 74.6)   # day khoang trong z = 6,4 (san 2,4), dinh 155,6
CONE_T = math.tan(math.radians(30))
CONE_CLR = 0.3             # khe lo non / ben
# tam bung (trang tri, khong con luoi loa)
BELLY_Z, BELLY_FRONT, BELLY_RF, BELLY_REAR = 48.0, -58.5, 34.2, -42.0
# 2 loa o 2 suon duoi canh, truc x, mat loa ra ngoai
SPK_Z, SPK_XF = 46.0, 69.0          # tam z, mat phang cua vanh loa (|x|)
BZL_RF, BZL_REAR = 36.0, 54.0
BZL_A = 25.0                        # goc non vanh loa (do so voi truc)
BZL_T = math.tan(math.radians(BZL_A))
BZL_RHO = 8.0                       # bo mep mat vanh loa       # ban kinh mat phang, mat sau cua ong non (|x|)
SPK_FACE = SPK_XF - 3.0 - GASKET_T  # mat loa (tam luoi day 3 + ron ep 1,5)
CUP_END = SPK_FACE - FLANGE_T       # mat sau mep loa = mat cuoi ong om = mat truoc vong ep
SPEAKERS = [{"center": [s * (SPK_FACE + LIP_PRE - SPEAKER_L / 2), 0.0, SPK_Z], "axis": "x"} for s in (-1, 1)]   # loa o vi tri DA KHOA (vong ep day vao LIP_PRE)
PCB_CENTER = [0.0, 8.0, 60.0]
EYE_X, EYE_Z, BEAK_Z = 36.5, 108.0, 102.0
RING_D, RING_T = 54.0, 3.0        # vong mat kem
BTN_TOP, BTN_F0, BTN_F1, SEAT_Z, SHELF_TOP = 166.0, 142.3, 144.8, 145.0, 136.3
SCREW_X, SCREW_Y = 24.0, 14.0     # 4 vit tu de len; boss: truoc y=-14 (nua truoc), sau y=+14 (nua sau)
BOSS_TOP = 16.0
PIN_D, PIN_HALF = 2.0, 8.0         # chot dinh vi: doan nhua 1,75 mm

def hexc(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)

# ============================================================ HAM CO BAN
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene

def new_obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); SC.collection.objects.link(o); return o

def cp(o, name=None):
    n = o.copy(); n.data = o.data.copy(); n.name = name or o.name + "_c"; SC.collection.objects.link(n); return n

def bop(a, b, op, keep=False):
    bpy.context.view_layer.update()
    m = a.modifiers.new('bool', 'BOOLEAN'); m.operation = op; m.object = b
    try:
        m.solver = 'MANIFOLD'
    except Exception:
        m.solver = 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(a.evaluated_get(dg))
    a.modifiers.remove(m)
    old = a.data; a.data = me; bpy.data.meshes.remove(old)
    if not keep:
        bpy.data.objects.remove(b)
    return a

def union(a, b): return bop(a, b, 'UNION')
def diff(a, b): return bop(a, b, 'DIFFERENCE')
def inter(a, b): return bop(a, b, 'INTERSECT')

def sup(name, c, rad, nt=2.0, nb=2.0, taper=0.0, rot=0.0, seg=96, rings=48):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        n = nt if z >= 0 else nb
        ln = math.hypot(x, y)
        nl = ln ** (2.0 / n) if ln > 1e-9 else 0.0
        nz = math.copysign(abs(z) ** (2.0 / n), z)
        f = (nl / ln) if ln > 1e-9 else 0.0
        s = 1.0 - taper * nz
        v.co = Vector((x * f * rad[0] * s, y * f * rad[1] * s, nz * rad[2]))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ Matrix.Rotation(math.radians(rot), 4, 'Y'), verts=bm.verts)
    return new_obj(name, bm)

def cyl(name, p0, p1, r0, r1=None, seg=48):
    p0 = Vector(p0); p1 = Vector(p1); d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r0,
                          radius2=r0 if r1 is None else r1, depth=d.length)
    rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2) @ rot, verts=bm.verts)
    return new_obj(name, bm)

def box(name, mn, mx):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((mn[0] if v.co.x < 0 else mx[0], mn[1] if v.co.y < 0 else mx[1], mn[2] if v.co.z < 0 else mx[2]))
    return new_obj(name, bm)

def lathe(name, prof, seg=72, M=None):
    """Tron xoay profile kin [(r, h)...] quanh truc z (r=0 tren truc)."""
    bm = bmesh.new(); rings = []
    for (r, h) in prof:
        if r < 1e-9:
            rings.append([bm.verts.new((0, 0, h))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), h)) for i in range(seg)])
    n = len(prof)
    for k in range(n):
        A, B = rings[k], rings[(k + 1) % n]
        for i in range(seg):
            j = (i + 1) % seg
            if len(A) == 1 and len(B) == 1:
                continue
            if len(A) == 1:
                bm.faces.new((A[0], B[j], B[i]))
            elif len(B) == 1:
                bm.faces.new((A[i], A[j], B[0]))
            else:
                bm.faces.new((A[i], A[j], B[j], B[i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if M is not None:
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return new_obj(name, bm)

def arc(cr, ch, rho, a0, a1, n=8):
    return [(cr + rho * math.cos(math.radians(a0 + (a1 - a0) * i / n)), ch + rho * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def frame(P, axis):
    z = Vector(axis).normalized(); x = Vector((1, 0, 0)); x = (x - z * x.dot(z)).normalized(); y = z.cross(x)
    return Matrix(((x.x, y.x, z.x, P[0]), (x.y, y.y, z.y, P[1]), (x.z, y.z, z.z, P[2]), (0, 0, 0, 1)))

def cyl_local(name, M, u0, u1, r, seg=48):
    return cyl(name, M @ Vector((0, 0, u0)), M @ Vector((0, 0, u1)), r, seg=seg)

def hexp(name, p0, p1):
    return cyl(name, p0, p1, M3_NUT_S / math.sqrt(3), seg=6)

def body_y(x, z):
    nz = (z - BZ) / BR[2]; n = NT if nz >= 0 else NB
    a = 1 - abs(nz) ** n; nl = a ** (1 / n) if a > 0 else 0
    s = 1 - TAPER * nz
    t = nl * nl - (x / (BR[0] * s)) ** 2
    return -BR[1] * s * math.sqrt(max(t, 0))

def body_normal(x, z):
    e = 0.05
    return Vector(((body_y(x + e, z) - body_y(x - e, z)) / (2 * e), -1, (body_y(x, z + e) - body_y(x, z - e)) / (2 * e))).normalized()

def cavity(grow=0.0):
    return sup('cav', (0, 0, CZ), (CRAD[0] + grow, CRAD[1] + grow, CRAD[2] + grow), NT, NB, TAPER)

# ============================================================ THAN NGOAI
OUTER = sup('outer', (0, 0, BZ), BR, NT, NB, TAPER)
for s in (-1, 1):
    union(OUTER, sup('ear', (s * 42, 0, 148), (17, 13, 26), 2, 2, 0.32, rot=s * 20, seg=48, rings=24))
    union(OUTER, sup('wing', (s * 58, 4, 80), (8, 22, 32), 2, 2, -0.3, rot=s * 5, seg=48, rings=24))
PLATE = sup('plate', (0, 0, BZ), BR, NT, NB, TAPER)
inter(PLATE, box('slab', (-200, -200, 0), (200, 200, FLOOR_CUT)))
diff(OUTER, box('flat', (-200, -200, -50), (200, 200, FLOOR_CUT)))
def outer(): return cp(OUTER, 'o')
def clip(o): return inter(o, outer())

S = outer(); diff(S, cavity())

# ---------------- chi tiet noi bo (them truoc khi cat lo) ----------------
EYES = []
for s in (-1, 1):
    P = Vector((s * EYE_X, body_y(s * EYE_X, EYE_Z), EYE_Z))
    M = frame(P, body_normal(s * EYE_X, EYE_Z)); EYES.append(M)
    t = cyl_local('tube', M, -12.9, 2.0, 23.2, seg=60); clip(t); union(S, t)
BEAK_P = Vector((0, body_y(0, BEAK_Z), BEAK_Z))
BEAK_M = frame(BEAK_P, body_normal(0, BEAK_Z) + Vector((0, 0, -0.25)))
t = cyl_local('bcollar', BEAK_M, -5.0, 2.0, 11.8); clip(t); union(S, t)
t = cyl('bcol', (0, 0, SEAT_Z), (0, 0, 175), 31.6, seg=90); clip(t); union(S, t)
t = box("shelf", (-12, 0.9, SHELF_TOP - 3.0), (12, 45, SHELF_TOP)); clip(t); union(S, t)

# ray dung giu bo (2 tam, bo trong 25 theo x) + chan truoc
hx = PCB_BOX[0] / 2 + FIT
pz0, pz1 = PCB_CENTER[2] - PCB_BOX[2] / 2, PCB_CENTER[2] + PCB_BOX[2] / 2
py0, py1 = PCB_CENTER[1] - PCB_BOX[1] / 2, PCB_CENTER[1] + PCB_BOX[1] / 2
for s in (-1, 1):
    a, b = sorted((s * hx, s * (hx + 2.0)))
    t = box('rail', (a, py0 + 6, 5.0), (b, py1 - 6, pz0 + 30)); clip(t); union(S, t)
t = box('stop', (-hx - 2, py0 - FIT - 2, 5.0), (hx + 2, py0 - FIT, pz0 + 12)); clip(t); union(S, t)

# boss vit: 4 tru tren san, dai doc theo mat ranh gioi khong vuot qua (nua truoc y<0, nua sau y>0)
for sx in (-SCREW_X, SCREW_X):
    for sy in (-SCREW_Y, SCREW_Y):
        union(S, cyl('boss', (sx, sy, 5.0), (sx, sy, BOSS_TOP), 7.0, seg=48))

# ============================================================ CAT LO
# lo nut chi khoet qua vanh giu nut (tu SEAT_Z - 1 len). Ban cu khoet tu z 120 -> cat mat gia cong tac trong r 25,4
# (cong tac lo lung) - Tuan hoi 'nut nhan o dau' 2026-11-06 moi thay.
diff(S, cyl('bhole', (0, 0, SEAT_Z - 1.0), (0, 0, 180), BUTTON_HOLE_D / 2, seg=96))
for dx in (-9, 0, 9):
    diff(S, cyl('mic', (dx, -85, 132), (dx, -20, 132), MIC_HOLE_D / 2, seg=16))
for M in EYES:
    diff(S, cyl_local('ehole', M, -30, 12, 17.0, seg=64))
    diff(S, cyl_local('epocket', M, -13.0, -6.0, 20.3, seg=64))
diff(S, cyl_local('beakhole', BEAK_M, -8.0, 12.0, 9.2))
# lo non cho tam bung (nho ngoai, rong vao trong -> yen non, lap tu trong)
def bcone(y, extra): return BELLY_RF + extra + CONE_T * (y - BELLY_FRONT)
diff(S, cyl('bhole2', (0, BELLY_FRONT - 1.5, BELLY_Z), (0, BELLY_REAR, BELLY_Z), bcone(BELLY_FRONT - 1.5, CONE_CLR), bcone(BELLY_REAR, CONE_CLR), seg=96))
# lo non cho vanh loa 2 suon
def zcone(h, extra): return BZL_RF + extra + BZL_T * (SPK_XF - h)
for s in (-1, 1):
    diff(S, cyl('szhole', (s * (SPK_XF + 1.5), 0, SPK_Z), (s * BZL_REAR, 0, SPK_Z), zcone(SPK_XF + 1.5, CONE_CLR), zcone(BZL_REAR, CONE_CLR), seg=96))
for i in range(5):
    x = (i - 2) * 7.0
    diff(S, box('vent', (x - VENT_W / 2, 30, 82 - VENT_L / 2), (x + VENT_W / 2, 70, 82 + VENT_L / 2)))
diff(S, box('usb', (-20, 38, 3), (20, 70, FLOOR_CUT + 12)))
for sx in (-SCREW_X, SCREW_X):
    for sy in (-SCREW_Y, SCREW_Y):
        diff(S, hexp('nut', (sx, sy, BOSS_TOP - NUT_DEPTH), (sx, sy, BOSS_TOP + 0.1)))
        diff(S, cyl('mclear', (sx, sy, 3.0), (sx, sy, BOSS_TOP - NUT_DEPTH + 0.1), M3_CLEAR_D / 2, seg=24))
# chot dinh vi o cac khoi dac (tai, canh, vanh nut): lo O2 sau 8 moi nua
for (px, pz) in ((-43, 142), (43, 142), (-59, 92), (59, 92), (-28.7, 160), (28.7, 160)):
    diff(S, cyl('pin', (px, Y0 - PIN_HALF, pz), (px, Y0 + PIN_HALF, pz), PIN_D / 2, seg=16))

# ============================================================ TACH 2 NUA
SRC = cp(S, 'src')
A = S; B = cp(S, 'back')
inter(A, box('fr', (-300, -300, -50), (300, Y0, 300)))
inter(B, box('bk', (-300, Y0, -50), (300, 300, 300)))
# de (plate): bat 4 vit vao tru, lo chim O9 sau 2,8 duoi, xuyen 3,4
for sx in (-SCREW_X, SCREW_X):
    for sy in (-SCREW_Y, SCREW_Y):
        diff(PLATE, cyl('plh', (sx, sy, -1), (sx, sy, 5), M3_CLEAR_D / 2, seg=24))
        diff(PLATE, cyl('plc', (sx, sy, -1), (sx, sy, 2.8), 4.5, seg=40))

# ============================================================ BO PHAN RIENG
# --- tam bung (trang tri): non nho ngoai, lap tu trong
rf = BELLY_RF; yf = BELLY_FRONT; rho = 3.0; t1 = rho * math.tan(math.radians(30))
prof = [(0, yf), (rf - t1, yf)]
prof += arc(rf - t1, yf + rho, rho, -90, -30, 6)[1:]
r_rear = rf + CONE_T * (BELLY_REAR - yf)
ti = 2.4 / math.cos(math.radians(30))
prof += [(r_rear, BELLY_REAR), (r_rear - ti, BELLY_REAR), (rf - ti + CONE_T * 3.0, yf + 3.0), (0, yf + 3.0)]
BELLY = lathe('belly', prof, seg=96, M=Matrix.Translation((0, 0, BELLY_Z)) @ Matrix.Rotation(-math.pi / 2, 4, 'X'))

# vay long chu V khac nong 0,6 (trang tri)
def vcut(px, pz):
    for sgn in (-1, 1):
        b = box('vc', (-0.8, yf - 1.5, 0.0), (0.8, yf + 0.6, 11.0))
        b.data.transform(Matrix.Translation((px, 0, pz)) @ Matrix.Rotation(sgn * math.radians(38), 4, 'Y'))
        diff(BELLY, b)
for (px, pz) in ((0, BELLY_Z + 8), (-13, BELLY_Z - 5), (13, BELLY_Z - 5), (0, BELLY_Z - 18)):
    vcut(px, pz)

# --- vanh loa (bezel) x2: ong non + luoi Ø56 + hoc loa + 4 vau; dung he cuc bo (z cuc bo = |x|)
def make_bezel():
    h0 = SPK_XF; rho = BZL_RHO
    turn = 90.0 - BZL_A; tb = rho * math.tan(math.radians(turn / 2)); tib = 2.4 / math.cos(math.radians(BZL_A))
    # mep mat luoi: in up mat luoi xuong -> doan bo sat ban gan nam ngang bi treo (slice 2026-11-06: can support 801 mm2).
    # Thay doan bo 90..40 do bang vat 50 do (>= 43 do in khong support), giu doan bo 40..25 do.
    cx = BZL_RF - tb; A_S, CH = 40.0, 50.0
    ax, az = cx + rho * math.cos(math.radians(A_S)), h0 - rho + rho * math.sin(math.radians(A_S))
    pr = [(0, h0), (ax - (h0 - az) / math.tan(math.radians(CH)), h0), (ax, az)]
    pr += arc(cx, h0 - rho, rho, A_S, BZL_A, 6)[1:]
    r_rear = BZL_RF + BZL_T * (SPK_XF - BZL_REAR)
    plate_back = h0 - 3.0
    pr += [(r_rear, BZL_REAR), (r_rear - tib, BZL_REAR), (BZL_RF - tib + BZL_T * 3.0, plate_back),
           (CUP_OR, plate_back), (CUP_OR, CUP_END), (SPEAKER_POCKET_D / 2, CUP_END), (SPEAKER_POCKET_D / 2, plate_back), (0, plate_back)]
    z = lathe('bezel', pr, seg=96)
    # luoi: luoi luc giac, lo Ø2,8 buoc 5,6 trong vung Ø56 (lo nam tron trong vung)
    bm = bmesh.new(); rmax = GRILLE_ZONE_D / 2 - GRILLE_HOLE_D / 2
    dy = GRILLE_PITCH * math.sqrt(3) / 2; cnt = 0
    for j in range(-6, 7):
        for i in range(-6, 7):
            x = i * GRILLE_PITCH + (GRILLE_PITCH / 2 if j % 2 else 0); y = j * dy
            if math.hypot(x, y) <= rmax:
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=14, radius1=GRILLE_HOLE_D / 2, radius2=GRILLE_HOLE_D / 2,
                                      depth=5.0, matrix=Matrix.Translation((x, y, h0 - 1.2)))
                cnt += 1
    gc = new_obj('grille', bm); diff(z, gc)
    # 3 chot ngam xoay tren mat ngoai ong om (he cuc bo, z = |x|; z tang ve phia tam luoi).
    # In up mat luoi xuong: mat +z cua chot (mat CHIU LUC, phang) up xuong ban, nho ra 1,1 mm - cau ngan.
    for a in BAY_ANG:
        R = Matrix.Rotation(math.radians(a), 4, 'Z')
        pz0 = CUP_END + BPIN_DZ
        pn = box('bpin', (CUP_OR - 0.5, -BPIN_W / 2, pz0), (CUP_OR + BPIN_H, BPIN_W / 2, pz0 + BPIN_T)); pn.data.transform(R)
        union(z, pn)
    return z, cnt

def sector(name, r0, r1, z0, z1, a0, a1, n=16):
    """Khoi cung vanh khuyen: ban kinh r0..r1, cao z0..z1, goc a0..a1 (do) quanh truc z."""
    bm = bmesh.new(); V = []
    for i in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * i / n); c, sn = math.cos(t), math.sin(t)
        V.append([bm.verts.new((r * c, r * sn, h)) for (r, h) in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for i in range(n):
        A, B_ = V[i], V[i + 1]
        for k in range(4):
            bm.faces.new((A[k], A[(k + 1) % 4], B_[(k + 1) % 4], B_[k]))
    bm.faces.new(V[0][::-1]); bm.faces.new(V[n])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)

def make_clamp_ring():
    """Vong ep NGAM XOAY (he cuc bo nhu vanh loa) o vi tri DA KHOA: moi O42 ep mat sau mep loa (vao sau mat cuoi ong om LIP_PRE),
    ong tay om ngoai ong om, 3 ranh chu L: doan doc mo o dau ong tay, doan ngang BAY_TWIST do, chot nam o cuoi doan ngang."""
    zB = CUP_END - OUT_GAP - SRING_T; zL = CUP_END + LIP_PRE; zO = CUP_END - OUT_GAP
    rl = SPEAKER_POCKET_D / 2 - 0.3; rsi = CUP_OR + SLEEVE_CLR; rso = rsi + SLEEVE_T; ztop = CUP_END + SLEEVE_LEN
    r = lathe('sring', [(RING_ID / 2, zB), (RING_ID / 2, zL), (rl, zL), (rl, zO), (rsi, zO), (rsi, ztop), (rso, ztop), (rso, zB)], seg=96)
    pz0 = CUP_END + BPIN_DZ; pz1 = pz0 + BPIN_T                 # chot (vi tri khoa): mat +z chot ty vao vach tren ranh
    rg = CUP_OR + BPIN_H + BPIN_CLR                               # day ranh
    half = math.degrees((BPIN_W / 2 + 0.4) / rsi)                 # nua be rong ranh theo goc (khe 0,4 hai ben chot)
    for a in BAY_ANG:
        g0, g1 = pz0 - GROOVE_CLR, pz1                            # ranh ngang: duoi co khe de xoay khi an them
        diff(r, sector('gh', rsi - 0.5, rg, g0, g1, a - BAY_TWIST - half, a + half, 12))
        diff(r, sector('gv', rsi - 0.5, rg, g0, ztop + 0.5, a - BAY_TWIST - half, a - BAY_TWIST + half, 4))
    return r
CUP_OR = SPEAKER_POCKET_D / 2 + 2.7  # ban kinh ngoai ong om
BEZEL_LOCAL, GRILLE_N = make_bezel()
SRING_LOCAL = make_clamp_ring()
def bezel_world(s):
    M = Matrix.Translation((0, 0, SPK_Z)) @ Matrix.Rotation(math.radians(90 * s), 4, 'Y')
    o = cp(BEZEL_LOCAL, 'bezel%d' % s); o.data.transform(M); return o
BEZELS = [bezel_world(-1), bezel_world(1)]
def sring_world(s):
    M = Matrix.Translation((0, 0, SPK_Z)) @ Matrix.Rotation(math.radians(90 * s), 4, 'Y')
    o = cp(SRING_LOCAL, 'sring%d' % s); o.data.transform(M); return o
SRINGS = [sring_world(-1), sring_world(1)]

# --- mo
bp = [(0, -9.0), (12, -9.0), (12, -6.2), (9, -6.2), (9, 0.0)]
bp += [(9 * math.cos(math.radians(a)), 7.5 * math.sin(math.radians(a))) for a in range(10, 91, 10)]
BEAK = lathe('beak', bp[:-1] + [(0, 7.5)], seg=64, M=BEAK_M)

# --- nut
cp_ = [(0, BTN_TOP), (19, BTN_TOP)] + arc(19, BTN_TOP - 6, 6, 90, 0, 8)[1:] + [(25, BTN_F1), (29, BTN_F1), (29, BTN_F0), (0, BTN_F0)]
CAP = lathe('cap', cp_, seg=96)
union(CAP, cyl('pad', (0, 8, BTN_F0 - 1.5), (0, 8, BTN_F0 + 0.3), 8.0, seg=48))

# --- kinh khuech tan mat (1 cai); vanh giu
dp = [(0, -6.0), (20, -6.0), (20, -9.8), (18.8, -9.8), (18.8, -6.0 - DIFFUSER_T), (0, -6.0 - DIFFUSER_T)]
DIFFS = [lathe('diff%d' % i, dp, seg=72, M=M) for i, M in enumerate(EYES)]

# --- vong mat kem (x2): dan len vo, mat sau theo be mat than, mat truoc phang; in mat truoc xuong
RINGS = []
for M in EYES:
    r = cyl_local('ring', M, -16.0, 16.0, RING_D / 2, seg=96)
    inter(r, sup('bb', (0, 0, BZ), (BR[0] + RING_T, BR[1] + RING_T, BR[2] + RING_T), NT, NB, TAPER))
    diff(r, outer())
    diff(r, cyl_local('rw', M, -30, 12, 17.3, seg=72))
    RINGS.append(r)

# ============================================================ XUAT STL (huong in)
def export_obj(o, T, path, recenter=True):
    c = cp(o, 'exp'); c.data.transform(T)
    xs = [v.co.x for v in c.data.vertices]; ys = [v.co.y for v in c.data.vertices]; zs = [v.co.z for v in c.data.vertices]
    c.data.transform(Matrix.Translation((-(max(xs) + min(xs)) / 2, -(max(ys) + min(ys)) / 2, -min(zs))))
    for ob in bpy.context.view_layer.objects:
        ob.select_set(False)
    c.select_set(True); bpy.context.view_layer.objects.active = c
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
    d = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    print("EXPORT %s %.1f x %.1f x %.1f" % (path.name, *d))
    bpy.data.objects.remove(c)

def Mx(rows): return Matrix(rows)
T_front = Mx(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, Y0), (0, 0, 0, 1)))
T_back = Mx(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, -Y0), (0, 0, 0, 1)))
T_belly = Mx(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, -BELLY_FRONT), (0, 0, 0, 1)))
T_cap = Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, BTN_TOP), (0, 0, 0, 1)))
T_beak = Matrix.Translation((0, 0, 9.0)) @ BEAK_M.inverted()
T_diff = Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, -6.0), (0, 0, 0, 1))) @ EYES[1].inverted()
export_obj(A, T_front, OUT / "shell-front.stl")
export_obj(B, T_back, OUT / "shell-back.stl")
export_obj(BELLY, T_belly, OUT / "belly.stl")
export_obj(BEAK, T_beak, OUT / "beak.stl")
export_obj(CAP, T_cap, OUT / "button-cap.stl")
export_obj(DIFFS[1], T_diff, OUT / "eye-diffuser.stl")
T_ring = EYES[1].inverted()
export_obj(RINGS[1], T_ring, OUT / "eye-ring.stl")
export_obj(PLATE, Mx(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))), OUT / "base-plate.stl")
export_obj(BEZEL_LOCAL, Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, SPK_XF), (0, 0, 0, 1))), OUT / "speaker-bezel.stl")
export_obj(SRING_LOCAL, Matrix.Identity(4), OUT / "speaker-ring.stl")   # day vong ep xuong ban, ong tay huong len

# lap rap
asm = bmesh.new()
for o in [A, B, PLATE, BELLY, BEAK, CAP] + BEZELS + SRINGS + DIFFS + RINGS:
    asm.from_mesh(o.data)
am = bpy.data.meshes.new('asm'); asm.to_mesh(am); asm.free()
ao = bpy.data.objects.new('asm', am); SC.collection.objects.link(ao)
for ob in bpy.context.view_layer.objects:
    ob.select_set(False)
ao.select_set(True); bpy.context.view_layer.objects.active = ao
bpy.ops.wm.stl_export(filepath=str(OUT / "owl-assembled.stl"), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
bpy.data.objects.remove(ao)

params = dict(wall=WALL, speaker_pocket_d=SPEAKER_POCKET_D, grille_hole_d=GRILLE_HOLE_D, mic_hole_d=MIC_HOLE_D, m3_clear_d=M3_CLEAR_D,
              m3_nut_s=M3_NUT_S, button_cap_d=BUTTON_CAP_D, button_hole_d=BUTTON_HOLE_D, diffuser_t=DIFFUSER_T, vent_w=VENT_W,
              speakers=SPEAKERS, pcb_center=PCB_CENTER, pcb_box=list(PCB_BOX),
              split_plane_y=Y0, grille_holes_per_speaker=GRILLE_N, speaker_dims=[SPEAKER_D, SPEAKER_L], pcb_dims_xyz=list(PCB_BOX),
              belly=dict(z=BELLY_Z, front_y=BELLY_FRONT, rf=BELLY_RF), eye=dict(x=EYE_X, z=EYE_Z), beak_z=BEAK_Z,
              screws=dict(x=SCREW_X, y=SCREW_Y, m3_nut_depth=NUT_DEPTH),
              speaker_clamp=dict(flange_t=FLANGE_T, gasket_t=GASKET_T, body_d_max=BODY_D_MAX, ring_t=SRING_T, ring_id=RING_ID,
                                 bayonet=dict(n=len(BAY_ANG), twist=BAY_TWIST, pin_w=BPIN_W, pin_h=BPIN_H, pin_t=BPIN_T, sleeve_clr=SLEEVE_CLR, pin_clr=BPIN_CLR,
                                 groove_clr=GROOVE_CLR, lip_pre=LIP_PRE, out_gap=OUT_GAP, sleeve_t=SLEEVE_T), gasket_locked=round(GASKET_T - LIP_PRE, 3),
                                 face_abs_x=SPK_FACE, cup_end_abs_x=CUP_END), pins=dict(d=PIN_D, half_depth=PIN_HALF), floor_cut=FLOOR_CUT, cone_clearance=CONE_CLR, fit=FIT, slide=SLIDE)
(OUT / "owl-params.json").write_text(json.dumps(params, indent=1), encoding="utf-8")

# ============================================================ ANH XEM TRUOC (Eevee, dung STL that)
import numpy as np, shutil
PCOL = dict(shell='#F6BE9A', cream='#FFF3DF', butter='#FFC857', white='#FFFFFF', spk='#6B6F78', pcb='#2E8B57')
TMP = OUT / "_tmp"; TMP.mkdir(exist_ok=True)
def dump(o, name):
    for ob in bpy.context.view_layer.objects:
        ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.wm.stl_export(filepath=str(TMP / (name + ".stl")), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
spk = []
for sp in SPEAKERS:
    c = Vector(sp["center"]); sg = 1 if c.x > 0 else -1; fx = c.x + sg * SPEAKER_L / 2
    so = cyl('spk', Vector((fx - sg * FLANGE_T, c.y, c.z)), Vector((fx, c.y, c.z)), SPEAKER_D / 2, seg=48)
    union(so, cyl('spkb', Vector((fx - sg * SPEAKER_L, c.y, c.z)), Vector((fx - sg * (FLANGE_T - 0.5), c.y, c.z)), BODY_D_MAX / 2 - 3, seg=48)); spk.append(so)
# cong tac tactile 6 x 6 giu cho (KEY4 noi song song, Tuan 2026-11-06): de tren gia, chan nut ep o (0, 8); cao 4,3 (TODO do)
SW_H = 4.3
swo = box('sw', (-3.0, 5.0, SHELF_TOP), (3.0, 11.0, SHELF_TOP + 3.5)); union(swo, cyl('swst', (0, 8, SHELF_TOP + 3.0), (0, 8, SHELF_TOP + SW_H), 1.75, seg=24))
pcbo = box('pcb', (-PCB_BOX[0] / 2, PCB_CENTER[1] - PCB_BOX[1] / 2, PCB_CENTER[2] - PCB_BOX[2] / 2), (PCB_BOX[0] / 2, PCB_CENTER[1] + PCB_BOX[1] / 2, PCB_CENTER[2] + PCB_BOX[2] / 2))
ITEMS = [(A, 'front', 'shell', (0, -75, 0)), (B, 'back', 'shell', (0, 75, 0)), (PLATE, 'plate', 'cream', (0, 0, -45)), (BELLY, 'belly', 'cream', (0, -130, 0)),
         (BEAK, 'beak', 'butter', (0, -135, 30)), (CAP, 'cap', 'butter', (0, 0, 55)), (BEZELS[0], 'bz0', 'shell', (-105, 0, 0)), (BEZELS[1], 'bz1', 'shell', (105, 0, 0)), (SRINGS[0], 'sr0', 'cream', (-25, 0, 0)), (SRINGS[1], 'sr1', 'cream', (25, 0, 0)),
         (DIFFS[0], 'd0', 'white', (-30, -110, 25)), (DIFFS[1], 'd1', 'white', (30, -110, 25)), (RINGS[0], 'r0', 'cream', (-40, -100, 0)), (RINGS[1], 'r1', 'cream', (40, -100, 0)),
         (spk[0], 's0', 'spk', (-55, 0, 0)), (spk[1], 's1', 'spk', (55, 0, 0)), (pcbo, 'pcb', 'pcb', (0, 0, 0)), (swo, 'sw', 'spk', (0, 0, 30))]
for o, n, c, off in ITEMS:
    dump(o, n)
# ban lap rap DO DUOC (Tuan 2026-11-06): moi chi tiet 1 STL o dung vi tri lap (mm) -> export_cad.py ra .blend + STEP
ASM_NAMES = dict(front="shell-front", back="shell-back", plate="base-plate", belly="belly", beak="beak", cap="button-cap",
                 bz0="speaker-bezel-L", bz1="speaker-bezel-R", sr0="speaker-ring-L", sr1="speaker-ring-R", d0="eye-diffuser-L",
                 d1="eye-diffuser-R", r0="eye-ring-L", r1="eye-ring-R", s0="speaker-dummy-L", s1="speaker-dummy-R", pcb="pcb-dummy", sw="switch-6x6-dummy")
(OUT / "asm").mkdir(exist_ok=True)
import shutil
for _, n, _, _ in ITEMS:
    shutil.copyfile(TMP / (n + ".stl"), OUT / "asm" / (ASM_NAMES[n] + ".stl"))

def fresh_scene(res):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = hexc('#FBF3E8'); bg.inputs['Strength'].default_value = 0.45
    for nm, loc, en in (('key', (-300, -400, 500), 2.2), ('fill', (400, -300, 200), 0.8), ('rim', (100, 400, 400), 1.0)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = en
        lo = bpy.data.objects.new(nm, ld); sc.collection.objects.link(lo)
        lo.rotation_euler = (-Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return sc
def load_items(sc, which, offs):
    for o, n, c, off in ITEMS:
        if n not in which:
            continue
        bpy.ops.wm.stl_import(filepath=str(TMP / (n + ".stl")))
        ob = bpy.context.selected_objects[0]
        m = bpy.data.materials.new(n); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = hexc(PCOL[c]); b.inputs['Roughness'].default_value = 0.6
        ob.data.materials.append(m)
        if offs:
            ob.location = off
def cam_at(sc, target, az, el, dist, lens=60):
    cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.clip_end = 5000
    cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el))))
    cam.location = Vector(target) + d * dist
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
def render_png(sc, path):
    sc.render.filepath = str(path); sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
def merge(p1, p2, out):
    imgs = []
    for p in (p1, p2):
        im = bpy.data.images.load(str(p)); a = np.empty(im.size[0] * im.size[1] * 4, dtype=np.float32); im.pixels.foreach_get(a)
        imgs.append(a.reshape(im.size[1], im.size[0], 4))
    big = np.concatenate(imgs, axis=1)
    nim = bpy.data.images.new('m', width=big.shape[1], height=big.shape[0], alpha=True)
    nim.pixels.foreach_set(big.reshape(-1)); nim.filepath_raw = str(out); nim.file_format = 'PNG'; nim.save()

ASM = ['front', 'back', 'plate', 'belly', 'beak', 'cap', 'bz0', 'bz1', 'sr0', 'sr1', 'd0', 'd1', 'r0', 'r1']
sc = fresh_scene((800, 1200)); load_items(sc, ASM, False)
cam_at(sc, (0, 0, 85), -32, 12, 560); render_png(sc, OUT / "_v1.png")
bpy.data.objects.remove(sc.camera)
cam_at(sc, (0, 0, 85), 148, 18, 560); render_png(sc, OUT / "_v2.png")
merge(OUT / "_v1.png", OUT / "_v2.png", OUT / "owl-preview.png")
sc = fresh_scene((1600, 1200)); load_items(sc, [n for _, n, _, _ in ITEMS], True)
cam_at(sc, (0, -20, 75), -30, 22, 950, 70); render_png(sc, OUT / "owl-exploded.png")
for f in ("_v1.png", "_v2.png"):
    (OUT / f).unlink()
shutil.rmtree(TMP, ignore_errors=True)
print("BUILD OK")
