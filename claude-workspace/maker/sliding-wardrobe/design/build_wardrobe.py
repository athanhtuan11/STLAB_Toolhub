"""Tu ao am tuong cua lua 4 canh - khung sat chiu luc + canh lam song nguyen cay (Blender, bpy).

Chay (tu design/):  blender -b -P build_wardrobe.py -- --out renders
Doi kich thuoc: sua P (W sau khi do), chay lai; roi `python draw_plans.py`.
Xuat: wardrobe.blend, renders/*.png, parts.json.
Don vi trong code: mm (Blender: m). Toa do: x trai->phai (tuong trai x=0), y truoc->sau (tuong sau y=D), z tu san.
"""
import bpy, json, math, os, sys

P = dict(
    W=3000,            # tuong-toi-tuong (TODO do thuc te, 3 diem lay so nho nhat)
    D=800,             # sau tu, tuong sau tai y=D
    # lam song ngoai troi (Tuan 2026-11-09): 220 x 2900 x 26
    lam_w=220, lam_L=2900, lam_t=26,
    lam_waves=4,       # TODO so song that cua thanh mua
    door_n=4, ov_min=40,        # chong mi toi thieu
    door_bars=[3, 4, 4, 3],     # so thanh lam moi canh (ngoai 3, giua 4) -> mo khoang deu hon
    # canh tu han (Tuan 2026-11-09): vien = hop 20x40x1.2 dat nam (mat 20 lo ra, sau 40), lam lot trong vien
    door_frame=(20, 40, 1.2),   # (mat lo, sau = day canh, day thanh)
    rail_back=(13, 26, 1.0),    # thanh giang sau lam hop 13x26 (do lam, bat vit tu sau)
    n_rail_back=4,
    lam_gap_side=1, lam_gap_end=1.5,    # khe quanh lam trong vien (gian no WPC, TODO theo hang)
    # ---- bo ray lua: banh do duoi + banh dan huong tren (TODO thay so theo bo ray mua)
    trk_base=5, ridge_h=8, ridge_w=6,   # ray duoi nhom: de day 5, go dan 6x8 moi lan
    wheel_d=40, wheel_t=12,             # banh do duoi (ranh V/U, o bi), 2 banh/canh
    wheel_in=70,                        # tim banh cach mep canh
    lift_off=8,                         # nang canh bao nhieu thi banh duoi thoat go (= ridge_h, an toan)
    door_gap_bot=7,                     # mep duoi canh cach dinh go ray
    roller_d=25, roller_h=25,           # banh dan huong tren truc dung, 2 banh/canh
    roller_in=60,
    ch_gap=5,                           # mep tren canh -> mieng mang tren
    ch_depth=45, ch_wall=2,             # mang ray tren chu U (long sau 45)
    aj_gap=5,                           # khe con lai tren khoa chong nhay sau khi van len
    # ---- khoa + chot (Tuan 2026-11-09: chot bi + khoa chong mi) – TODO so theo hang mua
    lock_d=20,                          # mat khoa an (push lock) lo tren lam canh truoc
    plunger_d=8, plunger_travel=14,     # chot khoa bat ra sau
    plunger_engage=5,                   # an vao vien canh sau toi thieu
    lock_rail=1,                        # khoa bat vao giang sau thu may (0-based) ~ tam tay
    ball_d=6, ball_hole_d=5,            # chot bi lo xo tren khoa chong nhay, lo tren lung mang
    DZ=120,                     # vung 2 ray phia truoc
    tube=(40, 40, 1.4),         # khung chiu luc hop sat 40x40x1.4 son tinh dien
    header=(40, 80, 1.4),       # dam dau cua (do ray tren) 40x80
    z_shelf=2300,               # mat ke hop noc
    board_t=17,                 # van ke hop noc (MFC/plywood)
    rod_d=27,
    rod_t=1.0,                  # day ong inox (TODO theo hang mua, nen >= 1.0)
    rod_load_kg=40,             # tai treo 1 ong (Tuan treo do kha nang - gia dinh, TODO)
    rod_sigma_max=100,          # MPa cho phep (inox 304 chay ~205 MPa -> he so an toan ~2)
    rod_defl_max=3,             # mm vong cho phep giua nhip
)
p = P
W, D = p["W"], p["D"]
LW, LT = p["lam_w"], p["lam_t"]
TB = p["tube"][0]
FW, FDP = p["door_frame"][0], p["door_frame"][1]
KB = p["door_bars"]
k = max(KB)
DWS = [kb * LW + 2 * p["lam_gap_side"] + 2 * FW for kb in KB]   # rong tung canh = thanh nguyen + vien
OV = (sum(DWS) - W) / (p["door_n"] - 1)                        # chong mi thuc te
DX0 = [sum(DWS[:i]) - i * OV for i in range(p["door_n"])]       # mep trai tung canh
DW = max(DWS)
OPEN = [DWS[0] - OV] + [DWS[i] - 2 * OV for i in range(1, p["door_n"] - 1)] + [DWS[-1] - OV]
DH = p["lam_L"]
z_ridge = p["trk_base"] + p["ridge_h"]                # dinh go ray duoi
dz0 = z_ridge + p["door_gap_bot"]                     # mep duoi canh
DHD = DH + 2 * p["lam_gap_end"] + 2 * FW              # cao canh (lam + vien tren/duoi)
dz1 = dz0 + DHD                                       # mep tren canh
z_ch0 = dz1 + p["ch_gap"]                             # mieng mang tren
z_ch1 = z_ch0 + p["ch_depth"]                         # mat duoi lung mang
H_TOP = z_ch1 + p["ch_wall"] + p["header"][0]         # dinh dam dau cua
# lan ray = tam chieu day canh
FD = FDP
LANES = [10 + FDP / 2, 10 + FDP + 8 + FDP / 2]
roller_top = dz1 + p["roller_h"]
CHECK = dict(
    lap_dat=(roller_top + p["lift_off"] + 2 <= z_ch1, "nang canh lift_off+2 ma banh tren chua cham lung mang"),
    an_khop=(roller_top - z_ch0 >= p["lift_off"] + 5, "banh tren an vao mang >= lift_off+5 (khong tuot khi nang)"),
    chong_nhay=(p["aj_gap"] < p["lift_off"], "khe tren khoa chong nhay < do nang thoat go"),
    chong_mi=(p["ov_min"] <= (sum(p["door_bars"]) * p["lam_w"] + p["door_n"] * (2 * p["lam_gap_side"] + 2 * p["door_frame"][0]) - p["W"]) / (p["door_n"] - 1) <= 150,
              "chong mi trong 40..150 (ngoai khoang -> doi door_bars)"),
    vung_ray=(LANES[1] + FD / 2 + 5 <= p["DZ"], "canh trong nam gon trong vung ray DZ"),
)
# ---- vi tri khoa chong mi: giua vien canh SAU tai cho chong mi (canh truoc o ray ngoai)
GAP_DOOR = LANES[1] - LANES[0] - FDP                 # khe giua 2 canh (theo chieu sau)
LOCKS = []
for i in range(p["door_n"] - 1):
    fi, bi = (i, i + 1) if i % 2 == 0 else (i + 1, i)   # canh truoc (ray ngoai, chi so chan) / canh sau
    xv = DX0[bi] + FW / 2 if bi > fi else DX0[bi] + DWS[bi] - FW / 2   # tam vien canh sau phia chong mi
    LOCKS.append(dict(front=fi, back=bi, x=xv))
zl0_ = dz0 + FW + p["lam_gap_end"]
Z_LOCK = zl0_ + (p["lock_rail"] + 0.5) * DH / p["n_rail_back"]
def _in_lam(L):
    x0f = DX0[L["front"]] + FW + p["lam_gap_side"]
    return x0f + p["lock_d"] / 2 + 3 <= L["x"] <= x0f + KB[L["front"]] * LW - p["lock_d"] / 2 - 3
CHECK["khoa_tren_lam"] = (all(_in_lam(L) for L in LOCKS), "lo khoa nam tron tren lam canh truoc (khong cat vien)")
CHECK["khoa_an_vien"] = (p["plunger_travel"] >= GAP_DOOR + p["plunger_engage"],
                         "chot khoa qua khe giua 2 canh + an vao vien canh sau >= engage")
CHECK["chot_bi"] = (p["ball_d"] / 2 > p["aj_gap"] / 2 and p["ball_hole_d"] < p["ball_d"],
                    "bi lo xo chạm lung mang, lo nho hon bi (bi khong lot)")
z_rail_top = H_TOP - TB
y0i, y1i = p["DZ"], D
y_mid = (y0i + y1i) / 2
# vi tri cac khung dung: 2 tuong + 3 cho chong mi
x_lines = [TB / 2] + [DX0[i + 1] + OV / 2 for i in range(p["door_n"] - 1)] + [W - TB / 2]

BAYS = [   # Tuan 2026-11-09: chi treo ong tron Ø27, ca 4 khoang 2 tang 2050/1030
    dict(name="K1 treo 2 tang", rods=[2050, 1030]),
    dict(name="K2 treo 2 tang", rods=[2050, 1030]),
    dict(name="K3 treo 2 tang", rods=[2050, 1030]),
    dict(name="K4 treo 2 tang", rods=[2050, 1030]),
]

# ---- kiem ong treo: dam don gian tai phan bo deu
def _rod_check():
    Do, t = p["rod_d"], p["rod_t"]
    Di = Do - 2 * t
    I = math.pi / 64 * (Do ** 4 - Di ** 4)                 # mm4
    Z = I / (Do / 2)                                      # mm3
    E = 193000                                            # MPa inox 304
    span = max(x_lines[b + 1] - x_lines[b] for b in range(len(x_lines) - 1)) - TB
    w = p["rod_load_kg"] * 9.81 / span                    # N/mm
    Mmax = w * span ** 2 / 8
    sig = Mmax / Z
    defl = 5 * w * span ** 4 / (384 * E * I)
    return dict(span=span, sigma=sig, defl=defl)
ROD = _rod_check()
CHECK["ong_ben"] = (ROD["sigma"] <= p["rod_sigma_max"],
                    f"ong O{p['rod_d']}x{p['rod_t']} nhip {ROD['span']:.0f} tai {p['rod_load_kg']} kg: ung suat {ROD['sigma']:.0f} MPa <= {p['rod_sigma_max']}")
CHECK["ong_vong"] = (ROD["defl"] <= p["rod_defl_max"], f"vong giua nhip {ROD['defl']:.1f} mm <= {p['rod_defl_max']}")

M = 0.001
parts = []


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def mat(name, hexc, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*srgb(hexc), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*srgb(hexc), 1)
    return m


MAT = {}
COLS = {}


def col(name):
    if name not in COLS:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COLS[name] = c
    return COLS[name]


def box(name, group, x0, x1, y0, y1, z0, z1, m, kind=None, spec=None):
    xs, ys, zs = sorted((x0, x1)), sorted((y0, y1)), sorted((z0, z1))
    v = [(xs[i] * M, ys[j] * M, zs[kk] * M) for i in (0, 1) for j in (0, 1) for kk in (0, 1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(MAT[m])
    o = bpy.data.objects.new(name, me)
    col(group).objects.link(o)
    d = sorted([xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0]], reverse=True)
    parts.append(dict(name=name, group=group, mat=m, kind=kind, spec=spec,
                      bbox=[xs[0], xs[1], ys[0], ys[1], zs[0], zs[1]],
                      L=round(d[0], 1), Wd=round(d[1], 1), Th=round(d[2], 1)))
    return o


def cyl(name, group, r, length, loc, rot, m, array=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r * M, depth=length * M)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = rot
    o.location = [v * M for v in loc]
    o.data.materials.append(MAT[m])
    for c in o.users_collection:
        c.objects.unlink(o)
    col(group).objects.link(o)
    if array:
        a = o.modifiers.new("Array", "ARRAY")
        a.use_relative_offset, a.use_constant_offset = False, True
        a.constant_offset_displace = [v * M for v in array[0]]
        a.count = array[1]
    return o


def steel(name, axis, a0, a1, c1, c2, prof="40x40"):
    """Hop sat theo truc axis tu a0->a1; c1,c2 la tam tiet dien theo 2 truc con lai."""
    w, h = (40, 40) if prof == "40x40" else (80, 40) if prof == "40x80" else (40, 20)
    if axis == "x":
        return box(name, "Khung sat", a0, a1, c1 - w / 2, c1 + w / 2, c2 - h / 2, c2 + h / 2, "steel", "steel", prof)
    if axis == "y":
        return box(name, "Khung sat", c1 - w / 2, c1 + w / 2, a0, a1, c2 - h / 2, c2 + h / 2, "steel", "steel", prof)
    return box(name, "Khung sat", c1 - w / 2, c1 + w / 2, c2 - h / 2, c2 + h / 2, a0, a1, "steel", "steel", prof)


def build():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    MAT.update(
        steel=mat("Sat son tinh dien den", "#2B2D30", 0.45, 0.6),
        lam=mat("Lam song go nau", "#7A5538", 0.55),
        board=mat("Van ke", "#D9C7A6", 0.6),
        rod=mat("Inox", "#DADDE0", 0.15, 1.0),
        alu=mat("Ray nhom", "#B9BEC3", 0.3, 1.0),
        nylon=mat("Banh nylon", "#F2F2EE", 0.35),
        rubber=mat("Cao su", "#C0392B", 0.7),
        dark=mat("Lo khoan", "#111111", 0.8),
        wall=mat("Tuong", "#E9E6E0", 0.9),
        floor=mat("San", "#CFC8BC", 0.8),
    )
    zs = p["z_shelf"]
    # ---- khung dung tai moi duong (2 tuong + 3 cho chong mi)
    for i, xl in enumerate(x_lines):
        n = f"KD{i}"
        # khung chu nhat kin: cot truoc + cot sau suot san -> dinh (do thang ngang ke truoc/sau xuong san)
        steel(f"{n}-cot-truoc", "z", 4, z_rail_top, xl, y0i + TB / 2)
        steel(f"{n}-cot-sau", "z", 4, z_rail_top, xl, y1i - TB / 2)
        steel(f"{n}-cot-giua", "z", 4, zs - TB, xl, y_mid)                         # cot giua (han tai do ong treo)
        steel(f"{n}-dam-ke", "y", y0i + TB, y1i - TB, xl, zs - TB / 2)             # dam ngang do ke
        steel(f"{n}-dam-dinh", "y", y0i + TB, y1i - TB, xl, H_TOP - TB / 2)
        for nm_, yy in (("truoc", y0i + TB / 2), ("giua", y_mid), ("sau", y1i - TB / 2)):   # ban de chan cot
            box(f"{n}-de-cot-{nm_}", "Khung sat", xl - 30, xl + 30, yy - 30, yy + 30, 0, 4, "steel", "plate", "60x60x4")
    # ---- thanh doc chieu ngang (tuong -> tuong)
    for nm, yc, zc in (("ke-truoc", y0i + TB / 2, zs - TB / 2), ("ke-sau", y1i - TB / 2, zs - TB / 2),
                       ("dinh-truoc", y0i + TB / 2, H_TOP - TB / 2), ("dinh-sau", y1i - TB / 2, H_TOP - TB / 2)):
        steel(f"Ngang-{nm}", "x", 0, W, yc, zc)
    steel("Dam-dau-cua", "x", 0, W, (10 + y0i - 10) / 2, H_TOP - TB / 2, "40x80")
    # ---- ke hop noc (van) theo khoang
    for b in range(4):
        xa, xb = x_lines[b] + (TB / 2 if b == 0 else 0), x_lines[b + 1] - (TB / 2 if b == 3 else 0)
        box(f"K{b + 1}-van-ke-noc", "Van", xa, xb, y0i, y1i, zs, zs + p["board_t"], "board", "board")
    # ---- ong treo Ø27 giua cac cot giua
    for b, spec in enumerate(BAYS):
        xa, xb = x_lines[b] + TB / 2, x_lines[b + 1] - TB / 2
        for zr in spec["rods"]:
            cyl(f"K{b + 1}-ong-{zr}", "Ong treo", p["rod_d"] / 2, xb - xa, ((xa + xb) / 2, y_mid, zr),
                (0, math.pi / 2, 0), "rod")
            parts.append(dict(name=f"K{b + 1}-ong-{zr}", group="Ong treo", mat="rod", kind="rod",
                              spec=f"Ø{p['rod_d']}", bbox=[xa, xb, y_mid - 13.5, y_mid + 13.5, zr - 13.5, zr + 13.5],
                              L=round(xb - xa - 2, 1), Wd=p["rod_d"], Th=p["rod_d"]))
    # ---- ray duoi (nhom, bat vit xuong san): de + 2 go
    box("Ray-duoi-de", "Ray", 0, W, 5, y0i - 5, 0, p["trk_base"], "alu", "track", "ray duoi doi")
    for li, yc in enumerate(LANES):
        box(f"Ray-duoi-go{li + 1}", "Ray", 0, W, yc - p["ridge_w"] / 2, yc + p["ridge_w"] / 2,
            p["trk_base"], z_ridge, "alu")
    # ---- ray tren: 2 mang U (long = banh tren + 2) treo duoi dam dau cua
    box("Ray-tren-lung", "Ray", 0, W, 5, y0i - 5, z_ch1, z_ch1 + p["ch_wall"], "alu", "track", "ray tren doi (2 mang U)")
    cw = p["roller_d"] + 2
    for li, yc in enumerate(LANES):
        for sgn in (-1, 1):
            yw = yc + sgn * cw / 2
            box(f"Ray-tren-thanh{li + 1}{'ab'[sgn > 0]}", "Ray", 0, W, min(yw, yw + sgn * p["ch_wall"]),
                max(yw, yw + sgn * p["ch_wall"]), z_ch0, z_ch1, "alu")
        st = p["roller_in"] - p["roller_d"] / 2 - 1     # mat chan: canh dung sat tuong (mep canh x=0 / x=W)
        for xa, xb in ((0, st), (W - st, W)):     # chan cuoi hanh trinh cao su
            box(f"Chan-cuoi-L{li + 1}-{int(xa)}", "Ray", xa, xb, yc - cw / 2, yc + cw / 2, z_ch0 + 5, z_ch1,
                "rubber", "stop", "chan cuoi cao su")
    # lo chot bi tren lung mang tai vi tri dong cua tung canh
    for i in range(p["door_n"]):
        yc = LANES[i % 2]
        cyl(f"Lo-chot-bi-C{i + 1}", "Ray", p["ball_hole_d"] / 2, 1, (DX0[i] + DWS[i] / 2, yc, z_ch1 - 0.4), (0, 0, 0), "dark")
    # ---- canh: vien hop 20x40 (mat 20) + giang sau 13x26 + k thanh lam nguyen cay lot trong vien
    r = 13
    pitch = LW / p["lam_waves"]
    rb_d, rb_w = p["rail_back"][0], p["rail_back"][1]
    for i in range(p["door_n"]):
        front = i % 2 == 0
        yc = LANES[0] if front else LANES[1]
        yf0, yf1 = yc - FDP / 2, yc + FDP / 2          # mat truoc / sau canh
        yl = yf1 - rb_d - LT                            # mat truoc lam (lui sau vien ~1)
        x0, DW = DX0[i], DWS[i]
        k = KB[i]
        g = f"Canh {i + 1}"
        pre = f"C{i + 1}-"
        box(pre + "vien-dung-trai", g, x0, x0 + FW, yf0, yf1, dz0, dz1, "steel", "dframe", "20x40")
        box(pre + "vien-dung-phai", g, x0 + DW - FW, x0 + DW, yf0, yf1, dz0, dz1, "steel", "dframe", "20x40")
        box(pre + "vien-ngang-duoi", g, x0 + FW, x0 + DW - FW, yf0, yf1, dz0, dz0 + FW, "steel", "dframe", "20x40")
        box(pre + "vien-ngang-tren", g, x0 + FW, x0 + DW - FW, yf0, yf1, dz1 - FW, dz1, "steel", "dframe", "20x40")
        zl0 = dz0 + FW + p["lam_gap_end"]
        for n in range(p["n_rail_back"]):
            zz = zl0 + (n + 0.5) * DH / p["n_rail_back"]
            box(pre + f"giang-sau-{n + 1}", g, x0 + FW, x0 + DW - FW, yf1 - rb_d, yf1, zz - rb_w / 2, zz + rb_w / 2,
                "steel", "rback", "13x26")
        for j in range(k):
            bx = x0 + FW + p["lam_gap_side"] + j * LW
            box(pre + f"lam{j + 1}", g, bx + 0.5, bx + LW - 0.5, yl + r, yl + LT, zl0, zl0 + DH, "lam", "lam", f"{LW}x{LT}")
            cyl(pre + f"lam{j + 1}-song", g, r, DH, (bx + pitch / 2, yl + r, zl0 + DH / 2), (0, 0, 0), "lam",
                array=((pitch, 0, 0), p["lam_waves"]))
        zw = z_ridge - 3 + p["wheel_d"] / 2          # go an vao ranh banh 3
        for side, xw, xr in (("trai", x0 + p["wheel_in"], x0 + p["roller_in"]),
                             ("phai", x0 + DW - p["wheel_in"], x0 + DW - p["roller_in"])):
            box(pre + f"hop-banh-{side}", g, xw - 40, xw + 40, yc - 9, yc + 9, dz0 + 2, dz0 + FW - 2, "rubber", "hw", "hop banh duoi (khoet ong vien duoi)")
            cyl(pre + f"banh-duoi-{side}", g, p["wheel_d"] / 2, p["wheel_t"], (xw, yc, zw), (math.pi / 2, 0, 0), "nylon")
            box(pre + f"de-banh-tren-{side}", g, xr - 25, xr + 25, yc - 9, yc + 9, dz1, dz1 + 4, "steel", "hw", "de banh tren")
            cyl(pre + f"banh-tren-{side}", g, p["roller_d"] / 2, p["roller_h"] - 4,
                (xr, yc, dz1 + 4 + (p["roller_h"] - 4) / 2), (0, 0, 0), "nylon")
        box(pre + "khoa-chong-nhay", g, x0 + DW / 2 - 20, x0 + DW / 2 + 20, yc - 10, yc + 10,
            dz1, z_ch1 - p["aj_gap"], "rubber", "hw", "khoa chong nhay")
        bpy.ops.mesh.primitive_uv_sphere_add(radius=p["ball_d"] / 2 * M, location=(
            (x0 + DW / 2) * M, yc * M, (z_ch1 - p["aj_gap"]) * M))
        bo = bpy.context.active_object
        bo.name = pre + "chot-bi"
        bo.data.materials.append(MAT["rod"])
        for c_ in bo.users_collection:
            c_.objects.unlink(bo)
        col(g).objects.link(bo)
        parts.append(dict(name=pre + "chot-bi", group=g, mat="rod", kind="hw", spec="chot bi lo xo",
                          bbox=[0] * 6, L=0, Wd=0, Th=0))
        for L in LOCKS:
            if L["front"] == i:      # khoa an tren canh truoc: mat khoa tren lam + than bat giang sau
                cyl(pre + f"khoa-an-{int(L['x'])}", g, p["lock_d"] / 2, LT + 4,
                    (L["x"], yl + LT / 2 - 2, Z_LOCK), (math.pi / 2, 0, 0), "rod")
                box(pre + f"than-khoa-{int(L['x'])}", g, L["x"] - 14, L["x"] + 14, yl + LT, yf1, Z_LOCK - 25, Z_LOCK + 25,
                    "steel", "hw", "khoa an (push lock) dong chia")
                cyl(pre + f"chot-khoa-{int(L['x'])}", g, p["plunger_d"] / 2, GAP_DOOR + p["plunger_engage"],
                    (L["x"], yf1 + (GAP_DOOR + p["plunger_engage"]) / 2, Z_LOCK), (math.pi / 2, 0, 0), "rod")
            if L["back"] == i:       # lo bat chot tren vien canh sau
                cyl(pre + f"lo-bat-chot-{int(L['x'])}", g, (p["plunger_d"] + 2) / 2, 1,
                    (L["x"], yf0 - 0.4, Z_LOCK), (math.pi / 2, 0, 0), "dark")
    return dict(P=P, LOCKS=LOCKS, Z_LOCK=Z_LOCK, GAP_DOOR=GAP_DOOR, DW=max(DWS), DWS=DWS, DX0=DX0, OPEN=OPEN, KB=KB, OV=OV, k=max(KB), DH=DH, DHD=DHD, FW=FW, FDP=FDP, H_TOP=H_TOP, LANES=LANES, dz=[dz0, dz1], z_ridge=z_ridge, z_ch=[z_ch0, z_ch1], CHECK={kk: [bool(v[0]), v[1]] for kk, v in CHECK.items()}, x_lines=x_lines, BAYS=BAYS, y_mid=y_mid)


def env():
    box("San", "Moi truong", -1200, W + 1200, -3000, D + 20, -10, 0, "floor", "env")
    box("Tuong-sau", "Moi truong", -200, W + 200, D, D + 100, 0, 3300, "wall", "env")
    box("Tuong-phai", "Moi truong", W, W + 100, -300, D, 0, 3300, "wall", "env")
    box("Tuong-trai", "Tuong trai", -100, 0, -300, D, 0, 3300, "wall", "env")


def setup_render():
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1400
    w = bpy.data.worlds.new("W")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*srgb("#ECEFF1"), 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    sc.world = w
    ld = bpy.data.lights.new("Sun", "SUN")
    ld.energy = 3.0
    ld.angle = 0.3
    s = bpy.data.objects.new("Sun", ld)
    s.rotation_euler = (math.radians(55), math.radians(10), math.radians(-30))
    sc.collection.objects.link(s)


def cam(name, loc, rot, ortho=None, lens=35):
    cd = bpy.data.cameras.new(name)
    cd.clip_end = 100
    if ortho:
        cd.type, cd.ortho_scale = "ORTHO", ortho
    else:
        cd.lens = lens
    o = bpy.data.objects.new(name, cd)
    o.location = [v * M for v in loc]
    o.rotation_euler = [math.radians(a) for a in rot]
    bpy.context.scene.collection.objects.link(o)
    return o


def shot(c, path, hide=(), move=None):
    sc = bpy.context.scene
    sc.camera = c
    for g in COLS:
        COLS[g].hide_render = g in hide
    saved = {}
    for pre, dx in (move or {}).items():
        for o in bpy.data.objects:
            if o.name.startswith(pre):
                saved[o.name] = o.location.x
                o.location.x += dx * M
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for nm, x in saved.items():
        bpy.data.objects[nm].location.x = x


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, argv[argv.index("--out") + 1] if "--out" in argv else "renders")
    os.makedirs(out, exist_ok=True)
    meta = build()
    env()
    setup_render()
    doors = [g for g in COLS if g.startswith("Canh")]
    front = cam("Cam-truoc", (W / 2, -7000, H_TOP / 2), (90, 0, 0), ortho=max(W, H_TOP) * 1.3 * M)
    iso = cam("Cam-iso", (-350, -2700, 1900), (82, 0, -24), lens=18)
    sh = DWS[0] - OV
    shot(front, os.path.join(out, "01-mat-truoc-dong-cua.png"))
    shot(front, os.path.join(out, "02-mat-truoc-khung-sat.png"), hide=doors + ["Ray"])
    shot(iso, os.path.join(out, "03-iso-mo-khoang-1-4.png"), hide=["Tuong trai"], move={"C1-": DWS[1] - OV, "C4-": -(DWS[2] - OV)})
    shot(iso, os.path.join(out, "04-iso-khong-cua.png"), hide=doors + ["Tuong trai"])
    shot(iso, os.path.join(out, "05-iso-mo-khoang-2-3.png"), hide=["Tuong trai"], move={"C2-": -(DWS[0] - OV), "C3-": DWS[3] - OV})
    inside = ["Tuong trai", "Khung sat", "Ong treo", "Van", "Moi truong"]
    cb = cam("Cam-ray-duoi", (W - 420, 520, 230), (68, 0, 205), lens=40)
    shot(cb, os.path.join(out, "06-chi-tiet-ray-duoi.png"), hide=inside)
    ct = cam("Cam-ray-tren", (W - 420, 520, H_TOP - 230), (112, 0, 205), lens=40)
    shot(ct, os.path.join(out, "07-chi-tiet-ray-tren.png"), hide=inside)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(here, "wardrobe.blend"))
    json.dump(dict(meta=meta, parts=parts), open(os.path.join(here, "parts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for kk, (ok, why) in CHECK.items():
        print(("PASS " if ok else "FAIL ") + kk + ": " + why)
    print(f"BUILD OK parts={len(parts)} bars={KB} DWS={DWS} OV={OV:.1f} OPEN={[round(o) for o in OPEN]} H_TOP={H_TOP:.0f}")


main()
