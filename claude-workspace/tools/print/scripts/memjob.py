"""Chay lenh trong Windows Job Object gioi han RAM = RAM dang trong luc chay - du phong (GB).
  python memjob.py <reserve_gb> -- <lenh...>
Vuot gioi han -> tien trinh con bi tu choi cap phat / kill, may khong treo (Tuan 2026-11-14:
cat lop tung ngon het 32 GB lam dung may). Vd: python memjob.py 3 -- python slice.py print.yaml
"""
import ctypes, ctypes.wintypes as w, subprocess, sys
k = ctypes.windll.kernel32
class MS(ctypes.Structure):
    _fields_ = [("dwLength", w.DWORD), ("dwMemoryLoad", w.DWORD)] + [(n, ctypes.c_ulonglong) for n in
        ("tot", "avail", "totPF", "availPF", "totV", "availV", "availExt")]
ms = MS(); ms.dwLength = ctypes.sizeof(MS); k.GlobalMemoryStatusEx(ctypes.byref(ms))
reserve = float(sys.argv[1]); cmd = sys.argv[sys.argv.index("--") + 1:]
limit = max(int(ms.avail - reserve * 2**30), 4 * 2**30)
print(f"[memjob] RAM trong {ms.avail/2**30:.1f} GB, gioi han {limit/2**30:.1f} GB", flush=True)
class BASIC(ctypes.Structure):
    _fields_ = [("a", ctypes.c_longlong), ("b", ctypes.c_longlong), ("LimitFlags", w.DWORD),
                ("c", ctypes.c_size_t), ("d", ctypes.c_size_t), ("e", w.DWORD), ("f", ctypes.c_size_t),
                ("g", w.DWORD), ("h", w.DWORD)]
class IO(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in "abcdef"]
class EXT(ctypes.Structure):
    _fields_ = [("Basic", BASIC), ("Io", IO), ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcess", ctypes.c_size_t), ("PeakJob", ctypes.c_size_t)]
k.CreateJobObjectW.restype = w.HANDLE
k.GetCurrentProcess.restype = w.HANDLE
for f in ("SetInformationJobObject", "QueryInformationJobObject"): getattr(k, f).argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD] + ([ctypes.c_void_p] if f[0] == "Q" else [])
k.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
job = k.CreateJobObjectW(None, None)
info = EXT(); info.Basic.LimitFlags = 0x200 | 0x2000   # JOB_MEMORY | KILL_ON_JOB_CLOSE
info.JobMemoryLimit = limit
assert k.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)), "SetInformationJobObject"
assert k.AssignProcessToJobObject(job, k.GetCurrentProcess()), "AssignProcessToJobObject"
r = subprocess.run(cmd)
k.QueryInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info), None)
print(f"[memjob] exit {r.returncode}, dinh RAM job {info.PeakJob/2**30:.2f} GB", flush=True)
sys.exit(r.returncode)
