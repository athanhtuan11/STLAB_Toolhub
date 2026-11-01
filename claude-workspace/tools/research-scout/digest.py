import datetime as dt, json, os, shlex, subprocess, sys, tempfile
from pathlib import Path
import store

CHAIN = ["gemini-3.8-flash-medium", "claude-sonnet-4-6", "claude-opus-4-6-thinking", "gpt-oss-120b-medium"]


def now():
    v = os.environ.get("STLAB_RESEARCH_NOW")
    return dt.datetime.fromisoformat(v) if v else dt.datetime.now(dt.timezone.utc)


def main():
    if "--print-chain" in sys.argv:
        print(json.dumps({"chain": CHAIN}))
        return 0
    w = store.read_watch()
    cfg = w.get("digest", {})
    week = now().strftime("%G-W%V")
    force = "--force" in sys.argv
    c = store.connect()
    try:
        exists = c.execute("SELECT 1 FROM digests WHERE week=?", (week,)).fetchone()
        if exists and not force:
            d = c.execute(
                "SELECT model,item_ids FROM digests WHERE week=? ORDER BY id DESC LIMIT 1", (week,)
            ).fetchone()
            print(
                json.dumps(
                    {
                        "week": week,
                        "model": d["model"],
                        "items": json.loads(d["item_ids"]),
                        "prompt_file": "",
                        "errors": [],
                    }
                )
            )
            return 0
        items = [x for x in store.list_items(limit=10000) if x["status"] != "bo-qua" and x.get("first_seen")]
        cutoff = now() - dt.timedelta(days=int(cfg.get("days", 7)))
        items = [x for x in items if dt.datetime.fromisoformat(x["first_seen"]) >= cutoff][: int(cfg.get("top_n", 10))]
        prompt = "Bối cảnh STLab, trung tâm STEAM Lâm Đồng: robot, in 3D Bambu A1, Arduino/ESP32/Raspberry Pi/STM32, FreeCAD, lớp 4-12. Chỉ dùng dữ liệu công khai đã quét; không bịa số. Hãy đưa ra top 5 gợi ý, mỗi gợi ý nêu vì sao hợp STLab, việc nên làm và mức tin cậy.\n"
        for x in items:
            prompt += (
                "- "
                + x["title"]
                + " | "
                + x["url"]
                + " | "
                + str(x["summary"] or "")[:200]
                + " | "
                + str(x["topic"])
                + "\n"
            )
        fd, path = tempfile.mkstemp(prefix="stlab-research-prompt-", suffix=".txt")
        os.close(fd)
        Path(path).write_text(prompt, encoding="utf-8")
        errors = []
        model = "khong-ai"
        content = "\n".join("- " + x["title"] + " | " + x["url"] for x in items)
        command = os.environ.get("STLAB_RESEARCH_LLM_CMD")
        if command:
            p = subprocess.run(command, shell=True, input=prompt, text=True, capture_output=True, encoding="utf-8")
            if p.returncode == 0 and "429" not in p.stdout.lower() and "quota" not in p.stdout.lower():
                model = "custom"
                content = p.stdout
            else:
                errors.append(p.stderr or p.stdout or "LLM command failed")
        else:
            for m in CHAIN:
                try:
                    with tempfile.TemporaryDirectory(prefix="stlab-research-empty-") as cwd:
                        p = subprocess.run(
                            ["agy", "-p", prompt, "--model", m, "--sandbox"],
                            cwd=cwd,
                            text=True,
                            capture_output=True,
                            encoding="utf-8",
                        )
                    if p.returncode == 0 and "429" not in p.stdout.lower() and "quota" not in p.stdout.lower():
                        model = m
                        content = p.stdout
                        break
                    errors.append(m + ": " + (p.stderr or p.stdout or "failed"))
                except Exception as e:
                    errors.append(m + ": " + str(e))
        c.execute(
            "INSERT INTO digests(week,created,model,content,item_ids) VALUES(?,?,?,?,?)",
            (week, now().isoformat(), model, content, json.dumps([x["id"] for x in items])),
        )
        c.commit()
        print(
            json.dumps(
                {
                    "week": week,
                    "model": model,
                    "items": [x["id"] for x in items],
                    "prompt_file": path,
                    "errors": errors,
                },
                ensure_ascii=False,
            )
        )
        return 0
    finally:
        c.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
