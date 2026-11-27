# run_v3.py - 1 lenh ve + kiem Cu Bong v3 (Tuan 2026-11-27: "ve va kiem qua lau"). In bang thoi gian + ket qua <= 15 dong.
#   python run_v3.py            ve -> (song song) assembly-check + kiem in nhanh (printability) + mau thu + file CAD -> gate
#   python run_v3.py --slice    ... + cat lop that (chi khi kiem in nhanh sach), roi gate
#   python run_v3.py --no-build chi kiem lai (khong ve)
#   python run_v3.py --release  ... + file CAD phat hanh .sc/.step/.blend (mac dinh: 3MF nhanh; Tuan duyet 2026-11-27)
# Tang 1 (vai giay): printability tren STL -> bat tran/treo truoc; tang 2 (~30-50 s): slice.py chi chay khi tang 1 sach va co --slice.
import subprocess, sys, time, shutil, hashlib, json, concurrent.futures as cf
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent
WS = PROJ.parents[1]
BL = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
PRINT_STL = ["shell-front", "shell-back", "seam-spline", "belly", "beak", "button-cap", "face-plate", "speaker-bezel-L", "speaker-bezel-R",
             "speaker-ring-L", "speaker-ring-R", "mic-clamp", "s3-tray", "button-base", "base", "belly-clamp"]
T = []
sys.path.insert(0, str(WS / "tools" / "metrics"))
from runlog import RunLog  # noqa: E402  (2026-11-27 do luong moi lan chay -> cad/metrics/runs.jsonl, Tuan duyet)
RL = None


def _cache_cad(out):
    return None if "CAD EXPORT nhanh" in out else ("hit" if "CACHE" in out else "miss")


def _cache_slice(out):
    n = out.count("CACHE (STL"); tot = sum(1 for l in out.splitlines() if l.strip().startswith(("A_", "B_", "C_", "D_", "E_")) and ":" in l)
    return "hit" if n and "Project gop: CACHE" in out else ("partial" if n else "miss")


def _detail_slice(out):
    import glob
    peaks = []
    for f in glob.glob(str(PROJ / "print" / "plates-v3" / "*" / "result.json")):
        try:
            peaks.append(json.loads(Path(f).read_text(encoding="utf-8")).get("peak_rss_mb") or 0)
        except ValueError:
            pass
    return {"plates_cache": out.count("CACHE (STL"), "merge_cache": "Project gop: CACHE" in out,
            "bambu_peak_rss_mb_max": round(max(peaks), 1) if peaks else None}


def run(name, cmd, cwd=HERE):
    t0 = time.time()
    if RL is not None:
        cf_ = _cache_cad if name.startswith("file CAD") else (_cache_slice if name.startswith("cat lop") else None)
        r = RL.run(name, cmd, cwd=cwd, cache_fn=cf_, detail_fn=_detail_slice if name.startswith("cat lop") else None)
    else:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    dt = time.time() - t0
    T.append((name, dt, r.returncode))
    return r


def blender(name, script, *args):
    return run(name, [BL, "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(script), "--", *args])


sys.path.insert(0, str(WS / "tools" / "print" / "scripts"))
import meshhash  # noqa: E402


def doi_hinh(src, dst):   # 2026-11-28: so HINH HOC theo dung sai 0,002 mm (boolean Blender doi thu tu tam giac + nhieu float moi lan dung)
    return not meshhash.same_geom(src, dst)       # -> STL trong print/ chi thay khi hinh doi that -> cache cat lop trung


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
    if RL is not None:
        RL.add("kiem in nhanh", time.time() - t0, 1 if bad else 0, detail={"n_stl": len(PRINT_STL)})
    return bad


def main():
    global RL
    a = sys.argv[1:]
    out = []
    mode = ("release" if "--release" in a else "fast") + ("+slice" if "--slice" in a else "") + ("+nobuild" if "--no-build" in a else "")
    RL = RunLog(HERE / "metrics", "english-teacher/owl-v3", mode=mode, cwd=HERE)
    if "--no-build" not in a:
        r = blender("ve (build_owl_v3)", HERE / "build_owl_v3.py", "out-v3")
        if r.returncode:
            print("VE LOI:\n" + "\n".join((r.stdout + r.stderr).splitlines()[-12:])); sys.exit(1)
    changed = []
    for n in PRINT_STL:
        src, dst = HERE / "out-v3" / f"{n}.stl", PROJ / "print" / "stl-v3" / f"{n}.stl"
        if doi_hinh(src, dst):
            shutil.copy2(src, dst); changed.append(n)
    with cf.ThreadPoolExecutor(4) as ex:
        # file CAD (Tuan duyet 2026-11-27): vong sua = 3MF nhanh; --release = .sc + .step + .blend (cache: hinh khong doi -> bo qua)
        rel = "--release" in a
        f_cad = ex.submit(run, "file CAD (" + ("sc/step/blend" if rel else "3mf") + ")",
                          [sys.executable, str(WS / "tools" / "cad-export" / "export_cad.py"), str(HERE / "out-v3" / "asm"), "owl-assembly"]
                          + ([] if rel else ["--fast"]))
        f_asm = ex.submit(blender, "assembly-check", WS / "tools" / "assembly-check" / "assembly_check.py", str(HERE / "assembly.json"))
        f_cp = ex.submit(blender, "mau thu (coupons)", HERE / "make_v3_coupons.py")
        bad = printability()
        r_asm, r_cp, r_cad = f_asm.result(), f_cp.result(), f_cad.result()
    for f in ("belly.stl", "beak.stl", "speaker-ring-R.stl", "belly-clamp.stl"):
        if doi_hinh(HERE / "out-v3" / f, PROJ / "print" / "stl-v3-test" / f):
            shutil.copy2(HERE / "out-v3" / f, PROJ / "print" / "stl-v3-test" / f)
    asm_line = [l for l in r_asm.stdout.splitlines() if l.startswith("ASSEMBLY")] or ["ASSEMBLY ?"]
    out.append(asm_line[0] + "".join("\n  " + l for l in r_asm.stdout.splitlines() if l.startswith("ASM FAIL"))[:600])
    if r_cad.returncode:
        out.append("file CAD: LOI " + r_cad.stdout[-400:])
    elif rel:
        out.append("file CAD: out-v3/owl-assembly.sc|.step|.blend|.3mf" + (" (CACHE)" if "CACHE" in r_cad.stdout else ""))
    else:
        out.append("file CAD: out-v3/owl-assembly.3mf (nhanh; them --release de xuat .sc/.step/.blend)")
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
    tri = sum(meshhash.load_tris(HERE / "out-v3" / "asm" / f"{n}.stl").shape[0] for n in PRINT_STL if (HERE / "out-v3" / "asm" / f"{n}.stl").exists())
    for w in RL.finish({"stl_changed": changed, "tri_total": tri, "gate": "PASS" if any(l.startswith("PASS gate") for l in gl) else "FAIL"}):
        print(w)
    print(f"do luong: cad/metrics/runs.jsonl (xem: python ../../../tools/metrics/runlog.py metrics)")


if __name__ == "__main__":
    main()
