# Gate "Vong doi mau in + trang Bao cao + bao loi ro" (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv\Scripts\python.exe tests\test_products_reports.py
import json, os, re, sys, tempfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="stlab-products-"))
STORE = TMP / "products.json"
os.environ["STLAB_PRODUCTS_FILE"] = str(STORE)  # khong dung file that
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
from toolhub import create_app  # noqa: E402
from toolhub import workspace as ws  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


H = {"Host": "127.0.0.1:5050"}
P = {**H, "X-Studio": "1"}
c = create_app().test_client()
STAGES = ["thiet-ke", "in-thu", "da-duyet", "da-dang", "dang-ban"]
LABELS = ["Thiết kế", "In thử", "Đã duyệt", "Đã đăng", "Đang bán"]
slug = ws.projects()[0]["slug"]

# ---- 1. Vong doi mau in ----
from toolhub import products  # noqa: E402
check(list(products.STAGES) == STAGES, f"products.STAGES phai = {STAGES}")
check(Path(products.store_path()) == STORE, "products.store_path() phai theo bien STLAB_PRODUCTS_FILE")

r = c.get(f"/projects/{slug}", headers=H)
html = r.get_data(as_text=True)
check(r.status_code == 200, f"/projects/{slug} status {r.status_code}")
for st, lb in zip(STAGES, LABELS):
    check(lb in html, f"trang chi tiet thieu buoc '{lb}'")
    check(f'data-post="/api/products/{slug}/stage/{st}"' in html, f"thieu nut chuyen sang {st}")
check(re.search(r'data-post="/api/products/[^"]+"[^>]*data-confirm="[^"]+"', html)
      or re.search(r'data-confirm="[^"]+"[^>]*data-post="/api/products/', html),
      "nut chuyen trang thai phai co data-confirm (hoi truoc khi ghi)")
check('href="/quote"' in html, "trang chi tiet phai co link toi /quote")

r = c.post(f"/api/products/{slug}/stage/in-thu", headers=H)
check(r.status_code == 403, "POST thieu X-Studio phai bi chan 403")
r = c.post(f"/api/products/{slug}/stage/khong-co", headers=P)
check(r.status_code == 400, f"stage sai phai 400, nhan {r.status_code}")
r = c.post("/api/products/khong--ton-tai/stage/in-thu", headers=P)
check(r.status_code == 404, f"slug sai phai 404, nhan {r.status_code}")
check(not STORE.exists(), "request loi KHONG duoc ghi file")

r = c.post(f"/api/products/{slug}/stage/in-thu", headers=P)
d = r.get_json() or {}
check(r.status_code == 200 and d.get("ok") is True and d.get("msg"), "POST hop le phai 200 {ok:true, msg}")
data = json.loads(STORE.read_text(encoding="utf-8")) if STORE.exists() else {}
e = data.get(slug, {})
check(e.get("stage") == "in-thu", "file luu stage in-thu")
check(re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", str(e.get("updated", ""))), "co truong updated (ngay ISO)")
check(len(e.get("history", [])) == 1 and e["history"][0].get("stage") == "in-thu", "history ghi 1 muc")
c.post(f"/api/products/{slug}/stage/da-duyet", headers=P)
data = json.loads(STORE.read_text(encoding="utf-8"))
check(data[slug]["stage"] == "da-duyet" and len(data[slug]["history"]) == 2, "chuyen tiep: history 2 muc")

r = c.get("/projects", headers=H)
html = r.get_data(as_text=True)
check("Mẫu in" in html, "/projects phai co khu 'Mẫu in'")
check("Đã duyệt" in html, "/projects phai hien nhan trang thai du an da theo doi")
r = c.get(f"/projects/{slug}", headers=H)
check(re.search(r'class="[^"]*\bcurrent\b[^"]*"[^>]*>[^<]*Đã duyệt', r.get_data(as_text=True)) is not None,
      "buoc hien tai co class 'current'")

app_js = (STUDIO / "toolhub" / "static" / "app.js").read_text(encoding="utf-8")
check("dataset.confirm" in app_js and "confirm(" in app_js, "app.js phai hoi confirm() khi nut co data-confirm")

# ---- 2. Trang Bao cao (docs/reports) ----
REP = STUDIO.parent / "docs" / "reports"
names = sorted(p.name for p in REP.glob("*.md") if not p.name.endswith(".spec.md"))
r = c.get("/reports", headers=H)
html = r.get_data(as_text=True)
check(r.status_code == 200, f"/reports status {r.status_code}")
for n in names:
    check(f'href="/reports/{n}"' in html, f"/reports thieu link {n}")
check(".spec.md" not in html, "/reports KHONG liet ke file .spec.md")
check('href="/reports"' not in c.get("/", headers=H).get_data(as_text=True), "2026-11-12 Tuan: bo Bao cao nghien cuu khoi menu")

r = c.get("/reports/print-products-market-research.md", headers=H)
html = r.get_data(as_text=True)
check(r.status_code == 200, "mo duoc bao cao print-products-market-research.md")
check("<table" in html and "<h2" in html, "bao cao phai render Markdown (h2, table), khong chi <pre>")
check('href="https://' in html, "link Markdown phai thanh <a href>")
for bad in ["../CLAUDE.md", "..%2FCLAUDE.md", "x.spec.md", "khong-co.md", "CLAUDE.md"]:
    check(c.get(f"/reports/{bad}", headers=H).status_code == 404, f"/reports/{bad} phai 404")

from toolhub import mdrender  # noqa: E402
out = mdrender.render("# T\n\n<script>alert(1)</script>\n\n[x](javascript:alert(1))\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
check("<script>" not in out, "mdrender phai escape HTML")
check("javascript:" not in out, "mdrender khong tao link javascript:")
check("<h1" in out and "<td>1</td>" in out, "mdrender: heading + bang")

# ---- 3. Bao loi ro (khong nuot loi) ----
res_js = (STUDIO / "toolhub" / "static" / "research.js").read_text(encoding="utf-8")
scan = res_js[res_js.find("#research-scan"):]
check(".ok" in scan, "nut quet research phai kiem response.ok")
check("Không" in scan, "nut quet research phai bao loi tieng Viet khi that bai")

if fails:
    print("FAIL", len(fails))
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_products_reports")
