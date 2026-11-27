"""printlog.py - ghi KET QUA IN + LAP THAT vao <du-an>/metrics/prints.jsonl (Tuan duyet 2026-11-27, bao cao "Do luong hieu nang chuoi CAD").
Moi lan in/lap 1 dong; noi voi runs.jsonl qua commit. Gio in + gam lay tu print-report.json cua bo in (neu co).

  python tools/metrics/printlog.py maker/english-teacher --yaml print/print-v3.yaml --plates A_shell_front,B_shell_back \
      --result pass --fit seam-spline=ok --fit mic-screw=tight --fit belly-clamp=loose --cause design-fit --note "gai bung hoi long"
  python tools/metrics/printlog.py maker/english-teacher --report        # tong ket: ty le dat lan dau, fit theo khe, Pareto nguyen nhan

--result: pass (dung duoc) | rework (phai sua thiet ke/in lai) | fail (hong ban in)
--fit <moi-ghep>=tight|ok|loose  (lap lai nhieu lan)
--cause (khi rework/fail, danh muc co dinh): design-fit, strength, printability, assembly, machine, material, operator
"""
import argparse
import collections
import json
import subprocess
import time
from pathlib import Path

CAUSES = ["design-fit", "strength", "printability", "assembly", "machine", "material", "operator"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--yaml", default="")
    ap.add_argument("--plates", default="")
    ap.add_argument("--result", choices=["pass", "rework", "fail"])
    ap.add_argument("--fit", action="append", default=[])
    ap.add_argument("--cause", choices=CAUSES)
    ap.add_argument("--note", default="")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    f = proj / "metrics" / "prints.jsonl"
    if a.report:
        return report(f)
    if not a.result:
        ap.error("--result la bat buoc (hoac --report)")
    if a.result != "pass" and not a.cause:
        ap.error("rework/fail can --cause (" + ", ".join(CAUSES) + ")")
    fits = {}
    for x in a.fit:
        k, _, v = x.partition("=")
        if v not in ("tight", "ok", "loose"):
            ap.error(f"--fit {x}: gia tri tight|ok|loose")
        fits[k] = v
    plates = [p for p in a.plates.split(",") if p]
    hours = grams = None
    if a.yaml:
        rp = proj / Path(a.yaml).parent
        rep = None
        for cand in rp.glob("plates*/print-report.json"):
            try:
                j = json.loads(cand.read_text(encoding="utf-8"))
            except ValueError:
                continue
            if Path(j.get("yaml", "")).name == Path(a.yaml).name:
                rep = j
        if rep:
            sel = [b for b in rep.get("ban", []) if not plates or b["ban"] in plates]
            hours = round(sum(b.get("thoi_gian_s", 0) for b in sel) / 3600, 2)
            grams = round(sum(b.get("gam", 0) for b in sel), 1)
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=proj, capture_output=True, text=True).stdout.strip()
    except OSError:
        commit = ""
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "project": proj.name, "commit": commit, "yaml": a.yaml, "plates": plates,
           "print_hours": hours, "grams": grams, "result": a.result, "cause": a.cause, "fits": fits, "note": a.note}
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(f, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("GHI", f, json.dumps(rec, ensure_ascii=False))


def report(f):
    if not f.exists():
        print("chua co du lieu in"); return
    rows = [json.loads(ln) for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
    n = len(rows); ok1 = sum(1 for r in rows if r["result"] == "pass")
    print(f"{n} lan in/lap | dat: {ok1} ({100 * ok1 / n:.0f} %) | gio in {sum(r.get('print_hours') or 0 for r in rows):.1f} h | "
          f"nhua {sum(r.get('grams') or 0 for r in rows):.0f} g")
    fit = collections.defaultdict(collections.Counter)
    for r in rows:
        for k, v in r.get("fits", {}).items():
            fit[k][v] += 1
    for k, c in sorted(fit.items()):
        tot = sum(c.values())
        print(f"  khe {k:24s} vua {c['ok']}/{tot}  chat {c['tight']}  long {c['loose']}")
    cz = collections.Counter(r["cause"] for r in rows if r.get("cause"))
    if cz:
        print("  nguyen nhan lam lai (Pareto): " + ", ".join(f"{k} {v}" for k, v in cz.most_common()))


if __name__ == "__main__":
    main()
