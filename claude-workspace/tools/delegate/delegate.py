# Giao viec code/script cho executor free (Codex -> OpenCode -> Kilo -> agy-sonnet -> Copilot -> agy) theo spec.md Claude viet, tu chay gate.
# Claude chi doc dong JSON cuoi (result.json); log dai nam trong thu muc run.
#   python tools/delegate/delegate.py <spec.md> [--executor auto|codex|opencode|kilo|agy-sonnet|copilot|agy] [--simulate-limit codex]
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
import argparse, datetime as dt, fnmatch, json, os, re, shutil, subprocess, sys, time
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
ADAPTERS = {"codex": "codex", "opencode": "opencode", "kilo": "kilo", "agy-sonnet": "agy-sonnet", "copilot": "copilot", "agy": "agy"}
STAT_FIELDS = ("rounds", "gate_pass", "pass_round1", "limited", "escalate", "seconds")

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
ORDER, COOLDOWN_H, FORBIDDEN = ORG["order"], ORG["cooldown"], ORG["forbidden"]
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
    until = until or reset_from_reason(reason) or now() + dt.timedelta(hours=COOLDOWN_H[name])
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


def tally(stats, result):
    """Cong don 1 run vao stats (dung chung cho update_stats va rebuild_stats)."""
    rounds = result.get("rounds") or []
    for i, r in enumerate(rounds):
        name = r.get("executor")
        if not name:
            continue
        s = stats.setdefault(name, new_stats())
        if r.get("limited"):
            s["limited"] += 1
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

def _agy_named(name, prompt):
    return [shutil.which("agy"), "-p", prompt, "--model", ORG["model"][name],
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

ADAPTERS.update(codex=_codex, opencode=_opencode, kilo=_kilo,
                **{"agy-sonnet": _agy_sonnet}, copilot=_copilot, agy=_agy)

def command(name, prompt):
    try:
        return ADAPTERS[name](prompt)
    except KeyError as e:
        raise ValueError(name) from e


def pick_queue(meta, cwd_rel, org):
    """Chon executor theo ky_nang/chi dinh va gioi han muc du lieu."""
    agents, policy = org["agents"], org["policy"]
    choice = meta.get("executor", "auto")
    if choice not in (None, "auto"):
        if choice not in agents or choice not in ADAPTERS:
            raise ValueError(f"executor khong hop le: {choice}")
        if agents[choice].get("trang_thai") == "nghi":
            raise ValueError(f"executor da nghi viec: {choice} (doi trang_thai trong org/agents.yaml neu can)")
        queue = [choice]
    elif meta.get("ky_nang") is not None:
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
    ap.add_argument("--executor", help="auto|codex|opencode|kilo|agy-sonnet|copilot|agy")
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

    choice = a.executor or meta["executor"]
    simulated = {x for x in a.simulate_limit.split(",") if x}
    meta["executor"] = choice
    try:
        queue = pick_queue(meta, cwd_rel, ORG)
    except ValueError as e:
        print(f"LOI: {e}", file=sys.stderr)
        sys.exit(1)
    if str(meta.get("uu_tien") or "") == "thanh-tich":
        queue = rank_by_stats(queue, load_stats())      # mac dinh giu chuoi trong so nhan su

    run_dir = os.path.join(USAGE, "delegate-runs", now().strftime("%Y%m%d-%H%M%S") + "-" + meta["task"])
    os.makedirs(run_dir, exist_ok=True)
    lock = take_lock(cwd_rel, meta["task"], run_dir)
    json.dump(dict(state="running", pid=os.getpid(), spec=os.path.abspath(a.spec)),
              open(os.path.join(run_dir, "state.json"), "w", encoding="utf-8"), ensure_ascii=False)
    try:
        run_task(a, meta, body, cwd, cwd_rel, allow, queue, simulated, run_dir,
                 resumed_from=resume_from, resume_ctx=resume_ctx)
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


def run_task(a, meta, body, cwd, cwd_rel, allow, queue, simulated, run_dir, resumed_from=None, resume_ctx=""):
    # Thu muc tam rieng trong cwd: sandbox Codex chi cho ghi trong cwd -> test dung tempfile/LOCALAPPDATA khong bi chan
    # (ESCALATE 2 lan 2026-10-27). Git bo qua (.gitignore), xoa khi xong.
    tmpdir = os.path.join(cwd, ".delegate-tmp")
    os.makedirs(tmpdir, exist_ok=True)
    env = dict(os.environ, OPENCODE_CONFIG=os.path.join(HERE, "opencode.json"), KILO_CONFIG=os.path.join(HERE, "kilo.json"), TMP=tmpdir, TEMP=tmpdir, TMPDIR=tmpdir,
               PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    before = {f: file_sig(f) for f in git_changed(cwd)}
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
        out, code, secs = run_proc(argv, cwd, stdin, int(meta["timeout_min"]) * 60, env)
        open(os.path.join(run_dir, f"{name}-{rnd}.log"), "w", encoding="utf-8").write(out)
        lines = [x.strip() for x in ANSI_RE.sub("", out).splitlines() if x.strip()]
        last = next((x for x in reversed(lines) if re.match(r"`?(DONE|BLOCKED|ESCALATE)", x)),
                    (lines or [""])[-1])[:200]
        r = dict(round=rnd, executor=name, exit=code, seconds=secs, last_line=last)
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
        gout, gcode, gsecs = run_proc(meta["gate"], cwd, None, 20 * 60, shell=True)
        open(os.path.join(run_dir, f"gate-{rnd}.log"), "w", encoding="utf-8").write(gout)
        r.update(gate_exit=gcode, gate_seconds=gsecs, gate_tail=tail(gout, 5))
        result["rounds"].append(r)
        _event_emit("delegate", "round", f"round {rnd} {'PASS' if gcode == 0 else 'FAIL'}", agent=name,
                    ref=run_dir, data={"round": rnd, "verdict": "PASS" if gcode == 0 else "FAIL", "gate_exit": gcode})
        bad = [f for f in git_changed(cwd) if before.get(f, "new") != file_sig(f) and mojibake(os.path.join(WS, f))]
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
    after = git_changed(cwd)
    touched = sorted(f for f in after if before.get(f, "new") != file_sig(f))
    def rel(f):
        return os.path.relpath(os.path.join(WS, f), cwd).replace("\\", "/")

    forbidden = [f for f in touched if any(fnmatch.fnmatch(f, p) or fnmatch.fnmatch(os.path.basename(f), p)
                                           for p in FORBIDDEN)]
    outside = [f for f in touched if f not in forbidden and
               (rel(f).startswith("..") or not any(fnmatch.fnmatch(rel(f), p) for p in allow))]
    result.update(changed=touched, forbidden_touched=forbidden, outside_allow=outside)
    broken = [f for f in touched if mojibake(os.path.join(WS, f))]
    if broken:
        # Loi ma hoa (3 lan 2026-10-27: Codex ghi file ANSI, chu tieng Viet thanh '?') -> khong nhan ket qua
        result["passed"] = False
        result["encoding_broken"] = broken
        result["error"] = "file bi loi ma hoa (chu thanh '?' hoac khong phai UTF-8) – giao lai, nhac ghi UTF-8"
    if forbidden:
        result["passed"] = False
        result["error"] = "executor dong vao file cam – Claude kiem tay, KHONG commit"
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


if __name__ == "__main__":
    main()
