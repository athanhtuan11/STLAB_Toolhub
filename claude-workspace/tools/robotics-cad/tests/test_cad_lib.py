# Test thu vien dung hinh chung (scripts/cad_lib.py) - unittest cua FreeCAD, khong mo GUI:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P tools/robotics-cad/tests -t test_cad_lib
import math
import os
import sys
import unittest

import FreeCAD as App

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")))
import cad_lib as cl  # noqa: E402

V = App.Vector
TOL = 1e-6


class TBox(unittest.TestCase):
    def test_span_any_order(self):
        a = cl.box(x=(0, 10), y=(-2, 2), z=(0, 5))
        b = cl.box(x=(10, 0), y=(2, -2), z=(5, 0))
        self.assertAlmostEqual(a.Volume, 200, 6)
        self.assertTrue(a.isSame(b) or abs(a.common(b).Volume - 200) < TOL)
        bb = a.BoundBox
        self.assertEqual((bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax), (0, -2, 0, 10, 2, 5))

    def test_keyword_only(self):
        with self.assertRaises(TypeError):
            cl.box((0, 1), (0, 1), (0, 1))   # chong chep nham kieu tham so cu

    def test_empty_span(self):
        with self.assertRaises(ValueError):
            cl.box(x=(1, 1), y=(0, 1), z=(0, 1))


class TCyl(unittest.TestCase):
    def test_axes_and_at(self):
        for ax, at, ctr in (("x", (3, 4), (5, 3, 4)), ("y", (3, 4), (3, 5, 4)), ("z", (3, 4), (3, 4, 5))):
            c = cl.cyl(1.0, ax, (0, 10), at)
            self.assertAlmostEqual(c.Volume, math.pi * 10, 3)
            m = c.BoundBox.Center
            self.assertTrue((m - V(*ctr)).Length < 1e-6, (ax, m))


class TRrect(unittest.TestCase):
    def test_volume_and_extent(self):
        s = cl.rrect("x", (0, 10), (3, 4), 1.5)
        self.assertEqual(len(s.Solids), 1)
        self.assertTrue(s.isValid())
        want = 10 * (6 * 8 - (4 - math.pi) * 1.5 ** 2)   # chu nhat tru 4 goc vuong + 4 phan tu tron
        self.assertAlmostEqual(s.Volume, want, 2)
        bb = s.BoundBox
        self.assertAlmostEqual(bb.YMax, 3, 6)
        self.assertAlmostEqual(bb.ZMax, 4, 6)

    def test_bad_radius(self):
        with self.assertRaises(ValueError):
            cl.rrect("x", (0, 1), (1, 2), 1.5)


class TTeardrop(unittest.TestCase):
    def test_tip_up_45(self):
        r = 2.0
        t = cl.teardrop(r, "y", (0, 8), (0, 10), tip=1)
        self.assertTrue(t.isValid())
        self.assertEqual(len(t.Solids), 1)
        self.assertGreater(t.Volume, math.pi * r * r * 8)                 # lon hon tru tron
        self.assertAlmostEqual(t.BoundBox.ZMax, 10 + r * math.sqrt(2), 3)  # mui 45 do o tren
        self.assertAlmostEqual(t.BoundBox.ZMin, 10 - r, 3)

    def test_tip_down_and_x(self):
        t = cl.teardrop(1.0, "x", (0, 5), (2, 0), tip=-1)
        self.assertAlmostEqual(t.BoundBox.ZMin, -math.sqrt(2), 3)
        self.assertAlmostEqual(t.BoundBox.XMax, 5, 6)

    def test_vertical_rejected(self):
        with self.assertRaises(ValueError):
            cl.teardrop(1.0, "z", (0, 5), (0, 0))


class TFrames(unittest.TestCase):
    def test_local_put_roundtrip(self):
        doc = App.newDocument("t_cadlib")
        try:
            o = doc.addObject("Part::Feature", "P")
            o.Shape = cl.box(x=(0, 1), y=(0, 1), z=(0, 1))
            o.Placement = App.Placement(V(10, 0, 0), App.Rotation(V(0, 0, 1), 30))
            frame = App.Placement(V(5, 5, 0), App.Rotation(V(0, 0, 1), 90))
            before = o.Shape.BoundBox
            s = cl.local(o, frame)
            cl.put(o, s, frame)
            after = o.Shape.BoundBox
            for a in ("XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax"):
                self.assertAlmostEqual(getattr(before, a), getattr(after, a), 6)
        finally:
            App.closeDocument(doc.Name)


class TConstants(unittest.TestCase):
    def test_fit_values(self):
        self.assertEqual((cl.FIT, cl.SLIDE, cl.PIN), (0.2, 0.3, 0.3))
