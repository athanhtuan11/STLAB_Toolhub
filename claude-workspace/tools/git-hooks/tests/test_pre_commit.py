# Gate hook pre-commit (Claude viet, executor KHONG sua). Chay tu claude-workspace:
#   python tools/git-hooks/tests/test_pre_commit.py
# Dung repo git tam, khong dung repo that.
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "pre_commit.py"
TMP = Path(tempfile.mkdtemp(prefix="stlab-precommit-test-"))
WS = "claude-workspace"


def git(*a, cwd=TMP):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True)


git("init", "-q")
git("config", "user.email", "t@t")
git("config", "user.name", "t")
git("config", "core.autocrlf", "false")


def case(files, expect_ok, must_say=None):
    """files: {duong_dan_tuong_doi_goc_repo: bytes}. Stage roi chay hook, sau do reset index."""
    for rel, data in files.items():
        p = TMP / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        git("add", "-f", rel)
    r = subprocess.run([sys.executable, str(HOOK)], cwd=TMP, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONUTF8="1"))
    out = r.stdout + r.stderr
    git("reset", "-q")
    for rel in files:
        (TMP / rel).unlink()
    ok = r.returncode == 0
    assert ok == expect_ok, f"{list(files)}: mong {'cho qua' if expect_ok else 'chan'}, exit={r.returncode}\n{out}"
    if must_say:
        assert must_say in out, f"thieu '{must_say}' trong:\n{out}"


# cho qua
case({f"{WS}/tools/x/ok.py": b"import os\nprint(os.name)\n", f"{WS}/docs/a.md": b"# ok\n"}, True)
case({f"{WS}/community/pins.tsv": b"a\tb\n", f"{WS}/community/links.tsv": b"a\tb\n"}, True)
case({f"{WS}/maker/du-an/design/concept.svg": b"<svg/>"}, True)            # svg la ma nguon, khong phai media
case({f"{WS}/tools/parts-library/img/relay.png": b"x" * 100}, True)  # anh ngoai maker/ duoc phep

# chan: file model, bi mat, ban clone cong dong, media maker, file lon, loi cu phap python, token
case({f"{WS}/maker/du-an/freecad/a.FCStd": b"PK"}, False, "a.FCStd")
case({f"{WS}/maker/du-an/.env": b"X=1\n"}, False, ".env")
case({f"{WS}/studio/.env.local": b"X=1\n"}, False, ".env.local")
case({f"{WS}/community/some-repo/README.md": b"x"}, False, "community/some-repo/README.md")
case({f"{WS}/maker/du-an/media/a.mp4": b"x"}, False, "a.mp4")
case({f"{WS}/maker/du-an/design/b.JPG": b"x"}, False, "b.JPG")
case({f"{WS}/docs/big.bin": b"0" * (2 * 1024 * 1024 + 1)}, False, "big.bin")
case({f"{WS}/tools/x/bad.py": b"def f(:\n    pass\n"}, False, "bad.py")
case({f"{WS}/tools/x/undef.py": b"print(chua_dinh_nghia)\n"}, False, "undef.py")
case({f"{WS}/tools/x/conf.py": b'KEY = "sk-' + b"a1B2" * 10 + b'"\n'}, False, "conf.py")
case({f"{WS}/tools/x/gh.md": b"token ghp_" + b"A" * 36 + b"\n"}, False, "gh.md")
case({f"{WS}/tools/x/k.txt": b"-----BEGIN OPENSSH " + b"PRIVATE KEY-----\nabc\n"}, False, "k.txt")  # tach chuoi: hook khong chan file test

# file da xoa (staged deletion) khong lam hook loi
p = TMP / f"{WS}/docs/del.md"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("x")
git("add", str(p.relative_to(TMP)))
git("commit", "-qm", "c", "--no-verify")
git("rm", "-q", str(p.relative_to(TMP)))
r = subprocess.run([sys.executable, str(HOOK)], cwd=TMP, capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr

# --all: quet moi file da theo doi (dung cho CI)
r = subprocess.run([sys.executable, str(HOOK), "--all"], cwd=TMP, capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr

shutil.rmtree(TMP, ignore_errors=True)
print("test_pre_commit PASS")
