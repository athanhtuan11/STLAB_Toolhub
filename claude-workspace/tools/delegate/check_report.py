# Gate cho bao cao nghien cuu do executor viet: du muc bat buoc + moi duong dan `community/...`, `tools/...` duoc dan
# phai TON TAI (chan bia) + du FILE cu the (khong chi thu muc) + it TODO (chan bao cao rong).
# Duong dan tinh tu claude-workspace/.
#   python check_report.py <report.md> "## Muc 1" "## Muc 2" ... [--max-todo 6] [--min-files 10]
# Bai hoc 2026-10-27: bao cao toan TODO + chi dan thu muc van PASS gate cu.
import argparse, os, re, sys

WS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("report")
ap.add_argument("sections", nargs="*")
ap.add_argument("--max-todo", type=int, default=6)
ap.add_argument("--min-files", type=int, default=10)
a = ap.parse_args()

text = open(a.report, encoding="utf-8").read()
bad = [s for s in a.sections if s not in text]
cited = sorted(set(re.findall(r"`((?:community|tools|docs)/[^`\s:#]+)", text)))
missing = [p for p in cited if not os.path.exists(os.path.join(WS, p.rstrip("/")))]
files = [p for p in cited if os.path.isfile(os.path.join(WS, p))]
todo = len(re.findall(r"\bTODO\b", text))
print(f"muc thieu: {bad}\nduong dan dan: {len(cited)}, khong ton tai: {missing}\n"
      f"file cu the: {len(files)} (can >= {a.min_files})\nTODO: {todo} (toi da {a.max_todo})")
sys.exit(0 if not bad and not missing and len(files) >= a.min_files and todo <= a.max_todo else 1)
