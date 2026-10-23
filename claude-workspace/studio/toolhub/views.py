from flask import Blueprint, abort, jsonify, render_template, request, send_file

import launcher

from . import chuanbiin
from . import photolab
from . import workspace as ws

bp = Blueprint("hub", __name__)


@bp.app_context_processor
def nav():
    return {"nav": [
        ("hub.tong_quan", "Tổng quan"), ("hub.ung_dung", "Ứng dụng & MCP"),
        ("hub.cong_dong", "Nguồn cộng đồng"), ("hub.skills", "Skills & agents"),
        ("hub.du_an", "Dự án"), ("hub.anh", "Sửa ảnh"), ("hub.thu_vien", "Thư viện linh kiện"), ("hub.prompt", "Prompt library"),
    ]}


@bp.get("/thu-vien")
def thu_vien():
    return render_template("thu-vien.html", lib=ws.library())


# ---------- Trang ----------
@bp.get("/")
def tong_quan():
    apps, pins, links, projects = launcher.status(), ws.pins(), ws.links(), ws.projects()
    reps = ws.reports()
    stats = {
        "apps": (sum(a["listening"] for a in apps), len(apps)),
        "pins": (sum(p["ok"] for p in pins), len(pins)),
        "links": (sum(x["ok"] for x in links), len(links)),
        "projects": len(projects),
        "todo": sum(p["todo"] for p in projects),
        "report": reps[0].removesuffix(".md") if reps else "chưa có",
    }
    return render_template("tong-quan.html", stats=stats, apps=apps, projects=projects)


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
    return render_template("du-an.html", projects=ws.projects())


@bp.get("/du-an/<slug>")
def du_an_chi_tiet(slug):
    p = ws.project(slug)
    if p is None:
        abort(404)
    return render_template("du-an-chi-tiet.html", p=p, in3d=chuanbiin.cau_hinh(p["rel"]) is not None)


# ---------- Chuan bi in (maker/robotics-cad/scripts/chuan-bi-in.py) ----------
def _rel(slug):
    p = ws.project(slug)
    if p is None or chuanbiin.cau_hinh(p["rel"]) is None:
        abort(404)
    return p["rel"]


@bp.get("/api/in/<slug>")
def api_in(slug):
    return jsonify(chuanbiin.trang_thai(_rel(slug)))


@bp.post("/api/in/<slug>/<kieu>/<lenh>")
def api_in_lenh(slug, kieu, lenh):
    rel = _rel(slug)
    if kieu not in chuanbiin.KIEU or lenh not in ("bat", "tat"):
        abort(404)
    return jsonify(chuanbiin.bat(rel, kieu) if lenh == "bat" else chuanbiin.tat(rel, kieu))


@bp.get("/du-an/<slug>/anh-in/<int:i>")
def du_an_anh_in(slug, i):
    p = chuanbiin.anh(_rel(slug), i)
    if p is None:
        abort(404)
    return send_file(p, max_age=0)


@bp.get("/anh")
def anh():
    return render_template("anh.html", src=request.args.get("src") or photolab.last_src())


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


# ---------- Sua anh (photo-ai) ----------
def _lab(fn, *args):
    try:
        return jsonify(fn(*args))
    except ValueError as e:
        return jsonify({"ok": False, "msg": str(e)}), 400


@bp.get("/api/anh/looks")
def api_anh_looks():
    return _lab(photolab.looks)


@bp.post("/api/anh/photos")
def api_anh_photos():
    return _lab(photolab.photos, (request.get_json(silent=True) or {}).get("src", ""))


@bp.post("/api/anh/preview")
def api_anh_preview():
    d = request.get_json(silent=True) or {}
    return _lab(photolab.preview, d.get("src", ""), str(d.get("photo", "")), str(d.get("look", "")),
                bool(d.get("local")))


@bp.post("/api/anh/apply")
def api_anh_apply():
    d = request.get_json(silent=True) or {}
    return _lab(photolab.apply, d.get("src", ""), str(d.get("look", "")), d.get("strength", 1), bool(d.get("local")))


@bp.get("/api/anh/job")
def api_anh_job():
    return jsonify(photolab.job())


@bp.post("/api/anh/open-output")
def api_anh_open_output():
    return jsonify(photolab.open_output())


@bp.get("/anh/file")
def anh_file():
    p = photolab.file_path(request.args.get("src", ""), request.args.get("p", ""))
    if p is None:
        abort(404)
    return send_file(p, max_age=0)
