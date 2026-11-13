# Logic OTA thuan (khong mang, khong genai) - 2026-11-13
import hashlib
import json
import os
import re
from pathlib import Path

BOARD_TYPE = "stlab-s3"
CHIP = "esp32s3"
FW_PREFIX = "/xiaozhi/firmware/s3/"
_NAME_RE = re.compile(r"^xiaozhi-[0-9][0-9.]*\.bin$")


def parse_version(s):
    """Giong Ota::ParseVersion trong ota.cc: tach '.', moi doan phai la so nguyen; loi -> None."""
    out = []
    for seg in str(s).split("."):
        if not re.fullmatch(r"[0-9]+", seg):
            return None
        out.append(int(seg))
    return out


def is_newer(new, cur):
    """Giong Ota::IsNewVersionAvailable: so tung so; bang tien to thi ban dai hon la moi."""
    c, n = parse_version(cur), parse_version(new)
    if c is None or n is None:
        return False
    for a, b in zip(n, c):
        if a > b:
            return True
        if a < b:
            return False
    return len(n) > len(c)


def safe_name(name):
    return bool(_NAME_RE.match(name or "")) and "/" not in name and "\\" not in name and ".." not in name


def sysinfo_ok(info):
    """Chi bo S3 cua STLab: chip esp32s3 VA board.type = stlab-s3."""
    if not isinstance(info, dict):
        return False
    chip = str(info.get("chip_model_name", "")).lower()
    btype = str((info.get("board") or {}).get("type", "")).lower()
    return chip == CHIP and btype == BOARD_TYPE


def pick_firmware(sysinfo, manifest, allowed=True, current=None, disabled=None):
    """Tra '/xiaozhi/firmware/s3/<file>' neu nen gui ban moi, khong thi None."""
    if disabled is None:
        disabled = os.environ.get("STLAB_OTA_DISABLE", "").strip() == "1"
    if disabled or not allowed or not sysinfo_ok(sysinfo) or not isinstance(manifest, dict):
        return None
    name = str(manifest.get("file", ""))
    ver = str(manifest.get("version", ""))
    if not safe_name(name) or parse_version(ver) is None:
        return None
    if current is None:
        current = (sysinfo.get("application") or {}).get("version", "")
    if not is_newer(ver, current):
        return None
    return FW_PREFIX + name


_CACHE = {}


def load_manifest(fw_dir):
    """Doc manifest.json + kiem file ton tai + sha256 khop; cache theo mtime. Loi -> None."""
    fw_dir = Path(fw_dir)
    mp = fw_dir / "manifest.json"
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
        name = str(m.get("file", ""))
        if not safe_name(name):
            return None
        fp = fw_dir / name
        st = fp.stat()
        key = (mp.stat().st_mtime_ns, st.st_mtime_ns, st.st_size)
        hit = _CACHE.get(str(fw_dir))
        if hit and hit[0] == key:
            return hit[1]
        h = hashlib.sha256(fp.read_bytes()).hexdigest()
        ok = h == str(m.get("sha256", "")).lower() and st.st_size == int(m.get("size", st.st_size))
        res = m if ok else None
        _CACHE[str(fw_dir)] = (key, res)
        return res
    except Exception:
        return None
