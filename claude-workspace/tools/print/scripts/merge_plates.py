"""Gop cac ban in (moi ban 1 file 3MF cua Bambu Studio CLI) thanh 1 project 3MF nhieu plate.

Dung boi slice.py (xem docstring slice.py). Cach lam (khong sua cat lop tung ban):
 1. Moi ban -> 1 plate: object cua ban doi id/ten file/UUID; toa do giu nguyen (cung goc ban in) cong lech o plate
    (bo cuc luoi Bambu Studio: buoc = 1,2 x kich thuoc ban, so cot = ceil(sqrt(N))).
 2. Moi ban -> 1 filament slot (filament_colour cua ban) => project co N filament, object plate i dung slot i.
    Mang filament_* trong project_settings.config lay khung tu 1 lan chay CLI (N filament), gia tri tung slot lay
    tu 3MF cua ban tuong ung.
 3. Tham so process khac nhau giua cac ban (brim_type, sparse_infill_density, ...) -> ghi de muc object trong
    model_settings.config cua chi tiet thuoc ban do.
 4. Thu cho Bambu Studio CLI cat lai project (--slice 0 = tat ca plate) -> Metadata/plate_N.gcode, gui in ngay duoc.
    2026-11-26: "G-code conflicts" truoc day do objectid luoi TRUNG giua cac plate (moi plate hien cung 1 mau) - da sua (cong off);
    CLI cat duoc ca project (co gcode tung plate). Neu CLI loi -> giu project chua cat: mo Bambu Studio bam Slice all.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
import tempfile
import uuid
import zipfile
from pathlib import Path
from xml.sax.saxutils import quoteattr

BED = 256.0  # A1
GAP = 0.2
# khoa project_settings khong chuyen thanh override object
KHONG_OVERRIDE = {"print_settings_id", "filament_settings_id", "default_filament_colour", "filament_colour"}


def _uid(seed: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def goc_plate(i: int, n: int):
    cols = max(1, math.ceil(math.sqrt(n)))
    return (i % cols) * BED * (1 + GAP), -(i // cols) * BED * (1 + GAP)


def _dich(tf: str, dx: float, dy: float) -> str:
    v = tf.split()
    v[9] = repr(float(v[9]) + dx)
    v[10] = repr(float(v[10]) + dy)
    return " ".join(v)


def mau_khung(exe, may, proc, fils, stl, tmp: Path):
    """Chay CLI voi N filament -> project_settings (mang filament_* dai N)."""
    lenh = [str(exe), "--load-settings", f"{may};{proc}", "--load-filaments", ";".join(str(f) for f in fils),
            "--arrange", "1", "--orient", "0", "--export-3mf", "tpl.3mf", "--outputdir", str(tmp), str(stl)]
    subprocess.run(lenh, cwd=tmp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000,
                   timeout=300)
    p = tmp / "tpl.3mf"
    if not p.exists():
        raise RuntimeError("CLI khong tao duoc project khung N filament")
    with zipfile.ZipFile(p) as z:
        return json.loads(z.read("Metadata/project_settings.config"))


def gop(ra: Path, ten: str, ds_ban: list, exe: Path, may: str, procs: dict, fils: dict, stl_mau: Path):
    """ds_ban: [{'ban': ten, ...}] theo thu tu plate; procs/fils: ban -> duong dan profile json.
    Tra ve (duong dan file, so plate, da_cat)."""
    plates = []
    for b in ds_ban:
        f = next((ra / b["ban"]).glob("*.3mf"), None)
        if f and b["ban"] in procs:
            plates.append((b["ban"], f))
    n = len(plates)
    if n == 0:
        return None, 0, False
    z = [zipfile.ZipFile(f) for _, f in plates]
    sett = [json.loads(x.read("Metadata/project_settings.config")) for x in z]
    with tempfile.TemporaryDirectory() as td:
        tpl = mau_khung(exe, may, procs[plates[0][0]], [fils[p] for p, _ in plates], stl_mau, Path(td))
    # --- project_settings: khung N filament + process cua ban dau
    ps = dict(sett[0])
    for k, v in tpl.items():
        if not isinstance(v, list):
            continue
        if len(v) == n and n > 1 and all(isinstance(s.get(k), list) and len(s[k]) == 1 for s in sett):
            ps[k] = [s[k][0] for s in sett]
        elif len(v) != len(sett[0].get(k) or []):
            ps[k] = v  # vd. flush_volumes_matrix (N x N), filament_map: lay khung N filament cua CLI
    mau = [str((s.get("filament_colour") or ["#00AE42"])[0]) for s in sett]
    ps["filament_colour"] = mau
    ps["default_filament_colour"] = mau
    # khoa process khac nhau giua cac ban -> override muc object
    khac = []
    for s in sett:
        ov = {}
        for k, v in s.items():
            if k in KHONG_OVERRIDE or k.startswith("filament") or k.endswith("_id"):
                continue
            if json.dumps(v, sort_keys=True) != json.dumps(sett[0].get(k), sort_keys=True):
                ov[k] = v if isinstance(v, str) else json.dumps(v)
        khac.append(ov)
    # --- ghep model
    files: dict[str, bytes] = {}
    res, build, objs_xml, plate_xml = [], [], [], []
    model_head = None
    for i, (ban, _) in enumerate(plates):
        zz = z[i]
        dx, dy = goc_plate(i, n)
        model = zz.read("3D/3dmodel.model").decode("utf-8")
        if model_head is None:
            model_head = model[:model.index("<resources>")]
        ms = zz.read("Metadata/model_settings.config").decode("utf-8")
        off = (i + 1) * 100
        rs = model[model.index("<resources>") + 11:model.index("</resources>")]
        bd = model[model.index("<build"):model.index("</build>")]
        for nm in zz.namelist():
            mm = re.fullmatch(r"3D/Objects/object_(\d+)\.model", nm)
            if mm:
                moi = f"3D/Objects/object_p{i + 1}_{mm.group(1)}.model"
                # 2026-11-26 (Tuan: "5 plates nhung cung 1 mau"): Bambu Studio tra luoi theo objectid cua component,
                # khong theo duong dan -> id luoi trong file con PHAI duy nhat giua cac plate (cong off) + UUID moi.
                sub = zz.read(nm).decode("utf-8")
                sub = re.sub(r'(<object id=")(\d+)(")', lambda m: f"{m.group(1)}{int(m.group(2)) + off}{m.group(3)}", sub)
                sub = re.sub(r'p:UUID="([^"]+)"', lambda m: f'p:UUID="{_uid(f"s{i}{nm}{m.group(1)}")}"', sub)
                files[moi] = sub.encode("utf-8")
                rs = rs.replace("/" + nm, "/" + moi)
        rs = re.sub(r'(<object id=")(\d+)(")', lambda m: f"{m.group(1)}{int(m.group(2)) + off}{m.group(3)}", rs)
        rs = re.sub(r'(<component [^>]*?objectid=")(\d+)(")', lambda m: f"{m.group(1)}{int(m.group(2)) + off}{m.group(3)}", rs)
        rs = re.sub(r'p:UUID="([^"]+)"', lambda m: f'p:UUID="{_uid(f"{i}{m.group(1)}")}"', rs)
        res.append(rs)
        for it in re.finditer(r"<item [^>]*/>", bd):
            s = it.group(0)
            s = re.sub(r'objectid="(\d+)"', lambda m: f'objectid="{int(m.group(1)) + off}"', s)
            s = re.sub(r'p:UUID="([^"]+)"', lambda m: f'p:UUID="{_uid(f"b{i}{m.group(1)}")}"', s)
            s = re.sub(r'transform="([^"]+)"', lambda m: f'transform="{_dich(m.group(1), dx, dy)}"', s)
            build.append(s)
        for m in re.finditer(r'<object id="(\d+)">(.*?)</object>', ms, re.S):
            body = re.sub(r'(<metadata key="extruder" value=")\d+(")', lambda q: f"{q.group(1)}{i + 1}{q.group(2)}",
                          m.group(2))
            extra = "".join(f"    <metadata key={quoteattr(k)} value={quoteattr(str(v))}/>\n" for k, v in khac[i].items())
            if extra:
                body = body.replace("    <metadata face_count", extra + "    <metadata face_count", 1)
            objs_xml.append(f'  <object id="{int(m.group(1)) + off}">{body}</object>')
        pl = re.search(r"<plate>.*?</plate>", ms, re.S).group(0)
        ins = []
        for t in re.findall(r"<model_instance>.*?</model_instance>", pl, re.S):
            t = re.sub(r'(key="object_id" value=")(\d+)(")', lambda q: f"{q.group(1)}{int(q.group(2)) + off}{q.group(3)}", t)
            t = re.sub(r'(key="identify_id" value=")(\d+)(")', lambda q: f"{q.group(1)}{int(q.group(2)) + off * 10}{q.group(3)}", t)
            ins.append("    " + t)
        plate_xml.append(
            "  <plate>\n"
            f'    <metadata key="plater_id" value="{i + 1}"/>\n'
            f'    <metadata key="plater_name" value={quoteattr(ban)}/>\n'
            '    <metadata key="locked" value="false"/>\n'
            '    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
            f'    <metadata key="filament_maps" value="{" ".join(["1"] * n)}"/>\n'
            '    <metadata key="filament_volume_maps" value="0"/>\n'
            + "\n".join(ins) + "\n  </plate>")
    model_xml = (model_head + "<resources>" + "".join(res) + " </resources>\n " + '<build p:UUID="' + _uid("build") +
                 '">\n  ' + "\n  ".join(build) + "\n </build>\n</model>\n")
    ms_xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "\n".join(objs_xml) + "\n" + "\n".join(plate_xml) +
              "\n  <assemble>\n  </assemble>\n</config>\n")
    rel_model = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for k, nm in enumerate(sorted(files), 1):
        rel_model.append(f' <Relationship Target="/{nm}" Id="rel-{k}" '
                         'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>')
    rel_model.append("</Relationships>")
    out = ra / f"{ten}.3mf"
    tho = ra / f"_{ten}.raw.3mf"
    with zipfile.ZipFile(tho, "w", zipfile.ZIP_DEFLATED) as o:
        o.writestr("[Content_Types].xml", z[0].read("[Content_Types].xml"))
        o.writestr("_rels/.rels", z[0].read("_rels/.rels"))
        o.writestr("3D/3dmodel.model", model_xml)
        o.writestr("3D/_rels/3dmodel.model.rels", "\n".join(rel_model))
        for nm, data in files.items():
            o.writestr(nm, data)
        o.writestr("Metadata/model_settings.config", ms_xml)
        o.writestr("Metadata/project_settings.config", json.dumps(ps, separators=(",", ":")))
    # cat lai tat ca plate -> gcode tung plate
    da_cat = False
    with tempfile.TemporaryDirectory() as td:
        lenh = [str(exe), "--slice", "0", "--export-3mf", "out.3mf", "--outputdir", td, str(tho)]
        try:
            subprocess.run(lenh, cwd=td, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           creationflags=0x08000000, timeout=900)
        except subprocess.TimeoutExpired:
            pass
        sl = Path(td) / "out.3mf"
        if sl.exists():
            with zipfile.ZipFile(sl) as zs:
                da_cat = all(f"Metadata/plate_{k}.gcode" in zs.namelist() for k in range(1, n + 1))
            if da_cat:
                out.write_bytes(sl.read_bytes())
    if not da_cat:
        out.write_bytes(tho.read_bytes())
    tho.unlink()
    return out, n, da_cat
