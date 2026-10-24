"""Lenh FreeCAD cua workbench STLab, chia theo quy trinh chuan (robotics-cad/CLAUDE.md muc "Quy trinh"):

1 Du an -> 2 Linh kien -> 3 Thiet ke -> 4 Kiem tra (tang 1) -> 5 In 3D (STL, kha nang in, cat lop) -> 6 Tai lieu.
Viec nang chay trong tien trinh rieng (runner.py); script pipeline chi DOC file da Luu -> lenh hoi Luu truoc.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets

from . import core, dialogs, panel, runner

STAGE_CMDS = {
    "1 Dự án": ["STLab_NewProject", "STLab_OpenProject", "STLab_ProjectFolder"],
    "2 Linh kiện": ["STLab_Components"],
    "3 Thiết kế": ["STLab_Labels", "STLab_PrintPreview", "STLab_Backup"],
    "4 Kiểm tra": ["STLab_CheckFast", "STLab_CheckFull", "STLab_CheckReport"],
    "5 In 3D": ["STLab_ExportStl", "STLab_Printability", "STLab_Slice", "STLab_PreparePrint", "STLab_Plates"],
    "6 Tài liệu": ["STLab_Bom", "STLab_MetricsDiff", "STLab_AssemblyPdf"],
}


def _msg(text, warn=False):
    (QtWidgets.QMessageBox.warning if warn else QtWidgets.QMessageBox.information)(Gui.getMainWindow(), "STLab", text)


def need_project(saved=True):
    """Du an hien tai; saved=True: model co thay doi chua Luu -> hoi Luu (script chi doc file da Luu)."""
    p = panel.current_project()
    if p is None:
        _msg("Chưa chọn dự án. Mở model của dự án (STLab › Mở dự án) hoặc chọn trong bảng STLab Workflow.")
        return None
    p.reload()
    if not saved:
        return p
    if not p.fcstd.exists():
        _msg(f"Chưa có model {p.fcstd}.\nDựng và Lưu model đúng đường dẫn này trước.", warn=True)
        return None
    d = p.is_open()
    if d and Gui.getDocument(d.Name).Modified:
        B = QtWidgets.QMessageBox.StandardButton
        r = QtWidgets.QMessageBox.question(
            Gui.getMainWindow(), "STLab",
            f"{p.fcstd.name} có thay đổi chưa Lưu.\nScript kiểm/xuất chỉ đọc file đã Lưu.\n\nLưu rồi chạy?",
            B.Save | B.Ignore | B.Cancel, B.Save)
        if r == B.Cancel:
            return None
        if r == B.Save:
            d.save()
    return p


def _images(*paths, title="Kết quả"):
    imgs = [x for x in paths if x and x.exists()]
    if imgs:
        dialogs.show(dialogs.ImageViewer(imgs, title))


class _Cmd:
    pixmap, menu, tip, accel = "", "", "", ""

    def GetResources(self):
        r = {"Pixmap": core.icon(self.pixmap), "MenuText": self.menu, "ToolTip": self.tip}
        if self.accel:
            r["Accel"] = self.accel
        return r

    def IsActive(self):
        return True


# ---------------------------------------------------------------- 1 du an

class NewProject(_Cmd):
    pixmap, menu = "NewProject", "Tạo dự án mới…"
    tip = "Tạo maker/<name>/ từ project-template (freecad/ + print/print.yaml), tạo model trống"

    def Activated(self):
        d = dialogs.NewProjectDialog()
        if d.exec() and d.project:
            panel.panel().reload()
            panel.log(f"Đã tạo {d.project.dir}. Nhớ: khai hướng in trong print/print.yaml (export.rules).")


class OpenProject(_Cmd):
    pixmap, menu, tip = "OpenProject", "Mở dự án…", "Danh sách dự án maker/*/print/print.yaml – mở model"

    def Activated(self):
        dialogs.OpenProjectDialog().exec()


class ProjectFolder(_Cmd):
    pixmap, menu, tip = "ProjectFolder", "Mở thư mục dự án", "Mở maker/<project>/ trong Explorer"

    def Activated(self):
        p = need_project(saved=False)
        if p:
            dialogs.open_path(p.dir)


# ---------------------------------------------------------------- 2 linh kien

class Components(_Cmd):
    pixmap, menu = "Components", "Thư viện linh kiện…"
    tip = "Tìm linh kiện trong components.yaml (thông số có nguồn), chèn STEP với Label CB_/LK_"

    def Activated(self):
        dialogs.show(dialogs.ComponentBrowser())


# ---------------------------------------------------------------- 3 thiet ke

class Labels(_Cmd):
    pixmap, menu = "Labels", "Kiểm tên Label…"
    tip = "Phân loại từng chi tiết (vít / linh kiện mua / in 3D / chưa phân loại) theo print.yaml, sửa Label tại chỗ"

    def IsActive(self):
        return App.ActiveDocument is not None

    def Activated(self):
        doc = App.ActiveDocument
        dialogs.show(dialogs.LabelChecker(doc, core.project_for_doc(doc)))


class PrintPreview(_Cmd):
    pixmap, menu = "PrintPreview", "Xem hướng in (bật/tắt)"
    tip = ("Chi tiết đang chọn → xoay theo print.yaml, đặt trên bàn A1 ảo cạnh model; đỏ = nhô ra. "
           "Không chọn gì = tắt. Không sửa file.")

    def IsActive(self):
        return App.ActiveDocument is not None and Gui.ActiveDocument is not None

    def Activated(self):
        from . import preview
        doc = App.ActiveDocument
        sel = [o for o in Gui.Selection.getSelection(doc.Name) if o.isDerivedFrom("Part::Feature")]
        if not sel:
            if not preview.clear(doc):
                _msg("Chọn chi tiết cần xem hướng in (có thể chọn nhiều), rồi bấm lại.")
            return
        p = core.project_for_doc(doc)
        if p is None:
            _msg("Model không thuộc dự án nào → không có print.yaml để biết hướng in.")
            return
        n, skip, n_over = preview.show(sel, p)
        panel.log(f"Xem hướng in: {n} chi tiết, {n_over} tam giác nhô ra (đỏ)"
                  + "".join(f"\n   bỏ qua {lb}: {why}" for lb, why in skip))
        if skip and not n:
            _msg("Không chi tiết nào khớp quy tắc export trong print.yaml:\n" + "\n".join(lb for lb, _ in skip))


class Backup(_Cmd):
    pixmap, menu, tip = "Backup", "Sao lưu model", "Lưu bản sao vào freecad/backup/<model>.<thời gian>.<ghi chú>.FCStd"

    def IsActive(self):
        return App.ActiveDocument is not None and bool(App.ActiveDocument.FileName)

    def Activated(self):
        note, ok = QtWidgets.QInputDialog.getText(Gui.getMainWindow(), "STLab – Sao lưu", "Ghi chú (tiếng Anh, ngắn):",
                                                  text="before-edit")
        if ok:
            f = core.backup(App.ActiveDocument, note)
            panel.log(f"Đã sao lưu: {f}")


# ---------------------------------------------------------------- 4 kiem tra

class CheckFast(_Cmd):
    pixmap, menu = "CheckFast", "Kiểm nhanh (tầng 1)"
    tip = "check.py mode=fast: hình học + lưới + va chạm, có cache (~10–60 s). Chạy nền."
    mode = "fast"

    def Activated(self):
        p = need_project()
        if not p:
            return
        panel.show_panel()

        def after(code):
            panel.panel().refresh_status()
            res = p.results().get("check")
            if res and res[0] in ("FAIL", "WARN"):
                dialogs.show(dialogs.CheckReport(p))
            else:
                _images(p.check_dir() / "overview.png", title="Kiểm tra")
        runner.runner().submit(runner.job_check(p, self.mode, after))


class CheckFull(CheckFast):
    pixmap, menu = "CheckFull", "Kiểm đầy đủ"
    tip = "check.py mode=full: thêm BOP, độ dày thành, overhang theo hướng trong file (~2 phút+). Chạy nền."
    mode = "full"


class CheckReport(_Cmd):
    pixmap, menu, tip = "CheckReport", "Xem lỗi kiểm tra", "Bảng FAIL/WARN – nhấp để chọn chi tiết lỗi trong 3D"

    def Activated(self):
        p = need_project(saved=False)
        if p:
            dialogs.show(dialogs.CheckReport(p))


# ---------------------------------------------------------------- 5 in 3D

class ExportStl(_Cmd):
    pixmap, menu, tip = "ExportStl", "Xuất STL theo hướng in", "export-stl.py: STL theo export.rules → print/stl/"

    def Activated(self):
        p = need_project()
        if p:
            panel.show_panel()
            runner.runner().submit(runner.job_export(p, lambda c: panel.panel().refresh_status()))


class Printability(_Cmd):
    pixmap, menu = "Printability", "Khả năng in (STL)"
    tip = "printability.py trên print/stl/: nhô ra không đỡ, chi tiết nhỏ cần brim. Xuất STL trước."

    def Activated(self):
        p = need_project(saved=False)
        if not p:
            return
        if not any(p.stl_dir.glob("*.stl")):
            _msg("Chưa có STL – bấm Xuất STL trước.")
            return
        panel.show_panel()
        job = runner.job_printability(p)
        job.after = lambda c: printability_summary(job)
        runner.runner().submit(job)


def printability_summary(job):
    """printability.py in 1 dong JSON / STL -> tom tat: can support (WARN), can brim (INFO)."""
    import json
    rs = []
    for ln in job.output:
        try:
            rs.append(json.loads(ln))
        except ValueError:
            panel.log(ln)
    sup = [r for r in rs if r.get("can_support")]
    brim = [r for r in rs if r.get("can_brim")]
    n = len(list(job.project.stl_dir.glob("*.stl")))
    panel.log(f"   {n} STL: {len(sup)} nhô ra không đỡ (WARN), {len(brim)} cần brim"
              + ("" if sup else " – không cần support"))
    for r in sup:
        panel.log(f"   - {r['stl']}: " + ", ".join(f"{c['mm2']} mm² ở z {c['z_mm']}" for c in r["cum_nho"][:3])
                  + " → sửa thiết kế (vát 45°, đổi hướng) / `support: true`")
    if brim:
        panel.log("   brim: " + ", ".join(r["stl"].removesuffix(".stl") for r in brim[:12])
                  + (f" … (+{len(brim) - 12})" if len(brim) > 12 else ""))


class Slice(_Cmd):
    pixmap, menu = "Slice", "Cắt lớp Bambu (tầng 2)"
    tip = "slice.py: Bambu Studio CLI theo print.yaml → plates/<bàn>/<bàn>.3mf + print-overview.png"

    def Activated(self):
        p = need_project(saved=False)
        if not p:
            return
        panel.show_panel()
        runner.runner().submit(runner.job_slice(p, lambda c: (panel.panel().refresh_status(), _images(
            p.plates_dir / "print-overview.png", title="Cắt lớp"))))


class PreparePrint(_Cmd):
    pixmap, menu = "PreparePrint", "Chuẩn bị in (cả vòng)"
    tip = "prepare-print.py: kiểm hết trước (tầng 1 + khả năng in), sạch mới cắt lớp. ~1–2 phút, chạy nền."
    accel = "Ctrl+Shift+P"

    def Activated(self):
        p = need_project()
        if p:
            run_prepare(p)


def run_prepare(p, show_result=True):
    panel.show_panel()

    def after(code):
        panel.panel().refresh_status()
        r = core._json(p.cfg_p.parent / "_prepare-print-result.json") or {}
        for t in r.get("tang", []):
            panel.log(f"   {t['ten']}: {t['ket_luan']} ({t['chi_tiet']})")
            for x in t.get("loi", [])[:8]:
                panel.log(f"      - {x}")
        if show_result:
            from pathlib import Path
            _images(*[Path(t["anh"]) for t in r.get("tang", []) if t.get("anh")], title=f"Chuẩn bị in – {p.name}")
    runner.runner().submit(runner.job_prepare(p, after=after))


class Plates(_Cmd):
    pixmap, menu, tip = "Plates", "Mở bàn in…", "Danh sách bàn in (.3mf) – mở bằng Bambu Studio"

    def Activated(self):
        p = need_project(saved=False)
        if not p:
            return
        if not p.plates():
            _msg("Chưa có file .3mf – bấm Chuẩn bị in.")
            return
        dialogs.show(dialogs.PlatePicker(p))


# ---------------------------------------------------------------- 6 tai lieu

class Bom(_Cmd):
    pixmap, menu, tip = "Bom", "BOM", "metrics.py + bom.py → BOM.csv + BOM.md (vít, linh kiện mua, chi tiết in → bàn)"

    def Activated(self):
        p = need_project()
        if not p:
            return
        panel.show_panel()

        def after(code):
            panel.panel().refresh_status()
            f = p.dir / "BOM.md"
            if code == 0 and f.exists():
                dialogs.show(dialogs.TextViewer(f"BOM – {p.name}", f.read_text(encoding="utf-8"), True, f))
        r = runner.runner()
        r.submit(runner.job_metrics(p))
        r.submit(runner.job_bom(p, after))


class MetricsDiff(_Cmd):
    pixmap, menu = "MetricsDiff", "So với commit trước"
    tip = "metrics.py diff: chi tiết mới/xóa/đổi thể tích/đổi vị trí so với git HEAD (bắt sửa ngoài ý muốn)"

    def Activated(self):
        p = need_project()
        if p:
            panel.show_panel()
            r = runner.runner()
            r.submit(runner.job_metrics(p))
            r.submit(runner.job_metrics_diff(p))


class AssemblyPdf(_Cmd):
    pixmap, menu, tip = "AssemblyPdf", "PDF lắp ráp", "assembly-pdf.py: ASSEMBLY.md → ASSEMBLY.pdf (Edge headless)"

    def Activated(self):
        p = need_project(saved=False)
        if not p:
            return
        if not (p.dir / "ASSEMBLY.md").exists():
            _msg("Dự án chưa có ASSEMBLY.md (mẫu: maker/pushrod-arm/ASSEMBLY.md).")
            return
        panel.show_panel()
        runner.runner().submit(runner.job_assembly_pdf(
            p, lambda c: c == 0 and (p.dir / "ASSEMBLY.pdf").exists() and dialogs.open_path(p.dir / "ASSEMBLY.pdf")))


class Panel(_Cmd):
    pixmap, menu, tip = "Panel", "Bảng STLab Workflow", "Hiện/ẩn bảng quy trình (dự án, 6 bước, nhật ký)"

    def Activated(self):
        panel.show_panel(toggle=True)


# ---------------------------------------------------------------- tu chay khi Luu

class SaveObserver:
    """Thay watch.py: Luu model cua du an + o "Tu chuan bi in moi khi Luu" dang bat -> prepare-print nen."""

    def slotFinishSaveDocument(self, doc, filename):
        if not panel.auto_on_save():
            return
        p = core.project_for_doc(doc)
        if p:
            panel.log(f"{p.fcstd.name} vừa Lưu → chuẩn bị in")
            run_prepare(p, show_result=False)


_observer = None


def register():
    global _observer
    for name, cls in list(globals().items()):
        if isinstance(cls, type) and issubclass(cls, _Cmd) and cls is not _Cmd:
            Gui.addCommand(f"STLab_{name}", cls())
    if _observer is None:
        _observer = SaveObserver()
        App.addDocumentObserver(_observer)
