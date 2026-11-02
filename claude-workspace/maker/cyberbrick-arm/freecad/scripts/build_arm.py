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
add('Base_drum', drum)

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
add('Turntable', turn)

# Arm_upper_L / R: hinh san van dong (2 nua tron R r_dau tam J1,J2 + dai noi), day day.
tt = P['tay_tren']
thick = tt['day']
rad = tt['r_dau']
hole = tt['lo_d']


def upper(y):
    ax = (j2 - j1).normalize()
    nn = V(-ax.z, 0, ax.x)
    pts = [j1 + nn * rad, j2 + nn * rad, j2 - nn * rad, j1 - nn * rad]
    s = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(0, thick, 0))
    s.translate(V(0, y, 0))
    s = s.fuse(cyl(rad, thick, (j1.x, y, j1.z), (0, 1, 0)))
    s = s.fuse(cyl(rad, thick, (j2.x, y, j2.z), (0, 1, 0)))
    for p in (j1, j2):
        s = s.cut(cyl(hole / 2, thick + 2.0, (p.x, y - 1.0, p.z), (0, 1, 0)))
    return s.removeSplitter()


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
fore = bake(fore, mat)
fore.translate(j2)
fore = fore.cut(cavity(s2)).cut(cavity(s3))
# lo truc vit xuyen vach truoc cho Worm (truc cang tay)
tv = P['truc_vit']
hole_w = cyl(tv['d'] / 2 + K, F + 2.0 - (tv['s0'] - 1.0),
             (0, 0, 0), (1, 0, 0))  # tam dat sau khi doi he
hole_w = bake(hole_w, mat)
hole_w.translate(j2 + dv * (tv['s0'] - 1.0))
fore = fore.cut(hole_w).removeSplitter()
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
add('Head', head.cut(worm))

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
