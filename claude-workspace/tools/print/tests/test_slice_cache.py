"""test_slice_cache.py - cache cat lop theo ban (slice.py, 2026-11-28).
2 ban nho trong thu muc tam: chay 2 lan -> lan 2 ca 2 ban CACHE + nhanh; doi thu tu tam giac 1 STL (cung hinh) -> van CACHE;
doi hinh 1 STL (dich 0,5 mm... thuc chat keo dan) -> chi ban do cat lai. Chay: python test_slice_cache.py
"""
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLICE = HERE.parent / "scripts" / "slice.py"
SRC = HERE.parents[2] / "maker" / "english-teacher" / "print" / "stl-v3"
fails = []


def box_stl(path, sx, sy, sz):
    v = [(0, 0, 0), (sx, 0, 0), (sx, sy, 0), (0, sy, 0), (0, 0, sz), (sx, 0, sz), (sx, sy, sz), (0, sy, sz)]
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    with open(path, "wb") as fh:
        fh.write(b"\0" * 80 + struct.pack("<I", len(f)))
        for t in f:
            fh.write(struct.pack("<3f", 0, 0, 0))
            for i in t:
                fh.write(struct.pack("<3f", *v[i]))
            fh.write(b"\0\0")


def run(yml):
    t0 = time.time()
    r = subprocess.run([sys.executable, str(SLICE), str(yml)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r, time.time() - t0


with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    (td / "stl").mkdir()
    box_stl(td / "stl" / "a.stl", 20, 20, 5)
    box_stl(td / "stl" / "b.stl", 15, 30, 4)
    yml = td / "print.yaml"
    yml.write_text("""machine: Bambu Lab A1 0.4 nozzle
filament: Bambu PETG Basic @BBL A1
stl: stl
plates_dir: plates
common: {curr_bed_type: Textured PEI Plate}
plates:
  pa: {process: 0.20mm Standard @BBL A1, color: "#F6BE9A", stl: ["a.stl"]}
  pb: {process: 0.20mm Standard @BBL A1, color: "#F6BE9A", stl: ["b.stl"]}
""", encoding="utf-8")
    r1, t1 = run(yml)
    if "KET LUAN: PASS" not in r1.stdout:
        fails.append("lan 1 khong PASS: " + r1.stdout[-500:] + r1.stderr[-300:])
    r2, t2 = run(yml)
    if r2.stdout.count("CACHE (STL") != 2:
        fails.append(f"lan 2 khong CACHE ca 2 ban ({r2.stdout.count('CACHE')})")
    if "KET LUAN: PASS" not in r2.stdout:
        fails.append("lan 2 khong PASS")
    if "Project gop: CACHE" not in r2.stdout:
        fails.append("lan 2: buoc gop project khong CACHE")
    # doi thu tu tam giac (cung hinh) -> van CACHE
    b = (td / "stl" / "a.stl").read_bytes(); n = struct.unpack("<I", b[80:84])[0]
    recs = [b[84 + 50 * i: 84 + 50 * (i + 1)] for i in range(n)]
    (td / "stl" / "a.stl").write_bytes(b[:84] + b"".join(reversed(recs)))
    r3, t3 = run(yml)
    if r3.stdout.count("CACHE (STL") != 2:
        fails.append(f"doi thu tu tam giac (cung hinh) ma khong CACHE ({r3.stdout.count('CACHE')})")
    # doi hinh b -> chi pb cat lai
    box_stl(td / "stl" / "b.stl", 15, 31, 4)
    r4, t4 = run(yml)
    if "pa: CACHE" not in r4.stdout or "pb: CACHE" in r4.stdout:
        fails.append("doi b.stl: mong pa CACHE, pb cat lai; stdout: " + " | ".join(l for l in r4.stdout.splitlines() if "CACHE" in l))
    if "KET LUAN: PASS" not in r4.stdout:
        fails.append("lan 4 khong PASS")
    if "Project gop: CACHE" in r4.stdout:
        fails.append("doi 1 ban ma buoc gop van CACHE (file gop cu sai)")
    print(f"thoi gian: lan 1 {t1:.1f} s, lan 2 (cache) {t2:.1f} s, doi thu tu {t3:.1f} s, doi 1 ban {t4:.1f} s")

for f_ in fails:
    print("FAIL", f_)
print("PASS test_slice_cache" if not fails else f"FAIL test_slice_cache ({len(fails)} loi)")
sys.exit(1 if fails else 0)
