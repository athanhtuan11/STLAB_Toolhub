# build_owl.py - CAD vo "Cu Bong" ban 1 (ESP32-A1S Audio Kit, 2 loa trai/phai). Blender 5.2 bpy/bmesh, chay nen.
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_owl.py -- out
# He lap rap: mm, +Z len, mat truoc = -Y, x ngang. Mat ranh gioi hai nua vo: mat phang y = Y0.
import bpy, bmesh, math, json, sys, os
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
CONE_T = math.tan(math.radians(10))   # nua goc yen non tam bung 10 do (2026-11-08: 30 do -> ong tru bung rong 44 cham mai/ giong kinh tao rang nhon 'floating')
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
PCB_CENTER = [0.0, 0.37, 70.0]   # 2026-11-08: y = Y0 (82 theo Y chia deu 2 nua) + z 70 -> tran mai nhon khong support
EYE_X, EYE_Z, BEAK_Z = 36.5, 108.0, 102.0
RING_D, RING_T = 54.0, 3.0        # vong mat kem (mat truoc phang)
BTN_TOP, SEAT_Z = 166.0, 145.0
# ---- 2026-11-08 Tuan: nut = switch phim co MX KHONG PCB (y tuong clicker). So lap ghep LAY TU fit-library:
#   catpaw/mx-socket: lo vuong 14,00 (press) sau 8,58 tu mieng; ranh V 45 do: 1,94-3,44 duoi mieng, sau nhat 2,69, rong 15,44
#   catpaw/mx-keycap-cross: lo chu thap 4,19 x 1,25 (sau 5,6 - o day chi can 3,6 = chieu cao chan MX)
# GIA DINH (TODO do switch that): thân switch tren mat ~6,6 (than 15,6 x 15,6 cao 3,0 + chan chu thap cao 3,6), than duoi 5,0, chan 3,3.
MX_HOLE, MX_DEPTH, MX_STEM_L, MX_STEM_W, MX_STEM_H = 14.0, 8.58, 4.19, 1.25, 3.6
MX_BODY_UP, MX_BODY_W, MX_HOUSING_H = 15.6, 5.0, 3.0           # than tren rong 15,6; than duoi sau 5,0; cao than tren (chua tinh chan chu thap) 3,0
MX_GROOVE = (1.94, 2.69, 3.44, 15.44)                          # ranh V: bat dau, sau nhat, het (duoi mieng), rong tai day
MX_INSERT, MX_TRAVEL = 1.2, 2.4                                # chan chu thap cam vao lo nap 1,2 mm luc nghi; nap chay toi da 2,4 mm (cham than switch; MX bat o ~2,0)
REST_UP = 0.2                                                  # nap nut nam sat dau cao 0,2 (vanh con lo khe 0,1 voi yen non)
CONE_CLR_KEY = 0.3                                             # khe ngang yen non nap nut
# ---- 2026-11-08 Tuan: 2 nut am luong VE LUNG (cum nut roi 'vol-pod' lap tu trong vo, giu bang 2 vit M3 bat tu ngoai lung).
VOL_X, VOL_Z = float(os.environ.get("OWL_VX", 24.0)), float(os.environ.get("OWL_VZ", 103.0))           # tam nut: |x| (cua so >= 14,6: cach thanh khe bo mach x=12,8 toi 1,8 mm de tran khe co do - 22 thi tran khe bo cheo; hop bo mach x +-12,5), z (vach lung nghieng 21 do, tren 5 khe thoat nhiet z<=91)
VOL_NECK_R, VOL_HOLE_R, VOL_FLANGE_R = 4.0, 4.5, 6.8           # nap nho: co O8, khe co O9,0, vanh O13,6 (< 14,00 de luon qua o; hon khe 2,3 mm/ben)
POD_W, POD_CB, POD_CT, POD_D = 9.6, -9.6, 10.35, 22.0          # pod (he cuc bo a,c,u: a ngang, c doc (z), u sau tu mat phang YF): nua rong, mep duoi (HO), mep tren, day
POD_PLATE, POD_BAY, POD_CLOSE = 3.0, 15.8, 7.95                # tam ngoai day 3 (co O8 truot), kenh vai switch 15,8, dau kin cua kenh o c = +7,95
POD_GAP, POD_RECESS = 0.3, 0.5                                 # khe pod - cua so 0,3/ben; mat phang YF thap hon be mat lung 0,5 o tam nut (nap nhô 3,2)
POD_DISH_R = 9.0                                               # lom dau nap O18,0 (dau nap O17,2): mat pod = be mat vo, lom xuong mat phang YF quanh nap
# vit M2.5 tu ren bat TU TRONG vo ra (2026-11-08 Tuan: giau vit): 'tai' pod o phia tren (+c) la khoi duoi tran mai chu A (mat tren doc 45 do song song tran, khe 0,4) co 2 lo O2,8 + hoc dau O5,0;
# lo moi 2,2 khoan thang vao khoi tran dac (thay tru roi: tru treo duoi tran khong in duoc khong support). POD_TF: khong con dung
POD_TF, POD_STRIP = 3.0, (-18.8, -5.6, POD_CT - 0.5, 20.7)     # day vanh; dai vanh (a0, a1, c0, c1)
POD_HOLES = ((-9.2, 12.3), (-15.2, 17.0))                      # (a, c) 2 lo vit (x = 24 + a: 14,8 va 8,8; z = 103 + c: tren hop bo z > 106,5)
SCR_CLEAR, SCR_HEAD, SCR_PILOT, SCR_PILOT_DEPTH, SCR_LEN = 2.8, 5.0, 2.2, 6.2, 10.0   # lo thong 2,8, hoc dau O5,0, lo moi 2,2 (sau 6,2 trong tran vo dac), vit M2.5 x 10
EAR_GAP, G_HEAD = 0.4, 4.0                                     # khe mat tai pod - tran mai (theo y); dau vit cach mat tai 4,0 (an ren = 10 - 4,4 = 5,6)
TALK_FLANGE_R = 29.0                                           # nap nut dau: vanh trong O58 (lo vo O50,8 -> hon 3,6 mm/ben)
TALK_ZB = 139.0                                                # mat duoi nap nut dau (z)
TENT_XM, TENT_ZLO, TENT_ZHI = 48.0, 6.0, 124.0                 # khoang trong chinh: mai chu A (45 do), de khong support
PCB_SLOT_X = 12.8                                              # 12,5 + khe 0,3
TENT_SL = 1.0                                                  # do doc mai: x giam TENT_SL mm moi mm cao (<= 1,07 -> nghieng >= 43 do so voi phuong ngang)
TENT_FLAT = 1.0                                                # nua be rong dinh mai (<= 1 mm: cau 2 mm)
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

def place(o, M):
    """Dat vat o bang ma tran M (dao chieu mat neu M co dinh thuc am - ma tran guong)."""
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

# ============================================================ HAM KHOANG TRONG / NUT MX (2026-11-08)
def extrude(name, poly, u0, u1, M):
    """Lang tru: da giac 2D (a, b) keo doc truc local z tu u0 den u1, dat bang ma tran M (local -> the gioi)."""
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
    """Toa do nua vo: local (x, h, z) -> the gioi (x, Y0 + sgn*h, z); h = cao tinh tu mat rap theo huong IN (nua truoc sgn=-1, nua sau sgn=+1)."""
    return Matrix(((1, 0, 0, 0), (0, sgn, 0, Y0), (0, 0, 1, 0), (0, 0, 0, 1)))

def diamond(r): return [(r, 0.0), (0.0, r), (-r, 0.0), (0.0, -r)]       # hinh vuong xoay 45 do, nua duong cheo r (mai 45 do, khong mai phang)
def hr(w): return w * math.sqrt(2) / 2                                    # nua duong cheo cua hinh vuong canh w

def teardrop(r, h0=-0.5):
    """Tiet dien giot nuoc (tron + chop 45 do huong len): (a, h) voi a = lech ngang, h = cao in; cung tron r, chop tai h = r*sqrt2."""
    pts = [(-r, h0), (-r, 0.0)]
    for k in range(1, 8):                       # cung 180 -> 135 do
        t = math.radians(180 - 45 * k / 7); pts.append((r * math.cos(t), r * math.sin(t)))
    pts += [(0.0, r * math.sqrt(2))]
    for k in range(0, 8):
        t = math.radians(45 - 45 * k / 7); pts.append((r * math.cos(t), r * math.sin(t)))
    pts += [(r, 0.0), (r, h0)]
    return pts

def bcone(y, extra): return BELLY_RF + extra + CONE_T * (y - BELLY_FRONT)    # ban kinh lo non tam bung tai y

def make_cavity():
    """Khoang trong in KHONG SUPPORT (2026-11-08): khoang cu (elipsoid) giao voi tap hop khoi mai 45 do (moi nua in mat rap xuong):
    mai chu A dai doc theo z (do rong tai mat rap +-TENT_XM, dinh = TENT_XM), ham bo mach (thanh dung +-12,8 + mai chu A), duong ham loa (giot nuoc),
    ong tru bung (phia truoc). Tran luon nghieng >= 45 do hoac dinh phang <= 2 mm."""
    parts = []
    pcb = PCB_CENTER; hp = PCB_BOX[1] / 2 + FIT                  # nua sau bo (y) + khe: tran ham bo mach = chan chan dau cuoi bo
    pz0, pz1 = pcb[2] - PCB_BOX[2] / 2 - FIT, pcb[2] + PCB_BOX[2] / 2 + FIT
    xm, f = TENT_XM, TENT_FLAT
    tent = [(-xm, -0.5), (xm, -0.5), (f, (xm - f) / TENT_SL), (-f, (xm - f) / TENT_SL)]
    xs_ = PCB_SLOT_X
    slot = [(-xs_, -0.5), (xs_, -0.5), (xs_, hp), (f, hp + (xs_ - f) / TENT_SL), (-f, hp + (xs_ - f) / TENT_SL), (-xs_, hp)]
    for sgn in (-1, 1):
        M = M_half(sgn)
        parts.append(extrude('tent', tent, TENT_ZLO, TENT_ZHI, M))
        parts.append(extrude('slot', slot, pz0, pz1, M))
        for sx in (-1, 1):                                       # duong ham loa: truc x, tam (y=Y0, z=SPK_Z), x tu 36 den het yen non
            Mx_ = Matrix(((0, 0, sx, 0), (0, sgn, 0, Y0), (1, 0, 0, SPK_Z), (0, 0, 0, 1)))   # local (a, h, u) -> (sx*u, Y0+sgn*h, SPK_Z + a)
            parts.append(extrude('spk', teardrop(BODY_D_MAX / 2 + 0.8), 36.0, 55.0, Mx_))
    rb = bcone(BELLY_REAR, CONE_CLR) + 0.4; h_top = Y0 - BELLY_REAR; cham = rb - 40.0          # ong cho tam bung lap tu trong: tru + non 45 do o dinh (khong de tran phang/ nong)
    parts.append(cyl('belly_t1', (0, Y0 + 0.5, BELLY_Z), (0, Y0 - (h_top - cham), BELLY_Z), rb, seg=96))
    parts.append(cyl('belly_t2', (0, Y0 - (h_top - cham) + 0.01, BELLY_Z), (0, BELLY_REAR, BELLY_Z), rb, rb - cham, seg=96))
    cav = parts[0]
    for p_ in parts[1:]:
        union(cav, p_)
    return inter(cav, cavity())

def mx_cutters(M, u_rim):
    """Cac khoi khoet cho 1 switch MX (truc local z; u tang tu mat tren nap vao trong): 'bay' vai switch, lo switch 14 xoay 45 do, ranh V, cua so day.
    M: local -> the gioi (local z = huong vao trong); u_rim = vi tri mieng lo (u); tra ve list vat the can diff."""
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
    out.append(extrude('mxwin', diamond(hr(9.0)), u_rim + MX_DEPTH - 0.1, u_rim + MX_DEPTH + 7.0, M))   # cua so day: day chan / day dan thoat vao khoang trong
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

# ---------------- chi tiet noi bo (them truoc khi cat lo) ----------------
EYES = []
EYE_COLLAR_R = 22.6        # 20,3 + 2,3: vanh dau ong <= 2,4 mm -> khong can support
for s in (-1, 1):
    P = Vector((s * EYE_X, body_y(s * EYE_X, EYE_Z), EYE_Z))
    M = frame(P, body_normal(s * EYE_X, EYE_Z)); EYES.append(M)
    t = cyl_local('tube', M, -12.9, 2.0, EYE_COLLAR_R, seg=60); clip(t); union(S, t)
BEAK_P = Vector((0, body_y(0, BEAK_Z), BEAK_Z))
BEAK_M = frame(BEAK_P, body_normal(0, BEAK_Z) + Vector((0, 0, -0.25)))
t = cyl_local('bcollar', BEAK_M, -5.0, 2.0, 11.6); clip(t); union(S, t)
t = cyl('bcol', (0, Y0, SEAT_Z), (0, Y0, 175), 31.6, seg=90); clip(t); union(S, t)

# ray (vay) giu bo: 2 tam hai ben khoang bo, dung tren san
hx = PCB_BOX[0] / 2 + FIT
pz0, pz1 = PCB_CENTER[2] - PCB_BOX[2] / 2, PCB_CENTER[2] + PCB_BOX[2] / 2
py0, py1 = PCB_CENTER[1] - PCB_BOX[1] / 2, PCB_CENTER[1] + PCB_BOX[1] / 2
for s in (-1, 1):
    a, b = sorted((s * hx, s * (hx + 2.0)))
    t = box('rail', (a, py0 + 6, 5.0), (b, py1 - 6, pz0 + 30)); clip(t); union(S, t)   # vay noi san va mai (dau tren cham thanh mai chu A -> khong bi khe USB cat roi)

# boss vit: 4 tru tren san, keo toi mat rap (hinh 'bia mo': tru + khoi xuong mat rap) -> khong co mat tru treo
for sx in (-SCREW_X, SCREW_X):
    for sy in (-SCREW_Y, SCREW_Y):
        b_ = cyl('boss', (sx, sy, 5.0), (sx, sy, BOSS_TOP), 7.0, seg=48)
        y_a, y_b = sorted((sy, Y0))
        union(b_, box('bossw', (sx - 7.0, y_a, 5.0), (sx + 7.0, y_b, BOSS_TOP)))
        union(S, b_)

# ============================================================ CAT LO
# lo nut dau: lo O50,8 tu mat tua (z 145) len; yen non 45 do + hoc vanh duoi mat tua (nap nut cam tu duoi len, lap truoc khi dong vo)
for sgn in (-1, 1):                                              # lo nut: giot nuoc (chop 45 do) de tran lo ngang khong treo
    diff(S, extrude('bhole', teardrop(BUTTON_HOLE_D / 2), SEAT_Z - 0.3, 180.0, M_half(sgn)))
TALK_R = TALK_FLANGE_R + 0.4
TALK_ZPOCKET = TALK_ZB - MX_TRAVEL - 0.4
z_cone_end = SEAT_Z - (TALK_R - BUTTON_HOLE_D / 2)
diff(S, lathe('tseat', [(0, SEAT_Z), (BUTTON_HOLE_D / 2, SEAT_Z), (TALK_R, z_cone_end), (TALK_R, TALK_ZPOCKET), (0, TALK_ZPOCKET)],
              seg=96, M=Matrix.Translation((0, Y0, 0))))        # yen non 45 do + hoc vanh (mot khoi xoay, khong mat trung nhau)
TALK_RIM = TALK_ZB + MX_INSERT - MX_STEM_H - MX_HOUSING_H           # mieng lo switch MX (z)
MT = Matrix(((1, 0, 0, 0), (0, 1, 0, Y0), (0, 0, -1, TALK_RIM), (0, 0, 0, 1)))   # local (a,b,u) -> (x, Y0 + y, TALK_RIM - u): u tang di xuong
for o_ in mx_cutters(MT, 0.0):
    diff(S, o_)
for dx in (-7, 0, 7):
    diff(S, cyl('mic', (dx, -8, 120), (dx, -85, 120), MIC_HOLE_D / 2, seg=16))
for M in EYES:
    diff(S, cyl_local('ehole', M, -30, 12, 17.9, seg=64))
    diff(S, cyl_local('epocket', M, -13.0, -6.0, 20.3, seg=64))
    diff(S, cyl_local('eshaft', M, -27.0, -12.9, 20.3, seg=64))          # duong lap kinh khuech tan tu khoang trong vao hoc
diff(S, cyl_local('beakhole', BEAK_M, -8.0, 12.0, 9.2))
diff(S, cyl_local('beakpocket', BEAK_M, -40.0, -5.0, 11.4))             # hoc vanh mo O22,8 (mo lap tu trong); tran vong 2,2 mm
# lo non cho tam bung (nho ngoai, rong vao trong -> yen non, lap tu trong)
diff(S, cyl('bhole2', (0, BELLY_FRONT - 1.5, BELLY_Z), (0, BELLY_REAR, BELLY_Z), bcone(BELLY_FRONT - 1.5, CONE_CLR), bcone(BELLY_REAR, CONE_CLR), seg=96))
# lo non cho vanh loa 2 suon
def zcone(h, extra): return BZL_RF + extra + BZL_T * (SPK_XF - h)
for s in (-1, 1):
    diff(S, cyl('szhole', (s * (SPK_XF + 1.5), 0, SPK_Z), (s * BZL_REAR, 0, SPK_Z), zcone(SPK_XF + 1.5, CONE_CLR), zcone(BZL_REAR, CONE_CLR), seg=96))
for i in range(5):
    x = (i - 2) * 7.0
    diff(S, box('vent', (x - VENT_W / 2, 30, 82 - VENT_L / 2), (x + VENT_W / 2, 70, 82 + VENT_L / 2)))
for sx in (-SCREW_X, SCREW_X):
    for sy in (-SCREW_Y, SCREW_Y):
        diff(S, hexp('nut', (sx, sy, BOSS_TOP - NUT_DEPTH), (sx, sy, BOSS_TOP + 0.1)))
        diff(S, cyl('mclear', (sx, sy, 3.0), (sx, sy, BOSS_TOP - NUT_DEPTH + 0.1), M3_CLEAR_D / 2, seg=24))
# ---- nut am luong o LUNG: cum nut roi vol-pod x2 (|x| = VOL_X), lap tu TRONG vo. Cat cua so + gai + lo vit tren vo sau (truoc khi tach nua).
VOL_D = dict(neck=3.0, cone=3.0, band=2.0)
VOL_ZB = VOL_D['neck'] + VOL_D['cone'] + VOL_D['band']          # mat duoi nap (u tu mat ngoai pod)
VOL_RIM = VOL_ZB + MX_TRAVEL + MX_HOUSING_H                       # 13,4: vai switch (than tren) tua o day
YF = -body_y(VOL_X, VOL_Z) - POD_RECESS                           # mat ngoai pod (mat phang y = YF)
def MP(sx): return Matrix(((sx, 0, 0, sx * VOL_X), (0, 0, -1, YF), (0, 1, 0, VOL_Z), (0, 0, 0, 1)))   # pod local (a, c, u) -> the gioi; sx=-1 = guong (a nguoc)
SW_AU = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))     # (p, q, r) -> pod (a, c, u) = (p, r, q): da giac (a,u) keo doc c
SW_CU = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))     # (p, q, r) -> pod (a, c, u) = (r, p, q): da giac (c,u) keo doc a
def lbox(mn, mx, M): return place(box('lb', mn, mx), M)
def pau(poly, c0, c1, M): return extrude('pau', poly, c0, c1, M @ SW_AU)
def pcu(poly, a0, a1, M): return extrude('pcu', poly, a0, a1, M @ SW_CU)
def lcyl(a, c, u0, u1, r, M, seg=48): return cyl('lc', M @ Vector((a, c, u0)), M @ Vector((a, c, u1)), r, seg=seg)
SHAFT_U = YF - 1.0                                                # day gieng: y = 1 (duoi mai/ khoang trong)
G, W_, D_, CB_, CT_ = POD_GAP, POD_W, POD_D, POD_CB, POD_CT
TENT_Y = lambda x: Y0 - 0.5 + (TENT_XM - abs(x)) / TENT_SL          # tran mai chu A (45 do) tai |x|
SKIP = os.environ.get('OWL_SKIP', '')
SCREW_INFO = []
for sx in (-1, 1):
    M = MP(sx); Wn = W_ + G
    if 'WIN' not in SKIP: diff(S, lbox((-Wn, CB_ - G, -14.0), (Wn, CT_ + G, SHAFT_U), M))                 # cua so cot (tuong dung): pod luon tu trong ra
    for (a_, c_) in POD_HOLES:
        x_s, z_s = sx * (VOL_X + a_), VOL_Z + c_
        diff(S, cyl('pilot', (x_s, TENT_Y(x_s) - 1.5, z_s), (x_s, TENT_Y(x_s) + SCR_PILOT_DEPTH, z_s), SCR_PILOT / 2, seg=24))   # lo moi 2,2 khoan vao tran vo dac (khong thung ra ngoai)
        SCREW_INFO.append(dict(x=round(x_s, 1), z=round(z_s, 1), wall_outside=round(-body_y(x_s, z_s) - (TENT_Y(x_s) + SCR_PILOT_DEPTH), 1)))
# chot dinh vi o cac khoi dac (tai, canh, vanh nut): lo O2 sau 8 moi nua
for (px, pz) in ((-43, 142), (43, 142), (-34, 130), (34, 130), (-28.7, 160), (28.7, 160)):
    diff(S, cyl('pin', (px, Y0 - PIN_HALF, pz), (px, Y0 + PIN_HALF, pz), PIN_D / 2, seg=16))

# ============================================================ TACH 2 NUA
SRC = cp(S, 'src')
A = S; B = cp(S, 'back')
inter(A, box('fr', (-300, -300, -50), (300, Y0, 300)))
inter(B, box('bk', (-300, Y0, -50), (300, 300, 300)))
diff(B, box('usb', (-20, Y0 - 1.0, 3), (20, 70, FLOOR_CUT + 12)))    # khe cap USB: khoet RIENG nua sau (khong dung mat rap)
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
bp = [(0, -9.0), (11.0, -9.0), (11.0, -6.2), (9, -6.2), (9, 0.0)]
bp += [(9 * math.cos(math.radians(a)), 7.5 * math.sin(math.radians(a))) for a in range(10, 91, 10)]
BEAK = lathe('beak', bp[:-1] + [(0, 7.5)], seg=64, M=BEAK_M)

# --- nut dau (talk): vanh trong O58 vat 45 do (in up dau xuong khong support), lo chu thap 4,19 x 1,25 o mat duoi (cam than MX), nap tren yen non cua vo
def cross_cutters(M, u_open, depth, dirn, angs=(45.0, 135.0)):
    """Lo chu thap (2 thanh 4,19 x 1,25, xoay 45 do cung than switch) tu mat u_open vao 'depth' mm theo huong dirn (+1/-1) doc truc local z."""
    out = []
    for ang in angs:
        z0, z1 = sorted((u_open - dirn * 0.2, u_open + dirn * depth))
        b_ = box('crs', (-MX_STEM_L / 2, -MX_STEM_W / 2, z0), (MX_STEM_L / 2, MX_STEM_W / 2, z1))
        b_.data.transform(M @ Matrix.Rotation(math.radians(ang), 4, 'Z')); out.append(b_)
    return out
cp_ = [(0, BTN_TOP), (19, BTN_TOP)] + arc(19, BTN_TOP - 6, 6, 90, 0, 8)[1:]
cp_ += [(25.0, SEAT_Z + REST_UP + 0.1), (TALK_FLANGE_R, SEAT_Z + REST_UP + 0.1 - (TALK_FLANGE_R - 25.0)), (TALK_FLANGE_R, TALK_ZB + REST_UP), (0, TALK_ZB + REST_UP)]
CAP = lathe('cap', cp_, seg=96, M=Matrix.Translation((0, Y0, 0)))
for o_ in cross_cutters(Matrix.Translation((0, Y0, TALK_ZB + REST_UP)), 0.0, MX_STEM_H, 1):
    diff(CAP, o_)

# --- 2 nap nut am luong nho (in up dau xuong): dau O16 co dau + / - lom (khong noi -> mat day phang), co O8 xuyen vo, non 45 do, vanh O14,4, lo chu thap o mat tren
VOL_HEAD_R, VOL_HEAD_H = 8.6, 3.5
def make_vol_cap(plus):
    z_neck, z_cone, z_top = VOL_HEAD_H, VOL_HEAD_H + VOL_D['neck'], VOL_HEAD_H + VOL_ZB
    pr = [(0, 0), (VOL_HEAD_R - 0.6, 0), (VOL_HEAD_R, 0.6), (VOL_HEAD_R, z_neck), (VOL_NECK_R, z_neck), (VOL_NECK_R, z_cone),
          (VOL_FLANGE_R, z_cone + (VOL_FLANGE_R - VOL_NECK_R)), (VOL_FLANGE_R, z_top), (0, z_top)]
    c = lathe('vcap', pr, seg=48)
    bars = [(9.0, 1.8)] + ([(1.8, 9.0)] if plus else [])
    for (w, h) in bars:
        diff(c, box('sym', (-w / 2, -h / 2, -0.1), (w / 2, h / 2, 0.8)))
    for o_ in cross_cutters(Matrix.Translation((0, 0, z_top)), 0.0, MX_STEM_H, -1, (0.0, 90.0)):   # chu thap thang truc (switch trong pod khong xoay 45 do)
        diff(c, o_)
    return c
VCAPS = {1: make_vol_cap(True), -1: make_vol_cap(False)}          # +x: vol_up (+), -x: vol_down (-)
def vol_cap_world(sx):
    o = cp(VCAPS[sx], 'vcapw%d' % sx)
    place(o, Matrix(((1, 0, 0, sx * VOL_X), (0, 0, -1, YF + VOL_HEAD_H + REST_UP), (0, 1, 0, VOL_Z), (0, 0, 0, 1))))   # z cuc bo -> u = z - dau - nang len 0,2; y = YF - u
    return o
VCAPS_W = {sx: vol_cap_world(sx) for sx in (-1, 1)}

# --- vol-pod (in MAT NGOAI XUONG, khong support): tam ngoai day 3 co kenh truot (co nap O8 truot tu mep HO duoi), kenh vai switch 15,8 (nap + than tren), mieng 45 do ->
#     o switch 14,00 (press) + ranh V (fit-library catpaw/mx-socket) mo ra mat trong; gai 45 do ben ngoai (chua 2 hoc dai oc M3) + gai tren de ty vao tran vo.
#     Lap tren ban: nap + switch truot vao kenh tu mep duoi (nap co chu thap), vo giu lai o cua so (nap khong truot ra duoc: dau nap tuy vao mep cua so).
O_LOC = outer(); O_LOC.data.transform(MP(1).inverted())            # be mat ngoai vo trong he cuc bo cua pod
def make_pod():
    L = Matrix.Identity(4); bw = POD_BAY / 2
    pod = lbox((-W_, CB_, -14.0), (W_, CT_, D_), L)
    inter(pod, cp(O_LOC, 'oloc'))                                  # mat ngoai pod = be mat vo (cong theo vach lung)
    ut = lambda a: YF - TENT_Y(VOL_X + a) + EAR_GAP                  # u cua mat tren tai pod tai a (song song tran mai, khe 0,4)
    union(pod, pau([(POD_STRIP[0], D_), (POD_STRIP[1], D_), (POD_STRIP[1], ut(POD_STRIP[1])), (POD_STRIP[0], ut(POD_STRIP[0]))], POD_STRIP[2], POD_STRIP[3], L))   # tai giu vit (phia tren)
    cb = CB_ - 0.1
    cuts = [lcyl(0.0, 0.0, -14.0, POD_PLATE + 0.05, VOL_HOLE_R, L), lbox((-VOL_HOLE_R, cb, -14.0), (VOL_HOLE_R, 0.0, POD_PLATE + 0.05), L),   # kenh co nap (xuyen lop da)
            lcyl(0.0, 0.0, -14.0, 0.0, POD_DISH_R, L, 64),                                                                                      # lom dau nap
            pau([(-VOL_HOLE_R, POD_PLATE - 0.05), (VOL_HOLE_R, POD_PLATE - 0.05), (bw, POD_PLATE + bw - VOL_HOLE_R), (-bw, POD_PLATE + bw - VOL_HOLE_R)], cb, POD_CLOSE, L),   # yen non 45 do cho non nap
            lbox((-bw, cb, POD_PLATE + bw - VOL_HOLE_R - 0.05), (bw, POD_CLOSE, VOL_RIM - 0.1), L),                                             # kenh vai
            pau([(-bw, VOL_RIM - 0.2), (bw, VOL_RIM - 0.2), (MX_HOLE / 2, VOL_RIM + 0.8), (-MX_HOLE / 2, VOL_RIM + 0.8)], cb, POD_CLOSE, L),   # vat 45 do ve 14,00
            lbox((-MX_HOLE / 2, cb, VOL_RIM + 0.7), (MX_HOLE / 2, POD_CLOSE, D_ + 0.1), L)]                                                     # o switch 14,00 (mo ra mat trong)
    g0, g1, g2, gw = MX_GROOVE; hw = MX_HOLE / 2; gh = gw / 2
    cuts.append(pau([(-hw, VOL_RIM + g0), (-gh, VOL_RIM + g1), (-hw, VOL_RIM + g2), (hw, VOL_RIM + g2), (gh, VOL_RIM + g1), (hw, VOL_RIM + g0)], cb, POD_CLOSE, L))   # ranh V
    for (a_, c_) in POD_HOLES:
        cuts.append(lcyl(a_, c_, ut(a_) - 0.1, D_ + 0.1, SCR_CLEAR / 2, L, 24))                                                                # lo vit 2,8
        cuts.append(lcyl(a_, c_, ut(a_) + G_HEAD, D_ + 0.1, SCR_HEAD / 2, L, 32))                                                              # hoc dau vit O5,0 (mat dau cach mat tai 4,0)
    for c_ in cuts:
        diff(pod, c_)
    return pod
POD_LOCAL = make_pod()
def pod_world(sx):
    o = cp(POD_LOCAL, 'podw%d' % sx); place(o, MP(sx)); return o
PODS_W = {sx: pod_world(sx) for sx in (-1, 1)}
def MK(sx): return Matrix(((1, 0, 0, sx * VOL_X), (0, 0, -1, YF), (0, 1, 0, VOL_Z), (0, 0, 0, 1)))   # switch: (a, b, u) -> (x, y = YF - u, z)

def mx_dummy(M, u_rim, name, rot=45.0):
    """Khoi gia switch MX kich thuoc that (xoay 45 do quanh truc): than duoi 14 x 14 sau 5,0 + 2 chan; than tren 15,6 x 15,6 cao 3,0; chan chu thap 4,0 x 1,2 cao 3,6 (TODO kiem switch that)."""
    R45 = Matrix.Rotation(math.radians(rot), 4, 'Z')
    parts = [box('lo', (-MX_HOLE / 2, -MX_HOLE / 2, u_rim), (MX_HOLE / 2, MX_HOLE / 2, u_rim + MX_BODY_W)),
             box('up', (-MX_BODY_UP / 2, -MX_BODY_UP / 2, u_rim - MX_HOUSING_H), (MX_BODY_UP / 2, MX_BODY_UP / 2, u_rim)),
             box('c1', (-2.0, -0.6, u_rim - MX_HOUSING_H - MX_STEM_H), (2.0, 0.6, u_rim - MX_HOUSING_H + 0.01)),
             box('c2', (-0.6, -2.0, u_rim - MX_HOUSING_H - MX_STEM_H), (0.6, 2.0, u_rim - MX_HOUSING_H + 0.01))]
    for (px, py) in ((-3.81, 2.54), (2.54, 5.08)):
        parts.append(cyl('pin', (px, py, u_rim + MX_BODY_W - 0.01), (px, py, u_rim + MX_BODY_W + 3.3), 0.8, seg=12))
    o = parts[0]
    for q in parts[1:]:
        union(o, q)
    place(o, M @ R45)
    o.name = name
    return o
MXSW = {'talk': mx_dummy(MT, 0.0, 'mx_talk'), 'vol_up': mx_dummy(MK(1), VOL_RIM, 'mx_up', 0.0), 'vol_down': mx_dummy(MK(-1), VOL_RIM, 'mx_dn', 0.0)}

# --- kinh khuech tan mat (1 cai); vanh giu
dp = [(0, -6.0), (20, -6.0), (20, -9.8), (18.8, -9.8), (18.8, -6.0 - DIFFUSER_T), (0, -6.0 - DIFFUSER_T)]
DIFFS = [lathe('diff%d' % i, dp, seg=72, M=M) for i, M in enumerate(EYES)]

# --- vong mat kem (x2): dan len vo, mat sau theo be mat than, mat truoc phang; in mat truoc xuong
RINGS = []
for M in EYES:
    r = cyl_local('ring', M, -16.0, RING_T, RING_D / 2, seg=96)        # mat truoc PHANG (vuong goc truc mat) cach tiep diem RING_T: in up mat phang xuong, khong support
    diff(r, outer())
    diff(r, cyl_local('rw', M, -30, 12, 18.2, seg=72))
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
T_ring = Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1))) @ EYES[1].inverted()      # mat truoc phang xuong ban
export_obj(RINGS[1], T_ring, OUT / "eye-ring.stl")
export_obj(PLATE, Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, FLOOR_CUT), (0, 0, 0, 1))), OUT / "base-plate.stl")   # lat: mat sat vo (rong hon) xuong ban -> mep vo thon dan len, khong treo
T_pod = Mx(((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, D_), (0, 0, 0, 1)))   # in MAT TRONG xuong ban (mat ngoai cong huong len), xoay 180 do quanh c
export_obj(POD_LOCAL, T_pod, OUT / "vol-pod-up.stl")      # +x (vol_up)
_pm = cp(POD_LOCAL, 'podmir'); place(_pm, Matrix.Diagonal((-1, 1, 1, 1)))
export_obj(_pm, T_pod, OUT / "vol-pod-down.stl")          # -x (vol_down): guong
export_obj(VCAPS[1], Matrix.Identity(4), OUT / "mx-cap-vol-up.stl")
export_obj(VCAPS[-1], Matrix.Identity(4), OUT / "mx-cap-vol-down.stl")
export_obj(BEZEL_LOCAL, Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, SPK_XF), (0, 0, 0, 1))), OUT / "speaker-bezel.stl")
export_obj(SRING_LOCAL, Matrix.Identity(4), OUT / "speaker-ring.stl")   # day vong ep xuong ban, ong tay huong len

# lap rap
asm = bmesh.new()
for o in [A, B, PLATE, BELLY, BEAK, CAP, VCAPS_W[1], VCAPS_W[-1], PODS_W[1], PODS_W[-1]] + BEZELS + SRINGS + DIFFS + RINGS:
    asm.from_mesh(o.data)
am = bpy.data.meshes.new('asm'); asm.to_mesh(am); asm.free()
ao = bpy.data.objects.new('asm', am); SC.collection.objects.link(ao)
for ob in bpy.context.view_layer.objects:
    ob.select_set(False)
ao.select_set(True); bpy.context.view_layer.objects.active = ao
bpy.ops.wm.stl_export(filepath=str(OUT / "owl-assembled.stl"), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
bpy.data.objects.remove(ao)

# do that do lech mat ngoai pod so voi be mat vo (BVH raycast tu ngoai vao, doc vien cua so; mat vo lay cach vien 0,35 mm ra ngoai cua so) + do nho cua nap
from mathutils.bvhtree import BVHTree
def _bvh(o):
    bm_ = bmesh.new(); bm_.from_mesh(o.data); t_ = BVHTree.FromBMesh(bm_); bm_.free(); return t_
T_SHELL = _bvh(B)
def _top(t_, x, z):
    h = t_.ray_cast(Vector((x, 120.0, z)), Vector((0, -1, 0)))
    return None if h[0] is None else h[0].y
FLUSH_DEV, CAP_PROT = 0.0, 0.0
for sx in (-1, 1):
    T_POD = _bvh(PODS_W[sx]); n_ok = 0
    for k in range(0, 41):
        for (a_, c_) in ((-W_ + 0.02 + (2 * W_ - 0.04) * k / 40, CB_ + 0.02), (-W_ + 0.02 + (2 * W_ - 0.04) * k / 40, CT_ - 0.02),
                         (-W_ + 0.02, CB_ + 0.02 + (CT_ - CB_ - 0.04) * k / 40), (W_ - 0.02, CB_ + 0.02 + (CT_ - CB_ - 0.04) * k / 40)):
            x_, z_ = sx * (VOL_X + a_), VOL_Z + c_
            yp = _top(T_POD, x_, z_)
            dx_, dz_ = (0.0, 0.0)
            if c_ <= CB_ + 0.05: dz_ = -(G + 0.05)
            elif c_ >= CT_ - 0.05: dz_ = G + 0.05
            elif a_ <= -W_ + 0.05: dx_ = -sx * (G + 0.05)
            else: dx_ = sx * (G + 0.05)
            ys = _top(T_SHELL, x_ + dx_, z_ + dz_)
            if yp is None or ys is None:
                continue
            n_ok += 1; FLUSH_DEV = max(FLUSH_DEV, abs(yp - ys))
    assert n_ok > 100, "raycast khong du mau"
    yc = -body_y(sx * VOL_X, VOL_Z); CAP_PROT = max(CAP_PROT, YF + VOL_HEAD_H + REST_UP + 0.0 - yc)
FLUSH_DEV, CAP_PROT = round(FLUSH_DEV, 2), round(CAP_PROT, 2)
print("FLUSH_MAX_DEV %.2f CAP_PROT %.2f" % (FLUSH_DEV, CAP_PROT))

params = dict(wall=WALL, speaker_pocket_d=SPEAKER_POCKET_D, grille_hole_d=GRILLE_HOLE_D, mic_hole_d=MIC_HOLE_D, m3_clear_d=M3_CLEAR_D,
              m3_nut_s=M3_NUT_S, button_cap_d=BUTTON_CAP_D, button_hole_d=BUTTON_HOLE_D, diffuser_t=DIFFUSER_T, vent_w=VENT_W,
              speakers=SPEAKERS, pcb_center=PCB_CENTER, pcb_box=list(PCB_BOX),
              split_plane_y=Y0, grille_holes_per_speaker=GRILLE_N, speaker_dims=[SPEAKER_D, SPEAKER_L], pcb_dims_xyz=list(PCB_BOX),
              belly=dict(z=BELLY_Z, front_y=BELLY_FRONT, rf=BELLY_RF), eye=dict(x=EYE_X, z=EYE_Z), beak_z=BEAK_Z,
              screws=dict(x=SCREW_X, y=SCREW_Y, m3_nut_depth=NUT_DEPTH),
              speaker_clamp=dict(flange_t=FLANGE_T, gasket_t=GASKET_T, body_d_max=BODY_D_MAX, ring_t=SRING_T, ring_id=RING_ID,
                                 bayonet=dict(n=len(BAY_ANG), twist=BAY_TWIST, pin_w=BPIN_W, pin_h=BPIN_H, pin_t=BPIN_T, sleeve_clr=SLEEVE_CLR, pin_clr=BPIN_CLR,
                                 groove_clr=GROOVE_CLR, lip_pre=LIP_PRE, out_gap=OUT_GAP, sleeve_t=SLEEVE_T), gasket_locked=round(GASKET_T - LIP_PRE, 3),
                                 face_abs_x=SPK_FACE, cup_end_abs_x=CUP_END), pins=dict(d=PIN_D, half_depth=PIN_HALF), floor_cut=FLOOR_CUT, cone_clearance=CONE_CLR, fit=FIT, slide=SLIDE,
              mx=dict(hole=MX_HOLE, socket_depth=MX_DEPTH, stem_cross_l=MX_STEM_L, stem_cross_w=MX_STEM_W, stem_cross_depth_used=MX_STEM_H,
                      groove=dict(from_rim=MX_GROOVE[0], deepest_at=MX_GROOVE[1], to=MX_GROOVE[2], width=MX_GROOVE[3]),
                      rotated_deg=45, travel_used=MX_TRAVEL, stem_insert=MX_INSERT, source="fit-library catpaw/mx-socket + catpaw/mx-keycap-cross; than switch 15,6 x 15,6 cao 3,0 + chan chu thap 3,6, than duoi 5,0: TODO kiem switch that",
                      keys=[dict(name="talk", gpio=23, key="KEY4", axis="z", pos=[0, Y0, TALK_RIM], flange_r=TALK_FLANGE_R, hole_r=BUTTON_HOLE_D / 2, flange_over=round(TALK_FLANGE_R - BUTTON_HOLE_D / 2, 2)),
                            dict(name="vol_up", gpio=18, key="KEY5", axis="y", pos=[VOL_X, round(YF, 2), VOL_Z], flange_r=VOL_FLANGE_R, hole_r=VOL_HOLE_R, flange_over=round(VOL_FLANGE_R - VOL_HOLE_R, 2)),
                            dict(name="vol_down", gpio=5, key="KEY6", axis="y", pos=[-VOL_X, round(YF, 2), VOL_Z], flange_r=VOL_FLANGE_R, hole_r=VOL_HOLE_R, flange_over=round(VOL_FLANGE_R - VOL_HOLE_R, 2))]),
              vol_pod=dict(parts=["vol-pod-up", "vol-pod-down"], face_y=round(YF, 2), center_x=VOL_X, center_z=VOL_Z, recess=POD_RECESS, depth=POD_D, flush_max_dev=FLUSH_DEV, cap_protrusion=CAP_PROT,
                           window=dict(width=2 * (POD_W + POD_GAP), height=CT_ - CB_ + 2 * POD_GAP, gap=POD_GAP), flange_margin=dict(ear_c_top=POD_STRIP[3] - POD_CT, ear_a=[POD_STRIP[0], POD_STRIP[1]]),
                           screws={"side": "inside", "size": "M2.5", "type": "tu ren, dau chim", "pilot_d": SCR_PILOT, "clear_d": SCR_CLEAR, "head_d": SCR_HEAD, "head_gap_to_ear": G_HEAD, "per_pod": 2,
                                   "len": SCR_LEN, "engage": round(SCR_LEN - G_HEAD - EAR_GAP, 1), "pilot_depth": SCR_PILOT_DEPTH, "boss": "khoi tran mai dac (khong tru roi)", "info": SCREW_INFO},
                           channel=dict(neck_slot=2 * VOL_HOLE_R, bay=POD_BAY, plate=POD_PLATE, open_edge="bottom")))
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
pcbo = box('pcb', (-PCB_BOX[0] / 2, PCB_CENTER[1] - PCB_BOX[1] / 2, PCB_CENTER[2] - PCB_BOX[2] / 2), (PCB_BOX[0] / 2, PCB_CENTER[1] + PCB_BOX[1] / 2, PCB_CENTER[2] + PCB_BOX[2] / 2))
ITEMS = [(A, 'front', 'shell', (0, -75, 0)), (B, 'back', 'shell', (0, 75, 0)), (PLATE, 'plate', 'cream', (0, 0, -45)), (BELLY, 'belly', 'cream', (0, -130, 0)),
         (BEAK, 'beak', 'butter', (0, -135, 30)), (CAP, 'cap', 'butter', (0, 0, 55)), (BEZELS[0], 'bz0', 'shell', (-105, 0, 0)), (BEZELS[1], 'bz1', 'shell', (105, 0, 0)), (SRINGS[0], 'sr0', 'cream', (-25, 0, 0)), (SRINGS[1], 'sr1', 'cream', (25, 0, 0)),
         (DIFFS[0], 'd0', 'white', (-30, -110, 25)), (DIFFS[1], 'd1', 'white', (30, -110, 25)), (RINGS[0], 'r0', 'cream', (-40, -100, 0)), (RINGS[1], 'r1', 'cream', (40, -100, 0)),
         (spk[0], 's0', 'spk', (-55, 0, 0)), (spk[1], 's1', 'spk', (55, 0, 0)), (pcbo, 'pcb', 'pcb', (0, 0, 0)),
         (VCAPS_W[1], 'cvu', 'butter', (70, 170, 10)), (VCAPS_W[-1], 'cvd', 'butter', (-70, 170, 10)),
         (PODS_W[1], 'pdu', 'shell', (70, 110, 10)), (PODS_W[-1], 'pdd', 'shell', (-70, 110, 10)),
         (MXSW['talk'], 'mxt', 'spk', (0, 0, 40)), (MXSW['vol_up'], 'mxu', 'spk', (70, 140, 10)), (MXSW['vol_down'], 'mxd', 'spk', (-70, 140, 10))]
for o, n, c, off in ITEMS:
    dump(o, n)
# ban lap rap DO DUOC (Tuan 2026-11-06): moi chi tiet 1 STL o dung vi tri lap (mm) -> export_cad.py ra .blend + STEP
ASM_NAMES = dict(front="shell-front", back="shell-back", plate="base-plate", belly="belly", beak="beak", cap="button-cap",
                 bz0="speaker-bezel-L", bz1="speaker-bezel-R", sr0="speaker-ring-L", sr1="speaker-ring-R", d0="eye-diffuser-L",
                 d1="eye-diffuser-R", r0="eye-ring-L", r1="eye-ring-R", s0="speaker-dummy-L", s1="speaker-dummy-R", pcb="pcb-dummy", cvu="mx-cap-vol-up", cvd="mx-cap-vol-down", pdu="vol-pod-up", pdd="vol-pod-down", mxt="mx-switch-talk", mxu="mx-switch-vol_up", mxd="mx-switch-vol_down")
(OUT / "asm").mkdir(exist_ok=True)
import shutil
for _, n, _, _ in ITEMS:
    shutil.copyfile(TMP / (n + ".stl"), OUT / "asm" / (ASM_NAMES[n] + ".stl"))

import os
if os.environ.get("OWL_FAST"):   # chi sinh STL + params, bo qua anh Eevee (dung khi lap thiet ke)
    shutil.rmtree(TMP, ignore_errors=True); print("BUILD OK (fast)"); sys.exit(0)

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

ASM = ['front', 'back', 'plate', 'belly', 'beak', 'cap', 'cvu', 'cvd', 'pdu', 'pdd', 'bz0', 'bz1', 'sr0', 'sr1', 'd0', 'd1', 'r0', 'r1']
sc = fresh_scene((800, 1200)); load_items(sc, ASM, False)
cam_at(sc, (0, 0, 85), -32, 12, 560); render_png(sc, OUT / "_v1.png")
bpy.data.objects.remove(sc.camera)
cam_at(sc, (0, 0, 85), 148, 18, 560); render_png(sc, OUT / "_v2.png")
merge(OUT / "_v1.png", OUT / "_v2.png", OUT / "owl-preview.png")
sc = fresh_scene((1600, 1200)); load_items(sc, [n for _, n, _, _ in ITEMS], True)
cam_at(sc, (0, -20, 75), -30, 22, 950, 70); render_png(sc, OUT / "owl-exploded.png")
# anh nhin thang tu LUNG (2 nut am luong) + anh cum nut tach lop
sc = fresh_scene((1100, 1400)); load_items(sc, ASM, False)
cam_at(sc, (0, 0, 95), 180, 4, 520); render_png(sc, OUT / "owl-back.png")
def load_off(sc, offs):
    for o, n, c, off in ITEMS:
        if n not in offs:
            continue
        bpy.ops.wm.stl_import(filepath=str(TMP / (n + ".stl")))
        ob = bpy.context.selected_objects[0]
        m = bpy.data.materials.new(n); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = hexc(PCOL[c]); b.inputs['Roughness'].default_value = 0.6
        ob.data.materials.append(m); ob.location = offs[n]
sc = fresh_scene((1600, 1000))
load_off(sc, dict(pdu=(0, 0, 0), pdd=(0, 0, 0), mxu=(0, 26, 0), mxd=(0, 26, 0), cvu=(0, 52, 0), cvd=(0, 52, 0)))
cam_at(sc, (0, YF + 20, VOL_Z), 215, 28, 330, 60); render_png(sc, OUT / "vol-pod.png")
for f in ("_v1.png", "_v2.png"):
    (OUT / f).unlink()
shutil.rmtree(TMP, ignore_errors=True)
print("BUILD OK")
