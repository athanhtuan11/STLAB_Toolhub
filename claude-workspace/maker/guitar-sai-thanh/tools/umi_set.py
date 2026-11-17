# Dat 1 tham so cua dan GUITAR UMI qua BLE theo dung cach app Umi lam (docs/ble-protocol.md), roi (tuy chon) tra ve gia tri cu.
#   python umi_set.py <MAC> <byte> <gia_tri> [--hold 4] [--no-restore]
# Vd: python umi_set.py C5:B3:D4:AA:E8:CD 15 10   -> am luong 10 trong 4 s roi tra lai
import argparse, asyncio, sys
from bleak import BleakClient

sys.stdout.reconfigure(encoding="utf-8")
CMD = "00002b12-0000-1000-8000-00805f9b34fb"     # app -> dan (handle 0x000D)
STAT = "00002b10-0000-1000-8000-00805f9b34fb"    # dan -> app (notify)
HELLO = bytes.fromhex("55fffe01")                # app gui de xin trang thai
SAFE = {4: None, 8: (0, 30), 11: (0, 255), 15: (0, 30), 19: (0, 30), 20: (75, 100), 21: (0, 2), 22: (0, 1),
        25: (0, 30), 27: (0, 30), 45: (0, 1)}   # chi cho phep cac byte da giai ma + khoang da thay


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mac"); ap.add_argument("idx", type=int); ap.add_argument("val", type=int)
    ap.add_argument("--hold", type=float, default=4.0); ap.add_argument("--no-restore", action="store_true")
    a = ap.parse_args()
    rng = SAFE.get(a.idx)
    if rng is None or not (rng[0] <= a.val <= rng[1]):
        sys.exit(f"byte {a.idx} = {a.val} ngoai danh sach/khoang da giai ma {rng} - khong gui")
    latest = {}
    ev = asyncio.Event()

    def on(_h, data):
        b = bytes(data)
        if len(b) >= 46 and b[0] == 0x03 and b[1] == 0x10:
            latest["s"] = b; ev.set()

    async with BleakClient(a.mac, timeout=20.0) as c:
        await c.start_notify(STAT, on)
        await c.write_gatt_char(CMD, HELLO, response=True)
        await asyncio.wait_for(ev.wait(), 5)
        st = latest["s"]
        old = st[a.idx]
        print(f"trang thai: pin {st[4]/10:.1f} V | am luong {st[15]} am sac {st[19]} echo {st[27]} | byte[{a.idx}] = {old}")

        def frame(v):
            f = bytearray(129)
            f[0:8] = bytes.fromhex("0300010000000000")
            f[8:len(st)] = st[8:129]
            f[a.idx] = v
            return bytes(f)

        await c.write_gatt_char(CMD, frame(a.val), response=True)
        print(f"DA GUI byte[{a.idx}] = {a.val}")
        await asyncio.sleep(1.0)
        ev.clear(); await c.write_gatt_char(CMD, HELLO, response=True); await asyncio.wait_for(ev.wait(), 5)
        print(f"dan bao lai byte[{a.idx}] = {latest['s'][a.idx]}  ({'OK' if latest['s'][a.idx] == a.val else 'KHAC'})")
        await asyncio.sleep(a.hold)
        if not a.no_restore:
            await c.write_gatt_char(CMD, frame(old), response=True)
            ev.clear(); await c.write_gatt_char(CMD, HELLO, response=True); await asyncio.wait_for(ev.wait(), 5)
            print(f"TRA VE byte[{a.idx}] = {old} -> dan bao {latest['s'][a.idx]}")


asyncio.run(main())
