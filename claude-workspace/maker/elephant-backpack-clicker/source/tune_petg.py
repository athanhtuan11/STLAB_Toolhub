"""Chuyen 3mf mau sang PETG + chinh cho chu noi dep (cong dong + wiki Bambu, xem README muc PETG).
  python -I tune_petg.py <vao.3mf> <ra.3mf>
- 3 slot nhua = profile he thong "Bambu PETG Basic @BBL A1" (dung chung cho PETG Generic - Tuan 2026-11-14),
  gia tri lay tu profile Bambu Studio da cai (giai inherits), giu mau slot cua tac gia.
- Tat ironing (PETG dinh dau phun, cong dong khuyen tat), "only one wall on top" = not apply (chu noi).
- Chu sac canh: vach ngoai 120 mm/s (PETG 13 mm3/s da tran ~155 mm/s), gia toc 3000, chu vi nho (ban kinh < 10 mm,
  gom net chu) chay 50 % ~ 60 mm/s. KHONG dung layer_config_ranges: CLI Bambu bao "incorrect slicing parameters"
  (2026-11-14, chua ro ly do; log CLI ma hoa) - do day lop khong anh huong canh chu tren mat tren.
"""
import json, re, sys, zipfile
from pathlib import Path
src, dst = sys.argv[1:3]
FIL = "Bambu PETG Basic @BBL A1"
PROFILES = Path(r"C:\Program Files\Bambu Studio\resources\profiles\BBL\filament")
TEXT_TUNE = {"outer_wall_speed": ["120"], "outer_wall_acceleration": ["3000"], "small_perimeter_threshold": ["10"]}

def resolve(name):
    d = json.loads((PROFILES / f"{name}.json").read_text(encoding="utf-8"))
    base = resolve(d["inherits"]) if d.get("inherits") else {}
    base.update(d); return base

prof = resolve(FIL)
skip = {"name", "inherits", "from", "instantiation", "setting_id", "type", "compatible_printers",
        "compatible_printers_condition", "filament_colour", "version", "description"}
z = zipfile.ZipFile(src)
ps = json.loads(z.read("Metadata/project_settings.config"))
n = len(ps["filament_colour"]); changed = []
for k, v in prof.items():
    if k in skip or k not in ps: continue
    if isinstance(ps[k], list) and len(ps[k]) == n and isinstance(v, list) and len(v) == 1:
        if ps[k] != v * n: changed.append(k)
        ps[k] = v * n
ps["filament_settings_id"] = [FIL] * n
ps["filament_ids"] = [prof.get("filament_id", "GFG99")] * n
ps["ironing_type"] = "no ironing"
ps["top_one_wall_type"] = "not apply"
ps["curr_bed_type"] = "Textured PEI Plate"
for k, v in TEXT_TUNE.items():
    ps[k] = v if isinstance(ps.get(k), list) else v[0]
dts = ps.get("different_settings_to_system")
if isinstance(dts, list) and len(dts) >= 2:
    for i in range(1, 1 + n): dts[i] = ""          # slot nhua = profile he thong, khong sua rieng
with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in z.infolist():
        if it.filename == "Metadata/layer_config_ranges.xml": continue
        data = z.read(it.filename)
        if it.filename == "Metadata/project_settings.config":
            data = json.dumps(ps, indent=4, ensure_ascii=False).encode("utf-8")
        zo.writestr(it, data)
print("WROTE", dst, "| doi", len(changed), "khoa nhua | vd:", {k: ps[k][0] for k in
      ["nozzle_temperature", "hot_plate_temp", "textured_plate_temp", "filament_max_volumetric_speed", "filament_flow_ratio", "fan_max_speed"] if k in ps})
