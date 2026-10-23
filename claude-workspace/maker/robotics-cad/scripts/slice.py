"""Cat lop bang Bambu Studio CLI theo print.yaml -> bao cao kha nang in DUNG HUONG IN (tang 2 cua quy trinh).

Slicer la noi kiem kha nang in that: vung lo lung, support, thoi gian, so gam - theo profile A1 chinh hang.
Tang 1 (check.py mode=fast) chi kiem hinh hoc + va cham tren file lap rap.

Chay (Python di kem FreeCAD co san yaml/matplotlib/PIL; khong can FreeCAD):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/slice.py <print.yaml> [out=<thu muc>] [only=P1,P2]

print.yaml (duong dan tuong doi theo data_dir) - mau: maker/robotics-cad/project-template/print/print.yaml.
Ra: <plates_dir>/<plate>/<plate>.3mf (mo thang bang Bambu Studio de in),
    print-overview.png (bang + anh tung ban), print-report.json.
Exit code 1 neu co ban FAIL (cat loi, ra ngoai ban in, vung lo lung) hoac co STL chua xep ban.

TRUOC khi cat (printability.py, 2026-10-23 - Tuan in that thay phan NHO RA khong support bi hong):
- chi tiet co phan nho ra (mat up xuong < 43 do, rong hon cau duoc) ma KHONG co support tu ve ben duoi
  -> WARN "sua thiet ke / ve Support_*" (Slicer KHONG bao loai nay - chi bao cum roi han).
  CHINH SACH (Tuan 2026-10-23): ve toi uu de khong can support; bat buoc thi support TU VE trong model
  (Label Support_*, khe Z 0.2 mm, xuat chung quy tac voi chi tiet); KHONG de slicer tu sinh support.
  `support_policy: slicer` trong print.yaml -> hanh vi cu: tu tach ban "<ban>__support" bat tree support cua slicer,
  lo lung -> tu xoay roi support.
- ban co chi tiet nho (chan < brim_contact_max_mm2) hoac cao manh -> bat brim (tru khi print.yaml da khai brim_type
  khac auto_brim).
Nguong: thresholds.yaml muc `print:`.
"""

from __future__ import annotations

import fnmatch
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import printability  # noqa: E402

EXE = Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")
BBL = EXE.parent / "resources" / "profiles" / "BBL"
MAU = {"PASS": "#4caf50", "WARN": "#ff9800", "FAIL": "#e53935", "INFO": "#9e9e9e"}
# canh bao khong lien quan chat luong chi tiet
BO_QUA = {"not_support_traditional_timelapse"}
# canh bao do chinh profile hang gay ra -> ghi chu, khong tinh WARN
GHI_CHU = {
    # Profile nhua dat nhiet ban > nhiet hoa mem (PLA chinh hang: 65 > 45 C). A1 khung ho; nhieu kha nang canh bao
    # nham may buong kin (tac dau in). TODO: mo 3MF bang Bambu Studio xem GUI co bao khong.
    "bed_temperature_too_high_than_filament": "nhiet ban > nhiet hoa mem cua nhua (theo profile, A1 khung ho)",
}
# loi lam hong ban in -> FAIL (cum tu trong warning_message cua result.json)
NANG = ("floating regions", "floating cantilever", "empty layer")
# support them khi xoay huong in van lo lung
SUPPORT = {"enable_support": "1", "support_type": "tree(auto)", "support_on_build_plate_only": "0"}
BRIM = {"brim_type": "outer_only", "brim_width": "5"}
NGUONG = Path(__file__).resolve().parent.parent / "thresholds.yaml"


def tham_so():
    a = {"yaml": None, "out": None, "only": ""}
    for t in sys.argv[1:]:
        k, eq, v = t.partition("=")
        if eq and k in a:
            a[k] = v
        else:
            a["yaml"] = t
    if not a["yaml"]:
        raise SystemExit(__doc__)
    return a


def chi_muc_profile():
    """Profile chinh hang + preset rieng cua Tuan trong Bambu Studio (preset rieng de len neu trung ten).
    Preset rieng (vd. KINGROON-PETG) da hieu chinh flow/PA tren may that -> uu tien cho ban in that."""
    idx = {}
    user = sorted(Path(os.environ.get("APPDATA", "")).joinpath("BambuStudio", "user").glob("*"))
    for sub in ("machine", "process", "filament"):
        for f in [*(BBL / sub).rglob("*.json"), *(p for u in user for p in (u / sub).rglob("*.json"))]:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                continue
            idx[(sub, d.get("name", f.stem))] = f
    return idx


def phang(idx, sub, ten):
    """Gop chuoi inherits cua profile chinh hang thanh 1 dict."""
    if (sub, ten) not in idx:
        raise SystemExit(f"Khong co profile {sub} '{ten}' trong {BBL}")
    d = json.loads(idx[(sub, ten)].read_text(encoding="utf-8"))
    cha = d.get("inherits")
    ra = phang(idx, sub, cha) if cha else {}
    ra.update({k: v for k, v in d.items() if k != "inherits"})
    return ra


def ghi(d, p):
    p.write_text(json.dumps(d, indent=1), encoding="utf-8")
    return str(p)


def cat(thu_muc, ten, stl, p_may, p_proc, p_fil, xoay=False):
    """Khoi chay Bambu Studio CLI (khong cho) cho 1 ban: xep ban, cat lop, xuat 3MF.
    xoay=True: --orient 1 (Bambu tu chon huong in it phan lo lung/support nhat)."""
    thu_muc.mkdir(parents=True, exist_ok=True)
    for f in thu_muc.iterdir():
        if f.is_file():
            f.unlink()
    lenh = [str(EXE), "--debug", "2", "--load-settings", f"{p_may};{p_proc}", "--load-filaments", p_fil,
            "--arrange", "1", "--orient", "1" if xoay else "0", "--avoid-extrusion-cali-region", "--slice", "0",
            "--export-3mf", f"{ten}.3mf", "--outputdir", str(thu_muc)] + [str(f) for f in stl]
    log = open(thu_muc / "cli_log.txt", "w", encoding="utf-8")
    p = subprocess.Popen(lenh, stdout=log, stderr=subprocess.STDOUT, cwd=thu_muc,
                         creationflags=0x08000000)  # CREATE_NO_WINDOW
    return p, log, thu_muc, {"stl": stl, "profile": (p_may, p_proc, p_fil)}


def lo_lung(r):
    return any(k in x for x in r.get("loi", []) for k in NANG)


def doi(viec):
    for p, log, _, _ in viec.values():
        p.wait()
        log.close()


def doc_ket_qua(thu_muc, ten):
    """result.json (thoi gian, gam, canh bao cat lop) + slice_info.config trong 3MF (support, ngoai ban, canh bao)."""
    r = {"ban": ten, "anh": None}
    f = thu_muc / "result.json"
    if not f.exists():
        return {**r, "trang_thai": "FAIL", "loi": ["khong co result.json (Bambu CLI loi, xem cli_log.txt)"]}
    j = json.loads(f.read_text(encoding="utf-8"))
    loi, canh_bao = [], []
    if j.get("return_code") != 0:
        loi.append(f"Bambu CLI: {j.get('error_string')}")
    sp = (j.get("sliced_plates") or [{}])[0]
    r["thoi_gian_s"] = round(sp.get("total_predication", 0))
    r["gam"] = round(sum(x.get("total_used_g", 0) for x in sp.get("filaments", [])), 1)
    r["so_chi_tiet"] = len(sp.get("objects", []))
    # result.json chi giu 1 canh bao; cli_log co du (vd. ca Housing_Shoulder lan Housing_Elbow)
    fl = thu_muc / "cli_log.txt"
    log = fl.read_text(encoding="utf-8", errors="replace") if fl.exists() else ""
    ds = {x.split("slicing warnings:", 1)[1].strip() for x in log.splitlines() if "slicing warnings:" in x}
    ds |= {(sp.get("warning_message") or "").strip()} - {""}
    for wm in sorted(ds):
        (loi if any(k in wm for k in NANG) else canh_bao).append(wm)
    r["co_canh_bao_cat"] = bool(ds)
    tmf = next(thu_muc.glob("*.3mf"), None)
    if tmf:
        with zipfile.ZipFile(tmf) as z:
            if "Metadata/slice_info.config" in z.namelist():
                plate = ET.fromstring(z.read("Metadata/slice_info.config")).find("plate")
                meta = {m.get("key"): m.get("value") for m in plate.findall("metadata")}
                r["support"] = meta.get("support_used") == "true"
                if meta.get("outside") == "true":
                    loi.append("chi tiet nam ngoai ban in")
                for w in plate.findall("warning"):
                    if w.get("msg") in GHI_CHU:
                        r.setdefault("ghi_chu", []).append(GHI_CHU[w.get("msg")])
                    elif w.get("msg") not in BO_QUA:
                        canh_bao.append(f"{w.get('msg')} (muc {w.get('level')})")
            if "Metadata/plate_1.png" in z.namelist():
                r["anh"] = str(thu_muc / "plate_1.png")
                Path(r["anh"]).write_bytes(z.read("Metadata/plate_1.png"))
    r["loi"], r["canh_bao"] = loi, sorted(set(canh_bao))
    r["trang_thai"] = "FAIL" if loi else ("WARN" if canh_bao else "PASS")
    return r


def anh_tong_quan(bc, png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image

    bans = bc["ban"]
    cot = 4
    hang_anh = (len(bans) + cot - 1) // cot
    cao_bang = 0.5 * (len(bans) + 1) + 0.6 + 0.3 * len(bc["stl_chua_xep"] or [])
    fig = plt.figure(figsize=(18, cao_bang + 4.2 * hang_anh))
    tong = cao_bang + 4.2 * hang_anh
    ax = fig.add_axes((0.01, 1 - cao_bang / tong, 0.98, (cao_bang - 0.6) / tong))
    ax.axis("off")
    cell, mau = [], []
    for b in bans:
        tg = b.get("thoi_gian_s", 0)
        ghi_chu = "; ".join(b["loi"] + b.get("canh_bao", []))
        cell.append([b["ban"], b["trang_thai"], f"{tg // 3600}h{tg % 3600 // 60:02d}", f"{b.get('gam', 0)} g",
                     "co" if b.get("support") else "khong", textwrap.shorten(ghi_chu or "-", 110)])
        mau.append(["#ffffff", MAU[b["trang_thai"]], "#ffffff", "#ffffff", "#ffffff", "#ffffff"])
    t = ax.table(cellText=cell, cellColours=mau, loc="upper left", cellLoc="left",
                 colLabels=["Bàn in", "Kết quả", "Thời gian", "Nhựa", "Support", "Cảnh báo của slicer"],
                 colWidths=[0.2, 0.06, 0.06, 0.06, 0.05, 0.57])
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    fig.suptitle(f"Cắt lớp Bambu Studio – KẾT QUẢ: {bc['ket_luan']}   "
                 f"tổng {bc['tong_thoi_gian_in']}, {bc['tong_gam']} g"
                 f"   (cắt lớp {bc['thoi_gian_chay_s']} s, {bc['thoi_gian']})", fontsize=12, x=0.01, ha="left")
    if bc["stl_chua_xep"]:
        fig.text(0.01, 1 - cao_bang / tong + 0.1 / tong, "STL CHƯA XẾP BÀN: " + ", ".join(bc["stl_chua_xep"]),
                 color="#e53935", fontsize=9)
    for k, b in enumerate(bans):
        h, c = divmod(k, cot)
        x0 = 0.01 + c * 0.245
        y0 = (hang_anh - 1 - h) * 4.2 / tong
        a2 = fig.add_axes((x0, y0, 0.235, 3.9 / tong))
        a2.axis("off")
        if b.get("anh"):
            a2.imshow(Image.open(b["anh"]))
        a2.set_title(f"{b['ban']} – {b['trang_thai']}", fontsize=9, color=MAU[b["trang_thai"]])
    fig.savefig(png, dpi=90)
    plt.close(fig)


def main():
    a = tham_so()
    t0 = time.time()
    cfg_p = Path(a["yaml"]).resolve()
    cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))
    goc = (cfg_p.parent / cfg.get("data_dir", ".")).resolve()  # FCStd/STL co the o ngoai repo
    stl_dir = (goc / cfg["stl"]).resolve()
    ra = Path(a["out"]).resolve() if a["out"] else (goc / cfg["plates_dir"]).resolve()
    prof = ra / "_profile"
    prof.mkdir(parents=True, exist_ok=True)
    tat_ca = sorted(stl_dir.glob("*.stl"))
    if not tat_ca:
        raise SystemExit(f"Khong co STL trong {stl_dir}")

    # xep STL vao ban; STL nao chua xep / bi xep 2 lan -> bao
    xep = {}
    for ten, b in cfg["plates"].items():
        bo = b.get("exclude", [])
        xep[ten] = [f for f in tat_ca if any(fnmatch.fnmatch(f.name, g) for g in b["stl"])
                    and not any(fnmatch.fnmatch(f.name, g) for g in bo)]
    dem = {f.name: sum(f in v for v in xep.values()) for f in tat_ca}
    chua_xep = [n for n, c in dem.items() if c == 0]
    trung = [n for n, c in dem.items() if c > 1]

    # phan tich hinh hoc theo huong in: phan nho ra can support, chi tiet nho can brim
    tng = yaml.safe_load(NGUONG.read_text(encoding="utf-8")) if NGUONG.exists() else {}
    ngp = dict(tng.get("print") or {}, overhang_deg=tng.get("overhang_deg", 45))
    pt = {f.name: printability.phan_tich(f, ngp) for f in tat_ca}

    idx = chi_muc_profile()
    may = phang(idx, "machine", cfg["machine"])
    may["from"] = "system"
    p_may = ghi(may, prof / "machine.json")
    chon = [x.strip() for x in a["only"].split(",") if x.strip()]
    chay, proc_d, xu_ly, brim, nho_ra = {}, {}, {}, {}, {}
    slicer_sp = cfg.get("support_policy", "modeled") == "slicer"
    if not chon:  # chay ca du an: xoa thu muc ban cu (doi ten/bo ban) de khong in nham 3MF cu - day la file sinh
        con = set(cfg["plates"]) | {f"{t}__orient" for t in cfg["plates"]} | {f"{t}__support" for t in cfg["plates"]}
        for d in ra.iterdir():
            if d.is_dir() and not d.name.startswith("_") and d.name not in con:
                shutil.rmtree(d)
        for f in prof.glob("*.json"):
            if f.name != "machine.json":  # vua ghi o tren
                f.unlink()  # profile ban ghep lai moi lan chay
    for ten, b in cfg["plates"].items():
        if chon and not any(fnmatch.fnmatch(ten, c) for c in chon):
            continue
        if not xep[ten]:
            print(f"bo qua {ten}: khong co STL", flush=True)
            continue
        d = phang(idx, "process", b["process"])
        d.update(cfg.get("common") or {})
        d.update(b.get("overrides") or {})
        d.update({"name": f"STLab {ten}", "from": "User", "inherits": b["process"], "instantiation": "true"})
        p_proc = ghi(d, prof / f"process_{ten}.json")
        proc_d[ten] = d
        fil = phang(idx, "filament", b.get("filament") or cfg["filament"])  # khong khai -> filament mac dinh du an
        fil.setdefault("from", "system")
        # ghi de nhua (khoa cua profile filament, gia tri dang list: {filament_max_volumetric_speed: ["12"]})
        fil.update(cfg.get("filament_overrides") or {})
        fil.update(b.get("filament_overrides") or {})
        # preset rieng (Bambu Studio GUI tao) thieu 2 khoa nay -> CLI bao "preset file is invalid" (da gap 2026-10-23)
        fil.setdefault("type", "filament")
        fil.setdefault("instantiation", "true")
        p_fil = ghi(fil, prof / f"filament_{ten}.json")
        stl_ban = xep[ten]
        co_sp = str(d.get("enable_support", "0")) == "1"
        treo_all = [] if co_sp else [f for f in stl_ban if pt[f.name]["can_support"]]
        if co_sp and not slicer_sp:
            nho_ra[ten] = ["ban dung support TU DONG cua slicer (print.yaml enable_support) - nen sua thiet ke / ve Support_*"]
        if treo_all and not slicer_sp:
            nho_ra[ten] = [f"{f.name}: nho ra khong do " + ", ".join(f"{c['mm2']} mm2 rong {c['rong_mm']} mm o z {c['z_mm']}"
                                                                for c in pt[f.name]["cum_nho"][:2]) for f in treo_all]
        treo = treo_all if slicer_sp else []
        nho = [f for f in stl_ban if pt[f.name]["can_brim"]]
        # auto_brim = de Bambu tu quyet -> Tuan thay chi tiet nho van bong (2026-10-23) -> ghi de; chi giu brim khai ro
        if nho and (b.get("overrides") or {}).get("brim_type") in (None, "auto_brim"):
            d.update(BRIM)
            p_proc = ghi(d, prof / f"process_{ten}.json")
            brim[ten] = {f.name: pt[f.name]["ly_do_brim"] for f in nho}
        con = [f for f in stl_ban if f not in treo]
        if con:
            chay[ten] = cat(ra / ten, ten, con, p_may, p_proc, p_fil)
        else:
            for f in (ra / ten).glob("*") if (ra / ten).exists() else []:
                if f.is_file():
                    f.unlink()
        if treo:  # nho ra o ban khong support -> ban rieng co support, GIU huong in
            d2 = dict(d, **SUPPORT)
            d2["name"] += " support"
            p_sp = ghi(d2, prof / f"process_{ten}__support.json")
            proc_d[ten + "__support"] = d2
            chay[ten + "__support"] = cat(ra / (ten + "__support"), ten + "__support", treo, p_may, p_sp, p_fil)
            xu_ly[ten] = {"xoay": [], "support": [f.name for f in treo],
                          "ly_do": {f.name: pt[f.name]["cum_nho"][:2] for f in treo}}
    print(f"Cat lop {len(chay)} ban song song ...", flush=True)
    doi(chay)
    bans = [doc_ket_qua(td, ten) for ten, (_, _, td, _) in chay.items()]
    # support TU VE (export support: true, khe Z 0.2): slicer khong biet do la support -> bao "floating" o lop ngay tren
    # khe (giong top_z_distance cua support slicer). printability da kiem moi mat nho ra deu co do -> doi thanh ghi chu.
    fx = stl_dir / "_export-stl.json"
    tu_ve = set(json.loads(fx.read_text(encoding="utf-8")).get("support_tu_ve", {})) if fx.exists() else set()

    def bo_khe(b):
        giu = []
        for x in b.get("loi", []):
            if any(f"object {n} has" in x for n in tu_ve) and not pt.get(next(n for n in tu_ve if f"object {n} has" in x),
                                                                        {}).get("can_support"):
                b.setdefault("ghi_chu", []).append("support tu ve (khe 0.2 mm): " + x.split("It seems object ")[-1]
                                                   .split(" has")[0])
            else:
                giu.append(x)
        b["loi"] = giu
        b["trang_thai"] = "FAIL" if giu else ("WARN" if b.get("canh_bao") else "PASS")

    for b in bans:  # nho ra khong co support (chinh sach modeled) -> WARN de sua thiet ke
        if nho_ra.get(b["ban"]):
            b["canh_bao"] = b.get("canh_bao", []) + nho_ra[b["ban"]]
            if b["trang_thai"] == "PASS":
                b["trang_thai"] = "WARN"

    # Bambu CLI chi bao 1 canh bao cat lop moi ban (lan nao bao chi tiet nao khong co dinh)
    # -> ban co canh bao: cat lai TUNG chi tiet de biet du chi tiet nao loi (nhanh: ~2 s, song song)
    le = {}
    for b in bans:
        if b.get("co_canh_bao_cat") and b.get("so_chi_tiet", 0) > 1:
            td, a_ = chay[b["ban"]][2], chay[b["ban"]][3]
            for f in a_["stl"]:
                le[(b["ban"], f.name)] = cat(td / "_per-part" / f.stem, f.stem, [f], *a_["profile"])
    kq_le = {}
    if le:
        print(f"Cat lai {len(le)} chi tiet rieng de tim du canh bao ...", flush=True)
        doi(le)
        kq_le = {k: doc_ket_qua(v[2], k[1]) for k, v in le.items()}
        for b in bans:
            ds = [r for k, r in kq_le.items() if k[0] == b["ban"]]
            if ds:
                b["loi"] = [x for x in b["loi"] if "It seems object" not in x]
                b["canh_bao"] = [x for x in b["canh_bao"] if "It seems object" not in x]
                for r in ds:
                    b["loi"] += [x for x in r["loi"] if "It seems object" in x]
                    b["canh_bao"] += [x for x in r["canh_bao"] if "It seems object" in x]
                b["trang_thai"] = "FAIL" if b["loi"] else ("WARN" if b["canh_bao"] else "PASS")
    for b in bans:
        bo_khe(b)

    # Lo lung -> (1) cho Bambu tu xoay huong in (--orient 1); (2) van lo lung -> them support
    # (thu tu do Tuan quy dinh 2026-10-23).
    # Chi tiet xu ly tach ra ban rieng "<ban>__orient" / "<ban>__support" de ban goc khong bi xoay/support theo.
    lo = []
    for b in bans if slicer_sp else []:  # modeled: lo lung = FAIL, sua thiet ke (khong tu xoay / support)
        if str(proc_d.get(b["ban"], {}).get("enable_support", "0")) == "1":
            continue  # ban da co support -> lo lung do support do
        stl = chay[b["ban"]][3]["stl"]
        if len(stl) == 1:
            lo += [(b["ban"], stl[0])] if lo_lung(b) else []
        else:
            lo += [(b["ban"], f) for f in stl if (b["ban"], f.name) in kq_le and lo_lung(kq_le[(b["ban"], f.name)])]
    if lo:
        print(f"{len(lo)} chi tiet lo lung -> thu cho Bambu xoay huong in ...", flush=True)
        tx = {(bn, f.name): cat(chay[bn][2] / "_orient" / f.stem, f.stem, [f], *chay[bn][3]["profile"], xoay=True)
              for bn, f in lo}
        doi(tx)
        can_sp = [(bn, f) for bn, f in lo if lo_lung(doc_ket_qua(tx[(bn, f.name)][2], f.stem))]
        p_sp = {}
        for bn in {bn for bn, _ in can_sp}:
            d2 = dict(proc_d[bn], **SUPPORT)
            d2["name"] += " support"
            p_sp[bn] = ghi(d2, prof / f"process_{bn}__support.json")
        if can_sp:
            print(f"{len(can_sp)} chi tiet xoay van lo lung -> them support ...", flush=True)
        moi = {}
        for bn in sorted({bn for bn, _ in lo}):
            pm, pp, pf = chay[bn][3]["profile"]
            tach_s = [f for b2, f in can_sp if b2 == bn]
            tach_x = [f for b2, f in lo if b2 == bn and f not in tach_s]
            con = [f for f in chay[bn][3]["stl"] if f not in tach_x + tach_s]
            if con:
                moi[bn] = cat(ra / bn, bn, con, pm, pp, pf)
            else:
                for f in (ra / bn).iterdir():
                    if f.is_file():
                        f.unlink()  # 3MF cu khong con dung -> xoa de khong in nham
            if tach_x:
                moi[bn + "__orient"] = cat(ra / (bn + "__orient"), bn + "__orient", tach_x, pm, pp, pf, xoay=True)
            if tach_s:  # gop voi ban __support da tach truoc do (phan nho ra) neu co
                cu = chay[bn + "__support"][3]["stl"] if bn + "__support" in chay else []
                moi[bn + "__support"] = cat(ra / (bn + "__support"), bn + "__support", cu + tach_s, pm, p_sp[bn], pf,
                                            xoay=not cu)
            x = xu_ly.setdefault(bn, {"xoay": [], "support": []})
            x["xoay"] += [f.name for f in tach_x]
            x["support"] += [f.name for f in tach_s]
        doi(moi)
        thay = [doc_ket_qua(v[2], ten) for ten, v in moi.items()]
        bans = sorted([b for b in bans if b["ban"] not in moi] + thay, key=lambda b: b["ban"])
    for b in bans:
        print(f"  {b['ban']}: {b['trang_thai']} {b.get('thoi_gian_s', 0) // 60} ph, {b.get('gam', 0)} g "
              + "; ".join(b["loi"] + b.get("canh_bao", [])), flush=True)

    tong_s = sum(b.get("thoi_gian_s", 0) for b in bans)
    ket_luan = "FAIL" if chua_xep or any(b["trang_thai"] == "FAIL" for b in bans) else (
        "WARN" if trung or any(b["trang_thai"] == "WARN" for b in bans) else "PASS")
    bc = {"yaml": str(cfg_p), "thoi_gian": time.strftime("%Y-%m-%d %H:%M"), "ket_luan": ket_luan,
          "tong_thoi_gian_in": f"{tong_s // 3600}h{tong_s % 3600 // 60:02d}",
          "tong_gam": round(sum(b.get("gam", 0) for b in bans), 1),
          "stl_chua_xep": chua_xep, "stl_xep_2_lan": trung, "xu_ly_lo_lung": xu_ly, "brim": brim, "ban": bans,
          "thoi_gian_chay_s": round(time.time() - t0, 1)}
    anh_tong_quan(bc, ra / "print-overview.png")
    (ra / "print-report.json").write_text(json.dumps(bc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"KET LUAN: {ket_luan}  ({bc['thoi_gian_chay_s']} s)  -> {ra}")
    return 1 if ket_luan == "FAIL" else 0


sys.exit(main())
