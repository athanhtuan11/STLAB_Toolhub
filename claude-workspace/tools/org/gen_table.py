#!/usr/bin/env python3
"""Generate the personnel table in CLAUDE.md from org/agents.yaml."""

import argparse
from pathlib import Path
import sys

import yaml

START = "<!-- org-table:start -->"
END = "<!-- org-table:end -->"
NOTE = "_Sinh t\u1ef1 \u0111\u1ed9ng t\u1eeb org/agents.yaml b\u1eb1ng tools/org/gen_table.py \u2013 kh\u00f4ng s\u1eeda tay._"
HEADERS = ("T\u1ea7ng", "Ch\u1ee9c danh", "Agent", "Model", "Chi ph\u00ed", "K\u1ef9 n\u0103ng", "B\u00e1o c\u00e1o cho", "Tr\u1ea1ng th\u00e1i")
LEVELS = {0: "0 \u2013 Gi\u00e1m \u0111\u1ed1c", 1: "1 \u2013 Qu\u1ea3n l\u00fd", 2: "2 \u2013 Nh\u00e2n vi\u00ean", "tu-van": "T\u01b0 v\u1ea5n"}
ORDER = {0: 0, 1: 1, 2: 2, "tu-van": 3}


def render_table(org_dir, newline):
    with (org_dir / "agents.yaml").open("r", encoding="utf-8-sig") as stream:
        agents = yaml.safe_load(stream)["agents"]
    agents = sorted(agents, key=lambda agent: ORDER[agent["tang"]])
    lines = [
        "| " + " | ".join(HEADERS) + " |",
        "| " + " | ".join("---" for _ in HEADERS) + " |",
    ]
    for agent in agents:
        fields = (
            LEVELS[agent["tang"]], str(agent["chuc_danh"]), f'`{agent["id"]}`',
            str(agent["model"]), str(agent["chi_phi"]),
            ", ".join(str(skill) for skill in agent["ky_nang"]),
            str(agent["bao_cao_cho"]), str(agent["trang_thai"]),
        )
        lines.append("| " + " | ".join(fields) + " |")
    lines.append(NOTE)
    return newline + newline.join(lines) + newline


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", type=Path, default=script_dir / "../../org")
    parser.add_argument("--claude", type=Path, default=script_dir / "../../CLAUDE.md")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        raw = args.claude.read_bytes()
        text = raw.decode("utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"Could not read CLAUDE.md: {exc}", file=sys.stderr)
        return 1
    if START not in text or END not in text or text.index(START) >= text.index(END):
        print("Missing org-table markers", file=sys.stderr)
        return 2
    newline = "\r\n" if "\r\n" in text else "\n"
    start = text.index(START) + len(START)
    end = text.index(END)
    updated = text[:start] + render_table(args.org, newline) + text[end:]
    if args.check:
        if updated != text:
            print("LECH")
            return 1
        return 0
    if updated != text or raw.startswith(b"\xef\xbb\xbf"):
        args.claude.write_bytes(updated.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
