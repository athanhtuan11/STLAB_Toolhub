"""Tat EcoQoS (power throttling) cho chinh tien trinh nay tren Windows 11.

Do 2026-11-06 (i5-13400F, nhan P + E): tien trinh chay an (Task Scheduler / cua so an) bi Windows day sang che do
tiet kiem -> Whisper small 2,1 s thanh 5,3-10,9 s. Tien trinh tu xin tat duoc, khong can quyen admin.
API: SetProcessInformation(ProcessPowerThrottling, PROCESS_POWER_THROTTLING_STATE) – ControlMask = EXECUTION_SPEED,
StateMask = 0 nghia la "khong tiet kiem toc do".
"""
import ctypes
import sys


def disable() -> bool:
    if sys.platform != "win32":
        return False
    from ctypes import wintypes

    class PROCESS_POWER_THROTTLING_STATE(ctypes.Structure):
        _fields_ = [("Version", wintypes.ULONG), ("ControlMask", wintypes.ULONG), ("StateMask", wintypes.ULONG)]

    PROCESS_POWER_THROTTLING_CURRENT_VERSION = 1
    PROCESS_POWER_THROTTLING_EXECUTION_SPEED = 0x1
    ProcessPowerThrottling = 4  # PROCESS_INFORMATION_CLASS
    st = PROCESS_POWER_THROTTLING_STATE(PROCESS_POWER_THROTTLING_CURRENT_VERSION,
                                        PROCESS_POWER_THROTTLING_EXECUTION_SPEED, 0)
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    k32.SetProcessInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    k32.SetProcessInformation.restype = wintypes.BOOL
    ok = bool(k32.SetProcessInformation(k32.GetCurrentProcess(), ProcessPowerThrottling,
                                        ctypes.byref(st), ctypes.sizeof(st)))
    try:  # muc uu tien Normal phong khi tien trinh cha o BelowNormal
        k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x20)  # NORMAL_PRIORITY_CLASS
    except Exception:  # noqa: BLE001
        pass
    return ok


if __name__ == "__main__":
    print("EcoQoS off:", disable())
