# Test yeu cau thiet ke pushrod-arm - chay bang bo test cua FreeCAD (unittest), khong mo GUI:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P maker/pushrod-arm/freecad/tests -t test_pushrod_arm
# Moi test = 1 yeu cau cua Tuan (ghi ngay). Sua model xong chay lai: do = hong yeu cau nao.
import json
import math
import os
import sys
import unittest

import FreeCAD as App

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.normpath(os.path.join(HERE, "..", "pushrod_arm.FCStd"))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "robotics-cad", "scripts")))
import fast_collide  # noqa: E402

TAGS = ("Shoulder", "Elbow")
FIT_GAP = 0.3       # Tuan 2026-10-24: khe lap co cau banh rang + truot 0,3 mm
TOL = 0.02          # dung sai do tren luoi (mm)
ELEC_GAP = 1.0      # mach dien tu: chua khe >= 1 mm (chieu cao linh kien uoc tinh)
D = {}              # doc, O (label -> obj), fc (Collider)


def setUpModule():
    D["doc"] = App.openDocument(FC)
    D["O"] = {o.Label: o for o in D["doc"].Objects if o.isDerivedFrom("Part::Feature") and not o.Shape.isNull()}


def tearDownModule():
    App.closeDocument(D["doc"].Name)


def O(label):
    return D["O"][label]


def collider(labels):
    key = tuple(sorted(labels))
    c = D.setdefault("col", {})
    if key not in c:
        c[key] = fast_collide.Collider({l: O(l) for l in labels})
    return c[key]


def gap(a, b, xa=5.0):
    return collider((a, b)).gap(a, b, xa)


def overlap(a, b):
    return collider((a, b)).volume(a, b) or 0.0


class T0File(unittest.TestCase):
    """2026-10-24: sua bang CLI lam mat GuiDocument.xml; chi tiet AN bi metrics/BOM/xuat STL bo qua am tham."""

    def test_gui_data_kept(self):
        import zipfile
        self.assertIn("GuiDocument.xml", zipfile.ZipFile(FC).namelist(), "mat du lieu hien thi (luu CLI?)")

    def test_no_hidden_parts(self):
        hidden = [o.Label for o in D["doc"].Objects if o.isDerivedFrom("Part::Feature") and not o.Shape.isNull()
                  and o.Shape.Solids and not o.Visibility
                  and not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
        self.assertEqual(hidden, [], "chi tiet an -> BOM/metrics/STL bo qua")


class T1Electronics(unittest.TestCase):
    """Tuan 2026-10-24: 'Model rx tx cua cyberbrick co shield, luc ve can chu y'."""

    def test_receiver_is_official_stack(self):
        self.assertIn("CB_XA003_XA004_receiver", D["O"], "dung STEP ghep XA003+XA004 cua hang (co shield)")
        for old in ("CB_XA004_receiver", "CB_XA003_core", "Socket_2x8"):
            self.assertNotIn(old, D["O"], "%s: model cu (tam phang, thieu chieu cao shield)" % old)
        bb = O("CB_XA003_XA004_receiver").Shape.BoundBox
        dims = sorted((bb.XLength, bb.YLength, bb.ZLength))
        for got, want in zip(dims, (22.6, 29.0, 30.0)):  # hop bao STEP hang (STL ghi 21,5)
            self.assertAlmostEqual(got, want, delta=0.6)

    def test_receiver_clearance(self):
        for other in ("Base_deck", "Turntable_gear_m1_z60", "CB_Servo9g_360_turntable", "Battery_bay"):
            g = gap("CB_XA003_XA004_receiver", other, 10.0)
            self.assertTrue(g is None or g >= ELEC_GAP - TOL, "%s: khe %.2f < %.1f mm" % (other, g or 0, ELEC_GAP))
        self.assertLess(overlap("CB_XA003_XA004_receiver", "Base_housing"), 0.5)


class T2Motor030(unittest.TestCase):
    """Tuan 2026-10-24: xi-lanh dung motor CyberBrick 030 + hop giam toc (khong phai N20), bo cuc B (motor chia ngang)."""

    def test_no_n20(self):
        self.assertFalse([l for l in D["O"] if "N20" in l])

    def test_gearbox_coaxial_with_worm(self):
        for t in TAGS:
            gb, w = O("CB_030_gearbox_" + t), O("Worm_" + t)
            ax_gb = gb.Placement.Rotation.multVec(App.Vector(0, 1, 0))           # truc ra = +Y cua STEP hang
            p_gb = gb.Placement.multVec(App.Vector(0, 15.2, 11.15))              # tam truc ra tai mat hop so
            r = O("Rack_" + t).Placement
            ax_w = r.Rotation.multVec(App.Vector(1, 0, 0))
            zs = -1 if t == "Shoulder" else 1
            p_w = r.multVec(App.Vector(60, 9.4, zs * 20.25))
            self.assertGreater(abs(ax_gb.dot(ax_w)), math.cos(math.radians(0.1)), t)
            off = (p_gb - p_w) - ax_w * (p_gb - p_w).dot(ax_w)
            self.assertLess(off.Length, 0.05, "%s lech truc %.3f mm" % (t, off.Length))

    def test_gearbox_fits_housing(self):
        for t in TAGS:
            self.assertLess(overlap("CB_030_gearbox_" + t, "Housing_" + t), 0.5, t)
            self.assertLess(overlap("CB_030_gearbox_" + t, "Worm_" + t), 0.5, t)

    def test_worm_socket_drives(self):
        """Lo truc vit phai co mat vat (truyen mo-men), khong duoc tron tron (2026-10-24 lan 2 do nham -> lo tron)."""
        for t in TAGS:
            r, zs = O("Rack_" + t).Placement, (-1 if t == "Shoulder" else 1)
            w = O("Worm_" + t).Shape
            inside = [k for k in range(0, 360, 5) if w.isInside(r.multVec(App.Vector(
                49.0, 9.4 + 2.5 * math.cos(math.radians(k)), zs * 20.25 + 2.5 * math.sin(math.radians(k)))), 1e-4, True)]
            self.assertTrue(0 < len(inside) < 72, "%s: %d/72 diem r 2,5 trong vat lieu" % (t, len(inside)))

    def test_worm_thrust_stop(self):
        """Datasheet LA024: luc doc truc (truc vit) hai motor -> vo phai chan dau truc vit, khe nho."""
        for t in TAGS:
            g = gap("Worm_" + t, "Housing_" + t, 2.0)
            self.assertIsNotNone(g, t)
            self.assertLessEqual(g, 0.5, t)


class T3Fits(unittest.TestCase):
    """Tuan 2026-10-24: 'Tang do rong khi gan co cau banh rang va truot' -> 0,3 mm."""

    PAIRS = [("Housing_{t}", "Rack_{t}"), ("Housing_{t}", "Pinion_WormWheel_{t}"),
             ("Housing_{t}", "Worm_{t}"), ("Worm_{t}", "CB_030_gearbox_{t}")]

    def test_slide_and_gear_fits(self):
        for t in TAGS:
            for a, b in self.PAIRS:
                a, b = a.format(t=t), b.format(t=t)
                g = gap(a, b)
                self.assertIsNotNone(g, "%s~%s xa hon 5 mm?" % (a, b))
                self.assertGreaterEqual(g, FIT_GAP - TOL, "%s~%s: %.3f mm" % (a, b, g))


class T4Marks(unittest.TestCase):
    """Tuan 2026-10-24: khac SO khop (cung so lap voi nhau): 2 = chot A, 5 = chot C (chi tiet in lai)."""

    def test_marks_engraved(self):
        for t, pins in (("Shoulder", "2"), ("Elbow", "5")):
            o = O("Housing_" + t)
            self.assertIn("STLab_Marks", o.PropertiesList, "Housing_%s chua khac dau" % t)
            self.assertIn(pins, o.STLab_Marks, t)


class T5Motion(unittest.TestCase):
    """Quet 24 tu the (yaw 0/90, 3 x 4 hanh trinh) - khong va cham, gom ca hop so moi."""

    def test_sweep(self):
        res = json.load(open(os.path.join(HERE, "..", "check", "kinematics-test.json"), encoding="utf-8"))
        self.assertEqual(res.get("unreachable"), [])
        bad = [(a["yaw"], a["L1"], a["L2"], a["hits"]) for a in res["arm"] if a["hits"]]
        self.assertEqual(bad, [])
        self.assertGreaterEqual(os.path.getmtime(os.path.join(HERE, "..", "check", "kinematics-test.json")),
                                os.path.getmtime(FC), "kinematics-test.json cu hon model -> chay lai kinematics_test.py")
