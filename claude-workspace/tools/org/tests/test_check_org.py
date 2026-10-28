# Gate cho check_org.py (Claude viet, executor KHONG sua file nay).
#   python tests/test_check_org.py      (chay tu tools/org)
import copy, os, shutil, subprocess, sys, tempfile
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "check_org.py")
WS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ORG = os.path.join(WS, "org")


def run(org_dir):
    r = subprocess.run([sys.executable, TOOL, "--org", org_dir], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


# 1) So that phai PASS
code, out = run(ORG)
print(out[-1500:])
assert code == 0, "so nhan su that phai PASS"

base = yaml.safe_load(open(os.path.join(ORG, "agents.yaml"), encoding="utf-8"))
pol = open(os.path.join(ORG, "policy.yaml"), encoding="utf-8").read()


def by_id(doc, i):
    return next(a for a in doc["agents"] if a["id"] == i)


def bad(name, mutate, want, policy=None):
    tmp = tempfile.mkdtemp(prefix="org-")
    doc = copy.deepcopy(base)
    mutate(doc)
    yaml.safe_dump(doc, open(os.path.join(tmp, "agents.yaml"), "w", encoding="utf-8"), allow_unicode=True)
    open(os.path.join(tmp, "policy.yaml"), "w", encoding="utf-8").write(policy or pol)
    code, out = run(tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    assert code != 0, f"[{name}] phai FAIL nhung exit 0"
    assert want in out, f"[{name}] thong bao phai chua '{want}', co:\n{out[-600:]}"
    print("FAIL dung:", name)


# 2) Moi luat phai bat duoc loi; thong bao chua ma loi (want)
bad("trung id", lambda d: d["agents"].append(copy.deepcopy(by_id(d, "codex"))), "E-ID-TRUNG")
bad("thieu truong", lambda d: by_id(d, "opencode").pop("ky_nang"), "E-THIEU-TRUONG")
bad("enum sai", lambda d: by_id(d, "opencode").__setitem__("loai", "robot"), "E-ENUM")
bad("bao cao cho khong ton tai", lambda d: by_id(d, "codex").__setitem__("bao_cao_cho", "ai-do"), "E-BAO-CAO")
bad("bao cao cho cap duoi", lambda d: by_id(d, "check-runner").__setitem__("bao_cao_cho", "codex"), "E-CAP")
bad("tra phi", lambda d: by_id(d, "codex").__setitem__("chi_phi", "tra-phi"), "E-TRA-PHI")
bad("tu duyet", lambda d: by_id(d, "opencode").__setitem__("nguoi_duyet", "opencode"), "E-TU-DUYET")
bad("ncc ngoai xem du lieu khach", lambda d: by_id(d, "agy").__setitem__("muc_du_lieu", "customer"), "E-DU-LIEU")
bad("subagent lech model", lambda d: by_id(d, "git-scribe").__setitem__("model", "sonnet"), "E-SUBAGENT")
bad("subagent lech tool", lambda d: by_id(d, "check-runner").__setitem__("tool", ["Bash"]), "E-SUBAGENT")
bad("subagent khong co file", lambda d: d["agents"].append(dict(copy.deepcopy(by_id(d, "git-scribe")), id="ma-agent")),
    "E-SUBAGENT")
bad("executor lech cooldown", lambda d: by_id(d, "opencode").__setitem__("cooldown_h", 9), "E-DELEGATE")
bad("executor khong co trong delegate", lambda d: d["agents"].append(dict(copy.deepcopy(by_id(d, "opencode")),
                                                                            id="kimi")), "E-DELEGATE")
bad("chuoi het han muc sai", lambda d: by_id(d, "codex").__setitem__("khi_het_han_muc", "agy"), "E-DELEGATE")


def add_unknown_trial(d):
    x = copy.deepcopy(by_id(d, "opencode"))
    x.update(id="unknown-trial", trang_thai="thu-viec", khi_het_han_muc=None)
    d["agents"].append(x)

bad("thu-viec khong co adapter", add_unknown_trial, "E-DELEGATE")
bad("policy thieu duong cam", lambda d: None, "E-POLICY", policy=pol.replace('  - "*.FCStd"\n', ""))
print("gate OK")
