# Statusline Antigravity CLI (agy) - hien HAN MUC con lai (Tuan 2026-10-26: "hien thi han muc bang do co san cua agent free").
# agy chay lenh nay (cmd /c) moi khi trang thai doi, dua JSON vao stdin, in stdout ra duoi o nhap
# (docs: https://antigravity.google/docs/cli/statusline - truong `quota`: remaining_fraction|remaining_amount, reset_in_seconds).
# Dang ky: ~/.gemini/antigravity-cli/settings.json -> statusLine {command, stack_with_default: true}. Chi doc stdin, khong goi mang.
import json
import sys

G, Y, R, D, X = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"


def left(sec):
    if sec is None:
        return ""
    sec = int(sec)
    d, h, m = sec // 86400, sec % 86400 // 3600, sec % 3600 // 60
    return " reset %s" % ("%dd%dh" % (d, h) if d else "%dh%02dm" % (h, m) if h else "%dm" % m)


try:
    j = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
except ValueError:
    j = {}
parts = []
ctx = (j.get("context_window") or {}).get("used_percentage")
if ctx is not None:
    parts.append("ctx %d%%" % ctx)
for name, q in sorted((j.get("quota") or {}).items()):
    if not isinstance(q, dict) or q.get("disabled"):
        continue
    if q.get("remaining_fraction") is not None:
        pct = 100 * float(q["remaining_fraction"])
        c = G if pct > 50 else Y if pct > 20 else R
        val = "%s%d%%%s" % (c, pct, X)
    elif q.get("remaining_amount") is not None:
        val = str(q["remaining_amount"])
    else:
        continue
    parts.append("%s %s%s%s%s" % (name.replace("_", " ")[:24], val, D, left(q.get("reset_in_seconds")), X))
if not j.get("quota"):
    parts.append(D + "han muc: chua co (go /usage)" + X)
sys.stdout.write("con lai: " + " | ".join(parts) + "\n")
