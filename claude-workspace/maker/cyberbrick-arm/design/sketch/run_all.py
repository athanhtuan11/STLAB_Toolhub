# Chay cac phuong an roi ghep nen suong. python run_all.py [samples] [ABC]
import subprocess, sys
from pathlib import Path
from PIL import Image
H = Path(__file__).resolve().parent; O = H.parent / "concepts"
B = r"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
N = sys.argv[1] if len(sys.argv) > 1 else "64"
vs = sys.argv[2] if len(sys.argv) > 2 else "ABC"
for v in vs:
    subprocess.run([B, "-b", "--factory-startup", "-P", str(H / "sketch_forms.py"), "--", v, str(O), N], capture_output=True)
    for p in O.glob("raw-%s-*.png" % v):
        im = Image.open(p).convert("RGBA"); bg = Image.new("RGBA", im.size, "#ECF1EF"); bg.alpha_composite(im)
        bg.convert("RGB").save(str(p).replace("raw-", "form-")); p.unlink()
