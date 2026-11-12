"""Buoc Toi uu in: phan tich hinh hoc, de xuat thong so, cat lop 2 phuong an."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from flask import jsonify, request, send_file

from . import quote as quote_lib

FREE_PY = quote_lib.FREE_PY
QUOTE_SLICE = quote_lib.QUOTE_SLICE
SCRIPTS = quote_lib.ws.ROOT / "tools" / "print" / "scripts"
FREECADCMD = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

STEP2STL = """import os
import Part
import MeshPart
shape = Part.read(os.environ["STLAB_STEP_IN"])
mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.1, AngularDeflection=0.523599)
mesh.write(os.environ["STLAB_STL_OUT"])
"""

_VARIANTS = {"default", "tuned"}


def _parsed_store():
    from . import views
    return getattr(views, "_parsed", {})


def _err(msg, code=400):
    return jsonify({"error": msg}), code


def _item(token):
    item = _parsed_store().get(token or "")
    if item is None:
        raise quote_lib.QuoteError("Ch\u01b0a c\u00f3 file in. H\u00e3y th\u1ea3 file tr\u01b0\u1edbc.")
    return item


def _step_to_stl(src):
    out_dir = Path(src).parent
    stl = out_dir / f"_tune_{Path(src).stem}.stl"
    script = out_dir / "_step2stl_tune.py"
    script.write_text(STEP2STL, encoding="utf-8")
    env = dict(os.environ, STLAB_STEP_IN=str(src), STLAB_STL_OUT=str(stl))
    p = subprocess.run([str(FREECADCMD), str(script)], env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300, creationflags=NO_WINDOW)
    if not stl.exists() or stl.stat().st_size == 0:
        msg = ((p.stdout or "") + (p.stderr or ""))[-300:]
        raise quote_lib.QuoteError("FreeCAD kh\u00f4ng \u0111\u1ed5i \u0111\u01b0\u1ee3c STEP sang STL: " + msg)
    return stl


def _model_file_for_tune(item):
    files = [Path(f) for f in (item.get("files") or [])]
    if not files:
        raise quote_lib.QuoteError("Ch\u01b0a c\u00f3 file in.")
    exts = {p.suffix.lower() for p in files}
    if exts and exts.issubset({".3mf"}):
        return None, "3mf"
    for p in files:
        if p.suffix.lower() in {".stl", ".obj"} and p.exists():
            return p, p.suffix.lower().lstrip(".")
    for p in files:
        if p.suffix.lower() in {".step", ".stp"} and p.exists():
            return _step_to_stl(p), "step"
    for p in files:
        if p.exists():
            return p, p.suffix.lower().lstrip(".")
    raise quote_lib.QuoteError("Kh\u00f4ng t\u00ecm th\u1ea5y file m\u00f4 h\u00ecnh.")


def _run_python_json(args, timeout=180):
    py = str(FREE_PY) if FREE_PY.exists() else sys.executable
    try:
        r = subprocess.run([py, *args], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, creationflags=NO_WINDOW, cwd=str(SCRIPTS))
    except subprocess.TimeoutExpired:
        raise quote_lib.QuoteError("Ph\u00e2n t\u00edch qu\u00e1 l\u00e2u")
    except OSError as e:
        raise quote_lib.QuoteError("Kh\u00f4ng ch\u1ea1y \u0111\u01b0\u1ee3c Python: " + str(e))
    out = (r.stdout or "").strip().splitlines()
    for line in reversed(out):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    err = ((r.stderr or "") + "\n" + (r.stdout or ""))[-400:]
    raise quote_lib.QuoteError("Kh\u00f4ng \u0111\u1ecdc \u0111\u01b0\u1ee3c k\u1ebft qu\u1ea3: " + err)


def _features(stl_path):
    code = (
        "import json,sys; sys.path.insert(0,r'%s'); "
        "from geometry_profile import features; print(json.dumps(features(sys.argv[1]), ensure_ascii=False))"
        % str(SCRIPTS).replace("\\", "\\\\")
    )
    py = str(FREE_PY) if FREE_PY.exists() else sys.executable
    try:
        r = subprocess.run([py, "-c", code, str(stl_path)], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=180, creationflags=NO_WINDOW)
    except Exception as e:
        raise quote_lib.QuoteError("Kh\u00f4ng ch\u1ea1y \u0111\u01b0\u1ee3c ph\u00e2n t\u00edch h\u00ecnh h\u1ecdc: " + str(e))
    for line in reversed((r.stdout or "").strip().splitlines()):
        if line.strip().startswith("{"):
            try:
                return json.loads(line.strip())
            except ValueError:
                pass
    raise quote_lib.QuoteError("Kh\u00f4ng \u0111\u1ecdc \u0111\u01b0\u1ee3c features: " + ((r.stderr or r.stdout or "")[-300:]))


def api_analyze():
    data = request.get_json(silent=True) or {}
    token = data.get("token") or ""
    goals = data.get("goals") or []
    if not isinstance(goals, list):
        goals = []
    goals = [str(g) for g in goals]
    try:
        item = _item(token)
        stl, kind = _model_file_for_tune(item)
        if kind == "3mf":
            return _err("T\u1ed1i \u01b0u in ch\u1ec9 nh\u1eadn STL/OBJ/STEP", 400)
        feat = _features(stl)
        sug = _run_python_json([str(SCRIPTS / "tune_rules.py"), str(stl), *goals], timeout=180)
        return jsonify({"features": feat, "process": sug.get("process") or {},
                        "filament": sug.get("filament") or {}, "items": sug.get("items") or []})
    except quote_lib.QuoteError as e:
        return _err(str(e), 400)
    except Exception as e:
        return _err("L\u1ed7i ph\u00e2n t\u00edch: " + str(e), 500)


def _find_3mf(out_dir):
    return next(Path(out_dir).glob("*.3mf"), None)


def _find_png(out_dir):
    p = Path(out_dir)
    for c in (p / "plate_1.png",):
        if c.exists():
            return c
    for c in p.rglob("plate_1.png"):
        return c
    tmf = _find_3mf(out_dir)
    if tmf:
        try:
            import zipfile
            with zipfile.ZipFile(tmf) as z:
                for n in ("Metadata/plate_1.png", "plate_1.png"):
                    try:
                        data = z.read(n)
                        dest = p / "plate_1.png"
                        dest.write_bytes(data)
                        return dest
                    except KeyError:
                        pass
        except Exception:
            pass
    return None


def _variant_dir(token, variant):
    return quote_lib.work_dir() / "tune" / token / variant


def _save_result(out_dir, token, variant):
    td = _variant_dir(token, variant)
    if td.exists():
        shutil.rmtree(td, ignore_errors=True)
    td.mkdir(parents=True, exist_ok=True)
    tmf = _find_3mf(out_dir)
    if tmf and tmf.exists():
        shutil.copy2(tmf, td / "quote.3mf")
    png = _find_png(out_dir)
    if png and png.exists():
        shutil.copy2(png, td / "plate_1.png")
    if not (td / "plate_1.png").exists() and (td / "quote.3mf").exists():
        try:
            import zipfile
            with zipfile.ZipFile(td / "quote.3mf") as z:
                data = z.read("Metadata/plate_1.png")
                (td / "plate_1.png").write_bytes(data)
        except Exception:
            pass
    qj = Path(out_dir) / "quote_slice.json"
    if qj.exists():
        shutil.copy2(qj, td / "quote_slice.json")
    return td


def _grams_from_res(res):
    g = res.get("grams") or {}
    try:
        return float(sum(float(v) for v in g.values()))
    except Exception:
        return 0.0


def _run_variant(model_file, material, process_name, overrides, out_dir):
    conn = quote_lib.connect()
    try:
        pricing = quote_lib.get_pricing(conn)
    finally:
        conn.close()
    mat = pricing["materials"].get(material) or {}
    profile = mat.get("slicer_profile") or quote_lib.default_profile(material, mat.get("type") or quote_lib.infer_type(material))
    if not profile:
        raise quote_lib.QuoteError(f"Nh\u1ef1a '{material}' ch\u01b0a c\u00f3 profile c\u1eaft l\u1edbp")
    args = [str(FREE_PY), str(QUOTE_SLICE), str(out_dir), f"filament={profile}",
            f"process={process_name}", "support=auto"]
    if overrides:
        ov_path = Path(out_dir) / "overrides.json"
        ov_path.write_text(json.dumps(overrides, ensure_ascii=False), encoding="utf-8")
        args.append(f"overrides={ov_path}")
    args.append(str(model_file))
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=900, creationflags=NO_WINDOW, cwd=str(out_dir))
    except subprocess.TimeoutExpired:
        raise quote_lib.QuoteError("C\u1eaft l\u1edbp qu\u00e1 l\u00e2u (> 15 ph\u00fat)")
    except OSError as e:
        raise quote_lib.QuoteError("Kh\u00f4ng ch\u1ea1y \u0111\u01b0\u1ee3c Bambu Studio CLI: " + str(e))
    res = quote_lib._last_json(r.stdout)
    if res is None:
        raise quote_lib.QuoteError("C\u1eaft l\u1edbp l\u1ed7i: " + ((r.stderr or r.stdout or "")[-300:] or "kh\u00f4ng c\u00f3 k\u1ebft qu\u1ea3"))
    return res


def api_slice():
    data = request.get_json(silent=True) or {}
    token = data.get("token") or ""
    material = data.get("material") or "PETG"
    proc = data.get("process") or {}
    fil = data.get("filament") or {}
    if not isinstance(proc, dict):
        proc = {}
    if not isinstance(fil, dict):
        fil = {}
    try:
        item = _item(token)
        stl, kind = _model_file_for_tune(item)
        if kind == "3mf":
            return _err("T\u1ed1i \u01b0u in ch\u1ec9 nh\u1eadn STL/OBJ/STEP", 400)
        base_tmp = quote_lib.work_dir() / "tune_tmp" / token
        base_tmp.mkdir(parents=True, exist_ok=True)
        process_name = quote_lib.load_defaults().get("print_options", {}).get("process") or "0.20mm Standard @BBL A1"

        out_def = base_tmp / "default"
        out_tun = base_tmp / "tuned"
        for d in (out_def, out_tun):
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)
            d.mkdir(parents=True, exist_ok=True)

        res_def = _run_variant(stl, material, process_name, None, out_def)
        overrides = {"process": proc, "filament": fil}
        res_tun = _run_variant(stl, material, process_name, overrides, out_tun)

        _save_result(out_def, token, "default")
        _save_result(out_tun, token, "tuned")

        def pack(res, variant):
            hours = round(float(res.get("seconds") or 0) / 3600.0, 4)
            return {
                "image_url": f"/api/quote/tune/image/{token}/{variant}",
                "download_url": f"/api/quote/tune/download/{token}/{variant}",
                "hours": hours,
                "grams": round(_grams_from_res(res), 3),
                "warnings": res.get("warnings") or [],
                "status": res.get("status"),
            }
        return jsonify({"default": pack(res_def, "default"), "tuned": pack(res_tun, "tuned")})
    except quote_lib.QuoteError as e:
        return _err(str(e), 400)
    except Exception as e:
        return _err("L\u1ed7i c\u1eaft l\u1edbp: " + str(e), 500)


def serve_image(token, variant):
    if variant not in _VARIANTS:
        return _err("Kh\u00f4ng h\u1ee3p l\u1ec7", 404)
    if token not in _parsed_store():
        return _err("Kh\u00f4ng t\u00ecm th\u1ea5y phi\u00ean", 404)
    p = _variant_dir(token, variant) / "plate_1.png"
    if not p.exists():
        m = _variant_dir(token, variant) / "quote.3mf"
        if m.exists():
            try:
                import zipfile
                with zipfile.ZipFile(m) as z:
                    data = z.read("Metadata/plate_1.png")
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(data)
            except Exception:
                pass
    if not p.exists():
        return _err("Kh\u00f4ng c\u00f3 \u1ea3nh", 404)
    return send_file(p, mimetype="image/png", max_age=0)


def serve_download(token, variant):
    if variant not in _VARIANTS:
        return _err("Kh\u00f4ng h\u1ee3p l\u1ec7", 404)
    if token not in _parsed_store():
        return _err("Kh\u00f4ng t\u00ecm th\u1ea5y phi\u00ean", 404)
    p = _variant_dir(token, variant) / "quote.3mf"
    if not p.exists():
        return _err("Kh\u00f4ng c\u00f3 file", 404)
    return send_file(p, mimetype="model/3mf", as_attachment=True, download_name=f"quote_{variant}.3mf", max_age=0)
