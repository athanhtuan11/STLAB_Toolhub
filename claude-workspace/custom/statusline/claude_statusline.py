# Statusline Claude Code - hien HAN MUC goi Pro (5 gio + tuan) de phoi hop token voi Codex/agy (Tuan 2026-10-26:
# "claude code thi them don vi do luong de minh phoi hop token. token claude code reset theo tuan").
# Claude Code chay lenh nay moi khi trang thai doi, dua JSON vao stdin (docs: code.claude.com/docs/en/statusline):
#   rate_limits.five_hour / seven_day: used_percentage (0..100), resets_at (epoch giay) - chi goi Pro/Max, sau phan hoi
#   API dau tien; cua so nao het han thi vang mat. cost.total_cost_usd = uoc tinh phia client (khong phai hoa don).
# Dang ky: ~/.claude/settings.json -> "statusLine": {"type": "command", "command":
#   "python D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/custom/statusline/claude_statusline.py", "refreshInterval": 60}
# Chi chay o CLI terminal (`claude`); panel VS Code khong goi statusline -> o do dung /usage.
# Ghi anh chup cho STLAB Toolhub (studio/toolhub/usage.py) vao %LOCALAPPDATA%/stlab-usage/claude.json. Khong goi mang.
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
G, Y, R, D, X = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"


def left(at):
    if not at:
        return ""
    sec = max(0, int(at - time.time()))
    d, h, m = sec // 86400, sec % 86400 // 3600, sec % 3600 // 60
    return " reset %s" % ("%dd%dh" % (d, h) if d else "%dh%02dm" % (h, m) if h else "%dm" % m)


def color(p):
    return G if p < 60 else Y if p < 85 else R


try:
    j = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")   # -sig: chiu BOM (PowerShell them khi pipe)
except ValueError:
    j = {}
rl = j.get("rate_limits") or {}
if rl.get("five_hour") or rl.get("seven_day"):
    try:
        d = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "stlab-usage")
        os.makedirs(d, exist_ok=True)
        tmp = os.path.join(d, "claude.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"time": time.time(), "rate_limits": {k: rl[k] for k in ("five_hour", "seven_day") if rl.get(k)},
                       "model": (j.get("model") or {}).get("display_name")}, f)
        os.replace(tmp, os.path.join(d, "claude.json"))
    except OSError:
        pass
parts = []
for key, name in (("five_hour", "5h"), ("seven_day", "tuần")):
    w = rl.get(key) or {}
    p = w.get("used_percentage")
    if p is not None:
        parts.append("%s%s %.0f%%%s%s" % (color(p), name, p, X, D + left(w.get("resets_at")) + X))
ctx = (j.get("context_window") or {}).get("used_percentage")
if ctx is not None:
    parts.append("ctx %d%%" % ctx)
cost = (j.get("cost") or {}).get("total_cost_usd")
if cost:
    parts.append(D + "~$%.2f phiên" % cost + X)
print("Claude " + " · ".join(parts) if parts else "Claude (chưa có số hạn mức - gửi 1 tin trước)")
