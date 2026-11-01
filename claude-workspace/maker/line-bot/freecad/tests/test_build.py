# Gate dung model line-bot tu tham so (Claude viet 2026-11-01, executor KHONG sua). Chay tu maker/line-bot:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P freecad/tests -t test_build
# Dung ban tam (bien LINEBOT_OUT) - khong dong freecad/line_bot.FCStd that.
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import FreeCAD as App

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
PROJ = HERE.parent.parent
SCRIPT = PROJ / "freecad" / "scripts" / "build_line_bot.py"
PARAMS = PROJ / "freecad" / "params.json"
FCC = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
V = App.Vector

IN = ["Base_plate", "Top_plate", "Motor_mount_L", "Motor_mount_R", "Caster_mount", "Line_bracket", "Sonar_bracket"]
REF = ["Ref_Mega", "Ref_N20_L", "Ref_N20_R", "Ref_Wheel_L", "Ref_Wheel_R", "Ref_Ball", "Ref_Line_array",
       "Ref_Sonar", "Ref_Battery", "Ref_Driver"]


def build(tmp, params=PARAMS):
    out = tmp / "line_bot.FCStd"
    env = dict(os.environ, LINEBOT_OUT=str(out), LINEBOT_PARAMS=str(params))
    r = subprocess.run([str(FCC), str(SCRIPT)], capture_output=True, text=True, timeout=900, env=env,
                       creationflags=0x08000000)
    assert out.exists(), f"khong ra file\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
    doc = App.openDocument(str(out))
    objs = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.Shape.Solids}
    return doc, objs


class TBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="linebot-test-"))
        cls.P = json.loads(PARAMS.read_text(encoding="utf-8"))
        cls.doc, cls.o = build(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        App.closeDocument(cls.doc.Name)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_01_du_doi_tuong(self):
        for lb in IN + REF:
            self.assertIn(lb, self.o, f"thieu {lb}; co: {sorted(self.o)}")

    def test_02_chi_tiet_in_hop_le(self):
        for lb in IN:
            s = self.o[lb].Shape
            self.assertEqual(len(s.Solids), 1, f"{lb}: {len(s.Solids)} solid")
            self.assertTrue(s.isValid(), lb)
            self.assertGreater(s.Volume, 100, lb)

    def test_03_kich_thuoc_bao(self):
        bb = App.BoundBox()
        for o in self.o.values():
            bb.add(o.Shape.BoundBox)
        b = self.P["bao"]
        self.assertLessEqual(bb.XLength, b["max_x"] + 1e-6, bb)
        self.assertLessEqual(bb.YLength, b["max_y"] + 1e-6, bb)
        self.assertLessEqual(bb.ZLength, b["max_z"] + 1e-6, bb)
        self.assertGreaterEqual(bb.ZMin, -0.05, bb)

    def test_04_xe_dung_thang(self):
        # 2 banh + bi cung cham san (z = 0) -> xe thang, cam bien dung chieu cao
        for lb in ("Ref_Wheel_L", "Ref_Wheel_R"):
            self.assertAlmostEqual(self.o[lb].Shape.BoundBox.ZMin, 0.0, delta=0.05, msg=lb)
        self.assertAlmostEqual(self.o["Ref_Ball"].Shape.BoundBox.ZMin, 0.0, delta=0.3)
        # bi phai nam sau truc banh (concept A: cam bien truoc, bi sau)
        self.assertLess(self.o["Ref_Ball"].Shape.BoundBox.Center.x, -20)

    def test_05_cam_bien_line_cach_san(self):
        lp = self.P["linh_kien"]["line"]
        bb = self.o["Ref_Line_array"].Shape.BoundBox
        self.assertAlmostEqual(bb.ZMin, lp["cao_san"], delta=0.2)
        self.assertGreater(bb.Center.x, 20, "mang do line phai o phia truoc truc banh")
        self.assertLess(abs(bb.Center.y), 0.5, "mang do line phai nam giua xe")

    def test_06_lo_mega_khop(self):
        # Mega dat tren Top_plate qua cot co lo M3 tu ren: tai tam moi lo dung, truc thang dung xuyen qua cot phai rong
        # (lo) va vong ban kinh 0,5 x cot_d phai la nhua
        mp = self.P["linh_kien"]["mega"]
        mb = self.o["Ref_Mega"].Shape.BoundBox
        top = self.o["Top_plate"].Shape
        tb = top.BoundBox
        r_ren = self.P["lo_vit"]["m3_tu_ren"] / 2
        for i in mp["lo_dung"]:
            x, y = mb.XMin + mp["lo"][i][0], mb.YMin + mp["lo"][i][1]
            self.assertFalse(top.isInside(V(x, y, tb.ZMax - 0.5), 0.01, True), f"lo {i} bi bit tai ({x:.2f},{y:.2f})")
            self.assertTrue(top.isInside(V(x + r_ren + 0.6, y, tb.ZMax - 0.5), 0.01, True),
                            f"quanh lo {i} khong co nhua cho vit an")
        self.assertGreaterEqual(mb.ZMin, tb.ZMax - 0.01, "Mega phai nam tren Top_plate")

    def test_07_khong_chong_nhau(self):
        labels = IN + REF
        for i, a in enumerate(labels):
            for b in labels[i + 1:]:
                if a.startswith("Ref_") and b.startswith("Ref_"):
                    continue
                sa, sb = self.o[a].Shape, self.o[b].Shape
                if not sa.BoundBox.intersect(sb.BoundBox):
                    continue
                v = sa.common(sb).Volume
                self.assertLess(v, 0.5, f"{a} chong {b}: {v:.2f} mm3")

    def test_08_khe_motor(self):
        # Mat hop so AP vach gia (bat vit M1.6) - dung thiet ke. Khe chi kiem o 4 mat ben + dau sau cua than motor:
        # diem cach mat motor 0,75 x khe ra ngoai phai la khong khi (khong nam trong gia). Claude sua 2026-11-01.
        k = self.P["khung"]["khe"]
        n = self.P["linh_kien"]["n20"]
        e = 0.75 * k
        for s, sg in (("L", 1), ("R", -1)):
            m = self.o[f"Motor_mount_{s}"].Shape
            b = self.o[f"Ref_N20_{s}"].Shape.BoundBox
            zc = b.ZMin + n["h"] / 2 if b.ZLength > n["h"] else b.Center.z
            body_y0 = sg * 59.0 - sg * (n["dai"] - n["truc_dai"] + n["dai_encoder_them"])   # dau sau than
            ym = (sg * 59.0 + body_y0) / 2                                                   # giua than
            pts = {"ben +x": V(n["w"] / 2 + e, ym, zc), "ben -x": V(-n["w"] / 2 - e, ym, zc),
                   "tren": V(0, ym, zc + n["h"] / 2 + e), "duoi": V(0, ym, zc - n["h"] / 2 - e),
                   "dau sau": V(0, body_y0 - sg * e, zc)}
            for ten, p in pts.items():
                self.assertFalse(m.isInside(p, 0.01, True), f"N20_{s} sat gia o {ten} (khe < {e:.2f} mm)")
            self.assertLess(self.o[f"Ref_N20_{s}"].Shape.common(m).Volume, 0.01, f"N20_{s} chong gia")

    def test_09_doi_tham_so(self):
        # doi banh 42 -> 48 va cot 35 -> 40: model dung lai, banh + bi van cham san, cam bien van 3 mm
        P2 = json.loads(PARAMS.read_text(encoding="utf-8"))
        P2["linh_kien"]["banh"]["d"] = 48.0
        P2["khung"]["cot_cao"] = 40.0
        p2 = self.tmp / "params2.json"
        p2.write_text(json.dumps(P2), encoding="utf-8")
        t2 = self.tmp / "b2"
        t2.mkdir()
        doc2, o2 = build(t2, p2)
        try:
            self.assertAlmostEqual(o2["Ref_Wheel_L"].Shape.BoundBox.ZMin, 0.0, delta=0.05)
            self.assertAlmostEqual(o2["Ref_Wheel_L"].Shape.BoundBox.ZLength, 48.0, delta=0.1)
            self.assertAlmostEqual(o2["Ref_Ball"].Shape.BoundBox.ZMin, 0.0, delta=0.3)
            self.assertAlmostEqual(o2["Ref_Line_array"].Shape.BoundBox.ZMin, 3.0, delta=0.2)
            self.assertGreater(o2["Top_plate"].Shape.BoundBox.ZMin, self.o["Top_plate"].Shape.BoundBox.ZMin + 4)
        finally:
            App.closeDocument(doc2.Name)
