"""Cat lop 1 file bat ky (STL/OBJ/STEP/3MF) bang Bambu Studio CLI theo profile A1 chinh hang.

Chay bang Python di kem FreeCAD (co yaml/matplotlib/PIL va FreeCAD Part cho STEP):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" quote_slice.py --list-filaments
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" quote_slice.py <out_dir> \
        filament="Bambu PETG Basic @BBL A1" [process="0.20mm Standard @BBL A1"] \
        [infill=<so %>] [support=auto|off] <file...>

Dung lai ham cua slice.py (chi_muc_profile, phang, ghi, cat, doc_ket_qua, SUPPORT).
Ra <out_dir>/quote.3mf (mo thang bang Bambu Studio de in), plate_1.png, result.json,
quote_slice.json + in JSON ket qua o dong cuoi stdout.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import slice as sl  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

FREECADCMD = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
MACHINE = "Bambu Lab A1 0.4 nozzle"
PROCESS_DEFAULT = "0.20mm Standard @BBL A1"
BED_TYPE = "Textured PEI Plate"
NO_WINDOW = 0x08000000
CLI_TIMEOUT = 300
MODEL_EXT = {".stl", ".obj"}
STEP_EXT = {".step", ".stp"}
ALL_EXT = MODEL_EXT | STEP_EXT | {".3mf"}

STEP2STL = """import os
import Part
import MeshPart
shape = Part.read(os.environ["STLAB_STEP_IN"])
mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.1, AngularDeflection=0.523599)
mesh.write(os.environ["STLAB_STL_OUT"])
"""


def _a1_name(name):
    return "A1" in name and "A1M" not in name and "A1 mini" not in name


def _nozzle_ok(name):
    m = re.search(r"(\d\.\d)\s*nozzle", name)
    return not m or m.group(1) == "0.4"


def _user_root():
    return Path(os.environ.get("APPDATA", "")).joinpath("BambuStudio", "user")


def list_profiles():
    """Profile filament/process dung duoc cho A1 0.4: chinh hang @BBL A1 + preset rieng cua Tuan."""
    idx = sl.chi_muc_profile()
    try:
        user = _user_root().resolve()
    except OSError:
        user = _user_root()
    fil, proc = set(), set()
    for (sub, name), path in idx.items():
        if sub not in ("filament", "process") or not _a1_name(name) or not _nozzle_ok(name):
            continue
        try:
            in_user = user in path.resolve().parents
        except OSError:
            in_user = False
        if "@BBL A1" in name or in_user:
            (fil if sub == "filament" else proc).add(name)
    return {"filaments": sorted(fil), "processes": sorted(proc)}


def filament_type(fil):
    t = fil.get("filament_type")
    if isinstance(t, list):
        t = t[0] if t else ""
    return str(t or "").strip()


def grams_from_3mf(path):
    """Gam theo loai nhua tu slice_info.config trong .3mf da cat lop."""
    with zipfile.ZipFile(path) as z:
        raw = z.read("Metadata/slice_info.config")
    out = {}
    for plate in ET.fromstring(raw).iter("plate"):
        for f in plate.findall("filament"):
            typ = f.get("type") or "Không rõ"
            try:
                g = float(f.get("used_g") or 0)
            except (TypeError, ValueError):
                g = 0.0
            out[typ] = out.get(typ, 0.0) + g
    return out


def _read_result(td):
    f = td / "result.json"
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _step_to_stl(src, out_dir, i):
    stl = out_dir / f"_{i}_{src.stem}.stl"
    script = out_dir / "_step2stl.py"
    script.write_text(STEP2STL, encoding="utf-8")
    env = dict(os.environ, STLAB_STEP_IN=str(src), STLAB_STL_OUT=str(stl))
    p = subprocess.run([str(FREECADCMD), str(script)], env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=CLI_TIMEOUT,
                       creationflags=NO_WINDOW)
    if not stl.exists() or stl.stat().st_size == 0:
        msg = (p.stdout or "") + (p.stderr or "")
        raise RuntimeError("FreeCAD không đổi được STEP sang STL: " + msg[-300:])
    return stl


def _parse_args(argv):
    a = {"out": None, "filament": None, "process": None, "infill": None, "support": "auto", "files": []}
    for t in argv:
        k, eq, v = t.partition("=")
        if eq and k in ("filament", "process", "infill", "support"):
            a[k] = v
        elif a["out"] is None:
            a["out"] = t
        else:
            a["files"].append(t)
    return a


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--list-filaments" in argv:
        print(json.dumps(list_profiles(), ensure_ascii=False))
        return 0

    a = _parse_args(argv)
    result = {"status": "fail", "seconds": 0, "grams": {}, "gcode_3mf": None,
              "warnings": [], "errors": [], "support": False, "fallback": None}
    if not a["out"]:
        result["errors"].append("thiếu thư mục ra (out_dir)")
        print(json.dumps(result, ensure_ascii=False))
        return 1
    out = Path(a["out"]).resolve()
    out.mkdir(parents=True, exist_ok=True)

    def finish(res):
        (out / "quote_slice.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(res, ensure_ascii=False))
        return 0 if res["status"] in ("ok", "warn") else 1

    if not a["filament"]:
        result["errors"].append("thiếu filament=\"<tên profile>\"")
        return finish(result)

    files = []
    for name in a["files"]:
        p = Path(name).resolve()
        if not p.is_file():
            result["errors"].append(f"không có file: {name}")
        elif p.suffix.lower() not in ALL_EXT:
            result["errors"].append(f"đuôi file không hỗ trợ: {p.name}")
        else:
            files.append(p)
    if result["errors"]:
        return finish(result)
    if not files:
        result["errors"].append("không có file in")
        return finish(result)

    try:
        infill = None if a["infill"] is None or str(a["infill"]).strip() == "" else int(float(a["infill"]))
    except ValueError:
        result["errors"].append(f"infill không phải số: {a['infill']}")
        return finish(result)
    support = (a["support"] or "auto").strip().lower()
    want_support = support != "off"
    process_name = (a["process"] or PROCESS_DEFAULT).strip()

    t0 = time.time()
    try:
        idx = sl.chi_muc_profile()
        may = sl.phang(idx, "machine", MACHINE)
        may["from"] = "system"
        prof = out / "_profile"
        prof.mkdir(parents=True, exist_ok=True)
        p_may = sl.ghi(may, prof / "machine.json")
        fil = sl.phang(idx, "filament", a["filament"])
        fil.setdefault("from", "system")
        fil.setdefault("type", "filament")
        fil.setdefault("instantiation", "true")
        p_fil = sl.ghi(fil, prof / "filament.json")
    except SystemExit as e:
        result["errors"].append(str(e))
        return finish(result)
    except (OSError, ValueError) as e:
        result["errors"].append("Không đọc được profile: " + str(e))
        return finish(result)

    def write_proc(support_on):
        proc = sl.phang(idx, "process", process_name)
        proc.update({"curr_bed_type": BED_TYPE, "name": "STLab quote", "from": "User",
                     "inherits": process_name, "instantiation": "true"})
        if infill is not None:
            proc["sparse_infill_density"] = f"{infill}%"
        if support_on:
            proc.update(sl.SUPPORT)
        return sl.ghi(proc, prof / ("process_support.json" if support_on else "process.json"))

    models, orient = [], True
    try:
        for i, p in enumerate(files):
            if p.suffix.lower() in STEP_EXT:
                models.append(_step_to_stl(p, out, i))
            else:
                models.append(p)
    except (RuntimeError, subprocess.SubprocessError, OSError) as e:
        result["errors"].append(str(e))
        return finish(result)
    orient = not all(p.suffix.lower() == ".3mf" for p in files)

    def run(support_on, sub_name):
        try:
            p_proc = write_proc(support_on)
        except SystemExit as e:
            raise RuntimeError(str(e))
        td = out / sub_name
        p, log, thu_muc, _ = sl.cat(td, "quote", models, p_may, p_proc, p_fil, xoay=orient)
        timed_out = False
        try:
            p.wait(timeout=CLI_TIMEOUT)
        except subprocess.TimeoutExpired:
            timed_out = True
            p.kill()
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                pass
        log.close()
        kq = sl.doc_ket_qua(thu_muc, "quote")
        if timed_out:
            kq.setdefault("loi", []).append("Bambu CLI quá 300 s")
        return td, kq

    def make(td, kq, support_on, fallback=None, warnings=None, errors=None):
        tmf = next(td.glob("*.3mf"), None)
        grams = {}
        if tmf:
            try:
                grams = grams_from_3mf(tmf)
            except (KeyError, zipfile.BadZipFile, ET.ParseError, OSError):
                grams = {}
        if sum(grams.values()) <= 0:
            rj = _read_result(td)
            sp = (rj.get("sliced_plates") or [{}])[0] if rj else {}
            total = sum(float(x.get("total_used_g") or 0) for x in (sp.get("filaments") or []))
            if total <= 0:
                total = float(kq.get("gam") or 0)
            if total > 0:
                grams = {filament_type(fil) or "Không rõ": total}
        errs = [str(x) for x in (kq.get("loi") or [])] + list(errors or [])
        warns = [str(x) for x in (kq.get("canh_bao") or [])] + list(warnings or [])
        if sum(grams.values()) <= 0:
            status = "fail"
        elif errs or warns:
            status = "warn"
        else:
            status = "ok"
        return {"status": status, "seconds": int(round(kq.get("thoi_gian_s") or 0)),
                "grams": grams, "gcode_3mf": str(tmf) if tmf else None,
                "warnings": warns, "errors": errs, "support": bool(support_on), "fallback": fallback}

    try:
        td, kq = run(want_support, "slice")
        res = make(td, kq, want_support)
        is_3mf = all(p.suffix.lower() == ".3mf" for p in models)
        if is_3mf and want_support and res["errors"]:
            td2, kq2 = run(False, "slice_support_off")
            res2 = make(td2, kq2, False, fallback="support-off",
                        warnings=["chưa tính support – kiểm lại trong Bambu Studio"],
                        errors=[f"bản có support lỗi: {x}" for x in res["errors"]])
            if sum(res2["grams"].values()) > sum(res["grams"].values()) or res2["status"] != "fail":
                res = res2
    except (RuntimeError, subprocess.SubprocessError, OSError) as e:
        result["errors"].append(str(e))
        return finish(result)

    res["slice_seconds"] = round(time.time() - t0, 1)
    return finish(res)


if __name__ == "__main__":
    sys.exit(main())
