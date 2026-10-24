"""Chay script pipeline (check.py, slice.py, ...) trong TIEN TRINH RIENG bang QProcess -> FreeCAD khong bi treo.

Moi lan chi 1 viec (cac script ghi chung thu muc ket qua). Viec moi khi dang ban -> xep hang.
Log day ra qua signal `line`; xong -> signal `finished(ten, exit_code)`.
"""

import re

from PySide import QtCore

from . import core

# dong nhieu cua freecadcmd (tien do mo file, banner, loi nap addon RobotCAD luc khoi dong) -> khong dua vao log
NOISE = re.compile(r"^\s*\(\d+ %\)\s*$|^Importing project files|^Postprocessing|^FreeCAD \d|^\(C\) 20\d\d|"
                   r"LGPL2\+|^Interlocking laser cut|ROS_DISTRO|^ROS2 was not detected|freecad\.robotcad|"
                   r"InitApplications|^saving.+$|File \"<(string|frozen os)>\"|add_dll_directory|^-{20,}$")


class Job:
    def __init__(self, title, program, args, project=None, after=None, echo=True):
        self.title, self.program, self.args = title, str(program), [str(a) for a in args]
        self.project, self.after, self.echo = project, after, echo  # echo=False: khong day log, after tu tom tat
        self.output = []


class Runner(QtCore.QObject):
    line = QtCore.Signal(str)
    started = QtCore.Signal(str)
    finished = QtCore.Signal(str, int)

    def __init__(self):
        super().__init__()
        self.queue, self.job, self.proc = [], None, None

    def busy(self):
        return self.job is not None

    def submit(self, job):
        if any(j.title == job.title for j in self.queue) or (self.job and self.job.title == job.title):
            self.line.emit(f"· {job.title}: đã có trong hàng chờ")
            return
        self.queue.append(job)
        if not self.busy():
            self._next()
        else:
            self.line.emit(f"· {job.title}: xếp hàng (đang chạy {self.job.title})")

    def cancel(self):
        self.queue.clear()
        if self.proc is not None:
            self.line.emit("· Dừng theo yêu cầu")
            self.proc.kill()

    def _next(self):
        if not self.queue:
            return
        self.job = self.queue.pop(0)
        p = QtCore.QProcess(self)
        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        env.remove("PYTHONHOME")
        env.remove("PYTHONPATH")
        p.setProcessEnvironment(env)
        p.setWorkingDirectory(str(core.RCAD))
        p.setProcessChannelMode(QtCore.QProcess.ProcessChannelMode.MergedChannels)
        p.readyReadStandardOutput.connect(self._read)
        p.finished.connect(self._done)
        p.errorOccurred.connect(self._error)
        self.proc, self._buf = p, ""
        self.started.emit(self.job.title)
        self.line.emit(f"▶ {self.job.title}")
        self._t = QtCore.QElapsedTimer()
        self._t.start()
        p.start(self.job.program, self.job.args)

    def _read(self):
        data = self._buf + bytes(self.proc.readAllStandardOutput()).decode("utf-8", "replace")
        *lines, self._buf = re.split(r"[\r\n]+", data)  # giu phan dong chua xong cho lan doc sau
        self._emit(lines)

    def _emit(self, lines):
        for ln in lines:
            if not ln.strip() or NOISE.search(ln.strip()):
                continue
            if ln.startswith("Traceback") and not self.job.output:  # loi nap addon luc freecadcmd khoi dong
                continue
            self.job.output.append(ln)
            if self.job.echo:
                self.line.emit(ln)

    def _error(self, err):
        if err == QtCore.QProcess.ProcessError.FailedToStart:
            self.line.emit(f"✗ Không chạy được {self.job.program}")
            self._done(-1, None)

    def _done(self, code, _status=None):
        if self.job is None:
            return
        self._emit([self._buf])
        job, s = self.job, self._t.elapsed() / 1000
        self.job, self.proc = None, None
        self.line.emit(f"{'✓' if code == 0 else '✗'} {job.title}: exit {code}, {s:.0f} s")
        self.finished.emit(job.title, code)
        if job.after:
            try:
                job.after(code)
            except Exception as e:  # loi hien thi ket qua khong duoc lam ket hang
                self.line.emit(f"✗ hiển thị kết quả lỗi: {e}")
        self._next()


_runner = None


def runner():
    global _runner
    if _runner is None:
        _runner = Runner()
    return _runner


# ---------------------------------------------------------------- lenh chuan cua pipeline

def job_check(p, mode="fast", after=None):
    args = ["--pass", p.fcstd, *p.check_args()] + (["mode=full"] if mode == "full" else [])
    return Job(f"Kiểm tra {'đầy đủ' if mode == 'full' else 'nhanh'} – {p.name}", core.FCC,
               [core.SCRIPTS / "check.py", *args], p, after)


def job_export(p, after=None):
    return Job(f"Xuất STL – {p.name}", core.FCC, [core.SCRIPTS / "export-stl.py", "--pass", p.cfg_p], p, after)


def job_printability(p, after=None):
    return Job(f"Khả năng in (STL) – {p.name}", core.PY, [core.SCRIPTS / "printability.py", p.stl_dir], p, after,
               echo=False)


def job_slice(p, after=None):
    return Job(f"Cắt lớp Bambu – {p.name}", core.PY, [core.SCRIPTS / "slice.py", p.cfg_p], p, after)


def job_prepare(p, force=False, after=None):
    return Job(f"Chuẩn bị in – {p.name}", core.PY,
               [core.SCRIPTS / "prepare-print.py", p.cfg_p] + (["force"] if force else []), p, after)


def job_metrics(p, after=None):
    return Job(f"Chỉ số hình học – {p.name}", core.FCC, [core.SCRIPTS / "metrics.py", "--pass", p.cfg_p], p, after)


def job_metrics_diff(p, after=None):
    return Job(f"So với commit trước – {p.name}", core.PY, [core.SCRIPTS / "metrics.py", "diff", p.cfg_p], p, after)


def job_bom(p, after=None):
    return Job(f"BOM – {p.name}", core.PY, [core.SCRIPTS / "bom.py", p.cfg_p], p, after)


def job_assembly_pdf(p, after=None):
    return Job(f"PDF lắp ráp – {p.name}", core.PY, [core.SCRIPTS / "assembly-pdf.py", p.dir / "ASSEMBLY.md"], p, after)
