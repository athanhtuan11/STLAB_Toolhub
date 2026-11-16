#!/usr/bin/env python3
"""Bundle the block-coding-car web app into one self-contained HTML file.

Usage:
    python build.py --out dist/index.html.gz

Reads src/index.html, src/style.css and the ES modules (sim, program, carlink, ui),
inlines the CSS, concatenates the modules in order into one plain <script>, writes the
gzipped file to --out and an uncompressed sibling dist/index.html for inspection.
Standard library only.
"""
import argparse
import gzip
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
MODULES = ["sim.js", "program.js", "carlink.js", "ui.js"]

CSS_TAG = '<link rel="stylesheet" href="style.css">'
JS_TAG = '<script type="module" src="ui.js"></script>'

IMPORT_RE = re.compile(r"^\s*import\s")
EXPORT_RE = re.compile(r"^(\s*)export\s+")


def read_text(name):
    path = os.path.join(SRC, name)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def strip_module(text):
    lines = []
    for line in text.splitlines():
        if IMPORT_RE.match(line):
            continue
        lines.append(EXPORT_RE.sub(r"\1", line))
    return "\n".join(lines)


def build_js():
    parts = []
    for name in MODULES:
        parts.append("// ---- " + name + " ----")
        parts.append(strip_module(read_text(name)))
    return "\n".join(parts)


def build_html(css, js):
    html = read_text("index.html")
    if CSS_TAG not in html:
        raise SystemExit("build: missing stylesheet tag in src/index.html")
    if JS_TAG not in html:
        raise SystemExit("build: missing module script tag in src/index.html")
    html = html.replace(CSS_TAG, "<style>\n" + css + "\n</style>", 1)
    html = html.replace(JS_TAG, "<script>\n" + js + "\n</script>", 1)
    return html


def main():
    ap = argparse.ArgumentParser(description="Bundle block-coding-car app")
    ap.add_argument("--out", default="dist/index.html.gz")
    args = ap.parse_args()

    css = read_text("style.css")
    js = build_js()
    html = build_html(css, js)

    out = args.out
    folder = os.path.dirname(os.path.abspath(out))
    os.makedirs(folder, exist_ok=True)

    raw = html.encode("utf-8")
    with open(os.path.join(folder, "index.html"), "wb") as fh:
        fh.write(raw)
    with open(out, "wb") as fh:
        fh.write(gzip.compress(raw, compresslevel=9, mtime=0))

    print("wrote %s (%d B, %d B gzip)" % (out, len(raw), os.path.getsize(out)))


if __name__ == "__main__":
    main()
