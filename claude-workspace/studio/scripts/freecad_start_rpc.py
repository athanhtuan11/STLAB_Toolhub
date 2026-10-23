# Chay khi launcher mo FreeCAD: bat RPC server cua addon FreeCADMCP cho phien nay.
# Khong doi setting "Auto-Start Server" (mo FreeCAD binh thuong thi van khong mo cong).
import FreeCAD
from PySide import QtCore


def _start_rpc():
    try:
        from rpc_server import rpc_server  # InitGui cua addon da them thu muc addon vao sys.path

        FreeCAD.Console.PrintMessage(f"[studio] {rpc_server.start_rpc_server()}\n")
    except Exception as e:  # addon chua cai hoac loi khoi dong
        FreeCAD.Console.PrintError(f"[studio] Khong bat duoc RPC server: {e}\n")


QtCore.QTimer.singleShot(1500, _start_rpc)
