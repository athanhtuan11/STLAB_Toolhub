"""Phan dung chung: ap kieu mau (preset STLab / LUT / XMP) + sua cuc bo PhotoCraft cho 1 anh.

Mot kieu cho ra 2 anh cung kich thuoc:
  under  anh truoc khi ap kieu      over  anh da ap kieu
Do manh s (0..1) = tron under/over (s = 1: ap het). Toolhub xem truoc bang cach chong 2 anh voi opacity,
xuat that bang blend() -> hai cach cho cung ket qua.

  base  under = anh may anh (plain)          over = preset STLab (+ sua cuc bo)
  LUT   under = preset STLab (+ sua cuc bo)  over = under + LUT (PhotoCraft Color Lookup)
  xmp   under = plain                        over = preset XMP qua LightCraft (+ sua cuc bo)
"""

from __future__ import annotations

import json
import os
import shutil
import threading
import subprocess
from pathlib import Path

from PIL import Image

from luts import COMMUNITY, OUT as LUTS, slug

ROOT = Path(__file__).resolve().parent.parent
LOOKS_FILE = ROOT / "presets" / "looks.json"
BASE_FILE = ROOT / "presets" / "su-kien-ngoai-troi.json"
LC_CLI = Path(r"C:\Program Files\LightCraft\lightcraft-cli.exe")
PC_CLI = Path(r"C:\Program Files\PhotoCraft\photocraft-cli.exe")
EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

# Nang sang nguoi bi nguoc sang (thu 2026-10-21 tren anh 20/10): chon nguoi -> lam mem vien -> nang bong + trung tone
LOCAL = [
    ("select.subject", {}),
    ("select.modify.feather", {"radius": 40}),
    ("image.adjustments.shadowsHighlights", {"shadowAmount": 25, "shadowTone": 45, "shadowRadius": 60, "color": 10}),
    ("image.adjustments.curves", {"points": [[0, 0], [128, 138], [255, 255]]}),
    ("select.deselect", {}),
]


def load_looks(path: Path = LOOKS_FILE) -> dict[str, dict]:
    return {lk["id"]: lk for lk in json.loads(path.read_text(encoding="utf-8"))["looks"]}


def base_values(path: Path = BASE_FILE) -> dict:
    v = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(v, dict) or any(isinstance(x, dict) for x in v.values()):
        raise ValueError('preset phai la JSON phang {"light.exposure": 0.1, ...}')
    return v


def kind(look: dict) -> str:
    return "xmp" if "xmp" in look else "lut" if ("hald" in look or "cube" in look) else "base"


def lut_file(look: dict) -> Path:
    if "hald" in look:
        p = LUTS / (slug(Path(look["hald"]).stem) + ".cube")
        if not p.exists():
            raise FileNotFoundError(f"{p.name} chua co -> chay: uv run scripts/luts.py --default")
        return p
    return COMMUNITY / look["cube"]


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0 or '"error"' in p.stdout:
        raise RuntimeError((p.stderr or p.stdout).strip()[-400:])


def lc_render(src: Path, out: Path, size: int, extra: list[str], quality: int = 92) -> None:
    run([str(LC_CLI), "render", str(src), "-o", str(out), "--size", str(size), "--quality", str(quality),
         "--opt", "colorSpace=srgb", "--opt", "removeLocation=true", "--opt", "metadata=none", *extra])  # fmt: skip


def pc_run(inp: Path, out: Path, cmds: list[tuple[str, dict]], quality: int = 92) -> None:
    """PhotoCraft can duong dan kieu Windows (D:/...) va CHEP EXIF tu anh vao -> chi dua anh da xoa metadata."""
    args = [str(PC_CLI), "run", str(inp.resolve())]
    for cid, params in cmds:
        args += ["--cmd", cid] + (["--params", json.dumps(params)] if params else [])
    run(args + ["--out", str(out.resolve()), "--quality", str(quality)])


def build(src: Path, look: dict, local: bool, work: Path, size: int, values: dict,
          quality: int = 92) -> tuple[Path, Path]:  # fmt: skip
    """Tao (under, over) trong thu muc work; file da co thi dung lai (cache cho Toolhub)."""
    work.mkdir(parents=True, exist_ok=True)
    loc = "-local" if local else ""

    def step(name: str, fn) -> Path:
        p = work / name
        if not p.exists():
            # ten tam rieng cho tung tien trinh/luong: Toolhub co the tao cung file song song
            tmp = p.with_name(f"tmp-{os.getpid()}-{threading.get_ident()}-{p.name}")
            fn(tmp)
            try:
                tmp.replace(p)
            except OSError:
                if not p.exists():
                    raise
                tmp.unlink(missing_ok=True)
        return p

    plain = lambda: step("plain.jpg", lambda o: lc_render(src, o, size, [], quality))  # noqa: E731
    base = step("base.jpg", lambda o: lc_render(src, o, size, [x for k, v in values.items() for x in ("--set", f"{k}={v}")], quality))
    if local:
        base = step("base-local.jpg", lambda o: pc_run(work / "base.jpg", o, LOCAL, quality))
    k = kind(look)
    if k == "base":
        return plain(), base
    if k == "lut":
        cmd = ("image.adjustments.colorLookup", {"file": lut_file(look).resolve().as_posix()})
        return base, step(f"{look['id']}{loc}.jpg", lambda o: pc_run(base, o, [cmd], quality))
    xmp = step(f"{look['id']}.jpg", lambda o: lc_render(src, o, size, ["--settings", str(COMMUNITY / look["xmp"])], quality))
    if local:
        xmp = step(f"{look['id']}-local.jpg", lambda o: pc_run(work / f"{look['id']}.jpg", o, LOCAL, quality))
    return plain(), xmp


def blend(under: Path, over: Path, strength: float, out: Path, quality: int = 92) -> None:
    """Tron theo do manh; giu ICC, khong mang EXIF."""
    if strength >= 0.999:
        shutil.copyfile(over, out)
        return
    a, b = Image.open(under), Image.open(over)
    icc = b.info.get("icc_profile")
    Image.blend(a.convert("RGB"), b.convert("RGB"), max(strength, 0.0)).save(out, quality=quality, icc_profile=icc)
