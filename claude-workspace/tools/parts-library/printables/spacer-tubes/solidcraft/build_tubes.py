"""Ong tru rong (spacer) bang SolidCraft. So lieu: params.json (mm). Truc Z, day z=0 = huong in (dung).
Ra: build/<ten>.sc, stl/<ten>.stl, spacer-tubes.sc (lap rap, moi ong 1 component), build-report.json.
Chay: python build_tubes.py"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLI = os.environ.get('SOLIDCRAFT_CLI', r'C:\Program Files\SolidCraft\solidcraft-cli.exe')
T = json.load(open(os.path.join(HERE, 'params.json'), encoding='utf-8'))['tubes']
BUILD = os.path.join(HERE, 'build'); STLD = os.path.join(HERE, 'stl')
os.makedirs(BUILD, exist_ok=True); os.makedirs(STLD, exist_ok=True)

def sh(args, what):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode != 0:
        sys.stderr.write('%s LOI (exit %d):\n%s\n%s\n' % (what, r.returncode, r.stdout[-2500:], r.stderr[-2500:])); sys.exit(1)

report = {}
for kind, p in T.items():
    name = kind.replace('-', '_').replace('.', 'p')
    stl = os.path.join(STLD, kind + '.stl').replace(os.sep, '/')
    cmds = [
        {"command": "solid.cylinder", "params": {"diameter": p['od'], "height": p['h'], "base": [0, 0, 0], "axis": "Z",
                                                 "operation": "new_body", "body_name": name}},
        {"command": "solid.cylinder", "params": {"diameter": p['id'], "height": p['h'] + 0.2, "base": [0, 0, -0.1], "axis": "Z",
                                                 "operation": "cut", "targets": [name]}},
        {"command": "file.export_stl", "params": {"path": stl, "bodies": [name], "quality": "fine"}},
        {"command": "inspect.measure", "params": {}},
    ]
    jp = os.path.join(BUILD, kind + '.json'); json.dump({"commands": cmds}, open(jp, 'w'), indent=1)
    res = os.path.join(BUILD, kind + '.result.json')
    sh([CLI, 'run', jp, '--save', os.path.join(BUILD, kind + '.sc'), '--results', '--json-out', res, '--quiet'], 'build ' + kind)
    b = json.load(open(res, encoding='utf-8'))[-1]['bodies'][0]
    report[kind] = {"params": p, "volume_mm3": b.get('volume_mm3'), "bbox": b['bbox'], "closed": b.get('closed')}

asm = [{"command": "component.insert_design", "params": {"path": os.path.join(BUILD, k + '.sc').replace(os.sep, '/'),
        "name": k, "translate": [20 * i, 0, 0]}} for i, k in enumerate(T)]
jp = os.path.join(BUILD, 'assembly.json'); json.dump({"commands": asm}, open(jp, 'w'))
sh([CLI, 'run', jp, '--save', os.path.join(HERE, 'spacer-tubes.sc'), '--quiet'], 'lap rap')
json.dump(report, open(os.path.join(HERE, 'build-report.json'), 'w', encoding='utf-8'), indent=1)

# Gate: the tich ly thuyet pi/4*(od^2-id^2)*h, sai < 1 %
import math
ok = True
for k, r in report.items():
    p = r['params']; v0 = math.pi / 4 * (p['od'] ** 2 - p['id'] ** 2) * p['h']; v = r['volume_mm3'] or 0
    err = abs(v - v0) / v0 * 100; ok &= err < 1 and r['closed'] is not False
    print('%-22s V=%.1f mm3 (ly thuyet %.1f, sai %.2f %%) bbox=%s' % (k, v, v0, err, r['bbox']))
print('TUBES', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
