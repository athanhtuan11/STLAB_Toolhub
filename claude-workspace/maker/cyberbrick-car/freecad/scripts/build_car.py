# Dung model xe cyberbrick-car TU THAM SO (chay lai = model moi, khong sua tay trong FreeCAD).
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" freecad/scripts/build_car.py
# Ra: freecad/cyberbrick_car.FCStd (ghi de file SINH RA tu script nay; ban truoc -> freecad/backup/) + freecad/colors.json.
# He truc: X tien, Y trai, Z len; goc = tam truc sau tren mat dat. Don vi mm. Kich thuoc linh kien do tu STEP chinh hang
# (community/cyberbrick-official/models, xem README "Nguon so do"); cho nao chua co so do that -> TODO trong README.
import json, math, os, shutil, sys, time
import FreeCAD as App, Part
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "tools", "robotics-cad", "scripts"))
import safe_edit as se  # noqa: E402  boolean co kiem (tools/robotics-cad/scripts/safe_edit.py)

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(PROJ, "freecad", "cyberbrick_car.FCStd")
LIB = os.path.join(PROJ, "..", "..", "community", "cyberbrick-official", "models")

P = dict(            # ---- tham so chinh (mm) ----
    wheelbase=140.0, track=72.0, wheel_r=16.8, tire_w=13.7,
    plate_z0=4.0, plate_t=2.4,          # tam san: gam 4 mm; 2.4 mm + cua so giam tai (tiet kiem nhua, Tuan 2026-10-23)
    clr=0.2,                            # khe lap ghep (Tuan chot 0.2)
    shell_t=1.3,                        # vo than xe = dung 3 duong Bambu (0.42 + 2 x 0.45); 1.2 -> 2 duong + lap khe vun
                                        # -> slicer bao floating (2026-10-23). 1.6 -> 1.3 tiet kiem nhua
    kingpin_y=20.0, kingpin_dx=7.0,     # chot lai truoc tam banh 7 mm (caster duong: tu ve thang)
    arm_len=12.0,                       # lai Ackermann: tay lai huong ve tam truc sau
    servo_dy=-3.5,                      # lech servo sang phai de gia servo nam trong san
    servo_type="pg001",                 # servo lai: "pg001" (CyberBrick 9g 180) | "mg90s" (Tower Pro, mua ngoai) - gia dung chung
    servo_horn_r=8.2,
    rear_arch_r=18.3, front_arch_r=18.8, front_arch_dx=5.0,   # dinh hoc banh duoi mat chan bun >= 3 mm
    stub_d=5.0,                         # truc banh truoc IN LIEN VANH (in dung), qua lo giot nuoc o khop lai
    rear_bore_d=5.4, rear_bore_af=3.7,  # truc ra double-D (do STEP: D5.3, dep 3.6 = chuan TT); TODO do bo 2 truc
    post_top=30.0, magnet_d=4.4, magnet_h=2.1,
    win_d=0.4,                          # kinh khac chim (Tuan 2026-10-26): vo 1,3 -> con 0,9 = 2 duong Bambu
)
P["servo_type"] = os.environ.get("CAR_SERVO", P["servo_type"])               # thu nhanh: CAR_SERVO=mg90s
Z_AX = P["wheel_r"]
PLATE_TOP = P["plate_z0"] + P["plate_t"]
YW = P["track"] / 2                      # tam banh theo Y
FX = P["wheelbase"]                      # truc truoc

doc = App.newDocument("cyberbrick_car")
COLORS = {}


def add(label, shape, color=None):
    o = doc.addObject("Part::Feature", label)
    o.Label = label
    o.Shape = shape
    if color:
        COLORS[label] = color
    return o


def step(rel):
    return Part.read(os.path.join(LIB, rel))


def placed(shape, rot=None, move=V()):
    s = shape.copy()
    if rot is not None:
        s.Placement = App.Placement(V(), rot).multiply(s.Placement)
    s.translate(move)
    return s


def cyl(r, h, base, axis):
    return Part.makeCylinder(r, h, base, axis)


def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def pos(sol):
    """Khoi dun tu Part.Face(da giac) co the AM the tich (thu tu dinh nguoc huong dun) -> boolean sau do hong am tham."""
    return sol if sol.Volume >= 0 else sol.reversed()


def fuse(*ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r.removeSplitter()


def screw(label, tip, axis, d, L):
    """Vit dau tru (proxy): than d x L tu 'tip' nguoc huong axis, dau 2d x 0.6d."""
    a = V(axis).normalize()
    head_base = tip - a * L
    s = cyl(d / 2, L, head_base, a).fuse(cyl(d, 0.6 * d, head_base - a * 0.6 * d, a))
    return add(label, s, (0.25, 0.25, 0.28))


# ================= LINH KIEN MUA (STEP chinh hang) =================
tire = step("la027-phi33-7x13-85mm-rubber-tire/phi33-7x13-85mm-rubber-tire.step")
tire.translate(-tire.BoundBox.Center)                                      # tam lop -> goc, truc X
tire = placed(tire, App.Rotation(V(0, 0, 1), 90))                            # truc X -> Y
for nm, x, y in (("RL", 0, YW), ("RR", 0, -YW), ("FL", FX, YW), ("FR", FX, -YW)):
    add(f"CB_Tire_{nm}", placed(tire, move=V(x, y, Z_AX)), (0.12, 0.12, 0.12))

# Hop so: dung STEP hop so 1 truc 030 (cung bo banh rang, cung vo) lam proxy cho bo 2 truc LA013 (1:21).
# local: truc ra double-D D5.3 o (x 0, z 11.15) theo Y, loi 8.1 mm khoi mat vo (y 15.2..23.3); dong co theo -Z.
# Xoay: local x->Z, y->Y, z->-X (dong co huong ve phia truoc); dat truc ra trung truc banh sau (x 0).
gb = step("la024-030-micro-dc-motor-with-sh1-0/030-micro-dc-motor-with-sh1-0-reducer.step")
GB_ROT = App.Rotation(V(0, 1, 0), -90)
GB_MOVE = V(11.15, -6.2, Z_AX)                                               # vo hop so doi xung quanh Y = 0
gearbox = placed(gb, GB_ROT, GB_MOVE)
add("CB_Gearbox_030_dual_axis", gearbox, (0.95, 0.80, 0.10))
# truc ra ben trai (bo 2 truc LA013): STEP chinh hang chi co bo 1 truc (truc phai, loi 8.1 mm). Do tu anh huong dan lap
# chinh hang (Assembly_Guide_of_Dual_Axis_030..., hinh chieu canh, ti le theo vo 18 mm): loi ~9 mm moi ben, D ~5.3-5.6.
add("CB_Gearbox_shaft_left", cyl(2.65, 9.0, V(0, -9.0, Z_AX), V(0, -1, 0)), (0.9, 0.9, 0.9))
# hop bao VO hop so (khong tinh dong co / truc): local x +-11, y -2.8..15.2, z -32.2..22.15
H = dict(x0=11.15 - 22.15, x1=11.15 + 32.2, y=9.0, z0=Z_AX - 11.0, z1=Z_AX + 11.0)

# Lai: chot lai (KPX, +-ky); tay lai huong ve tam truc sau (Ackermann); dau tay = diem noi thanh giang
KPX = FX + P["kingpin_dx"]
ANG = math.atan2(P["kingpin_y"], KPX)
TR_EX = KPX - P["arm_len"] * math.cos(ANG)
TR_EY = P["kingpin_y"] - P["arm_len"] * math.sin(ANG)
SDY = P["servo_dy"]

# Servo lai PG001: truc ra huong +X (ra phia truoc), nam ngang. local x->-Y, y->Z, z->-X.
# Gia servo dung chung PG001 + MG90S (so do tu STEP: PG001 chinh hang; MG90S GrabCAD, community/grabcad/towerpro-mg90s):
#   than 22.7 x 11.9 / 12.2; truc cach dau than 6.0 / 5.9; lo tai so voi truc -19.15,+8.47 / -19.4,+8.5;
#   mat truoc tai -> dinh truc 12.22 / 11.75 mm. Mat tua gia theo MG90S; PG001 vit keo ap vao gia (lech 0.47).
HORN_X1 = TR_EX - 2.4                                                       # mat truoc horn (danh nghia)
HX = HORN_X1 + 0.47                                                         # dinh truc khi tai ap gia
SHAFT_Z = 13.5
TAB_FRONT = HX - 11.75                                                      # mat truoc tai = mat sau gia
if P["servo_type"] == "mg90s":
    sv = Part.read(os.path.join(PROJ, "..", "..", "community", "grabcad", "towerpro-mg90s", "M90S_ali.step"))
    sv_body = sv.Solids[1].fuse(sv.Solids[0])                               # than + truc ra (bo day/chan cam)
    # local: truc +Z (dinh z 14.45) o (0,0); than ve -x 16.8 / +x 5.9; rong y +-6.1 -> x->-Y, y->-Z, z->+X
    SERVO_ROT = App.Rotation(App.Matrix(0, 0, 1, 0, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 1))
    servo_move = V(HX - 14.45, SDY, SHAFT_Z)
    SERVO_LABEL = "LK_Servo_MG90S_steering"
else:
    sv = step("pg002-pg001-9g-servo-motor-with-clutch-protection/9g-servo-motor-with-clutch-protection.step")
    sv_body = sv.Solids[0]                                                  # bo day cap (3 solid) - day mem
    SERVO_ROT = App.Rotation(App.Matrix(0, 0, -1, 0, -1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1))
    servo_move = V(HX - 14.52, 16.69 + SDY, SHAFT_Z - 5.9)
    SERVO_LABEL = "CB_Servo9g_180_steering"
servo = placed(sv_body, SERVO_ROT, servo_move)
add(SERVO_LABEL, servo, (0.2, 0.2, 0.22))
# horn (proxy cua horn kem servo) + chot M2 (TODO: khoan lo ngoai cung cua horn 2.0 mm)
PIN_Z = SHAFT_Z + P["servo_horn_r"]
horn = fuse(cyl(3.6, 4.15, V(HX - 4.15, SDY, SHAFT_Z), V(1, 0, 0)),
            box(HX - 4.15, SDY - 2.5, SHAFT_Z, HX, SDY + 2.5, PIN_Z),
            cyl(2.5, 4.15, V(HX - 4.15, SDY, PIN_Z), V(1, 0, 0)))
add("LK_Servo_horn", horn, (0.9, 0.9, 0.9))
screw("M2x8_horn_pin", V(HX + 3.0, SDY, PIN_Z), V(1, 0, 0), 2.0, 8.0)

# Bo thu XA003+XA004: mach nam ngang, mat loi XA003 HUONG XUONG (ben duoi co cum chan to o vi tri lo bat).
rc = step("xa003-xa004-remote-control-receiver/remote-control-receiver.step")
RC_C = V(62.0, -26.0, 18.3)
receiver = placed(rc, App.Rotation(V(1, 0, 0), -90), RC_C)
add("CB_XA004_receiver", receiver, (0.1, 0.1, 0.1))

# Pin PC003 2S 7.4 V: chi lay than pin (bo day 100 mm thang trong STEP - day mem), nam ngang ben trai dong co.
bt = step("pc003-14500-7-4v-800mah-li-ion-battery/14500-7-4v-800mah-li-ion-battery.step")
# STEP pin loi BOP: common() voi hop tra ve 10.6 mm3 (that bai AM THAM, 2026-10-23) -> lay cac mat cua than pin (y <= 51.2)
_pack = [f for f in bt.Solids[0].Faces if f.BoundBox.YMax <= 51.21]
try:
    bt = Part.makeSolid(Part.makeShell(_pack))
    assert bt.isValid() and bt.Volume > 15000
except Exception:
    bt = box(-14.2, 0, -8.15, 14.2, 51.2, 8.15)                             # du phong: hop bao than pin
BAT = dict(x0=43.3, yc=23.9, z0=PLATE_TOP + 0.3)
battery = placed(bt, App.Rotation(V(0, 0, 1), -90), V(BAT["x0"], BAT["yc"], BAT["z0"] + 8.15))
add("CB_Battery_PC003", battery, (0.15, 0.25, 0.65))

# Cong tac XA007: mach nam ngang, linh kien huong len.
sw = step("xa007-power-switch-board-with-2pin-xh2-54-connector/power-switch-board-with-2pin-xh2-54-connector.step")
SW_C = V(85.75, -23.5, PLATE_TOP + 5.0)  # y -23.5: tru do cach mat trong vo (|y| 41.9) 0.5 mm;                                  # lui 1.5: than MG90S dai hon 2 mm
switch = placed(Part.makeSolid(Part.makeShell(sw.Faces)) if not sw.Solids else sw, App.Rotation(V(1, 0, 0), 90), SW_C)
add("CB_Switch_XA007", switch, (0.1, 0.1, 0.1))

# ================= CHI TIET IN =================
# ---- San xe (Chassis) ----
pts = [(-30, 0), (-30, 20), (-24, 26), (14, 26), (26, 40), (FX - 32, 40), (FX - 22, 19.5), (FX - 6, 19.5), (FX - 2, 17),
       (FX + 12, 17), (FX + 20, 10), (FX + 20, 0)]
half = [V(x, y, 0) for x, y in pts]
poly = half + [V(x, -y, 0) for x, y in reversed(pts)][1:]
plate = pos(Part.Face(Part.makePolygon(poly + [poly[0]])).extrude(V(0, 0, P["plate_t"])))
plate.translate(V(0, 0, P["plate_z0"]))
try:
    plate = plate.makeFillet(4.0, [e for e in plate.Edges if abs(e.BoundBox.ZLength - P["plate_t"]) < 1e-6])
except Exception:
    pass
c = P["clr"] * 2
plate = plate.cut(box(H["x0"] - c, -H["y"] - c, 0, H["x1"] + c, H["y"] + c, 20))   # cua so hop so (day vo 5.8 mm)
add_ch = []
# vach kep hop so (vung dong co, x 12..32), day 4 mm, chot dinh vi D3.6 vao lo D4 cua vo (TODO kiem lo tren vo 2 truc)
yi = H["y"] + P["clr"]
WALL_TOP = H["z1"] + P["clr"]
WX0, WX1, SX = H["x1"] - 20.5, H["x1"] - 0.5, H["x1"] - 10.5                     # SX: thanh chan tren
for sgn in (1, -1):
    w = box(WX0, min(sgn * yi, sgn * (yi + 4)), PLATE_TOP - 0.01, WX1, max(sgn * yi, sgn * (yi + 4)), WALL_TOP)
    w = w.cut(cyl(1.05, 6, V(SX, sgn * (yi + 2), WALL_TOP - 5.0), V(0, 0, 1)))   # lo moi vit thanh chan
    add_ch.append(w)
    if sgn > 0:
        for xx in (11.15 + 18.0, 11.15 + 24.0):
            for zz in (Z_AX - 6.5, Z_AX + 6.5):
                add_ch.append(cyl(1.8, 1.2 + 0.01, V(xx, yi + 0.01, zz), V(0, -1, 0)))
# truc lai duoi (lug) quanh chot lai + tay noi vao san
for sgn in (1, -1):
    ky = sgn * P["kingpin_y"]
    lug = cyl(3.5, 10.6 - P["plate_z0"] - P["clr"], V(KPX, ky, P["plate_z0"]), V(0, 0, 1))
    lug = lug.fuse(box(KPX - 3.5, min(ky, sgn * 15), P["plate_z0"], KPX + 3.5, max(ky, sgn * 15), 10.6 - P["clr"]))
    lug = lug.cut(cyl(1.05, 20, V(KPX, ky, 0), V(0, 0, 1)))                # lo moi vit M2.5 x 16 (chot lai)
    add_ch.append(lug)
# giu pin: chan sau + chan truoc + vach ngoai (TODO: day dan velcro qua 2 khe)
add_ch += [box(BAT["x0"] - 1.7, 10.0, PLATE_TOP - 0.01, BAT["x0"] - 0.3, 36.0, PLATE_TOP + 8),
           box(BAT["x0"] + 51.2 + 0.3, 23.0, PLATE_TOP - 0.01, BAT["x0"] + 51.2 + 1.8, 36.0, PLATE_TOP + 8),
           box(BAT["x0"], BAT["yc"] + 14.2 + 0.3, PLATE_TOP - 0.01, BAT["x0"] + 51.2, BAT["yc"] + 14.2 + 1.8, PLATE_TOP + 9)]
# tru do bo thu (4 x M2.5 tu duoi len qua san): lo bat local (+-11.5, z +-12)
for dx in (-11.5, 11.5):
    for dy in (-12.0, 12.0):
        p = V(RC_C.x + dx, RC_C.y + dy, PLATE_TOP - 0.01)
        add_ch.append(cyl(2.6, RC_C.z - 1.7 - PLATE_TOP + 0.01, p, V(0, 0, 1)))
# tru do cong tac (2 x M2)
for dx in (-6.75, 6.75):
    add_ch.append(cyl(2.4, SW_C.z - PLATE_TOP + 0.01, V(SW_C.x + dx, SW_C.y + 15.5 * (1 if dx > 0 else -1), PLATE_TOP - 0.01), V(0, 0, 1)))
# gia servo: tam dung truoc tai servo, cua so cho co truc
TAB_X = TAB_FRONT                                                           # mat sau gia = mat truoc tai servo
# cua so bao ca 2 than (PG001 y -6.06..+16.69, z +-5.9; MG90S y -5.9..+16.8, z +-6.1 quanh truc) - luon servo tu sau.
# Tran cua so: 2 mai 45 do chum lai, chi chua cau 5 mm o dinh (cau 23 mm thang -> vuon ra khi in, kiem lop 2026-10-23)
WY0, WY1, WZ = SDY - 6.06 - P["clr"], SDY + 16.8 + P["clr"], SHAFT_Z + 6.1 + P["clr"]
RISE = ((WY1 - WY0) - 5.0) / 2
bracket = box(TAB_X, -13.6 + SDY, PLATE_TOP - 0.01, TAB_X + 2.6, 21.0 + SDY, WZ + RISE + 2.0)
gable = pos(Part.Face(Part.makePolygon([V(TAB_X - 1, WY0, PLATE_TOP), V(TAB_X - 1, WY1, PLATE_TOP), V(TAB_X - 1, WY1, WZ),
                                        V(TAB_X - 1, WY1 - RISE, WZ + RISE), V(TAB_X - 1, WY0 + RISE, WZ + RISE),
                                        V(TAB_X - 1, WY0, WZ), V(TAB_X - 1, WY0, PLATE_TOP)])).extrude(V(6, 0, 0)))
bracket = bracket.cut(gable)
for ty in (SDY + 19.28, SDY - 8.49):                                       # trung binh 2 loai (lech <= 0.13 mm)
    bracket = bracket.cut(cyl(0.8, 10, V(TAB_X - 1, ty, SHAFT_Z), V(1, 0, 0)))   # lo moi vit M2
add_ch.append(bracket)
# tru nam cham (than xe) x4
POSTS = [(-14.0, 19.0), (-14.0, -19.0), (FX - 35.0, 33.0), (FX - 35.0, -33.0)]
for x, y in POSTS:
    add_ch.append(cyl(3.5, P["post_top"] - PLATE_TOP + 0.01, V(x, y, PLATE_TOP - 0.01), V(0, 0, 1)))
# cua so giam tai (khong cat duoi tru / vach / gia): sau pin, giua bo thu, giua san, truoc giua 2 tai lai, sau truc sau
for x0, y0, x1, y1 in ((47, 14, 91, 34), (54, -34, 70, -18), (72, -4, 90, 8), (103, -10, 114, 12), (FX - 12, -10, FX + 2, 10),
                       (-27, -14, -19, 14)):
    w = box(x0, y0, P["plate_z0"] - 1, x1, y1, PLATE_TOP + 1)
    try:
        w = w.makeFillet(2.5, [e for e in w.Edges if e.BoundBox.ZLength > 1])
    except Exception:
        pass
    plate = plate.cut(w)
chassis = fuse(plate, *add_ch)
for x, y in POSTS:
    chassis = chassis.cut(cyl(P["magnet_d"] / 2, P["magnet_h"] + 0.01, V(x, y, P["post_top"] - P["magnet_h"]), V(0, 0, 1)))
# lo vit bat (M2.5 qua san vao tru bo thu)
for dx in (-11.5, 11.5):
    for dy in (-12.0, 12.0):
        chassis = chassis.cut(cyl(1.05, 40, V(RC_C.x + dx, RC_C.y + dy, 0), V(0, 0, 1)))
for dx in (-6.75, 6.75):
    chassis = chassis.cut(cyl(0.8, 40, V(SW_C.x + dx, SW_C.y + 15.5 * (1 if dx > 0 else -1), 0), V(0, 0, 1)))
add("Chassis", chassis, (0.85, 0.15, 0.12))
# vit bat linh kien (proxy de BOM dem): bo thu 4 x M2.5 x 6 tu duoi len qua san; cong tac 2 x M2 x 6; servo 2 x M2 x 8
for i, (dx, dy) in enumerate(((-11.5, -12.0), (-11.5, 12.0), (11.5, -12.0), (11.5, 12.0))):
    screw(f"M2_5x6_receiver{i + 1:03d}" if i else "M2_5x6_receiver", V(RC_C.x + dx, RC_C.y + dy, P["plate_z0"] + 6.0),
          V(0, 0, 1), 2.5, 6.0)
for i, dx in enumerate((-6.75, 6.75)):
    screw(f"M2x6_switch{i + 1:03d}" if i else "M2x6_switch",
          V(SW_C.x + dx, SW_C.y + 15.5 * (1 if dx > 0 else -1), PLATE_TOP + 4.0), V(0, 0, 1), 2.0, 6.0)
for i, ty in enumerate((SDY + 19.28, SDY - 8.49)):
    screw(f"M2x8_servo{i + 1:03d}" if i else "M2x8_servo", V(TAB_X + 2.6 + 0.01, ty, SHAFT_Z), V(1, 0, 0), 2.0, 8.0)

# thanh chan tren hop so (2 x M2.5 x 6 vao dinh 2 vach)
strap = box(SX - 3.0, -(yi + 4), WALL_TOP, SX + 3.0, yi + 4, WALL_TOP + 2.0)
for sgn in (1, -1):
    strap = strap.cut(cyl(1.35, 10, V(SX, sgn * (yi + 2), 0), V(0, 0, 1)))
add("Gearbox_strap", strap, (0.85, 0.15, 0.12))
for sgn, nm in ((1, "L"), (-1, "R")):
    screw(f"M2_5x6_strap_{nm}", V(SX, sgn * (yi + 2), WALL_TOP + 2.0 - 6.0), V(0, 0, -1), 2.5, 6.0)

# ---- Khop lai (knuckle): IN UP (mat tren z 22.8 xuong ban) - khong can support ----
# Than chot lai (tru dung) + khoi giu truc (lo ngang giot nuoc, dinh huong -z = huong len khi in up) + vach noi
# + 2 dai noi tren/duoi (chua cho long den + dau vit giu banh o giua). Truc banh in lien VANH (xem rim()).
BORE_Y0, BORE_Y1 = 24.0, YW - P["tire_w"] / 2 + 0.1 - 0.2                  # khoi giu truc: y 24 .. mat trong banh - 0.2
WASHER_T = 1.0


def giot_nuoc(r, y0, y1, cx, cz, dinh=-1):
    """Lo ngang theo Y, mat cat giot nuoc (tron + mui 45 do huong z*dinh) - in duoc khong can do."""
    tri = Part.Face(Part.makePolygon([V(cx + r * math.cos(math.radians(45)), 0, cz + dinh * r * math.sin(math.radians(45))),
                                      V(cx, 0, cz + dinh * r * math.sqrt(2)),
                                      V(cx - r * math.cos(math.radians(45)), 0, cz + dinh * r * math.sin(math.radians(45))),
                                      V(cx + r * math.cos(math.radians(45)), 0, cz + dinh * r * math.sin(math.radians(45)))]))
    t = tri.extrude(V(0, y1 - y0, 0))
    t.translate(V(0, y0, 0))
    return cyl(r, y1 - y0, V(cx, y0, cz), V(0, 1, 0)).fuse(t)


for sgn, nm in ((1, "L"), (-1, "R")):
    ky = sgn * P["kingpin_y"]
    yb0, yb1 = sorted((sgn * BORE_Y0, sgn * BORE_Y1))
    yw0, yw1 = sorted((ky, sgn * BORE_Y0))
    k = fuse(cyl(4.0, 22.8 - 10.6, V(KPX, ky, 10.6), V(0, 0, 1)),               # than chot lai
             box(FX - 4.0, yb0, 10.6, KPX + 0.5, yb1, 22.8),                     # khoi giu truc
             box(FX + 4.4, yw0, 10.6, KPX, yw1, 22.8),                           # vach noi
             box(FX - 4.0, yw0, 10.6, FX + 4.4, yw1, 12.4),                      # dai duoi
             box(FX - 4.0, yw0, 21.2, FX + 4.4, yw1, 22.8))                      # dai tren
    ex, ey = TR_EX, sgn * TR_EY
    d = V(ex - KPX, ey - ky, 0)
    nrm = V(-d.y, d.x, 0).normalize() * 2.0
    arm = pos(Part.Face(Part.makePolygon([V(KPX, ky, 20.5) + nrm, V(ex, ey, 20.5) + nrm, V(ex, ey, 20.5) - nrm,
                                      V(KPX, ky, 20.5) - nrm, V(KPX, ky, 20.5) + nrm])).extrude(V(0, 0, 2.3)))
    k = fuse(k, arm, cyl(3.0, 2.3, V(ex, ey, 20.5), V(0, 0, 1)))
    k = k.cut(cyl(1.35, 30, V(KPX, ky, 0), V(0, 0, 1)))                    # chot lai M2.5 x 16 (lo qua 2.7)
    k = k.cut(cyl(1.05, 10, V(ex, ey, 15), V(0, 0, 1)))                    # lo moi vit noi thanh giang
    k = k.cut(giot_nuoc(P["stub_d"] / 2 + P["clr"], yb0 - 1, yb1 + 1, FX, Z_AX))   # lo truc banh
    add(f"Knuckle_{nm}", k, (0.85, 0.15, 0.12))
    # long den giu banh (in) + vit M2.5 x 6 vao dau truc
    stub_end = sgn * (BORE_Y0 - 0.3)
    wy0, wy1 = sorted((stub_end, stub_end - sgn * WASHER_T))
    add(f"Washer_axle_{nm}", cyl(4.0, WASHER_T, V(FX, wy0, Z_AX), V(0, 1, 0)).cut(
        cyl(1.35, 5, V(FX, wy0 - 1, Z_AX), V(0, 1, 0))), (0.85, 0.15, 0.12))
    screw(f"M2_5x6_axle_{nm}", V(FX, stub_end + sgn * 4.5, Z_AX), V(0, sgn, 0), 2.5, 6.0)
    screw(f"M2_5x16_kingpin_{nm}", V(KPX, ky, 22.8 - 16.0), V(0, 0, -1), 2.5, 16.0)
    screw(f"M2_5x6_tierod_{nm}", V(ex, ey, 25.0 - 6.0), V(0, 0, -1), 2.5, 6.0)

# ---- Thanh giang (tie rod) + tai nhan chot horn ----
tr = box(TR_EX - 1.5, -TR_EY, 23.0, TR_EX + 2.0, TR_EY, 25.0)                # mep sau cach horn 0.4
for sgn in (1, -1):
    tr = tr.fuse(cyl(3.0, 2.0, V(TR_EX, sgn * TR_EY, 23.0), V(0, 0, 1)))
tab = box(HX + 0.33, SDY - 4.0, 19.0, HX + 2.33, SDY + 4.0, 23.01)
tr = fuse(tr, tab)
tr = tr.cut(box(HX, SDY - 1.1, 20.3, HX + 3, SDY + 1.1, 23.0 - 0.01))     # khe doc cho chot horn
for sgn in (1, -1):
    tr = tr.cut(cyl(1.35, 10, V(TR_EX, sgn * TR_EY, 20), V(0, 0, 1)))
add("Tie_rod", tr, (0.85, 0.15, 0.12))

# ---- Banh (rim) x4 ----
def rim(sgn, rear):
    yc = sgn * YW
    w = P["tire_w"] - 0.2
    y0 = yc - w / 2
    # dai giua (om long trong lop r15.25) vat 45 do 2 mep: in dung khong co go ngang 1.65 mm (kiem lop)
    dh = 15.05 - 13.4
    r = fuse(cyl(13.4, w, V(0, y0, 0), V(0, 1, 0)), cyl(15.05, 9.8 - 2 * dh, V(0, yc - 4.9 + dh, 0), V(0, 1, 0)),
             Part.makeCone(13.4, 15.05, dh, V(0, yc - 4.9, 0), V(0, 1, 0)),
             Part.makeCone(15.05, 13.4, dh, V(0, yc + 4.9 - dh, 0), V(0, 1, 0)))
    r = r.cut(cyl(11.4, w - 2.0, V(0, yc - sgn * 1.0 - (w - 2.0) / 2, 0), V(0, 1, 0)))   # long trong (mat ngoai day 2)
    hub_in = sgn * 9.6 if rear else yc - sgn * (w / 2)
    hy0, hy1 = sorted((hub_in, yc + sgn * w / 2))
    r = r.fuse(cyl(4.5, hy1 - hy0, V(0, hy0, 0), V(0, 1, 0)))
    face_y = yc + sgn * (w / 2) - (2.0 if sgn > 0 else 0)
    for k in range(5):                                                      # 5 cua so giua 5 nan
        a0 = 2 * math.pi * k / 5 + 0.18
        a1 = a0 + 2 * math.pi / 5 - 0.36
        pts = [V(r0 * math.cos(a), face_y - 0.01, r0 * math.sin(a)) for r0, a in
               [(5.6, a0), (11.0, a0), (11.0, (a0 + a1) / 2), (11.0, a1), (5.6, a1)]]
        wire = Part.Wire([Part.LineSegment(pts[0], pts[1]).toShape(),
                          Part.Arc(pts[1], pts[2], pts[3]).toShape(),
                          Part.LineSegment(pts[3], pts[4]).toShape(),
                          Part.LineSegment(pts[4], pts[0]).toShape()])
        r = r.cut(pos(Part.Face(wire).extrude(V(0, 2.02, 0))))
    if rear:  # lo double-D (2 mat dep) om truc ra
        dd = cyl(P["rear_bore_d"] / 2, 120, V(0, -60, 0), V(0, 1, 0)).common(
            box(-P["rear_bore_af"] / 2, -60, -5, P["rear_bore_af"] / 2, 60, 5))
        r = r.cut(dd)
    else:  # truc banh in lien vanh (vanh in dung -> truc theo phuong Z khi in, khong can do), lo moi vit o dau truc
        y_in = yc - sgn * w / 2
        s_end = sgn * (BORE_Y0 - 0.3)
        sy0, sy1 = sorted((y_in + sgn * 0.01, s_end))
        r = r.fuse(cyl(P["stub_d"] / 2, sy1 - sy0, V(0, sy0, 0), V(0, 1, 0)))
        hy = (s_end, s_end + sgn * 5.0)
        r = r.cut(cyl(1.05, 5.0, V(0, min(hy), 0), V(0, 1, 0)))
    return r


for nm, x, sgn, rear in (("RL", 0, 1, True), ("RR", 0, -1, True), ("FL", FX, 1, False), ("FR", FX, -1, False)):
    add(f"Wheel_{nm}", placed(rim(sgn, rear), move=V(x, 0, Z_AX)), (0.75, 0.75, 0.78))

# ---- Than xe coupe (loft cac mat cat) ----
Z0 = PLATE_TOP + 0.2
ST = [  # x, nua rong w, cao vai (belt) zb, cao dinh h, nua rong mai wr
    # IN DUNG (duoi up xuong ban): duoi no ra <= ~45 do de vo tu in khong can do
    (-41.5, 24, 17, 21.0, 19), (-35, 30, 22, 26.0, 25), (-28, 36, 27, 31.5, 31), (-21, 42, 33, 37.0, 36.5),
    (0, 44, 39, 42.0, 40), (18, 44, 37.5, 45, 31),                              # vom chan bun sau phong
    (38, 43.5, 37, 55, 26), (66, 43.5, 37, 56, 26), (88, 43.5, 37, 48, 30), (108, 43.5, 37.5, 41.0, 37),
    (FX, 43.5, 39.5, 43.0, 40), (FX + 20, 42, 34, 36.0, 37),                     # vom chan bun truoc phong (FX + 34, 34, 21, 23.5, 29),
    (FX + 39, 26, 16.5, 19.0, 21), (FX + 41, 17, 13.5, 15.5, 13)]               # mui bo tron


def upper_curve(w, zb, h, wr, zc):
    """1/4 tren phai (y >= 0): (w, zc) -> suon dung -> vai bo -> kinh nghieng -> mep mai (wr) -> dinh (0, h).
    Dang GT (Tuan 2026-10-26; concept freecad/scripts/concept_gt_body.py)."""
    wr = min(wr, w - 1.0)
    sh = min(1.4, max(0.6, (h - zb) * 0.2))                                  # ban kinh vai (thap o vom chan bun)
    poles = [V(w, zc, 0), V(w, zb - sh, 0), V(w - 0.3, zb + sh * 0.6, 0),
             V(wr + 1.5, h - 2.5, 0), V(wr * 0.55, h, 0), V(0, h, 0)]
    bs = Part.BSplineCurve()
    bs.buildFromPoles(poles, False, 3)
    return bs


def section(x, w, zb, h, wr, z0, t=0.0, n=48):
    """Mat cat YZ: than duoi sieu-ellipse (vuong bo, n=6) tu z0 toi giua suon; nua tren = suon dung toi vai zb, vai bo,
    kinh nghieng vao mep mai wr, dinh h (upper_curve). Cung so diem + cung tham so cho moi tram -> loft tron, khong gon."""
    w, zb, h, wr = w - t, zb - t, h - t, wr - t
    zc = (z0 + zb) / 2.0
    uc = upper_curve(w, zb, h, wr, zc)
    u0, u1 = uc.FirstParameter, uc.LastParameter
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2                               # seam o giua day (bi cat bo khi lam day ho)
        ca, sa = math.cos(a), math.sin(a)
        if sa < 0:   # nua duoi
            y = w * math.copysign(abs(ca) ** (2 / 6.0), ca)
            z = zc - (zc - z0) * abs(sa) ** (2 / 6.0)
        else:        # nua tren: 0 o suon -> 1 o dinh (doi xung)
            f = (a if ca >= 0 else math.pi - a) / (math.pi / 2)
            p = uc.value(u0 + (u1 - u0) * min(max(f, 0.0), 1.0))
            y, z = (math.copysign(p.x, ca) if abs(ca) > 1e-9 else 0.0), p.y
        pts.append(V(x, y, z))
    bs = Part.BSplineCurve()
    bs.interpolate(pts, PeriodicFlag=True)
    return Part.Wire(bs.toShape())


outer = Part.makeLoft([section(x, w, zb, h, wr, Z0) for x, w, zb, h, wr in ST], True, False)
inner = Part.makeLoft([section(x, w, zb, h, wr, Z0 - 6, P["shell_t"]) for x, w, zb, h, wr in ST[1:-1]], True, False)
# tran trong o mui (dinh khi in dung, +X len): SONG MAI nam ngang theo Y tai giua chieu cao khoang, 2 mat doc 50 do -
# vo tren + duoi moc dan vao trong roi khep o song mai (dinh huong LEN). Khong dung V/rang cua theo Y: day rang la go
# chia XUONG -> lop dau la duong bac cau 20 mm (kiem theo lop phat hien 2026-10-23).
NOSE_C = FX + 34.0                                                          # = cuoi doan vo thu hep o mui
NOSE_ZC = Z0  # song mai tai MEP DAY HO: day ho -> khong co vo duoi de mat doc duoi moc len (cum roi o day, kiem lop)
_w = [V(NOSE_C, 0, NOSE_ZC), V(NOSE_C - 1.2 * 60, 0, NOSE_ZC + 60), V(-200, 0, NOSE_ZC + 60),
      V(-200, 0, NOSE_ZC - 60), V(NOSE_C - 1.2 * 60, 0, NOSE_ZC - 60), V(NOSE_C, 0, NOSE_ZC)]
wnose = pos(Part.Face(Part.makePolygon(_w)).extrude(V(0, 120, 0)))
wnose.translate(V(0, -60, 0))
inner = inner.common(wnose)
body = outer.cut(inner)
DIAG = {"outer": [outer.isValid(), round(outer.Volume)], "inner": [inner.isValid(), round(inner.Volume)], "shell": [body.isValid(), round(body.Volume)]}
body = body.cut(box(-60, -60, -10, FX + 80, 60, Z0))                            # day phang
DIAG["flat"] = [body.isValid(), round(body.Volume)]
for x, r, dx in ((0, P["rear_arch_r"], 0), (FX, P["front_arch_r"], P["front_arch_dx"])):
    for sgn in (1, -1):
        y0, y1 = sorted((sgn * 25.0, sgn * 60.0))
        arch = cyl(r, y1 - y0, V(x - dx, y0, Z_AX), V(0, 1, 0))
        if dx:
            arch = fuse(arch, cyl(r, y1 - y0, V(x + dx, y0, Z_AX), V(0, 1, 0)),
                        box(x - dx, y0, Z_AX - r, x + dx, y1, Z_AX + r))
        # IN DUNG (+X len): dinh truoc hoc banh nhon 45 do (giot nuoc) + vat 45 do xuong mep duoi -> mep hoc banh
        # khong thanh tran treo. Kieu hoc banh goc canh.
        xf = x + dx
        c45 = r * math.cos(math.radians(45))
        xa = xf + r * math.sqrt(2)
        flare = pos(Part.Face(Part.makePolygon([V(xf, 0, Z_AX), V(xf + 0.98 * c45, 0, Z_AX + 0.98 * c45), V(xa, 0, Z_AX),
                                                V(xa + (Z_AX - Z0) + 1.0, 0, Z0 - 1.0), V(xf, 0, Z0 - 1.0),
                                                V(xf, 0, Z_AX)])).extrude(V(0, y1 - y0, 0)))
        flare.translate(V(0, y0, 0))
        arch = arch.fuse(flare)
        body = body.cut(arch)
        DIAG[f"arch_{x}_{sgn}"] = [body.isValid(), round(body.Volume)]


# ---- Kinh khac chim (Tuan 2026-10-26): lang tru kinh GIAO lop da [mat ngoai + 1 mm .. mat ngoai - win_d] ----
# dao loi ra ngoai 1 mm -> khong trung mat B-spline cua vo (trung mat -> boolean hong)
def lerp_st(x, k):
    """noi suy cot k (1 w, 2 zb, 3 h, 4 wr) cua ST theo x"""
    for (xa, *a), (xb, *b) in zip(ST, ST[1:]):
        if xa <= x <= xb:
            return a[k - 1] + (b[k - 1] - a[k - 1]) * (x - xa) / (xb - xa)


def rounded(pts, r, plane):
    vs = [V(p[0], 0, p[1]) if plane == "xz" else V(p[0], p[1], 0) for p in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).makeOffset2D(-r).makeOffset2D(r)


_xs = list(range(26, 93, 2))                                                 # kinh hong: vai + 2,5 .. mep mai - 3,5
fs = rounded([(x, lerp_st(x, 2) + 2.5) for x in _xs] + [(x, min(lerp_st(x, 3) - 3.5, 52.5)) for x in reversed(_xs)],
             2.5, "xz")
_wx, _rx = [89, 93, 97, 101, 105], [4, 10, 16, 22, 28, 34]                    # kinh lai / kinh sau (fastback)
fw = rounded([(x, lerp_st(x, 4) - 5) for x in _wx] + [(x, 5 - lerp_st(x, 4)) for x in reversed(_wx)], 2.0, "xy")
fr = rounded([(x, lerp_st(x, 4) - 7) for x in _rx] + [(x, 7 - lerp_st(x, 4)) for x in reversed(_rx)], 3.0, "xy")
fw.translate(V(0, 0, 38))
fr.translate(V(0, 0, 41))
skin = (Part.makeLoft([section(x, w, zb, h, wr, Z0, -1.0) for x, w, zb, h, wr in ST], True, False)
        .cut(Part.makeLoft([section(x, w, zb, h, wr, Z0, P["win_d"]) for x, w, zb, h, wr in ST], True, False)))
DIAG["solids_truoc_kinh"] = [round(x.Volume, 1) for x in body.Solids]
body = max(body.Solids, key=lambda x: abs(x.Volume))                        # manh vun do cat mat day -> boolean hong
for nm, prism in (("side", fs.extrude(V(0, 70, 0)).fuse(fs.extrude(V(0, -70, 0)))),
                  ("wind", fw.extrude(V(0, 0, 40))), ("rear", fr.extrude(V(0, 0, 40)))):
    body, _inf = se.safe_cut(body, skin.common(prism), rel_tol=0.15, abs_tol_mm3=30, mesh_mm=0.1, fuzzy=(0.0,))  # lop 0,4 mm: luoi 0,3 uoc lech 16 %
    DIAG[f"glass_{nm}"] = [body.isValid(), round(body.Volume), _inf["uoc_mm3"], _inf["doi_mm3"]]
# o nam cham: GAN tam giac moc tu vo xuong (canh duoi theo chieu in doc 50 do), hoc ngam dau tru + lo nam cham
# mat cat giot nuoc (mui huong +X = huong len khi in dung)


def giot_nuoc_z(r, z0, h, cx, cy):
    c45 = 0.9 * r * math.cos(math.radians(45))                              # day tam giac lot vao trong duong tron (tranh tiep tuyen)
    tri = pos(Part.Face(Part.makePolygon([V(cx + c45, cy + c45, z0), V(cx + r * math.sqrt(2), cy, z0), V(cx + c45, cy - c45, z0),
                                      V(cx + c45, cy + c45, z0)])).extrude(V(0, 0, h)))
    return cyl(r, h, V(cx, cy, z0), V(0, 0, 1)).fuse(tri)


ZB = P["post_top"] - 2.0 + P["clr"]
# gan cat bang loft GIUA be day vo (lech shell_t/2): mat gan khong trung mat B-spline cua vo (trung mat -> boolean hong)
MID = Part.makeLoft([section(x, w, zb, h, wr, Z0 - 6, P["shell_t"] / 2) for x, w, zb, h, wr in ST[1:-1]], True, False)
# cat mat day tao 2 manh vun 0.2 mm3 -> boolean tren khoi NHIEU solid hong (fuse ra -125 000 mm3, safe_fuse bat duoc)
DIAG["solids_truoc_gan"] = [round(x.Volume, 1) for x in body.Solids]
body = max(body.Solids, key=lambda x: abs(x.Volume))
for x, y in POSTS:
    fin = pos(Part.Face(Part.makePolygon([V(x - 4.8, 0, ZB), V(x + 4.8, 0, ZB), V(x + 4.8, 0, 80),
                                      V(x - 4.8 - 1.2 * (80 - ZB), 0, 80), V(x - 4.8, 0, ZB)])).extrude(V(0, 9.6, 0)))
    fin.translate(V(0, y - 4.8, 0))
    # khoet hoc tren GAN (khoi lang tru don gian, boolean ben) truoc khi gan vao vo B-spline:
    # dao bat dau duoi mat day gan 0.5 mm, 2 dao chong nhau 0.1 mm (mat gan trung -> boolean hong)
    for tool in (giot_nuoc_z(3.5 + P["clr"], ZB - 0.5, 2.5, x, y),
                 giot_nuoc_z(P["magnet_d"] / 2, ZB + 1.9, P["magnet_h"] + 0.1, x, y)):
        fin = fin.cut(tool)
    fc = fin.common(MID)
    DIAG.setdefault("fins", []).append(round(fc.Volume, 1))
    # safe_fuse: kiem luong them = V(gan) - V(giao) tinh tren luoi (boolean tren loft B-spline tung lat/lon nguoc am tham)
    _t0 = time.time()
    body, _inf = se.safe_fuse(body, fc, rel_tol=0.15, abs_tol_mm3=30, mesh_mm=0.3, fuzzy=(0.0,))
    print("FIN", x, y, round(time.time() - _t0, 1), "s", _inf["uoc_mm3"], _inf["doi_mm3"], flush=True)
# KHONG removeSplitter(): tren loft B-spline no lon nguoc solid (the tich am, STL phap tuyen nguoc)
DIAG["pre_fix"] = [body.isValid(), len(body.Solids), [round(x.Volume, 1) for x in body.Solids]]
body = max(body.Solids, key=lambda x: abs(x.Volume))                        # bo manh vun < 1 mm3 (do cat mat day)
if body.Volume < 0:
    body.reverse()
DIAG["final"] = [body.isValid(), round(body.Volume, 1)]
add("Body_coupe", body, (0.92, 0.35, 0.05))

for i, (x, y) in enumerate(POSTS):
    for part, z in (("chassis", P["post_top"] - P["magnet_h"]), ("body", P["post_top"] + P["clr"])):
        add(f"CB_Magnet_4x2_{part}_{i + 1}", cyl(2.0, 2.0, V(x, y, z), V(0, 0, 1)), (0.6, 0.6, 0.65))

doc.recompute()
# ---- luu (file SINH RA: ban cu -> backup) ----
os.makedirs(os.path.dirname(OUT), exist_ok=True)
if os.path.exists(OUT):
    bk = os.path.join(os.path.dirname(OUT), "backup")
    os.makedirs(bk, exist_ok=True)
    shutil.copy2(OUT, os.path.join(bk, "cyberbrick_car.%s.FCStd" % time.strftime("%Y%m%d-%H%M%S")))
doc.saveAs(OUT)
json.dump(COLORS, open(os.path.join(PROJ, "freecad", "colors.json"), "w"), indent=1)
json.dump(P, open(os.path.join(PROJ, "freecad", "params.json"), "w"), indent=1)
info = {o.Label: [round(v, 1) for v in (o.Shape.BoundBox.XMin, o.Shape.BoundBox.YMin, o.Shape.BoundBox.ZMin,
                                         o.Shape.BoundBox.XMax, o.Shape.BoundBox.YMax, o.Shape.BoundBox.ZMax)]
        for o in doc.Objects if o.Label in ("Body_coupe", "Chassis", "CB_Gearbox_030_dual_axis", "CB_Servo9g_180_steering",
                                            "CB_XA004_receiver", "CB_Battery_PC003", "CB_Switch_XA007", "Tie_rod")}
print("DIAG", json.dumps(DIAG))
print("BUILD_OK", json.dumps({"objects": len(doc.Objects), "body_valid": body.isValid(), "body_solids": len(body.Solids),
                              "chassis_valid": chassis.isValid(), "chassis_solids": len(chassis.Solids), "bb": info}))
