"""Han muc agent AI cho trang chinh (Tuan 2026-10-26: "hien len STLAB Toolhub"). CHI DOC file tren may, khong goi mang.

- Codex (ChatGPT Free): khoi `rate_limits` moi nhat trong ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl (Codex tu ghi
  moi lan chay, ca khi Claude goi qua plugin). Truong nay KHONG co trong docs Codex -> co the doi; doc loi thi bo qua.
- Gemini (agy): anh chup `quota` do custom/statusline/agy_statusline.py ghi vao %LOCALAPPDATA%/stlab-usage/agy.json
  (chi cap nhat khi mo TUI agy; agy goi qua deliberation khong chay statusline).
- Claude Pro: anh chup `rate_limits` (5 gio + tuan) do custom/statusline/claude_statusline.py ghi vao
  %LOCALAPPDATA%/stlab-usage/claude.json (chi khi chay `claude` trong terminal - panel VS Code khong goi statusline).
"""
import json
import os
import time
import ctypes
from pathlib import Path

import yaml

def _usage_dir():
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "stlab-usage"


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
        files = sorted((Path.home() / ".codex" / "sessions").glob("*/*/*/rollout-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
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
        j = json.loads((_usage_dir() / "agy.json").read_text(encoding="utf-8"))
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
    out = {"name": "Claude", "plan": "Pro", "bars": [], "updated": "", "note": ""}
    try:
        j = json.loads((_usage_dir() / "claude.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        out["note"] = ("Chưa có số: chạy `claude` trong terminal (statusline ghi hạn mức), "
                       "hoặc xem /usage trong panel VS Code.")
        return out
    t = j.get("time", 0)
    for key, label in (("five_hour", "5 giờ"), ("seven_day", "tuần")):
        w = (j.get("rate_limits") or {}).get(key) or {}
        if w.get("used_percentage") is not None and (w.get("resets_at") or 0) > time.time():
            out["bars"].append(_bar(label, w["used_percentage"], w.get("resets_at")))
    out["updated"] = time.strftime("%d/%m %H:%M", time.localtime(t)) if t else ""
    if not out["bars"]:
        out["note"] = "Ảnh chụp cũ đã qua giờ reset – chạy `claude` trong terminal để cập nhật."
    return out


def all_agents():
    return [claude(), codex(), gemini()]



def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _is_process_alive(pid):
    """Check a Windows process handle without sending a signal to it."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = ctypes.c_void_p
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        code = ctypes.c_ulong()
        try:
            return bool(kernel32.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == 259
        finally:
            kernel32.CloseHandle(handle)
    except (AttributeError, OSError):
        return False


def _date_label(value):
    for fmt, length in (("%Y-%m-%dT%H:%M:%S", 19), ("%Y-%m-%dT%H:%M", 16)):
        try:
            return time.strftime("%d/%m %H:%M", time.strptime(value[:length], fmt))
        except (TypeError, ValueError):
            pass
    return str(value)


def org_board():
    """Build the org dashboard from the workspace ledger and local usage files."""
    workspace = Path(__file__).resolve().parents[2]
    ledger = yaml.safe_load((workspace / "org" / "agents.yaml").read_text(encoding="utf-8")) or {}
    agents = ledger.get("agents", [])
    data_dir = _usage_dir()
    executor_data = _read_json(data_dir / "executors.json")
    stats_data = _read_json(data_dir / "agent-stats.json")
    now = time.time()
    providers = []
    sources = {"claude": ("Claude", claude), "codex": ("Codex", codex),
               "gemini": ("Gemini (agy)", gemini), "opencode": ("OpenCode", None)}
    agent_source = {}
    for agent in agents:
        aid = agent.get("id", "")
        model = str(agent.get("model", "")).lower()
        if agent.get("chi_phi") == "claude-quota":
            source = "claude"
        elif "codex" in aid.lower() or "gpt" in model or "codex" in model:
            source = "codex"
        elif "gemini" in aid.lower() or "agy" in aid.lower() or "gemini" in model:
            source = "gemini"
        elif "opencode" in aid.lower() or "opencode" in model:
            source = "opencode"
        else:
            continue
        agent_source[aid] = source

    def active_until(value):
        if not value:
            return False
        try:
            parsed = time.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")
            return time.mktime(parsed) > now
        except (TypeError, ValueError):
            try:
                from datetime import datetime
                return datetime.fromisoformat(value).timestamp() > now
            except (TypeError, ValueError, OverflowError):
                return False

    for source, (name, getter) in sources.items():
        usage = getter() if getter else {"name": name, "plan": "Zen free", "bars": [],
                                         "note": "Zen free – chưa có số hạn mức", "updated": ""}
        members = [a["id"] for a in agents if agent_source.get(a.get("id")) == source]
        limits = [executor_data.get(aid, {}).get("limited_until") for aid in members
                  if isinstance(executor_data.get(aid), dict)]
        latest = max((value for value in limits if active_until(value)), default="")
        providers.append({"id": source, "name": usage.get("name", name), "plan": usage.get("plan", ""),
                          "bars": usage.get("bars", []), "note": usage.get("note", ""),
                          "updated": usage.get("updated", ""), "agents": members,
                          "limited_until": _date_label(latest) if latest else ""})

    tiers = []
    for tier, label in ((0, "Giám đốc"), (1, "Quản lý"), (2, "Nhân viên"), ("tu-van", "Tư vấn")):
        rows = []
        for agent in agents:
            if agent.get("tang") != tier:
                continue
            aid = agent.get("id", "")
            status = "nghi" if agent.get("trang_thai") == "nghi" else "thu-viec" if agent.get("trang_thai") == "thu-viec" else "san-sang"
            executor = executor_data.get(aid, {})
            until = executor.get("limited_until") if isinstance(executor, dict) else None
            if active_until(until):
                status = "het-han-muc"
            status_text = ("Nghỉ" if status == "nghi" else "Thử việc" if status == "thu-viec" else
                           "Hết hạn mức tới " + _date_label(until) if status == "het-han-muc" else "Sẵn sàng")
            row = {"id": aid, "chuc_danh": agent.get("chuc_danh", ""), "model": agent.get("model", ""),
                   "chi_phi": agent.get("chi_phi", ""), "ky_nang": agent.get("ky_nang", []),
                   "bao_cao_cho": agent.get("bao_cao_cho", ""), "status": status, "status_text": status_text}
            stats = stats_data.get(aid)
            if isinstance(stats, dict):
                row["stats"] = dict(stats)
                rounds = stats.get("rounds", 0)
                if rounds:
                    row["stats"]["pass_rate"] = stats.get("gate_pass", 0) / rounds
            rows.append(row)
        tiers.append({"id": tier, "label": label, "agents": rows})

    attention = []
    runs = data_dir / "delegate-runs"
    if runs.is_dir():
        for run_dir in sorted(runs.iterdir()):
            if not run_dir.is_dir() or (run_dir / "result.json").exists():
                continue
            state = _read_json(run_dir / "state.json")
            if not _is_process_alive(state.get("pid")):
                run_name = run_dir.name.split("-", 2)[-1]
                attention.append({"level": "bad", "text": f"Việc {run_name} bị cắt ngang – chạy `python tools/delegate/delegate.py --resume {run_name}`"})
    for aid, entry in executor_data.items():
        if isinstance(entry, dict) and active_until(entry.get("limited_until")):
            attention.append({"level": "warn", "text": f"{aid} hết hạn mức tới {_date_label(entry['limited_until'])}"})
    return {"providers": providers, "tiers": tiers, "attention": attention}
