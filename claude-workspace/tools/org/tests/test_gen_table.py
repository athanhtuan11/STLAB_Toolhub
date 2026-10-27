# Gate buoc 4 so nhan su: sinh bang CLAUDE.md tu org/agents.yaml (Claude viet, executor KHONG sua).
#   python tests/test_gen_table.py      (chay tu tools/org)
import os, shutil, subprocess, sys, tempfile
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "gen_table.py")
ORG = os.path.abspath(os.path.join(HERE, "..", "..", "..", "org"))
S, E = "<!-- org-table:start -->", "<!-- org-table:end -->"
tmp = tempfile.mkdtemp(prefix="gen-table-test-")
md = os.path.join(tmp, "CLAUDE.md")
before, after = "# Tieu de\n\nDoan truoc giu nguyen.\n\n", "\n\nDoan sau giu nguyen.\n"
open(md, "w", encoding="utf-8").write(before + S + "\n| bang cu |\n" + E + after)


def run(*a):
    r = subprocess.run([sys.executable, TOOL, "--org", ORG, "--claude", md, *a], capture_output=True, text=True,
                       encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


assert run("--check")[0] == 1, "bang cu khac so -> --check exit 1"
code, out = run("--write")
assert code == 0, out
t = open(md, encoding="utf-8").read()
assert t.startswith(before + S) and t.endswith(E + after), "phan ngoai marker phai giu nguyen"
body = t[t.index(S) + len(S):t.index(E)]
agents = yaml.safe_load(open(os.path.join(ORG, "agents.yaml"), encoding="utf-8"))["agents"]
for a in agents:
    assert f"`{a['id']}`" in body and a["chuc_danh"] in body, f"bang thieu {a['id']}"
assert body.count("\n|") >= len(agents) + 2, "phai co dong tieu de + dong ke + moi agent 1 dong"
for col in ("Tầng", "Chức danh", "Model", "Chi phí", "Kỹ năng", "Báo cáo cho", "Trạng thái"):
    assert col in body, f"thieu cot {col}"
assert run("--check")[0] == 0, "sau --write, --check phai exit 0"
assert run("--write")[0] == 0 and open(md, encoding="utf-8").read() == t, "--write lan 2 khong doi gi"
open(md, "w", encoding="utf-8").write("khong co marker\n")
assert run("--check")[0] == 2, "thieu marker -> exit 2"
shutil.rmtree(tmp, ignore_errors=True)
print("gate OK")
