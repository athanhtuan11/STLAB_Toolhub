import html
import re


def render(text) -> str:
    lines = html.escape(str(text), quote=True).splitlines()
    out, paragraph = [], []
    code = None
    listing = None
    table = False

    def inline(value):
        value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
        value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)

        def link(match):
            label, url = match.group(1), match.group(2)
            if url.startswith(("http://", "https://")):
                return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
            if ":" not in url:
                return f'<a href="{url}">{label}</a>'
            return label
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, value)

    def flush_paragraph():
        if paragraph:
            out.append("<p>" + inline("<br>".join(paragraph)) + "</p>")
            paragraph.clear()

    def close_list():
        nonlocal listing
        if listing:
            out.append(f"</{listing}>")
            listing = None

    def cells(line):
        return [part.strip() for part in line.strip().strip("|").split("|")]

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            flush_paragraph(); close_list()
            if code is None:
                code = []
            else:
                out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
                code = None
            i += 1
            continue
        if code is not None:
            code.append(line); i += 1; continue
        if i + 1 < len(lines) and "|" in line and re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*", lines[i+1]):
            flush_paragraph(); close_list()
            headers = cells(line)
            out.append("<table><thead><tr>" + "".join("<th>" + inline(x) + "</th>" for x in headers) + "</tr></thead><tbody>")
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                row = cells(lines[i])
                out.append("<tr>" + "".join("<td>" + inline(x) + "</td>" for x in row) + "</tr>")
                i += 1
            out.append("</tbody></table>")
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            flush_paragraph(); close_list(); level = len(heading.group(1))
            out.append(f"<h{level}>" + inline(heading.group(2)) + f"</h{level}>")
        elif re.match(r"^\s*-\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            flush_paragraph()
            kind = "ul" if re.match(r"^\s*-", line) else "ol"
            if listing != kind:
                close_list(); listing = kind; out.append(f"<{kind}>")
            item = re.sub(r"^\s*(?:-|\d+\.)\s+", "", line)
            out.append("<li>" + inline(item) + "</li>")
        elif not line.strip():
            flush_paragraph(); close_list()
        else:
            close_list(); paragraph.append(line)
        i += 1
    flush_paragraph(); close_list()
    if code is not None:
        out.append("<pre><code>" + "\n".join(code) + "</code></pre>")
    return "\n".join(out)
