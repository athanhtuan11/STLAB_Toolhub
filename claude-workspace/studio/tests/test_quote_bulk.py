# Gate "Bao gia v4 – gia si theo so luong" (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv/Scripts/python.exe tests/test_quote_bulk.py
# DB test nam trong thu muc tam (bien STLAB_QUOTES_DB), khong dung DB that cua Tuan.
import json, math, os, re, sys, tempfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
TMP = Path(tempfile.mkdtemp(prefix="stlab-quote-bulk-"))
os.environ["STLAB_QUOTES_DB"] = str(TMP / "quotes.db")
os.environ["STLAB_QUOTES_WORK"] = str(TMP / "work")
from toolhub import create_app, quote  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


DEF = json.loads((STUDIO / "toolhub" / "quote_defaults.json").read_text(encoding="utf-8"))
BULK = ("bulk1_min_qty", "bulk1_discount_pct", "bulk2_min_qty", "bulk2_discount_pct")
for k in BULK:
    check(k in DEF["settings"], f"quote_defaults.json phai co {k}")

conn = quote.connect()
pr = quote.get_pricing(conn)
for k in BULK:
    check(pr["settings"].get(k) == DEF["settings"][k]["value"], f"DB moi lay mac dinh {k}")
    check(k in quote.pricing_sources(), f"pricing_sources co nguon cho {k}")

# Vit le 80 g / 230 phut, 1 ban
parsed = {"grams": {"PETG": 80.0}, "hours": 230 / 60, "plates": [{"index": 1, "seconds": 13800,
                                                                  "grams": {"PETG": 80.0}}]}
s = pr["settings"]
step = s["round_to_vnd"]


def ref_unit(q, disc):
    """Hoc doi thu: don gia = gia LE 1 cai (cong thuc cu, SL 1) × (1 − giam si); khong thap hon gia von/cai
    cua SL q. Duoi bac 1 giu gia le, khong giam them do chia cong chuan bi."""
    nob = {**pr, "settings": {**s, "bulk1_discount_pct": 0, "bulk2_discount_pct": 0}}
    one = quote.compute(parsed, nob, quantity=1)
    cq = quote.compute(parsed, nob, quantity=q)
    raw = max(one["price"] * (1 - disc), cq["cost"] / q)
    return math.ceil(raw / step - 1e-9) * step


c1 = quote.compute(parsed, pr, quantity=1)
check(c1.get("bulk_discount_pct") == 0, f"SL 1 khong giam si: {c1.get('bulk_discount_pct')}")
check(c1["unit_price"] == ref_unit(1, 0), f"SL 1 giu nguyen gia cu: {c1['unit_price']} vs {ref_unit(1, 0)}")

c49 = quote.compute(parsed, pr, quantity=49)
check(c49.get("bulk_discount_pct") == 0, "SL 49 chua toi bac 1")
check(c49["unit_price"] == c1["unit_price"], f"SL 49 giu gia le: {c49['unit_price']} vs {c1['unit_price']}")
c50_ = quote.compute(parsed, pr, quantity=50)
check(abs(c50_["unit_price"] / c1["unit_price"] - (1 - s["bulk1_discount_pct"])) < 0.05,
      f"SL 50 ≈ gia le × (1 − giam bac 1): {c50_['unit_price']} / {c1['unit_price']}")
c50 = quote.compute(parsed, pr, quantity=50)
d1, d2 = s["bulk1_discount_pct"], s["bulk2_discount_pct"]
check(c50.get("bulk_discount_pct") == d1, f"SL 50 giam bac 1 ({d1}): {c50.get('bulk_discount_pct')}")
check(c50["unit_price"] == ref_unit(50, d1), f"SL 50 don gia {c50['unit_price']} vs {ref_unit(50, d1)}")
check(c50["subtotal"] == c50["unit_price"] * 50, "thanh tien = don gia × SL")
check(c50["unit_price"] < c1["unit_price"], "mua 50 cai phai re hon 1 cai")
c100 = quote.compute(parsed, pr, quantity=100)
check(c100.get("bulk_discount_pct") == d2, f"SL 100 giam bac 2 ({d2})")
check(c100["unit_price"] == ref_unit(100, d2), f"SL 100 don gia {c100['unit_price']} vs {ref_unit(100, d2)}")
c500 = quote.compute(parsed, pr, quantity=500)
check(c500.get("bulk_discount_pct") == d2, "SL 500 van bac 2 (bac cao nhat)")
check(c1.get("unit_price_list") == c1["unit_price"], "unit_price_list = don gia le (SL 1)")
check(c50.get("unit_price_list") == ref_unit(50, 0), "unit_price_list = don gia truoc giam si")

# goi y bac tiep theo
nb = c1.get("next_bulk") or {}
check(nb.get("min_qty") == s["bulk1_min_qty"] and nb.get("discount_pct") == d1, f"SL 1 goi y bac 1: {nb}")
check(nb.get("unit_price") == c50["unit_price"], f"goi y bac 1 dung don gia SL 50: {nb}")
nb50 = c50.get("next_bulk") or {}
check(nb50.get("min_qty") == s["bulk2_min_qty"] and nb50.get("unit_price") == c100["unit_price"],
      f"SL 50 goi y bac 2: {nb50}")
check(c100.get("next_bulk") is None, "SL 100 khong con bac tiep")

# san gia: giam si khong duoc ban duoi gia von
cheap = {**pr, "settings": {**s, "pricing_value": 0.05, "bulk2_discount_pct": 0.5}}
cc = quote.compute(parsed, cheap, quantity=100)
check(cc["unit_price"] * 100 >= cc["cost"], f"giam si khong duoc duoi gia von: {cc['unit_price']}×100 < {cc['cost']}")
check(cc.get("bulk_floor") is True, "cham san gia von -> bulk_floor True")
check(c50.get("bulk_floor") is False, "SL 50 binh thuong -> bulk_floor False")

# pricing cu khong co khoa bulk (DB cu / test cu) -> khong loi, khong giam
old = {**pr, "settings": {k: v for k, v in s.items() if k not in BULK}}
co = quote.compute(parsed, old, quantity=100)
check(co.get("bulk_discount_pct") == 0 and co.get("next_bulk") is None, "thieu khoa bulk -> khong giam, khong loi")

# luu bang gia: 4 khoa bulk luu duoc
quote.save_settings(conn, {"bulk1_min_qty": 20, "bulk1_discount_pct": 0.05})
s2 = quote.get_pricing(conn)["settings"]
check(s2.get("bulk1_min_qty") == 20 and s2.get("bulk1_discount_pct") == 0.05, "save_settings luu khoa bulk")
c20 = quote.compute(parsed, quote.get_pricing(conn), quantity=20)
check(c20.get("bulk_discount_pct") == 0.05, "bac 1 doi thanh 20 cai / 5 % co hieu luc")
quote.reset_defaults(conn)
conn.close()

# trang + API
app = create_app()
cl = app.test_client()
H = {"Host": "127.0.0.1:5050"}
html = cl.get("/quote", headers=H).get_data(as_text=True)
for k in BULK:
    check(k in html, f"trang /quote co o nhap {k} trong bang gia")
check(re.search(r'id="bulk-line"', html), 'trang co dong giam gia si id="bulk-line"')
check(re.search(r'id="bulk-hint"', html), 'trang co goi y bac tiep theo id="bulk-hint"')
r = cl.get("/api/quote/pricing", headers=H)
if r.status_code == 200:
    js = r.get_json() or {}
    check(all(k in (js.get("settings") or {}) for k in BULK), "API bang gia tra 4 khoa bulk")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_quote_bulk")
