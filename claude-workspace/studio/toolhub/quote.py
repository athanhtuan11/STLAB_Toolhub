"""Bao gia in 3D: doc file cat lop Bambu, bang gia va bao gia luu SQLite.

Chi dung thu vien chuan. DB nam ngoai repo (co ten/SDT khach), mac dinh
%LOCALAPPDATA%\\stlab-quotes\\quotes.db, doi bang bien moi truong STLAB_QUOTES_DB.
"""
import base64
import json
import math
import os
import sqlite3
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from . import workspace as ws


class QuoteError(Exception):
    pass


SETTINGS_KEYS = (
    "electricity_price_vnd_per_kwh", "printer_power_w", "machine_price_vnd", "machine_lifetime_hours",
    "labor_rate_vnd_per_hour", "setup_hours_per_job", "post_hours_per_plate", "failure_pct",
    "pricing_method", "pricing_value", "round_to_vnd",
)
SHOP_KEYS = ("shop_phone", "shop_contact", "payment_note", "valid_days")
DEFAULTS = {"round_to_vnd": 1000, "valid_days": 7, "pricing_method": "markup"}


def _db_path():
    env = os.environ.get("STLAB_QUOTES_DB")
    if env:
        return Path(env)
    local = os.environ.get("LOCALAPPDATA")
    base = Path(local) if local else Path.home() / "AppData" / "Local"
    return base / "stlab-quotes" / "quotes.db"


def _num(v):
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def read_3mf(path):
    """Doc Metadata/slice_info.config trong file .gcode.3mf (duong dan hoac file-like)."""
    try:
        with zipfile.ZipFile(path) as z:
            try:
                raw = z.read("Metadata/slice_info.config")
            except KeyError:
                raise QuoteError("File chưa cắt lớp (không có Metadata/slice_info.config). "
                                 "Trong Bambu Studio: File → Export → Export plate sliced file "
                                 "(ra file .gcode.3mf).")
            root = ET.fromstring(raw)
            plates = []
            for pos, p in enumerate(root.iter("plate")):
                md = {m.get("key"): m.get("value") for m in p.findall("metadata")}
                try:
                    idx = int(md.get("index", pos + 1))
                except (TypeError, ValueError):
                    idx = pos + 1
                grams = {}
                for f in p.findall("filament"):
                    typ = f.get("type") or "Không rõ"
                    try:
                        g = float(f.get("used_g") or 0)
                    except ValueError:
                        g = 0.0
                    grams[typ] = grams.get(typ, 0.0) + g
                try:
                    img = z.read(f"Metadata/plate_{idx}.png")
                except KeyError:
                    img = None
                try:
                    seconds = int(float(md.get("prediction") or 0))
                except (TypeError, ValueError):
                    seconds = 0
                plates.append({"index": idx, "seconds": seconds, "grams": grams, "image_png": img})
    except QuoteError:
        raise
    except zipfile.BadZipFile:
        raise QuoteError("File không phải .3mf đã cắt lớp. Trong Bambu Studio: File → Export → "
                         "Export plate sliced file (ra file .gcode.3mf).")
    except (OSError, ET.ParseError, ValueError) as e:
        raise QuoteError("File cắt lớp không hợp lệ: " + str(e))
    if not plates:
        raise QuoteError("File chưa cắt lớp: không có bàn in nào trong slice_info.config.")
    total = {}
    for p in plates:
        for k, v in p["grams"].items():
            total[k] = total.get(k, 0.0) + v
    return {"plates": plates, "hours": sum(p["seconds"] for p in plates) / 3600, "grams": total}


def connect():
    p = _db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(p)
    c.row_factory = sqlite3.Row
    c.executescript(
        "CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT, updated_at TEXT);"
        "CREATE TABLE IF NOT EXISTS materials(name TEXT PRIMARY KEY, spool_price_vnd REAL,"
        " spool_weight_g REAL, updated_at TEXT);"
        "CREATE TABLE IF NOT EXISTS extras(id INTEGER PRIMARY KEY, label TEXT, price_vnd REAL,"
        " active INTEGER);"
        "CREATE TABLE IF NOT EXISTS quotes(id INTEGER PRIMARY KEY, number TEXT UNIQUE, created_at TEXT,"
        " customer_name TEXT, customer_phone TEXT, title TEXT, note TEXT, total_vnd REAL, data_json TEXT);"
    )
    now = datetime.now().isoformat()
    for k, v in DEFAULTS.items():
        c.execute("INSERT OR IGNORE INTO settings VALUES(?,?,?)", (k, json.dumps(v), now))
    c.commit()
    return c


def get_pricing(conn):
    settings = {r["key"]: _num(json.loads(r["value"])) for r in conn.execute("select * from settings")}
    mats = {r["name"]: {"spool_price_vnd": _num(r["spool_price_vnd"]),
                        "spool_weight_g": _num(r["spool_weight_g"])}
            for r in conn.execute("select * from materials order by name")}
    extras = [{"id": r["id"], "label": r["label"], "price_vnd": _num(r["price_vnd"])}
              for r in conn.execute("select id,label,price_vnd from extras where active=1 order by id")]
    return {"settings": settings, "materials": mats, "extras": extras}


def save_settings(conn, data):
    allowed = set(SETTINGS_KEYS) | set(SHOP_KEYS)
    now = datetime.now().isoformat()
    for k, v in data.items():
        if k not in allowed:
            continue
        conn.execute("insert into settings values(?,?,?) on conflict(key) do update set"
                     " value=excluded.value, updated_at=excluded.updated_at",
                     (k, json.dumps(v, ensure_ascii=False), now))
    conn.commit()


def save_material(conn, name, spool_price_vnd, spool_weight_g):
    conn.execute("insert into materials values(?,?,?,?) on conflict(name) do update set"
                 " spool_price_vnd=excluded.spool_price_vnd, spool_weight_g=excluded.spool_weight_g,"
                 " updated_at=excluded.updated_at",
                 (name, float(spool_price_vnd), float(spool_weight_g), datetime.now().isoformat()))
    conn.commit()


def delete_material(conn, name):
    conn.execute("delete from materials where name=?", (name,))
    conn.commit()


def save_extra(conn, label, price_vnd, id=None):
    if id is None:
        out = conn.execute("insert into extras(label,price_vnd,active) values(?,?,1)",
                           (label, float(price_vnd))).lastrowid
    else:
        conn.execute("insert into extras values(?,?,?,1) on conflict(id) do update set"
                     " label=excluded.label, price_vnd=excluded.price_vnd, active=1",
                     (int(id), label, float(price_vnd)))
        out = int(id)
    conn.commit()
    return out


def delete_extra(conn, id):
    conn.execute("delete from extras where id=?", (int(id),))
    conn.commit()


def compute(parsed, pricing, quantity=1, extras=None, other_fee_vnd=0):
    s = pricing.get("settings", {})
    mats = pricing.get("materials", {})
    grams = parsed.get("grams", {})
    missing = [k for k in SETTINGS_KEYS if k not in s]
    missing += [n for n in grams if n not in mats or not mats[n].get("spool_weight_g")]
    if "hours" not in parsed or "plates" not in parsed:
        missing += [k for k in ("hours", "plates") if k not in parsed]
    if missing:
        raise QuoteError("Thiếu dữ liệu bảng giá: " + ", ".join(missing))
    q = int(quantity)
    if q < 1:
        raise QuoteError("Số lượng phải ≥ 1")
    h = float(parsed["hours"])
    n = len(parsed["plates"])
    filament = sum(g * mats[t]["spool_price_vnd"] / mats[t]["spool_weight_g"]
                   for t, g in grams.items()) * q
    electricity = s["printer_power_w"] / 1000 * h * s["electricity_price_vnd_per_kwh"] * q
    depreciation = s["machine_price_vnd"] / s["machine_lifetime_hours"] * h * q
    labor = s["labor_rate_vnd_per_hour"] * (s["setup_hours_per_job"] + s["post_hours_per_plate"] * n * q)
    prices = {x["id"]: x["price_vnd"] for x in pricing.get("extras", [])}
    ex = sum(prices.get(int(i), 0) * int(v) for i, v in (extras or {}).items()) * q
    failure = s["failure_pct"] * (filament + electricity + depreciation)
    lines = {"filament": filament, "electricity": electricity, "depreciation": depreciation,
             "labor": labor, "extras": ex, "failure": failure}
    cost = sum(lines.values())
    method = s["pricing_method"]
    value = s["pricing_value"]
    if method == "margin":
        if value >= 1:
            raise QuoteError("Giá theo biên (margin) phải có hệ số nhỏ hơn 1")
        price = cost / (1 - value)
    else:
        price = cost * (1 + value)
    step = s["round_to_vnd"]
    unit_price = math.ceil(price / q / step - 1e-9) * step
    subtotal = unit_price * q
    return {"lines": lines, "cost": cost, "price": price, "unit_price": unit_price,
            "subtotal": subtotal, "other_fee": other_fee_vnd, "total": subtotal + other_fee_vnd,
            "quantity": q, "hours": h, "grams": grams, "method": method, "value": value}


def fmt_vnd(n):
    return f"{round(n):,}".replace(",", ".") + " đ"


def _next_number(conn):
    day = datetime.now().strftime("%Y%m%d")
    prefix = f"BG-{day}-"
    top = 0
    for r in conn.execute("select number from quotes where number like ?", (prefix + "%",)):
        try:
            top = max(top, int(str(r["number"]).rsplit("-", 1)[-1]))
        except ValueError:
            pass
    return f"{prefix}{top + 1:02d}"


def save_quote(conn, customer_name, customer_phone, title, parsed, calc, note):
    now = datetime.now()
    number = _next_number(conn)
    pr = get_pricing(conn)
    data = dict(calc)
    data["plates"] = [{"index": p["index"], "seconds": p["seconds"], "grams": p["grams"],
                       "hours": p["seconds"] / 3600} for p in parsed["plates"]]
    first = next((p for p in parsed["plates"] if p.get("image_png")), None)
    data["image"] = base64.b64encode(first["image_png"]).decode() if first else None
    data["pricing"] = pr
    data["valid_days"] = pr["settings"].get("valid_days", 7)
    rid = conn.execute(
        "insert into quotes(number,created_at,customer_name,customer_phone,title,note,total_vnd,data_json)"
        " values(?,?,?,?,?,?,?,?)",
        (number, now.isoformat(), customer_name, customer_phone, title, note, calc["total"],
         json.dumps(data, ensure_ascii=False))).lastrowid
    conn.commit()
    return rid


def get_quote(conn, id):
    r = conn.execute("select * from quotes where id=?", (int(id),)).fetchone()
    if r is None:
        return None
    d = dict(r)
    d["data"] = json.loads(d.pop("data_json"))
    return d


def list_quotes(conn, limit=50):
    return [dict(r) for r in conn.execute(
        "select id,number,created_at,customer_name,customer_phone,title,total_vnd"
        " from quotes order by created_at desc, id desc limit ?", (int(limit),))]


def project_3mf_files():
    p = ws.ROOT / "maker"
    return sorted(p.glob("*/print/plates/*/*.3mf")) if p.exists() else []
