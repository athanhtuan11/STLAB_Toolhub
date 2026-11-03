# Gate "Bao gia v6 – danh muc mau + anh phong nen + xuat Excel" (Claude viet, executor KHONG sua). Chay tu studio:
#   .venv\Scripts\python.exe tests\test_quote_catalog.py
# Tuan 2026-11-03: luu bao gia -> thong tin mau vao DB (bang catalog); sau nay xuat 1 lan ra Excel toan bo mau;
# anh mau co phong nen STLab (ban go + bang STLab) tu ghep offline (u2net tach nen, ghep len stlab-desk.jpg).
# DB + anh o thu muc tam (STLAB_QUOTES_DB / STLAB_QUOTES_WORK). Khong goi u2net that (gia lap cutout).
import io, os, sys, tempfile, zipfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
TMP = Path(tempfile.mkdtemp(prefix="stlab-quote-cat-"))
os.environ["STLAB_QUOTES_DB"] = str(TMP / "quotes.db")
os.environ["STLAB_QUOTES_WORK"] = str(TMP / "work")
from PIL import Image  # noqa: E402
import openpyxl  # noqa: E402
from toolhub import create_app, quote, catalog  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def png(size=(512, 512), alpha=True):
    """Vat the gia: hinh tron hong tren nen trong suot (giong plate_1.png cua Bambu)."""
    im = Image.new("RGBA" if alpha else "RGB", size, (0, 0, 0, 0) if alpha else (40, 40, 40))
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    w, h = size
    d.ellipse((w * .25, h * .25, w * .75, h * .75), fill=(230, 60, 160, 255) if alpha else (230, 60, 160))
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


SLICE = """<?xml version="1.0" encoding="UTF-8"?>
<config><plate><metadata key="index" value="1"/><metadata key="prediction" value="3600"/>
<filament id="1" type="PETG" used_g="41"/></plate></config>"""


def fake_3mf(with_img=True):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("Metadata/slice_info.config", SLICE)
        if with_img:
            z.writestr("Metadata/plate_1.png", png())
    return b.getvalue()


PLATE = STUDIO / "toolhub" / "static" / "quote" / "stlab-desk.jpg"
check(PLATE.exists(), "anh nen toolhub/static/quote/stlab-desk.jpg (Claude dat san, khong xoa)")
plate = Image.open(PLATE).convert("RGB")

# 1. Ghep anh len phong nen
rgba = Image.open(io.BytesIO(png())).convert("RGBA")
out = catalog.compose_on_plate(rgba)
check(out.mode == "RGB" and out.size == plate.size, f"compose: RGB, dung co anh nen {plate.size}: {out.mode} {out.size}")
W, H = out.size
cx, cy = int(0.52 * W), int(0.87 * H) - int(0.58 * H * 0.5)
px = out.getpixel((cx, cy))
check(px[0] > 180 and px[1] < 120 and px[2] > 110, f"vat the nam giua khung (x 52 %, day 87 % chieu cao): {px}")
for xy in ((5, 5), (W - 6, 5), (5, H - 6), (W - 6, H - 6)):
    a, b = out.getpixel(xy), plate.getpixel(xy)
    check(max(abs(a[i] - b[i]) for i in range(3)) <= 6, f"goc {xy} giu nguyen anh nen: {a} vs {b}")
sx, sy = cx, int(0.87 * H) + int(0.012 * H)
check(sum(out.getpixel((sx, sy))) < sum(plate.getpixel((sx, sy))) - 15,
      "co bong do ngay duoi vat the (toi hon anh nen)")
check(catalog.has_alpha(rgba) and not catalog.has_alpha(Image.open(io.BytesIO(png(alpha=False)))),
      "has_alpha: PNG nen trong suot -> True, anh chup -> False")

calls = []


def fake_cutout(img):
    calls.append(img.size)
    return Image.open(io.BytesIO(png(img.size))).convert("RGBA")


catalog.cutout_u2net = fake_cutout

# 2. Bang catalog
conn = quote.connect()
catalog.ensure(conn)
mid = catalog.create(conn, "Chân Chó Sticky", grams=41, unit_price=40000)
it = catalog.get(conn, mid)
check(it and it["name"] == "Chân Chó Sticky" and it["grams"] == 41 and it["unit_price"] == 40000
      and it["price_bulk1"] is None and it["model_key"] is None, f"create mau tay: {it}")
catalog.update(conn, mid, note="Quà tặng", price_bulk1="36000", grams="")
it = catalog.get(conn, mid)
check(it["note"] == "Quà tặng" and it["price_bulk1"] == 36000 and it["grams"] is None,
      f"update: chuoi so -> so, chuoi rong -> None: {it}")
catalog.update(conn, mid, grams=41, hacker="x", id=999)
check(catalog.get(conn, mid)["id"] == mid, "update bo qua truong la")

fn = catalog.set_photo(conn, mid, png(alpha=False), compose=False)
check(fn and (catalog.photo_dir() / fn).exists() and not calls, f"set_photo giu nguyen anh (khong tach nen): {fn} {calls}")
fn2 = catalog.set_photo(conn, mid, png((800, 450), alpha=False), compose=True)
p2 = Image.open(catalog.photo_dir() / fn2)
check(calls == [(800, 450)] and p2.size == plate.size, f"set_photo compose: anh chup -> u2net -> ghep nen: {calls} {p2.size}")
calls.clear()
catalog.set_photo(conn, mid, png(), compose=True)
check(not calls, "PNG da trong suot -> khong goi u2net")
conn.close()

# 3. API + luu bao gia -> catalog
Hh = {"Host": "127.0.0.1:5050"}
HP = {**Hh, "X-Studio": "1"}
cl = create_app().test_client()
c = quote.connect()
quote.save_material(c, "PETG Test", 300000, 1000, type="PETG")
c.close()
r = cl.post("/api/quote/upload", data={"file": (io.BytesIO(fake_3mf()), "Moc-Khoa-Cuu.gcode.3mf")},
            headers=HP, content_type="multipart/form-data")
tok = (r.get_json() or {}).get("token")
body = {"token": tok, "quantity": 120, "materials_map": {"PETG": "PETG Test"}, "title": "Móc khóa cừu",
        "customer_name": "Khách A", "customer_phone": "", "note": ""}
r = cl.post("/api/quote/save", json=body, headers=HP)
j = r.get_json() or {}
check(r.status_code == 200 and j.get("catalog_id"), f"save tra catalog_id: {r.status_code} {j}")
c = quote.connect()
pr = quote.get_pricing(c)
ref1 = quote.compute(quote.read_3mf(io.BytesIO(fake_3mf())), pr, quantity=1, materials_map={"PETG": "PETG Test"})
ref50 = quote.compute(quote.read_3mf(io.BytesIO(fake_3mf())), pr, quantity=int(pr["settings"]["bulk1_min_qty"]),
                      materials_map={"PETG": "PETG Test"})
ent = catalog.get(c, j.get("catalog_id"))
check(ent and ent["model_key"] == "moc-khoa-cuu" and ent["name"] == "Móc khóa cừu", f"catalog theo model_key + ten: {ent}")
check(ent and ent["unit_price"] == ref1["unit_price_list"], f"gia le = gia 1 cai (khong theo SL 120 cua khach): {ent and ent['unit_price']} vs {ref1['unit_price_list']}")
check(ent and ent["price_bulk1"] == ref50["unit_price"], f"gia si muc 1 = compute(qty=bulk1_min_qty): {ent and ent['price_bulk1']}")
check(ent and abs((ent["grams"] or 0) - 41) < 0.05 and ent["material"] == "PETG Test" and ent["quote_id"] == j.get("id"),
      f"grams/material/quote_id: {ent}")
check(ent and ent["photo"] and (catalog.photo_dir() / ent["photo"]).exists(), "anh mac dinh tu thumbnail ban in, da ghep nen")
check(not calls, "thumbnail Bambu co alpha -> khong goi u2net")
catalog.update(c, ent["id"], note="Bán chạy")
c.close()
body.update({"title": "", "quantity": 1})
j2 = cl.post("/api/quote/save", json=body, headers=HP).get_json() or {}
c = quote.connect()
ent2 = catalog.get(c, j2.get("catalog_id"))
check(j2.get("catalog_id") == j.get("catalog_id") and ent2["name"] == "Móc khóa cừu" and ent2["note"] == "Bán chạy",
      f"luu lai cung mau: cap nhat cung dong, giu ten + ghi chu khi tieu de rong: {ent2}")
check(len(catalog.list_all(c)) == 2, "2 mau trong danh muc")
c.close()

check(cl.post("/api/quote/catalog", json={"name": "X"}, headers=Hh).status_code == 403, "POST khong X-Studio -> 403")
r = cl.post("/api/quote/catalog", json={"name": "Bookmark Đà Lạt", "unit_price": 15000}, headers=HP)
nid = (r.get_json() or {}).get("id")
check(r.status_code == 200 and nid, f"tao mau tay qua API: {r.status_code}")
r = cl.post(f"/api/quote/catalog/{nid}", json={"grams": 8}, headers=HP)
check(r.status_code == 200 and (r.get_json() or {}).get("grams") == 8, "sua mau qua API tra ban ghi moi")
r = cl.post(f"/api/quote/catalog/{nid}/photo", data={"file": (io.BytesIO(png((640, 360), alpha=False)), "a.jpg")},
            headers=HP, content_type="multipart/form-data")
check(r.status_code == 200 and calls == [(640, 360)], f"tai anh chup -> tach nen + ghep: {r.status_code} {calls}")
r = cl.post(f"/api/quote/catalog/{nid}/photo", data={"file": (io.BytesIO(png()), "a.png"), "keep": "1"},
            headers=HP, content_type="multipart/form-data")
check(r.status_code == 200 and len(calls) == 1, "keep=1 -> giu nguyen anh")
g = cl.get(f"/quote/catalog/{nid}/photo", headers=Hh)
check(g.status_code == 200 and g.mimetype == "image/jpeg", f"xem anh mau: {g.status_code} {g.mimetype}")
check(cl.get("/quote/catalog/999/photo", headers=Hh).status_code == 404, "anh khong co -> 404")
r = cl.post(f"/api/quote/catalog/{nid}/delete", headers=HP)
c = quote.connect()
check(r.status_code == 200 and catalog.get(c, nid) is None and len(catalog.list_all(c)) == 2, "xoa mau")
c.close()
check(cl.post("/api/quote/catalog/999", json={"name": "x"}, headers=HP).status_code == 404, "sua mau khong co -> 404")

# 4. Trang danh muc
html = cl.get("/quote/catalog", headers=Hh).get_data(as_text=True)
check("Chân Chó Sticky" in html and "Móc khóa cừu" in html, "trang /quote/catalog liet ke mau")
check("/quote/catalog.xlsx" in html, "nut Xuat Excel")
check("/api/quote/catalog" in html, "JS sua/them/xoa/tai anh qua /api/quote/catalog")
check("/quote/catalog" in cl.get("/quote", headers=Hh).get_data(as_text=True), "tab Bao gia co link Danh muc mau")

# 5. Xuat Excel
r = cl.get("/quote/catalog.xlsx", headers=Hh)
check(r.status_code == 200 and "spreadsheetml" in (r.mimetype or ""), f"xlsx: {r.status_code} {r.mimetype}")
cd = r.headers.get("Content-Disposition", "")
check("BaoGia-STLab-" in cd and ".xlsx" in cd, f"ten file BaoGia-STLab-YYYYMMDD.xlsx: {cd}")
wb = openpyxl.load_workbook(io.BytesIO(r.data))
ws = wb.active
check(ws.title == "Bảng giá", f"ten sheet: {ws.title}")
cells = {c.coordinate: c.value for row in ws.iter_rows() for c in row if c.value is not None}
text = " | ".join(str(v) for v in cells.values())
check("STLab" in text and "BẢNG GIÁ SẢN PHẨM IN 3D" in text, "dau trang: STLab + tieu de")
hdr = [ws.cell(7, i).value for i in range(1, 9)]
check(hdr[:5] == ["STT", "Hình ảnh", "Tên sản phẩm", "Khối lượng (g)", "Giá lẻ (đ)"] and hdr[7] == "Ghi chú"
      and "50" in str(hdr[5]) and "100" in str(hdr[6]), f"hang tieu de cot (hang 7): {hdr}")
check(ws.freeze_panes == "A8", f"co dinh duoi tieu de: {ws.freeze_panes}")
rows = [[ws.cell(r_, i).value for i in range(1, 9)] for r_ in (8, 9)]
check(rows[0][0] == 1 and rows[0][2] == "Chân Chó Sticky" and rows[0][3] == 41 and rows[0][4] == 40000
      and rows[0][5] == 36000 and rows[0][7] == "Quà tặng", f"dong 1 = mau tao truoc: {rows[0]}")
check(rows[0][6] == "Liên hệ", f"gia trong -> 'Liên hệ': {rows[0][6]}")
check(rows[1][0] == 2 and rows[1][2] == "Móc khóa cừu", f"dong 2: {rows[1]}")
check("đ" in ws.cell(8, 5).number_format, f"dinh dang tien co 'đ': {ws.cell(8, 5).number_format}")
check(ws.cell(10, 3).value in (None, "") or "STT" not in str(ws.cell(10, 1).value), "khong thua dong")
check(len(ws._images) == 2, f"moi mau co anh -> 2 anh nhung: {len(ws._images)}")
check(int(ws.page_setup.paperSize) == 9 and ws.page_setup.orientation == "portrait"
      and ws.sheet_properties.pageSetUpPr.fitToPage and ws.page_setup.fitToWidth == 1,
      "in A4 doc, vua 1 trang ngang")
check(ws.print_title_rows and "7" in str(ws.print_title_rows), f"lap lai hang tieu de khi in: {ws.print_title_rows}")
check(len(r.data) < 1_500_000, f"file nhe (anh thu nho): {len(r.data)} byte")
check(any("vận chuyển" in str(v) for v in cells.values()), "ghi chu cuoi: chua gom phi van chuyen")

# 6. u2net that (chi chay khi da co model tren may): vat tron giua anh -> mat na phu dung vat, khong phai 1 hang pixel
_real = Path(os.environ.get("STLAB_U2NET") or Path.home() / ".u2net" / "u2net.onnx")
if _real.exists():
    import importlib
    cat2 = importlib.reload(catalog)
    src = Image.new("RGB", (800, 450), (60, 60, 60))
    from PIL import ImageDraw
    ImageDraw.Draw(src).ellipse((300, 125, 500, 325), fill=(230, 60, 160))
    m = cat2.cutout_u2net(src).getchannel("A")
    check(m.size == (800, 450), f"u2net: mat na dung co anh: {m.size}")
    check(m.getpixel((400, 225)) > 200 and m.getpixel((40, 40)) < 60, f"u2net: giua = vat, goc = nen: "
          f"{m.getpixel((400, 225))} / {m.getpixel((40, 40))}")
    bb = m.point(lambda v: 255 if v > 128 else 0).getbbox()
    check(bb and 260 < bb[0] < 340 and 85 < bb[1] < 165 and 460 < bb[2] < 540 and 285 < bb[3] < 365,
          f"u2net: khung vat ~ (300,125,500,325): {bb}")
else:
    print("(bo qua u2net that: chua co ~/.u2net/u2net.onnx)")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_quote_catalog")
