# Gate cong cu render Blender STLab (Claude viet 2026-11-02, executor KHONG sua). Chay tu claude-workspace:
#   python -m unittest tools/render/tests/test_render.py -v
# Dung model that maker/line-bot/freecad/line_bot.FCStd (chi doc) + cmf mau trong thu muc tam.
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageStat

WS = Path(__file__).resolve().parents[3]
RENDER = WS / "tools" / "render" / "render.py"
FC = WS / "maker" / "line-bot" / "freecad" / "line_bot.FCStd"
LABELS_IN = {"Base_plate", "Top_plate", "Motor_mount_L", "Motor_mount_R", "Caster_mount", "Line_bracket", "Sonar_bracket"}


class TRender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="render-test-", dir=os.environ.get("TMP")))
        cls.cmf = cls.tmp / "cmf.json"
        cls.cmf.write_text(json.dumps({
            "rules": [{"names": ["Base_plate", "Top_plate"], "color": "#1E5A45", "finish": "matte"},
                      {"names": ["Ref_*"], "color": "#2A2E33", "finish": "satin"}],
            "default": {"color": "#E8B33A", "finish": "satin"},
            "background": "#ECF1EF"}), encoding="utf-8")
        cls.out = cls.tmp / "out"
        cmd = [sys.executable, str(RENDER), str(FC), "--cmf", str(cls.cmf), "--out", str(cls.out),
               "--views", "iso,front", "--samples", "8", "--size", "800x600", "--name", "t"]
        cls.r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        cls.log = (cls.r.stdout or "")[-2000:] + (cls.r.stderr or "")[-2000:]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_01_exit_ok(self):
        self.assertEqual(self.r.returncode, 0, self.log)
        self.assertIn("RENDER OK", self.r.stdout, self.log)

    def test_02_anh_ra_dung_kich_thuoc(self):
        for v in ("iso", "front"):
            p = self.out / f"t-{v}.png"
            self.assertTrue(p.exists(), f"thieu {p.name}\n{self.log}")
            self.assertEqual(Image.open(p).size, (800, 600))

    def test_03_co_vat_the_khong_trang_tron(self):
        for v in ("iso", "front"):
            im = Image.open(self.out / f"t-{v}.png").convert("RGB")
            st = ImageStat.Stat(im)
            self.assertGreater(max(st.stddev), 12.0, f"{v}: anh gan nhu mot mau")
            w, h = im.size
            corner = im.getpixel((5, 5))
            bg = (0xEC, 0xF1, 0xEF)
            self.assertLess(sum(abs(a - b) for a, b in zip(corner, bg)), 60, f"{v}: goc anh khong phai nen {corner}")
            center = im.crop((w // 3, h // 3, 2 * w // 3, 2 * h // 3))
            diff = sum(1 for px in center.getdata() if sum(abs(a - b) for a, b in zip(px, bg)) > 60)
            self.assertGreater(diff / (center.width * center.height), 0.15, f"{v}: vat the khong o giua khung")

    def test_04_scene_json_ap_cmf(self):
        sc = json.loads((self.out / "t-scene.json").read_text(encoding="utf-8"))
        obj = {o["label"]: o for o in sc["objects"]}
        self.assertTrue(LABELS_IN <= set(obj), f"thieu object: {LABELS_IN - set(obj)}")
        self.assertEqual(obj["Base_plate"]["color"].upper(), "#1E5A45")
        self.assertEqual(obj["Ref_Mega"]["color"].upper(), "#2A2E33")
        self.assertEqual(obj["Caster_mount"]["color"].upper(), "#E8B33A")
        for o in sc["objects"]:
            self.assertTrue(Path(o["stl"]).exists(), o["stl"])


    def test_05_thay_mau_chi_tiet(self):
        # Claude them 2026-11-02: ban dau gate PASS nhung anh chi la 1 khoi trang (sai ti le phong/camera).
        # View iso phai thay ro tam xanh thong #1E5A45 (Base/Top_plate) va vang #E8B33A (default) - do theo kenh mau troi.
        im = Image.open(self.out / "t-iso.png").convert("RGB")
        px = list(im.getdata())
        xanh = sum(1 for r, g, b in px if g > r + 15 and g > b + 5) / len(px)
        vang = sum(1 for r, g, b in px if r > b + 60 and g > b + 30) / len(px)
        self.assertGreater(xanh, 0.03, f"iso: khong thay mau xanh tam ({xanh:.3f})")
        self.assertGreater(vang, 0.003, f"iso: khong thay mau vang chi tiet ({vang:.4f})")
        # vat the chiem 15-85 % khung (khong qua sat, khong qua nho)
        bg = (0xEC, 0xF1, 0xEF)
        obj = sum(1 for q in px if sum(abs(a - b) for a, b in zip(q, bg)) > 45) / len(px)
        self.assertTrue(0.15 < obj < 0.85, f"iso: vat the chiem {obj:.2f} khung")


    def test_06_vien_anh_la_nen(self):
        # Claude them 2026-11-02 (de xuat #1): 4 canh anh phai la nen suong - khong lot dai den/mep phong
        bg = (0xEC, 0xF1, 0xEF)
        for v in ("iso", "front"):
            im = Image.open(self.out / f"t-{v}.png").convert("RGB")
            w, h = im.size
            pts = [(x, 2) for x in range(0, w, 8)] + [(x, h - 3) for x in range(0, w, 8)] +                   [(2, y) for y in range(0, h, 8)] + [(w - 3, y) for y in range(0, h, 8)]
            bad = sum(1 for p in pts if sum(abs(a - b) for a, b in zip(im.getpixel(p), bg)) > 60)
            self.assertLess(bad / len(pts), 0.03, f"{v}: {bad}/{len(pts)} diem vien khong phai nen (dai den?)")

    def test_07_duong_dan_tuong_doi(self):
        # de xuat #1: --out/--cmf tuong doi phai tinh theo cwd cua lenh, khong ghi ra C:\
        cmd = [sys.executable, str(RENDER), str(FC), "--cmf", "cmf.json", "--out", "rel_out",
               "--views", "iso", "--samples", "4", "--size", "320x240", "--name", "r"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, cwd=str(self.tmp))
        self.assertEqual(r.returncode, 0, (r.stdout or "")[-1500:] + (r.stderr or "")[-1500:])
        self.assertTrue((self.tmp / "rel_out" / "r-iso.png").exists(), "anh khong nam trong rel_out/ cua cwd")

    def test_08_smooth_theo_goc(self):
        # de xuat #2: khong lam min moi polygon (mat phang bi loang) - dung Smooth by Angle (Blender 4.1+)
        src = (RENDER.parent / "blender_scene.py").read_text(encoding="utf-8")
        self.assertIn("smooth_by_angle", src.lower().replace(" ", "_"), "chua dung Smooth by Angle")
        self.assertNotRegex(src, r"for\s+\w+\s+in\s+\w+\.data\.polygons\s*:\s*\w+\.use_smooth\s*=\s*True",
                            "van bat use_smooth cho moi polygon")


if __name__ == "__main__":
    unittest.main()
