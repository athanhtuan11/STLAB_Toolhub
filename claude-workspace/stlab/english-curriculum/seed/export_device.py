#!/usr/bin/env python3
"""Sinh thu muc bai Seed cho may Cu Bong tu stlab/english-curriculum/seed/units.yaml.

Mac dinh ghi maker/english-teacher/lessons-seed/ (tinh tu vi tri script).
--check: chi so sanh, khong ghi; khac/Thieu/thua -> in ten file, exit 1; giong -> OK, exit 0.
"""
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                       # claude-workspace
UNITS = HERE / "units.yaml"
OUT_DIR = ROOT / "maker" / "english-teacher" / "lessons-seed"

HEADING = "## Chỉ dẫn cho AI"
DAILY = "hello, thank you, good job, bye-bye, let's sing"
ROADMAP_TITLE = "# Lộ trình Cú Bông theo giáo trình Seed (sinh tự động – không sửa tay)"


def slug(theme):
    """theme chu thuong, chi giu chu/so ASCII, noi bang '-'; vd 'Farm animals' -> 'farm-animals'."""
    out = []
    for ch in str(theme).lower():
        out.append(ch if ("a" <= ch <= "z") or ("0" <= ch <= "9") else "-")
    return "-".join(p for p in "".join(out).split("-") if p)


def dot(text):
    """Them dau cham cuoi neu chuoi chua ket thuc bang '.'."""
    s = str(text).rstrip()
    return s if s.endswith(".") else s + "."


def lesson_id(unit):
    return "%s-%s" % (unit["id"], slug(unit["theme"]))


def unit_md(level, unit):
    name = str(level["name"])
    age = str(level["age"])
    age_short = age.replace("tuổi", "").strip()
    lid = unit["id"]
    k = lid.rsplit("-u", 1)[1]
    theme = str(unit["theme"])
    theme_vi = str(unit["theme_vi"])
    core = ", ".join(str(w) for w in unit["core"])
    plus = ", ".join(str(w) for w in unit.get("plus") or [])
    patterns = " · ".join(str(p) for p in unit.get("patterns") or [])
    can_do = "; ".join(str(c) for c in unit.get("can_do") or [])
    song = dot(unit.get("song", ""))
    make = dot(unit.get("make", ""))
    tell = dot(unit.get("tell", ""))

    lines = [
        "# %s · Unit %s – %s (%s)" % (name, k, theme, theme_vi),
        "",
        "Tuổi: %s. Sinh tự động từ stlab/english-curriculum/seed/units.yaml bằng export_device.py – không sửa tay." % age,
        "Lớp học cùng chủ đề: stlab/english-curriculum/seed/lesson-plans/%s-*.md." % lid,
        "",
        HEADING,
        "",
        "(Dùng cho máy chủ. Tiếng Anh, nói ngắn.)",
        "",
        "- Lesson: %s (%s, ages %s). Vocabulary: %s. Teach ONE word per turn after greeting. "
        "Say each word twice, child repeats once." % (theme, name, age_short, core),
        "- Sentence patterns for this unit (use them as short models, ages 4+ only): %s" % dot(patterns),
        "- Extra words only for a confident child, after the vocabulary is solid: %s" % dot(plus),
        "- Song idea: %s If you do not know the exact words, make up a short simple chant with the vocabulary instead." % song,
        "- The class makes: %s Ask the child to tell about it like: %s" % (make, tell),
        "- Goals: %s" % dot(can_do),
        "- Only listening and speaking: never ask the child to read or write.",
        "- If child is silent: wait 5 seconds, say the word again and invite once more; then move on. "
        "Do not ask more than twice in a row.",
        "- If child speaks Vietnamese: reply in one short Vietnamese sentence, then teach one English word.",
        "- If child says a word wrong: praise the try and repeat the right word once, slowly. Never say \"wrong\".",
        "- Never ask the child's real name, age, school, address or parents' jobs.",
        "- If child seems hurt or scared, say in Vietnamese: \"Con nói với ba mẹ nhé!\"",
        "- Do not end the session or say goodbye yourself; the system decides when to stop "
        "(teaching the WORD 'bye-bye' is fine).",
        "",
    ]
    return "\n".join(lines)


def roadmap_rows(units):
    """Chia core thanh cap 2 tu theo thu tu, bo tu da ra o hang truoc trong cung bang."""
    seen = set()
    rows = []
    for u in units:
        lid = lesson_id(u)
        core = [str(w).lower() for w in u["core"]]
        for i in range(0, len(core), 2):
            chunk = core[i:i + 2]
            new = [w for w in chunk if w not in seen]
            if not new:
                continue
            seen.update(new)
            rows.append({"lesson_id": lid, "new": new})
    return rows


def roadmap_table(rows):
    out, review = [], "-"
    for i, r in enumerate(rows, 1):
        out.append("Week %d: %s | new: %s | review: %s | daily: %s | song: %s"
                   % (i, r["lesson_id"], ", ".join(r["new"]), review, DAILY, r["lesson_id"]))
        review = ", ".join(r["new"])
    return "\n".join(out)


def roadmap_md(by_id):
    young = roadmap_rows(by_id["s1"]["units"])
    old = roadmap_rows(by_id["s2"]["units"] + by_id["s3"]["units"])
    lines = [
        ROADMAP_TITLE,
        "",
        "Nguồn: stlab/english-curriculum/seed/units.yaml (export_device.py). Bé 2–3 tuổi học Seed 1; "
        "bé 4–5 tuổi học Seed 2 rồi Seed 3.",
        "Mỗi hàng 2 từ Core mới theo đúng thứ tự trong units.yaml; tiến độ theo con trỏ từ của máy chủ.",
        "",
        "## Lịch tuần 2–3 tuổi (máy đọc)",
        "",
        "```text",
        roadmap_table(young),
        "```",
        "",
        "## Lịch tuần (máy đọc)",
        "",
        "```text",
        roadmap_table(old),
        "```",
        "",
    ]
    return "\n".join(lines)


def generate():
    data = yaml.safe_load(UNITS.read_text(encoding="utf-8"))
    levels = data["levels"]
    by_id = {lv["id"]: lv for lv in levels}
    files = {}
    for lv in levels:
        for u in lv["units"]:
            files["%s.md" % lesson_id(u)] = unit_md(lv, u)
    files["ROADMAP.md"] = roadmap_md(by_id)
    return files


def main(argv):
    files = generate()
    if "--check" in argv:
        existing = {p.name for p in OUT_DIR.glob("*.md")} if OUT_DIR.is_dir() else set()
        bad = []
        for name in sorted(set(files) | existing):
            if name not in files or name not in existing:
                bad.append(name)
            elif (OUT_DIR / name).read_bytes() != files[name].encode("utf-8"):
                bad.append(name)
        if bad:
            print("\n".join(bad))
            return 1
        print("OK")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in OUT_DIR.glob("*.md"):
        p.unlink()
    for name in sorted(files):
        (OUT_DIR / name).write_bytes(files[name].encode("utf-8"))
    print("wrote %d files to %s" % (len(files), OUT_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
