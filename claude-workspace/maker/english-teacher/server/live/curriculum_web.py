"""Trang /curriculum tren may chu Cu Bong: xem giao trinh Seed, xem giao an, GHIM bai cho 1 may toi khi bo ghim.
Co PIN (bien moi truong STLAB_CURRICULUM_PIN, doc luc xu ly yeu cau), cookie phien ky HMAC, chong CSRF bang Origin.
Khong goi mang, khong CDN. Noi vao bridge: setup(app, cur=, seed_dir=, devices=, active=)."""
import hashlib
import hmac
import html
import os
import re
import secrets
import time
from collections import deque
from pathlib import Path
from urllib.parse import urlparse

import yaml
from aiohttp import web
from markdown_it import MarkdownIt

UNIT_RE = re.compile(r"^s[1-3]-u(?:[1-9]|1[0-9])$")   # 2026-11-17: them chu de mo rong u9..u13
SESSION_S = 30 * 24 * 3600
FAIL_MAX, FAIL_WINDOW_S = 10, 600
COOKIE = "stlab_cur"
STATIC = Path(__file__).resolve().parent / "static"


def esc(t):
    return html.escape(str(t if t is not None else ""), quote=False)


def attr(t):
    return html.escape(str(t if t is not None else ""), quote=True)


def _md():
    return MarkdownIt("commonmark", {"html": False}).enable("table")


def _render_md(md, text):
    out = md.render(text)
    return re.sub(r'<a href="[^"]*">(.*?)</a>', r"\1", out, flags=re.S)   # lien ket tuong doi sang .md khong dung duoc tren web


def _dots(items):
    return " · ".join(esc(x) for x in (items or []))


def setup(app, *, cur, seed_dir, devices, active, log=None):
    seed_dir = Path(seed_dir)
    key = secrets.token_bytes(32)          # khoa phien: sinh luc khoi dong, khong luu (khoi dong lai = dang nhap lai)
    fails = deque()
    md = _md()
    _units = {}

    def say(msg):
        if log:
            log(msg)

    # ---------- noi dung ----------
    def load_units():
        if not _units:
            data = yaml.safe_load((seed_dir / "units.yaml").read_text(encoding="utf-8")) or {}
            levels, flat = [], {}
            for lv in data.get("levels", []):
                levels.append(lv)
                for n, u in enumerate(lv.get("units", []), 1):
                    flat[u["id"]] = (lv, u, n)
            _units["levels"], _units["flat"] = levels, flat
        return _units["levels"], _units["flat"]

    def plan_sections(unit_id):
        files = sorted((seed_dir / "lesson-plans").glob(unit_id + "-*.md"))
        if not files:
            return []
        txt = files[0].read_text(encoding="utf-8")
        parts = re.split(r"(?m)^## ", txt)[1:]
        out = []
        for p in parts:
            head, _, body = p.partition("\n")
            out.append((head.strip(), _render_md(md, body)))
        return out

    def lessons_of(unit_id):
        return [i for i in cur.order if i.startswith(unit_id + "-")]

    def title_of(lid):
        return cur.lessons.get(lid, {}).get("title") or lid

    def unit_label(lid):
        m = re.match(r"^(s\d)-u(\d)", lid or "")
        try:
            _, flat = load_units()
            if m and (m.group(1) + "-u" + m.group(2)) in flat:
                lv, u, _n = flat[m.group(1) + "-u" + m.group(2)]
                return "%s · U%s %s" % (lv.get("name", m.group(1)), m.group(2), u.get("theme", ""))
        except Exception:
            pass
        return title_of(lid)

    # ---------- phien + PIN ----------
    def pin_env():
        return os.environ.get("STLAB_CURRICULUM_PIN", "")

    def sign(exp):
        return hmac.new(key, str(exp).encode(), hashlib.sha256).hexdigest()

    def make_cookie():
        exp = int(time.time()) + SESSION_S
        return "%d.%s" % (exp, sign(exp))

    def logged_in(request):
        v = request.cookies.get(COOKIE, "")
        exp, _, sig = v.partition(".")
        if not exp.isdigit() or not sig:
            return False
        if not hmac.compare_digest(sig.encode(), sign(int(exp)).encode()):
            return False
        return int(exp) > time.time()

    def origin_ok(request):
        o = request.headers.get("Origin", "")
        if not o:
            return False
        try:
            return urlparse(o).netloc.lower() == (request.host or "").lower()
        except ValueError:
            return False

    def page(title, body, status=200, extra_head=""):
        doc = ("<!doctype html><html lang=\"vi\"><head><meta charset=\"utf-8\">"
               "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
               "<title>%s</title><link rel=\"stylesheet\" href=\"/curriculum/static/curriculum.css?v=20261117b\">%s</head><body>"
               "<main class=\"wrap\">%s</main><script src=\"/curriculum/static/curriculum.js?v=20261117b\" defer></script></body></html>"
               % (esc(title), extra_head, body))
        return web.Response(text=doc, status=status, content_type="text/html", charset="utf-8",
                            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                                     "Referrer-Policy": "same-origin"})

    def login_form(msg="", status=200):
        m = '<p class="err">%s</p>' % esc(msg) if msg else ""
        body = ('<header class="top"><b>🦉 Giáo trình Cú Bông</b></header>'
                '<form class="card" method="post" action="/curriculum/login">%s'
                '<label for="pin">Nhập mã PIN của người lớn</label>'
                '<input id="pin" name="pin" type="password" autocomplete="current-password" required>'
                '<button class="btn pri full" type="submit">Vào</button></form>' % m)
        return page("Giáo trình Cú Bông", body, status)

    def gate(request, post=False, api=False):
        """None = cho qua; ngược lại là Response loi."""
        if not pin_env():
            return web.Response(text="Trang giáo trình chưa bật", status=503, charset="utf-8")
        if post and not origin_ok(request):
            return web.Response(text="Origin không hợp lệ", status=403, charset="utf-8")
        if not logged_in(request):
            if api:
                return web.json_response({"ok": False, "error": "login"}, status=401)
            return login_form()
        return None

    # ---------- trang ----------
    def device_cards():
        out = []
        for mac, name in devices().items():
            info = cur.pin_info(mac)
            sess = active(mac)
            det = cur.detour_info(nickname=name, device=mac)
            lid = info["lesson_id"] if info else None
            if not lid:
                try:
                    L = cur._load()["learners"].get(name) or (cur._load().get("devices") or {}).get(mac) or {}
                    lid = L.get("lesson")
                except Exception:
                    lid = None
            st = ('<span class="pill on">● đang trong buổi học</span>' if sess is not None
                  else '<span class="pill off">tắt / chờ</span>')
            cls = "card dev"
            at = ""
            pinline = ""
            if info:
                at = str(info.get("at", ""))
                try:
                    a = at.replace("T", " ")
                    pinline = ('<div class="row"><span class="pill pin">📌 Ghim bởi người lớn</span>'
                               '<span class="muted small">từ %s/%s %s</span></div>' % (a[8:10], a[5:7], a[11:16]))
                except Exception:
                    pinline = '<div class="row"><span class="pill pin">📌 Ghim bởi người lớn</span></div>'
            if sess is not None and det:
                det_lid = det.get("lesson_id")
                cur_txt = 'Đang dạy: <b>%s</b> <span class="pill">🙋 bé xin</span>' % esc(unit_label(det_lid))
            elif info and info.get("session"):
                sess_n = info["session"]
                sp = cur.session_plan(lid, sess_n)
                title_short = ""
                if sp and sp[0]:
                    m_h = re.match(r"^Buổi\s*\d+\s*[–-]\s*(.+)", sp[0].strip())
                    title_short = m_h.group(1).strip() if m_h else sp[0].strip()
                sess_label = (" · Buổi %d – %s" % (sess_n, title_short)) if title_short else (" · Buổi %d" % sess_n)
                cur_txt = "Đang dạy: <b>%s%s</b>" % (esc(unit_label(lid)), esc(sess_label))
            elif lid:
                cur_txt = "Đang dạy: <b>%s</b>" % esc(unit_label(lid))
            else:
                cur_txt = "Chưa có bài hiện tại"
            btn = ('<button class="btn" type="button" data-unpin="%s">Bỏ ghim → về lộ trình</button>' % attr(mac)) if info else ""
            out.append('<div class="%s" data-device="%s"%s><h3>Máy “%s” <span class="muted small">·%s</span> %s</h3><div>%s</div>%s%s</div>'
                       % (cls, attr(mac), " data-pinned" if info else "", esc(name), esc(str(mac)[-5:]), st, cur_txt, pinline, btn))
        if not out:
            out.append('<div class="card muted">Chưa có máy Cú Bông nào kết nối.</div>')
        return "".join(out)

    def unit_state(unit_id, prog, pinned_ids, detour_ids=None):
        ls = lessons_of(unit_id)
        if detour_ids and any(l in detour_ids for l in ls):
            return "now", "🙋 bé đang học"
        if any(l in pinned_ids for l in ls):
            return "now", "📌 đang dạy"
        n = sum(prog.get(l, {}).get("taught", 0) for l in ls)
        m = sum(prog.get(l, {}).get("total", 0) for l in ls)
        if m and n >= m:
            return "done", "✓ đã học"
        if n:
            return "part", "%d/%d từ" % (n, m)
        return "none", "chưa học"

    def index_html():
        levels, _flat = load_units()
        devs = devices()
        first_nick = next(iter(devs.values()), None)
        prog = cur.progress(first_nick) if first_nick else {}
        pinned_ids = {(cur.pin_info(m) or {}).get("lesson_id") for m in devs}
        detour_ids = {cur.detour_info(nickname=name, device=mac).get("lesson_id")
                      for mac, name in devs.items()
                      if active(mac) is not None and cur.detour_info(nickname=name, device=mac)}
        tabs, panels = [], []
        for i, lv in enumerate(levels):
            lid = lv["id"]
            tabs.append('<button type="button" class="tab%s" data-level="%s">%s<br><span class="muted">%s</span></button>'
                        % (" on" if i == 0 else "", attr(lid), esc(lv.get("name", lid)), esc(lv.get("age", ""))))
            cards = []
            for n, u in enumerate(lv.get("units", []), 1):
                kind, label = unit_state(u["id"], prog, pinned_ids, detour_ids)
                cards.append('<a class="card unit %s" data-unit="%s" href="/curriculum/%s"><div class="num">%d</div>'
                             '<div class="grow"><h4>%s · %s</h4><div class="words">%s</div></div>'
                             '<span class="mark %s">%s</span></a>'
                             % ("unit-on" if kind == "now" else "", attr(u["id"]), attr(u["id"]), n, esc(u.get("theme", "")),
                                esc(u.get("theme_vi", "")), esc(", ".join(str(w) for w in u.get("core", []))), kind, esc(label)))
            panels.append('<section class="panel" data-panel="%s"%s>%s</section>'
                          % (attr(lid), "" if i == 0 else " hidden", "".join(cards)))
        body = ('<header class="top"><b>🦉 Giáo trình Cú Bông</b>'
                '<form method="post" action="/curriculum/logout"><button class="link" type="submit">Thoát</button></form></header>'
                '%s<div class="tabs">%s</div>%s' % (device_cards(), "".join(tabs), "".join(panels)))
        return page("Giáo trình Cú Bông", body)

    def unit_html(unit_id):
        _levels, flat = load_units()
        lv, u, n = flat[unit_id]
        total = len(lv.get("units", []))
        rows = [("Từ Core", _dots(u.get("core"))), ("Từ Plus", _dots(u.get("plus"))), ("Mẫu câu", _dots(u.get("patterns"))),
                ("Bài hát", esc(u.get("song", ""))), ("Make &amp; Tell", esc(u.get("make", "")) + " → " + esc(u.get("tell", ""))),
                ("Bé làm được", _dots(u.get("can_do")))]
        table = "".join("<tr><th>%s</th><td>%s</td></tr>" % (a, b) for a, b in rows)
        devs = devices()
        radios = []
        for i, (mac, name) in enumerate(devs.items()):
            st = " ·" + str(mac)[-5:] + (" · đang trong buổi học" if active(mac) is not None else "")
            radios.append('<label class="opt"><input type="radio" name="device" value="%s"%s><span>%s<span class="muted">%s</span></span></label>'
                          % (attr(mac), " checked" if len(devs) == 1 else "", esc(name), esc(st)))
        if not radios:
            radios.append('<div class="muted">Chưa có máy nào.</div>')
        sheet = ('<div class="sheet" id="pick" data-lesson="%s" hidden><b id="pick-title">Cú Bông dạy “%s”?</b>'
                 '<div class="muted">Chọn máy:</div>%s'
                 '<div class="card note">Máy đổi sang bài này <b>ngay</b> (đang học thì đổi giữa buổi) và các buổi sau vẫn dạy '
                 'bài này tới khi bấm <b>Bỏ ghim</b>. Từ đã dạy vẫn ghi vào tiến độ.</div>'
                 '<p class="err" id="pick-msg" hidden></p>'
                 '<button class="btn pri full" type="button" data-confirm>📌 Ghim bài</button>'
                 '<button class="btn full" type="button" data-cancel>Hủy</button></div>'
                 % (attr(unit_id), esc(u.get("theme", "")), "".join(radios)))
        sessions = plan_sections(unit_id)
        # 2026-11-17 Tuan: nut buoi phai hien trang thai ghim -> {so buoi | 0 = ca bai: [ten may]}
        unit_lessons = set(lessons_of(unit_id))
        pinned_here = {}
        for mac, name in devs.items():
            info = cur.pin_info(mac)
            if info and info.get("lesson_id") in unit_lessons:
                pinned_here.setdefault(int(info.get("session") or 0), []).append(str(name))
        details_list = []
        for h, b in sessions:
            m = re.match(r"^Buổi\s*(\d+)", h)
            btn_session = ""
            on = False
            if m:
                n_sess = m.group(1)
                who = pinned_here.get(int(n_sess))
                on = bool(who)
                if on:
                    btn_session = ('<div class="row"><span class="pill pin" data-pinned-session="%s">📌 Đang dạy buổi này · máy %s</span></div>'
                                   % (n_sess, esc(", ".join(who))))
                btn_session += (f'<button class="btn{" pri" if on else ""}" type="button" data-pin-session="{n_sess}">'
                                f'{"✅ Đang ghim – ghim lại cho máy khác" if on else "📌 Cú Bông dạy buổi này"}</button>')
            details_list.append(f'<details data-session{" open" if on else ""}><summary>{"📌 " if on else ""}{esc(h)}</summary>'
                                f'{btn_session}<div class="md">{b}</div></details>')
        unit_note = ('<div class="row"><span class="pill pin" data-pinned-session="0">📌 Đang ghim cả chủ đề · máy %s</span></div>'
                     % esc(", ".join(pinned_here[0]))) if pinned_here.get(0) else ""
        plan = unit_note + "".join(details_list)
        plan_card = '<div class="card"><b>Giáo án cho người dạy</b>%s</div>' % (plan or '<div class="muted">Chưa có giáo án.</div>')
        body = ('<header class="top"><a class="muted" href="/curriculum">← %s</a><span class="muted">U%d / %d</span></header>'
                '<h2>%s · %s</h2><div class="muted">%s · %s · %s buổi × %s phút</div>'
                '<button class="btn pri full big" type="button" data-pin="%s">🦉 Cú Bông dạy bài này</button>'
                '<div class="card"><table>%s</table></div>%s%s<div class="dim" id="dim" hidden></div>'
                % (esc(lv.get("name", "")), n, total, esc(u.get("theme", "")), esc(u.get("theme_vi", "")),
                   esc(lv.get("name", "")), esc(lv.get("age", "")), 8, 30, attr(unit_id), table, plan_card, sheet))
        return page("%s · Giáo trình Cú Bông" % u.get("theme", unit_id), body)

    # ---------- handler ----------
    async def h_index(request):
        g = gate(request)
        return g if g is not None else index_html()

    async def h_unit(request):
        g = gate(request)
        if g is not None:
            return g
        uid = request.match_info["unit"]
        _l, flat = load_units()
        if not UNIT_RE.match(uid) or uid not in flat:
            raise web.HTTPNotFound()
        return unit_html(uid)

    async def h_login(request):
        g_pin = pin_env()
        if not g_pin:
            return web.Response(text="Trang giáo trình chưa bật", status=503, charset="utf-8")
        if not origin_ok(request):
            return web.Response(text="Origin không hợp lệ", status=403, charset="utf-8")
        now = time.time()
        while fails and now - fails[0] > FAIL_WINDOW_S:
            fails.popleft()
        if len(fails) >= FAIL_MAX:
            return login_form("Nhập sai nhiều lần, thử lại sau ít phút.", 429)
        form = await request.post()
        given = str(form.get("pin", ""))
        if not hmac.compare_digest(given.encode(), g_pin.encode()):
            fails.append(now)
            return login_form("Sai mã PIN.", 401)
        secure = request.headers.get("X-Forwarded-Proto", "").lower() == "https"
        resp = web.HTTPSeeOther("/curriculum")
        resp.set_cookie(COOKIE, make_cookie(), max_age=SESSION_S, path="/curriculum", httponly=True,
                        samesite="Strict", secure=secure)
        raise resp

    async def h_logout(request):
        if not pin_env():
            return web.Response(text="Trang giáo trình chưa bật", status=503, charset="utf-8")
        if not origin_ok(request):
            return web.Response(text="Origin không hợp lệ", status=403, charset="utf-8")
        resp = web.HTTPSeeOther("/curriculum")
        resp.del_cookie(COOKIE, path="/curriculum")
        raise resp

    async def body_json(request):
        try:
            d = await request.json()
            return d if isinstance(d, dict) else {}
        except Exception:
            return {}

    async def h_pin(request):
        g = gate(request, post=True, api=True)
        if g is not None:
            return g
        d = await body_json(request)
        mac, lesson = str(d.get("device", "")), str(d.get("lesson", ""))
        devs = devices()
        if mac not in devs:
            return web.json_response({"ok": False, "error": "device"}, status=400)
        session = d.get("session")
        if "session" in d and session is not None and type(session) is not int:
            return web.json_response({"ok": False, "error": "session"}, status=400)
        try:
            lid = cur.pin(mac, lesson, session=session)
        except ValueError:
            if session is not None:
                try:
                    cur.resolve_lesson(lesson)
                    return web.json_response({"ok": False, "error": "session"}, status=400)
                except ValueError:
                    return web.json_response({"ok": False, "error": "lesson"}, status=400)
            return web.json_response({"ok": False, "error": "lesson"}, status=400)
        say("[CURRICULUM] ghim %s %s%s" % (mac, lid, " buoi %d" % session if session is not None else ""))
        pushed = False
        sess = active(mac)
        if sess is not None:
            try:
                res = cur.pinned_instructions(devs[mac], device=mac)
                if res:
                    await sess.send_lesson("[lesson] An adult picked a lesson on the web: %s. Switch to it now, warmly. %s"
                                           % (title_of(lid), res["instructions"]))
                    pushed = True
            except Exception as e:  # noqa: BLE001
                say("[CURRICULUM] day bai vao may loi %s" % type(e).__name__)
        resp = {"ok": True, "lesson_id": lid, "pushed": pushed}
        if session is not None:
            resp["session"] = session
        return web.json_response(resp)

    async def h_unpin(request):
        g = gate(request, post=True, api=True)
        if g is not None:
            return g
        d = await body_json(request)
        mac = str(d.get("device", ""))
        if mac not in devices():
            return web.json_response({"ok": False, "error": "device"}, status=400)
        cur.unpin(mac)
        say("[CURRICULUM] bo ghim %s" % mac)
        return web.json_response({"ok": True})

    app.router.add_get("/curriculum", h_index)
    app.router.add_post("/curriculum/login", h_login)
    app.router.add_post("/curriculum/logout", h_logout)
    app.router.add_post("/curriculum/api/pin", h_pin)
    app.router.add_post("/curriculum/api/unpin", h_unpin)
    app.router.add_static("/curriculum/static/", STATIC, follow_symlinks=False)
    app.router.add_get("/curriculum/{unit}", h_unit)
