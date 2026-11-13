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
pol = lambda r, a: [round(r * math.cos(a), 3), round(r * math.sin(a), 3)]

r_in = L['R'] + L['gap']; R = r_in + L['wall']          # R = ban kinh vien day (E5 + E6), tam D
xr, yt = P['right_x'], P['top_y']
xl = xr - P['E2']; y1 = yt - P['E1']; y3 = yt - P['E3']; rf = P['fillet_E1']
d = math.hypot(xr, y3); at = math.atan2(y3, xr) - math.acos(R / d)   # tiep tuyen tu chan E3, nhanh duoi
a_top = math.pi - math.asin(min(y1 / R, 1.0))                        # cung gap do cao chan E1 (phia trai)
a0, a1 = math.radians(L['a0']), math.radians(L['a1'])

poly = [[xl, yt], [xr, yt], [xr, y3]]                                # E2, E3
poly += [pol(R, a) for a in np.linspace(at, a1 - 2 * math.pi, 40)]   # E4 (doan) + E5 cung day
poly += [pol(R, a) for a in np.linspace(a1, a0, 16)[1:]]             # E6 vanh om
poly += [pol(R, a) for a in np.linspace(a0, a_top, 6)[1:]]           # tiep cung toi do cao chan E1
fc = (xl - rf, y1 + rf)                                              # E7: doan ngang + bo lom R=rf vao E1
poly.append([round(xl - rf, 3), round(y1, 3)])
poly += [[round(fc[0] + rf * math.cos(a), 3), round(fc[1] + rf * math.sin(a), 3)] for a in np.linspace(-math.pi / 2, 0, 8)[1:]]
lip = [pol(R, a) for a in np.linspace(a0, a1, 16)] + [pol(r_in, a) for a in np.linspace(a1, a0, 16)]

cmd = []
A = lambda c, **p: cmd.append({"command": c, "params": p})
A("sketch.create", plane={"origin": [0, 0, H], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
A("sketch.line", points=poly, closed=True); A("sketch.finish")
A("solid.extrude", distance=T, operation="new_body", body_name="mount")
J = {"operation": "join", "targets": ["mount"]}; C = {"operation": "cut", "targets": ["mount"]}
A("sketch.create", plane={"origin": [0, 0, -L['depth']], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
A("sketch.line", points=lip, closed=True); A("sketch.finish")
A("solid.extrude", distance=L['depth'] + H + 0.5, **J)
A("solid.cylinder", diameter=PA['shoulder_d'], height=H + 0.5, base=[pa[0], pa[1], 0], axis="Z", **J)
A("solid.cylinder", diameter=PA['d'], height=PA['len'] + 0.5, base=[pa[0], pa[1], -PA['len']], axis="Z", **J)
A("solid.cylinder", diameter=BB['od'], height=H + 0.5, base=[hb[0], hb[1], 0], axis="Z", **J)
A("solid.cylinder", diameter=BB['id'], height=Z1 + 0.2, base=[hb[0], hb[1], -0.1], axis="Z", **C)

# --- cong tac den phanh: up mat P1 xuong tam ga, nut N chia -X (ve E1) ---
S = P['sensor']; SP = S['place']
sx0 = xl + SP['dx']                       # mat co nut N
sy1 = yt + SP['dy']                       # canh tren than
sx1, sy0 = sx0 + S['W'], sy1 - S['H']
p1 = [round(sx0 + SP['P1_from_plunger'], 3), round(sy1 - SP['P1_from_top'], 3)]
pl = [round(sx0 + SP['L_from_plunger'], 3), round(sy0 - SP['L_below_bottom'], 3)]
post_h = S['T'] - SP['ear_t']             # tai L nam o mat xa tam ga -> tru do tai cao T - ear_t
A("solid.cylinder", diameter=SP['P1_hole_d'], height=T + 0.6, base=[p1[0], p1[1], H - 0.3], axis="Z", **C)
# tai L: tam ga co vau O post_d (mat tam + 3 mm xuong duoi) lo O3,4 cho oc M4 tu ren; ong dem roi cao post_h dat giua tai va tam
boss_dn = 3.0
A("solid.cylinder", diameter=SP['post_d'], height=T + boss_dn, base=[pl[0], pl[1], H - boss_dn], axis="Z", **J)
A("solid.cylinder", diameter=SP['post_hole_d'], height=T + boss_dn + 0.2, base=[pl[0], pl[1], H - boss_dn - 0.1], axis="Z", **C)
A("solid.cylinder", diameter=SP['post_d'], height=post_h, base=[pl[0], pl[1], Z1], axis="Z", operation="new_body", body_name="spacer")
A("solid.cylinder", diameter=4.4, height=post_h + 0.2, base=[pl[0], pl[1], Z1 - 0.1], axis="Z", operation="cut", targets=["spacer"])
# than cong tac (chi de xem, khong in)
A("sketch.create", plane={"origin": [0, 0, Z1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
A("sketch.rectangle.two_point", p0=[sx0, sy0], p1=[sx1, sy1]); A("sketch.finish")
A("solid.extrude", distance=S['T'], operation="new_body", body_name="switch")
A("solid.cylinder", diameter=SP['N_d'], height=S['N_stick_out'], base=[sx0 - S['N_stick_out'], sy1 - SP['N_from_top'], Z1 + S['T'] / 2],
  axis="X", operation="join", targets=["switch"])
A("solid.cylinder", diameter=8.0, height=SP['ear_t'], base=[pl[0], pl[1], Z1 + post_h], axis="Z", operation="join", targets=["switch"])
A("appearance.assign", bodies=["switch"], color="#333333", opacity=0.6)

# --- ma canh (note trong .sc) + tham so ten ro ---
p4 = pol(R, at)
EDGES = [
    {"ma": "E1", "ten": "mep trai (canh khoi luc giac)", "dai_mm": P['E1'], "nhan": [xl - 3, (yt + y1) / 2]},
    {"ma": "E2", "ten": "canh tren", "dai_mm": P['E2'], "nhan": [(xl + xr) / 2, yt + 1.5]},
    {"ma": "E3", "ten": "canh phai (sat xi-lanh)", "dai_mm": P['E3'], "nhan": [xr + 2.5, (yt + y3) / 2]},
    {"ma": "E4", "ten": "doan thang tiep tuyen", "dai_mm": round(math.dist([xr, y3], p4), 2),
     "nhan": [(xr + p4[0]) / 2 + 2.5, (y3 + p4[1]) / 2]},
    {"ma": "E5", "ten": "cung day R%.1f tam D (gop E5-E11 cu)" % R, "dai_mm": round(R * abs(at - (a1 - 2 * math.pi)), 2),
     "nhan": pol(R + 2.5, -math.pi / 2)},
    {"ma": "E6", "ten": "cung vanh om (E12 cu) R trong %.1f / ngoai %.1f, sau %.1f" % (r_in, R, L['depth']),
     "dai_mm": round(R * abs(a1 - a0), 2), "nhan": pol(R + 3.5, (a0 + a1) / 2)},
    {"ma": "E7", "ten": "bo noi cung -> chan E1 (E13 cu), bo R%.1f" % rf, "dai_mm": None, "nhan": [xl - 4, y1 - 1.5]},
]
for e in EDGES:
    e['nhan'] = [round(float(v), 2) for v in e['nhan']]
    A("note.add", anchor=[e['nhan'][0], e['nhan'][1], Z1],
      text="%s %s%s" % (e['ma'], e['ten'], (" | %.1f mm" % e['dai_mm']) if e['dai_mm'] else ""))
A("note.add", anchor=[pa[0], pa[1], -PA['len']], text="A chot dac O%.1f dai %.1f | vai O%.1f cao %.1f" % (PA['d'], PA['len'], PA['shoulder_d'], H))
A("note.add", anchor=[hb[0], hb[1], Z1], text="B tru rong O%.1f / lo O%.1f (oc M4) | cao %.1f" % (BB['od'], BB['id'], H))
A("note.add", anchor=[0, 0, Z1], text="D tam dai oc (goc toa do) | tam ga day %.1f, mat duoi cao %.1f" % (T, H))
A("note.add", anchor=[(pa[0] + hb[0]) / 2, (pa[1] + hb[1]) / 2 + 2, Z1], text="C = A-B %.1f mm" % P['C_mm'])
A("note.add", anchor=[p1[0], p1[1], Z1], text="P1 lo chot cong tac O%.1f" % SP['P1_hole_d'])
A("note.add", anchor=[pl[0], pl[1], Z1 + post_h], text="L ong dem roi O%.0f/O4.4 cao %.2f + lo ren O%.1f oc M4" % (SP['post_d'], post_h, SP['post_hole_d']))
A("note.add", anchor=[sx0 - S['N_stick_out'], sy1 - SP['N_from_top'], Z1 + S['T'] / 2], text="N nut nhan (nho %.2f) -> ve E1" % S['N_stick_out'])
for nm, val, cm in [("C_AB", P['C_mm'], "tam A - tam B"), ("R_mep", L['R'], "mep cung tay thang, tam D"), ("R_vien", R, "vien day ga"),
                    ("E1", P['E1'], ""), ("E2", P['E2'], ""), ("E3", P['E3'], ""),
                    ("cao_dai_oc", H, "mat duoi tam ga"), ("day_tam", T, ""), ("sau_vanh", L['depth'], "mep cung day"),
                    ("chot_A_d", PA['d'], ""), ("chot_A_dai", PA['len'], ""), ("tru_B_od", BB['od'], ""), ("lo_B_d", BB['id'], "")]:
    A("parameters.add", name=nm, expression="%g mm" % val, comment=cm)

raw = os.path.join(BUILD, 'mount.raw.stl').replace(os.sep, '/')
raw_sp = os.path.join(BUILD, 'spacer.raw.stl').replace(os.sep, '/')
A("file.export_stl", path=raw, bodies=["mount"], quality="fine")
A("file.export_stl", path=raw_sp, bodies=["spacer"], quality="fine"); A("inspect.measure")
jp = os.path.join(BUILD, 'mount.json'); json.dump({"commands": cmd}, open(jp, 'w'), indent=1)
res = os.path.join(BUILD, 'mount.result.json')
r = subprocess.run([CLI, 'run', jp, '--save', os.path.join(HERE, 'brake-sensor-mount.sc'), '--results', '--json-out', res, '--quiet'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
if r.returncode:
    sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:]); sys.exit(1)

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
    for t_, p_ in [('A', pa), ('B', hb), ('D', [0, 0])]:
        ax.annotate(t_, (p_[0] + 1.5, p_[1] + 1.5), color='crimson', fontsize=14, weight='bold')
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
    ax.set_title('Ga cam bien tay thang v2 - nhin tu tren (ma canh = note trong .sc)')
    plt.savefig(os.path.join(HERE, '..', 'review', 'edges-named.png'), dpi=80, bbox_inches='tight')
except Exception as e:
    print('anh duyet loi:', e)

ok = rep['closed'] is not False and rep['shells'] in (None, 1)
print('px/mm %.2f  R_vien %.2f' % (K, R))
print('MOUNT', 'PASS' if ok else 'FAIL', rep)
sys.exit(0 if ok else 1)
