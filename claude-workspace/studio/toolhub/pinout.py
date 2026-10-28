"""Sinh so do chan (SVG) cho linh kien robotics tu du lieu components.yaml.

Chi dung thu vien chuan. Moi chu lay tu YAML deu duoc html.escape; mau chi bang
bien CSS var(--...) cua Toolhub (khong hex), theo DESIGN.md.
"""
import html

# muc -> (mau CSS, nhan chu thich)
LEVELS = {
    "ac220": ("var(--err)", "220 VAC \u2013 nguy hi\u1ec3m"),
    "5v": ("var(--warn)", "5 V"),
    "3v3": ("var(--accent)", "3,3 V"),
    "gnd": ("var(--muted)", "GND"),
    "tin-hieu": ("var(--text)", "t\u00edn hi\u1ec7u"),
}
ORDER = ["ac220", "5v", "3v3", "gnd", "tin-hieu"]

M = 12
ROW = 28
PIN_H = 24
PIN_W = 150
COMP_W = 150
FIN = 6
LINE = 24
LBL_W = 180
HEAD = 30
LEG_H = 26
BOX_TITLE = 30


def _e(value):
    return html.escape("" if value is None else str(value), quote=True)


def _cut(value, n=28):
    s = "" if value is None else str(value)
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def _txt(x, y, value, fill="var(--text)", size=11, anchor="start",
         weight=None, mono=False, opacity=None, cut=28):
    style = "fill:%s;font-family:var(--font-%s);font-size:%spx" % (
        fill, "mono" if mono else "ui", size)
    if weight:
        style += ";font-weight:%s" % weight
    if opacity is not None:
        style += ";opacity:%s" % opacity
    ta = ' text-anchor="%s"' % anchor if anchor != "start" else ""
    return ('<g><title>%s</title><text x="%.1f" y="%.1f" style="%s"%s>%s</text></g>'
            % (_e(value), x, y, style, ta, _e(_cut(value, cut))))


def _norm(chan):
    pins = []
    for c in chan or []:
        if not isinstance(c, dict):
            continue
        ten = str(c.get("ten") or "").strip()
        if not ten:
            continue
        ben = "phai" if str(c.get("ben") or "trai").strip() == "phai" else "trai"
        muc = str(c.get("muc") or "tin-hieu").strip()
        if muc not in LEVELS:
            muc = "tin-hieu"
        pins.append({"ten": ten, "ben": ben, "muc": muc,
                     "mo_ta": str(c.get("mo_ta") or "")})
    return pins


def render_svg(ten, chan, so_do=None):
    """Tra ve chuoi SVG (XML hop le) hoac "" khi khong co chan."""
    pins = _norm(chan)
    if not pins:
        return ""
    ten = "" if ten is None else str(ten)

    left = [p for p in pins if p["ben"] == "trai"]
    right = [p for p in pins if p["ben"] == "phai"]

    rows = []
    if isinstance(so_do, dict):
        for r in so_do.get("noi") or []:
            if isinstance(r, (list, tuple)) and r:
                name = str(r[0] or "").strip()
                if name:
                    rows.append((name,
                                 str(r[1]) if len(r) > 1 else "",
                                 str(r[2]) if len(r) > 2 else ""))
    has_diagram = bool(rows)

    referenced = {name for name, _d, _n in rows}
    missing = []
    for name, _d, _n in rows:
        if (not any(p["ten"] == name for p in pins)
                and not any(m["ten"] == name for m in missing)):
            missing.append({"ten": name, "ben": "trai", "muc": "tin-hieu",
                            "mo_ta": "", "missing": True})
    left = left + missing
    nrows = max(len(left), len(right), 1)

    head_h = HEAD if has_diagram else 0
    box_top = M + head_h
    box_h = BOX_TITLE + nrows * ROW + 8

    if has_diagram:
        left_x = M + LBL_W + FIN + LINE
        box_x = left_x + PIN_W
        width = box_x + COMP_W + PIN_W + FIN + LINE + LBL_W + M
    else:
        left_x = M
        box_x = M + PIN_W
        width = box_x + COMP_W + PIN_W + M
    height = box_top + box_h + LEG_H + M

    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="100%%" style="max-width:%dpx" viewBox="0 0 %d %d" '
           'role="img" aria-label="%s">'
           % (width, width, height, _e("S\u01a1 \u0111\u1ed3 ch\u00e2n: " + ten))]

    if has_diagram:
        du_an = str(so_do.get("du_an") or "")
        tieu_de = str(so_do.get("tieu_de") or "")
        head = (du_an + ": " + tieu_de) if du_an else tieu_de
        if head:
            out.append(_txt(M, M + 17, head, size=12, weight="600", cut=120))

    out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" '
               'style="fill:var(--card);stroke:var(--line)"/>'
               % (box_x, box_top, COMP_W, box_h))
    out.append(_txt(box_x + COMP_W / 2, box_top + 20, ten,
                    size=12, anchor="middle", weight="700", cut=20))

    sides = ((left, left_x, True), (right, box_x + COMP_W, False))
    pos = {}
    for side, sx, is_left in sides:
        for i, p in enumerate(side):
            cy = box_top + BOX_TITLE + i * ROW + ROW / 2
            pos[p["ten"]] = (p, sx, cy)
            is_missing = bool(p.get("missing"))
            faded = has_diagram and p["ten"] not in referenced
            color = LEVELS[p["muc"]][0]
            if is_missing:
                rect_style = ("fill:var(--card);stroke:var(--err);"
                              "stroke-width:1.5;stroke-dasharray:5 3")
            else:
                rect_style = "fill:var(--card);stroke:var(--line)"
            out.append('<g%s>' % (' opacity="0.45"' if faded else ""))
            out.append('<rect x="%d" y="%.1f" width="%d" height="%d" rx="5" '
                       'style="%s"/>' % (sx, cy - PIN_H / 2, PIN_W, PIN_H, rect_style))
            stripe_x = sx + PIN_W - 4 if is_left else sx
            out.append('<rect x="%d" y="%.1f" width="4" height="%d" rx="2" '
                       'style="fill:%s"/>' % (stripe_x, cy - PIN_H / 2, PIN_H, color))
            out.append(_txt(sx + 8, cy - 1, p["ten"], fill=color, size=11,
                            mono=True, weight="600"))
            if p.get("mo_ta") or is_missing:
                mo_ta = p.get("mo_ta") or "kh\u00f4ng c\u00f3 ch\u00e2n n\u00e0y"
                out.append(_txt(sx + 8, cy + 10, mo_ta,
                                fill="var(--err)" if is_missing else "var(--muted)",
                                size=9))
            out.append('</g>')

    if has_diagram:
        for name, dest, note in rows:
            p, sx, cy = pos[name]
            is_missing = bool(p.get("missing"))
            color = "var(--err)" if is_missing else LEVELS[p["muc"]][0]
            if p["ben"] == "trai":
                x1 = sx
                x2 = M + LBL_W + FIN
                tx = M + LBL_W
                anchor = "end"
            else:
                x1 = sx + PIN_W
                x2 = x1 + FIN + LINE
                tx = x2
                anchor = "start"
            dash = ' stroke-dasharray="4 3"' if is_missing else ""
            out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" '
                       'style="stroke:%s;stroke-width:1.5"%s/>'
                       % (x1, cy, x2, cy, color, dash))
            out.append(_txt(tx, cy - 1, dest, size=10, anchor=anchor))
            if note:
                out.append(_txt(tx, cy + 10, note, fill="var(--muted)", size=9,
                                anchor=anchor))

    legend_y = box_top + box_h + 17
    lx = M
    for muc in ORDER:
        if not any(p["muc"] == muc for p in pins):
            continue
        color, label = LEVELS[muc]
        out.append('<rect x="%d" y="%.1f" width="9" height="9" rx="2" '
                   'style="fill:%s"/>' % (lx, legend_y - 8, color))
        out.append(_txt(lx + 14, legend_y, label, size=10))
        lx += 14 + 9 + len(label) * 6 + 16

    out.append("</svg>")
    return "".join(out)
