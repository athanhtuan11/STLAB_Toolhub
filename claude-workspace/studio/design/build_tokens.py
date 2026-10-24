"""tokens.json -> CSS bien (Toolhub) + kiem do tuong phan WCAG. Chay: python studio/design/build_tokens.py

Ra: studio/toolhub/static/tokens.css (sinh tu dong, KHONG sua tay).
Workbench FreeCAD doc thang tokens.json (maker/robotics-cad/workbench/STLab/stlab_wb/core.py).
Exit 1 neu cap mau chu/nen nao duoi nguong (4,5:1 chu thuong, 3:1 vien/icon).
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOK = json.loads((HERE / "tokens.json").read_text(encoding="utf-8"))
OUT = HERE.parent / "toolhub" / "static" / "tokens.css"


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# (chu, nen, nguong): cap that su xuat hien trong giao dien
PAIRS = [("text", "bg", 4.5), ("text", "card", 4.5), ("muted", "card", 4.5), ("muted", "bg", 4.5),
         ("accent", "card", 4.5), ("accent", "bg", 4.5), ("ok", "card", 4.5), ("warn", "card", 4.5),
         ("err", "card", 4.5), ("on-highlight", "highlight", 4.5), ("line", "card", 1.2)]


def check():
    bad = []
    for mode in ("light", "dark"):
        t = TOK[mode]
        for fg, bg, need in PAIRS:
            r = ratio(t[fg], t[bg])
            if r < need:
                bad.append(f"{mode}: {fg} tren {bg} = {r:.2f} < {need}")
        # chu trang tren nut chinh (accent) o che do sang
    r = ratio("#FFFFFF", TOK["light"]["accent"])
    if r < 4.5:
        bad.append(f"light: chu trang tren accent = {r:.2f}")
    r = ratio(TOK["dark"]["bg"], TOK["dark"]["accent"])
    if r < 4.5:
        bad.append(f"dark: chu nen tren accent = {r:.2f}")
    for k, s in TOK["stages"].items():  # icon chu trang tren mau buoc: chu dam lon -> 3:1
        r = ratio("#FFFFFF", s["color"])
        if r < 3:
            bad.append(f"buoc {k}: chu trang tren {s['color']} = {r:.2f} < 3")
    return bad


def css():
    f = TOK["font"]

    def block(t):
        return "".join(f"  --{k}: {v};\n" for k, v in t.items())
    stages = "".join(f"  --stage-{k}: {s['color']};\n" for k, s in TOK["stages"].items())
    on_accent_dark = TOK["dark"]["bg"]
    return (f"/* SINH TU studio/design/tokens.json bang build_tokens.py - KHONG SUA TAY */\n"
            f":root {{\n{block(TOK['light'])}  --on-accent: #FFFFFF;\n{stages}"
            f"  --font-ui: \"{f['ui']}\", {f['fallback']};\n  --font-mono: {f['mono']};\n"
            f"  --r-control: {TOK['radius']['control']}px;\n  --r-card: {TOK['radius']['card']}px;\n"
            f"  color-scheme: light;\n}}\n"
            f"@media (prefers-color-scheme: dark) {{\n  :root {{\n"
            + "".join(f"  {ln}\n" for ln in block(TOK["dark"]).splitlines())
            + f"    --on-accent: {on_accent_dark};\n    color-scheme: dark;\n  }}\n}}\n")


def main():
    bad = check()
    OUT.write_text(css(), encoding="utf-8")
    print(f"-> {OUT}")
    for b in bad:
        print("TUONG PHAN THAP:", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
