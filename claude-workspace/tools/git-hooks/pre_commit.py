#!/usr/bin/env python3
"""STLab pre-commit: chan file khong duoc len git va loi Python co ban.

Chay duoc trong repo git bat ky. Mac dinh xet file da stage (doc tu index);
--all xet moi file git ls-files (dung cho CI). Ngoai stdlib chi can lenh
`ruff` neu co (khong co thi bo qua luat loi Python, chi canh bao).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WS = "claude-workspace/"
SIZE_LIMIT = 2 * 1024 * 1024
MEDIA_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".mkv",
    ".mp3", ".wav", ".m4a", ".pdf",
}
SECRETS = (
    ("token-sk", re.compile(rb"sk-[A-Za-z0-9_-]{20,}")),
    ("token-github", re.compile(rb"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("token-aws", re.compile(rb"AKIA[0-9A-Z]{16}")),
    ("private-key", re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)
RUFF_SELECT = "E9,F63,F7,F82"
GUIDE = ("Commit bi chan: go file vi pham khoi git (git restore --staged <file>) "
         "hoac chuyen file ra ngoai repo roi commit lai.")


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True)


def _find_ruff():
    found = shutil.which("ruff")
    if found:
        return found
    exe = Path(sys.executable)
    for name in ("ruff.exe", "ruff"):
        cand = exe.parent / name
        if cand.is_file():
            return str(cand)
    return None


def path_rules(rel):
    """Cac luat chi dua vao duong dan (rel tinh tu goc repo, dang a/b/c)."""
    low = rel.lower()
    base = low.rsplit("/", 1)[-1]
    found = []
    if low.startswith(WS + "maker/") and low.endswith(".fcstd"):
        found.append("model-fcstd")
    if base == ".env" or base.startswith(".env."):
        found.append("env")
    if low.startswith(WS + "community/"):
        rest = low[len(WS + "community/"):]
        if "/" in rest and not rest.startswith("reports/"):
            found.append("community-clone")
    if low.startswith(WS + "maker/"):
        if os.path.splitext(base)[1] in MEDIA_EXT:
            found.append("media-maker")
    return found


def _ruff_bad(items):
    """Tra ve danh sach file .py co loi; items = [(rel, data_bytes)]."""
    if not items:
        return []
    ruff = _find_ruff()
    if not ruff:
        print("CANH BAO: khong co ruff tren PATH, bo qua kiem loi Python.")
        return []
    tmp = tempfile.mkdtemp(prefix="stlab-ruff-")
    tmp_root = Path(tmp)
    mapping = {}
    try:
        for i, (rel, data) in enumerate(items):
            name = rel.replace("\\", "/").rsplit("/", 1)[-1]
            dest = tmp_root / str(i) / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            mapping["%d/%s" % (i, name)] = rel
        r = subprocess.run(
            [ruff, "check", "--select", RUFF_SELECT, "--no-cache", "--quiet", "."],
            cwd=str(tmp_root), capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if r.returncode == 0:
            return []
        bad = []
        seen = set()
        for line in (r.stdout + "\n" + r.stderr).splitlines():
            key = line.replace("\\", "/")
            if key.startswith("./"):
                key = key[2:]
            head = key.split(":", 1)[0]
            rel = mapping.get(head)
            if rel and rel not in seen:
                seen.add(rel)
                bad.append(rel)
        if bad:
            return bad
        return _ruff_bad_per_file(ruff, items, tmp_root)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _ruff_bad_per_file(ruff, items, tmp_root):
    bad = []
    for i, (rel, data) in enumerate(items):
        name = rel.replace("\\", "/").rsplit("/", 1)[-1]
        d = tmp_root / ("single-%d" % i)
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_bytes(data)
        r = subprocess.run(
            [ruff, "check", "--select", RUFF_SELECT, "--no-cache", "--quiet", name],
            cwd=str(d), capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if r.returncode != 0:
            bad.append(rel)
    return bad


def main(argv):
    scan_all = "--all" in argv
    r = _git(None, "rev-parse", "--show-toplevel")
    if r.returncode != 0:
        print("Khong tim thay goc git; bo qua kiem tra.")
        return 0
    root = r.stdout.decode("utf-8", "replace").strip()
    if not root:
        return 0

    if scan_all:
        raw = _git(root, "ls-files", "-z").stdout
    else:
        raw = _git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").stdout
    rels = [x.decode("utf-8", "replace") for x in raw.split(b"\x00") if x]

    violations = []
    seen = set()

    def add(rule, rel):
        key = (rule, rel)
        if key not in seen:
            seen.add(key)
            violations.append(key)

    py_items = []
    for rel in rels:
        for rule in path_rules(rel):
            add(rule, rel)

        if scan_all:
            abs_path = os.path.join(root, *rel.split("/"))
            if not os.path.isfile(abs_path):
                continue
            size = os.path.getsize(abs_path)
        else:
            r = _git(root, "cat-file", "-s", ":" + rel)
            if r.returncode != 0:
                continue
            try:
                size = int(r.stdout.strip())
            except ValueError:
                continue

        if size > SIZE_LIMIT:
            add("file-lon", rel)
            continue

        if scan_all:
            try:
                data = Path(abs_path).read_bytes()
            except OSError:
                continue
        else:
            data = _git(root, "show", ":" + rel).stdout

        if b"\x00" not in data:
            for rule, pattern in SECRETS:
                if pattern.search(data):
                    add(rule, rel)
                    break

        if rel.lower().endswith(".py"):
            py_items.append((rel, data))

    for rel in _ruff_bad(py_items):
        add("loi-python", rel)

    for rule, rel in violations:
        print("CHAN %s: %s" % (rule, rel))
    if violations:
        print(GUIDE)
        return 1
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
