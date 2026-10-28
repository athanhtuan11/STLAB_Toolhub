"""Pin diagram on a real board photo + project wiring diagram (WireViz).

photo_svg: draws tools/robotics-cad/library/<anh_chan.file> and a coloured
label per pin, using pinout.core primitives (Group/Rect/Text/Circle/Path/Image).
wiring_svg: builds a WireViz dict and renders it to inline SVG.

Only data from components.yaml is used; no dimensions are invented.
All colours are Toolhub CSS variables (no hex), see studio/design/DESIGN.md.
"""
import html
import json
import logging
import os
import re
import shutil
import threading
from pathlib import Path
from urllib.parse import quote

from pinout.core import Circle, Group, Image as SvgImage, Path as SvgPath, Rect, Text
from wireviz.wireviz import parse as wv_parse

from .pinout import LEVELS, ORDER

log = logging.getLogger(__name__)

STUDIO = Path(__file__).resolve().parent.parent
ROOT = STUDIO.parent
LIBRARY_DIR = ROOT / "tools" / "robotics-cad" / "library"
LIBRARY_YAML = LIBRARY_DIR / "components.yaml"
IMG_ROUTE = "/library/img/"
GRAPHVIZ_BIN = r"C:\Program Files\Graphviz\bin"

WIRE_COLORS = {"ac220": "BN", "5v": "RD", "3v3": "YE", "gnd": "BK", "tin-hieu": "GN"}
LEVEL_LABEL = {k: LEVELS[k][1] for k in LEVELS}

BOX_H = 36
TIER_GAP = 6
IMG_PAD = 14
M = 16
GUTTER_GAP = 12
BOTTOM_GAP = 22

_cache = {}
_lock = threading.Lock()


def _img_url(rel):
    return IMG_ROUTE + quote(str(rel).replace("\\", "/"), safe="/")


def _level(muc):
    return muc if muc in LEVELS else "tin-hieu"


def _esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def _pin_name(pin):
    name = str(pin.get("ten") or "").strip()
    if pin.get("xac_nhan") is False:
        name += "?"
    return name


def _norm_pins(component):
    pins = []
    for c in component.get("chan") or []:
        if not isinstance(c, dict):
            continue
        ten = str(c.get("ten") or "").strip()
        if not ten:
            continue
        try:
            x = float(c.get("x"))
            y = float(c.get("y"))
        except (TypeError, ValueError):
            log.warning("pin %s has no numeric x/y - skipped", ten)
            continue
        ben = str(c.get("ben") or "trai").strip()
        if ben not in ("trai", "phai", "tren", "duoi"):
            ben = "trai"
        pins.append({
            "ten": ten, "ben": ben, "muc": _level(str(c.get("muc") or "tin-hieu")),
            "mo_ta": str(c.get("mo_ta") or ""), "x": x, "y": y,
            "xac_nhan": c.get("xac_nhan"),
        })
    return pins


def _label(pin):
    name = _pin_name(pin)
    desc = pin.get("mo_ta") or ""
    if len(desc) > 46:
        desc = desc[:45] + "\u2026"
    width = max(len(name) * 7.2 + 16, len(desc) * 4.8 + 16)
    return name, desc, max(74.0, min(250.0, width))


def _text(value, x, y, cls):
    return Text(_esc(value), x=round(x, 1), y=round(y, 1), tag=cls)


def _rect(x, y, w, h, cls, radius=6):
    return Rect(x=round(x, 1), y=round(y, 1), width=round(w, 1), height=round(h, 1),
                corner_radius=radius, tag=cls)


def _circle(x, y, r, cls):
    return Circle(cx=round(x, 1), cy=round(y, 1), r=r, tag=cls)


def _path(d, cls):
    return SvgPath(d, tag=cls)


def _rows(items):
    """Assign pins to horizontal tiers (labels must not overlap); returns tier count."""
    tiers = []
    for item in sorted(items, key=lambda p: p["x"]):
        w = item["_w"]
        left, right = item["x"] - w / 2, item["x"] + w / 2
        for i, end in enumerate(tiers):
            if left >= end + 10:
                tiers[i] = right
                item["_tier"] = i
                break
        else:
            item["_tier"] = len(tiers)
            tiers.append(right)
    return len(tiers)


def _stack(items):
    """Stack labels vertically (left/right side), returns first/last y in image coords."""
    last = None
    for item in sorted(items, key=lambda p: p["y"]):
        top = item["y"] - BOX_H / 2
        if last is not None and top < last + TIER_GAP:
            top = last + TIER_GAP
        item["_top"] = top
        last = top + BOX_H
    return last


def _css():
    rules = [
        ".bg{fill:var(--card)}",
        ".frame{fill:var(--card);stroke:var(--line);stroke-width:1}",
        ".lb{stroke:var(--line);stroke-width:0}",
        ".dot{stroke:var(--card);stroke-width:1.5}",
        ".lead{fill:none;stroke-width:1.6;stroke-linecap:round;opacity:.9}",
        ".tname{font-family:var(--font-mono);font-size:11px;font-weight:600;"
        "fill:var(--on-accent)}",
        ".tdesc{font-family:var(--font-ui);font-size:8.5px;fill:var(--on-accent);"
        "opacity:.85}",
        ".legend{font-family:var(--font-ui);font-size:10px;fill:var(--text)}",
    ]
    for muc, (color, _label) in LEVELS.items():
        rules.append(".fl-%s{fill:%s}" % (muc, color))
        rules.append(".st-%s{stroke:%s}" % (muc, color))
    return "<style>" + "".join(rules) + "</style>"


def _photo_impl(component):
    info = component.get("anh_chan") or {}
    rel = str(info.get("file") or "").strip()
    if not rel:
        return ""
    try:
        img_w = float(info.get("w"))
        img_h = float(info.get("h"))
    except (TypeError, ValueError):
        log.warning("anh_chan without w/h - no diagram")
        return ""
    pins = _norm_pins(component)
    if not pins:
        return ""
    for pin in pins:
        pin["_name"], pin["_desc"], pin["_w"] = _label(pin)

    top = [p for p in pins if p["ben"] == "tren"]
    bottom = [p for p in pins if p["ben"] == "duoi"]
    left = [p for p in pins if p["ben"] == "trai"]
    right = [p for p in pins if p["ben"] == "phai"]

    n_top = _rows(top)
    n_bottom = _rows(bottom)
    _stack(left)
    _stack(right)

    left_w = max([p["_w"] for p in left], default=0)
    right_w = max([p["_w"] for p in right], default=0)
    left_gutter = max(M + 8, left_w + GUTTER_GAP * 2 + 4) if left else M
    right_gutter = max(M, right_w + GUTTER_GAP + 4) if right else M

    image_x = left_gutter
    image_y = M + (n_top * (BOX_H + TIER_GAP) + IMG_PAD if n_top else 0)
    image_bottom = image_y + img_h
    canvas_w = left_gutter + img_w + right_gutter

    bottom_top = image_bottom + IMG_PAD
    if n_bottom:
        bottom_end = bottom_top + n_bottom * (BOX_H + TIER_GAP)
    else:
        bottom_end = image_bottom
    legend_y = bottom_end + (BOTTOM_GAP if bottom_end > image_bottom else 0) + 18
    canvas_h = legend_y + M

    root = Group()
    root.add(_rect(0, 0, canvas_w, canvas_h, "bg", radius=10))
    root.add(_rect(image_x - 3, image_y - 3, img_w + 6, img_h + 6, "frame", radius=8))
    img_path = LIBRARY_DIR / rel
    if img_path.is_file():
        root.add(SvgImage(img_path.as_posix(), x=image_x, y=image_y,
                          width=img_w, height=img_h))
    else:
        log.warning("pin photo not found: %s", img_path)

    def box_x(px, w):
        return max(M, min(canvas_w - M - w, px - w / 2))

    for side, pins_side in (("tren", top), ("duoi", bottom)):
        for p in pins_side:
            w = p["_w"]
            bx = box_x(p["x"] + image_x, w)
            by = (M + p["_tier"] * (BOX_H + TIER_GAP)) if side == "tren" else \
                 (bottom_top + p["_tier"] * (BOX_H + TIER_GAP))
            px = image_x + p["x"]
            py = image_y + p["y"]
            edge = by + BOX_H if side == "tren" else by
            dy = "%.1f" % edge
            d = "M%.1f %.1f L%.1f %s L%.1f %s" % (px, py, px, dy, bx + w / 2, dy)
            root.add(_path(d, "lead st-%s" % p["muc"]))
            root.add(_circle(px, py, 4, "dot fl-%s" % p["muc"]))
            root.add(_rect(bx, by, w, BOX_H, "lb fl-%s" % p["muc"]))
            root.add(_text(p["_name"], bx + 8, by + 15, "tname"))
            if p["_desc"]:
                root.add(_text(p["_desc"], bx + 8, by + 28, "tdesc"))

    def place_side(pins_side, is_left):
        if not pins_side:
            return
        for p in pins_side:
            w = p["_w"]
            by = image_y + p["_top"]
            bx = (image_x - GUTTER_GAP - w) if is_left else (image_x + img_w + GUTTER_GAP)
            px = image_x + p["x"]
            py = image_y + p["y"]
            edge = bx + w if is_left else bx
            d = "M%.1f %.1f L%.1f %.1f" % (px, py, edge, py)
            root.add(_path(d, "lead st-%s" % p["muc"]))
            root.add(_circle(px, py, 4, "dot fl-%s" % p["muc"]))
            root.add(_rect(bx, by, w, BOX_H, "lb fl-%s" % p["muc"]))
            root.add(_text(p["_name"], bx + 8, by + 15, "tname"))
            if p["_desc"]:
                root.add(_text(p["_desc"], bx + 8, by + 28, "tdesc"))

    place_side(left, True)
    place_side(right, False)

    used = [m for m in ORDER if any(p["muc"] == m for p in pins)]
    lx = M
    for muc in used:
        root.add(_rect(lx, legend_y - 8, 9, 9, "fl-%s" % muc, radius=2))
        label = LEVEL_LABEL[muc]
        root.add(_text(label, lx + 14, legend_y, "legend"))
        lx += 14 + 9 + len(label) * 6 + 16

    title = str(component.get("ten") or "")
    url = _img_url(rel)
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="100%%" style="max-width:%dpx" viewBox="0 0 %d %d" role="img" aria-label="%s">'
        % (canvas_w, canvas_w, canvas_h, _esc("S\u01a1 \u0111\u1ed3 ch\u00e2n: " + title)),
        _css(),
        root.render(),
        "</svg>",
    ]
    svg = "".join(out)
    return re.sub(r'(xlink:href|href)="[^"]*"',
                  lambda m: '%s="%s"' % (m.group(1), url), svg)


def photo_svg(component):
    """SVG of the real board photo with a coloured label per pin ('' if no photo)."""
    if not (component or {}).get("anh_chan"):
        return ""
    info = component["anh_chan"]
    key = ("photo", component.get("id"), _mtime(LIBRARY_YAML),
           _mtime(LIBRARY_DIR / str(info.get("file") or "")))
    with _lock:
        if key in _cache:
            return _cache[key]
    try:
        svg = _photo_impl(component)
    except Exception:  # noqa: BLE001
        log.exception("photo_svg failed for %s", component.get("id"))
        svg = ""
    with _lock:
        _cache[key] = svg
    return svg


def _mtime(path):
    try:
        return Path(path).stat().st_mtime
    except OSError:
        return 0


def _ensure_dot():
    if shutil.which("dot"):
        return
    if Path(GRAPHVIZ_BIN, "dot.exe").exists() or Path(GRAPHVIZ_BIN, "dot").exists():
        os.environ["PATH"] = GRAPHVIZ_BIN + os.pathsep + os.environ.get("PATH", "")


def _wiring_dict(component, so_do):
    rows = []
    for r in (so_do or {}).get("noi") or []:
        if isinstance(r, (list, tuple)) and r and str(r[0] or "").strip():
            rows.append((str(r[0]).strip(), str(r[1]) if len(r) > 1 else "",
                         str(r[2]) if len(r) > 2 else ""))
    if not rows:
        return None

    chan = {str(c.get("ten") or "").strip(): c for c in component.get("chan") or []
            if isinstance(c, dict)}
    pins, missing = [], []
    for name, _dest, _note in rows:
        if name not in pins:
            pins.append(name)
        if name not in chan and name not in missing:
            missing.append(name)

    connectors = {}
    notes = "kh\u00f4ng c\u00f3 ch\u00e2n n\u00e0y: " + ", ".join(missing) if missing else None
    title = str(component.get("ten") or "")
    if len(title) > 48:
        title = title[:47] + "\u2026"
    conn = {"type": title or "Connector", "pins": pins}
    if notes:
        conn["notes"] = notes
    info = component.get("anh_chan") or {}
    src = LIBRARY_DIR / str(info.get("file") or "")
    if info.get("file") and src.is_file():
        conn["image"] = {"src": src.as_posix(), "width": 180}
    connectors["J1"] = conn

    cables, connections = {}, []
    for i, (name, dest, note) in enumerate(rows, 1):
        cpin = chan.get(name) or {}
        muc = _level(str(cpin.get("muc") or "tin-hieu"))
        cable = {"wirecount": 1, "color": WIRE_COLORS.get(muc, "GN")}
        if muc == "ac220":
            cable["wirelabels"] = ["220 VAC"]
        cables["W%d" % i] = cable
        dconn = {"style": "simple", "type": dest or "?", "pincount": 1}
        if note:
            dconn["notes"] = note
        connectors["D%d" % i] = dconn
        connections.append([{"J1": name}, {"W%d" % i: 1}, {"D%d" % i: 1}])

    return {"connectors": connectors, "cables": cables, "connections": connections}


def wiring_svg(component, so_do):
    """Inline SVG of one project wiring diagram ('' on error); cached."""
    so_key = json.dumps(so_do, ensure_ascii=False, sort_keys=True, default=str)
    info = component.get("anh_chan") or {}
    key = ("wiring", component.get("id"), _mtime(LIBRARY_YAML),
           _mtime(LIBRARY_DIR / str(info.get("file") or "")), so_key)
    with _lock:
        if key in _cache:
            return _cache[key]
    svg = ""
    try:
        data = _wiring_dict(component, so_do)
        if data:
            _ensure_dot()
            svg = wv_parse(data, return_types="svg")
            svg = _clean_wireviz(svg, component)
    except Exception:  # noqa: BLE001
        log.exception("wiring_svg failed for %s", component.get("id"))
        svg = ""
    with _lock:
        _cache[key] = svg
    return svg


def _clean_wireviz(svg, component):
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg or "")
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg, flags=re.I)
    info = component.get("anh_chan") or {}
    url = _img_url(info.get("file") or "")
    svg = re.sub(r'(xlink:href|href)="[^"]*"',
                 lambda m: '%s="%s"' % (m.group(1), url), svg)
    svg = re.sub(r'(<svg\b[^>]*?)\swidth="[^"]*"',
                 lambda m: m.group(1) + ' width="100%"', svg, count=1)
    svg = re.sub(r'(<svg\b[^>]*?)\sheight="[^"]*"',
                 lambda m: m.group(1), svg, count=1)
    return svg
