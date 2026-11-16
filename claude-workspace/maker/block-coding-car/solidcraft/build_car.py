"""Dung than xe A "Xe hop mat cuoi" (block-coding-car) bang SolidCraft CLI. Mau: maker/esp32-s3-cam/solidcraft/build_cam_d.py.
params.json -> moi chi tiet 1 script lenh (build/<label>.*, cache sha256, chay song song) ->
  car.sc lap rap (component.insert_design), out/asm/<label>.stl (toa do lap rap, gate dung),
  stl/<label>.stl (dung huong in, zmin = 0) + stl/colors.json, build-report.json.
He toa do: san z = 0, xe nhin +X, truc 2 banh qua (0, 0, od/2), _L = +Y.
Bien moi truong: CAR_OUT (thu muc ra, mac dinh thu muc nay), CAR_NO_CACHE=1."""
import hashlib, json, math, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('CAR_OUT', HERE)
CLI = os.environ.get('SOLIDCRAFT_CLI', r'C:\Program Files\SolidCraft\solidcraft-cli.exe')
P = json.load(open(os.path.join(HERE, 'params.json'), encoding='utf-8'))
FONT = 'C:/Windows/Fonts/arialbd.ttf'

# ---------------- thong so lay tu params ----------------
BD, WH, MT, SK = P['body'], P['wheel'], P['motor_28byj48'], P['skid']
BAT, SB, EY, SC = P['battery_4aa'], P['stop_button'], P['eye'], P['screw_m25']
ULN, ESP, BUCK, AMP = P['uln2003_board'], P['esp32_s3'], P['buck_boost'], P['max98357']
SPK, PSW, LED, DK = P['speaker'], P['power_switch'], P['led_eye'], P['deck']
COL = P['colors']
HW = BD['l'] / 2                      # 56
RC = BD['corner_r_plan']              # 26
WALL, ZB, ZT = BD['wall'], BD['z_bottom'], BD['z_roof_top']
ROOF_T, CH = BD['roof_t'], BD['roof_chamfer']
TR2 = P['track_mm'] / 2               # 29
AX_Z = WH['od'] / 2                   # 24 tam truc banh
GC = P['ground_clearance_min']        # 4

# ---------------- hang hinh hoc nho (co giai thich) ----------------
FIT = 0.3          # khe lap ghep chung (co ngot PETG)
FLOOR_T = 3.5      # day san Chassis: z 4 .. 7.5 (dau vit M2.5 chim 1,5 + 1,0 lop doi)
FZ1 = GC + FLOOR_T                    # 7.5 mat tren san
HX_C, R_C = HW - WALL - FIT, RC - WALL - FIT   # chu vi Chassis/Deck = mat bang trong Body tru khe
BULK_T = P['bulkhead_t']
TUBE_W = 1.0       # thanh ong pin (2 duong in, >= wall_min)
TUBE_TOP = 48.0
DECK_Z0, DECK_T = DK['z'], DK['t']
DECK_Z1 = DECK_Z0 + DECK_T
FACE_X0 = 50.0     # mat trong Face = mat loa (spec 'x ~50')
FACE_T = 6.0       # Face day 6 (x 50..56)
FACE_Z0, FACE_Z1 = 7.8, 73.7           # Face dung tren san Chassis +0,3, duoi mep tren o khoet 0,3
NOTCH_HW = BD['face_notch_w'] / 2      # 28
FACE_HW = NOTCH_HW - FIT               # 27.7
BODY_COLS = [(40.8, 48.0), (40.8, -48.0), (-44.85, 44.85), (-44.85, -44.85)]  # cot vit Body, ly do: cach tam cung goc 21 mm
DECK_POSTS = [(40.0, 38.0), (40.0, -38.0), (-34.0, 42.0), (-34.0, -42.0)]
ESP_X0 = 14.0                          # ESP32 dat doc theo Y; lui ra sau de chua cho Eye_holder (TODO: goi y spec 20..46)
ESP_X1 = ESP_X0 + ESP['w']
ESP_Z0 = DECK_Z1 + ESP['under_clear']  # 69.5
MX_PT = 73.3                           # mat tren tam Btn_holder
MX_PLATE_T = SB['mx_plate_t']
MX_Z0 = MX_PT - MX_PLATE_T - SB['mx_below_plate']   # 63.7
MX_Z1 = MX_PT + SB['mx_above_plate']                # 80.1
CAP_FL_T = 2.3                          # go mu day 2,3: khi day len 5 mm van chong len noc (gate 7) ma nhan 4 mm van cach Btn_holder 0,1
CAP_FL_Z0 = ZT - ROOF_T - 0.3 - CAP_FL_T   # 77.4 .. 79.7 (khe 0,3 duoi noc)
EYE_Y = EY['y']
SKID_PEG_D, SKID_PEG_H = 6.0, 0.9      # chot dinh vi chan trượt cam vao san
SKIDS_POS = {'Skid_Main': SK['main'], 'Skid_Tip_L': SK['anti_tip'][0], 'Skid_Tip_R': SK['anti_tip'][1],
             'Skid_Tip_F': SK['anti_tip'][2]}

parts = {}
cmd = []
bodies_of = {}


def part(label, *bodies):
    global cmd
    cmd = parts[label] = []
    bodies_of[label] = list(bodies) or [label]


def A(c, **p):
    cmd.append({"command": c, "params": p})


def opkw(op, tgt):
    return {"operation": "new_body", "body_name": tgt} if op == "new" else {"operation": op, "targets": [tgt]}


def box(tgt, op, x, y, z):
    x0, x1 = sorted(x); y0, y1 = sorted(y); z0, z1 = sorted(z)
    A("solid.box", corner=[x0, y0, z0], length=x1 - x0, width=y1 - y0, height=z1 - z0, **opkw(op, tgt))


def cyl(tgt, op, d, axis, span, at):
    a, b = sorted(span)
    base = {'x': [a, at[0], at[1]], 'y': [at[0], a, at[1]], 'z': [at[0], at[1], a]}[axis]
    A("solid.cylinder", diameter=d, height=b - a, base=base, axis=axis.upper(), **opkw(op, tgt))


def PZ(z): return {"origin": [0, 0, z], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]}          # phap tuyen +Z
def PXZ(y): return {"origin": [0, y, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]}         # phap tuyen -Y, sketch (x, z)
def PYZ(x): return {"origin": [x, 0, 0], "x_dir": [0, 1, 0], "y_dir": [0, 0, 1]}         # phap tuyen +X, sketch (y, z)


def rrz(tgt, op, za, zb, hx, hy, r, cx=0.0, cy=0.0, taper=None):
    A("sketch.create", plane=PZ(za))
    A("sketch.rectangle.rounded", p0=[cx - hx, cy - hy], p1=[cx + hx, cy + hy], radius=r)
    A("sketch.finish")
    kw = {"taper": "%g deg" % taper} if taper is not None else {}
    A("solid.extrude", distance=zb - za, **kw, **opkw(op, tgt))


def poly(tgt, op, plane, pts, dist):
    """Da giac dong (cac diem 2D trong mat phang sketch) -> extrude dist theo phap tuyen."""
    A("sketch.create", plane=plane)
    A("sketch.line", points=[list(p) for p in pts] + [list(pts[0])])
    A("sketch.finish")
    A("solid.extrude", distance=dist, **opkw(op, tgt))


def dd(tgt, op, plane, c, d, f, dist):
    """Lo double-D: vong tron Ø d, 2 mat phang cach nhau f, tam c trong mat phang sketch."""
    r, hf = d / 2, f / 2
    v = math.sqrt(r * r - hf * hf)
    cu, cv = c
    A("sketch.create", plane=plane)
    A("sketch.line", points=[[cu + hf, cv - v], [cu + hf, cv + v]])
    A("sketch.arc.center_point", center=[cu, cv], start=[cu + hf, cv + v], end=[cu - hf, cv + v])
    A("sketch.line", points=[[cu - hf, cv + v], [cu - hf, cv - v]])
    A("sketch.arc.center_point", center=[cu, cv], start=[cu - hf, cv - v], end=[cu + hf, cv - v])
    A("sketch.finish")
    A("solid.extrude", distance=dist, **opkw(op, tgt))


def csk(tgt, base, axis, r_big, r_hole):
    """Con (countersink) 45 do. Loi nhan truck: top_radius = r_hole - 0,3, cao +0,3; cat con truoc, lo tru sau."""
    A("solid.cone", radius=r_big, top_radius=r_hole - .3, height=r_big - r_hole + .3, base=base, axis=axis,
      operation="cut", targets=[tgt])


def text_cut(tgt, plane, txt, at, h, depth):
    A("sketch.create", plane=plane)
    A("sketch.text", text=txt, at=at, height=h, align="center", font=FONT)
    A("sketch.finish")
    A("solid.extrude", distance=depth, operation="cut", targets=[tgt])


def frame(tgt, x, y, z0, z1, wall):
    """Khung 4 thanh bao quanh hinh chu nhat trong (x, y) (cac thanh chong len nhau 0,1 de 1 khoi)."""
    (xa, xb), (ya, yb) = x, y
    box(tgt, "join", (xa - wall, xb + wall), (ya - wall, ya + .1), (z0, z1))
    box(tgt, "join", (xa - wall, xb + wall), (yb - .1, yb + wall), (z0, z1))
    box(tgt, "join", (xa - wall, xa + .1), (ya, yb), (z0, z1))
    box(tgt, "join", (xb - .1, xb + wall), (ya, yb), (z0, z1))


def color(label, key):
    A("appearance.assign", bodies=[label], color=COL[key])


# =============== Chassis (den) ===============
B = "Chassis"; part(B)
rrz(B, "new", GC, FZ1, HX_C, HX_C, R_C)
box(B, "join", (40, HW - .3), (-(FACE_HW - .3), FACE_HW - .3), (GC, FZ1))          # luoi duoi Face (lap kin khe duoi o khoet)
for s in (1, -1):                                                                  # hoc banh (khe >= 2 theo X, 1,5 theo Y)
    y_in = s * (TR2 - WH['width'] / 2 - P['wheel_gap'])      # 23.5 (mat ngoai vach)
    y_out = s * (TR2 + WH['width'] / 2 + P['wheel_gap'])     # 34.5
    box(B, "cut", (-(WH['rim_d'] / 2 + 2), WH['rim_d'] / 2 + 2), (y_in, y_out), (GC - .1, FZ1 + .1))
BX = BAT['x_center']
tx0, tx1 = BX - BAT['t'] / 2 - BAT['fit_gap'], BX + BAT['t'] / 2 + BAT['fit_gap']       # ong pin trong -42.5..-25.5
ty = BAT['w'] / 2 + BAT['fit_gap']                                                      # 29.5
box(B, "join", (tx0 - TUBE_W, tx1 + TUBE_W), (-(ty + TUBE_W), ty + TUBE_W), (FZ1 - .1, TUBE_TOP))
for s in (1, -1):                                                                       # vach motor
    ylo, yhi = sorted((s * (MT['center_gap'] / 2 + MT['body_h']), s * (MT['center_gap'] / 2 + MT['body_h'] + BULK_T)))
    box(B, "join", (-22, 22), (ylo, yhi), (FZ1 - .1, 44))
for s in (1, -1):
    ylo, yhi = sorted((s * (MT['center_gap'] / 2 + MT['body_h']), s * (MT['center_gap'] / 2 + MT['body_h'] + BULK_T)))
    # lo boss giot nuoc (dinh nhon len +Z de in ngang khong support): vong tron Ø(boss_d+1) + tam giac tiep tuyen
    rb = (MT['boss_d'] + 1) / 2
    k = rb / math.sqrt(2)
    A("sketch.create", plane=PXZ(yhi + .1))
    A("sketch.line", points=[[k, AX_Z + k], [0, AX_Z + rb * math.sqrt(2)], [-k, AX_Z + k]])
    A("sketch.arc.center_point", center=[0, AX_Z], start=[-k, AX_Z + k], end=[k, AX_Z + k])
    A("sketch.finish")
    A("solid.extrude", distance=yhi - ylo + .2, operation="cut", targets=[B])
    for sx in (1, -1):                                                                  # 2 lo M2.5 tu ren cua tai motor
        cyl(B, "cut", SC['self_tap'], 'y', (ylo - .1, yhi + .1), (sx * MT['ear_pitch'] / 2, AX_Z + MT['shaft_offset']))
for (px, py) in DECK_POSTS:                                                             # 4 cot do Deck
    cyl(B, "join", 7.0, 'z', (FZ1 - .1, DECK_Z0), (px, py))
for (px, py) in DECK_POSTS:
    cyl(B, "cut", SC['self_tap'], 'z', (DECK_Z0 - 10, DECK_Z0 + .1), (px, py))
box(B, "cut", (tx0, tx1), (-ty, ty), (GC - .1, TUBE_TOP + .1))                           # long ong pin xuyen san
for s in (1, -1):                                                                       # tai nap pin: ngan hoc duoi san
    ya, yb = sorted((s * (ty - .1), s * 35.2))
    box(B, "cut", (BX - 4.2, BX + 4.2), (ya, yb), (GC - .1, 6.0))
cyl(B, "join", 7.0, 'z', (FZ1 - .1, 11.5), (BX, 32.3))                                   # bo vit nap pin
cyl(B, "cut", SC['self_tap'], 'z', (5.9, 11.0), (BX, 32.3))
for (px, py) in BODY_COLS:                                                              # vit M2.5 len cot Body, dau vit duoi san
    cyl(B, "cut", SC['clear'], 'z', (GC - .1, FZ1 + .1), (px, py))
    cyl(B, "cut", SC['head_d'], 'z', (GC - .1, GC + SC['head_h']), (px, py))
for n, pos in SKIDS_POS.items():                                                        # vit chan truot tu TRONG xuong
    px, py = pos[0], pos[1]
    cyl(B, "cut", SKID_PEG_D + .3, 'z', (GC - .1, GC + SKID_PEG_H + .1), (px, py))      # hoc chot dinh vi
    cyl(B, "cut", SC['clear'], 'z', (GC, FZ1 + .1), (px, py))
    cyl(B, "cut", SC['head_d'], 'z', (FZ1 - 1.5, FZ1 + .1), (px, py))                   # bac dau vit (sau 1,5)
sxm, sy = PSW['x'], PSW['y']
box(B, "cut", (sxm - 8, sxm + 8), (sy - 2.4, sy + 2.4), (GC - .1, GC + 1.5))              # ngan duoi cho can gat (gờ che 2 ben)
box(B, "cut", (sxm - PSW['slot_l'] / 2, sxm + PSW['slot_l'] / 2), (sy - 1.6, sy + 1.6), (GC - .1, FZ1 + .1))
frame(B, (sxm - PSW['l'] / 2 - .3, sxm + PSW['l'] / 2 + .3), (sy - PSW['w'] / 2 - .3, sy + PSW['w'] / 2 + .3), FZ1 - .1, FZ1 + 4, 1.2)
for s in (1, -1):                                                                       # 2 de loa (vau giu loa nam o Face)
    ya, yb = sorted((s * 7, s * 11))
    box(B, "join", (SPK['x_face'] - SPK['h'], SPK['x_face']), (ya, yb), (FZ1 - .1, SPK['z_center'] - SPK['d'] / 2 - .2))
color(B, 'chassis')

# =============== Battery_lid (den) ===============
B = "Battery_lid"; part(B)
box(B, "new", (tx0 + .15, tx1 - .15), (-(ty - .15), ty - .15), (GC, GC + 1.0))           # tam day dung trong long ong, pin nam tren
for s in (1, -1):
    ya, yb = sorted((s * (ty - .3), s * 35.0))
    box(B, "join", (BX - 4, BX + 4), (ya, yb), (GC, GC + P['battery_lid_t']))           # tai nam trong ngan hoc duoi san
csk(B, [BX, 32.3, GC], [0, 0, 1], 2.5, SC['clear'] / 2)
cyl(B, "cut", SC['clear'], 'z', (GC - .1, GC + P['battery_lid_t'] + .1), (BX, 32.3))
color(B, 'chassis')

# =============== Chan truot (den) ===============
for n, pos in SKIDS_POS.items():
    part(n)
    z0 = pos[2]
    cyl(n, "new", SK['d'], 'z', (z0, GC), (pos[0], pos[1]))
    A("solid.fillet", edges=[[pos[0] + SK['d'] / 2, pos[1], z0]], radius=1.5, body=n)
    cyl(n, "join", SKID_PEG_D, 'z', (GC - .1, GC + SKID_PEG_H), (pos[0], pos[1]))
    cyl(n, "cut", SC['self_tap'], 'z', (z0 + 0.9, GC + SKID_PEG_H + .1), (pos[0], pos[1]))
    color(n, 'chassis')

# =============== Deck (den) ===============
B = "Deck"; part(B)
rrz(B, "new", DECK_Z0, DECK_Z1, HX_C, HX_C, R_C)
box(B, "cut", (FACE_X0 - .3, 60), (-60, 60), (DECK_Z0 - .1, DECK_Z1 + .1))               # chua khe cho Face (mat trong x 50)
box(B, "cut", (BX - BAT['t'] / 2 - 1.0, BX + BAT['t'] / 2 + 1.0), (-(BAT['w'] / 2 + 1.0), BAT['w'] / 2 + 1.0), (DECK_Z0 - .1, DECK_Z1 + .1))
box(B, "cut", (2, 12), (-14, 14), (DECK_Z0 - .1, DECK_Z1 + .1))                         # lo luon day
for (px, py) in DECK_POSTS:
    cyl(B, "cut", SC['clear'], 'z', (DECK_Z0 - .1, DECK_Z1 + .1), (px, py))
for (px, py) in BODY_COLS:
    cyl(B, "cut", SC['head_d'] + 2.2, 'z', (DECK_Z0 - .1, DECK_Z1 + .1), (px, py))     # tranh cot Body
EH_X = 45.05
for s in (1, -1):
    cyl(B, "cut", SC['clear'], 'z', (DECK_Z0 - .1, DECK_Z1 + .1), (EH_X, s * 10))       # vit Eye_holder tu duoi len
ZT0 = DECK_Z1 - .2                                                                      # chan chong vao Deck 0,2 de 1 khoi
ulx0 = -25.5
for s in (1, -1):                                                                       # tru M2.5 do ULN2003 (cach mep 3, TODO khoang lo theo hang)
    for hx in (ulx0 + 3, ulx0 + ULN['l'] - 3):
        for hy in (18 + 3, 18 + ULN['w'] - 3):
            cyl(B, "join", 6.0, 'z', (ZT0, DECK_Z1 + 4.0), (hx, s * hy))
for s in (1, -1):
    for hx in (ulx0 + 3, ulx0 + ULN['l'] - 3):
        for hy in (18 + 3, 18 + ULN['w'] - 3):
            cyl(B, "cut", SC['self_tap'], 'z', (DECK_Z0 + 1.0, DECK_Z1 + 4.1), (hx, s * hy))
ey = ESP['l'] / 2
box(B, "join", (ESP_X0 - 2.4, ESP_X0 - .4), (-ey - .03, ey + .03), (ZT0, ESP_Z0 + ESP['pcb_t']))     # 2 go canh dai (cach PCB 0,4)
box(B, "join", (ESP_X1 + .4, ESP_X1 + 2.4), (-ey - .03, ey + .03), (ZT0, ESP_Z0 + ESP['pcb_t']))
for s in (1, -1):                                                                       # moi do duoi PCB (chi o 2 dau, de Dupont o giua)
    ya, yb = sorted((s * 22, s * 30))
    box(B, "join", (ESP_X0 - .5, ESP_X0 + .8), (ya, yb), (ESP_Z0 - 1.0, ESP_Z0))
    box(B, "join", (ESP_X1 - .8, ESP_X1 + .5), (ya, yb), (ESP_Z0 - 1.0, ESP_Z0))
for s in (1, -1):                                                                       # 2 lay o 2 dau PCB
    ya, yb = sorted((s * (ey + .4), s * (ey + 2.0)))
    box(B, "join", (22, 32), (ya, yb), (ZT0, ESP_Z0 + ESP['pcb_t'] + 1.3))
    ya, yb = sorted((s * (ey - 1.0), s * (ey + 2.0)))
    box(B, "join", (22, 32), (ya, yb), (ESP_Z0 + ESP['pcb_t'] + .1, ESP_Z0 + ESP['pcb_t'] + 1.3))
AMP_BOX = ((18.5, 18.5 + AMP['l']), (-3 - AMP['w'], -3))
BUCK_BOX = ((19.0, 19.0 + BUCK['l']), (4.0, 4.0 + BUCK['w']))
for (bx, by) in (AMP_BOX, BUCK_BOX):                                                    # khung giu mach (khe 0,4)
    frame(B, (bx[0] - .4, bx[1] + .4), (by[0] - .4, by[1] + .4), ZT0, DECK_Z1 + 3.0, 1.2)
color(B, 'chassis')

# =============== Body (mau than) ===============
B = "Body"; part(B)
zc = ZT - CH                                                  # 78.5: bat dau vat mep noc
rrz(B, "new", ZB, zc, HW, HW, RC)
rrz(B, "join", zc, ZT, HW, HW, RC, taper=-45)                 # vat 4 x 45 do
zin = ZT - ROOF_T                                             # 80 mat trong noc
d_in = WALL * math.sqrt(2)
z_knee = zc + WALL - d_in                                     # 77.59: noi thanh trong va mat vat trong
rrz(B, "cut", ZB - .1, z_knee, HW - WALL, HW - WALL, RC - WALL)
rrz(B, "cut", z_knee, zin, HW - WALL, HW - WALL, RC - WALL, taper=-45)
box(B, "cut", (40, HW + 4), (-NOTCH_HW, NOTCH_HW), (ZB - .1, BD['face_notch_top_z']))   # o khoet cho Face
for (px, py) in BODY_COLS:                                                              # 4 cot vit
    cyl(B, "join", SC['boss_d'], 'z', (FZ1, zin + .25), (px, py))   # dinh 80,25: duoi mat vat ngoai (80,5 tai mep cot) -> khong tiep tuyen
for (px, py) in BODY_COLS:
    cyl(B, "cut", SC['self_tap'], 'z', (FZ1 - .1, FZ1 + 10), (px, py))
BP = (-34.0, 6.0)                                                                       # 2 tru giu Btn_holder (cach noi 20 mm de ne go mu)
for px in BP:
    cyl(B, "join", 6.5, 'z', (MX_PT, zin + .5), (px, 0))
for px in BP:
    cyl(B, "cut", SC['self_tap'], 'z', (MX_PT - .1, MX_PT + 6), (px, 0))
cyl(B, "cut", SB['roof_hole_d'], 'z', (zin - .1, ZT + .1), (SB['x'], SB['y']))
color(B, 'body')

# =============== Face (kem) ===============
B = "Face"; part(B)
box(B, "new", (FACE_X0, HW), (-FACE_HW, FACE_HW), (FACE_Z0, FACE_Z1))
for s in (1, -1):                                                                       # 2 mat
    cyl(B, "cut", EY['hole_d'], 'x', (FACE_X0 - .1, HW + .1), (s * EYE_Y, EY['z']))
    cyl(B, "cut", EY['diffuser_d'] + .6, 'x', (FACE_X0 - .1, FACE_X0 + 1.3), (s * EYE_Y, EY['z']))   # hoc Diffuser sau 1,3
for k in range(7):                                                                      # luoi loa: 7 khe rong 2, cach 4
    yc = (k - 3) * 4
    box(B, "cut", (FACE_X0 - .1, HW + .1), (yc - 1, yc + 1), (14, 34))
cz, ro, ri = 52.0, 14.5, 13.5                                                           # mieng cuoi: rang cung rong 1,0 sau 1,0
a1, a2 = math.radians(-130), math.radians(-50)
po = lambda r, a: [r * math.cos(a), cz + r * math.sin(a)]
A("sketch.create", plane=PYZ(HW - EY['smile_groove']))
A("sketch.arc.center_point", center=[0, cz], start=po(ro, a1), end=po(ro, a2))
A("sketch.line", points=[po(ro, a2), po(ri, a2)])
A("sketch.arc.center_point", center=[0, cz], start=po(ri, a2), end=po(ri, a1), clockwise=True)
A("sketch.line", points=[po(ri, a1), po(ro, a1)])
A("sketch.finish")
A("solid.extrude", distance=EY['smile_groove'] + .1, operation="cut", targets=[B])
for s in (1, -1):                                                                       # 2 vau giu loa (kep 2 ben, khe 0,3)
    ya, yb = sorted((s * (SPK['d'] / 2 + .3), s * (SPK['d'] / 2 + 2.3)))
    box(B, "join", (SPK['x_face'] - SPK['h'] + 1.5, FACE_X0 + .1), (ya, yb), (SPK['z_center'] - 3, SPK['z_center'] + 3))
FL = BD['face_flange'] - 1.0                                                            # 2,0: gờ tru ra sau thanh Body (vat 45 do de in khong support)
# go tren: tiet dien (x, z) lay tren mep tren Face, keo doc Y
poly(B, "join", PXZ(FACE_HW), [(FACE_X0, FACE_Z1 - .2), (HW - 2.4, FACE_Z1 - .2), (HW - 2.4, FACE_Z1), (HW - 2.4 - FL, FACE_Z1 + FL), (FACE_X0, FACE_Z1 + FL)], 2 * FACE_HW)
for s in (1, -1):                                                                       # go 2 ben (tiet dien (x, y), keo doc Z)
    e = s * FACE_HW
    pts = [(FACE_X0, e - s * .2), (HW - 2.4, e - s * .2), (HW - 2.4, e), (HW - 2.4 - FL, e + s * FL), (FACE_X0, e + s * FL)]
    poly(B, "join", PZ(FACE_Z0), pts, FACE_Z1 - FACE_Z0)
color(B, 'face')

# =============== Diffuser_L/R (trang) ===============
for n, s in (("Diffuser_L", 1), ("Diffuser_R", -1)):
    part(n)
    cyl(n, "new", EY['diffuser_d'], 'x', (FACE_X0 + 1.3 - EY['diffuser_t'], FACE_X0 + 1.3), (s * EYE_Y, EY['z']))
    color(n, 'diffuser')

# =============== Eye_holder (den) ===============
B = "Eye_holder"; part(B)
LED_X0 = FACE_X0 + 1.3 - EY['diffuser_t'] - LED['led_h'] - LED['pcb_t']      # 47.1 mat sau mach LED
box(B, "new", (EH_X - 2.05, LED_X0), (-(EYE_Y + 8), EYE_Y + 8), (DECK_Z1, EY['z'] + LED['pcb_d'] / 2 + 2.5))
for s in (1, -1):
    cyl(B, "cut", SC['self_tap'], 'z', (DECK_Z1 - .1, DECK_Z1 + 6), (EH_X, s * 10))
color(B, 'chassis')

# =============== Stop_cap (do) ===============
B = "Stop_cap"; part(B)
cx, cy = SB['x'], SB['y']
ztop = ZT + SB['cap_h_above_roof']
cyl(B, "new", SB['cap_flange_d'], 'z', (CAP_FL_Z0, CAP_FL_Z0 + CAP_FL_T), (cx, cy))
cyl(B, "join", SB['cap_d'], 'z', (CAP_FL_Z0 + CAP_FL_T - .1, ztop), (cx, cy))
A("solid.fillet", edges=[[cx + SB['cap_d'] / 2, cy, ztop]], radius=1.0, body=B)
arm = 1.35  # TODO do be rong canh chu thap that cua stem MX (cong dong 4,19 x ~1,3)
box(B, "cut", (cx - SB['stem_cross'] / 2, cx + SB['stem_cross'] / 2), (cy - arm / 2, cy + arm / 2), (CAP_FL_Z0 - .1, CAP_FL_Z0 + 4.0))
box(B, "cut", (cx - arm / 2, cx + arm / 2), (cy - SB['stem_cross'] / 2, cy + SB['stem_cross'] / 2), (CAP_FL_Z0 - .1, CAP_FL_Z0 + 4.0))
color(B, 'stop')

# =============== Btn_holder (den) ===============
B = "Btn_holder"; part(B)
box(B, "new", (SB['x'] - 24.5, SB['x'] + 24.5), (-10, 10), (MX_PT - MX_PLATE_T, MX_PT))
for px in BP:
    cyl(B, "join", 9.0, 'z', (MX_PT - MX_PLATE_T - 2.5, MX_PT - MX_PLATE_T + .1), (px, 0))
box(B, "cut", (SB['x'] - SB['mx_socket'] / 2, SB['x'] + SB['mx_socket'] / 2), (-SB['mx_socket'] / 2, SB['mx_socket'] / 2), (MX_PT - MX_PLATE_T - 3, MX_PT + .1))
for px in BP:
    cyl(B, "cut", SC['clear'], 'z', (MX_PT - MX_PLATE_T - 3, MX_PT + .1), (px, 0))
    cyl(B, "cut", SC['head_d'], 'z', (MX_PT - MX_PLATE_T - 3, MX_PT - MX_PLATE_T - .5), (px, 0))
color(B, 'chassis')

# =============== Banh (den) ===============
for n, s in (("Wheel_L", 1), ("Wheel_R", -1)):
    part(n)
    ya, yb = sorted((s * (TR2 - WH['width'] / 2), s * (TR2 + WH['width'] / 2)))
    gy = s * TR2
    hg = WH['oring_groove_w'] / 2
    core = WH['rim_d'] - 2 * WH['oring_groove_d']
    cyl(n, "new", core, 'y', (ya, yb), (0, AX_Z))                                         # loi (day ranh O-ring)
    cyl(n, "join", WH['rim_d'], 'y', (ya, gy - hg), (0, AX_Z))                            # 2 vanh 2 ben ranh
    cyl(n, "join", WH['rim_d'], 'y', (gy + hg, yb), (0, AX_Z))
    dd(n, "cut", PXZ(yb + .1), (0, AX_Z), P['dshaft_use'][0], P['dshaft_use'][1], yb - ya + .2)
    color(n, 'wheel')

# =============== Coupon (den, ngoai xe) ===============
B = "Coupon"; part(B)
CX0 = 170.0
box(B, "new", (CX0, CX0 + 92), (-30, 22), (0, 4))
for i, (d, f) in enumerate(P['dshaft_press_try']):
    x = CX0 + 8 + 12 * i
    dd(B, "cut", PZ(-.1), (x, 12), d, f, 4.2)
    text_cut(B, PZ(3.4), '%.1f' % d, [x, 3.8], 2.5, .8)
for i, d in enumerate((2.2, 2.3, 2.4)):
    x = CX0 + 8 + 12 * i
    cyl(B, "cut", d, 'z', (-.1, 4.1), (x, -12))
    text_cut(B, PZ(3.4), '%.1f' % d, [x, -19.5], 2.5, .8)
mxs = SB['mx_socket']
box(B, "cut", (CX0 + 48 - mxs / 2, CX0 + 48 + mxs / 2), (12 - mxs / 2, 12 + mxs / 2), (-.1, 4.1))
text_cut(B, PZ(3.4), '%.1f' % mxs, [CX0 + 48, 2.5], 2.5, .8)
cyl(B, "cut", SB['roof_hole_d'], 'z', (-.1, 4.1), (CX0 + 56, -12))
text_cut(B, PZ(3.4), '%.0f' % SB['roof_hole_d'], [CX0 + 56, -28.0], 2.5, .8)
cyl(B, "join", SB['cap_d'], 'z', (3.9, 8.0), (CX0 + 76, 5))
color(B, 'chassis')

# =============== Ref_* (hop/tru tham chieu, chi trong out/asm) ===============
REFS = ["Ref_Motor_L", "Ref_Motor_R", "Ref_ULN_L", "Ref_ULN_R", "Ref_ESP32", "Ref_Buck", "Ref_Amp", "Ref_Speaker",
        "Ref_Battery", "Ref_Switch", "Ref_MX", "Ref_LED_L", "Ref_LED_R"]
part("Ref", *REFS)
mz = AX_Z + MT['shaft_offset']                                  # tam than motor z 32
for n, s in (("Ref_Motor_L", 1), ("Ref_Motor_R", -1)):
    fl = MT['center_gap'] / 2 + MT['body_h']                    # mat bich |y| = 21
    cyl(n, "new", MT['body_d'], 'y', sorted((s * MT['center_gap'] / 2, s * fl)), (0, mz))
    box(n, "join", (-(MT['ear_pitch'] / 2 + MT['ear_w'] / 2), MT['ear_pitch'] / 2 + MT['ear_w'] / 2),
        sorted((s * (fl - MT['ear_t']), s * fl)), (mz - MT['ear_w'] / 2, mz + MT['ear_w'] / 2))
    for sx in (1, -1):
        cyl(n, "cut", MT['ear_hole'], 'y', sorted((s * (fl - 1.1), s * (fl + .1))), (sx * MT['ear_pitch'] / 2, mz))
    cyl(n, "join", MT['boss_d'], 'y', sorted((s * (fl - .5), s * (fl + MT['boss_h']))), (0, AX_Z))
    cyl(n, "join", MT['shaft_d'], 'y', sorted((s * (fl + MT['boss_h'] - .1), s * (fl + MT['boss_h'] + MT['shaft_len']))), (0, AX_Z))
    box(n, "join", (-MT['body_d'] / 2 - MT['cap_depth'], -MT['body_d'] / 2 + 1.0),
        sorted((s * (fl - 1.5 - MT['cap_w']), s * (fl - 1.5))), (mz - MT['cap_h'] / 2, mz + MT['cap_h'] / 2))
for n, s in (("Ref_ULN_L", 1), ("Ref_ULN_R", -1)):
    box(n, "new", (ulx0, ulx0 + ULN['l']), sorted((s * 18, s * (18 + ULN['w']))), (DECK_Z1 + 4.0, DECK_Z1 + 4.0 + ULN['h']))
box("Ref_ESP32", "new", (ESP_X0, ESP_X1), (-ey, ey), (ESP_Z0, ESP_Z0 + ESP['pcb_t']))
box("Ref_ESP32", "join", (22, 32), (-20, 20), (ESP_Z0 + ESP['pcb_t'] - .1, ESP_Z0 + ESP['pcb_t'] + ESP['top_h']))
box("Ref_Buck", "new", BUCK_BOX[0], BUCK_BOX[1], (DECK_Z1, DECK_Z1 + BUCK['h']))
box("Ref_Amp", "new", AMP_BOX[0], AMP_BOX[1], (DECK_Z1, DECK_Z1 + AMP['h']))
cyl("Ref_Speaker", "new", SPK['d'], 'x', (SPK['x_face'] - SPK['h'], SPK['x_face']), (0, SPK['z_center']))
box("Ref_Battery", "new", (BX - BAT['t'] / 2, BX + BAT['t'] / 2), (-BAT['w'] / 2, BAT['w'] / 2), (BAT['z_bottom'], BAT['z_bottom'] + BAT['h']))
box("Ref_Switch", "new", (sxm - PSW['l'] / 2, sxm + PSW['l'] / 2), (sy - PSW['w'] / 2, sy + PSW['w'] / 2), (FZ1, FZ1 + PSW['h']))
hs = SB['mx_socket'] / 2 - .05                                   # phan qua tam 13,9 (lo tam 14,0)
box("Ref_MX", "new", (SB['x'] - hs, SB['x'] + hs), (-hs, hs), (MX_Z0, MX_PT + .1))
box("Ref_MX", "join", (SB['x'] - 7.8, SB['x'] + 7.8), (-7.8, 7.8), (MX_PT, MX_Z1))
for n, s in (("Ref_LED_L", 1), ("Ref_LED_R", -1)):
    cyl(n, "new", LED['pcb_d'], 'x', (LED_X0, LED_X0 + LED['pcb_t']), (s * EYE_Y, EY['z']))
    box(n, "join", (LED_X0 + LED['pcb_t'] - .1, LED_X0 + LED['pcb_t'] + LED['led_h']), (s * EYE_Y - 2.5, s * EYE_Y + 2.5),
        (EY['z'] - 2.5, EY['z'] + 2.5))

# =============== Tham so chinh (Tuan mo .sc do) ===============
A_ = parts["Wheel_L"]
A_.insert(0, {"command": "parameters.add", "params": {"name": "Track", "expression": "%g mm" % P['track_mm'], "comment": "Vet banh"}})
A_.insert(1, {"command": "parameters.add", "params": {"name": "WheelRim", "expression": "%g mm" % WH['rim_d'], "comment": "O vanh in (+ O-ring = 48)"}})
A_ = parts["Body"]
A_.insert(0, {"command": "parameters.add", "params": {"name": "BodySize", "expression": "%g mm" % BD['l'], "comment": "Mat bang than 112 x 112"}})
A_.insert(1, {"command": "parameters.add", "params": {"name": "BodyWall", "expression": "%g mm" % WALL, "comment": "Day thanh"}})
A_ = parts["Deck"]
A_.insert(0, {"command": "parameters.add", "params": {"name": "DeckZ", "expression": "%g mm" % DECK_Z0, "comment": "Cao mat duoi Deck"}})

# ---------------- chay ----------------
PRINT = ["Chassis", "Battery_lid", "Skid_Main", "Skid_Tip_L", "Skid_Tip_R", "Skid_Tip_F", "Deck", "Body", "Face", "Diffuser_L",
         "Diffuser_R", "Eye_holder", "Stop_cap", "Btn_holder", "Wheel_L", "Wheel_R", "Coupon"]
# huong in: (truc, goc) -> xoay roi tinh tien zmin = 0 (None = giu nguyen)
ORIENT = {"Body": ('x', 180), "Face": ('y', 90), "Btn_holder": ('x', 180), "Wheel_L": ('x', 90), "Wheel_R": ('x', -90)}
COLOR_KEY = {"Chassis": "chassis", "Battery_lid": "chassis", "Deck": "chassis", "Body": "body", "Face": "face",
             "Diffuser_L": "diffuser", "Diffuser_R": "diffuser", "Eye_holder": "chassis", "Stop_cap": "stop",
             "Btn_holder": "chassis", "Wheel_L": "wheel", "Wheel_R": "wheel", "Coupon": "chassis",
             "Skid_Main": "chassis", "Skid_Tip_L": "chassis", "Skid_Tip_R": "chassis", "Skid_Tip_F": "chassis"}
ORDER = PRINT + ["Ref"]

BUILD, ASM, STLD = (os.path.join(OUT, d) for d in ('build', os.path.join('out', 'asm'), 'stl'))
for d in (BUILD, ASM, STLD):
    os.makedirs(d, exist_ok=True)
NO_CACHE = os.environ.get('CAR_NO_CACHE') == '1'
T0 = time.time()


def sh(args, what):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        sys.stderr.write('%s LOI (exit %d):\n%s\n%s\n' % (what, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
        sys.exit(1)
    return r.stdout


CLIV = sh([CLI, '--version'], 'version').strip()


def P_(label, ext): return os.path.join(BUILD, label + ext)


def key_of(label):
    blob = json.dumps({"cli": CLIV, "orient": ORIENT.get(label), "commands": parts[label], "bodies": bodies_of[label]}, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()


def asm_path(body): return os.path.join(ASM, body.lower() + '.stl')


def rotate_stl(src, dst, axis, angle):
    b = open(src, 'rb').read(); n = int(np.frombuffer(b, '<u4', 1, 80)[0])
    rec = np.frombuffer(b, np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), n, 84)
    a = math.radians(angle); c, s_ = round(math.cos(a), 12), round(math.sin(a), 12)
    R = (np.array([[1, 0, 0], [0, c, -s_], [0, s_, c]]) if axis == 'x' else np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])).astype(np.float64)
    v = rec['v'].astype(np.float64) @ R.T; nn = rec['n'].astype(np.float64) @ R.T
    v[..., 2] -= v[..., 2].min()
    out = rec.copy(); out['v'] = v.astype('<f4'); out['n'] = nn.astype('<f4')
    open(dst, 'wb').write(b[:80] + b[80:84] + out.tobytes())


def shift_stl(src, dst):
    rotate_stl(src, dst, 'x', 0)


def build_one(label):
    cmds = list(parts[label])
    for bn in bodies_of[label]:
        cmds.append({"command": "file.export_stl", "params": {"path": asm_path(bn).replace(os.sep, '/'), "bodies": [bn], "quality": "fine"}})
    cmds.append({"command": "inspect.measure", "params": {}})
    jp = P_(label, '.json'); json.dump({"commands": cmds}, open(jp, 'w'))
    sh([CLI, 'run', jp, '--save', P_(label, '.sc'), '--results', '--json-out', P_(label, '.result.json'), '--quiet'], 'build ' + label)
    open(P_(label, '.key'), 'w').write(key_of(label))


def cached(label):
    if NO_CACHE:
        return False
    need = [P_(label, '.sc'), P_(label, '.result.json'), P_(label, '.key')] + [asm_path(b) for b in bodies_of[label]]
    return all(os.path.exists(f) for f in need) and open(P_(label, '.key')).read() == key_of(label)


todo = [l for l in ORDER if not cached(l)]; done = [l for l in ORDER if l not in todo]
with ThreadPoolExecutor(max(2, (os.cpu_count() or 4) // 2)) as ex:
    list(ex.map(build_one, todo))

# STL huong in + colors.json (ghi lai khi chi tiet doi hoac chua co)
colors = {}
for l in PRINT:
    dst = os.path.join(STLD, l.lower() + '.stl')
    ax, ang = ORIENT.get(l, ('x', 0))
    if l in todo or not os.path.exists(dst):
        rotate_stl(asm_path(l), dst, ax, ang)
    colors[l.lower() + '.stl'] = COL[COLOR_KEY[l]]
json.dump(colors, open(os.path.join(STLD, 'colors.json'), 'w'), indent=1)

# Lap rap car.sc: ghep cac .sc chi tiet
scpath = os.path.join(OUT, 'car.sc'); akey = os.path.join(BUILD, 'assembly.key')
akv = hashlib.sha256(''.join(key_of(l) for l in ORDER).encode()).hexdigest()
if todo or NO_CACHE or not os.path.exists(scpath) or not os.path.exists(akey) or open(akey).read() != akv:
    asm = [{"command": "component.insert_design", "params": {"path": P_(l, '.sc').replace(os.sep, '/'), "name": l}} for l in ORDER]
    jp = os.path.join(BUILD, 'assembly.json'); json.dump({"commands": asm}, open(jp, 'w'))
    sh([CLI, 'run', jp, '--save', scpath, '--quiet'], 'lap rap car.sc')
    open(akey, 'w').write(akv)

bodies = {}
for l in ORDER:
    for b in json.load(open(P_(l, '.result.json'), encoding='utf-8'))[-1]['bodies']:
        bodies[b['name']] = {"volume_mm3": b.get('volume_mm3'), "bbox": b['bbox'], "closed": b.get('closed'),
                             "shells": b.get('kernel', {}).get('shells')}
sec = round(time.time() - T0, 1)
json.dump({"bodies": bodies, "built": todo, "cached": done, "seconds": sec},
          open(os.path.join(OUT, 'build-report.json'), 'w', encoding='utf-8'), indent=1)
print('CAR OK built=%d cached=%d %.1f s' % (len(todo), len(done), sec))
