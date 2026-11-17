# Ket noi 1 thiet bi BLE, liet ke service/characteristic, DOC cac gia tri doc duoc, nghe notify 10 s. KHONG GHI.
import asyncio, sys
from bleak import BleakClient

sys.stdout.reconfigure(encoding="utf-8")
ADDR = sys.argv[1]


def show(b):
    txt = "".join(chr(c) if 32 <= c < 127 else "." for c in b)
    return f"{b.hex(' ')}  |{txt}|"


async def main():
    async with BleakClient(ADDR, timeout=20.0) as c:
        print("connected:", c.is_connected, "mtu:", getattr(c, "mtu_size", "?"))
        notif = []
        for s in c.services:
            print(f"\nSERVICE {s.uuid}  ({s.description})")
            for ch in s.characteristics:
                print(f"  CHAR {ch.uuid} h={ch.handle} [{','.join(ch.properties)}] ({ch.description})")
                if "read" in ch.properties:
                    try:
                        print("     read:", show(await c.read_gatt_char(ch)))
                    except Exception as e:
                        print("     read loi:", type(e).__name__, e)
                for d in ch.descriptors:
                    print(f"     desc {d.uuid} h={d.handle}")
                if "notify" in ch.properties or "indicate" in ch.properties:
                    notif.append(ch)
        for ch in notif:
            try:
                await c.start_notify(ch, lambda h, data, u=ch.uuid: print(f"  NOTIFY {u}: {show(bytes(data))}"))
            except Exception as e:
                print("  notify loi", ch.uuid, type(e).__name__)
        if notif:
            print(f"\nNghe notify 10 s tren {len(notif)} characteristic (go dan/van num luc nay neu muon)...")
            await asyncio.sleep(10)


asyncio.run(main())
