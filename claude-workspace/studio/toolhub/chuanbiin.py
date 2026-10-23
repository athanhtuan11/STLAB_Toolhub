"""Trang Du an: nut "Chuan bi in" va "Tu chay khi Luu" cho du an co in_3d/ban-in.yaml (GD D).

Goi maker/robotics-cad/scripts/chuan-bi-in.py / theo-doi.py bang Python di kem FreeCAD (co yaml, matplotlib).
Chi doc ket qua `_ket-qua-chuan-bi-in.json` canh ban-in.yaml; anh chi tra file .png ma ket qua tro toi.
Tien trinh chay nen; PID ghi ra file de Toolhub khoi dong lai van biet / tat duoc.
"""
import json
import subprocess
import time
from pathlib import Path

from .workspace import ROOT

PY = Path(r"C:\Program Files\FreeCAD 1.1\bin\python.exe")
SCRIPTS = ROOT / "maker" / "robotics-cad" / "scripts"
NO_WINDOW = 0x08000000
KIEU = {"chay": "chuan-bi-in.py", "theo-doi": "theo-doi.py"}


def cau_hinh(rel):
    p = ROOT / rel / "in_3d" / "ban-in.yaml"
    return p if p.exists() else None


def _pid_file(y, kieu):
    return y.parent / f"_{kieu}.pid"


def _song(y, kieu):
    f = _pid_file(y, kieu)
    if not f.exists():
        return False
    pid = f.read_text().strip()
    r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True,
                       creationflags=NO_WINDOW)
    if pid in r.stdout:
        return True
    f.unlink()
    return False


def trang_thai(rel):
    y = cau_hinh(rel)
    if y is None:
        return None
    kq = y.parent / "_ket-qua-chuan-bi-in.json"
    log = y.parent / "_log-chay.txt"
    return {
        "ket_qua": json.loads(kq.read_text(encoding="utf-8")) if kq.exists() else None,
        "chay": _song(y, "chay"), "theo_doi": _song(y, "theo-doi"),
        "log": log.read_text(encoding="utf-8", errors="replace")[-1500:] if log.exists() else "",
    }


def bat(rel, kieu):
    y = cau_hinh(rel)
    if y is None or kieu not in KIEU:
        raise ValueError("du an khong co in_3d/ban-in.yaml")
    if _song(y, kieu):
        return {"ok": True, "msg": "Đang chạy rồi"}
    if kieu == "chay" and _song(y, "theo-doi"):
        pass  # cho phep chay tay khi dang theo doi (theo-doi chi chay khi file doi)
    log = open(y.parent / ("_log-chay.txt" if kieu == "chay" else "_log-theo-doi.txt"), "w", encoding="utf-8")
    p = subprocess.Popen([str(PY), str(SCRIPTS / KIEU[kieu]), str(y)], stdout=log, stderr=subprocess.STDOUT,
                         cwd=ROOT, creationflags=NO_WINDOW)
    _pid_file(y, kieu).write_text(str(p.pid))
    return {"ok": True, "msg": ("Đang chuẩn bị in (~1–2 phút)…" if kieu == "chay"
                                else "Bật tự chạy khi Lưu file FreeCAD") + f" [{time.strftime('%H:%M:%S')}]"}


def tat(rel, kieu):
    y = cau_hinh(rel)
    if y is None or not _song(y, kieu):
        return {"ok": True, "msg": "Không chạy"}
    pid = _pid_file(y, kieu).read_text().strip()
    subprocess.run(["taskkill", "/PID", pid, "/T", "/F"], capture_output=True, creationflags=NO_WINDOW)
    _pid_file(y, kieu).unlink(missing_ok=True)
    return {"ok": True, "msg": "Đã tắt"}


def anh(rel, i):
    """Anh tong-quan cua tang i trong ket qua gan nhat (chi file .png do chuan-bi-in tro toi)."""
    st = trang_thai(rel)
    try:
        p = Path(st["ket_qua"]["tang"][i]["anh"])
    except (TypeError, KeyError, IndexError):
        return None
    return p if p.suffix == ".png" and p.exists() else None
