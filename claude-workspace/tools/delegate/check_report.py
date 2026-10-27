# Gate cho bao cao nghien cuu do executor viet: du muc bat buoc + moi duong dan `community/...`, `tools/...` duoc dan
# phai TON TAI (chan bia). Duong dan tinh tu claude-workspace/.
#   python check_report.py <report.md> "## Muc 1" "## Muc 2" ...
import os, re, sys

WS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
report, sections = sys.argv[1], sys.argv[2:]
text = open(report, encoding="utf-8").read()
bad = [s for s in sections if s not in text]
cited = sorted(set(re.findall(r"`((?:community|tools|docs)/[^`\s:#]+)", text)))
missing = [p for p in cited if not os.path.exists(os.path.join(WS, p.rstrip("/")))]
print(f"muc thieu: {bad}\nduong dan dan: {len(cited)}, khong ton tai: {missing}")
sys.exit(0 if not bad and not missing and len(cited) >= 10 else 1)
