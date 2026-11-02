# Gate tao dang phuong an B (Tuan chon 2026-11-02) - Claude viet, executor KHONG sua. Chay tu maker/cyberbrick-arm:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P freecad/tests -t test_form
# Khung (khop, tam voi, khong chong) van do test_skeleton giu - gate chay CA HAI.
import json
import math
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import FreeCAD as App

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
PROJ = HERE.parent.parent
SCRIPT = PROJ / "freecad" / "scripts" / "build_arm.py"
PARAMS = PROJ / "freecad" / "params.json"
FCC = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
V = App.Vector


class TFormB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="arm-form-"))
        cls.P = json.loads(PARAMS.read_text(encoding="utf-8"))
        out = cls.tmp / "arm.FCStd"
        env = dict(os.environ, ARM_OUT=str(out), ARM_PARAMS=str(PARAMS), ARM_POSE="nghi")
        r = subprocess.run([str(FCC), str(SCRIPT)], capture_output=True, text=True, timeout=900, env=env,
                           creationflags=0x08000000)
        assert out.exists(), r.stdout[-1500:] + r.stderr[-1500:]
        cls.doc = App.openDocument(str(out))
        cls.o = {x.Label: x for x in cls.doc.Objects if x.isDerivedFrom("Part::Feature") and x.Shape.Solids}
        cls.j = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
        cls.F = cls.P["dang"]

    @classmethod
    def tearDownClass(cls):
        App.closeDocument(cls.doc.Name)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def fa(self, s, n, y):
        """Diem trong he cang tay -> the gioi."""
        J2, J3 = V(*self.j["J2"]), V(*self.j["J3"])
        d = (J3 - J2).normalize()
        nn = V(-d.z, 0, d.x)
        return J2 + d * s + nn * n + V(0, y, 0)

    def test_01_co_khoi_dang(self):
        self.assertIn("dang", self.P, "params.json thieu khoi 'dang' (Claude them)")
        self.assertEqual(self.F["phuong_an"], "B")

    def test_02_vat_day_foot(self):
        f = self.o["Foot_plate"].Shape
        h = self.P["de"]["tam_day"]["rong"] / 2
        v = self.F["vat_day"]
        self.assertFalse(f.isInside(V(h - v / 3, 0, v / 3), 0.01, True), "Foot_plate: canh day chua vat")
        self.assertTrue(f.isInside(V(h - 0.5, 0, 3.0), 0.01, True))

    def test_03_khe_tan_nhiet_de(self):
        d = self.o["Base_drum"].Shape
        r = self.P["de"]["trong"]["d_ngoai"] / 2 - self.P["de"]["trong"]["thanh"] / 2
        k = self.F["khe_tan_nhiet"]
        z = (k["z"][0] + k["z"][1]) / 2
        for i in range(k["so"]):
            a = math.radians(k["goc_tam"] + (i - (k["so"] - 1) / 2) * k["buoc_goc"])
            self.assertFalse(d.isInside(V(r * math.cos(a), r * math.sin(a), z), 0.01, True), f"thieu khe {i}")
        a = math.radians(k["goc_tam"] + 90)
        self.assertTrue(d.isInside(V(r * math.cos(a), r * math.sin(a), z), 0.01, True), "thanh trong o ngoai vung khe")

    def test_04_vat_cang_tay_khong_thung_khoang_s3(self):
        fo = self.o["Forearm"].Shape
        c = self.P["cang_tay"]
        L, nmax, v = c["L"], c["n_truoc"][1], self.F["vat_cang_tay"]
        self.assertFalse(fo.isInside(self.fa(L - 1.0, nmax - 1.0, 0), 0.01, True), "goc tren-truoc chua vat")
        self.assertTrue(fo.isInside(self.fa(L - 1.0, nmax - v - 0.5, 0), 0.01, True), "vat qua sau")
        # thanh quanh S3: diem cach goc khoang S3 ra ngoai 1,2 mm theo phap tuyen mat vat phai la nhua
        s3 = self.o["CB_Servo9g_S3"].Shape
        J2, J3 = V(*self.j["J2"]), V(*self.j["J3"])
        d = (J3 - J2).normalize()
        nn = V(-d.z, 0, d.x)
        best = max(s3.Vertexes, key=lambda p: (p.Point - J2).dot(d) + (p.Point - J2).dot(nn)).Point
        q = best + (d + nn).normalize() * (self.P["khe"] + 1.2)
        q.y = 0
        self.assertTrue(fo.isInside(q, 0.01, True), "mat vat lam thung khoang S3 (thanh < 1,2)")

    def test_05_logo_hai_mat(self):
        fo = self.o["Forearm"].Shape
        lg = self.F["logo"]
        y0 = self.P["cang_tay"]["y"][1]
        for sg in (1, -1):
            pts = [self.fa(s, n, sg * (y0 - lg["sau"] / 2))
                   for s in [lg["s"] - lg["dai"] / 2 + i * lg["dai"] / 30 for i in range(31)]
                   for n in [lg["n"] - lg["cao"] / 2 + k * lg["cao"] / 10 for k in range(11)]]
            rong = sum(1 for p in pts if not fo.isInside(p, 0.01, True)) / len(pts)
            self.assertTrue(0.05 < rong < 0.7, f"logo mat {'+' if sg > 0 else '-'}Y: ti le khac {rong:.2f}")

    def test_06_tay_tren_bat_giac_om_horn(self):
        r = self.P["tay_tren"]["r_dau"] - 0.5
        for lab in ("Arm_upper_L", "Arm_upper_R"):
            sh = self.o[lab].Shape
            yc = (sh.BoundBox.YMin + sh.BoundBox.YMax) / 2
            for J in (self.j["J1"], self.j["J2"]):
                for k in range(8):
                    a = math.radians(22.5 + 45 * k)
                    p = V(J[0] + r * math.cos(a), yc, J[2] + r * math.sin(a))
                    self.assertTrue(sh.isInside(p, 0.01, True), f"{lab}: horn O20 lo ra o goc {k}")

    def test_07_nhieu_mat_hon_hop(self):
        # da bo/vat: moi chi tiet vo chinh co nhieu mat hon hop tron
        for lab in ("Base_drum", "Turntable", "Forearm", "Head", "Switch_holder", "Arm_upper_L"):
            self.assertGreater(len(self.o[lab].Shape.Faces), 14, f"{lab}: chua bo/vat")


if __name__ == "__main__":
    unittest.main()
