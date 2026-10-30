# Gate "Bao gia v5 – nho phu kien theo mau" (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv/Scripts/python.exe tests/test_quote_model_extras.py
# Tuan 2026-10-30: phu kien chon + so luong bang tay theo tung san pham; tab nho lai theo TEN FILE,
# lan sau tha cung mau thi tu dien san. DB test o thu muc tam (STLAB_QUOTES_DB).
import io, os, sys, tempfile, zipfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
TMP = Path(tempfile.mkdtemp(prefix="stlab-quote-mx-"))
os.environ["STLAB_QUOTES_DB"] = str(TMP / "quotes.db")
os.environ["STLAB_QUOTES_WORK"] = str(TMP / "work")
from toolhub import create_app, quote  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


SLICE = """<?xml version="1.0" encoding="UTF-8"?>
<config><plate><metadata key="index" value="1"/><metadata key="prediction" value="3600"/>
<filament id="1" type="PETG" used_g="12.5"/></plate></config>"""


def fake_3mf():
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("Metadata/slice_info.config", SLICE)
    return b.getvalue()


# 1. Khoa mau tu ten file: bo duoi file, bo ".gcode", chu thuong, bo khoang trang dau/cuoi
mk = quote.model_key
check(mk("Moc-Khoa.gcode.3mf") == "moc-khoa", f"model_key gcode.3mf: {mk('Moc-Khoa.gcode.3mf')!r}")
check(mk("moc-khoa.3mf") == "moc-khoa", "model_key .3mf")
check(mk("moc-khoa.STL") == "moc-khoa", "model_key .stl cung mau voi file da cat lop")
check(mk("  Moc Khoa .step ") == "moc khoa", f"model_key strip: {mk('  Moc Khoa .step ')!r}")
check(mk(["b.stl", "A.stl"]) == mk(["a.stl", "b.stl"]) == "a+b", f"nhieu file: sap xep, noi '+': {mk(['b.stl', 'A.stl'])!r}")
check(mk("") == "" and mk([]) == "", "ten rong -> khoa rong")

# 2. Luu / doc trong DB
conn = quote.connect()
quote.save_extra(conn, "Nam châm 6x2", 1500)
quote.save_extra(conn, "Insert M3", 800)
ids = {e["label"]: e["id"] for e in quote.get_pricing(conn)["extras"]}
i1, i2 = ids["Nam châm 6x2"], ids["Insert M3"]
check(quote.get_model_extras(conn, "moc-khoa") is None, "mau chua luu -> None")
saved = quote.save_model_extras(conn, "moc-khoa", {str(i1): 4, i2: "2", 999999: 3, "x": 1})
got = quote.get_model_extras(conn, "moc-khoa")
check(got is not None and got["extras"] == {str(i1): 4, str(i2): 2},
      f"luu id hop le, khoa la chuoi, bo id khong ton tai / sai kieu: {got}")
check(got and got.get("updated_at"), "co updated_at")
check(saved and saved.get("extras") == got["extras"], "save tra lai ban da luu")
quote.save_model_extras(conn, "moc-khoa", {str(i1): 1})
check(quote.get_model_extras(conn, "moc-khoa")["extras"] == {str(i1): 1}, "luu lai ghi de (khong cong don)")
quote.save_model_extras(conn, "moc-khoa", {str(i1): 0})
z = quote.get_model_extras(conn, "moc-khoa")
check(z is not None and z["extras"] == {}, f"tat ca = 0 van luu (Tuan da chon 'khong phu kien' cho mau nay): {z}")
quote.save_model_extras(conn, "moc-khoa", {str(i1): 4, str(i2): 2})
quote.delete_extra(conn, i2)
check(quote.get_model_extras(conn, "moc-khoa")["extras"] == {str(i1): 4},
      "phu kien da xoa khoi bang gia khong tra ve nua")
check(quote.save_model_extras(conn, "", {str(i1): 1}) is None, "khoa rong -> khong luu, tra None")
conn.close()

# 3. API
H = {"Host": "127.0.0.1:5050"}
HP = {**H, "X-Studio": "1"}
cl = create_app().test_client()

r = cl.post("/api/quote/upload", data={"file": (io.BytesIO(fake_3mf()), "Moc-Khoa.gcode.3mf")},
            headers=HP, content_type="multipart/form-data")
j = r.get_json() or {}
check(r.status_code == 200, f"upload {r.status_code} {j}")
check(j.get("model_key") == "moc-khoa", f"upload tra model_key: {j.get('model_key')!r}")
check(j.get("saved_extras") == {"extras": {str(i1): 4}, "updated_at": j.get("saved_extras", {}).get("updated_at")},
      f"upload tra saved_extras cua mau da nho: {j.get('saved_extras')}")
tok = j.get("token")

r = cl.post("/api/quote/upload", data={"file": (io.BytesIO(b"solid x\nendsolid x\n"), "mau-moi.stl")},
            headers=HP, content_type="multipart/form-data")
j2 = r.get_json() or {}
check(r.status_code == 200 and j2.get("model_key") == "mau-moi" and j2.get("saved_extras") is None,
      f"mau moi: model_key + saved_extras None: {j2}")

r = cl.post("/api/quote/parse", data={"file": (io.BytesIO(fake_3mf()), "moc-khoa.gcode.3mf")},
            headers=HP, content_type="multipart/form-data")
j3 = r.get_json() or {}
check(r.status_code == 200 and j3.get("model_key") == "moc-khoa" and (j3.get("saved_extras") or {}).get("extras") == {str(i1): 4},
      f"parse cung tra model_key + saved_extras: {j3.get('model_key')} {j3.get('saved_extras')}")

check(cl.post("/api/quote/model-extras", json={"token": tok, "extras": {str(i1): 2}}, headers=H).status_code == 403,
      "POST model-extras khong X-Studio -> 403")
r = cl.post("/api/quote/model-extras", json={"token": tok, "extras": {str(i1): 2}}, headers=HP)
j4 = r.get_json() or {}
check(r.status_code == 200 and j4.get("model_key") == "moc-khoa" and j4.get("extras") == {str(i1): 2}
      and j4.get("updated_at"), f"POST model-extras luu theo token: {r.status_code} {j4}")
r = cl.post("/api/quote/model-extras", json={"token": "khong-co", "extras": {}}, headers=HP)
check(r.status_code == 400, f"token sai -> 400: {r.status_code}")
c = quote.connect()
check(quote.get_model_extras(c, "moc-khoa")["extras"] == {str(i1): 2}, "API da ghi DB")
c.close()

# 4. Giao dien
html = cl.get("/quote", headers=H).get_data(as_text=True)
check('id="extras-note"' in html, "co dong ghi chu nguon phu kien (id=extras-note)")
check("/api/quote/model-extras" in html, "JS goi /api/quote/model-extras khi Tuan sua so luong")
check("saved_extras" in html, "JS dung saved_extras de dien san")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_quote_model_extras")
