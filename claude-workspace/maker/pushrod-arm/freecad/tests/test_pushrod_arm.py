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
# PUSHROD_ARM_FCSTD: chay test tren ban sao (thu script sua truoc khi dung file that - 2026-10-26)
FC = os.environ.get("PUSHROD_ARM_FCSTD") or os.path.normpath(os.path.join(HERE, "..", "pushrod_arm.FCStd"))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "tools", "robotics-cad", "scripts")))
import fast_collide  # noqa: E402
import assembly_paths  # noqa: E402

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
    """Tuan 2026-10-24: xi-lanh dung motor CyberBrick 030 + hop giam toc (khong phai N20), motor chia ngang.
    2026-10-25: xi-lanh PISTON - truc ra hop so quay z28 -> z12 dau ty ren M3 (thay truc vit + thanh rang)."""

    def frame(self, t):
        return O("Piston_rod_" + t).Placement, (-1 if t == "Shoulder" else 1)

    def test_no_n20(self):
        self.assertFalse([l for l in D["O"] if "N20" in l])

    def test_gearbox_coaxial_with_z28(self):
        """Truc ra hop so nam dung tam lo z28: giua be rong banh rang, r 1,5 trong truc (mat vat 1,8), r 3,0 ngoai truc."""
        for t in TAGS:
            r, zs = self.frame(t)
            gb = O("CB_030_gearbox_" + t).Shape
            g = _local(O("Gear_z28_" + t).Shape, r).BoundBox
            xm = (g.XMin + g.XMax) / 2
            def ring(rad):
                return [gb.isInside(r.multVec(App.Vector(xm, rad * math.cos(math.radians(k)),
                                                         zs * 20.0 + rad * math.sin(math.radians(k)))), 1e-4, True)
                        for k in range(0, 360, 15)]
            self.assertTrue(all(ring(1.5)), "%s: truc ra khong o tam z28" % t)
            self.assertFalse(any(ring(3.0)), "%s: truc ra lech / phinh" % t)

    def test_gearbox_fits_housing(self):
        for t in TAGS:
            self.assertLess(overlap("CB_030_gearbox_" + t, "Housing_" + t), 0.5, t)
            self.assertLess(overlap("CB_030_gearbox_" + t, "Gear_z28_" + t), 0.5, t)

    def test_z28_socket_drives(self):
        """Lo z28 phai co mat vat (truyen mo-men), khong duoc tron (bai hoc Worm 2026-10-24)."""
        for t in TAGS:
            r, zs = self.frame(t)
            g = O("Gear_z28_" + t).Shape
            xm = (lambda b: (b.XMin + b.XMax) / 2)(_local(g, r).BoundBox)
            inside = [k for k in range(0, 360, 5) if g.isInside(r.multVec(App.Vector(
                xm, 2.5 * math.cos(math.radians(k)), zs * 20.0 + 2.5 * math.sin(math.radians(k)))), 1e-4, True)]
            self.assertTrue(0 < len(inside) < 72, "%s: %d/72 diem r 2,5 trong vat lieu" % (t, len(inside)))

    def test_screw_thrust_stop(self):
        """Ty ren chiu luc doc truc -> banh rang z12 ke 2 vach vo, khe nho (khong de hop so nhua chiu)."""
        for t in TAGS:
            g = gap("Gear_z12_" + t, "Housing_" + t, 2.0)
            self.assertIsNotNone(g, t)
            self.assertLessEqual(g, 0.5, t)


def _local(shape, pl):
    s = shape.copy(); s.transformShape(pl.inverse().toMatrix()); return s


class T3Fits(unittest.TestCase):
    """Tuan 2026-10-24: 'Tang do rong khi gan co cau banh rang va truot' -> 0,3 mm."""

    PAIRS = [("Housing_{t}", "Piston_rod_{t}"), ("Housing_{t}", "Gear_z28_{t}")]

    def test_slide_and_gear_fits(self):
        for t in TAGS:
            for a, b in self.PAIRS:
                a, b = a.format(t=t), b.format(t=t)
                g = gap(a, b)
                self.assertIsNotNone(g, "%s~%s xa hon 5 mm?" % (a, b))
                self.assertGreaterEqual(g, FIT_GAP - TOL, "%s~%s: %.3f mm" % (a, b, g))


class T8Piston(unittest.TestCase):
    """2026-10-25: Rack_Elbow lech khi len xuong -> xi-lanh piston kieu Cyberbrick Excavator. Hanh trinh du, ty ren
    luon an dai oc, ty rong chua du ty ren khi rut het."""

    L = {"Shoulder": (92.0, 99.7764836463904, 118.0), "Elbow": (92.0, 121.59676825402742, 128.0)}

    def test_stroke_and_screw(self):
        for t in TAGS:
            lmin, l0, lmax = self.L[t]
            r = O("Piston_rod_" + t).Placement
            sc = _local(O([l for l in D["O"] if l.startswith("LK_Threaded_rod_M3") and l.endswith(t)][0]).Shape, r).BoundBox
            nut = _local(O("LK_Nut_M3_piston_" + t).Shape, r).BoundBox
            rod = _local(O("Piston_rod_" + t).Shape, r).BoundBox
            self.assertLess(nut.XMax + (lmax - l0), sc.XMax - 1.0, "%s: duoi het, dai oc tuot ty ren" % t)
            self.assertGreater(rod.XMin + (lmin - l0), sc.XMin + 5.0, "%s: rut het, piston dam banh rang" % t)


class T9Assemble(unittest.TestCase):
    """Tuan 2026-10-26: Housing_Elbow + Piston_rod_Elbow in rieng KHONG lap vao nhau duoc (piston 6 x 10,4 > bac mieng ong
    6,6 x 8,6, dau kia kin) trong khi mo phong + va cham PASS: mo phong chi DAT san chi tiet vao cho. Moi cap dang cham
    phai co duong TINH TIEN tach rieng (tools/robotics-cad/scripts/assembly_paths.py); ngoai le ghi ly do o day."""

    ALLOW = {  # (mau_a, mau_b) fnmatch: ly do chong/ket CO CHU DICH
        ("*M2_5x*", "*"): "vit M2.5 tu ren vao lo moi (chong = ren an)",
        ("CB_Servo9g_180_gripper", "Servo_horn"): "tay servo ep len cot rang servo",
        ("CB_Servo9g_360_turntable", "Pinion_m1_z10_turntable"): "banh rang z10 ep len cot servo",
        ("Gear_z12_*", "LK_Nut_M3_gear_*"): "hoc dai oc nong hon dai oc 0,1 mm (dai oc nho 0,1 - chap nhan; "
                                            "TODO lan in z12 sau: hoc sau them 0,2)",
        ("Base_housing", "Battery_bay"): "pin PC003 nghieng luon duoi go giu 1,2 mm (xoay - cong cu chi thu tinh tien)",
        ("Base_housing", "Receiver_riser"): "ong nang nghieng duoi go 1,1 mm; ke tam, bo o v2",
        ("CB_030_gearbox_*", "Pin_gearbox_*"): "LOI DA BIET -> test_gearbox_pins (expectedFailure)",
    }

    @staticmethod
    def _objs():
        return {k: o for k, o in D["O"].items() if o.Shape.Solids and not k.startswith("_")}

    def test_all_parts_assemblable(self):
        res, pairs = assembly_paths.trapped(self._objs(), allow=list(self.ALLOW))
        self.assertGreater(len(pairs), 100, "it cap dang cham - model doi?")
        self.assertEqual(res, [], "cap KHONG lap duoc (ket/chong san):\n" + "\n".join("%s | %s %s" % r for r in res))

    def test_cylinder_insertion_path(self):
        """Ty truot vao tu mieng ong (+x he xi-lanh); dai oc piston truot vao ranh theo +y (mat tren khi in)."""
        for t in TAGS:
            objs = {k: O(k) for k in ("Housing_" + t, "Piston_rod_" + t, "LK_Nut_M3_piston_" + t)}
            col = fast_collide.Collider(objs)
            F = O("Piston_rod_" + t).Placement.Rotation
            for a, b, axis in (("Piston_rod_" + t, "Housing_" + t, (1, 0, 0)), ("LK_Nut_M3_piston_" + t, "Piston_rod_" + t, (0, 1, 0))):
                d = assembly_paths.free_direction(col, a, b, O(a))
                self.assertIsNotNone(d, "%s ket trong %s" % (a, b))
                want = F.multVec(App.Vector(*axis))
                self.assertAlmostEqual(abs(d[0] * want.x + d[1] * want.y + d[2] * want.z), 1.0, 3,
                                       "%s: thao theo %s, mong doi truc %s he xi-lanh" % (a, d, axis))

    @unittest.expectedFailure
    def test_gearbox_pins(self):
        """TODO (2026-10-26): Pin_gearbox dam vao hop so 030 ~52 mm3/chot. STEP hang: tai (+-9; -4,02) la kenh O4 BIT 2 dau
        (day vo 1 mm, nap 2,15 mm) -> can Tuan xem hop so THAT: mat nao co lo O4? Sua xong -> bo expectedFailure."""
        objs = {k: o for k, o in self._objs().items() if k.startswith(("CB_030_gearbox_", "Pin_gearbox_"))}
        res, _ = assembly_paths.trapped(objs)
        self.assertEqual(res, [])


class T4Marks(unittest.TestCase):
    """Tuan 2026-10-24: khac SO khop (cung so lap voi nhau): 2 = chot A, 5 = chot C (chi tiet in lai)."""

    def test_marks_engraved(self):
        for t, pins in (("Shoulder", "2"), ("Elbow", "5")):
            o = O("Housing_" + t)
            self.assertIn("STLab_Marks", o.PropertiesList, "Housing_%s chua khac dau" % t)
            self.assertIn(pins, o.STLab_Marks, t)


class T6PrintFile(unittest.TestCase):
    """Tuan 2026-10-24 toi: support tu ve lap kin lo truc Worm trong STL. Kiem FILE IN: lo truc z28 con trong;
    2026-10-25 them: long ong piston khong bi lap."""

    def test_gear_stl_socket_open(self):
        import Mesh
        for t in TAGS:
            p = os.path.join(HERE, "..", "..", "print", "stl", "05_PushRod_%s__Gear_z28_%s.stl" % (t, t))
            m = Mesh.Mesh(p)
            self.assertEqual(len(m.getSeparateComponents()), 1, "%s: co manh roi" % t)
            for z in (1.0, 2.5, 4.0):
                loops = m.crossSections([((0, 0, z), (0, 0, 1))])[0]
                self.assertEqual(len(loops), 2, "%s z %.1f: %d vong (can vanh + lo)" % (t, z, len(loops)))
            self.assertGreaterEqual(os.path.getmtime(p), os.path.getmtime(FC), "%s: STL cu hon model -> xuat lai" % t)

    def test_housing_stl_bore_open(self):
        import Mesh
        for t in TAGS:
            m = Mesh.Mesh(os.path.join(HERE, "..", "..", "print", "stl", "05_PushRod_%s__Housing_%s.stl" % (t, t)))
            self.assertEqual(len(m.getSeparateComponents()), 1, "%s: co manh roi / support" % t)


class T7Pins(unittest.TestCase):
    """Tuan 2026-10-25: chot (Pin_S...) "qua khit khong the nhet vo" Boom001/Turret; "lam rong nen yeu luc".
    Khop QUAY: khe >= 0,3 mm/ben voi MOI lo dong truc; chot dac (lo vit chi o dau, <= 6 mm); in NAM."""

    PINS = ["Pin_S", "Pin_A", "Pin_B", "Pin_C", "Pin_D", "Pin_E", "Pin_jaw2"]

    def _axis(self, s):
        import Part
        f = max((f for f in s.Faces if isinstance(f.Surface, Part.Cylinder)), key=lambda f: f.Area)
        return f.Surface.Axis, f.Surface.Center, f.Surface.Radius

    def test_rotating_clearance(self):
        import Part
        for n in self.PINS:
            s = O(n).Shape
            ax, c, r = self._axis(s)
            holes = []
            for q in D["O"].values():
                if q.Label.startswith(("Pin_", "M2_5")) or not q.Shape.BoundBox.intersect(s.BoundBox):
                    continue
                for f in q.Shape.Faces:
                    su = f.Surface
                    if (isinstance(su, Part.Cylinder) and abs(abs(su.Axis.dot(ax)) - 1) < 1e-3
                            and (su.Center - c).cross(ax).Length < 0.05 and r < su.Radius < r + 1.0):
                        holes.append((q.Label, su.Radius - r))
            self.assertTrue(holes, "%s: khong thay lo nao" % n)
            tight = [(lb, round(g, 3)) for lb, g in holes if g < 0.3 - TOL]
            self.assertEqual(tight, [], "%s: khe < 0,3 mm/ben" % n)

    def test_solid_pin(self):
        for n in self.PINS:
            s = O(n).Shape
            ax, c, r = self._axis(s)
            ts = [v.Point.sub(c).dot(ax) for v in s.Vertexes]
            t0, t1 = min(ts), max(ts)
            hollow = []
            for k in range(1, 20):  # mat cat doc than: chi 1 vong (dac), tru doan lo vit o dau (<= 6 mm)
                t = t0 + (t1 - t0) * k / 20
                if min(t - t0, t1 - t) <= 6.0:
                    continue
                if len(s.slice(ax, (c + ax * t).dot(ax))) != 1:
                    hollow.append(round(t - t0, 1))
            self.assertEqual(hollow, [], "%s: than rong tai (mm)" % n)

    def test_pins_print_lying(self):
        import Mesh
        for n in self.PINS:
            m = Mesh.Mesh(os.path.join(HERE, "..", "..", "print", "stl", "07_Pins__%s.stl" % n))
            bb = m.BoundBox
            self.assertLess(bb.ZLength, max(bb.XLength, bb.YLength), "%s: in DUNG (gay ngang lop)" % n)


class T5Motion(unittest.TestCase):
    """Quet 24 tu the (yaw 0/90, 3 x 4 hanh trinh) - khong va cham, gom ca hop so moi."""

    def test_sweep(self):
        res = json.load(open(os.path.join(HERE, "..", "check", "kinematics-test.json"), encoding="utf-8"))
        self.assertEqual(res.get("unreachable"), [])
        bad = [(a["yaw"], a["L1"], a["L2"], a["hits"]) for a in res["arm"] if a["hits"]]
        self.assertEqual(bad, [])
        self.assertGreaterEqual(os.path.getmtime(os.path.join(HERE, "..", "check", "kinematics-test.json")),
                                os.path.getmtime(FC), "kinematics-test.json cu hon model -> chay lai kinematics_test.py")
