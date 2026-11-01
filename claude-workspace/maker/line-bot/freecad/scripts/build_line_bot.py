"""Script FreeCAD dung TOAN BO model xe line-bot tu params.json (concept A - Khung tang).
Chay: freecadcmd scripts/build_line_bot.py
Ra: line_bot.FCStd (bien LINEBOT_OUT, mac dinh canh scripts/).
Khong co so kich thuoc linh kien nao viet cung trong script nay (tru hang bo tri ghi ro trong spec).
He truc: X tien, Y trai, Z len; goc = trung diem 2 truc banh tren mat san.
"""
import json
import math
import os
import shutil
import sys
import time

import FreeCAD as App
import Part

# --- duong dan ---
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)  # maker/line-bot/freecad
LIB = os.path.join(PROJ, "..", "..", "..", "tools", "robotics-cad", "scripts")
sys.path.insert(0, LIB)
from cad_lib import box, cyl, rrect, V  # noqa: E402

# --- doc params ---
PARAMS_DEFAULT = os.path.join(PROJ, "params.json")
PARAMS = os.environ.get("LINEBOT_PARAMS", PARAMS_DEFAULT)
P = json.loads(open(PARAMS, encoding="utf-8").read())

OUT_DEFAULT = os.path.join(PROJ, "line_bot.FCStd")
OUT = os.environ.get("LINEBOT_OUT", OUT_DEFAULT)

# --- tham chieu params ---
banh = P["linh_kien"]["banh"]
n20 = P["linh_kien"]["n20"]
mega = P["linh_kien"]["mega"]
bi_do = P["linh_kien"]["bi_do"]
line = P["linh_kien"]["line"]
sr04 = P["linh_kien"]["sr04"]
pin_2s = P["linh_kien"]["pin_2s"]
driver = P["linh_kien"]["driver"]
khung = P["khung"]
lo_vit = P["lo_vit"]

# --- hang tinh toan ---
R = banh["d"] / 2.0           # ban kinh banh
khe = khung["khe"]             # khe lap ghep
tam_duoi_t = khung["tam_duoi_t"]
tam_tren_t = khung["tam_tren_t"]
cot_cao = khung["cot_cao"]
cot_d = khung["cot_d"]
bo_goc_r = khung["bo_goc_r"]
m3x = lo_vit["m3_xuyen"]
m3r = lo_vit["m3_tu_ren"]
m16 = lo_vit["m16_xuyen"]

# --- hang bo tri (spec cot dinh) ---
# Base_plate: day tai z = R + n20.h/2 + khe + 2.0
Z_BASE_BOT = R + n20["h"] / 2.0 + khe + 2.0
Z_BASE_TOP = Z_BASE_BOT + tam_duoi_t
# Top_plate: day tai dinh cot
Z_TOP_BOT = Z_BASE_TOP + cot_cao
Z_TOP_TOP = Z_TOP_BOT + tam_tren_t
# Cot vi tri (±58, ±48) tinh tu tam
COT_POS = [(-58, -48), (-58, 48), (58, -48), (58, 48)]
# Base_plate kich thuoc: 140 x 120 (X: -70..+70, Y: -60..+60)
BP_X = (-70.0, 70.0)
BP_Y = (-60.0, 60.0)

# --- tao doc ---
doc = App.newDocument("line_bot")

COLOR_PRINT = (0x3a / 255, 0x8f / 255, 0xd9 / 255)  # xanh #3a8fd9
COLOR_MEGA = (0.0, 0.7, 0.2)                          # xanh la
COLOR_WHEEL = (0.1, 0.1, 0.1)                         # den
COLOR_SENSOR = (0.8, 0.1, 0.2)                        # do
COLOR_SONAR = (0.5, 0.1, 0.7)                         # tim

COLORS = {}


def add(label, shape, color=None):
    o = doc.addObject("Part::Feature", label)
    o.Label = label
    o.Shape = shape
    if color:
        COLORS[label] = color
    return o


def fuse_all(*shapes):
    """Gop nhieu solid thanh 1, removeSplitter."""
    s = shapes[0]
    for t in shapes[1:]:
        s = s.fuse(t)
    return s.removeSplitter()


def cut_all(base, *tools):
    """Cat base boi nhieu tool gop lai mot lan."""
    if not tools:
        return base
    tool = fuse_all(*tools) if len(tools) > 1 else tools[0]
    return base.cut(tool)


# ===========================================================================
# 1. REF_WHEEL_L / REF_WHEEL_R
# Tru O banh.d day banh.w, truc song song Y
# Mat trong tai |y| = 61, ra ngoai toi |y| = 61 + banh.w
# Tam truc tai x=0, z=R
# ===========================================================================
WHEEL_Y_IN = 61.0  # hang bo tri

for side, sign in (("L", 1), ("R", -1)):
    y_in = sign * WHEEL_Y_IN
    y_out = sign * (WHEEL_Y_IN + banh["w"])
    # cyl(r, axis, span, at=(y_truc_1, y_truc_2))
    # truc song song Y -> axis='y', at=(x_tam, z_tam) = (0, R)
    wheel = cyl(banh["d"] / 2.0, "y", (min(y_in, y_out), max(y_in, y_out)), at=(0.0, R))
    add(f"Ref_Wheel_{side}", wheel, COLOR_WHEEL)

# ===========================================================================
# 2. REF_N20_L / REF_N20_R
# Khoi n20.w (X) x n20.h (Z) x (n20.dai - n20.truc_dai + dai_encoder_them) (Y)
# + truc O truc_d dai truc_dai huong ra ngoai
# Mat hop so (goc truc) tai |y| = 59, than di vao trong
# Tam truc tai (0, +/-, R)
# ===========================================================================
GEARBOX_Y_FACE = 59.0  # hang bo tri
n20_body_len = n20["dai"] - n20["truc_dai"] + n20["dai_encoder_them"]

for side, sign in (("L", 1), ("R", -1)):
    # mat hop so tai sign*59
    # than di vao trong (sign nguoc lai)
    y_face = sign * GEARBOX_Y_FACE
    y_far = y_face - sign * n20_body_len  # dau xa cua than
    y_lo = min(y_face, y_far)
    y_hi = max(y_face, y_far)
    body_n20 = box(
        x=(- n20["w"] / 2.0, n20["w"] / 2.0),
        y=(y_lo, y_hi),
        z=(R - n20["h"] / 2.0, R + n20["h"] / 2.0),
    )
    # truc: tu mat hop so ra ngoai, dai truc_dai
    y_shaft_end = y_face + sign * n20["truc_dai"]
    y_sh_lo = min(y_face, y_shaft_end)
    y_sh_hi = max(y_face, y_shaft_end)
    shaft = cyl(n20["truc_d"] / 2.0, "y", (y_sh_lo, y_sh_hi), at=(0.0, R))
    motor_shape = fuse_all(body_n20, shaft)
    add(f"Ref_N20_{side}", motor_shape)

# ===========================================================================
# 3. MOTOR_MOUNT_L / MOTOR_MOUNT_R
# Khoi om motor: hoc (n20.w + 2*khe) x (n20.h + 2*khe) de motor luon tu phia trong
# Vach dau phia mat hop so day 2.5: lo truc O(truc_d+1.6), 2 lo M1.6 cach ±vit_cach_tam
# Mat tren phang ap day Base_plate, 2 lo M3 tu ren (O m3_tu_ren, sau 8) vit tu tren xuong
# Thanh quanh hoc >= 2.0
# ===========================================================================
MM_WALL = 2.0        # thanh toi thieu
MM_CAP = 1.6         # vach mat hop so (Claude 2026-11-01: 59 + 1,6 = 60,6 -> chua 0,4 toi mat trong banh |y| = 61)

# Motor mount: mat tren tai Z_BASE_BOT (ap day Base_plate)
# Motor body nam tu y_face = ±59 vao trong
# Cac kich thuoc hoc
hoc_w = n20["w"] + 2 * khe   # theo X
hoc_h = n20["h"] + 2 * khe   # theo Z

# Chieu dai hoc (theo Y): bang chieu dai than motor (khong tinh truc)
hoc_len = n20_body_len + khe  # chieu dai hoc: mat hop so AP vach (bat vit M1.6), khe chi o dau sau

# Mat tren cua gia = Z_BASE_BOT
# Z tam motor = R, Z day hoc = R - hoc_h/2, Z dinh hoc = R + hoc_h/2
# Chieu cao gia tu Z_BASE_BOT xuong den Z_BASE_BOT - (Z_BASE_BOT - (R - hoc_h/2)) + MM_CAP
# Chieu cao ben ngoai: tu day gia xuong den Z (R - n20.h/2 - khe) + MM_WALL
z_hoc_bot = R - hoc_h / 2.0
z_hoc_top = R + hoc_h / 2.0

# Chieu cao gia (theo Z): tu Z_BASE_BOT xuong bao phu hoc + thanh duoi
mm_height = Z_BASE_BOT - z_hoc_bot + MM_WALL  # chieu cao toan bo gia

# Vi tri M3 tu ren tren mat tren (theo X, theo Y tu mat hop so)
# Dat 2 lo M3 cach nhau theo Y, ca 2 nam trong vung vach ngoai
MM_SCREW_OFFSET_X = 0.0            # giua theo X
MM_SCREW_OFFSET_Y = (hoc_len / 2.0 + MM_WALL / 2.0 + 2.0)  # tu tam gia theo Y (ra phia encoder)

for side, sign in (("L", 1), ("R", -1)):
    y_face = sign * GEARBOX_Y_FACE  # mat hop so
    # Y ngoai cung cua gia: tu y_face den y_face - sign*(hoc_len + MM_CAP)
    # Thanh ngoai: y_face toi y_face + sign*MM_CAP (phia ngoai - vach mat hop so)
    # Hoc: tu y_face - sign*0 den y_face - sign*hoc_len
    y_hoc_inner = y_face - sign * hoc_len  # cuoi hoc (phia trong xe)

    # Pham vi Y cua gia: tu mat ngoai (y_face + sign*MM_CAP) den cuoi trong (y_hoc_inner - sign*MM_WALL)
    y_mount_outer = y_face + sign * MM_CAP
    y_mount_inner = y_hoc_inner - sign * MM_WALL

    y_lo = min(y_mount_outer, y_mount_inner)
    y_hi = max(y_mount_outer, y_mount_inner)

    # X cua gia: tam motor tai x=0, gia rong hoc_w + 2*MM_WALL
    x_lo = -(hoc_w / 2.0 + MM_WALL)
    x_hi = (hoc_w / 2.0 + MM_WALL)

    # Z cua gia: tu (z_hoc_bot - MM_WALL) den Z_BASE_BOT
    z_lo = z_hoc_bot - MM_WALL
    z_hi = Z_BASE_BOT

    mount_solid = box(x=(x_lo, x_hi), y=(y_lo, y_hi), z=(z_lo, z_hi))

    # Cat hoc motor (tu phia trong - y_hoc_inner vao den y_face)
    hoc_y_lo = min(y_face, y_hoc_inner)
    hoc_y_hi = max(y_face, y_hoc_inner)
    hoc_motor = box(
        x=(-hoc_w / 2.0, hoc_w / 2.0),
        y=(hoc_y_lo, hoc_y_hi),
        z=(R - hoc_h / 2.0, R + hoc_h / 2.0),
    )

    # Lo truc tren vach mat hop so: O(truc_d + 1.6)
    r_truc_lo = (n20["truc_d"] + 1.6) / 2.0
    shaft_hole = cyl(r_truc_lo, "y", (y_face - sign * 0.1, y_face + sign * (MM_CAP + 0.1)), at=(0.0, R))

    # 2 lo M1.6 vit N20 tren vach mat hop so, cach tam truc ±vit_cach_tam theo X
    m16_holes = []
    for dx in (-n20["vit_cach_tam"], n20["vit_cach_tam"]):
        m16_holes.append(
            cyl(m16 / 2.0, "y", (y_face - sign * 0.1, y_face + sign * (MM_CAP + 0.1)), at=(dx, R))
        )

    # 2 lo M3 tu ren tren mat tren (vit tu tren xuong, sau 8)
    m3_depth = 8.0
    m3_holes_top = []
    # Dat 2 lo trong vach trong (pham vi vat lieu dam bao) tai x=±3.5
    # Vach trong tai y_mount_inner, day MM_WALL=2mm; khoan tu Z_BASE_BOT xuong 8
    y_m3_1 = y_mount_inner + sign * (MM_WALL / 2.0)  # tam vach trong
    y_m3_2 = y_m3_1  # cung y, khac x (x=+3.5 va x=-3.5)
    mm_screw_dx = 3.5  # cach tam 3.5 mm theo X

    for x_off in (-mm_screw_dx, mm_screw_dx):
        m3_holes_top.append(
            cyl(m3r / 2.0, "z", (Z_BASE_BOT - m3_depth, Z_BASE_BOT + 0.1), at=(x_off, y_m3_1))
        )

    # Gop cac lo, cat 1 lan
    all_cuts = [hoc_motor, shaft_hole] + m16_holes + m3_holes_top
    mount_shape = cut_all(mount_solid, *all_cuts)

    add(f"Motor_mount_{side}", mount_shape, COLOR_PRINT)

# ===========================================================================
# 4. BASE_PLATE
# Tam bo goc (bo_goc_r) day tam_duoi_t, day tai Z_BASE_BOT
# 140 (X: -70..+70) x 120 (Y: -60..+60)
# 4 cot O cot_d cao cot_cao tai (±58, ±48), dinh co lo M3 tu ren sau 8
# Lo M3 xuyen (O m3_xuyen) khop moi lo vit cua Motor_mount, Caster_mount, Line_bracket, Sonar_bracket
# Khe luon day 30 x 10 o giua
# Khay pin: 2 go cao 6 day 2 giu Ref_Battery, tam pin tai x=-12, y=0
# 2 khe day dan 20 x 3 hai ben khay
# ===========================================================================

# Tam chinh co bo goc
base_plate_solid = rrect(
    "z", (Z_BASE_BOT, Z_BASE_TOP),
    half=(70.0, 60.0),
    r=bo_goc_r,
    at=(0.0, 0.0),
)

# 4 cot in lien huong len
COLS = []
for cx, cy in COT_POS:
    col = cyl(cot_d / 2.0, "z", (Z_BASE_TOP, Z_BASE_TOP + cot_cao), at=(cx, cy))
    COLS.append(col)

base_plate_solid = fuse_all(base_plate_solid, *COLS)

# Khay pin: 2 go cao 6 day 2 giu pin
# Pin 2S: bbox = [77, 41, 20], tam tai x=-12, y=0
# Pin nam tren mat Base_plate (Z_BASE_TOP), day pin = Z_BASE_TOP
pin_cx = -12.0
pin_cy = 0.0
pin_bx, pin_by, pin_bz = pin_2s["bbox"]
# Go Y: nam hai ben pin theo Y
go_cao = 6.0
go_day = 2.0
# go trai va phai theo Y (pin rong pin_by theo Y)
go_y_half = pin_by / 2.0 + go_day / 2.0  # tam go
go_len = pin_bx + 4.0  # dai go theo X (rong hon pin 2mm moi ben)
for gy_sign in (-1, 1):
    go_cy = pin_cy + gy_sign * go_y_half
    go_shape = box(
        x=(pin_cx - go_len / 2.0, pin_cx + go_len / 2.0),
        y=(go_cy - go_day / 2.0, go_cy + go_day / 2.0),
        z=(Z_BASE_TOP, Z_BASE_TOP + go_cao),
    )
    base_plate_solid = base_plate_solid.fuse(go_shape)

base_plate_solid = base_plate_solid.removeSplitter()

# --- Cat lo va khe ---
cuts_bp = []

# Khe luon day: 30 x 10 o giua (X=0, Y=0), xuyen qua tam
wire_slot = box(x=(-15.0, 15.0), y=(-5.0, 5.0), z=(Z_BASE_BOT - 0.5, Z_BASE_TOP + 0.5))
cuts_bp.append(wire_slot)

# 2 khe day dan 20 x 3 hai ben khay pin
for khe_sign in (-1, 1):
    khe_cy = pin_cy + khe_sign * (pin_by / 2.0 + go_day + 1.5)
    khe_shape = box(
        x=(pin_cx - 10.0, pin_cx + 10.0),
        y=(khe_cy - 1.5, khe_cy + 1.5),
        z=(Z_BASE_BOT - 0.5, Z_BASE_TOP + 0.5),
    )
    cuts_bp.append(khe_shape)

# Lo M3 dinh cot (tu ren sau 8): xuyen tu dinh cot xuong 8
for cx, cy in COT_POS:
    z_top_col = Z_BASE_TOP + cot_cao
    cuts_bp.append(cyl(m3r / 2.0, "z", (z_top_col - 8.0, z_top_col + 0.1), at=(cx, cy)))

# Lo M3 xuyen Base_plate khop Motor_mount (2 lo moi ben = 4 lo)
# Vi tri khop voi 2 lo tren mat tren Motor_mount: ca 2 trong vach trong, x=±3.5
n20_body_len_val = n20["dai"] - n20["truc_dai"] + n20["dai_encoder_them"]
hoc_len_val = n20_body_len_val
MM_SCREW_DX = 3.5  # cach tam truc X cua motor mount
for sign in (1, -1):
    y_face = sign * GEARBOX_Y_FACE
    y_hoc_inner_val = y_face - sign * hoc_len_val
    y_mount_inner_val = y_hoc_inner_val - sign * MM_WALL
    y_m3_val = y_mount_inner_val + sign * (MM_WALL / 2.0)
    for x_off in (-MM_SCREW_DX, MM_SCREW_DX):
        cuts_bp.append(cyl(m3x / 2.0, "z", (Z_BASE_BOT - 0.1, Z_BASE_TOP + 0.1), at=(x_off, y_m3_val)))

# Lo M3 xuyen cho Caster_mount (2 vit M3 tai x=-55, y=0, offset ±15 theo X)
CASTER_X = -55.0
CASTER_SCREW_DY = 0.0
CASTER_SCREW_DX = 12.0  # khoang cach 2 vit M3 caster theo X (chon phu hop)
for dx in (-CASTER_SCREW_DX, CASTER_SCREW_DX):
    cuts_bp.append(cyl(m3x / 2.0, "z", (Z_BASE_BOT - 0.1, Z_BASE_TOP + 0.1), at=(CASTER_X + dx, 0.0)))

# Lo M3 xuyen cho Line_bracket (2 vit M3 tai x=line.truoc_truc)
LINE_X = line["truoc_truc"]
LINE_SCREW_DY = 15.0  # khoang cach 2 vit M3 line_bracket theo Y
for dy in (-LINE_SCREW_DY, LINE_SCREW_DY):
    cuts_bp.append(cyl(m3x / 2.0, "z", (Z_BASE_BOT - 0.1, Z_BASE_TOP + 0.1), at=(LINE_X, dy)))

# Lo M3 cho Sonar_bracket (2 vit, tai x=vach_x - SB_DE_X/2)
# Sonar nam o mui xe, vach bracket tai X_MAX = 70 - bracket_t (chon bracket_t=3)
BRACKET_T = 3.0
# SONAR_CX: tam sonar theo X (dung de tinh vi tri Ref_Sonar)
SONAR_CX = 70.0 - BRACKET_T - sr04["bbox"][0] / 2.0
SB_DE_X_BASE = 20.0  # chia se hang so voi phan sonar_bracket
SONAR_SCREW_X_BP = 70.0 - BRACKET_T - SB_DE_X_BASE / 2.0  # tam de
SONAR_SCREW_DY = sr04["mat_cach"] / 2.0
for dy in (-SONAR_SCREW_DY, SONAR_SCREW_DY):
    cuts_bp.append(cyl(m3x / 2.0, "z", (Z_BASE_BOT - 0.1, Z_BASE_TOP + 0.1), at=(SONAR_SCREW_X_BP, dy)))

# Cat tat ca 1 lan
base_shape = cut_all(base_plate_solid, *cuts_bp)
add("Base_plate", base_shape, COLOR_PRINT)

# Luu toa do cot dinh de Top_plate dung
COL_TOP_Z = Z_BASE_TOP + cot_cao  # = Z_TOP_BOT

# ===========================================================================
# 5. TOP_PLATE + REF_MEGA
# Tam bo goc day tam_tren_t, day tai COL_TOP_Z
# 140 x 120; 4 lo M3 xuyen trung cot; khe day 30 x 10
# 4 cot do Mega O6 cao 5 tai 4 lo mega.lo_dung
# Ref_Mega: hop mega.bbox, day tai dinh cot do Mega
# ===========================================================================
Z_TOP_B = COL_TOP_Z
Z_TOP_T = Z_TOP_B + tam_tren_t

top_solid = rrect(
    "z", (Z_TOP_B, Z_TOP_T),
    half=(70.0, 60.0),
    r=bo_goc_r,
    at=(0.0, 0.0),
)

# 4 cot do Mega tren mat top_plate: Mega bbox tam tai (0, 0)
# Toa do lo dung = goc hop bao (XMin, YMin) + mega.lo[i]
mega_bx, mega_by, mega_bz = mega["bbox"]
mega_xmin = -mega_bx / 2.0
mega_ymin = -mega_by / 2.0

MEGA_COT_R = 3.0    # ban kinh cot do Mega: O6
MEGA_COT_H = 5.0    # chieu cao cot do Mega

mega_col_positions = []
for i in mega["lo_dung"]:
    lx = mega["lo"][i][0]
    ly = mega["lo"][i][1]
    cx = mega_xmin + lx
    cy = mega_ymin + ly
    mega_col_positions.append((cx, cy))
    mc = cyl(MEGA_COT_R, "z", (Z_TOP_T, Z_TOP_T + MEGA_COT_H), at=(cx, cy))
    top_solid = top_solid.fuse(mc)

top_solid = top_solid.removeSplitter()

# Cat lo top_plate
cuts_tp = []

# Khe day 30 x 10
cuts_tp.append(box(x=(-15.0, 15.0), y=(-5.0, 5.0), z=(Z_TOP_B - 0.1, Z_TOP_T + 0.1)))

# 4 lo M3 xuyen trung cot Base_plate
for cx, cy in COT_POS:
    cuts_tp.append(cyl(m3x / 2.0, "z", (Z_TOP_B - 0.1, Z_TOP_T + 0.1), at=(cx, cy)))

# Lo M3 tu ren tren cot do Mega (sau 7, khong xuyen tam)
for cx, cy in mega_col_positions:
    cuts_tp.append(cyl(m3r / 2.0, "z", (Z_TOP_T + MEGA_COT_H - 7.0, Z_TOP_T + MEGA_COT_H + 0.1), at=(cx, cy)))

top_shape = cut_all(top_solid, *cuts_tp)
add("Top_plate", top_shape, COLOR_PRINT)

# Ref_Mega: hop bbox, day tai dinh cot do Mega
Z_MEGA_BOT = Z_TOP_T + MEGA_COT_H
mega_box = box(
    x=(mega_xmin, mega_xmin + mega_bx),
    y=(mega_ymin, mega_ymin + mega_by),
    z=(Z_MEGA_BOT, Z_MEGA_BOT + mega_bz),
)
add("Ref_Mega", mega_box, COLOR_MEGA)

# ===========================================================================
# 6. CASTER_MOUNT + REF_BALL
# Bi cau O d_bi tai x=-55, y=0, day bi cham z=0
# Caster_mount: tru tu day Base_plate xuong, hoc cau, mieng duoi hep
# Chieu cao tu tinh tu R de bi cham san
# ===========================================================================
d_bi = bi_do["d_bi"]
r_bi = d_bi / 2.0

# Bi tai x=-55, y=0, day bi = z=0 -> tam bi tai z = r_bi
# Caster_mount: tru tu Z_BASE_BOT xuong, can dat bi cham san
# Chieu cao caster = Z_BASE_BOT - r_bi (tu tam bi den day Base_plate)
# Tinh chinh xac: day tru = z=0 (mat san), nhung phai co mat de do
# Thuc te: tru bat dau tu Z_BASE_BOT xuong den (r_bi - r_bi) + khoang gio bi
# Tru cao: Z_BASE_BOT - 0 = Z_BASE_BOT (tru tu base xuong san)
# Nhung phai biet vi tri dai bi -> chieu cao = Z_BASE_BOT - 0 (mat san)
# Tru ngoai Ø = d_bi + 0.4 + 2*MM_WALL (lop nhua xung quanh hoc)
CASTER_WALL = 2.5    # thanh bao quanh hoc bi
r_hoc = (d_bi + 0.4) / 2.0      # ban kinh hoc cau
r_tru_ngoai = r_hoc + CASTER_WALL

# Chieu cao tru: tu Z_BASE_BOT xuong, day tru tai san (z=0)
# nhung can giu bi -> day tru = z = 0, cao = Z_BASE_BOT
# Mieng duoi (Ø 0.85*d_bi) hep, bi ep vao tu duoi len
r_mouth = (0.85 * d_bi) / 2.0

CASTER_HEIGHT = Z_BASE_BOT  # tu san len den day Base_plate
caster_tru = cyl(r_tru_ngoai, "z", (0.0, CASTER_HEIGHT), at=(CASTER_X, 0.0))

# Hoc cau: tam bi tai (CASTER_X, 0, r_bi)
# Cat khoi cau Ø(d_bi + 0.4) tu z = r_bi - r_hoc den r_bi + r_hoc (nhung cat den di vao)
# Thuc te dung Part.makeSphere hoac xap xi bang cyl
# Dung hinh tru xap xi: khoet tru Ø(d_bi+0.4) tu z=0 den z=r_bi+r_hoc
hoc_cau = Part.makeSphere(r_hoc, V(CASTER_X, 0.0, r_bi))

# Mieng duoi: lo Ø(0.85*d_bi) tu z=0 xuong (xuyen mat duoi)
mieng_duoi = cyl(r_mouth, "z", (-0.1, r_bi + 0.1), at=(CASTER_X, 0.0))

# 2 lo M3 xuyen de bắt len Base_plate (khop voi lo da cat o Base_plate)
m3_caster_holes = []
for dx in (-CASTER_SCREW_DX, CASTER_SCREW_DX):
    m3_caster_holes.append(
        cyl(m3r / 2.0, "z", (CASTER_HEIGHT - 8.0, CASTER_HEIGHT + 0.1), at=(CASTER_X + dx, 0.0))
    )

caster_shape = cut_all(caster_tru, hoc_cau, mieng_duoi, *m3_caster_holes)
add("Caster_mount", caster_shape, COLOR_PRINT)

# Ref_Ball: khoi cau tham chieu
ref_ball = Part.makeSphere(r_bi, V(CASTER_X, 0.0, r_bi))
add("Ref_Ball", ref_ball)

# ===========================================================================
# 7. LINE_BRACKET + REF_LINE_ARRAY
# Mang = hop line.pcb, mat duoi cach san line.cao_san, tam tai x=line.truoc_truc, y=0
# Canh dai theo Y
# Line_bracket: chu L bat duoi Base_plate (2 vit M3 tu tren)
# 2 lo M3 xuyen dang ranh doc dai 6 de chinh cao ±3
# ===========================================================================
_lpcb = line["pcb"]  # [75, 13, 1.6]: canh dai (75) theo Y, canh ngan (13) theo X
lpcb_y = _lpcb[0]   # 75 mm: canh dai -> Y
lpcb_x = _lpcb[1]   # 13 mm: canh ngan -> X
lpcb_z = _lpcb[2]   # 1.6 mm: day
line_cx = line["truoc_truc"]
line_cy = 0.0
Z_LINE_BOT = line["cao_san"]   # mat duoi mang cach san
Z_LINE_TOP = Z_LINE_BOT + lpcb_z

# Ref_Line_array: hop, canh dai (75) theo Y, canh ngan (13) theo X
ref_line = box(
    x=(line_cx - lpcb_x / 2.0, line_cx + lpcb_x / 2.0),
    y=(line_cy - lpcb_y / 2.0, line_cy + lpcb_y / 2.0),
    z=(Z_LINE_BOT, Z_LINE_TOP),
)
add("Ref_Line_array", ref_line, COLOR_SENSOR)

# Line_bracket: chu L
# - Phan ngang (de): gan vao day Base_plate, co 2 lo M3 ranh doc
# - Phan dung (chan): xuong den mang, om mang tu hai dau X
LB_T = 2.5        # day vach bracket
LB_CLAMP_T = 2.0  # day om mang (theo X)

# Phan de ngang: tu Base_plate xuong mot doan, tai x=line_cx
# De: hop ngang bat vao Base_plate
lb_de_x = (-lpcb_x / 2.0 - LB_CLAMP_T - 5.0, lpcb_x / 2.0 + LB_CLAMP_T + 5.0)  # rong hon mang
lb_de_y = (-lpcb_y / 2.0 - LB_T - 2.0, lpcb_y / 2.0 + LB_T + 2.0)
lb_de_z = (Z_BASE_BOT - LB_T, Z_BASE_BOT)
# NOTE: spec noi bracket chu L, de bat len Base_plate
# Thuc te bracket L: de ngang phia tren, chan dung phia duoi
# De tai Z_BASE_BOT (ap vao day Base_plate), chan xuong den mang

# Chan dung: xuong tu Z_BASE_BOT den Z_LINE_TOP (tiep xuc mat tren mang)
# Chan om hai dau X cua mang
lb_chan_left = box(
    x=(line_cx - lpcb_x / 2.0 - LB_CLAMP_T, line_cx - lpcb_x / 2.0),
    y=(-lpcb_y / 2.0 - LB_T, lpcb_y / 2.0 + LB_T),
    z=(Z_LINE_TOP, Z_BASE_BOT),
)
lb_chan_right = box(
    x=(line_cx + lpcb_x / 2.0, line_cx + lpcb_x / 2.0 + LB_CLAMP_T),
    y=(-lpcb_y / 2.0 - LB_T, lpcb_y / 2.0 + LB_T),
    z=(Z_LINE_TOP, Z_BASE_BOT),
)

# De ngang: noi 2 chan, dat vao Base_plate
lb_de = box(
    x=(line_cx - lpcb_x / 2.0 - LB_CLAMP_T, line_cx + lpcb_x / 2.0 + LB_CLAMP_T),
    y=(-lpcb_y / 2.0 - LB_T, lpcb_y / 2.0 + LB_T),
    z=(Z_BASE_BOT - LB_T, Z_BASE_BOT),
)

lb_solid = fuse_all(lb_chan_left, lb_chan_right, lb_de)

# Cat lo M3 ranh doc (slot) de chinh cao ±3, dai 6
# Ranh nam tren phan chan, theo chieu Z, dai 6, rong m3x
# Vi tri ranh: 2 ranh tai y = ±LINE_SCREW_DY, x = line_cx
SLOT_LEN = 6.0
SLOT_RAD = m3x / 2.0

lb_cuts = []
# Ranh dang slot Z tai dinh lb_chan (gan Base_plate), de chinh cao +/-3
# Slot xuyen qua phan de va phan tren cua chan, dai 6 mm theo Z
# Vi tri slot: tap trung tai Z_BASE_BOT - LB_T/2 (giua de), dai 6
SLOT_Z_CENTER = Z_BASE_BOT - LB_T / 2.0
for dy in (-LINE_SCREW_DY, LINE_SCREW_DY):
    slot_chan = box(
        x=(line_cx - SLOT_RAD, line_cx + SLOT_RAD),
        y=(dy - SLOT_RAD, dy + SLOT_RAD),
        z=(SLOT_Z_CENTER - SLOT_LEN / 2.0, SLOT_Z_CENTER + SLOT_LEN / 2.0),
    )
    lb_cuts.append(slot_chan)

line_bracket_shape = cut_all(lb_solid, *lb_cuts)
add("Line_bracket", line_bracket_shape, COLOR_PRINT)

# ===========================================================================
# 8. SONAR_BRACKET + REF_SONAR
# HC-SR04 dung dung o mui xe, mat phat huong +X
# Tam cao hon mat Base_plate 15
# Bracket: vach dung co 2 lo Ø(mat_d+0.4) cach nhau mat_cach
# De bat len Base_plate (2 vit M3)
# Khong vuot bao X (max X = 70)
# ===========================================================================
# Sonar bbox [45, 20, 15]: X=45 (chieu truoc-sau), Y=20 (rong), Z=15 (cao)
# Dung dung: mat phat (+X) la mat rong nhat
# Tam sonar tai: x = SONAR_CX (tinh de khong vuot bao X=70)
# z tam sonar: Z_BASE_TOP + 15 (tam cao hon mat Base_plate 15)
Z_SONAR_CX = Z_BASE_TOP + 15.0

# Vach bracket tai x = SONAR_CX + sr04.bbox[0]/2 + BRACKET_T/2
# (vach bat vao phia sau sonar, sonar gan ap vach)
# De bat len Base_plate vach mat sau sonar tai x = SONAR_CX + sr04["bbox"][0]/2
vach_x = 70.0 - BRACKET_T  # vach trong (mat sau sonar), x cua vach

# Sonar: mat truoc tai vach_x - sr04["bbox"][0], mat sau tai vach_x
# Kiem tra: mat truoc >= -70 (khong kha thi, but sonar chi dai 45)
sonar_x_front = vach_x - sr04["bbox"][0]
sonar_x_back = vach_x

# Ref_Sonar: hop sonar
ref_sonar = box(
    x=(sonar_x_front, sonar_x_back),
    y=(-sr04["bbox"][1] / 2.0, sr04["bbox"][1] / 2.0),
    z=(Z_SONAR_CX - sr04["bbox"][2] / 2.0, Z_SONAR_CX + sr04["bbox"][2] / 2.0),
)
add("Ref_Sonar", ref_sonar, COLOR_SONAR)

# Sonar bracket: vach dung tai x = vach_x..vach_x+BRACKET_T, noi lien voi de tren mat Base_plate
SB_DE_T = LB_T         # day phan de
SB_DE_Y = sr04["bbox"][1] + 4.0  # rong de va vach
SB_DE_X = 10.0                   # dai de theo X (lui vao trong 10mm, tranh chong Ref_Driver)

# Vach dung: tu Z_BASE_TOP den Z_SONAR_CX + sr04.bbox[2]/2 + 1
sb_vach_z_lo = Z_BASE_TOP
sb_vach_z_hi = Z_SONAR_CX + sr04["bbox"][2] / 2.0 + 1.0

sb_vach = box(
    x=(vach_x, vach_x + BRACKET_T),
    y=(-SB_DE_Y / 2.0, SB_DE_Y / 2.0),
    z=(sb_vach_z_lo, sb_vach_z_hi),
)

# De ngang TREN mat Base_plate (noi lien vach dung): bat len Base_plate bang vit M3 tu duoi len
sb_de = box(
    x=(vach_x - SB_DE_X, vach_x + BRACKET_T),
    y=(-SB_DE_Y / 2.0, SB_DE_Y / 2.0),
    z=(Z_BASE_TOP, Z_BASE_TOP + SB_DE_T),  # tren mat Base_plate
)

sb_solid = fuse_all(sb_vach, sb_de)

# 2 lo mat sonar tren vach: Ø(mat_d + 0.4), cach nhau mat_cach
r_mat = (sr04["mat_d"] + 0.4) / 2.0
y_mat_1 = -sr04["mat_cach"] / 2.0
y_mat_2 = sr04["mat_cach"] / 2.0

sb_cuts = []
for y_m in (y_mat_1, y_mat_2):
    sb_cuts.append(cyl(r_mat, "x", (vach_x - 0.1, vach_x + BRACKET_T + 0.1), at=(y_m, Z_SONAR_CX)))

# 2 lo M3 xuyen de bat len Base_plate (tu duoi len: screw gap duoi tren len)
# Vi tri vit tai x = vach_x - SB_DE_X/2 (giua phan de)
SONAR_SCREW_X = vach_x - SB_DE_X / 2.0  # x cua vit sonar bracket
for dy in (-SONAR_SCREW_DY, SONAR_SCREW_DY):
    sb_cuts.append(cyl(m3x / 2.0, "z", (Z_BASE_TOP - 0.1, Z_BASE_TOP + SB_DE_T + 0.1), at=(SONAR_SCREW_X, dy)))

sonar_bracket_shape = cut_all(sb_solid, *sb_cuts)
add("Sonar_bracket", sonar_bracket_shape, COLOR_PRINT)

# ===========================================================================
# 9. REF_DRIVER
# Hop driver.bbox nam tren Base_plate phia truoc khay pin, khong cham cot
# ===========================================================================
drv_bx, drv_by, drv_bz = driver["bbox"]
# Phia truoc khay pin (x > pin_cx + pin_bx/2), khong cham cot (cot tai x=±58)
# Va khong cham Sonar_bracket de (x < 47)
# Dat driver tai x canh pin, tren mat Base_plate
drv_x_start = pin_cx + pin_bx / 2.0 + 5.0   # cach pin 5mm
drv_cx = drv_x_start + drv_bx / 2.0
drv_cy = 0.0
drv_z_bot = Z_BASE_TOP

drv_box = box(
    x=(drv_cx - drv_bx / 2.0, drv_cx + drv_bx / 2.0),
    y=(drv_cy - drv_by / 2.0, drv_cy + drv_by / 2.0),
    z=(drv_z_bot, drv_z_bot + drv_bz),
)
add("Ref_Driver", drv_box)

# ===========================================================================
# 10. REF_BATTERY
# Hop pin 2S nam tren Base_plate, tam tai x=-12, y=0
# ===========================================================================
ref_bat = box(
    x=(pin_cx - pin_bx / 2.0, pin_cx + pin_bx / 2.0),
    y=(pin_cy - pin_by / 2.0, pin_cy + pin_by / 2.0),
    z=(Z_BASE_TOP, Z_BASE_TOP + pin_bz),
)
add("Ref_Battery", ref_bat)

# ===========================================================================
# 11. DOC RECOMPUTE & LUU
# ===========================================================================
doc.recompute()

# Backup neu file da ton tai
os.makedirs(os.path.dirname(OUT) if os.path.dirname(OUT) else ".", exist_ok=True)
if os.path.exists(OUT):
    bk_dir = os.path.join(os.path.dirname(OUT) or ".", "backup")
    os.makedirs(bk_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(OUT, os.path.join(bk_dir, "line_bot.%s.FCStd" % ts))

doc.saveAs(OUT)

# In ket qua
in_parts = ["Base_plate", "Top_plate", "Motor_mount_L", "Motor_mount_R",
            "Caster_mount", "Line_bracket", "Sonar_bracket"]
bb_all = App.BoundBox()
for o in doc.Objects:
    if o.isDerivedFrom("Part::Feature") and o.Shape.Solids:
        bb_all.add(o.Shape.BoundBox)

print("LINEBOT OK %d %.1fx%.1fx%.1f" % (
    len(in_parts),
    bb_all.XLength, bb_all.YLength, bb_all.ZLength,
))
