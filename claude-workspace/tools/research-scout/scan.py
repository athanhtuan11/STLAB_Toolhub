import datetime as dt, json, math, os, sys, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path
import store


def now():
    v = os.environ.get("STLAB_RESEARCH_NOW")
    return dt.datetime.fromisoformat(v) if v else dt.datetime.now(dt.timezone.utc)


def date(v):
    if not v:
        return None
    try:
        return dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        try:
            return parsedate_to_datetime(v)
        except Exception:
            return None


def fetch(url):
    h = {"User-Agent": "stlab-research-scout"}
    if "api.github.com" in url and os.environ.get("GITHUB_TOKEN"):  # tuy chon, chi doc tu bien moi truong
        h["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    r = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(r, timeout=20) as x:
        return x.read()


def data_file(name, url):
    d = os.environ.get("STLAB_RESEARCH_FIXTURES")
    if d:
        p = Path(d) / name
        if not p.exists():
            raise FileNotFoundError(name)
        return p.read_bytes()
    return fetch(url)


def match_topic(title, summary, source, topics, hint=None):
    s = title.casefold()
    found = [t for t in topics if any(str(k).casefold() in s for k in t.get("keywords", []))]
    if not found:
        s = summary.casefold()
        found = [t for t in topics if any(str(k).casefold() in s for k in t.get("keywords", []))]
    if found:
        return max(found, key=lambda t: float(t.get("weight", 1))).get("id")
    if hint:  # chu de khai trong watch (truy van github / repo theo doi)
        return hint
    for t in topics:
        if t.get("id", "").casefold() in source.casefold() or t.get("ten", "").casefold() in source.casefold():
            return t.get("id")
    return "khac"


def add(src, url, title, summary, pub, base, topics, hint=None, strict=False):
    """strict: chi lay khi tieu de/tom tat chua tu khoa chu de (HN hay lac de)."""
    if strict and match_topic(title, summary, "", topics) == "khac":
        return 0
    n = now()
    d = date(pub)
    fresh = 1 if d is None or (n - d).total_seconds() <= 604800 else 0.5
    topic = match_topic(title, summary, src, topics, hint)
    return store.add_item(
        src,
        url,
        title,
        summary,
        pub,
        topic,
        base * store.topic_weight(topic) * fresh,
        first_seen=n.isoformat(),
        extra={"base_score": base},
    )


def main():
    w = store.read_watch()
    ts = w.get("topics", [])
    counts = {"github": 0, "release": 0, "feed": 0, "hn": 0}
    errors = []
    if "--rescore" in sys.argv:
        c = store.connect()
        try:
            for r in c.execute("SELECT id,topic,source,published FROM items").fetchall():
                d = date(r["published"])
                fresh = 1 if d is None or (now() - d).total_seconds() <= 604800 else 0.5
                base = json.loads(
                    c.execute("SELECT extra FROM items WHERE id=?", (r["id"],)).fetchone()[0] or "{}"
                ).get("base_score", 2 if r["source"] == "release" else 1)
                c.execute(
                    "UPDATE items SET score=? WHERE id=?", (base * store.topic_weight(r["topic"]) * fresh, r["id"])
                )
            c.commit()
        finally:
            c.close()
        print(json.dumps({"new": 0, "by_source": counts, "errors": []}))
        return 0
    for i, q in enumerate(w.get("github_queries", [])):
        if i and not os.environ.get("STLAB_RESEARCH_FIXTURES") and not os.environ.get("GITHUB_TOKEN"):
            time.sleep(7)  # search API khong dang nhap: 10 luot/phut
        try:
            since = (now() - dt.timedelta(days=int(q.get("pushed_days", 90)))).date().isoformat()
            url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
                {"q": q["q"] + " pushed:>" + since, "sort": "updated"}
            )
            if os.environ.get("STLAB_RESEARCH_FIXTURES"):
                obj = json.loads(data_file("github_search.json", url))
            else:
                obj = json.loads(fetch(url))
            for x in obj.get("items", []):
                stars = int(x.get("stargazers_count", 0))
                if stars >= int(q.get("min_stars", 0)):
                    counts["github"] += add(
                        "github",
                        x.get("html_url"),
                        x.get("full_name", ""),
                        x.get("description") or "",
                        x.get("pushed_at"),
                        math.log10(stars + 1),
                        ts,
                        hint=q.get("topic"),
                    )
        except Exception as e:
            errors.append("github: " + str(e))
    for entry in w.get("repos", []):
        repo = entry if isinstance(entry, str) else entry["repo"]
        hint = None if isinstance(entry, str) else entry.get("topic")
        try:
            owner, name = repo.split("/", 1)
            url = "https://api.github.com/repos/" + repo + "/releases?per_page=1"
            raw = data_file("releases_" + owner + "__" + name + ".json", url)
            obj = json.loads(raw)
            for x in obj[:1]:
                counts["release"] += add(
                    "release",
                    x.get("html_url"),
                    repo + " " + (x.get("tag_name") or x.get("name") or ""),
                    (x.get("name") or "") + " " + (x.get("body") or "")[:300],
                    x.get("published_at"),
                    2,
                    ts,
                    hint=hint,
                )
        except Exception as e:
            errors.append("release " + repo + ": " + str(e))
    for f in w.get("feeds", []):
        name = f.get("name", "feed")
        try:
            root = ET.fromstring(data_file("feed_" + name + ".xml", f["url"]))
            ns = {"a": "http://www.w3.org/2005/Atom"}
            for x in root.findall(".//item"):
                counts["feed"] += add(
                    "feed",
                    x.findtext("link") or "",
                    x.findtext("title") or "",
                    x.findtext("description") or "",
                    x.findtext("pubDate"),
                    1,
                    ts,
                )
            for x in root.findall("a:entry", ns):
                link = next((z.get("href") for z in x.findall("a:link", ns) if z.get("href")), "")
                pub = x.findtext("a:updated", default="", namespaces=ns) or x.findtext(
                    "a:published", default="", namespaces=ns
                )
                counts["feed"] += add(
                    "feed",
                    link,
                    x.findtext("a:title", default="", namespaces=ns),
                    x.findtext("a:summary", default="", namespaces=ns),
                    pub,
                    1,
                    ts,
                )
        except Exception as e:
            errors.append(name + ": " + str(e))
    for q in w.get("hn", []):
        try:
            url = "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode(
                {"query": q["query"], "tags": "story"}
            )
            obj = json.loads(data_file("hn.json", url))
            for x in obj.get("hits", []):
                points = int(x.get("points") or 0)
                if points >= int(q.get("min_points", 0)):
                    link = x.get("url") or "https://news.ycombinator.com/item?id=" + str(x.get("objectID"))
                    counts["hn"] += add(
                        "hn",
                        link,
                        x.get("title", ""),
                        x.get("story_text") or "",
                        x.get("created_at"),
                        math.log10(points + 1),
                        ts,
                        strict=True,
                    )
        except Exception as e:
            errors.append("hn " + q.get("query", "") + ": " + str(e))
    print(json.dumps({"new": sum(counts.values()), "by_source": counts, "errors": errors}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
