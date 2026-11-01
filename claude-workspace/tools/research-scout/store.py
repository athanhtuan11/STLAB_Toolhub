import json, os, sqlite3
from pathlib import Path

STATUSES = {"moi", "quan-tam", "bo-qua"}


def _path():
    v = os.environ.get("STLAB_RESEARCH_DB")
    return (
        Path(v)
        if v
        else Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
        / "stlab-research"
        / "research.db"
    )


def connect():
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(p))
    c.row_factory = sqlite3.Row
    c.executescript(
        "CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY,source TEXT,url TEXT UNIQUE,title TEXT,summary TEXT,published TEXT,topic TEXT,score REAL,status TEXT,first_seen TEXT,extra TEXT); CREATE TABLE IF NOT EXISTS digests(id INTEGER PRIMARY KEY,week TEXT,created TEXT,model TEXT,content TEXT,item_ids TEXT);"
    )
    return c


def add_item(
    source, url, title, summary="", published=None, topic="khac", score=0, status="moi", first_seen=None, extra=None
):
    c = connect()
    try:
        x = c.execute(
            "INSERT OR IGNORE INTO items(source,url,title,summary,published,topic,score,status,first_seen,extra) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                source,
                url,
                title,
                summary,
                published,
                topic,
                score,
                status,
                first_seen,
                json.dumps(extra or {}, ensure_ascii=False),
            ),
        )
        c.commit()
        return x.rowcount > 0
    finally:
        c.close()


def list_items(topic=None, status=None, limit=200):
    c = connect()
    try:
        q = "SELECT * FROM items WHERE 1=1"
        a = []
        if topic is not None:
            q += " AND topic=?"
            a.append(topic)
        if status is not None:
            q += " AND status=?"
            a.append(status)
        return [dict(r) for r in c.execute(q + " ORDER BY score DESC,id DESC LIMIT ?", a + [limit])]
    finally:
        c.close()


def set_status(item_id, status):
    if status not in STATUSES:
        return False
    c = connect()
    try:
        x = c.execute("UPDATE items SET status=? WHERE id=?", (status, item_id))
        c.commit()
        return x.rowcount > 0
    finally:
        c.close()


def latest_digest():
    c = connect()
    try:
        r = c.execute("SELECT * FROM digests ORDER BY id DESC LIMIT 1").fetchone()
        return dict(r) if r else None
    finally:
        c.close()


def _watch_path(path=None):
    return Path(path or os.environ.get("STLAB_RESEARCH_WATCH", Path(__file__).with_name("watch.yaml")))


def read_watch(path=None):
    p = _watch_path(path)
    s = p.read_text(encoding="utf-8")
    try:
        import yaml

        return yaml.safe_load(s) or {}
    except ImportError:
        return json.loads(s)


def topics(watch_path=None):
    return read_watch(watch_path).get("topics", [])


def topic_weight(topic):
    # "khac" (khong khop chu de nao) chi nua trong so -> khong lan at tin dung chu de
    base = next((float(t.get("weight", 1)) for t in topics() if t.get("id") == topic), 0.5 if topic == "khac" else 1.0)
    c = connect()
    try:
        up = c.execute("SELECT count(*) FROM items WHERE topic=? AND status='quan-tam'", (topic,)).fetchone()[0]
        down = c.execute("SELECT count(*) FROM items WHERE topic=? AND status='bo-qua'", (topic,)).fetchone()[0]
    finally:
        c.close()
    return max(0.2, min(3, base * (1 + 0.2 * (up - down))))
