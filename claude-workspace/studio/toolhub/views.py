import base64
import io
import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from flask import Blueprint, abort, jsonify, render_template, request, send_file, url_for

import launcher

from . import opener
from . import printprep
from . import quote as quote_lib
from . import usage
from . import workspace as ws

bp = Blueprint("hub", __name__)


@bp.app_context_processor
def nav():
    # Menu gon: viec hang ngay o ngoai, trang he thong gom vao "Them"
    main = [("hub.overview", "Trang chính"), ("hub.projects", "Dự án"), ("hub.library", "Linh kiện")]
    more = [("hub.apps", "Ứng dụng & MCP"), ("hub.quote", "Báo giá"), ("hub.community", "Nguồn cộng đồng"),
            ("hub.skills", "Skills & agents"), ("hub.prompt", "Prompt library")]
    ep = request.endpoint or ""
    on = next((e for e, _ in main + more if ep == e or ep.startswith(e + "_")), None)
    return {"nav": main, "nav_more": more, "nav_on": on, "more_on": next((lb for e, lb in more if e == on), None)}


@bp.get("/library")
def library():
    return render_template("library.html", lib=ws.library(), labels=ws.LABELS)


IMG_EXT = {".png", ".jpg", ".jpeg", ".svg", ".webp"}


@bp.get("/library/img/<path:rel>")
def library_img(rel):
    base = (ws.LIBRARY_DIR / "images").resolve()
    target = (ws.LIBRARY_DIR / rel).resolve()
    if target != base and base not in target.parents:
        abort(404)
    if target.suffix.lower() not in IMG_EXT or not target.is_file():
        abort(404)
    return send_file(target, max_age=0)


@bp.get("/library/<cid>")
def library_item(cid):
    c = ws.library_item(cid)
    if c is None:
        abort(404)
    return render_template("library-detail.html", c=c, labels=ws.LABELS)


# ---------- Trang ----------
@bp.get("/")
def overview():
    # Trang chinh phai hien ngay: trang thai app (den) va "Can chu y" (git 21 repo ~2 s) nap sau bang JS
    apps = [a for a in launcher.load_config()["apps"] if Path(a["exe"]).exists()]
    projects = ws.projects()
    active, other = [], []
    for p in projects:
        st = printprep.trang_thai(p["rel"])
        if st is None:
            other.append(p)
            continue
        kq = st["ket_qua"] or {}
        tt = [t["ket_luan"] for t in kq.get("tang", [])]
        p["print"] = {"chay": st["chay"], "luc": kq.get("thoi_gian"),
                      "ket_luan": "FAIL" if "FAIL" in tt else "WARN" if "WARN" in tt else "PASS" if tt else None,
                      "tom_tat": next((t["chi_tiet"] for t in kq.get("tang", []) if t["ten"].startswith("Tang 2")), "")}
        active.append(p)
    return render_template("overview.html", apps=apps, active=active, other=other)


@bp.get("/api/health")
def api_health():
    """Chi nhung dieu can chu y (rong = on) cho dong "Can chu y" o trang chinh."""
    issues = [(f"{a['name']} chưa cài trên máy", "hub.apps") for a in launcher.load_config()["apps"]
              if not Path(a["exe"]).exists()]
    if n := sum(not p["ok"] for p in ws.pins()):
        issues.append((f"{n} repo cộng đồng lệch điểm ghim", "hub.community"))
    if n := sum(not x["ok"] for x in ws.links()):
        issues.append((f"{n} skill/agent liên kết lỗi", "hub.skills"))
    return jsonify([{"text": t, "url": url_for(ep)} for t, ep in issues])


@bp.get("/api/org")
def api_org():
    """Nhan su AI, han muc va can chu y tu so nhan su + file local."""
    return jsonify(usage.org_board())


@bp.get("/api/usage")
def api_usage():
    """Han muc Claude/Codex/Gemini cho o "Han muc AI" o trang chinh (chi doc file tren may - toolhub/usage.py)."""
    return jsonify(usage.all_agents())


@bp.get("/apps")
def apps():
    cfg = launcher.load_config()
    return render_template("apps.html", apps=cfg["apps"], media=cfg["media_dir"],
                           mcp=list(launcher.mcp_servers()), layout=cfg.get("layout", {}),
                           desktop=launcher.desktop_status())


@bp.get("/community")
def community():
    return render_template("community.html", pins=ws.pins(), reports=ws.reports())


@bp.get("/community/report/<name>")
def community_report(name):
    text = ws.report(name)
    if text is None:
        abort(404)
    return render_template("report.html", name=name, text=text)


@bp.get("/skills")
def skills():
    rows = ws.links()
    groups = {}
    for r in rows:
        groups.setdefault(r["scope"], []).append(r)
    return render_template("skills.html", groups=groups, total=len(rows), ok=sum(r["ok"] for r in rows))


@bp.get("/projects")
def projects():
    ps = ws.projects()
    for p in ps:
        p["main_file"] = opener.primary(p["rel"])
    return render_template("projects.html", projects=ps)


@bp.get("/projects/<slug>")
def project_detail(slug):
    p = ws.project(slug)
    if p is None:
        abort(404)
    return render_template("project-detail.html", p=p, in3d=printprep.cau_hinh(p["rel"]) is not None,
                           files=opener.files(p["rel"]))


# ---------- Chuan bi in (tools/robotics-cad/scripts/prepare-print.py) ----------
def _rel(slug):
    p = ws.project(slug)
    if p is None or printprep.cau_hinh(p["rel"]) is None:
        abort(404)
    return p["rel"]


@bp.get("/api/print/<slug>")
def api_in(slug):
    return jsonify(printprep.trang_thai(_rel(slug)))


@bp.post("/api/print/<slug>/<kieu>/<lenh>")
def api_in_lenh(slug, kieu, lenh):
    rel = _rel(slug)
    if kieu not in printprep.KIEU or lenh not in ("on", "off"):
        abort(404)
    return jsonify(printprep.bat(rel, kieu) if lenh == "on" else printprep.tat(rel, kieu))


@bp.get("/projects/<slug>/print-image/<int:i>")
def project_print_image(slug, i):
    p = printprep.anh(_rel(slug), i)
    if p is None:
        abort(404)
    return send_file(p, max_age=0)


@bp.get("/prompt")
def prompt():
    return render_template("prompt.html", prompts=ws.prompts())


# ---------- API ----------
@bp.get("/api/status")
def api_status():
    return jsonify(launcher.status())


@bp.post("/api/start/<app_id>")
def api_start(app_id):
    try:
        return jsonify(launcher.start(app_id))
    except KeyError as e:
        return jsonify({"ok": False, "msg": str(e)}), 404


@bp.post("/api/mcp-check/<name>")
def api_mcp_check(name):
    if name not in launcher.mcp_servers():
        return jsonify({"ok": False, "msg": f"Không có MCP server '{name}'"}), 404
    return jsonify(launcher.mcp_check(name))


@bp.post("/api/claude")
def api_claude():
    return jsonify(launcher.open_claude())


@bp.post("/api/layout/<app_id>")
def api_layout(app_id):
    try:
        return jsonify(launcher.arrange(app_id))
    except KeyError as e:
        return jsonify({"ok": False, "msg": str(e)}), 404


@bp.post("/api/desktop-sync")
def api_desktop_sync():
    return jsonify(launcher.desktop_sync())


@bp.post("/api/community-check")
@bp.post("/api/community-check/<name>")
def api_community_check(name=None):
    return jsonify(ws.run_check(name))


@bp.post("/api/open/<slug>")
def api_open(slug):
    return jsonify(ws.open_in_vscode(slug))


@bp.post("/api/open-file/<slug>/<int:i>")
def api_open_file(slug, i):
    """Mo file thu i (theo opener.files) bang phan mem tao ra no - web khong gui duong dan."""
    p = ws.project(slug)
    if p is None:
        abort(404)
    return jsonify(opener.open_file(p["rel"], i))

# ---------- Bao gia in 3D (toolhub/quote.py) ----------
_parsed = {}
EDGE = [Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")]
FONT_DIR = Path(__file__).resolve().parent / "static" / "fonts"


@bp.app_template_filter("vnd")
def vnd(n):
    return quote_lib.fmt_vnd(n)


def _remember(parsed, name):
    token = base64.urlsafe_b64encode(os.urandom(12)).decode().rstrip("=")
    _parsed[token] = {"parsed": parsed, "name": name}
    while len(_parsed) > 20:
        _parsed.pop(next(iter(_parsed)))
    return token


def _item(data):
    item = _parsed.get(data.get("token") or "")
    if item is None:
        raise quote_lib.QuoteError("Chưa có file in. Hãy thả file .3mf đã cắt lớp trước.")
    return item


def _fee(v):
    v = float(v or 0)
    return int(v) if v.is_integer() else v


def _materials_map(data):
    mm = data.get("materials_map")
    if not isinstance(mm, dict):
        return None
    return {str(k): str(v) for k, v in mm.items() if k and v}


def _calc(data):
    item = _item(data)
    extras = {}
    for k, v in (data.get("extras") or {}).items():
        try:
            extras[int(k)] = int(v)
        except (TypeError, ValueError):
            continue
    conn = quote_lib.connect()
    try:
        pricing = quote_lib.get_pricing(conn)
    finally:
        conn.close()
    calc = quote_lib.compute(item["parsed"], pricing, quantity=int(data.get("quantity") or 1),
                             extras=extras, other_fee_vnd=_fee(data.get("other_fee_vnd")),
                             materials_map=_materials_map(data))
    calc["extras_detail"] = [{"id": eid, "count": int((data.get("extras") or {}).get(str(eid), 0))}
                             for eid in extras if int((data.get("extras") or {}).get(str(eid), 0))]
    return calc


def _vi(x, nd=2):
    s = f"{float(x):.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def _page(id):
    conn = quote_lib.connect()
    try:
        qd = quote_lib.get_quote(conn, id)
    finally:
        conn.close()
    if qd is None:
        abort(404)
    data = qd["data"]
    pricing = data.get("pricing") or {}
    settings = pricing.get("settings", {})
    created = datetime.fromisoformat(qd["created_at"])
    valid = created + timedelta(days=int(data.get("valid_days") or 7))
    labels = {e["id"]: e["label"] for e in pricing.get("extras", [])}
    extras_text = [f"{labels.get(e['id'], 'Phụ kiện #' + str(e['id']))} × {e['count']}"
                   for e in (data.get("extras_detail") or []) if e.get("count")]
    chosen = data.get("materials") or data.get("grams") or {}
    materials_text = " · ".join(f"{k} {_vi(v, 1)} g" for k, v in chosen.items())
    plates_text = " · ".join(
        f"Bàn {p['index']}: {_vi(p['seconds'] / 3600)} h, "
        + ", ".join(f"{k} {_vi(v, 1)} g" for k, v in (p.get("grams") or {}).items())
        for p in (data.get("plates") or []))
    return {"q": qd, "data": data, "settings": settings, "created": created, "valid_until": valid,
            "extras_text": extras_text, "materials_text": materials_text, "plates_text": plates_text}


def _font_css():
    rules = []
    for weight in (400, 600, 700):
        for sub in ("vietnamese", "latin"):
            f = FONT_DIR / f"be-vietnam-pro-{weight}-{sub}.woff2"
            if f.exists():
                rules.append("@font-face{font-family:'Be Vietnam Pro';font-style:normal;"
                             f"font-weight:{weight};src:url('{f.as_uri()}') format('woff2');}}")
    return "<style>" + "".join(rules) + "</style>"


@bp.get("/quote")
def quote():
    conn = quote_lib.connect()
    try:
        history = quote_lib.list_quotes(conn, 20)
        pricing = quote_lib.get_pricing(conn)
    finally:
        conn.close()
    for h in history:
        h["date_text"] = datetime.fromisoformat(h["created_at"]).strftime("%d/%m/%Y")
    projects = [f.relative_to(ws.ROOT).as_posix() for f in quote_lib.project_3mf_files()]
    pricing["sources"] = quote_lib.pricing_sources()
    return render_template("quote.html", history=history, projects=projects, pricing=pricing,
                           sources_json=json.dumps(pricing["sources"], ensure_ascii=False),
                           defaults_updated=quote_lib.defaults_updated())


def _pricing_with_sources(conn):
    pr = quote_lib.get_pricing(conn)
    pr["sources"] = quote_lib.pricing_sources()
    return pr


@bp.get("/api/quote/pricing")
def api_quote_pricing():
    conn = quote_lib.connect()
    try:
        return jsonify(_pricing_with_sources(conn))
    finally:
        conn.close()


@bp.post("/api/quote/pricing/reset")
def api_quote_pricing_reset():
    conn = quote_lib.connect()
    try:
        quote_lib.reset_defaults(conn)
        return jsonify(_pricing_with_sources(conn))
    finally:
        conn.close()


@bp.post("/api/quote/pricing")
def api_quote_pricing_save():
    data = request.get_json(silent=True) or {}
    conn = quote_lib.connect()
    try:
        if isinstance(data.get("settings"), dict):
            quote_lib.save_settings(conn, data["settings"])
        for name, v in (data.get("materials") or {}).items():
            if v is None:
                quote_lib.delete_material(conn, name)
            else:
                quote_lib.save_material(conn, name, v.get("spool_price_vnd") or 0,
                                        v.get("spool_weight_g") or 0)
        for e in data.get("extras") or []:
            if e.get("delete"):
                if e.get("id"):
                    quote_lib.delete_extra(conn, e["id"])
            else:
                quote_lib.save_extra(conn, e.get("label") or "", e.get("price_vnd") or 0,
                                     e.get("id") or None)
        return jsonify(_pricing_with_sources(conn))
    finally:
        conn.close()


@bp.post("/api/quote/parse")
def api_quote_parse():
    f = request.files.get("file")
    try:
        if f is not None and f.filename:
            parsed = quote_lib.read_3mf(f.stream)
            name = f.filename
        else:
            data = request.get_json(silent=True) or {}
            rel = (data.get("path") or "").replace("\\", "/")
            match = next((p for p in quote_lib.project_3mf_files()
                          if p.relative_to(ws.ROOT).as_posix() == rel), None)
            if match is None:
                abort(404)
            parsed = quote_lib.read_3mf(match)
            name = match.name
    except quote_lib.QuoteError as e:
        return jsonify({"error": str(e)}), 400
    token = _remember(parsed, name)
    plates = []
    for p in parsed["plates"]:
        img = p.get("image_png")
        plates.append({"index": p["index"], "seconds": p["seconds"], "grams": p["grams"],
                       "image": "data:image/png;base64," + base64.b64encode(img).decode() if img else None})
    return jsonify({"token": token, "name": name, "hours": parsed["hours"],
                    "grams": parsed["grams"], "plates": plates})


@bp.post("/api/quote/calc")
def api_quote_calc():
    try:
        calc = _calc(request.get_json(silent=True) or {})
    except quote_lib.QuoteError as e:
        return jsonify({"error": str(e)}), 400
    calc.update({k + "_text": quote_lib.fmt_vnd(calc[k])
                 for k in ("total", "unit_price", "cost", "subtotal")})
    return jsonify(calc)


@bp.post("/api/quote/save")
def api_quote_save():
    data = request.get_json(silent=True) or {}
    try:
        calc = _calc(data)
    except quote_lib.QuoteError as e:
        return jsonify({"error": str(e)}), 400
    item = _item(data)
    conn = quote_lib.connect()
    try:
        qid = quote_lib.save_quote(conn, data.get("customer_name") or "", data.get("customer_phone") or "",
                                   data.get("title") or "", item["parsed"], calc, data.get("note") or "",
                                   materials_map=_materials_map(data))
        qd = quote_lib.get_quote(conn, qid)
    finally:
        conn.close()
    return jsonify({"id": qid, "number": qd["number"]})


@bp.get("/quote/<int:id>")
def quote_print(id):
    return render_template("quote-print.html", **_page(id))


@bp.get("/quote/<int:id>/pdf")
def quote_pdf(id):
    ctx = _page(id)
    html = render_template("quote-print.html", **_ctx_pdf(ctx))
    edge = next((e for e in EDGE if e.exists()), None)
    if edge is None:
        abort(503)
    with tempfile.TemporaryDirectory(prefix="stlab-quote-") as td:
        hp = Path(td) / "quote.html"
        hp.write_text(html, encoding="utf-8")
        out = Path(td) / "quote.pdf"
        subprocess.run([str(edge), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={Path(td) / 'edge'}", f"--print-to-pdf={out}", hp.as_uri()],
                       check=True, capture_output=True, timeout=180)
        pdf = out.read_bytes()
    return send_file(io.BytesIO(pdf), mimetype="application/pdf",
                     download_name=f"{ctx['q']['number']}.pdf")


def _ctx_pdf(ctx):
    return {**ctx, "font_css": _font_css()}


@bp.get("/api/quote/projects")
def api_quote_projects():
    return jsonify([f.relative_to(ws.ROOT).as_posix() for f in quote_lib.project_3mf_files()])
