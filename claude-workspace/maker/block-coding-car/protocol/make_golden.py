#!/usr/bin/env python3
"""Ban tham chieu cua PROTOCOL.md (muc 1-3) -> sinh golden.json cho gate firmware + app.

python make_golden.py          # ghi golden.json
python make_golden.py --check  # exit 1 neu golden.json khac ban sinh (quen chay lai)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPS = {"fwd": (1, 4, 1), "back": (1, 4, 1), "left": None, "right": None,
       "sound": (0, 2, 0), "eye": (0, 5, 0), "repeat": (2, 4, 2)}
MAX_BLOCKS, MAX_BODY = 12, 6  # toi da 40 buoc (2 repeat x4, body 6+4)


class ProgError(Exception):
    pass


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def expand(doc):
    """doc = dict chuong trinh -> list buoc [id, op, arg]; loi -> ProgError(code)."""
    if not isinstance(doc, dict) or "prog" not in doc:
        raise ProgError("bad_json")
    if doc.get("v") != 1:
        raise ProgError("bad_version")
    prog = doc["prog"]
    if not isinstance(prog, list):
        raise ProgError("bad_json")
    if not prog:
        raise ProgError("empty")
    ids, count = set(), [0]

    def check(blk, inside):
        if not isinstance(blk, dict):
            raise ProgError("bad_json")
        op = blk.get("op")
        if op not in OPS:
            raise ProgError("bad_op")
        bid = blk.get("id")
        if not _is_int(bid) or not 0 <= bid <= 999:
            raise ProgError("bad_arg")
        if bid in ids:
            raise ProgError("dup_id")
        ids.add(bid)
        count[0] += 1
        rng = OPS[op]
        arg = 0
        if rng:
            lo, hi, dflt = rng
            n = blk.get("n", dflt)
            if not _is_int(n) or not lo <= n <= hi:
                raise ProgError("bad_arg")
            arg = n
        if op == "repeat":
            if inside:
                raise ProgError("nested_repeat")
            body = blk.get("body")
            if not isinstance(body, list) or not body:
                raise ProgError("empty_repeat")
            if len(body) > MAX_BODY:
                raise ProgError("too_many_blocks")
            body_steps = []
            for b in body:
                body_steps += check(b, True)
            return body_steps * arg
        return [[bid, op, arg]]

    steps = []
    for b in prog:
        steps += check(b, False)
    if count[0] > MAX_BLOCKS:
        raise ProgError("too_many_blocks")
    return steps


DIRS = "NESW"
DXY = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def simulate(steps, start=(0, 5, "N"), size=6):
    x, y, h = start
    trace, edge = [], None
    for bid, op, arg in steps:
        if op in ("fwd", "back"):
            dx, dy = DXY[h]
            if op == "back":
                dx, dy = -dx, -dy
            for _ in range(arg):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < size and 0 <= ny < size):
                    edge = bid
                    break
                x, y = nx, ny
        elif op == "left":
            h = DIRS[(DIRS.index(h) + 3) % 4]
        elif op == "right":
            h = DIRS[(DIRS.index(h) + 1) % 4]
        trace.append([x, y, h])
        if edge is not None:
            break
    return {"trace": trace, "final": [x, y, h], "edge": edge}


def B(i, op, n=None, body=None):
    d = {"id": i, "op": op}
    if n is not None:
        d["n"] = n
    if body is not None:
        d["body"] = body
    return d


VALID = [
    ("tien-1", [B(0, "fwd")]),
    ("cap1-hinh-chu-L", [B(0, "fwd"), B(1, "fwd"), B(2, "right"), B(3, "fwd")]),
    ("quay-du-vong", [B(0, "left"), B(1, "left"), B(2, "left"), B(3, "left")]),
    ("lui-trong-luoi", [B(0, "fwd", 3), B(1, "back", 2)]),
    ("so-o-3", [B(0, "fwd", 3), B(1, "right"), B(2, "fwd", 4)]),
    ("lap-hinh-vuong", [B(0, "repeat", 4, [B(1, "fwd", 2), B(2, "right")])]),
    ("lap-mac-dinh-2", [B(0, "repeat", None, [B(1, "fwd")]), B(2, "sound", 1)]),
    ("am-thanh-den", [B(0, "eye", 3), B(1, "sound"), B(2, "fwd"), B(3, "eye", 5), B(4, "sound", 2)]),
    ("cham-mep-tren", [B(0, "fwd", 4), B(1, "fwd", 2), B(2, "right")]),
    ("lui-ra-mep-ngay", [B(0, "back"), B(1, "fwd")]),
    ("trai-roi-tien-ra-mep", [B(0, "left"), B(1, "fwd")]),
    ("mep-trong-lap", [B(0, "right"), B(1, "repeat", 4, [B(2, "fwd", 2), B(3, "sound")])]),
    ("id-khong-lien-tuc", [B(7, "fwd"), B(42, "right"), B(999, "back")]),
    ("khoa-la-bo-qua", [{"id": 0, "op": "fwd", "n": 1, "color": "blue"}, {"id": 1, "op": "left", "n": 3}]),
    ("du-12-khoi", [B(i, "right") for i in range(10)] + [B(10, "repeat", 2, [B(11, "eye", 1)])]),
    ("du-40-buoc", [B(0, "repeat", 4, [B(i, "sound") for i in range(1, 7)]),
                    B(7, "repeat", 4, [B(i, "eye", 2) for i in range(8, 12)])]),
]

INVALID = [
    ("rong", {"v": 1, "prog": []}, "empty"),
    ("sai-phien-ban", {"v": 2, "prog": [B(0, "fwd")]}, "bad_version"),
    ("thieu-prog", {"v": 1}, "bad_json"),
    ("op-la", {"v": 1, "prog": [B(0, "jump")]}, "bad_op"),
    ("n-qua-lon", {"v": 1, "prog": [B(0, "fwd", 5)]}, "bad_arg"),
    ("n-chuoi", {"v": 1, "prog": [{"id": 0, "op": "fwd", "n": "2"}]}, "bad_arg"),
    ("n-so-thuc", {"v": 1, "prog": [{"id": 0, "op": "eye", "n": 1.5}]}, "bad_arg"),
    ("am-thanh-3", {"v": 1, "prog": [B(0, "sound", 3)]}, "bad_arg"),
    ("lap-1", {"v": 1, "prog": [B(0, "repeat", 1, [B(1, "fwd")])]}, "bad_arg"),
    ("thieu-id", {"v": 1, "prog": [{"op": "fwd"}]}, "bad_arg"),
    ("id-1000", {"v": 1, "prog": [B(1000, "fwd")]}, "bad_arg"),
    ("trung-id-trong-lap", {"v": 1, "prog": [B(0, "fwd"), B(1, "repeat", 2, [B(0, "left")])]}, "dup_id"),
    ("lap-rong", {"v": 1, "prog": [B(0, "repeat", 2, [])]}, "empty_repeat"),
    ("lap-thieu-body", {"v": 1, "prog": [B(0, "repeat", 2)]}, "empty_repeat"),
    ("lap-long", {"v": 1, "prog": [B(0, "repeat", 2, [B(1, "repeat", 2, [B(2, "fwd")])])]}, "nested_repeat"),
    ("body-7", {"v": 1, "prog": [B(0, "repeat", 2, [B(i, "left") for i in range(1, 8)])]}, "too_many_blocks"),
    ("13-khoi", {"v": 1, "prog": [B(i, "left") for i in range(13)]}, "too_many_blocks"),
]


def build():
    cases = []
    for name, prog in VALID:
        doc = {"v": 1, "prog": prog}
        steps = expand(doc)
        cases.append({"name": name, "doc": doc, "ok": True, "steps": steps, "sim": simulate(steps)})
    for name, doc, code in INVALID:
        try:
            expand(doc)
        except ProgError as e:
            assert str(e) == code, (name, str(e), code)
            cases.append({"name": name, "doc": doc, "ok": False, "code": code})
            continue
        raise AssertionError(f"{name}: khong loi, can {code}")
    return {"_note": "Sinh tu make_golden.py theo PROTOCOL.md - KHONG sua tay.",
            "start": [0, 5, "N"], "size": 6, "cases": cases}


def main():
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    out = HERE / "golden.json"
    if "--check" in sys.argv:
        ok = out.exists() and out.read_text(encoding="utf-8") == text
        print("golden.json", "OK" if ok else "CU - chay lai make_golden.py")
        sys.exit(0 if ok else 1)
    out.write_text(text, encoding="utf-8")
    print(f"golden.json: {len(data['cases'])} ca")


if __name__ == "__main__":
    main()
