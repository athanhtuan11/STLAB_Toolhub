"""Sinh icon SVG cho workbench STLab (mau theo buoc quy trinh).
Chay lai khi them lenh: python workbench/make_icons.py"""

from pathlib import Path

OUT = Path(__file__).resolve().parent / "STLab" / "stlab_wb" / "icons"
STAGE = {1: "#4a6fa5", 2: "#7a5aa6", 3: "#2f8f83", 4: "#c0504d", 5: "#e07020", 6: "#5b7c3a", 0: "#333333"}
# ten lenh -> (buoc, chu tren icon)
ICONS = {
    "NewProject": (1, "+"), "OpenProject": (1, "P"), "ProjectFolder": (1, "F"),
    "Components": (2, "LK"),
    "Labels": (3, "Aa"), "PrintPreview": (3, "↻"), "Backup": (3, "BK"),
    "CheckFast": (4, "✓"), "CheckFull": (4, "✓✓"), "CheckReport": (4, "!"),
    "ExportStl": (5, "STL"), "Printability": (5, "45°"), "Slice": (5, "≡"), "PreparePrint": (5, "▶"),
    "Plates": (5, "3MF"),
    "Bom": (6, "BOM"), "MetricsDiff": (6, "Δ"), "AssemblyPdf": (6, "PDF"),
    "Panel": (0, "☰"), "Workbench": (0, "ST"),
}


def svg(color, text, step):
    size = 30 if len(text) == 1 else (22 if len(text) == 2 else 16)
    badge = (f'<circle cx="52" cy="12" r="10" fill="#fff"/><text x="52" y="17" font-size="14" font-weight="bold" '
             f'text-anchor="middle" fill="{color}" font-family="Segoe UI, Arial">{step}</text>') if step else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
            f'<rect x="3" y="3" width="58" height="58" rx="12" fill="{color}"/>'
            f'<text x="32" y="{32 + size * 0.36:.0f}" font-size="{size}" font-weight="bold" text-anchor="middle" '
            f'fill="#fff" font-family="Segoe UI, Arial">{text}</text>{badge}</svg>\n')


OUT.mkdir(parents=True, exist_ok=True)
for name, (step, text) in ICONS.items():
    (OUT / f"{name}.svg").write_text(svg(STAGE[step], text, step), encoding="utf-8")
print(f"{len(ICONS)} icon -> {OUT}")
