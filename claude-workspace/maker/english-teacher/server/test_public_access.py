# Gate truy cap tu internet (Claude viet 2026-11-11). Offline, khong can bo/Gemini:
#   runtime\.venv\Scripts\python.exe -X utf8 test_public_access.py
import asyncio, json, os, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="public-access-"))
os.environ.setdefault("GOOGLE_API_KEY", "x")
os.environ["STLAB_LEARNERS_PATH"] = str(TMP / "learners.json")
for k in ("STLAB_PUBLIC_HOST", "STLAB_DEVICE_TOKEN", "STLAB_ALLOWED_DEVICES"):
    os.environ.pop(k, None)
os.environ["STLAB_XIAOZHI_SERVER"] = "192.168.1.56"
sys.path.insert(0, str(HERE / "live"))
import bridge  # noqa: E402
from aiohttp.test_utils import make_mocked_request  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def ota(headers):
    req = make_mocked_request("GET", "/xiaozhi/ota/", headers=headers)
    r = asyncio.run(bridge.ota_handler(req))
    return r.status, (json.loads(r.body) if r.body else {})


MAC = "e0:8c:fe:64:20:a4"
TOKEN = "t" * 32

# 1) Mac dinh (LAN, khong bien moi): giu hanh vi cu
s, b = ota({"Device-Id": MAC})
check(s == 200 and b["websocket"]["url"] == "ws://192.168.1.56:8000/xiaozhi/v1/", f"LAN: url cu ({b})")
check(b["websocket"]["token"] == "", "LAN: token rong")
check(bridge.authorize({"Device-Id": MAC}), "LAN: khong token -> cho vao")
bridge.check_public_config()  # khong raise

# 2) Bat domain thieu token / danh sach -> dung han
os.environ["STLAB_PUBLIC_HOST"] = "teacher.example.vn"
for env in ({}, {"STLAB_DEVICE_TOKEN": TOKEN}, {"STLAB_ALLOWED_DEVICES": MAC},
            {"STLAB_DEVICE_TOKEN": "ngan", "STLAB_ALLOWED_DEVICES": MAC}):
    for k in ("STLAB_DEVICE_TOKEN", "STLAB_ALLOWED_DEVICES"):
        os.environ.pop(k, None)
    os.environ.update(env)
    try:
        bridge.check_public_config()
        check(False, f"thieu khoa {sorted(env)} -> phai SystemExit")
    except SystemExit:
        pass

# 3) Cau hinh day du
os.environ["STLAB_DEVICE_TOKEN"] = TOKEN
os.environ["STLAB_ALLOWED_DEVICES"] = MAC.upper() + ", aa:bb:cc:dd:ee:ff"
bridge.check_public_config()
s, b = ota({"Device-Id": MAC})
check(s == 200 and b["websocket"]["url"] == "wss://teacher.example.vn/xiaozhi/v1/", f"public: wss url ({b})")
check(b["websocket"]["token"] == TOKEN, "public: OTA tra token cho bo hop le")
s, b = ota({"Device-Id": "11:22:33:44:55:66"})
check(s == 403 and "websocket" not in b, "OTA bo la -> 403, khong lo token")
s, b = ota({})
check(s == 403, "OTA khong Device-Id -> 403")

ok_h = {"Device-Id": MAC, "Authorization": "Bearer " + TOKEN}
check(bridge.authorize(ok_h), "WS dung token + bo hop le -> vao")
check(bridge.authorize({"device-id": MAC, "authorization": TOKEN}), "WS token khong 'Bearer' van nhan")
check(not bridge.authorize({"Device-Id": MAC}), "WS thieu token -> chan")
check(not bridge.authorize({"Device-Id": MAC, "Authorization": "Bearer sai"}), "WS sai token -> chan")
check(not bridge.authorize({"Device-Id": "11:22:33:44:55:66", "Authorization": "Bearer " + TOKEN}), "WS bo la dung token -> chan")

src = (HERE / "live" / "bridge.py").read_text(encoding="utf-8")
check("authorize(h)" in src and "close(code=4401" in src, "ws_handler phai goi authorize truoc Session")
check("check_public_config()" in src.split("async def main():")[1][:600], "main() phai goi check_public_config")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_public_access")
