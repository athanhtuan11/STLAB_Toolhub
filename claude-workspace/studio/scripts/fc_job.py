"""Chay script FreeCAD nang trong tien trinh freecadcmd RIENG, chay nen – moi lenh MCP tra loi < 1 s.

Ly do: Claude tren web/app goi may qua "thiet bi tu xa" chi cho moi lenh 60 s; lenh hinh hoc cua FreeCAD
giu GIL nen FreeCAD dang mo dung ca RPC (get_rpc_status cung phai cho). Tien trinh rieng thi khong.

Dung (qua MCP execute_code – chay trong FreeCAD dang mo, chi mat vai ms):
    import runpy; J = runpy.run_path(r"D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/studio/scripts/fc_job.py")
    job = J["start"](r"D:/.../viec.py")          # -> thu muc job, tra ve ngay
    J["status"](job)                               # {"state": "running"|"done"|"failed", "elapsed_s", "log_tail"}
Script viec.py: tu import FreeCAD/Part, tu mo va luu file (doc.saveAs / shape.exportBrep). Xong thi
reload_document (neu ghi de .FCStd dang mo) hoac chen .brep. Tien trinh nay chi doc/ghi file script tu chi dinh.

Ben trong freecadcmd file nay chay voi bien moi truong FC_JOB_DIR (che do "runner").
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

FREECADCMD = r"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe"
JOBS = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "stlab-fc-jobs"


def _write(p: Path, data: dict) -> None:
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def start(script: str) -> str:
    """Khoi chay script trong freecadcmd rieng, tra ve thu muc job ngay lap tuc."""
    src = Path(script)
    if not src.is_file():
        raise FileNotFoundError(script)
    job = JOBS / time.strftime(f"%Y%m%d-%H%M%S-{src.stem}")
    job.mkdir(parents=True, exist_ok=True)
    _write(job / "status.json", {"state": "starting", "script": str(src), "start": time.time()})
    env = dict(os.environ, FC_JOB_DIR=str(job), FC_JOB_SCRIPT=str(src))
    flags = 0x00000008 | 0x00000200 | 0x08000000  # DETACHED_PROCESS | NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    with open(job / "log.txt", "w", encoding="utf-8") as log:
        p = subprocess.Popen([FREECADCMD, str(Path(__file__).resolve())], env=env, stdout=log,
                             stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, creationflags=flags)
    (job / "pid").write_text(str(p.pid))
    return str(job)


def status(job: str, tail: int = 1500) -> dict:
    """Trang thai job; doc file nen khong phu thuoc FreeCAD nao dang ban."""
    d = Path(job)
    st = json.loads((d / "status.json").read_text(encoding="utf-8"))
    st["elapsed_s"] = round((st.get("end") or time.time()) - st["start"], 1)
    log = d / "log.txt"
    if log.exists():
        st["log_tail"] = log.read_text(encoding="utf-8", errors="replace")[-tail:]
    if st["state"] in ("starting", "running") and st["elapsed_s"] > 15:
        pid = (d / "pid").read_text().strip()
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        if pid not in out:
            st["state"] = "failed"
            st["error"] = "tien trinh freecadcmd da thoat ma khong bao xong (crash?) – xem log_tail"
    return st


def _runner() -> None:
    job = Path(os.environ["FC_JOB_DIR"])
    script = os.environ["FC_JOB_SCRIPT"]
    st = json.loads((job / "status.json").read_text(encoding="utf-8"))
    st.update(state="running", pid=os.getpid())
    _write(job / "status.json", st)
    try:
        g = {"__name__": "__main__", "__file__": script, "JOB_DIR": str(job)}
        exec(compile(Path(script).read_text(encoding="utf-8"), script, "exec"), g)
        st.update(state="done")
    except BaseException:
        st.update(state="failed", error=traceback.format_exc()[-3000:])
    st["end"] = time.time()
    _write(job / "status.json", st)
    sys.stdout.flush()
    os._exit(0)  # thoat ngay, khong cho FreeCAD don dep (tranh treo khi thoat)


if os.environ.get("FC_JOB_DIR") and "FreeCAD" in sys.modules:
    _runner()
