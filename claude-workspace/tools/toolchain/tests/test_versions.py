# Gate bang phien ban cong cu (Claude viet, executor KHONG sua). Chay tu claude-workspace:
#   python tools/toolchain/tests/test_versions.py
# Chay that tren may Tuan (doc phien ban cong cu dang cai), ghi ra thu muc tam - khong dong docs/toolchain.md.
import json, re, subprocess, sys, tempfile, time
from pathlib import Path

WS = Path(__file__).resolve().parents[3]
SCRIPT = WS / "tools" / "toolchain" / "versions.py"
TMP = Path(tempfile.mkdtemp(prefix="toolchain-test-"))
out_md, out_json = TMP / "toolchain.md", TMP / "toolchain.json"

t0 = time.time()
r = subprocess.run([sys.executable, str(SCRIPT), "--out", str(out_md), "--json", str(out_json)],
                   cwd=WS, capture_output=True, text=True, timeout=600, encoding="utf-8")
assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
assert time.time() - t0 < 300, "qua cham"
j = json.loads(out_json.read_text(encoding="utf-8"))

# 1) cong cu: moi muc {id, name, version, source}; version = chuoi phien ban hoac null (KHONG bia)
tools = {t["id"]: t for t in j["tools"]}
need = {"freecad", "bambu-studio", "esp-idf", "python", "git", "node", "uv", "codex", "opencode", "kilo", "copilot",
        "agy", "claude-code", "graphviz", "hyperframes"}
assert need <= set(tools), need - set(tools)
for t in tools.values():
    assert {"id", "name", "version", "source"} <= set(t), t
    assert t["version"] is None or re.match(r"^v?\d+(\.\d+)+", t["version"]), t
assert tools["freecad"]["version"].startswith("1.1"), tools["freecad"]      # da kiem: 1.1.4 dang cai
assert tools["python"]["version"].startswith("3."), tools["python"]
assert tools["git"]["version"], tools["git"]
assert tools["claude-code"]["version"], tools["claude-code"]               # extension VS Code 2.1.x

# 2) community: moi thu muc con trong community/ (tru reports) co 1 dong
dirs = sorted(p.name for p in (WS / "community").iterdir() if p.is_dir() and p.name != "reports")
com = {c["name"]: c for c in j["community"]}
assert sorted(com) == dirs, set(dirs) ^ set(com)
for c in com.values():
    assert {"name", "size_mb", "linked", "pin", "last_commit"} <= set(c), c
    assert isinstance(c["size_mb"], (int, float)) and c["size_mb"] >= 0
    assert isinstance(c["linked"], bool)
assert j["community_total_mb"] > 1000, j["community_total_mb"]              # da do: ~7,5 GB
assert any(c["linked"] for c in com.values()) and not all(c["linked"] for c in com.values())

# 3) markdown: 2 bang, sap community theo dung luong giam dan, khong ghi duong dan ca nhan day du
md = out_md.read_text(encoding="utf-8")
assert md.startswith("# ") and "| Công cụ |" in md and "| Repo |" in md, md[:300]
sizes = [com[n]["size_mb"] for n in re.findall(r"^\| `([^`]+)` \|", md, re.M) if n in com]
assert len(sizes) == len(com) and sizes == sorted(sizes, reverse=True), sizes[:5]
assert "C:\\Users\\hoang" not in md and "C:/Users/hoang" not in md, "khong ghi duong dan home that"
print("test_versions PASS")
