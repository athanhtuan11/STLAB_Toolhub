"""Bao gia in 3D: doc file cat lop Bambu, bang gia va bao gia luu SQLite.

Chi dung thu vien chuan. DB nam ngoai repo (co ten/SDT khach), mac dinh
%LOCALAPPDATA%\\stlab-quotes\\quotes.db, doi bang bien moi truong STLAB_QUOTES_DB.
"""
import base64
import hashlib
import json
import math
import os
import shutil
import sqlite3
import subprocess
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
BULK_KEYS = ("bulk1_min_qty", "bulk1_discount_pct", "bulk2_min_qty", "bulk2_discount_pct")
SHOP_KEYS = ("shop_phone", "shop_contact", "payment_note", "valid_days")
DEFAULTS_FILE = Path(__file__).resolve().parent / "quote_defaults.json"
WORK_ENV = "STLAB_QUOTES_WORK"
MAX_UPLOADS = 30
NO_WINDOW = 0x08000000
FREE_PY = Path(r"C:\Program Files\FreeCAD 1.1\bin\python.exe")
QUOTE_SLICE = ws.ROOT / "tools" / "robotics-cad" / "scripts" / "quote_slice.py"
TYPE_KEYS = ("PCTG", "PETG", "PET", "PLA", "TPU", "ABS", "ASA", "PC", "PA", "PVA", "HIPS", "PE", "PP")
_profiles_cache = None
_slice_cache = {}


def load_defaults():
    """Thoi gia mac dinh (Claude tra, co nguon) trong quote_defaults.json canh file .py."""
    try:
        return json.loads(DEFAULTS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise QuoteError("Không đọc được thời giá mặc định (quote_defaults.json): " + str(e))


def defaults_updated():
    return load_defaults().get("updated") or ""


def pricing_sources():
    """Nguon cua tung khoa thoi gia + 'material:<ten>' cho nhua (hien tren trang)."""
    defaults = load_defaults()
    out = {}
    for k, d in (defaults.get("settings") or {}).items():
        src = {"source": d.get("source") or ""}
        if d.get("url"):
            src["url"] = d["url"]
        if d.get("gia_dinh"):
            src["gia_dinh"] = True
        out[k] = src
    for name, m in (defaults.get("materials") or {}).items():
        src = {"source": m.get("source") or ""}
        if m.get("url"):
            src["url"] = m["url"]
        if m.get("gia_dinh"):
            src["gia_dinh"] = True
        out["material:" + name] = src
    return out


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


def infer_type(name):
    """Suy loai nhua tu ten (PETG truoc PET, PCTG truoc PC)."""
    up = str(name or "").upper()
    for t in TYPE_KEYS:
        if t in up:
            return t
    return ""


def default_profile(name, type_=None):
    """Profile trong quote_defaults.json neu ten trung nhua mac dinh, con lai Generic <loai> @BBL A1."""
    m = (load_defaults().get("materials") or {}).get(name) or {}
    return m.get("slicer_profile") or (f"Generic {type_} @BBL A1" if type_ else "")


def work_dir():
    """Thu muc upload + ket qua cat lop (mac dinh %LOCALAPPDATA%\\stlab-quotes, env STLAB_QUOTES_WORK)."""
    env = os.environ.get(WORK_ENV)
    if env:
        base = Path(env)
    else:
        local = os.environ.get("LOCALAPPDATA")
        base = (Path(local) if local else Path.home() / "AppData" / "Local") / "stlab-quotes"
    uploads = base / "uploads"
    for sub in (uploads, base / "slices"):
        sub.mkdir(parents=True, exist_ok=True)
    try:
        dirs = sorted((p for p in uploads.iterdir() if p.is_dir()),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        dirs = []
    for old in dirs[MAX_UPLOADS:]:
        shutil.rmtree(old, ignore_errors=True)
    return base


def _last_json(text):
    for line in reversed((text or "").strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def slicer_profiles():
    """Danh sach profile filament/process A1 0.4 (quote_slice.py --list-filaments, cache trong bo nho)."""
    global _profiles_cache
    if _profiles_cache is not None:
        return _profiles_cache
    if not FREE_PY.exists() or not QUOTE_SLICE.exists():
        raise QuoteError("Không tìm thấy FreeCAD hoặc quote_slice.py để cắt lớp")
    try:
        r = subprocess.run([str(FREE_PY), str(QUOTE_SLICE), "--list-filaments"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=180,
                           creationflags=NO_WINDOW, cwd=str(QUOTE_SLICE.parent))
    except (OSError, subprocess.SubprocessError) as e:
        raise QuoteError("Không đọc được danh sách profile cắt lớp: " + str(e))
    j = _last_json(r.stdout)
    if j is None:
        raise QuoteError("Không đọc được danh sách profile cắt lớp: " + (r.stderr or r.stdout or "")[-300:])
    _profiles_cache = {"filaments": sorted(set(j.get("filaments") or [])),
                       "processes": sorted(set(j.get("processes") or []))}
    return _profiles_cache


def _files_key(files):
    parts = []
    for f in files:
        try:
            st = Path(f).stat()
            parts.append(f"{Path(f).name}:{st.st_size}:{int(st.st_mtime)}")
        except OSError:
            parts.append(str(f))
    return "|".join(parts)


def _slice_parsed(res):
    gp = res.get("gcode_3mf")
    if gp and Path(gp).exists():
        try:
            return read_3mf(gp)
        except QuoteError:
            pass
    seconds = int(res.get("seconds") or 0)
    grams = res.get("grams") or {}
    return {"plates": [{"index": 1, "seconds": seconds, "grams": grams, "image_png": None}],
            "hours": seconds / 3600, "grams": grams}


def _slice_ok(res):
    gp = res.get("gcode_3mf")
    return res.get("status") in ("ok", "warn") and bool(gp) and Path(gp).exists()


def _run_slice(out, profile, process, infill, support, files):
    out.mkdir(parents=True, exist_ok=True)
    args = [str(FREE_PY), str(QUOTE_SLICE), str(out), f"filament={profile}",
            f"process={process}", f"support={support}"]
    if infill not in (None, ""):
        args.append(f"infill={infill}")
    args += [str(f) for f in files]
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=600, creationflags=NO_WINDOW, cwd=str(out))
    except subprocess.TimeoutExpired:
        raise QuoteError("Cắt lớp quá lâu (> 10 phút)")
    except OSError as e:
        raise QuoteError("Không chạy được Bambu Studio CLI: " + str(e))
    res = _last_json(r.stdout)
    if res is None:
        raise QuoteError("Cắt lớp lỗi: " + ((r.stderr or r.stdout or "")[-300:] or "không có kết quả"))
    if res.get("status") == "fail":
        raise QuoteError("Cắt lớp lỗi: " + ("; ".join(res.get("errors") or []) or "không rõ lỗi"))
    return res


def slice_model(files, material_name, options=None, token=None):
    """Cat lop file model theo profile nhua da chon; cache theo (token, profile, process, infill, support)."""
    options = options or {}
    files = [Path(f) for f in files]
    if not files:
        raise QuoteError("Chưa có file in")
    conn = connect()
    try:
        pricing = get_pricing(conn)
    finally:
        conn.close()
    mat = pricing["materials"].get(material_name)
    if not mat:
        raise QuoteError(f"Nhựa '{material_name}' chưa có trong bảng giá")
    opts = load_defaults().get("print_options") or {}
    profile = mat.get("slicer_profile") or default_profile(
        material_name, mat.get("type") or infer_type(material_name))
    if not profile:
        raise QuoteError(f"Nhựa '{material_name}' chưa có profile cắt lớp")
    process = str(options.get("process") or opts.get("process") or "0.20mm Standard @BBL A1")
    infill = options.get("infill")
    support = str(options.get("support") or opts.get("support") or "auto").lower()
    if support not in ("auto", "off"):
        support = "auto"
    key = (token or _files_key(files), profile, process, "" if infill in (None, "") else str(infill), support)
    if key in _slice_cache:
        return _slice_cache[key]
    digest = hashlib.sha1(repr(key).encode("utf-8")).hexdigest()[:16]
    out = work_dir() / "slices" / digest
    res = None
    qjson = out / "quote_slice.json"
    if qjson.exists():
        try:
            cached = json.loads(qjson.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cached = None
        if cached and _slice_ok(cached):
            res = cached
    if res is None:
        res = _run_slice(out, profile, process, infill, support, files)
    parsed = _slice_parsed(res)
    _slice_cache[key] = (res, parsed)
    return res, parsed


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


def model_key(name):
    """Stable key based only on the uploaded file name(s)."""
    suffixes = {".3mf", ".stl", ".obj", ".step", ".stp"}
    def one(value):
        name = Path(str(value or "").strip()).name
        ext = Path(name).suffix.lower()
        if ext in suffixes:
            name = name[:-len(Path(name).suffix)]
        if name.lower().endswith(".gcode"):
            name = name[:-6]
        return name.strip().lower()
    if isinstance(name, (list, tuple)):
        return "+".join(sorted(k for k in (one(v) for v in name) if k))
    return one(name)


def connect():
    p = _db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(p)
    c.row_factory = sqlite3.Row
    c.executescript(
        "CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT, updated_at TEXT);"
        "CREATE TABLE IF NOT EXISTS materials(name TEXT PRIMARY KEY, spool_price_vnd REAL,"
        " spool_weight_g REAL, updated_at TEXT, type TEXT, slicer_profile TEXT);"
        "CREATE TABLE IF NOT EXISTS extras(id INTEGER PRIMARY KEY, label TEXT, price_vnd REAL,"
        " active INTEGER);"
        "CREATE TABLE IF NOT EXISTS model_extras(model_key TEXT PRIMARY KEY, extras_json TEXT, updated_at TEXT);"
        "CREATE TABLE IF NOT EXISTS quotes(id INTEGER PRIMARY KEY, number TEXT UNIQUE, created_at TEXT,"
        " customer_name TEXT, customer_phone TEXT, title TEXT, note TEXT, total_vnd REAL, data_json TEXT);"
    )
    cols = {r["name"] for r in c.execute("PRAGMA table_info(materials)")}
    for col in ("type", "slicer_profile"):
        if col not in cols:
            c.execute(f"ALTER TABLE materials ADD COLUMN {col} TEXT")
    now = datetime.now().isoformat()
    defaults = load_defaults()
    for k, d in (defaults.get("settings") or {}).items():
        c.execute("INSERT OR IGNORE INTO settings VALUES(?,?,?)",
                  (k, json.dumps(d.get("value"), ensure_ascii=False), now))
    for name, m in (defaults.get("materials") or {}).items():
        t = m.get("type") or infer_type(name)
        c.execute("INSERT OR IGNORE INTO materials(name,spool_price_vnd,spool_weight_g,updated_at,type,"
                  "slicer_profile) VALUES(?,?,?,?,?,?)",
                  (name, float(m.get("spool_price_vnd") or 0), float(m.get("spool_weight_g") or 0), now,
                   t, m.get("slicer_profile") or default_profile(name, t)))
    for r in c.execute("select name, type, slicer_profile from materials"):
        if r["type"] and r["slicer_profile"]:
            continue
        t = r["type"] or infer_type(r["name"])
        sp = r["slicer_profile"] or default_profile(r["name"], t)
        c.execute("update materials set type=?, slicer_profile=? where name=?", (t, sp, r["name"]))
    for e in defaults.get("extras") or []:
        label = e.get("label") or ""
        if label and not c.execute("select 1 from extras where label=?", (label,)).fetchone():
            c.execute("insert into extras(label,price_vnd,active) values(?,?,1)",
                      (label, float(e.get("price_vnd") or 0)))
    c.commit()
    return c



def save_model_extras(conn, key, extras):
    if not key:
        return None
    active = {r["id"] for r in conn.execute("select id from extras where active=1")}
    clean = {}
    for k, v in (extras or {}).items():
        try:
            eid, count = int(k), int(v)
        except (TypeError, ValueError, OverflowError):
            continue
        if eid in active and count > 0:
            clean[str(eid)] = count
    updated = datetime.now().isoformat(timespec="seconds")
    payload = json.dumps(clean, ensure_ascii=False)
    conn.execute("insert into model_extras(model_key,extras_json,updated_at) values(?,?,?) "
                 "on conflict(model_key) do update set extras_json=excluded.extras_json, updated_at=excluded.updated_at",
                 (key, payload, updated))
    conn.commit()
    return {"extras": clean, "updated_at": updated}


def get_model_extras(conn, key):
    row = conn.execute("select extras_json,updated_at from model_extras where model_key=?", (key,)).fetchone()
    if row is None:
        return None
    try:
        stored = json.loads(row["extras_json"] or "{}")
    except (TypeError, ValueError):
        stored = {}
    active = {r["id"] for r in conn.execute("select id from extras where active=1")}
    clean = {}
    for k, v in stored.items():
        try:
            eid, count = int(k), int(v)
        except (TypeError, ValueError, OverflowError):
            continue
        if eid in active and count > 0:
            clean[str(eid)] = count
    return {"extras": clean, "updated_at": row["updated_at"]}


def reset_defaults(conn):
    """Ghi de thoi gia + nhua mac dinh; cap nhat phu kien mac dinh theo nhan (khong tao trung)."""
    defaults = load_defaults()
    now = datetime.now().isoformat()
    for k, d in (defaults.get("settings") or {}).items():
        conn.execute("insert into settings values(?,?,?) on conflict(key) do update set"
                     " value=excluded.value, updated_at=excluded.updated_at",
                     (k, json.dumps(d.get("value"), ensure_ascii=False), now))
    for name, m in (defaults.get("materials") or {}).items():
        t = m.get("type") or infer_type(name)
        conn.execute("insert into materials(name,spool_price_vnd,spool_weight_g,updated_at,type,slicer_profile)"
                     " values(?,?,?,?,?,?) on conflict(name) do update set"
                     " spool_price_vnd=excluded.spool_price_vnd, spool_weight_g=excluded.spool_weight_g,"
                     " updated_at=excluded.updated_at, type=excluded.type,"
                     " slicer_profile=excluded.slicer_profile",
                     (name, float(m.get("spool_price_vnd") or 0), float(m.get("spool_weight_g") or 0), now,
                      t, m.get("slicer_profile") or default_profile(name, t)))
    for e in defaults.get("extras") or []:
        label = e.get("label") or ""
        if not label:
            continue
        row = conn.execute("select id from extras where label=? order by id limit 1", (label,)).fetchone()
        if row is None:
            conn.execute("insert into extras(label,price_vnd,active) values(?,?,1)",
                         (label, float(e.get("price_vnd") or 0)))
        else:
            conn.execute("update extras set price_vnd=? where id=?",
                         (float(e.get("price_vnd") or 0), row["id"]))
    conn.commit()


def get_pricing(conn):
    settings = {r["key"]: _num(json.loads(r["value"])) for r in conn.execute("select * from settings")}
    mats = {r["name"]: {"spool_price_vnd": _num(r["spool_price_vnd"]),
                        "spool_weight_g": _num(r["spool_weight_g"]),
                        "type": r["type"] or "",
                        "slicer_profile": r["slicer_profile"] or ""}
            for r in conn.execute("select * from materials order by name")}
    extras = [{"id": r["id"], "label": r["label"], "price_vnd": _num(r["price_vnd"])}
              for r in conn.execute("select id,label,price_vnd from extras where active=1 order by id")]
    return {"settings": settings, "materials": mats, "extras": extras}


def save_settings(conn, data):
    allowed = set(SETTINGS_KEYS) | set(BULK_KEYS) | set(SHOP_KEYS)
    now = datetime.now().isoformat()
    for k, v in data.items():
        if k not in allowed:
            continue
        if v is None:
            conn.execute("delete from settings where key=?", (k,))
            continue
        conn.execute("insert into settings values(?,?,?) on conflict(key) do update set"
                     " value=excluded.value, updated_at=excluded.updated_at",
                     (k, json.dumps(v, ensure_ascii=False), now))
    conn.commit()


def save_material(conn, name, spool_price_vnd, spool_weight_g, type=None, slicer_profile=None):
    row = conn.execute("select type, slicer_profile from materials where name=?", (name,)).fetchone()
    t = type or (row["type"] if row else "") or infer_type(name)
    sp = slicer_profile or (row["slicer_profile"] if row else "") or default_profile(name, t)
    conn.execute("insert into materials(name,spool_price_vnd,spool_weight_g,updated_at,type,slicer_profile)"
                 " values(?,?,?,?,?,?) on conflict(name) do update set"
                 " spool_price_vnd=excluded.spool_price_vnd, spool_weight_g=excluded.spool_weight_g,"
                 " updated_at=excluded.updated_at, type=excluded.type, slicer_profile=excluded.slicer_profile",
                 (name, float(spool_price_vnd), float(spool_weight_g), datetime.now().isoformat(), t, sp))
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


def _merge_grams(grams, mapping):
    out = {}
    for t, g in (grams or {}).items():
        name = (mapping or {}).get(t) or t
        out[name] = out.get(name, 0.0) + g
    return out


def _resolve_materials(grams, mats, mapping):
    """Loai trong file khong co trong map -> nhua cung ten, khong thi nhua dau tien cung type."""
    out = {}
    for t in (grams or {}):
        if t in mapping:
            out[t] = mapping[t]
        elif t in mats:
            out[t] = t
        else:
            tt = infer_type(t)
            cand = next((n for n in sorted(mats)
                         if tt and (mats[n].get("type") or infer_type(n)) == tt), None)
            out[t] = cand or t
    return out


def _bulk_tiers(settings):
    """Cac bac si hop le (min_qty, discount_pct); bo bac thieu so hoac <= 0."""
    out = []
    for i in range(0, len(BULK_KEYS), 2):
        try:
            mn = float(settings[BULK_KEYS[i]])
            dc = float(settings[BULK_KEYS[i + 1]])
        except (KeyError, TypeError, ValueError):
            continue
        if mn <= 0 or dc <= 0:
            continue
        out.append((mn, dc))
    return out


def bulk_tier(settings, quantity):
    """Bac si ap dung: bac co min_qty lon nhat ma quantity >= min_qty; khong co -> None."""
    best = None
    for mn, dc in _bulk_tiers(settings or {}):
        if quantity >= mn and (best is None or mn > best[0]):
            best = (mn, dc)
    return best


def _next_bulk_tier(settings, quantity):
    """Bac ke tiep co min_qty > quantity (bac gan nhat); khong co -> None."""
    best = None
    for mn, dc in _bulk_tiers(settings or {}):
        if mn > quantity and (best is None or mn < best[0]):
            best = (mn, dc)
    return best


def compute(parsed, pricing, quantity=1, extras=None, other_fee_vnd=0, materials_map=None):
    s = pricing.get("settings", {})
    mats = pricing.get("materials", {})
    mapping = _resolve_materials(parsed.get("grams", {}), mats, materials_map or {})
    grams = _merge_grams(parsed.get("grams", {}), mapping)
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
    prices = {x["id"]: x["price_vnd"] for x in pricing.get("extras", [])}
    ex1 = sum(prices.get(int(i), 0) * int(v) for i, v in (extras or {}).items())
    method = s["pricing_method"]
    value = s["pricing_value"]

    def _bundle(qq):
        """Gia von + gia ban cho so luong qq (cong thuc cu, khong de quy)."""
        filament = sum(g * mats[t]["spool_price_vnd"] / mats[t]["spool_weight_g"]
                       for t, g in grams.items()) * qq
        electricity = s["printer_power_w"] / 1000 * h * s["electricity_price_vnd_per_kwh"] * qq
        depreciation = s["machine_price_vnd"] / s["machine_lifetime_hours"] * h * qq
        labor = s["labor_rate_vnd_per_hour"] * (s["setup_hours_per_job"] + s["post_hours_per_plate"] * n * qq)
        ex = ex1 * qq
        failure = s["failure_pct"] * (filament + electricity + depreciation)
        ln = {"filament": filament, "electricity": electricity, "depreciation": depreciation,
              "labor": labor, "extras": ex, "failure": failure}
        c = sum(ln.values())
        if method == "margin":
            if value >= 1:
                raise QuoteError("Giá theo biên (margin) phải có hệ số nhỏ hơn 1")
            p = c / (1 - value)
        else:
            p = c * (1 + value)
        return ln, c, p

    lines, cost, price = _bundle(q)
    price_1 = _bundle(1)[2]
    step = s["round_to_vnd"]
    tier = bulk_tier(s, q)
    disc = tier[1] if tier else 0
    price_q = price_1
    floor = cost / q
    raw = price_q * (1 - disc)
    bulk_floor = raw < floor
    if bulk_floor:
        raw = floor
    unit_price = math.ceil(raw / step - 1e-9) * step
    list_raw = max(price_1, floor)
    unit_price_list = math.ceil(list_raw / step - 1e-9) * step
    subtotal = unit_price * q
    nxt = _next_bulk_tier(s, q)
    next_bulk = None
    if nxt:
        nq = int(math.ceil(nxt[0])) or 1
        ncalc = compute(parsed, pricing, quantity=nq, extras=extras, other_fee_vnd=other_fee_vnd,
                        materials_map=materials_map)
        next_bulk = {"min_qty": _num(nxt[0]), "discount_pct": nxt[1],
                     "unit_price": ncalc["unit_price"]}
    return {"lines": lines, "cost": cost, "price": price, "unit_price": unit_price,
            "subtotal": subtotal, "other_fee": other_fee_vnd, "total": subtotal + other_fee_vnd,
            "quantity": q, "hours": h, "grams": parsed.get("grams", {}), "materials": grams,
            "materials_map": dict(mapping), "method": method, "value": value,
            "bulk_discount_pct": disc, "bulk_floor": bulk_floor, "unit_price_list": unit_price_list,
            "next_bulk": next_bulk}


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


def save_quote(conn, customer_name, customer_phone, title, parsed, calc, note, materials_map=None):
    now = datetime.now()
    number = _next_number(conn)
    pr = get_pricing(conn)
    mapping = materials_map or {}
    data = dict(calc)
    data["bulk_discount_pct"] = calc.get("bulk_discount_pct") or 0
    data["unit_price_list"] = calc.get("unit_price_list", calc.get("unit_price"))
    data["materials_map"] = dict(mapping)
    data["materials"] = calc.get("materials") or {}
    data["plates"] = [{"index": p["index"], "seconds": p["seconds"],
                       "grams": _merge_grams(p["grams"], mapping),
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
