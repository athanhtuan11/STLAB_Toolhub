from pathlib import Path

from flask import Blueprint, abort, jsonify, render_template, request, send_file, url_for

import launcher

from . import opener
from . import printprep
from . import workspace as ws

bp = Blueprint("hub", __name__)


@bp.app_context_processor
def nav():
    # Menu gon: viec hang ngay o ngoai, trang he thong gom vao "Them"
    main = [("hub.tong_quan", "Trang chính"), ("hub.du_an", "Dự án"), ("hub.thu_vien", "Linh kiện")]
    more = [("hub.ung_dung", "Ứng dụng & MCP"), ("hub.cong_dong", "Nguồn cộng đồng"), ("hub.skills", "Skills & agents"),
            ("hub.prompt", "Prompt library")]
    ep = request.endpoint or ""
    on = next((e for e, _ in main + more if ep == e or ep.startswith(e + "_")), None)
    return {"nav": main, "nav_more": more, "nav_on": on, "more_on": next((lb for e, lb in more if e == on), None)}


@bp.get("/thu-vien")
def thu_vien():
    return render_template("thu-vien.html", lib=ws.library())


# ---------- Trang ----------
@bp.get("/")
def tong_quan():
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
    return render_template("tong-quan.html", apps=apps, active=active, other=other)


@bp.get("/api/health")
def api_health():
    """Chi nhung dieu can chu y (rong = on) cho dong "Can chu y" o trang chinh."""
    issues = [(f"{a['name']} chưa cài trên máy", "hub.ung_dung") for a in launcher.load_config()["apps"]
              if not Path(a["exe"]).exists()]
    if n := sum(not p["ok"] for p in ws.pins()):
        issues.append((f"{n} repo cộng đồng lệch điểm ghim", "hub.cong_dong"))
    if n := sum(not x["ok"] for x in ws.links()):
        issues.append((f"{n} skill/agent liên kết lỗi", "hub.skills"))
    return jsonify([{"text": t, "url": url_for(ep)} for t, ep in issues])


@bp.get("/ung-dung")
def ung_dung():
    cfg = launcher.load_config()
    return render_template("ung-dung.html", apps=cfg["apps"], media=cfg["media_dir"],
                           mcp=list(launcher.mcp_servers()), layout=cfg.get("layout", {}),
                           desktop=launcher.desktop_status())


@bp.get("/cong-dong")
def cong_dong():
    return render_template("cong-dong.html", pins=ws.pins(), reports=ws.reports())


@bp.get("/cong-dong/bao-cao/<name>")
def cong_dong_bao_cao(name):
    text = ws.report(name)
    if text is None:
        abort(404)
    return render_template("bao-cao.html", name=name, text=text)


@bp.get("/skills")
def skills():
    rows = ws.links()
    groups = {}
    for r in rows:
        groups.setdefault(r["scope"], []).append(r)
    return render_template("skills.html", groups=groups, total=len(rows), ok=sum(r["ok"] for r in rows))


@bp.get("/du-an")
def du_an():
    ps = ws.projects()
    for p in ps:
        p["main_file"] = opener.primary(p["rel"])
    return render_template("du-an.html", projects=ps)


@bp.get("/du-an/<slug>")
def du_an_chi_tiet(slug):
    p = ws.project(slug)
    if p is None:
        abort(404)
    return render_template("du-an-chi-tiet.html", p=p, in3d=printprep.cau_hinh(p["rel"]) is not None,
                           files=opener.files(p["rel"]))


# ---------- Chuan bi in (maker/robotics-cad/scripts/prepare-print.py) ----------
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


@bp.get("/du-an/<slug>/print-image/<int:i>")
def du_an_anh_in(slug, i):
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


