# Gate man chu viet phan BO (Claude viet 2026-11-28, executor KHONG sua). Spec: spec-literacy.md
# Chay: python check_literacy.py   (sau sync.ps1 + build.ps1)
import re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
B = H / "boards" / "stlab-s3"
A = H / "assets"
fails = []
def need(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
def read(p):
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

board = read(B / "stlab_s3.cc")
eyes = read(B / "owl_eyes_display.cc") + read(B / "owl_eyes_display.h")
allsrc = board + eyes + "".join(read(p) for p in B.glob("*.cc") if p.name not in ("stlab_s3.cc", "owl_eyes_display.cc"))
cfg = read(B / "config.h")

# 1. Tool MCP tren bo + notification
for t in ("self.screen.show_word", "self.screen.show_pick", "self.screen.show_letter", "self.screen.show_stickers", "self.screen.clear"):
    need(f'"{t}"' in board, "AddTool " + t)
need("AddTool" in board, "dung McpServer AddTool")
need("notifications/stlab_touch" in allsrc and "SendMcpMessage" in allsrc, "cham -> SendMcpMessage notifications/stlab_touch")
for k in ('\\"screen\\"', '\\"word\\"', '\\"correct\\"'):
    need(k in allsrc or k.replace('\\"', '"') in allsrc, "notification co truong " + k.replace('\\', ''))

# 2. Mau / hinh hoc theo mockup
for c in ("FFF3DF", "22304A", "FF8A3D", "5BD27A", "5A6273", "FFC83D"):
    need(re.search(c, eyes, re.I) is not None, "mau the #" + c)
for n in ("26", "134", "186", "17", "18"):
    need(re.search(r"\b%s\b" % n, eyes) is not None, "so mockup %s px" % n)
need(re.search(r"\b8000\b", eyes) is not None and re.search(r"\b15000\b", eyes) is not None, "tu ve mat 8 s (B: 15 s)")
need(re.search(r"\b220\b", eyes) is not None, "gach chan ~220 ms/chu")
need(re.search(r"\b400\b", allsrc) is not None, "chong doi 400 ms")
for k in ("TOUCH_SWAP_XY", "TOUCH_MIRROR_X", "TOUCH_MIRROR_Y"):
    need(re.search(r"#define\s+%s\s+(true|false|0|1)\b" % k, cfg) is not None, k + " trong config.h")
need("GetAssetData" in eyes, "doc hinh tu assets (GetAssetData, mmap)")

# 3. Phong Andika
fonts = list(B.glob("*andika*")) + list(B.glob("*Andika*"))
need(len(fonts) >= 3, "3 file phong Andika C trong boards/stlab-s3 (52/34/120) – co %d" % len(fonts))
need(any("52" in p.name for p in fonts) and any("34" in p.name for p in fonts) and any("120" in p.name for p in fonts), "co du co 52/34/120")
need((A / "fonts" / "OFL.txt").exists(), "assets/fonts/OFL.txt (giay phep Andika)")

# 4. Hinh Twemoji
mp = read(A / "pic-map.yaml"); mk = read(A / "make_pics.py")
need("twemoji@14.0.2" in mk and "72x72" in mk, "make_pics.py tai Twemoji 14.0.2 72x72 (ghim ban)")
need("ROADMAP.md" in mk, "make_pics.py doc tu tu lessons-seed/ROADMAP.md")
entries = re.findall(r"^\s*([a-z][a-z \-']*)\s*:\s*(\S+)", mp, re.M)
need(len(entries) >= 250, "pic-map.yaml >= 250 tu (co %d)" % len(entries))
for w, code in (("cat", "1f431"), ("dog", "1f436"), ("apple", "1f34e")):
    need(any(e[0].strip() == w and code in e[1].lower() for e in entries), f"pic-map: {w} -> {code}")
pics = list((A / "pics").glob("*.bin"))
need(len(pics) >= 150, "assets/pics/*.bin sinh ra >= 150 (co %d)" % len(pics))
gi = read(H / ".gitignore") + read(A / ".gitignore")
need("pics" in gi and ".cache" in gi, ".gitignore co assets/pics + .cache")
pat = "\n".join(read(p) for p in sorted((H / "patches").glob("*.patch")))
need("DEFAULT_ASSETS_EXTRA_FILES" in pat and "stlab" in pat.lower(), "patch dua hinh vao assets bang DEFAULT_ASSETS_EXTRA_FILES")
need("make_pics.py" in read(H / "sync.ps1"), "sync.ps1 chay make_pics.py")
need("Twemoji" in read(H / "README.md") and "CC BY 4.0" in read(H / "README.md"), "README ghi cong Twemoji CC BY 4.0")

# 5. Build moi + gate cu
bin_ = H / "build-src" / "build" / "xiaozhi.bin"
srcs = [B / "owl_eyes_display.cc", B / "stlab_s3.cc", B / "config.h"]
need(bin_.exists() and all(bin_.stat().st_mtime > s.stat().st_mtime for s in srcs if s.exists()), "xiaozhi.bin moi hon ma nguon")
blog = read(H / "build.log")
need(bool(blog) and "error:" not in blog, "build.log khong loi")
ga = H / "build-src" / "build" / "generated_assets.bin"
need(ga.exists() and ga.stat().st_size > 1_000_000, "generated_assets.bin > 1 MB (co hinh)")
need(re.search(r"\bTODO\b|\bFIXME\b", board + eyes) is None, "khong TODO/FIXME trong ma bo")
for g in ("check_s3.py", "check_display.py"):
    r = subprocess.run([sys.executable, str(H / g)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    need(r.returncode == 0, g + " PASS" + ("" if r.returncode == 0 else ": " + " | ".join(l for l in r.stdout.splitlines() if l.startswith("FAIL"))[:300]))

print("\nKET QUA:", "PASS" if not fails else "FAIL (%d)" % len(fails))
sys.exit(1 if fails else 0)
