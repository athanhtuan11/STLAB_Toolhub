# Chay 1 script CAN GUI (render saveImage, ViewObject...) trong FreeCAD GUI RIENG, tu mo file + tu thoat.
# Khong dung phien FreeCAD cua Tuan (GUI hay crash; RPC tinh toan nang lam treo GUI - 2026-10-24).
#   set FC_FILE=<file.FCStd>   set FC_SCRIPT=<script.py>   [set FC_OUT=<log.txt>]
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode tools/robotics-cad/scripts/gui_run.py
# Script duoc chay sau khi file da mo (App.getDocument(<ten>) dung duoc). Khong Luu file. Loi -> ghi FC_OUT.
import os
import traceback

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore


def run():
    out = os.environ.get("FC_OUT") or os.path.join(os.environ.get("TEMP", "."), "gui_run.log")
    msg = "OK"
    try:
        doc = App.openDocument(os.environ["FC_FILE"])
        Gui.activateWorkbench("PartWorkbench")
        Gui.ActiveDocument = Gui.getDocument(doc.Name)
        p = os.environ["FC_SCRIPT"]
        exec(compile(open(p, encoding="utf-8").read(), p, "exec"), {"__name__": "__main__"})
        App.closeDocument(doc.Name)
    except Exception:
        msg = "FAIL\n" + traceback.format_exc()
    with open(out, "w", encoding="utf-8") as f:
        f.write(msg)
    QtCore.QTimer.singleShot(500, Gui.getMainWindow().close)


QtCore.QTimer.singleShot(1500, run)
