"""Model board vi dieu khien / may tinh nhung tu nguon CHINH HANG da ghim (community/pins.tsv).

  arduino-docs-content       (CC-BY-SA-4.0)  file *-step.zip trong docs.arduino.cc -> giai nen
  espressif-kicad-libraries  (CC-BY-SA-4.0 + mien tru thiet ke)  STEP module ESP32 -> dung truc tiep

Du lieu (khong len git) o community/boards-official/:
  models/<id>/<id>.step   ban giai nen, ten khong dau kebab-case
  models.json             hop bao (mm) do bang FreeCAD (lenh measure)

Lenh:
  python boards.py extract     giai nen Arduino (zip, hoac tar.gz doi ten .zip – Modulino Matrix)
  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" boards.py      do hop bao bang FreeCAD (khong tham so = measure)
File tai ve chi la du lieu: khong chay gi ben trong.
"""

from __future__ import annotations

import io
import json
import tarfile
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # claude-workspace
ARDUINO = ROOT / "community" / "arduino-docs-content"
ESPRESSIF = ROOT / "community" / "espressif-kicad-libraries" / "3dmodels" / "espressif.3dshapes"
DATA = ROOT / "community" / "boards-official"
MODELS = DATA / "models"

# id -> file nguon trong arduino-docs-content (ma san pham ABX...)
ARDUINO_BOARDS = {
    "arduino-uno-r4-wifi": "content/hardware/uno/boards/uno-r4-wifi/downloads/ABX00087-step.zip",
    "arduino-uno-q": "content/hardware/uno/boards/uno-q/downloads/ABX00162-step.zip",
    "arduino-nano-esp32": "content/hardware/nano/boards/nano-esp32/downloads/ABX00083-step.zip",
    "arduino-nano-r4": "content/hardware/nano/boards/nano-r4/downloads/ABX00142-step.zip",
    "arduino-giga-r1-wifi": "content/hardware/mega/boards/giga-r1-wifi/downloads/ABX00063-step.zip",
}
MODULINO = "content/hardware/modulino/modulino-nodes"


def arduino_sources() -> dict[str, Path]:
    src = {k: ARDUINO / v for k, v in ARDUINO_BOARDS.items()}
    for z in sorted((ARDUINO / MODULINO).glob("*/downloads/*-step.zip")):
        src["arduino-" + z.parts[-3]] = z  # modulino-<ten>
    return src


def read_step(path: Path) -> bytes:
    """Lay noi dung STEP duy nhat trong file tai ve (zip, hoac tar.gz doi ten .zip). Chi doc, khong giai nen ra dia."""
    raw = path.read_bytes()
    if raw[:2] == b"\x1f\x8b":
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as t:
            files = [m for m in t.getmembers() if m.isfile() and not m.name.startswith("__MACOSX/")]
            if len(files) != 1:
                raise ValueError(f"{path.name}: can dung 1 file, co {[m.name for m in files]}")
            return t.extractfile(files[0]).read()
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if not n.startswith("__MACOSX/") and not n.endswith("/")]
        if len(names) != 1:
            raise ValueError(f"{path.name}: can dung 1 file, co {names}")
        return z.read(names[0])


def cmd_extract() -> None:
    MODELS.mkdir(parents=True, exist_ok=True)
    for bid, src in arduino_sources().items():
        data = read_step(src)
        if not data.lstrip().startswith(b"ISO-10303-21"):
            raise ValueError(f"{src.name}: khong phai STEP")
        out = MODELS / bid / f"{bid}.step"
        out.parent.mkdir(exist_ok=True)
        out.write_bytes(data)
        print(f"{bid:32} {len(data) / 1e6:5.1f} MB  <- {src.relative_to(ARDUINO).as_posix()}")


def cmd_measure() -> None:
    import Part  # chi co trong Python cua FreeCAD

    files = sorted(MODELS.glob("*/*.step")) + sorted(ESPRESSIF.glob("*.[sS][tT][eE][pP]"))
    res = {}
    for f in files:
        s = Part.read(str(f))
        b = s.optimalBoundingBox() if hasattr(s, "optimalBoundingBox") else s.BoundBox
        key = f.relative_to(ROOT).as_posix()
        res[key] = {"bbox_mm": [round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)],
                    "hop_le": s.isValid(), "solid": len(s.Solids)}
        print(f"{f.name:40} {res[key]}")
    (DATA / "models.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")


if "FreeCAD" in sys.modules:  # freecadcmd chay file nhu module, khong qua __main__
    cmd_measure()
elif __name__ == "__main__":
    {"extract": cmd_extract, "measure": cmd_measure}[sys.argv[1]]()
