# Gate "viec song song" cho delegate.py (Claude viet 2026-11-02, executor KHONG sua). Khong goi executor that.
#   python tests/test_parallel.py      (chay tu tools/delegate)
# (A) khoa ghi allow -> file do run khac dang chay so huu KHONG tinh outside_allow cua run nay.
# (B) worktree: true -> git worktree rieng + junction community/ + chep file chua commit; chi chep ve file allow.
import importlib.util, inspect, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "delegate.py")
spec = importlib.util.spec_from_file_location("delegate", SRC)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

tmp = tempfile.mkdtemp(prefix="delegate-par-")
d.USAGE = os.path.join(tmp, "usage")
os.makedirs(os.path.join(d.USAGE, "locks"))
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
        print("FAIL:", msg)
    else:
        print("ok  :", msg)


# ---------- (A) khoa ghi allow ----------
rd_me = os.path.join(tmp, "run-me")
rd_other = os.path.join(tmp, "run-other")
os.makedirs(rd_me), os.makedirs(rd_other)
p = d.take_lock("tools/x", "task-me", rd_me, allow_ws=["tools/x/a.py"])
lk = json.load(open(p, encoding="utf-8"))
check(lk.get("allow_ws") == ["tools/x/a.py"], "A1 take_lock ghi allow_ws vao khoa")
check(lk.get("cwd") == "tools/x", "A1 take_lock ghi cwd vao khoa")

# run khac dang song (pid hien tai) so huu build.py; run da chet (pid gia) so huu docs/*
json.dump(dict(pid=os.getpid(), task="other", start="x", run_dir=rd_other, cwd="maker/y",
               allow_ws=["maker/y/freecad/scripts/build.py"]),
          open(os.path.join(d.USAGE, "locks", "maker_y.json"), "w", encoding="utf-8"))
json.dump(dict(pid=999999, task="dead", start="x", run_dir=os.path.join(tmp, "run-dead"), cwd="docs",
               allow_ws=["docs/*"]),
          open(os.path.join(d.USAGE, "locks", "docs.json"), "w", encoding="utf-8"))
files = ["maker/y/freecad/scripts/build.py", "docs/a.md", "tools/x/a.py"]
got = set(d.other_runs_claim(files, rd_me))
check(got == {"maker/y/freecad/scripts/build.py"}, f"A2 other_runs_claim chi lay file cua run khac CON SONG ({got})")
check(set(d.other_runs_claim(files, rd_other)) == {"tools/x/a.py"}, "A3 khong tu nhan file cua chinh minh")
src = inspect.getsource(d.run_task)
check("other_runs" in src and "other_runs_claim" in src, "A4 run_task loai file run khac khoi outside_allow, ghi result['other_runs']")

# ---------- (B) worktree ----------
repo = os.path.join(tmp, "repo")
os.makedirs(os.path.join(repo, "ws", "community"))
def git(*a, cwd=repo):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout
git("init", "-q")
git("config", "user.email", "t@t"), git("config", "user.name", "t")
open(os.path.join(repo, ".gitignore"), "w").write("ws/community/\n*.FCStd\n")
open(os.path.join(repo, "ws", "a.txt"), "w").write("v1")
git("add", "-A"), git("commit", "-qm", "init")
open(os.path.join(repo, "ws", "a.txt"), "w").write("v2-chua-commit")          # sua chua commit
open(os.path.join(repo, "ws", "b.txt"), "w").write("moi")                     # file moi chua commit
open(os.path.join(repo, "ws", "community", "x.step"), "w").write("STEP")      # bi ignore, gate can doc
open(os.path.join(repo, "ws", "m.FCStd"), "w").write("FC")                    # bi ignore, gate can doc
d.WS = os.path.join(repo, "ws")

rd_wt = os.path.join(tmp, "run-wt")
os.makedirs(rd_wt)
wt = d.make_worktree(rd_wt)                                    # tra ve thu muc tuong ung WS trong worktree
check(os.path.isdir(wt) and os.path.normcase(wt) != os.path.normcase(d.WS), "B1 make_worktree tao thu muc rieng")
check(open(os.path.join(wt, "a.txt")).read() == "v2-chua-commit", "B2 file sua chua commit duoc chep vao worktree")
check(os.path.exists(os.path.join(wt, "b.txt")), "B3 file moi chua commit duoc chep vao worktree")
check(open(os.path.join(wt, "community", "x.step")).read() == "STEP", "B4 community/ doc duoc trong worktree (junction)")
check(os.path.exists(os.path.join(wt, "m.FCStd")), "B5 file .FCStd bi ignore co mat trong worktree")

open(os.path.join(wt, "a.txt"), "w").write("v3-executor")
open(os.path.join(wt, "c.txt"), "w").write("ngoai allow")
copied, skipped = d.sync_back(wt, ["a.txt"])
check(open(os.path.join(d.WS, "a.txt")).read() == "v3-executor" and "a.txt" in copied, "B6 sync_back chep file allow ve")
check(not os.path.exists(os.path.join(d.WS, "c.txt")) and "c.txt" in skipped, "B7 sync_back KHONG chep file ngoai allow")

d.remove_worktree(wt)
check(not os.path.exists(wt), "B8 remove_worktree xoa thu muc worktree")
check(open(os.path.join(d.WS, "community", "x.step")).read() == "STEP", "B9 XOA WORKTREE KHONG LAM MAT community/ GOC")
check(os.path.exists(os.path.join(d.WS, "m.FCStd")), "B10 xoa worktree khong dong vao .FCStd goc")
check(len(git("worktree", "list").strip().splitlines()) == 1, "B11 git worktree list chi con cay chinh")
check("worktree" in inspect.getsource(d.run_task), "B12 run_task doc meta worktree: true")

subprocess.run([sys.executable, "-m", "py_compile", SRC], check=True)
shutil.rmtree(tmp, ignore_errors=True)
print("PASS" if not fails else f"{len(fails)} FAIL")
sys.exit(1 if fails else 0)
