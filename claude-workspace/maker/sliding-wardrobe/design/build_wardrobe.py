"""Tu ao am tuong cua lua 2 canh - khung sat chiu luc + canh lam song nguyen cay (Blender, bpy).

Tuan 2026-11-11: chi muon 2 canh; co ray hop 40x40; khong tim duoc ray duoi, chi U de mua (U chan 40x40), canh nang
-> CHIU TAI O DUOI: 2 thanh U chan 40x40 nam ngua tren san, moi canh 2 cum banh (2 banh 608 boc POM / cum) lan trong long U.
Ray hop 40x40 tren + xe treo CHI GIU CANH DUNG, khong chiu tai; xe treo kin trong ray -> canh khong nhac du de banh thoat U.
Ban treo + dan huong giua: backup/2026-11-11-truoc-ray-u-duoi/. Ban 4 canh: backup/2026-11-11-truoc-2-canh-treo/.

Chay (tu design/):  blender -b -P build_wardrobe.py -- --out renders
Doi kich thuoc: sua P (W sau khi do), chay lai.
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
    lam_kg=10.0,       # TODO CAN 1 THANH THAT. Uoc WPC rong ~8-12 kg/thanh 2,9 m -> chi de tinh tai
    door_n=2, ov_min=40, ov_max=200,   # chong mi cho phep
    door_bars=[7, 7],           # Tuan 2026-11-11: 2 canh, moi canh 7 thanh (14 thanh nguyen cay nhu cu)
    # canh tu han: vien hop 20x40x1.2 dat nam (mat 20 lo ra, sau 40), lam lot trong vien
    door_frame=(20, 40, 1.2),
    rail_back=(13, 26, 1.0),    # thanh giang sau lam hop 13x26
    n_rail_back=4,
    lam_gap_side=1, lam_gap_end=1.5,
    # ---- ray DUOI chiu tai (Tuan 2026-11-11): U chan 40x40 nam ngua, bat vit dau bang xuong san
    U=(40, 40, 2.5),            # (rong = day canh, cao canh, day ton) TODO do U mua (day 2-3)
    wheel_d=32, wheel_w=12,     # banh = bac dan 608 boc POM (TODO theo hang mua)
    wheel_kg=None,              # TODO tai 1 banh cua hang mua -> script so voi tai can
    bogie_in=110,               # tam cum banh cach mep canh
    bogie_pitch=60,             # 2 banh / cum, cach nhau
    bogie_w=30,                 # be rong cang banh (lot long U, khe ~2,5 moi ben = do lac chan canh)
    u_gap=6,                    # day vien duoi canh -> mieng U
    # ---- ray TREN chi giu dung: ray hop 40x40 (Tuan co san) + xe treo khong chiu tai
    track=(40, 40),             # ray hop (rong y, cao z)
    track_wall=2,               # day vach ray (TODO do)
    track_slot=14,              # khe day ray cho bulong di qua (TODO do)
    hanger_gap=25,              # mep tren canh -> day ray (bat + bulong chinh, TODO theo xe treo)
    trolley_in=110,             # tam xe treo cach mep canh
    trolley_L=90, trolley_h=28, # than xe treo trong ray
    trolley_play=3,             # chinh bulong de banh xe treo ho tren mep ray 3 -> xe treo khong do tai
    # ---- khoa + tay nam
    lock_d=20, plunger_d=8, plunger_travel=14, plunger_engage=5, lock_rail=1,
    handle_w=30, handle_h=200, handle_z=950,   # tam khe tu san (TODO chinh theo nguoi dung; cach giang sau >= 30)
    handle_lam=[2, 6],          # C1 thanh 2, C2 thanh 6 -> doi xung (351 tu moi tuong), C2 lua het van keo ve duoc
    handle_finger=15,
    DZ=120,                     # vung 2 ray phia truoc
    tube=(40, 40, 1.4),         # khung chiu luc hop sat 40x40x1.4
    header=(40, 40, 1.4),       # dam do ray tren: hop 40x40, 1 dam / 1 ray (khong chiu tai canh - chi giu dung)
    z_shelf=2300, board_t=17,
    rod_d=27, rod_t=1.0, rod_load_kg=40, rod_sigma_max=100, rod_defl_max=3,
)
p = P
W, D = p["W"], p["D"]
LW, LT = p["lam_w"], p["lam_t"]
TB = p["tube"][0]
FW, FDP = p["door_frame"][0], p["door_frame"][1]
KB = p["door_bars"]
k = max(KB)
DWS = [kb * LW + 2 * p["lam_gap_side"] + 2 * FW for kb in KB]
OV = (sum(DWS) - W) / (p["door_n"] - 1)
DX0 = [sum(DWS[:i]) - i * OV for i in range(p["door_n"])]
DW = max(DWS)


def _travel(i):
    """Hanh trinh trai/phai toi da cua canh i: cham canh cung ray hoac tuong (chan cuoi)."""
    j_l, j_r = i - 2, i + 2
    left_lim = DX0[j_l] + DWS[j_l] if j_l >= 0 else 0
    right_lim = DX0[j_r] if j_r < p["door_n"] else W
    return DX0[i] - left_lim, right_lim - (DX0[i] + DWS[i])


TRAVEL = [_travel(i) for i in range(p["door_n"])]
OPEN = [TRAVEL[0][1]] + [TRAVEL[-1][0]]          # lua 1 canh het co -> khoang mo
DH = p["lam_L"]
DHD = DH + 2 * p["lam_gap_end"] + 2 * FW              # cao canh (lam + vien tren/duoi)
UB, UH, UT = p["U"]
dz0 = UH + p["u_gap"]                                 # day vien duoi canh (tren mieng U)
dz1 = dz0 + DHD                                       # mep tren canh
z_tr0 = dz1 + p["hanger_gap"]                         # day ray treo
z_tr1 = z_tr0 + p["track"][1]                         # dinh ray = day dam dau cua
H_HEAD = p["header"][1]
H_TOP = z_tr1 + H_HEAD                                # dinh dam dau cua
FD = FDP
LANES = [10 + FDP / 2, 10 + FDP + 8 + FDP / 2]        # tam 2 lop canh (khe giua 2 canh 8)
GAP_DOOR = LANES[1] - LANES[0] - FDP
z_axle = UT + p["wheel_d"] / 2                        # truc banh (banh lan tren long U)

# ---- khoi luong canh (tu tiet dien sat + so thanh lam)
def _kgm(a, b, t):
    return (2 * (a + b) * t - 4 * t * t) * 7.85e-3      # kg/m hop chu nhat


def door_kg(i):
    dw = DWS[i]
    frame = 2 * (dw + DHD) / 1000 * _kgm(*p["door_frame"][:2], p["door_frame"][2])
    rails = p["n_rail_back"] * (dw - 2 * FW) / 1000 * _kgm(*p["rail_back"][:2], p["rail_back"][2])
    return frame + rails + KB[i] * p["lam_kg"] + 2.5      # +2,5 kg cum banh, bat treo, khoa, vit


DOOR_KG = [door_kg(i) for i in range(p["door_n"])]
WHEEL_NEED = max(DOOR_KG) / 4 * 1.5                   # tai 1 banh can (4 banh/canh, he so 1,5)

CHECK = dict(
    chong_mi=(p["ov_min"] <= OV <= p["ov_max"], f"chong mi {OV:.0f} trong {p['ov_min']}..{p['ov_max']} (ngoai khoang -> doi door_bars)"),
    vung_ray=(LANES[1] + FD / 2 + 5 <= p["DZ"], "canh trong nam gon trong vung ray DZ"),
    ray_vua=(p["track"][0] <= LANES[1] - LANES[0], "2 ray hop dat canh nhau vua khoang cach 2 lop canh"),
)
U_IN = UB - 2 * UT                                     # long U
CHECK["banh_long_U"] = (p["wheel_w"] + 4 <= U_IN and p["bogie_w"] + 2 <= U_IN,
                        f"banh {p['wheel_w']} + cang {p['bogie_w']} lot long U {U_IN:.0f} (chan canh lac +-{(U_IN - p['bogie_w']) / 2:.1f})")
CHECK["banh_duoi_mieng"] = (UT + p["wheel_d"] <= UH - 3, "dinh banh thap hon mieng U (banh nam han trong U)")
_lift = p["track"][1] - 2 * p["track_wall"] - p["trolley_play"] - p["trolley_h"]   # nhac canh toi khi xe treo cham noc ray
CHECK["chong_nhay"] = (_lift + 5 <= UH - UT, f"nhac canh toi da {_lift:.0f} mm (xe treo cham noc ray) < {UH - UT:.0f} can de banh thoat U")
CHECK["xe_treo_ho"] = (p["trolley_play"] > 0, "xe treo ho tren mep ray -> khong do tai, chi giu dung")
if p["wheel_kg"]:
    CHECK["tai_banh"] = (p["wheel_kg"] >= WHEEL_NEED, f"banh {p['wheel_kg']} kg >= can {WHEEL_NEED:.0f} kg")

# ---- khoa chong mi: khoa an tren lam canh truoc (C1), chot ban vao vien canh sau (C2)
LOCKS = []
for i in range(p["door_n"] - 1):
    fi, bi = (i, i + 1) if i % 2 == 0 else (i + 1, i)
    xv = DX0[bi] + FW / 2 if bi > fi else DX0[bi] + DWS[bi] - FW / 2
    LOCKS.append(dict(front=fi, back=bi, x=xv))
zl0_ = dz0 + FW + p["lam_gap_end"]
Z_LOCK = zl0_ + (p["lock_rail"] + 0.5) * DH / p["n_rail_back"]


def _in_lam(L):
    x0f = DX0[L["front"]] + FW + p["lam_gap_side"]
    return x0f + p["lock_d"] / 2 + 3 <= L["x"] <= x0f + KB[L["front"]] * LW - p["lock_d"] / 2 - 3


CHECK["khoa_tren_lam"] = (all(_in_lam(L) for L in LOCKS), "lo khoa nam tron tren lam canh truoc (khong cat vien)")
CHECK["khoa_an_vien"] = (p["plunger_travel"] >= GAP_DOOR + p["plunger_engage"],
                         "chot khoa qua khe giua 2 canh + an vao vien canh sau >= engage")
# ---- tay nam: khe xuyen giua 1 thanh lam moi canh
HANDLES = []
for i in range(p["door_n"]):
    j = p["handle_lam"][i] - 1
    HANDLES.append(dict(door=i, lam=j + 1, x=DX0[i] + FW + p["lam_gap_side"] + j * LW + LW / 2))
_hz0, _hz1 = p["handle_z"] - p["handle_h"] / 2, p["handle_z"] + p["handle_h"] / 2
_rails_z = [zl0_ + (n + 0.5) * DH / p["n_rail_back"] for n in range(p["n_rail_back"])]
CHECK["tay_nam_ne"] = (all(_hz1 + 30 <= zr - p["rail_back"][1] / 2 or _hz0 - 30 >= zr + p["rail_back"][1] / 2 for zr in _rails_z)
                       and (_hz1 + 30 <= Z_LOCK - p["lock_d"] / 2 or _hz0 - 30 >= Z_LOCK + p["lock_d"] / 2)
                       and all(1 <= p["handle_lam"][i] <= KB[i] for i in range(p["door_n"])),
                       "khe tay nam cach giang sau + lo khoa >= 30 (sau khe trong de moc tay)")


def _front_pos(fi):
    tl, tr = TRAVEL[fi]
    return {DX0[fi], DX0[fi] - tl, DX0[fi] + tr}


def _seen(xa, xb, fronts):
    return all(xb <= fx or xa >= fx + DWS[fi] for fi, fx in fronts)


def _handle_ok(h):
    i = h["door"]
    if i % 2 == 0:
        return True
    r = p["handle_w"] / 2 + p["handle_finger"]
    off = h["x"] - DX0[i]
    fis = [f for f in range(p["door_n"]) if f % 2 == 0]
    if not _seen(h["x"] - r, h["x"] + r, [(f, DX0[f]) for f in fis]):
        return False
    tl, tr = TRAVEL[i]
    import itertools
    for x0 in (DX0[i] - tl, DX0[i] + tr):
        for combo in itertools.product(*[sorted(_front_pos(f)) for f in fis]):
            if _seen(x0 + off - r, x0 + off + r, list(zip(fis, combo))):
                return True
    return False


CHECK["tay_nam_thay"] = (all(_handle_ok(h) for h in HANDLES),
                         "canh ray trong: dong cua thay tay nam, lua het van keo ve duoc (khong bi canh truoc che kin)")
z_rail_top = H_TOP - TB
y0i, y1i = p["DZ"], D
y_mid = (y0i + y1i) / 2
# khung dung: 3 khung DAY DU (2 tuong + giua, cot truoc nap sau cho chong mi) + 2 khung LUNG (khong cot truoc)
X_FULL = [TB / 2, W / 2, W - TB / 2]
X_HALF = [(X_FULL[0] + X_FULL[1]) / 2, (X_FULL[1] + X_FULL[2]) / 2]
x_lines = sorted(X_FULL + X_HALF)

BAYS = [   # Tuan 2026-11-09: chi treo ong tron O27, ca 4 khoang 2 tang 2050/1030
    dict(name="K1 treo 2 tang", rods=[2050, 1030]),
    dict(name="K2 treo 2 tang", rods=[2050, 1030]),
    dict(name="K3 treo 2 tang", rods=[2050, 1030]),
    dict(name="K4 treo 2 tang", rods=[2050, 1030]),
]


def _rod_check():
    Do, t = p["rod_d"], p["rod_t"]
    Di = Do - 2 * t
    I = math.pi / 64 * (Do ** 4 - Di ** 4)
    Z = I / (Do / 2)
    E = 193000
    span = max(x_lines[b + 1] - x_lines[b] for b in range(len(x_lines) - 1)) - TB
    w = p["rod_load_kg"] * 9.81 / span
    Mmax = w * span ** 2 / 8
    return dict(span=span, sigma=Mmax / Z, defl=5 * w * span ** 4 / (384 * E * I))


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
    w, h = {"40x40": (40, 40), "40x80": (80, 40), "40x80v": (40, 80)}.get(prof, (40, 20))
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
    # ---- khung dung: day du (cot truoc + sau) o 2 tuong + giua; lung (khong cot truoc) o giua moi nua
    for i, xl in enumerate(x_lines):
        n = f"KD{i}"
        full = xl in X_FULL
        if full:
            steel(f"{n}-cot-truoc", "z", 4, z_rail_top, xl, y0i + TB / 2)
        steel(f"{n}-cot-sau", "z", 4, z_rail_top, xl, y1i - TB / 2)
        steel(f"{n}-cot-giua", "z", 4, zs - TB, xl, y_mid)
        # khung lung: dam ke + dam dinh gac len thanh ngang truoc (khong cot truoc -> khong can loi lay do)
        steel(f"{n}-dam-ke", "y", y0i + TB, y1i - TB, xl, zs - TB / 2)
        steel(f"{n}-dam-dinh", "y", y0i + TB, y1i - TB, xl, H_TOP - TB / 2)
        for nm_, yy in ((("truoc", y0i + TB / 2),) if full else ()) + (("giua", y_mid), ("sau", y1i - TB / 2)):
            box(f"{n}-de-cot-{nm_}", "Khung sat", xl - 30, xl + 30, yy - 30, yy + 30, 0, 4, "steel", "plate", "60x60x4")
    for nm, yc, zc in (("ke-truoc", y0i + TB / 2, zs - TB / 2), ("ke-sau", y1i - TB / 2, zs - TB / 2),
                       ("dinh-truoc", y0i + TB / 2, H_TOP - TB / 2), ("dinh-sau", y1i - TB / 2, H_TOP - TB / 2)):
        steel(f"Ngang-{nm}", "x", 0, W, yc, zc)
    # ---- 2 dam do ray tren 40x40 (moi ray 1 dam), bat vao cot truoc 2 tuong + cot giua - chi giu canh dung
    for li, yc in enumerate(LANES):
        steel(f"Dam-dau-cua-{li + 1}", "x", 0, W, yc, z_tr1 + H_HEAD / 2, "40x40")
        # cot truoc khung day du dung tu san len do dam (o vung ray, sat tuong / cho chong mi)
    for xl in X_FULL:
        box(f"Bat-dam-{int(xl)}", "Khung sat", xl - 20, xl + 20, LANES[0] - 20, y0i, z_tr1, z_tr1 + H_HEAD,
            "steel", "plate", "bat noi dam dau cua - cot truoc")
    # ---- ke hop noc + ong treo theo khoang
    for b in range(len(x_lines) - 1):
        xa, xb = x_lines[b] + (TB / 2 if b == 0 else 0), x_lines[b + 1] - (TB / 2 if b == len(x_lines) - 2 else 0)
        box(f"K{b + 1}-van-ke-noc", "Van", xa, xb, y0i, y1i, zs, zs + p["board_t"], "board", "board")
    for b, spec in enumerate(BAYS):
        xa, xb = x_lines[b] + TB / 2, x_lines[b + 1] - TB / 2
        for zr in spec["rods"]:
            cyl(f"K{b + 1}-ong-{zr}", "Ong treo", p["rod_d"] / 2, xb - xa, ((xa + xb) / 2, y_mid, zr),
                (0, math.pi / 2, 0), "rod")
            parts.append(dict(name=f"K{b + 1}-ong-{zr}", group="Ong treo", mat="rod", kind="rod",
                              spec=f"Ø{p['rod_d']}", bbox=[xa, xb, y_mid - 13.5, y_mid + 13.5, zr - 13.5, zr + 13.5],
                              L=round(xb - xa - 2, 1), Wd=p["rod_d"], Th=p["rod_d"]))
    # ---- ray treo hop 40x40 (ve: 3 vach + day co khe) bat duoi moi dam dau cua
    tw, th = p["track"]
    for li, yc in enumerate(LANES):
        g = "Ray"
        box(f"Ray-treo-{li + 1}-tren", g, 0, W, yc - tw / 2, yc + tw / 2, z_tr1 - 2, z_tr1, "alu", "track", f"ray hop {tw}x{th}")
        for sgn in (-1, 1):
            box(f"Ray-treo-{li + 1}-vach{'ab'[sgn > 0]}", g, 0, W, yc + sgn * tw / 2 - (2 if sgn > 0 else 0),
                yc + sgn * tw / 2 + (0 if sgn > 0 else 2), z_tr0, z_tr1, "alu", "track", f"ray hop {tw}x{th}")
            ys0 = yc + sgn * p["track_slot"] / 2
            box(f"Ray-treo-{li + 1}-day{'ab'[sgn > 0]}", g, 0, W, min(ys0, yc + sgn * tw / 2), max(ys0, yc + sgn * tw / 2),
                z_tr0, z_tr0 + 2, "alu", "track", f"ray hop {tw}x{th}")
        # chan cuoi: dau dong cua co LAY GIU (thay chot bi), dau kia cao su
        st = p["trolley_in"] - p["trolley_L"] / 2 - 1
        closed_left = li % 2 == 0          # C1 dong o tuong trai, C2 dong o tuong phai
        for xa, xb, latch in ((0, st, closed_left), (W - st, W, not closed_left)):
            box(f"Chan-cuoi-R{li + 1}-{int(xa)}", g, xa, xb, yc - tw / 2 + 3, yc + tw / 2 - 3, z_tr0 + 3, z_tr1 - 3,
                "rubber", "stop", "chan cuoi co lay giu canh dong" if latch else "chan cuoi cao su")
    # ---- ray DUOI chiu tai: U chan 40x40 nam ngua, tuong -> tuong, moi lop canh 1 thanh (canh che kin khi dong)
    for li, yc in enumerate(LANES):
        g = "Ray"
        box(f"Ray-U-{li + 1}-long", g, 0, W, yc - UB / 2, yc + UB / 2, 0, UT, "steel", "utrack", f"U chan {UB}x{UH}x{UT}")
        for sgn in (-1, 1):
            yw = yc + sgn * UB / 2
            box(f"Ray-U-{li + 1}-canh{'ab'[sgn > 0]}", g, 0, W, min(yw, yw - sgn * UT), max(yw, yw - sgn * UT),
                UT, UH, "steel", "utrack-side", f"U chan {UB}x{UH}x{UT}")
        # chan cuoi cao su trong long U (cum banh cham) - 2 dau
        st = p["bogie_in"] - p["bogie_pitch"] / 2 - p["wheel_d"] / 2 - 1
        for xa, xb in ((0, st), (W - st, W)):
            box(f"Chan-U-{li + 1}-{int(xa)}", g, xa, xb, yc - U_IN / 2, yc + U_IN / 2, UT, UH - 4, "rubber", "stop-u",
                "chan cuoi cao su trong long U")
    # ---- canh: vien hop 20x40 + giang sau 13x26 + 7 thanh lam nguyen cay + ranh duoi + bat treo tren
    r = 13
    pitch = LW / p["lam_waves"]
    rb_d, rb_w = p["rail_back"][0], p["rail_back"][1]
    for i in range(p["door_n"]):
        front = i % 2 == 0
        yc = LANES[0] if front else LANES[1]
        yf0, yf1 = yc - FDP / 2, yc + FDP / 2
        yl = yf1 - rb_d - LT
        x0, dw = DX0[i], DWS[i]
        kk = KB[i]
        g = f"Canh {i + 1}"
        pre = f"C{i + 1}-"
        box(pre + "vien-dung-trai", g, x0, x0 + FW, yf0, yf1, dz0, dz1, "steel", "dframe", "20x40")
        box(pre + "vien-dung-phai", g, x0 + dw - FW, x0 + dw, yf0, yf1, dz0, dz1, "steel", "dframe", "20x40")
        box(pre + "vien-ngang-duoi", g, x0 + FW, x0 + dw - FW, yf0, yf1, dz0, dz0 + FW, "steel", "dframe", "20x40")
        box(pre + "vien-ngang-tren", g, x0 + FW, x0 + dw - FW, yf0, yf1, dz1 - FW, dz1, "steel", "dframe", "20x40")
        zl0 = dz0 + FW + p["lam_gap_end"]
        for n in range(p["n_rail_back"]):
            zz = zl0 + (n + 0.5) * DH / p["n_rail_back"]
            box(pre + f"giang-sau-{n + 1}", g, x0 + FW, x0 + dw - FW, yf1 - rb_d, yf1, zz - rb_w / 2, zz + rb_w / 2,
                "steel", "rback", "13x26")
        for j in range(kk):
            bx = x0 + FW + p["lam_gap_side"] + j * LW
            box(pre + f"lam{j + 1}", g, bx + 0.5, bx + LW - 0.5, yl + r, yl + LT, zl0, zl0 + DH, "lam", "lam", f"{LW}x{LT}")
            cyl(pre + f"lam{j + 1}-song", g, r, DH, (bx + pitch / 2, yl + r, zl0 + DH / 2), (0, 0, 0), "lam",
                array=((pitch, 0, 0), p["lam_waves"]))
        hx, hw_, hh = HANDLES[i]["x"], p["handle_w"], p["handle_h"]
        box(pre + "tay-nam", g, hx - hw_ / 2, hx + hw_ / 2, yl - 1, yl + LT + 0.5,
            p["handle_z"] - hh / 2 + hw_ / 2, p["handle_z"] + hh / 2 - hw_ / 2, "dark", "hole", f"khe nam {hw_}x{hh} xuyen lam")
        for zc in (p["handle_z"] - hh / 2 + hw_ / 2, p["handle_z"] + hh / 2 - hw_ / 2):
            cyl(pre + f"tay-nam-{int(zc)}", g, hw_ / 2, LT + 1.5, (hx, yl + LT / 2 - 0.25, zc), (math.pi / 2, 0, 0), "dark")
        # 2 cum banh duoi: cang thep han day vien duoi, 2 banh 608 boc POM lan tren long U
        for side, xb_ in (("trai", x0 + p["bogie_in"]), ("phai", x0 + dw - p["bogie_in"])):
            bw = p["bogie_w"]
            box(pre + f"cang-banh-{side}", g, xb_ - p["bogie_pitch"] / 2 - 18, xb_ + p["bogie_pitch"] / 2 + 18,
                yc - bw / 2, yc + bw / 2, z_axle + 4, dz0, "steel", "bogie", "cang banh han day vien duoi, vit chinh cao")
            for dx in (-p["bogie_pitch"] / 2, p["bogie_pitch"] / 2):
                cyl(pre + f"banh-duoi-{side}-{int(dx)}", g, p["wheel_d"] / 2, p["wheel_w"], (xb_ + dx, yc, z_axle),
                    (math.pi / 2, 0, 0), "nylon")
        # 2 bat treo + bulong + xe treo trong ray
        for side, xt in (("trai", x0 + p["trolley_in"]), ("phai", x0 + dw - p["trolley_in"])):
            box(pre + f"bat-treo-{side}", g, xt - 30, xt + 30, yc - 15, yc + 15, dz1, dz1 + 6, "steel", "hw",
                "bat treo bat vien tren (tan rut ren M8)")
            cyl(pre + f"bulong-treo-{side}", g, 4, z_tr0 + 8 - dz1 - 6, (xt, yc, (dz1 + 6 + z_tr0 + 8) / 2), (0, 0, 0), "rod")
            zt0 = z_tr0 + 4
            box(pre + f"xe-treo-{side}", g, xt - p["trolley_L"] / 2, xt + p["trolley_L"] / 2, yc - 8, yc + 8,
                zt0, zt0 + p["trolley_h"], "steel", "hw", "xe treo (theo bo ray)")
            for dx in (-p["trolley_L"] / 3, p["trolley_L"] / 3):
                cyl(pre + f"banh-treo-{side}-{int(dx)}", g, 8, 30, (xt + dx, yc, zt0 + 10), (math.pi / 2, 0, 0), "nylon")
        for L in LOCKS:
            if L["front"] == i:
                cyl(pre + f"khoa-an-{int(L['x'])}", g, p["lock_d"] / 2, LT + 4,
                    (L["x"], yl + LT / 2 - 2, Z_LOCK), (math.pi / 2, 0, 0), "rod")
                box(pre + f"than-khoa-{int(L['x'])}", g, L["x"] - 14, L["x"] + 14, yl + LT, yf1, Z_LOCK - 25, Z_LOCK + 25,
                    "steel", "hw", "khoa an (push lock)")
                cyl(pre + f"chot-khoa-{int(L['x'])}", g, p["plunger_d"] / 2, GAP_DOOR + p["plunger_engage"],
                    (L["x"], yf1 + (GAP_DOOR + p["plunger_engage"]) / 2, Z_LOCK), (math.pi / 2, 0, 0), "rod")
            if L["back"] == i:
                cyl(pre + f"lo-bat-chot-{int(L['x'])}", g, (p["plunger_d"] + 2) / 2, 1,
                    (L["x"], yf0 - 0.4, Z_LOCK), (math.pi / 2, 0, 0), "dark")
    return dict(P=P, TRAVEL=TRAVEL, LOCKS=LOCKS, HANDLES=HANDLES, Z_LOCK=Z_LOCK, GAP_DOOR=GAP_DOOR, DW=max(DWS), DWS=DWS,
                DX0=DX0, OPEN=OPEN, KB=KB, OV=OV, k=max(KB), DH=DH, DHD=DHD, FW=FW, FDP=FDP, H_TOP=H_TOP, LANES=LANES,
                dz=[dz0, dz1], z_track=[z_tr0, z_tr1], z_axle=z_axle, U_IN=U_IN, DOOR_KG=DOOR_KG, WHEEL_NEED=WHEEL_NEED,
                ROD=ROD, CHECK={kk: [bool(v[0]), v[1]] for kk, v in CHECK.items()},
                x_lines=x_lines, X_FULL=X_FULL, X_HALF=X_HALF, BAYS=BAYS, y_mid=y_mid)



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



def setup_anim(fps=24):
    """Moi canh 1 Empty goc; C1 lua phai het co -> dong, roi C2 lua trai het co -> dong."""
    sc = bpy.context.scene
    sc.render.fps = fps
    seq = [(0, TRAVEL[0][1]), (1, -TRAVEL[1][0])]
    mv, hold, gap = int(2.0 * fps), int(0.8 * fps), int(0.4 * fps)
    roots = []
    for i in range(p["door_n"]):
        e = bpy.data.objects.new(f"Canh{i + 1}-goc", None)
        sc.collection.objects.link(e)
        for o in list(COLS[f"Canh {i + 1}"].objects):
            o.parent = e
        roots.append(e)
    f = gap
    for i, dx in seq:
        e = roots[i]
        for fr, x in ((f, 0), (f + mv, dx), (f + mv + hold, dx), (f + 2 * mv + hold, 0)):
            e.location.x = x * M
            e.keyframe_insert("location", index=0, frame=fr)
        f += 2 * mv + hold + gap
    sc.frame_start, sc.frame_end = 1, f
    return f


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
    shot(front, os.path.join(out, "01-mat-truoc-dong-cua.png"))
    shot(front, os.path.join(out, "02-mat-truoc-khung-sat.png"), hide=doors + ["Ray"])
    shot(iso, os.path.join(out, "03-iso-mo-nua-trai.png"), hide=["Tuong trai"], move={"C1-": TRAVEL[0][1]})
    shot(iso, os.path.join(out, "04-iso-khong-cua.png"), hide=doors + ["Tuong trai"])
    shot(iso, os.path.join(out, "05-iso-mo-nua-phai.png"), hide=["Tuong trai"], move={"C2-": -TRAVEL[1][0]})
    inside = ["Tuong trai", "Khung sat", "Ong treo", "Van", "Moi truong"]
    cb = cam("Cam-ray-U", (W - 330, -380, 260), (68, 0, -40), lens=40)
    shot(cb, os.path.join(out, "06-chi-tiet-ray-U-duoi.png"), hide=["Tuong trai", "Ong treo", "Van"],
         move={"C2-": -TRAVEL[1][0]})
    ct = cam("Cam-ray-treo", (W - 420, 520, H_TOP - 330), (108, 0, 205), lens=40)
    shot(ct, os.path.join(out, "07-chi-tiet-ray-treo.png"), hide=inside)
    ch = cam("Cam-tay-nam", (W / 2 - 250, -1100, p["handle_z"] + 250), (78, 0, -12), lens=35)
    shot(ch, os.path.join(out, "08-chi-tiet-tay-nam.png"))
    n_fr = setup_anim()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(here, "wardrobe.blend"))
    json.dump(dict(meta=meta, parts=parts), open(os.path.join(here, "parts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for kk, (ok, why) in CHECK.items():
        print(("PASS " if ok else "FAIL ") + kk + ": " + why)
    print(f"INFO canh {[round(x, 1) for x in DOOR_KG]} kg (lam_kg={p['lam_kg']} TODO can) -> banh can >= {WHEEL_NEED:.0f} kg/banh (4 banh/canh)")
    if "--anim" in argv:
        sc = bpy.context.scene
        sc.camera = bpy.data.objects["Cam-iso"]
        for g in COLS:
            COLS[g].hide_render = g == "Tuong trai"
        sc.render.resolution_x, sc.render.resolution_y = 960, 840
        fdir = os.path.join(here, "anim-frames")
        os.makedirs(fdir, exist_ok=True)
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = os.path.join(fdir, "f_")
        bpy.ops.render.render(animation=True)
        print("ANIM FRAMES", n_fr)
    print(f"BUILD OK parts={len(parts)} bars={KB} DWS={DWS} OV={OV:.1f} OPEN={[round(o) for o in OPEN]} H_TOP={H_TOP:.0f}")


main()
