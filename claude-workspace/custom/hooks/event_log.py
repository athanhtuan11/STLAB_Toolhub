# Hook ghi su kien cho Trung tam dieu hanh Toolhub (Tuan duyet 2026-10-27, docs/reports/ops-center-design.md).
# File mong: logic o tools/org/events.py hook_main(). KHONG luu noi dung prompt/ma – chi tieu de ngan + ten file.
# Dang ky: <repo>/.claude/settings.json – SessionStart, UserPromptSubmit, PostToolUse (async), SubagentStop, Stop,
# Notification. Moi loi -> im lang, exit 0 (khong bao gio lam hong phien Claude).
import os
import sys

try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "org"))
    import events
    events.hook_main()
except Exception:
    pass
sys.exit(0)
