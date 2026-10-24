"""Bang "STLab Workflow" (dock ben phai): du an hien tai + 6 buoc quy trinh chuan + trang thai + nhat ky chay nen.

Nut trong bang chi goi lenh FreeCAD (Gui.runCommand) -> 1 cho xu ly, giong het menu/toolbar.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from . import core, runner
from .dialogs import COLOR

STAGES = [
    ("1 · Dự án", [("STLab_NewProject", "Tạo mới"), ("STLab_OpenProject", "Mở dự án"),
                   ("STLab_ProjectFolder", "Thư mục")], []),
    ("2 · Linh kiện", [("STLab_Components", "Thư viện linh kiện")], []),
    ("3 · Thiết kế", [("STLab_Labels", "Kiểm tên Label"), ("STLab_PrintPreview", "Xem hướng in"),
                      ("STLab_Backup", "Sao lưu")], []),
    ("4 · Kiểm tra", [("STLab_CheckFast", "Kiểm nhanh"), ("STLab_CheckFull", "Kiểm đầy đủ"),
                      ("STLab_CheckReport", "Xem lỗi")], ["check"]),
    ("5 · In 3D", [("STLab_ExportStl", "Xuất STL"), ("STLab_Printability", "Khả năng in"),
                   ("STLab_Slice", "Cắt lớp"), ("STLab_PreparePrint", "Chuẩn bị in (cả vòng)"),
                   ("STLab_Plates", "Mở bàn in")], ["export", "slice", "prepare"]),
    ("6 · Tài liệu", [("STLab_Bom", "BOM"), ("STLab_MetricsDiff", "So với commit trước"),
                      ("STLab_AssemblyPdf", "PDF lắp ráp")], ["bom"]),
]
RESULT_NAME = {"check": "Kiểm tra", "export": "Xuất STL", "slice": "Cắt lớp", "prepare": "Chuẩn bị in", "bom": "BOM"}


class WorkflowPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.projects, self._doc_seen = [], None
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)

        top = QtWidgets.QHBoxLayout()
        self.combo = QtWidgets.QComboBox()
        self.combo.setToolTip("Dự án đang làm (tự chọn theo model đang mở)")
        b = QtWidgets.QToolButton()
        b.setText("⟳")
        b.setToolTip("Làm mới danh sách dự án + trạng thái")
        b.clicked.connect(self.reload)
        top.addWidget(self.combo, 1)
        top.addWidget(b)
        lay.addLayout(top)
        self.state = QtWidgets.QLabel()
        self.state.setWordWrap(True)
        lay.addWidget(self.state)

        self.status = {}
        for title, cmds, keys in STAGES:
            g = QtWidgets.QGroupBox(title)
            gl = QtWidgets.QVBoxLayout(g)
            gl.setSpacing(3)
            flow = QtWidgets.QGridLayout()
            for i, (cmd, text) in enumerate(cmds):
                bt = QtWidgets.QPushButton(text)
                bt.setIcon(QtGui.QIcon(core.icon(cmd.split("_", 1)[1])))
                bt.clicked.connect(lambda _=False, c=cmd: Gui.runCommand(c))
                flow.addWidget(bt, i // 2, i % 2)
            gl.addLayout(flow)
            if title.startswith("5"):
                self.auto = QtWidgets.QCheckBox("Tự chuẩn bị in mỗi khi Lưu")
                self.auto.setToolTip("Thay cho watch.py: Lưu model → chạy prepare-print nền")
                gl.addWidget(self.auto)
            for k in keys:
                lb = QtWidgets.QLabel()
                lb.setTextFormat(QtCore.Qt.TextFormat.RichText)
                self.status[k] = lb
                gl.addWidget(lb)
            lay.addWidget(g)

        row = QtWidgets.QHBoxLayout()
        self.busy = QtWidgets.QLabel("Rảnh")
        stop = QtWidgets.QPushButton("Dừng")
        stop.clicked.connect(runner.runner().cancel)
        clear = QtWidgets.QPushButton("Xóa log")
        row.addWidget(self.busy, 1)
        row.addWidget(stop)
        row.addWidget(clear)
        lay.addLayout(row)
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(3000)
        self.log.setFont(QtGui.QFont("Consolas", 8))
        clear.clicked.connect(self.log.clear)
        lay.addWidget(self.log, 1)

        r = runner.runner()
        r.line.connect(self.append)
        r.started.connect(lambda t: self.busy.setText(f"<b>Đang chạy:</b> {t}"))
        r.finished.connect(self._finished)
        self.combo.currentIndexChanged.connect(self.refresh_status)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(1500)
        self.reload()

    # ------------------------------------------------------------ du an
    def reload(self):
        cur = self.current()
        self.projects = core.list_projects()
        self.combo.blockSignals(True)
        self.combo.clear()
        for p in self.projects:
            self.combo.addItem(p.name, str(p.cfg_p))
        self.combo.blockSignals(False)
        if cur:
            self.select(cur)
        self._doc_seen = None
        self.poll()
        self.refresh_status()

    def current(self):
        i = self.combo.currentIndex()
        return self.projects[i] if 0 <= i < len(self.projects) else None

    def select(self, project):
        i = self.combo.findData(str(project.cfg_p))
        if i >= 0 and i != self.combo.currentIndex():
            self.combo.setCurrentIndex(i)

    def poll(self):
        doc = App.ActiveDocument
        name = doc.Name if doc else None
        if name != self._doc_seen:
            self._doc_seen = name
            p = core.project_for_doc(doc)
            if p:
                self.select(p)
        p = self.current()
        if not p:
            self.state.setText("Chưa có dự án – bấm <b>Tạo mới</b>.")
            return
        d = p.is_open()
        if not p.fcstd.exists():
            s = f"<span style='color:{COLOR['WARN']}'>Chưa có model {p.fcstd.name}</span>"
        elif not d:
            s = f"Model {p.fcstd.name} chưa mở"
        elif Gui.getDocument(d.Name).Modified:
            s = (f"<span style='color:{COLOR['WARN']}'>{p.fcstd.name}: có thay đổi CHƯA LƯU</span>"
                 " – kiểm/xuất đọc file đã lưu")
        else:
            s = f"<span style='color:{COLOR['PASS']}'>{p.fcstd.name}: đã lưu</span>"
        self.state.setText(s)

    def refresh_status(self, *_):
        p = self.current()
        res = p.results() if p else {}
        for k, lb in self.status.items():
            if k in res:
                kl, tom, _img = res[k]
                lb.setText(f"{RESULT_NAME[k]}: <b style='color:{COLOR.get(kl, '#000')}'>{kl}</b> · {tom}")
            else:
                lb.setText(f"{RESULT_NAME[k]}: <span style='color:#888'>chưa chạy</span>")

    # ------------------------------------------------------------ log
    def append(self, text):
        self.log.appendPlainText(text)

    def _finished(self, title, code):
        self.busy.setText("Rảnh")
        self.refresh_status()


_dock = None


def panel():
    """-> WorkflowPanel (tao dock lan dau)."""
    global _dock
    mw = Gui.getMainWindow()
    if _dock is None or not _dock.parent():
        _dock = QtWidgets.QDockWidget("STLab Workflow", mw)
        _dock.setObjectName("STLabWorkflow")
        sc = QtWidgets.QScrollArea()
        sc.setWidgetResizable(True)
        sc.setWidget(WorkflowPanel())
        _dock.setWidget(sc)
        mw.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, _dock)
    return _dock.widget().widget()


def show_panel(toggle=False):
    panel()
    if toggle and _dock.isVisible():
        _dock.hide()
    else:
        _dock.show()
        _dock.raise_()


def log(text):
    if _dock is not None:
        panel().append(text)
    App.Console.PrintMessage(f"[STLab] {text}\n")


def auto_on_save():
    return _dock is not None and panel().auto.isChecked()


def current_project():
    """Du an cua model dang mo; khong co -> du an chon trong bang."""
    p = core.project_for_doc(App.ActiveDocument)
    if p:
        return p
    return panel().current() if _dock is not None else None
