# Gate trang "Nhan su AI" (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv/Scripts/python.exe tests/test_org_board.py
import json, os, re, sys, tempfile, time
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
WS = STUDIO.parent
TMP = Path(tempfile.mkdtemp(prefix="org-board-test-"))
os.environ["LOCALAPPDATA"] = str(TMP)                       # truoc khi import toolhub (usage.py doc luc import)
U = TMP / "stlab-usage"
(U / "delegate-runs" / "20261027-100000-viec-bi-cat").mkdir(parents=True)
json.dump({"state": "running", "pid": 999999, "spec": "x.md"},
          open(U / "delegate-runs" / "20261027-100000-viec-bi-cat" / "state.json", "w"))
(U / "delegate-runs" / "20261027-090000-viec-xong").mkdir(parents=True)
json.dump({"verdict": "PASS"}, open(U / "delegate-runs" / "20261027-090000-viec-xong" / "result.json", "w"))
until = time.strftime("%Y-%m-%dT%H:%M+07:00", time.localtime(time.time() + 3 * 3600))
json.dump({"codex": {"limited_until": until, "reason": "429"}}, open(U / "executors.json", "w"))
json.dump({"opencode": {"rounds": 10, "gate_pass": 8, "pass_round1": 6, "limited": 0, "escalate": 0, "seconds": 938,
                       "last_run": "2026-10-30T10:04", "last_pass": "2026-10-29T08:00"}},
          open(U / "agent-stats.json", "w"))

sys.path.insert(0, str(STUDIO))
from toolhub import create_app  # noqa: E402
import yaml  # noqa: E402

c = create_app().test_client()
H = {"Host": "127.0.0.1:5050"}
r = c.get("/api/org", headers=H)
assert r.status_code == 200, r.status_code
d = r.get_json()

# 1) Nguon han muc (Tuan 2026-10-30: du MOI nguon, nguon chua co so van hien + "lan cuoi chay")
prov = {p["id"]: p for p in d["providers"]}
assert set(prov) == {"claude", "codex", "gemini", "opencode", "kilo", "copilot"}, set(prov)
for p in prov.values():
    assert {"name", "bars", "agents", "limited_until", "note", "last_run"} <= set(p), p.keys()
assert set(prov["claude"]["agents"]) == {"claude-main", "check-runner", "doc-writer", "git-scribe"}
assert set(prov["codex"]["agents"]) == {"codex", "ask-gpt"}
assert set(prov["gemini"]["agents"]) == {"agy", "agy-sonnet", "ask-gemini"}, prov["gemini"]["agents"]
assert "Antigravity" in prov["gemini"]["name"], prov["gemini"]["name"]
assert prov["opencode"]["agents"] == ["opencode"] and prov["kilo"]["agents"] == ["kilo"]
assert prov["copilot"]["agents"] == ["copilot"]
mine = [a for p in prov.values() for a in p["agents"]]
assert len(mine) == len(set(mine)), "moi agent chi thuoc 1 nguon"
assert prov["codex"]["limited_until"], "codex dang het han muc (executors.json) phai hien gio"
assert prov["opencode"]["last_run"] == "30/10 10:04", prov["opencode"]["last_run"]
assert prov["kilo"]["last_run"] == "" and "chưa có số" in prov["kilo"]["note"].lower(), prov["kilo"]
assert "chưa có số" in prov["copilot"]["note"].lower(), prov["copilot"]

# 2) So do: 4 tang, du agent theo so that, trang thai dung
agents = yaml.safe_load(open(WS / "org" / "agents.yaml", encoding="utf-8"))["agents"]
tiers = d["tiers"]
assert [t["label"] for t in tiers] == ["Giám đốc", "Quản lý", "Nhân viên", "Tư vấn"], [t["label"] for t in tiers]
got = {a["id"]: a for t in tiers for a in t["agents"]}
assert set(got) == {a["id"] for a in agents}
for a in got.values():
    assert {"chuc_danh", "model", "ky_nang", "status", "status_text"} <= set(a), a.keys()
    assert a["status"] in ("san-sang", "het-han-muc", "thu-viec", "nghi"), a["status"]
assert got["codex"]["status"] == "het-han-muc" and got["opencode"]["status"] == "san-sang"
assert got["opencode"]["stats"]["pass_rate"] == 0.8 and got["opencode"]["stats"]["rounds"] == 10

# 3) Can chu y: run bi cat ngang (pid chet, khong result) + nhan vien het han muc; run da xong khong hien
att = d["attention"]
assert any("viec-bi-cat" in x["text"] and "--resume" in x["text"] for x in att), att
assert any("codex" in x["text"] for x in att), att
assert not any("viec-xong" in x["text"] for x in att)

# 4) Trang chinh + /api/usage cu van chay; khong ma hex moi trong giao dien
r = c.get("/", headers=H)
html = r.get_data(as_text=True)
assert r.status_code == 200 and "Nhân sự AI" in html and "/api/org" in html
assert c.get("/api/usage", headers=H).status_code == 200
tpl = (STUDIO / "toolhub" / "templates" / "overview.html").read_text(encoding="utf-8")
assert not re.search(r"#[0-9a-fA-F]{3,8}\b", re.sub(r"&#\d+;", "", tpl)), "khong dat ma hex trong template"
css = (STUDIO / "toolhub" / "static" / "style.css").read_text(encoding="utf-8")
assert not re.search(r":\s*#[0-9a-fA-F]{3,8}\b", css), "style.css chi dung var(--...)"
print("gate OK")
