"""runlog.py - do luong moi lan chay chuoi CAD (Tuan duyet 2026-11-27, bao cao docs/reports/Do luong hieu nang chuoi CAD.md).

Moi lan chay ghi 1 dong JSON vao <metrics_dir>/runs.jsonl:
  {"ts", "project", "commit", "dirty", "mode", "load_cpu_pct", "ram_free_mb", "total_s",
   "steps": [{"step", "s", "rc", "peak_mem_mb", "cache", "detail"}]}
peak_mem_mb = PeakWorkingSetSize cua tien trinh con (Windows ghi san, doc qua handle sau khi tien trinh xong; khong lay mau).
Canh bao cham di: so voi trung vi + MAD cua <= 20 lan gan nhat CUNG (step, mode, cache); chi bao khi lan nay VA lan truoc deu vuot
(nguong = max(trung vi + 3,5 x 1,4826 x MAD, trung vi x 1,15, trung vi + 1 s) - cac so [chon], chinh sau ~2 tuan du lieu).
    from runlog import RunLog
    rl = RunLog(metrics_dir, "english-teacher/v3", mode="fast")
    r = rl.run("ve", [exe, ...], cwd=...)            # subprocess.run-giong, tra CompletedProcess
    rl.add("kiem in nhanh", 4.8, rc=0)                 # buoc chay trong tien trinh
    rl.finish()                                        # ghi dong + in canh bao (tra danh sach canh bao)
    python runlog.py <metrics_dir> [--last 10]         # bang tom tat lich su
"""
import ctypes
import json
import os
import statistics
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path


class _PMC(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]


def _peak_mb(popen):
    """PeakWorkingSetSize (MB) cua tien trinh con da ket thuc (handle Popen con mo). Ngoai Windows / loi -> None."""
    if os.name != "nt":
        return None
    try:
        f = ctypes.WinDLL("psapi").GetProcessMemoryInfo
        f.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC), wintypes.DWORD]
        f.restype = wintypes.BOOL
        pmc = _PMC(); pmc.cb = ctypes.sizeof(_PMC)
        if f(wintypes.HANDLE(int(popen._handle)), ctypes.byref(pmc), pmc.cb):
            return round(pmc.PeakWorkingSetSize / 2 ** 20, 1)
    except Exception:  # noqa: BLE001 - do luong khong duoc lam hong lan chay
        pass
    return None


def _git(cwd):
    try:
        c = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=cwd, capture_output=True, text=True, timeout=10).stdout.strip()
        d = bool(subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=cwd, capture_output=True, text=True,
                                timeout=20).stdout.strip())
        return c, d
    except Exception:  # noqa: BLE001
        return "", None


class RunLog:
    def __init__(self, metrics_dir, project, mode="", cwd=None):
        self.dir = Path(metrics_dir); self.dir.mkdir(parents=True, exist_ok=True)
        self.project, self.mode = project, mode
        self.t0 = time.time(); self.steps = []
        self.commit, self.dirty = _git(cwd or self.dir)
        self.load, self.ram_free = None, None
        try:
            import psutil
            self.load = psutil.cpu_percent(interval=0.2)
            self.ram_free = round(psutil.virtual_memory().available / 2 ** 20)
        except Exception:  # noqa: BLE001
            pass

    def add(self, step, seconds, rc=0, peak_mem_mb=None, cache=None, detail=None):
        self.steps.append({"step": step, "s": round(seconds, 2), "rc": rc, "peak_mem_mb": peak_mem_mb, "cache": cache,
                           "detail": detail or {}})

    def run(self, step, cmd, cwd=None, cache_fn=None, detail_fn=None):
        """Chay lenh (capture stdout/stderr), do thoi gian + RAM dinh; cache_fn(stdout)->'hit'/'miss'/'partial'/None."""
        t = time.time()
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        out, err = p.communicate()
        dt = time.time() - t
        r = subprocess.CompletedProcess(cmd, p.returncode, out, err)
        try:
            cache = cache_fn(out) if cache_fn else None
            det = detail_fn(out) if detail_fn else None
        except Exception:  # noqa: BLE001
            cache, det = None, None
        self.add(step, dt, p.returncode, _peak_mb(p), cache, det)
        return r

    def finish(self, extra=None):
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "project": self.project, "commit": self.commit, "dirty": self.dirty,
               "mode": self.mode, "load_cpu_pct": self.load, "ram_free_mb": self.ram_free, "total_s": round(time.time() - self.t0, 2),
               "steps": self.steps}
        if extra:
            rec.update(extra)
        hist = self.history()
        f = self.dir / "runs.jsonl"
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return self.warnings(rec, hist)

    def history(self):
        f = self.dir / "runs.jsonl"
        if not f.exists():
            return []
        out = []
        for ln in f.read_text(encoding="utf-8").splitlines():
            try:
                j = json.loads(ln)
            except ValueError:
                continue
            if j.get("project") == self.project:
                out.append(j)
        return out

    @staticmethod
    def _limit(vals):
        med = statistics.median(vals)
        mad = statistics.median([abs(v - med) for v in vals])
        return med, max(med + 3.5 * 1.4826 * mad, med * 1.15, med + 1.0)

    def warnings(self, rec, hist):
        """Canh bao khi buoc nay cham hon nguong o CA lan nay va lan cung nhom ngay truoc (>= 5 lan lich su)."""
        warn = []
        for st in rec["steps"]:
            if st.get("rc"):
                continue
            key = (st["step"], rec["mode"], st.get("cache"))
            same = [(j, s) for j in hist for s in j["steps"] if (s["step"], j.get("mode"), s.get("cache")) == key and not s.get("rc")]
            if len(same) < 5:
                continue
            vals = [s["s"] for _, s in same[-20:]]
            med, lim = self._limit(vals[:-1] if len(vals) > 5 else vals)
            if st["s"] > lim and same[-1][1]["s"] > lim:
                warn.append(f"CHAM DI: {st['step']} ({rec['mode']}, cache={st.get('cache')}) {st['s']:.1f} s > nguong {lim:.1f} s "
                            f"(trung vi {med:.1f} s, 2 lan lien tiep)")
        tot = [j["total_s"] for j in hist if j.get("mode") == rec["mode"]][-20:]
        if len(tot) >= 5:
            med, lim = self._limit(tot)
            if rec["total_s"] > lim and tot[-1] > lim:
                warn.append(f"CHAM DI: tong vong ({rec['mode']}) {rec['total_s']:.0f} s > nguong {lim:.0f} s (trung vi {med:.0f} s)")
        return warn


def summary(metrics_dir, last=10):
    f = Path(metrics_dir) / "runs.jsonl"
    if not f.exists():
        print("chua co du lieu"); return
    rows = [json.loads(ln) for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()][-last:]
    for j in rows:
        st = ", ".join(f"{s['step']} {s['s']:.0f}s" + (f"[{s['cache']}]" if s.get("cache") else "") +
                       (f" {s['peak_mem_mb']:.0f}MB" if s.get("peak_mem_mb") else "") for s in j["steps"])
        print(f"{j['ts']} {j['commit']}{'*' if j.get('dirty') else ''} {j['mode']:7s} tong {j['total_s']:5.1f}s | {st}")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    n = int(sys.argv[sys.argv.index("--last") + 1]) if "--last" in sys.argv else 10
    summary(a[0] if a else ".", n)
