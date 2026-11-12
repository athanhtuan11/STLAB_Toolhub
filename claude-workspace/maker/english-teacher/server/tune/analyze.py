"""Phan tich runtime/live.log cho agent voice-tuner: dem barge/TUNE/nhac/phien, muc giong-nen, chi so, goi y chinh nguong.
Chay: python analyze.py [--log runtime/live.log] [--since HH:MM] [--json]
Chi doc log cuc bo, khong gui di dau. Chiu duoc byte NUL / ma hoa hong."""
import argparse
import json
import os
import re
import statistics
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parent.parent
TS = re.compile(r"^(\d\d):(\d\d):(\d\d)\s")


def read_lines(path):
    raw = Path(path).read_bytes().replace(b"\x00", b"")
    return raw.decode("utf-8", errors="ignore").splitlines()


def to_min(h, m, s=0):
    return int(h) * 60 + int(m) + int(s) / 60.0


def median(v):
    return round(statistics.median(v), 1) if v else None


def analyze(log_path, since=None):
    lines = read_lines(log_path) if Path(log_path).exists() else []
    since_min = None
    if since:
        m = re.match(r"^(\d{1,2}):(\d\d)$", since)
        if m:
            since_min = to_min(m.group(1), m.group(2))
    rep = {"log": str(log_path), "lines": 0, "barges": 0, "tune_changes": 0, "music_plays": 0, "sessions": 0}
    voice, noise, times = [], [], []
    metrics = []
    for ln in lines:
        mt = TS.match(ln)
        t = to_min(*mt.groups()) if mt else None
        if since_min is not None and (t is None or t < since_min):
            continue
        rep["lines"] += 1
        if t is not None:
            times.append(t)
        if "[BARGE]" in ln:
            rep["barges"] += 1
        if "[TUNE]" in ln and re.search(r"\[TUNE\]\s+(barge|voice)", ln):
            rep["tune_changes"] += 1
        if "[MUSIC] play" in ln:
            rep["music_plays"] += 1
        if "thiet bi ket noi" in ln:
            rep["sessions"] += 1
        if "[LIVE-LEVEL]" in ln:
            g = re.search(r"giong=(-?\d+(?:\.\d+)?)dBFS", ln)
            n = re.search(r"nen=(-?\d+(?:\.\d+)?)dBFS", ln)
            if g:
                voice.append(float(g.group(1)))
            if n:
                noise.append(float(n.group(1)))
        if "[LIVE-METRIC]" in ln:
            d = {}
            for k, v in re.findall(r"(\w+)=(-?\d+(?:\.\d+)?)", ln.split("[LIVE-METRIC]", 1)[1]):
                d[k] = float(v) if "." in v else int(v)
            if d:
                metrics.append(d)
    rep["levels"] = {"voice_dbfs_median": median(voice), "noise_dbfs_median": median(noise), "n": len(voice)}
    rep["metrics"] = metrics
    span = (max(times) - min(times)) if len(times) > 1 else 0.0
    rep["span_min"] = round(span, 1)
    tp = os.environ.get("STLAB_TUNING_PATH", "").strip()
    tpath = Path(tp) if tp else SERVER / "data" / "tuning.json"
    try:
        tj = json.loads(tpath.read_text(encoding="utf-8"))
        rep["tuning"] = tj.get("values", {})
    except (OSError, ValueError):
        rep["tuning"] = {}
    rep["suggestions"] = suggest(rep, voice, noise)
    return rep


def suggest(rep, voice, noise):
    s = []
    vm = rep["levels"]["voice_dbfs_median"]
    nm = rep["levels"]["noise_dbfs_median"]
    tgt = rep["tuning"].get("agc_target_dbfs", -18)
    if vm is not None:
        if vm < -20:
            s.append(f"giọng trung vị {vm:g} dBFS < -20 → tăng agc_target (hiện {tgt:g}) hoặc agc_max_gain_db")
        elif vm > -8:
            s.append(f"giọng trung vị {vm:g} dBFS > -8 → mic quá to, giảm agc_target hoặc xa mic hơn")
    if vm is not None and nm is not None and vm - nm < 15:
        s.append(f"giọng ({vm:g}) chỉ hơn nền ({nm:g}) {vm - nm:g} dB < 15 → nền ồn/xa mic, đừng tăng gain thêm")
    if rep["span_min"] >= 1:
        rate = rep["barges"] / rep["span_min"]
        if rate > 3:
            s.append(f"barge {rate:.1f} lần/phút > 3 → có thể tiếng vọng: nâng barge_threshold/barge_ms, kiểm AEC, chỉnh STLAB_AEC_REF_DELAY_MS")
    elif rep["barges"] > 3:
        s.append(f"barge {rep['barges']} lần trong < 1 phút → có thể tiếng vọng")
    if rep["barges"] and rep["tune_changes"] == 0:
        s.append("có barge nhưng chưa có lần tự chỉnh nào → kiểm [TUNE] / quyền ghi data/tuning.json")
    sess = rep["sessions"]
    if sess and rep["barges"] / sess > 6:
        s.append(f"trung bình {rep['barges'] / sess:.1f} barge/phiên → ngưỡng ngắt lời có thể quá thấp")
    t = rep["tuning"]
    if t.get("barge_threshold", 0) >= 0.94:
        s.append("barge_threshold sát trần 0.95 → bé có thể khó ngắt lời; xem lại AEC thay vì nâng tiếp")
    if t.get("barge_threshold", 1) <= 0.62:
        s.append("barge_threshold sát sàn 0.6 → dễ ngắt nhầm; kiểm bé có phải chạm nút nhiều không")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(SERVER / "runtime" / "live.log"))
    ap.add_argument("--since", default=None, help="HH:MM, chi tinh tu gio nay")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep = analyze(a.log, a.since)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.json:
        print(json.dumps(rep, ensure_ascii=False))
        return 0
    lv = rep["levels"]
    print(f"Log {rep['log']}: {rep['lines']} dòng, {rep['span_min']} phút")
    print(f"Phiên {rep['sessions']} | barge {rep['barges']} | tự chỉnh {rep['tune_changes']} | nhạc {rep['music_plays']}")
    print(f"Giọng trung vị {lv['voice_dbfs_median']} dBFS, nền {lv['noise_dbfs_median']} dBFS (n={lv['n']})")
    if rep["tuning"]:
        print("Ngưỡng hiện tại: " + ", ".join(f"{k}={v}" for k, v in rep["tuning"].items()))
    if rep["metrics"]:
        print("Chỉ số cuối: " + ", ".join(f"{k}={v}" for k, v in rep["metrics"][-1].items()))
    print("Gợi ý:" if rep["suggestions"] else "Gợi ý: không có")
    for x in rep["suggestions"]:
        print(" - " + x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
