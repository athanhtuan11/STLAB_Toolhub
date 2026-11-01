import json, sys, store

if len(sys.argv) != 4 or sys.argv[1] != "mark":
    print(json.dumps({"error": "usage"}))
    sys.exit(1)
try:
    i = int(sys.argv[2])
except ValueError:
    print(json.dumps({"error": "id"}))
    sys.exit(1)
s = sys.argv[3]
if s not in store.STATUSES or not store.set_status(i, s):
    print(json.dumps({"error": "invalid id or status"}))
    sys.exit(1)
print(json.dumps({"id": i, "status": s}, ensure_ascii=False))
