# Dua cua so FreeCAD sang MAN HINH PHU (Tuan 2026-10-25: "toi xai man hinh chinh viec khac, mo FreeCAD o man hinh thu 2").
# Dung 2 cach:
#   - import trong script GUI (gui_run.py goi move_to_second_screen() ngay khi chay)
#   - mo file de XEM: "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" <file.FCStd> tools/robotics-cad/scripts/second_screen.py
#     (FreeCAD chay file .py tren dong lenh sau khi mo file)
# Chi 1 man hinh -> giu nguyen. FreeCAD luu vi tri cua so khi thoat -> lan sau tu mo o man hinh phu.
import FreeCADGui as Gui
from PySide import QtGui


def move_to_second_screen():
    app = QtGui.QGuiApplication
    screens = [s for s in app.screens() if s is not app.primaryScreen()]
    mw = Gui.getMainWindow()
    if not screens or mw is None:
        return False
    mw.showNormal()
    mw.setGeometry(screens[0].availableGeometry())
    mw.showMaximized()
    return True


if __name__ in ("__main__", "second_screen"):
    move_to_second_screen()
