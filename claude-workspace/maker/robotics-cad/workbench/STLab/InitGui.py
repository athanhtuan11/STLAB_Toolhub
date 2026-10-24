"""Workbench STLab cho FreeCAD 1.1 - giao dien cho pipeline maker/robotics-cad/scripts (mot nguon).

Thu muc nay nam trong claude-workspace/maker/robotics-cad/workbench/STLab; Mod/STLab cua FreeCAD chi la junction
(cai bang workbench/install.py).
"""

import FreeCADGui as Gui


class STLabWorkbench(Gui.Workbench):
    MenuText = "STLab"
    ToolTip = "Quy trình STLab: Dự án → Linh kiện → Thiết kế → Kiểm tra → In 3D → Tài liệu"

    def __init__(self):
        import os
        import FreeCAD as App
        # InitGui chay bang exec: khong co __file__ -> lay theo thu muc Mod
        base = os.path.join(App.getUserAppDataDir(), "Mod", "STLab")
        self.__class__.Icon = os.path.join(base, "stlab_wb", "icons", "Workbench.svg")

    def Initialize(self):
        from stlab_wb import commands
        commands.register()
        for stage, cmds in commands.STAGE_CMDS.items():
            self.appendToolbar(f"STLab {stage}", cmds)
            self.appendMenu(["STLab", stage], cmds)
        self.appendMenu("STLab", ["Separator", "STLab_Panel"])
        self.appendToolbar("STLab", ["STLab_Panel"])

    def Activated(self):
        from stlab_wb import panel
        panel.show_panel()

    def Deactivated(self):
        pass

    def ContextMenu(self, recipient):
        if recipient == "View":
            self.appendContextMenu("STLab", ["STLab_PrintPreview", "STLab_Labels", "STLab_CheckReport"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(STLabWorkbench())
