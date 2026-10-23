"""Trang Sua anh: goi photo-ai/scripts/looklab.py (xem truoc) va develop.py (ap cho ca loat).

Toolhub khong cai Pillow/numpy: moi xu ly anh chay bang Python cua photo-ai (.venv rieng).
Chi DOC thu muc nguon; moi file ghi vao <nguon>-edit/ (lab/ cho xem truoc, xuat-<kieu>/ cho ket qua).
"""
from __future__ import annotations

import json
import re
import subprocess
import threading
import time
from pathlib import Path

from .workspace import ROOT

PHOTO_AI = ROOT / "photo-ai"
PY = PHOTO_AI / ".venv" / "Scripts" / "python.exe"
STATE = PHOTO_AI / ".lab-state.json"  # thu muc anh dung lan truoc (khong len git)
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

_job: dict = {}
_lock = threading.Lock()


def last_src() -> str:
    try:
        return json.loads(STATE.read_text(encoding="utf-8")).get("src", "")
    except (OSError, ValueError):
        return ""


def check_src(s: str) -> Path:
    p = Path((s or "").strip().strip('"'))
    if not p.is_absolute() or not p.is_dir():
        raise ValueError(f"Không có thư mục ảnh: {s}")
    if p.name.endswith("-edit") or ROOT in p.resolve().parents:
        raise ValueError("Chọn thư mục ảnh GỐC (không phải thư mục -edit hay trong workspace)")
    return p


def edit_dir(src: Path) -> Path:
    return src.parent / (src.name + "-edit")


def call(*args: str, timeout: int = 600) -> dict:
    if not PY.exists():
        return {"ok": False, "msg": "Chưa có môi trường photo-ai: chạy `uv sync` trong photo-ai"}
    p = subprocess.run([str(PY), str(PHOTO_AI / "scripts" / "looklab.py"), *args], cwd=PHOTO_AI,
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=timeout, creationflags=NO_WINDOW)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"ok": False, "msg": (p.stderr or p.stdout).strip()[-400:] or f"looklab lỗi ({p.returncode})"}


def looks() -> dict:
    return call("looks")


def photos(src: str) -> dict:
    p = check_src(src)
    STATE.write_text(json.dumps({"src": str(p)}, ensure_ascii=False), encoding="utf-8")
    return call("photos", str(p))


def preview(src: str, photo: str, look: str, local: bool) -> dict:
    if not re.fullmatch(r"[\w.\- ]+", photo) or not re.fullmatch(r"[\w\-]+", look):
        return {"ok": False, "msg": "Tên ảnh/kiểu không hợp lệ"}
    return call("preview", str(check_src(src)), photo, look, *(["--local"] if local else []))


def file_path(src: str, rel: str) -> Path | None:
    """Chi phuc vu .jpg trong lab/ va xuat-*/ cua thu muc -edit."""
    try:
        ed = edit_dir(check_src(src)).resolve()
    except ValueError:
        return None
    p = (ed / rel).resolve()
    first = p.relative_to(ed).parts[0] if ed in p.parents else ""
    if p.suffix.lower() != ".jpg" or not (first == "lab" or first.startswith("xuat-")) or not p.is_file():
        return None
    return p


# ---------- Ap cho ca loat (chay nen) ----------
def out_name(look: str, strength: float, local: bool) -> str:
    return f"xuat-{look}{'-local' if local else ''}-{round(strength * 100)}"


def apply(src: str, look: str, strength: float, local: bool) -> dict:
    s = check_src(src)
    if not re.fullmatch(r"[\w\-]+", look):
        return {"ok": False, "msg": "Kiểu không hợp lệ"}
    strength = min(max(float(strength), 0.0), 1.0)
    with _lock:
        if _job.get("proc") and _job["proc"].poll() is None:
            return {"ok": False, "msg": "Đang chạy một lượt áp dụng, chờ xong đã"}
        ed = edit_dir(s)
        out = ed / out_name(look, strength, local)
        log = ed / "lab" / "ap-dung.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        cmd = [str(PY), str(PHOTO_AI / "scripts" / "develop.py"), str(s), "--out", str(out),
               "--look", look, "--strength", f"{strength:.2f}"]
        if (ed / "cull" / "dat").is_dir():
            cmd += ["--list", str(ed / "cull" / "dat")]
        if local:
            cmd.append("--local")
        fh = open(log, "w", encoding="utf-8")
        proc = subprocess.Popen(cmd, cwd=PHOTO_AI, stdout=fh, stderr=subprocess.STDOUT, creationflags=NO_WINDOW,
                                env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"})
        _job.update(proc=proc, log=log, out=out, src=str(s), started=time.time(), fh=fh)
    return {"ok": True, "msg": f"Đang áp dụng → {out.name}"}


def job() -> dict:
    if not _job:
        return {"state": "none"}
    proc, log, out = _job["proc"], _job["log"], _job["out"]
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    done = re.findall(r"^(\d+)/(\d+) anh", text, re.M)
    i, n = (int(done[-1][0]), int(done[-1][1])) if done else (0, 0)
    code = proc.poll()
    res = {"state": "running" if code is None else ("done" if code == 0 else "error"), "i": i, "n": n,
           "out": str(out), "out_name": out.name, "src": _job["src"], "secs": round(time.time() - _job["started"])}
    if code is not None:
        if not _job["fh"].closed:
            _job["fh"].close()
        qa = re.search(r"QA dat (\d+)/(\d+)", text)
        res["qa"] = qa.group(0).replace("QA dat", "QA đạt") if qa else ""
        res["warn"] = [ln.strip()[2:] for ln in text.splitlines() if ln.strip().startswith("! ")][:20]
        res["sheets"] = sorted(p.name for p in out.glob("contact-*.jpg")) if out.is_dir() else []
        if code != 0:
            res["msg"] = text.strip()[-600:]
    return res


def open_output() -> dict:
    out = _job.get("out")
    if not out or not Path(out).is_dir():
        return {"ok": False, "msg": "Chưa có thư mục kết quả"}
    subprocess.Popen(["explorer", str(out)])
    return {"ok": True, "msg": f"Đã mở {Path(out).name}"}
