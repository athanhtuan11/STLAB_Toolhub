import argparse
import json
import os
import statistics
import sys

DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fits.json")
FIT_TYPES = {"rotate", "slide", "press", "clearance", "self-tap", "unknown"}
REQUIRED = ("id", "interface", "fit", "hole_mm", "shaft_mm", "clearance_mm", "nominal_mm", "source", "confidence", "verified")


def load(path=None):
    with open(path or DEFAULT, "r", encoding="utf-8") as stream:
        return json.load(stream)["entries"]


def validate(entries):
    errors = []
    seen = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append("entry %d is not an object" % index)
            continue
        for key in REQUIRED:
            if key not in entry:
                errors.append("missing required key: %s" % key)
        if "id" in entry:
            try:
                if entry["id"] in seen:
                    errors.append("duplicate id: %s" % entry["id"])
                seen.add(entry["id"])
            except TypeError:
                errors.append("invalid id")
        if "fit" in entry and entry["fit"] not in FIT_TYPES:
            errors.append("invalid fit")
        hole, shaft = entry.get("hole_mm"), entry.get("shaft_mm")
        if "hole_mm" in entry and "shaft_mm" in entry and hole is None and shaft is None:
            errors.append("hole_mm and shaft_mm cannot both be None")
        if hole is not None and shaft is not None:
            try:
                clearance = entry.get("clearance_mm")
                if clearance is None or abs(clearance - (hole - shaft)) > 0.005:
                    errors.append("clearance_mm does not match hole_mm - shaft_mm")
            except (TypeError, ValueError):
                errors.append("clearance_mm, hole_mm, and shaft_mm must be numeric")
        if "confidence" in entry:
            try:
                if not 0 <= entry["confidence"] <= 1:
                    errors.append("confidence must be in [0, 1]")
            except TypeError:
                errors.append("confidence must be in [0, 1]")
        source = entry.get("source")
        if not isinstance(source, dict) or not source.get("model"):
            errors.append("source.model is required")
        if not isinstance(source, dict) or not source.get("method"):
            errors.append("source.method is required")
    return errors


def _confidence(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("-inf")


def lookup(entries, interface):
    matched = [entry for entry in entries if entry.get("interface") == interface]
    return sorted(matched, key=lambda entry: (not bool(entry.get("verified")), -_confidence(entry.get("confidence"))))


def recommend(entries, interface):
    found = lookup(entries, interface)
    if not found:
        return None
    verified = [entry for entry in found if entry.get("verified")]
    chosen = verified if verified else found

    def median(key):
        values = [entry[key] for entry in chosen if entry.get(key) is not None]
        return round(statistics.median(values), 4) if values else None

    fits = {}
    for entry in chosen:
        fit = entry.get("fit")
        fits[fit] = fits.get(fit, 0) + 1
    max_count = max(fits.values())
    common_fit = next(entry.get("fit") for entry in chosen if fits[entry.get("fit")] == max_count)
    return {"interface": interface, "basis": "verified" if verified else "community", "n": len(chosen),
            "ids": [entry.get("id") for entry in chosen], "hole_mm": median("hole_mm"),
            "shaft_mm": median("shaft_mm"), "clearance_mm": median("clearance_mm"), "fit": common_fit}


def add_from_features(path, features_json, feature_id, entry_id, interface, fit, model, nominal_mm=None, note=""):
    with open(features_json, "r", encoding="utf-8") as stream:
        data = json.load(stream)
    feature = next((item for item in data.get("features", []) if item.get("id") == feature_id), None)
    if feature is None:
        raise ValueError("feature_id not found")
    kind = feature.get("type")
    if kind == "hole":
        hole_mm, shaft_mm = feature.get("d_mm"), None
    elif kind == "boss":
        hole_mm, shaft_mm = None, feature.get("d_mm")
    else:
        raise ValueError("arc or unsupported feature type")
    entry = {"id": entry_id, "interface": interface, "fit": fit, "hole_mm": hole_mm, "shaft_mm": shaft_mm,
             "clearance_mm": None, "nominal_mm": nominal_mm,
             "source": {"model": model, "parts": "%s#%s" % (os.path.basename(data.get("file", "")), feature_id),
                        "method": "stl-fit"},
             "print": {"printer": "TODO (tac gia)", "material": "TODO (tac gia)"},
             "confidence": feature.get("confidence"), "verified": False, "note": note}
    with open(path, "r", encoding="utf-8") as stream:
        document = json.load(stream)
    errors = validate(document["entries"] + [entry])
    if errors:
        raise ValueError("invalid entry: " + "; ".join(errors))
    document["entries"].append(entry)
    with open(path, "w", encoding="utf-8", newline="") as stream:
        json.dump(document, stream, ensure_ascii=False, indent=1)
        stream.write("\n")
    return entry


def _dump(value):
    json.dump(value, sys.stdout, ensure_ascii=False, indent=1)
    sys.stdout.write("\n")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("--file", default=DEFAULT)
    lookup_parser = commands.add_parser("lookup")
    lookup_parser.add_argument("interface")
    lookup_parser.add_argument("--file", default=DEFAULT)
    recommend_parser = commands.add_parser("recommend")
    recommend_parser.add_argument("interface")
    recommend_parser.add_argument("--file", default=DEFAULT)
    args = parser.parse_args(argv)
    entries = load(args.file)
    if args.command == "check":
        errors = validate(entries)
        for error in errors:
            print(error)
        return 1 if errors else 0
    if args.command == "lookup":
        _dump(lookup(entries, args.interface))
        return 0
    result = recommend(entries, args.interface)
    if result is None:
        print("No entries for interface: %s" % args.interface, file=sys.stderr)
        return 1
    _dump(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
