# Chay script FreeCAD bang CLI cho DUNG: traceback day du + exit code that.
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode maker/robotics-cad/scripts/fc_cli.py --pass <script.py> [args...]
# Vi sao (do 2026-10-24, FreeCAD 1.1.4): freecadcmd gap exception van tra exit 0, chi in 1 dong
# "Exception while processing file: ... [msg]" - co lan msg con SAI (bao loi guard trong khi loi that la AttributeError).
# Trong script: sys.argv = [script, args...]. In "FC_CLI OK" / "FC_CLI FAIL" o cuoi de grep.
import os
import sys
import traceback

argv = sys.argv[sys.argv.index("--pass") + 1:] if "--pass" in sys.argv else []
if not argv:
    print("FC_CLI FAIL: thieu --pass <script.py>")
    os._exit(2)
script = os.path.abspath(argv[0])
sys.argv = [script] + argv[1:]
sys.path.insert(0, os.path.dirname(script))
try:
    exec(compile(open(script, encoding="utf-8").read(), script, "exec"), {"__name__": "__main__", "__file__": script})
except SystemExit as e:
    code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    print("FC_CLI %s (SystemExit %s)" % ("OK" if code == 0 else "FAIL", e.code), flush=True)
    os._exit(code)
except BaseException:
    print(traceback.format_exc(), flush=True)
    print("FC_CLI FAIL", flush=True)
    os._exit(1)
print("FC_CLI OK", flush=True)
os._exit(0)
