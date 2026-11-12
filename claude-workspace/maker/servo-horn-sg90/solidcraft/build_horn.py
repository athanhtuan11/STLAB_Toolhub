"""Servo horn in 3D: khop con SG90 (Print2Drive, A1 + PETG da chay) + dang/do dai/rong arm CyberBrick PG001/PG002.
So lieu: tools/model-study/fit-library/fits.json (sg90-horn/*, cyberbrick-horn/*). Truc: tam truc servo = goc toa do,
z=0 mat duoi hub (phia servo), arm doc +X. Ra: build/*.sc, stl/<kieu>.stl (huong in: mat arm up xuong ban), servo-horn.sc,
build-report.json. Chay: python build_horn.py"""
import json, math, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get('SOLIDCRAFT_CLI', r'C:\Program Files\SolidCraft\solidcraft-cli.exe')
P = json.load(open(os.path.join(HERE, 'params.json'), encoding='utf-8'))
H, PL, AR = P['hub'], P['plate'], P['arms']
BUILD = os.path.join(HERE, 'build'); STLD = os.path.join(HERE, 'stl')
os.makedirs(BUILD, exist_ok=True); os.makedirs(STLD, exist_ok=True)

Z1 = H['height']; Z2 = Z1 + PL['t']          # mat tren hub / mat tren arm
R = H['od'] / 2

def build_cmds(name, arms):
    cmd = []
    A = lambda c, **p: cmd.append({"command": c, "params": p})
    tgt = {"operation": "join", "targets": [name]}
    A("solid.cylinder", diameter=H['od'], height=Z2, base=[0, 0, 0], axis="Z", operation="new_body", body_name=name)
    for a in arms:
        # canh thang y = +-(w0 - k*x) tu x=0 (trong hub) toi diem tiep tuyen dau tron (tip_c, tip_r)
        th = math.radians(a['angle']); c, r, w0, k = a['tip_c'], a['tip_r'], a['w0'], a['k']
        q = math.sqrt(1 + k * k)
        ux, uy = math.cos(th), math.sin(th); vx, vy = -uy, ux        # u doc arm, v ngang
        loc = [(0, w0), (c + r * k / q, r / q), (c + r * k / q, -r / q), (0, -w0)]
        pts = [[round(x * ux + y * vx, 4), round(x * uy + y * vy, 4)] for x, y in loc]
        A("sketch.create", plane={"origin": [0, 0, Z1], "x_dir": [1, 0, 0], "y_dir": [0, 1, 0]})
        # 1 bien dang lien: day cung trong hub -> canh tren -> cung dau arm -> canh duoi (tru dau rieng bi loi nhan khi tiep tuyen)
        tip = [round((c + r) * ux, 4), round((c + r) * uy, 4)]
        A("sketch.line", points=[pts[3], pts[0], pts[1]])
        A("sketch.arc.three_point", start=pts[1], end=pts[2], through=tip)
        A("sketch.line", points=[pts[2], pts[3]])
        A("sketch.finish"); A("solid.extrude", distance=PL['t'], **tgt)
    cut = {"operation": "cut", "targets": [name]}
    B = P['bore']   # lo con om truc khia SG90: mieng D_mouth sau z_lead, con toi D_deep o z=Z1
    S = P['screw']  # lo vit xuyen + loe 90 do + hoc dau vit tren mat arm
    z_cb = Z2 - S['cb_depth']; z_cs = z_cb - (S['d_cb'] - S['d']) / 2
    # 1 bien dang (r, z) quay quanh Z: con/tru trung truc cat rieng bi loi nhan truck
    prof = [(0, -0.1), (B['d_mouth'] / 2, -0.1), (B['d_mouth'] / 2, B['z_lead']), (B['d_deep'] / 2, Z1),
            (S['d'] / 2, Z1), (S['d'] / 2, z_cs), (S['d_cb'] / 2, z_cb), (S['d_cb'] / 2, Z2 + 0.1), (0, Z2 + 0.1)]
    A("sketch.create", plane={"origin": [0, 0, 0], "x_dir": [1, 0, 0], "y_dir": [0, 0, 1]})
    A("sketch.line", points=[[round(x, 4), round(z, 4)] for x, z in prof], closed=True)
    A("sketch.finish"); A("solid.revolve", axis="Z", **cut)
    for a in arms:
        th = math.radians(a['angle'])
        for x in a['holes']:
            A("solid.cylinder", diameter=PL['hole_d'], height=PL['t'] + 0.2,
              base=[round(x * math.cos(th), 4), round(x * math.sin(th), 4), Z1 - 0.1], axis="Z", **cut)
    return cmd

def sh(args, what):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        sys.stderr.write('%s LOI (exit %d):\n%s\n%s\n' % (what, r.returncode, r.stdout[-2500:], r.stderr[-2500:])); sys.exit(1)

def flip_stl(src, dst):
    """Lat 180 do quanh X (mat arm xuong ban), zmin = 0."""
    b = open(src, 'rb').read(); n = int(np.frombuffer(b, '<u4', 1, 80)[0])
    rec = np.frombuffer(b, np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), n, 84).copy()
    Rm = np.diag([1.0, -1.0, -1.0])
    v = rec['v'].astype(np.float64) @ Rm.T; v[..., 2] -= v[..., 2].min()
    rec['v'] = v.astype('<f4'); rec['n'] = (rec['n'].astype(np.float64) @ Rm.T).astype('<f4')
    open(dst, 'wb').write(b[:84] + rec.tobytes())

report = {}
for kind, arms in AR.items():
    name = kind.replace('-', '_')
    cmds = build_cmds(name, arms)
    raw = os.path.join(BUILD, kind + '.raw.stl')
    cmds.append({"command": "file.export_stl", "params": {"path": raw.replace(os.sep, '/'), "bodies": [name], "quality": "fine"}})
    cmds.append({"command": "inspect.measure", "params": {}})
    jp = os.path.join(BUILD, kind + '.json'); json.dump({"commands": cmds}, open(jp, 'w'), indent=1)
    res = os.path.join(BUILD, kind + '.result.json')
    sh([CLI, 'run', jp, '--save', os.path.join(BUILD, kind + '.sc'), '--results', '--json-out', res, '--quiet'], 'build ' + kind)
    flip_stl(raw, os.path.join(STLD, kind + '.stl')); os.remove(raw)
    for b in json.load(open(res, encoding='utf-8'))[-1]['bodies']:
        report[kind] = {"volume_mm3": b.get('volume_mm3'), "bbox": b['bbox'], "closed": b.get('closed'),
                        "shells": b.get('kernel', {}).get('shells')}

# Lap rap: 3 kieu dat canh nhau theo Y (moi kieu 1 component, dung toa do truc servo)
asm = []
for i, kind in enumerate(AR):
    asm.append({"command": "component.insert_design", "params": {"path": os.path.join(BUILD, kind + '.sc').replace(os.sep, '/'), "name": kind, "translate": [0, -45 * i, 0]}})
jp = os.path.join(BUILD, 'assembly.json'); json.dump({"commands": asm}, open(jp, 'w'))
sh([CLI, 'run', jp, '--save', os.path.join(HERE, 'servo-horn.sc'), '--quiet'], 'lap rap')
json.dump(report, open(os.path.join(HERE, 'build-report.json'), 'w', encoding='utf-8'), indent=1)
print('HORN OK', {k: round(v['volume_mm3'] or 0, 1) for k, v in report.items()})
