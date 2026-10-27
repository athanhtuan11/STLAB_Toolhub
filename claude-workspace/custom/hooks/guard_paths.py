# Hook PreToolUse "hang rao" (Tuan 2026-10-27): chan/hoi khi phien Claude hoac agent ghi vao duong dan nhay cam.
#   Doc JSON hook tu stdin; danh sach lay tu org/policy.yaml muc hang_rao (cam -> deny, hoi -> ask).
#   Chi xet Edit/Write/MultiEdit/NotebookEdit (lenh Bash KHONG duoc xet – executor da co kiem rieng trong delegate.py).
#   Dang ky: <repo>/.claude/settings.json -> hooks.PreToolUse, matcher "Edit|Write|MultiEdit|NotebookEdit".
#   Loi doc policy -> dung danh sach mac dinh ben duoi (khong mo toang hang rao).
import fnmatch
import json
import os
import sys

WS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEFAULT = {"cam": ["community/*/*", "*.FCStd", "*.env", ".env"],
           "hoi": ["org/*", "*/print.yaml", "print.yaml", "stlab/parent-reports/*"]}
TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def rules():
    try:
        import yaml
        r = yaml.safe_load(open(os.path.join(WS, "org", "policy.yaml"), encoding="utf-8"))["hang_rao"]
        return {"cam": list(r.get("cam") or []), "hoi": list(r.get("hoi") or [])}
    except Exception:
        return DEFAULT


def match(rel, pats):
    return next((p for p in pats if fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p)), None)


def decide(event):
    if event.get("tool_name") not in TOOLS:
        return None
    ti = event.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path")
    if not path:
        return None
    try:
        rel = os.path.relpath(os.path.abspath(path), WS).replace("\\", "/")
    except ValueError:                                  # khac o dia (vd C:) -> ngoai workspace
        return None
    if rel.startswith(".."):                            # ngoai claude-workspace: khong xet
        return None
    r = rules()
    p = match(rel, r["cam"])
    if p:
        return "deny", f"Hàng rào STLab: không được ghi `{rel}` (mẫu `{p}`, org/policy.yaml). Báo lên trên nếu thật sự cần."
    p = match(rel, r["hoi"])
    if p:
        return "ask", f"Hàng rào STLab: `{rel}` cần Tuan duyệt (mẫu `{p}`, org/policy.yaml)."
    return None


def main():
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    except ValueError:
        return
    d = decide(event)
    if d:
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": d[0],
                                      "permissionDecisionReason": d[1]}}
        sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False).encode("utf-8"))


if __name__ == "__main__":
    main()
