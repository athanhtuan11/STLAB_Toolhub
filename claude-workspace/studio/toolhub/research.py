"""Research scout data and actions for the Toolhub page."""
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
SCOUT = WORKSPACE / "tools" / "research-scout"
if str(SCOUT) not in sys.path:
    sys.path.insert(0, str(SCOUT))

import store  # noqa: E402


def _topics():
    try:
        return store.topics()
    except (OSError, ValueError, TypeError):
        return []


def digest():
    try:
        return store.latest_digest()
    except (OSError, ValueError):
        return None


def data(topic=None, status=None):
    try:
        items = store.list_items(topic=topic or None, status=status or None)
    except (OSError, ValueError):
        items = []
    if status is None:
        items = [item for item in items if item.get("status") != "bo-qua"]
    items.sort(key=lambda item: (float(item.get("score") or 0), int(item.get("id") or 0)), reverse=True)
    return {"items": items, "digest": digest(), "topics": _topics()}


def set_status(item_id, status):
    if status not in ("quan-tam", "bo-qua", "moi"):
        return "invalid"
    try:
        if not any(item.get("id") == item_id for item in store.list_items(limit=100000)):
            return "missing"
        return "ok" if store.set_status(item_id, status) else "missing"
    except (OSError, ValueError):
        return "missing"


def scan():
    command = os.environ.get("STLAB_RESEARCH_SCAN_CMD")
    kwargs = {"cwd": str(WORKSPACE), "shell": True} if command else {"cwd": str(WORKSPACE)}
    if not command:
        command = [sys.executable, str(SCOUT / "scan.py")]
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(command, **kwargs)
