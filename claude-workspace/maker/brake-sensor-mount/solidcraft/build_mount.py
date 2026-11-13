"""Ga cam bien tay thang v0 - SolidCraft. So lieu: params.json. Ra: build/mount.sc, brake-sensor-mount.sc,
stl/mount.stl (huong in: mat tren up xuong ban, chot + vanh om huong len), build-report.json, ../review/overlay.png.
Chay: python build_mount.py"""
import json, math, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get('SOLIDCRAFT_CLI', r'C:\Program Files\SolidCraft\solidcraft-cli.exe')
P = json.load(open(os.path.join(HERE, 'params.json'), encoding='utf-8'))
BUILD = os.path.join(HERE, 'build'); STLD = os.path.join(HERE, 'stl')
os.makedirs(BUILD, exist_ok=True); os.makedirs(STLD, exist_ok=True)
OX, OY = P['img_origin_px']
_a, _b = P['pin_a']['px'], P['boss_b']['px']
K = math.hypot(_a[0] - _b[0], _a[1] - _b[1]) / P['C_mm']          # px/mm theo C do that
H = P['standoff']; T = P['plate_t']; Z1 = H + T                    # tam ga: z H..Z1 (tren dai oc)
mm = lambda p: [round((p[0] - OX) / K, 3), round((OY - p[1]) / K, 3)]

L = P['lip']; cx = L['center_dx_mm']; r_in = L['R'] + L['gap']; r_out = r_in + L['wall']
angs = np.radians(np.linspace(L['a0'], L['a1'], 16))
ring = lambda r, aa: [[round(cx + r * math.cos(a), 3), round(r * math.sin(a), 3)] for a in aa]
poly = [mm(p) for p in P['outline_px']] + ring(r_out, angs[::-1])
lip = ring(r_out, angs) + ring(r_in, angs[::-1])

cmd = []
A = lambda c, **p: cmd.append({"command": c, "params": p})
A("sketch.create", plane={"origin": [0, 0, H], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
A("sketch.line", points=poly, closed=True); A("sketch.finish")
A("solid.extrude", distance=T, operation="new_body", body_name="mount")
J = {"operation": "join", "targets": ["mount"]}; C = {"operation": "cut", "targets": ["mount"]}
# vanh om mep cung: tu z=-depth (mat duoi mep tay thang) len toi tam ga
A("sketch.create", plane={"origin": [0, 0, -L['depth']], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
A("sketch.line", points=lip, closed=True); A("sketch.finish")
A("solid.extrude", distance=L['depth'] + H + 0.5, **J)
pa = mm(P['pin_a']['px']); PA = P['pin_a']
A("solid.cylinder", diameter=PA['shoulder_d'], height=H + 0.5, base=[pa[0], pa[1], 0], axis="Z", **J)
A("solid.cylinder", diameter=PA['d'], height=PA['len'] + 0.5, base=[pa[0], pa[1], -PA['len']], axis="Z", **J)
hb = mm(P['boss_b']['px']); BB = P['boss_b']
A("solid.cylinder", diameter=BB['od'], height=H + 0.5, base=[hb[0], hb[1], 0], axis="Z", **J)
A("solid.cylinder", diameter=BB['id'], height=Z1 + 0.2, base=[hb[0], hb[1], -0.1], axis="Z", **C)
# --- Nhan ten canh + chi tiet (note trong .sc) de Tuan do va bao lai theo ma ---
EDGE_NAMES = ["mep trai (canh khoi luc giac)", "canh tren", "canh phai (sat xi-lanh)", "lom phai 1", "lom phai 2",
              "lom phai 3", "lom phai 4", "day phai", "day giua", "day trai", "cheo trai duoi"]
pts = poly; nseg = len(P['outline_px'])
cen = np.mean(np.array(pts), 0)
EDGES = []
def label(p, q, code, name, curve=False, length=None):
    m = np.array([(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]); dv = m - cen; dv = dv / (np.linalg.norm(dv) + 1e-9)
    at = m + dv * 2.5
    L_ = length if length is not None else math.hypot(q[0] - p[0], q[1] - p[1])
    EDGES.append({"ma": code, "ten": name, "dai_mm": round(L_, 2), "tu": p, "den": q, "nhan": [round(at[0], 2), round(at[1], 2)]})
    A("note.add", anchor=[round(at[0], 2), round(at[1], 2), Z1], text="%s %s | %.1f mm" % (code, name, L_))
for i in range(nseg - 1):
    label(pts[i], pts[i + 1], "E%d" % (i + 1), EDGE_NAMES[i])
i0 = nseg - 1
label(pts[i0], pts[i0 + 1], "E%d" % nseg, EDGE_NAMES[nseg - 1])
arc_len = r_out * abs(math.radians(L['a1'] - L['a0']))
amid = math.radians((L['a0'] + L['a1']) / 2)
EDGES.append({"ma": "E%d" % (nseg + 1), "ten": "cung vanh om (ngoai) R%.1f" % r_out, "dai_mm": round(arc_len, 2)})
A("note.add", anchor=[round(cx + (r_out + 2.5) * math.cos(amid), 2), round((r_out + 2.5) * math.sin(amid), 2), Z1],
  text="E%d cung vanh om | R trong %.1f / ngoai %.1f, sau %.1f" % (nseg + 1, r_in, r_out, L['depth']))
label(pts[-1], pts[0], "E%d" % (nseg + 2), "noi vanh -> mep trai")
A("note.add", anchor=[pa[0], pa[1], -PA['len']], text="A chot dac O%.1f dai %.1f | vai O%.1f cao %.1f" % (PA['d'], PA['len'], PA['shoulder_d'], H))
A("note.add", anchor=[hb[0], hb[1], Z1], text="B tru rong O%.1f / lo O%.1f (oc M4) | cao %.1f" % (BB['od'], BB['id'], H))
A("note.add", anchor=[0, 0, Z1], text="D tam dai oc (goc toa do) | tam ga day %.1f, mat duoi cao %.1f" % (T, H))
A("note.add", anchor=[(pa[0] + hb[0]) / 2, (pa[1] + hb[1]) / 2 + 2, Z1], text="C = A-B %.1f mm" % P['C_mm'])
for nm, val, cm in [("C_AB", P['C_mm'], "tam A - tam B"), ("R_cung", L['R'], "ban kinh mep cung tay thang"),
                    ("cao_dai_oc", H, "mat duoi tam ga"), ("day_tam", T, "tam ga"), ("sau_vanh", L['depth'], "mep cung day"),
                    ("chot_A_d", PA['d'], ""), ("chot_A_dai", PA['len'], ""), ("tru_B_od", BB['od'], ""), ("lo_B_d", BB['id'], "")]:
    A("parameters.add", name=nm, expression="%g mm" % val, comment=cm)
raw = os.path.join(BUILD, 'mount.raw.stl').replace(os.sep, '/')
A("file.export_stl", path=raw, bodies=["mount"], quality="fine"); A("inspect.measure")
jp = os.path.join(BUILD, 'mount.json'); json.dump({"commands": cmd}, open(jp, 'w'), indent=1)
res = os.path.join(BUILD, 'mount.result.json')
r = subprocess.run([CLI, 'run', jp, '--save', os.path.join(HERE, 'brake-sensor-mount.sc'), '--results', '--json-out', res, '--quiet'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
if r.returncode: sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:]); sys.exit(1)

# STL huong in: lat 180 quanh X, zmin=0
b = open(raw, 'rb').read(); n = int(np.frombuffer(b, '<u4', 1, 80)[0])
rec = np.frombuffer(b, np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), n, 84).copy()
Rm = np.diag([1.0, -1.0, -1.0]); v = rec['v'].astype(float) @ Rm.T; v[..., 2] -= v[..., 2].min()
rec['v'] = v.astype('<f4'); rec['n'] = (rec['n'].astype(float) @ Rm.T).astype('<f4')
open(os.path.join(STLD, 'mount.stl'), 'wb').write(b[:84] + rec.tobytes()); os.remove(raw)
body = json.load(open(res, encoding='utf-8'))[-1]['bodies'][0]
rep = {"volume_mm3": body.get('volume_mm3'), "bbox": body['bbox'], "closed": body.get('closed'), "shells": body.get('kernel', {}).get('shells')}
json.dump(rep, open(os.path.join(HERE, 'build-report.json'), 'w'), indent=1)

# Anh duyet: chong vien len anh goc
try:
    from PIL import Image, ImageDraw
    img = Image.open(r"D:/HONOR Share/Honor Share/IMG_20261113_085228_edit_859872405454222.jpg").convert('RGB')
    d = ImageDraw.Draw(img, 'RGBA'); px = lambda q: (q[0] * K + OX, OY - q[1] * K)
    d.polygon([px(q) for q in poly], fill=(0, 200, 255, 70), outline=(0, 230, 255, 255))
    d.polygon([px(q) for q in lip], fill=(80, 255, 80, 120))
    for c, dd, col in [(pa, PA['d'], (255, 220, 0)), (pa, PA['shoulder_d'], (255, 220, 0)), (hb, BB['id'], (255, 80, 80)), (hb, BB['od'], (255, 80, 80))]:
        x, y = px(c); rr = dd / 2 * K; d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=col + (255,), width=4)
    img.save(os.path.join(HERE, '..', 'review', 'overlay.png'))
except Exception as e:
    print('overlay loi:', e)
json.dump(EDGES, open(os.path.join(HERE, 'edges.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 11)); pp = np.array(poly + [poly[0]])
    ax.fill(pp[:, 0], pp[:, 1], color='#cfe8ff'); ax.plot(pp[:, 0], pp[:, 1], 'k-', lw=1.5)
    lp = np.array(lip + [lip[0]]); ax.fill(lp[:, 0], lp[:, 1], color='#7ee08a'); 
    for c0, d0, col in [(pa, PA['shoulder_d'], 'orange'), (pa, PA['d'], 'orange'), (hb, BB['od'], 'red'), (hb, BB['id'], 'red')]:
        ax.add_patch(plt.Circle(c0, d0 / 2, fill=False, color=col, lw=2))
    for e in EDGES:
        if 'nhan' in e:
            ax.annotate('%s %.1f' % (e['ma'], e['dai_mm']), e['nhan'], ha='center', va='center', fontsize=11, color='navy', weight='bold')
    ax.annotate('E%d cung R%.1f' % (nseg + 1, r_out), (cx + (r_out + 3) * math.cos(amid), (r_out + 3) * math.sin(amid)), ha='center', color='green', weight='bold')
    for t_, p_ in [('A', pa), ('B', hb), ('D', [0, 0])]:
        ax.annotate(t_, (p_[0] + 1.5, p_[1] + 1.5), color='crimson', fontsize=14, weight='bold')
    ax.plot([pa[0], hb[0]], [pa[1], hb[1]], 'm--'); ax.annotate('C %.1f' % P['C_mm'], ((pa[0] + hb[0]) / 2, (pa[1] + hb[1]) / 2 + 1), color='m', weight='bold')
    ax.plot(0, 0, 'k+', ms=15)
    allp = np.array(poly + [e['nhan'] for e in EDGES if 'nhan' in e])
    ax.set_xlim(allp[:, 0].min() - 4, allp[:, 0].max() + 4); ax.set_ylim(allp[:, 1].min() - 3, allp[:, 1].max() + 3)
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_xlabel('X mm (goc = tam dai oc D)'); ax.set_ylabel('Y mm')
    ax.set_title('Ga cam bien tay thang - nhin tu tren (ma canh = note trong .sc)')
    plt.savefig(os.path.join(HERE, '..', 'review', 'edges-named.png'), dpi=80, bbox_inches='tight')
except Exception as e:
    print('ban ve loi:', e)
ok = rep['closed'] is not False and (rep['shells'] in (None, 1))
print('px/mm', round(K, 2)); print('MOUNT', 'PASS' if ok else 'FAIL', rep); sys.exit(0 if ok else 1)
