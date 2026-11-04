# Gate "phat hien treo + chia viec xoay vong" (Claude viet, executor KHONG sua).
#   python tests/test_watchdog_rr.py      (chay tu tools/delegate)
import importlib.util, inspect, os, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "delegate.py")
spec = importlib.util.spec_from_file_location("delegate", SRC)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
TMP = tempfile.mkdtemp(prefix="delegate-wd-test-")
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# ---- 1. Dem viec 7 ngay ----
check(hasattr(d, "recent_counts"), "thieu ham recent_counts(days=7, root=None)")
check(hasattr(d, "order_fair"), "thieu ham order_fair(queue, counts)")
if hasattr(d, "recent_counts"):
    root = os.path.join(TMP, "runs")
    today = time.strftime("%Y%m%d")
    old = time.strftime("%Y%m%d", time.localtime(time.time() - 20 * 86400))
    for name, logs in [(f"{today}-100000-a", ["codex-1.log", "codex-2.log"]),
                       (f"{today}-110000-b", ["opencode-1.log"]),
                       (f"{today}-120000-c", ["codex-1.log", "kilo-2.log"]),
                       (f"{old}-120000-old", ["kilo-1.log", "kilo-2.log", "kilo-3.log"])]:
        os.makedirs(os.path.join(root, name))
        for lg in logs:
            open(os.path.join(root, name, lg), "w").close()
    c = d.recent_counts(days=7, root=root)
    check(c.get("codex") == 3, f"codex 7 ngay phai = 3 vong, nhan {c.get('codex')}")
    check(c.get("opencode") == 1 and c.get("kilo") == 1, f"opencode=1, kilo=1 (bo run cu hon 7 ngay), nhan {c}")
    check(c.get("copilot", 0) == 0, "copilot chua chay = 0")
if hasattr(d, "order_fair"):
    q = d.order_fair(["codex", "opencode", "kilo", "copilot"], {"codex": 3, "opencode": 1, "kilo": 1})
    check(q == ["copilot", "opencode", "kilo", "codex"], f"order_fair: it viec truoc, bang nhau giu thu tu goc; nhan {q}")
src = inspect.getsource(d)
check("order_fair(" in inspect.getsource(d.pick_queue) or "order_fair(" in src.split("def order_fair")[0] + src.split("def order_fair")[-1].split("\n", 1)[-1],
      "pick_queue/main phai dung order_fair cho executor auto")

# ---- 2. Phat hien treo ----
check(hasattr(d, "run_proc_watch"), "thieu ham run_proc_watch(argv, cwd, stdin, timeout_s, stall_s, watch_dir, env=None)")
if hasattr(d, "run_proc_watch"):
    py = sys.executable
    w = os.path.join(TMP, "w")
    os.makedirs(w)
    pidf = os.path.join(TMP, "grandchild.pid")
    # a) im lang + co chau ngu 60 s -> STALL, ca cay bi dung
    code_a = ("import subprocess,sys,time;"
              f"p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']);open(r'{pidf}','w').write(str(p.pid));"
              "time.sleep(60)")
    t = time.time()
    out, code, secs = d.run_proc_watch([py, "-c", code_a], w, None, 120, 4, w)
    el = time.time() - t
    check(code == -2 and "STALL" in out, f"im lang 4 s phai tra code -2 + 'STALL', nhan code={code}")
    check(el < 30, f"phai dung trong ~stall_s + chu ky kiem (<30 s), mat {el:.0f} s")
    time.sleep(1)
    if os.path.exists(pidf):
        gp = int(open(pidf).read())
        alive = d.pid_alive(gp) if hasattr(d, "pid_alive") else True
        check(not alive, "tien trinh chau phai bi dung (kill ca cay)")
    # b) in ra moi 1 s trong 7 s -> khong STALL
    out, code, secs = d.run_proc_watch([py, "-u", "-c", "import time\nfor i in range(7):\n print(i, flush=True); time.sleep(1)"],
                                       w, None, 60, 3, w)
    check(code == 0 and "STALL" not in out and "6" in out, f"co output deu thi khong STALL, nhan code={code}")
    # c) im lang nhung ghi file moi 1 s -> khong STALL
    f = os.path.join(w, "progress.txt").replace("\\", "/")
    out, code, secs = d.run_proc_watch([py, "-c", f"import time\nfor i in range(7):\n open('{f}','a').write('x'); time.sleep(1)"],
                                       w, None, 60, 3, w)
    check(code == 0 and "STALL" not in out, f"ghi file deu thi khong STALL, nhan code={code}")
    # d) qua timeout tong -> code -1 TIMEOUT nhu cu
    out, code, secs = d.run_proc_watch([py, "-u", "-c", "import time\nwhile True:\n print('.', flush=True); time.sleep(0.5)"],
                                       w, None, 5, 30, w)
    check(code == -1 and "TIMEOUT" in out, f"qua timeout tong phai code -1 + TIMEOUT, nhan code={code}")
main_src = inspect.getsource(d.main) if hasattr(d, "main") else src
check("run_proc_watch(" in main_src, "main phai chay executor bang run_proc_watch (gate van run_proc)")
check("STALL_MIN" in src or "DELEGATE_STALL_MIN" in src, "nguong treo mac dinh 6 phut, doi duoc bang bien DELEGATE_STALL_MIN")
check("stall" in main_src and "mark_limited" in main_src, "khi STALL: mark_limited(executor, 'stall ...') roi chuyen nguoi ke tiep")

# ---- 3. Gate khong ke thua bien MSYS (Git Bash) ----
check(hasattr(d, "clean_env"), "thieu ham clean_env(env=None) bo MSYSTEM/MSYSTEM_PREFIX/MSYSTEM_CHOST/MINGW_PREFIX/MSYS/CHERE_INVOKING")
if hasattr(d, "clean_env"):
    e = d.clean_env({"MSYSTEM": "MINGW64", "MSYS": "x", "PATH": "p", "MINGW_PREFIX": "m"})
    check("MSYSTEM" not in e and "MSYS" not in e and "MINGW_PREFIX" not in e and e.get("PATH") == "p", f"clean_env sai: {e}")
check("clean_env(" in main_src, "main phai chay gate (va executor) voi env=clean_env(...)")

if fails:
    print("FAIL", len(fails))
    for x in fails:
        print(" -", x)
    sys.exit(1)
print("PASS test_watchdog_rr")
