import argparse
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FC_CMD = Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
VIEWS = ("iso", "front", "top", "side34")


def color(v):
    if not isinstance(v, str) or len(v) != 7 or v[0] != "#":
        raise ValueError("Expected #RRGGBB color, got %r" % (v,))
    int(v[1:], 16)
    return v.upper()


def run(cmd, env=None):
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    out = (p.stdout or "") + "\n" + (p.stderr or "")
    if out.strip():
        print("\n".join(out.splitlines()[-20:]))
    if p.returncode:
        tail = "\n".join(out.splitlines()[-12:])
        raise RuntimeError("command failed (%d): %s\n%s" % (p.returncode, cmd[0], tail))


def main():
    ap = argparse.ArgumentParser(description="Render FreeCAD model preview images with Blender")
    ap.add_argument("model", type=Path)
    ap.add_argument("--cmf", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--views", default="iso,front,top,side34")
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--size", default="1600x1200")
    ap.add_argument("--name")
    ap.add_argument("--engine", choices=("eevee", "cycles"), default="eevee")
    a = ap.parse_args()

    try:
        # Resolve every path against the directory the command was run from,
        # and pass only absolute paths down to FreeCAD / Blender.
        a.model = a.model.resolve()
        a.cmf = a.cmf.resolve()
        a.out = a.out.resolve()
        if not a.model.is_file():
            raise ValueError("Model file does not exist: %s" % a.model)
        if not a.cmf.is_file():
            raise ValueError("CMF file does not exist: %s" % a.cmf)

        cmf = json.loads(a.cmf.read_text(encoding="utf-8"))
        default = cmf.get("default", {"color": "#D9DDD9", "finish": "satin"})
        bg = color(cmf.get("background", "#ECF1EF"))
        for style in [default] + list(cmf.get("rules", [])):
            color(style["color"])
            if style["finish"] not in ("matte", "satin", "gloss"):
                raise ValueError("Invalid finish: %r" % (style["finish"],))

        views = [v.strip() for v in a.views.split(",") if v.strip()]
        if not views or any(v not in VIEWS for v in views):
            raise ValueError("Invalid view list: %s (allowed: %s)" % (a.views, ", ".join(VIEWS)))

        w, h = map(int, a.size.lower().split("x"))
        if w <= 0 or h <= 0:
            raise ValueError("Invalid size: %s" % a.size)
        if a.samples <= 0:
            raise ValueError("--samples must be positive")

        name = a.name or a.model.stem
        a.out.mkdir(parents=True, exist_ok=True)
        stl_dir = (a.out / "_stl").resolve()
        stl_dir.mkdir(parents=True, exist_ok=True)
        manifest = (a.out / (name + "-export.json")).resolve()
        scene_path = (a.out / (name + "-scene.json")).resolve()

        env = os.environ.copy()
        env.update(
            RENDER_MODEL=str(a.model),
            RENDER_STL_DIR=str(stl_dir),
            RENDER_EXPORT_JSON=str(manifest),
        )
        if not FC_CMD.is_file():
            raise RuntimeError("FreeCAD command not found: %s" % FC_CMD)
        run([str(FC_CMD), str(HERE / "fc_export.py")], env)

        exported = json.loads(manifest.read_text(encoding="utf-8"))
        objects = []
        for item in exported:
            style = default
            for rule in cmf.get("rules", []):
                names = rule["names"] if isinstance(rule["names"], list) else [rule["names"]]
                if any(fnmatch.fnmatchcase(item["label"], n) for n in names):
                    style = rule
                    break
            objects.append({
                "label": item["label"],
                "stl": str(Path(item["stl"]).resolve()),
                "color": color(style["color"]),
                "finish": style["finish"],
            })

        scene = {
            "background": bg,
            "views": views,
            "objects": objects,
            "size": [w, h],
            "engine": a.engine,
            "samples": a.samples,
        }
        scene_path.write_text(json.dumps(scene, ensure_ascii=False, indent=2), encoding="utf-8")

        if not BLENDER.is_file():
            raise RuntimeError("Blender not found: %s" % BLENDER)
        run([str(BLENDER), "-b", "--factory-startup", "-P", str(HERE / "blender_scene.py"),
             "--", str(scene_path)])

        missing = [name + "-" + v + ".png" for v in views if not (a.out / (name + "-" + v + ".png")).is_file()]
        if missing:
            raise RuntimeError("Blender did not create: " + ", ".join(missing))
        print("RENDER OK %d images" % len(views))
        return 0
    except Exception as exc:
        print("render: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
