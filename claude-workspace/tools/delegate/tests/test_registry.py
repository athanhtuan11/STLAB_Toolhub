# Gate buoc 2 so nhan su: delegate.py doc org/agents.yaml + org/policy.yaml thay hang so cung (Claude viet, KHONG sua).
#   python tests/test_registry.py      (chay tu tools/delegate)
import copy, importlib.util, os, shutil, sys, tempfile
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "delegate.py")
WS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ORG = os.path.join(WS, "org")
spec = importlib.util.spec_from_file_location("delegate", SRC)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

# 1) So that -> gia tri module (check_org.py van dung ORDER/COOLDOWN_H/FORBIDDEN)
org = d.load_org()
assert org["order"] == ["codex", "opencode", "kilo", "agy-sonnet", "copilot", "agy"], org["order"]
assert d.ORDER == org["order"] and d.COOLDOWN_H == {"codex": 5, "opencode": 1, "kilo": 1, "agy-sonnet": 24, "copilot": 24, "agy": 24}, (d.ORDER, d.COOLDOWN_H)
assert org["model"]["opencode"] == "opencode/deepseek-v4.1-flash-free" and org["model"]["agy"] == "gemini-3.8-flash-high"
pol = yaml.safe_load(open(os.path.join(ORG, "policy.yaml"), encoding="utf-8"))
assert set(pol["duong_cam"]) <= set(d.FORBIDDEN), "FORBIDDEN phai lay tu policy.duong_cam"
src = open(SRC, encoding="utf-8").read()
for hard in ('ORDER = ["codex"', '"opencode": 1, "agy": 24', 'OPENCODE_MODEL = "opencode/'):
    assert hard not in src, f"con hang so cung trong delegate.py: {hard}"
assert {"codex", "opencode", "kilo", "agy-sonnet", "copilot", "agy"} <= set(d.ADAPTERS), "ADAPTERS phai co moi executor"
assert d.pick_queue(dict(executor="kilo"), "tools/x", org) == ["kilo"]
argv, stdin = d.command("kilo", "P")
assert argv[1:4] == ["run", "--model", "kilo/kilo-auto/free"] and stdin == "P", argv
argv, _ = d.command("agy-sonnet", "P")
assert "claude-sonnet-4-6" in argv and "--sandbox" in argv, argv
assert argv[2].startswith("P") and "delegate.py runs the gate" in argv[2], argv[2]
argv, stdin = d.command("copilot", "P")
# prompt qua stdin: argv cua copilot.cmd di qua cmd.exe lam vo & | % " (thu 2026-10-28)
assert stdin == "P" and "P" not in argv and "-p" not in argv, argv
assert "--sandbox" in argv and "--deny-tool=shell(git push)" in argv, argv
assert "--model" not in argv and "--allow-all-paths" not in argv, argv


TMP_ROOT = tempfile.mkdtemp(prefix="delegate-registry-test-")   # don cuoi file; sandbox co the dat TEMP trong cwd


def tmp_org(mutate=None, mpol=None):
    t = tempfile.mkdtemp(prefix="org-", dir=TMP_ROOT)
    a = yaml.safe_load(open(os.path.join(ORG, "agents.yaml"), encoding="utf-8"))
    p = copy.deepcopy(pol)
    if mutate:
        mutate(a)
    if mpol:
        mpol(p)
    yaml.safe_dump(a, open(os.path.join(t, "agents.yaml"), "w", encoding="utf-8"), allow_unicode=True)
    yaml.safe_dump(p, open(os.path.join(t, "policy.yaml"), "w", encoding="utf-8"), allow_unicode=True)
    return t


def ag(a, i):
    return next(x for x in a["agents"] if x["id"] == i)


def must_fail(fn, why):
    try:
        fn()
    except (ValueError, SystemExit):
        return
    raise AssertionError(f"phai loi: {why}")


# 2) Nghi viec -> bo khoi chuoi, noi tiep theo khi_het_han_muc cua nguoi nghi
o = d.load_org(tmp_org(lambda a: ag(a, "opencode").__setitem__("trang_thai", "nghi")))
assert o["order"] == ["codex", "kilo", "agy-sonnet", "copilot", "agy"], o["order"]
must_fail(lambda: d.pick_queue(dict(executor="opencode"), "tools/x", o), "nghi viec ma goi dich danh van chay")

# 3) pick_queue theo ky_nang / executor / muc du lieu / thu viec
assert d.pick_queue(dict(ky_nang="bao-cao"), "docs/reports", org) == ["codex"]
# agy chi giu doc-ma tu 2026-10-27 (han muc tuan dung chung voi ask-gemini/doc-writer) -> khong vao viec code/CAD
assert d.pick_queue(dict(ky_nang="cad-script"), "tools/x", org) == ["codex", "opencode", "kilo", "agy-sonnet"]
assert d.pick_queue(dict(ky_nang=["code", "cad-script"]), "tools/x", org) == ["codex", "opencode", "kilo", "agy-sonnet"]
assert d.pick_queue(dict(ky_nang="doc-ma"), "tools/x", org) == ["codex", "agy-sonnet", "copilot", "agy"]
assert d.pick_queue(dict(executor="auto"), "tools/x", org) == ["codex", "opencode", "kilo", "agy-sonnet", "copilot", "agy"]
assert d.pick_queue(dict(executor="opencode"), "tools/x", org) == ["opencode"]
must_fail(lambda: d.pick_queue(dict(ky_nang="hat-karaoke"), "tools/x", org), "khong ai co ky nang")
must_fail(lambda: d.pick_queue(dict(executor="kimi"), "tools/x", org), "executor khong co trong so")
assert d.pick_queue(dict(executor="auto"), "maker/pump-control/firmware", org) == ["codex", "opencode", "kilo", "agy-sonnet", "copilot", "agy"], \
    "du an trong maker/ la viec binh thuong (Tuan 2026-10-27)"
must_fail(lambda: d.pick_queue(dict(executor="auto"), "stlab/parent-reports", org), "bao cao phu huynh")


def add_trial(a):
    x = copy.deepcopy(ag(a, "opencode"))
    x.update(id="kimi", trang_thai="thu-viec", khi_het_han_muc=None)
    a["agents"].append(x)


must_fail(lambda: d.load_org(tmp_org(add_trial)), "thu-viec khong co ADAPTER -> loi ro rang")

# 4) Executor chinh-thuc khong co adapter -> load_org bao loi (khong im lang)
must_fail(lambda: d.load_org(tmp_org(lambda a: (add_trial(a), ag(a, "kimi").__setitem__("trang_thai", "chinh-thuc"),
                                                ag(a, "agy").__setitem__("khi_het_han_muc", "kimi")))),
          "chinh-thuc ma khong co ADAPTER")
# 5) So hong -> loi ro rang, khong dung mac dinh ngam
must_fail(lambda: d.load_org(tempfile.mkdtemp(dir=TMP_ROOT)), "thieu agents.yaml")
shutil.rmtree(TMP_ROOT, ignore_errors=True)
print("gate OK")
