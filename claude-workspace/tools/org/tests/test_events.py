# Gate buoc 1 trung tam dieu hanh: kho su kien + hang cho duyet + hook + delegate ghi su kien (Claude viet, KHONG sua).
#   python tools/org/tests/test_events.py      (chay tu claude-workspace)
import importlib.util, json, os, subprocess, sys, tempfile, time

WS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TMP = tempfile.mkdtemp(prefix="events-test-")
os.environ["LOCALAPPDATA"] = TMP                                  # truoc moi import


def load(name, rel):
    s = importlib.util.spec_from_file_location(name, os.path.join(WS, rel))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


ev = load("events", "tools/org/events.py")
DB = os.path.join(TMP, "stlab-usage", "events.db")

# 1) emit + recent
a = ev.emit("claude", "session_start", "Mở phiên", agent="claude-main", session="s1")
b = ev.emit("delegate", "run_end", "codex xong việc", agent="codex", ref="run-1", data={"verdict": "PASS"})
assert isinstance(a, int) and b > a and os.path.exists(DB)
rows = ev.recent(limit=10)
assert [r["id"] for r in rows][:2] == [b, a], "recent: moi nhat truoc"
assert {"id", "ts", "source", "kind", "title", "agent", "session", "parent", "ref", "data"} <= set(rows[0])
assert rows[0]["data"] == {"verdict": "PASS"}
assert [r["id"] for r in ev.recent(after_id=a)] == [b], "after_id cho polling"
assert [r["id"] for r in ev.recent(agent="claude-main")] == [a]

# 2) khong bao gio lam hong cong viec chinh: duong dan khong ghi duoc -> None, khong raise
bad = os.path.join(TMP, "la-file")
open(bad, "w").write("x")
os.environ["LOCALAPPDATA"] = bad
assert ev.emit("x", "y", "z") is None
os.environ["LOCALAPPDATA"] = TMP

# 3) hang cho duyet
q = ev.add_approval("robotic arm: hướng A/B/C?", source="claude-main", ref="maker/x/brief.md", options=["A", "B", "C"])
assert any(x["id"] == q and x["state"] == "cho" and x["options"] == ["A", "B", "C"] for x in ev.list_approvals("cho"))
assert ev.resolve(q, "da-duyet", by="tuan", note="A") is True
x = next(x for x in ev.list_approvals() if x["id"] == q)
assert x["state"] == "da-duyet" and x["by"] == "tuan" and x["note"] == "A"
assert ev.resolve(999999, "da-duyet", by="tuan") is False
assert any(r["kind"] == "approval_resolved" for r in ev.recent()), "duyet cung ghi su kien"

# 4) CLI
def cli(*args):
    r = subprocess.run([sys.executable, os.path.join(WS, "tools/org/events.py"), *args], capture_output=True,
                       text=True, encoding="utf-8", env=dict(os.environ, LOCALAPPDATA=TMP))
    assert r.returncode == 0, r.stderr[-400:]
    return json.loads(r.stdout)


nid = cli("approvals", "add", "Chọn màu?", "--source", "claude-main", "--ref", "a.md")["id"]
assert any(x["id"] == nid for x in cli("approvals", "list", "--state", "cho"))
assert cli("approvals", "resolve", str(nid), "--state", "tu-choi", "--note", "để sau")["ok"] is True
assert isinstance(cli("tail", "--limit", "3"), list)

# 5) hook: khong luu noi dung prompt; gan dung agent; rac -> exit 0; du nhanh
HOOK = os.path.join(WS, "custom/hooks/event_log.py")


def hook(payload):
    t = time.time()
    r = subprocess.run([sys.executable, HOOK], input=json.dumps(payload).encode("utf-8") if payload is not None else b"rac",
                       capture_output=True, env=dict(os.environ, LOCALAPPDATA=TMP))
    assert r.returncode == 0, r.stderr[-300:]
    assert time.time() - t < 3, "hook qua cham"


n0 = ev.recent(limit=1)[0]["id"]
hook({"hook_event_name": "UserPromptSubmit", "session_id": "s9", "prompt": "BI-MAT-KHONG-LUU 123"})
hook({"hook_event_name": "PostToolUse", "session_id": "s9", "tool_name": "Edit",
      "tool_input": {"file_path": "D:/x/maker/arm/brief.md", "old_string": "BI-MAT-KHONG-LUU"}})
hook({"hook_event_name": "SubagentStop", "session_id": "s9", "agent_type": "doc-writer", "agent_id": "a1"})
hook({"hook_event_name": "Stop", "session_id": "s9"})
hook(None)
new = ev.recent(after_id=n0, limit=50)
assert len(new) >= 4, new
blob = json.dumps(new, ensure_ascii=False)
assert "BI-MAT-KHONG-LUU" not in blob, "hook KHONG duoc luu noi dung prompt/ma"
assert any(r["kind"] == "tool" and "brief.md" in r["title"] for r in new)
assert any(r["kind"] == "subagent_stop" and r["agent"] == "doc-writer" for r in new)
assert all(r["source"] == "hook" for r in new)

# 6) delegate ghi su kien + ESCALATE -> muc duyet (executor gia, khong ton han muc)
d = load("delegate", "tools/delegate/delegate.py")
d.command = lambda name, prompt: ([sys.executable, "-c", "print('ESCALATE: can quyen ghi org')"], None)
d.installed = lambda n: True
n1 = ev.recent(limit=1)[0]["id"]
sys.argv = ["delegate.py", os.path.join(WS, "tools/delegate/selftest/spec.md"), "--executor", "opencode"]
try:
    d.main()
except SystemExit:
    pass
kinds = [r["kind"] for r in ev.recent(after_id=n1, limit=50)]
assert "run_start" in kinds and "run_end" in kinds, kinds
assert any(x["source"] == "delegate" and x["state"] == "cho" and "can quyen ghi org" in x["question"]
           for x in ev.list_approvals("cho")), "ESCALATE phai tao muc cho duyet"
print("gate OK")
