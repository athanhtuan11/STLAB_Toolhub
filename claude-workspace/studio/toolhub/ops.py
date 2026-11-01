"""Operations center data and event actions."""
import re
import subprocess
import sys
import time
from pathlib import Path
from . import usage
WORKSPACE = Path(__file__).resolve().parents[2]
ORG_TOOLS = WORKSPACE / "tools" / "org"
if str(ORG_TOOLS) not in sys.path:
    sys.path.insert(0, str(ORG_TOOLS))
import events  # noqa: E402
RUNS_DIR = usage._usage_dir() / "delegate-runs"
RUN_RE = re.compile(r"^\d{8}-\d{6}-[a-z0-9-]+$")
def _task(run, result):
    return str(result.get("task") or run.split("-", 2)[-1])
def _seconds(folder):
    try:
        stamp = (folder / "state.json").stat().st_mtime
    except OSError:
        try:
            stamp = time.mktime(time.strptime(folder.name[:15], "%Y%m%d-%H%M%S"))
        except ValueError:
            stamp = folder.stat().st_mtime
    return max(0, int(time.time() - stamp))
def _runs():
    rows = []
    try:
        folders = [p for p in RUNS_DIR.iterdir() if p.is_dir()]
    except OSError:
        return rows
    for folder in folders:
        state = usage._read_json(folder / "state.json")
        result_path = folder / "result.json"
        has_result = result_path.is_file()
        result = usage._read_json(result_path) if has_result else {}
        alive = usage._is_process_alive(state.get("pid"))
        verdict = str(result.get("verdict", "")).upper() if has_result else ""
        row = {"task": _task(folder.name, result), "run": folder.name}
        try:
            modified = max(folder.stat().st_mtime, (folder / ("result.json" if has_result else "state.json")).stat().st_mtime)
        except OSError:
            modified = folder.stat().st_mtime
        if not has_result and alive:
            row.update({"executor": state.get("executor", ""), "seconds": _seconds(folder)})
            col = "dang_chay"
        elif verdict == "PASS":
            row["verdict"], col = verdict, "xong"
        elif verdict == "FAIL" or (not has_result and state and not alive):
            row["verdict"], col = verdict or "FAIL", "loi"
        elif verdict == "ESCALATE":
            row.update({"verdict": verdict, "note": result.get("escalate", "")})
            col = "bao_len"
        else:
            continue
        rows.append((modified, col, row))
    return sorted(rows, key=lambda item: item[0], reverse=True)
def summary():
    approvals = [a for a in events.list_approvals() if a.get("state") == "cho"]
    rows = _runs()
    return {"cho_duyet": len(approvals), "dang_chay": sum(c == "dang_chay" for _, c, _ in rows), "loi": sum(c == "loi" for _, c, _ in rows)}
def data():
    approvals = sorted((a for a in events.list_approvals() if a.get("state") == "cho"), key=lambda a: a.get("id", 0), reverse=True)
    rows = _runs()
    board = {key: [] for key in ("dang_chay", "xong", "loi", "bao_len")}
    for _, col, row in rows:
        board[col].append(row)
    try:
        timeline = events.recent(50)
    except Exception:
        timeline = []
    try:
        proc = subprocess.run(["git", "log", "-10", "--format=%h%x09%ad%x09%s", "--date=format:%Y-%m-%d %H:%M"], cwd=WORKSPACE, capture_output=True, text=True, timeout=5, check=True)
        commits = []
        for line in proc.stdout.splitlines():
            parts = line.split("\t", 2)
            if len(parts) == 3:
                commits.append({"hash": parts[0], "date": parts[1], "subject": parts[2]})
    except (OSError, subprocess.SubprocessError):
        commits = []
    return {"approvals": approvals, "running": board["dang_chay"], "board": {key: values[:20] for key, values in board.items()}, "timeline": timeline, "commits": commits, "summary": summary()}
def timeline_after(after):
    try:
        cursor = int(after)
    except (TypeError, ValueError):
        cursor = 0
    try:
        rows = events.recent(500)
    except Exception:
        rows = []
    return [item for item in rows if int(item.get("id", 0)) > cursor]
