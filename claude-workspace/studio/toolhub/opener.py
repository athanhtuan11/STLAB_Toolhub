"""Nut "Mo bang phan mem tao ra no" cho moi du an (Tuan 2026-10-24).

An toan: trinh duyet KHONG gui duong dan file. files(rel) tu liet ke file mo duoc trong thu muc du an (duoi file
nam trong OPENERS); API chi nhan so thu tu trong danh sach do. POST can X-Studio (kiem o __init__).
- .FCStd -> FreeCAD: dang mo (cong RPC 9875) thi mo file trong cua so do (mo them, khong mat bai dang sua);
  chua mo thi launcher khoi dong FreeCAD kem RPC + file.
- .blend -> Blender: KHONG mo de len Blender dang chay (mat bai chua luu) -> dang chay thi mo cua so moi.
- .3mf/.stl -> Bambu Studio; .fcproj -> FilmCraft; .pdf/.mp4/.png -> ung dung mac dinh cua Windows.
"""
import os
import subprocess
import xmlrpc.client
from pathlib import Path

import launcher

from .workspace import ROOT

# duoi file -> (id ung dung, ten hien thi). id trong apps.json "apps" hoac "openers"; "system" = mac dinh Windows
OPENERS = {".fcstd": "freecad", ".blend": "blender", ".3mf": "bambu", ".stl": "bambu", ".fcproj": "filmcraft",
           ".pdf": "system", ".mp4": "system"}
SKIP = {"backup", "check", "stl", "_log", "node_modules", ".git", "__pycache__"}  # + thu muc "_*" (file sinh)
NO_WINDOW = 0x08000000


def _apps():
    cfg = launcher.load_config()
    apps = {a["id"]: a for a in cfg["apps"]}
    apps.update(cfg.get("openers", {}))
    return apps


def files(rel):
    """[{i, name, rel, app, app_name}] - thu tu co dinh (sap xep) de so thu tu on dinh giua cac lan tai trang."""
    d = (ROOT / rel).resolve()
    apps = _apps()
    out = []
    for p in sorted(d.rglob("*")):
        if not p.is_file() or any(x in SKIP or x.startswith("_") for x in p.relative_to(d).parts[:-1]):
            continue
        app = OPENERS.get(p.suffix.lower())
        if app is None or (app != "system" and app not in apps):
            continue
        if p.suffix.lower() == ".stl" and "plates" not in p.parts:  # STL sinh ra hang loat: chi 3MF ban in
            continue
        name = "Windows" if app == "system" else apps[app]["name"]
        out.append({"name": p.name, "rel": p.relative_to(d).as_posix(), "app": app, "app_name": name, "path": p})
    rank = {"freecad": 0, "blender": 1, "filmcraft": 2, "bambu": 3, "system": 4}
    out.sort(key=lambda f: (rank.get(f["app"], 9), f["rel"]))
    for i, f in enumerate(out):
        f["i"] = i
    return out


def primary(rel):
    """File chinh cua du an (cho nut tren trang chinh): FreeCAD > Blender > FilmCraft > ban in."""
    fs = [f for f in files(rel) if f["app"] != "system"]
    return fs[0] if fs else None


def open_file(rel, i):
    fs = files(rel)
    if not 0 <= i < len(fs):
        return {"ok": False, "msg": "Không tìm thấy file (danh sách đã đổi) – tải lại trang"}
    f = fs[i]
    p = f["path"]
    if not p.resolve().is_relative_to((ROOT / rel).resolve()):  # phong ho (symlink tro ra ngoai)
        return {"ok": False, "msg": "File nằm ngoài thư mục dự án – không mở"}
    app = f["app"]
    if app == "system":
        os.startfile(str(p))
        return {"ok": True, "msg": f"Đã mở {p.name}"}
    a = _apps()[app]
    if app == "freecad":
        return _freecad(a, p)
    if app == "blender" and launcher.process_running(a["image"]):
        _popen([a["exe"], str(p)], a)  # cua so moi: khong dong de bai dang mo
        return {"ok": True, "msg": f"Blender đang chạy → mở {p.name} trong cửa sổ Blender mới"}
    if not Path(a["exe"]).exists():
        return {"ok": False, "msg": f"{a['name']}: chưa cài ({a['exe']})"}
    if "port" in a and not launcher.port_open(a["port"]):  # co MCP, chua chay: launcher (bat cong + xep canh Claude)
        r = launcher.start(app, extra_args=[str(p)])
        return {"ok": r["ok"], "msg": f"{p.name}: {r['msg']}"}
    _popen([a["exe"], str(p)], a)
    return {"ok": True, "msg": f"Đã mở {p.name} bằng {a['name']}"}


def _freecad(a, p):
    if launcher.port_open(a["port"]):
        code = ("import os, FreeCAD\n"
                f"p = {str(p)!r}\n"
                "d = next((x for x in FreeCAD.listDocuments().values()\n"
                "          if x.FileName and os.path.normcase(x.FileName) == os.path.normcase(p)), None)\n"
                "print('da mo san' if d else 'mo moi')\n"
                "d = d or FreeCAD.openDocument(p)\n"
                "FreeCAD.setActiveDocument(d.Name)\n")
        try:
            r = xmlrpc.client.ServerProxy(f"http://localhost:{a['port']}", allow_none=True).execute_code(code)
        except OSError as e:
            return {"ok": False, "msg": f"FreeCAD không trả lời RPC: {e}"}
        if not r.get("success", True):
            return {"ok": False, "msg": f"FreeCAD báo lỗi khi mở {p.name}: {str(r.get('error', r))[:200]}"}
        return {"ok": True, "msg": f"Đã mở {p.name} trong FreeCAD đang chạy"}
    r = launcher.start("freecad", extra_args=[str(p)])
    return {"ok": r["ok"], "msg": f"{p.name}: {r['msg']}"}


def _popen(cmd, a):
    subprocess.Popen(cmd, cwd=str(Path(a["exe"]).parent), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, close_fds=True,
                     creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
