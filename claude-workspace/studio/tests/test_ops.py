# Gate trang "Dieu hanh" /ops (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv/Scripts/python.exe tests/test_ops.py
# Du lieu gia trong thu muc tam (LOCALAPPDATA), khong dung events.db that.
import json, os, sys, tempfile, time
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
WS = STUDIO.parent
TMP = Path(tempfile.mkdtemp(prefix="ops-test-"))
os.environ["LOCALAPPDATA"] = str(TMP)                       # truoc khi import toolhub / events
sys.stdout.reconfigure(encoding="utf-8")
U = TMP / "stlab-usage"
R = U / "delegate-runs"


def run(name, state=None, result=None):
    d = R / name
    d.mkdir(parents=True)
    if state is not None:
        json.dump(state, open(d / "state.json", "w"))
    if result is not None:
        json.dump(result, open(d / "result.json", "w"))
        (d / "handoff.md").write_text("ban giao", encoding="utf-8")


run("20261101-100000-viec-dang-chay", state={"state": "running", "pid": os.getpid(), "spec": "a.md",
                                             "executor": "codex"})
run("20261101-090000-viec-bi-cat", state={"state": "running", "pid": 999999, "spec": "b.md"})
run("20261101-080000-viec-xong", result={"verdict": "PASS", "task": "viec-xong"})
run("20261101-070000-viec-loi", result={"verdict": "FAIL", "task": "viec-loi"})
run("20261101-060000-viec-bao-len", result={"verdict": "ESCALATE", "task": "viec-bao-len", "escalate": "thieu quyen"})

sys.path.insert(0, str(WS / "tools" / "org"))
import events  # noqa: E402

for k in range(60):
    events.emit("hook", "tool", f"Edit file{k}.py", agent="claude-main", session="s1")
events.emit("delegate", "run_end", "viec-xong PASS", agent="codex")
a1 = events.add_approval("Cho in ban moi?", "claude", ref="maker/x/print/print.yaml")
a2 = events.add_approval("Them nguon cong dong?", "guard")
events.resolve(a2, "tu-choi", "tuan")

sys.path.insert(0, str(STUDIO))
from toolhub import create_app  # noqa: E402

c = create_app().test_client()
H = {"Host": "127.0.0.1:5050"}

# 1) trang /ops: du 6 khung theo thiet ke (docs/reports/ops-center-design.md muc 3)
r = c.get("/ops", headers=H)
assert r.status_code == 200, r.status_code
html = r.get_data(as_text=True)
for w in ("approvals", "running", "board", "timeline", "org", "commits"):
    assert f'data-widget="{w}"' in html, w

# 2) API tong
r = c.get("/api/ops", headers=H)
assert r.status_code == 200, r.status_code
d = r.get_json()
assert [x["id"] for x in d["approvals"]] == [a1], d["approvals"]          # chi muc dang 'cho'
assert d["approvals"][0]["question"] == "Cho in ban moi?"
assert [x["task"] for x in d["running"]] == ["viec-dang-chay"], d["running"]
assert d["running"][0]["executor"] == "codex" and d["running"][0]["seconds"] >= 0
b = d["board"]
assert set(b) == {"dang_chay", "xong", "loi", "bao_len"}, set(b)
assert [x["task"] for x in b["dang_chay"]] == ["viec-dang-chay"]
assert [x["task"] for x in b["xong"]] == ["viec-xong"]
assert {x["task"] for x in b["loi"]} == {"viec-loi", "viec-bi-cat"}, b["loi"]   # bi cat ngang = loi
assert [x["task"] for x in b["bao_len"]] == ["viec-bao-len"]
assert b["bao_len"][0]["note"] == "thieu quyen", b["bao_len"]
assert all("run" in x for col in b.values() for x in col)                 # ten thu muc run de mo handoff
t = d["timeline"]
assert len(t) == 50, len(t)                                               # mac dinh 50 su kien moi nhat
assert t[0]["id"] > t[-1]["id"]
assert {"id", "ts", "source", "agent", "kind", "title"} <= set(t[0])
assert d["summary"] == {"cho_duyet": 1, "dang_chay": 1, "loi": 2}, d["summary"]
cm = d["commits"]
assert 1 <= len(cm) <= 10 and {"hash", "subject", "date"} <= set(cm[0]), cm[:1]
assert len(cm[0]["hash"]) >= 7

# 3) dong thoi gian theo con tro
last = t[0]["id"]
events.emit("hook", "stop", "Stop", agent="claude-main")
r = c.get(f"/api/ops/timeline?after={last}", headers=H)
assert r.status_code == 200
assert [x["title"] for x in r.get_json()["timeline"]] == ["Stop"], r.get_json()

# 4) duyet: POST thieu X-Studio -> 403 (chong CSRF), du header -> doi trang thai
r = c.post(f"/api/ops/approvals/{a1}", headers=H, json={"state": "da-duyet", "note": "ok"})
assert r.status_code == 403, r.status_code
HP = dict(H, **{"X-Studio": "1"})
r = c.post(f"/api/ops/approvals/{a1}", headers=HP, json={"state": "bay-ba"})
assert r.status_code == 400, r.status_code
r = c.post(f"/api/ops/approvals/{a1}", headers=HP, json={"state": "da-duyet", "note": "ok"})
assert r.status_code == 200, r.status_code
st = {x["id"]: x for x in events.list_approvals()}
assert st[a1]["state"] == "da-duyet" and st[a1]["by"] == "tuan" and st[a1]["note"] == "ok", st[a1]
assert c.get("/api/ops", headers=H).get_json()["summary"]["cho_duyet"] == 0
r = c.post("/api/ops/approvals/99999", headers=HP, json={"state": "da-duyet"})
assert r.status_code == 404, r.status_code

# 5) handoff cua run: chi doc trong delegate-runs, chan duong dan thoat
r = c.get("/api/ops/run/20261101-060000-viec-bao-len/handoff", headers=H)
assert r.status_code == 200 and "ban giao" in r.get_data(as_text=True)
r = c.get("/api/ops/run/..%2F..%2Fx/handoff", headers=H)
assert r.status_code in (400, 404), r.status_code

# 6) trang chinh co dai tom tat dan toi /ops
html = c.get("/", headers=H).get_data(as_text=True)
assert 'href="/ops"' in html and "data-ops-summary" in html

# 7) Host la -> 403 (giu chong DNS rebinding)
assert c.get("/api/ops", headers={"Host": "evil.com"}).status_code == 403

print("test_ops PASS")
