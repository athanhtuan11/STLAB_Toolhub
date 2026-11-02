# Gate khung lap rap cyberbrick-arm tu tham so (Claude viet 2026-11-02, executor KHONG sua). Chay tu maker/cyberbrick-arm:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P freecad/tests -t test_skeleton
# Dung 3 tu the vao thu muc tam (ARM_OUT, ARM_POSE) - khong dong freecad/cyberbrick_arm.FCStd that.
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

IN = ["Foot_plate", "Base_drum", "Pinion_24T", "Gearbox_shell", "Switch_holder", "Turntable",
      "Arm_upper_L", "Arm_upper_R", "Forearm", "Head", "Worm", "Finger_L", "Finger_R", "Finger_D"]
CB = ["CB_Servo9g_S1", "CB_Servo9g_S2", "CB_Servo9g_S3", "CB_Motor_030", "CB_Battery_PC003",
      "CB_XA004_receiver", "CB_Switch_XA007"]
# linh kien phai nam trong khoi bao cua chi tiet chua no (hop bao, dung sai 0,5)
CHUA = {"CB_Motor_030": "Gearbox_shell", "CB_XA004_receiver": "Base_drum", "CB_Battery_PC003": "Base_drum",
        "CB_Switch_XA007": "Switch_holder", "CB_Servo9g_S2": "Forearm"}


def build(tmp, pose):
    out = tmp / f"arm_{pose}.FCStd"
    env = dict(os.environ, ARM_OUT=str(out), ARM_PARAMS=str(PARAMS), ARM_POSE=pose)
    r = subprocess.run([str(FCC), str(SCRIPT)], capture_output=True, text=True, timeout=900, env=env,
                       creationflags=0x08000000)
    js = out.with_suffix(".json")
    assert out.exists() and js.exists(), f"khong ra file {out.name}/.json\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
    doc = App.openDocument(str(out))
    objs = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.Shape.Solids}
    return doc, objs, json.loads(js.read_text(encoding="utf-8"))


def fk(P, pose):
    """Dong hoc thuan doc lap voi script: tra J1, J2, J3, T (x, z) + huong cang tay."""
    t1, phi = P["tu_the"][pose]
    x1, z1 = P["vai"]["J1"]
    a = math.radians(t1)
    j2 = (x1 + P["tay_tren"]["L"] * math.cos(a), z1 + P["tay_tren"]["L"] * math.sin(a))
    b = math.radians(t1 + phi)
    d = (math.cos(b), math.sin(b))
    j3 = (j2[0] + P["cang_tay"]["L"] * d[0], j2[1] + P["cang_tay"]["L"] * d[1])
    t = (j3[0] + P["ngon"]["L3"] * d[0], j3[1] + P["ngon"]["L3"] * d[1])
    return (x1, z1), j2, j3, t, d


class TSkeleton(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="arm-test-"))
        cls.P = json.loads(PARAMS.read_text(encoding="utf-8"))
        cls.B = {p: build(cls.tmp, p) for p in cls.P["tu_the"]}

    @classmethod
    def tearDownClass(cls):
        for doc, _, _ in cls.B.values():
            App.closeDocument(doc.Name)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_01_du_doi_tuong(self):
        for p, (_, o, _) in self.B.items():
            thieu = [k for k in IN + CB if k not in o]
            self.assertEqual(thieu, [], f"{p}: thieu {thieu}")

    def test_02_chi_tiet_in_hop_le(self):
        _, o, _ = self.B["nghi"]
        for k in IN:
            s = o[k].Shape
            self.assertTrue(s.isValid(), f"{k} hong")
            self.assertEqual(len(s.Solids), 1, f"{k} co {len(s.Solids)} solid")
            self.assertGreater(s.Volume, 1.0, k)

    def test_03_linh_kien_la_step_that(self):
        # bao linh kien (mm, sap xep) - tu STEP chinh hang; cho phep 1,0 vi bo day/xoay
        _, o, _ = self.B["nghi"]
        mong = {"CB_Battery_PC003": sorted(self.P["linh_kien"]["pin_than"]), "CB_XA004_receiver": [21.5, 29.0, 30.0],
                "CB_Switch_XA007": [19.8, 20.5, 32.0], "CB_Motor_030": [12.0, 15.5, 52.2]}
        for k, m in mong.items():
            b = o[k].Shape.BoundBox
            got = sorted([b.XLength, b.YLength, b.ZLength])
            for g, e in zip(got, m):
                self.assertAlmostEqual(g, e, delta=1.0, msg=f"{k} bao {got} != {m}")
        for s in ("S1", "S2", "S3"):
            b = o[f"CB_Servo9g_{s}"].Shape.BoundBox
            self.assertLess(max(b.XLength, b.YLength, b.ZLength), 40.0, f"S{s}: con day cap? bao qua lon")

    def test_04_dong_hoc_khop_json(self):
        for p, (_, _, j) in self.B.items():
            J1, J2, J3, T, _ = fk(self.P, p)
            for ten, ref in (("J1", J1), ("J2", J2), ("J3", J3), ("T", T)):
                x, y, z = j[ten]
                self.assertAlmostEqual(x, ref[0], delta=0.05, msg=f"{p} {ten}.x")
                self.assertAlmostEqual(z, ref[1], delta=0.05, msg=f"{p} {ten}.z")
                self.assertAlmostEqual(y, 0.0, delta=0.05, msg=f"{p} {ten}.y")
            lo, hi = self.P["gioi_han"]["vai"]
            self.assertTrue(lo <= self.P["tu_the"][p][0] <= hi, f"{p}: goc vai ngoai gioi han")
            lo, hi = self.P["gioi_han"]["khuyu"]
            self.assertTrue(lo <= self.P["tu_the"][p][1] <= hi, f"{p}: goc khuyu ngoai gioi han")

    def test_05_truc_servo_trung_khop(self):
        # truc S1 qua J1, S2 qua J2 (truc // Y, dinh truc huong +Y, dinh <= mat trong tam tay trai);
        # S3 truc doc cang tay, xuyen vao trong Worm.
        yt = self.P["tay_tren"]["y_trong"]
        for p, (_, o, j) in self.B.items():
            for s, J in (("S1", j["J1"]), ("S2", j["J2"])):
                sh = o[f"CB_Servo9g_{s}"].Shape
                hit = [y / 2.0 for y in range(-20, 2 * int(yt) + 1) if sh.isInside(V(J[0], y / 2.0, J[2]), 0.01, True)]
                self.assertTrue(hit, f"{p}: truc {s} khong qua khop")
                self.assertGreater(max(hit) - min(hit), 10.0, f"{p}: {s} chi cham khop {min(hit)}..{max(hit)}")
                self.assertLessEqual(sh.BoundBox.YMax, yt + 0.01, f"{p}: {s} loi qua mat trong tam tay")
                self.assertGreater(sh.BoundBox.YMax, yt - 2.0, f"{p}: dinh truc {s} xa tam tay")
            J2, J3 = V(*j["J2"]), V(*j["J3"])
            d = (J3 - J2).normalize()
            s3 = o["CB_Servo9g_S3"].Shape
            pts = [J2 + d * (self.P["truc_vit"]["s0"] - k * 0.5) for k in range(0, 12)]
            self.assertTrue(any(s3.isInside(q, 0.01, True) for q in pts), f"{p}: truc S3 khong nam tren truc cang tay")
            w = o["Worm"].Shape
            self.assertTrue(w.isInside(J2 + d * (self.P["truc_vit"]["s0"] + 10), 0.01, True), f"{p}: Worm lech truc")

    def test_06_linh_kien_trong_vo(self):
        _, o, _ = self.B["nghi"]
        for c, h in CHUA.items():
            bc, bh = o[c].Shape.BoundBox, o[h].Shape.BoundBox
            bh.enlarge(0.5)
            self.assertTrue(bh.isInside(bc), f"{c} ra ngoai {h}")
        # trong de: moi linh kien ben trong nam trong tru noi
        r_in = self.P["de"]["trong"]["d_ngoai"] / 2 - self.P["de"]["trong"]["thanh"]
        for c in ("CB_Motor_030", "CB_XA004_receiver", "CB_Battery_PC003", "Gearbox_shell"):
            b = o[c].Shape.BoundBox
            for x in (b.XMin, b.XMax):
                for y in (b.YMin, b.YMax):
                    self.assertLessEqual(math.hypot(x, y), r_in + 0.01, f"{c} goc ({x:.1f},{y:.1f}) loi khoi trong de")

    def test_07_khong_chong_nhau_moi_tu_the(self):
        for p, (_, o, _) in self.B.items():
            labels = IN + CB
            for i, a in enumerate(labels):
                for b in labels[i + 1:]:
                    sa, sb = o[a].Shape, o[b].Shape
                    if not sa.BoundBox.intersect(sb.BoundBox):
                        continue
                    v = sa.common(sb).Volume
                    self.assertLess(v, 0.5, f"{p}: {a} chong {b}: {v:.2f} mm3")

    def test_08_tren_mat_ban(self):
        for p, (_, o, _) in self.B.items():
            for k in IN + CB:
                self.assertGreaterEqual(o[k].Shape.BoundBox.ZMin, -0.01, f"{p}: {k} xuyen mat ban")
            self.assertAlmostEqual(o["Foot_plate"].Shape.BoundBox.ZMin, 0.0, delta=0.01)

    def test_09_muc_tieu_tam_voi(self):
        m = self.P["muc_tieu"]
        _, _, j = self.B["vuon_xa"]
        self.assertGreaterEqual(math.hypot(j["T"][0], j["T"][1]), m["tam_voi_min"], "tam voi ngan")
        _, _, j = self.B["gap_ban"]
        self.assertLessEqual(j["T"][2], m["gap_ban_z_max"], "khong gap toi mat ban")
        self.assertGreaterEqual(j["T"][0], m["gap_ban_x_min"], "gap ban qua gan de")
        # dau ngon phai nam trong khoi ngon (Finger_* ket thuc tai T)
        _, o, j = self.B["gap_ban"]
        T = V(*j["T"])
        dmin = min(o[f"Finger_{k}"].Shape.distToShape(Part_vertex(T))[0] for k in "LRD")
        self.assertLess(dmin, self.P["ngon"]["ban_kinh"] + self.P["ngon"]["tiet_dien"], "ngon khong toi dau T")

    def test_10_doi_tham_so(self):
        # doi L tay tren 55,86 -> 65: J2 doi theo, van dung + khong chong
        P2 = json.loads(PARAMS.read_text(encoding="utf-8"))
        P2["tay_tren"]["L"] = 65.0
        p2 = self.tmp / "params2.json"
        p2.write_text(json.dumps(P2), encoding="utf-8")
        out = self.tmp / "b2.FCStd"
        env = dict(os.environ, ARM_OUT=str(out), ARM_PARAMS=str(p2), ARM_POSE="nghi")
        subprocess.run([str(FCC), str(SCRIPT)], capture_output=True, text=True, timeout=900, env=env,
                       creationflags=0x08000000)
        j = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(math.dist(j["J1"], j["J2"]), 65.0, delta=0.05)
        doc = App.openDocument(str(out))
        try:
            o = {x.Label: x for x in doc.Objects if x.isDerivedFrom("Part::Feature") and x.Shape.Solids}
            b = o["Arm_upper_L"].Shape.BoundBox
            self.assertGreater(b.XLength + b.ZLength, 65.0)
        finally:
            App.closeDocument(doc.Name)


def Part_vertex(p):
    import Part
    return Part.Vertex(p)


if __name__ == "__main__":
    unittest.main()
