"""Trang Du an: nut "Chuan bi in" va "Tu chay khi Luu" cho du an co print/print.yaml (GD D).

Goi tools/robotics-cad/scripts/prepare-print.py / watch.py bang Python di kem FreeCAD (co yaml, matplotlib).
Chi doc ket qua `_prepare-print-result.json` canh print.yaml; anh chi tra file .png ma ket qua tro toi.
Tien trinh chay nen; PID ghi ra file de Toolhub khoi dong lai van biet / tat duoc.
"""
import csv
import json
import subprocess
import time
from pathlib import Path

from .workspace import ROOT

PY = Path(r"C:\Program Files\FreeCAD 1.1\bin\python.exe")
SCRIPTS = ROOT / "tools" / "robotics-cad" / "scripts"
NO_WINDOW = 0x08000000
KIEU = {"run": "prepare-print.py", "watch": "watch.py"}


def cau_hinh(rel):
    p = ROOT / rel / "print" / "print.yaml"
    return p if p.exists() else None


def _pid_file(y, kieu):
    return y.parent / f"_{kieu}.pid"


def _song(y, kieu):
    f = _pid_file(y, kieu)
    if not f.exists():
        return False
    pid = f.read_text().strip()
    # PID Windows duoc cap lai sau khi tien trinh ket thuc -> phai khop CA ten anh (python.exe cua FreeCAD), khong chi PID,
    # neu khong nut "Tat" (taskkill /T /F) co the giet nham tien trinh khac (ra soat 2026-10-26)
    if pid.isdigit():
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                           creationflags=NO_WINDOW)
        for row in csv.reader(r.stdout.splitlines()):
            if len(row) > 1 and row[1] == pid and row[0].lower() == PY.name.lower():
                return True
    f.unlink()
    return False


def trang_thai(rel):
    y = cau_hinh(rel)
    if y is None:
        return None
    kq = y.parent / "_prepare-print-result.json"
    log = y.parent / "_log-run.txt"
    return {
        "ket_qua": json.loads(kq.read_text(encoding="utf-8")) if kq.exists() else None,
        "chay": _song(y, "run"), "theo_doi": _song(y, "watch"),
        "log": log.read_text(encoding="utf-8", errors="replace")[-1500:] if log.exists() else "",
    }


def bat(rel, kieu):
    y = cau_hinh(rel)
    if y is None or kieu not in KIEU:
        raise ValueError("du an khong co print/print.yaml")
    if _song(y, kieu):
        return {"ok": True, "msg": "Đang chạy rồi"}
    if kieu == "run" and _song(y, "watch"):
        pass  # cho phep chay tay khi dang theo doi (theo-doi chi chay khi file doi)
    log = open(y.parent / ("_log-run.txt" if kieu == "run" else "_log-watch.txt"), "w", encoding="utf-8")
    with log:   # tien trinh con giu ban sao handle; cha dong ngay (khong ro handle moi lan chay)
        p = subprocess.Popen([str(PY), str(SCRIPTS / KIEU[kieu]), str(y)], stdout=log, stderr=subprocess.STDOUT,
                             cwd=ROOT, creationflags=NO_WINDOW)
    _pid_file(y, kieu).write_text(str(p.pid))
    return {"ok": True, "msg": ("Đang chuẩn bị in (~1–2 phút)…" if kieu == "run"
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
    """Anh tong-quan cua tang i trong ket qua gan nhat (chi file .png do prepare-print tro toi)."""
    st = trang_thai(rel)
    try:
        p = Path(st["ket_qua"]["tang"][i]["anh"])
    except (TypeError, KeyError, IndexError):
        return None
    ok = p.suffix == ".png" and p.exists() and p.resolve().is_relative_to((ROOT / rel).resolve())  # chi anh trong du an
    return p if ok else None
