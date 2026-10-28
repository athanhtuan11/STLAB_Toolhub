# Gate "Bao gia in 3D" (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv/Scripts/python.exe tests/test_quote.py
# DB test nam trong thu muc tam (bien STLAB_QUOTES_DB), khong dung DB that cua Tuan.
import io, os, re, sys, tempfile, zipfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
TMP = Path(tempfile.mkdtemp(prefix="stlab-quote-test-"))
os.environ["STLAB_QUOTES_DB"] = str(TMP / "quotes.db")
from toolhub import create_app, quote  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


SLICE = """<?xml version="1.0" encoding="UTF-8"?>
<config>
  <plate>
    <metadata key="index" value="1"/>
    <metadata key="prediction" value="3600"/>
    <metadata key="weight" value="100.00"/>
    <filament id="1" type="PETG" color="#00AE42" used_m="33.1" used_g="100.00"/>
  </plate>
  <plate>
    <metadata key="index" value="2"/>
    <metadata key="prediction" value="1800"/>
    <metadata key="weight" value="30.00"/>
    <filament id="1" type="PETG" color="#00AE42" used_m="6.6" used_g="20.00"/>
    <filament id="2" type="TPU" color="#000000" used_m="3.0" used_g="10.00"/>
  </plate>
</config>"""
PNG = b"\x89PNG\r\n\x1a\nfake"


def fake_3mf():
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("Metadata/slice_info.config", SLICE)
        z.writestr("Metadata/plate_1.png", PNG)
        z.writestr("Metadata/plate_2.png", PNG)
    return b.getvalue()


# 1. Doc 3MF
p = quote.read_3mf(io.BytesIO(fake_3mf()))
check(len(p["plates"]) == 2, f"2 ban in, co {len(p['plates'])}")
check(p["plates"][0]["seconds"] == 3600 and p["plates"][1]["seconds"] == 1800, "seconds lay tu metadata prediction")
check(p["plates"][1]["grams"] == {"PETG": 20.0, "TPU": 10.0}, f"grams theo type: {p['plates'][1]['grams']}")
check(p["plates"][0]["image_png"] == PNG, "anh Metadata/plate_N.png")
check(abs(p["hours"] - 1.5) < 1e-9, "tong gio = 1.5")
check(p["grams"] == {"PETG": 120.0, "TPU": 10.0}, f"tong gam theo nhua: {p['grams']}")
try:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("3D/3dmodel.model", "x")
    quote.read_3mf(io.BytesIO(b.getvalue()))
    check(False, "3MF chua cat lop (khong co slice_info) phai raise QuoteError")
except quote.QuoteError as e:
    check("cắt lớp" in str(e), "loi phai nhac 'cắt lớp' (xuat .gcode.3mf tu Bambu Studio)")

REAL = STUDIO.parent / "maker/pushrod-arm/print/plates/P2_Turret_Turntable__0.20_PETG/P2_Turret_Turntable__0.20_PETG.3mf"
if REAL.exists():
    r = quote.read_3mf(REAL)
    check(r["plates"][0]["seconds"] == 10516, "file that P2: 10516 s")
    check(abs(r["grams"]["PETG"] - 76.13) < 0.01, "file that P2: 76.13 g PETG")

# 2. DB + bang gia
SETTINGS = {
    "electricity_price_vnd_per_kwh": 3000, "printer_power_w": 100,
    "machine_price_vnd": 10_000_000, "machine_lifetime_hours": 5000,
    "labor_rate_vnd_per_hour": 50_000, "setup_hours_per_job": 0.5, "post_hours_per_plate": 0.25,
    "failure_pct": 0.1, "pricing_method": "markup", "pricing_value": 1.0, "round_to_vnd": 1000, "valid_days": 7,
}
conn = quote.connect()
check(Path(os.environ["STLAB_QUOTES_DB"]).exists(), "connect() tao DB tai STLAB_QUOTES_DB")
pr = quote.get_pricing(conn)
# Tuan 2026-10-28: thoi gia tu dien tu toolhub/quote_defaults.json, van sua duoc
import json  # noqa: E402
DEF = json.loads((STUDIO / "toolhub" / "quote_defaults.json").read_text(encoding="utf-8"))
for k, d in DEF["settings"].items():
    check(pr["settings"].get(k) == d["value"], f"DB moi lay mac dinh {k}={d['value']}, co {pr['settings'].get(k)}")
    check(bool(d.get("source")), f"mac dinh {k} phai co source")
for m, d in DEF["materials"].items():
    got = pr["materials"].get(m) or {}
    check(got.get("spool_price_vnd") == d["spool_price_vnd"] and got.get("spool_weight_g") == d["spool_weight_g"],
          f"DB moi co nhua mac dinh {m}")
check(any(x["label"] == DEF["extras"][0]["label"] for x in pr["extras"]), "DB moi co phu kien mac dinh")
check(quote.pricing_sources()["printer_power_w"]["source"] == DEF["settings"]["printer_power_w"]["source"],
      "pricing_sources() tra nguon tung khoa (de hien tren trang)")
c0 = quote.compute(p, pr, quantity=1, materials_map={"TPU": "PETG"})
check(c0["total"] > 0, "file + chon nhua la ra gia ngay, khong can nhap gi them")
try:
    quote.compute(p, pr, quantity=1)
    check(False, "nhua TPU chua co gia va khong doi nhua -> QuoteError")
except quote.QuoteError as e:
    check("TPU" in str(e), f"loi phai neu ten nhua thieu: {e}")
quote.save_settings(conn, {"printer_power_w": None})
try:
    quote.compute(p, quote.get_pricing(conn), quantity=1, materials_map={"TPU": "PETG"})
    check(False, "khoa bi xoa (None) -> QuoteError")
except quote.QuoteError as e:
    check("printer_power_w" in str(e), f"loi phai liet ke khoa thieu: {e}")
quote.reset_defaults(conn)
check(quote.get_pricing(conn)["settings"]["printer_power_w"] == DEF["settings"]["printer_power_w"]["value"],
      "reset_defaults() dua thoi gia ve mac dinh")
conn.close()
conn = quote.connect()
check(quote.get_pricing(conn)["settings"]["printer_power_w"] == DEF["settings"]["printer_power_w"]["value"],
      "connect() lan 2 khong ghi de / khong nhan doi")
check(len([x for x in quote.get_pricing(conn)["extras"] if x["label"] == DEF["extras"][0]["label"]]) == 1,
      "phu kien mac dinh khong bi them lai moi lan connect/reset")

quote.save_settings(conn, SETTINGS)
quote.save_material(conn, "PETG", spool_price_vnd=300_000, spool_weight_g=1000)
quote.save_material(conn, "TPU", spool_price_vnd=500_000, spool_weight_g=1000)
eid = quote.save_extra(conn, label="Insert ren M3", price_vnd=1000)
pr = quote.get_pricing(conn)
check({k: pr["materials"]["PETG"].get(k) for k in ("spool_price_vnd", "spool_weight_g")}
      == {"spool_price_vnd": 300000, "spool_weight_g": 1000}, f"material: {pr['materials']}")
check(any(x["id"] == eid and x["label"] == "Insert ren M3" for x in pr["extras"]), "extra luu duoc")
conn.close()
conn = quote.connect()  # mo lai: du lieu con
check(quote.get_pricing(conn)["settings"]["printer_power_w"] == 100, "settings ton tai sau khi mo lai DB")

# 3. Tinh gia (so tinh tay trong spec-quote.md)
pr = quote.get_pricing(conn)
c = quote.compute(p, pr, quantity=2, extras={eid: 4}, other_fee_vnd=20_000)
exp = {"filament": 82000, "electricity": 900, "depreciation": 6000, "labor": 75000, "extras": 8000, "failure": 8890}
for k, v in exp.items():
    check(abs(c["lines"][k] - v) < 0.01, f"{k}: {c['lines'][k]} != {v}")
check(abs(c["cost"] - 180790) < 0.01, f"cost {c['cost']} != 180790")
check(abs(c["price"] - 361580) < 0.01, f"price markup {c['price']} != 361580")
# v4 (2026-10-28): duoi bac si, don gia = gia le 1 cai (khong chia cong chuan bi theo SL) – xem test_quote_bulk.py
c1 = quote.compute(p, pr, quantity=1, extras={eid: 4}, other_fee_vnd=20_000)
check(c1["unit_price"] % 1000 == 0 and c1["unit_price"] >= c1["price"], f"unit_price lam tron LEN 1000: {c1['unit_price']}")
check(c["unit_price"] == c1["unit_price"], f"SL 2 giu gia le: {c['unit_price']} vs {c1['unit_price']}")
check(c["subtotal"] == 2 * c1["unit_price"] and c["total"] == c["subtotal"] + 20_000, f"subtotal/total {c['subtotal']}/{c['total']}")
EXP_TOTAL = c["total"]
quote.save_settings(conn, {"pricing_method": "margin", "pricing_value": 0.5})
c2 = quote.compute(p, quote.get_pricing(conn), quantity=2, extras={eid: 4}, other_fee_vnd=20_000)
check(abs(c2["price"] - 361580) < 0.01, "margin 0.5 = markup 1.0")
quote.save_settings(conn, {"pricing_method": "margin", "pricing_value": 1.0})
try:
    quote.compute(p, quote.get_pricing(conn), quantity=1)
    check(False, "margin >= 1 phai raise QuoteError")
except quote.QuoteError:
    pass
quote.save_settings(conn, {"pricing_method": "markup", "pricing_value": 1.0})
quote.save_material(conn, "PLA", spool_price_vnd=250_000, spool_weight_g=1000)
c3 = quote.compute(p, quote.get_pricing(conn), quantity=1, materials_map={"PETG": "PLA", "TPU": "PLA"})
check(abs(c3["lines"]["filament"] - 130 * 250) < 0.01, f"doi nhua: 130 g x 250 d/g, co {c3['lines']['filament']}")
check(c3.get("materials") == {"PLA": 130.0}, f"calc ghi nhua da chon + gam: {c3.get('materials')}")
try:
    quote.compute(p, quote.get_pricing(conn), quantity=1, materials_map={"PETG": "ABS"})
    check(False, "doi sang nhua khong co trong bang gia -> QuoteError")
except quote.QuoteError as e:
    check("ABS" in str(e), "loi neu ten nhua khong co")
check(quote.fmt_vnd(1234000) == "1.234.000 đ" and quote.fmt_vnd(0) == "0 đ", "fmt_vnd kieu Viet Nam")

# 4. Luu bao gia
qid = quote.save_quote(conn, customer_name="Khách Thử", customer_phone="0900000000",
                       title="Tay máy – bàn P2", parsed=p, calc=c, note="")
q = quote.get_quote(conn, qid)
check(q["number"].startswith("BG-") and q["total_vnd"] == EXP_TOTAL, f"bao gia luu: {q.get('number')} {q.get('total_vnd')}")
check(any(x["id"] == qid for x in quote.list_quotes(conn)), "list_quotes co bao gia vua luu")
qid2 = quote.save_quote(conn, customer_name="B", customer_phone="", title="x", parsed=p, calc=c, note="")
check(quote.get_quote(conn, qid2)["number"] != q["number"], "so bao gia khong trung")
conn.close()

# 5. Trang + API
_c = quote.connect()
EXP_API = quote.compute(p, quote.get_pricing(_c), quantity=2, extras={eid: 4}, other_fee_vnd=20_000)["total"]
_c.close()
EXP_API_TEXT = quote.fmt_vnd(EXP_API)
H = {"Host": "127.0.0.1:5050"}
HP = {**H, "X-Studio": "1"}
cl = create_app().test_client()
r = cl.get("/quote", headers=H)
html = r.get_data(as_text=True)
check(r.status_code == 200, f"/quote {r.status_code}")
for need in ('id="file"', 'id="quantity"', 'id="pricing-form"', "Giá vốn", "Lịch sử báo giá"):
    check(need in html, f"/quote thieu {need}")
check("Zalo" not in html, "Tuan: khong can nut Zalo")
check('id="material-map"' in html, "chon nhua cho tung loai trong file (id=material-map)")
check(re.search(r'<details[^>]*id="pricing-panel"', html) is not None, "bang gia gap trong <details id=pricing-panel>")
check('id="pricing-reset"' in html, "nut khoi phuc thoi gia mac dinh")
check(DEF["settings"]["printer_power_w"]["source"][:30] in html, "hien nguon thoi gia canh o nhap")
check('href="/quote"' in cl.get("/", headers=H).get_data(as_text=True), "menu co link /quote")

check(cl.post("/api/quote/pricing", json={"settings": {"printer_power_w": 120}}, headers=H).status_code == 403,
      "POST khong X-Studio -> 403")
r = cl.post("/api/quote/pricing", json={"settings": {"printer_power_w": 120},
                                        "materials": {"PLA": {"spool_price_vnd": 250000, "spool_weight_g": 1000}}},
            headers=HP)
check(r.status_code == 200 and r.get_json()["settings"]["printer_power_w"] == 120, "luu bang gia qua API")
check("PLA" in cl.get("/api/quote/pricing", headers=H).get_json()["materials"], "GET pricing co PLA")

r = cl.post("/api/quote/parse", data={"file": (io.BytesIO(fake_3mf()), "x.gcode.3mf")},
            headers=HP, content_type="multipart/form-data")
j = r.get_json() or {}
check(r.status_code == 200 and len(j.get("plates", [])) == 2, f"parse upload: {r.status_code}")
check(j.get("token"), "parse tra token de tinh/luu tiep")
check(str(j.get("plates", [{}])[0].get("image", "")).startswith("data:image/png;base64,"), "anh ban in dang data URL")
r = cl.post("/api/quote/parse", data={"file": (io.BytesIO(b"not zip"), "x.3mf")},
            headers=HP, content_type="multipart/form-data")
check(r.status_code == 400 and "error" in (r.get_json() or {}), "file hong -> 400 + error")

r = cl.post("/api/quote/calc", json={"token": j.get("token"), "quantity": 2, "extras": {str(eid): 4},
                                     "other_fee_vnd": 20000}, headers=HP)
k = r.get_json() or {}
check(r.status_code == 200 and k.get("total") == EXP_API and k.get("total_text") == EXP_API_TEXT, f"calc API: {k}")
r = cl.post("/api/quote/calc", json={"token": j.get("token"), "quantity": 1,
                                     "materials_map": {"PETG": "PLA", "TPU": "PLA"}}, headers=HP)
check(r.status_code == 200 and (r.get_json() or {}).get("materials") == {"PLA": 130.0},
      "calc API nhan materials_map (chi can file + chon nhua)")
r = cl.post("/api/quote/save", json={"token": j.get("token"), "quantity": 2, "extras": {str(eid): 4},
                                     "other_fee_vnd": 20000, "customer_name": "Khách Thử",
                                     "customer_phone": "0900000000", "title": "Tay máy", "note": ""}, headers=HP)
sid = (r.get_json() or {}).get("id")
check(r.status_code == 200 and sid, "save API tra id")
r = cl.get(f"/quote/{sid}", headers=H)
t = r.get_data(as_text=True)
check(r.status_code == 200 and "BÁO GIÁ IN 3D" in t and "Khách Thử" in t and EXP_API_TEXT in t,
      "ban bao gia cho khach: tieu de, ten khach, tong tien")
check("Giá vốn" not in t and "Khấu hao" not in t, "ban cho khach KHONG lo gia von")
check(cl.get("/quote/999999", headers=H).status_code == 404, "bao gia khong co -> 404")

r = cl.post("/api/quote/pricing/reset", json={}, headers=HP)
PW = DEF["settings"]["printer_power_w"]["value"]
check(r.status_code == 200 and r.get_json()["settings"]["printer_power_w"] == PW,
      "POST /api/quote/pricing/reset -> thoi gia mac dinh")
check("sources" in cl.get("/api/quote/pricing", headers=H).get_json(), "GET pricing kem sources")

plates = quote.project_3mf_files()
check(all(f.suffix == ".3mf" and "maker" in f.parts for f in plates), "project_3mf_files chi .3mf trong maker/")
r = cl.post("/api/quote/parse", json={"path": "../../Windows/win.ini"}, headers=HP)
check(r.status_code in (400, 404), "parse theo path chi nhan file trong danh sach du an")
if REAL.exists():
    rel = REAL.relative_to(STUDIO.parent).as_posix()
    r = cl.post("/api/quote/parse", json={"path": rel}, headers=HP)
    check(r.status_code == 200, f"parse file du an {rel}: {r.status_code}")

if os.environ.get("QUOTE_PDF") == "1":  # Edge headless ~ vai giay; Claude chay rieng
    r = cl.get(f"/quote/{sid}/pdf", headers=H)
    check(r.status_code == 200 and r.data[:4] == b"%PDF", "xuat PDF")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_quote")
