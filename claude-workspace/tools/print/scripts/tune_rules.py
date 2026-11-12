"""Sinh de xuat thong so slicer tu dac trung hinh hoc (luat muc 3 + 8.9)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PRESETS_PATH = Path(__file__).resolve().parent / "tune" / "presets.json"

# Muc nguon theo bao cao (preset co cot Muc; khoa ngoai preset khong ro -> P)
LEVELS = {
    "enable_support": "S",
    "support_type": "S",
    "support_style": "P",
    "brim_type": "S",
    "brim_width": "S",
    "brim_object_gap": "P",
    "support_on_build_plate_only": "P",
    "layer_height": "P",
}


def _load_presets():
    try:
        return json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def suggest(features, goals=()):
    goals = set(goals or [])
    presets = _load_presets()
    process = {}
    filament = {}
    items = []

    def add(key, value, pack, reason, level="P", preset=""):
        if pack == "filament":
            filament[key] = value
        else:
            process[key] = value
        items.append({"key": key, "value": value, "pack": pack, "reason": reason,
                      "level": level or "P", "preset": preset or ""})

    def apply_preset(name, reason, only=None, skip=None):
        p = presets.get(name) or {}
        for k, v in (p.get("process") or {}).items():
            if only and k not in only:
                continue
            if skip and k in skip:
                continue
            add(k, v, "process", reason, LEVELS.get(k, "P"), name)
        for k, v in (p.get("filament") or {}).items():
            if only and k not in only:
                continue
            if skip and k in skip:
                continue
            add(k, v, "filament", reason, LEVELS.get(k, "P"), name)

    can_support = bool(features.get("can_support"))
    contact = float(features.get("contact_mm2") or 0)
    aspect = float(features.get("aspect") or 0)
    max_over = float(features.get("max_overhang_mm2") or 0)
    small = bool(features.get("small"))
    holes = int(features.get("holes") or 0)
    curved = float(features.get("curved_frac") or 0)

    # a. khong can do
    if not can_support:
        add("enable_support", "0", "process", "Kh\u00f4ng c\u00f3 ph\u1ea7n nh\u00f4 c\u1ea7n \u0111\u1ee1.", "S")
    # b. can do
    if can_support:
        add("enable_support", "1", "process", "C\u00f3 ph\u1ea7n nh\u00f4 c\u1ea7n \u0111\u1ee1.", "S")
        pname = "support_pretty" if "support_pretty" in goals else "support_easy"
        apply_preset(pname, "Preset " + pname + " theo m\u1ee5c ti\u00eau support.")
        if "support_pretty" not in goals:
            if max_over > 100:
                add("support_type", "normal(auto)", "process",
                    "M\u1ea3ng nh\u00f4 l\u1edbn ph\u1eb3ng n\u00ean d\u00f9ng support th\u01b0\u1eddng.", "P")
                add("support_style", "default", "process",
                    "M\u1ea3ng nh\u00f4 l\u1edbn ph\u1eb3ng n\u00ean d\u00f9ng ki\u1ec3u m\u1eb7c \u0111\u1ecbnh.", "P")
            else:
                add("support_type", "tree(auto)", "process",
                    "M\u1eb7c \u0111\u1ecbnh A1: support c\u00e2y cho ph\u1ea7n nh\u00f4 th\u01b0\u1eddng.", "S")

    # c. brim
    need_brim = (contact < 120) or (aspect >= 2.5)
    if need_brim:
        apply_preset("brim_easy", "Ch\u00e2n nh\u1ecf ho\u1eb7c chi ti\u1ebft cao m\u1ea3nh n\u00ean d\u00f9ng brim.")
        add("brim_type", "outer_only", "process", "Brim v\u00e0nh ngo\u00e0i d\u1ec5 g\u1ee1.", "S")
        if aspect >= 2.5:
            apply_preset("tall_thin", "Chi ti\u1ebft cao m\u1ea3nh (aspect \u2265 2.5).")
    else:
        add("brim_type", "no_brim", "process",
            "Ch\u00e2n l\u1edbn, th\u1ea5p n\u00ean kh\u00f4ng c\u1ea7n brim.", "P")
    if "pretty_edge" in goals:
        add("brim_object_gap", "0.2", "process", "M\u1ee5c ti\u00eau m\u00e9p \u0111\u1eb9p: khe brim l\u1edbn h\u01a1n, d\u1ec5 g\u1ee1.", "P")

    # d. chi tiet nho
    if small:
        apply_preset("small_parts", "Chi ti\u1ebft nh\u1ecf (max(bbox x,y) < 20 mm).")
    # giu preset tall_thin khi cao manh (gate yeu cau)
    if aspect >= 2.5:
        apply_preset("tall_thin", "Chi ti\u1ebft cao m\u1ea3nh (aspect \u2265 2.5).")

    # e. nhieu lo
    if holes >= 4:
        apply_preset("petg_stringing", "Nhi\u1ec1u l\u1ed7 (holes \u2265 4) d\u1ec5 b\u1ecb t\u01a1.")

    # f. mat cong lon
    if curved > 0.3:
        add("layer_height", "0.16", "process",
            "M\u1eb7t cong l\u1edbn (curved_frac > 0.3) n\u00ean d\u00f9ng l\u1edbp th\u1ea5p h\u01a1n.", "P")

    # g. muc tieu bo sung
    if "surface_pretty" in goals:
        apply_preset("surface_pretty", "M\u1ee5c ti\u00eau b\u1ec1 m\u1eb7t \u0111\u1eb9p.")
    if "plate_only" in goals:
        add("support_on_build_plate_only", "1", "process",
            "M\u1ee5c ti\u00eau ch\u1ec9 \u0111\u1ee1 t\u1eeb b\u00e0n in.", "P")

    return {"process": process, "filament": filament, "items": items}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    if not argv:
        print(json.dumps({"error": "usage: tune_rules.py <stl> [goal ...]"}, ensure_ascii=False))
        sys.exit(1)
    stl = argv[0]
    goals = argv[1:]
    try:
        from geometry_profile import features
        f = features(stl)
        print(json.dumps(suggest(f, goals=goals), ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)
