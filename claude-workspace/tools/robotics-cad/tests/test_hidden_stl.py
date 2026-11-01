# Gate bai hoc inbox 2026-10-25 (Claude viet, executor KHONG sua):
#  - "cong cu bo qua thu gi phai bao, khong im lang": check.py phai liet ke chi tiet AN (FAIL tru khi hidden-ok)
#  - "kiem tren artifact cuoi": export-stl.py so the tich STL voi model, lech -> WARN/FAIL
# Chay tu tools/robotics-cad:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P tests -t test_hidden_stl
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import FreeCAD as App
import Part

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = HERE.parent / "scripts"
FCC = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
V = App.Vector


def chay(*args):
    return subprocess.run([str(FCC), *map(str, args)], capture_output=True, text=True, timeout=600,
                          creationflags=0x08000000)


class THiddenStl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="hidden-stl-test-"))
        doc = App.newDocument("hiddenstl")
        a = doc.addObject("Part::Box", "A")
        a.Label, a.Length, a.Width, a.Height = "Visible_box", 10, 10, 10
        h = doc.addObject("Part::Box", "H")
        h.Label, h.Length, h.Width, h.Height = "Hidden_leaf", 10, 10, 10
        h.Placement.Base = V(100, 0, 0)
        h.Visibility = False
        b = doc.addObject("Part::Box", "B")
        b.Label, b.Length, b.Width, b.Height = "Cut_base", 20, 20, 10
        b.Placement.Base = V(0, 100, 0)
        t = doc.addObject("Part::Cylinder", "T")
        t.Label, t.Radius, t.Height = "Cut_tool", 3, 10
        t.Placement.Base = V(10, 110, 0)
        c = doc.addObject("Part::Cut", "C")
        c.Label, c.Base, c.Tool = "Cut_result", b, t
        b.Visibility = t.Visibility = False   # dau vao boolean an la DUNG, khong duoc bao
        s = doc.addObject("Part::Sphere", "S")
        s.Label, s.Radius = "Ball", 5
        s.Placement.Base = V(0, -100, 5)
        doc.recompute()
        cls.fcstd = cls.tmp / "model.FCStd"
        doc.saveAs(str(cls.fcstd))
        App.closeDocument(doc.Name)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def check(self, out, *extra):
        r = chay(SCRIPTS / "check.py", "--pass", self.fcstd, f"out={out}", *extra)
        rep = json.loads((out / "report.json").read_text(encoding="utf-8"))
        return r, rep

    def test_hidden_fail(self):
        r, rep = self.check(self.tmp / "c1")
        an = rep["chi_tiet_an"]
        self.assertEqual(an["nhan"], ["Hidden_leaf"], an)   # Cut_base/Cut_tool la dau vao -> khong tinh
        self.assertEqual(an["trang_thai"], "FAIL", an)
        self.assertEqual(rep["ket_luan"], "FAIL")
        self.assertEqual(r.returncode, 1, r.stdout[-500:])

    def test_hidden_ok(self):
        r, rep = self.check(self.tmp / "c2", "hidden-ok=Hidden_*")
        an = rep["chi_tiet_an"]
        self.assertEqual(an["nhan"], ["Hidden_leaf"], an)
        self.assertEqual(an["trang_thai"], "INFO", an)
        self.assertNotEqual(rep["ket_luan"], "FAIL", r.stdout[-800:])

    def export(self, ten, mesh):
        y = self.tmp / f"{ten}.yaml"
        y.write_text(json.dumps({"fcstd": "model.FCStd", "stl": f"stl-{ten}", "export": {
            "mesh": mesh, "rules": [{"names": ["Visible_box"], "group": "01"}, {"names": ["Ball"], "group": "02"}]}}),
            encoding="utf-8")   # JSON la YAML hop le
        r = chay(SCRIPTS / "export-stl.py", "--pass", y)
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        return json.loads((self.tmp / f"stl-{ten}" / "_export-stl.json").read_text(encoding="utf-8"))

    def test_stl_volume_fine(self):
        j = self.export("fine", {"linear_mm": 0.03, "angular_rad": 0.2618})
        tt = j["the_tich"]
        self.assertEqual(set(tt), {"01__Visible_box.stl", "02__Ball.stl"}, tt)
        box = tt["01__Visible_box.stl"]
        self.assertAlmostEqual(box["model_mm3"], 1000, delta=0.5)
        self.assertAlmostEqual(box["stl_mm3"], 1000, delta=0.5)
        self.assertLess(abs(box["lech_pct"]), 0.01)
        self.assertEqual(j["stl_lech"], [], j)

    def test_stl_volume_coarse(self):
        j = self.export("coarse", {"linear_mm": 1.5, "angular_rad": 1.0})
        ball = j["the_tich"]["02__Ball.stl"]
        self.assertGreater(abs(ball["lech_pct"]), 2.0, ball)
        lech = {x["file"]: x for x in j["stl_lech"]}
        self.assertEqual(set(lech), {"02__Ball.stl"}, lech)
        self.assertEqual(lech["02__Ball.stl"]["trang_thai"], "FAIL")
