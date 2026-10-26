# Test mau cho moi du an (copy tu tools/robotics-cad/project-template, 2026-10-26) - unittest cua FreeCAD, khong mo GUI:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P maker/<project>/freecad/tests -t test_model
# Ban sao file model de thu: MODEL_FCSTD=<duong dan>. Them test YEU CAU cua Tuan vao lop T2Requirements (moi yeu cau 1 test,
# ghi ngay + loi Tuan) - xem maker/pushrod-arm/freecad/tests/test_pushrod_arm.py lam mau.
import fnmatch
import glob
import os
import sys
import unittest

import FreeCAD as App
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.normpath(os.path.join(PROJ, "..", "..", "tools", "robotics-cad", "scripts")))
import assembly_paths  # noqa: E402

FC = os.environ.get("MODEL_FCSTD") or (sorted(glob.glob(os.path.join(PROJ, "freecad", "*.FCStd"))) or [None])[0]
CFG = yaml.safe_load(open(os.path.join(PROJ, "print", "print.yaml"), encoding="utf-8"))
COMPONENTS = ["CB_*", "LK_*", "M2_5x*", "M2x*", "M3x*"]   # linh kien mua: nhieu solid / STEP hang -> bo qua kiem 1 solid
D = {}


def setUpModule():
    if not FC:
        raise unittest.SkipTest("chua co file .FCStd trong freecad/")
    D["doc"] = App.openDocument(FC)
    D["O"] = {o.Label: o for o in D["doc"].Objects if o.isDerivedFrom("Part::Feature") and o.Shape.Solids
              and not o.Label.startswith("_")}


def tearDownModule():
    if "doc" in D:
        App.closeDocument(D["doc"].Name)


def in_print(label):
    return not any(fnmatch.fnmatch(label, p) for p in COMPONENTS)


class T1Geometry(unittest.TestCase):
    def test_has_parts(self):
        self.assertTrue(D["O"], "model khong co chi tiet nao")

    def test_valid_shapes(self):
        """Chi tiet IN phai hop le; STEP linh kien mua hong thi check.py bao WARN (khong phai viec cua minh)."""
        bad = [k for k, o in D["O"].items() if in_print(k) and not o.Shape.isValid()]
        self.assertEqual(bad, [], "hinh hong (isValid False)")

    def test_printed_parts_single_solid(self):
        multi = [k for k, o in D["O"].items() if in_print(k) and len(o.Shape.Solids) != 1]
        self.assertEqual(multi, [], "chi tiet in co nhieu manh (khai multi-solid trong print.yaml neu co chu dich)")

    def test_positive_volume(self):
        neg = [k for k, o in D["O"].items() if in_print(k) and o.Shape.Volume <= 0]
        self.assertEqual(neg, [], "the tich am/0 (loft lon nguoc? xem cad_lib.pos)")

    def test_no_hidden_parts(self):
        hidden = [k for k, o in D["O"].items() if hasattr(o, "Visibility") and not o.Visibility]
        self.assertEqual(hidden, [], "chi tiet dang an - check.py/metrics bo qua chi tiet an (Luu GUI sau khi an de xem?)")


class T1Assembly(unittest.TestCase):
    def test_all_parts_assemblable(self):
        """Moi cap dang cham tach duoc bang tinh tien; ngoai le lay tu print.yaml `assembly.allow` (ghi ly do o do)."""
        if CFG.get("assembly") is None:
            self.skipTest("print.yaml chua co khoi assembly:")
        a = CFG["assembly"] or {}
        allow = [tuple(p.split("|")) for p in a.get("allow", []) if "|" in p]
        known = {tuple(p.split("|")) for p in a.get("known", []) if "|" in p}   # loi DA BIET, dang cho xu ly (TODO)
        res, pairs = assembly_paths.trapped(D["O"], allow=allow)
        moi = [r for r in res if (r[0], r[1]) not in known and (r[1], r[0]) not in known]
        self.assertEqual(moi, [], "cap KHONG lap duoc:\n" + "\n".join("%s | %s %s" % r for r in moi))
        con = sorted({(r[0], r[1]) for r in res} - {(m[0], m[1]) for m in moi})
        if con:
            print("\n  [assembly.known - chua xu ly] " + "; ".join("%s | %s" % c for c in con))


class T2Requirements(unittest.TestCase):
    """Yeu cau rieng cua du an (Tuan). Vd: khe 0,3 mm giua banh rang, tam quay 180 do khong va cham..."""
