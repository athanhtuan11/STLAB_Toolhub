# Giao viec code/script cho executor free (Codex -> OpenCode -> agy) theo spec.md Claude viet, tu chay gate.
# Claude chi doc dong JSON cuoi (result.json); log dai nam trong thu muc run.
#   python tools/delegate/delegate.py <spec.md> [--executor auto|codex|opencode|agy] [--simulate-limit codex]
#   python tools/delegate/delegate.py --status            # executor nao dang het han muc
#   python tools/delegate/delegate.py --clear-limit codex # xoa danh dau het han muc
# Spec: front matter YAML (task, cwd, allow, gate, timeout_min, max_rounds, executor) + noi dung Markdown,
# mau o templates/spec.md. Duong dan tuong doi tinh tu claude-workspace/.
# Run: %LOCALAPPDATA%/stlab-usage/delegate-runs/<thoi-gian>-<task>/
#      {prompt-N.txt, <executor>-N.log, gate-N.log, result.json}
# Han muc: %LOCALAPPDATA%/stlab-usage/executors.json {executor: {limited_until, reason}}
import argparse, datetime as dt, fnmatch, json, os, re, shutil, subprocess, sys, time
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, "..", ".."))
USAGE = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "stlab-usage")
LIMITS = os.path.join(USAGE, "executors.json")
ORDER = ["codex", "opencode", "agy"]
COOLDOWN_H = {"codex": 5, "opencode": 1, "agy": 24}   # TODO: chua biet chu ky reset that cua Codex Free/Zen free
OPENCODE_MODEL = "opencode/deepseek-v4.1-flash-free"
AGY_MODEL = "gemini-3.8-flash-high"
# Khong giao ra ngoai: du lieu phu huynh, nguon cong dong ghim
REFUSE_CWD = ["stlab/parent-reports", "community"]
# Executor khong duoc dong toi (kiem bang git status sau khi chay)
FORBIDDEN = ["*.FCStd", "*/print.yaml", "print.yaml", "community/*", "*.env", ".env", "*/parent-reports/*"]
LIMIT_RE = re.compile(r"\b429\b|rate.?limit|usage limit|quota (?:reached|exceeded)|exceeded your|too many requests|"
                      r"individual quota", re.I)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

RULES = """You are an executor working for Claude (the lead engineer). Follow the spec exactly.
Rules:
- Work ONLY inside the current directory. Do not read or write outside it.
- Create/modify ONLY files matching: {allow}
- NEVER touch: *.FCStd, print.yaml, community/, .env, keys/passwords. Never git commit/push/reset/checkout.
- Do NOT invent dimensions, component specs or safety values. If the spec lacks a number, write TODO and stop.
- When done, run the gate command yourself: `{gate}` (exit 0 = PASS). Fix and rerun until it passes.
- Last line of your reply: `DONE` if the gate passes, otherwise `BLOCKED: <one-line reason>`.

=== SPEC: {task} ===
{body}
"""
RETRY = """
=== ROUND {n}: the gate FAILED last round. Fix the cause, keep earlier correct work. Gate output (tail): ===
{tail}
"""


def now():
    return dt.datetime.now().astimezone()


def load_limits():
    try:
        return json.load(open(LIMITS, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_limits(lim):
    os.makedirs(USAGE, exist_ok=True)
    json.dump(lim, open(LIMITS, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def is_limited(name, lim):
    until = lim.get(name, {}).get("limited_until")
    return bool(until) and dt.datetime.fromisoformat(until) > now()


def mark_limited(name, reason, until=None):
    lim = load_limits()
    until = until or now() + dt.timedelta(hours=COOLDOWN_H[name])
    lim[name] = dict(limited_until=until.isoformat(timespec="minutes"), reason=reason[:200])
    save_limits(lim)


def pid_alive(pid):
    """Windows: OpenProcess + GetExitCodeProcess (os.kill(pid, 0) tren Windows se GIET tien trinh)."""
    import ctypes
    k = ctypes.windll.kernel32
    h = k.OpenProcess(0x1000, False, int(pid))          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = k.GetExitCodeProcess(h, ctypes.byref(code))
    k.CloseHandle(h)
    return bool(ok) and code.value == 259               # STILL_ACTIVE


def lock_path(cwd_rel):
    return os.path.join(USAGE, "locks", re.sub(r"[^A-Za-z0-9_-]+", "_", cwd_rel) + ".json")


def take_lock(cwd_rel, task, run_dir):
    """1 tac vu / cwd: 2 phien Claude giao trung thu muc thi tu choi. Khoa cua tien trinh da chet (mat dien) = mo coi."""
    p = lock_path(cwd_rel)
    try:
        old = json.load(open(p, encoding="utf-8"))
        if pid_alive(old["pid"]):
            sys.exit(f"TU CHOI: cwd '{cwd_rel}' dang chay tac vu '{old['task']}' (pid {old['pid']}, tu {old['start']})")
    except (OSError, ValueError, KeyError):
        pass
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(dict(pid=os.getpid(), task=task, start=now().isoformat(timespec="seconds"), run_dir=run_dir),
              open(p, "w", encoding="utf-8"), ensure_ascii=False)
    return p


def run_states():
    """Cac run khong co result.json: dang chay (pid song) hoac bi cat ngang (pid chet: mat dien, bi kill)."""
    root = os.path.join(USAGE, "delegate-runs")
    out = []
    for d in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        rd = os.path.join(root, d)
        if os.path.exists(os.path.join(rd, "result.json")):
            continue
        try:
            st = json.load(open(os.path.join(rd, "state.json"), encoding="utf-8"))
        except (OSError, ValueError):
            st = {}
        alive = bool(st.get("pid")) and pid_alive(st["pid"])
        out.append(dict(run=d, state="running" if alive else "interrupted", spec=st.get("spec")))
    return out


def parse_spec(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        sys.exit("spec thieu front matter YAML (--- ... ---)")
    meta = yaml.safe_load(m.group(1)) or {}
    for k in ("task", "cwd", "gate"):
        if not meta.get(k):
            sys.exit(f"spec thieu khoa '{k}'")
    meta.setdefault("allow", ["*"])
    meta.setdefault("timeout_min", 15)
    meta.setdefault("max_rounds", 2)
    meta.setdefault("executor", "auto")
    return meta, m.group(2).strip()


def command(name, prompt):
    """(argv, stdin) cho tung executor. Lenh da thu that 2026-10-26/27 tren Windows."""
    if name == "codex":
        exe = shutil.which("codex.cmd") or shutil.which("codex")
        return [exe, "exec", "--sandbox", "workspace-write", "--skip-git-repo-check",
                "-c", "features.prefer_mxc=true", "-"], prompt
    if name == "opencode":
        exe = os.path.join(os.environ.get("APPDATA", ""), "npm", "node_modules", "opencode-ai", "bin", "opencode.exe")
        exe = exe if os.path.exists(exe) else shutil.which("opencode")
        return [exe, "run", "--model", OPENCODE_MODEL], prompt
    if name == "agy":
        return [shutil.which("agy"), "-p", prompt, "--model", AGY_MODEL,
                "--dangerously-skip-permissions", "--sandbox"], None
    raise ValueError(name)


def installed(name):
    return command(name, "")[0][0] is not None


def run_proc(argv, cwd, stdin, timeout_s, env=None, shell=False):
    t = time.time()
    try:
        p = subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout_s, env=env, shell=shell)
        out, code = (p.stdout or "") + (p.stderr or ""), p.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        out, code = out + f"\n[delegate] TIMEOUT {timeout_s} s", -1
    return out, code, round(time.time() - t)


def git_changed(path):
    """Tap file thay doi/moi (git status, duong dan tuong doi WS, dau '/')."""
    p = subprocess.run(["git", "status", "--porcelain", "-uall", "--", "."], cwd=path, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, capture_output=True,
                         text=True).stdout.strip()
    files = set()
    for line in p.stdout.splitlines():
        f = line[3:].split(" -> ")[-1].strip('"')
        files.add(os.path.relpath(os.path.join(top, f), WS).replace("\\", "/"))
    return files


def file_sig(f):
    try:
        st = os.stat(os.path.join(WS, f))
        return (st.st_size, st.st_mtime_ns)
    except OSError:
        return None


def tail(text, n=40):
    return "\n".join(text.strip().splitlines()[-n:])


def main():
    sys.stdout.reconfigure(encoding="utf-8")            # pipe tren Windows mac dinh cp1252 -> loi khi in tieng Viet
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--executor")
    ap.add_argument("--simulate-limit", default="", help="danh sach executor gia lap het han muc (thu nghiem)")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--clear-limit")
    ap.add_argument("--mark-limit", nargs=2, metavar=("EXECUTOR", "UNTIL"),
                    help="danh dau het han muc toi thoi diem ISO, vd: agy 2026-11-02T12:00")
    a = ap.parse_args()

    if a.status or a.clear_limit or a.mark_limit:
        if a.mark_limit:
            until = dt.datetime.fromisoformat(a.mark_limit[1]).astimezone()
            mark_limited(a.mark_limit[0], "danh dau tay", until)
        lim = load_limits()
        if a.clear_limit:
            lim.pop(a.clear_limit, None)
            save_limits(lim)
        st = {n: dict(installed=installed(n), limited=is_limited(n, lim), **lim.get(n, {})) for n in ORDER}
        st["runs_without_result"] = run_states()
        print(json.dumps(st, ensure_ascii=False))
        return
    if not a.spec:
        ap.error("thieu spec")

    meta, body = parse_spec(a.spec)
    cwd_rel = meta["cwd"].replace("\\", "/").strip("/")
    if any(cwd_rel == r or cwd_rel.startswith(r + "/") or ("/" + r + "/") in ("/" + cwd_rel + "/") for r in REFUSE_CWD):
        sys.exit(f"TU CHOI: cwd '{cwd_rel}' chua du lieu khong duoc gui ra ngoai")
    cwd = os.path.join(WS, cwd_rel)
    if not os.path.isdir(cwd):
        sys.exit(f"cwd khong ton tai: {cwd}")
    allow = [x if isinstance(x, str) else str(x) for x in meta["allow"]]

    choice = a.executor or meta["executor"]
    simulated = {x for x in a.simulate_limit.split(",") if x}
    queue = ORDER if choice == "auto" else [choice]

    run_dir = os.path.join(USAGE, "delegate-runs", now().strftime("%Y%m%d-%H%M%S") + "-" + meta["task"])
    os.makedirs(run_dir, exist_ok=True)
    lock = take_lock(cwd_rel, meta["task"], run_dir)
    json.dump(dict(state="running", pid=os.getpid(), spec=os.path.abspath(a.spec)),
              open(os.path.join(run_dir, "state.json"), "w", encoding="utf-8"), ensure_ascii=False)
    try:
        run_task(a, meta, body, cwd, cwd_rel, allow, queue, simulated, run_dir)
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


def run_task(a, meta, body, cwd, cwd_rel, allow, queue, simulated, run_dir):
    env = dict(os.environ, OPENCODE_CONFIG=os.path.join(HERE, "opencode.json"))
    before = {f: file_sig(f) for f in git_changed(cwd)}
    result = dict(task=meta["task"], cwd=cwd_rel, run_dir=run_dir, rounds=[], skipped=[], passed=False)
    prompt = RULES.format(allow=", ".join(allow), gate=meta["gate"], task=meta["task"], body=body)

    rnd = 0
    while rnd < int(meta["max_rounds"]):
        lim = load_limits()
        name = next((n for n in queue if installed(n) and not is_limited(n, lim) and n not in simulated), None)
        if not name:
            result["skipped"] = [dict(executor=n, why="simulated" if n in simulated else
                                      "not installed" if not installed(n) else "limited") for n in queue]
            result["error"] = "het executor (han muc/chua cai)"
            break
        rnd += 1
        open(os.path.join(run_dir, f"prompt-{rnd}.txt"), "w", encoding="utf-8").write(prompt)
        argv, stdin = command(name, prompt)
        out, code, secs = run_proc(argv, cwd, stdin, int(meta["timeout_min"]) * 60, env)
        open(os.path.join(run_dir, f"{name}-{rnd}.log"), "w", encoding="utf-8").write(out)
        lines = [x.strip() for x in ANSI_RE.sub("", out).splitlines() if x.strip()]
        last = next((x for x in reversed(lines) if re.match(r"`?(DONE|BLOCKED)", x)), (lines or [""])[-1])[:200]
        r = dict(round=rnd, executor=name, exit=code, seconds=secs, last_line=last)
        if code != 0 and LIMIT_RE.search(out[-4000:]):
            mark_limited(name, tail(out, 3))
            r["limited"] = True
            result["rounds"].append(r)
            rnd -= 1                                    # vong nay khong tinh, chuyen executor ke tiep
            continue
        gout, gcode, gsecs = run_proc(meta["gate"], cwd, None, 20 * 60, shell=True)
        open(os.path.join(run_dir, f"gate-{rnd}.log"), "w", encoding="utf-8").write(gout)
        r.update(gate_exit=gcode, gate_seconds=gsecs, gate_tail=tail(gout, 5))
        result["rounds"].append(r)
        if gcode == 0:
            result["passed"] = True
            break
        prompt += RETRY.format(n=rnd + 1, tail=tail(gout))

    # Kiem file thay doi: cam + ngoai allow (so voi truoc khi chay)
    after = git_changed(cwd)
    touched = sorted(f for f in after if before.get(f, "new") != file_sig(f))
    def rel(f):
        return os.path.relpath(os.path.join(WS, f), cwd).replace("\\", "/")

    forbidden = [f for f in touched if any(fnmatch.fnmatch(f, p) or fnmatch.fnmatch(os.path.basename(f), p)
                                           for p in FORBIDDEN)]
    outside = [f for f in touched if f not in forbidden and
               (rel(f).startswith("..") or not any(fnmatch.fnmatch(rel(f), p) for p in allow))]
    result.update(changed=touched, forbidden_touched=forbidden, outside_allow=outside)
    if forbidden:
        result["passed"] = False
        result["error"] = "executor dong vao file cam – Claude kiem tay, KHONG commit"
    result["verdict"] = "PASS" if result["passed"] and not outside else "WARN" if result["passed"] else "FAIL"
    json.dump(result, open(os.path.join(run_dir, "result.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["verdict"] != "FAIL" else 1)


if __name__ == "__main__":
    main()
