# CLI (fc_cli.py): xi-lanh RACK -> PISTON (Tuan 2026-10-25). Rack_Elbow lech khi len xuong (thanh rang 1 phia, chi ranh
# truot don) -> Tuan chon xi-lanh piston kieu Cyberbrick Excavator; khong co N20 nen dung lai motor 030 + hop so:
# hop so dat CANH ong, z28 (truc ra O5,3, lo 2 mat vat nhu Worm) -> z12 (dau ty ren M3 roi, kep dai oc) -> piston kep dai oc
# M3 trong lo vuong (chong xoay) -> ty rong (ty ren chui vao) -> mat ty cu. Giu chot A/B/C/D, Boom, cang tay.
# Concept + do khoang trong: scripts/render_concept_piston_030.py, docs/reports/pushrod-arm-actuator-alternatives.md muc 4d.
# Doi trong model (moi tag Shoulder/Elbow, he xi-lanh = Placement Rack_<tag> tu the goc):
#   Housing_<tag>  : hinh moi (tai chot cu + buong banh rang + ong + bac dan huong + tam ga hop so + 2 vau), Placement = he xi-lanh
#   Rack_<tag>     : doi Label -> Piston_rod_<tag> (piston + ty + mat ty cu), giu Placement (he xi-lanh)
#   CB_030_gearbox_<tag>: dat lai (truc ra quay -x, canh ong)
#   them Gear_z28_<tag>, Gear_z12_<tag>, LK_Threaded_rod_M3_L<n>_<tag>, LK_Nut_M3_gear_<tag>, LK_Nut_M3_piston_<tag>
#   xoa Worm_, Pinion_WormWheel_, Washer_shaft_, M2_5x6_shaft_, Pin_gearbox_ (backup truoc khi sua)
import json
import math
import sys

sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
LOG = open(P + "check/piston-cylinder-2026-10-25.log", "w", encoding="utf-8")
doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-piston-cylinder")
OBJ = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
GRP = {o.Label: o for o in doc.Objects if o.isDerivedFrom("App::DocumentObjectGroup")}
REST = {o.Name: o.Placement for o in OBJ.values()}   # dang o tu the goc (guard)
STEP = ("D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/community/cyberbrick-official/models/"
        "la024-030-micro-dc-motor-with-sh1-0/030-micro-dc-motor-with-sh1-0-reducer.step")
OUT_G = V(0, 15.2, 11.15)   # tam truc ra tai mat vo hop so (he hop so, do tren STEP hang - xem 2026-10-24_cylinder_030_gearbox.py)
SHAFT_L, SHAFT_R, SHAFT_FLAT = 8.1, 2.65, 1.8
PIN_G = [(-9.0, -4.02), (9.0, -4.02)]   # 2 lo Ø4 nap hop so (he hop so x, z), truc // truc ra

FIT = 0.3                  # khe truot / an khop (Tuan 2026-10-24)
ZG, ZS_ = 28, 12           # banh rang truc hop so, banh rang ty ren (m1)
D = (ZG + ZS_) / 2         # 20 mm: hop so (nua rong 11) nam ngoai ong r 8,5
GW = 4.5                   # be rong banh rang
PIST_L, NUT_AF, NUT_T = 8.0, 5.5, 2.4    # piston dai, dai oc luc giac M3 (DIN 934)
ROD_Y, ROD_Z, ROD_R = 3.0, 4.0, 1.5      # ty: day 6 (= mat ty cu / rack, lot ranh Boom vai), cao 8, bo goc 1,5
BORE_SCREW = 1.8                         # lo ty ren M3 trong ty (Ø3,6)
BUSH_L = 6.0
Y_FLAT_IN = 0.5                          # vo xi-lanh cat phang mat -y, an vao ong 0,5 mm (in nam)

CFG = {  # x0 = dau tuong sau buong banh rang; r_tube; bore = canh lo vuong piston; Lmin/L0/Lmax; zs = phia hop so
    "Elbow": dict(x0=18.0, r_tube=8.5, bore=11.0, Lmin=92.0, L0=None, Lmax=128.0, zs=1, pins=("C", "D")),
    "Shoulder": dict(x0=11.0, r_tube=7.0, bore=9.4, Lmin=92.0, L0=None, Lmax=118.0, zs=-1, pins=("A", "B")),
}
A20 = math.radians(20)


def invf(a): return math.tan(a) - a


def gear_pts(cy, cz, z, m=1.0, ph=0.0, bl=0.15, n_=6):   # nhu 2026-10-22_build_pushrods_v3.py (x = 0), mat phang y-z
    rp = m * z / 2; rb = rp * math.cos(A20); ra = rp + m; rf = rp - 1.25 * m
    psi = (math.pi / 2) / z - bl / (2 * rp); r0 = max(rb, rf)
    def th(r): return psi + invf(A20) - invf(math.acos(min(1, rb / r)))
    pts = []
    for i in range(z):
        c = math.radians(ph) + 2 * math.pi * i / z; rs = [r0 + (ra - r0) * k / n_ for k in range(n_ + 1)]
        if rf < rb: pts.append((rf, c - th(rb)))
        pts += [(r, c - th(r)) for r in rs] + [(r, c + th(r)) for r in reversed(rs)]
        if rf < rb: pts.append((rf, c + th(rb)))
        a0 = c + th(r0); a1 = c + 2 * math.pi / z - th(r0); pts += [(rf, a0 + (a1 - a0) * k / 3) for k in range(1, 3)]
    return [(cy + r * math.cos(a), cz + r * math.sin(a)) for r, a in pts]


def prism_x(pts, x0, x1):   # da giac (y, z) dun doc x
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(x1 - x0, 0, 0))


def xcyl(r, x0, x1, y=0.0, z=0.0): return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def box(x0, x1, y0, y1, z0, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def rrect(hy, hz, r, x0, x1):   # hinh chu nhat bo goc doc x, tam truc
    s = box(x0, x1, -hy + r, hy - r, -hz, hz).fuse(box(x0, x1, -hy, hy, -hz + r, hz - r))
    for sy in (-1, 1):
        for sz in (-1, 1):
            s = s.fuse(xcyl(r, x0, x1, sy * (hy - r), sz * (hz - r)))
    return s.removeSplitter()


def hexagon(af, x0, x1, rot=0.0):
    rc = af / math.sqrt(3)
    return prism_x([(rc * math.cos(math.radians(rot + 60 * k)), rc * math.sin(math.radians(rot + 60 * k))) for k in range(6)], x0, x1)


def build(tag, c):
    """Chi tiet trong he xi-lanh, tu the goc (L0). Tra dict ten -> (shape, nhom 'H' gan vo | 'R' theo ty)."""
    zs, x0, rt, bore = c["zs"], c["x0"], c["r_tube"], c["bore"]
    xg0, xg1 = x0 + 1.5, x0 + 1.5 + GW + 2 * FIT       # khoang banh rang (khe doc truc 0,3 moi ben)
    xw1 = xg1 + 1.5                                      # het tuong truoc
    xface = xw1 + 0.5                                    # mat vo hop so (quay ve -x)
    xp_ret = xw1 + 0.5                                   # duoi piston khi rut het
    stroke = c["Lmax"] - c["Lmin"]
    xt1 = xp_ret + PIST_L + stroke + BUSH_L              # het ong
    off = c["L0"] - c["Lmin"]                            # ty o tu the goc lech khoi rut het
    gz = zs * D
    Y_FLAT = rt - Y_FLAT_IN
    # ---- vo (Cyl_Housing): tai chot cu + co + buong banh rang + ong + bac dan huong + tam ga hop so ----
    old = OBJ["Housing_" + tag].Shape.copy(); old.transformShape(REST[OBJ["Rack_" + tag].Name].inverse().toMatrix())
    lug = old.common(box(-8, 9.5, -3.5, 3.5, -9, 9))
    neck = box(6, x0 + 0.5, -3, 3, -5.5, 5.5)
    cham = xcyl(8.7, x0, xw1).cut(xcyl(7.6, xg0, xg1)).fuse(xcyl(8.7, x0, xg0))     # vo buong + tuong sau dac
    cham = cham.cut(box(xg0, xg1, -9.5, 9.5, zs * 3.5, zs * 40))                     # cua so: z28 an vao + tha banh rang
    cham = cham.cut(box(xg1 - 0.1, xw1 + 0.1, -BORE_SCREW, BORE_SCREW, 0, zs * 20))  # rang chu U tuong truoc cho ty ren
    # lo piston CHU NHAT 6,6 x bore (piston day 6 = ty -> ty + piston in nam phang khong support, 2026-10-25)
    tube = xcyl(rt, xw1 - 0.5, xt1).cut(rrect(ROD_Y + FIT, bore / 2, 1.0, xw1, xt1 - BUSH_L))
    tube = tube.cut(rrect(ROD_Y + FIT, ROD_Z + FIT, ROD_R + FIT, xt1 - BUSH_L - 0.1, xt1 + 0.1))
    tube = tube.cut(xcyl(BORE_SCREW, xg1, xw1 + 0.6))
    # tam ga hop so: mat vo hop so (STEP: x +-11, z -32,2..22,15 quanh truc ra z 11,15 -> he xi-lanh y -11..43, z gz+-11)
    # tam ga quanh truc + 2 lo chot. Lo truc r 4,2: chan truc ra co go r ~3,7 (lan dau r 3,2 -> chong 7 mm3)
    plate = box(xface - 2.0, xface, -Y_FLAT, 19.5, gz - 11, gz + 11).cut(xcyl(4.2, xface - 2.1, xface + 0.1, 0, gz))
    pin_xy = [(15.17, gz + zs * px) for px, _ in PIN_G]                               # 2 lo O4 nap hop so (truc // x)
    for py, pz in pin_xy:
        plate = plate.cut(xcyl(2.05, xface - 2.1, xface + 0.1, py, pz))
    web = box(xw1 - 0.5, xface, -3, 3, 0, zs * (D - 7))     # noi tam ga voi ong, dung truoc loi truc hop so (r 1,4)
    hous = lug.fuse([neck, cham, tube, plate, web]).removeSplitter()
    hous = hous.cut(xcyl(5.6, xg0 - 0.1, xg1 + 0.1, 0, gz))                           # khong cham z28 (dinh r 15)
    hous = hous.cut(box(-20, 200, -Y_FLAT - 10, -Y_FLAT, -60, 60)).removeSplitter()   # day phang de in nam (mat -y)
    # ---- hop so 030 (STEP hang): he hop so -> he xi-lanh: c_x = -g_y, c_y = -g_z, c_z = g_x (det +1), truc ra quay -x ----
    gb = Part.read(STEP)
    M = App.Matrix(0, -1, 0, 0, 0, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 1)
    gb = gb.transformGeometry(M)
    o = M.multiply(OUT_G); gb.translate(V(xface, 0, gz) - V(o.x, o.y, o.z))
    # ---- banh rang ----
    # lo 2 mat vat cho truc ra: do huong + kich thuoc mat vat tren STEP nhu Worm (2026-10-24_cylinder_030_gearbox.py,
    # da in + lap vua). Lan dau 2026-10-25 gia dinh mat vat vuong goc z -> chong 10 mm3 (mat vat nam xeo).
    raw = Part.read(STEP)
    sol = [q for q in raw.Solids if abs(q.BoundBox.YMax - 23.3) < 0.05][0]
    out = [math.radians(k) for k in range(360) if not sol.isInside(
        V(2.4 * math.cos(math.radians(k)), 20.0, 11.15 + 2.4 * math.sin(math.radians(k))), 1e-4, True)]
    assert out, "khong thay mat vat tren truc ra"
    an = math.atan2(sum(math.sin(2 * t) for t in out), sum(math.cos(2 * t) for t in out)) / 2
    fd = V(math.cos(an), 0, math.sin(an))
    pr = sol.common(Part.makeBox(30, 30, 30, V(-15, OUT_G.y + 0.5, OUT_G.z - 15)))
    pts = [q for e in pr.Edges for q in e.discretize(Deflection=0.005)]
    s_r = max(math.hypot(q.x, q.z - OUT_G.z) for q in pts)
    s_f = max(abs(q.x * fd.x + (q.z - OUT_G.z) * fd.z) for q in pts)
    assert s_f < s_r - 0.3, ("khong do duoc mat vat", s_r, s_f)
    nd = M.multiply(fd); nd = V(nd.x, nd.y, nd.z); nd.normalize()          # phap tuyen mat vat (he xi-lanh, mat y-z)
    print(tag, "truc ra r %.3f mat vat %.3f phap tuyen %s" % (s_r, s_f, nd), file=LOG, flush=True)
    sock = xcyl(s_r + FIT, xg0 - 1, xg1 + 1, 0, gz)
    slab = box(xg0 - 1, xg1 + 1, -10, 10, -s_f - FIT, s_f + FIT)
    slab.rotate(V(0, 0, 0), V(1, 0, 0), math.degrees(math.atan2(-nd.y, nd.z)))  # quay x: (0,0,1) -> nd
    slab.translate(V(0, 0, gz))
    sock = sock.common(slab)
    g28 = prism_x(gear_pts(0, gz, ZG), xg0 + FIT, xg1 - FIT).cut(sock)   # truc ra 8,1 mm phu het be rong banh rang
    ph12 = min((prism_x(gear_pts(0, 0, ZS_, ph=k * 3.75), xg0 + FIT, xg1 - FIT).common(g28).Volume, k * 3.75)
               for k in range(8))[1]   # pha z12: it chong lan voi z28 nhat
    g12 = prism_x(gear_pts(0, 0, ZS_, ph=ph12), xg0 + FIT, xg1 - FIT).cut(hexagon(NUT_AF + 0.2, xg0, xg0 + 2.6)).cut(xcyl(1.6, xg0 - 1, xg1 + 1))
    nut_g = hexagon(NUT_AF, xg0 + FIT, xg0 + FIT + NUT_T).cut(xcyl(1.5, xg0, xg0 + 3))
    nut_pos = xp_ret + PIST_L / 2
    screw_x1 = nut_pos + stroke + NUT_T / 2 + 2.5
    screw = xcyl(1.5, xg0 + FIT, screw_x1)
    # chot gan hop so (nhu Pin_gearbox 2026-10-24: in rieng dac, lap chat O3,9 vao lo O4 nap hop so): mu sau tam ga
    pins = Part.makeCompound([xcyl(1.95, xface - 2.0, xface + 7.0, py, pz).fuse(xcyl(3.0, xface - 3.0, xface - 2.0, py, pz))
                              for py, pz in pin_xy])
    # ---- piston + ty (theo tu the goc: +off) ----
    xp = xp_ret + off
    sp = bore - 2 * FIT
    piston = rrect(ROD_Y, sp / 2, 0.8, xp, xp + PIST_L)
    # dai oc luc giac M3: 2 mat phang ep z (khong xoay), 2 goc nho ra mat y (3,18 < thanh lo 3,3 giu lai) - lap tu canh y
    piston = piston.cut(hexagon(NUT_AF + 0.2, xp + PIST_L / 2 - (NUT_T + 0.3) / 2, xp + PIST_L / 2 + (NUT_T + 0.3) / 2, 0))
    L0 = c["L0"]
    rack = OBJ["Rack_" + tag].Shape.copy(); rack.transformShape(REST[OBJ["Rack_" + tag].Name].inverse().toMatrix())
    eye = rack.common(box(L0 - 6.5, L0 + 9, -3.5, 3.5, -9, 9))
    rod = piston.fuse([rrect(ROD_Y, ROD_Z, ROD_R, xp + PIST_L - 0.5, L0 - 5.0), eye]).removeSplitter()
    rod = rod.cut(xcyl(BORE_SCREW, xp - 0.1, screw_x1 + off + 0.8))
    nut_p = hexagon(NUT_AF, xp + PIST_L / 2 - NUT_T / 2, xp + PIST_L / 2 + NUT_T / 2, 0).cut(xcyl(1.5, xp, xp + PIST_L))
    info = dict(stroke=stroke, tube_end=round(xt1, 1), tube_od=2 * rt, screw_len=round(screw_x1 - xg0 - 0.25, 1),
                piston_ret=[round(xp_ret, 1), round(xp_ret + PIST_L, 1)], eye_clear_ret=round(c["Lmin"] - xt1, 1),
                rod_bore_end_rest=round(screw_x1 + off + 0.8, 1), mm_per_out_rev=round(0.5 * ZG / ZS_, 2))
    parts = {"Cyl_Housing": (hous, "H"), "CB_030_gearbox_new": (gb, "H"), "Gear_z28": (g28, "H"), "Pin_gearbox": (pins, "H"), "Gear_z12_screw": (g12, "H"),
             "Nut_M3_gear": (nut_g, "H"), "Screw_M3": (screw, "H"), "Piston_rod": (rod, "R"), "Nut_M3_piston": (nut_p, "R")}
    return parts, info



for tag, c in CFG.items():
    F = OBJ["Rack_" + tag].Placement
    c["L0"] = {"Shoulder": 99.7764836463904, "Elbow": 121.59676825402742}[tag]   # chot-chot tu the goc (sim: L1_0, L2_0)
    parts, info = build(tag, c)
    print(tag, info, file=LOG, flush=True)
    for nm, (sh, grp) in parts.items():
        assert sh.isValid() and len(sh.Solids) >= 1, (tag, nm)
    g = GRP["PushRod_" + tag]

    def put(obj_or_label, shape, label=None):
        o = OBJ.get(obj_or_label) if isinstance(obj_or_label, str) else obj_or_label
        if o is None:
            o = doc.addObject("Part::Feature", label.replace(".", "_")); g.addObject(o)
        o.Label = label or o.Label
        # Placement cua shape (translate() ghi vao Placement, transformShape tinh tien cung chi doi Placement) phai GOP
        # vao Placement object: lan chay dau 2026-10-25 dat thang F -> hop so 030 nam o goc chot.
        pl = shape.Placement
        o.Placement = App.Placement(); o.Shape = shape; o.Placement = F.multiply(pl)
        OBJ[o.Label] = o
        if (label or o.Label).startswith("Piston_rod"):
            assert pl.isIdentity(), "Piston_rod phai co Placement = he xi-lanh (macro lay he toa do tu no)"
        return o
    put("Housing_" + tag, parts["Cyl_Housing"][0])
    put("Rack_" + tag, parts["Piston_rod"][0], "Piston_rod_" + tag)
    put("CB_030_gearbox_" + tag, parts["CB_030_gearbox_new"][0])
    put(None, parts["Gear_z28"][0], "Gear_z28_" + tag)
    put(None, parts["Gear_z12_screw"][0], "Gear_z12_" + tag)
    put(None, parts["Screw_M3"][0], "LK_Threaded_rod_M3_L%d_%s" % (math.ceil(info["screw_len"] / 5) * 5, tag))
    put(None, parts["Nut_M3_gear"][0], "LK_Nut_M3_gear_" + tag)
    put(None, parts["Nut_M3_piston"][0], "LK_Nut_M3_piston_" + tag)
    put(None, parts["Pin_gearbox"][0], "Pin_gearbox_new_" + tag)
    for old in ("Worm_", "Pinion_WormWheel_", "Washer_shaft_", "M2_5x6_shaft_", "Pin_gearbox_"):
        if old + tag in OBJ:
            doc.removeObject(OBJ.pop(old + tag).Name)
    OBJ["Pin_gearbox_new_" + tag].Label = "Pin_gearbox_" + tag   # ten cu (print.yaml/BOM), chot moi
doc.recompute()
rp = P + "pushrod_arm_rest.json"
rest = json.load(open(rp))
for o in doc.Objects:
    if o.isDerivedFrom("Part::Feature"):
        rest[o.Name] = [list(o.Placement.Base), list(o.Placement.Rotation.Q)]
for n in list(rest):
    if doc.getObject(n) is None:
        rest.pop(n)
json.dump(rest, open(rp, "w"))
print("saved", se.save(doc, gui_from=bk), "backup", bk, file=LOG, flush=True)
