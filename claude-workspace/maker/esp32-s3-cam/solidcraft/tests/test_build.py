# Gate vo camera mau D dung bang SolidCraft (Claude viet 2026-11-05, executor KHONG sua).
# Chay tu maker/esp32-s3-cam/solidcraft:   python tests/test_build.py
# So tham chieu = ban FreeCAD cu (build_cam_d.py, params 2026-11-05: pcb_h 40, stack_t 18) - do bang freecadcmd.
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CLI = Path(r"C:\Program Files\SolidCraft\solidcraft-cli.exe")
BUILD = HERE / "build_cam_d.py"
PRINT = ["Body", "Bezel", "U_frame", "Base", "Pin_cap", "Coupon", "Coupon_ring"]
REF = ["Ref_Stack", "Ref_Cam"]
# Label: (the tich mm3, (dx, dy, dz) bao trong he toa do lap rap) - tu FreeCAD
FC = {
    "Body": (35726.3, (56.0, 37.0, 64.0)),     # 2026-11-05 lui mach 2,5 mm (de ong kinh 8,5 tu khay the)
    "Bezel": (9943.3, (56.0, 11.7, 64.0)),    # 2026-11-05 lo ong kinh 15,0 (Tuan chot) + chan ty mach dai them 2,5
    "U_frame": (45917.4, (76.0, 76.0, 76.0)),
    "Base": (39134.5, (86.0, 86.0, 10.0)),
    "Pin_cap": (295.6, (14.0, 14.0, 2.0)),
    "Coupon": (10474.5, (99.5, 46.5, 10.0)),  # 2026-11-05 noi Y cho hang lo ong kinh 14,2/14,6/15,0
    "Coupon_ring": (485.2, (15.0, 15.0, 4.0)),
}
VOL_TOL = 0.01   # 1 %: chu khac + lo con ne loi nhan (top_radius - 0,3)
BB_TOL = 0.05    # mm


def stl_bbox(p):
    b = Path(p).read_bytes()
    n = struct.unpack("<I", b[80:84])[0]
    assert len(b) == 84 + 50 * n, "%s khong phai STL nhi phan hop le" % p
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for i in range(n):
        v = struct.unpack("<9f", b[84 + 50 * i + 12:84 + 50 * i + 48])
        for k in range(9):
            a = k % 3
            lo[a] = min(lo[a], v[k])
            hi[a] = max(hi[a], v[k])
    return lo, hi, n


class TBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="camd-sc-"))
        env = dict(os.environ, CAMD_OUT=str(cls.tmp))
        r = subprocess.run([sys.executable, str(BUILD)], capture_output=True, text=True, timeout=900, env=env)
        cls.log = r.stdout[-3000:] + r.stderr[-3000:]
        assert r.returncode == 0, "build loi:\n" + cls.log
        cls.sc = cls.tmp / "cam_d.sc"
        assert cls.sc.exists(), "khong ra cam_d.sc\n" + cls.log
        e = subprocess.run([str(CLI), "eval", "--in", str(cls.sc)], capture_output=True, text=True, timeout=600)
        t = e.stdout
        cls.ev = json.loads(t[t.index("{"):])
        cls.bodies = {b["name"]: b for b in cls.ev.get("bodies", [])}

    def test_01_du_body(self):
        for n in PRINT + REF:
            self.assertIn(n, self.bodies, "thieu body %s" % n)

    def test_02_the_tich(self):
        for n, (v, _) in FC.items():
            got = self.bodies[n]["volume_mm3"]
            self.assertAlmostEqual(got, v, delta=v * VOL_TOL, msg="%s the tich %.1f, FreeCAD %.1f" % (n, got, v))

    def test_03_bao(self):
        for n, (_, d) in FC.items():
            bb = self.bodies[n]["bbox"]
            got = [bb["max"][i] - bb["min"][i] for i in range(3)]
            for i in range(3):
                self.assertAlmostEqual(got[i], d[i], delta=BB_TOL, msg="%s bao %s, FreeCAD %s" % (n, got, d))

    def test_04_mot_khoi(self):
        # moi chi tiet in la 1 khoi dong kin (khong manh roi)
        for n in PRINT:
            b = self.bodies[n]
            self.assertTrue(b.get("closed"), "%s khong kin" % n)
            self.assertEqual(b.get("kernel", {}).get("shells"), 1, "%s co %s shell" % (n, b.get("kernel", {}).get("shells")))

    def test_05_stl_huong_in(self):
        d = self.tmp / "stl"
        for n in PRINT:
            p = d / (n.lower() + ".stl")
            self.assertTrue(p.exists(), "thieu stl/%s" % p.name)
            lo, hi, tri = stl_bbox(p)
            self.assertGreater(tri, 12)
            self.assertAlmostEqual(lo[2], 0.0, delta=0.01, msg="%s khong nam tren ban (zmin %.3f)" % (p.name, lo[2]))
        lo, hi, _ = stl_bbox(d / "body.stl")
        self.assertAlmostEqual(hi[2] - lo[2], 37.0, delta=0.1, msg="body.stl phai in nam mat sau xuong (cao 37)")
        lo, hi, _ = stl_bbox(d / "bezel.stl")
        self.assertAlmostEqual(hi[2] - lo[2], 11.7, delta=0.1, msg="bezel.stl phai in mat truoc xuong")
        for n, dz in (("u_frame", 76.0), ("base", 10.0), ("pin_cap", 2.0), ("coupon", 10.0), ("coupon_ring", 4.0)):
            lo, hi, _ = stl_bbox(d / (n + ".stl"))
            self.assertAlmostEqual(hi[2] - lo[2], dz, delta=0.1, msg="%s.stl sai huong in" % n)
        for n in REF:
            self.assertFalse((d / (n.lower() + ".stl")).exists(), "khong xuat STL cho %s" % n)

    def test_07_ong_kinh_chui_lo(self):
        # 2026-11-05: ong kinh xoay D14 chui qua lo bezel, khe >= 0,3/ben, nho ra truoc mat vo
        P = json.loads((HERE / "params.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual((P["mat_truoc"]["lo_ong_kinh_d"] - P["mach"]["ong_kinh_d"]) / 2, 0.3 - 1e-9)
        cam = self.bodies["Ref_Cam"]["bbox"]; bez = self.bodies["Bezel"]["bbox"]
        self.assertLess(cam["min"][1], bez["min"][1] - 5, "ong kinh phai nho ra truoc mat vo")

    def test_06_doc_params(self):
        src = BUILD.read_text(encoding="utf-8")
        self.assertIn("params.json", src)
        for so in ("40.5", "22.0", "27.6", "41.1"):
            self.assertNotIn(so, src, "so cung %s trong build - phai lay tu params.json" % so)


if __name__ == "__main__":
    unittest.main(verbosity=2)
