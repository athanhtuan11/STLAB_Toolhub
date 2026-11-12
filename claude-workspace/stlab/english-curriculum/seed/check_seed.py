# Kiem noi dung chang Seed (units.yaml) va sinh scope-and-sequence.md.
#   python check_seed.py            # chi kiem
#   python check_seed.py --write    # kiem + ghi scope-and-sequence.md
# Kiem: 8 chu de/cap, du truong, so tu Core khop Thong tu 50/2020 (khoang 35/70/100, +-3), so tu Plus, khong trung tu
# trong mot cap, co du so dem toi count_to, chu de can robot phai co phuong an thay the.
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
NUMS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
FIELDS = ["id", "theme", "theme_vi", "core", "plus", "patterns", "song", "make", "tell", "can_do"]
sys.stdout.reconfigure(encoding="utf-8")
data = yaml.safe_load((HERE / "units.yaml").read_text(encoding="utf-8"))
fails, prev_count = [], 0

for lv in data["levels"]:
    units = lv["units"]
    if len(units) != 8:
        fails.append(f"{lv['id']}: phai co 8 chu de, dang co {len(units)}")
    seen, core_n, plus_n = {}, 0, 0
    for i, u in enumerate(units, 1):
        for f in FIELDS:
            if not u.get(f):
                fails.append(f"{u.get('id', '?')}: thieu '{f}'")
        if u.get("id") != f"{lv['id']}-u{i}":
            fails.append(f"{u.get('id')}: id phai la {lv['id']}-u{i}")
        if u.get("make_needs") and not u.get("make_fallback"):
            fails.append(f"{u['id']}: can {u['make_needs']} thi phai co make_fallback")
        if len(u.get("patterns", [])) < 2 or len(u.get("can_do", [])) != 2:
            fails.append(f"{u['id']}: can >= 2 mau cau va dung 2 muc can_do")
        for w in list(u.get("core", [])) + list(u.get("plus", [])):
            if not isinstance(w, str):   # YAML doc yes/no/on/off thanh True/False neu khong dat trong ngoac kep
                fails.append(f"{u['id']}: tu {w!r} khong phai chuoi - dat trong ngoac kep")
            key = str(w).lower()
            if key in seen:
                fails.append(f"{u['id']}: tu '{w}' da co o {seen[key]}")
            seen[key] = u["id"]
        core_n += len(u.get("core", []))
        plus_n += len(u.get("plus", []))
    if abs(core_n - lv["core_target"]) > 3:
        fails.append(f"{lv['id']}: Core {core_n} tu, muc tieu khoang {lv['core_target']} (+-3)")
    if abs(plus_n - lv["plus_target"]) > 3:
        fails.append(f"{lv['id']}: Plus {plus_n} tu, muc tieu {lv['plus_target']} (+-3)")
    core_words = {str(w).lower() for u in units for w in u["core"]}
    for n in NUMS[prev_count:lv["count_to"]]:
        if n not in core_words:
            fails.append(f"{lv['id']}: thieu so '{n}' (dem toi {lv['count_to']})")
    prev_count = lv["count_to"]
    lv["_core_n"], lv["_plus_n"] = core_n, plus_n
    print(f"{lv['id']} ({lv['age']}): Core {core_n} tu / muc tieu {lv['core_target']}, Plus +{plus_n}, dem toi {lv['count_to']}")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)

if "--write" in sys.argv:
    out = ["# Seed – bảng nội dung 3 năm (sinh tự động từ `units.yaml`, không sửa tay)", "",
           "Chạy lại: `python check_seed.py --write`. Từ **Core** mọi bé đều học; từ *Plus* là phần mở rộng.", ""]
    for lv in data["levels"]:
        out += [f"## {lv['name']} · {lv['age']} · Core {lv['_core_n']} từ, Plus thêm {lv['_plus_n']} từ, đếm tới {lv['count_to']}", "",
                "| Chủ đề | Từ Core | Từ Plus | Mẫu câu | Bài hát / chant | Make & Tell | Bé làm được |",
                "|---|---|---|---|---|---|---|"]
        for i, u in enumerate(lv["units"], 1):
            make = u["make"] + (f" (cần `{u['make_needs']}`; thay thế: {u['make_fallback']})" if u.get("make_needs") else "")
            out.append(f"| {i}. **{u['theme']}** – {u['theme_vi']} | {', '.join(map(str, u['core']))} | {', '.join(map(str, u['plus']))} "
                       f"| {'<br>'.join(u['patterns'])} | {u['song']} | {make}<br>→ {u['tell']} | {'<br>'.join(u['can_do'])} |")
        out.append("")
    (HERE / "scope-and-sequence.md").write_text("\n".join(out), encoding="utf-8")
    print("da ghi scope-and-sequence.md")
print("PASS check_seed")
