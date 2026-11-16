# Gate CAD v1 xe A block-coding-car (Claude 2026-11-16; executor KHONG sua). Spec: ../spec-cad-v1.md
# Chay tu maker/block-coding-car/solidcraft:
#   ..\..\..\tools\model-study\.venv\Scripts\python.exe tests\test_build.py
# Mau: maker/card-coding-robot/solidcraft/tests/test_build.py
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
SLICE = HERE.parents[2] / "tools" / "print" / "scripts" / "slice.py"
PRINT_YAML = HERE.parent / "print" / "print.yaml"
SKIP_SLICE = "--no-slice" in sys.argv

SKIDS = ["Skid_Main", "Skid_Tip_L", "Skid_Tip_R", "Skid_Tip_F"]  # Claude 2026-11-16: chan truot tach rieng, vit tu trong
PRINT = ["Chassis", "Battery_lid", *SKIDS, "Deck", "Body", "Face", "Diffuser_L", "Diffuser_R", "Eye_holder",
         "Stop_cap", "Btn_holder", "Wheel_L", "Wheel_R", "Coupon"]
REF = ["Ref_Motor_L", "Ref_Motor_R", "Ref_ULN_L", "Ref_ULN_R", "Ref_ESP32", "Ref_Buck", "Ref_Amp", "Ref_Speaker",
       "Ref_Battery", "Ref_Switch", "Ref_MX", "Ref_LED_L", "Ref_LED_R"]
# chi tiet lap tu trong: day theo huong nay 5 mm phai vuong chi tiet khac (khong rut ra tu ngoai duoc)
CAPTURED = {"Face": (1, 0, 0), "Diffuser_L": (1, 0, 0), "Diffuser_R": (1, 0, 0), "Stop_cap": (0, 0, 1)}
REF_MASS = {"Ref_Motor_L": P["motor_28byj48"]["mass_g"], "Ref_Motor_R": P["motor_28byj48"]["mass_g"],
            "Ref_ULN_L": P["uln2003_board"]["mass_g"], "Ref_ULN_R": P["uln2003_board"]["mass_g"],
            "Ref_ESP32": P["esp32_s3"]["mass_g"], "Ref_Buck": P["buck_boost"]["mass_g"],
            "Ref_Amp": P["max98357"]["mass_g"], "Ref_Speaker": P["speaker"]["mass_g"],
            "Ref_Battery": P["battery_4aa"]["mass_g"]}
ASM_ONLY = ["Coupon"]  # coupon khong nam tren xe
COLOR_OF = {**{k: "chassis" for k in SKIDS}, "Chassis": "chassis", "Battery_lid": "chassis", "Deck": "chassis", "Body": "body", "Face": "face",
            "Diffuser_L": "diffuser", "Diffuser_R": "diffuser", "Eye_holder": "chassis", "Stop_cap": "stop",
            "Btn_holder": "chassis", "Wheel_L": "wheel", "Wheel_R": "wheel", "Coupon": "chassis"}


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
    return lo[:-1] + up[:-1]


def inside_dist(h, q):
    d = 1e9
    for i in range(len(h)):
        a, b = np.array(h[i]), np.array(h[(i + 1) % len(h)])
        e = b - a
        n = np.array([-e[1], e[0]]) / np.linalg.norm(e)
        d = min(d, float(np.dot(np.array(q) - a, n)))
    return d


def inter_vol(a, b):
    x = trimesh.boolean.intersection([a, b], engine="manifold")
    return 0.0 if x is None or x.is_empty else float(x.volume)


class TCar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = subprocess.run([sys.executable, str(HERE / "build_car.py")], capture_output=True, text=True,
                           timeout=1500, cwd=HERE)
        cls.log = r.stdout[-3000:] + r.stderr[-3000:]
        assert r.returncode == 0 and "CAR OK" in r.stdout, "build loi: " + cls.log
        cls.rep = json.loads((HERE / "build-report.json").read_text(encoding="utf-8"))["bodies"]
        cls.m = {}
        for n in PRINT + REF:
            f = HERE / "out" / "asm" / (n.lower() + ".stl")
            assert f.exists(), "thieu " + str(f)
            cls.m[n] = trimesh.load(f, force="mesh")
        cls.car = [n for n in PRINT if n not in ASM_ONLY]

    def test_01_bodies_closed(self):
        for n in PRINT:
            self.assertIn(n, self.rep, "build-report thieu " + n)
            self.assertTrue(self.rep[n]["closed"], n + " khong kin")
            self.assertEqual(self.rep[n]["shells"], 1, n + " nhieu shell")
            self.assertTrue(self.m[n].is_watertight, n + " STL lap rap khong kin")
        self.assertTrue((HERE / "car.sc").exists(), "thieu car.sc (Tuan mo do)")

    def test_02_bbox(self):
        v = np.vstack([self.m[n].vertices for n in self.car])
        ext = v.max(0) - v.min(0)
        for k in range(3):
            self.assertLessEqual(ext[k], P["max_bbox"][k] + 0.01, "bao truc %d = %.1f" % (k, ext[k]))

    def test_03_wheels_track_turn(self):
        cl, cr = self.m["Wheel_L"].bounding_box.centroid, self.m["Wheel_R"].bounding_box.centroid
        mid = (cl + cr) / 2
        self.assertLessEqual(abs(mid[0]), 0.5, "truc banh lech X %.2f" % mid[0])
        self.assertLessEqual(abs(mid[1]), 0.5, "truc banh lech Y %.2f" % mid[1])
        self.assertLessEqual(abs(cl[0] - cr[0]), 0.3, "2 banh khong cung truc")
        self.assertGreater(cl[1], 0, "Wheel_L phai o +Y (ben trai khi nhin +X)")
        track = abs(cl[1] - cr[1])
        self.assertAlmostEqual(track, P["track_mm"], delta=0.5, msg="vet banh %.2f (PROTOCOL steps_90 tinh theo %.0f)"
                               % (track, P["track_mm"]))
        for n in ("Wheel_L", "Wheel_R"):
            ext = self.m[n].extents
            self.assertAlmostEqual(max(ext[0], ext[2]), P["wheel"]["rim_d"], delta=0.3, msg=n + " sai O vanh")
        v = np.vstack([self.m[n].vertices for n in self.car])
        rmax = float(np.max(np.hypot(v[:, 0], v[:, 1])))
        print("\n  vet banh %.2f mm, ban kinh quay %.1f mm" % (track, rmax))
        self.assertLessEqual(rmax, P["max_turn_radius"], "ban kinh quay %.1f" % rmax)

    def test_04_ground_and_hidden_wheels(self):
        # banh: vanh O45 + O-ring -> diem cham san that = z 0; vanh in cach san (od - rim)/2
        lift = (P["wheel"]["od"] - P["wheel"]["rim_d"]) / 2
        for n in ("Wheel_L", "Wheel_R"):
            self.assertAlmostEqual(float(self.m[n].bounds[0][2]), lift, delta=0.2, msg=n + " sai do cao truc")
            c = self.m[n].bounding_box.centroid
            self.assertAlmostEqual(c[2], P["wheel"]["od"] / 2, delta=0.3, msg=n + " truc khong o z = od/2")
        zc = self.m["Skid_Main"].vertices[:, 2].min()
        self.assertAlmostEqual(zc, P["skid"]["main"][2], delta=0.15, msg="chan truot chinh phai cham san (z %.2f)" % zc)
        c = self.m["Skid_Main"].bounding_box.centroid
        self.assertLess(math.hypot(c[0] - P["skid"]["main"][0], c[1] - P["skid"]["main"][1]), 1.0, "Skid_Main sai vi tri")
        for n, s in zip(("Skid_Tip_L", "Skid_Tip_R", "Skid_Tip_F"), P["skid"]["anti_tip"]):
            m = self.m[n]
            c = m.bounding_box.centroid
            self.assertLess(math.hypot(c[0] - s[0], c[1] - s[1]), 1.0, n + " sai vi tri %s" % s)
            self.assertAlmostEqual(float(m.vertices[:, 2].min()), s[2], delta=0.2, msg=n + " sai do cao")
        for n in [x for x in self.car + REF if x not in ("Wheel_L", "Wheel_R", *SKIDS)]:
            z = self.m[n].vertices[:, 2].min()
            self.assertGreaterEqual(z, P["ground_clearance_min"] - 0.01, "%s qua sat san (zmin %.2f)" % (n, z))
        bh = hull2d(self.m["Body"].vertices[:, :2])
        for n in ("Wheel_L", "Wheel_R"):
            for q in self.m[n].vertices[:, :2]:
                self.assertGreaterEqual(inside_dist(bh, q), 2.0, n + " qua sat/ngoai hinh chieu Body (ngon tay)")

    def test_05_tip_angle(self):
        rho = P["petg_density_g_cm3"] / 1000.0 * P["print_fill_factor"]
        ms, cs = [], []
        for n in self.car:
            ms.append(self.m[n].volume * rho)
            cs.append(self.m[n].center_mass)
        for n, g in REF_MASS.items():
            ms.append(g)
            cs.append(self.m[n].bounding_box.centroid)
        ms, cs = np.array(ms), np.array(cs)
        com = (ms[:, None] * cs).sum(0) / ms.sum()
        pts = []
        for n in ("Wheel_L", "Wheel_R"):
            c = self.m[n].bounding_box.centroid
            pts.append([c[0], self.m[n].bounds[0][1]])
            pts.append([c[0], self.m[n].bounds[1][1]])
        for n in SKIDS:
            v = self.m[n].vertices
            pts += list(v[v[:, 2] <= P["anti_tip_z_max"]][:, :2])
        h = hull2d(np.array(pts))
        d = inside_dist(h, com[:2])
        self.assertGreater(d, 0, "trong tam nam ngoai da giac chong")
        ang = math.degrees(math.atan2(d, com[2]))
        # 3 diem ti that: trong tam phai nam giua truc banh va chan chinh sau
        main = P["skid"]["main"]
        self.assertLess(com[0], -1.0, "trong tam phai sau truc banh (x %.1f) de ti len chan chinh sau" % com[0])
        self.assertGreater(com[0], main[0] + 10, "trong tam qua sat chan sau")
        print("  khoi luong %.0f g, trong tam (%.1f, %.1f, %.1f), goc lat %.1f deg" % (ms.sum(), *com, ang))
        self.assertGreaterEqual(ang, P["tip_angle_min_deg"], "goc lat %.1f" % ang)
        self.assertLessEqual(self.m["Ref_Battery"].bounding_box.centroid[2], P["battery_cg_z_max"], "pin dat qua cao")
        self.assertLess(self.m["Ref_Battery"].bounding_box.centroid[0], -20, "Ref_Battery phai sau truc")

    def test_06_no_interference(self):
        names = self.car + REF
        bad = []
        for a, b in itertools.combinations(names, 2):
            pair = {a, b}
            if any(p.startswith("Wheel") for p in pair) and any(p.startswith("Ref_Motor") for p in pair):
                continue  # truc ep vao banh
            if pair == {"Stop_cap", "Ref_MX"}:
                continue  # stem MX cam vao mu
            ba, bb = self.m[a].bounds, self.m[b].bounds
            if np.any(ba[1] < bb[0]) or np.any(bb[1] < ba[0]):
                continue
            vol = inter_vol(self.m[a], self.m[b])
            if vol > 2.0:
                bad.append("%s x %s %.1f mm3" % (a, b, vol))
        self.assertFalse(bad, "va cham: " + "; ".join(bad))

    def test_07_stop_button(self):
        sb = P["stop_button"]
        cap, mx, body = self.m["Stop_cap"], self.m["Ref_MX"], self.m["Body"]
        c = cap.bounding_box.centroid
        self.assertAlmostEqual(c[0], sb["x"], delta=0.5)
        self.assertAlmostEqual(c[1], sb["y"], delta=0.5)
        roof_top = body.vertices[:, 2].max()
        self.assertAlmostEqual(roof_top, P["body"]["z_roof_top"], delta=0.2, msg="noc Body sai cao")
        self.assertGreaterEqual(cap.bounds[1][2] - roof_top, sb["mx_travel"] + 1.0,
                                "mu Dung phai nho len khoi noc >= hanh trinh + 1 mm")
        self.assertLess(abs(mx.bounding_box.centroid[0] - sb["x"]) + abs(mx.bounding_box.centroid[1] - sb["y"]), 1.0,
                        "Ref_MX khong dong truc mu")
        # nhan mu xuong het hanh trinh: khong cham Body (go phia duoi khong ket vao noc)
        down = cap.copy()
        down.apply_translation([0, 0, -sb["mx_travel"]])
        self.assertLess(inter_vol(down, body), 0.5, "mu Dung ket vao Body khi nhan")
        self.assertLess(inter_vol(down, self.m["Btn_holder"]), 0.5, "mu Dung cham Btn_holder truoc khi het hanh trinh")

    def test_08_captured_parts(self):
        others = [x for x in self.car]
        for n, d in CAPTURED.items():
            mv = self.m[n].copy()
            mv.apply_translation(np.array(d, float) * 5.0)
            hit = any(inter_vol(mv, self.m[o]) > 0.5 for o in others if o != n)
            self.assertTrue(hit, n + " rut ra ngoai duoc (khong co go chan tu trong)")

    def test_09_print_stl_colors(self):
        cj = HERE / "stl" / "colors.json"
        self.assertTrue(cj.exists(), "thieu stl/colors.json (mau ban in theo thiet ke)")
        colors = json.loads(cj.read_text(encoding="utf-8"))
        for n in PRINT:
            f = HERE / "stl" / (n.lower() + ".stl")
            self.assertTrue(f.exists(), "thieu " + str(f))
            m = trimesh.load(f, force="mesh")
            self.assertAlmostEqual(float(m.bounds[0][2]), 0.0, delta=0.02, msg=n + " STL in khong dat zmin=0")
            self.assertLessEqual(float(np.max(m.extents[:2])), 250, n + " qua ban A1")
            self.assertAlmostEqual(m.volume, self.m[n].volume, delta=max(1.0, 0.005 * m.volume),
                                   msg=n + " STL in khac the tich ban lap rap")
            self.assertEqual(colors.get(f.name, "").upper(), P["colors"][COLOR_OF[n]].upper(), n + " sai mau colors.json")

    def test_10_slice(self):
        if SKIP_SLICE:
            self.skipTest("--no-slice")
        self.assertTrue(PRINT_YAML.exists(), "thieu print/print.yaml")
        r = subprocess.run([str(FC_PY), str(SLICE), str(PRINT_YAML)], capture_output=True, text=True,
                           timeout=2400, cwd=PRINT_YAML.parent)
        rep_f = PRINT_YAML.parent / "plates" / "print-report.json"
        self.assertTrue(rep_f.exists(), "slice khong ra print-report.json: " + r.stdout[-1500:] + r.stderr[-1500:])
        rep = json.loads(rep_f.read_text(encoding="utf-8"))
        self.assertFalse(rep["stl_chua_xep"], "STL chua xep ban: %s" % rep["stl_chua_xep"])
        for b in rep["ban"]:
            print("  %s: %s %.0f ph %.1f g" % (b["ban"], b["trang_thai"], b["thoi_gian_s"] / 60, b["gam"]))
            self.assertEqual(b["trang_thai"], "PASS", "%s: %s %s" % (b["ban"], b["loi"], b["canh_bao"]))
            self.assertFalse(b["support"], b["ban"] + " dung support")


if __name__ == "__main__":
    argv = [a for a in sys.argv if a != "--no-slice"]
    unittest.main(argv=argv, verbosity=2)
