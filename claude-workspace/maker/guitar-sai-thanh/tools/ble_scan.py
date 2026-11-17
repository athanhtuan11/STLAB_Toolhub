# Quet BLE 15 s, in thiet bi theo RSSI (chi doc, khong ket noi).
import asyncio, sys
from bleak import BleakScanner

sys.stdout.reconfigure(encoding="utf-8")


async def main():
    found = await BleakScanner.discover(timeout=15.0, return_adv=True)
    rows = []
    for addr, (dev, adv) in found.items():
        rows.append((adv.rssi, addr, adv.local_name or dev.name or "", adv))
    rows.sort(key=lambda r: r[0], reverse=True)
    for rssi, addr, name, adv in rows[:25]:
        manu = {f"0x{k:04X}": v.hex() for k, v in adv.manufacturer_data.items()}
        print(f"{rssi:>4} dBm | {addr} | {name!r} | svc={adv.service_uuids} | manu={manu} | tx={adv.tx_power}")


asyncio.run(main())
