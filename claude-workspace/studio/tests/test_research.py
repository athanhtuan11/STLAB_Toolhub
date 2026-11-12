# Gate trang "Nghien cuu" /research (Claude viet 2026-11-01, executor KHONG sua). Chay tu thu muc studio:
#   .venv\Scripts\python.exe tests\test_research.py
# DB tam (STLAB_RESEARCH_DB) + lenh quet gia (STLAB_RESEARCH_SCAN_CMD) - khong dong du lieu that, khong goi mang.
import json, os, sys, tempfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
WS = STUDIO.parent
TMP = Path(tempfile.mkdtemp(prefix="research-page-test-"))
os.environ["STLAB_RESEARCH_DB"] = str(TMP / "research.db")
os.environ["STLAB_RESEARCH_WATCH"] = str(WS / "tools" / "research-scout" / "watch.yaml")
marker = TMP / "scan-ran.txt"
os.environ["STLAB_RESEARCH_SCAN_CMD"] = f'"{sys.executable}" -c "open(r\'{marker}\',\'w\').write(\'ok\')"'
sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(WS / "tools" / "research-scout"))
import store  # noqa: E402

store.add_item("github", "https://github.com/acme/esp32-kit", "acme/esp32-kit", "ESP32 <b>robot</b> kit", "2026-10-30",
               "esp32", 3.0, first_seen="2026-11-01T07:00:00+07:00")
store.add_item("feed", "https://blog.arduino.cc/x", "Arduino news", "UNO Q", "2026-10-30", "arduino", 1.0,
               first_seen="2026-11-01T07:00:00+07:00")
store.add_item("hn", "https://example.org/old", "Tin da bo", "x", "2026-10-30", "esp32", 0.5,
               first_seen="2026-11-01T07:00:00+07:00")
ids = {x["title"]: x["id"] for x in store.list_items()}
store.set_status(ids["Tin da bo"], "bo-qua")
con = store.connect()
con.execute("INSERT INTO digests(week, created, model, content, item_ids) VALUES(?,?,?,?,?)",
            ("2026-W44", "2026-11-01T07:30:00+07:00", "claude-sonnet-4-6", "GOI Y: thu esp32-kit cho line-bot <script>x</script>",
             json.dumps([ids["acme/esp32-kit"]])))
con.commit()
con.close()

sys.path.insert(0, str(STUDIO))
from toolhub import create_app  # noqa: E402

c = create_app().test_client()
H = {"Host": "127.0.0.1:5050"}
HP = dict(H, **{"X-Studio": "1"})

# 1) trang: ban tong hop tuan + danh sach; escape HTML; mac dinh an muc bo-qua
r = c.get("/research", headers=H)
assert r.status_code == 200, r.status_code
html = r.get_data(as_text=True)
assert "2026-W44" in html and "GOI Y: thu esp32-kit" in html and "claude-sonnet-4-6" in html
assert "<script>x</script>" not in html, "noi dung AI phai duoc escape"
assert "acme/esp32-kit" in html and "Arduino news" in html
assert "Tin da bo" not in html
assert "<b>robot</b>" not in html
assert 'href="https://github.com/acme/esp32-kit"' in html and 'rel="noopener' in html

# 2) API loc
d = c.get("/api/research?topic=esp32", headers=H).get_json()
assert [x["title"] for x in d["items"]] == ["acme/esp32-kit"], d
assert {"id", "title", "url", "topic", "score", "status", "source", "summary"} <= set(d["items"][0])
assert d["digest"]["week"] == "2026-W44"
assert any(t["id"] == "esp32" for t in d["topics"])
d = c.get("/api/research?status=bo-qua", headers=H).get_json()
assert [x["title"] for x in d["items"]] == ["Tin da bo"], d

# 3) phan hoi Quan tam / Bo qua: can X-Studio; status sai 400; id khong co 404
kid = ids["acme/esp32-kit"]
assert c.post(f"/api/research/{kid}/status", headers=H, json={"status": "quan-tam"}).status_code == 403
assert c.post(f"/api/research/{kid}/status", headers=HP, json={"status": "lung-tung"}).status_code == 400
assert c.post("/api/research/999999/status", headers=HP, json={"status": "quan-tam"}).status_code == 404
r = c.post(f"/api/research/{kid}/status", headers=HP, json={"status": "quan-tam"})
assert r.status_code == 200, r.status_code
assert [x for x in store.list_items() if x["id"] == kid][0]["status"] == "quan-tam"

# 4) nut "Quet ngay": chay lenh quet o nen, tra 202 ngay
r = c.post("/api/research/scan", headers=HP)
assert r.status_code == 202, r.status_code
import time  # noqa: E402
for _ in range(50):
    if marker.exists():
        break
    time.sleep(0.1)
assert marker.exists(), "lenh quet khong chay"
assert c.post("/api/research/scan", headers=H).status_code == 403

# 5) menu + DB rong khong loi
# 2026-11-12 Tuan: bo muc Nghien cuu khoi menu (route /research van chay)
assert 'href="/research"' not in c.get("/", headers=H).get_data(as_text=True)
os.environ["STLAB_RESEARCH_DB"] = str(TMP / "rong.db")
assert c.get("/research", headers=H).status_code == 200
assert c.get("/api/research", headers=H).get_json()["items"] == []

print("test_research PASS")
