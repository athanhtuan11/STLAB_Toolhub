"""Thu micro tu bo ESP32-A1S qua UART, ghi WAV. Dung: python rec.py --port COM5 --sec 4 --in 1 --out rec-in1.wav [--tone]"""
import argparse, base64, sys, threading, time, wave, zlib

import serial

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def beep_thread(ms, delay):
    time.sleep(delay)
    try:
        import winsound
        winsound.Beep(1000, ms)
    except Exception as e:  # khong co thiet bi am thanh
        print("[tone] khong phat duoc loa PC:", e)


def analyze(path, in_):
    import numpy as np
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(float)
    x = x[int(0.3 * sr):] if len(x) > sr else x
    x = x - x.mean()
    rms = float(np.sqrt((x ** 2).mean()))
    peak = int(np.abs(x).max()) if len(x) else 0
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x), 1 / sr)
    band = (f >= 900) & (f <= 1100)
    valid = f >= 100
    peak_hz = float(f[valid][np.argmax(spec[valid])])
    e_band = spec[band].sum()
    e_rest = spec[valid & ~band].sum()
    # so sanh mat do nang luong (moi Hz) cho cong bang
    dens_band = e_band / max(band.sum(), 1)
    dens_rest = e_rest / max((valid & ~band).sum(), 1)
    snr = 10 * np.log10((dens_band + 1e-9) / (dens_rest + 1e-9))
    line = "[KQ-MIC] in=%d rms=%.1f peak=%d peak_hz=%.0f snr_1k_db=%.1f" % (in_, rms, peak, peak_hz, snr)
    print(line)
    return line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="COM5")
    ap.add_argument("--sec", type=int, default=4)
    ap.add_argument("--in", dest="inp", type=int, default=1, choices=[1, 2])
    ap.add_argument("--out", default="rec.wav")
    ap.add_argument("--tone", action="store_true")
    a = ap.parse_args()
    p = serial.Serial()
    p.port, p.baudrate, p.timeout = a.port, 115200, 1
    p.dtr = False; p.rts = False   # tranh reset bo khi mo cong (EN/IO0 qua DTR/RTS)
    p.open()
    p.reset_input_buffer()
    p.write(("REC %d %d\n" % (a.sec, a.inp)).encode())
    if a.tone:
        threading.Thread(target=beep_thread, args=(int(a.sec * 1000 - 1000), 0.5 + 0.3), daemon=True).start()
    deadline = time.time() + a.sec + 20 + a.sec * 8
    nbytes, data, in_block, crc_hex = 0, [], False, None
    while time.time() < deadline:
        ln = p.readline().decode("utf-8", "replace").strip()
        if ln.startswith("[REC] BEGIN"):
            nbytes = int(ln.split()[2]); in_block = True; data = []
        elif ln.startswith("[REC] END"):
            crc_hex = ln.split()[2]; break
        elif in_block and ln and not ln.startswith("["):
            data.append(ln)
    if crc_hex is None:
        print("LOI: khong nhan duoc khoi [REC] END"); sys.exit(1)
    raw = base64.b64decode("".join(data))
    crc = "%08x" % (zlib.crc32(raw) & 0xFFFFFFFF)
    ok = crc == crc_hex.lower() and len(raw) == nbytes
    print("[REC] %d byte, crc %s (bo gui %s) -> %s" % (len(raw), crc, crc_hex, "OK" if ok else "SAI"))
    if not ok:
        sys.exit(1)
    with wave.open(a.out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(raw)
    print("da ghi", a.out)
    analyze(a.out, a.inp)


if __name__ == "__main__":
    main()
