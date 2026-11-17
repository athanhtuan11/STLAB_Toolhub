# Nghe notify cua GUITAR UMI trong N giay, ghi moc thoi gian + chi cac byte THAY DOI so voi goi truoc. KHONG GHI vao dan.
import asyncio, sys, time
from bleak import BleakClient

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
ADDR, SECS = sys.argv[1], float(sys.argv[2])
CHARS = ["00002b10-0000-1000-8000-00805f9b34fb", "00002b16-0000-1000-8000-00805f9b34fb"]
last = {}
t0 = time.time()


def on(uuid):
    def cb(_h, data):
        b = bytes(data)
        t = time.time() - t0
        prev = last.get(uuid)
        if prev is None:
            print(f"{t:6.1f}s {uuid[4:8]} FULL len={len(b)}: {b.hex(' ')}")
        elif b != prev:
            diff = [f"[{i}] {prev[i] if i < len(prev) else '-'}->{b[i]}" for i in range(len(b)) if i >= len(prev) or prev[i] != b[i]]
            print(f"{t:6.1f}s {uuid[4:8]} DOI: {', '.join(diff)}")
        else:
            print(f"{t:6.1f}s {uuid[4:8]} (lap lai)")
        last[uuid] = b
    return cb


async def main():
    async with BleakClient(ADDR, timeout=20.0) as c:
        print(f"connected, nghe {SECS:.0f} s ...")
        for u in CHARS:
            await c.start_notify(u, on(u))
        await asyncio.sleep(SECS)
        print("HET GIO")


asyncio.run(main())
