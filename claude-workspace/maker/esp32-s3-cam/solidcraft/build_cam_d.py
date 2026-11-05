"""Dung vo camera mau D bang SolidCraft (port tu ../freecad/scripts/build_cam_d.py - ban FreeCAD la chuan).
Doc params.json -> sinh cam_d.json -> solidcraft-cli run -> cam_d.sc -> xuat 7 STL huong in vao <out>/stl/.
Thu muc ra: bien moi truong CAMD_OUT (mac dinh: thu muc nay). Truc: X phai, Y ra sau, Z len."""
import json, math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('CAMD_OUT', HERE)
CLI = os.environ.get('SOLIDCRAFT_CLI', r'C:\Program Files\SolidCraft\solidcraft-cli.exe')
P = json.loads(open(os.environ.get('CAMD_PARAMS', os.path.join(HERE, 'params.json')), encoding='utf-8').read())
T, M, S, N, U, D = [P[k] for k in ('than', 'mat_truoc', 'mach', 'truc_nghieng', 'khung_u', 'de_xoay')]
K = P['khe_nhiet']; USB = P['usb']; C = P['coupon']

zd = D['de_cao'] - D['lom_sau'] + D['dia_day']; zp = zd + N['cao_tam_tren_dia']
y0 = -(T['d'] + M['t']) / 2 + M['t']; yp = y0 + .5 + S['cam_cao_tren_pcb']
zl = zp + S['pcb_h'] / 2 - S['ong_kinh_cach_canh_tren']

cmd = []
def A(c, **p): cmd.append({"command": c, "params": p})
def XZ(y): return {"origin": [0, y, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}   # phap tuyen -Y
Y = [0, 1, 0]

def op_kw(op, tgt):
    return {"operation": "new_body", "body_name": tgt} if op == "new" else {"operation": op, "targets": [tgt]}

def box(tgt, op, x, y, z):
    x0, x1 = sorted(x); y0_, y1 = sorted(y); z0, z1 = sorted(z)
    A("solid.box", corner=[x0, y0_, z0], length=x1 - x0, width=y1 - y0_, height=z1 - z0, **op_kw(op, tgt))

def cyl(tgt, op, d, axis, span, at):
    a, b = sorted(span)
    base = {'x': [a, at[0], at[1]], 'y': [at[0], a, at[1]], 'z': [at[0], at[1], a]}[axis]
    A("solid.cylinder", diameter=d, height=b - a, base=base, axis=axis.upper(), **op_kw(op, tgt))

def rr_y(tgt, op, ya, yb, hx, hz, r, cx, cz):
    """Lang tru chu nhat bo goc doc Y, y tu ya den yb (phac thao tai yb, day lui -Y)."""
    A("sketch.create", plane=XZ(yb))
    A("sketch.rectangle.rounded", p0=[cx - hx, cz - hz], p1=[cx + hx, cz + hz], radius=r)
    A("sketch.finish"); A("solid.extrude", distance=yb - ya, **op_kw(op, tgt))

def rr_z(tgt, op, za, zb, hx, hy, r, cx, cy):
    A("sketch.create", plane={"origin": [0, 0, za], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
    A("sketch.rectangle.rounded", p0=[cx - hx, cy - hy], p1=[cx + hx, cy + hy], radius=r)
    A("sketch.finish"); A("solid.extrude", distance=zb - za, **op_kw(op, tgt))

def hexcut(tgt, flat, axis, span, at):
    a, b = sorted(span); r = flat / math.sqrt(3)
    if axis == 'x':
        pl = {"origin": [a, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}
    else:
        pl = {"origin": [0, 0, a], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}
    A("sketch.create", plane=pl)
    A("sketch.polygon.inscribed", center=list(at), radius=r, sides=6, angle=0)
    A("sketch.finish"); A("solid.extrude", distance=b - a, operation="cut", targets=[tgt])

def text_cut(tgt, plane, txt, at, h, depth):
    A("sketch.create", plane=plane)
    A("sketch.text", text=txt, at=at, height=h, align="center", font=M['font'])
    A("sketch.finish"); A("solid.extrude", distance=depth, operation="cut", targets=[tgt])

# ---------------- Body: vo rong, ho mat truoc ----------------
B = "Body"
rr_y(B, "new", y0, y0 + T['d'], T['w'] / 2, T['h'] / 2, T['r_goc'], 0, zp)
rr_y(B, "cut", y0 - .1, y0 + T['d'] - T['thanh'], T['w'] / 2 - T['thanh'], T['h'] / 2 - T['thanh'], T['r_goc'] - T['thanh'], 0, zp)
ov = .5; k = S['khe_moi_ben']; wi = T['w'] / 2 - T['thanh']; hi = T['h'] / 2 - T['thanh']; yr = y0 + T['d'] - T['thanh']
holes = []   # (ham, args) - cat sau khi hop het phan them
def hole(f, *a): holes.append((f, a))
for sx in (-1, 1):
    for sz in (-1, 1):
        x = sx * (T['w'] / 2 - M['vit_cach_canh']); z = zp + sz * (T['h'] / 2 - M['vit_cach_canh'])
        # Loi nhan truck: tru dau vit tiep tuyen voi thanh trong (x = +-wi) -> 'Union: no result'. Ne: hop noi truoc, tru sau.
        box(B, "join", (x, sx * (wi + ov)), (y0, y0 + M['tru_vit_sau']), (z, zp + sz * (hi + ov)))
        cyl(B, "join", M['tru_vit_d'] - .1, 'y', (y0, y0 + M['tru_vit_sau']), (x, z))   # d - 0,1 mm: khong tiep tuyen voi thanh trong
        hole(cyl, B, "cut", M['vit_m25_tu_ren'], 'y', (y0 - .1, y0 + M['tru_vit_sau']), (x, z))
    for za, zb in ((zp + 6, zp + 18), (zp - 18, zp - 6)):
        box(B, "join", (sx * (wi + ov), sx * (S['pcb_w'] / 2 + k)), (yp, yp + S['stack_t']), (za, zb))
    box(B, "join", (sx * (S['pcb_w'] / 2 - 5.5), sx * (S['pcb_w'] / 2 - 2.5)), (yp + S['stack_t'] + k, yr + ov), (zp - S['pcb_h'] / 2, zp + S['pcb_h'] / 2))
    for sz in (-1, 1):
        zin = zp + sz * (S['pcb_h'] / 2 + k); zw = zp + sz * (hi + ov)
        xc = sx * (S['pcb_w'] / 2 - 2.5); yc = yp + S['stack_t'] - 2
        box(B, "join", (xc - 1.5, xc + 1.5), (yc - 1.5, yc + 1.5), (zin, zw))
    xi_ = sx * (wi + ov); xo = sx * (wi - N['tru_than_dai'])
    cyl(B, "join", N['tru_than_d'], 'x', (xi_, xo), (0, zp))
    hole(hexcut, B, N['dai_oc_s'], 'x', (xo - sx * .01, xo + sx * N['dai_oc_sau']), (0, zp))
hole(cyl, B, "cut", N['m3_xuyen'], 'x', (-T['w'] / 2 - .1, T['w'] / 2 + .1), (0, zp))
hole(rr_z, B, "cut", zp - T['h'] / 2 - .1, zp - T['h'] / 2 + T['thanh'] + .1, USB['o_rong_x'] / 2, USB['o_sau_y'] / 2, USB['bo_mep'], 0, yp + S['stack_t'] - USB['o_sau_y'] / 2)
for x in (-21, -17.5, -14, 14, 17.5, 21):
    hole(box, B, "cut", (x - K['rong'] / 2, x + K['rong'] / 2), (yp + 2, yp + 2 + K['dai']), (zp - T['h'] / 2 - .1, zp - T['h'] / 2 + T['thanh'] + .1))
for x in (-10, -6, -2, 2, 6, 10):
    hole(box, B, "cut", (x - K['rong'] / 2, x + K['rong'] / 2), (y0 + 3, y0 + 3 + K['dai']), (zp + T['h'] / 2 - T['thanh'] - .1, zp + T['h'] / 2 + .1))
for f, a in holes: f(*a)

# ---------------- Bezel ----------------
B = "Bezel"; yf = y0 - M['t']
rr_y(B, "new", yf, y0, T['w'] / 2, T['h'] / 2, T['r_goc'], 0, zp)
cyl(B, "cut", M['lo_ong_kinh_d'], 'y', (yf - .1, y0 + .1), (0, zl))
cyl(B, "cut", M['vong_trang_tri_d'], 'y', (yf - .1, yf + M['vong_trang_tri_sau']), (0, zl))
zled = zl - M['den_duoi_ong_kinh']
for sx in (-1, 1): cyl(B, "cut", M['den_d'], 'y', (yf + M['den_da_mong'], y0 + .1), (sx * M['den_cach_nhau'] / 2, zled))
rs = M['vit_m25_xuyen'] / 2
for sx in (-1, 1):
    for sz in (-1, 1):
        x = sx * (T['w'] / 2 - M['vit_cach_canh']); z = zp + sz * (T['h'] / 2 - M['vit_cach_canh'])
        # Loi nhan truck: con trung truc + trung ban kinh voi lo tru -> 'no result'. Ne: con top_radius = r-0,3, cao +0,3
        # (cung goc 45 do), cat con truoc, lo tru sau.
        A("solid.cone", radius=2.5, top_radius=rs - .3, height=2.5 - rs + .3, base=[x, yf, z], axis=Y, operation="cut", targets=[B])
        cyl(B, "cut", M['vit_m25_xuyen'], 'y', (yf - .1, y0 + .1), (x, z))
# chu: tam chu tai (0, zled - chu_duoi_den); 'at' la duong co so nen tru nua chieu cao
text_cut(B, XZ(yf + M['chu_sau']), M['chu'], [0, zled - M['chu_duoi_den'] - M['chu_cao'] / 2], M['chu_cao'], M['chu_sau'] + .1)
for sx in (-1, 1):
    for sz in (-1, 1):
        cyl(B, "join", 2.5, 'y', (y0 - 1, yp - S['khe_moi_ben']), (sx * (S['pcb_w'] / 2 - 1.5), zp + sz * (S['pcb_h'] / 2 - 1.5)))

# ---------------- U_frame ----------------
B = "U_frame"
cyl(B, "new", D['dia_d'], 'z', (zd - D['dia_day'], zd), (0, 0))
xi = T['w'] / 2 + N['khe_tay_than']
for sx in (-1, 1):
    x = sx * xi; xe = x + sx * U['tay_day']
    box(B, "join", (x, xe), (-U['tay_sau_y'] / 2, U['tay_sau_y'] / 2), (zd - 1, zd + U['tay_cao']))
zt = zd + U['tay_cao']
A("solid.fillet", edges=[[sx * (xi + U['tay_day'] / 2), sy * U['tay_sau_y'] / 2, zt] for sx in (-1, 1) for sy in (-1, 1)], radius=3, body=B)
cyl(B, "cut", D['lo_dia_d'], 'z', (zd - D['dia_day'] - .1, zd + .1), (0, 0))
cyl(B, "cut", D['loc_dia_d'], 'z', (zd - D['loc_dia_sau'], zd + .1), (0, 0))
for sx in (-1, 1):
    x = sx * xi; xe = x + sx * U['tay_day']
    cyl(B, "cut", N['m3_xuyen'], 'x', (x - sx * .1, xe + sx * .1), (0, zp))
    cyl(B, "cut", N['loc_dau_vit_d'], 'x', (xe - sx * N['loc_dau_vit_sau'], xe + sx * .1), (0, zp))

# ---------------- Base (tien xoay, bo R2 bang cung that) ----------------
B = "Base"
Rb = D['de_d'] / 2; hb = D['de_cao']; rf = 2.0
A("sketch.create", plane="XZ")   # sketch x = +X, sketch y = -Z
A("sketch.line", points=[[0, 0], [Rb, 0], [Rb, -(hb - rf)]])
A("sketch.arc.center_point", center=[Rb - rf, -(hb - rf)], start=[Rb, -(hb - rf)], end=[Rb - rf, -hb], clockwise=True)
A("sketch.line", points=[[Rb - rf, -hb], [0, -hb], [0, 0]]); A("sketch.finish")
A("solid.revolve", axis="Z", body_name=B, operation="new_body")
floor = D['de_cao'] - D['lom_sau']; ptop = zd - D['loc_dia_sau'] + D['khe_doc']
cyl(B, "cut", D['lom_d'], 'z', (floor, D['de_cao'] + .1), (0, 0))
cyl(B, "join", D['chot_d'], 'z', (floor - 1, ptop), (0, 0))
cyl(B, "cut", M['vit_m25_tu_ren'], 'z', (ptop - 8, ptop + .1), (0, 0))
rl = D['lo_khoa_d'] / 2
for sx in (-1, 1):
    x = sx * D['lo_khoa_cach'] / 2
    # Loi nhan truck: con (countersink) trung truc + trung ban kinh voi lo tru. Ne: top_radius = r-0,3, cao +0,3 (45 do), con truoc, lo tru sau.
    A("solid.cone", radius=D['lo_khoa_dau_d'] / 2, top_radius=rl - .3, height=(D['lo_khoa_dau_d'] - D['lo_khoa_d']) / 2 + .3,
      base=[x, 0, floor], axis=[0, 0, -1], operation="cut", targets=[B])
    cyl(B, "cut", D['lo_khoa_d'], 'z', (-.1, D['de_cao'] + .1), (x, 0))

# ---------------- Pin_cap ----------------
B = "Pin_cap"
cyl(B, "new", D['nap_chot_d'], 'z', (ptop, ptop + D['nap_chot_day']), (0, 0))
cyl(B, "cut", M['vit_m25_xuyen'], 'z', (ptop - .1, ptop + D['nap_chot_day'] + .1), (0, 0))

# ---------------- Ref (hop tham chieu) ----------------
box("Ref_Stack", "new", (-S['pcb_w'] / 2, S['pcb_w'] / 2), (yp, yp + S['stack_t']), (zp - S['pcb_h'] / 2, zp + S['pcb_h'] / 2))
box("Ref_Cam", "new", (-4.25, 4.25), (y0 + .5, y0 + 4.7), (zl - 4.25, zl + 4.25))

# ---------------- Coupon + Coupon_ring (ring dat tai y=40 de khong chong Coupon) ----------------
B = "Coupon"
box(B, "new", (-35, 35), (-17, 17), (0, 4)); xs = (-23, 0, 23)
for x, d in zip(xs, C['m3_xuyen']): cyl(B, "cut", d, 'z', (-.1, 4.1), (x, -8))
for x, d in zip(xs, C['dai_oc_s']):
    hexcut(B, d, 'z', (1.4, 4.1), (x, -8))
    cyl(B, "cut", 3.4, 'z', (-.1, 4.1), (x, -8))
for x, d in zip(xs, C['lo_ong_kinh']): cyl(B, "cut", d, 'z', (-.1, 4.1), (x, 8))
for x, d in zip((-10, 10), C['den_da_mong']): cyl(B, "cut", 3.4, 'z', (d, 4.1), (x, 0))
cyl(B, "join", 8, 'z', (3.9, 10), (30, 0))
fw = S['pcb_w'] + 2 * S['khe_moi_ben']; fh = S['pcb_h'] + 2 * S['khe_moi_ben']
box(B, "join", (34.5, 34.5 + fw + 2.4), (-fh / 2 - 1.2, fh / 2 + 1.2), (0, 5))
box(B, "cut", (35.7, 35.7 + fw), (-fh / 2, fh / 2), (-.1, 5.1))
for lst, yy in ((C['m3_xuyen'], -14.5), (C['lo_ong_kinh'], 14.5)):
    for x, d in zip(xs, lst):
        text_cut(B, {"origin": [0, 0, 3.6], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}, '%g' % d, [x, yy - 1.5], 3, .6)
R = "Coupon_ring"
cyl(R, "new", 15, 'z', (0, 4), (0, 40))
cyl(R, "cut", D['lo_dia_d'], 'z', (-.1, 4.1), (0, 40))

# ---------------- Chay ----------------
def sh(args, what):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        sys.stderr.write('%s LOI (exit %d):\n%s\n%s\n' % (what, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
        sys.exit(1)
    return r.stdout

os.makedirs(OUT, exist_ok=True); stldir = os.path.join(OUT, 'stl'); os.makedirs(stldir, exist_ok=True)
jpath = os.path.join(OUT, 'cam_d.json'); scpath = os.path.join(OUT, 'cam_d.sc')
json.dump({"commands": cmd}, open(jpath, 'w', encoding='utf-8'), indent=1)
sh([CLI, 'run', jpath, '--save', scpath, '--quiet'], 'build cam_d.sc')

# Xuat STL theo huong in: xoay quanh goc truoc, do bbox roi tinh tien zmin = 0.
EXP = [('body', 'Body', [1, 0, 0], -90), ('bezel', 'Bezel', [1, 0, 0], 90), ('u_frame', 'U_frame', None, 0), ('base', 'Base', None, 0),
       ('pin_cap', 'Pin_cap', None, 0), ('coupon', 'Coupon', None, 0), ('coupon_ring', 'Coupon_ring', None, 0)]
def rot_cmds():
    return [{"command": "solid.move", "params": {"bodies": [lb], "axis": ax, "angle": ang}} for _, lb, ax, ang in EXP if ax]
def ev(script):
    jp = os.path.join(OUT, '_rot.json'); json.dump({"commands": script}, open(jp, 'w'))
    t = sh([CLI, 'eval', jp, '--in', scpath], 'eval huong in')
    return {b['name']: b for b in json.loads(t[t.index('{'):])['bodies']}
bb = ev(rot_cmds())
out = rot_cmds()
for fn, lb, ax, ang in EXP:
    zmin = bb[lb]['bbox']['min'][2]
    if abs(zmin) > 1e-9: out.append({"command": "solid.move", "params": {"bodies": [lb], "translate": [0, 0, -zmin]}})
for fn, lb, ax, ang in EXP:
    out.append({"command": "file.export_stl", "params": {"path": os.path.join(stldir, fn + '.stl').replace('\\', '/'), "bodies": [lb], "quality": "fine"}})
xp = os.path.join(OUT, '_export.json'); json.dump({"commands": out}, open(xp, 'w'))
sh([CLI, 'run', xp, '--in', scpath, '--quiet'], 'xuat STL')   # khong --save: cam_d.sc giu nguyen
for f in ('_rot.json', '_export.json'): os.remove(os.path.join(OUT, f))
print('CAMD OK')
