"""Xep cua so tren Windows: ung dung mot ben, Claude Desktop mot ben (chi thu vien chuan, ctypes).

- Tim cua so chinh theo ten exe (cua so hien, co tieu de, khong phai console), chon cua so lon nhat.
- Dat theo vung lam viec (work area, tru taskbar) cua man hinh chinh hoac man hinh chi dinh.
- Bu vien vo hinh cua Windows 10/11 (DWM extended frame) de 2 cua so khit nhau.
"""
import ctypes
import os
import time
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
dwmapi = ctypes.WinDLL("dwmapi")

try:  # toa do vat ly, dung tren man hinh co ti le phong (DPI)
    user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # PER_MONITOR_AWARE_V2
except (AttributeError, OSError):
    pass

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
MONITORENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC,
                                     ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.EnumDisplayMonitors.argtypes = [wintypes.HDC, ctypes.c_void_p, MONITORENUMPROC, wintypes.LPARAM]
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND] + [ctypes.c_int] * 4 + [wintypes.UINT]

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
GW_OWNER = 4
SW_RESTORE = 9
SWP_NOZORDER, SWP_NOACTIVATE = 0x0004, 0x0010
DWMWA_EXTENDED_FRAME_BOUNDS, DWMWA_CLOAKED = 9, 14
SKIP_CLASSES = {"ConsoleWindowClass", "CASCADIA_HOSTING_WINDOW_CLASS", "PseudoConsoleWindow"}


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]


def _exe_path(pid):
    h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(len(buf))
        ok = kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size))
        return buf.value if ok else ""
    finally:
        kernel32.CloseHandle(h)


def _cloaked(hwnd):
    v = wintypes.DWORD()
    dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(v), ctypes.sizeof(v))
    return v.value != 0


def _rect(hwnd):
    r = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r


def find_window(image, path_contains=""):
    """Cua so chinh lon nhat cua tien trinh co ten exe `image` (vd. blender.exe)."""
    found = []

    def cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd) or user32.GetWindow(hwnd, GW_OWNER):
            return True
        if user32.GetWindowTextLengthW(hwnd) == 0 or _cloaked(hwnd):
            return True
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        if cls.value in SKIP_CLASSES:
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        path = _exe_path(pid.value)
        if os.path.basename(path).lower() != image.lower():
            return True
        if path_contains and path_contains.lower() not in path.lower():
            return True
        r = _rect(hwnd)
        found.append(((r.right - r.left) * (r.bottom - r.top), hwnd))
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return max(found)[1] if found else None


def wait_window(image, path_contains="", timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        h = find_window(image, path_contains)
        if h:
            return h
        time.sleep(0.5)
    return None


def monitors():
    """Danh sach vung lam viec: [{'primary': bool, 'work': (x, y, w, h)}], man hinh chinh dau tien."""
    out = []

    def cb(hmon, _hdc, _rc, _):
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW(hmon, ctypes.byref(mi))
        w = mi.rcWork
        out.append({"primary": bool(mi.dwFlags & 1),
                    "work": (w.left, w.top, w.right - w.left, w.bottom - w.top)})
        return True

    user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(cb), 0)
    return sorted(out, key=lambda m: not m["primary"])


def _visible_rect(hwnd):
    f = wintypes.RECT()
    if dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(f), ctypes.sizeof(f)) != 0:
        f = _rect(hwnd)
    return (f.left, f.top, f.right - f.left, f.bottom - f.top)


def place(hwnd, x, y, w, h, tries=4):
    """Dat cua so dung vung nhin thay (x, y, w, h). Thu lai vi app Electron (Claude Desktop)
    khoi phuc kich thuoc bat dong bo va co the ghi de vi tri vua dat."""
    if user32.IsZoomed(hwnd) or user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
        end = time.time() + 2
        while time.time() < end and (user32.IsZoomed(hwnd) or user32.IsIconic(hwnd)):
            time.sleep(0.05)
        time.sleep(0.4)  # cho app xu ly xong WM_SIZE cua lan khoi phuc
    for _ in range(tries):
        _set_pos(hwnd, x, y, w, h)
        time.sleep(0.3)
        vx, vy, vw, vh = _visible_rect(hwnd)
        if abs(vx - x) <= 2 and abs(vy - y) <= 2 and abs(vw - w) <= 2 and abs(vh - h) <= 2:
            return True
    return False


def _set_pos(hwnd, x, y, w, h):
    outer = _rect(hwnd)
    frame = wintypes.RECT()
    if dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(frame),
                                    ctypes.sizeof(frame)) == 0:
        dl, dt = frame.left - outer.left, frame.top - outer.top
        dr, db = outer.right - frame.right, outer.bottom - frame.bottom
    else:
        dl = dt = dr = db = 0
    user32.SetWindowPos(hwnd, None, x - dl, y - dt, w + dl + dr, h + dt + db, SWP_NOZORDER | SWP_NOACTIVATE)


def split(app_hwnd, claude_hwnd, app_side="left", app_ratio=0.6, monitor=0):
    """App chiem app_ratio be ngang man hinh `monitor` (0 = man hinh chinh), Claude phan con lai."""
    mons = monitors()
    x, y, w, h = mons[min(monitor, len(mons) - 1)]["work"]
    aw = int(w * app_ratio)
    if app_side == "left":
        ok = place(app_hwnd, x, y, aw, h) & place(claude_hwnd, x + aw, y, w - aw, h)
    else:
        ok = place(claude_hwnd, x, y, w - aw, h) & place(app_hwnd, x + w - aw, y, aw, h)
    user32.SetForegroundWindow(claude_hwnd)
    return ok
