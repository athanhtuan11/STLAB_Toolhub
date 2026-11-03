# Gate dung vo camera mau D tu tham so (Claude viet 2026-11-03, executor KHONG sua). Chay tu maker/esp32-s3-cam/freecad:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P tests -t test_build
# Dung ban tam (bien CAMD_OUT) - khong dong file that.
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import FreeCAD as App
import Mesh

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
FC = HERE.parent
SCRIPT = FC / "scripts" / "build_cam_d.py"
PARAMS = FC / "params.json"
FCC = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
V = App.Vector

PRINT = ["Body", "Bezel", "U_frame", "Base", "Pin_cap", "Coupon", "Coupon_ring"]
REF = ["Ref_Stack", "Ref_Cam", "Ref_Screw_L", "Ref_Screw_R"]
STL = ["body", "bezel", "u_frame", "base", "pin_cap", "coupon", "coupon_ring"]


def build(tmp):
    out = tmp / "cam_d.FCStd"
    env = dict(os.environ, CAMD_OUT=str(out), CAMD_PARAMS=str(PARAMS))
    r = subprocess.run([str(FCC), str(SCRIPT)], capture_output=True, text=True, timeout=900, env=env,
                       creationflags=0x08000000)
    assert out.exists(), "khong ra file\n%s\n%s" % (r.stdout[-1500:], r.stderr[-1500:])
    doc = App.openDocument(str(out))
    objs = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.Shape.Solids}
    return doc, objs, out


class TBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="camd-test-"))
        P = json.loads(PARAMS.read_text(encoding="utf-8"))
        cls.P = P
        cls.doc, cls.o, cls.out = build(cls.tmp)
        T, M, S, N, D = P["than"], P["mat_truoc"], P["mach"], P["truc_nghieng"], P["de_xoay"]
        cls.zd = D["de_cao"] - D["lom_sau"] + D["dia_day"]
        cls.zp = cls.zd + N["cao_tam_tren_dia"]
        cls.y0 = -(T["d"] + M["t"]) / 2 + M["t"]
        cls.ypcb = cls.y0 + 0.5 + S["cam_cao_tren_pcb"]
        cls.zl = cls.zp + S["pcb_h"] / 2 - S["ong_kinh_cach_canh_tren"]

    @classmethod
    def tearDownClass(cls):
        App.closeDocument(cls.doc.Name)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def inside(self, lb, x, y, z):
        return self.o[lb].Shape.isInside(V(x, y, z), 0.01, True)

    def test_01_du_doi_tuong(self):
        for lb in PRINT + REF:
            self.assertIn(lb, self.o, "thieu %s; co: %s" % (lb, sorted(self.o)))

    def test_02_chi_tiet_in_hop_le(self):
        for lb in PRINT:
            s = self.o[lb].Shape
            self.assertEqual(len(s.Solids), 1, "%s: %d solid" % (lb, len(s.Solids)))
            self.assertTrue(s.isValid(), lb)
            self.assertGreater(s.Volume, 50, lb)

    def test_03_kich_thuoc_bao(self):
        T, M, D, U, N = self.P["than"], self.P["mat_truoc"], self.P["de_xoay"], self.P["khung_u"], self.P["truc_nghieng"]
        tol = 0.25
        b = self.o["Body"].Shape.BoundBox
        self.assertAlmostEqual(b.XLength, T["w"], delta=tol)
        self.assertAlmostEqual(b.ZLength, T["h"], delta=tol)
        self.assertAlmostEqual(b.YMin, self.y0, delta=tol)
        self.assertAlmostEqual(b.YMax, self.y0 + T["d"], delta=tol)
        self.assertAlmostEqual(b.ZMin, self.zp - T["h"] / 2, delta=tol)
        z = self.o["Bezel"].Shape.BoundBox
        # tam mat truoc y0-t..y0; 4 cot chan nho ra sau toi y_pcb - khe
        self.assertAlmostEqual(z.YMin, self.y0 - M["t"], delta=tol)
        self.assertAlmostEqual(z.YMax, self.ypcb - self.P["mach"]["khe_moi_ben"], delta=tol)
        self.assertAlmostEqual(z.XLength, T["w"], delta=tol)
        bb = self.o["Base"].Shape.BoundBox
        self.assertAlmostEqual(bb.XLength, D["de_d"], delta=tol)
        self.assertAlmostEqual(bb.ZMin, 0, delta=tol)
        self.assertAlmostEqual(bb.ZMax, D["de_cao"], delta=tol)
        u = self.o["U_frame"].Shape.BoundBox
        self.assertAlmostEqual(u.ZMin, self.zd - D["dia_day"], delta=tol)
        self.assertAlmostEqual(u.ZMax, self.zd + U["tay_cao"], delta=0.5)
        self.assertAlmostEqual(u.XLength, D["dia_d"], delta=tol)
        # tong cao ca cum ~ 96 mm (dang Tuan duyet)
        top = max(self.o[l].Shape.BoundBox.ZMax for l in ["Body", "Bezel", "U_frame", "Base"])
        self.assertLess(abs(top - (self.zp + T["h"] / 2)), 0.5, "dinh cum %.2f" % top)

    def test_04_khong_giao_nhau(self):
        pairs = [("Body", "Bezel"), ("Body", "U_frame"), ("Bezel", "U_frame"), ("U_frame", "Base"),
                 ("Pin_cap", "U_frame"), ("Pin_cap", "Base"), ("Ref_Stack", "Body"), ("Ref_Stack", "Bezel"),
                 ("Ref_Cam", "Bezel"), ("Ref_Cam", "Body")]
        for a, b in pairs:
            v = self.o[a].Shape.common(self.o[b].Shape).Volume
            self.assertLess(v, 0.05, "%s giao %s: %.3f mm3" % (a, b, v))

    def test_05_mach_vua_hoc(self):
        S = self.P["mach"]
        s = self.o["Ref_Stack"].Shape.BoundBox
        self.assertAlmostEqual(s.XLength, S["pcb_w"], delta=0.05)
        self.assertAlmostEqual(s.ZLength, S["pcb_h"], delta=0.05)
        self.assertAlmostEqual(s.YLength, S["stack_t"], delta=0.05)
        self.assertAlmostEqual(s.YMin, self.ypcb, delta=0.05)
        k = S["khe_moi_ben"]
        # dan huong: co vat lieu Body ngay ngoai khe ben (gan), khong co trong khe
        xg = S["pcb_w"] / 2 + k
        found = any(self.inside("Body", sx * (xg + 0.4), self.ypcb + S["stack_t"] / 2, self.zp + dz)
                    for sx in (1, -1) for dz in (8, 12, 16, -8, -12, -16))
        self.assertTrue(found, "khong thay gan dan huong mach o |x| = %.2f" % xg)
        self.assertFalse(self.inside("Body", xg - 0.1, self.ypcb + S["stack_t"] / 2, self.zp + 12), "gan lan vao khe")

    def test_06_ong_kinh_den(self):
        M = self.P["mat_truoc"]
        yc = self.y0 - M["t"] / 2
        self.assertFalse(self.inside("Bezel", 0, yc, self.zl), "lo ong kinh khong xuyen")
        r = M["lo_ong_kinh_d"] / 2
        self.assertFalse(self.inside("Bezel", r - 0.1, yc, self.zl), "lo ong kinh nho hon %.2f" % M["lo_ong_kinh_d"])
        self.assertTrue(self.inside("Bezel", r + 0.3, self.y0 - 0.3, self.zl), "lo ong kinh qua to")
        zled = self.zl - M["den_duoi_ong_kinh"]
        for sx in (1, -1):
            x = sx * M["den_cach_nhau"] / 2
            ytruoc = self.y0 - M["t"]
            self.assertTrue(self.inside("Bezel", x, ytruoc + M["den_da_mong"] / 2, zled), "mat da mong den")
            self.assertFalse(self.inside("Bezel", x, ytruoc + M["den_da_mong"] + 0.3, zled), "khong co lo mu den")
        c = self.o["Ref_Cam"].Shape.BoundBox
        self.assertAlmostEqual((c.ZMin + c.ZMax) / 2, self.zl, delta=0.1)
        self.assertAlmostEqual(c.YMin, self.y0 + 0.5, delta=0.1)

    def test_07_truc_nghieng(self):
        T, N, U = self.P["than"], self.P["truc_nghieng"], self.P["khung_u"]
        xi = T["w"] / 2 + N["khe_tay_than"]
        for sx in (1, -1):
            # lo truc xuyen tay U va than tai (y=0, z=zp)
            for x in (xi + 1, xi + U["tay_day"] - 1, T["w"] / 2 - 1):
                lb = "U_frame" if x > T["w"] / 2 else "Body"
                self.assertFalse(self.inside(lb, sx * x, 0, self.zp), "%s co vat lieu tren truc x=%.1f" % (lb, sx * x))
            self.assertTrue(self.inside("U_frame", sx * (xi + 1), 0, self.zp + N["m3_xuyen"] / 2 + 0.3), "lo M3 tay qua to")
            # hoc dai oc: rong hon lo M3 trong do sau dai_oc_sau tinh tu mat trong tru
            xin = T["w"] / 2 - T["thanh"] - N["tru_than_dai"]
            p = sx * (xin + N["dai_oc_sau"] / 2)
            self.assertFalse(self.inside("Body", p, 0, self.zp + N["dai_oc_s"] / 2 - 0.25), "khong co hoc dai oc")
            self.assertTrue(self.inside("Body", p, 0, self.zp + N["dai_oc_s"] / 2 + 0.6), "hoc dai oc qua to")
            # vit M3x12 an dai oc: dau vit o mat loc, mui vit qua mat trong hoc dai oc
            seat = xi + U["tay_day"] - N["loc_dau_vit_sau"]
            self.assertLessEqual(seat - 12.0, xin + 0.3, "vit M3x12 khong toi dai oc")
            self.assertGreaterEqual(seat - 12.0, xin - 3.0, "vit M3x12 thua qua dai vao trong (cham mach?)")
        # nghieng +-30 khong cham dia
        b = self.o["Body"].Shape.copy()
        for ang in (30, -30):
            r = b.copy()
            r.rotate(V(0, 0, self.zp), V(1, 0, 0), ang)
            self.assertLess(r.common(self.o["U_frame"].Shape).Volume, 0.05, "nghieng %d cham khung U" % ang)

    def test_08_de_xoay(self):
        D, M = self.P["de_xoay"], self.P["mat_truoc"]
        zf = D["de_cao"] - D["lom_sau"]
        self.assertTrue(self.inside("Base", D["chot_d"] / 2 - 0.15, 0, zf + 2), "chot nho hon %.1f" % D["chot_d"])
        self.assertFalse(self.inside("Base", D["chot_d"] / 2 + 0.1, 0, zf + 2), "chot to hon %.1f" % D["chot_d"])
        self.assertFalse(self.inside("U_frame", D["lo_dia_d"] / 2 - 0.1, 0, zf + 2), "lo dia nho hon %.1f" % D["lo_dia_d"])
        self.assertTrue(self.inside("U_frame", D["lo_dia_d"] / 2 + 0.2, 0, zf + 2), "lo dia to qua")
        self.assertFalse(self.inside("Base", 0, 0, zf + 1), "thieu lo tu ren M2.5 trong chot")
        for sx in (1, -1):
            self.assertFalse(self.inside("Base", sx * D["lo_khoa_cach"] / 2, 0, 2), "thieu lo vit tuong")
        self.assertTrue(self.inside("Base", 20, 20, 0.3), "mat day phai phang/dac")
        cap = self.o["Pin_cap"].Shape.BoundBox
        self.assertAlmostEqual(cap.XLength, D["nap_chot_d"], delta=0.2)
        self.assertLessEqual(cap.ZMax, self.zd + 0.01, "nap chot nho len khoi dia")

    def test_09_khe_nhiet_usb(self):
        T, U, K = self.P["than"], self.P["usb"], self.P["khe_nhiet"]
        S = self.P["mach"]
        zb = self.zp - T["h"] / 2 + T["thanh"] / 2
        zt = self.zp + T["h"] / 2 - T["thanh"] / 2
        yb = self.ypcb + 2 + K["dai"] / 2
        nb = sum(1 for x in (14, 17.5, 21, -14, -17.5, -21) if not self.inside("Body", x, yb, zb))
        self.assertGreaterEqual(nb, 6, "khe hut duoi: %d/6" % nb)
        yt = self.y0 + 3 + K["dai"] / 2
        nt = sum(1 for x in (-10, -6, -2, 2, 6, 10) if not self.inside("Body", x, yt, zt))
        self.assertGreaterEqual(nt, 6, "khe thoat tren: %d/6" % nt)
        yu = self.ypcb + S["stack_t"] - U["o_sau_y"] / 2
        self.assertFalse(self.inside("Body", 0, yu, zb), "thieu o USB")
        self.assertFalse(self.inside("Body", U["o_rong_x"] / 2 - 2, yu, zb), "o USB hep")

    def test_10_coupon(self):
        c = self.o["Coupon"].Shape
        self.assertGreater(len(c.Faces), 40, "coupon qua it chi tiet")
        r = self.o["Coupon_ring"].Shape.BoundBox
        self.assertAlmostEqual(r.XLength, 15, delta=0.2)

    def test_11_stl_huong_in(self):
        d = self.out.parent / "stl"
        for n in STL:
            p = d / (n + ".stl")
            self.assertTrue(p.exists(), "thieu stl/%s.stl" % n)
            m = Mesh.Mesh(str(p))
            self.assertGreater(m.CountFacets, 20, n)
            self.assertAlmostEqual(m.BoundBox.ZMin, 0, delta=0.05, msg="%s chua dat mat in xuong z=0" % n)
        # Body in nam mat sau xuong ban: chieu cao in = T.d
        mb = Mesh.Mesh(str(d / "body.stl")).BoundBox
        self.assertAlmostEqual(mb.ZLength, self.P["than"]["d"], delta=0.3, msg="body.stl phai in nam mat sau xuong")
        mz = Mesh.Mesh(str(d / "bezel.stl")).BoundBox
        self.assertLess(mz.ZLength, self.P["mat_truoc"]["t"] + 7.5, "bezel.stl phai in mat truoc xuong")


if __name__ == "__main__":
    unittest.main()
