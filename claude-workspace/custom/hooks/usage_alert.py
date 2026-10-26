# Hook Claude Code (Tuan 2026-10-26, phuong an 1 "dung do co san" - docs/reports/ai-resource-management-oss.md):
#   StopFailure "rate_limit"          -> ghi log + bong bong thong bao Windows
#   Notification quota_auto_resume_*  -> ghi log
# Doc JSON hook tu stdin. Chi ghi file cuc bo, khong goi mang. Log: ~/.claude/usage-log/rate-limit.log
# Python thay .ps1: Windows dang o ExecutionPolicy mac dinh (chan file .ps1) - khong noi chinh sach.
# Dang ky trong ~/.claude/settings.json (hooks); go: xoa 2 muc hook do.
import datetime
import json
import os
import subprocess
import sys

TOAST = r"""
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon = [System.Drawing.SystemIcons]::Warning
$n.Visible = $true
$n.ShowBalloonTip(10000, 'Claude cham han muc', 'Chuyen viec chu sang doc-writer / ask-gemini. Xem /usage de biet gio reset.', 'Warning')
Start-Sleep -Seconds 8
$n.Dispose()
"""

try:
    j = json.loads(sys.stdin.read() or "{}")
except ValueError:
    j = {}
evt = j.get("hook_event_name", "?")
kind = j.get("error") or j.get("notification_type") or "?"
d = os.path.join(os.path.expanduser("~"), ".claude", "usage-log")
os.makedirs(d, exist_ok=True)
with open(os.path.join(d, "rate-limit.log"), "a", encoding="utf-8") as f:
    f.write("%s\t%s\t%s\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), evt, kind, j.get("cwd", "")))
if evt == "StopFailure" and "--no-toast" not in sys.argv:
    subprocess.run(["powershell.exe", "-NoProfile", "-Command", TOAST], check=False)
