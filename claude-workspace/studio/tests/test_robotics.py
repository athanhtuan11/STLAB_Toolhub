# Gate trang "Robotics" /robotics (Claude viet 2026-11-11, executor KHONG sua). Chay tu thu muc studio:
#   .venv\Scripts\python.exe tests\test_robotics.py
# Doc workspace that (chi doc). Manifest loi -> manifest tam qua STLAB_ROBOTICS_MANIFEST.
import json, os, re, sys, tempfile, time
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
WS = STUDIO.parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(STUDIO))

MANIFEST = json.loads((STUDIO / "toolhub" / "robotics.json").read_text(encoding="utf-8"))
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


from toolhub import create_app  # noqa: E402
from toolhub import robotics  # noqa: E402

c = create_app().test_client()
H = {"Host": "127.0.0.1:5050"}

# ---- 1. Du lieu: robotics.data() ----
t0 = time.time()
d = robotics.data()
check(time.time() - t0 < 3, "robotics.data() phai < 3 s")
check(set(d) >= {"projects", "simulations", "statuses"}, "data() phai co projects, simulations, statuses")
KEYS = {"rel", "slug", "name", "title", "summary", "audience", "status", "status_label", "next", "cover",
        "updated", "plates", "assembly_pdf", "bom", "todo", "detail_url"}
rows = {p["rel"]: p for p in d["projects"]}
check([p["rel"] for p in d["projects"]] == [p["rel"] for p in MANIFEST["projects"]],
      "projects giu dung thu tu manifest")
for p in d["projects"]:
    miss = KEYS - set(p)
    check(not miss, f"{p.get('rel')}: thieu khoa {sorted(miss)}")
    if miss:
        continue
    folder = WS / p["rel"]
    check(p["slug"] == p["rel"].replace("/", "--"), f"{p['rel']}: slug sai")
    check(p["name"] == p["rel"].split("/")[-1], f"{p['rel']}: name = ten thu muc")
    check(p["status_label"] == MANIFEST["statuses"][p["status"]], f"{p['rel']}: status_label sai")
    # so ban in = print/plates/<ban>/*.3mf (KHONG dem _orient/, _per-part/)
    want = len(list(folder.glob("print/plates/*/*.3mf"))) + len(list(folder.glob("solidcraft/print/plates/*/*.3mf")))
    check(p["plates"] == want, f"{p['rel']}: plates {p['plates']} != {want}")
    check(p["assembly_pdf"] == (folder / "ASSEMBLY.pdf").is_file(), f"{p['rel']}: assembly_pdf sai")
    check(p["bom"] == (folder / "BOM.md").is_file(), f"{p['rel']}: bom sai")
    has_claude = (folder / "CLAUDE.md").is_file()
    check(bool(p["detail_url"]) == has_claude, f"{p['rel']}: detail_url chi co khi co CLAUDE.md")
    if has_claude:
        check(p["detail_url"] == f"/projects/{p['slug']}", f"{p['rel']}: detail_url sai")
        txt = (folder / "CLAUDE.md").read_text(encoding="utf-8")
        check(p["todo"] == len(re.findall(r"\bTODO\b", txt)), f"{p['rel']}: todo dem sai")
    check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", p["updated"] or "") is not None, f"{p['rel']}: updated phai YYYY-MM-DD (git log)")
    if p["cover"]:
        check(p["cover"].startswith(f"/robotics/img/{p['slug']}/"), f"{p['rel']}: cover phai qua /robotics/img/<slug>/")

# anh bia tu dong theo thu tu uu tien
check(rows["maker/pushrod-arm"]["cover"].endswith("/freecad/images/assembly/cover.png"), "pushrod-arm: cover assembly")
check(rows["maker/sesame-quadruped"]["cover"].endswith("/print/plates/p1-body/preview.png"), "sesame: cover preview ban in")
check(rows["maker/line-bot"]["cover"].endswith("/design/concepts/concept-a-3-4.png"), "line-bot: cover concept 3-4")
check(rows["maker/uwb-drone-positioning"]["cover"] in ("", None), "uwb: khong co anh -> cover rong")
check(rows["maker/sesame-quadruped"]["detail_url"] in ("", None), "sesame khong CLAUDE.md -> khong detail")
check(rows["maker/pushrod-arm"]["assembly_pdf"] is True, "pushrod-arm co ASSEMBLY.pdf")

sims = {s["id"]: s for s in d["simulations"]}
check(set(sims) == {"gearsbot", "erebus"}, "simulations: gearsbot + erebus")
g = sims.get("gearsbot", {})
check(len(g.get("links", [])) == 3, "gearsbot: 3 link")
check(g.get("cover") == "/robotics/sim/gearsbot/cover", "gearsbot: cover qua /robotics/sim/<id>/cover")
check(g.get("readme_url") == "/robotics/sim/gearsbot/readme" and g.get("lesson_url") == "/robotics/sim/gearsbot/lesson",
      "gearsbot: readme_url/lesson_url")
check(sims.get("erebus", {}).get("lesson_url") in ("", None), "erebus: khong giao an -> lesson_url rong")
check(sims.get("erebus", {}).get("cover") in ("", None), "erebus: khong anh -> cover rong")

# ---- 2. Manifest sai -> bao loi ro ----
TMP = Path(tempfile.mkdtemp(prefix="robotics-test-"))
for bad, why in [
    ({**MANIFEST, "projects": [{**MANIFEST["projects"][0], "status": "bay-ba"}]}, "status la"),
    ({**MANIFEST, "projects": [{**MANIFEST["projects"][0], "rel": "maker/khong-co"}]}, "thu muc khong ton tai"),
    ({**MANIFEST, "projects": [{**MANIFEST["projects"][0], "rel": "../outside"}]}, "rel ngoai maker/"),
]:
    f = TMP / "bad.json"
    f.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    os.environ["STLAB_ROBOTICS_MANIFEST"] = str(f)
    try:
        robotics.data()
        check(False, f"manifest {why}: phai raise ValueError")
    except ValueError:
        pass
os.environ.pop("STLAB_ROBOTICS_MANIFEST")

# ---- 3. Trang ----
r = c.get("/robotics", headers=H)
check(r.status_code == 200, f"/robotics -> {r.status_code}")
html = r.get_data(as_text=True)
nav = html[html.find("<nav"):html.find("</nav>")]
check('href="/robotics"' in nav and "Robotics" in nav, "menu chinh phai co Robotics -> /robotics")
check("/ops" not in nav and "Điều hành" not in nav, "menu khong con Dieu hanh /ops")
check('class="on"' in nav[:nav.find('href="/robotics"') + 40] or 'href="/robotics" class="on"' in nav,
      "muc Robotics phai sang (on) khi dang o /robotics")
for p in MANIFEST["projects"]:
    name = p["rel"].split("/")[-1]
    check(name in html, f"trang thieu du an {name}")
    check(p["summary"] in html, f"trang thieu mo ta {name}")
    check(p["next"] in html, f"trang thieu buoc tiep {name}")
for label in {MANIFEST["statuses"][p["status"]] for p in MANIFEST["projects"]}:
    check(label in html, f"trang thieu nhan trang thai {label}")
check(html.count("data-robot=") == len(MANIFEST["projects"]), "moi du an 1 the data-robot")
check(html.count("data-sim=") == 2, "2 the mo phong data-sim")
for s in MANIFEST["simulations"]:
    for ln in s["links"]:
        url = ln["url"].replace("&", "&amp;")
        check(url in html, f"thieu link mo phong {ln['label']}")
for a in re.findall(r'<a [^>]*href="https?://[^"]+"[^>]*>', html):
    check('target="_blank"' in a and "noopener" in a, f"link ngoai thieu target/_blank noopener: {a[:80]}")
check("/robotics/sim/gearsbot/readme" in html and "/robotics/sim/gearsbot/lesson" in html, "thieu link README/giao an gearsbot")
check(html.count('loading="lazy"') >= 5, "anh bia phai loading=lazy")
check("/projects/maker--line-bot" in html, "the line-bot phai link chi tiet")
check("/robotics/file/maker--pushrod-arm/ASSEMBLY.pdf" in html, "pushrod-arm phai co link ASSEMBLY.pdf")
check(c.get("/ops", headers=H).status_code == 404, "/ops phai 404 (da go)")
check(c.get("/api/ops", headers=H).status_code == 404, "/api/ops phai 404 (da go)")
check(c.get("/robotics", headers={"Host": "evil.com"}).status_code == 403, "Host la -> 403")

# ---- 4. Anh / file / tai lieu: chi trong thu muc du an, dung loai ----
lb = rows["maker/line-bot"]
r = c.get(lb["cover"], headers=H)
check(r.status_code == 200 and r.mimetype == "image/png", f"anh bia line-bot -> {r.status_code} {r.mimetype}")
for bad in ["/robotics/img/maker--line-bot/CLAUDE.md",
            "/robotics/img/maker--line-bot/..%2F..%2Fstudio%2Fdesign%2Fx.png",
            "/robotics/img/maker--line-bot/../pushrod-arm/freecad/images/assembly/cover.png",
            "/robotics/img/maker--khong-co/a.png",
            "/robotics/img/maker--smart-home/x.png",
            "/robotics/file/maker--pushrod-arm/CLAUDE.md",
            "/robotics/file/maker--line-bot/ASSEMBLY.pdf",
            "/robotics/sim/khong-co/readme",
            "/robotics/sim/erebus/lesson",
            "/robotics/sim/erebus/cover"]:
    check(c.get(bad, headers=H).status_code == 404, f"{bad} phai 404")
r = c.get("/robotics/file/maker--pushrod-arm/ASSEMBLY.pdf", headers=H)
check(r.status_code == 200 and r.mimetype == "application/pdf", "ASSEMBLY.pdf pushrod-arm -> 200 pdf")
r = c.get("/robotics/sim/gearsbot/cover", headers=H)
check(r.status_code == 200 and r.mimetype == "image/png", "anh gearsbot -> 200 png")
r = c.get("/robotics/sim/gearsbot/readme", headers=H)
t = r.get_data(as_text=True)
check(r.status_code == 200 and "<h1" in t and "GearsBot" in t and 'href="/robotics"' in t,
      "README gearsbot render markdown (mdrender) trong khung Toolhub, co link ve /robotics")
r = c.get("/robotics/sim/gearsbot/lesson", headers=H)
check(r.status_code == 200 and "<h1" in r.get_data(as_text=True), "giao an gearsbot render")

# ---- 5. Khong ma gia ----
src = (STUDIO / "toolhub" / "robotics.py").read_text(encoding="utf-8")
check("pass\n" not in src and "NotImplemented" not in src and "..." not in src.replace('"..."', ""), "robotics.py khong ma gia")
css = (STUDIO / "toolhub" / "static" / "style.css").read_text(encoding="utf-8")
check(re.search(r"\.robot[-\w]*\s*\{[^}]*#[0-9a-fA-F]{3,6}", css) is None, "style.css: khong dat hex (dung token)")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_robotics")
