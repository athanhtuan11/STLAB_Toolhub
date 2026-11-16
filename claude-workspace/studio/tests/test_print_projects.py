# Gate "In 3D gom theo du an" (Claude viet 2026-11-16, executor KHONG sua). Tuan: "In 3D, gom du an lai 1 muc thoi. ban dang
# lam 1 du an tung chi tiet rieng le. block-coding-car thi chi 1 muc. nhan vo thi se mo ra plates".
# Chay tu thu muc studio: .venv\Scripts\python.exe -X utf8 tests\test_print_projects.py   (dung ban in that trong maker/)
import os, re, sys
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
os.environ["STLAB_DRY_OPEN"] = "1"
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


from toolhub import create_app  # noqa: E402

app = create_app()
c = app.test_client()
B = "http://127.0.0.1:5050"

r = c.get("/api/prints", base_url=B)
pj = r.get_json() or {}
plates = pj.get("prints") or []
groups = pj.get("projects")
ok(r.status_code == 200 and isinstance(groups, list) and groups, "/api/prints tra them 'projects' (danh sach nhom)")
groups = groups or []

# 1. Moi (source, folder) = dung 1 nhom; khoa giu nguyen 'prints' (trang linh kien/du an van dung)
keys = [(g.get("source"), g.get("folder")) for g in groups]
ok(len(keys) == len(set(keys)), "moi du an chi 1 nhom (khong trung)")
ok(len(groups) == len({(p["source"], p["folder"]) for p in plates}), f"so nhom = so du an co ban in ({len(groups)})")
need = {"project", "title", "source", "folder", "plates", "plate_count", "minutes", "grams", "image_url", "mtime", "cad"}
ok(all(need <= set(g) for g in groups), "nhom co project, title, source, folder, plates, plate_count, minutes, grams, image_url, mtime, cad")
ok(sum(len(g.get("plates") or []) for g in groups) == len(plates), "tong ban trong cac nhom = so ban in")
ok(all(g.get("plate_count") == len(g.get("plates") or []) for g in groups), "plate_count = so ban")
ok([g["mtime"] for g in groups] == sorted((g["mtime"] for g in groups), reverse=True), "nhom moi nhat truoc")
ok(all(g["mtime"] == max(p["mtime"] for p in g["plates"]) for g in groups if g.get("plates")), "mtime nhom = ban moi nhat")

# 2. block-coding-car: 1 muc, 6 ban p1..p6 theo thu tu ten, tong gio/gam
bcc = [g for g in groups if g["project"] == "block-coding-car"]
ok(len(bcc) == 1, f"block-coding-car chi 1 muc ({len(bcc)})")
if bcc:
    g = bcc[0]
    names = [p["plate"] for p in g["plates"]]
    ok(names == sorted(names) and len(names) >= 6 and names[0].startswith("p1-"), f"ban xep theo ten p1.. ({names})")
    ms = [p["minutes"] for p in g["plates"] if p["minutes"] is not None]
    gs = [p["grams"] for p in g["plates"] if p["grams"] is not None]
    ok(g["minutes"] == sum(ms), f"minutes nhom = tong ({g['minutes']} vs {sum(ms)})")
    ok(gs and abs(g["grams"] - round(sum(gs), 1)) < 0.05, f"grams nhom = tong ({g['grams']} vs {round(sum(gs), 1)})")
    first_img = next((p["image_url"] for p in g["plates"] if p["image_url"]), None)
    ok(g["image_url"] == first_img and first_img, "anh nhom = anh ban dau tien co anh")
    ok(all(set(p) >= {"plate", "minutes", "grams", "image_url", "project"} for p in g["plates"]), "moi ban trong nhom du truong")

# 3. Trang chinh: the du an, nhan vao mo danh sach ban (JS)
home = c.get("/", base_url=B).get_data(as_text=True)
ok("/api/prints" in home and 'id="print-grid"' in home, "trang chinh van nap /api/prints vao #print-grid")
js = (STUDIO / "toolhub" / "static" / "prints.js").read_text(encoding="utf-8")
ok("data.projects" in js or ".projects" in js, "prints.js dung danh sach projects")
ok("location.hash" in js and "hashchange" in js, "prints.js: mo du an theo #hash, nut Back cua trinh duyet quay lai")
ok(re.search(r"Tất cả dự án", js) is not None, "co nut quay lai 'Tất cả dự án'")
ok(re.search(r"bàn in", js) is not None and "plate_count" in js, "the du an hien so ban in (plate_count)")
ok("printCard(" in js, "giu ham printCard cho tung ban khi mo du an")
ok(re.search(r"\)\s*\{\s*\}", re.sub(r"catch\s*\(\)\s*=>\s*\{\s*\}", "", js)) is None, "khong co ham rong")
css = (STUDIO / "toolhub" / "static" / "style.css").read_text(encoding="utf-8")
ok(".print-project" in css, "style.css co lop .print-project cho the du an")

print(("GATE FAIL (%d)" % len(fails)) if fails else "GATE PASS")
sys.exit(1 if fails else 0)
