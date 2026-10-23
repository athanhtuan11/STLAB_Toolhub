"""Phan tich clip trong projects/<du-an>/inbox -> projects/<du-an>/analysis/ (de Claude lap ke hoach dung).

    uv run python scripts/analyze.py projects/<du-an>

Moi clip: thong tin (ffprobe), chep loi theo tu (faster-whisper, tren may) + bang sua loi, diem cat canh,
anh khung hinh + bang anh tong hop (contact sheet). Clip ghi trong <du-an>/rieng-tu.txt: KHONG trich anh
(Claude chi doc chep loi). Tong hop cho Claude: analysis/tom-tat.md.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".mts"}


def ff(tool):
    found = shutil.which(tool)
    if found:
        return found
    for base in (os.environ.get("FFMPEG_DIR", ""), r"C:\ffmpeg-master-latest-win64-gpl-shared\bin"):
        p = Path(base) / f"{tool}.exe"
        if base and p.exists():
            return str(p)
    sys.exit(f"Khong tim thay {tool} (dat FFMPEG_DIR)")


def probe(clip):
    out = subprocess.run([ff("ffprobe"), "-v", "error", "-print_format", "json", "-show_format", "-show_streams",
                          str(clip)], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    rot = int((v.get("tags") or {}).get("rotate", 0) or 0)
    for sd in v.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", rot) or rot)
    w, h = v.get("width"), v.get("height")
    if abs(rot) in (90, 270):
        w, h = h, w
    return {"duration": round(float(d["format"]["duration"]), 3), "width": w, "height": h,
            "fps": round(int(num) / max(int(den), 1), 3), "audio": a is not None, "rotation": rot}


def corrections():
    f = ROOT / "sua-loi.txt"
    rules = []
    if f.exists():
        for ln in f.read_text(encoding="utf-8").splitlines():
            if "=>" in ln and not ln.startswith("#"):
                wrong, right = (x.strip() for x in ln.split("=>", 1))
                rules.append((re.compile(rf"(?<!\w){re.escape(wrong)}(?!\w)", re.I), right))
    return rules


def apply_corrections(tr, rules):
    for s in tr["segments"]:
        for rx, right in rules:
            s["text"] = rx.sub(right, s["text"])
    for w in tr["words"]:
        for rx, right in rules:
            w["text"] = rx.sub(right, w["text"])
    return tr


def scenes(clip, threshold=0.15):
    """Thoi diem cat canh (giay) bang bo loc scene cua ffmpeg."""
    r = subprocess.run([ff("ffmpeg"), "-hide_banner", "-i", str(clip), "-vf",
                        f"select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [round(float(m), 2) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def frames(clip, outdir, duration, n=12):
    """n anh deu nhau (rong 360 px) + contact sheet 4 cot co ghi thoi diem."""
    outdir.mkdir(parents=True, exist_ok=True)
    step = max(duration / n, 0.5)
    times = [round(i * step + step / 2, 2) for i in range(n) if i * step + step / 2 < duration]
    for t in times:
        subprocess.run([ff("ffmpeg"), "-v", "error", "-y", "-ss", str(t), "-i", str(clip), "-frames:v", "1",
                        "-vf", "scale=360:-2", str(outdir / f"t{t:07.2f}.jpg")], check=True)
    # Contact sheet 4 cot: ghi thoi diem len tung anh, noi thanh chuoi khung roi xep luoi (tile).
    font = outdir / "_font.ttf"  # drawtext tren Windows: dung font o thu muc hien tai, tranh dau ':' cua o dia
    shutil.copy(r"C:\Windows\Fonts\arial.ttf", font)
    rows = (len(times) + 3) // 4
    inputs, labels = [], []
    for i, t in enumerate(times):
        inputs += ["-i", f"t{t:07.2f}.jpg"]
        labels.append(f"[{i}:v]drawtext=fontfile=_font.ttf:text='{t:.1f}s':x=8:y=8:fontsize=26:"
                      f"fontcolor=yellow:box=1:boxcolor=black@0.6[f{i}]")
    tiles = "".join(f"[f{i}]" for i in range(len(times)))
    filt = f"{';'.join(labels)};{tiles}concat=n={len(times)}:v=1:a=0,tile=4x{rows}:padding=4:color=white"
    subprocess.run([ff("ffmpeg"), "-v", "error", "-y", *inputs, "-filter_complex", filt, "-frames:v", "1",
                    str(outdir.parent / "contact.jpg")], check=True, cwd=str(outdir))
    font.unlink(missing_ok=True)
    return times


def pauses(words, min_gap=0.7):
    return [{"sau_tu": a["text"], "tu": a["end"], "den": b["start"], "dai": round(b["start"] - a["end"], 2)}
            for a, b in zip(words, words[1:]) if b["start"] - a["end"] >= min_gap]


def main(project):
    project = Path(project).resolve()
    inbox, out = project / "inbox", project / "analysis"
    clips = sorted(p for p in inbox.iterdir() if p.suffix.lower() in VIDEO_EXT)
    if not clips:
        sys.exit(f"Chua co clip trong {inbox}")
    private = set()
    if (project / "rieng-tu.txt").exists():
        private = {ln.strip() for ln in (project / "rieng-tu.txt").read_text(encoding="utf-8").splitlines()
                   if ln.strip() and not ln.startswith("#")}
    sys.path.insert(0, str(HERE))
    from transcribe import transcribe
    rules = corrections()
    summary = [f"# Phân tích: {project.name}", "",
               "Thời điểm tính bằng giây trong từng clip gốc. Dùng cho plan.json (doan: clip, tu, den).", ""]
    for clip in clips:
        d = out / clip.stem
        d.mkdir(parents=True, exist_ok=True)
        info = probe(clip)
        tfile = d / "transcript.json"
        if not tfile.exists() or tfile.stat().st_mtime < clip.stat().st_mtime:
            print(f"[..] chép lời {clip.name} ({info['duration']} s)…", flush=True)
            tr = transcribe(clip) if info["audio"] else {"segments": [], "words": [], "language": None}
            tfile.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
        tr = apply_corrections(json.loads(tfile.read_text(encoding="utf-8")), rules)
        (d / "transcript.fixed.json").write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
        cuts = scenes(clip)
        is_private = clip.name in private
        times = [] if is_private else frames(clip, d / "frames", info["duration"])
        (d / "info.json").write_text(json.dumps({**info, "scene_cuts": cuts, "frames": times,
                                                 "private": is_private}, indent=1), encoding="utf-8")
        summary += [f"## {clip.name}",
                    f"- {info['duration']} s · {info['width']}×{info['height']} · {info['fps']} fps"
                    f" · {'có' if info['audio'] else 'KHÔNG có'} tiếng",
                    f"- Điểm cắt cảnh (s): {', '.join(map(str, cuts)) or 'không có'}",
                    "- Ảnh: " + ("RIÊNG TƯ – không trích ảnh, chỉ dùng chép lời" if is_private
                                 else f"`analysis/{clip.stem}/contact.jpg` (12 khung, có ghi thời điểm)"),
                    "", "Chép lời:"]
        summary += [f"- [{s['start']:.2f}–{s['end']:.2f}] {s['text']}" for s in tr["segments"]] or ["- (không có lời)"]
        ps = pauses(tr["words"])
        if ps:
            summary += ["", "Khoảng lặng ≥ 0,7 s: " + "; ".join(f"{p['tu']:.2f}–{p['den']:.2f} ({p['dai']} s)"
                                                                 for p in ps)]
        summary.append("")
        print(f"[OK] {clip.name}: {len(tr['words'])} từ, {len(cuts)} cắt cảnh, {len(times)} ảnh"
              f"{' (riêng tư)' if is_private else ''}")
    (out / "tom-tat.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"[OK] Tóm tắt: {out / 'tom-tat.md'}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
