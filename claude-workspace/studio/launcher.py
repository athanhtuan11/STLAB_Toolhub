"""STLab Studio launcher: mo ung dung (FreeCAD, Blender, LightCraft, PhotoCraft) va kiem tra MCP.

Chi dung thu vien chuan: cac file .bat goi truc tiep, app.py (Flask) import lai.
Cau hinh ung dung o apps.json, cau hinh MCP o .mcp.json (cung file Claude Code doc).

    python launcher.py status
    python launcher.py start <id|all>
    python launcher.py mcp-check <ten|all>
    python launcher.py claude
"""
import json
import os
import queue
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

STUDIO = Path(__file__).resolve().parent
CONFIG = STUDIO / "apps.json"
MCP_JSON = STUDIO / ".mcp.json"
WIN = sys.platform == "win32"
NO_WINDOW = subprocess.CREATE_NO_WINDOW if WIN else 0


def load_config():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    v = {
        "studio": STUDIO.as_posix(),
        "localappdata": os.environ.get("LOCALAPPDATA", "").replace("\\", "/"),
        "userprofile": os.environ.get("USERPROFILE", "").replace("\\", "/"),
    }
    v["media"] = cfg["media_dir"].format(**v)
    cfg["media_dir"] = v["media"]
    if "claude_desktop" in cfg:
        cfg["claude_desktop"]["config"] = cfg["claude_desktop"]["config"].format(**v)
    for a in cfg["apps"]:
        a["exe"] = a["exe"].format(**v)
        a["args"] = [s.format(**v) for s in a.get("args", [])]
    return cfg


def get_app(app_id):
    for a in load_config()["apps"]:
        if a["id"] == app_id:
            return a
    raise KeyError(f"Không có ứng dụng '{app_id}' trong apps.json")


def port_open(port, timeout=0.3):
    try:
        with socket.create_connection(("localhost", port), timeout=timeout):
            return True
    except OSError:
        return False


def process_running(image):
    if not WIN:
        return False
    out = subprocess.run(
        ["tasklist", "/FI", f"IMAGENAME eq {image}", "/NH", "/FO", "CSV"],
        capture_output=True, text=True, creationflags=NO_WINDOW,
    ).stdout
    return image.lower() in out.lower()


def running_images():
    """Ten exe dang chay (chu thuong) - 1 lan goi tasklist cho moi ung dung, thay vi 1 lan / ung dung."""
    if not WIN:
        return set()
    out = subprocess.run(["tasklist", "/NH", "/FO", "CSV"], capture_output=True, text=True,
                         creationflags=NO_WINDOW).stdout
    return {ln.split('","')[0].strip('"').lower() for ln in out.splitlines() if ln}


def status():
    from concurrent.futures import ThreadPoolExecutor
    apps = load_config()["apps"]
    imgs = running_images()
    with ThreadPoolExecutor(len(apps) or 1) as ex:  # cong dong -> cho timeout song song
        nghe = list(ex.map(lambda a: port_open(a["port"]), apps))
    return [{"id": a["id"], "name": a["name"], "port": a["port"], "mcp": a.get("mcp"), "note": a.get("note", ""),
             "installed": Path(a["exe"]).exists(), "running": a["image"].lower() in imgs, "listening": n}
            for a, n in zip(apps, nghe)]


def start(app_id, wait=90, pair=None, extra_args=()):
    """Mo ung dung (neu cong chua mo), cho cong san sang, roi xep canh Claude Desktop (neu bat layout).
    extra_args: them vao cuoi lenh (vd. file can mo - nut "mo bang phan mem goc", toolhub/opener.py)."""
    r = _start(app_id, wait, extra_args)
    layout = load_config().get("layout", {})
    if r["ok"] and (layout.get("enabled") if pair is None else pair):
        lr = arrange(app_id)
        r = {"ok": r["ok"], "msg": f"{r['msg']}. {lr['msg']}"}
    return r


def _start(app_id, wait=90, extra_args=()):
    """Mo ung dung neu cong chua mo, roi cho cong san sang. Tra ve {ok, msg}."""
    cfg = load_config()
    a = get_app(app_id)
    if not Path(a["exe"]).exists():
        return {"ok": False, "msg": f"{a['name']}: chưa cài ({a['exe']})"}
    if port_open(a["port"]):
        return {"ok": True, "msg": f"{a['name']}: đã chạy, cổng {a['port']} sẵn sàng cho MCP"}
    if a.get("single_instance") and process_running(a["image"]):
        return {"ok": False, "msg": f"{a['name']}: đang mở nhưng chưa bật cổng điều khiển. "
                                    "Đóng app rồi mở lại bằng launcher."}
    Path(cfg["media_dir"]).mkdir(parents=True, exist_ok=True)
    (Path(os.environ.get("LOCALAPPDATA", STUDIO)) / "stlab-studio").mkdir(parents=True, exist_ok=True)
    env = {**os.environ, **a.get("env", {})}
    for k in a.get("env_unset", []):  # vd. DEBUG: RobotCAD mo debugpy tren 0.0.0.0:5678 neu co bien nay
        env.pop(k, None)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP) if WIN else 0
    subprocess.Popen(
        [a["exe"], *a["args"], *extra_args], cwd=str(Path(a["exe"]).parent), env=env, creationflags=flags,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True,
    )
    deadline = time.time() + wait
    while time.time() < deadline:
        if port_open(a["port"]):
            return {"ok": True, "msg": f"{a['name']}: đã mở, cổng {a['port']} sẵn sàng cho MCP"}
        time.sleep(1)
    return {"ok": False, "msg": f"{a['name']}: đã mở nhưng sau {wait} s cổng {a['port']} vẫn đóng. "
                                "Kiểm tra addon/cài đặt MCP trong app."}


def _expand(s):
    # Giong Claude Code: ${VAR} va ${VAR:-mac-dinh}
    return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}",
                  lambda m: os.environ.get(m.group(1), m.group(2) or ""), s)


# Tool CHI DOC dung de xac nhan MCP server da noi vao app dang chay (khong sua gi trong app).
PROBES = {
    "freecad": "list_documents",
    "blender": "get_scene_info",
    "lightcraft": "ui_inspect",
    "photocraft": "session_list",
    "filmcraft": "ui_inspect",
}


def mcp_servers():
    return json.loads(MCP_JSON.read_text(encoding="utf-8"))["mcpServers"]


def mcp_check(name, timeout=120):
    """Chay MCP server nhu Claude Code, gui initialize + tools/list. Tra ve {ok, msg, tools}."""
    srv = mcp_servers()[name]
    cmd = [_expand(srv["command"]), *[_expand(x) for x in srv.get("args", [])]]
    env = {**os.environ, **{k: _expand(v) for k, v in srv.get("env", {}).items()}}
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             env=env, cwd=str(STUDIO), creationflags=NO_WINDOW)
    except OSError as e:
        return {"ok": False, "msg": f"{name}: không chạy được lệnh MCP ({e})", "tools": []}
    lines = queue.Queue()
    threading.Thread(target=lambda: [lines.put(ln) for ln in p.stdout], daemon=True).start()

    def send(obj):
        p.stdin.write((json.dumps(obj) + "\n").encode("utf-8"))
        p.stdin.flush()

    def wait_for(msg_id, deadline):
        while time.time() < deadline:
            try:
                line = lines.get(timeout=0.5)
            except queue.Empty:
                if p.poll() is not None:
                    return None
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if msg.get("id") == msg_id:
                return msg
        return None

    deadline = time.time() + timeout
    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "stlab-studio-check", "version": "0.1"}}})
        init = wait_for(1, deadline)
        if not init or "result" not in init:
            return {"ok": False, "msg": f"{name}: server không trả lời initialize", "tools": []}
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        res = wait_for(2, deadline)
        if not res or "result" not in res:
            return {"ok": False, "msg": f"{name}: không lấy được danh sách tool", "tools": []}
        tools = [t["name"] for t in res["result"].get("tools", [])]
        info = init["result"].get("serverInfo", {})
        head = f"{name}: {info.get('name', '?')} {info.get('version', '')}, {len(tools)} tool"
        probe = PROBES.get(name)
        if probe not in tools:
            return {"ok": True, "tools": tools, "msg": f"{head} (không có tool kiểm tra kết nối app)"}
        send({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": probe, "arguments": {}}})
        call = wait_for(3, deadline)
        text = ""
        if call and "result" in call:
            text = " ".join(c.get("text", "") for c in call["result"].get("content", []))[:200]
        # Mot so server (Blender) tra loi loi duoi dang van ban ma khong dat isError.
        failed = (not call or "result" not in call or call["result"].get("isError")
                  or re.search(r"^\s*error|could not connect|not reachable|cannot connect", text, re.I))
        if failed:
            return {"ok": False, "tools": tools, "msg": f"{head}, nhưng chưa nối được app ({probe}): {text}"}
        return {"ok": True, "tools": tools, "msg": f"{head}, đã nối app ({probe} OK)"}
    except OSError as e:
        return {"ok": False, "msg": f"{name}: lỗi kết nối stdio ({e})", "tools": []}
    finally:
        p.kill()


# ---------- Claude Desktop: mo, xep cua so, dong bo MCP ----------
def ensure_claude_desktop(timeout=60):
    """Tra ve hwnd cua so Claude Desktop; mo app neu chua chay."""
    import winlayout
    cd = load_config()["claude_desktop"]
    h = winlayout.find_window(cd["image"], cd["path_contains"])
    if h:
        return h
    subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{cd['aumid']}"], creationflags=NO_WINDOW)
    return winlayout.wait_window(cd["image"], cd["path_contains"], timeout)


def arrange(app_id):
    """Xep ung dung mot ben, Claude Desktop mot ben (theo `layout` trong apps.json)."""
    if not WIN:
        return {"ok": False, "msg": "Chỉ hỗ trợ Windows"}
    import winlayout
    cfg = load_config()
    lay = cfg.get("layout", {})
    a = get_app(app_id)
    app_h = winlayout.wait_window(a["image"], timeout=45)
    if not app_h:
        return {"ok": False, "msg": f"Không tìm thấy cửa sổ {a['name']} để xếp"}
    cl_h = ensure_claude_desktop()
    if not cl_h:
        return {"ok": False, "msg": "Không mở được Claude Desktop"}
    ok = winlayout.split(app_h, cl_h, lay.get("app_side", "left"), lay.get("app_ratio", 0.6), lay.get("monitor", 0))
    side = "bên trái" if lay.get("app_side", "left") == "left" else "bên phải"
    if not ok:
        return {"ok": False, "msg": f"Đã thử xếp {a['name']} và Claude Desktop nhưng một cửa sổ không nhận vị trí mới"}
    return {"ok": True, "msg": f"Đã xếp {a['name']} {side}, Claude Desktop bên còn lại"}


def _norm(v):
    return json.dumps(v, sort_keys=True).replace("\\\\", "/")


def _desktop_entries():
    """Muc MCP cho Claude Desktop tu .mcp.json: Desktop khong mo rong ${VAR} -> ghi duong dan tuyet doi."""
    out = {}
    for name, srv in mcp_servers().items():
        cmd = _expand(srv["command"])
        if os.sep not in cmd and "/" not in cmd:  # vd. "uvx": dung duong dan day du (app GUI co PATH khac)
            cmd = shutil.which(cmd) or cmd
        e = {"command": cmd.replace("/", "\\"), "args": [_expand(x) for x in srv.get("args", [])]}
        if srv.get("env"):
            e["env"] = {k: _expand(v) for k, v in srv["env"].items()}
        out[name] = e
    return out


def desktop_status():
    """So sanh MCP trong Claude Desktop voi .mcp.json: moi server la 'khop', 'khac' hoac 'thieu'."""
    path = Path(load_config()["claude_desktop"]["config"])
    have = json.loads(path.read_text(encoding="utf-8")).get("mcpServers", {}) if path.exists() else {}
    rows = []
    for name, want in _desktop_entries().items():
        st = "thieu" if name not in have else ("khop" if _norm(have[name]) == _norm(want) else "khac")
        rows.append({"name": name, "state": st})
    extra = sorted(set(have) - {r["name"] for r in rows})
    return {"path": str(path), "rows": rows, "extra": extra}


def desktop_sync():
    """Ghi 4 MCP server vao cau hinh Claude Desktop. Sao luu truoc; khong dung toi server/cai dat khac.

    Claude Desktop phai DANG TAT (no co the ghi de file khi dang chay). Dong bo xong thi mo lai Desktop.
    """
    import winlayout
    cd = load_config()["claude_desktop"]
    if winlayout.find_window(cd["image"], cd["path_contains"]) or process_running_path(cd["path_contains"]):
        return {"ok": False, "msg": "Claude Desktop đang chạy. Thoát hẳn (khay hệ thống → Quit) rồi đồng bộ lại."}
    path = Path(cd["config"])
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    servers = data.setdefault("mcpServers", {})
    changed = []
    for name, want in _desktop_entries().items():
        if name not in servers or _norm(servers[name]) != _norm(want):
            changed.append(name)
            servers[name] = want
    if not changed:
        return {"ok": True, "msg": "Claude Desktop đã có đủ 4 MCP server, không cần đổi"}
    note = ""
    if path.exists():
        bak = path.with_name(path.name + time.strftime(".bak-%Y%m%d-%H%M%S"))
        shutil.copy2(path, bak)
        note = f" (sao lưu: {bak.name})"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    ensure_claude_desktop()
    return {"ok": True, "msg": f"Đã cập nhật Claude Desktop: {', '.join(changed)}{note}. Đã mở lại Claude Desktop."}


def process_running_path(path_contains):
    """Co tien trinh nao (ke ca chay ngam o khay) co duong dan chua path_contains khong."""
    if not WIN:
        return False
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-Process | Where-Object { $_.Path } | ForEach-Object { $_.Path }"],
                         capture_output=True, text=True, creationflags=NO_WINDOW).stdout
    return any(path_contains.lower() in ln.lower() for ln in out.splitlines())


def open_claude(folder=STUDIO):
    """Mo VS Code (co extension Claude Code) tai thu muc studio, de dung .mcp.json o day."""
    subprocess.Popen(["cmd", "/c", "code", str(folder)], creationflags=NO_WINDOW)
    return {"ok": True, "msg": f"Đã mở VS Code tại {folder}. Mở khung Claude Code, gõ /mcp để xem kết nối."}


def _main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, arg = argv[0], (argv[1] if len(argv) > 1 else "all")
    if cmd == "status":
        for r in status():
            st = "SẴN SÀNG" if r["listening"] else ("đang mở, cổng đóng" if r["running"] else "tắt")
            print(f"{r['name']:<20} cổng {r['port']:<5} {st}{'' if r['installed'] else '  (chưa cài)'}")
        return 0
    if cmd == "start":
        ids = [a["id"] for a in load_config()["apps"]] if arg == "all" else [arg]
        results = [start(i) for i in ids]
    elif cmd == "mcp-check":
        names = list(mcp_servers()) if arg == "all" else [arg]
        results = [mcp_check(n) for n in names]
    elif cmd == "claude":
        results = [open_claude()]
    elif cmd == "layout":
        results = [arrange(arg)]
    elif cmd == "desktop-status":
        s = desktop_status()
        print(f"Cấu hình Claude Desktop: {s['path']}")
        for r in s["rows"]:
            print(f"  {r['name']:<12} {r['state']}")
        if s["extra"]:
            print(f"  (server khác của bạn, giữ nguyên: {', '.join(s['extra'])})")
        return 0
    elif cmd == "desktop-sync":
        results = [desktop_sync()]
    else:
        print(f"Lệnh không hợp lệ: {cmd}\n{__doc__}")
        return 2
    for r in results:
        print(("[OK]  " if r["ok"] else "[LỖI] ") + r["msg"])
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
