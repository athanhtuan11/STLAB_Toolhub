# Gate research-scout (Claude viet 2026-11-01, executor KHONG sua). Chay tu claude-workspace:
#   python tools/research-scout/tests/test_scout.py
# Khong goi mang: STLAB_RESEARCH_FIXTURES tro toi thu muc du lieu mau; AI gia qua STLAB_RESEARCH_LLM_CMD.
import json, os, shutil, sqlite3, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent
FIX = HERE / "fixtures"
TMP = Path(tempfile.mkdtemp(prefix="research-scout-test-"))
DB = TMP / "research.db"

WATCH = {
    "topics": [
        {"id": "esp32", "ten": "ESP32", "keywords": ["esp32"], "weight": 1.0},
        {"id": "arduino", "ten": "Arduino", "keywords": ["arduino", "uno"], "weight": 1.0},
        {"id": "raspberry-pi", "ten": "Raspberry Pi", "keywords": ["raspberry", "pico"], "weight": 1.0},
        {"id": "line-robot", "ten": "Xe dò line", "keywords": ["line follower", "line sensor"], "weight": 1.5},
    ],
    "github_queries": [{"q": "esp32 robot", "min_stars": 50, "pushed_days": 90}],
    "repos": [{"repo": "espressif/esp-idf", "topic": "esp32"}],   # chu de khai ro (khong suy tu ten repo)
    "feeds": [{"name": "arduino", "url": "https://blog.arduino.cc/feed/"},
              {"name": "rpi", "url": "https://www.raspberrypi.com/news/feed/"},
              {"name": "broken", "url": "https://example.invalid/feed"}],
    "hn": [{"query": "line follower", "min_points": 20}],
    "digest": {"top_n": 5, "days": 7},
}


def env(**kw):
    e = dict(os.environ, STLAB_RESEARCH_DB=str(DB), STLAB_RESEARCH_WATCH=str(TMP / "watch.json"),
             STLAB_RESEARCH_FIXTURES=str(FIX), PYTHONUTF8="1", STLAB_RESEARCH_NOW="2026-11-01T07:00:00+07:00")
    e.update(kw)
    return e


def run(script, *args, **kw):
    r = subprocess.run([sys.executable, str(TOOL / script), *args], capture_output=True, text=True,
                       env=env(**kw), timeout=120, encoding="utf-8")
    lines = [l for l in r.stdout.strip().splitlines() if l.startswith("{")]
    assert lines, f"{script} khong in JSON\nstdout={r.stdout[-800:]}\nstderr={r.stderr[-800:]}"
    return r.returncode, json.loads(lines[-1])


def rows(sql, *a):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        return [dict(x) for x in con.execute(sql, a)]
    finally:
        con.close()


(TMP / "watch.json").write_text(json.dumps(WATCH, ensure_ascii=False), encoding="utf-8")   # JSON la YAML hop le

# 1) quet lan dau: github 1 (repo 5 sao bi loc), release 1, rss 2, atom 1, hn 1 (3 diem bi loc) = 6; feed hong -> errors
code, j = run("scan.py")
assert code == 0, j
assert j["new"] == 6, j
assert j["by_source"] == {"github": 1, "release": 1, "feed": 3, "hn": 1}, j["by_source"]
assert any("broken" in e for e in j["errors"]), j["errors"]
items = rows("SELECT * FROM items")
assert len(items) == 6
need = {"id", "source", "url", "title", "summary", "published", "topic", "score", "status", "first_seen"}
assert need <= set(items[0]), set(items[0])
by_url = {x["url"]: x for x in items}
kit = by_url["https://github.com/acme/esp32-robot-kit"]
assert kit["topic"] == "esp32" and kit["status"] == "moi" and kit["score"] > 0, kit
assert by_url["https://example.org/line-follower"]["topic"] == "line-robot"           # trung nhieu chu de -> weight cao nhat
assert by_url["https://www.raspberrypi.com/news/pico-2-w-classroom/"]["topic"] == "raspberry-pi"
assert by_url["https://github.com/espressif/esp-idf/releases/tag/v6.1.2"]["source"] == "release"

# 2) quet lai: khong trung
code, j = run("scan.py")
assert code == 0 and j["new"] == 0, j

# 3) phan hoi cua Tuan doi trong so chu de -> diem lai
rel = by_url["https://github.com/espressif/esp-idf/releases/tag/v6.1.2"]
before = kit["score"]
code, j = run("scout.py", "mark", str(rel["id"]), "quan-tam")
assert code == 0 and j["status"] == "quan-tam", j
code, j = run("scan.py", "--rescore")
assert code == 0, j
kit2 = rows("SELECT * FROM items WHERE id=?", kit["id"])[0]
assert kit2["score"] > before, (before, kit2["score"])
code, j = run("scout.py", "mark", str(by_url["https://blog.arduino.cc/2026/10/29/maker-faire/"]["id"]), "bo-qua")
assert code == 0 and j["status"] == "bo-qua"
code, j = run("scout.py", "mark", "999999", "quan-tam")
assert code != 0
code, j = run("scout.py", "mark", str(kit["id"]), "linh-tinh")
assert code != 0

# 4) tong hop tuan bang AI gia: chi lay toi da top_n, bo muc bo-qua, prompt chi co tieu de/url/tom tat
fake = f'"{sys.executable}" "{FIX / "fake_llm.py"}"'
code, j = run("digest.py", STLAB_RESEARCH_LLM_CMD=fake)
assert code == 0, j
d = rows("SELECT * FROM digests ORDER BY id DESC")[0]
assert {"id", "week", "created", "model", "content", "item_ids"} <= set(d), set(d)
assert d["week"] == "2026-W44", d["week"]
ids = json.loads(d["item_ids"])
assert 1 <= len(ids) <= 5, ids
assert by_url["https://blog.arduino.cc/2026/10/29/maker-faire/"]["id"] not in ids
assert "GOI Y TUAN" in d["content"] and f"{len(ids)} muc" in d["content"], d["content"]
prompt = Path(j["prompt_file"]).read_text(encoding="utf-8")
assert "esp32-robot-kit" in prompt and "STLab" in prompt
for bad in ("parent-reports", ".env", "D:\\04_Stlab", "maker/"):
    assert bad not in prompt, bad

# 5) AI loi het -> van luu ban tong hop thô (danh sach) + ghi loi, exit 0
fail = f'"{sys.executable}" "{FIX / "fake_llm_fail.py"}"'
code, j = run("digest.py", "--force", STLAB_RESEARCH_LLM_CMD=fail)
assert code == 0, j
d2 = rows("SELECT * FROM digests ORDER BY id DESC")[0]
assert d2["model"] == "khong-ai" and "esp32-robot-kit" in d2["content"], d2
assert j["errors"], j

# 6) chuoi model mac dinh dung agy theo thu tu luat STLab (khong goi that – chi kiem cau hinh in ra)
code, j = run("digest.py", "--print-chain")
assert code == 0
assert j["chain"] == ["gemini-3.8-flash-medium", "claude-sonnet-4-6", "claude-opus-4-6-thinking", "gpt-oss-120b-medium"], j

# 7) API Python cho Toolhub
sys.path.insert(0, str(TOOL))
os.environ["STLAB_RESEARCH_DB"] = str(DB)
import store  # noqa: E402
lst = store.list_items(topic="esp32")
assert lst and all(x["topic"] == "esp32" for x in lst)
assert store.latest_digest()["week"] == "2026-W44"
assert [t["id"] for t in store.topics(str(TMP / "watch.json"))] == ["esp32", "arduino", "raspberry-pi", "line-robot"]
assert store.set_status(kit["id"], "bo-qua") is True and store.set_status(424242, "bo-qua") is False

shutil.rmtree(TMP, ignore_errors=True)
print("test_scout PASS")
