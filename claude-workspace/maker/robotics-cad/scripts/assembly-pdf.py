"""Tao PDF huong dan lap rap (chu + hinh) tu ASSEMBLY.md cua 1 du an.

Chay: python scripts/assembly-pdf.py maker/<project>/ASSEMBLY.md   -> maker/<project>/ASSEMBLY.pdf
Cach lam: Markdown (tap con dung trong ASSEMBLY.md) -> HTML co CSS in A4 -> Microsoft Edge headless --print-to-pdf
(co san tren Windows, chu tieng Viet chuan, chon/tim chu duoc). Khong can cai them goi.
- Trang bia: ten du an, ngay, anh cuoi (buoc cuoi), muc luc cac buoc.
- Moi "## Buoc ..." sang trang moi; anh step-XX-a.png tu dong kem step-XX-b.png (phong to) canh nhau.
"""

import html
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EDGE = [Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")]

CSS = """
@page { size: A4; margin: 14mm 14mm 16mm 14mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; color: #222; line-height: 1.4; }
h1 { font-size: 22pt; margin: 0 0 4mm; }
h2 { font-size: 15pt; border-bottom: 2px solid #e07020; padding-bottom: 1.5mm; margin: 0 0 3mm; }
.step { page-break-before: always; }
.sec { margin-bottom: 5mm; }
.cover { text-align: center; page-break-after: always; }
.cover img { width: 150mm; margin: 6mm 0; }
.cover .meta { color: #666; }
.toc { text-align: left; margin: 6mm auto; width: 150mm; columns: 2; font-size: 10pt; }
.imgs { display: flex; gap: 3mm; margin: 2mm 0 3mm; page-break-inside: avoid; }
.imgs figure { margin: 0; flex: 1; border: 1px solid #ccc; }
.imgs img { width: 100%; display: block; }
.imgs figcaption { font-size: 8.5pt; color: #666; text-align: center; padding: 1mm; }
table { border-collapse: collapse; margin: 2mm 0; font-size: 9.5pt; }
th, td { border: 1px solid #bbb; padding: 1mm 2mm; text-align: left; }
th { background: #f3f3f3; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f2f2f2; padding: 0 1mm; }
ul { margin: 1mm 0 2mm 5mm; padding-left: 4mm; }
li { margin: 1mm 0; }
.todo { background: #fff3cd; }
.footer-note { color: #888; font-size: 8.5pt; margin-top: 6mm; }
"""


def inline(s, goc):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{(goc / m.group(2)).as_uri()}">{m.group(1)}</a>'
               if not m.group(2).startswith("http") else f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    return s.replace("TODO", '<span class="todo">TODO</span>')


def anh(rel, goc):
    p = (goc / rel).resolve()
    ds = [(p, "Toàn cảnh – chi tiết mới tô xanh")]
    m = re.match(r"(.*step-\d+)-([ab])\.png$", str(p))
    if m:  # luon kem ca 2 goc: a (toan canh) + b (phong to)
        ds = [(Path(m.group(1) + "-a.png"), "Toàn cảnh – chi tiết mới tô xanh"),
              (Path(m.group(1) + "-b.png"), "Phóng to chi tiết mới")]
    the = "".join(f'<figure><img src="{q.as_uri()}"><figcaption>{c}</figcaption></figure>'
                  for q, c in ds if q.exists())
    return f'<div class="imgs">{the}</div>'


def md_html(md, goc):
    dong = md.splitlines()
    out, i, buoc, trong_step = [], 0, [], False
    tieu_de = ""
    while i < len(dong):
        d = dong[i]
        if d.startswith("# "):
            tieu_de = d[2:].strip()
            i += 1
            continue
        if d.startswith("## "):
            if trong_step:
                out.append("</section>")
            ten = d[3:].strip()
            lop = "step" if ten.startswith(("Bước", "Step")) else "sec"  # chi cac buoc moi sang trang moi
            out.append(f'<section class="{lop}"><h2>{inline(ten, goc)}</h2>')
            buoc.append(ten)
            trong_step = True
        elif d.startswith("!["):
            out.append(anh(re.search(r"\(([^)]+)\)", d).group(1), goc))
        elif d.startswith("|"):
            rows = []
            while i < len(dong) and dong[i].startswith("|"):
                if not re.match(r"^\|[\s\-|:]+\|$", dong[i]):
                    rows.append([c.strip() for c in dong[i].strip("|").split("|")])
                i += 1
            o = ["th", "td"]
            t = "<table>" + "".join(
                "<tr>" + "".join(f"<{o[k > 0]}>{inline(c, goc)}</{o[k > 0]}>" for c in r) + "</tr>"
                for k, r in enumerate(rows)) + "</table>"
            out.append(t)
            continue
        elif d.startswith("- "):
            items = []
            while i < len(dong) and (dong[i].startswith("- ") or (dong[i].startswith("  ") and dong[i].strip())):
                if dong[i].startswith("- "):
                    items.append(dong[i][2:].strip())
                else:
                    items[-1] += " " + dong[i].strip()
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x, goc)}</li>" for x in items) + "</ul>")
            continue
        elif d.strip():
            para = [d.strip()]
            while i + 1 < len(dong) and dong[i + 1].strip() and not re.match(r"^(#|- |\||!\[)", dong[i + 1]):
                i += 1
                para.append(dong[i].strip())
            out.append(f"<p>{inline(' '.join(para), goc)}</p>")
        i += 1
    if trong_step:
        out.append("</section>")
    return tieu_de, buoc, "\n".join(out)


def main():
    src = Path(sys.argv[1]).resolve()
    goc = src.parent
    tieu_de, buoc, than = md_html(src.read_text(encoding="utf-8"), goc)
    cuoi = sorted(goc.glob("freecad/images/assembly/step-*-a.png"))
    bia_anh = f'<img src="{cuoi[-1].as_uri()}">' if cuoi else ""
    muc_luc = "".join(f"<div>{html.escape(b)}</div>" for b in buoc)
    bia = (f'<section class="cover"><h1>{html.escape(tieu_de)}</h1>'
           f'<div class="meta">STLab · {goc.name} · tạo {time.strftime("%Y-%m-%d")} từ ASSEMBLY.md</div>'
           f'{bia_anh}<div class="toc">{muc_luc}</div>'
           '<div class="footer-note">Ảnh render từ model FreeCAD; mục đánh dấu TODO cần bổ sung khi lắp thật.</div>'
           '</section>')
    doc = (f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>{html.escape(tieu_de)}</title>'
           f"<style>{CSS}</style></head><body>{bia}{than}</body></html>")
    out = src.with_suffix(".pdf")
    edge = next((e for e in EDGE if e.exists()), None)
    if edge is None:
        raise SystemExit("Khong tim thay Microsoft Edge")
    with tempfile.TemporaryDirectory() as td:
        h = Path(td) / "assembly.html"
        h.write_text(doc, encoding="utf-8")
        subprocess.run([str(edge), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={Path(td) / 'edge'}", f"--print-to-pdf={out}", h.as_uri()],
                       check=True, capture_output=True, timeout=180)
    print(f"PDF: {out} ({out.stat().st_size // 1024} KB, {len(buoc)} muc)")


main()
