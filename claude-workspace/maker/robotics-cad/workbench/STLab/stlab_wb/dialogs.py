"""Hop thoai cua workbench STLab (PySide). Moi hop thoai doc/ghi qua core.py, khong tu tinh lai logic pipeline."""

import json
import os
import re
from pathlib import Path

import FreeCAD as App
import FreeCADGui as Gui
import yaml
from PySide import QtCore, QtGui, QtWidgets

from . import core

MW = Gui.getMainWindow


def _colors():
    """Mau trang thai tu studio/design/tokens.json, bo sang/toi theo giao dien FreeCAD dang dung."""
    t = core.tokens()
    win = QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Window)
    m = t["dark" if win.lightness() < 128 else "light"]
    return {**{k: m[v] for k, v in t["status"].items()}, "TEXT": m["text"], "MUTED": m["muted"]}


COLOR = _colors()


def open_path(p):
    os.startfile(str(p))


def select_labels(labels, doc=None):
    doc = doc or App.ActiveDocument
    if doc is None:
        return 0
    Gui.Selection.clearSelection()
    n = 0
    for lb in labels:
        for o in doc.getObjectsByLabel(lb):
            Gui.Selection.addSelection(o)
            n += 1
    if n:
        Gui.SendMsgToActiveView("ViewSelection")
    return n


def _table(headers):
    t = QtWidgets.QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
    t.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    t.verticalHeader().setVisible(False)
    t.horizontalHeader().setStretchLastSection(True)
    return t  # bat sort SAU khi chen dong (dang sort ma chen -> lech hang)


def _item(text, color=None, data=None):
    it = QtWidgets.QTableWidgetItem(str(text))
    if color:
        it.setForeground(QtGui.QColor(color))
    if data is not None:
        it.setData(QtCore.Qt.ItemDataRole.UserRole, data)
    return it


# ---------------------------------------------------------------- xem anh / van ban

class ImageViewer(QtWidgets.QDialog):
    """Xem anh ket qua (overview.png, print-overview.png...) - Tuan duyet bang anh."""

    def __init__(self, images, title="Kết quả"):
        super().__init__(MW())
        self.setWindowTitle(title)
        self.resize(1100, 800)
        lay = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget()
        for p in images:
            p = Path(p)
            if not p.exists():
                continue
            sc = QtWidgets.QScrollArea()
            lb = QtWidgets.QLabel()
            pm = QtGui.QPixmap(str(p))
            lb.setPixmap(pm.scaledToWidth(min(pm.width(), 1050), QtCore.Qt.TransformationMode.SmoothTransformation))
            sc.setWidget(lb)
            tabs.addTab(sc, p.name)
        lay.addWidget(tabs)
        row = QtWidgets.QHBoxLayout()
        if images:
            b = QtWidgets.QPushButton("Mở thư mục")
            b.clicked.connect(lambda: open_path(Path(images[0]).parent))
            row.addWidget(b)
        row.addStretch()
        close = QtWidgets.QPushButton("Đóng")
        close.clicked.connect(self.close)
        row.addWidget(close)
        lay.addLayout(row)


class TextViewer(QtWidgets.QDialog):
    def __init__(self, title, text, markdown=False, path=None):
        super().__init__(MW())
        self.setWindowTitle(title)
        self.resize(900, 700)
        lay = QtWidgets.QVBoxLayout(self)
        tb = QtWidgets.QTextBrowser()
        tb.setOpenExternalLinks(True)
        if markdown:
            tb.setMarkdown(text)
        else:
            tb.setPlainText(text)
        lay.addWidget(tb)
        row = QtWidgets.QHBoxLayout()
        if path:
            b = QtWidgets.QPushButton("Mở file")
            b.clicked.connect(lambda: open_path(path))
            row.addWidget(b)
        row.addStretch()
        close = QtWidgets.QPushButton("Đóng")
        close.clicked.connect(self.close)
        row.addWidget(close)
        lay.addLayout(row)


def show(dlg):
    dlg.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
    dlg.show()
    return dlg


# ---------------------------------------------------------------- 1. du an

class NewProjectDialog(QtWidgets.QDialog):
    """Tao du an tu project-template (nhu lenh /new-project): maker/<name>/ voi freecad/ + print/."""

    def __init__(self):
        super().__init__(MW())
        self.setWindowTitle("STLab – Tạo dự án mới")
        self.project = None
        f = QtWidgets.QFormLayout(self)
        self.name = QtWidgets.QLineEdit()
        self.name.setPlaceholderText("vd. line-follower")
        self.desc = QtWidgets.QLineEdit()
        self.desc.setPlaceholderText("Mô tả 1 dòng (tiếng Việt)")
        self.model = QtWidgets.QCheckBox("Tạo file model trống và mở luôn")
        self.model.setChecked(True)
        self.hint = QtWidgets.QLabel()
        self.hint.setWordWrap(True)
        f.addRow("Tên (tiếng Anh, kebab-case)", self.name)
        f.addRow("Mô tả", self.desc)
        f.addRow(self.model)
        f.addRow(self.hint)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok
                                        | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.create)
        bb.rejected.connect(self.reject)
        f.addRow(bb)
        self.ok = bb.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.name.textChanged.connect(self.validate)
        self.validate()

    def validate(self):
        n = self.name.text().strip()
        if not n:
            msg, ok = "Nhập tên dự án.", False
        elif not core.PROJECT_NAME.match(n):
            msg, ok = "Chỉ chữ thường a-z, số, dấu '-' (kebab-case, tiếng Anh).", False
        elif (core.MAKER / n).exists():
            msg, ok = f"maker/{n}/ đã tồn tại – chọn tên khác (không ghi đè).", False
        else:
            msg, ok = f"Sẽ tạo maker/{n}/ (freecad/ + print/), model freecad/{n.replace('-', '_')}.FCStd", True
        self.hint.setText(msg)
        self.ok.setEnabled(ok)

    def create(self):
        try:
            self.project = core.new_project(self.name.text().strip(), self.desc.text().strip(), self.model.isChecked())
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "STLab", str(e))
            return
        self.accept()


class OpenProjectDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__(MW())
        self.setWindowTitle("STLab – Dự án")
        self.resize(820, 420)
        lay = QtWidgets.QVBoxLayout(self)
        self.t = _table(["Dự án", "Model", "Chuẩn bị in gần nhất", "Kết luận"])
        lay.addWidget(self.t)
        self.projects = core.list_projects()
        for p in self.projects:
            r = self.t.rowCount()
            self.t.insertRow(r)
            res = p.results().get("prepare", ("–", "chưa chạy", ""))
            self.t.setItem(r, 0, _item(p.name, data=str(p.cfg_p)))
            self.t.setItem(r, 1, _item(p.fcstd.name if p.fcstd.exists() else f"(chưa có) {p.fcstd.name}",
                                       None if p.fcstd.exists() else COLOR["WARN"]))
            self.t.setItem(r, 2, _item(res[1]))
            self.t.setItem(r, 3, _item(res[0], COLOR.get(res[0])))
        self.t.setSortingEnabled(True)
        self.t.resizeColumnsToContents()
        self.t.doubleClicked.connect(self.open_model)
        row = QtWidgets.QHBoxLayout()
        for text, fn in (("Mở model", self.open_model), ("Mở thư mục", self.open_dir), ("Đóng", self.close)):
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        lay.addLayout(row)

    def current(self):
        r = self.t.currentRow()
        if r < 0:
            return None
        cp = self.t.item(r, 0).data(QtCore.Qt.ItemDataRole.UserRole)
        return next(p for p in self.projects if str(p.cfg_p) == cp)

    def open_model(self):
        p = self.current()
        if not p:
            return
        if not p.fcstd.exists():
            QtWidgets.QMessageBox.information(self, "STLab",
                                              f"Chưa có {p.fcstd}.\nDựng model rồi Lưu đúng đường dẫn này.")
            return
        d = p.is_open()
        if d:  # da mo -> chuyen sang cua so 3D cua no
            mdi = MW().findChild(QtWidgets.QMdiArea)
            for w in (mdi.subWindowList() if mdi else []):
                if w.windowTitle().startswith(d.Label):
                    mdi.setActiveSubWindow(w)
                    break
        else:
            App.openDocument(str(p.fcstd))
        self.close()

    def open_dir(self):
        p = self.current()
        if p:
            open_path(p.dir)


# ---------------------------------------------------------------- 2. linh kien

class ComponentBrowser(QtWidgets.QDialog):
    """Thu vien linh kien (library/components.yaml) -> chen STEP vao model voi Label dung quy uoc CB_/LK_."""

    def __init__(self):
        super().__init__(MW())
        self.setWindowTitle("STLab – Thư viện linh kiện")
        self.resize(1100, 640)
        cat = yaml.safe_load(core.CATALOG.read_text(encoding="utf-8"))
        self.roots = {k: core.WS / v for k, v in (cat.get("library_roots") or {}).items()}
        self.root = core.WS / cat.get("library_root", "community/freecad-library")
        self.items = cat.get("components", [])
        lay = QtWidgets.QHBoxLayout(self)
        left = QtWidgets.QVBoxLayout()
        top = QtWidgets.QHBoxLayout()
        self.kind = QtWidgets.QComboBox()
        self.kind.addItem("Tất cả loại", "")
        for k in sorted({c.get("loai", "?") for c in self.items}):
            self.kind.addItem(k, k)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Tìm (tên, id, thông số)…")
        top.addWidget(self.kind)
        top.addWidget(self.search, 1)
        left.addLayout(top)
        self.t = _table(["id", "Tên", "Loại", "Hộp bao (mm)", "Model"])
        left.addWidget(self.t, 1)
        lay.addLayout(left, 3)
        right = QtWidgets.QVBoxLayout()
        self.info = QtWidgets.QTextBrowser()
        self.info.setOpenExternalLinks(True)
        right.addWidget(self.info, 1)
        self.label = QtWidgets.QLineEdit()
        right.addWidget(QtWidgets.QLabel("Label khi chèn (CB_ = CyberBrick, LK_ = linh kiện mua khác):"))
        right.addWidget(self.label)
        row = QtWidgets.QHBoxLayout()
        self.ins = QtWidgets.QPushButton("Chèn vào model")
        self.ins.clicked.connect(self.insert)
        b = QtWidgets.QPushButton("Mở thư mục model")
        b.clicked.connect(lambda: self.path() and open_path(self.path().parent))
        row.addWidget(self.ins)
        row.addWidget(b)
        right.addLayout(row)
        lay.addLayout(right, 2)
        self.kind.currentIndexChanged.connect(self.fill)
        self.search.textChanged.connect(self.fill)
        self.t.itemSelectionChanged.connect(self.detail)
        self.t.doubleClicked.connect(self.insert)
        self.fill()

    def path(self, c=None):
        c = c or self.current()
        if not c or not c.get("model"):
            return None
        return (self.roots.get(c.get("thu_vien"), self.root) / c["model"])

    def current(self):
        r = self.t.currentRow()
        if r < 0:
            return None
        cid = self.t.item(r, 0).data(QtCore.Qt.ItemDataRole.UserRole)
        return next((c for c in self.items if c["id"] == cid), None)

    def fill(self):
        k, q = self.kind.currentData(), self.search.text().strip().lower()
        self.t.setSortingEnabled(False)
        self.t.setRowCount(0)
        for c in self.items:
            if k and c.get("loai") != k:
                continue
            if q and q not in json.dumps(c, ensure_ascii=False).lower():
                continue
            r = self.t.rowCount()
            self.t.insertRow(r)
            p = self.path(c)
            ok = p is not None and p.exists()
            self.t.setItem(r, 0, _item(c["id"], data=c["id"]))
            self.t.setItem(r, 1, _item(c.get("ten", "")))
            self.t.setItem(r, 2, _item(c.get("loai", "")))
            self.t.setItem(r, 3, _item(" × ".join(f"{v:g}" for v in c.get("bbox_mm", []))))
            self.t.setItem(r, 4, _item("có" if ok else "thiếu file", None if ok else COLOR["WARN"]))
        self.t.setSortingEnabled(True)
        self.t.resizeColumnsToContents()

    def detail(self):
        c = self.current()
        if not c:
            return
        h = [f"<h3>{c.get('ten', c['id'])}</h3><p><b>id:</b> {c['id']} · <b>loại:</b> {c.get('loai', '')}</p>"]
        if c.get("bbox_mm"):
            h.append(f"<p><b>Hộp bao (đo từ model):</b> {' × '.join(f'{v:g}' for v in c['bbox_mm'])} mm</p>")
        if c.get("dung_tu_ban_ve"):
            h.append(f"<p style='color:{COLOR['WARN']}'>Dựng từ bản vẽ: mặt bằng đúng, chiều cao cổng/header là ƯỚC TÍNH → "
                     "chừa khe ≥ 1 mm, đo hàng thật trước khi in hộp.</p>")
        if c.get("thong_so"):
            h.append("<table border=0 cellspacing=2>" + "".join(
                f"<tr><td><b>{k}</b></td><td>{v}</td></tr>" for k, v in c["thong_so"].items()) + "</table>")
        if c.get("todo"):
            h.append("<p><b>TODO:</b> " + "; ".join(map(str, c["todo"])) + "</p>")
        if c.get("nguon"):
            h.append("<p><b>Nguồn:</b><br>" + "<br>".join(f"<a href='{u}'>{u}</a>" for u in c["nguon"]) + "</p>")
        p = self.path(c)
        h.append(f"<p><small>{p if p else 'không có model'}</small></p>")
        self.info.setHtml("".join(h))
        pre = "CB_" if c.get("loai") == "cyberbrick" else "LK_"
        cid = re.sub(r"^cb-", "", c["id"]) if pre == "CB_" else c["id"]
        self.label.setText(pre + re.sub(r"[^A-Za-z0-9]+", "_", cid).strip("_"))
        self.ins.setEnabled(bool(p and p.exists()))

    def insert(self):
        c, p = self.current(), self.path()
        if not c or not p or not p.exists():
            QtWidgets.QMessageBox.information(self, "STLab", "Chưa có file model. Tải thư viện theo docs/COMMUNITY.md.")
            return
        doc = App.ActiveDocument or App.newDocument()
        import Part
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            doc.openTransaction(f"Chèn {c['id']}")
            sh = Part.read(str(p))
            bb = App.BoundBox()
            for x in core.parts(doc):
                bb.add(x.Shape.BoundBox)
            if bb.isValid():  # dat canh model (cach 10 mm theo X), khong chong len goc toa do
                b = sh.BoundBox
                sh.translate(App.Vector(bb.XMax + 10 - b.XMin, bb.Center.y - b.Center.y, bb.ZMin - b.ZMin))
            o = doc.addObject("Part::Feature", self.label.text().strip() or c["id"])
            o.Label = self.label.text().strip() or c["id"]
            o.Shape = sh
            o.addProperty("App::PropertyString", "ComponentId", "STLab", "id trong components.yaml")
            o.addProperty("App::PropertyString", "ComponentSource", "STLab", "file model")
            o.ComponentId, o.ComponentSource = c["id"], str(p)
            doc.commitTransaction()
            doc.recompute()
            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(o)
            Gui.SendMsgToActiveView("ViewSelection")
        except Exception as e:
            doc.abortTransaction()
            QtWidgets.QMessageBox.warning(self, "STLab", f"Không chèn được: {e}")
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()


# ---------------------------------------------------------------- 3. thiet ke: kiem ten Label

class LabelChecker(QtWidgets.QDialog):
    """Bang moi chi tiet: loai (vit / linh kien mua / in 3D / chua phan loai), huong in + ban, canh bao.
    Sua Label ngay trong bang (co Undo). Chon dong -> chon chi tiet trong 3D."""

    def __init__(self, doc, project):
        super().__init__(MW())
        self.doc, self.project = doc, project
        self.setWindowTitle(f"STLab – Kiểm tên Label – {doc.Label}")
        self.resize(1000, 640)
        lay = QtWidgets.QVBoxLayout(self)
        self.sum = QtWidgets.QLabel()
        lay.addWidget(self.sum)
        if not project:
            w = QtWidgets.QLabel("Model không thuộc dự án nào (maker/<project>/print/print.yaml) → chỉ kiểm vít và "
                                 "tên có dấu. Mở model từ STLab › Mở dự án.")
            w.setStyleSheet(f"color:{COLOR['WARN']}")
            lay.addWidget(w)
        top = QtWidgets.QHBoxLayout()
        self.only = QtWidgets.QCheckBox("Chỉ hiện dòng cần sửa")
        self.only.toggled.connect(self.fill)
        top.addWidget(self.only)
        top.addStretch()
        top.addWidget(QtWidgets.QLabel("Nhấp đúp ô Label để đổi tên"))
        lay.addLayout(top)
        self.t = _table(["Label", "Loại", "Nhóm · hướng in · bàn", "Cảnh báo"])
        self.t.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        lay.addWidget(self.t, 1)
        row = QtWidgets.QHBoxLayout()
        b = QtWidgets.QPushButton("Làm mới")
        b.clicked.connect(self.fill)
        row.addWidget(b)
        if project:
            b = QtWidgets.QPushButton("Mở print.yaml")
            b.clicked.connect(lambda: open_path(project.cfg_p))
            row.addWidget(b)
        row.addStretch()
        b = QtWidgets.QPushButton("Đóng")
        b.clicked.connect(self.close)
        row.addWidget(b)
        lay.addLayout(row)
        self.t.itemSelectionChanged.connect(self.pick)
        self.t.itemChanged.connect(self.rename)
        self._filling = False
        self.fill()

    def fill(self):
        if self.project:
            self.project.reload()
        self._filling = True
        self.t.setSortingEnabled(False)
        self.t.setRowCount(0)
        dem = {}
        for o in core.parts(self.doc):
            loai, ct, canh = core.classify(o.Label, self.project)
            dem[loai] = dem.get(loai, 0) + 1
            if self.only.isChecked() and not canh:
                continue
            r = self.t.rowCount()
            self.t.insertRow(r)
            it = _item(o.Label, data=o.Name)
            it.setFlags(it.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
            self.t.setItem(r, 0, it)
            for i, v in enumerate((loai, ct, "; ".join(canh)), 1):
                x = _item(v, COLOR["WARN"] if canh else None)
                x.setFlags(x.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.t.setItem(r, i, x)
        self.t.setSortingEnabled(True)
        self.t.sortItems(3, QtCore.Qt.SortOrder.DescendingOrder)  # dong co canh bao len dau
        self.t.resizeColumnsToContents()
        self._filling = False
        self.sum.setText(" · ".join(f"<b>{k}</b>: {v}" for k, v in sorted(dem.items()))
                         + (f" · <span style='color:{COLOR['WARN']}'>cần sửa: {dem.get('chưa phân loại', 0)}</span>"))

    def pick(self):
        r = self.t.currentRow()
        if r >= 0:
            o = self.doc.getObject(self.t.item(r, 0).data(QtCore.Qt.ItemDataRole.UserRole))
            if o:
                Gui.Selection.clearSelection()
                Gui.Selection.addSelection(o)

    def rename(self, it):
        if self._filling or it.column() != 0:
            return
        o = self.doc.getObject(it.data(QtCore.Qt.ItemDataRole.UserRole))
        new = it.text().strip()
        if o and new and new != o.Label:
            self.doc.openTransaction(f"Đổi Label {o.Label} → {new}")
            o.Label = new
            self.doc.commitTransaction()
            QtCore.QTimer.singleShot(0, self.fill)


# ---------------------------------------------------------------- 4. kiem tra: xem loi

class CheckReport(QtWidgets.QDialog):
    """Doc report.json cua check.py: moi dong FAIL/WARN -> nhap de chon (va phong to) chi tiet trong model."""

    def __init__(self, project):
        super().__init__(MW())
        self.project = project
        self.setWindowTitle(f"STLab – Lỗi kiểm tra – {project.name}")
        self.resize(1000, 600)
        lay = QtWidgets.QVBoxLayout(self)
        self.head = QtWidgets.QLabel()
        lay.addWidget(self.head)
        self.info = QtWidgets.QCheckBox("Hiện cả INFO (chạm nhau, khe nhỏ đã khai)")
        self.info.toggled.connect(self.fill)
        lay.addWidget(self.info)
        self.t = _table(["Mức", "Chi tiết", "Mục", "Tóm tắt"])
        lay.addWidget(self.t, 1)
        row = QtWidgets.QHBoxLayout()
        b = QtWidgets.QPushButton("Ảnh tổng quan")
        b.clicked.connect(lambda: show(ImageViewer(sorted(self.project.check_dir().glob("*.png")), "Kiểm tra")))
        row.addWidget(b)
        row.addStretch()
        b = QtWidgets.QPushButton("Đóng")
        b.clicked.connect(self.close)
        row.addWidget(b)
        lay.addLayout(row)
        self.t.itemSelectionChanged.connect(self.pick)
        self.fill()

    def fill(self):
        rp = self.project.check_dir() / "report.json"
        b = core._json(rp)
        self.t.setSortingEnabled(False)
        self.t.setRowCount(0)
        if not b:
            self.head.setText("Chưa có kết quả – bấm Kiểm nhanh.")
            return
        kl = b.get("ket_luan", "?")
        self.head.setText(f"<b style='color:{COLOR.get(kl, COLOR['TEXT'])}'>{kl}</b> · {b.get('file')} · "
                          f"{b.get('thoi_gian')} · "
                          f"{b.get('thoi_gian_chay_s')} s – kết quả trên file ĐÃ LƯU lúc kiểm")
        muc = ("FAIL", "WARN", "INFO") if self.info.isChecked() else ("FAIL", "WARN")
        rows = []
        for c in b.get("chi_tiet", []):
            for k, v in c.get("ket_qua", {}).items():
                if v.get("trang_thai") in muc:
                    rows.append((v["trang_thai"], c["nhan"], [c["nhan"]], k, v.get("tom_tat", "")))
        for x in (b.get("va_cham") or {}).get("cap", []):
            if x.get("trang_thai") in muc:
                rows.append((x["trang_thai"], f"{x['a']} ~ {x['b']}", [x["a"], x["b"]], "va chạm",
                             x.get("tom_tat", "")))
        for x in b.get("quet_khop", []) or []:
            if x.get("trang_thai") in muc:
                rows.append((x["trang_thai"], x.get("khop", "?"), [], "quét khớp", x.get("tom_tat", "")))
        rows.sort(key=lambda r: ("FAIL", "WARN", "INFO").index(r[0]))
        for tt, name, labels, k, tom in rows:
            r = self.t.rowCount()
            self.t.insertRow(r)
            self.t.setItem(r, 0, _item(tt, COLOR.get(tt), data=labels))
            self.t.setItem(r, 1, _item(name))
            self.t.setItem(r, 2, _item(k))
            self.t.setItem(r, 3, _item(tom))
        self.t.setSortingEnabled(True)
        self.t.resizeColumnsToContents()

    def pick(self):
        r = self.t.currentRow()
        if r < 0:
            return
        labels = self.t.item(r, 0).data(QtCore.Qt.ItemDataRole.UserRole) or []
        doc = self.project.is_open()
        if doc and labels:
            select_labels(labels, doc)


class PlatePicker(QtWidgets.QDialog):
    """Chon ban in (.3mf) de mo bang Bambu Studio."""

    def __init__(self, project):
        super().__init__(MW())
        self.setWindowTitle(f"STLab – Bàn in – {project.name}")
        self.resize(700, 400)
        lay = QtWidgets.QVBoxLayout(self)
        rep = core._json(project.plates_dir / "print-report.json") or {}
        info = {b["ban"]: b for b in rep.get("ban", [])}
        self.t = _table(["Bàn", "Kết luận", "Thời gian", "Nhựa (g)"])
        for f in project.plates():
            b = info.get(f.stem)
            if b is None and info:
                b = {"trang_thai": "cũ – không có trong lần cắt gần nhất"}
            b = b or {}
            r = self.t.rowCount()
            self.t.insertRow(r)
            self.t.setItem(r, 0, _item(f.stem, data=str(f)))
            tg = b.get("thoi_gian_s", 0)
            self.t.setItem(r, 1, _item(b.get("trang_thai", "?"), COLOR.get(b.get("trang_thai"), COLOR["MUTED"])))
            self.t.setItem(r, 2, _item(f"{tg // 3600}h{tg % 3600 // 60:02d}" if tg else ""))
            self.t.setItem(r, 3, _item(b.get("gam", "")))
        self.t.setSortingEnabled(True)
        self.t.sortItems(0)
        self.t.resizeColumnsToContents()
        self.t.doubleClicked.connect(self.open)
        lay.addWidget(self.t)
        row = QtWidgets.QHBoxLayout()
        for text, fn in (("Mở bằng Bambu Studio", self.open), ("Thư mục bàn in", lambda: open_path(project.plates_dir)),
                         ("Đóng", self.close)):
            b = QtWidgets.QPushButton(text)
            b.clicked.connect(fn)
            row.addWidget(b)
        lay.addLayout(row)

    def open(self):
        r = self.t.currentRow()
        if r < 0:
            return
        f = self.t.item(r, 0).data(QtCore.Qt.ItemDataRole.UserRole)
        if core.BAMBU.exists():
            QtCore.QProcess.startDetached(str(core.BAMBU), [f])
        else:
            open_path(f)
