# Gate CAD v1 Cu con (Claude viet 2026-11-09, executor KHONG sua). Spec: ../spec-cad-v1.md
# Chay tu maker/card-coding-robot/solidcraft:
#   ../../../tools/model-study/.venv/Scripts/python.exe tests/test_build.py
import itertools
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np
import trimesh

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent.parent
P = json.loads((HERE / "params.json").read_text(encoding="utf-8"))
FC_PY = Path(r"C:/Program Files/FreeCAD 1.1/bin/python.exe")  # co yaml cho slice.py
SLICE = HERE.parents[2] / "tools" / "robotics-cad" / "scripts" / "slice.py"
PRINT_YAML = HERE.parent / "print" / "print.yaml"

PRINT = ["Chassis", "Battery_lid", "Shell", "Top", "Belly", "Eye_L", "Eye_R", "Pupil_L", "Pupil_R",
         "Diffuser_L", "Diffuser_R", "Beak", "Wing_Run", "Wing_Clear", "Wheel_L", "Wheel_R", "Coupon"]
REF = ["Ref_Motor_L", "Ref_Motor_R", "Ref_ULN_L", "Ref_ULN_R", "Ref_ESP32", "Ref_RC522", "Ref_Speaker",
       "Ref_Amp", "Ref_Battery", "Ref_Btn_Run", "Ref_Btn_Clear", "Ref_LED_L", "Ref_LED_R"]
CAPTURED = ["Eye_L", "Eye_R", "Pupil_L", "Pupil_R", "Diffuser_L", "Diffuser_R", "Beak", "Belly", "Wing_Run", "Wing_Clear"]
REF_MASS = {"Ref_Motor_L": P["motor_28byj48"]["mass_g"], "Ref_Motor_R": P["motor_28byj48"]["mass_g"],
            "Ref_ULN_L": P["uln2003_board"]["mass_g"], "Ref_ULN_R": P["uln2003_board"]["mass_g"],
            "Ref_ESP32": P["esp32_devkit"]["mass_g"], "Ref_RC522": P["rc522"]["mass_g"],
            "Ref_Speaker": P["speaker"]["mass_g"], "Ref_Amp": P["max98357"]["mass_g"],
            "Ref_Battery": P["battery_4aa"]["mass_g"]}
ASM_ONLY = ["Coupon"]  # coupon khong nam tren robot


def hull2d(pts):
    pts = sorted(set(map(tuple, np.round(pts, 4))))
    if len(pts) < 3:
        return pts
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]  # nguoc chieu kim dong ho


def inside_dist(h, q):
    """khoang cach >0 neu q nam trong da giac loi h (CCW), <0 neu ngoai."""
    d = 1e9
    for i in range(len(h)):
        a, b = np.array(h[i]), np.array(h[(i + 1) % len(h)])
        e = b - a
        n = np.array([-e[1], e[0]]) / np.linalg.norm(e)  # phap tuyen huong vao trong
        d = min(d, float(np.dot(np.array(q) - a, n)))
    return d


class TOwl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([sys.executable, str(HERE / "build_owl.py")], capture_output=True, text=True,
                           timeout=1200, cwd=HERE)
        cls.log = r.stdout[-3000:] + r.stderr[-3000:]
        assert r.returncode == 0 and "OWL OK" in r.stdout, "build loi: " + cls.log
        cls.rep = json.loads((HERE / "build-report.json").read_text(encoding="utf-8"))["bodies"]
        cls.m = {}
        for n in PRINT + REF:
            f = HERE / "out" / "asm" / (n.lower() + ".stl")
            assert f.exists(), "thieu " + str(f)
            cls.m[n] = trimesh.load(f, force="mesh")
        cls.robot = [n for n in PRINT if n not in ASM_ONLY]

    def test_01_bodies_closed(self):
        for n in PRINT:
            self.assertIn(n, self.rep, "build-report thieu " + n)
            self.assertTrue(self.rep[n]["closed"], n + " khong kin")
            self.assertEqual(self.rep[n]["shells"], 1, n + " nhieu shell")
            self.assertTrue(self.m[n].is_watertight, n + " STL lap rap khong kin")

    def test_02_bbox(self):
        v = np.vstack([self.m[n].vertices for n in self.robot])
        ext = v.max(0) - v.min(0)
        for k in range(3):
            self.assertLessEqual(ext[k], P["max_bbox"][k] + 0.01, "bao truc %d = %.1f" % (k, ext[k]))

    def test_03_turn_in_cell(self):
        cl, cr = self.m["Wheel_L"].bounding_box.centroid, self.m["Wheel_R"].bounding_box.centroid
        mid = (cl + cr) / 2
        self.assertLessEqual(abs(mid[0]), 1.0, "truc banh lech X %.2f" % mid[0])
        self.assertLessEqual(abs(mid[1]), 1.0, "truc banh lech Y %.2f" % mid[1])
        self.assertLessEqual(abs(cl[0] - cr[0]), 1.0, "2 banh khong cung truc (dX %.2f)" % (cl[0] - cr[0]))
        v = np.vstack([self.m[n].vertices for n in self.robot])
        rmax = float(np.max(np.hypot(v[:, 0], v[:, 1])))
        self.assertLessEqual(rmax, P["max_turn_radius"], "ban kinh quay %.1f" % rmax)

    def test_04_ground(self):
        for n in ("Wheel_L", "Wheel_R", "Chassis"):
            z = self.m[n].vertices[:, 2].min()
            self.assertTrue(-0.3 <= z <= 0.3, "%s phai cham san (zmin %.2f)" % (n, z))
        for n in [x for x in self.robot + REF if x not in ("Wheel_L", "Wheel_R", "Chassis")]:
            z = self.m[n].vertices[:, 2].min()
            self.assertGreaterEqual(z, P["ground_clearance_min"] - 0.01, "%s qua sat san (zmin %.2f)" % (n, z))
        sh = hull2d(self.m["Shell"].vertices[:, :2])
        for n in ("Wheel_L", "Wheel_R"):
            for q in self.m[n].vertices[:, :2]:
                self.assertGreaterEqual(inside_dist(sh, q), -0.01, n + " lo ra ngoai hinh chieu Shell (ngon tay)")

    def test_05_tip_angle(self):
        rho = P["petg_density_g_cm3"] / 1000.0 * P["print_fill_factor"]
        ms, cs = [], []
        for n in self.robot:
            ms.append(self.m[n].volume * rho)
            cs.append(self.m[n].center_mass)
        for n, g in REF_MASS.items():
            ms.append(g)
            cs.append(self.m[n].bounding_box.centroid)
        ms, cs = np.array(ms), np.array(cs)
        com = (ms[:, None] * cs).sum(0) / ms.sum()
        contact = np.vstack([self.m[n].vertices[self.m[n].vertices[:, 2] < 0.3][:, :2]
                             for n in ("Wheel_L", "Wheel_R", "Chassis")])
        h = hull2d(contact)
        self.assertGreaterEqual(len(h), 3, "da giac chong < 3 diem")
        d = inside_dist(h, com[:2])
        self.assertGreater(d, 0, "trong tam nam ngoai da giac chong")
        ang = math.degrees(math.atan2(d, com[2]))
        print("\n  khoi luong %.0f g, trong tam (%.1f, %.1f, %.1f), goc lat %.1f deg" % (ms.sum(), *com, ang))
        self.assertGreaterEqual(ang, P["tip_angle_min_deg"], "goc lat %.1f" % ang)
        self.assertLessEqual(self.m["Ref_Battery"].vertices[:, 2].max(), P["battery_z_max"], "pin dat qua cao")

    def test_06_no_interference(self):
        names = self.robot + REF
        bad = []
        for a, b in itertools.combinations(names, 2):
            if {a[:5], b[:9]} == {"Wheel", "Ref_Motor"} or {b[:5], a[:9]} == {"Wheel", "Ref_Motor"}:
                continue
            ba, bb = self.m[a].bounds, self.m[b].bounds
            if np.any(ba[1] < bb[0]) or np.any(bb[1] < ba[0]):
                continue
            x = trimesh.boolean.intersection([self.m[a], self.m[b]], engine="manifold")
            if x is not None and not x.is_empty and x.volume > 2.0:
                bad.append("%s x %s %.1f mm3" % (a, b, x.volume))
        self.assertFalse(bad, "va cham: " + "; ".join(bad))

    def test_07_card_gap(self):
        rc = self.m["Ref_RC522"]
        c = rc.bounding_box.centroid
        o = np.array([[c[0], c[1], rc.bounds[1][2] + 0.01]])
        hits = []
        for n in self.robot:
            loc, _, _ = self.m[n].ray.intersects_location(o, np.array([[0, 0, 1.0]]), multiple_hits=True)
            hits += [(float(p[2]) - o[0, 2], n) for p in loc]
        hits.sort()
        self.assertTrue(hits, "khong co gi tren RC522")
        self.assertEqual(hits[0][1], "Top", "mat dau tien tren RC522 la %s (phai Top)" % hits[0][1])
        self.assertLessEqual(hits[0][0], P["rc522"]["card_gap_max"], "RC522 cach Top %.1f" % hits[0][0])
        top = [h for h, n in hits if n == "Top"]
        self.assertGreaterEqual(len(top), 2)
        self.assertLessEqual(top[1] - top[0], 2.05, "day ranh the day %.2f" % (top[1] - top[0]))

    def test_08_captured_parts(self):
        """chi tiet trang tri lap tu trong: day ra ngoai 5 mm phai vuong Shell/chi tiet khac."""
        for n in CAPTURED:
            m = self.m[n]
            c = m.center_mass
            d = np.array([c[0], c[1], 0.0])
            if np.linalg.norm(d) < 1e-6:
                d = np.array([0, 0, 1.0])
            d /= np.linalg.norm(d)
            mv = m.copy()
            mv.apply_translation(d * 5.0)
            hit = False
            for o in [x for x in self.robot if x != n]:
                x = trimesh.boolean.intersection([mv, self.m[o]], engine="manifold")
                if x is not None and not x.is_empty and x.volume > 0.5:
                    hit = True
                    break
            self.assertTrue(hit, n + " rut ra ngoai duoc (khong co go chan tu trong)")

    def test_09_print_stl(self):
        for n in PRINT:
            f = HERE / "stl" / (n.lower() + ".stl")
            self.assertTrue(f.exists(), "thieu " + str(f))
            m = trimesh.load(f, force="mesh")
            self.assertAlmostEqual(float(m.bounds[0][2]), 0.0, delta=0.02, msg=n + " STL in khong dat zmin=0")
            self.assertLessEqual(float(np.max(m.extents)), 250, n + " qua ban A1")
            self.assertAlmostEqual(m.volume, self.m[n].volume, delta=max(1.0, 0.005 * m.volume),
                                   msg=n + " STL in khac the tich ban lap rap")

    def test_10_slice(self):
        self.assertTrue(PRINT_YAML.exists(), "thieu print/print.yaml")
        r = subprocess.run([str(FC_PY), str(SLICE), str(PRINT_YAML)], capture_output=True, text=True,
                           timeout=1800, cwd=PRINT_YAML.parent)
        rep_f = PRINT_YAML.parent / "plates" / "print-report.json"
        self.assertTrue(rep_f.exists(), "slice khong ra print-report.json: " + r.stdout[-1500:] + r.stderr[-1500:])
        rep = json.loads(rep_f.read_text(encoding="utf-8"))
        self.assertFalse(rep["stl_chua_xep"], "STL chua xep ban: %s" % rep["stl_chua_xep"])
        for b in rep["ban"]:
            print("  %s: %s %.0f ph %.1f g" % (b["ban"], b["trang_thai"], b["thoi_gian_s"] / 60, b["gam"]))
            self.assertEqual(b["trang_thai"], "PASS", "%s: %s %s" % (b["ban"], b["loi"], b["canh_bao"]))
            self.assertFalse(b["support"], b["ban"] + " dung support")


if __name__ == "__main__":
    unittest.main(verbosity=2)
