"""Gate nhanh sau build_horn.py: hop bao + kin + 1 shell, so voi CyberBrick (bao arm) va SG90 (cao 4,87).
Chay: python test_horn.py  (doi chieu duong bao/lo con chi tiet: docs/research-notes/servo-horn-sg90-cyberbrick-fits.md)"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'build-report.json'), encoding='utf-8'))
# kieu: (xmin, xmax, ymin, ymax) theo STEP CyberBrick, z = 0..4,87 theo SG90 Print2Drive
EXP = {'half': (-3.63, 16.05, -3.63, 3.63), 'line': (-16.05, 16.05, -3.63, 3.63), 'cross': (-16.05, 18.46, -8.35, 8.35)}
fail = 0
for k, (x0, x1, y0, y1) in EXP.items():
    b = R[k]; mn, mx = b['bbox']['min'], b['bbox']['max']
    got = (mn[0], mx[0], mn[1], mx[1]); err = max(abs(g - e) for g, e in zip(got, (x0, x1, y0, y1)))
    ok = err < 0.02 and abs(mx[2] - 4.87) < 0.01 and abs(mn[2]) < 0.01 and b['closed'] and b['shells'] == 1
    fail += not ok
    print(f"{'PASS' if ok else 'FAIL'} {k}: sai bao {err:.3f} mm, z {mn[2]:.2f}..{mx[2]:.2f}, V {b['volume_mm3']:.1f} mm3")
sys.exit(1 if fail else 0)
