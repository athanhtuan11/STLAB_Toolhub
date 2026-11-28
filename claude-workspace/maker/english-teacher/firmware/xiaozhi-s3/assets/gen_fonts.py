"""Sinh phông Andika Bold (OFL) -> file C LVGL 9 cho bo stlab-s3 (boards/stlab-s3/andika_bold_<cỡ>.c). Cần node/npx.
Chạy: python gen_fonts.py   (chỉ khi đổi cỡ/ký tự; file C đã commit trong boards/stlab-s3).
Tên biến phông = tên file xuất (lv_font_conv 1.5.2 không có --lv-font-name)."""
import subprocess, sys
from pathlib import Path

A = Path(__file__).resolve().parent
OUT = A.parent / "boards" / "stlab-s3"
TTF = A / "fonts" / "Andika-Bold.ttf"
SETS = [(52, " -'"), (34, " -'"), (120, "")]   # a-z + khoảng trắng, '-' , "'" ; cỡ 120 chỉ a-z
for size, syms in SETS:
    out = OUT / ("andika_bold_%d.c" % size)
    cmd = ["npx", "-y", "lv_font_conv@1.5.2", "--font", str(TTF), "--size", str(size), "--bpp", "4", "--no-compress",
           "--format", "lvgl", "--range", "0x61-0x7A", "--lv-include", "lvgl.h", "-o", str(out)]
    if syms:
        cmd += ["--symbols", syms]
    if subprocess.run(cmd, shell=(sys.platform == "win32")).returncode != 0:
        sys.exit("lv_font_conv loi cỡ %d" % size)
print("gen_fonts OK")
