"""Ga cam bien tay thang v2 - SolidCraft. So lieu: params.json (goc = tam dai oc D, Z=0 mat tay thang).
Vien: chu nhat tren (E1 trai, E2 tren, E3 phai) + doan tiep tuyen E4 + cung day E5 (R = R_mep + khe + thanh, tam D)
+ cung vanh om E6 + bo noi E7 vao chan E1. Note ma canh + tham so ten ro trong .sc.
Ra: brake-sensor-mount.sc, stl/mount.stl (huong in: mat tren up xuong ban), build-report.json, edges.json,
../review/overlay.png, ../review/edges-named.png. Chay: python build_mount.py"""
import json, math, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get('SOLIDCRAFT_CLI', r'C:\Program Files\SolidCraft\solidcraft-cli.exe')
PHOTO = r"D:/HONOR Share/Honor Share/IMG_20261113_085228_edit_859872405454222.jpg"
P = json.load(open(os.path.join(HERE, 'params.json'), encoding='utf-8'))
BUILD = os.path.join(HERE, 'build'); STLD = os.path.join(HERE, 'stl')
os.makedirs(BUILD, exist_ok=True); os.makedirs(STLD, exist_ok=True)
OX, OY = P['img_origin_px']; PA, BB, L = P['pin_a'], P['boss_b'], P['lip']
K = math.hypot(PA['px'][0] - BB['px'][0], PA['px'][1] - BB['px'][1]) / P['C_mm']   # px/mm theo C do that
H = P['standoff']; T = P['plate_t']; Z1 = H + T                                    # tam ga z H..Z1
mm = lambda p: [round((p[0] - OX) / K, 3), round((OY - p[1]) / K, 3)]
pa, hb = mm(PA['px']), mm(BB['px'])
hb = [round(hb[0] + BB.get('dx_mm', 0), 3), round(hb[1] + BB.get('dy_mm', 0), 3)]   # Tuan chinh vi tri B
bz0 = BB.get('z0', 0.0)   # mat duoi tru B (am = xuong thap hon mat tay thang)
pol = lambda r, a: [round(r * math.cos(a), 3), round(r * math.sin(a), 3)]

r_in = L['R'] + L['gap']; R = r_in + L['wall']          # R = ban kinh vien day (E5 + E6), tam D
xr, yt = P['right_x'], P['top_y']
xl = xr - P['E2']; y1 = yt - P['E1']; y3 = yt - P['E3']; rf = P['fillet_E1']
if P.get('fit_switch'):   # v3.6 (Tuan): tam ga chua tron cong tac (mep phai + day cong tac)
    _S = P['sensor']; _sp = _S['place']
    _sx1 = xl + _sp['dx'] + _S['W']; _sy0 = yt + _sp['dy'] - _S['H']
    xr = max(xr, round(_sx1 + P['fit_switch'].get('margin', 0.0), 3)); y3 = min(y3, round(_sy0 - P['fit_switch'].get('margin', 0.0), 3))
    if 'y3' in P['fit_switch']: y3 = min(y3, P['fit_switch']['y3'])   # v3.8 Tuan: keo dai E3 xuong cho de khong tho
d = math.hypot(xr, y3); at = math.atan2(y3, xr) - math.acos(R / d)   # tiep tuyen tu chan E3, nhanh duoi
a_top = math.pi - math.asin(min(y1 / R, 1.0))                        # cung gap do cao chan E1 (phia trai)
a0, a1 = math.radians(L['a0']), math.radians(L['a1'])

AL = P.get('arc_left')
if AL:
    # v3.3 (Tuan): 1 cung tron lien tu chan E1 -> mep trai (cach E1 'offset' mm) -> day (y = bottom_y) -> tiep tuyen E4
    # tam (ac_x, ac_y), ban kinh ar: ac_x - ar = xl - off ; ac_y - ar = yb ; qua (xl, y1)
    off, yb = AL['offset_from_E1'], AL['bottom_y']
    def _arc(yb_):
        u, w = off, y1 - yb_                               # (u - ar)^2 + (w - ar)^2 = ar^2
        ar_ = (u + w) - math.sqrt((u + w) ** 2 - (u * u + w * w))
        return ar_, (xl - off + ar_, yb_ + ar_)
    ar, ac = _arc(yb)
    # v3.6 (Tuan): cung phai om tron vau L2 + tai L (ban kinh wrap_L) - ha day toi khi du
    if AL.get('wrap_L'):
        _S = P['sensor']; _sp = _S['place']
        _sx0 = xl + _sp['dx']; _sy0 = yt + _sp['dy'] - _S['H']
        _pl = (_sx0 + _sp['L_from_plunger'], _sy0 - _sp['L_below_bottom'])
        while math.dist(_pl, ac) + AL['wrap_L'] > ar:
            yb -= 0.05; ar, ac = _arc(yb)
    pc = lambda a: [round(ac[0] + ar * math.cos(a), 3), round(ac[1] + ar * math.sin(a), 3)]
    dx_, dy_ = xr - ac[0], y3 - ac[1]; dd = math.hypot(dx_, dy_)
    at2 = math.atan2(dy_, dx_) - math.acos(ar / dd)        # tiep tuyen tu chan E3, nhanh duoi
    a_e1 = math.atan2(y1 - ac[1], xl - ac[0])              # diem chan E1 tren cung
    # cung chay theo chieu kim dong ho tu at2 (duoi phai) qua day, trai, len toi chan E1
    angs_ = np.linspace(at2, a_e1 - 2 * math.pi, 90) if a_e1 > at2 else np.linspace(at2, a_e1, 90)
    poly = [[xl, yt], [xr, yt], [xr, y3]] + [pc(a) for a in angs_]
    at = at2
else:
    poly = [[xl, yt], [xr, yt], [xr, y3]]                                # E2, E3
    poly += [pol(R, a) for a in np.linspace(at, a1 - 2 * math.pi, 40)]   # E4 (doan) + E5 cung day
    poly += [pol(R, a) for a in np.linspace(a1, a0, 16)[1:]]             # E6 vanh om
    poly += [pol(R, a) for a in np.linspace(a0, a_top, 6)[1:]]           # tiep cung toi do cao chan E1
    fc = (xl - rf, y1 + rf)                                              # E7: doan ngang + bo lom R=rf vao E1
    poly.append([round(xl - rf, 3), round(y1, 3)])
    poly += [[round(fc[0] + rf * math.cos(a), 3), round(fc[1] + rf * math.sin(a), 3)] for a in np.linspace(-math.pi / 2, 0, 8)[1:]]
lip = [pol(R, a) for a in np.linspace(a0, a1, 16)] + [pol(r_in, a) for a in np.linspace(a1, a0, 16)]
if AL:   # v3.4 (Tuan): vanh om chay HET cung vien E5 (chan E1 -> qua tru L -> E4), bam theo cung vien
    lw = L['wall']
    # v3.6: vanh giu cung CU (bottom_y goc) - chi vien tam noi rong; vanh nam duoi tam (z -depth..H)
    lar, lac = _arc(AL['bottom_y'])
    _xr0, _y30 = P['right_x'], yt - P['E3']                # goc chan E3 cu -> diem dau vanh E6a cu
    _d0 = math.hypot(_xr0 - lac[0], _y30 - lac[1])
    _a0 = math.atan2(_y30 - lac[1], _xr0 - lac[0]) - math.acos(lar / _d0)
    _ae = math.atan2(y1 - lac[1], xl - lac[0])
    l_angs = np.linspace(_a0, _ae - 2 * math.pi if _ae > _a0 else _ae, 90)
    ri = lar - lw
    lpc = lambda a: [round(lac[0] + lar * math.cos(a), 3), round(lac[1] + lar * math.sin(a), 3)]
    pci = lambda a: [round(lac[0] + ri * math.cos(a), 3), round(lac[1] + ri * math.sin(a), 3)]
    # v3.5 (Tuan): bo doan dau vanh phia E6b (chan E1) dai cut_E6b mm - doan nay can khi bop
    step = abs(l_angs[1] - l_angs[0]) * lar
    k = int(round(L.get('cut_E6b', 0.0) / step))
    angs_lip = l_angs[:len(l_angs) - k] if k else l_angs
    lip = [lpc(a) for a in angs_lip] + [pci(a) for a in angs_lip[::-1]]
    r_in, R = ri, lar

cmd = []
A = lambda c, **p: cmd.append({"command": c, "params": p})
A("sketch.create", plane={"origin": [0, 0, H], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
A("sketch.line", points=poly, closed=True); A("sketch.finish")
A("solid.extrude", distance=T, operation="new_body", body_name="mount")
J = {"operation": "join", "targets": ["mount"]}; C = {"operation": "cut", "targets": ["mount"]}
A("sketch.create", plane={"origin": [0, 0, -L['depth']], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
A("sketch.line", points=lip, closed=True); A("sketch.finish")
A("solid.extrude", distance=L['depth'] + H, **J)
A("solid.cylinder", diameter=PA['shoulder_d'], height=H + 0.5, base=[pa[0], pa[1], 0], axis="Z", **J)
A("solid.cylinder", diameter=PA['d'], height=PA['len'] + 0.5, base=[pa[0], pa[1], -PA['len']], axis="Z", **J)
A("solid.cylinder", diameter=BB['od'], height=H - bz0 + 0.5, base=[hb[0], hb[1], bz0], axis="Z", **J)
A("solid.cylinder", diameter=BB['id'], height=Z1 - bz0 + 0.2, base=[hb[0], hb[1], bz0 - 0.1], axis="Z", **C)

# --- cong tac den phanh: up mat P1 xuong tam ga, nut N chia -X (ve E1) ---
S = P['sensor']; SP = S['place']
sx0 = xl + SP['dx']                       # mat co nut N
sy1 = yt + SP['dy']                       # canh tren than
sx1, sy0 = sx0 + S['W'], sy1 - S['H']
p1 = [round(sx0 + SP['P1_from_plunger'], 3), round(sy1 - SP['P1_from_top'], 3)]
pl = [round(sx0 + SP['L_from_plunger'], 3), round(sy0 - SP['L_below_bottom'], 3)]
post_h = SP.get('post_h', S['T'] - SP['ear_t'])   # ong dem L1 (v3.7 Tuan: 4,85)
MG = P.get('merge', False)                # v3.7 Tuan: gop de vao ga thanh 1 khoi
SB = P['switch_base']; bt = SB['t']; JT = P['joint']
ZS = Z1 + bt                              # v3.6: de nam tren mat ga (z Z1..ZS), cong tac nam tren de
jp_ = JT['pos']                           # chot noi de -> ga
# ga: o chot rong O hole_d sau depth tu mat tren + vau duoi tam
if not MG:
    A("solid.cylinder", diameter=JT['boss_od'], height=JT['depth'] - T + 1.0 + 0.3, base=[jp_[0], jp_[1], Z1 - JT['depth'] - 1.0], axis="Z", **J)
    A("solid.cylinder", diameter=JT['hole_d'], height=JT['depth'] + 0.1, base=[jp_[0], jp_[1], Z1 - JT['depth']], axis="Z", **C)
# tai L: ga co vau O post_d (tam + 3 mm xuong duoi) lo O3,4 cho oc M4 tu ren
boss_dn = 3.0
A("solid.cylinder", diameter=SP['post_d'], height=T + boss_dn, base=[pl[0], pl[1], H - boss_dn], axis="Z", **J)
A("solid.cylinder", diameter=SP['post_hole_d'], height=T + boss_dn + 0.2, base=[pl[0], pl[1], H - boss_dn - 0.1], axis="Z", **C)
# ong dem roi giua de va tai L
A("solid.cylinder", diameter=SP['post_d'], height=post_h, base=[pl[0], pl[1], ZS], axis="Z", operation="new_body", body_name="spacer")
A("solid.cylinder", diameter=4.4, height=post_h + 0.2, base=[pl[0], pl[1], ZS - 0.1], axis="Z", operation="cut", targets=["spacer"])
# than cong tac (chi de xem, khong in)
A("sketch.create", plane={"origin": [0, 0, ZS], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
A("sketch.rectangle.two_point", p0=[sx0, sy0], p1=[sx1, sy1]); A("sketch.finish")
A("solid.extrude", distance=S['T'], operation="new_body", body_name="switch")
A("solid.cylinder", diameter=SP['N_d'], height=S['N_stick_out'], base=[sx0 - S['N_stick_out'], sy1 - SP['N_from_top'], ZS + S['T'] / 2],
  axis="X", operation="join", targets=["switch"])
A("solid.cylinder", diameter=8.0, height=SP['ear_t'], base=[pl[0], pl[1], ZS + post_h], axis="Z", operation="join", targets=["switch"])
A("appearance.assign", bodies=["switch"], color="#333333", opacity=0.6)

# --- ma canh (note trong .sc) + tham so ten ro ---
p4 = pol(R, at)
EDGES = [
    {"ma": "E1", "ten": "mep trai (canh khoi luc giac)", "dai_mm": P['E1'], "nhan": [xl - 3, (yt + y1) / 2]},
    {"ma": "E2", "ten": "canh tren", "dai_mm": round(xr - xl, 2), "nhan": [(xl + xr) / 2, yt + 1.5]},
    {"ma": "E3", "ten": "canh phai (sat xi-lanh)", "dai_mm": round(yt - y3, 2), "nhan": [xr + 2.5, (yt + y3) / 2]},
    {"ma": "E4", "ten": "doan thang tiep tuyen", "dai_mm": round(math.dist([xr, y3], p4), 2),
     "nhan": [(xr + p4[0]) / 2 + 2.5, (y3 + p4[1]) / 2]},
    {"ma": "E5", "ten": "cung day R%.1f tam D (gop E5-E11 cu)" % R, "dai_mm": round(R * abs(at - (a1 - 2 * math.pi)), 2),
     "nhan": pol(R + 2.5, -math.pi / 2)},
    {"ma": "E6", "ten": "cung vanh om (E12 cu) R trong %.1f / ngoai %.1f, sau %.1f" % (r_in, R, L['depth']),
     "dai_mm": round(R * abs(a1 - a0), 2), "nhan": pol(R + 3.5, (a0 + a1) / 2)},
    {"ma": "E7", "ten": "bo noi cung -> chan E1 (E13 cu), bo R%.1f" % rf, "dai_mm": None, "nhan": [xl - 4, y1 - 1.5]},
]
if AL:   # v3.3: E5+E6+E7 thanh 1 cung lien; E6 chi con la vanh om duoi tam
    p4 = pc(at2)
    EDGES[3] = {"ma": "E4", "ten": "doan thang tiep tuyen", "dai_mm": round(math.dist([xr, y3], p4), 2),
                "nhan": [(xr + p4[0]) / 2 + 2.5, (y3 + p4[1]) / 2]}
    EDGES[4] = {"ma": "E5", "ten": "cung lien R%.1f (chan E1 -> trai -> day -> E4, gop E5-E7)" % ar,
                "dai_mm": round(ar * abs(angs_[-1] - angs_[0]), 2),
                "nhan": [round(ac[0] + (ar + 2.5) * math.cos(-2.4), 2), round(ac[1] + (ar + 2.5) * math.sin(-2.4), 2)]}
    EDGES[5] = {"ma": "E6", "ten": "vanh om: R ngoai %.2f / trong %.2f quanh tam %s, thanh %.1f, sau %.1f duoi mat tay thang" % (lar, ri, "(%.2f, %.2f)" % lac, lw, L['depth']),
                "dai_mm": round(lar * abs(angs_lip[-1] - angs_lip[0]), 2),
                "nhan": [round(ac[0] + (ri - 3) * math.cos(-2.4), 2), round(ac[1] + (ri - 3) * math.sin(-2.4), 2)]}
    del EDGES[6]
for e in EDGES:
    e['nhan'] = [round(float(v), 2) for v in e['nhan']]
    A("note.add", anchor=[e['nhan'][0], e['nhan'][1], Z1],
      text="%s %s%s" % (e['ma'], e['ten'], (" | %.1f mm" % e['dai_mm']) if e['dai_mm'] else ""))
XY = lambda q: "(%.2f, %.2f)" % (q[0], q[1])
A("note.add", anchor=[pa[0], pa[1], -PA['len']], text="A1 chot dac O%.1f dai %.1f (cam lo A) | tam %s" % (PA['d'], PA['len'], XY(pa)))
A("note.add", anchor=[pa[0] + PA['shoulder_d'] / 2, pa[1], H / 2], text="A2 vai chot A O%.1f cao %.1f (z 0 -> %.1f)" % (PA['shoulder_d'], H, H))
A("note.add", anchor=[hb[0], hb[1], Z1], text="B1 lo xuyen O%.1f oc M4 | tam %s" % (BB['id'], XY(hb)))
A("note.add", anchor=[hb[0] + BB['od'] / 2, hb[1], bz0], text="B2 tru rong O%.1f cao %.1f (z %.1f -> %.1f)" % (BB['od'], H - bz0, bz0, H))
A("note.add", anchor=[0, 0, Z1], text="D tam dai oc (0, 0) = goc toa do")
A("note.add", anchor=[xr - 3, yt - 3, Z1], text="T tam ga day %.1f (z %.1f -> %.1f), mat duoi tua len dai oc" % (T, H, Z1))
if AL:
    A("note.add", anchor=[ac[0], ac[1], Z1], text="O tam cung E5/E6 %s, R %.2f" % (XY(ac), ar))
    A("note.add", anchor=[*lpc(angs_lip[0]), -L['depth']], text="E6a dau vanh (phia tru L)")
    A("note.add", anchor=[*lpc(angs_lip[-1]), -L["depth"]], text="E6b cuoi vanh (da bo %.2f mm phia chan E1)" % L.get("cut_E6b", 0))
A("note.add", anchor=[(pa[0] + hb[0]) / 2, (pa[1] + hb[1]) / 2 + 2, Z1], text="C = A-B %.1f mm" % P['C_mm'])
A("note.add", anchor=[p1[0], p1[1], ZS], text="DE-P1 lo chot cong tac O%.1f xuyen de | tam %s" % (SP['P1_hole_d'], XY(p1)))
if not MG: A("note.add", anchor=[jp_[0], jp_[1], Z1], text="J1 o chot rong tren ga O%.1f sau %.1f (nhan chot de O%.0f cao %.0f) | tam %s" % (JT['hole_d'], JT['depth'], JT['pin_d'], JT['pin_h'], XY(jp_)))
if not MG: A("note.add", anchor=[jp_[0] + JT['boss_od'] / 2, jp_[1], Z1 - JT['depth'] - 1.0], text="J2 vau o chot duoi tam O%.0f" % JT['boss_od'])
A("note.add", anchor=[pl[0], pl[1], ZS + post_h], text="L1 ong dem roi O%.0f / lo O4.4, cao %.2f (giua de va tai) | tam %s | oc M4x25 qua tai+ong+de vao ga" % (SP['post_d'], post_h, XY(pl)))
A("note.add", anchor=[pl[0] + SP['post_d'] / 2, pl[1], H - 3], text="L2 vau O%.0f duoi tam sau 3, lo ren O%.1f oc M4" % (SP['post_d'], SP['post_hole_d']))
A("note.add", anchor=[sx0 + S['W'] / 2, sy1, ZS + S['T']], text="S cong tac %.2f x %.2f x %.2f (chi de xem, khong in)" % (S['W'], S['H'], S['T']))
A("note.add", anchor=[sx0 - S['N_stick_out'], sy1 - SP['N_from_top'], ZS + S['T'] / 2], text="N nut nhan (nho %.2f) -> ve E1" % S['N_stick_out'])
for nm, val, cm in [("C_AB", P['C_mm'], "tam A - tam B"), ("R_mep", L['R'], "mep cung tay thang, tam D"), ("R_vien", R, "vien day ga"),
                    ("E1", P['E1'], ""), ("E2", P['E2'], ""), ("E3", P['E3'], ""),
                    ("cao_dai_oc", H, "mat duoi tam ga"), ("day_tam", T, ""), ("sau_vanh", L['depth'], "mep cung day"),
                    ("chot_A_d", PA['d'], ""), ("chot_A_dai", PA['len'], ""), ("tru_B_od", BB['od'], ""), ("lo_B_d", BB['id'], "")]:
    A("parameters.add", name=nm, expression="%g mm" % val, comment=cm)

# --- DE cong tac (phan in rieng, Tuan 2026-11-13): tam day SB['t'] theo dau cong tac + tai L, lo P1, tru L lien (in phang, tru huong len)
bdx = SB.get('display_dx', 0.0)            # 0 = dat dung cho lap tren ga
def hull(pts_):
    pts_ = sorted(set(map(tuple, pts_)))
    def half(ps):
        h = []
        for p_ in ps:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p_[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p_[0] - h[-2][0]) <= 0: h.pop()
            h.append(p_)
        return h
    lo, up = half(pts_), half(pts_[::-1]); return [list(q) for q in lo[:-1] + up[:-1]]
base_pts = [[sx0, sy0], [sx1, sy0], [sx1, sy1], [sx0, sy1]] +            [[pl[0] + SB['ear_r'] * math.cos(a), pl[1] + SB['ear_r'] * math.sin(a)] for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
base_poly = [[round(x + bdx, 3), round(y, 3)] for x, y in hull(base_pts)]
bp1 = [p1[0] + bdx, p1[1]]; bpl = [pl[0] + bdx, pl[1]]; bjp = [jp_[0] + bdx, jp_[1]]
def base_cmds(A_, name, join_to=None):
    """DE: tam z Z1..ZS, lo P1, lo L. Tach (v3.6): chot noi O pin_d mat duoi, lo L O4,4. Gop (v3.7): join vao ga, lo L O3,4 (ren M4 xuyen ca khoi)."""
    tg = join_to or name
    A_("sketch.create", plane={"origin": [0, 0, Z1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
    A_("sketch.line", points=(poly if MG else base_poly), closed=True); A_("sketch.finish")   # gop: phu het vien ga -> mat tren phang, in khong support
    if join_to: A_("solid.extrude", distance=bt, operation="join", targets=[tg])
    else: A_("solid.extrude", distance=bt, operation="new_body", body_name=name)
    if not MG:
        A_("solid.cylinder", diameter=JT['pin_d'], height=JT['pin_h'] + 0.5, base=[bjp[0], bjp[1], Z1 - JT['pin_h']], axis="Z", operation="join", targets=[tg])
    A_("solid.cylinder", diameter=(SP['post_hole_d'] if MG else 4.4), height=bt + 0.2, base=[bpl[0], bpl[1], Z1 - 0.1], axis="Z", operation="cut", targets=[tg])
    A_("solid.cylinder", diameter=SP['P1_hole_d'], height=bt + 0.2, base=[bp1[0], bp1[1], Z1 - 0.1], axis="Z", operation="cut", targets=[tg])
    if MG:   # B: lo M4 xuyen het tu duoi len + hoc dau oc tren mat (dau oc nam duoi cong tac)
        A_("solid.cylinder", diameter=BB['id'], height=ZS - bz0 + 0.2, base=[hb[0], hb[1], bz0 - 0.1], axis="Z", operation="cut", targets=[tg])
        A_("solid.cylinder", diameter=BB['cb_d'], height=BB['cb_depth'] + 0.1, base=[hb[0], hb[1], ZS - BB['cb_depth']], axis="Z", operation="cut", targets=[tg])
base_cmds(A, "base", join_to="mount" if MG else None)
BA = P.get('bump_A')   # v3.8: E2 lui 2 -> buou tron quanh A de om vai A2 + lo P1
if BA:
    A("solid.cylinder", diameter=BA['d'], height=(ZS if MG else Z1) - H, base=[pa[0], pa[1], H], axis="Z", **J)
    A("solid.cylinder", diameter=SP['P1_hole_d'], height=bt + 0.2, base=[p1[0], p1[1], Z1 - 0.1], axis="Z", **C)

raw = os.path.join(BUILD, 'mount.raw.stl').replace(os.sep, '/')
raw_sp = os.path.join(BUILD, 'spacer.raw.stl').replace(os.sep, '/')
raw_b = os.path.join(BUILD, 'base.raw.stl').replace(os.sep, '/')
A("file.export_stl", path=raw, bodies=["mount"], quality="fine")
if not MG: A("file.export_stl", path=raw_b, bodies=["base"], quality="fine")
A("file.export_stl", path=raw_sp, bodies=["spacer"], quality="fine"); A("inspect.measure")
jp = os.path.join(BUILD, 'mount.json'); json.dump({"commands": cmd}, open(jp, 'w'), indent=1)
res = os.path.join(BUILD, 'mount.result.json')
r = subprocess.run([CLI, 'run', jp, '--save', os.path.join(BUILD, 'print.sc'), '--results', '--json-out', res, '--quiet'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
if r.returncode:
    sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:]); sys.exit(1)

# --- file .sc de DO: moi chi tiet 1 body co ten + mau (bam vao mat -> thay ten body) ---
cN = []
N_ = lambda c, **p: cN.append({"command": c, "params": p})
cyl = lambda name, d, h, z0, q, col: (N_("solid.cylinder", diameter=d, height=h, base=[q[0], q[1], z0], axis="Z", operation="new_body", body_name=name),
                                      N_("appearance.assign", bodies=[name], color=col))
cutN = lambda d, h, z0, q, tg: N_("solid.cylinder", diameter=d, height=h, base=[q[0], q[1], z0], axis="Z", operation="cut", targets=tg)
N_("sketch.create", plane={"origin": [0, 0, H], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
N_("sketch.line", points=poly, closed=True); N_("sketch.finish")
N_("solid.extrude", distance=T, operation="new_body", body_name="T_tam_ga"); N_("appearance.assign", bodies=["T_tam_ga"], color="#3a8fd8")
N_("sketch.create", plane={"origin": [0, 0, -L['depth']], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
N_("sketch.line", points=lip, closed=True); N_("sketch.finish")
N_("solid.extrude", distance=L['depth'] + H, operation="new_body", body_name="E6_vanh_om"); N_("appearance.assign", bodies=["E6_vanh_om"], color="#4caf50")
cyl("A2_vai_chot_A", PA['shoulder_d'], H, 0, pa, "#ffb300")
cyl("A1_chot_A_O3.7", PA['d'], PA['len'], -PA['len'], pa, "#e65100")
cyl("B2_tru_rong_B", BB['od'], H - bz0, bz0, hb, "#e53935")
cyl("L2_vau_L_duoi_tam", SP['post_d'], boss_dn, H - boss_dn, pl, "#8e24aa")
cutN(BB['id'], Z1 - bz0 + 0.2, bz0 - 0.1, hb, ["T_tam_ga", "B2_tru_rong_B"])
if not MG:
    cyl("J2_vau_o_chot", JT['boss_od'], JT['depth'] - T + 1.0, Z1 - JT['depth'] - 1.0, jp_, "#5e35b1")
    cutN(JT['hole_d'], JT['depth'] + 0.1, Z1 - JT['depth'], jp_, ["T_tam_ga", "J2_vau_o_chot"])
cutN(SP['post_hole_d'], T + boss_dn + 0.2, H - boss_dn - 0.1, pl, ["T_tam_ga", "L2_vau_L_duoi_tam"])
cyl("L1_ong_dem_roi", SP['post_d'], post_h, ZS, pl, "#ff8c00"); cutN(4.4, post_h + 0.2, ZS - 0.1, pl, ["L1_ong_dem_roi"])
N_("sketch.create", plane={"origin": [0, 0, ZS], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
N_("sketch.rectangle.two_point", p0=[sx0, sy0], p1=[sx1, sy1]); N_("sketch.finish")
N_("solid.extrude", distance=S['T'], operation="new_body", body_name="S_cong_tac_chi_xem")
N_("solid.cylinder", diameter=SP['N_d'], height=S['N_stick_out'], base=[sx0 - S['N_stick_out'], sy1 - SP['N_from_top'], ZS + S['T'] / 2],
   axis="X", operation="new_body", body_name="N_nut_nhan")
N_("appearance.assign", bodies=["S_cong_tac_chi_xem"], color="#333333", opacity=0.45)
N_("appearance.assign", bodies=["N_nut_nhan"], color="#00e676")
if BA:
    cyl("T2_buou_vien_quanh_A", BA['d'], (ZS if MG else Z1) - H, H, pa, "#3a8fd8")
    cutN(SP['P1_hole_d'], bt + 0.2, Z1 - 0.1, p1, ["T2_buou_vien_quanh_A"])
DEN = "DE_tang_tren_gop_lien_ga" if MG else "DE_cong_tac_khoi_tren"
base_cmds(N_, DEN); N_("appearance.assign", bodies=[DEN], color="#00acc1")
cN += [c for c in cmd if c['command'] in ('note.add', 'parameters.add')]
N_("note.add", anchor=[bpl[0], bpl[1], ZS], text="DE-L lo xuyen O4.4 (oc M4) | de day %.1f (z %.1f -> %.1f)" % (bt, Z1, ZS))
if MG:
    N_("note.add", anchor=[hb[0], hb[1], ZS], text="B3 hoc dau oc M4 O%.1f sau %.1f (dau oc nam duoi cong tac) | lo B xuyen tu z %.1f -> %.1f" % (BB['cb_d'], BB['cb_depth'], bz0, ZS))
else:
    N_("note.add", anchor=[bjp[0], bjp[1], Z1 - JT['pin_h']], text="DE-J chot noi O%.1f cao %.1f mat duoi de -> cam o J1 tren ga" % (JT['pin_d'], JT['pin_h']))
jn = os.path.join(BUILD, 'named.json'); json.dump({"commands": cN}, open(jn, 'w'), indent=1)
r = subprocess.run([CLI, 'run', jn, '--save', os.path.join(HERE, 'brake-sensor-mount.sc'), '--quiet'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
if r.returncode:
    sys.stderr.write('NAMED: ' + r.stdout[-3000:] + r.stderr[-3000:]); sys.exit(1)

# STL huong in: lat 180 quanh X, zmin = 0
b = open(raw, 'rb').read(); n = int(np.frombuffer(b, '<u4', 1, 80)[0])
rec = np.frombuffer(b, np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), n, 84).copy()
Rm = np.diag([1.0, -1.0, -1.0]); v = rec['v'].astype(float) @ Rm.T; v[..., 2] -= v[..., 2].min()
rec['v'] = v.astype('<f4'); rec['n'] = (rec['n'].astype(float) @ Rm.T).astype('<f4')
open(os.path.join(STLD, 'mount.stl'), 'wb').write(b[:84] + rec.tobytes()); os.remove(raw)
# ong dem: dung dung, zmin = 0, dat canh ga
b = open(raw_sp, 'rb').read(); n = int(np.frombuffer(b, '<u4', 1, 80)[0])
rec = np.frombuffer(b, np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), n, 84).copy()
v = rec['v'].astype(float); v[..., 2] -= v[..., 2].min(); rec['v'] = v.astype('<f4')
open(os.path.join(STLD, 'spacer-L.stl'), 'wb').write(b[:84] + rec.tobytes()); os.remove(raw_sp)
# de cong tac: lat 180 quanh X (mat tren xuong ban, chot noi huong len), zmin = 0
if not MG:
    b = open(raw_b, 'rb').read(); n = int(np.frombuffer(b, '<u4', 1, 80)[0])
    rec = np.frombuffer(b, np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), n, 84).copy()
    v = rec['v'].astype(float) @ Rm.T; v[..., 2] -= v[..., 2].min(); rec['v'] = v.astype('<f4'); rec['n'] = (rec['n'].astype(float) @ Rm.T).astype('<f4')
    open(os.path.join(STLD, 'switch-base.stl'), 'wb').write(b[:84] + rec.tobytes()); os.remove(raw_b)
bodies = {bd.get('name'): bd for bd in json.load(open(res, encoding='utf-8'))[-1]['bodies']}
body = bodies.get('mount') or list(bodies.values())[0]
rep = {"volume_mm3": body.get('volume_mm3'), "bbox": body['bbox'], "closed": body.get('closed'),
       "shells": body.get('kernel', {}).get('shells'), "bodies": sorted(k for k in bodies if k)}
json.dump(rep, open(os.path.join(HERE, 'build-report.json'), 'w'), indent=1)
json.dump(EDGES, open(os.path.join(HERE, 'edges.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- anh duyet ---
try:
    from PIL import Image, ImageDraw
    img = Image.open(PHOTO).convert('RGB'); dr = ImageDraw.Draw(img, 'RGBA')
    px = lambda q: (q[0] * K + OX, OY - q[1] * K)
    dr.polygon([px(q) for q in poly], fill=(0, 200, 255, 70), outline=(0, 230, 255, 255))
    dr.polygon([px(q) for q in lip], fill=(80, 255, 80, 120))
    for c0, d0, col in [(pa, PA['d'], (255, 220, 0)), (pa, PA['shoulder_d'], (255, 220, 0)),
                        (hb, BB['id'], (255, 80, 80)), (hb, BB['od'], (255, 80, 80))]:
        x, y = px(c0); rr = d0 / 2 * K; dr.ellipse([x - rr, y - rr, x + rr, y + rr], outline=col + (255,), width=4)
    dr.rectangle([px([sx0, sy1]), px([sx1, sy0])], outline=(255, 255, 255, 255), width=4)
    nx, ny = px([sx0 - S['N_stick_out'], sy1 - SP['N_from_top']]); dr.ellipse([nx - 12, ny - 12, nx + 12, ny + 12], fill=(80, 255, 80, 255))
    for q in (p1, pl):
        x, y = px(q); dr.ellipse([x - 3 * K, y - 3 * K, x + 3 * K, y + 3 * K], outline=(255, 255, 255, 255), width=4)
    img.save(os.path.join(HERE, '..', 'review', 'overlay.png'))

    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 11)); pp = np.array(poly + [poly[0]])
    ax.fill(pp[:, 0], pp[:, 1], color='#cfe8ff'); ax.plot(pp[:, 0], pp[:, 1], 'k-', lw=1.5)
    lp = np.array(lip + [lip[0]]); ax.fill(lp[:, 0], lp[:, 1], color='#7ee08a')
    ax.add_patch(plt.Circle((0, 0), L['R'], fill=False, ls=':', color='gray'))
    ax.annotate('mep tay thang R%g' % L['R'], (-4, -L['R'] + 1), color='gray')
    for c0, d0, col in [(pa, PA['shoulder_d'], 'orange'), (pa, PA['d'], 'orange'), (hb, BB['od'], 'red'), (hb, BB['id'], 'red')]:
        ax.add_patch(plt.Circle(c0, d0 / 2, fill=False, color=col, lw=2))
    for e in EDGES:
        t = e['ma'] + ((' %.1f' % e['dai_mm']) if e['dai_mm'] else '')
        ax.annotate(t, e['nhan'], ha='center', va='center', fontsize=12, color='navy', weight='bold')
    NL = chr(10)
    feats = [(('A  chot O%.1f dai %.1f' + NL + '   vai O%.0f cao %.1f' + NL + '   %s') % (PA['d'], PA['len'], PA['shoulder_d'], H, XY(pa)), pa, (-13, 3)),
             (('B  lo O%.1f M4, tru O%.0f' + NL + '   cao %.1f  %s') % (BB['id'], BB['od'], H - bz0, XY(hb)), hb, (2, 4)),
             ('D  tam dai oc (0,0)', [0, 0], (1.5, 1.5)),
             ('P1 lo O%.1f  %s' % (SP['P1_hole_d'], XY(p1)), p1, (2, -2.5)),
             (('L  ong dem O%.0f cao %.2f' + NL + '   lo ren O%.1f  %s') % (SP['post_d'], post_h, SP['post_hole_d'], XY(pl)), pl, (5, -2))]
    if AL:
        feats.append((('O  tam cung R%.2f' + NL + '   %s') % (ar, XY(ac)), list(ac), (-4, -4)))
        ax.plot(*ac, 'kx', ms=10)
        for t_, a_ in [('E6a', angs_lip[0]), ('E6b', angs_lip[-1])]:
            q = lpc(a_); ax.plot(*q, 'go', ms=8); ax.annotate(t_, (q[0] + 0.6, q[1] + 0.6), color='green', weight='bold')
    for t_, p_, o_ in feats:
        ax.annotate(t_, (p_[0] + o_[0], p_[1] + o_[1]), color='crimson', fontsize=9, weight='bold')
    ax.plot([pa[0], hb[0]], [pa[1], hb[1]], 'm--')
    ax.annotate('C %.1f' % P['C_mm'], ((pa[0] + hb[0]) / 2, (pa[1] + hb[1]) / 2 + 1), color='m', weight='bold')
    ax.plot(0, 0, 'k+', ms=15)
    ax.add_patch(plt.Rectangle((sx0, sy0), S['W'], S['H'], fill=False, ls='--', color='k', lw=1.5))
    ax.annotate('cong tac %.1f x %.1f' % (S['W'], S['H']), (sx0 + 12, sy1 - 3), fontsize=10)
    ax.plot([sx0, sx0 - S['N_stick_out']], [sy1 - SP['N_from_top']] * 2, 'g-', lw=5); ax.annotate('N', (sx0 - S['N_stick_out'] - 1.5, sy1 - SP['N_from_top'] + 0.8), color='green', weight='bold')
    for t_, q, d0 in [('P1', p1, SP['P1_hole_d']), ('L', pl, SP['post_d'])]:
        ax.add_patch(plt.Circle(q, d0 / 2, fill=False, color='purple', lw=2)); ax.annotate(t_, (q[0] + 2, q[1] - 1), color='purple', weight='bold')
    allp = np.array(poly + [e['nhan'] for e in EDGES] + [[sx0 - 6, sy0 - 4], [sx1 + 2, sy1]])
    ax.set_xlim(allp[:, 0].min() - 3, allp[:, 0].max() + 3); ax.set_ylim(allp[:, 1].min() - 3, allp[:, 1].max() + 3)
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_xlabel('X mm (goc = tam dai oc D)'); ax.set_ylabel('Y mm')
    ax.set_title('Ga cam bien tay thang v3.4 - nhin tu tren | ma = note trong .sc | toa do (x, y) mm tu tam D')
    plt.savefig(os.path.join(HERE, '..', 'review', 'edges-named.png'), dpi=80, bbox_inches='tight')
except Exception as e:
    print('anh duyet loi:', e)

# --- anh duyet DE cong tac: ban ve tren + canh ben (ma canh DE-E1..) + anh 3D SolidCraft ---
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    bpp = [[x - bdx, y] for x, y in base_poly]                   # ve theo toa do ga (bo lech hien thi)
    BE = []
    for i in range(len(bpp)):
        p_, q_ = bpp[i], bpp[(i + 1) % len(bpp)]
        Ld = math.dist(p_, q_)
        if Ld > 2.0: BE.append((p_, q_, Ld))
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 7.5), gridspec_kw={'width_ratios': [3, 2]})
    pp = np.array(bpp + [bpp[0]]); ax.fill(pp[:, 0], pp[:, 1], color='#b2ebf2'); ax.plot(pp[:, 0], pp[:, 1], 'k-', lw=1.5)
    cen_b = np.mean(np.array(bpp), 0)
    for j, (p_, q_, Ld) in enumerate(BE):
        m = (np.array(p_) + np.array(q_)) / 2; dv = m - cen_b; dv /= np.linalg.norm(dv) + 1e-9
        ax.annotate('DE-E%d\n%.1f' % (j + 1, Ld), m + dv * 2.8, ha='center', va='center', color='navy', weight='bold', fontsize=10)
    ax.add_patch(plt.Circle(p1, SP['P1_hole_d'] / 2, fill=False, color='crimson', lw=2))
    ax.annotate('DE-P1 lo O%.1f xuyen\n%s' % (SP['P1_hole_d'], XY(p1)), (p1[0] + 3, p1[1] + 1), color='crimson', weight='bold')
    ax.add_patch(plt.Circle(pl, 2.2, fill=False, color='purple', lw=2))
    ax.add_patch(plt.Circle(pl, SP['post_d'] / 2, fill=False, color='orange', ls='--', lw=1.5))
    ax.annotate('DE-L lo O4.4 xuyen (M4)\nong dem L1 O8 dat tren\n%s' % XY(pl), (pl[0] + 5, pl[1] - 1), color='purple', weight='bold')
    if not MG: ax.add_patch(plt.Circle(jp_, JT['pin_d'] / 2, color='#5e35b1', alpha=.6))
    if not MG: ax.annotate('DE-J chot noi O%.0f cao %.0f\n(mat duoi) %s' % (JT['pin_d'], JT['pin_h'], XY(jp_)), (jp_[0] + 3, jp_[1] - 1), color='#5e35b1', weight='bold')
    ax.plot([sx0, sx0 - S['N_stick_out']], [sy1 - SP['N_from_top']] * 2, 'g-', lw=5)
    ax.annotate('N nut (cong tac)', (sx0 - S['N_stick_out'], sy1 - SP['N_from_top'] + 1), color='green', weight='bold')
    ax.add_patch(plt.Rectangle((sx0, sy0), S['W'], S['H'], fill=False, ls='--', color='gray'))
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_xlabel('X mm (cung goc toa do voi ga, tam D)'); ax.set_ylabel('Y mm')
    ax.set_title('DE cong tac (khoi tren, in rieng) - nhin tu tren, day %.1f mm' % bt)
    ax.set_xlim(sx0 - 9, sx1 + 6); ax.set_ylim(pl[1] - 8, sy1 + 4)
    # canh ben (cat doc qua L va P1 theo X)
    ax2.add_patch(plt.Rectangle((sx0, 0), S['W'], bt, color='#b2ebf2', ec='k'))
    if not MG: ax2.add_patch(plt.Rectangle((jp_[0] - JT['pin_d'] / 2, -JT['pin_h']), JT['pin_d'], JT['pin_h'], color='#5e35b1', ec='k'))
    if not MG: ax2.annotate('DE-J chot %.0f' % JT['pin_h'], (jp_[0] + JT['pin_d'] / 2 + 0.5, -JT['pin_h'] / 2), color='#5e35b1', weight='bold')
    ax2.add_patch(plt.Rectangle((pl[0] - SP['post_d'] / 2, bt), SP['post_d'], post_h, color='orange', alpha=.5, ec='k'))
    ax2.add_patch(plt.Rectangle((sx0, bt), S['W'], S['T'], fill=False, ls='--', color='gray'))
    ax2.annotate('cong tac (chi xem) cao %.2f' % S['T'], (sx0 + 9, bt + S['T'] / 2), color='gray')
    ax2.annotate('L1 ong dem roi %.2f' % post_h, (pl[0] + SP['post_d'] / 2 + 0.5, bt + post_h / 2), color='purple', weight='bold')
    ax2.annotate('day %.1f' % bt, (sx1 + 0.5, bt / 2), color='navy', weight='bold')
    ax2.set_aspect('equal'); ax2.set_xlim(sx0 - 3, sx1 + 8); ax2.set_ylim(-JT['pin_h'] - 2, bt + S['T'] + 3); ax2.grid(alpha=.3)
    ax2.set_title('Nhin ngang (X-Z)'); ax2.set_xlabel('X mm'); ax2.set_ylabel('Z mm')
    plt.tight_layout(); plt.savefig(os.path.join(HERE, '..', 'review', 'switch-base.png'), dpi=80)
    json.dump([{"ma": "DE-E%d" % (j + 1), "tu": p_, "den": q_, "dai_mm": round(Ld, 2)} for j, (p_, q_, Ld) in enumerate(BE)],
              open(os.path.join(HERE, 'edges-base.json'), 'w', encoding='utf-8'), indent=1)
except Exception as e:
    print('anh de loi:', e)

ok = rep['closed'] is not False and rep['shells'] in (None, 1)
print('px/mm %.2f  R_vien %.2f' % (K, R))
print('MOUNT', 'PASS' if ok else 'FAIL', rep)
sys.exit(0 if ok else 1)
