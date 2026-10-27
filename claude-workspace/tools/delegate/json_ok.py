# Dung trong lenh gate: exit 0 neu khoa <key> trong file JSON la true, nguoc lai exit 1 (in summary neu co).
#   python json_ok.py gate.json passed
import json, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
print(sys.argv[1], d.get("summary", ""), "->", d.get(sys.argv[2]))
sys.exit(0 if d.get(sys.argv[2]) is True else 1)
