"""Dung video trong FilmCraft tu ke hoach cua Claude: projects/<du-an>/plan.json -> .fcproj + .mp4.

    uv run python scripts/build.py projects/<du-an> [--no-export]

plan.json (Claude viet sau khi doc analysis/tom-tat.md, xem anh contact.jpg va brief.md):
{
  "template": "reel-9x16",
  "ten": "xe-robot-esp32",                      # ten file (khong dau, kebab-case)
  "mo_dau": "XE ROBOT ESP32 TRONG 1 PHUT",      # chu hook 2-3 s dau (null = khong co)
  "cuoi": "Theo dõi STLab để xem phần 2",        # CTA cuoi video (null = khong co)
  "doan": [ {"clip": "a.mp4", "tu": 0.0, "den": 5.4, "ly_do": "gioi thieu"}, ... ],
  "bo_tu_dem": true, "phu_de": true
}
Trong moi doan, cac tu dem va khoang lang dai deu bi cat (theo template). Ket qua: projects/<du-an>/build/
(<ten>.fcproj mo duoc trong FilmCraft de chinh tiep, captions.srt, kiem-tra-*.png) va out/<ten>.mp4.
"""
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from fc import FilmCraft, ticks  # noqa: E402


def norm(word):
    w = unicodedata.normalize("NFC", word).lower()
    return re.sub(r"[^\w\s]", "", w).strip()


def keep_runs(words, seg_from, seg_to, fillers, max_gap, pad):
    """Cac khoang [a, b] (giay, trong clip goc) can giu: bo tu dem + khoang lang > max_gap."""
    ws = [w for w in words if w["start"] >= seg_from - 0.05 and w["end"] <= seg_to + 0.05]
    ws = [w for w in ws if norm(w["text"]) not in fillers]
    if not ws:  # doan khong co loi (canh minh hoa) -> giu nguyen
        return [(seg_from, seg_to, [])]
    runs, cur = [], [ws[0]]
    for w in ws[1:]:
        if w["start"] - cur[-1]["end"] > max_gap:
            runs.append(cur)
            cur = [w]
        else:
            cur.append(w)
    runs.append(cur)
    out = []
    for r in runs:
        a = max(seg_from, r[0]["start"] - pad)
        b = min(seg_to, r[-1]["end"] + pad)
        out.append((a, b, r))
    return out


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def measure_lufs(path):
    """Do on tich hop (EBU R128) bang ffmpeg."""
    from analyze import ff
    r = subprocess.run([ff("ffmpeg"), "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    vals = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", r.stderr, flags=re.M)
    if not vals:
        raise RuntimeError("Không đo được độ ồn")
    return float(vals[-1])


def compounds():
    """Cum tu khong duoc ngat giua (cum-tu.txt + tu-vung.txt): tap cac cap (am tiet truoc, am tiet sau)."""
    pairs = set()
    for f in (ROOT / "cum-tu.txt", ROOT / "tu-vung.txt"):
        if f.exists():
            for ln in f.read_text(encoding="utf-8").splitlines():
                ws = [norm(x) for x in ln.split()] if not ln.startswith("#") else []
                pairs.update(zip(ws, ws[1:]))
    return pairs


def _clauses(words):
    """Tach theo dau cau/dau phay va khoang nghi > 0.6 s."""
    out, cur = [], []
    for w in words:
        if cur and w["t0"] - cur[-1]["t1"] > 0.6:
            out.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?,;:]$", w["text"]):
            out.append(cur)
            cur = []
    return out + ([cur] if cur else [])


def _split_balanced(ws, max_chars, max_dur, pairs):
    """Chia 1 menh de qua dai thanh n dong deu nhau; khong ngat giua cum tu; uu tien khoang nghi."""
    text = lambda xs: " ".join(x["text"] for x in xs)  # noqa: E731
    if len(text(ws)) <= max_chars and ws[-1]["t1"] - ws[0]["t0"] <= max_dur * 1.4:
        return [ws]
    n = max(2, -(-len(text(ws)) // max_chars))
    target = len(text(ws)) / n
    best, best_s = None, None
    for i in range(len(ws) - 1):  # ngat sau tu i
        first = len(text(ws[:i + 1]))
        if first > max_chars or len(text(ws[i + 1:])) < 6:
            continue
        s = abs(first - target) / max_chars - (ws[i + 1]["t0"] - ws[i]["t1"])
        if (norm(ws[i]["text"]), norm(ws[i + 1]["text"])) in pairs:
            s += 1.0
        if best_s is None or s < best_s:
            best, best_s = i, s
    if best is None:
        best = max(0, min(len(ws) - 2, len(ws) // 2 - 1))
    return [ws[:best + 1]] + _split_balanced(ws[best + 1:], max_chars, max_dur, pairs)


def make_cues(timed_words, max_chars, max_dur, upper):
    """Dong phu de: theo menh de; menh de dai chia deu, khong ngat giua cum tu; gop manh cuoi qua ngan."""
    pairs = compounds()
    cues = []
    for cl in _clauses(timed_words):
        for part in _split_balanced(cl, max_chars, max_dur, pairs):
            t = " ".join(x["text"] for x in part)
            if cues and len(t) < 8 and len(" ".join(x["text"] for x in cues[-1])) + len(t) + 1 <= max_chars + 6 \
                    and part[0]["t0"] - cues[-1][-1]["t1"] < 0.4:
                cues[-1] = cues[-1] + part
            else:
                cues.append(part)
    out = []
    for c in cues:
        text = " ".join(x["text"] for x in c).strip()
        text = re.sub(r"[,;:]$", "", text)
        out.append({"t0": c[0]["t0"], "t1": c[-1]["t1"], "text": text.upper() if upper else text})
    for a, b in zip(out, out[1:]):  # khong de 2 dong chong nhau
        a["t1"] = min(a["t1"], b["t0"] - 0.02)
    return out


def build(project, export=True):
    project = Path(project).resolve()
    plan = json.loads((project / "plan.json").read_text(encoding="utf-8"))
    tpl = yaml.safe_load((ROOT / "templates" / plan["template"] / "cau-hinh.yaml").read_text(encoding="utf-8"))
    name = plan["ten"]
    bdir, odir = project / "build", project / "out"
    bdir.mkdir(exist_ok=True)
    odir.mkdir(exist_ok=True)
    fillers = {norm(f) for f in tpl["cat"]["bo_tu_dem"]} if plan.get("bo_tu_dem", True) else set()
    k = tpl["khung"]

    # 1) Danh sach doan cat (giay trong clip goc) + tu tuong ung tren timeline
    cuts, timed, cursor = [], [], 0.0
    for d in plan["doan"]:
        clip = project / "inbox" / d["clip"]
        tr_file = project / "analysis" / clip.stem / "transcript.fixed.json"
        words = json.loads(tr_file.read_text(encoding="utf-8"))["words"] if tr_file.exists() else []
        for a, b, ws in keep_runs(words, d["tu"], d["den"], fillers, tpl["cat"]["khoang_lang_toi_da_s"],
                                  tpl["cat"]["dem_s"]):
            cuts.append({"clip": clip, "src_in": a, "dur": b - a, "at": cursor})
            for w in ws:
                timed.append({"text": w["text"], "t0": cursor + (w["start"] - a), "t1": cursor + (w["end"] - a)})
            cursor += b - a
    total = cursor
    print(f"[..] {len(cuts)} đoạn cắt, tổng {total:.1f} s (mục tiêu {tpl['thoi_luong_s']['muc_tieu']} s)")

    # 2) Phu de SRT tren thoi gian timeline
    srt = bdir / "captions.srt"
    pd = tpl["phu_de"]
    cues = make_cues(timed, pd["ky_tu_toi_da"], pd["thoi_luong_toi_da_s"], pd["in_hoa"]) if plan.get("phu_de", True) \
        else []
    srt.write_text("".join(f"{i}\n{srt_time(c['t0'])} --> {srt_time(c['t1'])}\n{c['text']}\n\n"
                           for i, c in enumerate(cues, 1)), encoding="utf-8")

    with FilmCraft() as fc:
        fc.run("file.newSequence", name=name, width=k["width"], height=k["height"], fps=k["fps"])
        items = {}
        for c in cuts:
            if c["clip"] not in items:
                items[c["clip"]] = fc.run("file.import", paths=[str(c["clip"])])["items"][0]
        # 3) Dat cac doan lien nhau tren V1/A1
        for c in cuts:
            fc.run("timeline.place", item=items[c["clip"]], track="V1", seconds=round(c["at"], 4),
                   sourceIn=ticks(c["src_in"]), duration=ticks(c["dur"]), insert=False)
        seq = fc.sequence()
        vitems = seq["video"][0]["items"]
        aclips = [it["clip"] for it in seq["audio"][0]["items"]]
        # 4) Khung: clip khac ti le -> auto_reframe (bam chu the) + phong motion de phu kin khung
        kd = tpl["khung_doc"]
        for it in vitems:
            info = json.loads((project / "analysis" / Path(it["name"]).stem / "info.json").read_text(encoding="utf-8"))
            sw, sh = info["width"], info["height"]
            cover = max(k["width"] / sw, k["height"] / sh)
            if abs(sw / sh - k["width"] / k["height"]) > 0.01:
                fc.run("effects.apply", clips=[it["clip"]], effect=kd["effect"])
                fc.run("effects.setParam", clip=it["clip"], effect=kd["effect"], param="aspect", value=kd["aspect"])
                fc.run("effects.setParam", clip=it["clip"], effect=kd["effect"], param="preset", value=kd["preset"])
            if abs(cover - 1) > 0.001:
                fc.run("effects.setParam", clip=it["clip"], effect="motion", param="scale", value=round(cover * 100, 3))
        # 5) Am thanh: danh dau loi noi (de giam nhac khi noi). Do on chinh o buoc 8 tren ban dung that.
        # Khong dung essentialSound.autoMatch: no do tren ca clip goc (gom khoang lang da cat) -> lech ~3 LU.
        fc.run("essentialSound.setType", clips=aclips, type="dialogue")
        # 6) Phu de
        if cues:
            fc.run("captions.import", path=str(srt), name="Phụ đề")
            st = {"font": pd["font"], "size": pd["co_chu"], "color": pd["mau"], "background": False,
                  "outline": pd["vien"], "outlineColor": pd["mau_vien"], "align": "center",
                  "anchor": pd["neo"], "margin": pd["le_duoi"]}
            try:
                fc.run("captions.setStyle", track="C1", **st)
            except Exception as e:  # kieu phu de khong ap duoc -> van giu phu de mac dinh
                print(f"[canh bao] captions.setStyle: {str(e)[:200]}")
        # 7) Chu mo dau / CTA tren V2 (chu tu tao theo kieu "chu_lon" cua template)
        cl = tpl["chu_lon"]
        for key in ("mo_dau", "cuoi"):
            if not plan.get(key):
                continue
            dur = tpl[key]["thoi_luong_s"]
            at = 0.0 if key == "mo_dau" else max(total - dur, 0)
            r = fc.run("graphics.newText", text=plan[key], position=cl["vi_tri"], box=cl["hop"], size=cl["co_chu"],
                       seconds=dur, time=ticks(at), track=1, newClip=True)
            gclip = r.get("clip") if isinstance(r, dict) else None
            fc.run("graphics.set", **({"clip": gclip} if gclip else {}),
                   props={"font": cl["font"], "font_style": cl["font_style"], "size": cl["co_chu"],
                          "align": "center", "fill_color": cl["mau"], "stroke": True,
                          "stroke_width": cl["vien"], "stroke_color": cl["mau_vien"], "shadow": True})
        # 8) Do on: xuat WAV ban dung -> do EBU R128 -> chinh gain cac clip -> do lai
        target = tpl["am_thanh"]["loudness_lufs"]
        wav = bdir / "_do-am-luong.wav"
        for _ in range(2):
            fc.run("export.quick", path=str(wav), format="wav", wait=True)
            lufs = measure_lufs(wav)
            delta = round(target - lufs, 2)
            print(f"[..] độ ồn {lufs:.1f} LUFS (mục tiêu {target}) -> chỉnh {delta:+.1f} dB")
            if abs(delta) <= 0.5:
                break
            fc.run("clip.audioGain", clips=aclips, mode="adjust", db=delta, relative=True)
        wav.unlink(missing_ok=True)
        # 9) Luu du an + anh kiem tra
        fcproj = bdir / f"{name}.fcproj"
        fc.run("file.saveAs", path=str(fcproj))
        checks = sorted({0.8, round(total / 2, 2), round(max(total - 1.0, 0), 2)})
        for t in checks:
            (bdir / f"kiem-tra-{t:06.2f}s.png").write_bytes(fc.frame_png(t))
        # 10) Xuat video
        out = odir / f"{name}.mp4"
        if export:
            # Phu de: in cung vao hinh (TikTok/Reels) + xuat kem .srt canh file mp4
            fc.run("export.quick", preset=tpl["xuat"]["preset"], path=str(out), wait=True,
                   burnCaptions=bool(cues), **({"captionSidecar": "srt"} if cues else {}))
    print(f"[OK] Dự án FilmCraft: {fcproj}")
    print(f"[OK] Ảnh kiểm tra: {', '.join(f'kiem-tra-{t:06.2f}s.png' for t in checks)} (thư mục build/)")
    if export:
        print(f"[OK] Video: {out} ({out.stat().st_size // 1024} KB)" if out.exists() else "[LỖI] Không thấy file xuất")
    return {"duration": total, "cuts": len(cuts), "captions": len(cues)}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--no-export", action="store_true")
    a = ap.parse_args()
    build(a.project, export=not a.no_export)
