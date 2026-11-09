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
    door_n=4, ov_min=40,        # chong mi toi thieu; so thanh/canh tu chon
    door_frame=(20, 40, 1.2),   # khung canh hop sat 20x40x1.2 (an sau lam)
    door_z0=15,                 # khe banh xe/ray duoi (TODO theo bo ray)
    top_guide=45,               # chieu cao ray dan huong tren (TODO)
    DZ=120,                     # vung 2 ray phia truoc
    tube=(40, 40, 1.4),         # khung chiu luc hop sat 40x40x1.4 son tinh dien
    header=(40, 80, 1.4),       # dam dau cua (do ray tren) 40x80
    z_shelf=2300,               # mat ke hop noc
    board_t=17,                 # van ke hop noc (MFC/plywood)
    rod_d=27,
)
p = P
W, D = p["W"], p["D"]
LW, LT = p["lam_w"], p["lam_t"]
TB = p["tube"][0]
k = 1
while p["door_n"] * k * LW - W < (p["door_n"] - 1) * p["ov_min"]:
    k += 1
DW = k * LW                                           # rong canh = k thanh nguyen
OV = (p["door_n"] * DW - W) / (p["door_n"] - 1)       # chong mi thuc te
DH = p["lam_L"]
dz0, dz1 = p["door_z0"], p["door_z0"] + DH
H_TOP = dz1 - 15 + p["top_guide"] + p["header"][0]    # dinh dam dau cua
z_rail_top = H_TOP - TB
y0i, y1i = p["DZ"], D
y_mid = (y0i + y1i) / 2
# vi tri cac khung dung: 2 tuong + 3 cho chong mi
x_lines = [TB / 2] + [(i + 1) * (DW - OV) + OV / 2 for i in range(p["door_n"] - 1)] + [W - TB / 2]

BAYS = [   # Tuan 2026-11-09: chi treo ong tron Ø27, khong ngan keo/ke
    dict(name="K1 treo 2 tang", rods=[2050, 1030]),
    dict(name="K2 treo dai", rods=[1950]),
    dict(name="K3 treo dai", rods=[1950]),
    dict(name="K4 treo 2 tang", rods=[2050, 1030]),
]

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
        wall=mat("Tuong", "#E9E6E0", 0.9),
        floor=mat("San", "#CFC8BC", 0.8),
    )
    zs = p["z_shelf"]
    # ---- khung dung tai moi duong (2 tuong + 3 cho chong mi)
    for i, xl in enumerate(x_lines):
        n = f"KD{i}"
        steel(f"{n}-cot-giua", "z", 0, zs - TB, xl, y_mid)                         # cot giua (bat ong treo)
        steel(f"{n}-dam-ke", "y", y0i + TB, y1i - TB, xl, zs - TB / 2)             # dam ngang do ke
        steel(f"{n}-cot-tren-truoc", "z", zs, z_rail_top, xl, y0i + TB / 2)
        steel(f"{n}-cot-tren-sau", "z", zs, z_rail_top, xl, y1i - TB / 2)
        steel(f"{n}-dam-dinh", "y", y0i + TB, y1i - TB, xl, H_TOP - TB / 2)
        if 0 < i < len(x_lines) - 1:   # chan de cot giua bat san
            box(f"{n}-de-cot", "Khung sat", xl - 50, xl + 50, y_mid - 50, y_mid + 50, 0, 4, "steel", "plate", "100x100x4")
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
    # ---- ray
    box("Ray-duoi", "Ray", 0, W, 5, y0i - 5, 0, 8, "alu", "track", "ray duoi doi")
    box("Ray-tren", "Ray", 0, W, 5, y0i - 5, dz1 - 15, dz1 - 15 + p["top_guide"], "alu", "track", "ray tren doi")
    # ---- canh: khung 20x40 + k thanh lam nguyen cay
    fw, fd = p["door_frame"][1], p["door_frame"][0]
    r = 13
    pitch = LW / p["lam_waves"]
    for i in range(p["door_n"]):
        front = i % 2 == 0
        yl = 10 if front else 10 + LT + fd + 8          # mat truoc lam
        x0 = i * (DW - OV)
        g = f"Canh {i + 1}"
        yf0, yf1 = yl + LT, yl + LT + fd
        for side, (a, b_) in (("trai", (x0 + 10, x0 + 10 + fw)), ("phai", (x0 + DW - 10 - fw, x0 + DW - 10))):
            box(f"C{i + 1}-khung-dung-{side}", g, a, b_, yf0, yf1, dz0, dz1, "steel", "dframe", "20x40")
        for zz in (dz0 + 30, (dz0 + dz1) / 2, dz1 - 30):
            box(f"C{i + 1}-khung-ngang-{int(zz)}", g, x0 + 10 + fw, x0 + DW - 10 - fw, yf0, yf1,
                zz - 10, zz + 10, "steel", "dframe", "20x40")
        for j in range(k):
            bx = x0 + j * LW
            box(f"C{i + 1}-lam{j + 1}", g, bx + 0.5, bx + LW - 0.5, yl + r, yl + LT, dz0, dz1, "lam", "lam", f"{LW}x{LT}")
            cyl(f"C{i + 1}-lam{j + 1}-song", g, r, DH, (bx + pitch / 2, yl + r, (dz0 + dz1) / 2), (0, 0, 0), "lam",
                array=((pitch, 0, 0), p["lam_waves"]))
    return dict(P=P, DW=DW, OV=OV, k=k, DH=DH, H_TOP=H_TOP, x_lines=x_lines, BAYS=BAYS, y_mid=y_mid)


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
    sh = DW - OV
    shot(front, os.path.join(out, "01-mat-truoc-dong-cua.png"))
    shot(front, os.path.join(out, "02-mat-truoc-khung-sat.png"), hide=doors + ["Ray"])
    shot(iso, os.path.join(out, "03-iso-mo-khoang-1-4.png"), hide=["Tuong trai"], move={"C1-": sh, "C4-": -sh})
    shot(iso, os.path.join(out, "04-iso-khong-cua.png"), hide=doors + ["Tuong trai"])
    shot(iso, os.path.join(out, "05-iso-mo-khoang-2-3.png"), hide=["Tuong trai"], move={"C2-": -sh, "C3-": sh})
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(here, "wardrobe.blend"))
    json.dump(dict(meta=meta, parts=parts), open(os.path.join(here, "parts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"BUILD OK parts={len(parts)} k={k} DW={DW} OV={OV:.1f} H_TOP={H_TOP:.0f}")


main()
