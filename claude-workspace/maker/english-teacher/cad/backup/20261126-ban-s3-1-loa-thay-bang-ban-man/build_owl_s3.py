# build_owl_s3.py - CAD vo "Cu Bong" ban S3 (ESP32-S3, 1 loa o bung, mic o tran). Blender 5.2 bpy/bmesh.
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_owl_s3.py -- out-s3
# He lap rap: mm, +Z len, mat truoc = -Y, x ngang. Mat ranh gioi hai nua vo: mat phang y = Y0.
import bpy, bmesh, math, json, sys, os, shutil
from pathlib import Path
from mathutils import Vector, Matrix

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================ THAM SO (mm)
WALL = 2.4                 # thanh vo
SPEAKER_POCKET_D = 52.6    # loa O52 + khe 0,3/ben
SPEAKER_D, SPEAKER_L = 52.0, 26.0

# Co cau giu loa bang mep truoc (Tuan do mep day 5, than < O39) - KHONG VIT:
# ron EVA giua mat tam luoi va mat loa; vong ep NGAM XOAY (bayonet): 3 chot tren ong om vanh loa, 3 ranh chu L trong ong tay vong ep;
# an vong ep vao (ep them ron) roi xoay BAY_TWIST, nha ra -> ron day vong ep lui, mat tren chot ty vao vach ranh -> khoa.
FLANGE_T, GASKET_T = 5.0, 1.5          # GASKET_T: khe danh nghia mat luoi - mat loa khi chua ep them
BODY_D_MAX = 39.0                      # than loa < O39
SRING_T, RING_ID = 2.4, 47.0           # vong ep loa. 2026-11-18 Tuan: loa khong chui qua lo O42 -> O47 (moi de mep loa 2,5/ben), bo 4 lay PETG
BAY_ANG = (90.0, 210.0, 330.0)         # goc 3 chot (vi tri da khoa)
BAY_TWIST = 30.0                       # goc xoay khoa
BPIN_W, BPIN_H, BPIN_T = 4.0, 1.1, 1.5 # chot: rong tiep tuyen, nho ra, day doc truc
BPIN_DZ = 2.5                          # mat duoi chot cach mat cuoi ong om
SLEEVE_CLR, BPIN_CLR, GROOVE_CLR = 0.25, 0.25, 0.3
SLEEVE_T, SLEEVE_LEN = 2.4, 5.0
LIP_PRE, OUT_GAP = 0.3, 0.3
GRILLE_HOLE_D, GRILLE_PITCH, GRILLE_ZONE_D = 2.8, 5.6, 56.0
MIC_HOLE_D = 2.0
M3_CLEAR_D, M3_NUT_S, NUT_DEPTH = 3.4, 5.8, 2.8
BUTTON_CAP_D, BUTTON_HOLE_D = 50.0, 50.8
DIFFUSER_T = 0.8
VENT_W, VENT_L = 2.0, 18.0

# S3 LINH KIEN:
# Bo ESP32-S3: hop giu cho 72 x 29 x 16 (pcb_box), dung dung o nua sau, dau USB xuong duoi
PCB_BOX = (29.0, 72.0, 16.0)          # x rong, y DAI (nam ngang, dau USB ve LUNG +y), z day
PCB_Y_USB = 44.7                      # mat cong USB (y); dau truoc bo o y = 44,7 - 72 = -27,3 (sat than loa y <= -28,6)
PCB_CENTER = [0.0, PCB_Y_USB - PCB_BOX[1] / 2, 34.0]
USB_GAP_ROOF = 0.3                    # mai hoc (chan mai) cach mat cong 0,3 mm; dinh mai cao hon 8,2 (45 do)
CABLE_W, CABLE_H, CABLE_R = 14.0, 9.0, 2.0   # lo cap USB-C thang, chu nhat bo goc R2

# Ampli MAX98357A: 22 x 22 x 10, dat sau loa trong bung, cach tam loa <= 70 mm
AMP_BOX = (22.0, 22.0, 10.0)
AMP_CENTER = [0.0, -12.0, 18.0]

# Mic INMP441: o tran z >= 100, cach tam loa >= 60 mm, ron EVA >= 1.0 quanh lo
MIC_BOX = (17.0, 8.0, 17.0)
MIC_CENTER = [0.0, -34.5, 115.4]   # y: vach trong cong theo x (x=0: -46, x=8,5: -39,5) -> o dat sau do + chan sat
MIC_SEAL_DEPTH, MIC_SEAL_CLR = 1.0, 0.15   # go lom (me cung) tren vach tran cho dau ong cam vao; bo ron EVA, in PETG
MC_W, MC_T, MC_H = 24.0, 2.5, 17.0   # nap kep: truot vao 2 ranh o 2 tru, ep module vao ron
MC_BACK_GAP = 1.4                    # mat sau o giu cho -> mat truoc tam kep (pad 1,2 + ho 0,2)
# Ong dan am (liền nap kep): OD 7, ID 3, tu mat module toi cach vach trong tran MIC_TUBE_GAP
MIC_TUBE_DZ = 1.0                    # tam ong cao hon tam module 1,0 de tranh mat sau mo (z <= 113,5)
MIC_TUBE_OD, MIC_TUBE_ID, MIC_TUBE_GAP = 7.0, 4.0, 0.3   # GAP: khe day go lom - mut ong. ID 4: lo am module lech tam chua ro
# 2026-11-18 Tuan: kep mic cu khong hop module. INMP441 Shopee = PCB TRON ~O15, header 6 chan 2,54 (ShillehTek manual, ask-gpt);
# han day thang (bo header). Hoc tron O15,6 (0,3/ben) nhet tu TREN xuong, mat sau ho de han day.
MIC_PCB_D, MIC_PCB_CLR, MIC_PCB_SLOT = 15.0, 0.3, 1.9   # SLOT: be day PCB (TODO do: PCB 1,0-1,6 -> long thi cham keo nong)
MIC_PCB_ZC = 0.5                    # tam PCB cao hon MIC_CENTER 0,5 (dinh PCB z 123,7 <= hop giu cho 123,9)
MIC_WALL_Y0 = -45.4                  # vach trong tran o x = 0..2 (do tren mesh)
YOKE_T, YOKE_BACK = 1.5, -9.6        # yoke dung truoc mat module (mat module o ly = -9,4), cach 0,2

# 1 LOA O BUNG: truc y, mat loa huong -y (ra truoc), z trong khoang 45..55
SPK_Z = 48.0
SPK_CY = -41.6
SPK_CENTER = [0.0, SPK_CY, SPK_Z]       # diem dat vanh/vong (co dinh)
SPK_LOA_Y = SPK_CY                      # 2026-11-18: bo lay PETG; mep loa ep bang moi vong (LIP_PRE) len bang xop 2 mm dan mat loa
SPEAKERS = [{"center": SPK_CENTER, "axis": "y"}]

FIT, SLIDE = 0.3, 0.2
Y0 = 0.37                  # mat phang ranh gioi 2 nua
BZ, BR, NT, NB, TAPER = 78.0, (66.0, 56.0, 80.0), 2.2, 4.2, 0.05
FLOOR_CUT = 4.0           # vo cat phang o z = 4; tam de day 4 mm
CZ, CRAD = 81.0, (BR[0] - WALL, BR[1] - WALL, 74.6)
CONE_T = math.tan(math.radians(10))
CONE_CLR = 0.3

# Tam bung: giu nguyen ban A1S de khong bi lech yen non
BELLY_Z, BELLY_FRONT, BELLY_RF, BELLY_REAR = 48.0, -58.5, 34.2, -42.0

# Hinh hoc vanh loa theo truc Y (local z -> world -y)
SPK_XF = 69.0
SPK_FACE = SPK_XF - 3.0 - GASKET_T
CUP_END = SPK_FACE - FLANGE_T
CUP_OR = SPEAKER_POCKET_D / 2 + 2.7
z_spk_center = SPK_FACE + LIP_PRE - SPEAKER_L / 2

EYE_X, EYE_Z, BEAK_Z = 36.5, 108.0, 102.0
RING_D, RING_T = 54.0, 3.0
BTN_TOP, SEAT_Z = 166.0, 145.0

# Switch MX (fit-library catpaw)
MX_HOLE, MX_DEPTH, MX_STEM_L, MX_STEM_W, MX_STEM_H = 14.0, 8.58, 4.19, 1.25, 3.6
MX_BODY_UP, MX_BODY_W, MX_HOUSING_H = 15.6, 5.0, 3.0
MX_GROOVE = (1.94, 2.69, 3.44, 15.44)
MX_INSERT, MX_TRAVEL = 1.2, 2.4
# 2026-11-18 Tuan: button-cap khong nhet duoc chan switch (chu thap khoet thang vao khoi dac, PETG co lo). Theo mau catpaw: chu thap
# nam trong ONG NHUN O5,71, ranh vong quanh ong de ong gian nhe khi ep. Kem bo thu chu thap 3 co (mx-cross-gauge.stl).
MX_TUBE_OD, MX_RELIEF_R, MX_RELIEF_H = 5.71, 4.6, 4.0
MX_GAUGE_W = (1.25, 1.35, 1.45)
REST_UP = 0.2
CONE_CLR_KEY = 0.3

# Vol-pod o lung (2 nut am luong)
VOL_X, VOL_Z = 24.0, 103.0
VOL_NECK_R, VOL_HOLE_R, VOL_FLANGE_R = 4.0, 4.5, 6.8
POD_W, POD_CB, POD_CT, POD_D = 9.6, -9.6, 10.35, 22.0
POD_PLATE, POD_BAY, POD_CLOSE = 3.0, 15.8, 7.95
POD_GAP, POD_RECESS = 0.3, 0.5
POD_DISH_R = 9.0
POD_TF, POD_STRIP = 3.0, (-18.8, -5.6, POD_CT - 0.5, 20.7)
POD_HOLES = ((-9.2, 12.3), (-15.2, 17.0))
SCR_CLEAR, SCR_HEAD, SCR_PILOT, SCR_PILOT_DEPTH, SCR_LEN = 2.8, 5.0, 2.2, 6.2, 10.0
EAR_GAP, G_HEAD = 0.4, 4.0
TALK_FLANGE_R = 29.0
TALK_ZB = 139.0
TENT_XM, TENT_ZLO, TENT_ZHI = 48.0, 6.0, 124.0
TENT_SL = 1.0
TENT_FLAT = 1.0
SCREW_X, SCREW_Y = 24.0, 14.0
BOSS_TOP = 16.0
PIN_D, PIN_HALF = 2.0, 8.0

def hexc(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)

# ============================================================ HAM CO BAN
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene

def new_obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); SC.collection.objects.link(o); return o

def place(o, M):
    o.data.transform(M)
    if M.determinant() < 0:
        o.data.flip_normals()
    return o

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
    if M is not None:
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
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

# ============================================================ KHOANG TRONG
def extrude(name, poly, u0, u1, M):
    bm = bmesh.new()
    lo = [bm.verts.new((a, b, u0)) for a, b in poly]; hi = [bm.verts.new((a, b, u1)) for a, b in poly]
    n = len(poly)
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)

def M_half(sgn):
    return Matrix(((1, 0, 0, 0), (0, sgn, 0, Y0), (0, 0, 1, 0), (0, 0, 0, 1)))

def diamond(r): return [(r, 0.0), (0.0, r), (-r, 0.0), (0.0, -r)]
def hr(w): return w * math.sqrt(2) / 2

def teardrop(r, h0=-0.5):
    pts = [(-r, h0), (-r, 0.0)]
    for k in range(1, 8):
        t = math.radians(180 - 45 * k / 7); pts.append((r * math.cos(t), r * math.sin(t)))
    pts += [(0.0, r * math.sqrt(2))]
    for k in range(0, 8):
        t = math.radians(45 - 45 * k / 7); pts.append((r * math.cos(t), r * math.sin(t)))
    pts += [(r, 0.0), (r, h0)]
    return pts

def bcone(y, extra): return BELLY_RF + extra + CONE_T * (y - BELLY_FRONT)

def make_cavity():
    parts = []
    xm, f = TENT_XM, TENT_FLAT
    tent = [(-xm, -0.5), (xm, -0.5), (f, (xm - f) / TENT_SL), (-f, (xm - f) / TENT_SL)]
    for sgn in (-1, 1):
        M = M_half(sgn)
        parts.append(extrude('tent', tent, TENT_ZLO, TENT_ZHI, M))
    # Khoang ong tru bung cho loa va tam bung:
    # rb = 37.8; keo dai qua BELLY_REAR de nuot hoan toan duoi bhole2 (khong de lai goc nhon/mat phang o z=42.4)
    rb = bcone(BELLY_REAR, CONE_CLR) + 0.4
    parts.append(cyl('belly_t1', (0, Y0 + 0.5, BELLY_Z), (0, BELLY_REAR - 2.0, BELLY_Z), rb + 0.2, seg=96))
    cav = parts[0]
    for p_ in parts[1:]:
        union(cav, p_)
    return inter(cav, cavity())

def mx_cutters(M, u_rim):
    out = []
    out.append(extrude('mxbay', diamond(hr(MX_BODY_UP + 0.2)), u_rim - MX_HOUSING_H - 0.6, u_rim + 0.02, M))
    out.append(extrude('mxpocket', diamond(hr(MX_HOLE)), u_rim, u_rim + MX_DEPTH, M))
    g0, g1, g2, gw = MX_GROOVE
    bm = bmesh.new(); pts = []
    for (u, w) in ((g0, MX_HOLE), (g1, gw), (g2, MX_HOLE)):
        r = hr(w)
        for a, b in diamond(r):
            pts.append(bm.verts.new(Vector((a, b, u_rim + u))))
    bmesh.ops.convex_hull(bm, input=pts)
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out.append(new_obj('mxgroove', bm))
    out.append(extrude('mxwin', diamond(hr(9.0)), u_rim + MX_DEPTH - 0.1, u_rim + MX_DEPTH + 7.0, M))
    return out

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

S = outer(); diff(S, make_cavity())

# ---------------- chi tiet noi bo ----------------
EYES = []
EYE_COLLAR_R = 22.6
for s in (-1, 1):
    P = Vector((s * EYE_X, body_y(s * EYE_X, EYE_Z), EYE_Z))
    M = frame(P, body_normal(s * EYE_X, EYE_Z)); EYES.append(M)
    t = cyl_local('tube', M, -12.9, 2.0, EYE_COLLAR_R, seg=60); clip(t); union(S, t)
BEAK_P = Vector((0, body_y(0, BEAK_Z), BEAK_Z))
BEAK_M = frame(BEAK_P, body_normal(0, BEAK_Z) + Vector((0, 0, -0.25)))
t = cyl_local('bcollar', BEAK_M, -5.0, 2.0, 11.6); clip(t); union(S, t)
t = cyl('bcol', (0, Y0, SEAT_Z), (0, Y0, 175), 31.6, seg=90); clip(t); union(S, t)

# Bo ESP32-S3 NAM NGANG (cap USB-C thang, Tuan 2026-11-12): hoc dung bo (tran PHANG), 2 ray vach + gac do canh PCB, chan dau truoc,
# lo cap chu nhat 14 x 9 R2 xuyen vach lung thang hang cong USB. Lap tu tren xuong truoc khi dong 2 nua vo.
PZ0, PZ1 = PCB_CENTER[2] - PCB_BOX[2] / 2, PCB_CENTER[2] + PCB_BOX[2] / 2      # 26..42
hx = PCB_BOX[0] / 2 + FIT   # 14.8
Y_ROOF = PCB_Y_USB + USB_GAP_ROOF
Y_FRONT = PCB_Y_USB - PCB_BOX[1]
CABLE_WALL_T = 56.4 - Y_ROOF   # day phan dac tu tran hoc toi mat ngoai lung (do tren mesh o x=0, z=34)
LEDGE_T = 1.8
for s in (-1, 1):
    a, b = sorted((s * hx, s * (hx + 2.4)))
    t = box('pcb_wall', (a, Y_FRONT + 0.8 - 1.6 - 0.0, 4.0), (b, 36.0, PZ1 + 1.0)); clip(t); union(S, t)             # vach ray (dung tu san)
    a2, b2 = sorted((s * 12.5, s * hx))
    t = box('pcb_ledge', (a2, Y_FRONT - 2.7, PZ0 - LEDGE_T - 0.2), (b2, 36.0, PZ0 - 0.2)); clip(t); union(S, t)   # gac do canh PCB
for s in (-1, 1):   # chan dau KHONG co USB: khoi dac tu san toi sat dau bo (duoi than loa z < 30)
    a, b = sorted((s * 12.5, s * (hx + 2.4)))
    t = box('pcb_stop', (a, Y_FRONT - 2.7, 4.0), (b, Y_FRONT - 0.2, PZ0 + 4.0)); clip(t); union(S, t)
# hoc phang vao phan dac (tent) phia sau: cho dau USB cua bo
_zh = (PZ1 - PZ0) / 2 + 0.2          # nua cao hoc; mai hinh chu A (45 do) -> in khong support
_zc = PCB_CENTER[2]
pk = extrude('pcb_pocket', [(_zc - _zh, 30.0), (_zc + _zh, 30.0), (_zc + _zh, Y_ROOF), (_zc, Y_ROOF + _zh), (_zc - _zh, Y_ROOF)],
             -hx, hx, Matrix(((0, 0, 1, 0), (0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 1))))
diff(S, pk)
# lo cap USB-C
def rrect(w, h, r, n=6):
    pts = []
    for (cx, cz, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            t_ = math.radians(a0 + 90 * k / n); pts.append((cx + r * math.cos(t_), cz + r * math.sin(t_)))
    return pts
M_cab = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1))) @ Matrix.Translation((0, 0, 0))
cab = extrude('cable', rrect(CABLE_W, CABLE_H, CABLE_R), Y_ROOF - 0.5, 90.0, M_cab)
cab.data.transform(Matrix.Translation((PCB_CENTER[0], 0, PCB_CENTER[2]))); diff(S, cab)

# 4 tru vit o de
for sx in (-SCREW_X, SCREW_X):
    for sy in (-SCREW_Y, SCREW_Y):
        b_ = cyl('boss', (sx, sy, 5.0), (sx, sy, BOSS_TOP), 7.0, seg=48)
        y_a, y_b = sorted((sy, Y0))
        union(b_, box('bossw', (sx - 7.0, y_a, 5.0), (sx + 7.0, y_b, BOSS_TOP)))
        union(S, b_)

# ============================================================ CAT LO
# Lo nut dau
for sgn in (-1, 1):
    diff(S, extrude('bhole', teardrop(BUTTON_HOLE_D / 2), SEAT_Z - 0.3, 180.0, M_half(sgn)))
TALK_R = TALK_FLANGE_R + 0.4
TALK_ZPOCKET = TALK_ZB - MX_TRAVEL - 0.4
z_cone_end = SEAT_Z - (TALK_R - BUTTON_HOLE_D / 2)
diff(S, lathe('tseat', [(0, SEAT_Z), (BUTTON_HOLE_D / 2, SEAT_Z), (TALK_R, z_cone_end), (TALK_R, TALK_ZPOCKET), (0, TALK_ZPOCKET)],
              seg=96, M=Matrix.Translation((0, Y0, 0))))
TALK_RIM = TALK_ZB + MX_INSERT - MX_STEM_H - MX_HOUSING_H
MT = Matrix(((1, 0, 0, 0), (0, 1, 0, Y0), (0, 0, -1, TALK_RIM), (0, 0, 0, 1)))
for o_ in mx_cutters(MT, 0.0):
    diff(S, o_)

# Mic INMP441: 2 tuong ranh (nap kep truot vao tu phia mat rap)
# Khong co chan dem sau lo: tran treo (in khong support) -> lo xuyen vach mong 2-3 mm, ron tua len phan day quanh o
_gy0 = MIC_CENTER[1] + MIC_BOX[1] / 2 + MC_BACK_GAP - 0.15   # ranh rong MC_T + 0,3 (khe truot 0,15/ben)
_gy1 = _gy0 + MC_T + 0.3
for s_ in (-1, 1):
    xa, xb = sorted((s_ * 10.2, s_ * 14.2))
    # tuong ranh: ta dung tu mat rap (y = Y0) toi vach tran -> in thang dung, khong support
    rail_ = box('micrail', (xa, -46.0, MIC_CENTER[2] - MC_H / 2), (xb, Y0 - 0.01, MIC_CENTER[2] + MC_H / 2))
    ga, gb = sorted((s_ * 10.0, s_ * (MC_W / 2 + 0.4)))
    diff(rail_, box('micgroove', (ga, _gy0, MIC_CENTER[2] - MC_H / 2 - 1.0), (gb, _gy1, MIC_CENTER[2] + MC_H / 2 + 1.0)))
    clip(rail_); union(S, rail_)

# Go lom (me cung) mat trong vach tran: dau ong dan am cam vao, khe 0,15/ben
diff(S, cyl('micseal', (MIC_CENTER[0], MIC_WALL_Y0 - MIC_SEAL_DEPTH, MIC_CENTER[2] + MIC_TUBE_DZ), (MIC_CENTER[0], MIC_WALL_Y0 + 6.0, MIC_CENTER[2] + MIC_TUBE_DZ), MIC_TUBE_OD / 2 + MIC_SEAL_CLR, seg=48))
# 3 lo mic o tran: z = 118, giua 2 mat, tren mo
for dx in (-1.5, 0.0, 1.5):
    diff(S, cyl('mic', (dx, -30, MIC_CENTER[2] + MIC_TUBE_DZ), (dx, -65, MIC_CENTER[2] + MIC_TUBE_DZ), MIC_HOLE_D / 2, seg=24))

# Lo mat, mo
for M in EYES:
    diff(S, cyl_local('ehole', M, -30, 12, 17.9, seg=64))
    diff(S, cyl_local('epocket', M, -13.0, -6.0, 20.3, seg=64))
    diff(S, cyl_local('eshaft', M, -27.0, -12.9, 20.3, seg=64))
diff(S, cyl_local('beakhole', BEAK_M, -8.0, 12.0, 9.2))
diff(S, cyl_local('beakpocket', BEAK_M, -40.0, -5.0, 11.4))

# Lo non tam bung: cat xuyen vao khoang trong (BELLY_REAR = -42.0)
diff(S, cyl('bhole2', (0, BELLY_FRONT - 1.5, BELLY_Z), (0, BELLY_REAR, BELLY_Z), bcone(BELLY_FRONT - 1.5, CONE_CLR), bcone(BELLY_REAR, CONE_CLR), seg=96))

# 5 khe thoat nhiet o lung
for i in range(5):
    x = (i - 2) * 7.0
    diff(S, box('vent', (x - VENT_W / 2, 30, 82 - VENT_L / 2), (x + VENT_W / 2, 70, 82 + VENT_L / 2)))

# Hoc dai oc vit de
for sx in (-SCREW_X, SCREW_X):
    for sy in (-SCREW_Y, SCREW_Y):
        diff(S, hexp('nut', (sx, sy, BOSS_TOP - NUT_DEPTH), (sx, sy, BOSS_TOP + 0.1)))
        diff(S, cyl('mclear', (sx, sy, 3.0), (sx, sy, BOSS_TOP - NUT_DEPTH + 0.1), M3_CLEAR_D / 2, seg=24))

# Cua so vol-pod o lung
VOL_D = dict(neck=3.0, cone=3.0, band=2.0)
VOL_ZB = VOL_D['neck'] + VOL_D['cone'] + VOL_D['band']
VOL_RIM = VOL_ZB + MX_TRAVEL + MX_HOUSING_H
YF = -body_y(VOL_X, VOL_Z) - POD_RECESS
def MP(sx): return Matrix(((sx, 0, 0, sx * VOL_X), (0, 0, -1, YF), (0, 1, 0, VOL_Z), (0, 0, 0, 1)))
SW_AU = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
SW_CU = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
def lbox(mn, mx, M): return place(box('lb', mn, mx), M)
def pau(poly, c0, c1, M): return extrude('pau', poly, c0, c1, M @ SW_AU)
def pcu(poly, a0, a1, M): return extrude('pcu', poly, a0, a1, M @ SW_CU)
def lcyl(a, c, u0, u1, r, M, seg=48): return cyl('lc', M @ Vector((a, c, u0)), M @ Vector((a, c, u1)), r, seg=seg)
SHAFT_U = YF - 1.0
G, W_, D_, CB_, CT_ = POD_GAP, POD_W, POD_D, POD_CB, POD_CT
TENT_Y = lambda x: Y0 - 0.5 + (TENT_XM - abs(x)) / TENT_SL
SCREW_INFO = []   # ban S3: khong con vol-pod, lung kin lien khoi

# Chot dinh vi 2 nua vo
for (px, pz) in ((-43, 142), (43, 142), (-34, 130), (34, 130), (-28.7, 160), (28.7, 160)):
    diff(S, cyl('pin', (px, Y0 - PIN_HALF, pz), (px, Y0 + PIN_HALF, pz), PIN_D / 2, seg=16))

# ============================================================ TACH 2 NUA
SRC = cp(S, 'src')
A = S; B = cp(S, 'back')
inter(A, box('fr', (-300, -300, -50), (300, Y0, 300)))
inter(B, box('bk', (-300, Y0, -50), (300, 300, 300)))

# Tam de: 4 lo vit chim M3
for sx in (-SCREW_X, SCREW_X):
    for sy in (-SCREW_Y, SCREW_Y):
        diff(PLATE, cyl('plh', (sx, sy, -1), (sx, sy, 5), M3_CLEAR_D / 2, seg=24))
        diff(PLATE, cyl('plc', (sx, sy, -1), (sx, sy, 2.8), 4.5, seg=40))
# 2026-11-18: 2 lo moi O2,2 sau 3,5 cho vit M2.5 bat khay ampli (tam de z 0..4)
for _sx in (-8.75, 8.75):
    diff(PLATE, cyl('plamp', (_sx, AMP_CENTER[1], FLOOR_CUT - 3.5), (_sx, AMP_CENTER[1], FLOOR_CUT + 1.0), 1.1, seg=20))

# ============================================================ BO PHAN RIENG
# --- Tam bung (belly): khoet lo vua vanh loa (khe truot 0,2-0,3)
# Vanh loa BZL_RF_S3 = 29.5 mm -> lo khoet r_hole = 29.75 mm
rf = BELLY_RF; yf = BELLY_FRONT; rho = 3.0; t1 = rho * math.tan(math.radians(30))
r_hole = 29.75
r_rear = rf + CONE_T * (BELLY_REAR - yf)
ti = 2.4 / math.cos(math.radians(30))
prof_belly = [(r_hole, yf), (rf - t1, yf)]
prof_belly += arc(rf - t1, yf + rho, rho, -90, -30, 6)[1:]
prof_belly += [(r_rear, BELLY_REAR), (r_rear - ti, BELLY_REAR), (rf - ti + CONE_T * 3.0, yf + 3.0), (r_hole, yf + 3.0)]
BELLY = lathe('belly', prof_belly, seg=96, M=Matrix.Translation((0, 0, BELLY_Z)) @ Matrix.Rotation(-math.pi / 2, 4, 'X'))

# Vay long chu V tren bung (ngoai r_hole)
def vcut(px, pz):
    for sgn in (-1, 1):
        b = box('vc', (-0.8, yf - 1.5, 0.0), (0.8, yf + 0.6, 11.0))
        b.data.transform(Matrix.Translation((px, 0, pz)) @ Matrix.Rotation(sgn * math.radians(38), 4, 'Y'))
        diff(BELLY, b)
for (px, pz) in ((-20, BELLY_Z + 12), (20, BELLY_Z + 12), (-23, BELLY_Z - 10), (23, BELLY_Z - 10)):
    vcut(px, pz)

# --- Vanh loa 1 cai o BUNG (speaker-bezel): ong non + luoi O56 + hoc loa + 3 chot ngam xoay
BZL_RF_S3 = 29.5    # ban kinh mat ngoai vanh loa (vua lo bung r_hole=29.75)
def make_bezel():
    h0 = SPK_XF; rho = 2.5
    cx = BZL_RF_S3 - rho
    pr = [(0, h0), (cx, h0)]
    pr += arc(cx, h0 - rho, rho, 90, 0, 6)[1:]
    plate_back = h0 - 3.0
    pr += [(BZL_RF_S3, plate_back),
           (CUP_OR, plate_back), (CUP_OR, CUP_END), (SPEAKER_POCKET_D / 2, CUP_END), (SPEAKER_POCKET_D / 2, plate_back), (0, plate_back)]
    z = lathe('bezel', pr, seg=96)
    # Luoi luc giac O56, lo O2.8 buoc 5.6
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
    # 3 chot ngam xoay tren mat ngoai ong om
    for a in BAY_ANG:
        R = Matrix.Rotation(math.radians(a), 4, 'Z')
        pz0 = CUP_END + BPIN_DZ
        pn = box('bpin', (CUP_OR - 0.5, -BPIN_W / 2, pz0), (CUP_OR + BPIN_H, BPIN_W / 2, pz0 + BPIN_T)); pn.data.transform(R)
        union(z, pn)
    return z, cnt

def sector(name, r0, r1, z0, z1, a0, a1, n=16):
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

# --- Vong ep ngam xoay 1 cai (speaker-ring). 2026-11-18: BO 4 lay PETG (chan loa chui qua) - moi vong ep thang len mep loa,
# bang xop 2 mm dan vong mat loa (khe GASKET_T 1,5 -> khoa con GASKET_T - LIP_PRE = 1,2) lam lo xo.
def make_clamp_ring(locked=False):
    zB = CUP_END - OUT_GAP - SRING_T; zL = CUP_END + LIP_PRE; zO = CUP_END - OUT_GAP
    rl = SPEAKER_POCKET_D / 2 - 0.3; rsi = CUP_OR + SLEEVE_CLR; rso = rsi + SLEEVE_T; ztop = CUP_END + SLEEVE_LEN
    r = lathe('sring', [(RING_ID / 2, zB), (RING_ID / 2, zL), (rl, zL), (rl, zO), (rsi, zO), (rsi, ztop), (rso, ztop), (rso, zB)], seg=96)
    pz0 = CUP_END + BPIN_DZ; pz1 = pz0 + BPIN_T
    rg = CUP_OR + BPIN_H + BPIN_CLR
    half = math.degrees((BPIN_W / 2 + 0.4) / rsi)
    for a in BAY_ANG:
        g0, g1 = pz0 - GROOVE_CLR, pz1
        diff(r, sector('gh', rsi - 0.5, rg, g0, g1, a - BAY_TWIST - half, a + half, 12))
        diff(r, sector('gv', rsi - 0.5, rg, g0, ztop + 0.5, a - BAY_TWIST - half, a - BAY_TWIST + half, 4))
    return r

BEZEL_LOCAL, GRILLE_N = make_bezel()
SRING_LOCAL = make_clamp_ring(False)       # ban in (lay o trang thai tu do)
SRING_LOCKED = SRING_LOCAL                 # khong con lay -> ban lap = ban in

# Toa do lap rap world cua loa bung:
# local z -> world -y
M_spk_world = Matrix.Translation(SPK_CENTER) @ Matrix.Rotation(math.radians(90), 4, 'X') @ Matrix.Translation((0, 0, -z_spk_center))
BEZEL_W = cp(BEZEL_LOCAL, 'bezel_w'); BEZEL_W.data.transform(M_spk_world)
SRING_W = cp(SRING_LOCKED, 'sring_w'); SRING_W.data.transform(M_spk_world)

# --- Khay ampli MAX98357A (amp-tray.stl). 2026-11-18 Tuan: "tam tam, khong toi uu", han day thang (khong cau dau/jack).
# Module Shopee clone tim 18 x 19 (Phipps listing, ask-gpt) / Adafruit 3006 19,4 x 17,8 x 3,0. PCB truot doc y vao 2 RAY RANH giu 2 mep
# (canh ~18 nam ngang x), vau chan dau +y, go khoa 0,4 dau -y; 2 dau PCB de trong cho day I2S + day loa; gam ho 3 mm + khe thoang.
# Bat xuong tam de bang 2 vit M2.5 x 6 (lo xuyen O2,8 + hoc dau O5,2; tam de co lo moi O2,2).
AMP_FEET_H = AMP_CENTER[2] - AMP_BOX[2] / 2 - 2.4 - 4.0   # (giu ten cu) 6,6
AMP_PCB_W, AMP_PCB_L = 18.0, 19.4                     # x (giua 2 ray), y (doc ray); TODO do module that
AMP_RAIL_CLR, AMP_SLOT = 0.25, 2.0                    # khe ngang moi ben; be ranh (PCB 1,6 + 0,4; TODO do day PCB)
AMP_GAP_UNDER = 3.0                                   # gam ho duoi PCB
AMP_SCREW_X = 8.75
AMP_BASE_T = 2.5
AMP_TRAY_Z = 7.3                                      # day hoc vo truoc tai khay: z 6,4-7,1 (do ray_cast 2026-11-18) + 0,2
def make_amp_tray():
    zt = AMP_BASE_T                                   # mat tren de (local); day khay dat tren day hoc vo z 7,3
    z_pcb = zt + AMP_GAP_UNDER                        # mat duoi PCB 11,8
    xi = AMP_PCB_W / 2 - 1.0                          # mep trong ray (PCB an vao ranh 1,0)
    xg = AMP_PCB_W / 2 + AMP_RAIL_CLR                 # day ranh
    xo = xg + 2.0                                     # mat ngoai ray
    L = AMP_PCB_L + 3.0; y0, y1 = -L / 2, L / 2       # go 1,6 + vau 1,0 + khe 0,4 -> cho PCB 19,8
    tray = box('at_base', (-xo, y0, 0.0), (xo, y1, zt))
    for dx in (-4.0, 0.0, 4.0):                       # khe thoang xuyen de (giua 2 lo vit)
        diff(tray, box('vent', (dx - 1.2, y0 + 3.0, -0.5), (dx + 1.2, y1 - 3.0, zt + 0.5)))
    for dx in (-AMP_SCREW_X, AMP_SCREW_X):            # vit M2.5 x 6: 3 mm trong khay + 3 mm vao tam de
        diff(tray, cyl('at_hole', (dx, 0, -0.5), (dx, 0, zt + 0.5), 1.4, seg=24))
    for s_ in (-1, 1):
        xa, xb = sorted((s_ * xi, s_ * xo))
        rail = box('at_rail', (xa, y0, zt - 0.2), (xb, y1, z_pcb + AMP_SLOT + 1.2))
        ga, gb = sorted((s_ * (xi - 0.5), s_ * xg))
        diff(rail, box('at_slot', (ga, y0 - 1, z_pcb), (gb, y1 + 1, z_pcb + AMP_SLOT)))
        union(tray, rail)
        # go khoa dau -y: PCB truot qua (vat 45 do), bat xuong sau go
        ba, bb = sorted((s_ * (xi - 1.2), s_ * xi))
        bump = extrude('at_bump', [(y0 + 0.2, z_pcb - 0.01), (y0 + 1.6, z_pcb - 0.01), (y0 + 1.6, z_pcb + 0.4), (y0 + 1.2, z_pcb + 0.4)],
                       ba, bb, Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
        union(tray, bump)
    # vau chan dau +y: chi cao 0,8 qua mat duoi PCB (day han o mat tren di qua)
    union(tray, box('at_stop', (-xi, y1 - 1.0, zt - 0.2), (xi, y1, z_pcb + 0.8)))
    return tray

AMP_TRAY_LOCAL = make_amp_tray()
M_amp_tray_w = Matrix.Translation((AMP_CENTER[0], AMP_CENTER[1], AMP_TRAY_Z))
for _sx in (-AMP_SCREW_X, AMP_SCREW_X):   # lo moi O2,2 xuyen day vo truoc (vit M2.5 x 6 xuong tam de)
    diff(A, cyl('amppilot', (_sx, AMP_CENTER[1], FLOOR_CUT - 0.5), (_sx, AMP_CENTER[1], AMP_TRAY_Z + 0.5), 1.1, seg=20))
AMP_TRAY_W = cp(AMP_TRAY_LOCAL, 'amp_tray_w'); AMP_TRAY_W.data.transform(M_amp_tray_w)

# --- Kep mic INMP441 (mic-clamp.stl). 2026-11-18 lam lai cho PCB TRON O15 (Shopee), han day thang.
# Local: y = 0 mat truoc tam truot (vao ranh vo), -y ra tran; z = 0 o MIC_CENTER z. In DUNG (z len) nhu khi lap.
def make_mic_clamp():
    rp = MIC_PCB_D / 2 + MIC_PCB_CLR                 # 7,8
    zc = MIC_PCB_ZC
    yf_pcb = YOKE_BACK + 0.5                          # mat truoc PCB (local) -9,1
    yr_pcb = yf_pcb + MIC_PCB_SLOT                    # mat sau PCB -7,2
    clamp = box('mc_base', (-MC_W / 2, 0.0, -9.9), (MC_W / 2, MC_T, MC_H / 2))      # tam truot vao 2 ranh vo
    diff(clamp, box('mc_win', (-6.0, -1.0, -4.0), (6.0, MC_T + 1.0, MC_H / 2 + 1.0)))   # cua so day ra sau
    ub = box('mc_u', (-9.0, yf_pcb - 0.1, -9.9), (9.0, yr_pcb + 1.8, zc + 4.5))      # khoi U giu PCB
    diff(ub, cyl('mc_pocket', (0, yf_pcb, zc), (0, yr_pcb, zc), rp, seg=72))           # hoc tron O15,6
    diff(ub, box('mc_slot', (-rp, yf_pcb, zc), (rp, yr_pcb, zc + 20)))                 # mo tren -> nhet tu tren xuong
    diff(ub, box('mc_back', (-5.5, yr_pcb - 0.01, -11.0), (5.5, yr_pcb + 2.0, zc + 6.0)))   # mat sau ho giua: han day + chip
    union(clamp, ub)
    for sx in (-1, 1):                                # 2 thanh noi khoi U -> tam truot (trong ray vo |x| 10,2)
        xa, xb = sorted((sx * 8.3, sx * 10.0))
        union(clamp, box('mc_bar', (xa, yr_pcb, -9.9), (xb, 0.2, zc + 4.5)))
    yfy = YOKE_BACK - YOKE_T + 0.5                    # mat truoc yoke
    union(clamp, box('mc_yoke', (-5.5, yfy, -9.9), (5.5, yf_pcb, MIC_TUBE_DZ + 5.5)))   # |x| 5,5: vach tran cong
    y_end = (MIC_WALL_Y0 - MIC_SEAL_DEPTH + MIC_TUBE_GAP) - (MIC_CENTER[1] + MIC_BOX[1] / 2 + MC_BACK_GAP)   # mut ong (local y)
    union(clamp, cyl('mc_tube', (0, yfy + 0.3, MIC_TUBE_DZ), (0, y_end, MIC_TUBE_DZ), MIC_TUBE_OD / 2, seg=48))
    diff(clamp, cyl('mc_bore', (0, yf_pcb + 0.5, MIC_TUBE_DZ), (0, y_end - 0.5, MIC_TUBE_DZ), MIC_TUBE_ID / 2, seg=32))
    return clamp

MIC_CLAMP_LOCAL = make_mic_clamp()
M_mic_clamp_w = Matrix.Translation((MIC_CENTER[0], MIC_CENTER[1] + MIC_BOX[1] / 2 + MC_BACK_GAP, MIC_CENTER[2]))
MIC_CLAMP_W = cp(MIC_CLAMP_LOCAL, 'mic_clamp_w'); MIC_CLAMP_W.data.transform(M_mic_clamp_w)

# --- Mo (beak)
bp = [(0, -9.0), (11.0, -9.0), (11.0, -6.2), (9, -6.2), (9, 0.0)]
bp += [(9 * math.cos(math.radians(a)), 7.5 * math.sin(math.radians(a))) for a in range(10, 91, 10)]
BEAK = lathe('beak', bp[:-1] + [(0, 7.5)], seg=64, M=BEAK_M)
# Khoet nhe mat sau mo cho dau ong dan am
diff(BEAK, cyl('beaknotch', (MIC_CENTER[0], MIC_WALL_Y0 - MIC_SEAL_DEPTH - 1.0, MIC_CENTER[2] + MIC_TUBE_DZ), (MIC_CENTER[0], MIC_WALL_Y0 + 4.0, MIC_CENTER[2] + MIC_TUBE_DZ), MIC_TUBE_OD / 2 + 0.4, seg=48))

# --- Nut dau (button-cap)
def cross_cutters(M, u_open, depth, dirn, angs=(45.0, 135.0)):
    out = []
    for ang in angs:
        z0, z1 = sorted((u_open - dirn * 0.2, u_open + dirn * depth))
        b_ = box('crs', (-MX_STEM_L / 2, -MX_STEM_W / 2, z0), (MX_STEM_L / 2, MX_STEM_W / 2, z1))
        b_.data.transform(M @ Matrix.Rotation(math.radians(ang), 4, 'Z')); out.append(b_)
    return out

cp_ = [(0, BTN_TOP), (19, BTN_TOP)] + arc(19, BTN_TOP - 6, 6, 90, 0, 8)[1:]
cp_ += [(25.0, SEAT_Z + REST_UP + 0.1), (TALK_FLANGE_R, SEAT_Z + REST_UP + 0.1 - (TALK_FLANGE_R - 25.0)), (TALK_FLANGE_R, TALK_ZB + REST_UP), (0, TALK_ZB + REST_UP)]
CAP = lathe('cap', cp_, seg=96, M=Matrix.Translation((0, Y0, 0)))
# ranh vong quanh ong chu thap (ong O5,71 nhun duoc nhu catpaw), roi khoet chu thap
_zc = TALK_ZB + REST_UP
_rel = cyl('caprel', (0, Y0, _zc - 0.5), (0, Y0, _zc + MX_RELIEF_H), MX_RELIEF_R, seg=64)
diff(_rel, cyl('captube', (0, Y0, _zc - 1.0), (0, Y0, _zc + MX_RELIEF_H + 1.0), MX_TUBE_OD / 2, seg=48))
diff(CAP, _rel)
for o_ in cross_cutters(Matrix.Translation((0, Y0, _zc)), 0.0, MX_STEM_H, 1):
    diff(CAP, o_)

# --- Bo thu chu thap (mx-cross-gauge.stl): 3 khoi, khe 1,25 / 1,35 / 1,45; so cham canh truoc = thu tu (1, 2, 3 cham)
def make_cross_gauge():
    g = box('gbase', (-17.0, -6.0, 0.0), (17.0, 6.0, 1.2))
    for i, w in enumerate(MX_GAUGE_W):
        cx = (i - 1) * 11.5
        blk = box('gblk', (cx - 5.2, -5.2, 0.0), (cx + 5.2, 5.2, 7.0))
        rel = cyl('grel', (cx, 0, 7.0 - MX_RELIEF_H), (cx, 0, 7.5), MX_RELIEF_R, seg=48)
        diff(rel, cyl('gtube', (cx, 0, 2.0), (cx, 0, 8.0), MX_TUBE_OD / 2, seg=48))
        diff(blk, rel)
        for ang in (45.0, 135.0):
            c_ = box('gcr', (-MX_STEM_L / 2, -w / 2, 7.0 - 4.5), (MX_STEM_L / 2, w / 2, 7.5))
            c_.data.transform(Matrix.Translation((cx, 0, 0)) @ Matrix.Rotation(math.radians(ang), 4, 'Z'))
            diff(blk, c_)
        for k in range(i + 1):
            diff(blk, cyl('gdot', (cx - 2.0 + 2.0 * k, -5.8, 4.0), (cx - 2.0 + 2.0 * k, -4.6, 4.0), 0.6, seg=12))
        union(g, blk)
    return g
GAUGE = make_cross_gauge()


# --- Kinh khuech tan mat (diffuser)
dp = [(0, -6.0), (20, -6.0), (20, -9.8), (18.8, -9.8), (18.8, -6.0 - DIFFUSER_T), (0, -6.0 - DIFFUSER_T)]
DIFFS = [lathe('diff%d' % i, dp, seg=72, M=M) for i, M in enumerate(EYES)]

# --- Vong mat (eye-ring)
RINGS = []
for M in EYES:
    r = cyl_local('ring', M, -16.0, RING_T, RING_D / 2, seg=96)
    diff(r, outer())
    diff(r, cyl_local('rw', M, -30, 12, 18.2, seg=72))
    RINGS.append(r)

# ============================================================ XUAT STL
def export_obj(o, T, path):
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
T_ring = Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1))) @ EYES[1].inverted()
T_pod = Mx(((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, D_), (0, 0, 0, 1)))

# Chia nho tam giac to quanh cac khoi giu cho (hinh khong doi: chi cat canh tam giac phang)
# de gate kiem va cham theo hop bao khong bi tam giac to lan sang o mic/ampli.
def refine(o, lo, hi, L=6.0):
    bm_ = bmesh.new(); bm_.from_mesh(o.data)
    for _ in range(10):
        es = set()
        for f in bm_.faces:
            vs = [v.co for v in f.verts]
            if all(max(c[i] for c in vs) < lo[i] or min(c[i] for c in vs) > hi[i] for i in (0, 1, 2)) or                any(max(c[i] for c in vs) < lo[i] or min(c[i] for c in vs) > hi[i] for i in (0, 1, 2)):
                continue
            for e in f.edges:
                if e.calc_length() > L:
                    es.add(e)
        if not es:
            break
        bmesh.ops.subdivide_edges(bm_, edges=list(es), cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm_, faces=bm_.faces[:])
    bm_.to_mesh(o.data); o.data.update(); bm_.free()

_mc, _mb = MIC_CENTER, MIC_BOX
for _o in (A, B):
    refine(_o, (_mc[0] - _mb[0] / 2 - 4, _mc[1] - _mb[1] / 2 - 4, _mc[2] - _mb[2] / 2 - 4),
               (_mc[0] + _mb[0] / 2 + 4, _mc[1] + _mb[1] / 2 + 4, _mc[2] + _mb[2] / 2 + 4))

# 12 chi tiet in required by gate_owl_s3
export_obj(A, T_front, OUT / "shell-front.stl")
export_obj(B, T_back, OUT / "shell-back.stl")
export_obj(BELLY, T_belly, OUT / "belly.stl")
export_obj(BEAK, T_beak, OUT / "beak.stl")
export_obj(CAP, T_cap, OUT / "button-cap.stl")
export_obj(DIFFS[1], T_diff, OUT / "eye-diffuser.stl")
export_obj(BEZEL_LOCAL, Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, SPK_XF), (0, 0, 0, 1))), OUT / "speaker-bezel.stl")
export_obj(SRING_LOCAL, Matrix.Identity(4), OUT / "speaker-ring.stl")

# mic-clamp: in mat phang mc_base xuong ban (z_min = 0)
T_mic_clamp = Matrix.Identity(4)   # in dung nhu khi lap (tam kep dung tren canh duoi); ong nam ngang ngan
export_obj(MIC_CLAMP_LOCAL, T_mic_clamp, OUT / "mic-clamp.stl")

# amp-tray: in day khay xuong ban (z_min = 0)
export_obj(AMP_TRAY_LOCAL, Matrix.Identity(4), OUT / "amp-tray.stl")
export_obj(GAUGE, Matrix.Identity(4), OUT / "mx-cross-gauge.stl")

# Cac chi tiet bo sung (tấm đế, vòng mắt, pod)
export_obj(PLATE, Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, FLOOR_CUT), (0, 0, 0, 1))), OUT / "base-plate.stl")
export_obj(RINGS[1], T_ring, OUT / "eye-ring.stl")

# ============================================================ LAP RAP (owl-assembled.stl)
asm = bmesh.new()
for o in [A, B, PLATE, BELLY, BEAK, CAP, BEZEL_W, SRING_W, MIC_CLAMP_W, AMP_TRAY_W] + DIFFS + RINGS:
    asm.from_mesh(o.data)
am = bpy.data.meshes.new('asm'); asm.to_mesh(am); asm.free()
ao = bpy.data.objects.new('asm', am); SC.collection.objects.link(ao)
for ob in bpy.context.view_layer.objects:
    ob.select_set(False)
ao.select_set(True); bpy.context.view_layer.objects.active = ao
bpy.ops.wm.stl_export(filepath=str(OUT / "owl-assembled.stl"), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
bpy.data.objects.remove(ao)

# ============================================================ ASM CHI TIET (do duoc + gate bayonet)
(OUT / "asm").mkdir(exist_ok=True)
def export_asm(o, path):
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)

export_asm(BEZEL_W, OUT / "asm" / "speaker-bezel.stl")
export_asm(SRING_W, OUT / "asm" / "speaker-ring.stl")
export_asm(A, OUT / "asm" / "shell-front.stl")
export_asm(B, OUT / "asm" / "shell-back.stl")
export_asm(BELLY, OUT / "asm" / "belly.stl")
export_asm(BEAK, OUT / "asm" / "beak.stl")
export_asm(CAP, OUT / "asm" / "button-cap.stl")
export_asm(AMP_TRAY_W, OUT / "asm" / "amp-tray.stl")
export_asm(MIC_CLAMP_W, OUT / "asm" / "mic-clamp.stl")

# ============================================================ PARAMS JSON
params = dict(
    variant="s3",
    wall=WALL,
    speaker_pocket_d=SPEAKER_POCKET_D,
    grille_hole_d=GRILLE_HOLE_D,
    mic_hole_d=MIC_HOLE_D,
    m3_clear_d=M3_CLEAR_D,
    m3_nut_s=M3_NUT_S,
    button_cap_d=BUTTON_CAP_D,
    button_hole_d=BUTTON_HOLE_D,
    diffuser_t=DIFFUSER_T,
    vent_w=VENT_W,
    speakers=[{"center": [0.0, round(SPK_LOA_Y, 2), SPK_Z], "axis": "y"}],
    pcb_center=PCB_CENTER,
    pcb_box=list(PCB_BOX),
    amp_center=AMP_CENTER,
    amp_pcb=dict(center=[0.0, round(AMP_CENTER[1] + 0.3, 2), round(AMP_TRAY_Z + AMP_BASE_T + AMP_GAP_UNDER + 0.2 + 0.8, 2)],
                 box=[AMP_PCB_W, AMP_PCB_L, 1.6], parts_h=3.0, note="clone Shopee 18x19 / Adafruit 19,4x17,8; parts_h TODO do"),
    amp_box=list(AMP_BOX),
    mic=dict(center=MIC_CENTER, box=list(MIC_BOX), holes=3, hole_x=[-1.5, 0.0, 1.5], hole_z=round(MIC_CENTER[2] + MIC_TUBE_DZ, 2), axis="y",
             tube=dict(od=MIC_TUBE_OD, id=MIC_TUBE_ID, gap_to_wall=MIC_TUBE_GAP, wall_y=MIC_WALL_Y0),
             seal=dict(type="labyrinth", depth=MIC_SEAL_DEPTH, clearance=MIC_SEAL_CLR),
             pcb=dict(center=[0.0, round(MIC_CENTER[1] + MIC_BOX[1] / 2 + MC_BACK_GAP + YOKE_BACK + 0.5 + 0.85, 2), round(MIC_CENTER[2] + MIC_PCB_ZC, 2)],
                      d=MIC_PCB_D, t=1.6, axis="y", note="INMP441 Shopee tron ~O15 (ShillehTek); day PCB TODO")),
    pcb_usb=dict(center=[PCB_CENTER[0], PCB_Y_USB, PCB_CENTER[2]], dir="+y"),
    cable_slot=dict(side="back", w=CABLE_W, h=CABLE_H, r=CABLE_R, center=[PCB_CENTER[0], round(Y_ROOF + CABLE_WALL_T / 2, 2), PCB_CENTER[2]], wall_t=round(CABLE_WALL_T, 2)),
    split_plane_y=Y0,
    grille_holes_per_speaker=GRILLE_N,
    speaker_dims=[SPEAKER_D, SPEAKER_L],
    speaker_clamp=dict(
        flange_t=FLANGE_T,
        gasket_t=GASKET_T,
        body_d_max=BODY_D_MAX,
        ring_t=SRING_T,
        ring_id=RING_ID,
        gasket_locked=round(GASKET_T - LIP_PRE, 3),
        gasket_slot_kept=True,   # ranh ron giu nguyen cho ron TPU 2 mm sau nay
        gasket_note="bang xop 2 mm dan vong mat loa (khong con lay PETG, 2026-11-18)",
        bayonet=dict(
            n=len(BAY_ANG),
            twist=BAY_TWIST,
            pin_w=BPIN_W,
            pin_h=BPIN_H,
            pin_t=BPIN_T,
            sleeve_clr=SLEEVE_CLR,
            pin_clr=BPIN_CLR,
            groove_clr=GROOVE_CLR,
            lip_pre=LIP_PRE,
            out_gap=OUT_GAP,
            sleeve_t=SLEEVE_T
        )
    ),
    mx=dict(
        hole=MX_HOLE,
        socket_depth=MX_DEPTH,
        stem_cross_l=MX_STEM_L,
        stem_cross_w=MX_STEM_W,
        keys=[
            dict(name="talk", gpio=1, axis="z", pos=[0.0, Y0, TALK_RIM], flange_over=round(TALK_FLANGE_R - BUTTON_HOLE_D / 2, 2))
        ]
    )
)
(OUT / "owl-params.json").write_text(json.dumps(params, indent=1), encoding="utf-8")

# ============================================================ ANH PREVIEW & EXPLODED
import numpy as np
PCOL = dict(shell='#F6BE9A', cream='#FFF3DF', butter='#FFC857', white='#FFFFFF', spk='#6B6F78', pcb='#2E8B57', amp='#4169E1')
TMP = OUT / "_tmp"; TMP.mkdir(exist_ok=True)

def dump(o, name):
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.wm.stl_export(filepath=str(TMP / (name + ".stl")), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)

spk_dummy = cyl('spk_d', Vector((0, SPK_LOA_Y - 13.0, SPK_Z)), Vector((0, SPK_LOA_Y - 13.0 + FLANGE_T, SPK_Z)), SPEAKER_D / 2, seg=48)
union(spk_dummy, cyl('spk_db', Vector((0, SPK_LOA_Y - 13.0 + FLANGE_T, SPK_Z)), Vector((0, SPK_LOA_Y + 13.0, SPK_Z)), BODY_D_MAX / 2, seg=48))
pcb_dummy = box('pcb_d', (-PCB_BOX[0] / 2, PCB_CENTER[1] - PCB_BOX[1] / 2, PCB_CENTER[2] - PCB_BOX[2] / 2),
                         (PCB_BOX[0] / 2, PCB_CENTER[1] + PCB_BOX[1] / 2, PCB_CENTER[2] + PCB_BOX[2] / 2))
amp_dummy = box('amp_d', (-AMP_BOX[0] / 2, AMP_CENTER[1] - AMP_BOX[1] / 2, AMP_CENTER[2] - AMP_BOX[2] / 2),
                         (AMP_BOX[0] / 2, AMP_CENTER[1] + AMP_BOX[1] / 2, AMP_CENTER[2] + AMP_BOX[2] / 2))
mic_dummy = box('mic_d', (-MIC_BOX[0] / 2, MIC_CENTER[1] - MIC_BOX[1] / 2, MIC_CENTER[2] - MIC_BOX[2] / 2),
                         (MIC_BOX[0] / 2, MIC_CENTER[1] + MIC_BOX[1] / 2, MIC_CENTER[2] + MIC_BOX[2] / 2))

ITEMS = [
    (A, 'front', 'shell', (0, -75, 0)),
    (B, 'back', 'shell', (0, 75, 0)),
    (PLATE, 'plate', 'cream', (0, 0, -45)),
    (BELLY, 'belly', 'cream', (0, -130, 0)),
    (BEAK, 'beak', 'butter', (0, -135, 30)),
    (CAP, 'cap', 'butter', (0, 0, 55)),
    (BEZEL_W, 'bezel', 'shell', (0, -155, 0)),
    (SRING_W, 'sring', 'cream', (0, -85, 0)),
    (spk_dummy, 'spk', 'spk', (0, -110, 0)),
    (AMP_TRAY_W, 'amptray', 'shell', (0, -35, 0)),
    (amp_dummy, 'amp', 'amp', (0, -35, 15)),
    (MIC_CLAMP_W, 'micclamp', 'shell', (0, -60, 40)),
    (mic_dummy, 'mic', 'pcb', (0, -85, 40)),
    (DIFFS[0], 'd0', 'white', (-30, -110, 25)),
    (DIFFS[1], 'd1', 'white', (30, -110, 25)),
    (RINGS[0], 'r0', 'cream', (-40, -100, 0)),
    (RINGS[1], 'r1', 'cream', (40, -100, 0)),
    (pcb_dummy, 'pcb', 'pcb', (0, 30, 0)),
]
for o, n, c, off in ITEMS:
    dump(o, n)

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

ASM = ['front', 'back', 'plate', 'belly', 'beak', 'cap', 'bezel', 'sring', 'd0', 'd1', 'r0', 'r1', 'micclamp', 'amptray']
sc = fresh_scene((800, 1200)); load_items(sc, ASM, False)
cam_at(sc, (0, 0, 85), -32, 12, 560); render_png(sc, OUT / "_v1.png")
bpy.data.objects.remove(sc.camera)
cam_at(sc, (0, 0, 85), 148, 18, 560); render_png(sc, OUT / "_v2.png")
merge(OUT / "_v1.png", OUT / "_v2.png", OUT / "owl-preview.png")

# Chinh dien: camera truc -Y, truc giao (kiem tam loa x = 0, 2 mat doi xung)
sc = fresh_scene((1000, 1300)); load_items(sc, ASM, False)
cd_ = bpy.data.cameras.new('camf'); cd_.type = 'ORTHO'; cd_.ortho_scale = 200; cd_.clip_end = 5000
cf_ = bpy.data.objects.new('camf', cd_); sc.collection.objects.link(cf_); sc.camera = cf_
cf_.location = (0, -600, 85); cf_.rotation_euler = (math.radians(90), 0, 0)
render_png(sc, OUT / "owl-front.png")
# Mat sau: camera truc +Y, truc giao (thay lo cap USB-C)
cf_.location = (0, 600, 85); cf_.rotation_euler = (math.radians(90), 0, math.radians(180))
render_png(sc, OUT / "owl-back.png")

sc = fresh_scene((1600, 1200)); load_items(sc, [n for _, n, _, _ in ITEMS], True)
cam_at(sc, (0, -20, 75), -30, 22, 950, 70); render_png(sc, OUT / "owl-exploded.png")

for f in ("_v1.png", "_v2.png"):
    if (OUT / f).exists(): (OUT / f).unlink()
shutil.rmtree(TMP, ignore_errors=True)

print("BUILD S3 OK")
