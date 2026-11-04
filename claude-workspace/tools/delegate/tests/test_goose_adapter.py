# Gate adapter Goose (Claude viet 2026-11-04, KHONG sua).   python tests/test_goose_adapter.py  (chay tu tools/delegate)
import importlib.util, os, sys, tempfile
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "delegate.py")
WS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
spec = importlib.util.spec_from_file_location("delegate", SRC)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

fails = []
def check(ok, msg):
    if not ok:
        fails.append(msg)

# 1) Adapter co trong ADAPTERS, prompt qua stdin, model lay tu org (khong hang so cung)
check("goose" in d.ADAPTERS, "ADAPTERS thieu 'goose'")
if "goose" in d.ADAPTERS:
    argv, stdin = d.command("goose", "PROMPT-X")
    check(stdin == "PROMPT-X", f"prompt phai qua stdin, nhan stdin={stdin!r}")
    check("PROMPT-X" not in " ".join(str(x) for x in argv), "prompt khong duoc nam trong argv")
    check(bool(argv) and str(argv[0]).lower().replace("\\", "/").split("/")[-1] in ("goose", "goose.exe"),
          f"argv[0] phai la goose(.exe), nhan {argv[:1]}")
    check(argv[1:2] == ["run"], f"argv[1] phai la 'run': {argv}")
    for flag in ("--no-session",):
        check(flag in argv, f"thieu {flag}: {argv}")
    check("-i" in argv and argv[argv.index("-i") + 1] == "-", f"phai co '-i -' (doc stdin): {argv}")
    check("--provider" in argv and argv[argv.index("--provider") + 1] == "google", f"--provider google: {argv}")
    check("--model" in argv and argv[argv.index("--model") + 1] == d.ORG["model"]["goose"],
          f"--model phai la ORG['model']['goose']={d.ORG['model'].get('goose')}: {argv}")
    check("-s" not in argv and "--interactive" not in argv, "khong duoc chay che do tuong tac")
src = open(SRC, encoding="utf-8").read()
check('"gemini-3.5-flash"' not in src, "model goose phai doc tu org/agents.yaml, khong hang so cung")

# 2) Goose khong gioi han thu muc -> bat buoc worktree
check("goose" in getattr(d, "NEED_WORKTREE", ()), "thieu NEED_WORKTREE chua 'goose'")
nw = getattr(d, "needs_worktree", None)
check(callable(nw), "thieu ham needs_worktree(meta, queue, fallback_queue=None)")
if callable(nw):
    check(nw({"worktree": False}, ["codex", "kilo"]) is False, "khong co goose, worktree=False -> False")
    check(nw({"worktree": True}, ["codex"]) is True, "spec worktree=True -> True")
    check(nw({"worktree": False}, ["goose"]) is True, "queue co goose -> True")
    check(nw({"worktree": False}, ["codex"], ["kilo", "goose"]) is True, "fallback co goose -> True")
    check(nw({}, ["codex"], None) is False, "meta rong -> False")
check("needs_worktree(" in src.split("def run_task", 1)[-1], "run_task phai dung needs_worktree(...) de quyet use_wt")

# 3) Org: goose thu-viec -> nap duoc, KHONG vao chuoi tu dong; chinh-thuc -> sau copilot, truoc agy
doc = yaml.safe_load(open(os.path.join(WS, "org", "agents.yaml"), encoding="utf-8"))
g = next((a for a in doc["agents"] if a.get("id") == "goose"), None)
check(g is not None, "org/agents.yaml thieu goose")
if g is not None and "goose" in d.ADAPTERS:
    tmp = tempfile.mkdtemp(prefix="goose-gate-")
    import shutil
    shutil.copy(os.path.join(WS, "org", "policy.yaml"), os.path.join(tmp, "policy.yaml"))
    def org_with(state):
        g["trang_thai"] = state
        with open(os.path.join(tmp, "agents.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
        return d.load_org(tmp)
    try:
        o = org_with("thu-viec")
        check("goose" not in o["order"], f"thu-viec khong vao chuoi tu dong: {o['order']}")
        check(d.pick_queue(dict(executor="goose"), "tools/x", o) == ["goose"], "goi dich danh goose phai duoc")
        o = org_with("chinh-thuc")
        check(o["order"][-2:] == ["goose", "agy"] and o["order"].index("copilot") < o["order"].index("goose"),
              f"chinh-thuc: ... copilot -> goose -> agy, nhan {o['order']}")
    except Exception as e:  # noqa: BLE001
        fails.append(f"load_org loi: {e!r}")

if fails:
    print("FAIL test_goose_adapter:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_goose_adapter")
