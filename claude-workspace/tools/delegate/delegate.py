# Giao viec code/script cho executor free (Codex -> OpenCode -> Kilo -> agy-sonnet -> Copilot -> Goose -> agy) theo spec.md Claude viet, tu chay gate.
# Claude chi doc dong JSON cuoi (result.json); log dai nam trong thu muc run.
#   python tools/delegate/delegate.py <spec.md> [--executor auto|codex|opencode|kilo|agy-sonnet|copilot|goose|agy] [--simulate-limit codex]
#   python tools/delegate/delegate.py --status            # executor nao dang het han muc
#   python tools/delegate/delegate.py --clear-limit codex # xoa danh dau het han muc
#   python tools/delegate/delegate.py --stats [--rebuild] # thanh tich tung executor (JSON: gate_pass/rounds)
#   python tools/delegate/delegate.py --resume <run>      # chay lai run bi cat ngang (run_dir moi, prompt them ngu canh)
#   Run khong PASS -> handoff.md trong run_dir (tom tat vong, gate, file thay doi, buoc tiep).
# Spec: front matter YAML (task, cwd, allow, gate, timeout_min, max_rounds, executor, ky_nang) + Markdown.
# Nhan su, ky_nang, model va chinh sach lay tu claude-workspace/org/agents.yaml + policy.yaml.
# mau o templates/spec.md. Duong dan tuong doi tinh tu claude-workspace/.
# Run: %LOCALAPPDATA%/stlab-usage/delegate-runs/<thoi-gian>-<task>/
#      {prompt-N.txt, <executor>-N.log, gate-N.log, result.json}
# Han muc: %LOCALAPPDATA%/stlab-usage/executors.json {executor: {limited_until, reason}}
# Thanh tich: %LOCALAPPDATA%/stlab-usage/agent-stats.json {executor: {rounds, gate_pass, pass_round1,
#      limited, escalate, seconds}}; update_stats moi run, --stats --rebuild tinh lai tu lich su run.
import argparse, codecs, datetime as dt, fnmatch, json, os, queue as queue_module, re, shutil, signal, subprocess, sys, threading, time
import yaml


HERE = os.path.dirname(os.path.abspath(__file__))

try:
    sys.path.insert(0, os.path.join(HERE, "..", "org"))
    import events as _events
except Exception:
    _events = None

def _event_emit(*args, **kwargs):
    try:
        if _events:
            return _events.emit(*args, **kwargs)
    except Exception:
        pass
    return None
WS = os.path.abspath(os.path.join(HERE, "..", ".."))
USAGE = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "stlab-usage")
LIMITS = os.path.join(USAGE, "executors.json")
ADAPTERS = {"codex": "codex", "opencode": "opencode", "kilo": "kilo", "agy-sonnet": "agy-sonnet", "copilot": "copilot", "goose": "goose", "agy": "agy"}
STAT_FIELDS = ("rounds", "gate_pass", "pass_round1", "limited", "stalled", "escalate", "seconds")
STALL_MIN = float(os.environ.get("DELEGATE_STALL_MIN", "6"))
NEED_WORKTREE = {"goose"}

def load_org(org_dir=None):
    """Nap so nhan su va policy; loi/hong so phai duoc bao ro."""
    org_dir = org_dir or os.path.join(WS, "org")
    try:
        with open(os.path.join(org_dir, "agents.yaml"), encoding="utf-8") as f:
            doc = yaml.safe_load(f)
        with open(os.path.join(org_dir, "policy.yaml"), encoding="utf-8") as f:
            policy = yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        raise ValueError(f"khong doc duoc so org: {e}") from e
    if not isinstance(doc, dict) or not isinstance(doc.get("agents"), list) or not isinstance(policy, dict):
        raise ValueError("so org sai cau truc")
    agents = {a.get("id"): a for a in doc["agents"] if isinstance(a, dict) and a.get("id")}
    ex = {i: a for i, a in agents.items() if a.get("loai") == "cli-executor" and a.get("chi_phi") != "tra-phi"}
    for ident, a in ex.items():
        if a.get("trang_thai") in ("chinh-thuc", "thu-viec") and ident not in ADAPTERS:
            raise ValueError(f"executor khong co ADAPTERS: {ident}")
    incoming = {a.get("khi_het_han_muc") for a in ex.values() if a.get("khi_het_han_muc") in ex}
    starts = [i for i in ex if ex[i].get("trang_thai") == "chinh-thuc" and i not in incoming]
    if len(starts) != 1:
        raise ValueError("chuoi khi_het_han_muc khong co diem bat dau duy nhat")
    order, seen, ident = [], set(), starts[0]
    while ident is not None:
        if ident in seen:
            break
        if ident not in ex:
            raise ValueError(f"chuoi khi_het_han_muc khong hop le tai {ident}")
        seen.add(ident)
        a = ex[ident]
        if a.get("trang_thai") == "chinh-thuc":
            if ident not in ADAPTERS:
                raise ValueError(f"executor khong co ADAPTERS: {ident}")
            order.append(ident)
        ident = a.get("khi_het_han_muc")
    return dict(order=order, cooldown={i: a.get("cooldown_h") for i, a in ex.items()},
                model={i: a.get("model") for i, a in agents.items()}, forbidden=policy.get("duong_cam"),
                agents=agents, policy=policy)

ORG = load_org()
ORDER, COOLDOWN_H, FORBIDDEN = ORG["order"], {n: ORG["cooldown"][n] for n in ORG["order"]}, ORG["forbidden"]
# Khong giao ra ngoai: du lieu phu huynh, nguon cong dong ghim
REFUSE_CWD = ["stlab/parent-reports", "community"]
# Executor khong duoc dong toi (kiem bang git status sau khi chay)
LIMIT_RE = re.compile(r"\b429\b|rate.?limit|usage limit|quota (?:reached|exceeded)|exceeded your|too many requests|"
                      r"individual quota", re.I)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

RULES = """You are an executor working for Claude (the lead engineer). Follow the spec exactly.
Rules:
- WRITE only inside the current directory. READ only inside the current directory{read}.
- Create/modify ONLY files matching: {allow}
- NEVER touch: *.FCStd, print.yaml, community/, .env, keys/passwords. Never git commit/push/reset/checkout.
- Do NOT invent dimensions, component specs or safety values. If the spec lacks a number, write TODO and stop.
- Text files are UTF-8 WITHOUT BOM and keep Vietnamese diacritics. On this Windows machine PowerShell 5.1
  turns every non-ASCII letter into '?' when text goes through a pipe (`@'...'@ | python`, `echo ... |`),
  Set-Content, Out-File or `>`. Pure-ASCII content (code, comments without diacritics) may be written any way that
  works for you. NEVER pass NON-ASCII text (Vietnamese diacritics, '·', '–') through PowerShell: either use a
  file-editing tool (apply_patch / edit) or Python whose COMMAND IS PURE ASCII with every non-ASCII char written as
  \\uXXXX, e.g. python -c "open('r.md','w',encoding='utf-8').write('Ki\\u1ec3m')". Files with letters turned into '?'
  are rejected.
- When done, run the gate command yourself: `{gate}` (exit 0 = PASS). Fix and rerun until it passes.
- If a step needs a permission you do not have, or is not your job (outside this spec), STOP and do not work
  around it: last line `ESCALATE: <what is needed and why>` – Claude (your manager) will decide.
- Last line of your reply: `DONE` if the gate passes, otherwise `BLOCKED: <one-line reason>` or `ESCALATE: ...`.

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


def reset_from_reason(reason):
    """Gio het han muc doc tu thong bao loi, vd agy 'Resets in 137h19m52s' (2026-10-27) – chinh xac hon COOLDOWN_H."""
    m = re.search(r"[Rr]esets? in (?:(\d+)h)?\s*(?:(\d+)m)?", reason or "")
    if not m or not (m.group(1) or m.group(2)):
        return None
    return now() + dt.timedelta(hours=int(m.group(1) or 0), minutes=int(m.group(2) or 0))


def mark_limited(name, reason, until=None):
    lim = load_limits()
    until = until or reset_from_reason(reason) or now() + dt.timedelta(hours=COOLDOWN_H.get(name, ORG["cooldown"][name]))
    lim[name] = dict(limited_until=until.isoformat(timespec="minutes"), reason=reason[:200])
    save_limits(lim)


def stats_path():
    return os.path.join(USAGE, "agent-stats.json")


def load_stats():
    try:
        with open(stats_path(), encoding="utf-8") as f:
            doc = json.load(f)
        return doc if isinstance(doc, dict) else {}
    except (OSError, ValueError):
        return {}


def save_stats(stats):
    os.makedirs(USAGE, exist_ok=True)
    with open(stats_path(), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=1, ensure_ascii=False)


def new_stats():
    return dict.fromkeys(STAT_FIELDS, 0)


def run_stamp(result):
    """Moc thoi gian tu ten run_dir 'YYYYMMDD-HHMMSS-<task>' -> 'YYYY-MM-DDTHH:MM'; sai dang -> ''."""
    m = re.match(r"^(\d{8})-(\d{6})-", os.path.basename(str(result.get("run_dir") or "")))
    if not m:
        return ""
    d, t = m.groups()
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}T{t[:2]}:{t[2:4]}"


def tally(stats, result):
    """Cong don 1 run vao stats (dung chung cho update_stats va rebuild_stats)."""
    rounds = result.get("rounds") or []
    stamp = run_stamp(result)
    for i, r in enumerate(rounds):
        name = r.get("executor")
        if not name:
            continue
        s = stats.setdefault(name, new_stats())
        if stamp:
            if stamp > (s.get("last_run") or ""):
                s["last_run"] = stamp
            if r.get("limited") and stamp > (s.get("last_limited") or ""):
                s["last_limited"] = stamp
            if r.get("gate_exit") == 0 and stamp > (s.get("last_pass") or ""):
                s["last_pass"] = stamp
        if r.get("limited"):
            s["limited"] += 1
            continue
        if r.get("stalled"):
            s["stalled"] = s.get("stalled", 0) + 1
            secs = r.get("seconds")
            if isinstance(secs, (int, float)):
                s["seconds"] += int(secs)
            continue
        s["rounds"] += 1
        if r.get("gate_exit") == 0:
            s["gate_pass"] += 1
            if i == 0:                                  # vong 1 cua run da dat ngay
                s["pass_round1"] += 1
        secs = r.get("seconds")
        if isinstance(secs, (int, float)):
            s["seconds"] += int(secs)
    if rounds and result.get("verdict") == "ESCALATE":
        name = rounds[-1].get("executor")
        if name:                                        # run bao len tren, vong cuoi cua ai thi tinh cho nguoi do
            stats.setdefault(name, new_stats())["escalate"] += 1


def update_stats(result):
    """Cong don 1 run vao agent-stats.json."""
    stats = load_stats()
    tally(stats, result)
    save_stats(stats)
    return stats


def run_roots():
    """Thu muc chua cac run: USAGE/delegate-runs; chua co thi tim delegate-runs canh thu muc cha."""
    primary = os.path.join(USAGE, "delegate-runs")
    if os.path.isdir(primary):
        return [primary]
    parent = os.path.join(os.path.dirname(os.path.normpath(USAGE)), "delegate-runs")
    if os.path.isdir(parent) and os.path.normcase(os.path.abspath(parent)) != os.path.normcase(os.path.abspath(primary)):
        return [parent]
    return [primary]


def recent_counts(days=7, root=None):
    """Count executor log files in recent date-stamped run directories."""
    roots = [root] if root is not None else run_roots()
    cutoff = (dt.date.today() - dt.timedelta(days=max(1, int(days)) - 1)).strftime("%Y%m%d")
    counts = {}
    log_re = re.compile(r"^(.+)-\d+\.log$")
    for runs_root in roots:
        try:
            run_names = os.listdir(runs_root)
        except OSError:
            continue
        for run_name in run_names:
            if not re.match(r"^\d{8}-", run_name) or run_name[:8] < cutoff:
                continue
            run_dir = os.path.join(runs_root, run_name)
            if not os.path.isdir(run_dir):
                continue
            try:
                for filename in os.listdir(run_dir):
                    match = log_re.match(filename)
                    if match and os.path.isfile(os.path.join(run_dir, filename)):
                        name = match.group(1)
                        counts[name] = counts.get(name, 0) + 1
            except OSError:
                continue
    return counts


def order_fair(queue, counts):
    """Order executors by recent rounds, retaining the original order for ties."""
    return sorted(queue, key=lambda name: counts.get(name, 0))


def rebuild_stats():
    """Tinh lai thanh tich TU DAU tu moi <run>/result.json (idempotent)."""
    stats = {}
    for root in run_roots():
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            p = os.path.join(root, name, "result.json")
            try:
                with open(p, encoding="utf-8") as f:
                    result = json.load(f)
            except (OSError, ValueError):
                continue
            if isinstance(result, dict):
                tally(stats, result)
    save_stats(stats)
    return stats


def rank_by_stats(queue, stats, min_rounds=3):
    """Executor du >= min_rounds vong xep theo gate_pass/rounds giam dan, roi moi nguoi con lai.
    Bang nhau (va nguoi < min_rounds) giu thu tu goc."""
    def rate(name):
        s = stats.get(name) or {}
        rounds = s.get("rounds") or 0
        return rounds, (s.get("gate_pass") or 0) / rounds if rounds else 0

    ready = [n for n in queue if rate(n)[0] >= min_rounds]
    rest = [n for n in queue if rate(n)[0] < min_rounds]
    ready.sort(key=lambda n: rate(n)[1], reverse=True)   # sort on dinh: bang nhau giu thu tu goc
    return ready + rest


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


def take_lock(cwd_rel, task, run_dir, allow_ws=None):
    """1 tac vu / cwd: 2 phien Claude giao trung thu muc thi tu choi. Khoa cua tien trinh da chet (mat dien) = mo coi.
    Ghi them cwd + allow_ws (mau glob tuong doi WS) de run khac biet file nao dang duoc run nay so huu."""
    p = lock_path(cwd_rel)
    try:
        old = json.load(open(p, encoding="utf-8"))
        if pid_alive(old["pid"]):
            sys.exit(f"TU CHOI: cwd '{cwd_rel}' dang chay tac vu '{old['task']}' (pid {old['pid']}, tu {old['start']})")
    except (OSError, ValueError, KeyError):
        pass
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(dict(pid=os.getpid(), task=task, start=now().isoformat(timespec="seconds"), run_dir=run_dir,
                   cwd=cwd_rel, allow_ws=list(allow_ws or [])),
              open(p, "w", encoding="utf-8"), ensure_ascii=False)
    return p


def _pid_ok(pid):
    try:
        return bool(pid) and pid_alive(pid)
    except (TypeError, ValueError, OSError):
        return False


def _same_dir(a, b):
    return bool(a) and os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def _lock_alive(rd):
    """Khoa con song trong USAGE/locks/*.json co run_dir trung run nay (state.json mat/thieu pid)."""
    ldir = os.path.join(USAGE, "locks")
    try:
        names = os.listdir(ldir)
    except OSError:
        return False
    for f in names:
        if not f.endswith(".json"):
            continue
        try:
            lk = json.load(open(os.path.join(ldir, f), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if _same_dir(lk.get("run_dir"), rd) and _pid_ok(lk.get("pid")):
            return True
    return False


def other_runs_claim(files, my_run_dir):
    """File (tuong doi WS) dang nam trong allow cua MOT run khac con song -> khong tinh la ngoai allow cua run nay."""
    ldir = os.path.join(USAGE, "locks")
    try:
        names = os.listdir(ldir)
    except OSError:
        return []
    claimed = []
    for f in names:
        if not f.endswith(".json"):
            continue
        try:
            lk = json.load(open(os.path.join(ldir, f), encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(lk, dict):
            continue
        if not _pid_ok(lk.get("pid")):                  # chu so huu da chet -> khoa mo coi, khong giu file
            continue
        if _same_dir(lk.get("run_dir"), my_run_dir):    # khoa cua chinh run nay
            continue
        pats = [p for p in (lk.get("allow_ws") or []) if isinstance(p, str)]
        for x in files:
            rel = str(x).replace("\\", "/")
            if any(fnmatch.fnmatch(rel, p) for p in pats) and x not in claimed:
                claimed.append(x)
    return claimed


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
        alive = _pid_ok(st.get("pid")) or _lock_alive(rd)
        out.append(dict(run=d, state="running" if alive else "interrupted", spec=st.get("spec")))
    return out


def read_tail(path, n=40):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return tail(f.read(), n)
    except OSError:
        return ""


def build_resume(run_dir):
    """(spec_path, context) de chay lai run bi cat ngang; loi -> ValueError."""
    root = os.path.join(USAGE, "delegate-runs")
    rd = os.path.abspath(run_dir if os.path.isdir(run_dir) else os.path.join(root, run_dir))
    if not os.path.isdir(rd):
        raise ValueError(f"run khong ton tai: {run_dir}")
    if os.path.exists(os.path.join(rd, "result.json")):
        raise ValueError("run da xong (co result.json)")
    try:
        st = json.load(open(os.path.join(rd, "state.json"), encoding="utf-8"))
    except (OSError, ValueError):
        st = {}
    if _pid_ok(st.get("pid")) or _lock_alive(rd):
        raise ValueError("run van dang chay (pid con song) – khong resume de tranh chay trung")
    spec = st.get("spec")
    if not spec:
        raise ValueError("state.json thieu 'spec'")

    # Log executor vong cuoi: <executor>-N.log co N lon nhat (bo qua gate-N.log).
    logs = []
    for f in os.listdir(rd):
        m = re.match(r"^(.+)-(\d+)\.log$", f)
        if m and m.group(1) != "gate":
            logs.append((int(m.group(2)), os.path.getmtime(os.path.join(rd, f)), f, m.group(1)))
    name = os.path.basename(os.path.normpath(rd))
    parts = [f"=== Lan chay truoc bi cat ngang (resume tu run {name}) ==="]
    if logs:
        top = max(logs)
        n, f = top[0], top[2]
        parts += [f"--- {f} (duoi 40 dong) ---", read_tail(os.path.join(rd, f))]
        g = f"gate-{n}.log"
        if os.path.exists(os.path.join(rd, g)):
            parts += [f"--- {g} (duoi 40 dong) ---", read_tail(os.path.join(rd, g))]
    else:
        parts.append("(khong thay log executor)")
    return spec, "\n".join(parts)


def write_handoff(run_dir, result):
    """Ghi handoff.md (tieng Viet) khi run khong PASS; tra duong dan file."""
    p = os.path.join(run_dir, "handoff.md")
    tasks = result.get("task", "?")
    lines = [f"# Handoff: {tasks}", "",
             f"- Task: `{tasks}`",
             f"- Verdict: **{result.get('verdict', '?')}**",
             f"- Run: `{os.path.basename(os.path.normpath(run_dir))}`"]
    if result.get("resumed_from"):
        lines.append(f"- Tiep tu run: `{result['resumed_from']}`")
    if result.get("error"):
        lines.append(f"- Loi: {result['error']}")
    if result.get("escalate"):
        lines.append(f"- BAO LEN TREN (executor thieu quyen/ngoai viec, Claude quyet): {result['escalate']}")
    lines += ["", "## Tung vong"]
    for r in result.get("rounds", []):
        lines += [f"### Vong {r.get('round', '?')} - {r.get('executor', '?')}",
                  f"- Thoi gian: {r.get('seconds', '?')} s",
                  f"- Dong cuoi: {r.get('last_line', '')}",
                  f"- Gate exit: {r.get('gate_exit', '?')}",
                  "- Gate tail:",
                  "```",
                  str(r.get("gate_tail", "")),
                  "```"]
    lines += ["", "## File thay doi"]
    for title, key in (("Da doi", "changed"), ("File cam", "forbidden_touched"), ("Ngoai allow", "outside_allow")):
        vals = result.get(key) or []
        lines.append(f"- {title}: " + (", ".join(f"`{v}`" for v in vals) if vals else "(khong co)"))
    lines += ["", "Bước tiếp: `python tools/delegate/delegate.py --resume <ten run>` hoặc Claude sửa spec"]
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return p


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
    meta.setdefault("ky_nang", None)
    meta.setdefault("read", [])                          # thu muc duoc DOC them (tuong doi claude-workspace), khong ghi
    if not isinstance(meta.get("worktree"), bool):       # tuy chon: chay trong git worktree rieng (mac dinh False)
        meta["worktree"] = bool(meta.get("worktree"))
    return meta, m.group(2).strip()


def _codex(prompt):
    """Dung lenh Codex hien tai."""
    name = "codex"
    if name == "codex":
        exe = shutil.which("codex.cmd") or shutil.which("codex")
        return [exe, "exec", "--sandbox", "workspace-write", "--skip-git-repo-check",
                "-c", "features.prefer_mxc=true", "-"], prompt
    return None, None

def _opencode(prompt):
    name = "opencode"
    if name == "opencode":
        exe = os.path.join(os.environ.get("APPDATA", ""), "npm", "node_modules", "opencode-ai", "bin", "opencode.exe")
        exe = exe if os.path.exists(exe) else shutil.which("opencode")
        return [exe, "run", "--model", ORG["model"][name]], prompt
    return None, None

def _agy(prompt):
    return _agy_named("agy", prompt)

AGY_NOTE = """
NOTE (agy sandbox): your sandbox has no python and cannot see paths outside the current directory, so you
cannot run the gate. Do NOT run it and do NOT ESCALATE for that – delegate.py runs the gate right after you and
sends you its output next round if it fails. Write the files, check them by reading, then reply `DONE`."""


def _agy_named(name, prompt):
    # sandbox agy khong thay python (thu 2026-10-28) -> gate do delegate.py chay, giu --sandbox
    return [shutil.which("agy"), "-p", prompt + AGY_NOTE, "--model", ORG["model"][name],
            "--dangerously-skip-permissions", "--sandbox"], None

def _kilo(prompt):
    exe = shutil.which("kilo.cmd") or shutil.which("kilo")
    return [exe, "run", "--model", ORG["model"]["kilo"]], prompt

def _agy_sonnet(prompt):
    return _agy_named("agy-sonnet", prompt)

def _copilot(prompt):
    exe = shutil.which("copilot.cmd") or shutil.which("copilot")
    # prompt qua stdin (argv cua copilot.cmd qua cmd.exe vo & | % "); --sandbox = MXC cua HDH (thu 2026-10-28)
    argv = [exe, "-s", "--no-ask-user", "--sandbox", "--allow-all-tools", "--disable-builtin-mcps",
            "--deny-tool=shell(git commit)", "--deny-tool=shell(git push)",
            "--deny-tool=shell(git reset)", "--deny-tool=shell(git checkout)",
            "--deny-tool=shell(rm -rf)", "--deny-tool=shell(Remove-Item)"]
    model = ORG["model"]["copilot"]
    if model != "auto":
        argv += ["--model", model]
    return argv, prompt

def _goose(prompt):
    exe = shutil.which("goose")
    profile = os.environ.get("USERPROFILE")
    if not exe and profile:
        candidate = os.path.join(profile, ".local", "goose", "goose-package", "goose.exe")
        exe = candidate if os.path.exists(candidate) else None
    return [exe, "run", "--no-session", "-i", "-", "--provider", "google",
            "--model", ORG["model"]["goose"]], prompt

ADAPTERS.update(codex=_codex, opencode=_opencode, kilo=_kilo,
                **{"agy-sonnet": _agy_sonnet}, copilot=_copilot, goose=_goose, agy=_agy)

def needs_worktree(meta, queue, fallback_queue=None):
    return bool(meta.get("worktree") is True or
                any(name in NEED_WORKTREE for name in (queue or []) + (fallback_queue or [])))

def command(name, prompt):
    try:
        return ADAPTERS[name](prompt)
    except KeyError as e:
        raise ValueError(name) from e


def pick_queue(meta, cwd_rel, org, counts=None):
    """Chon executor theo ky_nang/chi dinh va gioi han muc du lieu; counts (recent_counts) -> xoay vong order_fair."""
    agents, policy = org["agents"], org["policy"]
    choice = meta.get("executor", "auto")
    fair = choice in (None, "auto")
    if choice not in (None, "auto"):
        if choice not in agents or choice not in ADAPTERS:
            raise ValueError(f"executor khong hop le: {choice}")
        if agents[choice].get("trang_thai") == "nghi":
            raise ValueError(f"executor da nghi viec: {choice} (doi trang_thai trong org/agents.yaml neu can)")
        queue = [choice]
    elif meta.get("ky_nang") is not None:
        fair = True
        skills = meta["ky_nang"]
        skills = [skills] if isinstance(skills, str) else skills
        if not isinstance(skills, list) or not skills:
            raise ValueError("ky_nang phai la chuoi hoac danh sach khong rong")
        queue = [i for i in org["order"] if set(skills) <= set(agents[i].get("ky_nang") or [])]
        if not queue:
            raise ValueError("khong co executor du ky_nang")
    else:
        queue = list(org["order"])
    data = policy.get("muc_du_lieu") or {}
    folders = data.get("thu_muc") or {}
    level = data.get("mac_dinh")
    for folder, value in folders.items():
        folder = str(folder).strip("/")
        if (cwd_rel == folder or cwd_rel.startswith(folder + "/")) and len(folder) > len(next((x for x in folders if (cwd_rel == x or cwd_rel.startswith(str(x).strip("/") + "/")) and len(str(x)) > len(folder)), "")):
            level = value
    levels = data.get("thu_tu") or []
    if level not in levels:
        raise ValueError(f"muc du lieu khong hop le: {level}")
    queue = [i for i in queue if agents[i].get("muc_du_lieu") in levels and levels.index(agents[i]["muc_du_lieu"]) >= levels.index(level)]
    if not queue:
        raise ValueError("khong executor nao du muc du lieu")
    if fair and counts is not None:
        queue = order_fair(queue, counts)
    return queue

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


def clean_env(env=None):
    """Return a copy of the environment without inherited MSYS variables."""
    result = dict(os.environ if env is None else env)
    blocked = {"MSYSTEM", "MSYSTEM_PREFIX", "MSYSTEM_CHOST", "MINGW_PREFIX", "MSYS", "CHERE_INVOKING"}
    for key in list(result):
        if key.upper() in blocked:
            result.pop(key, None)
    return result


def _watch_snapshot(watch_dir):
    ignored = {".git", "build", "managed_components", "node_modules", ".delegate-tmp"}
    snapshot = {}
    for current, dirs, files in os.walk(watch_dir):
        dirs[:] = [name for name in dirs if name.lower() not in ignored]
        for filename in files:
            path = os.path.join(current, filename)
            try:
                snapshot[path] = os.stat(path).st_mtime_ns
            except OSError:
                continue
    return snapshot


def _stop_process_tree(proc):
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            pass
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def run_proc_watch(argv, cwd, stdin, timeout_s, stall_s, watch_dir, env=None):
    """Run an executor while monitoring output and project-file progress."""
    start = time.monotonic()
    previous_files = _watch_snapshot(watch_dir)
    kwargs = {}
    if os.name != "nt":
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=clean_env(env), **kwargs)
    chunks = queue_module.Queue()

    def read_output():
        try:
            while True:
                data = os.read(proc.stdout.fileno(), 4096)
                if not data:
                    break
                chunks.put(data)
        except OSError:
            pass
        finally:
            chunks.put(None)

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    if stdin is not None:
        def write_input():
            try:
                proc.stdin.write(stdin.encode("utf-8") if isinstance(stdin, str) else stdin)
                proc.stdin.flush()
            except (BrokenPipeError, OSError):
                pass
            finally:
                try:
                    proc.stdin.close()
                except OSError:
                    pass
        threading.Thread(target=write_input, daemon=True).start()

    decoder = codecs.getincrementaldecoder("utf-8")("replace")
    output = []
    eof = False
    last_progress = start
    next_scan = start

    def consume(item):
        nonlocal eof, last_progress
        if item is None:
            eof = True
            tail = decoder.decode(b"", final=True)
            if tail:
                output.append(tail)
                last_progress = time.monotonic()
            return
        text = decoder.decode(item)
        if text:
            output.append(text)
            last_progress = time.monotonic()

    def drain_after_stop():
        deadline = time.monotonic() + 1.0
        while not eof and time.monotonic() < deadline:
            try:
                consume(chunks.get(timeout=min(0.1, deadline - time.monotonic())))
            except queue_module.Empty:
                if not reader.is_alive():
                    break

    while True:
        current = time.monotonic()
        timeout_left = timeout_s - (current - start)
        stall_left = stall_s - (current - last_progress)
        if timeout_left <= 0:
            _stop_process_tree(proc)
            drain_after_stop()
            return "".join(output) + f"\n[delegate] TIMEOUT {timeout_s} s", -1, round(time.monotonic() - start)
        if stall_left <= 0:
            _stop_process_tree(proc)
            drain_after_stop()
            return "".join(output) + f"\n[delegate] STALL {stall_s:g} s", -2, round(time.monotonic() - start)

        try:
            item = chunks.get(timeout=min(1.0, timeout_left, stall_left))
            consume(item)
        except queue_module.Empty:
            pass
        current = time.monotonic()
        if current >= next_scan:
            current_files = _watch_snapshot(watch_dir)
            if any(current_files.get(path, 0) > mtime for path, mtime in previous_files.items()) or \
                    any(path not in previous_files for path in current_files):
                last_progress = current
            previous_files = current_files
            next_scan = current + 1.0
        if proc.poll() is not None and eof:
            return "".join(output), proc.returncode, round(time.monotonic() - start)


def git_changed_rel(path, base=None):
    """Tap file thay doi/moi (git status, duong dan tuong doi `base`, dau '/')."""
    base = base or WS
    p = subprocess.run(["git", "status", "--porcelain", "-uall", "--", "."], cwd=path, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, capture_output=True,
                         text=True).stdout.strip()
    files = set()
    for line in p.stdout.splitlines():
        f = line[3:].split(" -> ")[-1].strip('"')
        files.add(os.path.relpath(os.path.join(top, f), base).replace("\\", "/"))
    return files


def git_changed(path):
    """Tap file thay doi/moi (git status, duong dan tuong doi WS, dau '/')."""
    return git_changed_rel(path, WS)


def file_sig(f):
    try:
        st = os.stat(os.path.join(WS, f))
        return (st.st_size, st.st_mtime_ns)
    except OSError:
        return None


def _sig_at(root, rel):
    try:
        st = os.stat(os.path.join(root, rel))
        return (st.st_size, st.st_mtime_ns)
    except OSError:
        return None


def _is_link(path):
    """Thu muc la junction/symlink -> KHONG di theo (tranh xoa/chép vao community goc)."""
    try:
        if os.path.islink(path):
            return True
        return bool(getattr(os.path, "isjunction", lambda p: False)(path))
    except OSError:
        return False


def _walk_files(root):
    """Duyet file trong root, bo qua .git va khong di vao junction/symlink."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [x for x in dirnames if x != ".git" and not _is_link(os.path.join(dirpath, x))]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def _snapshot(root):
    return {os.path.relpath(p, root).replace("\\", "/"): _sig_at(root, os.path.relpath(p, root))
            for p in _walk_files(root)}


_WT_INFO = {}


def _wt_key(path):
    return os.path.normcase(os.path.abspath(path))


def make_worktree(run_dir):
    """Tao git worktree rieng cho run; chep file chua commit, noi community/ bang junction, chep *.FCStd bi ignore.
    Tra ve thu muc tuong ung WS trong worktree (de chay executor/gate tai do)."""
    top = subprocess.run(["git", "-C", WS, "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True).stdout.strip()
    if not top:
        raise RuntimeError(f"khong tim thay git repo cho WS: {WS}")
    ws_rel = os.path.relpath(WS, top)
    name = os.path.basename(os.path.normpath(run_dir))
    wt_root = os.path.join(USAGE, "delegate-wt", name)
    os.makedirs(os.path.dirname(wt_root), exist_ok=True)
    subprocess.run(["git", "-C", WS, "worktree", "add", "--detach", wt_root, "HEAD"], check=True,
                   capture_output=True, text=True)

    # Chep moi file chua commit (sua + moi, khong bi ignore) cua CA repo, giu duong dan tuong doi top.
    st = subprocess.run(["git", "-C", top, "status", "--porcelain", "-uall"], capture_output=True,
                        text=True, encoding="utf-8", errors="replace")
    for line in st.stdout.splitlines():
        if len(line) < 4:
            continue
        f = line[3:].split(" -> ")[-1].strip('"')
        src = os.path.join(top, f)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(wt_root, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    wt_ws = os.path.normpath(os.path.join(wt_root, ws_rel))

    # community/ la nguon ghim chi doc: noi bang junction (khong chep, khong di theo khi xoa).
    junction = None
    comm_src = os.path.join(WS, "community")
    if os.path.isdir(comm_src):
        junction = os.path.join(wt_ws, "community")
        if os.path.isdir(junction) and not _is_link(junction):
            try:
                os.rmdir(junction)                       # chi xoa duoc neu rong
            except OSError:
                junction = None
        if junction and not os.path.exists(junction):
            os.makedirs(os.path.dirname(junction), exist_ok=True)
            subprocess.run(f'cmd /c mklink /J "{junction}" "{comm_src}"', shell=True,
                           capture_output=True, text=True)

    # File *.FCStd bi ignore nhung gate can doc -> chep vao worktree (giu duong dan).
    comm_prefix = os.path.normcase(os.path.join(WS, "community")) + os.sep
    for p in _walk_files(WS):
        if os.path.normcase(p).startswith(comm_prefix):     # community/ chi doc: khong chep qua junction
            continue
        if not fnmatch.fnmatch(os.path.basename(p), "*.FCStd"):
            continue
        rel = os.path.relpath(p, WS)
        dst = os.path.join(wt_ws, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(p, dst)

    _WT_INFO[_wt_key(wt_ws)] = dict(root=wt_root, junction=junction, baseline=_snapshot(wt_ws))
    return wt_ws


def sync_back(wt_ws, allow_ws):
    """Chep file thay doi/moi trong worktree (so voi luc tao) khop allow_ws ve WS. Tra (copied, skipped)."""
    info = _WT_INFO.get(_wt_key(wt_ws)) or {}
    base = info.get("baseline")
    copied, skipped = [], []
    for p in _walk_files(wt_ws):
        rel = os.path.relpath(p, wt_ws).replace("\\", "/")
        if base is not None and base.get(rel) == _sig_at(wt_ws, rel):
            continue                                    # khong doi so voi luc tao worktree
        if any(fnmatch.fnmatch(rel, pat) for pat in allow_ws if isinstance(pat, str)):
            dst = os.path.join(WS, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(p, dst)
            copied.append(rel)
        else:
            skipped.append(rel)
    return copied, skipped


def remove_worktree(wt_ws):
    """Go junction bang os.rmdir TRUOC (khong theo link vao community goc), roi go git worktree."""
    key = _wt_key(wt_ws)
    info = _WT_INFO.pop(key, {})
    wt_root = info.get("root")
    if not wt_root:
        wt_root = subprocess.run(["git", "-C", wt_ws, "rev-parse", "--show-toplevel"], capture_output=True,
                                 text=True).stdout.strip() or os.path.dirname(wt_ws)
    junction = info.get("junction") or os.path.join(wt_ws, "community")
    if os.path.isdir(junction) and _is_link(junction):
        try:
            os.rmdir(junction)
        except OSError:
            pass
    subprocess.run(["git", "-C", WS, "worktree", "remove", "--force", wt_root], capture_output=True, text=True)
    subprocess.run(["git", "-C", WS, "worktree", "prune"], capture_output=True, text=True)
    if os.path.exists(wt_root):
        for dirpath, dirnames, _ in os.walk(wt_root):   # con lai: go moi junction roi moi xoa
            for x in list(dirnames):
                j = os.path.join(dirpath, x)
                if _is_link(j):
                    try:
                        os.rmdir(j)
                    except OSError:
                        pass
        shutil.rmtree(wt_root, ignore_errors=True)
        subprocess.run(["git", "-C", WS, "worktree", "prune"], capture_output=True, text=True)


TEXT_EXT = (".py", ".md", ".html", ".css", ".js", ".json", ".yaml", ".yml", ".txt", ".csv", ".c", ".h", ".cpp", ".ino")


def mojibake(path, min_hits=3):
    """File text khong doc duoc UTF-8, hoac >= min_hits cho chu cai bi thay bang dau hoi (vd 'Kiem' thanh 'Ki' + '?' + 'm')."""
    if not path.lower().endswith(TEXT_EXT) or not os.path.isfile(path):
        return False
    try:
        text = open(path, "rb").read().decode("utf-8")
    except UnicodeDecodeError:
        return True
    text = re.sub(r"https?://\S+", "", text)            # bo URL (view.php?id=...) khoi dem
    return len(re.findall(r"[^\W\d_]\?[^\W\d_]", text)) >= min_hits


def tail(text, n=40):
    return "\n".join(text.strip().splitlines()[-n:])


def main():
    sys.stdout.reconfigure(encoding="utf-8")            # pipe tren Windows mac dinh cp1252 -> loi khi in tieng Viet
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--executor", help="auto|codex|opencode|kilo|agy-sonnet|copilot|goose|agy")
    ap.add_argument("--simulate-limit", default="", help="danh sach executor gia lap het han muc (thu nghiem)")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--stats", action="store_true", help="in thanh tich tung executor (JSON)")
    ap.add_argument("--rebuild", action="store_true", help="tinh lai thanh tich tu lich su run (dung voi --stats)")
    ap.add_argument("--clear-limit")
    ap.add_argument("--resume", metavar="RUN", help="chay lai run bi cat ngang (ten hoac duong dan run_dir)")
    ap.add_argument("--mark-limit", nargs=2, metavar=("EXECUTOR", "UNTIL"),
                    help="danh dau het han muc toi thoi diem ISO, vd: agy 2026-11-02T12:00")
    a = ap.parse_args()

    if a.stats or a.rebuild:
        stats = load_stats()
        if a.rebuild or not stats:                      # chua co so lieu thi dung lai tu lich su run
            stats = rebuild_stats()
        out = {}
        for name, s in stats.items():
            row = {k: s.get(k, 0) for k in STAT_FIELDS}
            row["pass_rate"] = row["gate_pass"] / row["rounds"] if row["rounds"] else 0
            out[name] = row
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    if a.status or a.clear_limit or a.mark_limit:
        if a.mark_limit:
            until = dt.datetime.fromisoformat(a.mark_limit[1]).astimezone()
            mark_limited(a.mark_limit[0], "danh dau tay", until)
        lim = load_limits()
        if a.clear_limit:
            lim.pop(a.clear_limit, None)
            save_limits(lim)
        # chi executor co adapter (agent Claude/tu van khong goi qua delegate)
        ids = dict.fromkeys(ORDER + [n for n in ORG["agents"] if n in ADAPTERS])
        st = {n: dict(installed=installed(n), limited=is_limited(n, lim), **lim.get(n, {})) for n in ids}
        st["runs_without_result"] = run_states()
        st["recent_7d"] = recent_counts()
        print(json.dumps(st, ensure_ascii=False))
        return
    resume_from, resume_ctx = None, ""
    if a.resume:
        try:
            a.spec, resume_ctx = build_resume(a.resume)
        except ValueError as e:
            print(f"LOI: {e}", file=sys.stderr)
            sys.exit(1)
        resume_from = os.path.basename(os.path.normpath(a.resume.rstrip("/\\")))
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
    allow_ws = [(cwd_rel + "/" + p).replace("\\", "/") if cwd_rel else p.replace("\\", "/") for p in allow]

    choice = a.executor or meta["executor"]
    simulated = {x for x in a.simulate_limit.split(",") if x}
    meta["executor"] = choice
    try:
        queue = pick_queue(meta, cwd_rel, ORG, recent_counts())
        fallback_meta = dict(meta, executor="auto")
        try:
            fallback_queue = pick_queue(fallback_meta, cwd_rel, ORG, recent_counts())
        except ValueError:
            fallback_queue = []
    except ValueError as e:
        print(f"LOI: {e}", file=sys.stderr)
        sys.exit(1)
    def execute_executor(argv, work, stdin, timeout_s, stall_s, watch_dir, env=None):
        return run_proc_watch(argv, work, stdin, timeout_s, stall_s, watch_dir, env=clean_env(env))
    if str(meta.get("uu_tien") or "") == "thanh-tich":
        queue = rank_by_stats(queue, load_stats())      # mac dinh giu chuoi trong so nhan su

    run_dir = os.path.join(USAGE, "delegate-runs", now().strftime("%Y%m%d-%H%M%S") + "-" + meta["task"])
    os.makedirs(run_dir, exist_ok=True)
    lock = take_lock(cwd_rel, meta["task"], run_dir, allow_ws=allow_ws)
    json.dump(dict(state="running", pid=os.getpid(), spec=os.path.abspath(a.spec)),
              open(os.path.join(run_dir, "state.json"), "w", encoding="utf-8"), ensure_ascii=False)
    try:
        run_task(a, meta, body, cwd, cwd_rel, allow, queue, simulated, run_dir,
                 resumed_from=resume_from, resume_ctx=resume_ctx, allow_ws=allow_ws,
                 fallback_queue=fallback_queue, executor_runner=execute_executor)
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


def run_task(a, meta, body, cwd, cwd_rel, allow, queue, simulated, run_dir, resumed_from=None, resume_ctx="",
             allow_ws=None, fallback_queue=None, executor_runner=None):
    allow_ws = allow_ws if allow_ws is not None else \
        [(cwd_rel + "/" + p).replace("\\", "/") if cwd_rel else p.replace("\\", "/") for p in allow]
    use_wt = needs_worktree(meta, queue, fallback_queue)
    wt_ws = make_worktree(run_dir) if use_wt else None      # worktree rieng: executor/gate chay trong ban sao
    work = os.path.join(wt_ws, cwd_rel) if use_wt else cwd
    root = wt_ws if use_wt else WS
    try:
        # Thu muc tam rieng trong cwd: sandbox Codex chi cho ghi trong cwd -> test dung tempfile/LOCALAPPDATA khong bi chan
        # (ESCALATE 2 lan 2026-10-27). Git bo qua (.gitignore), xoa khi xong.
        tmpdir = os.path.join(work, ".delegate-tmp")
        os.makedirs(tmpdir, exist_ok=True)
        env = clean_env(dict(os.environ, OPENCODE_CONFIG=os.path.join(HERE, "opencode.json"), KILO_CONFIG=os.path.join(HERE, "kilo.json"), TMP=tmpdir, TEMP=tmpdir, TMPDIR=tmpdir,
                             PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))
        before = {f: _sig_at(root, f) for f in git_changed_rel(work, root)}
        result = dict(task=meta["task"], cwd=cwd_rel, run_dir=run_dir, rounds=[], skipped=[], passed=False)
        started_at = time.time()
        first_executor = queue[0] if queue else "executor"
        _event_emit("delegate", "run_start", f"{first_executor} nhan {meta['task']}", agent=first_executor, ref=run_dir)
        if resumed_from:
            result["resumed_from"] = resumed_from
        extra = [os.path.join(WS, p) for p in meta["read"]]
        read = (" and these READ-ONLY paths: " + ", ".join(extra)) if extra else ""
        prompt = RULES.format(allow=", ".join(allow), gate=meta["gate"], task=meta["task"], body=body, read=read)
        if resume_ctx:
            prompt += "\n\n" + resume_ctx

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
            runner = executor_runner or run_proc_watch
            out, code, secs = runner(argv, work, stdin, int(meta["timeout_min"]) * 60,
                                     STALL_MIN * 60, work, env=clean_env(env))
            open(os.path.join(run_dir, f"{name}-{rnd}.log"), "w", encoding="utf-8").write(out)
            lines = [x.strip() for x in ANSI_RE.sub("", out).splitlines() if x.strip()]
            last = next((x for x in reversed(lines) if re.match(r"`?(DONE|BLOCKED|ESCALATE)", x)),
                        (lines or [""])[-1])[:200]
            r = dict(round=rnd, executor=name, exit=code, seconds=secs, last_line=last)
            if code == -2:
                mark_limited(name, f"stall {STALL_MIN:g} phut", until=now() + dt.timedelta(minutes=30))
                r["stalled"] = True
                result["rounds"].append(r)
                _event_emit("delegate", "round", f"round {rnd} STALL", agent=name, ref=run_dir,
                            data={"round": rnd, "verdict": "STALL"})
                rnd -= 1
                if name in ORG["order"]:
                    index = ORG["order"].index(name)
                    queue = [candidate for candidate in ORG["order"][index + 1:]
                             if candidate in (fallback_queue or [])]
                else:
                    queue = []
                continue
            if re.match(r"`?ESCALATE", last):
                # Bao len tren: executor thieu quyen/ngoai viec -> dung han, KHONG giao lai, Claude quyet (org/policy.yaml)
                result["rounds"].append(r)
                result["escalate"] = last.split(":", 1)[-1].strip(" `")
                _event_emit("delegate", "round", f"round {rnd} ESCALATE", agent=name, ref=run_dir,
                            data={"round": rnd, "verdict": "ESCALATE"})
                break
            if code != 0 and LIMIT_RE.search(out[-4000:]):
                mark_limited(name, tail(out, 3))
                r["limited"] = True
                result["rounds"].append(r)
                rnd -= 1                                    # vong nay khong tinh, chuyen executor ke tiep
                continue
            gout, gcode, gsecs = run_proc(meta["gate"], work, None, 20 * 60, env=clean_env(env), shell=True)
            open(os.path.join(run_dir, f"gate-{rnd}.log"), "w", encoding="utf-8").write(gout)
            r.update(gate_exit=gcode, gate_seconds=gsecs, gate_tail=tail(gout, 5))
            result["rounds"].append(r)
            _event_emit("delegate", "round", f"round {rnd} {'PASS' if gcode == 0 else 'FAIL'}", agent=name,
                        ref=run_dir, data={"round": rnd, "verdict": "PASS" if gcode == 0 else "FAIL", "gate_exit": gcode})
            bad = [f for f in git_changed_rel(work, root)
                   if before.get(f, "new") != _sig_at(root, f) and mojibake(os.path.join(root, f))]
            if gcode == 0 and not bad:
                result["passed"] = True
                break
            if bad:                                         # gate dat nhung file hong ma hoa -> giao lai kem nhac
                r["encoding_broken"] = bad
                gout = (f"ENCODING BROKEN in {bad}: Vietnamese letters became '?'. Rewrite these files with your "
                        "file-editing tool only (apply_patch), never through a PowerShell pipe/Set-Content.\n" + gout)
            prompt += RETRY.format(n=rnd + 1, tail=tail(gout))

        # Kiem file thay doi: cam + ngoai allow (so voi truoc khi chay)
        shutil.rmtree(tmpdir, ignore_errors=True)
        after = git_changed_rel(work, root)
        touched = sorted(f for f in after if before.get(f, "new") != _sig_at(root, f))
        def rel(f):
            return os.path.relpath(os.path.join(root, f), work).replace("\\", "/")

        forbidden = [f for f in touched if any(fnmatch.fnmatch(f, p) or fnmatch.fnmatch(os.path.basename(f), p)
                                               for p in FORBIDDEN)]
        claimed = other_runs_claim(touched, run_dir)        # file run KHAC con song dang so huu (khoa allow)
        outside = [f for f in touched if f not in forbidden and f not in claimed and
                   (rel(f).startswith("..") or not any(fnmatch.fnmatch(rel(f), p) for p in allow))]
        result.update(changed=touched, forbidden_touched=forbidden, outside_allow=outside, other_runs=claimed)
        broken = [f for f in touched if mojibake(os.path.join(root, f))]
        if broken:
            # Loi ma hoa (3 lan 2026-10-27: Codex ghi file ANSI, chu tieng Viet thanh '?') -> khong nhan ket qua
            result["passed"] = False
            result["encoding_broken"] = broken
            result["error"] = "file bi loi ma hoa (chu thanh '?' hoac khong phai UTF-8) – giao lai, nhac ghi UTF-8"
        if forbidden:
            result["passed"] = False
            result["error"] = "executor dong vao file cam – Claude kiem tay, KHONG commit"
        if wt_ws and result["passed"]:                      # PASS: chep file allow tu worktree ve WS (khong git commit)
            copied, not_synced = sync_back(wt_ws, allow_ws)
            result["synced"] = copied
            result["not_synced"] = not_synced
        result["verdict"] = ("ESCALATE" if result.get("escalate") and not forbidden else
                             "PASS" if result["passed"] and not outside else "WARN" if result["passed"] else "FAIL")
        if result["verdict"] != "PASS":
            result["handoff"] = write_handoff(run_dir, result)
        if result["verdict"] == "ESCALATE" and _events:
            try:
                _events.add_approval(f"{result['rounds'][-1].get('executor', 'executor')}: {result.get('escalate', '')}",
                                     source="delegate", ref=os.path.basename(os.path.normpath(run_dir)))
            except Exception:
                pass
        _event_emit("delegate", "run_end", f"{meta['task']} {result['verdict']}", ref=run_dir,
                    data={"verdict": result["verdict"], "rounds": len(result["rounds"]), "seconds": round(time.time() - started_at)})
        update_stats(result)                                # ghi thanh tich truoc khi chot result.json
        json.dump(result, open(os.path.join(run_dir, "result.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit({"FAIL": 1, "ESCALATE": 2}.get(result["verdict"], 0))
    finally:
        if wt_ws:
            remove_worktree(wt_ws)


if __name__ == "__main__":
    main()
