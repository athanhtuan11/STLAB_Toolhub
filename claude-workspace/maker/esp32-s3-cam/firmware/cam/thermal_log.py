# Do nhiet theo thoi gian qua /status (Claude viet, executor KHONG sua).
# python thermal_log.py --host stlab-cam.local --min 15 --out thermal-<ten>.csv
import argparse, csv, json, sys, time, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser()
ap.add_argument("--host", default="stlab-cam.local")
ap.add_argument("--min", type=float, default=15)
ap.add_argument("--every", type=float, default=10)
ap.add_argument("--out", required=True)
a = ap.parse_args()
keys = ["nhiet_do_chip", "so_nguoi_xem", "fps_thuc", "motion", "cam_sleep", "ap_on", "wifi_ps", "uptime_s", "version"]
rows, t0 = [], time.time()
with open(a.out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["t_s"] + keys)
    while time.time() - t0 < a.min * 60:
        try:
            with urllib.request.urlopen("http://%s/status" % a.host, timeout=5) as r:
                s = json.loads(r.read())
            row = [round(time.time() - t0)] + [s.get(k) for k in keys]
            w.writerow(row); f.flush(); rows.append(s)
            print(*row, flush=True)
        except Exception as e:
            print("loi", e, flush=True)
        time.sleep(a.every)
temps = [r.get("nhiet_do_chip") for r in rows if isinstance(r.get("nhiet_do_chip"), (int, float))]
if temps:
    tail = temps[-max(1, len(temps) // 5):]
    viewers = max(r.get("so_nguoi_xem", 0) or 0 for r in rows)
    print("TOM TAT: dau %.1f C, cuoi(TB 20%% cuoi) %.1f C, max %.1f C, nguoi xem toi da %d, %d mau"
          % (temps[0], sum(tail) / len(tail), max(temps), viewers, len(temps)))
