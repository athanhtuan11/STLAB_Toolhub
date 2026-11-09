"""Tu ao cua lua 4 canh - model tham so Blender (don vi trong code: mm, Blender: m).

Chay:  blender -b -P build_wardrobe.py -- --out renders   (tu thu muc design/)
Doi kich thuoc: sua P ben duoi (W sau khi do thuc te), chay lai.
Xuat: wardrobe.blend, renders/*.png, parts.json (cho draw_plans.py lam ban ve + cut list).
"""
import bpy, json, math, os, sys

# ----------------------------------------------------------------- tham so (mm)
P = dict(
    W=3000,          # rong tong (TODO do lai thuc te, tru khe bu tuong ~10-20/ben)
    H=2900,          # cao tong (theo kho lam song 2900)
    D=800,           # sau tong
    T=17,            # van than MFC/MDF chong am
    T_back=9,        # van hau
    H_low=2300,      # cao module duoi (vach <= 2440 kho van)
    plinth=80,       # chan tu
    DZ=100,          # vung ray cua phia truoc (TODO theo bo ray mua)
    door_n=4, door_ov=40,       # chong mi canh
    door_t=18,                  # day canh (khung nhom + lam song) TODO
    gap_top=40, gap_bot=15,     # khe ray tren/duoi (TODO theo bo ray)
    lam_pitch=30, lam_r=6,      # buoc song lam song (TODO do tam that)
    rod_d=27,                   # ong treo tron inox
    slide_len=550,              # ray bi ngan keo
    clad_t=12,                  # op vach ngoai bang thanh lam song nguyen cay 2900 (TODO day tam that)
    clad_sides=True,            # False neu tu sat 2 tuong
)
p = P
CL = p["clad_t"] if p["clad_sides"] else 0
W, H, D, T = p["W"] - 2 * CL, p["H"], p["D"], p["T"]   # W = rong than; op lam song nam ngoai
Wc = W / 2                       # moi tu rong W/2 (2 tu ghep)
zb = p["plinth"] + T             # mat san trong
z_low_top = p["H_low"] - T       # mat duoi tran module duoi
y_in0 = p["DZ"]                  # mat truoc khoang trong
y_in1 = D - p["T_back"]          # mat truoc van hau

# Bo tri tung khoang (z tinh tu san nha, mm). Khoang 1 & 4 o ngoai -> mo du rong cho ngan keo.
BAYS = [   # Tuan 2026-11-09: khong ngan keo/ke, chi treo ong tron Ø27
    dict(name="K1 treo 2 tang", drawers=[], shelves=[], rods=[2050, 1030]),
    dict(name="K2 treo dai",    drawers=[], shelves=[], rods=[1950]),
    dict(name="K3 treo dai",    drawers=[], shelves=[], rods=[1950]),
    dict(name="K4 treo 2 tang", drawers=[], shelves=[], rods=[2050, 1030]),
]

parts = []
M = 0.001


def mat(name, rgb, rough=0.5, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*rgb, 1)
    return m


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


MAT = dict(
    carcass=mat("MFC van soi", srgb("#D6C3A3"), 0.55),
    interior=mat("MFC van soi", srgb("#D6C3A3"), 0.55),
    back=mat("Van hau", srgb("#E8DFCF"), 0.7),
    drawer=mat("Mat ngan keo trang", srgb("#F1EEE8"), 0.4),
    door=mat("Lam song oc cho", srgb("#6E4E36"), 0.45),
    alu=mat("Nhom", srgb("#B9BEC3"), 0.3, 1.0),
    rod=mat("Inox", srgb("#DADDE0"), 0.15, 1.0),
    dark=mat("Khe tay nam", srgb("#2A2A2A"), 0.6),
)

COLS = {}


def col(name):
    if name not in COLS:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        COLS[name] = c
    return COLS[name]


def box(name, group, x0, x1, y0, y1, z0, z1, m, cut=True):
    xs, ys, zs = sorted((x0, x1)), sorted((y0, y1)), sorted((z0, z1))
    v = [(xs[i] * M, ys[j] * M, zs[k] * M) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.materials.append(MAT[m])
    o = bpy.data.objects.new(name, me)
    col(group).objects.link(o)
    d = sorted([xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0]], reverse=True)
    parts.append(dict(name=name, group=group, mat=m, cut=cut,
                      bbox=[xs[0], xs[1], ys[0], ys[1], zs[0], zs[1]],
                      L=round(d[0], 1), Wd=round(d[1], 1), Th=round(d[2], 1)))
    return o


def cyl(name, group, r, x0, x1, y, z, m, axis="X"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r * M, depth=abs(x1 - x0) * M)
    o = bpy.context.active_object
    o.name = name
    if axis == "X":
        o.rotation_euler = (0, math.pi / 2, 0)
        o.location = ((x0 + x1) / 2 * M, y * M, z * M)
    o.data.materials.append(MAT[m])
    for c in o.users_collection:
        c.objects.unlink(o)
    col(group).objects.link(o)
    return o


def build():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    pl, Hl = p["plinth"], p["H_low"]

    for c in range(2):
        x0, x1 = c * Wc, (c + 1) * Wc
        xm = (x0 + x1) / 2
        tag = "L" if c == 0 else "R"
        outer_left = c == 0
        # ---- module duoi
        for side, (sx0, sx1) in (("trai", (x0, x0 + T)), ("phai", (x1 - T, x1))):
            outer = (side == "trai" and outer_left) or (side == "phai" and not outer_left)
            box(f"Duoi-{tag}-vach-{side}", "Than", sx0, sx1, 0 if outer else y_in0, D, 0, Hl, "carcass")
            box(f"Noc-{tag}-vach-{side}", "Than", sx0, sx1, 0 if outer else y_in0, D, Hl, H, "carcass")
        box(f"Duoi-{tag}-day", "Than", x0 + T, x1 - T, 0, D, pl, pl + T, "carcass")
        box(f"Duoi-{tag}-tran", "Than", x0 + T, x1 - T, y_in0, D, Hl - T, Hl, "carcass")
        box(f"Duoi-{tag}-chan", "Than", x0 + T, x1 - T, 40, 40 + T, 0, pl, "carcass")
        box(f"Duoi-{tag}-vach-giua", "Than", xm - T / 2, xm + T / 2, y_in0, y_in1, zb, z_low_top, "carcass")
        for k, (bx0, bx1) in enumerate(((x0 + T, xm), (xm, x1 - T))):
            box(f"Duoi-{tag}-hau{k + 1}", "Than", bx0, bx1, y_in1, D, zb, z_low_top, "back")
        # ---- hop noc
        box(f"Noc-{tag}-day", "Than", x0 + T, x1 - T, y_in0, D, Hl, Hl + T, "carcass")
        box(f"Noc-{tag}-tran", "Than", x0 + T, x1 - T, 0, D, H - T, H, "carcass")
        box(f"Noc-{tag}-vach-giua", "Than", xm - T / 2, xm + T / 2, y_in0, y_in1, Hl + T, H - T, "carcass")
        box(f"Noc-{tag}-hau", "Than", x0 + T, x1 - T, y_in1, D, Hl + T, H - T, "back")

    # ---- noi that tung khoang
    bay_x = []
    for c in range(2):
        x0, x1 = c * Wc, (c + 1) * Wc
        xm = (x0 + x1) / 2
        bay_x += [(x0 + T, xm - T / 2), (xm + T / 2, x1 - T)]
    for b, (spec, (bx0, bx1)) in enumerate(zip(BAYS, bay_x)):
        n = f"K{b + 1}"
        for zt in spec["shelves"]:
            box(f"{n}-ke-{zt}", "Noi that", bx0 + 1, bx1 - 1, y_in0 + 10, y_in1, zt - T, zt, "interior")
        yr = (y_in0 + y_in1) / 2
        for zr in spec["rods"]:
            cyl(f"{n}-ong-treo-{zr}", "Phu kien", p["rod_d"] / 2, bx0, bx1, yr, zr, "rod")
            for xx in (bx0, bx1 - 8):
                bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.025, depth=0.008)
                o = bpy.context.active_object
                o.name = f"{n}-bat-ong-{zr}"
                o.rotation_euler = (0, math.pi / 2, 0)
                o.location = ((xx + 4) * M, yr * M, zr * M)
                o.data.materials.append(MAT["rod"])
                for cc in o.users_collection:
                    cc.objects.unlink(o)
                col("Phu kien").objects.link(o)
            parts.append(dict(name=f"{n}-ong-treo-{zr}", group="Phu kien", mat="rod", cut=False,
                              bbox=[bx0, bx1, yr - 12.5, yr + 12.5, zr - 12.5, zr + 12.5],
                              L=round(bx1 - bx0 - 2, 1), Wd=p["rod_d"], Th=p["rod_d"]))
        z = zb
        for k, h in enumerate(spec["drawers"]):
            fy0 = y_in0 + 10
            box(f"{n}-nk{k + 1}-mat", "Noi that", bx0 + 2, bx1 - 2, fy0, fy0 + T, z + 2, z + h - 2, "drawer")
            box(f"{n}-nk{k + 1}-khe-tay", "Noi that", bx0 + 120, bx1 - 120, fy0 - 0.5, fy0 + 1,
                z + h - 32, z + h - 20, "dark", cut=False)
            iw0, iw1 = bx0 + 12.7, bx1 - 12.7       # ray bi 12.7/ben
            by0, by1 = fy0 + T, fy0 + T + p["slide_len"]
            bz0, bz1 = z + 20, z + h - 40
            box(f"{n}-nk{k + 1}-hong-trai", "Noi that", iw0, iw0 + 15, by0, by1, bz0, bz1, "interior")
            box(f"{n}-nk{k + 1}-hong-phai", "Noi that", iw1 - 15, iw1, by0, by1, bz0, bz1, "interior")
            box(f"{n}-nk{k + 1}-hau", "Noi that", iw0 + 15, iw1 - 15, by1 - 15, by1, bz0, bz1, "interior")
            box(f"{n}-nk{k + 1}-day", "Noi that", iw0 + 15, iw1 - 15, by0, by1 - 15, bz0, bz0 + 9, "back")
            z += h

    # ---- ray + canh lua
    ztr = H - T - p["gap_top"]
    box("Ray-tren", "Ray", T, W - T, 5, p["DZ"] - 5, ztr, H - T, "alu", cut=False)
    box("Ray-duoi", "Ray", T, W - T, 5, p["DZ"] - 5, zb, zb + 10, "alu", cut=False)
    Wi = W - 2 * T
    dw = (Wi + (p["door_n"] - 1) * p["door_ov"]) / p["door_n"]
    dz0, dz1 = zb + p["gap_bot"], ztr + 15
    for i in range(p["door_n"]):
        front = i % 2 == 0
        yc = 30 if front else 72
        y0, y1 = yc - p["door_t"] / 2, yc + p["door_t"] / 2
        dx0 = T + i * (dw - p["door_ov"])
        g = f"Canh {i + 1}"
        box(f"Canh{i + 1}-tam", g, dx0 + 20, dx0 + dw - 20, y0 + 3, y1, dz0, dz1, "door", cut=False)
        box(f"Canh{i + 1}-khung-trai", g, dx0, dx0 + 20, y0 - 4, y1, dz0, dz1, "alu", cut=False)
        box(f"Canh{i + 1}-khung-phai", g, dx0 + dw - 20, dx0 + dw, y0 - 4, y1, dz0, dz1, "alu", cut=False)
        box(f"Canh{i + 1}-khung-tren", g, dx0 + 20, dx0 + dw - 20, y0, y1, dz1 - 25, dz1, "alu", cut=False)
        box(f"Canh{i + 1}-khung-duoi", g, dx0 + 20, dx0 + dw - 20, y0, y1, dz0, dz0 + 40, "alu", cut=False)
        # song lam: 1 thanh tron + Array
        n = int((dw - 40) // p["lam_pitch"])
        r = cyl(f"Canh{i + 1}-song", g, p["lam_r"], 0, 1, 0, 0, "door")
        r.rotation_euler = (0, 0, 0)
        r.scale = (1, 1, (dz1 - dz0 - 65) / 1)
        r.location = ((dx0 + 20 + (dw - 40 - (n - 1) * p["lam_pitch"]) / 2) * M,
                      (y0 + 3) * M, ((dz0 + 40 + dz1 - 25) / 2) * M)
        a = r.modifiers.new("Array", "ARRAY")
        a.use_relative_offset, a.use_constant_offset = False, True
        a.constant_offset_displace = (p["lam_pitch"] * M, 0, 0)
        a.count = n
    # ---- op lam song 2 vach ngoai: thanh nguyen cay H=2900, song dung
    if CL:
        for side, (cx0, cx1, sgn) in (("trai", (-CL, -CL + 6, -1)), ("phai", (W + CL - 6, W + CL, 1))):
            box(f"Op-lam-song-{side}", "Op lam song", cx0, cx1, 0, D, 0, H, "door", cut=False)
            n = int(D // p["lam_pitch"])
            r = cyl(f"Op-{side}-song", "Op lam song", p["lam_r"], 0, 1, 0, 0, "door")
            r.rotation_euler = (0, 0, 0)
            r.scale = (1, 1, H)
            xr = (cx0 if sgn < 0 else cx1) + sgn * (-p["lam_r"] + 6) * 0 + (0 if sgn < 0 else 0)
            r.location = ((cx0 + 6 if sgn > 0 else cx1 - 6) * M, ((D - (n - 1) * p["lam_pitch"]) / 2) * M, H / 2 * M)
            a = r.modifiers.new("Array", "ARRAY")
            a.use_relative_offset, a.use_constant_offset = False, True
            a.constant_offset_displace = (0, p["lam_pitch"] * M, 0)
            a.count = n
        parts.append(dict(name="Op-lam-song (2 vach)", group="Op lam song", mat="door", cut=False,
                          bbox=[-CL, W + CL, 0, D, 0, H], L=H, Wd=D, Th=CL))
    meta = dict(P=P, W_body=W, CL=CL, BAYS=BAYS, bay_x=bay_x, door_w=dw, door_h=dz1 - dz0, door_z=[dz0, dz1])
    return meta


def setup_render(out):
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1400
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in
        sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
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
    # san
    box("San", "Moi truong", -1500, W + 1500, -2500, D + 50, -5, 0, "back", cut=False)
    box("Tuong", "Moi truong", -1500, W + 1500, D, D + 10, 0, 3200, "back", cut=False)
    os.makedirs(out, exist_ok=True)


def cam(name, loc, rot, ortho=None, lens=35):
    cd = bpy.data.cameras.new(name)
    cd.clip_end = 100
    if ortho:
        cd.type = "ORTHO"
        cd.ortho_scale = ortho
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
    if move:
        for nm_prefix, dx in move.items():
            for o in bpy.data.objects:
                if o.name.startswith(nm_prefix):
                    saved[o.name] = o.location.x
                    o.location.x += dx * M
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for nm, x in saved.items():
        bpy.data.objects[nm].location.x = x


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[argv.index("--out") + 1] if "--out" in argv else "renders"
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, out)
    meta = build()
    setup_render(out)
    doors = [g for g in COLS if g.startswith("Canh")]
    ortho = max(W, H) * 1.32 * M
    front = cam("Cam-truoc", (W / 2, -6000, H / 2), (90, 0, 0), ortho=ortho)
    iso = cam("Cam-iso", (-350, -2650, 1850), (82, 0, -24), lens=18)
    shift = meta["door_w"] - P["door_ov"]
    shot(front, os.path.join(out, "01-mat-truoc-dong-cua.png"))
    shot(front, os.path.join(out, "02-mat-truoc-bo-tri-trong.png"), hide=doors + ["Ray"])
    shot(iso, os.path.join(out, "03-iso-mo-khoang-1-4.png"), move={"Canh1-": shift, "Canh4-": -shift})
    shot(iso, os.path.join(out, "04-iso-khong-cua.png"), hide=doors)
    shot(iso, os.path.join(out, "05-iso-mo-khoang-2-3.png"), move={"Canh2-": -shift, "Canh3-": shift})
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(here, "wardrobe.blend"))
    with open(os.path.join(here, "parts.json"), "w", encoding="utf-8") as f:
        json.dump(dict(meta=meta, parts=parts), f, ensure_ascii=False, indent=1)
    print("BUILD OK", len(parts), "parts")


main()
