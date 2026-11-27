# run_v3.py - 1 lenh ve + kiem Cu Bong v3 (Tuan 2026-11-27: "ve va kiem qua lau"). In bang thoi gian + ket qua <= 15 dong.
#   python run_v3.py            ve -> (song song) assembly-check + kiem in nhanh (printability) + mau thu + file CAD -> gate
#   python run_v3.py --slice    ... + cat lop that (chi khi kiem in nhanh sach), roi gate
#   python run_v3.py --no-build chi kiem lai (khong ve)
# Tang 1 (vai giay): printability tren STL -> bat tran/treo truoc; tang 2 (~30-50 s): slice.py chi chay khi tang 1 sach va co --slice.
import subprocess, sys, time, shutil, hashlib, json, concurrent.futures as cf
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent
WS = PROJ.parents[1]
BL = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
PRINT_STL = ["shell-front", "shell-back", "seam-spline", "belly", "beak", "button-cap", "face-plate", "speaker-bezel-L", "speaker-bezel-R",
             "speaker-ring-L", "speaker-ring-R", "mic-clamp", "s3-tray", "button-base", "base"]
T = []


def run(name, cmd, cwd=HERE):
    t0 = time.time()
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    dt = time.time() - t0
    T.append((name, dt, r.returncode))
    return r


def blender(name, script, *args):
    return run(name, [BL, "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(script), "--", *args])


def h(p):
    return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else ""


def printability():
    t0 = time.time()
    sys.path.insert(0, str(WS / "tools" / "print" / "scripts"))
    import printability as P
    bad = []
    for n in PRINT_STL:
        tri = P.doc_stl(str(PROJ / "print" / "stl-v3" / f"{n}.stl"))
        cum, _, _ = P.vung_can_do(tri, dict(P.MAC_DINH))
        if cum:
            bad.append(f"{n}: {cum[0]['mm2']} mm2 rong {cum[0]['rong_mm']} z {cum[0]['z_mm']}")
    T.append(("kiem in nhanh", time.time() - t0, 1 if bad else 0))
    return bad


def main():
    a = sys.argv[1:]
    out = []
    if "--no-build" not in a:
        r = blender("ve (build_owl_v3)", HERE / "build_owl_v3.py", "out-v3")
        if r.returncode:
            print("VE LOI:\n" + "\n".join((r.stdout + r.stderr).splitlines()[-12:])); sys.exit(1)
    changed = []
    for n in PRINT_STL:
        src, dst = HERE / "out-v3" / f"{n}.stl", PROJ / "print" / "stl-v3" / f"{n}.stl"
        if h(src) != h(dst):
            shutil.copy2(src, dst); changed.append(n)
    with cf.ThreadPoolExecutor(4) as ex:
        # file CAD mo-ra-do (Tuan 2026-11-27): .sc + .step + .blend tu out-v3/asm, chay song song voi kiem
        f_cad = ex.submit(run, "file CAD (sc/step/blend)", [sys.executable, str(WS / "tools" / "cad-export" / "export_cad.py"),
                                                            str(HERE / "out-v3" / "asm"), "owl-assembly"])
        f_asm = ex.submit(blender, "assembly-check", WS / "tools" / "assembly-check" / "assembly_check.py", str(HERE / "assembly.json"))
        f_cp = ex.submit(blender, "mau thu (coupons)", HERE / "make_v3_coupons.py")
        bad = printability()
        r_asm, r_cp, r_cad = f_asm.result(), f_cp.result(), f_cad.result()
    for f in ("belly.stl", "beak.stl"):
        shutil.copy2(HERE / "out-v3" / f, PROJ / "print" / "stl-v3-test" / f)
    asm_line = [l for l in r_asm.stdout.splitlines() if l.startswith("ASSEMBLY")] or ["ASSEMBLY ?"]
    out.append(asm_line[0] + "".join("\n  " + l for l in r_asm.stdout.splitlines() if l.startswith("ASM FAIL"))[:600])
    out.append("file CAD: " + ("out-v3/owl-assembly.sc|.step|.blend" if r_cad.returncode == 0 else "LOI " + r_cad.stdout[-400:]))
    out.append("kiem in nhanh: " + ("SACH" if not bad else "CAN SUA\n  " + "\n  ".join(bad)))
    if "--slice" in a:
        if bad or r_asm.returncode:
            out.append("cat lop: BO QUA (sua loi tang 1 truoc)")
        else:
            r = run("cat lop (slice.py)", [sys.executable, str(WS / "tools/print/scripts/memjob.py"), "3", "--", sys.executable,
                                           str(WS / "tools/print/scripts/slice.py"), "print/print-v3.yaml"], cwd=PROJ)
            out.append("cat lop: " + ([l for l in r.stdout.splitlines() if "KET LUAN" in l] or ["?"])[0].strip())
    r_g = blender("gate_owl_v3", HERE / "gate_owl_v3.py", "out-v3")
    gl = [l for l in r_g.stdout.splitlines() if l.startswith(("V3 lat", "PASS gate", "FAIL gate", " - "))]
    out += gl[:6]
    print("STL doi:", ", ".join(changed) or "khong")
    print("\n".join(out))
    print("thoi gian: " + ", ".join(f"{n} {dt:.0f}s" for n, dt, _ in T) + f" | tong {sum(dt for _, dt, _ in T):.0f}s (song song thuc te it hon)")


if __name__ == "__main__":
    main()
