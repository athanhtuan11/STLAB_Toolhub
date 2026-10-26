"""Han muc agent AI cho trang chinh (Tuan 2026-10-26: "hien len STLAB Toolhub"). CHI DOC file tren may, khong goi mang.

- Codex (ChatGPT Free): khoi `rate_limits` moi nhat trong ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl (Codex tu ghi
  moi lan chay, ca khi Claude goi qua plugin). Truong nay KHONG co trong docs Codex -> co the doi; doc loi thi bo qua.
- Gemini (agy): anh chup `quota` do custom/statusline/agy_statusline.py ghi vao %LOCALAPPDATA%/stlab-usage/agy.json
  (chi cap nhat khi mo TUI agy; agy goi qua deliberation khong chay statusline).
- Claude Pro: khong co nguon chinh thuc doc tu ngoai -> chi nhac /usage.
"""
import json
import os
import time
from pathlib import Path

CODEX = Path.home() / ".codex" / "sessions"
AGY = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "stlab-usage" / "agy.json"


def _window(minutes):
    if not minutes:
        return ""
    if minutes % 1440 == 0:
        d = minutes // 1440
        return {1: "ngày", 7: "tuần", 30: "30 ngày"}.get(d, f"{d} ngày")
    return f"{minutes // 60} giờ" if minutes % 60 == 0 else f"{minutes} phút"


def _bar(label, used, resets_at=None, reset_in=None):
    if resets_at is None and reset_in is not None:
        resets_at = time.time() + reset_in
    return {"label": label, "used": round(float(used), 1),
            "reset": time.strftime("%d/%m %H:%M", time.localtime(resets_at)) if resets_at else ""}


def _last_rate_limits(path):
    """Dong cuoi co rate_limits trong 1 file rollout (doc tu cuoi, file nho)."""
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if '"rate_limits"' not in line:
            continue
        try:
            j = json.loads(line)
        except ValueError:
            continue
        rl = (j.get("payload") or {}).get("rate_limits") or j.get("rate_limits")
        if isinstance(rl, dict):
            return rl
    return None


def codex():
    out = {"name": "Codex", "plan": "ChatGPT Free", "bars": [], "note": "", "updated": ""}
    try:
        files = sorted(CODEX.glob("*/*/*/rollout-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
    except OSError:
        files = []
    for f in files:
        rl = _last_rate_limits(f)
        if not rl:
            continue
        out["plan"] = "ChatGPT " + str(rl.get("plan_type") or "?").capitalize()
        for key in ("primary", "secondary"):
            w = rl.get(key)
            if isinstance(w, dict) and w.get("used_percent") is not None:
                out["bars"].append(_bar("cửa sổ " + _window(w.get("window_minutes")), w["used_percent"], w.get("resets_at")))
        out["updated"] = time.strftime("%d/%m %H:%M", time.localtime(f.stat().st_mtime))
        break
    if not out["bars"]:
        out["note"] = "Chưa có dữ liệu – dùng Codex 1 lần (/codex:review, ask-gpt)."
    return out


def gemini():
    out = {"name": "Gemini (agy)", "plan": "Google free", "bars": [], "note": "", "updated": ""}
    try:
        j = json.loads(AGY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        out["note"] = ("Chưa có số: agy chỉ báo hạn mức khi mở trong terminal. Gõ agy → đợi dòng "
                       "\"con lai: …\" dưới ô nhập → /exit, rồi tải lại trang.")
        return out
    t = j.get("time", 0)
    for name, q in sorted((j.get("quota") or {}).items()):
        if not isinstance(q, dict) or q.get("disabled") or q.get("remaining_fraction") is None:
            continue
        reset_in = q.get("reset_in_seconds")
        out["bars"].append(_bar(name.replace("_", " "), 100 * (1 - float(q["remaining_fraction"])),
                                t + reset_in if reset_in is not None else None))
    out["plan"] = j.get("plan_tier") or out["plan"]
    out["updated"] = time.strftime("%d/%m %H:%M", time.localtime(t)) if t else ""
    if not out["bars"]:
        out["note"] = "agy chưa báo hạn mức – gõ /usage trong agy."
    return out


def claude():
    return {"name": "Claude", "plan": "Pro", "bars": [], "updated": "",
            "note": "Xem /usage trong Claude Code (không có nguồn đọc từ ngoài)."}


def all_agents():
    return [claude(), codex(), gemini()]
