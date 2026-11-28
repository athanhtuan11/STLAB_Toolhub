"""Wiring diagram: load YAML + render SVG (WireViz). Chi doc file YAML, khong sua."""
import os
import re
import shutil
import threading
from pathlib import Path

import yaml
from wireviz.wireviz import parse as wv_parse

VALID_LEVELS = {"5v", "3v3", "gnd", "tin-hieu", "loa"}
VALID_COLORS = {"RD", "OG", "BK", "YE", "GN", "BU", "VT", "TQ", "WH", "PK", "GY", "BN"}
COLOR_VN = {
    "RD": "\u0111\u1ecf", "OG": "cam", "BK": "\u0111en", "YE": "v\u00e0ng",
    "GN": "xanh l\u00e1", "BU": "xanh d\u01b0\u01a1ng", "VT": "t\u00edm",
    "TQ": "xanh ng\u1ecdc", "WH": "tr\u1eafng", "PK": "h\u1ed3ng",
    "GY": "x\u00e1m", "BN": "n\u00e2u",
}
# WireViz color hex for inline style (not in style.css)
COLOR_HEX = {
    "RD": "#e53935", "OG": "#fb8c00", "BK": "#212121", "YE": "#fdd835",
    "GN": "#43a047", "BU": "#1e88e5", "VT": "#8e24aa", "TQ": "#00acc1",
    "WH": "#f5f5f5", "PK": "#e91e63", "GY": "#757575", "BN": "#6d4c41",
}

GRAPHVIZ_BIN = r"C:\Program Files\Graphviz\bin"
_cache: dict = {}
_lock = threading.Lock()


def _ensure_dot():
    if shutil.which("dot"):
        return
    if Path(GRAPHVIZ_BIN, "dot.exe").exists() or Path(GRAPHVIZ_BIN, "dot").exists():
        os.environ["PATH"] = GRAPHVIZ_BIN + os.pathsep + os.environ.get("PATH", "")


def _mtime(path):
    try:
        return Path(path).stat().st_mtime
    except OSError:
        return 0


def _split_part_pin(s):
    """Split 'part.pin' on FIRST dot only."""
    s = str(s)
    idx = s.find(".")
    if idx < 0:
        raise ValueError(f"Thieu dau cham trong '{s}' (can dang 'part.pin')")
    return s[:idx], s[idx + 1:]


def load(path) -> dict:
    """Load wiring YAML, validate, return dict {title, groups, parts, wires, notes}."""
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    title = data.get("title", "")
    groups = data.get("groups", {})
    parts = data.get("parts", {})
    raw_wires = data.get("wires", [])
    notes = data.get("notes", [])

    # Validate parts exist and have correct structure
    for part_id, part_info in parts.items():
        pins = part_info.get("pins", [])
        if not isinstance(pins, list):
            raise ValueError(f"Part '{part_id}': pins phai la danh sach")

    wires = []
    for i, w in enumerate(raw_wires):
        raw_from = str(w.get("from", ""))
        raw_to = str(w.get("to", ""))

        # Split part.pin on first dot
        from_part, from_pin = _split_part_pin(raw_from)
        to_part, to_pin = _split_part_pin(raw_to)

        # Validate parts
        if from_part not in parts:
            raise ValueError(f"Day {i + 1}: part '{from_part}' khong co trong phan parts")
        if to_part not in parts:
            raise ValueError(f"Day {i + 1}: part '{to_part}' khong co trong phan parts")

        # Validate pins
        from_pins = parts[from_part].get("pins", [])
        if from_pin not in from_pins:
            raise ValueError(f"Day {i + 1}: chan '{from_pin}' khong co trong part '{from_part}' (co: {from_pins})")
        to_pins = parts[to_part].get("pins", [])
        if to_pin not in to_pins:
            raise ValueError(f"Day {i + 1}: chan '{to_pin}' khong co trong part '{to_part}' (co: {to_pins})")

        # Validate level
        level = str(w.get("level", ""))
        if level not in VALID_LEVELS:
            raise ValueError(f"Day {i + 1}: level '{level}' khong hop le (phai la {VALID_LEVELS})")

        # Validate color
        color = str(w.get("color", ""))
        if color not in VALID_COLORS:
            raise ValueError(f"Day {i + 1}: mau '{color}' khong hop le (phai la {VALID_COLORS})")

        # Validate group
        group = str(w.get("group", ""))
        if group not in groups:
            raise ValueError(f"Day {i + 1}: nhom '{group}' khong co trong phan groups (co: {list(groups.keys())})")

        from_label = parts[from_part].get("label", from_part)
        to_label = parts[to_part].get("label", to_part)
        group_label = groups.get(group, group)
        note = str(w.get("note", "")) if w.get("note") is not None else ""

        wires.append({
            "from_part": from_part,
            "from_pin": from_pin,
            "to_part": to_part,
            "to_pin": to_pin,
            "from_label": from_label,
            "to_label": to_label,
            "level": level,
            "color": color,
            "color_name": COLOR_VN[color],
            "group": group,
            "group_label": group_label,
            "note": note,
        })

    return {
        "title": title,
        "groups": groups,
        "parts": parts,
        "wires": wires,
        "notes": notes,
    }


def _pin(name):
    """Ten chan cho WireViz; ten toan chu so ("1") WireViz hieu la so thu tu -> "#1"."""
    name = str(name)
    return "#" + name if name.isdigit() else name


def _build_wv_dict(wdata, group=None):
    """Build WireViz input dict from wiring data, optionally filtered by group."""
    parts = wdata["parts"]
    groups = wdata["groups"]
    wires = wdata["wires"]

    # Validate group filter
    if group is not None and group not in groups:
        raise ValueError(f"Nhom '{group}' khong co trong file (co: {list(groups.keys())})")

    # Filter wires by group
    if group is not None:
        active_wires = [w for w in wires if w["group"] == group]
    else:
        active_wires = wires

    if not active_wires:
        return None

    # Collect parts that actually appear in active wires
    used_parts = set()
    for w in active_wires:
        used_parts.add(w["from_part"])
        used_parts.add(w["to_part"])

    # Build connectors: each part as a connector with its pins IN YAML ORDER
    # Only include pins that are connected in active wires
    connectors = {}
    for part_id in parts:
        if part_id not in used_parts:
            continue
        part_info = parts[part_id]
        all_pins = part_info.get("pins", [])
        # Only include pins used in active wires
        used_pins_in_part = set()
        for w in active_wires:
            if w["from_part"] == part_id:
                used_pins_in_part.add(w["from_pin"])
            if w["to_part"] == part_id:
                used_pins_in_part.add(w["to_pin"])
        # Keep original order from YAML
        filtered_pins = [p for p in all_pins if p in used_pins_in_part]
        if not filtered_pins:
            continue
        connectors[part_id] = {
            "type": part_info.get("label", part_id),
            # 2026-11-28: chan = TEN chan (khong danh so 1..N theo nhom: "esp:5" bi doc nham thanh GPIO5)
            "pins": [_pin(p) for p in filtered_pins],
        }

    # Build cables and connections
    cables = {}
    connections = []
    for i, w in enumerate(active_wires, 1):
        cable_id = f"W{i}"
        cables[cable_id] = {
            "wirecount": 1,
            "color": w["color"],
        }
        connections.append([
            {w["from_part"]: _pin(w["from_pin"])},
            {cable_id: 1},
            {w["to_part"]: _pin(w["to_pin"])},
        ])

    return {
        "connectors": connectors,
        "cables": cables,
        "connections": connections,
    }


def _clean_svg(svg_text):
    """Strip <?xml/DOCTYPE, set width=100%, remove height attr."""
    svg_text = re.sub(r"<\?xml[^>]*\?>\s*", "", svg_text or "")
    svg_text = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg_text, flags=re.I)
    svg_text = re.sub(r"<!--.*?-->\s*", "", svg_text, flags=re.S)
    svg_text = svg_text.replace("&#45;", "-")
    i = svg_text.find("<svg")
    if i > 0:
        svg_text = svg_text[i:]
    svg_text = re.sub(
        r'(<svg\b[^>]*?)\swidth="[^"]*"',
        lambda m: m.group(1) + ' width="100%"',
        svg_text, count=1,
    )
    svg_text = re.sub(
        r'(<svg\b[^>]*?)\sheight="[^"]*"',
        lambda m: m.group(1),
        svg_text, count=1,
    )
    return svg_text


def svg(path, group=None) -> str:
    """Render wiring SVG (inline, no <?xml/DOCTYPE). Cached by (path, mtime, group)."""
    path = Path(path)
    mt = _mtime(path)
    cache_key = (str(path), mt, group)

    with _lock:
        if cache_key in _cache:
            return _cache[cache_key]

    # Load and validate (raises ValueError on bad data/group)
    wdata = load(path)

    # Validate group now (load() doesn't get group param)
    if group is not None and group not in wdata["groups"]:
        raise ValueError(f"Nhom '{group}' khong co trong file (co: {list(wdata['groups'].keys())})")

    result = ""
    try:
        wv_dict = _build_wv_dict(wdata, group=group)
        if wv_dict:
            _ensure_dot()
            raw = wv_parse(wv_dict, return_types="svg")
            result = _clean_svg(raw)
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001
        import logging
        logging.getLogger(__name__).exception("wiring.svg failed: %s", exc)
        result = ""

    with _lock:
        _cache[cache_key] = result
    return result
