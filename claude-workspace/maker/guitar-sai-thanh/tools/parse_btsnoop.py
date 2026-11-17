# Doc btsnoop (H4), in cac goi ATT ghi (0x12 write req, 0x52 write cmd) + 1 so notify (0x1B), kem gio unix.
import struct, sys
sys.stdout.reconfigure(encoding="utf-8")
path = sys.argv[1]
OFF = 0x00DCDDB30F2F8000  # us tu nam 0 -> 1970
data = open(path, "rb").read()
assert data[:8] == b"btsnoop\0", "khong phai btsnoop"
i, n_notify = 16, 0
while i + 24 <= len(data):
    orig, incl, flags, drops, ts = struct.unpack(">IIIIq", data[i:i + 24])
    pkt = data[i + 24:i + 24 + incl]
    i += 24 + incl
    if not pkt or pkt[0] != 0x02 or len(pkt) < 10:   # chi ACL
        continue
    hdl, alen = struct.unpack("<HH", pkt[1:5])
    l2len, cid = struct.unpack("<HH", pkt[5:9])
    if cid != 0x0004:
        continue
    att = pkt[9:]
    op = att[0]
    t = (ts - OFF) / 1e6
    sent = (flags & 1) == 0   # bit0 = 0: host -> controller (dien thoai gui di)
    if op in (0x12, 0x52) and len(att) >= 3:
        h = struct.unpack("<H", att[1:3])[0]
        print(f"{t:.3f} {'TX' if sent else 'RX'} WRITE{'' if op == 0x12 else '-CMD'} h=0x{h:04x} len={len(att)-3}: {att[3:].hex(' ')}")
    elif op == 0x1B and len(att) >= 3 and n_notify < 3:
        n_notify += 1
        h = struct.unpack("<H", att[1:3])[0]
        print(f"{t:.3f} NOTIFY h=0x{h:04x} len={len(att)-3}: {att[3:40].hex(' ')} ...")
