"""Tu ao am tuong cua lua 2 canh TREO (khong ray duoi) - khung sat chiu luc + canh lam song nguyen cay (Blender, bpy).

Tuan 2026-11-11: chi co ray cua lua hop 40x40, chi muon 2 canh -> canh treo tren ray, bo ray duoi.
Chong lac chan canh: 1 dan huong san o GIUA (x = W/2, luon nam duoi ca 2 canh), chot nylon chay trong ranh day canh.
Ban 4 canh banh do duoi: backup/2026-11-11-truoc-2-canh-treo/.

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
    # ---- he treo: ray hop 40x40 (Tuan co san) + xe treo chay trong ray. TODO thay so theo bo ray/xe treo that
    track=(40, 40),             # ray hop (rong y, cao z)
    track_slot=14,              # khe day ray cho bulong treo di qua (TODO do)
    hanger_gap=25,              # mep tren canh -> day ray (bat treo + bulong chinh cao, TODO theo xe treo)
    trolley_in=110,             # tam xe treo cach mep canh
    trolley_L=90, trolley_h=28, # than xe treo trong ray (ve minh hoa)
    trolley_kg=None,            # TODO tai 1 xe treo cua hang mua (kg) -> script so voi tai can
    # ---- dan huong san (chong lac): ranh duoi day canh + chot nylon bat san o giua
    floor_gap=8,                # day ranh -> mat san
    slot_w=12, slot_d=15,       # ranh tao boi 2 sat la 3 x slot_d han duoi vien duoi
    pin_d=10,                   # chot nylon (hoac banh 608 nho) chay trong ranh
    pin_engage=10,              # chot an vao ranh
    slot_end=60,                # chot phai cach dau ranh toi thieu (ca khi lua het)
    # ---- khoa + tay nam
    lock_d=20, plunger_d=8, plunger_travel=14, plunger_engage=5, lock_rail=1,
    handle_w=30, handle_h=200, handle_z=950,   # tam khe tu san (TODO chinh theo nguoi dung; cach giang sau >= 30)
    handle_lam=[2, 6],          # C1 thanh 2, C2 thanh 6 -> doi xung (351 tu moi tuong), C2 lua het van keo ve duoc
    handle_finger=15,
    DZ=120,                     # vung 2 ray phia truoc
    tube=(40, 40, 1.4),         # khung chiu luc hop sat 40x40x1.4
    header=(40, 80, 1.4),       # dam dau cua 40x80 DAT DUNG (80 theo phuong dung), 1 dam / 1 ray
    steel_E=200000, steel_sigma_max=140,   # MPa (thep CT3 chay ~235 -> he so ~1,7)
    header_defl_div=400,        # vong cho phep L/400
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
dz0 = p["floor_gap"] + p["slot_d"]                    # day vien duoi (ranh dan huong nam duoi)
dz1 = dz0 + DHD                                       # mep tren canh
z_tr0 = dz1 + p["hanger_gap"]                         # day ray treo
z_tr1 = z_tr0 + p["track"][1]                         # dinh ray = day dam dau cua
H_HEAD = p["header"][1]
H_TOP = z_tr1 + H_HEAD                                # dinh dam dau cua
FD = FDP
LANES = [10 + FDP / 2, 10 + FDP + 8 + FDP / 2]        # tam 2 lop canh (khe giua 2 canh 8)
GAP_DOOR = LANES[1] - LANES[0] - FDP
X_GUIDE = W / 2                                       # dan huong san o giua (duoi cho chong mi)

# ---- khoi luong canh (tu tiet dien sat + so thanh lam)
def _kgm(a, b, t):
    return (2 * (a + b) * t - 4 * t * t) * 7.85e-3      # kg/m hop chu nhat


def door_kg(i):
    dw = DWS[i]
    frame = 2 * (dw + DHD) / 1000 * _kgm(*p["door_frame"][:2], p["door_frame"][2])
    rails = p["n_rail_back"] * (dw - 2 * FW) / 1000 * _kgm(*p["rail_back"][:2], p["rail_back"][2])
    slot = 2 * dw / 1000 * 3 * p["slot_d"] * 7.85e-3
    return frame + rails + slot + KB[i] * p["lam_kg"] + 1.5      # +1,5 kg bat treo, khoa, vit


DOOR_KG = [door_kg(i) for i in range(p["door_n"])]
TROLLEY_NEED = max(DOOR_KG) / 2 * 1.5                 # tai 1 xe treo can (2 xe/canh, he so 1,5)

CHECK = dict(
    chong_mi=(p["ov_min"] <= OV <= p["ov_max"], f"chong mi {OV:.0f} trong {p['ov_min']}..{p['ov_max']} (ngoai khoang -> doi door_bars)"),
    vung_ray=(LANES[1] + FD / 2 + 5 <= p["DZ"], "canh trong nam gon trong vung ray DZ"),
    ray_vua=(p["track"][0] <= LANES[1] - LANES[0], "2 ray hop dat canh nhau vua khoang cach 2 lop canh"),
)
# dan huong: chot giua luon nam trong ranh cua ca 2 canh o moi vi tri (dong / lua het trai / lua het phai)
def _guide_ok(i):
    tl, tr = TRAVEL[i]
    for x0 in (DX0[i], DX0[i] - tl, DX0[i] + tr):
        if not (x0 + p["slot_end"] <= X_GUIDE <= x0 + DWS[i] - p["slot_end"]):
            return False
    return True


CHECK["dan_huong"] = (all(_guide_ok(i) for i in range(p["door_n"])),
                      f"chot dan huong x={X_GUIDE:.0f} luon nam trong ranh 2 canh (cach dau ranh >= {p['slot_end']}) suot hanh trinh")
CHECK["chot_an_ranh"] = (p["pin_engage"] <= p["slot_d"] - 3 and p["pin_d"] < p["slot_w"],
                         "chot an vao ranh, ranh rong hon chot (chi lac duoc +-1 mm)")

# ---- dam dau cua: moi ray 1 dam 40x80 dat dung, nhip giua 2 khung (tuong - giua), 1 canh tai giua nhip (bat loi nhat)
def _header_check():
    b, h, t = p["header"]
    I = (b * h ** 3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12
    Z = I / (h / 2)
    span = W / 2 - TB
    Pn = max(DOOR_KG) * 9.81
    Mmax = Pn * span / 4
    return dict(span=span, sigma=Mmax / Z, defl=Pn * span ** 3 / (48 * p["steel_E"] * I))


HEAD = _header_check()
CHECK["dam_ung_suat"] = (HEAD["sigma"] <= p["steel_sigma_max"],
                         f"dam dau cua 40x80 dung, nhip {HEAD['span']:.0f}, canh {max(DOOR_KG):.0f} kg giua nhip: {HEAD['sigma']:.0f} MPa <= {p['steel_sigma_max']}")
CHECK["dam_vong"] = (HEAD["defl"] <= HEAD["span"] / p["header_defl_div"],
                     f"vong dam {HEAD['defl']:.1f} mm <= L/{p['header_defl_div']} = {HEAD['span'] / p['header_defl_div']:.1f}")
if p["trolley_kg"]:
    CHECK["xe_treo"] = (p["trolley_kg"] >= TROLLEY_NEED, f"xe treo {p['trolley_kg']} kg >= can {TROLLEY_NEED:.0f} kg")

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
    # ---- 2 dam dau cua 40x80 DAT DUNG, moi dam tren 1 ray; tai xuong cot truoc 2 tuong + cot giua
    for li, yc in enumerate(LANES):
        steel(f"Dam-dau-cua-{li + 1}", "x", 0, W, yc, z_tr1 + H_HEAD / 2, "40x80v")
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
    # ---- dan huong san: de thep + 2 chot nylon (1 chot / lop canh) o x = W/2, bat 2 vit xuong san
    gx = X_GUIDE
    box("Dan-huong-san-de", "Ray", gx - 30, gx + 30, LANES[0] - 18, LANES[1] + 18, 0, 3, "steel", "guide",
        "de dan huong san 3 x 60 x 84, 2 vit no")
    for li, yc in enumerate(LANES):
        cyl(f"Dan-huong-chot-{li + 1}", "Ray", p["pin_d"] / 2, p["floor_gap"] + p["pin_engage"] - 3,
            (gx, yc, 3 + (p["floor_gap"] + p["pin_engage"] - 3) / 2), (0, 0, 0), "nylon")
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
        # ranh dan huong: 2 sat la 3 x slot_d han duoi vien duoi, suot chieu rong canh
        for sgn in (-1, 1):
            ya = yc + sgn * p["slot_w"] / 2
            box(pre + f"ranh-la{'ab'[sgn > 0]}", g, x0, x0 + dw, min(ya, ya + sgn * 3), max(ya, ya + sgn * 3),
                p["floor_gap"], dz0, "steel", "slot", f"la 3x{p['slot_d']} ranh dan huong")
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
                dz=[dz0, dz1], z_track=[z_tr0, z_tr1], X_GUIDE=X_GUIDE, DOOR_KG=DOOR_KG, TROLLEY_NEED=TROLLEY_NEED,
                HEAD=HEAD, ROD=ROD, CHECK={kk: [bool(v[0]), v[1]] for kk, v in CHECK.items()},
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
    cb = cam("Cam-dan-huong", (X_GUIDE + 230, 430, 190), (62, 0, 152), lens=40)   # tu trong tu nhin ra, thap
    shot(cb, os.path.join(out, "06-chi-tiet-dan-huong-san.png"), hide=["Tuong trai", "Ong treo", "Van", "Khung sat"])
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
    print(f"INFO canh {[round(x, 1) for x in DOOR_KG]} kg (lam_kg={p['lam_kg']} TODO can) -> xe treo can >= {TROLLEY_NEED:.0f} kg/xe")
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
