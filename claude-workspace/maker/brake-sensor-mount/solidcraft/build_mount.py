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
ok = rep['closed'] is not False and (rep['shells'] in (None, 1))
print('px/mm', round(K, 2)); print('MOUNT', 'PASS' if ok else 'FAIL', rep); sys.exit(0 if ok else 1)
