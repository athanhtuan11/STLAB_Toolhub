# Gate cong cu kiem lap rap (Claude viet 2026-11-27, executor KHONG sua file nay).
# Chay: python -X utf8 -m unittest discover -s tests -v   (cwd = tools/assembly-check)
# Can Blender 5.2 (bien moi truong BLENDER hoac duong dan mac dinh).
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "assembly_check.py"
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
OWL_ASM = HERE.parents[2] / "maker" / "english-teacher" / "cad" / "out-s3-screen" / "asm"


# ---------- STL hop thuan Python (nhieu hop trong 1 file = 1 part)
def box_tris(lo, hi):
    x0, y0, z0 = lo; x1, y1, z1 = hi
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return [(v[a], v[b], v[c]) for a, b, c in f]


def write_stl(path, boxes):
    lines = ["solid p"]
    for lo, hi in boxes:
        for t in box_tris(lo, hi):
            lines.append(" facet normal 0 0 0\n  outer loop")
            lines += [f"   vertex {p[0]} {p[1]} {p[2]}" for p in t]
            lines.append("  endloop\n endfacet")
    lines.append("endsolid p")
    Path(path).write_text("\n".join(lines), encoding="ascii")


# Hop de mo nap: san 40x40x2 + 4 vach cao toi z 20 (vach day 2, cham san, khong chong).
BASE = [((0, 0, 0), (40, 40, 2)), ((0, 0, 2), (2, 40, 20)), ((38, 0, 2), (40, 40, 20)),
        ((2, 0, 2), (38, 2, 20)), ((2, 38, 2), (38, 40, 20))]
CUBE_OK = [((2.3, 2.3, 2.0), (37.7, 37.7, 12.0))]      # ngoi tren san (cham), cach vach 0,3
CUBE_PEN = [((1.5, 2.3, 2.0), (37.7, 37.7, 12.0))]     # chong vach trai 0,5 mm
BAR = [((-5, 15, 25), (45, 25, 30))]                    # thanh ngang tren mieng hop (cao hon vach 5 mm)


def run(cfg_dir, cfg, extra=()):
    p = Path(cfg_dir) / "assembly.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(TOOL), "--", str(p), *extra],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    rep_p = Path(cfg_dir) / "assembly-report.json"
    rep = json.loads(rep_p.read_text(encoding="utf-8")) if rep_p.exists() else None
    return r, rep


def kinds(rep, level):
    return [(i["check"], tuple(i.get("parts", []))) for i in rep["issues"] if i["level"] == level]


def has(rep, level, check, *parts):
    for i in rep["issues"]:
        if i["level"] == level and i["check"] == check and all(p in i.get("parts", []) for p in parts):
            return True
    return False


def base_cfg(**over):
    cfg = {
        "asm_dir": "asm",
        "tol": {"penetration": 0.2, "path_step": 0.5, "seat_stop": 0.5, "probe": 2.0},
        "order": ["base", "cube"],
        "parts": {
            "base": {"fixed": True},
            "cube": {"insert": {"dir": [0, 0, -1], "from": 40}},
        },
        "allowed_contacts": [["base", "cube"]],
        "joints": [{"type": "snap", "parts": ["cube", "base"], "blocks": ["+z"], "note": "3 lay gai"}],
    }
    cfg.update(over)
    return cfg


@unittest.skipUnless(Path(BLENDER).exists(), "khong co Blender")
class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="asmchk-")
        (Path(self.d) / "asm").mkdir()
        write_stl(Path(self.d) / "asm" / "base.stl", BASE)

    def put(self, name, boxes):
        write_stl(Path(self.d) / "asm" / f"{name}.stl", boxes)

    def test_00_static_no_stub(self):
        src = TOOL.read_text(encoding="utf-8")
        for need in ("BVHTree", "def check_pairs", "def check_paths", "def check_retention", "def check_config", "assembly-report.json"):
            self.assertIn(need, src, f"assembly_check.py thieu {need}")
        self.assertGreater(len([l for l in src.splitlines() if l.strip() and not l.strip().startswith("#")]), 120, "ma qua ngan (ma gia?)")
        self.assertNotIn("NotImplementedError", src)

    def test_01_ok_pass(self):
        self.put("cube", CUBE_OK)
        r, rep = run(self.d, base_cfg())
        self.assertIsNotNone(rep, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertEqual(rep["verdict"], "PASS", json.dumps(rep["issues"], ensure_ascii=False))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(rep["parts"], ["base", "cube"])

    def test_02_penetration_fail(self):
        self.put("cube", CUBE_PEN)
        r, rep = run(self.d, base_cfg())
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(has(rep, "FAIL", "pair", "base", "cube"), kinds(rep, "FAIL"))
        pen = [i for i in rep["issues"] if i["check"] == "pair" and i["level"] == "FAIL"][0]
        self.assertIn("where", pen)   # vi tri (tam vung chong) de nguoi sua tim

    def test_03_contact_not_allowed_is_warn(self):
        self.put("cube", CUBE_OK)
        r, rep = run(self.d, base_cfg(allowed_contacts=[]))
        self.assertEqual(rep["verdict"], "PASS", kinds(rep, "FAIL"))
        self.assertTrue(has(rep, "WARN", "contact", "base", "cube"), kinds(rep, "WARN"))

    def test_04_retention_free_dir_fail(self):
        self.put("cube", CUBE_OK)
        r, rep = run(self.d, base_cfg(joints=[]))
        self.assertEqual(rep["verdict"], "FAIL")
        fr = [i for i in rep["issues"] if i["check"] == "retention" and i["level"] == "FAIL"]
        self.assertTrue(fr, kinds(rep, "FAIL"))
        self.assertIn("cube", fr[0]["parts"])
        self.assertEqual(sorted(fr[0]["free_dirs"]), ["+z"])   # san chan -z, vach chan +-x +-y (probe 2 > khe 0,3)

    def test_05_path_blocked_fail(self):
        self.put("cube", CUBE_OK); self.put("bar", BAR)
        cfg = base_cfg(order=["base", "bar", "cube"])
        cfg["parts"]["bar"] = {"insert": {"dir": [0, 0, -1], "from": 30}}
        cfg["joints"].append({"type": "screw", "parts": ["bar", "base"], "blocks": ["*"], "note": "2 vit M3"})
        r, rep = run(self.d, cfg)
        self.assertEqual(rep["verdict"], "FAIL")
        bl = [i for i in rep["issues"] if i["check"] == "path" and i["level"] == "FAIL"]
        self.assertTrue(bl, kinds(rep, "FAIL"))
        self.assertIn("cube", bl[0]["parts"]); self.assertIn("bar", bl[0]["parts"])
        self.assertIn("at", bl[0])   # quang duong con lai (mm) luc vuong

    def test_06_path_ok_when_order_fixed(self):
        self.put("cube", CUBE_OK); self.put("bar", BAR)
        cfg = base_cfg(order=["base", "cube", "bar"])
        cfg["parts"]["bar"] = {"insert": {"dir": [0, 0, -1], "from": 30}}
        cfg["joints"].append({"type": "screw", "parts": ["bar", "base"], "blocks": ["*"], "note": "2 vit M3"})
        r, rep = run(self.d, cfg)
        self.assertFalse([i for i in rep["issues"] if i["check"] == "path"], rep["issues"])

    def test_07_moves_polyline(self):
        # duong lap 2 doan: vao ngang roi ha xuong -> van PASS
        self.put("cube", CUBE_OK)
        cfg = base_cfg()
        cfg["parts"]["cube"] = {"insert": {"moves": [[30, 0, 0], [0, 0, -40]]}}
        r, rep = run(self.d, cfg)
        self.assertEqual(rep["verdict"], "PASS", rep["issues"])

    def test_08_config_errors(self):
        self.put("cube", CUBE_OK); self.put("extra", [((100, 100, 0), (110, 110, 10))])
        cfg = base_cfg()
        cfg["joints"].append({"type": "pin", "parts": ["cube", "base"], "blocks": ["+y"], "note": "chot", "pin_part": "pin-2mm"})
        cfg["joints"].append({"type": "magic", "parts": ["cube", "base"], "blocks": ["+x"], "note": "?"})
        r, rep = run(self.d, cfg)
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertTrue(has(rep, "FAIL", "config", "extra"), kinds(rep, "FAIL"))      # STL khong khai bao
        self.assertTrue(any(i["check"] == "config" and "pin-2mm" in i["msg"] for i in rep["issues"]), rep["issues"])  # chot khong ve
        self.assertTrue(any(i["check"] == "config" and "magic" in i["msg"] for i in rep["issues"]), rep["issues"])

    def test_09_glue_is_warn(self):
        self.put("cube", CUBE_OK)
        r, rep = run(self.d, base_cfg(joints=[{"type": "glue", "parts": ["cube", "base"], "blocks": ["+z"], "note": "keo nong"}]))
        self.assertEqual(rep["verdict"], "PASS", kinds(rep, "FAIL"))
        self.assertTrue(has(rep, "WARN", "joint", "cube"), kinds(rep, "WARN"))

    def test_10_auto_mode(self):
        self.put("cube", CUBE_PEN)
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(TOOL), "--", "--auto", str(Path(self.d) / "asm"),
                            "--report", str(Path(self.d) / "auto.json")], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        rep = json.loads((Path(self.d) / "auto.json").read_text(encoding="utf-8"))
        self.assertEqual(rep["verdict"], "FAIL")
        self.assertTrue(has(rep, "FAIL", "pair", "base", "cube"))

    def test_11_flex_needs_snap(self):
        self.put("cube", CUBE_OK)
        cfg = base_cfg()
        cfg["parts"]["cube"]["insert"]["flex"] = 0.5
        cfg["joints"] = [{"type": "screw", "parts": ["cube", "base"], "blocks": ["*"], "note": "vit"}]
        r, rep = run(self.d, cfg)
        self.assertTrue(has(rep, "FAIL", "config", "cube"), kinds(rep, "FAIL"))   # flex khong co joint snap -> FAIL
        cfg["joints"] = [{"type": "snap", "parts": ["cube", "base"], "blocks": ["*"], "note": "lay gai"}]
        r, rep = run(self.d, cfg)
        self.assertEqual(rep["verdict"], "PASS", kinds(rep, "FAIL"))
        cfg["parts"]["cube"]["insert"]["flex"] = 2.0
        r, rep = run(self.d, cfg)
        self.assertTrue(has(rep, "FAIL", "config", "cube"), kinds(rep, "FAIL"))   # flex > 1,0 -> FAIL

    @unittest.skipUnless(OWL_ASM.exists(), "khong co asm Cu Bong")
    def test_20_owl_regression(self):
        # Loi that 2026-11-27: bung + mo chong vo truoc; 2 nua vo, vanh loa chi CHAM (khong duoc bao chong).
        out = Path(self.d) / "owl.json"
        r = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(TOOL), "--", "--auto", str(OWL_ASM),
                            "--report", str(out)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        rep = json.loads(out.read_text(encoding="utf-8"))
        self.assertTrue(has(rep, "FAIL", "pair", "belly", "shell-front"), kinds(rep, "FAIL"))
        self.assertTrue(has(rep, "FAIL", "pair", "beak", "shell-front"), kinds(rep, "FAIL"))
        self.assertFalse(has(rep, "FAIL", "pair", "shell-back", "shell-front"))
        self.assertFalse(has(rep, "FAIL", "pair", "speaker-bezel-L", "shell-front"))
        self.assertFalse(has(rep, "FAIL", "pair", "speaker-bezel-L", "speaker-ring-L"))


if __name__ == "__main__":
    unittest.main()
