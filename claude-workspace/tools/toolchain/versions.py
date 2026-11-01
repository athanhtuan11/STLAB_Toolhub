#!/usr/bin/env python3
"""Report installed STLab tool versions and community repository sizes."""
import argparse, datetime as dt, json, os, re, shutil, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
WS = HERE.parents[1]
def run(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20, shell=False)
        return (p.stdout + "\n" + p.stderr).strip() if p.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError): return ""
def read_tsv(path):
    try: return [x.split("\t") for x in path.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip() and not x.lstrip().startswith("#")]
    except OSError: return []
def tool_rows():
    rows=[]
    def add(i,n,v,s): rows.append({"id":i,"name":n,"version":v,"source":s})
    fc=r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
    out=run([fc,"--version"]) if Path(fc).is_file() else ""
    m=re.search(r"FreeCAD\s+(v?\d+(?:\.\d+)+)",out,re.I)
    add("freecad","FreeCAD",m.group(1) if m else None,"freecadcmd --version")
    bp=r"C:\Program Files\Bambu Studio\bambu-studio.exe"
    ver=None; ps=shutil.which("powershell") or shutil.which("pwsh")
    if ps and Path(bp).is_file():
        x=run([ps,"-NoProfile","-Command",f"(Get-Item -LiteralPath '{bp}').VersionInfo | ForEach-Object {{ if ($_.ProductVersion) {{ $_.ProductVersion }} else {{ $_.FileVersion }} }}"])
        x=x.splitlines()[0].strip() if x else ""
        ver=".".join(str(int(p)) for p in x.split(".")) if re.fullmatch(r"\d+(\.\d+)+",x) else None  # FileVersion 02.08.02.61 -> 2.8.2.61
    add("bambu-studio","Bambu Studio",ver,"file ProductVersion/FileVersion")
    dirs=[]; ep=os.environ.get("IDF_PATH")
    if ep and Path(ep).is_dir(): dirs.append(Path(ep))
    root=Path(r"C:\Espressif\frameworks")
    if root.is_dir(): dirs += [x for x in root.glob("esp-idf-v*") if x.is_dir()]
    vs=[]
    for d in dirs:
        v=None
        try:
            f=d/"version.txt"
            if f.is_file(): v=f.read_text(encoding="utf-8",errors="replace").strip().splitlines()[0]
        except (OSError,IndexError): pass
        if not v:
            m=re.search(r"esp-idf-v(.+)$",d.name); v=m.group(1) if m else None
        if v and v not in vs: vs.append(v)
    vs.sort(key=lambda x:tuple(int(y) if y.isdigit() else y for y in re.findall(r"\d+|\D+",x)))
    add("esp-idf","ESP-IDF",vs[-1] if vs else None,"IDF_PATH / esp-idf version.txt"+(": "+", ".join(vs) if len(vs)>1 else ""))
    add("python","Python",".".join(map(str,sys.version_info[:3])),"sys.version")
    for i,n,c in [("git","Git","git"),("node","Node.js","node"),("uv","uv","uv"),("codex","Codex","codex"),("opencode","OpenCode","opencode"),("kilo","Kilo","kilo"),("copilot","Copilot","copilot"),("agy","Antigravity","agy")]:
        exe=shutil.which(c); out=run([exe,"--version"]) if exe else ""; m=re.search(r"v?\d+(?:\.\d+)+",out)
        add(i,n,m.group(0) if m else None,c+" --version")
    exe=shutil.which("dot") or next((str(q) for q in [Path(r"C:\Program Files\Graphviz\bin\dot.exe")] if q.is_file()),None); out=run([exe,"-V"]) if exe else ""; m=re.search(r"version\s+(\d+(?:\.\d+)+)",out,re.I)
    add("graphviz","Graphviz",m.group(1) if m else None,"dot -V")
    exts=Path.home()/".vscode"/"extensions"; matches=sorted(exts.glob("anthropic.claude-code-*"),key=lambda x:x.stat().st_mtime if x.exists() else 0); cv=None
    for x in matches:
        m=re.match(r"anthropic\.claude-code-(\d+(?:\.\d+)+)",x.name)
        if m: cv=m.group(1)
    add("claude-code","Claude Code",cv,"VS Code extension")
    hyper=None; hp=WS/"video-ai"/"CLAUDE.md"
    try:
        m=re.search(r"hyperframes[^\n]{0,100}?(0\.8\.\d+)",hp.read_text(encoding="utf-8",errors="replace"),re.I)
        if m: hyper=m.group(1)
    except OSError: pass
    if hyper is None:
        for row in read_tsv(WS/"community"/"pins.tsv"):
            if "hyperframes" in "\t".join(row).lower():
                m=re.search(r"0\.8\.\d+","\t".join(row))
                if m: hyper=m.group(0); break
    add("hyperframes","HyperFrames",hyper,"ghim")
    return rows
def community_rows():
    base=WS/"community"; pins={}; linked=set()
    for row in read_tsv(base/"pins.tsv"):
        if row: pins[row[0].strip()]=(row[4].strip()[:12] if len(row)>4 and row[4].strip() else (row[3].strip() if len(row)>3 and row[3].strip() else None))
    for row in read_tsv(base/"links.tsv"):
        for cell in row:
            m=re.search(r"(?:^|/)community/([^/]+)(?:/|$)",cell.replace("\\","/"))
            if m: linked.add(m.group(1))
    try: folders=sorted(x for x in base.iterdir() if x.is_dir() and x.name!="reports")
    except OSError: folders=[]
    result=[]
    for folder in folders:
        total=0; stack=[folder]
        while stack:
            cur=stack.pop()
            try:
                with os.scandir(cur) as entries:
                    for e in entries:
                        try:
                            if e.is_symlink(): continue
                            if e.is_dir(follow_symlinks=False): stack.append(Path(e.path))
                            elif e.is_file(follow_symlinks=False): total+=e.stat(follow_symlinks=False).st_size
                        except OSError: pass
            except OSError: pass
        commit=run(["git","-C",str(folder),"log","-1","--format=%cs"])
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",commit): commit=None
        result.append({"name":folder.name,"size_mb":round(total/1048576,1),"linked":folder.name in linked,"pin":pins.get(folder.name),"last_commit":commit})
    result.sort(key=lambda x:(-x["size_mb"],x["name"]))
    return result
def markdown(data):
    now=dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines=[f"# Phi\u00ean b\u1ea3n c\u00f4ng c\u1ee5 (sinh t\u1ef1 \u0111\u1ed9ng \u2013 {now})","",
    "Ch\u1ea1y `python tools/toolchain/versions.py` \u0111\u1ec3 c\u1eadp nh\u1eadt, kh\u00f4ng s\u1eeda tay.","",
    "| C\u00f4ng c\u1ee5 | Phi\u00ean b\u1ea3n | L\u1ea5y t\u1eeb |","|---|---|---|"]
    for t in data["tools"]: lines.append(f"| {t['name']} | {t['version'] if t['version'] is not None else 'unknown'} | {t['source']} |")
    lines += ["","| Repo | MB | Li\u00ean k\u1ebft | Ghim | Commit cu\u1ed1i |","|---|---:|---|---|---|"]
    for r in data["community"]:
        linked="c\u00f3" if r["linked"] else "kh\u00f4ng"
        lines.append(f"| `{r['name']}` | {r['size_mb']:.1f} | {linked} | {r['pin'] or 'unknown'} | {r['last_commit'] or 'unknown'} |")
    lines.append(f"| T\u1ed5ng | {data['community_total_mb']:.1f} | | | |")
    lines += ["","\u1ee8ng vi\u00ean g\u1ee1/sparse \u2013 Tuan quy\u1ebft:"]
    cand=[r for r in data["community"] if not r["linked"] and r["size_mb"]>100]
    lines.extend([f"- `{r['name']}` ({r['size_mb']:.1f} MB)" for r in cand] or ["- Kh\u00f4ng c\u00f3"])
    return "\n".join(lines)+"\n"
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,default=WS/"docs"/"toolchain.md"); ap.add_argument("--json",dest="json_out",type=Path); a=ap.parse_args()
    ts=tool_rows(); cs=community_rows(); data={"tools":ts,"community":cs,"community_total_mb":round(sum(x["size_mb"] for x in cs),1)}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(markdown(data),encoding="utf-8",newline="\n")
    if a.json_out:
        a.json_out.parent.mkdir(parents=True,exist_ok=True); a.json_out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
if __name__=="__main__": main()
