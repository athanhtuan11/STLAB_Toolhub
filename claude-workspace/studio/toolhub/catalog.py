"""Danh mục mẫu: lưu thông tin mẫu từ báo giá, ảnh có phông nền STLab, xuất Excel."""
import io
import math
import os
import urllib.request
from datetime import datetime
from pathlib import Path

from . import quote

PLATE = Path(__file__).parent / "static" / "quote" / "stlab-desk.jpg"
U2NET_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
_FIELDS_NUM = ("grams", "unit_price", "price_bulk1", "price_bulk2")
_EDITABLE = ("name", "grams", "unit_price", "price_bulk1", "price_bulk2", "note")
_session = None


def photo_dir():
    d = quote._db_path().parent / "catalog-photos"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS catalog(id INTEGER PRIMARY KEY, model_key TEXT UNIQUE, name TEXT,"
                 " grams REAL, unit_price REAL, price_bulk1 REAL, price_bulk2 REAL, material TEXT, hours REAL,"
                 " quote_id INTEGER, photo TEXT, note TEXT, created_at TEXT, updated_at TEXT)")
    conn.commit()


def _n(v):
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def _num_in(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip().replace(",", ".")
        if v == "":
            return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _fetch(conn, sql, args=()):
    cur = conn.execute(sql, args)
    cols = [d[0] for d in cur.description]
    rows = []
    for r in cur.fetchall():
        d = dict(zip(cols, tuple(r)))
        for k in _FIELDS_NUM + ("hours",):
            d[k] = _n(d.get(k))
        rows.append(d)
    return rows


def get(conn, id):
    ensure(conn)
    rows = _fetch(conn, "SELECT * FROM catalog WHERE id=?", (id,))
    return rows[0] if rows else None


def list_all(conn):
    ensure(conn)
    return _fetch(conn, "SELECT * FROM catalog ORDER BY id")


def create(conn, name, grams=None, unit_price=None, price_bulk1=None, price_bulk2=None, note=""):
    ensure(conn)
    now = datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO catalog(model_key,name,grams,unit_price,price_bulk1,price_bulk2,note,created_at,updated_at)"
        " VALUES(NULL,?,?,?,?,?,?,?,?)",
        (name, _num_in(grams), _num_in(unit_price), _num_in(price_bulk1), _num_in(price_bulk2), note or "", now, now))
    conn.commit()
    return cur.lastrowid


def update(conn, id, /, **fields):
    ensure(conn)
    if get(conn, id) is None:
        return None
    sets, args = [], []
    for k, v in fields.items():
        if k not in _EDITABLE:
            continue
        if k in _FIELDS_NUM:
            v = _num_in(v)
        elif v is None:
            v = ""
        sets.append(f"{k}=?")
        args.append(v)
    sets.append("updated_at=?")
    args.append(datetime.now().isoformat())
    conn.execute(f"UPDATE catalog SET {', '.join(sets)} WHERE id=?", (*args, id))
    conn.commit()
    return get(conn, id)


def delete(conn, id):
    ensure(conn)
    it = get(conn, id)
    if it is None:
        return
    if it.get("photo"):
        try:
            (photo_dir() / it["photo"]).unlink()
        except OSError:
            pass
    conn.execute("DELETE FROM catalog WHERE id=?", (id,))
    conn.commit()


def upsert_from_quote(conn, model_key, name, parsed, pricing, extras=None, materials_map=None, quote_id=None):
    ensure(conn)
    c1 = quote.compute(parsed, pricing, quantity=1, extras=extras, materials_map=materials_map)
    s = pricing.get("settings", {})
    bulk = {}
    for k in (1, 2):
        try:
            mq = float(s.get(f"bulk{k}_min_qty"))
        except (TypeError, ValueError):
            mq = 0
        bulk[k] = None
        if mq > 0:
            bulk[k] = quote.compute(parsed, pricing, quantity=int(math.ceil(mq)), extras=extras,
                                    materials_map=materials_map)["unit_price"]
    grams = round(sum(c1["materials"].values()), 1)
    material = " + ".join(c1["materials"])
    now = datetime.now().isoformat()
    row = _fetch(conn, "SELECT id, name FROM catalog WHERE model_key=?", (model_key,))
    if row:
        cid = row[0]["id"]
        new_name = name if (name or "").strip() else row[0]["name"]
        conn.execute("UPDATE catalog SET name=?, grams=?, unit_price=?, price_bulk1=?, price_bulk2=?, material=?,"
                     " hours=?, quote_id=?, updated_at=? WHERE id=?",
                     (new_name, grams, c1["unit_price_list"], bulk[1], bulk[2], material, parsed["hours"],
                      quote_id, now, cid))
    else:
        cur = conn.execute("INSERT INTO catalog(model_key,name,grams,unit_price,price_bulk1,price_bulk2,material,"
                           "hours,quote_id,note,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                           (model_key, name or model_key, grams, c1["unit_price_list"], bulk[1], bulk[2], material,
                            parsed["hours"], quote_id, "", now, now))
        cid = cur.lastrowid
    conn.commit()
    return cid


# ---------- Ảnh ----------
def has_alpha(img):
    if "A" not in img.getbands():
        return False
    low = sum(img.getchannel("A").histogram()[:250])
    return low >= 0.05 * (img.width * img.height)


def _model_path():
    env = os.environ.get("STLAB_U2NET")
    return Path(env) if env else Path.home() / ".u2net" / "u2net.onnx"


def _get_session():
    global _session
    if _session is None:
        import onnxruntime as ort
        p = _model_path()
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(".onnx.part")
            urllib.request.urlretrieve(U2NET_URL, tmp)
            tmp.replace(p)
        _session = ort.InferenceSession(str(p), providers=["CPUExecutionProvider"])
    return _session


def cutout_u2net(img):
    import numpy as np
    from PIL import Image
    sess = _get_session()
    rgb = img.convert("RGB")
    small = rgb.resize((320, 320), Image.LANCZOS)
    arr = np.asarray(small, dtype=np.float32)
    arr = arr / max(float(arr.max()), 1e-6)
    arr = (arr - np.array([0.485, 0.456, 0.406], dtype=np.float32)) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
    x = arr.transpose(2, 0, 1)[None].astype(np.float32)
    out = sess.run(None, {sess.get_inputs()[0].name: x})[0][0, 0]  # (1,1,320,320) -> (320,320)
    mn, mx = float(out.min()), float(out.max())
    m = (out - mn) / max(mx - mn, 1e-8)
    mask = Image.fromarray((m * 255).astype("uint8"), "L").resize(rgb.size, Image.LANCZOS)
    res = rgb.convert("RGBA")
    res.putalpha(mask)
    return res


def compose_on_plate(rgba):
    from PIL import Image, ImageEnhance, ImageFilter
    plate = Image.open(PLATE).convert("RGB")
    W, H = plate.size
    rgba = rgba.convert("RGBA")
    a = rgba.getchannel("A").point(lambda v: 0 if v < 128 else 255)
    a = a.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    bbox = a.getbbox()
    if not bbox:
        return plate
    rgb = rgba.convert("RGB").crop(bbox)
    a = a.crop(bbox)
    w, h = rgb.size
    s = min(0.40 * W / w, 0.58 * H / h)
    nw, nh = max(1, int(round(w * s))), max(1, int(round(h * s)))
    rgb = rgb.resize((nw, nh), Image.LANCZOS)
    a = a.resize((nw, nh), Image.LANCZOS)
    cx, by = int(0.52 * W), int(0.87 * H)
    x, y = cx - nw // 2, by - nh
    rgb = ImageEnhance.Brightness(ImageEnhance.Color(rgb).enhance(1.10)).enhance(1.08)
    out = plate.copy()

    def shadow(dx, dy, blur, k, color):
        nonlocal out
        m = Image.new("L", (W, H), 0)
        m.paste(a, (x + dx, y + dy))
        m = m.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * k))
        out = Image.composite(Image.new("RGB", (W, H), color), out, m)

    shadow(int(W * .012), int(H * .03), H * .03, 0.45, (70, 40, 15))
    shadow(0, int(H * .008), H * .008, 0.55, (35, 20, 8))
    out.paste(rgb, (x, y), a)
    return out


def set_photo(conn, id, data, compose=True):
    from PIL import Image, ImageOps
    ensure(conn)
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
    if not compose:
        res = img.convert("RGB")
        res.thumbnail((1672, 1672), Image.LANCZOS)
    else:
        if has_alpha(img):
            rgba = img.convert("RGBA")
        else:
            rgb = img.convert("RGB")
            rgb.thumbnail((1600, 1600), Image.LANCZOS)
            rgba = cutout_u2net(rgb)
        res = compose_on_plate(rgba)
    fn = f"{id}.jpg"
    res.save(photo_dir() / fn, "JPEG", quality=88)
    conn.execute("UPDATE catalog SET photo=?, updated_at=? WHERE id=?", (fn, datetime.now().isoformat(), id))
    conn.commit()
    return fn


# ---------- Excel ----------
def _pct(d):
    v = float(d or 0) * 100
    return str(int(round(v))) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def export_xlsx(conn, pricing):
    from openpyxl import Workbook
    from openpyxl.drawing.image import Image as XImage
    from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
    from openpyxl.drawing.xdr import XDRPositiveSize2D
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils.units import pixels_to_EMU
    from PIL import Image

    BLUE, ORANGE, GREY, LINE, ZEBRA = "1E4FD8", "F47B20", "6B7280", "D0D5DD", "F3F6FC"
    s = pricing.get("settings", {})
    items = list_all(conn)
    wb = Workbook()
    ws = wb.active
    ws.title = "Bảng giá"
    for col, wd in zip("ABCDEFGH", (6, 34, 34, 13, 15, 15, 15, 24)):
        ws.column_dimensions[col].width = wd

    def F(**k):
        return Font(name="Arial", **k)

    def top(row, text, font, height):
        ws.merge_cells(f"A{row}:H{row}")
        ws[f"A{row}"] = text
        ws[f"A{row}"].font = font
        ws[f"A{row}"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[row].height = height

    top(1, "STLab · 3D Printing • Robotics • STEAM", F(size=20, bold=True, color=BLUE), 32)
    sub = "Trung tâm STEAM · Đức Trọng, Lâm Đồng"
    if s.get("shop_phone"):
        sub += f" · ĐT {s['shop_phone']}"
    if s.get("shop_contact"):
        sub += f" · {s['shop_contact']}"
    top(2, sub, F(size=10, color=GREY), 16)
    for c in "ABCDEFGH":
        ws[f"{c}3"].fill = PatternFill("solid", fgColor=ORANGE)
    ws.row_dimensions[3].height = 4
    top(4, "BẢNG GIÁ SẢN PHẨM IN 3D", F(size=16, bold=True), 26)
    top(5, f"Cập nhật {datetime.now().strftime('%d/%m/%Y')} · Giá cho 1 sản phẩm, đã gồm nhựa, điện, công in",
        F(size=10, italic=True, color=GREY), 16)
    ws.row_dimensions[6].height = 6

    def q(k):
        try:
            return _n(float(s.get(f"bulk{k}_min_qty")))
        except (TypeError, ValueError):
            return ""
    heads = ["STT", "Hình ảnh", "Tên sản phẩm", "Khối lượng (g)", "Giá lẻ (đ)",
             f"Sỉ ≥{q(1)} cái (−{_pct(s.get('bulk1_discount_pct'))}%)",
             f"Sỉ ≥{q(2)} cái (−{_pct(s.get('bulk2_discount_pct'))}%)", "Ghi chú"]
    thin = Side(style="thin", color=LINE)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for i, h in enumerate(heads, 1):
        c = ws.cell(7, i, h)
        c.font = F(size=11, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=BLUE)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border
    ws.row_dimensions[7].height = 32
    ws.freeze_panes = "A8"
    ws.print_title_rows = "7:7"

    col_px_b = 34 * 7 + 5
    row_px = int(102 * 96 / 72)
    r = 8
    for n, it in enumerate(items, 1):
        fill = PatternFill("solid", fgColor=ZEBRA) if n % 2 == 0 else None
        vals = [n, None, it["name"] or "", it["grams"], it["unit_price"], it["price_bulk1"], it["price_bulk2"],
                it["note"] or ""]
        for i, v in enumerate(vals, 1):
            c = ws.cell(r, i)
            c.border = border
            if fill:
                c.fill = fill
            c.alignment = Alignment(horizontal="center", vertical="center")
            if i == 1:
                c.value = v
                c.font = F(size=11)
            elif i == 3:
                c.value = v
                c.font = F(size=11, bold=True)
                c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            elif i == 4:
                c.value = v
                c.font = F(size=11)
                c.number_format = "0" if (v is None or float(v).is_integer()) else "0.#"
                c.alignment = Alignment(horizontal="right", vertical="center")
            elif i in (5, 6, 7):
                if v is None:
                    c.value = "Liên hệ"
                    c.font = F(size=11, color=GREY)
                else:
                    c.value = v
                    c.font = F(size=11)
                    c.number_format = '#,##0" đ"'
                    c.alignment = Alignment(horizontal="right", vertical="center")
            elif i == 8:
                c.value = v
                c.font = F(size=10)
                c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.row_dimensions[r].height = 102
        p = photo_dir() / it["photo"] if it.get("photo") else None
        if p and p.exists():
            im = Image.open(p).convert("RGB")
            im.thumbnail((230, 129), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=85)
            buf.seek(0)
            xi = XImage(buf)
            xi.width, xi.height = im.size
            ox = max(0, (col_px_b - im.width) // 2)
            oy = max(0, (row_px - im.height) // 2)
            marker = AnchorMarker(col=1, colOff=pixels_to_EMU(ox), row=r - 1, rowOff=pixels_to_EMU(oy))
            xi.anchor = OneCellAnchor(_from=marker, ext=XDRPositiveSize2D(pixels_to_EMU(im.width),
                                                                           pixels_to_EMU(im.height)))
            ws.add_image(xi)
        r += 1
    r += 1
    notes = ["• Giá sỉ áp dụng khi đặt cùng một mẫu.", "• Giá chưa gồm phí vận chuyển.",
             f"• Báo giá có hiệu lực {_n(s.get('valid_days', 7))} ngày kể từ ngày cập nhật."]
    for t in notes:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        ws.cell(r, 1, t).font = F(size=9.5, color=GREY)
        ws.cell(r, 1).alignment = Alignment(horizontal="left", vertical="center")
        r += 1

    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "portrait"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_margins.left = ws.page_margins.right = ws.page_margins.top = ws.page_margins.bottom = 0.4
    ws.print_options.horizontalCentered = True
    ws.oddFooter.center.text = "STLab – Trang &P/&N"
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()
