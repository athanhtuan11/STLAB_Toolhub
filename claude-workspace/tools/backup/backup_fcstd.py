import hashlib, json, os, sys, tempfile
from datetime import datetime
from pathlib import Path


def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()


def cp(src, dst, expected):
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".stlab-", suffix=".tmp", dir=dst.parent)
    os.close(fd)
    tmp = Path(name)
    try:
        with src.open("rb") as a, tmp.open("wb") as b:
            for block in iter(lambda: a.read(1048576), b""):
                b.write(block)
            b.flush()
            os.fsync(b.fileno())
        if sha(tmp) != expected:
            raise OSError("SHA-256 mismatch after copy")
        os.replace(tmp, dst)
    finally:
        if tmp.exists():
            tmp.unlink()


def main():
    here = Path(__file__).resolve().parent
    cfg = Path(os.environ.get("STLAB_BACKUP_CONFIG", str(here / "backup.json")))
    with cfg.open(encoding="utf-8") as f:
        c = json.load(f)
    root = Path(c["source_root"])
    if not root.is_absolute():
        root = (here / root).resolve()
    keep = int(c["keep_versions"])
    if keep < 0:
        raise ValueError("keep_versions must be non-negative")
    files = {}
    for pat in c["include"]:
        for p in root.glob(pat):
            if p.is_file() and p.suffix == ".FCStd":
                files[p.relative_to(root)] = p
    stats = {r: {"copied": False, "unchanged": False} for r in files}
    dests = []
    pruned = 0
    for raw in c["destinations"]:
        d = Path(os.path.expandvars(raw)).expanduser()
        item = {"path": str(d), "status": "missing", "copied": 0}
        if not d.exists() and not d.parent.exists():
            dests.append(item)
            continue
        try:
            d.mkdir(parents=True, exist_ok=True)
            item["status"] = "ok"
            for rel, src in files.items():
                expected = sha(src)
                cur = d / "current" / rel
                if cur.is_file() and sha(cur) == expected:
                    stats[rel]["unchanged"] = True
                    continue
                if cur.is_file():
                    vd = d / "versions" / rel.parent
                    vd.mkdir(parents=True, exist_ok=True)
                    stamp = datetime.fromtimestamp(cur.stat().st_mtime).strftime("%Y%m%d-%H%M%S")
                    version = vd / (rel.stem + "." + stamp + ".FCStd")
                    n = 1
                    while version.exists():
                        version = vd / (rel.stem + "." + stamp + "-" + str(n) + ".FCStd")
                        n += 1
                    os.replace(cur, version)
                    versions = sorted(vd.glob(rel.stem + ".*.FCStd"), key=lambda p: p.name)
                    excess = max(0, len(versions) - keep)
                    for old in versions[:excess]:
                        old.unlink()
                    pruned += excess
                cp(src, cur, expected)
                stats[rel]["copied"] = True
                item["copied"] += 1
        except Exception as e:
            item["status"] = "error"
            item["error"] = str(e)
        dests.append(item)
    result = {
        "time": datetime.now().astimezone().isoformat(),
        "copied": sum(1 for x in stats.values() if x["copied"]),
        "unchanged": sum(1 for x in stats.values() if not x["copied"] and x["unchanged"]),
        "versions_pruned": pruned,
        "destinations": dests,
    }
    state = Path(
        os.environ.get(
            "STLAB_BACKUP_STATE",
            os.path.join(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local")), "stlab-backup"),
        )
    )
    state.mkdir(parents=True, exist_ok=True)
    (state / "last.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if any(x["status"] == "ok" for x in dests) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
