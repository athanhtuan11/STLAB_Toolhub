# Kiem giao an Seed (lesson-plans/<id>-*.md) theo mau s1-u1-hello.md va units.yaml.
#   python check_plans.py            # ca 24 chu de
#   python check_plans.py s2         # mot cap
#   python check_plans.py s2-u3      # mot chu de
# Moi giao an: 8 buoi dung ten/thu tu, bang phut lien tuc 0 -> 30, moi tu Core xuat hien o >= 3 buoi, moi tu Plus >= 1 buoi,
# du mau cau, buoi 6 co muc An toan, co So quan sat voi dung 2 muc "be lam duoc", co muc Gui phu huynh.
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PLANS = HERE / "lesson-plans"
NAMES = ["Meet", "Meet more", "Sing", "Story", "Play", "Make", "Tell", "Party"]
sys.stdout.reconfigure(encoding="utf-8")
data = yaml.safe_load((HERE / "units.yaml").read_text(encoding="utf-8"))
only = sys.argv[1] if len(sys.argv) > 1 else ""
fails, checked = [], 0


def has(word, text):
    return re.search(r"(?<![A-Za-z])" + re.escape(str(word)) + r"(?![A-Za-z])", text, flags=re.I) is not None


for lv in data["levels"]:
    for u in lv["units"]:
        uid = u["id"]
        if only and not uid.startswith(only):
            continue
        checked += 1
        files = sorted(PLANS.glob(f"{uid}-*.md"))
        if len(files) != 1:
            fails.append(f"{uid}: can dung 1 file lesson-plans/{uid}-<ten>.md, thay {len(files)}")
            continue
        text = files[0].read_text(encoding="utf-8")
        err = lambda m: fails.append(f"{files[0].name}: {m}")
        if not re.fullmatch(rf"{uid}-[a-z0-9]+(-[a-z0-9]+)*\.md", files[0].name):
            err("ten file phai kebab-case tieng Anh")
        head = text.split("\n## ")[0]
        if u["theme"] not in head or u["theme_vi"] not in head:
            err("dau file thieu ten chu de (Anh + Viet)")
        if len(text.splitlines()) < 90:
            err("qua ngan (< 90 dong) - chua du chi tiet")
        parts = re.split(r"^## Buổi (\d) – ([^\n:]+)", text, flags=re.M)
        sessions = {}
        for i in range(1, len(parts) - 2, 3):
            body = re.split(r"^## ", parts[i + 2], flags=re.M)[0]
            sessions[int(parts[i])] = (parts[i + 1].strip(), body)
        for n, name in enumerate(NAMES, 1):
            if n not in sessions:
                err(f"thieu '## Buổi {n} – {name}'")
                continue
            title, body = sessions[n]
            if title != name and not title.startswith(name + " "):
                err(f"buoi {n}: ten phai bat dau bang '{name}', dang la '{title}'")
            rows = re.findall(r"^\|\s*(\d+)–(\d+)\s*\|([^|]*)\|([^|]*)\|", body, flags=re.M)
            if not rows:
                err(f"buoi {n}: thieu bang | Phút | Việc | Giáo viên nói |")
                continue
            t = 0
            for a, b, viec, _ in rows:
                if int(a) != t or int(b) <= int(a):
                    err(f"buoi {n}: phut khong lien tuc tai {a}–{b}")
                    break
                if len(viec.strip()) < 8:
                    err(f"buoi {n}: o 'Việc' {a}–{b} qua so sai")
                t = int(b)
            if t != 30:
                err(f"buoi {n}: tong phut = {t}, phai 30")
            if len(rows) < 5:
                err(f"buoi {n}: can >= 5 buoc")
        bodies = {n: b for n, (_, b) in sessions.items()}
        for w in u["core"]:
            k = sum(has(w, b) for b in bodies.values())
            if k < 3:
                err(f"tu Core '{w}' chi co o {k} buoi (can >= 3)")
        for w in u["plus"]:
            if not any(has(w, b) for b in bodies.values()):
                err(f"tu Plus '{w}' khong co trong buoi nao")
        for p in u["patterns"]:
            first = re.split(r" – | / ", p)[0].strip().rstrip(".!?")
            if first.lower() not in text.lower():
                err(f"thieu mau cau '{first}'")
        if 6 in bodies and "**An toàn:**" not in bodies[6]:
            err("buoi 6 thieu dong '**An toàn:**'")
        if "## Sổ quan sát" not in text or not all(c in text for c in u["can_do"]):
            err("thieu '## Sổ quan sát' voi dung 2 muc can_do trong units.yaml")
        if "Gửi phụ huynh" not in text:
            err("thieu muc 'Gửi phụ huynh'")
        if u.get("make_needs") and "thay thế" not in text.lower():
            err("chu de can robot: phai ghi phuong an thay the")

if fails:
    print(f"FAIL ({len(fails)} loi / {checked} chu de)")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"PASS check_plans ({checked} chu de)")
