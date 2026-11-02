# Dung khung lap rap tay may cyberbrick-arm TU THAM SO (chay lai = model moi, khong sua tay trong FreeCAD).
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" freecad/scripts/build_arm.py
# Ra: ARM_OUT (mac dinh freecad/cyberbrick_arm.FCStd) + <ARM_OUT>.json. File dich co san -> backup truoc khi ghi.
# He truc: X truoc, Y trai, Z len; goc = tam truc de tren mat ban. Don vi mm / do.
import json
import math
import os
import shutil
import time
from pathlib import Path

import FreeCAD as App
import Part

V = App.Vector
HERE = Path(__file__).resolve().parent
PROJ = HERE.parent.parent
P = json.loads(Path(os.environ.get('ARM_PARAMS', str(PROJ / 'freecad' / 'params.json'))).read_text(encoding='utf-8'))
OUT = Path(os.environ.get('ARM_OUT', str(PROJ / 'freecad' / 'cyberbrick_arm.FCStd'))).resolve()
pose = os.environ.get('ARM_POSE', 'tu_the_mac_dinh')
if pose == 'tu_the_mac_dinh':
    pose = P['tu_the_mac_dinh']
t1, phi = P['tu_the'][pose]
K = P['khe']
DANG = P['dang']
VAT_DAY = DANG['vat_day']
VAT_CANH = DANG['vat_canh']
VAT_FORE = DANG['vat_cang_tay_canh']
VAT_HEAD = DANG['vat_dau_kep']
VAT_ARM = DANG['tay_tren_bat_giac_vat']
doc = App.newDocument('cyberbrick_arm')
LIB = PROJ.parent.parent / 'community' / 'cyberbrick-official' / 'models'
GREY = (0.82, 0.84, 0.86)
DARK = (0.12, 0.12, 0.13)
ORANGE = (1.0, 0.43, 0.08)
SERVO_P0 = V(16.69, 5.9, -14.52)  # dinh truc ra trong he local STEP PG001


def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, h, base, axis):
    return Part.makeCylinder(r, h, V(*base), V(*axis))


def add(name, shape, col=GREY):
    if shape.Volume < 0:
        shape.reverse()
    o = doc.addObject('Part::Feature', name)
    o.Label = name
    o.Shape = shape
    try:
        o.ViewObject.ShapeColor = col
    except Exception:
        pass
    return o


def step(key):
    return Part.read(str(LIB / P['linh_kien'][key]))


def rot_matrix(ex, ey, ez):
    """Ma tran 3x3 voi cot = anh cua e_x, e_y, e_z (FreeCAD Matrix.multVec = M.p)."""
    M = App.Matrix()
    M.A11, M.A21, M.A31 = ex
    M.A12, M.A22, M.A32 = ey
    M.A13, M.A23, M.A33 = ez
    return M


def bake(shape, M):
    q = shape.copy()
    q.Placement = App.Placement()
    q.transformShape(M)
    return q


def place_p0(shape, ex, ey, ez, target, p0):
    """dat = R.(p - P0) + target (R co cot la anh cua e_x,e_y,e_z)."""
    M = rot_matrix(ex, ey, ez)
    R = App.Rotation(M)
    t = V(*target) - R.multVec(V(*p0))
    M.A14, M.A24, M.A34 = t.x, t.y, t.z
    return bake(shape, M)


def place_center(shape, rot, target):
    """xoay quanh goc roi dich de tam hop bao trung `target`."""
    q = bake(shape, rot.toMatrix())
    q.translate(V(*target) - q.BoundBox.Center)
    return q


def cavity(shape, margin=K):
    b = shape.BoundBox
    return box(b.XMin - margin, b.YMin - margin, b.ZMin - margin,
               b.XMax + margin, b.YMax + margin, b.ZMax + margin)


# ---------------- Vat canh / logo (phuong an B) ----------------
def _chamfer_once(shape, dist, edges):
    if not edges:
        return shape
    try:
        r = shape.makeChamfer(dist, edges)
        if r.isValid() and len(r.Solids) == len(shape.Solids) and r.Volume > 0:
            return r
    except Exception:
        pass
    return shape


def chamfer_first(shape, dist, preds):
    """Thu tung nhom, dung o nhom dau tien vat duoc."""
    for pred in preds:
        r = _chamfer_once(shape, dist, [e for e in shape.Edges if pred(e)])
        if r is not shape:
            return r
    return shape


def chamfer_groups(shape, dist, preds):
    """Vat lan luot tung nhom; nhom nao loi thi bo qua nhom do."""
    out = shape
    for pred in preds:
        out = _chamfer_once(out, dist, [e for e in out.Edges if pred(e)])
    return out


def flat_z(e, z, tol=1e-3):
    b = e.BoundBox
    return abs(b.ZMin - z) < tol and abs(b.ZMax - z) < tol


def par_y(e, tol=1e-4):
    b = e.BoundBox
    return b.XLength < tol and b.ZLength < tol and b.YLength > tol


def par_dir(e, vec, tol=0.999):
    try:
        return abs(e.tangentAt(0.5).dot(vec.normalize())) > tol
    except Exception:
        return False


def is_line(e):
    return e.Curve.TypeId == 'Part::GeomLine'


def rim(z, rad, tol=0.05):
    def pred(e):
        b = e.BoundBox
        if abs(b.ZMin - z) > 1e-3 or abs(b.ZMax - z) > 1e-3:
            return False
        return all(abs(math.hypot(v.Point.x, v.Point.y) - rad) < tol for v in e.Vertexes)
    return pred


def text_tool(text, font, width, height, depth, cols, base):
    """Chu khac: cao height, rong width (scale X), sau depth, dat theo 3 cot cols."""
    import Draft
    obj = Draft.makeShapeString(text, str(font), height, 0)
    shp = obj.Shape.copy()
    doc.removeObject(obj.Name)
    bb = shp.BoundBox
    m = App.Matrix()
    m.A11 = width / bb.XLength
    m.A22 = height / bb.YLength
    m.A33 = 1.0
    m.A14 = -bb.Center.x * m.A11
    m.A24 = -bb.Center.y * m.A22
    m.A34 = -0.1
    shp = shp.transformGeometry(m)
    sol = None
    for f in shp.Faces:
        e = f.extrude(V(0, 0, depth))
        sol = e if sol is None else sol.fuse(e)
    sol = sol.removeSplitter()
    W = App.Matrix(cols[0][0], cols[1][0], cols[2][0], base.x,
                   cols[0][1], cols[1][1], cols[2][1], base.y,
                   cols[0][2], cols[1][2], cols[2][2], base.z,
                   0, 0, 0, 1)
    q = sol.transformGeometry(W)
    if q.Volume < 0:
        q.reverse()
    return q


# ---------------- Co dinh: de ----------------
d = P['de']
f = d['tam_day']
foot = box(-f['rong'] / 2, -f['rong'] / 2, 0, f['rong'] / 2, f['rong'] / 2, f['cao'])
try:
    foot = foot.makeFillet(f['bo_goc_r'],
                           [e for e in foot.Edges if e.BoundBox.ZLength > f['cao'] - 1e-6])
except Exception:
    pass
foot = foot.cut(cyl(f['hoc_r'], f['hoc_sau'] + 1.0,
                    (0, 0, f['cao'] - f['hoc_sau']), (0, 0, 1)))
foot = chamfer_first(foot, VAT_DAY, [
    lambda e: flat_z(e, 0.0),
    lambda e: flat_z(e, 0.0) and is_line(e),
    lambda e: flat_z(e, 0.0) and is_line(e) and e.CenterOfMass.x > 0 and abs(e.CenterOfMass.y) < 1e-6])
add('Foot_plate', foot.removeSplitter())

# ---------------- Quay theo de ----------------
tr = d['trong']
R = tr['d_ngoai'] / 2
Ri = R - tr['thanh']
z0, z1 = tr['z0'], tr['z1']
drum = cyl(R, z1 - z0, (0, 0, z0), (0, 0, 1))
drum = drum.cut(cyl(Ri, z1 - z0 + 1.0, (0, 0, z0 + tr['san']), (0, 0, 1)))
pin = P['bo_tri']['pin']
R_shelf = R - tr['thanh'] + 0.5
shelf = box(-R_shelf, -(pin['y'][1] + 2.0), tr['ke_pin_z'],
            R_shelf, pin['y'][1] + 2.0, tr['ke_pin_z'] + tr['ke_pin_day'])
shelf = shelf.common(cyl(R_shelf, tr['ke_pin_day'], (0, 0, tr['ke_pin_z']), (0, 0, 1)))
drum = drum.fuse(shelf).removeSplitter()
drum = chamfer_first(drum, VAT_CANH, [rim(z1, R)])
drum = chamfer_first(drum, VAT_DAY, [rim(z0, R)])
kk = DANG['khe_tan_nhiet']
r_khe = R - tr['thanh'] / 2
for i in range(kk['so']):
    ang = math.radians(kk['goc_tam'] + (i - (kk['so'] - 1) / 2) * kk['buoc_goc'])
    sl = Part.makeBox(2.0 * R, kk['rong'], kk['z'][1] - kk['z'][0],
                      V(-R, -kk['rong'] / 2, kk['z'][0]))
    sl.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(ang))
    sl.translate(V(r_khe * math.cos(ang), r_khe * math.sin(ang), 0))
    drum = drum.cut(sl)
add('Base_drum', drum.removeSplitter())

g = d['banh_rang_nho']
add('Pinion_24T', cyl(g['d'] / 2, g['day'], (g['tam'][0], g['tam'][1], g['z0']), (0, 0, 1)), ORANGE)

# Motor 030: local dai theo Y -> world X; tam hop bao trung tam bo_tri.hop_so.
gb = P['bo_tri']['hop_so']
mot = step('motor_030')
mot = mot.Solids[0].fuse(mot.Solids[1])
mot = place_center(mot, App.Rotation(V(0, 0, 1), -90),
                   tuple((gb[k][0] + gb[k][1]) / 2 for k in ('x', 'y', 'z')))
add('CB_Motor_030', mot, DARK)
add('Gearbox_shell', box(gb['x'][0], gb['y'][0], gb['z'][0],
                         gb['x'][1], gb['y'][1], gb['z'][1]).cut(mot))

# Bo thu XA004: ca 13 solid (bo day), xoay local Y -> world Z (canh 21,5 thang dung), giua hop bo_tri.bo_thu.
rc = step('bo_thu')
rcv = rc.Solids[0]
for s in rc.Solids[1:]:
    rcv = rcv.fuse(s)
bt = P['bo_tri']['bo_thu']
add('CB_XA004_receiver',
    place_center(rcv, App.Rotation(V(1, 0, 0), 90),
                 tuple((bt[k][0] + bt[k][1]) / 2 for k in ('x', 'y', 'z'))), DARK)

# Pin PC003: chi than pin (bo day): solid goc local Y 0..158,9 -> cat con Y 0..51,2.
# STEP chi day 16,3 (dinh 18,5 nam o dau day phia xa) -> bao khong dat pin_than;
# khi lech > 1,0 mm dung khoi co bao = pin_than (params cho phep "khoi co bao ~ pin_than").
bat = step('pin')
pin_body = bat.Solids[0].common(box(-20.0, 0.0, -10.0, 20.0, P['linh_kien']['pin_than'][1], 12.0))
_pb = pin_body.BoundBox
_pt = P['linh_kien']['pin_than']
if any(abs(a - b) > 1.0 for a, b in zip(sorted([_pb.XLength, _pb.YLength, _pb.ZLength]), sorted(_pt))):
    pin_body = box(-_pt[0] / 2, 0.0, -_pt[2] / 2, _pt[0] / 2, _pt[1], _pt[2] / 2)
add('CB_Battery_PC003',
    place_center(pin_body, App.Rotation(V(0, 0, 1), 90),
                 tuple((pin[k][0] + pin[k][1]) / 2 for k in ('x', 'y', 'z'))), DARK)

# Cong tac XA007: proxy hop bao - STEP hang khong co solid.
sw = step('cong_tac')
swb = sw.BoundBox
sb = P['bo_tri']['gia_cong_tac']
# dat sat mat ngoai trong (x = -R) de khong lan vao thanh trong; ho so mo ve -X.
sw_c = (-(R + swb.XLength / 2), (sb['y'][0] + sb['y'][1]) / 2, (sb['z'][0] + sb['z'][1]) / 2)
sw_proxy = Part.makeBox(swb.XLength, swb.YLength, swb.ZLength,
                        V(sw_c[0] - swb.XLength / 2, sw_c[1] - swb.YLength / 2,
                          sw_c[2] - swb.ZLength / 2))
holder = box(sb['x'][0], sb['y'][0], sb['z'][0], sb['x'][1], sb['y'][1], sb['z'][1])
holder = holder.cut(cyl(R, sb['z'][1] - sb['z'][0] + 2.0, (0, 0, sb['z'][0] - 1.0), (0, 0, 1)))
holder = holder.cut(cavity(sw_proxy))
holder = chamfer_groups(holder, VAT_DAY, [lambda e: flat_z(e, sb['z'][0])])
holder = chamfer_groups(holder, VAT_CANH, [
    lambda e: flat_z(e, sb['z'][1]),
    lambda e: abs(e.BoundBox.ZLength - (sb['z'][1] - sb['z'][0])) < 1e-3])
add('Switch_holder', holder.removeSplitter())
add('CB_Switch_XA007', sw_proxy, DARK)

# Dong hoc thuan.
x1, z1j = P['vai']['J1']
a = math.radians(t1)
b = math.radians(t1 + phi)
L = P['tay_tren']['L']
F = P['cang_tay']['L']
L3 = P['ngon']['L3']
j1 = V(x1, 0, z1j)
j2 = j1 + V(L * math.cos(a), 0, L * math.sin(a))
dv = V(math.cos(b), 0, math.sin(b))
n = V(-dv.z, 0, dv.x)
j3 = j2 + dv * F
tip = j3 + dv * L3

# Servo PG001 (chi Solids[0], 3 solid con lai la day). Dat theo quyet dinh Claude 2026-11-02.
# STEP de RONG long truc (lo vit dan ~1,9 do tu STEP): them loi truc dac cung ban kinh
# de truc ra lien tuc (mo phong vit/horn), khong doi bao ngoai va vi tri P0.
sv = step('servo').Solids[0].fuse(cyl(0.95, 6.5, (16.69, 5.9, -14.5), (0, 0, 1)))
yt = P['tay_tren']['y_trong']
s1 = place_p0(sv, (1, 0, 0), (0, 0, 1), (0, -1, 0),
              (j1.x, yt - 0.1, j1.z), SERVO_P0)
s2 = place_p0(sv, (dv.x, dv.y, dv.z), (n.x, n.y, n.z), (0, -1, 0),
              (j2.x, yt - 0.1, j2.z), SERVO_P0)
s3_t = j2 + dv * P['truc_vit']['s0']
s3 = place_p0(sv, (-n.x, -n.y, -n.z), (0, -1, 0), (-dv.x, -dv.y, -dv.z),
              (s3_t.x, s3_t.y, s3_t.z), SERVO_P0)
add('CB_Servo9g_S1', s1, DARK)
add('CB_Servo9g_S2', s2, DARK)
add('CB_Servo9g_S3', s3, DARK)

# Turntable: dia + thap, khoet cho S1 (xuyen mat +Y cua thap).
ma = P['mam']
th = ma['thap']
turn = cyl(R, ma['day'], (0, 0, ma['z0']), (0, 0, 1)).fuse(
    box(th['x'][0], th['y'][0], ma['z0'] + ma['day'], th['x'][1], th['y'][1], th['z1']))
turn = turn.cut(cavity(s1)).removeSplitter()
turn = chamfer_first(turn, VAT_CANH, [rim(ma['z0'] + ma['day'], R)])
turn = chamfer_first(turn, VAT_DAY, [rim(ma['z0'], R)])
turn = chamfer_first(turn, VAT_CANH, [lambda e: flat_z(e, th['z1'])])
turn = chamfer_first(turn, VAT_CANH, [
    lambda e: abs(e.BoundBox.ZLength - (th['z1'] - ma['z0'] - ma['day'])) < 1e-3])
add('Turntable', turn.removeSplitter())

# Arm_upper_L / R: 2 dau bat giac (bao loi 2 hinh vuong canh 2*r_dau quanh J1, J2), moi goc vat.
tt = P['tay_tren']
thick = tt['day']
rad = tt['r_dau']
hole = tt['lo_d']


def upper(y):
    ax = (j2 - j1).normalize()
    nn = V(-ax.z, 0, ax.x)
    lc = (j2 - j1).Length
    v = VAT_ARM
    pts = [(-rad + v, -rad), (lc + rad - v, -rad), (lc + rad, -rad + v),
           (lc + rad, rad - v), (lc + rad - v, rad), (-rad + v, rad),
           (-rad, rad - v), (-rad, -rad + v)]
    poly = [j1 + ax * u + nn * w for u, w in pts]
    s = Part.Face(Part.makePolygon(poly + [poly[0]])).extrude(V(0, thick, 0))
    s.translate(V(0, y, 0))
    for p in (j1, j2):
        s = s.cut(cyl(hole / 2, thick + 2.0, (p.x, y - 1.0, p.z), (0, 1, 0)))
    s = s.removeSplitter()
    s = chamfer_first(s, VAT_DAY, [
        lambda e: abs(e.BoundBox.YMin - y) < 1e-4 and abs(e.BoundBox.YMax - y) < 1e-4,
        lambda e: abs(e.BoundBox.YMin - y) < 1e-4 and abs(e.BoundBox.YMax - y) < 1e-4 and is_line(e)])
    s = chamfer_first(s, VAT_DAY, [
        lambda e: abs(e.BoundBox.YMin - (y + thick)) < 1e-4 and abs(e.BoundBox.YMax - (y + thick)) < 1e-4,
        lambda e: abs(e.BoundBox.YMin - (y + thick)) < 1e-4 and abs(e.BoundBox.YMax - (y + thick)) < 1e-4 and is_line(e)])
    # khoet cho dia mam quay (goc duoi cua bat giac lan vao dia o tu the nghi)
    return s.cut(turn).removeSplitter()


add('Arm_upper_L', upper(yt))
add('Arm_upper_R', upper(-yt - thick))

# Forearm: he (s, y, n); doan sau n_sau, doan truoc n_truoc.
cf = P['cang_tay']
mat = App.Matrix(dv.x, 0, n.x, 0,
                 0, 1, 0, 0,
                 dv.z, 0, n.z, 0,
                 0, 0, 0, 1)
fore = box(cf['s_sau'], cf['y'][0], cf['n_sau'][0],
           cf['s_doi'], cf['y'][1], cf['n_sau'][1]).fuse(
    box(cf['s_doi'], cf['y'][0], cf['n_truoc'][0],
        F, cf['y'][1], cf['n_truoc'][1]))
# cat vat goc tren-truoc: mat phang s + n = L + n_truoc[1] - vat_cang_tay
nmax = cf['n_truoc'][1]
vf = VAT_FORE
vcat = DANG['vat_cang_tay']
tri = Part.Face(Part.makePolygon([
    V(F - vcat, 0, nmax), V(F - vcat + 200.0, 0, nmax - 200.0),
    V(F - vcat + 400.0, 0, nmax), V(F - vcat + 200.0, 0, nmax + 200.0),
    V(F - vcat, 0, nmax)]))
cutv = tri.extrude(V(0, cf['y'][1] - cf['y'][0] + 10.0, 0))
cutv.translate(V(0, cf['y'][0] - 5.0, 0))
if cutv.Volume < 0:
    cutv.reverse()
fore = fore.cut(cutv)
fore = chamfer_groups(fore, vf, [
    lambda e: par_y(e) and all(v.Point.x > cf['s_doi'] + 1e-6 for v in e.Vertexes),
    lambda e: par_y(e) and all(v.Point.x < cf['s_doi'] - 1e-6 for v in e.Vertexes)])
fore = bake(fore, mat)
fore.translate(j2)
fore = fore.cut(cavity(s2)).cut(cavity(s3))
# lo truc vit xuyen vach truoc cho Worm (truc cang tay)
tv = P['truc_vit']
hole_w = cyl(tv['d'] / 2 + K, F + 2.0 - (tv['s0'] - 1.0),
             (0, 0, 0), (1, 0, 0))  # tam dat sau khi doi he
hole_w = bake(hole_w, mat)
hole_w.translate(j2 + dv * (tv['s0'] - 1.0))
fore = fore.cut(hole_w)
# logo STLAB khac sau 2 mat +-Y, chu doc xuoi tu mat do
lg = DANG['logo']
y0 = cf['y'][1]
fontp = PROJ.parent.parent / lg['font']
base_p = j2 + dv * lg['s'] + n * lg['n'] + V(0, y0, 0)
base_m = j2 + dv * lg['s'] + n * lg['n'] + V(0, -y0, 0)
txt_p = text_tool(lg['chu'], fontp, lg['dai'], lg['cao'], lg['sau'] + 0.1,
                  ((-dv.x, 0, -dv.z), (n.x, 0, n.z), (0, -1, 0)), base_p)
txt_m = text_tool(lg['chu'], fontp, lg['dai'], lg['cao'], lg['sau'] + 0.1,
                  ((dv.x, 0, dv.z), (n.x, 0, n.z), (0, 1, 0)), base_m)
fore = fore.cut(txt_p).cut(txt_m).removeSplitter()
add('Forearm', fore)

# Worm + Head + ngon.
worm = cyl(tv['d'] / 2, tv['dai'], (0, 0, 0), (1, 0, 0))
worm = bake(worm, mat)
worm.translate(j2 + dv * tv['s0'])
add('Worm', worm, ORANGE)

dk = P['dau_kep']
head = box(F, -dk['nua'], -dk['nua'], F + dk['dai'], dk['nua'], dk['nua'])
head = bake(head, mat)
head.translate(j2)
h2 = chamfer_first(head, VAT_HEAD, [lambda e: True])
if h2 is head:
    h2 = chamfer_groups(head, VAT_HEAD, [
        lambda e: par_dir(e, dv), lambda e: par_dir(e, n), lambda e: par_dir(e, V(0, 1, 0))])
add('Head', h2.cut(worm))

ng = P['ngon']
w = ng['tiet_dien']
s_start = F + dk['dai'] + K
s_end = F + L3
for key, deg in ng['goc'].items():
    an = math.radians(deg)
    off = V(0, ng['ban_kinh'] * math.cos(an), 0) + n * (ng['ban_kinh'] * math.sin(an))
    fg = box(s_start, -w / 2, -w / 2, s_end, w / 2, w / 2)
    fg = bake(fg, mat)
    fg.translate(j2 + off)
    add('Finger_' + key, fg)

doc.recompute()
OUT.parent.mkdir(parents=True, exist_ok=True)
if OUT.exists():
    bk = OUT.parent / 'backup'
    bk.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, bk / ('cyberbrick_arm.' + time.strftime('%Y%m%d-%H%M%S') + '.FCStd'))
doc.saveAs(str(OUT))
data = {'pose': pose, 'angles': [t1, phi],
        'J1': [j1.x, j1.y, j1.z], 'J2': [j2.x, j2.y, j2.z],
        'J3': [j3.x, j3.y, j3.z], 'T': [tip.x, tip.y, tip.z]}
OUT.with_suffix('.json').write_text(json.dumps(data), encoding='utf-8')
bb = Part.makeCompound([o.Shape for o in doc.Objects
                        if o.isDerivedFrom('Part::Feature') and o.Shape.Solids]).BoundBox
print('ARM OK %s T=(%.2f,%.2f) %.2f x %.2f x %.2f'
      % (pose, tip.x, tip.z, bb.XLength, bb.YLength, bb.ZLength))
# FORM B OK
